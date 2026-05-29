# Plan de Développement - Pac-Man Project

## 📅 Roadmap d'implémentation

Ce document détaille un **plan de développement séquencé** pour réaliser le projet Pac-Man en phases cohérentes et testables.

**Objectif**: Implémenter le projet en 6 phases + déploiement, chacune étant testable indépendamment.

---

## 🎯 Vue d'ensemble des phases

```
Phase 0: Infrastructure
    ↓
Phase 1: Configuration & State
    ↓
Phase 2: Entities & Core Gameplay
    ↓
Phase 3: IA & Maze Integration
    ↓
Phase 4: UI & Input
    ↓
Phase 5: Polish & Features
    ↓
Phase 6: Testing & Packaging
    ↓
Deployment
```

---

## 🔧 PHASE 0: Infrastructure (Durée: 2-3 jours)

### Objectifs
- [ ] Initialiser la structure du projet
- [ ] Configurer l'environnement de développement
- [ ] Mettre en place les outils (linting, testing, logging)
- [ ] Créer les bases utilitaires

### Tâches

#### 0.1 Structure des répertoires
```bash
mkdir -p src/{config,game,entities/{ai},maze,ui/{scenes},input,highscore,cheat,utils}
mkdir -p tests
mkdir -p doc/{PROJECT_MANAGEMENT}
mkdir -p .data
```

#### 0.2 Fichiers de base
- [ ] `requirements.txt` - Dépendances
  ```
    pygame==X.X.X         # Rendu graphique
  A-Maze-ing==X.X.X     # Génération labyrinthe (à obtenir)
  pytest==X.X.X         # Tests
  mypy==X.X.X           # Type checking
  flake8==X.X.X         # Linting
  ```

- [ ] `Makefile`
  ```makefile
  install:
  	pip install -r requirements.txt
  
  run:
  	python3 pac-man.py config.json
  
  debug:
  	python3 -m pdb pac-man.py config.json
  
  clean:
  	find . -type d -name __pycache__ -exec rm -rf {} +
  	find . -type d -name .mypy_cache -exec rm -rf {} +
  	find . -type d -name .pytest_cache -exec rm -rf {} +
  
  lint:
  	flake8 src tests
  	mypy src tests --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
  
  test:
  	pytest tests -v
  ```

- [ ] `.gitignore`
  ```
  __pycache__/
  *.pyc
  .mypy_cache/
  .pytest_cache/
  .venv/
  *.egg-info/
  dist/
  build/
  .data/highscores.json
  ```

#### 0.3 Utilitaires de base

**`src/utils/constants.py`**
```python
from enum import Enum

# Game constants
TILE_SIZE = 20
FPS = 60
FRAME_TIME = 1.0 / FPS

# Colors (RGB)
class Color(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    PINK = (255, 184, 255)
    CYAN = (0, 255, 255)
    ORANGE = (255, 184, 82)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)
```

**`src/utils/logger.py`**
```python
import logging

def setup_logger(name: str) -> logging.Logger:
    """Setup logging with standard format."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

**`src/utils/exceptions.py`**
```python
class PacmanError(Exception):
    """Base exception for Pac-Man game."""
    pass

class ConfigError(PacmanError):
    """Configuration error."""
    pass

class MazeGenerationError(PacmanError):
    """Maze generation error."""
    pass

class GameStateError(PacmanError):
    """Game state error."""
    pass
```

**`src/utils/types.py`**
```python
from typing import Tuple

Position = Tuple[int, int]  # (x, y) in tiles
Velocity = Tuple[int, int]  # (dx, dy)
```

#### 0.4 Fichier d'entrée principal

**`pac-man.py`** (point d'entrée)
```python
#!/usr/bin/env python3
"""Pac-Man game - Main entry point."""

import sys
import logging
from pathlib import Path

from src.config.config_loader import ConfigLoader
from src.config.config_validator import ConfigValidator
from src.game.game_manager import GameManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main() -> int:
    """Main entry point."""
    if len(sys.argv) != 2:
        logger.error("Usage: python3 pac-man.py <config.json>")
        return 1
    
    config_path = sys.argv[1]
    
    try:
        config = ConfigLoader.load(config_path)
        config = ConfigValidator.validate(config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return 1
    
    try:
        game = GameManager(config)
        game.run()
    except Exception as e:
        logger.error(f"Game error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### 0.5 Configuration de base

**`config.json`** (template)
```json
{
  // Configuration du jeu Pac-Man
  "highscore_filename": ".data/highscores.json",
  "lives": 3,
  "pacgum_count": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "ghost_respawn_time": 10,
  "super_pacgum_duration": 10,
  "levels": [
    {
      "width": 21,
      "height": 21,
      "seed": 42,
      "max_time": 90
    }
  ]
}
```

### ✅ Checkpoint Phase 0
```bash
make install  # ✅ Installe sans erreurs
make lint     # ✅ 0 erreurs flake8 + mypy
ls src/*/     # ✅ Tous les répertoires existent
```

---

## 📝 PHASE 1: Configuration & GameState (Durée: 2-3 jours)

### Objectifs
- [ ] Parser JSON avec commentaires
- [ ] Valider configuration
- [ ] Créer GameState (singleton)
- [ ] Tests unitaires

### Dépendances
- Phase 0 ✅

### Tâches

#### 1.1 Config Loader

**`src/config/config_loader.py`**
```python
"""Configuration loader with comment support."""

import json
import re
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Load JSON config files with comment support."""
    
    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        """Load config from JSON file with comments."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(path, 'r') as f:
            content = f.read()
        
        content = ConfigLoader._remove_comments(content)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def _remove_comments(content: str) -> str:
        """Remove comments from JSON content."""
        # Remove // comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Remove # comments
        content = re.sub(r'#.*?$', '', content, flags=re.MULTILINE)
        return content
```

#### 1.2 Config Validator

**`src/config/config_validator.py`**
```python
"""Configuration validation and defaults."""

from typing import Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ConfigValidator:
    """Validate and apply defaults to configuration."""
    
    DEFAULT_CONFIG = {
        "highscore_filename": ".data/highscores.json",
        "lives": 3,
        "pacgum_count": 42,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "ghost_respawn_time": 10,
        "super_pacgum_duration": 10,
        "levels": [
            {"width": 21, "height": 21, "seed": 42, "max_time": 90}
        ]
    }
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate config and apply defaults."""
        if not isinstance(config, dict):
            logger.warning("Config is not a dict, using defaults")
            return ConfigValidator.DEFAULT_CONFIG.copy()
        
        # Merge with defaults
        validated = ConfigValidator.DEFAULT_CONFIG.copy()
        validated.update(config)
        
        # Validate values
        ConfigValidator._validate_values(validated)
        
        return validated
    
    @staticmethod
    def _validate_values(config: Dict[str, Any]) -> None:
        """Validate individual values."""
        # Validate lives
        if config.get("lives", 3) < 1:
            logger.warning("Invalid lives count, using default: 3")
            config["lives"] = 3
        
        # Validate points
        for key in ["points_per_pacgum", "points_per_super_pacgum", "points_per_ghost"]:
            if config.get(key, 0) < 0:
                logger.warning(f"Invalid {key}, using default")
                config[key] = ConfigValidator.DEFAULT_CONFIG[key]
        
        # Validate levels
        if not isinstance(config.get("levels"), list) or len(config["levels"]) == 0:
            logger.warning("Invalid levels, using default")
            config["levels"] = ConfigValidator.DEFAULT_CONFIG["levels"]
```

#### 1.3 Game State

**`src/game/game_state.py`**
```python
"""Global game state (Singleton)."""

from typing import List, Optional
from dataclasses import dataclass, field
from src.utils.types import Position
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class GameState:
    """Global game state."""
    score: int = 0
    lives: int = 3
    current_level: int = 1
    level_time_remaining: int = 90
    is_paused: bool = False
    is_game_over: bool = False
    is_victory: bool = False
    pacman_position: Position = (0, 0)
    ghost_positions: List[Position] = field(default_factory=list)
    pellets_eaten: int = 0
    
    _instance: Optional['GameState'] = None
    
    def __new__(cls) -> 'GameState':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def reset(self) -> None:
        """Reset game state."""
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.is_paused = False
        self.is_game_over = False
        self.is_victory = False
    
    def add_score(self, points: int) -> None:
        """Add points to score."""
        self.score += max(0, points)
    
    def lose_life(self) -> None:
        """Lose one life."""
        self.lives -= 1
        logger.info(f"Life lost! Remaining: {self.lives}")
    
    def next_level(self) -> None:
        """Move to next level."""
        self.current_level += 1
        logger.info(f"Level: {self.current_level}")
```

#### 1.4 Tests

**`tests/test_config.py`**
```python
"""Test configuration loading and validation."""

import pytest
import json
import tempfile
from pathlib import Path

from src.config.config_loader import ConfigLoader
from src.config.config_validator import ConfigValidator
from src.utils.exceptions import ConfigError

def test_config_loader_valid():
    """Test loading valid config."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"lives": 5}, f)
        f.flush()
        
        config = ConfigLoader.load(f.name)
        assert config["lives"] == 5
        
        Path(f.name).unlink()

def test_config_loader_with_comments():
    """Test loading config with comments."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("""
        {
          // Comment style C++
          "lives": 5,  // Lives count
          # Comment style Python
          "points_per_pacgum": 10  # Points
        }
        """)
        f.flush()
        
        config = ConfigLoader.load(f.name)
        assert config["lives"] == 5
        assert config["points_per_pacgum"] == 10
        
        Path(f.name).unlink()

def test_config_validator_defaults():
    """Test validation applies defaults."""
    config = {"lives": 5}
    validated = ConfigValidator.validate(config)
    
    assert validated["lives"] == 5
    assert validated["points_per_pacgum"] == 10
    assert len(validated["levels"]) > 0

def test_config_loader_file_not_found():
    """Test error when file not found."""
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("nonexistent.json")

def test_config_loader_invalid_json():
    """Test error for invalid JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json}")
        f.flush()
        
        with pytest.raises(ValueError):
            ConfigLoader.load(f.name)
        
        Path(f.name).unlink()
```

**`tests/test_gamestate.py`**
```python
"""Test GameState."""

from src.game.game_state import GameState

def test_gamestate_singleton():
    """Test GameState is singleton."""
    state1 = GameState()
    state2 = GameState()
    assert state1 is state2

def test_gamestate_add_score():
    """Test adding score."""
    state = GameState()
    state.score = 0
    state.add_score(10)
    assert state.score == 10
    state.add_score(5)
    assert state.score == 15

def test_gamestate_lose_life():
    """Test losing life."""
    state = GameState()
    state.lives = 3
    state.lose_life()
    assert state.lives == 2

def test_gamestate_reset():
    """Test reset."""
    state = GameState()
    state.score = 100
    state.lives = 1
    state.reset()
    assert state.score == 0
    assert state.lives == 3
```

### ✅ Checkpoint Phase 1
```bash
make install
make lint       # ✅ 0 erreurs
make test       # ✅ Tous les tests passent
python3 pac-man.py config.json  # ✅ Démarre (sans jeu encore)
```

---

## 🎮 PHASE 2: Entities & Core Gameplay (Durée: 3-4 jours)

### Objectifs
- [ ] Créer classes Entity, Pacman, Ghost, Pellet
- [ ] Mouvement de base
- [ ] Collision detection simple
- [ ] Scoring basique

### Dépendances
- Phase 1 ✅

### Tâches

#### 2.1 Entity de base

**`src/entities/entity.py`**
```python
"""Base entity class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.utils.types import Position, Velocity

@dataclass
class Entity(ABC):
    """Base class for all game entities."""
    x: int
    y: int
    
    @property
    def position(self) -> Position:
        """Get position as tuple."""
        return (self.x, self.y)
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update entity state."""
        pass
    
    def move_to(self, x: int, y: int) -> None:
        """Move entity to position."""
        self.x = x
        self.y = y
```

#### 2.2 Pacman

**`src/entities/pacman.py`**
```python
"""Pacman entity."""

from src.entities.entity import Entity
from src.utils.constants import Direction
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Pacman(Entity):
    """Pacman entity."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.direction: Direction = Direction.NONE
        self.next_direction: Direction = Direction.NONE
        self.is_invincible: bool = False
    
    def update(self, delta_time: float) -> None:
        """Update Pacman state."""
        # Try next direction first
        if self.next_direction != Direction.NONE:
            self.direction = self.next_direction
            self.next_direction = Direction.NONE
    
    def set_direction(self, direction: Direction) -> None:
        """Set next direction."""
        self.next_direction = direction
    
    def move(self, dx: int, dy: int) -> None:
        """Move Pacman."""
        self.x += dx
        self.y += dy
```

#### 2.3 Ghost

**`src/entities/ghost.py`**
```python
"""Ghost entity."""

from enum import Enum
from src.entities.entity import Entity
from src.utils.constants import Color
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GhostType(Enum):
    """Ghost types with colors."""
    BLINKY = Color.RED
    PINKY = Color.PINK
    INKY = Color.CYAN
    CLYDE = Color.ORANGE

class Ghost(Entity):
    """Ghost entity."""
    
    def __init__(self, ghost_type: GhostType, x: int, y: int):
        super().__init__(x, y)
        self.ghost_type = ghost_type
        self.color = ghost_type.value
        self.is_edible: bool = False
        self.edible_timer: float = 0.0
        self.spawn_x: int = x
        self.spawn_y: int = y
    
    def update(self, delta_time: float) -> None:
        """Update ghost state."""
        if self.is_edible:
            self.edible_timer -= delta_time
            if self.edible_timer <= 0:
                self.is_edible = False
    
    def become_edible(self, duration: float) -> None:
        """Make ghost edible."""
        self.is_edible = True
        self.edible_timer = duration
    
    def respawn(self) -> None:
        """Respawn ghost at spawn point."""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.is_edible = False
```

#### 2.4 Pellet

**`src/entities/pellet.py`**
```python
"""Pellet entity."""

from src.entities.entity import Entity

class Pellet(Entity):
    """Pellet entity (pacgum or power pellet)."""
    
    def __init__(self, x: int, y: int, is_super: bool = False):
        super().__init__(x, y)
        self.is_super = is_super
        self.points = 50 if is_super else 10
        self.is_eaten = False
    
    def update(self, delta_time: float) -> None:
        """Update pellet (no-op for pellets)."""
        pass
    
    def eat(self) -> int:
        """Eat pellet and return points."""
        if not self.is_eaten:
            self.is_eaten = True
            return self.points
        return 0
```

#### 2.5 Collision Detection

**`src/game/collision.py`**
```python
"""Collision detection."""

from typing import List, Optional
from src.entities.pacman import Pacman
from src.entities.ghost import Ghost
from src.entities.pellet import Pellet
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CollisionDetector:
    """Detect collisions between entities."""
    
    @staticmethod
    def check_pacman_ghost_collision(
        pacman: Pacman,
        ghosts: List[Ghost]
    ) -> Optional[Ghost]:
        """Check if Pacman collides with any ghost."""
        for ghost in ghosts:
            if pacman.x == ghost.x and pacman.y == ghost.y:
                return ghost
        return None
    
    @staticmethod
    def check_pacman_pellet_collision(
        pacman: Pacman,
        pellets: List[Pellet]
    ) -> Optional[Pellet]:
        """Check if Pacman collides with any pellet."""
        for pellet in pellets:
            if not pellet.is_eaten and pacman.x == pellet.x and pacman.y == pellet.y:
                return pellet
        return None
```

#### 2.6 Tests

**`tests/test_entities.py`**
```python
"""Test entities."""

from src.entities.pacman import Pacman
from src.entities.ghost import Ghost, GhostType
from src.entities.pellet import Pellet
from src.utils.constants import Direction

def test_pacman_creation():
    """Test Pacman creation."""
    pacman = Pacman(10, 10)
    assert pacman.x == 10
    assert pacman.y == 10

def test_pacman_move():
    """Test Pacman movement."""
    pacman = Pacman(10, 10)
    pacman.move(1, 0)
    assert pacman.x == 11
    assert pacman.y == 10

def test_ghost_creation():
    """Test Ghost creation."""
    ghost = Ghost(GhostType.BLINKY, 0, 0)
    assert ghost.x == 0
    assert ghost.y == 0
    assert ghost.spawn_x == 0
    assert ghost.spawn_y == 0

def test_ghost_edible():
    """Test ghost becoming edible."""
    ghost = Ghost(GhostType.BLINKY, 0, 0)
    assert not ghost.is_edible
    ghost.become_edible(10.0)
    assert ghost.is_edible

def test_pellet_creation():
    """Test Pellet creation."""
    pellet = Pellet(5, 5, is_super=False)
    assert pellet.x == 5
    assert pellet.y == 5
    assert pellet.points == 10
    assert not pellet.is_eaten

def test_pellet_eat():
    """Test eating pellet."""
    pellet = Pellet(5, 5, is_super=True)
    points = pellet.eat()
    assert points == 50
    assert pellet.is_eaten
```

### ✅ Checkpoint Phase 2
```bash
make lint       # ✅ 0 erreurs
make test       # ✅ Tous les tests passent
```

---

## 🧠 PHASE 3: IA & Maze Integration (Durée: 4-5 jours)

### Objectifs
- [ ] Intégrer A-Maze-ing
- [ ] Générer labyrinthe
- [ ] Pathfinding BFS
- [ ] IA fantômes (chase/flee)

### Dépendances
- Phase 2 ✅
- A-Maze-ing package installé

### Tâches

#### 3.1 Maze

**`src/maze/tile.py`**
```python
"""Tile types for maze."""

from enum import Enum

class TileType(Enum):
    """Tile type in maze."""
    WALL = 0
    CORRIDOR = 1
    SPAWN_POINT = 2
```

**`src/maze/maze.py`**
```python
"""Maze representation."""

from typing import List, Tuple, Set
from src.maze.tile import TileType
from src.utils.types import Position

class Maze:
    """Maze representation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[TileType]] = [
            [TileType.CORRIDOR for _ in range(width)]
            for _ in range(height)
        ]
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.tiles[y][x] != TileType.WALL
    
    def get_neighbors(self, x: int, y: int) -> List[Position]:
        """Get walkable neighbors."""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def get_center(self) -> Position:
        """Get center position."""
        return (self.width // 2, self.height // 2)
    
    def get_corners(self) -> List[Position]:
        """Get corner positions."""
        return [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1)
        ]
```

#### 3.2 Maze Generator

**`src/maze/maze_generator.py`**
```python
"""Maze generation using A-Maze-ing."""

from typing import List
from src.maze.maze import Maze
from src.entities.ghost import Ghost, GhostType
from src.entities.pellet import Pellet
from src.utils.logger import setup_logger
from src.utils.exceptions import MazeGenerationError

logger = setup_logger(__name__)

try:
    from AMazing import maze_generator as amz
except ImportError:
    amz = None

class MazeGenerator:
    """Generate mazes using A-Maze-ing package."""
    
    @staticmethod
    def generate(width: int, height: int, seed: int) -> Maze:
        """Generate maze."""
        if amz is None:
            logger.warning("A-Maze-ing not available, using fallback")
            return MazeGenerator._create_fallback_maze(width, height)
        
        try:
            # Generate maze with A-Maze-ing
            maze_data = amz.generate(
                width=width,
                height=height,
                seed=seed,
                PERFECT=False  # Enable corridors for Pac-Man
            )
            
            maze = Maze(width, height)
            # Convert maze_data to our representation
            # (depends on A-Maze-ing API)
            return maze
        except Exception as e:
            logger.error(f"Maze generation failed: {e}")
            return MazeGenerator._create_fallback_maze(width, height)
    
    @staticmethod
    def _create_fallback_maze(width: int, height: int) -> Maze:
        """Create simple fallback maze."""
        maze = Maze(width, height)
        # Create simple square maze with borders
        for x in range(width):
            maze.tiles[0][x] = maze.tiles[height-1][x] = TileType.WALL
        for y in range(height):
            maze.tiles[y][0] = maze.tiles[y][width-1] = TileType.WALL
        return maze
    
    @staticmethod
    def place_pellets(maze: Maze, config: dict) -> List[Pellet]:
        """Place pellets in maze."""
        pellets: List[Pellet] = []
        corners = maze.get_corners()
        
        # Super-pellets at corners
        for x, y in corners:
            if maze.is_walkable(x, y):
                pellets.append(Pellet(x, y, is_super=True))
        
        # Regular pellets in corridors
        # (simplified: add to some corridors)
        count = 0
        max_pellets = config.get("pacgum_count", 42)
        for y in range(maze.height):
            for x in range(maze.width):
                if maze.is_walkable(x, y) and count < max_pellets:
                    # Skip corners and spawn
                    if (x, y) not in corners and (x, y) != maze.get_center():
                        pellets.append(Pellet(x, y, is_super=False))
                        count += 1
        
        return pellets
    
    @staticmethod
    def place_ghosts(maze: Maze) -> List[Ghost]:
        """Place ghosts at corners."""
        ghosts: List[Ghost] = []
        corners = maze.get_corners()
        ghost_types = [GhostType.BLINKY, GhostType.PINKY, GhostType.INKY, GhostType.CLYDE]
        
        for i, (x, y) in enumerate(corners):
            if i < len(ghost_types) and maze.is_walkable(x, y):
                ghosts.append(Ghost(ghost_types[i], x, y))
        
        return ghosts
```

#### 3.3 Pathfinding

**`src/entities/ai/pathfinding.py`**
```python
"""Pathfinding algorithms."""

from typing import List, Optional, Tuple
from collections import deque
from src.maze.maze import Maze
from src.utils.types import Position

class Pathfinder:
    """Pathfinding using BFS."""
    
    @staticmethod
    def bfs(
        maze: Maze,
        start: Position,
        goal: Position
    ) -> Optional[Position]:
        """Find next step toward goal using BFS."""
        if start == goal:
            return None
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            for nx, ny in maze.get_neighbors(x, y):
                if (nx, ny) == goal:
                    if len(path) > 1:
                        return path[1]
                    return (nx, ny)
                
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        
        return None
    
    @staticmethod
    def manhattan_distance(p1: Position, p2: Position) -> int:
        """Calculate Manhattan distance."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
```

#### 3.4 Ghost AI

**`src/entities/ai/ghost_behavior.py`**
```python
"""Ghost AI behavior."""

from random import choice, random
from src.entities.ai.pathfinding import Pathfinder
from src.entities.pacman import Pacman
from src.entities.ghost import Ghost, GhostType
from src.maze.maze import Maze
from src.utils.types import Position

class GhostAI:
    """Ghost AI logic."""
    
    @staticmethod
    def calculate_next_move(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze
    ) -> Optional[Position]:
        """Calculate next move for ghost."""
        if ghost.is_edible:
            return GhostAI._flee_behavior(ghost, pacman, maze)
        else:
            return GhostAI._chase_behavior(ghost, pacman, maze)
    
    @staticmethod
    def _chase_behavior(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze
    ) -> Optional[Position]:
        """Chase Pacman."""
        if ghost.ghost_type == GhostType.BLINKY:
            # Direct chase
            return Pathfinder.bfs(maze, ghost.position, pacman.position)
        elif ghost.ghost_type == GhostType.PINKY:
            # Ambush: target ahead of Pacman
            target_x = pacman.x + (4 if pacman.direction == Direction.RIGHT else 0)
            target_y = pacman.y + (4 if pacman.direction == Direction.DOWN else 0)
            return Pathfinder.bfs(maze, ghost.position, (target_x, target_y))
        elif ghost.ghost_type == GhostType.INKY:
            # Random between chase and escape
            if random() > 0.5:
                return Pathfinder.bfs(maze, ghost.position, pacman.position)
            else:
                return GhostAI._random_move(ghost, maze)
        else:  # CLYDE
            # Scatter if close
            distance = Pathfinder.manhattan_distance(ghost.position, pacman.position)
            if distance < 8:
                return GhostAI._random_move(ghost, maze)
            else:
                return Pathfinder.bfs(maze, ghost.position, pacman.position)
    
    @staticmethod
    def _flee_behavior(
        ghost: Ghost,
        pacman: Pacman,
        maze: Maze
    ) -> Optional[Position]:
        """Flee from Pacman."""
        # Move away from Pacman
        neighbors = maze.get_neighbors(ghost.x, ghost.y)
        if not neighbors:
            return None
        
        # Choose neighbor farthest from Pacman
        farthest = max(
            neighbors,
            key=lambda p: Pathfinder.manhattan_distance(p, pacman.position)
        )
        return farthest
    
    @staticmethod
    def _random_move(ghost: Ghost, maze: Maze) -> Optional[Position]:
        """Random move."""
        neighbors = maze.get_neighbors(ghost.x, ghost.y)
        return choice(neighbors) if neighbors else None
```

#### 3.5 Tests

**`tests/test_maze.py`**
```python
"""Test maze functionality."""

from src.maze.maze import Maze
from src.maze.tile import TileType

def test_maze_creation():
    """Test maze creation."""
    maze = Maze(21, 21)
    assert maze.width == 21
    assert maze.height == 21

def test_maze_walkability():
    """Test walkability check."""
    maze = Maze(10, 10)
    assert maze.is_walkable(5, 5)
    maze.tiles[5][5] = TileType.WALL
    assert not maze.is_walkable(5, 5)

def test_maze_neighbors():
    """Test getting neighbors."""
    maze = Maze(10, 10)
    neighbors = maze.get_neighbors(5, 5)
    assert len(neighbors) == 4
```

### ✅ Checkpoint Phase 3
```bash
make lint
make test
# Labyrinthe généré et navigable
```

---

## 🎨 PHASE 4: UI & Input (Durée: 3-4 jours)

### Objectifs
- [ ] Créer Renderer (wrapper pygame)
- [ ] Système de scènes
- [ ] Gestion des entrées
- [ ] Menus basiques

### Dépendances
- Phase 3 ✅

### Tâches

#### 4.1 Renderer

**`src/ui/colors.py`**
```python
"""Color definitions."""

from src.utils.constants import Color as ColorEnum

COLORS = {
    ColorEnum.BLACK: (0, 0, 0),
    ColorEnum.WHITE: (255, 255, 255),
    # ... etc
}
```

**`src/ui/renderer.py`**
```python
"""Renderer wrapper for pygame."""

from typing import Tuple, Optional
import pygame
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Renderer:
    """Renderer using pygame."""
    
    def __init__(self, width: int, height: int, title: str = "Pac-Man"):
        """Initialize renderer."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.width = width
        self.height = height
    
    def clear(self, color: Tuple[int, int, int]) -> None:
        """Clear screen."""
        self.screen.fill(color)
    
    def present(self) -> None:
        """Present frame."""
        pygame.display.update()
    
    def close(self) -> None:
        """Close renderer."""
        pygame.quit()
```

#### 4.2 Scene System

**`src/ui/scenes/scene.py`**
```python
"""Base scene class."""

from abc import ABC, abstractmethod
from src.ui.renderer import Renderer

class Scene(ABC):
    """Base class for all scenes."""
    
    @abstractmethod
    def on_enter(self) -> None:
        """Called when scene becomes active."""
        pass
    
    @abstractmethod
    def on_exit(self) -> None:
        """Called when scene becomes inactive."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update scene."""
        pass
    
    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        """Render scene."""
        pass
    
    @abstractmethod
    def handle_input(self, key: int) -> None:
        """Handle input."""
        pass
```

**`src/ui/scenes/main_menu.py`**
```python
"""Main menu scene."""

from src.ui.scenes.scene import Scene
from src.ui.renderer import Renderer

class MainMenuScene(Scene):
    """Main menu."""
    
    def __init__(self):
        self.options = ["Start Game", "Highscores", "Instructions", "Exit"]
        self.selected = 0
    
    def on_enter(self) -> None:
        """Enter menu."""
        pass
    
    def on_exit(self) -> None:
        """Exit menu."""
        pass
    
    def update(self, delta_time: float) -> None:
        """Update menu."""
        pass
    
    def render(self, renderer: Renderer) -> None:
        """Render menu."""
        renderer.clear((0, 0, 0))
        # Draw menu options
    
    def handle_input(self, key: int) -> None:
        """Handle input."""
        pass
```

#### 4.3 Input Handler

**`src/input/key_bindings.py`**
```python
"""Key bindings."""

from enum import Enum

class Action(Enum):
    """Game actions."""
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    PAUSE = 4
    SELECT = 5
    BACK = 6
    CHEAT = 7

# Key mapping
KEY_MAP = {
    # Arrow keys
    65362: Action.MOVE_UP,      # Up
    65364: Action.MOVE_DOWN,    # Down
    65361: Action.MOVE_LEFT,    # Left
    65363: Action.MOVE_RIGHT,   # Right
    # WASD
    ord('w'): Action.MOVE_UP,
    ord('a'): Action.MOVE_LEFT,
    ord('s'): Action.MOVE_DOWN,
    ord('d'): Action.MOVE_RIGHT,
    # Special
    ord('p'): Action.PAUSE,
    ord('\r'): Action.SELECT,
    65307: Action.BACK,         # ESC
}
```

**`src/input/input_handler.py`**
```python
"""Input handling."""

from src.input.key_bindings import Action, KEY_MAP
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class InputHandler:
    """Handle user input."""
    
    @staticmethod
    def poll_events() -> list:
        """Poll input events."""
        # Implementation depends on renderer library
        return []
    
    @staticmethod
    def key_to_action(key: int) -> Optional[Action]:
        """Convert key to action."""
        return KEY_MAP.get(key)
```

### ✅ Checkpoint Phase 4
```bash
make lint
make test
# Menu s'affiche, peut naviguer
```

---

## 🎯 PHASE 5: Game Loop & Integration (Durée: 4-5 jours)

### Objectifs
- [ ] Boucle de jeu principale
- [ ] Intégration de tous les modules
- [ ] Logic de victoire/défaite
- [ ] Transitions entre scenes

### Dépendances
- Phase 4 ✅

### Tâches

#### 5.1 Game Loop

**`src/game/game_loop.py`**
```python
"""Main game loop."""

import time
from src.utils.logger import setup_logger
from src.utils.constants import FPS, FRAME_TIME

logger = setup_logger(__name__)

class GameLoop:
    """Main game loop."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.running = False
        self.clock = time.time()
    
    def run(self) -> None:
        """Run game loop."""
        self.running = True
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Cap delta time
            if delta_time > FRAME_TIME * 2:
                delta_time = FRAME_TIME
            
            # Update
            self.game_manager.update(delta_time)
            
            # Render
            self.game_manager.render()
            
            # Input
            self.game_manager.handle_input()
            
            # Frame timing
            elapsed = time.time() - current_time
            sleep_time = max(0, FRAME_TIME - elapsed)
            time.sleep(sleep_time)
```

#### 5.2 Game Manager

**`src/game/game_manager.py`**
```python
"""Main game manager."""

from typing import Dict
from src.config.config_loader import ConfigLoader
from src.config.config_validator import ConfigValidator
from src.game.game_state import GameState
from src.game.level_manager import LevelManager
from src.ui.ui_manager import UIManager
from src.highscore.highscore_manager import HighscoreManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class GameManager:
    """Main game manager."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.state = GameState()
        self.level_manager = LevelManager(config)
        self.ui_manager = UIManager()
        self.highscore_manager = HighscoreManager(
            config.get("highscore_filename", ".data/highscores.json")
        )
    
    def start_game(self) -> None:
        """Start new game."""
        self.state.reset()
        self.level_manager.load_level(1)
        self.ui_manager.switch_scene("game")
    
    def update(self, delta_time: float) -> None:
        """Update game state."""
        self.ui_manager.update(delta_time)
    
    def render(self) -> None:
        """Render game."""
        self.ui_manager.render()
    
    def handle_input(self) -> None:
        """Handle input."""
        self.ui_manager.handle_input()
```

### ✅ Checkpoint Phase 5
```bash
make run
# Jeu tourne, peut jouer un niveau
```

---

## 🧪 PHASE 6: Polish & Testing (Durée: 3-4 jours)

### Objectifs
- [ ] Système de highscores complet
- [ ] Mode triche
- [ ] Gestion complète des erreurs
- [ ] Tests complets
- [ ] Documentation

### Tâches

#### 6.1 Highscores

**`src/highscore/highscore_manager.py`** (complet)
```python
"""Highscore management."""

import json
from pathlib import Path
from typing import List
from dataclasses import dataclass, asdict
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class ScoreEntry:
    """A highscore entry."""
    name: str
    score: int
    timestamp: int

class HighscoreManager:
    """Manage highscores."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.scores: List[ScoreEntry] = []
        self.load()
    
    def load(self) -> None:
        """Load highscores from file."""
        if not self.filepath.exists():
            self.scores = []
            return
        
        try:
            with open(self.filepath) as f:
                data = json.load(f)
                self.scores = [ScoreEntry(**entry) for entry in data]
        except Exception as e:
            logger.error(f"Failed to load highscores: {e}")
            self.scores = []
    
    def save(self) -> None:
        """Save highscores to file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump([asdict(s) for s in self.scores], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save highscores: {e}")
    
    def add_score(self, name: str, score: int) -> bool:
        """Add score if in top 10."""
        # Validate name
        if len(name) > 10 or not all(c.isalnum() or c.isspace() for c in name):
            return False
        
        entry = ScoreEntry(name, score, int(time.time()))
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        self.scores = self.scores[:10]  # Keep top 10
        self.save()
        return True
```

#### 6.2 Mode Triche

**`src/cheat/cheat_mode.py`**
```python
"""Cheat mode."""

from src.game.game_state import GameState
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CheatMode:
    """Cheat commands."""
    
    @staticmethod
    def toggle_invincibility(state: GameState) -> None:
        """Toggle invincibility."""
        # Implementation
        pass
    
    @staticmethod
    def skip_level(state: GameState) -> None:
        """Skip to next level."""
        state.next_level()
```

#### 6.3 Tests complets

Ajouter tests pour:
- [ ] Collision detection
- [ ] Scoring
- [ ] Ghost AI
- [ ] Level progression
- [ ] Highscores persistence

### ✅ Checkpoint Phase 6
```bash
make test       # ✅ 100% tests pass
make lint       # ✅ 0 erreurs
```

---

## 📦 PHASE 7: Packaging & Deployment (Durée: 2-3 jours)

### Objectifs
- [ ] Créer exécutable standalone
- [ ] Publier sur Itch.io/Steam
- [ ] README complet
- [ ] Documentation finale

### Tâches

#### 7.1 Packaging

**`setup.py` ou PyInstaller**
```python
# PyInstaller
pyinstaller --onefile --windowed pac-man.py
```

#### 7.2 Déploiement Itch.io

1. Créer compte Itch.io
2. Créer nouveau projet
3. Upload build
4. Test depuis plateforme

#### 7.3 Documentation finale

- [ ] Remplir [doc/ARCHITECTURE.md](../../doc/ARCHITECTURE.md)
- [ ] Remplir [doc/DESIGN.md](../../doc/DESIGN.md)
- [ ] Remplir [doc/API.md](../../doc/API.md)
- [ ] Remplir [README.md](../../README.md) complet
- [ ] Remplir [doc/PROJECT_MANAGEMENT/](../../doc/PROJECT_MANAGEMENT/)

### ✅ Final Checkpoint
```bash
./pac-man  # Exécutable standalone fonctionne
git push
# Itch.io playable
```

---

## 📊 Timeline recommandée

| Phase | Durée | Cumul | Status |
|-------|-------|-------|--------|
| **0** | 2-3j | 2-3j | Infrastructure ✓ |
| **1** | 2-3j | 4-6j | Config + State ✓ |
| **2** | 3-4j | 7-10j | Entities ✓ |
| **3** | 4-5j | 11-15j | IA + Maze ⏳ |
| **4** | 3-4j | 14-19j | UI ⏳ |
| **5** | 4-5j | 18-24j | Game Loop ⏳ |
| **6** | 3-4j | 21-28j | Polish ⏳ |
| **7** | 2-3j | 23-31j | Deploy ⏳ |

**Total estimé**: 23-31 jours (3-4 semaines + buffer)

---

## 🎯 Stratégie de développement

### Approche recommandée

1. **Commit régulièrement**: Chaque sous-tâche terminée
2. **Test en continu**: Linter + tests à chaque phase
3. **Code review**: Relire le code avant commit
4. **Documentation**: Documenter en même temps que coder

### Commits types

```
Phase 0:
- chore: setup project structure
- feat: add logging utilities
- feat: add constants and types

Phase 1:
- feat: add config loader with comments
- feat: add config validator
- feat: add game state singleton
- test: add config and state tests

Phase 2:
- feat: add entity base class
- feat: add pacman entity
- feat: add ghost entity
- feat: add pellet entity
- test: add entity tests

... etc
```

### Branches recommandées

```
main/master        # Version stable
└── dev            # Développement
    ├── phase/0    # Infrastructure
    ├── phase/1    # Config
    ├── phase/2    # Entities
    ├── phase/3    # IA
    ├── phase/4    # UI
    ├── phase/5    # Game Loop
    └── phase/6    # Polish
```

---

## ⚠️ Pièges à éviter

### 1. Commencer par l'UI
**❌ MAUVAIS**: Implémenter l'interface graphique en premier
**✅ BON**: Commencer par la logique métier, UI en dernier

### 2. Ignorer les tests
**❌ MAUVAIS**: Coder sans tests, tester à la fin
**✅ BON**: Tests + code simultanément (TDD)

### 3. Dépendances circulaires
**❌ MAUVAIS**: A dépend de B, B dépend de A
**✅ BON**: Hiérarchie claire, pas de cycles

### 4. Oublier la gestion d'erreurs
**❌ MAUVAIS**: Laisser des `try-except` génériques
**✅ BON**: Exceptions spécifiques, logs clairs

### 5. Configuration rigide
**❌ MAUVAIS**: Valeurs hardcodées en dur
**✅ BON**: Configuration externe, defaults robustes

---

## ✅ Checklist avant chaque commit

- [ ] Code compiles (`make lint`)
- [ ] Tests passent (`make test`)
- [ ] Type hints complètes (`mypy`)
- [ ] Pas de `print()` (utiliser logger)
- [ ] Docstrings à jour
- [ ] Commit message clair
- [ ] Une seule feature par commit

---

## 🔗 Références

- [ARCHITECTURE.md](../../doc/ARCHITECTURE.md)
- [ACCEPTANCE_TEST_PLAN.md](../../doc/ACCEPTANCE_TEST_PLAN.md)
- [.copilot-instructions.md](../../.copilot-instructions.md)

---

**Dernière mise à jour**: 1 Mai 2026
**Statut**: Ready for development

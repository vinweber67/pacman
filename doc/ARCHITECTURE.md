# Architecture de Conception - Pac-Man

## 1. Vue d'ensemble

Le projet Pac-Man est structuré selon une architecture modulaire basée sur la séparation des préoccupations. L'application suit le pattern Model-View-Controller adapté aux jeux, avec des couches distinctes pour:

- **Gestion de l'état du jeu** (Model)
- **Rendu graphique** (View)
- **Logique métier et contrôle** (Controller)
- **Utilitaires et services** (Services)

```
┌─────────────────────────────────────────────────┐
│              Application Principale               │
│           (pac-man.py - Point d'entrée)          │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐         ┌────▼──────┐
   │ Config   │         │ Game      │
   │ Manager  │         │ Manager   │
   └────┬─────┘         └────┬──────┘
        │                    │
        │         ┌──────────┼──────────┐
        │         │          │          │
   ┌────▼──┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐
   │ Game  │  │Level │  │ UI   │  │ High-│
   │State  │  │Mgmt  │  │ Mgmt │  │score │
   └────┬──┘  └──┬───┘  └──┬───┘  └──┬───┘
        │        │         │         │
        ├────────┴─────────┼─────────┤
        │                  │         │
   ┌────▼──────┐     ┌────▼─────┐  │
   │ Game Loop │     │ Renderer  │  │
   │ (Events)  │     │ (MLX)     │  │
   └───────────┘     └───────────┘  │
                                    │
                    ┌───────────────┘
                    │
            ┌───────▼────────┐
            │ Highscores     │
            │ Persistence    │
            └────────────────┘
```

---

## 2. Structure des répertoires

```
Pacman/
├── pac-man.py                 # Point d'entrée principal
├── config.json                # Configuration du jeu
├── requirements.txt           # Dépendances Python
├── Makefile                   # Automatisation
├── README.md                  # Documentation
├── ARCHITECTURE.md            # Cette architecture
├── .gitignore                 # Fichiers à ignorer
│
├── src/                       # Code source principal
│   ├── __init__.py
│   ├── config/                # Gestion de la configuration
│   │   ├── __init__.py
│   │   ├── config_loader.py   # Chargement JSON avec commentaires
│   │   └── config_validator.py # Validation et defaults
│   │
│   ├── game/                  # Logique principale du jeu
│   │   ├── __init__.py
│   │   ├── game_manager.py    # Orchestration globale
│   │   ├── game_state.py      # État du jeu (données persistantes)
│   │   ├── level_manager.py   # Gestion des niveaux
│   │   └── game_loop.py       # Boucle de jeu principale
│   │
│   ├── entities/              # Entités du jeu
│   │   ├── __init__.py
│   │   ├── entity.py          # Classe de base
│   │   ├── pacman.py          # Joueur
│   │   ├── ghost.py           # Fantômes (Blinky, Pinky, Inky, Clyde)
│   │   ├── pellet.py          # Pacgums et Super-pacgums
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── ghost_behavior.py    # Comportement IA des fantômes
│   │       └── pathfinding.py       # Algorithmes de recherche de chemin
│   │
│   ├── maze/                  # Gestion du labyrinthe
│   │   ├── __init__.py
│   │   ├── maze_generator.py  # Intégration A-Maze-ing
│   │   ├── maze.py            # Représentation du labyrinthe
│   │   └── tile.py            # Types de tuiles (mur, corridor, etc.)
│   │
│   ├── ui/                    # Interface utilisateur
│   │   ├── __init__.py
│   │   ├── ui_manager.py      # Orchestration de l'UI
│   │   ├── scenes/
│   │   │   ├── __init__.py
│   │   │   ├── scene.py       # Classe de base pour les scènes
│   │   │   ├── main_menu.py   # Menu principal
│   │   │   ├── game_scene.py  # Vue du jeu
│   │   │   ├── pause_menu.py  # Menu de pause
│   │   │   ├── game_over.py   # Écran de fin
│   │   │   ├── highscores.py  # Affichage des highscores
│   │   │   └── instructions.py # Instructions
│   │   ├── renderer.py        # Rendu graphique (MLX wrapper)
│   │   ├── assets.py          # Gestion des ressources graphiques
│   │   └── colors.py          # Palette de couleurs
│   │
│   ├── input/                 # Gestion des entrées
│   │   ├── __init__.py
│   │   ├── input_handler.py   # Capture et traitement des entrées
│   │   └── key_bindings.py    # Mapping des touches
│   │
│   ├── highscore/             # Système de highscores
│   │   ├── __init__.py
│   │   ├── highscore_manager.py # Gestion persistante
│   │   ├── score_entry.py      # Modèle d'une entrée de score
│   │   └── storage.py          # Abstraction de stockage (JSON)
│   │
│   ├── cheat/                 # Mode triche
│   │   ├── __init__.py
│   │   └── cheat_mode.py      # Commandes de triche
│   │
│   └── utils/                 # Utilitaires
│       ├── __init__.py
│       ├── logger.py          # Logging
│       ├── constants.py       # Constantes du jeu
│       ├── exceptions.py      # Exceptions personnalisées
│       └── types.py           # Aliases de types
│
├── tests/                     # Tests unitaires
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_pacman.py
│   ├── test_ghosts.py
│   ├── test_maze.py
│   ├── test_highscore.py
│   └── test_game_logic.py
│
├── docs/                      # Documentation supplémentaire
│   ├── game_design.md
│   └── api.md
│
├── build/                     # Fichiers générés (ignorés)
├── dist/                      # Distribution empaquetée
└── .data/                     # Données de jeu (highscores, etc.)
    └── highscores.json
```

---

## 3. Modules principaux et responsabilités

### 3.1 Configuration (`src/config/`)

**Responsabilité**: Charger, valider et fournir la configuration du jeu.

```python
# config_loader.py
class ConfigLoader:
    """
    Charge les fichiers JSON avec support des commentaires.
    - Supp porte les commentaires # 
    - Gère les erreurs de fichier
    - Retourne un dict validé
    """
    def load(path: str) -> dict
    def remove_comments(content: str) -> str
```

```python
# config_validator.py
class ConfigValidator:
    """
    Valide la configuration et applique les defaults.
    - Vérifie les clés obligatoires
    - Clamp les valeurs invalides
    - Log les problèmes sans crasher
    """
    def validate(config: dict) -> dict
    def apply_defaults(config: dict) -> dict
```

**Configuration par défaut recommandée**:
```json
{
  "highscore_filename": ".data/highscores.json",
  "levels": [
    {"width": 21, "height": 21, "seed": 42, "max_time": 90}
  ],
  "lives": 3,
  "pacgum_count": 42,
  "points_per_pacgum": 10,
  "points_per_super_pacgum": 50,
  "points_per_ghost": 200,
  "ghost_respawn_time": 10,
  "super_pacgum_duration": 10
}
```

---

### 3.2 État du jeu (`src/game/`)

**Responsabilité**: Maintenir l'état global du jeu.

```python
# game_state.py
class GameState:
    """
    Singleton contenant tout l'état du jeu.
    """
    score: int
    lives: int
    current_level: int
    level_time_remaining: int
    is_paused: bool
    is_game_over: bool
    is_victory: bool
    pacman: Pacman
    ghosts: List[Ghost]
    maze: Maze
    pellets: List[Pellet]
    
    def reset_level(): void
    def next_level(): void
    def lose_life(): void
    def add_score(points: int): void
```

---

### 3.3 Entités (`src/entities/`)

**Responsabilité**: Représenter et gérer les acteurs du jeu.

#### 3.3.1 Entity (Classe de base)

```python
# entity.py
class Entity:
    """Classe de base pour tous les acteurs du jeu."""
    position: Tuple[int, int]  # (x, y) en tuiles
    velocity: Tuple[int, int]  # Direction du mouvement
    
    def update(delta_time: float): void
    def render(renderer: Renderer): void
    def move(direction: Direction): void
    def can_move_to(position: Tuple[int, int]) -> bool
```

#### 3.3.2 Pacman

```python
# pacman.py
class Pacman(Entity):
    """
    Le joueur.
    - Contrôlé par l'utilisateur
    - Mange les pellets
    - Fuit les fantômes
    """
    is_invincible: bool
    eating_animation_frame: int
    
    def eat_pellet(pellet: Pellet): void
    def update_direction(input_direction: Direction): void
    def lose_life(): void
```

#### 3.3.3 Ghost (Fantôme)

```python
# ghost.py
class Ghost(Entity):
    """
    Un fantôme autonome.
    Comportements: Chase (normal), Flee (comestible), Eaten (respawn)
    """
    name: str  # "Blinky", "Pinky", "Inky", "Clyde"
    color: Color
    is_edible: bool
    eaten_timer: float
    behavior: GhostBehavior
    
    def update(delta_time: float): void
    def chase_pacman(pacman: Pacman): void
    def flee_from_pacman(pacman: Pacman): void
    def respawn(): void
    def become_edible(): void
```

#### 3.3.4 Pellet

```python
# pellet.py
class Pellet(Entity):
    """
    Un pellet (pacgum ou super-pacgum).
    """
    is_super: bool  # True = power-up
    points: int
    
    def is_eaten() -> bool
    def mark_eaten(): void
```

---

### 3.4 IA des Fantômes (`src/entities/ai/`)

**Responsabilité**: Implémenter les comportements autonomes.

```python
# ghost_behavior.py
class GhostBehavior(Enum):
    CHASE = 0      # Chasse Pac-Man
    FLEE = 1       # Fuit Pac-Man
    SCATTER = 2    # Dispersion (se replie)
    EATEN = 3      # Respawn

class GhostAI:
    """
    Moteur IA pour les fantômes.
    - BFS/DFS pour pathfinding
    - Comportement adaptatif
    - Random pour l'imprévisibilité
    """
    def calculate_next_move(
        ghost: Ghost, 
        pacman: Pacman, 
        maze: Maze
    ) -> Direction:
        """Retourne la prochaine direction à prendre."""
        pass
```

---

### 3.5 Labyrinthe (`src/maze/`)

**Responsabilité**: Gérer la génération et la structure du labyrinthe.

```python
# maze_generator.py
class MazeGenerator:
    """
    Wrapper pour le package A-Maze-ing.
    - Génère des labyrinthes avec PERFECT=False
    - Gère les erreurs de génération
    - Place les entités initiales
    """
    def generate(width: int, height: int, seed: int) -> Maze:
        pass
    def place_pellets(maze: Maze, config: dict): void
    def place_ghosts(maze: Maze) -> List[Ghost]: ...
    def get_pacman_spawn() -> Tuple[int, int]: ...

# maze.py
class Maze:
    """
    Représentation du labyrinthe.
    """
    width: int
    height: int
    tiles: List[List[Tile]]  # 2D grid
    
    def is_walkable(position: Tuple[int, int]) -> bool
    def get_neighbors(position: Tuple[int, int]) -> List[Tuple[int, int]]
    def get_corridor_center() -> Tuple[int, int]
    def get_corner_positions() -> List[Tuple[int, int]]

# tile.py
class TileType(Enum):
    WALL = 0
    CORRIDOR = 1
    SPAWN_POINT = 2
```

---

### 3.6 Logique de jeu (`src/game/`)

```python
# game_manager.py
class GameManager:
    """
    Orchestration globale du jeu.
    - Initialise les niveaux
    - Gère le passage entre états
    - Coordonne collision detection, scoring, etc.
    """
    config: Config
    game_state: GameState
    level_manager: LevelManager
    ui_manager: UIManager
    highscore_manager: HighscoreManager
    
    def start_game(): void
    def update(delta_time: float): void
    def handle_input(input: InputEvent): void
    def check_collisions(): void
    def check_win_condition(): bool
    def end_game(is_victory: bool): void

# level_manager.py
class LevelManager:
    """
    Gère les niveaux individuels.
    """
    def load_level(level_num: int): void
    def unload_level(): void
    def tick_timer(delta_time: float): void
    def is_level_complete() -> bool

# game_loop.py
class GameLoop:
    """
    Boucle de jeu principale (60 FPS).
    """
    def run(): void  # Bloquant jusqu'à arrêt
```

---

### 3.7 Interface Utilisateur (`src/ui/`)

**Responsabilité**: Rendu graphique et gestion des scènes.

#### Architecture des scènes

```python
# scenes/scene.py
class Scene(ABC):
    """Classe de base pour toutes les scènes."""
    
    @abstractmethod
    def on_enter(): void
    
    @abstractmethod
    def on_exit(): void
    
    @abstractmethod
    def update(delta_time: float): void
    
    @abstractmethod
    def render(renderer: Renderer): void
    
    @abstractmethod
    def handle_input(event: InputEvent): void

# scenes/main_menu.py
class MainMenuScene(Scene):
    """Menu principal avec options."""
    options: List[str]  # ["Start", "Highscores", "Instructions", "Exit"]
    selected_index: int
    
    def handle_input(event: InputEvent): void
    def render(renderer: Renderer): void

# scenes/game_scene.py
class GameScene(Scene):
    """Vue de jeu active."""
    def render(renderer: Renderer): void  # Dessine maze, entities, HUD

# scenes/pause_menu.py
class PauseMenuScene(Scene):
    """Menu de pause."""
    def on_enter(): void  # Pause le GameState

# scenes/game_over.py
class GameOverScene(Scene):
    """Écran de fin (victoire ou défaite)."""
    def render(renderer: Renderer): void
    def get_player_name() -> str  # Entrée de texte

# ui_manager.py
class UIManager:
    """
    Gestionnaire central des scènes.
    """
    current_scene: Scene
    scenes: Dict[str, Scene]
    
    def switch_scene(scene_name: str): void
    def render(renderer: Renderer): void
    def handle_input(event: InputEvent): void

# renderer.py
class Renderer:
    """
    Wrapper pour MLX (ou autre librairie graphique).
    Responsable du rendu bas niveau.
    """
    def draw_rectangle(x, y, w, h, color): void
    def draw_text(x, y, text, color): void
    def draw_tile(tile: Tile, x, y): void
    def present(): void  # Affiche le frame
    def clear(color: Color): void
```

---

### 3.8 Gestion des entrées (`src/input/`)

```python
# input_handler.py
class InputHandler:
    """
    Capture et interprète les entrées clavier/souris.
    """
    key_bindings: Dict[Key, Action]
    
    def handle_event(event: Event) -> Optional[InputEvent]
    def poll_events() -> List[InputEvent]

# key_bindings.py
class Action(Enum):
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    PAUSE = 4
    CHEAT = 5
    SELECT = 6
    BACK = 7

# Support WASD + Arrow keys
KEY_MAP = {
    ARROW_UP: Action.MOVE_UP,
    'w': Action.MOVE_UP,
    ARROW_DOWN: Action.MOVE_DOWN,
    's': Action.MOVE_DOWN,
    # etc.
}
```

---

### 3.9 Highscores (`src/highscore/`)

```python
# highscore_manager.py
class HighscoreManager:
    """
    Gère la persistence des highscores.
    """
    scores: List[ScoreEntry]
    filepath: str
    
    def load(): void
    def save(): void
    def add_score(name: str, score: int): bool  # Retourne True si top 10
    def get_top_10() -> List[ScoreEntry]

# score_entry.py
class ScoreEntry:
    """Une entrée de highscore."""
    name: str       # Max 10 chars, alphanumérique + espaces
    score: int      # Non-négatif
    timestamp: int  # Unix timestamp

# storage.py
class ScoreStorage(ABC):
    """Abstraction pour le stockage."""
    @abstractmethod
    def load(path: str) -> List[ScoreEntry]: ...
    
    @abstractmethod
    def save(path: str, scores: List[ScoreEntry]): ...

class JSONScoreStorage(ScoreStorage):
    """Implémentation JSON."""
    def load(path: str) -> List[ScoreEntry]: ...
    def save(path: str, scores: List[ScoreEntry]): ...
```

---

### 3.10 Mode Triche (`src/cheat/`)

```python
# cheat_mode.py
class CheatMode:
    """
    Commandes de triche pour faciliter l'évaluation.
    """
    def toggle_invincibility(game_state: GameState): void
    def skip_level(game_state: GameState): void
    def freeze_ghosts(game_state: GameState): void
    def add_lives(game_state: GameState, count: int): void
    def increase_speed(game_state: GameState, factor: float): void
    def show_all_keys(maze: Maze): void
```

---

## 4. Flux de contrôle

### 4.1 Démarrage de l'application

```
pac-man.py
    │
    ├─► ConfigLoader.load("config.json")
    │       └─► ConfigValidator.validate()
    │
    ├─► GameManager.__init__(config)
    │       ├─► UIManager.__init__()
    │       ├─► HighscoreManager.load()
    │       └─► GameState.__init__()
    │
    └─► GameManager.show_main_menu()
            └─► UIManager.switch_scene("main_menu")
```

### 4.2 Boucle de jeu principale

```
GameLoop.run()
    └─► while not quit:
            │
            ├─► InputHandler.poll_events()
            │       └─► GameManager.handle_input()
            │
            ├─► GameManager.update(delta_time)
            │       ├─► LevelManager.tick_timer()
            │       ├─► Pacman.update()
            │       ├─► Ghost.update() x4
            │       ├─► GameManager.check_collisions()
            │       ├─► GameManager.check_win_condition()
            │       └─► GhostAI.calculate_next_move() x4
            │
            ├─► UIManager.render(Renderer)
            │       └─► CurrentScene.render()
            │
            └─► Renderer.present()
```

### 4.3 Détection de collision

```
GameManager.check_collisions()
    │
    ├─► Pour chaque fantôme:
    │       │
    │       ├─► if ghost.position == pacman.position:
    │       │       if ghost.is_edible:
    │       │           ├─► GameState.add_score(points_per_ghost)
    │       │           ├─► ghost.become_eaten()
    │       │           └─► ghost.respawn_timer = 10s
    │       │       else if !pacman.is_invincible:
    │       │           ├─► GameState.lose_life()
    │       │           └─► pacman.respawn()
    │
    └─► Pour chaque pellet:
            │
            └─► if pellet.position == pacman.position:
                    if pellet.is_super:
                        ├─► GameState.add_score(points_per_super)
                        ├─► for ghost in ghosts:
                        │       ghost.become_edible(duration=10s)
                        └─► pellet.mark_eaten()
                    else:
                        ├─► GameState.add_score(points_per_pacgum)
                        └─► pellet.mark_eaten()
```

---

## 5. Stratégies de design

### 5.1 IA des fantômes

Chaque fantôme a un **comportement adaptatif**:

1. **Mode Chase** (par défaut):
   - **Blinky** (rouge): Poursuite directe via BFS
   - **Pinky** (rose): Ambush (target position + 4 tuiles devant)
   - **Inky** (cyan): Imprévisible (mix entre chasse et random)
   - **Clyde** (orange): Scatter (retourne à son coin) si trop proche

2. **Mode Edible** (après super-pacgum):
   - Fuit Pac-Man (direction opposée)
   - Timer de X secondes avant redevenir normal

3. **Mode Eaten**:
   - Retourne au coin d'origine
   - Respawn au point de départ

### 5.2 Gestion des niveaux

```
Level 1: seed=42 (fixé)
Level 2-10: seed=random

Progression:
├─► Load level
├─► Generate maze
├─► Place pellets
├─► Place ghosts + Pacman
├─► Start timer (90s)
├─► Play until:
│   ├─► All pellets eaten → Next level
│   ├─► Timer reached → Restart level (config)
│   └─► All lives lost → Game Over
└─► Keep score + lives between levels
```

### 5.3 Gestion des erreurs

```python
try:
    # Charger config
    config = ConfigLoader.load(sys.argv[1])
except FileNotFoundError:
    logger.error("Config file not found: use default")
    config = DEFAULT_CONFIG
except JSONDecodeError:
    logger.error("Invalid JSON: using defaults for invalid keys")
    config = merge_with_defaults(partial_config)

# Générer labyrinthe
try:
    maze = MazeGenerator.generate(...)
except Exception as e:
    logger.error(f"Maze generation failed: {e}")
    logger.info("Using fallback maze")
    maze = create_fallback_maze()
```

---

## 6. Dépendances externes

```
mlx42              # Rendu graphique (ou pygame/pyglet)
numpy              # Calculs matriciels
A-Maze-ing        # Génération de labyrinthe (attribué)
pytest             # Tests (dev)
mypy               # Type checking (dev)
flake8             # Linting (dev)
```

---

## 7. Technologies recommandées

| Aspect | Choix |
|--------|-------|
| **Langage** | Python 3.10+ |
| **Graphiques** | MLX42 ou Pygame |c
| **Configuration** | JSON avec parser personnalisé |
| **Persistence** | JSON (highscores) |
| **AI/Pathfinding** | BFS + Random walk |
| **Tests** | pytest + unittest |
| **Type-checking** | mypy |
| **Linting** | flake8 |

---

## 8. Checklist d'implémentation

- [ ] **Phase 1: Infrastructure**
  - [ ] Config loader + validator
  - [ ] Logger + exceptions
  - [ ] Game state + entity base class

- [ ] **Phase 2: Gameplay core**
  - [ ] Maze integration
  - [ ] Pacman + ghost entities
  - [ ] Collision detection + scoring
  - [ ] Ghost AI (basic chase)

- [ ] **Phase 3: UI + Input**
  - [ ] Renderer (MLX wrapper)
  - [ ] Scene system
  - [ ] Main menu + game view
  - [ ] Input handler

- [ ] **Phase 4: Polish**
  - [ ] Highscore system
  - [ ] Cheat mode
  - [ ] Sound (optionnel)
  - [ ] Animations

- [ ] **Phase 5: Packaging + Deployment**
  - [ ] PyInstaller/cx_Freeze setup
  - [ ] Itch.io/Steam build
  - [ ] README complète

---

## 9. Patterns de design utilisés

| Pattern | Utilisation |
|---------|------------|
| **Singleton** | GameState, UIManager |
| **Observer** | Input events, game state changes |
| **Strategy** | GhostBehavior (chase/flee/scatter) |
| **Factory** | Scene creation, entity creation |
| **State Machine** | Game phases (menu → playing → paused → over) |
| **MVC** | GameState (M), Renderer (V), GameManager (C) |
| **Command** | Input handling, cheat mode |
| **Template Method** | Scene base class |

---

## 10. Considérations de performance

- **Maze pathfinding**: Cache les résultats BFS pour réduire recalcul
- **Collision detection**: Spatial hashing optionnel (si > 100 entités)
- **Rendering**: Dirty rectangle optimization (redessiner uniquement changements)
- **FPS Target**: 60 FPS (frame time = 16.67ms)
- **Memory**: Pré-allouer structures de données

---

## 11. Tests recommandés

```python
# test_config.py
def test_config_loader_valid_json()
def test_config_loader_with_comments()
def test_config_validator_defaults()
def test_invalid_config_clamping()

# test_pacman.py
def test_pacman_movement()
def test_pacman_collision_with_pellet()
def test_pacman_collision_with_ghost()

# test_ghosts.py
def test_ghost_chase_behavior()
def test_ghost_flee_behavior()
def test_ghost_edible_timeout()

# test_maze.py
def test_maze_generation_deterministic()
def test_maze_walkability()
def test_pathfinding_bfs()

# test_highscore.py
def test_save_load_scores()
def test_top_10_filtering()
def test_invalid_name_validation()
```

---

## Conclusion

Cette architecture fournit une base solide et modulaire pour construire un Pac-Man complet. Les points clés:

✅ **Séparation des préoccupations**: Chaque module a une responsabilité claire
✅ **Extensibilité**: Facile d'ajouter des features (niveaux, ghosts, modes)
✅ **Testabilité**: Dépendances injectables, logique métier découplée
✅ **Robustesse**: Gestion d'erreurs complète, pas de crash
✅ **Performance**: Optimisations ciblées pour 60 FPS stable

Commencez par les fondations (config, state, entities) avant de construire les couches UI et gameplay.

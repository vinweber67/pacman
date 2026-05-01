# API Overview

## Entry Point
- [pac-man.py](../pac-man.py)
  - `main() -> int`

## Config
- [src/config/config_loader.py](../src/config/config_loader.py)
  - `ConfigLoader.load(filepath: str) -> dict[str, Any]`
- [src/config/config_validator.py](../src/config/config_validator.py)
  - `ConfigValidator.validate(config: dict[str, Any]) -> dict[str, Any]`

## Game
- [src/game/game_manager.py](../src/game/game_manager.py)
  - `run()`, `handle_input(key)`, `update(delta_time)`, `render()`
- [src/game/game_loop.py](../src/game/game_loop.py)
  - `run(max_frames=None)`, `step(delta_time, keys=None)`
- [src/game/level_manager.py](../src/game/level_manager.py)
  - `load_level(level_number)`, `advance_level()`
- [src/game/game_state.py](../src/game/game_state.py)
  - singleton shared state

## Maze
- [src/maze/maze_generator.py](../src/maze/maze_generator.py)
  - `generate(width, height, seed) -> Maze`
- [src/maze/maze.py](../src/maze/maze.py)
  - `is_walkable(x, y)`, `get_neighbors(x, y)`

## Highscores
- [src/highscore/highscore_manager.py](../src/highscore/highscore_manager.py)
  - `add_score(name, score) -> bool`
  - `get_top_10() -> list[ScoreEntry]`

## Cheats
- [src/cheat/cheat_mode.py](../src/cheat/cheat_mode.py)
  - invincibility, freeze, lives, speed, skip level

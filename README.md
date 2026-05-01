*This project has been created as part of the 42 curriculum by [team members].*

## Description
Pac-Man is a modular Python implementation of the arcade game with configurable levels, maze generation through an external assigned package, persistent highscores, cheat mode, and a scene-based UI.

## Instructions
### Requirements
- Python 3.10+
- Linux/macOS with graphical environment

### Install
- `make install`

### Run
- `make run`
- Alternative: `python3 pac-man.py config.json`

### Development commands
- `make lint`
- `make lint-strict`
- `make test`
- `make clean`

## Configuration
Configuration is loaded from a JSON file with comment support (`#` and `//`).
Main keys:
- `highscore_filename`
- `levels` (`width`, `height`, `seed`, `max_time`)
- `lives`
- `pacgum_count`
- `points_per_pacgum`
- `points_per_super_pacgum`
- `points_per_ghost`
- `ghost_respawn_time`
- `super_pacgum_duration`

See [config.json](config.json) for the full default example.

## Highscore
Highscores are persisted in JSON (default `.data/highscores.json`) through [src/highscore/highscore_manager.py](src/highscore/highscore_manager.py).
Rules:
- Top 10 entries only
- Name max 10 chars (alphanumeric + spaces)
- Non-negative scores
- Robust load/save on missing/corrupt files

## Maze Generation
The maze is generated using the assigned external wheel package (`4 Pacman - data.whl`) through the adapter in [src/maze/maze_generator.py](src/maze/maze_generator.py).
The generator is used as-is with `perfect=False`.

## Implementation
Technical highlights:
- Singleton game state
- Scene-driven UI manager
- Tile/grid rendering with pygame
- Config loader + validator with defaults/clamping
- Unit tests for core modules

## General Software Architecture
Main modules:
- [src/config](src/config)
- [src/game](src/game)
- [src/entities](src/entities)
- [src/maze](src/maze)
- [src/ui](src/ui)
- [src/input](src/input)
- [src/highscore](src/highscore)
- [src/cheat](src/cheat)
- [src/utils](src/utils)

Architecture details are documented in [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md).

## Project Management
Project management artifacts are in [doc/PROJECT_MANAGEMENT](doc/PROJECT_MANAGEMENT).

## Resources
- Official requirements: [doc/subject.md](doc/subject.md)
- Architecture: [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md)
- Acceptance checklist: [doc/ACCEPTANCE_TEST_PLAN.md](doc/ACCEPTANCE_TEST_PLAN.md)

AI usage:
- Boilerplate generation
- Refactoring assistance
- Test scaffolding
- Documentation drafting
All generated code was reviewed and tested before integration.

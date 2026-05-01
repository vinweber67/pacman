# Design Decisions

## Renderer choice
The project uses pygame as the current graphical backend for portability and simpler setup in this environment.

## Maze integration strategy
The assigned external wheel is consumed through an adapter (`MazeGenerator`) to keep internal interfaces stable and avoid modifying third-party code.

## State management
A singleton `GameState` is used for simple access from loop, manager, and scenes.

## UI architecture
A scene manager drives transitions between menu/game/pause/highscores/instructions screens.

## Testing strategy
Pytest unit tests cover core modules (config, entities, maze, AI, game loop, highscores, input, UI). Additional shell scripts validate phase milestones.

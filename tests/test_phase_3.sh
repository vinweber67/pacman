#!/bin/bash
# Pac-Man Phase 3 - Test Suite
# Validation script for Maze & AI integration

set +e

echo "================================"
echo "Pac-Man Phase 3 - Test Suite"
echo "================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

test_count=0
pass_count=0
fail_count=0

run_test() {
    test_count=$((test_count + 1))
    local test_name="$1"
    local command="$2"

    echo -e "${BLUE}[TEST $test_count]${NC} $test_name"

    if eval "$command" > /tmp/test_phase_3_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_phase_3_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

echo -e "${YELLOW}=== SECTION 1: Required Files ===${NC}"
echo ""
run_test "src/maze/maze.py exists" "test -f src/maze/maze.py"
run_test "src/maze/tile.py exists" "test -f src/maze/tile.py"
run_test "src/maze/maze_generator.py exists" "test -f src/maze/maze_generator.py"
run_test "src/entities/ai/pathfinding.py exists" "test -f src/entities/ai/pathfinding.py"
run_test "src/entities/ai/ghost_behavior.py exists" "test -f src/entities/ai/ghost_behavior.py"
run_test "tests/test_maze.py exists" "test -f tests/test_maze.py"
run_test "tests/test_ai.py exists" "test -f tests/test_ai.py"

echo -e "${YELLOW}=== SECTION 2: Imports ===${NC}"
echo ""
run_test "Import Maze" "python3 -c 'from src.maze.maze import Maze'"
run_test "Import MazeGenerator" "python3 -c 'from src.maze.maze_generator import MazeGenerator'"
run_test "Import Pathfinder" "python3 -c 'from src.entities.ai.pathfinding import Pathfinder'"
run_test "Import GhostAI" "python3 -c 'from src.entities.ai.ghost_behavior import GhostAI'"

echo -e "${YELLOW}=== SECTION 3: Maze Behavior ===${NC}"
echo ""
run_test "Maze creation works" "python3 -c 'from src.maze.maze import Maze; m = Maze(7, 7); assert m.width == 7 and m.height == 7'"
run_test "Maze walkability works" "python3 -c 'from src.maze.maze import Maze; from src.maze.tile import TileType; m = Maze(5, 5); m.tiles[2][2] = TileType.WALL; assert m.is_walkable(2, 2) is False'"
run_test "Maze generator builds borders" "python3 -c 'from src.maze.maze_generator import MazeGenerator; from src.maze.tile import TileType; m = MazeGenerator.generate(7, 7, 42); assert m.tiles[0][0] == TileType.WALL'"
run_test "Pellet placement works" "python3 -c 'from src.maze.maze_generator import MazeGenerator; m = MazeGenerator.generate(7, 7, 42); p = MazeGenerator.place_pellets(m, {\"pacgum_count\": 5}); assert len(p) == 5'"
run_test "Ghost placement works" "python3 -c 'from src.maze.maze_generator import MazeGenerator; g = MazeGenerator.generate(7, 7, 42); ghosts = MazeGenerator.place_ghosts(g); assert len(ghosts) == 4'"

echo -e "${YELLOW}=== SECTION 4: AI Behavior ===${NC}"
echo ""
run_test "Pathfinder distance" "python3 -c 'from src.entities.ai.pathfinding import Pathfinder; assert Pathfinder.manhattan_distance((0,0), (3,4)) == 7'"
run_test "BFS returns a step" "python3 -c 'from src.entities.ai.pathfinding import Pathfinder; from src.maze.maze import Maze; m = Maze(5, 5); step = Pathfinder.bfs(m, (1,1), (3,1)); assert step is not None'"
run_test "GhostAI returns a move" "python3 -c 'from src.entities.ai.ghost_behavior import GhostAI; from src.entities.ghost import Ghost, GhostType; from src.entities.pacman import Pacman; from src.maze.maze import Maze; m = Maze(7, 7); p = Pacman(4, 4); g = Ghost(GhostType.BLINKY, 1, 1); assert GhostAI.calculate_next_move(g, p, m) is not None'"

echo -e "${YELLOW}=== SECTION 5: Unit Tests ===${NC}"
echo ""
run_test "Run test_maze.py" "python3 -m pytest tests/test_maze.py -v --tb=short"
run_test "Run test_ai.py" "python3 -m pytest tests/test_ai.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

echo -e "${YELLOW}=== SECTION 6: Code Quality ===${NC}"
echo ""
run_test "flake8 on phase 3 sources" "python3 -m flake8 src tests pac-man.py"
run_test "make lint passes" "make lint"

echo -e "${YELLOW}=== SECTION 7: Integration Checks ===${NC}"
echo ""
run_test "Entities package imports" "python3 -c \"import src.entities; import src.entities.ai; print('ok')\""
run_test "Maze center available" "python3 -c 'from src.maze.maze import Maze; m = Maze(9, 9); assert m.get_center() == (4, 4)'"

echo ""
echo "================================"
echo -e "${BLUE}Test Summary${NC}"
echo "================================"
echo -e "Total Tests:  ${BLUE}$test_count${NC}"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}✅ All tests passed! Phase 3 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

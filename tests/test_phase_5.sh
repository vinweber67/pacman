#!/bin/bash
# Pac-Man Phase 5 - Test Suite
# Validation script for Game Loop & Integration

set +e

echo "================================"
echo "Pac-Man Phase 5 - Test Suite"
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

    if eval "$command" > /tmp/test_phase_5_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_phase_5_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

echo -e "${YELLOW}=== SECTION 1: Required Files ===${NC}"
echo ""
run_test "src/game/game_loop.py exists" "test -f src/game/game_loop.py"
run_test "src/game/level_manager.py exists" "test -f src/game/level_manager.py"
run_test "src/ui/scenes/game_scene.py exists" "test -f src/ui/scenes/game_scene.py"
run_test "src/highscore/highscore_manager.py exists" "test -f src/highscore/highscore_manager.py"
run_test "src/cheat/cheat_mode.py exists" "test -f src/cheat/cheat_mode.py"
run_test "tests/test_game_loop.py exists" "test -f tests/test_game_loop.py"

echo -e "${YELLOW}=== SECTION 2: Imports ===${NC}"
echo ""
run_test "Import GameLoop" "python3 -c 'from src.game.game_loop import GameLoop'"
run_test "Import LevelManager" "python3 -c 'from src.game.level_manager import LevelManager'"
run_test "Import GameScene" "python3 -c 'from src.ui.scenes.game_scene import GameScene'"
run_test "Import HighscoreManager" "python3 -c 'from src.highscore.highscore_manager import HighscoreManager'"
run_test "Import CheatMode" "python3 -c 'from src.cheat.cheat_mode import CheatMode'"

echo -e "${YELLOW}=== SECTION 3: Game Logic ===${NC}"
echo ""
run_test "LevelManager loads level" "python3 -c 'from src.game.level_manager import LevelManager; from src.game.game_state import GameState; config = {\"levels\": [{\"width\": 7, \"height\": 7, \"seed\": 42, \"max_time\": 12}], \"pacgum_count\": 5}; s = GameState(); s.reset(); m = LevelManager(config); level = m.load_level(1); assert level.maze.width == 7 and s.current_level == 1'"
run_test "GameLoop step decreases time" "python3 -c 'from src.game.game_loop import GameLoop; from src.game.game_manager import GameManager; config = {\"levels\": [{\"width\": 7, \"height\": 7, \"seed\": 42, \"max_time\": 12}], \"pacgum_count\": 5}; m = GameManager(config); m.start_game(); loop = GameLoop(m); loop.step(1.0, keys=[]); from src.game.game_state import GameState; assert GameState().level_time_remaining == 11'"
run_test "Cheat skip advances level" "python3 -c \"from src.game.game_manager import GameManager; from src.game.game_state import GameState; config = {'highscore_filename': '.data/highscores.json', 'levels': [{'width': 7, 'height': 7, 'seed': 42, 'max_time': 12}, {'width': 9, 'height': 9, 'seed': 7, 'max_time': 15}], 'pacgum_count': 5}; s = GameState(); s.reset(); m = GameManager(config); m.start_game(); m.handle_input(ord('c')); assert GameState().current_level == 2\""

echo -e "${YELLOW}=== SECTION 4: Unit Tests ===${NC}"
echo ""
run_test "Run test_game_loop.py" "python3 -m pytest tests/test_game_loop.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

echo -e "${YELLOW}=== SECTION 5: Code Quality ===${NC}"
echo ""
run_test "flake8 on phase 5 sources" "python3 -m flake8 src tests pac-man.py"
run_test "make lint passes" "make lint"

echo -e "${YELLOW}=== SECTION 6: Integration Checks ===${NC}"
echo ""
run_test "Packages import" "python3 -c \"import src.game; import src.highscore; import src.cheat; import src.ui.scenes; print('ok')\""
run_test "UI manager has game scene" "python3 -c 'from src.ui.ui_manager import UIManager; ui = UIManager(); ui.switch_scene(\"game\"); assert ui.current_scene_name == \"game\"'"
run_test "Game loop stops on request" "python3 -c 'from src.game.game_loop import GameLoop; from src.game.game_manager import GameManager; m = GameManager({\"levels\": [{\"width\": 7, \"height\": 7, \"seed\": 42, \"max_time\": 12}], \"pacgum_count\": 5}); loop = GameLoop(m); loop.stop(); assert loop.running is False'"

echo ""
echo "================================"
echo -e "${BLUE}Test Summary${NC}"
echo "================================"
echo -e "Total Tests:  ${BLUE}$test_count${NC}"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}✅ All tests passed! Phase 5 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

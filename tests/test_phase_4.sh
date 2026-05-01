#!/bin/bash
# Pac-Man Phase 4 - Test Suite
# Validation script for UI & Input

set +e

echo "================================"
echo "Pac-Man Phase 4 - Test Suite"
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

    if eval "$command" > /tmp/test_phase_4_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_phase_4_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

echo -e "${YELLOW}=== SECTION 1: Required Files ===${NC}"
echo ""
run_test "src/ui/renderer.py exists" "test -f src/ui/renderer.py"
run_test "src/ui/colors.py exists" "test -f src/ui/colors.py"
run_test "src/ui/ui_manager.py exists" "test -f src/ui/ui_manager.py"
run_test "src/ui/scenes/scene.py exists" "test -f src/ui/scenes/scene.py"
run_test "src/ui/scenes/main_menu.py exists" "test -f src/ui/scenes/main_menu.py"
run_test "src/input/key_bindings.py exists" "test -f src/input/key_bindings.py"
run_test "src/input/input_handler.py exists" "test -f src/input/input_handler.py"
run_test "tests/test_ui.py exists" "test -f tests/test_ui.py"
run_test "tests/test_input.py exists" "test -f tests/test_input.py"

echo -e "${YELLOW}=== SECTION 2: Imports ===${NC}"
echo ""
run_test "Import Renderer" "python3 -c 'from src.ui.renderer import Renderer'"
run_test "Import UIManager" "python3 -c 'from src.ui.ui_manager import UIManager'"
run_test "Import MainMenuScene" "python3 -c 'from src.ui.scenes.main_menu import MainMenuScene'"
run_test "Import InputHandler" "python3 -c 'from src.input.input_handler import InputHandler'"
run_test "Import Action" "python3 -c 'from src.input.key_bindings import Action'"

echo -e "${YELLOW}=== SECTION 3: UI Behavior ===${NC}"
echo ""
run_test "Renderer falls back headless" "python3 -c 'from src.ui.renderer import Renderer; r = Renderer(320, 240); assert r.width == 320 and r.height == 240'"
run_test "Color palette is available" "python3 -c 'from src.ui.colors import COLORS; from src.utils.constants import Color; assert COLORS[Color.BLACK] == (0, 0, 0)'"
run_test "Main menu navigation works" "python3 -c 'from src.ui.scenes.main_menu import MainMenuScene; m = MainMenuScene(); m.handle_input(65364); assert m.selected == 1'"
run_test "UIManager keeps menu scene on unknown scene" "python3 -c 'from src.ui.ui_manager import UIManager; ui = UIManager(); scene = ui.current_scene; ui.switch_scene(\"unknown\"); assert ui.current_scene is scene'"

echo -e "${YELLOW}=== SECTION 4: Input Behavior ===${NC}"
echo ""
run_test "Arrow keys map correctly" "python3 -c 'from src.input.input_handler import InputHandler; from src.input.key_bindings import Action; assert InputHandler.key_to_action(65362) == Action.MOVE_UP'"
run_test "WASD keys map correctly" "python3 -c 'from src.input.input_handler import InputHandler; from src.input.key_bindings import Action; assert InputHandler.key_to_action(ord(\"d\")) == Action.MOVE_RIGHT'"
run_test "Special keys map correctly" "python3 -c 'from src.input.input_handler import InputHandler; from src.input.key_bindings import Action; assert InputHandler.key_to_action(ord(\"c\")) == Action.CHEAT'"
run_test "Unknown key returns None" "python3 -c 'from src.input.input_handler import InputHandler; assert InputHandler.key_to_action(99999) is None'"

echo -e "${YELLOW}=== SECTION 5: Unit Tests ===${NC}"
echo ""
run_test "Run test_ui.py" "python3 -m pytest tests/test_ui.py -v --tb=short"
run_test "Run test_input.py" "python3 -m pytest tests/test_input.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

echo -e "${YELLOW}=== SECTION 6: Code Quality ===${NC}"
echo ""
run_test "flake8 on phase 4 sources" "python3 -m flake8 src tests pac-man.py"
run_test "make lint passes" "make lint"

echo -e "${YELLOW}=== SECTION 7: Integration Checks ===${NC}"
echo ""
run_test "Entities and UI packages import" "python3 -c \"import src.ui; import src.ui.scenes; import src.input; print('ok')\""
run_test "UI manager can render headless" "python3 -c 'from src.ui.ui_manager import UIManager; ui = UIManager(); ui.render()'"

echo ""
echo "================================"
echo -e "${BLUE}Test Summary${NC}"
echo "================================"
echo -e "Total Tests:  ${BLUE}$test_count${NC}"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}✅ All tests passed! Phase 4 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

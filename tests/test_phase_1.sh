#!/bin/bash
# Pac-Man Phase 1 - Test Suite
# Validation script for Configuration & GameState

set +e

echo "================================"
echo "Pac-Man Phase 1 - Test Suite"
echo "================================"
echo ""

# Colors
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

    if eval "$command" > /tmp/test_phase_1_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_phase_1_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

# ============================================================================
# SECTION 1: Required Files
# ============================================================================
echo -e "${YELLOW}=== SECTION 1: Required Files ===${NC}"
echo ""

run_test "src/game/game_state.py exists" "test -f src/game/game_state.py"
run_test "tests/test_gamestate.py exists" "test -f tests/test_gamestate.py"

# ============================================================================
# SECTION 2: GameState Imports
# ============================================================================
echo -e "${YELLOW}=== SECTION 2: GameState Imports ===${NC}"
echo ""

run_test "Import GameState" "python3 -c 'from src.game.game_state import GameState'"
run_test "Instantiate GameState" "python3 -c 'from src.game.game_state import GameState; state = GameState(); print(state)'"
run_test "Singleton identity" "python3 -c 'from src.game.game_state import GameState; a = GameState(); b = GameState(); assert a is b'"

# ============================================================================
# SECTION 3: GameState Behavior
# ============================================================================
echo -e "${YELLOW}=== SECTION 3: GameState Behavior ===${NC}"
echo ""

run_test "Reset restores defaults" "python3 -c 'from src.game.game_state import GameState; s = GameState(); s.score = 123; s.lives = 1; s.reset(); assert s.score == 0 and s.lives == 3'"
run_test "Add score works" "python3 -c 'from src.game.game_state import GameState; s = GameState(); s.reset(); s.add_score(25); assert s.score == 25'"
run_test "Lose life triggers game over" "python3 -c 'from src.game.game_state import GameState; s = GameState(); s.reset(); s.lives = 1; s.lose_life(); assert s.is_game_over is True and s.lives == 0'"
run_test "Next level increments" "python3 -c 'from src.game.game_state import GameState; s = GameState(); s.reset(); s.next_level(); assert s.current_level == 2 and s.level_time_remaining == 90'"
run_test "Pause toggle works" "python3 -c 'from src.game.game_state import GameState; s = GameState(); s.reset(); s.toggle_pause(); assert s.is_paused is True; s.toggle_pause(); assert s.is_paused is False'"

# ============================================================================
# SECTION 4: Unit Tests
# ============================================================================
echo -e "${YELLOW}=== SECTION 4: Unit Tests ===${NC}"
echo ""

run_test "Run test_gamestate.py" "python3 -m pytest tests/test_gamestate.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

# ============================================================================
# SECTION 5: Code Quality
# ============================================================================
echo -e "${YELLOW}=== SECTION 5: Code Quality ===${NC}"
echo ""

run_test "flake8 on src/tests/pac-man.py" "python3 -m flake8 src tests pac-man.py"
run_test "make lint passes" "make lint"

# ============================================================================
# SECTION 6: Configuration Integration
# ============================================================================
echo -e "${YELLOW}=== SECTION 6: Configuration Integration ===${NC}"
echo ""

run_test "Load config.json with ConfigLoader" "python3 -c \"from src.config.config_loader import ConfigLoader; c = ConfigLoader.load('config.json'); assert 'lives' in c and 'levels' in c\""
run_test "Validate config.json with ConfigValidator" "python3 -c \"from src.config.config_loader import ConfigLoader; from src.config.config_validator import ConfigValidator; c = ConfigLoader.load('config.json'); v = ConfigValidator.validate(c); assert v['lives'] >= 1 and len(v['levels']) > 0\""

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "================================"
echo -e "${BLUE}Test Summary${NC}"
echo "================================"
echo -e "Total Tests:  ${BLUE}$test_count${NC}"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e ""
    echo -e "${GREEN}✅ All tests passed! Phase 1 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

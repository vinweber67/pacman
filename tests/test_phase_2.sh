#!/bin/bash
# Pac-Man Phase 2 - Test Suite
# Validation script for Entities & Core Gameplay

set +e

echo "================================"
echo "Pac-Man Phase 2 - Test Suite"
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

    if eval "$command" > /tmp/test_phase_2_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_phase_2_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

# ============================================================================
# SECTION 1: Required Files
# ============================================================================
echo -e "${YELLOW}=== SECTION 1: Required Files ===${NC}"
echo ""

run_test "src/entities/entity.py exists" "test -f src/entities/entity.py"
run_test "src/entities/pacman.py exists" "test -f src/entities/pacman.py"
run_test "src/entities/ghost.py exists" "test -f src/entities/ghost.py"
run_test "src/entities/pellet.py exists" "test -f src/entities/pellet.py"
run_test "src/game/collision.py exists" "test -f src/game/collision.py"
run_test "tests/test_entities.py exists" "test -f tests/test_entities.py"

# ============================================================================
# SECTION 2: Entity Imports
# ============================================================================
echo -e "${YELLOW}=== SECTION 2: Entity Imports ===${NC}"
echo ""

run_test "Import Entity" "python3 -c 'from src.entities.entity import Entity'"
run_test "Import Pacman" "python3 -c 'from src.entities.pacman import Pacman'"
run_test "Import Ghost and GhostType" "python3 -c 'from src.entities.ghost import Ghost, GhostType'"
run_test "Import Pellet" "python3 -c 'from src.entities.pellet import Pellet'"
run_test "Import CollisionDetector" "python3 -c 'from src.game.collision import CollisionDetector'"

# ============================================================================
# SECTION 3: Entity Behavior
# ============================================================================
echo -e "${YELLOW}=== SECTION 3: Entity Behavior ===${NC}"
echo ""

run_test "Pacman creation works" "python3 -c 'from src.entities.pacman import Pacman; p = Pacman(10, 10); assert p.x == 10 and p.y == 10'"
run_test "Pacman movement works" "python3 -c 'from src.entities.pacman import Pacman; p = Pacman(10, 10); p.move(1, 0); assert p.x == 11 and p.y == 10'"
run_test "Pacman direction update works" "python3 -c 'from src.entities.pacman import Pacman; from src.utils.constants import Direction; p = Pacman(0, 0); p.set_direction(Direction.RIGHT); p.update(0.016); assert p.direction == Direction.RIGHT'"
run_test "Ghost creation works" "python3 -c 'from src.entities.ghost import Ghost, GhostType; g = Ghost(GhostType.BLINKY, 1, 2); assert g.x == 1 and g.y == 2 and g.spawn_x == 1 and g.spawn_y == 2'"
run_test "Ghost edible state works" "python3 -c 'from src.entities.ghost import Ghost, GhostType; g = Ghost(GhostType.BLINKY, 1, 2); g.become_edible(5.0); assert g.is_edible is True'"
run_test "Pellet eat works" "python3 -c 'from src.entities.pellet import Pellet; p = Pellet(3, 4, is_super=True); points = p.eat(); assert points == 50 and p.is_eaten is True'"

# ============================================================================
# SECTION 4: Collision Detection
# ============================================================================
echo -e "${YELLOW}=== SECTION 4: Collision Detection ===${NC}"
echo ""

run_test "Pacman-ghost collision detection" "python3 -c 'from src.entities.pacman import Pacman; from src.entities.ghost import Ghost, GhostType; from src.game.collision import CollisionDetector; p = Pacman(5, 5); g = Ghost(GhostType.BLINKY, 5, 5); assert CollisionDetector.check_pacman_ghost_collision(p, [g]) is g'"
run_test "Pacman-pellet collision detection" "python3 -c 'from src.entities.pacman import Pacman; from src.entities.pellet import Pellet; from src.game.collision import CollisionDetector; p = Pacman(5, 5); pellet = Pellet(5, 5); assert CollisionDetector.check_pacman_pellet_collision(p, [pellet]) is pellet'"
run_test "No collision returns None" "python3 -c 'from src.entities.pacman import Pacman; from src.entities.ghost import Ghost, GhostType; from src.game.collision import CollisionDetector; p = Pacman(0, 0); g = Ghost(GhostType.BLINKY, 5, 5); assert CollisionDetector.check_pacman_ghost_collision(p, [g]) is None'"

# ============================================================================
# SECTION 5: Unit Tests
# ============================================================================
echo -e "${YELLOW}=== SECTION 5: Unit Tests ===${NC}"
echo ""

run_test "Run test_entities.py" "python3 -m pytest tests/test_entities.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

# ============================================================================
# SECTION 6: Code Quality
# ============================================================================
echo -e "${YELLOW}=== SECTION 6: Code Quality ===${NC}"
echo ""

run_test "flake8 on phase 2 sources" "python3 -m flake8 src tests pac-man.py"
run_test "make lint passes" "make lint"

# ============================================================================
# SECTION 7: Integration Checks
# ============================================================================
echo -e "${YELLOW}=== SECTION 7: Integration Checks ===${NC}"
echo ""

run_test "Import Direction and Collision flow" "python3 -c 'from src.utils.constants import Direction; from src.game.collision import CollisionDetector; print(Direction.RIGHT)'"
run_test "Entities package imports" "python3 -c \"import src.entities; import src.entities.ai; print('ok')\""

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
    echo -e "${GREEN}✅ All tests passed! Phase 2 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

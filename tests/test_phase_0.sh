#!/bin/bash
# Pac-Man Phase 0 - Test Suite
# Complete testing guide for infrastructure validation

# Don't exit on first error - we want to run all tests
set +e

echo "================================"
echo "Pac-Man Phase 0 - Test Suite"
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

# Helper function to run a test
run_test() {
    test_count=$((test_count + 1))
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}[TEST $test_count]${NC} $test_name"
    
    if eval "$command" > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Output:"
        cat /tmp/test_output.txt
        fail_count=$((fail_count + 1))
    fi
    echo ""
}

# ============================================================================
# SECTION 1: Directory Structure
# ============================================================================
echo -e "${YELLOW}=== SECTION 1: Directory Structure ===${NC}"
echo ""

run_test "Check src directory exists" "test -d src"
run_test "Check tests directory exists" "test -d tests"
run_test "Check doc directory exists" "test -d doc"
run_test "Check .data directory exists" "test -d .data"
run_test "Check doc/PROJECT_MANAGEMENT exists" "test -d doc/PROJECT_MANAGEMENT"

# ============================================================================
# SECTION 2: Required Files
# ============================================================================
echo -e "${YELLOW}=== SECTION 2: Required Files ===${NC}"
echo ""

run_test "requirements.txt exists" "test -f requirements.txt"
run_test "Makefile exists" "test -f Makefile"
run_test ".gitignore exists" "test -f .gitignore"
run_test "config.json exists" "test -f config.json"
run_test "pac-man.py exists" "test -f pac-man.py"
run_test "pac-man.py is executable readable" "test -r pac-man.py"

# ============================================================================
# SECTION 3: Source Code Structure
# ============================================================================
echo -e "${YELLOW}=== SECTION 3: Source Code Structure ===${NC}"
echo ""

run_test "src/__init__.py exists" "test -f src/__init__.py"
run_test "src/config/__init__.py exists" "test -f src/config/__init__.py"
run_test "src/config/config_loader.py exists" "test -f src/config/config_loader.py"
run_test "src/config/config_validator.py exists" "test -f src/config/config_validator.py"
run_test "src/game/__init__.py exists" "test -f src/game/__init__.py"
run_test "src/game/game_manager.py exists" "test -f src/game/game_manager.py"
run_test "src/utils/__init__.py exists" "test -f src/utils/__init__.py"
run_test "src/utils/constants.py exists" "test -f src/utils/constants.py"
run_test "src/utils/logger.py exists" "test -f src/utils/logger.py"
run_test "src/utils/exceptions.py exists" "test -f src/utils/exceptions.py"
run_test "src/utils/types.py exists" "test -f src/utils/types.py"

# ============================================================================
# SECTION 4: Test Files
# ============================================================================
echo -e "${YELLOW}=== SECTION 4: Test Files ===${NC}"
echo ""

run_test "tests/__init__.py exists" "test -f tests/__init__.py"
run_test "tests/test_config.py exists" "test -f tests/test_config.py"
run_test "tests/test_utils.py exists" "test -f tests/test_utils.py"

# ============================================================================
# SECTION 5: Code Quality - Linting
# ============================================================================
echo -e "${YELLOW}=== SECTION 5: Code Quality - Linting ===${NC}"
echo ""

run_test "flake8 on src/" "python3 -m flake8 src pac-man.py"
run_test "flake8 on tests/" "python3 -m flake8 tests"

# ============================================================================
# SECTION 6: Program Execution
# ============================================================================
echo -e "${YELLOW}=== SECTION 6: Program Execution ===${NC}"
echo ""

run_test "Run with valid config" "python3 pac-man.py config.json > /dev/null 2>&1"
run_test "Correct exit code with valid config" "python3 pac-man.py config.json > /dev/null 2>&1; test \$? -eq 0"

# ============================================================================
# SECTION 7: Error Handling
# ============================================================================
echo -e "${YELLOW}=== SECTION 7: Error Handling ===${NC}"
echo ""

run_test "Error on missing argument" "! python3 pac-man.py > /dev/null 2>&1"
run_test "Error code 1 on missing argument" "python3 pac-man.py > /dev/null 2>&1; test \$? -eq 1"

run_test "Error on file not found" "! python3 pac-man.py nonexistent.json > /dev/null 2>&1"
run_test "Error code 1 on file not found" "python3 pac-man.py nonexistent.json > /dev/null 2>&1; test \$? -eq 1"

# Invalid JSON
echo '{"invalid}' > /tmp/invalid.json
run_test "Error on invalid JSON" "! python3 pac-man.py /tmp/invalid.json > /dev/null 2>&1"
run_test "Error code 1 on invalid JSON" "python3 pac-man.py /tmp/invalid.json > /dev/null 2>&1; test \$? -eq 1"

# ============================================================================
# SECTION 8: Configuration Loading
# ============================================================================
echo -e "${YELLOW}=== SECTION 8: Configuration Loading ===${NC}"
echo ""

run_test "Config has required keys" "python3 -c \"from src.config.config_loader import ConfigLoader; c=ConfigLoader.load('config.json'); assert 'levels' in c and 'lives' in c\""
run_test "Config has 10 levels" "python3 -c \"from src.config.config_loader import ConfigLoader; c=ConfigLoader.load('config.json'); assert len(c['levels']) >= 10\""
run_test "First level has seed 42" "python3 -c \"from src.config.config_loader import ConfigLoader; c=ConfigLoader.load('config.json'); assert c['levels'][0]['seed'] == 42\""

# ============================================================================
# SECTION 9: Unit Tests
# ============================================================================
echo -e "${YELLOW}=== SECTION 9: Unit Tests ===${NC}"
echo ""

run_test "Run test_utils.py" "python3 -m pytest tests/test_utils.py -v --tb=short"
run_test "Run test_config.py" "python3 -m pytest tests/test_config.py -v --tb=short"
run_test "Run all tests" "python3 -m pytest tests/ -v --tb=short"

# ============================================================================
# SECTION 10: Module Imports
# ============================================================================
echo -e "${YELLOW}=== SECTION 10: Module Imports ===${NC}"
echo ""

run_test "Import constants" "python3 -c 'from src.utils.constants import Direction, Color, GamePhase'"
run_test "Import logger" "python3 -c 'from src.utils.logger import setup_logger, get_logger'"
run_test "Import exceptions" "python3 -c 'from src.utils.exceptions import ConfigError, GameStateError'"
run_test "Import config_loader" "python3 -c 'from src.config.config_loader import ConfigLoader'"
run_test "Import config_validator" "python3 -c 'from src.config.config_validator import ConfigValidator'"
run_test "Import game_manager" "python3 -c 'from src.game.game_manager import GameManager'"

# ============================================================================
# SECTION 11: Makefile Commands
# ============================================================================
echo -e "${YELLOW}=== SECTION 11: Makefile Commands ===${NC}"
echo ""

run_test "make clean works" "make clean > /dev/null 2>&1"
run_test "make lint passes" "make lint > /dev/null 2>&1"

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
    echo -e "${GREEN}✅ All tests passed! Phase 0 is complete!${NC}"
    exit 0
else
    echo -e ""
    echo -e "${RED}❌ Some tests failed. Review the output above.${NC}"
    exit 1
fi

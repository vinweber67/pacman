.PHONY: install run debug clean lint lint-strict test help

help:
	@echo "Pac-Man Game - Available commands:"
	@echo "  make install      - Install project dependencies"
	@echo "  make run          - Run the game"
	@echo "  make debug        - Run in debug mode (pdb)"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make lint         - Check code style with flake8 and mypy"
	@echo "  make lint-strict  - Run mypy in strict mode"
	@echo "  make test         - Run unit tests with pytest"

install:
	pip install -r requirements.txt

run:
	python3 pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean completed"

lint:
	flake8 src tests pac-man.py
	mypy src tests pac-man.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	mypy src tests pac-man.py --strict

test:
	pytest tests -v --tb=short

.DEFAULT_GOAL := help

.PHONY: install run debug clean lint lint-strict test help

PYTHON := .venv/bin/python
UV := uv
UV_PIP := $(UV) pip install --python $(PYTHON)
UV_RUN := $(UV) run --python $(PYTHON)

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
	@if [ ! -f "mazegenerator-00001-py3-none-any.whl" ]; then \
		echo "Error: required wheel '4 Pacman - data.whl' not found"; \
		exit 1; \
	fi; \
	$(UV) venv .venv; \
	tmp_wheel="/tmp/mazegenerator-2.0.1-py3-none-any.whl"; \
	cp "mazegenerator-00001-py3-none-any.whl" "$$tmp_wheel"; \
	$(UV_PIP) "$$tmp_wheel"; \
	$(UV_PIP) -e ".[dev]"

run: install
	$(UV_RUN) pac-man.py config.json

debug:
	$(UV_RUN) -m pdb pac-man.py config.json

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean completed"

lint:
	$(UV_RUN) -m flake8 src tests pac-man.py
	$(UV_RUN) -m mypy src tests pac-man.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV_RUN) -m mypy src tests pac-man.py --strict

test:
	$(UV_RUN) -m pytest tests -v --tb=short

.DEFAULT_GOAL := help

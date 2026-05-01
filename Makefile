.PHONY: install run debug clean lint lint-strict test help

PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP := $(PYTHON) -m pip

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
	@if [ ! -f "4 Pacman - data.whl" ]; then \
		echo "Error: required wheel '4 Pacman - data.whl' not found"; \
		exit 1; \
	fi; \
	tmp_wheel="/tmp/mazegenerator-2.0.1-py3-none-any.whl"; \
	cp "4 Pacman - data.whl" "$$tmp_wheel"; \
	$(PIP) install "$$tmp_wheel"; \
	if [ -f "mlx-2.2-py3-none-any.whl" ]; then \
		$(PIP) install "mlx-2.2-py3-none-any.whl"; \
	else \
		echo "Warning: optional wheel 'mlx-2.2-py3-none-any.whl' not found"; \
	fi; \
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) pac-man.py config.json

debug:
	$(PYTHON) -m pdb pac-man.py config.json

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean completed"

lint:
	$(PYTHON) -m flake8 src tests pac-man.py
	$(PYTHON) -m mypy src tests pac-man.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m mypy src tests pac-man.py --strict

test:
	$(PYTHON) -m pytest tests -v --tb=short

.DEFAULT_GOAL := help

# Guide de Test - Phase 0

## 📋 Vue d'ensemble

Ce guide te permet de valider complètement que la **Phase 0** est correctement implémentée.

---

## 🚀 Démarrage Rapide

### Option 1: Test Script Automatisé (Recommandé)

```bash
# Rendre le script exécutable
chmod +x test_phase_0.sh

# Exécuter tous les tests
./test_phase_0.sh
```

Cela va exécuter **30+ tests** automatiquement et afficher un résumé.

### Option 2: Tests Manuels (Pour déboguer)

Voir sections ci-dessous pour exécuter chaque test individuellement.

---

## 🔍 Tests Détaillés

### Section 1: Structure des Répertoires

```bash
# Vérifier que tous les répertoires existent
test -d src && echo "✅ src/" || echo "❌ src/"
test -d tests && echo "✅ tests/" || echo "❌ tests/"
test -d doc && echo "✅ doc/" || echo "❌ doc/"
test -d .data && echo "✅ .data/" || echo "❌ .data/"
test -d doc/PROJECT_MANAGEMENT && echo "✅ doc/PROJECT_MANAGEMENT/" || echo "❌ doc/PROJECT_MANAGEMENT/"

# Lister la structure
tree -L 2 src/
```

**Résultat attendu:** Tous les répertoires existent

---

### Section 2: Fichiers Requis

```bash
# Vérifier les fichiers de configuration
ls -la requirements.txt
ls -la Makefile
ls -la .gitignore
ls -la config.json
ls -la pac-man.py

# Vérifier la lisibilité
file pac-man.py
head -1 pac-man.py  # Doit être #!/usr/bin/env python3
```

**Résultat attendu:** Tous les fichiers existent

---

### Section 3: Fichiers Sources

```bash
# Vérifier les __init__.py
ls -la src/__init__.py
ls -la src/config/__init__.py
ls -la src/game/__init__.py
ls -la src/utils/__init__.py

# Vérifier les modules
ls -la src/config/config_loader.py
ls -la src/config/config_validator.py
ls -la src/game/game_manager.py
ls -la src/utils/constants.py
ls -la src/utils/logger.py
ls -la src/utils/exceptions.py
ls -la src/utils/types.py
```

**Résultat attendu:** Tous les fichiers existent

---

### Section 4: Fichiers de Test

```bash
ls -la tests/__init__.py
ls -la tests/test_config.py
ls -la tests/test_utils.py

# Compter le nombre de tests
grep -c "def test_" tests/test_config.py
grep -c "def test_" tests/test_utils.py
```

**Résultat attendu:** Tous les fichiers existent, au moins 20 tests

---

### Section 5: Code Quality - Linting

```bash
# Vérifier PEP 8 avec flake8
make lint

# Alternative: command directe
python3 -m flake8 src pac-man.py tests
```

**Résultat attendu:** ✅ 0 erreurs, 0 warnings

---

### Section 6: Exécution du Programme

```bash
# Lancer avec config valide
python3 pac-man.py config.json

# Vérifier le code de retour
python3 pac-man.py config.json
echo "Exit code: $?"
```

**Résultat attendu:**
- Logs affichés avec timestamps
- Logs colorés (optionnel sur terminal)
- Code de retour: 0 (succès)
- Pas de traceback Python

---

### Section 7: Gestion d'Erreurs

#### 7.1: Pas d'argument

```bash
python3 pac-man.py
echo "Exit code: $?"
```

**Résultat attendu:**
- Message clair: "Usage: python3 pac-man.py <config.json>"
- Code de retour: 1 (erreur)
- Pas de traceback

#### 7.2: Fichier inexistant

```bash
python3 pac-man.py nonexistent_file.json
echo "Exit code: $?"
```

**Résultat attendu:**
- Message: "Config file not found: nonexistent_file.json"
- Code de retour: 1

#### 7.3: JSON invalide

```bash
# Créer un fichier JSON invalide
echo '{"invalid}' > /tmp/bad_config.json

python3 pac-man.py /tmp/bad_config.json
echo "Exit code: $?"
```

**Résultat attendu:**
- Message avec détail du parsing error
- Code de retour: 1
- Pas de traceback Python complet

#### 7.4: Non-JSON file

```bash
python3 pac-man.py README.md
echo "Exit code: $?"
```

**Résultat attendu:**
- Message d'erreur
- Code de retour: 1

---

### Section 8: Configuration

```bash
# Vérifier que config.json est valide
python3 -c "
import json
with open('config.json') as f:
    content = f.read()
    # La config a des commentaires, donc on utilise le loader
    from src.config.config_loader import ConfigLoader
    config = ConfigLoader.load('config.json')
    print(f'✅ Config loaded: {len(config)} keys')
    print(f'✅ Lives: {config[\"lives\"]}')
    print(f'✅ Levels: {len(config[\"levels\"])} levels')
"

# Vérifier les commentaires
grep -c "^  //" config.json  # Commentaires C++
grep -c "^  #" config.json   # Commentaires Python
```

**Résultat attendu:**
- Configuration charge correctement
- 10 niveaux ou plus
- Support des commentaires fonctionne

---

### Section 9: Tests Unitaires

```bash
# Exécuter tous les tests
python3 -m pytest tests/ -v

# Exécuter avec coverage
python3 -m pytest tests/ -v --cov=src

# Exécuter un test spécifique
python3 -m pytest tests/test_config.py::TestConfigLoader::test_load_valid_config -v
```

**Résultat attendu:**
- ✅ 22+ tests passés
- 0 tests échoués
- Pas de warnings

---

### Section 10: Imports et Modules

```bash
# Vérifier que tous les modules sont importables
python3 -c "from src.utils.constants import Direction, Color, GamePhase; print('✅ constants')"
python3 -c "from src.utils.logger import setup_logger; print('✅ logger')"
python3 -c "from src.utils.exceptions import ConfigError; print('✅ exceptions')"
python3 -c "from src.config.config_loader import ConfigLoader; print('✅ config_loader')"
python3 -c "from src.config.config_validator import ConfigValidator; print('✅ config_validator')"
python3 -c "from src.game.game_manager import GameManager; print('✅ game_manager')"

# Test complet d'import
python3 pac-man.py config.json 2>&1 | head -5
```

**Résultat attendu:** Tous les imports fonctionnent

---

### Section 11: Makefile

```bash
# Vérifier les commandes Makefile
make help

# Tester make clean
make clean
ls -la __pycache__ 2>&1  # Ne devrait pas exister

# Tester make lint
make lint

# Tester make test (si pytest est disponible)
make test
```

**Résultat attendu:** Toutes les commandes fonctionnent

---

### Section 12: Constantes et Énumérations

```bash
# Vérifier les constantes
python3 -c "
from src.utils.constants import Direction, Color, TILE_SIZE, FPS
print(f'TILE_SIZE = {TILE_SIZE}')
print(f'FPS = {FPS}')
print(f'Direction.UP = {Direction.UP.value}')
print(f'Color.RED = {Color.RED.value}')
print('✅ Constants OK')
"

# Vérifier les propriétés Direction
python3 -c "
from src.utils.constants import Direction
d = Direction.UP
print(f'dx={d.dx}, dy={d.dy}')
print(f'opposite={d.opposite()}')
print('✅ Direction OK')
"
```

**Résultat attendu:** Toutes les constantes et énums fonctionnent

---

### Section 13: Logger

```bash
# Tester le logging
python3 -c "
from src.utils.logger import setup_logger
logger = setup_logger('test', use_colors=False)
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
print('✅ Logger OK')
"
```

**Résultat attendu:** Messages affichés avec couleurs (si terminal supporte)

---

## 📊 Checklist de Validation

```
Phase 0 - Infrastructure
========================

Répertoires
□ src/ et tous sous-répertoires
□ tests/
□ doc/ et doc/PROJECT_MANAGEMENT/
□ .data/

Fichiers de Configuration
□ requirements.txt
□ Makefile
□ .gitignore
□ config.json (10+ niveaux)
□ pac-man.py

Fichiers Sources
□ src/__init__.py et tous sous-paquets
□ src/config/config_loader.py
□ src/config/config_validator.py
□ src/game/game_manager.py
□ src/utils/constants.py
□ src/utils/logger.py
□ src/utils/exceptions.py
□ src/utils/types.py

Fichiers Tests
□ tests/test_config.py (14+ tests)
□ tests/test_utils.py (8+ tests)

Code Quality
□ flake8: 0 erreurs
□ Type hints: complètes
□ Docstrings: PEP 257

Exécution
□ python3 pac-man.py config.json → exit 0
□ python3 pac-man.py → exit 1 (erreur usage)
□ python3 pac-man.py nonexistent.json → exit 1
□ Gestion d'erreurs: messages clairs, pas de traceback

Tests
□ pytest tests/ → 22+ tests passés
□ Tous les imports fonctionnent
□ Config charge correctement

Makefile
□ make install
□ make run
□ make clean
□ make lint
□ make test
□ make help
```

---

## 🎯 Résultat Attendu

À la fin de tous ces tests, tu devrais avoir:

✅ **Tous les fichiers en place**
✅ **Zéro erreur flake8**
✅ **22+ tests passés**
✅ **Program se lance correctement**
✅ **Gestion d'erreurs complète**
✅ **Logs structurés et lisibles**
✅ **Configuration chargée et validée**

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'pytest'"
```bash
pip install pytest
# ou
make install
```

### "flake8: command not found"
```bash
pip install flake8
```

### "mypy: command not found"
```bash
pip install mypy
```

### "Config file not found"
```bash
# Vérifier que config.json existe
ls -la config.json
# Donner le chemin complet
python3 pac-man.py $(pwd)/config.json
```

### Logs ne sont pas colorés
```bash
# C'est normal si terminal ne supporte pas les couleurs
# Vérifier que les logs apparaissent quand même
```

---

## 📝 Notes

- Phase 0 est une **infrastructure basique**
- Les modules (Phase 1+) ne sont que des stubs
- C'est normal qu'on ne puisse pas jouer encore
- Le focus est sur la **structure et qualité du code**

---

## 🎓 Prochaines Étapes

Une fois Phase 0 validée:
1. ✅ Phase 0 complète
2. → **Phase 1: Configuration & GameState**
3. → Phase 2: Entities & Gameplay
4. → Phase 3: IA & Maze
5. → Phase 4: UI
6. → Phase 5: Game Loop
7. → Phase 6: Polish
8. → Phase 7: Packaging

---

**Bon test! 🎮**

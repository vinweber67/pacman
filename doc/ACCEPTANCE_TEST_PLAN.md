# Test Checklist - Pac-Man Project

## 📋 Plan d'acceptation des tests

Ce document fournit une **checklist complète** pour valider que le projet respecte tous les requirements du sujet et de l'architecture.

À utiliser lors de la défense pour vérifier que **aucune feature n'a été oubliée**.

---

## ✅ PARTIE 1: Configuration et Démarrage

### 1.1 Lancement du programme

- [ ] Le programme se lance avec: `python3 pac-man.py config.json`
- [ ] Le programme refuse de se lancer sans argument
- [ ] Le programme refuse de se lancer avec plus d'un argument
- [ ] Le programme refuse de se lancer avec un fichier qui n'existe pas (message clair, pas de traceback)
- [ ] Le programme refuse de se lancer avec un fichier non-JSON (message clair)
- [ ] Le programme affiche un message d'erreur clair pour JSON invalide
- [ ] Le programme démarre immédiatement après avec la config valide

### 1.2 Configuration (config.json)

- [ ] Le fichier `config.json` existe et est valid JSON
- [ ] Les commentaires `#` sont supportés et ignorés
- [ ] Les commentaires C++ `//` sont supportés (bonus)
- [ ] Les clés recommandées sont présentes:
  - [ ] `highscore_filename` (défaut: `.data/highscores.json`)
  - [ ] `levels` (array avec width, height, seed, max_time)
  - [ ] `lives` (défaut: 3)
  - [ ] `pacgum_count` (défaut: 42)
  - [ ] `points_per_pacgum` (défaut: 10)
  - [ ] `points_per_super_pacgum` (défaut: 50)
  - [ ] `points_per_ghost` (défaut: 200)
  - [ ] `ghost_respawn_time` (défaut: 10s)
  - [ ] `super_pacgum_duration` (défaut: 10s)

### 1.3 Gestion des erreurs de configuration

- [ ] Configuration manquante → defaults appliqués, log clair
- [ ] Clés invalides → ignorées, pas de crash
- [ ] Valeurs invalides → clamped aux defaults, log clair
- [ ] Aucun traceback Python affiché
- [ ] Le jeu continue avec config partiellement valide

### 1.4 Configuration du labyrinthe

- [ ] Au moins 10 niveaux configurés
- [ ] Premier niveau utilise seed fixe (ex: 42)
- [ ] Niveaux suivants utilisent seeds aléatoires
- [ ] Chaque niveau a width, height, max_time définis

---

## ✅ PARTIE 2: Intégration du générateur de labyrinthe (A-Maze-ing)

### 2.1 Utilisation du package

- [ ] Le package A-Maze-ing est importé et utilisé
- [ ] Le package est utilisé AS-IS (pas modifié)
- [ ] Le paramètre `PERFECT=False` est utilisé
- [ ] La génération produit des labyrinthes jouables (corridors)
- [ ] Les murs ne bloquent pas tous les passages

### 2.2 Gestion des erreurs de génération

- [ ] Si la génération échoue → message clair, pas de crash
- [ ] Un fallback/labyrinthe par défaut est utilisé
- [ ] Le jeu est toujours jouable

### 2.3 Placement des entités

- [ ] Les pacgums sont placés dans les corridors
- [ ] 4 super-pacgums sont placés aux 4 coins
- [ ] 4 fantômes sont placés aux 4 coins
- [ ] Pac-Man démarre au centre du labyrinthe
- [ ] Les positions de spawn sont valides (corridors, pas murs)

---

## ✅ PARTIE 3: Jouabilité - Pac-Man

### 3.1 Mouvement

- [ ] Pac-Man se déplace avec les touches FLÉCHE UP/DOWN/LEFT/RIGHT
- [ ] Pac-Man se déplace avec les touches WASD (W=up, A=left, S=down, D=right)
- [ ] Pac-Man se déplace uniquement dans les corridors
- [ ] Pac-Man ne traverse pas les murs
- [ ] La vitesse est constante
- [ ] Les mouvements se font carreau par carreau (pas de mouvement fluide/pixel-perfect)

### 3.2 Manger les pacgums

- [ ] Pac-Man mange les pacgums au contact
- [ ] Le score augmente de `points_per_pacgum` (config)
- [ ] Le pacgum disparaît
- [ ] Le compteur de pacgums restants diminue

### 3.3 Manger les super-pacgums

- [ ] Pac-Man mange les super-pacgums au contact
- [ ] Le score augmente de `points_per_super_pacgum` (config)
- [ ] Le super-pacgum disparaît
- [ ] Les fantômes deviennent comestibles
- [ ] L'effet dure `super_pacgum_duration` secondes (config)
- [ ] Après l'effet, les fantômes redeviennent normaux

### 3.4 Manger les fantômes

- [ ] Pac-Man peut manger les fantômes quand ils sont comestibles (edible)
- [ ] Le score augmente de `points_per_ghost` (config) par fantôme mangé
- [ ] Le fantôme mangé disparaît et respawn après `ghost_respawn_time` secondes
- [ ] Le fantôme respawn à son coin d'origine

### 3.5 Vies et game-over

- [ ] Pac-Man commence avec `lives` vies (config, défaut: 3)
- [ ] Toucher un fantôme non-comestible = perte de 1 vie
- [ ] Après perte de vie, Pac-Man respawn au centre
- [ ] Quand lives = 0, affichage "Game Over"
- [ ] Le jeu ne continue pas après game-over

### 3.6 Respawn

- [ ] Après perte de vie, Pac-Man respawn au centre du labyrinthe
- [ ] Les fantômes ne respawn pas immédiatement (restent à leur position)
- [ ] Les pacgums qui ont été mangés restent mangés

---

## ✅ PARTIE 4: Jouabilité - Fantômes

### 4.1 Mouvement autonome

- [ ] Les 4 fantômes se déplacent automatiquement
- [ ] Les fantômes se déplacent uniquement dans les corridors
- [ ] Les fantômes ne traversent pas les murs
- [ ] Les fantômes changent de direction régulièrement

### 4.2 Comportement Chase (normal)

- [ ] Blinky (rouge): Chasse Pac-Man directement via BFS/pathfinding
- [ ] Pinky (rose): Ambush - cible position + 4 tuiles devant Pac-Man
- [ ] Inky (cyan): Imprévisible - mix entre chasse et random
- [ ] Clyde (orange): Scatter si Pac-Man trop proche, sinon retour au coin

### 4.3 Comportement Edible (après super-pacgum)

- [ ] Les fantômes fuient Pac-Man dans la direction opposée
- [ ] Les fantômes continuent à fuir pendant `super_pacgum_duration` secondes
- [ ] Une fois l'effet expiré, les fantômes redeviennent normaux
- [ ] Le temps restant de mode edible est visible pour le joueur (bonus)

### 4.4 Respawn après être mangé

- [ ] Fantôme mangé: timer de `ghost_respawn_time` secondes (config, défaut: 10s)
- [ ] Après le timer, le fantôme respawn à son coin d'origine
- [ ] Les autres fantômes continuent normalement pendant le respawn

### 4.5 Identification des fantômes

- [ ] Blinky est rouge
- [ ] Pinky est rose/magenta
- [ ] Inky est cyan/turquoise
- [ ] Clyde est orange/jaune
- [ ] Les couleurs sont clairement distinguables

---

## ✅ PARTIE 5: Progression et niveaux

### 5.1 Conditions de victoire par niveau

- [ ] Quand tous les pacgums sont mangés → niveau complété
- [ ] Affichage "Level Complete" ou transition vers niveau suivant
- [ ] Score et vies conservés pour le niveau suivant
- [ ] Pas de reset du score entre niveaux

### 5.2 Génération des niveaux

- [ ] Niveau 1: Généré avec seed fixe (42) → reproductible
- [ ] Niveaux 2-10+: Générés avec seeds aléatoires → variété
- [ ] Chaque niveau a un labyrinthe différent (visuellement)
- [ ] Chaque niveau est jouable

### 5.3 Gestion du temps par niveau

- [ ] Timer affiché: `max_time` secondes (config, ex: 90s)
- [ ] Timer diminue en continu
- [ ] Quand timer atteint 0:
  - [ ] OPTION A: Niveau redémarré
  - [ ] OPTION B: Jeu terminé
  - [ ] (Comportement documenté dans README)

### 5.4 Fin du jeu

- [ ] Quand tous les niveaux (10+) sont complétés → affichage "Victory"
- [ ] Quand le joueur perd toutes ses vies → affichage "Game Over"
- [ ] À la fin, affichage du score final
- [ ] Prompt pour entrer le nom du joueur

---

## ✅ PARTIE 6: Système de Highscores

### 6.1 Stockage

- [ ] Les highscores sont stockés dans un fichier (chemin config)
- [ ] Fichier existe et est valid JSON
- [ ] Le fichier est créé s'il n'existe pas
- [ ] Le fichier persiste entre redémarrages

### 6.2 Gestion des scores

- [ ] Quand le jeu se termine (victoire ou défaite), prompt pour entrer le nom
- [ ] Maximum 10 caractères alphanumériques + espaces
- [ ] Si le score est top 10, il est sauvegardé
- [ ] Les 10 meilleurs scores sont conservés
- [ ] Les anciens scores sont supprimés (si > 10 entrées)

### 6.3 Affichage des highscores

- [ ] Menu principal affiche option "View Highscores"
- [ ] Cliquer affiche les top 10 scores avec noms
- [ ] Format clair: Rank | Name | Score
- [ ] Classement par score décroissant
- [ ] Retour au menu principal depuis highscores

### 6.4 Robustesse

- [ ] Si fichier highscores manquant → liste vide, pas de crash
- [ ] Si fichier corromptu → liste vide, pas de crash
- [ ] Si nom invalide (> 10 chars ou caractères spéciaux) → rejeté, re-prompt
- [ ] Scores toujours non-négatifs

---

## ✅ PARTIE 7: Interface Utilisateur

### 7.1 Menu principal

- [ ] Menu visible au démarrage
- [ ] Options claires et lisibles:
  - [ ] "Start Game"
  - [ ] "View Highscores"
  - [ ] "Instructions"
  - [ ] "Exit"
- [ ] Navigation avec flèches haut/bas
- [ ] Sélection avec Entrée
- [ ] "Exit" ferme le jeu correctement

### 7.2 Vue de jeu

- [ ] Labyrinthe affiché à l'écran
- [ ] Pac-Man visible et animé
- [ ] 4 fantômes visibles et distinguables
- [ ] Pacgums visibles
- [ ] Super-pacgums visibles et différents des pacgums
- [ ] Pas de flickering ou lag

### 7.3 HUD en jeu

Visible en permanence pendant le jeu:
- [ ] Score actuel
- [ ] Vies restantes
- [ ] Niveau actuel
- [ ] Temps restant pour le niveau

### 7.4 Menu de pause

- [ ] Accessible avec la touche P (ou définie)
- [ ] Affichage clair: "PAUSED"
- [ ] Options:
  - [ ] Resume
  - [ ] Return to Main Menu
- [ ] Le jeu ne se met pas à jour quand en pause
- [ ] Les entités sont figées

### 7.5 Écran de game-over

- [ ] Affichage clair du score final
- [ ] Message: "Game Over" ou "You Lost"
- [ ] Prompt pour entrer le nom
- [ ] Après saisie du nom, retour au menu principal

### 7.6 Écran de victoire

- [ ] Affichage clair du score final
- [ ] Message de félicitations: "Victory!" ou "You Won!"
- [ ] Prompt pour entrer le nom
- [ ] Après saisie du nom, retour au menu principal

### 7.7 Instructions

- [ ] Menu principal affiche option "Instructions"
- [ ] Explique les contrôles
- [ ] Explique l'objectif du jeu
- [ ] Explique les règles basiques
- [ ] Retour au menu avec une touche

---

## ✅ PARTIE 8: Mode Triche (Cheat Mode)

### 8.1 Activation

- [ ] Mode triche activable via touche (ex: Ctrl+H)
- [ ] Activé pendant la phase d'évaluation
- [ ] Facilite l'évaluation

### 8.2 Fonctionnalités de triche

Au moins 3-4 parmi:
- [ ] **Invincibilité**: Pac-Man ne peut pas être mangé
- [ ] **Level Skip**: Passer au niveau suivant instantanément
- [ ] **Ghost Freeze**: Les fantômes ne se déplacent plus
- [ ] **Extra Lives**: Ajouter des vies
- [ ] **Speed Boost**: Pac-Man se déplace plus vite
- [ ] **Show All Paths**: Afficher les chemins de pathfinding
- [ ] **No Time Limit**: Le timer disparaît/est infini

### 8.3 Interface du mode triche

- [ ] Menu accessible en jeu avec touche dédiée
- [ ] Affichage des commandes disponibles
- [ ] Activation/désactivation des cheats
- [ ] Visible mais non-intrusif

---

## ✅ PARTIE 9: Code Quality

### 9.1 Structure et architecture

- [ ] Code organisé en modules selon [doc/ARCHITECTURE.md](../doc/ARCHITECTURE.md)
- [ ] Chaque module a une responsabilité claire
- [ ] Pas de dépendances circulaires
- [ ] Imports organisés et clairs
- [ ] Fichiers de taille raisonnable (< 500 lignes)

### 9.2 Style de code - PEP 8 + flake8

```bash
make lint
```

- [ ] `flake8 .` retourne 0 erreurs
- [ ] Pas de ligne trop longue (> 79 caractères)
- [ ] Pas de trailing whitespace
- [ ] Indentation cohérente (4 espaces)
- [ ] Imports au début du fichier

### 9.3 Type hints - mypy

```bash
make lint
```

- [ ] `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` retourne 0 erreurs
- [ ] Toutes les fonctions ont des type hints sur paramètres et retour
- [ ] Toutes les variables ont des type hints
- [ ] Pas de `Any` non-justifié

### 9.4 Docstrings - PEP 257

- [ ] Toutes les fonctions ont des docstrings
- [ ] Toutes les classes ont des docstrings
- [ ] Format Google style (ou NumPy, cohérent)
- [ ] Docstrings incluent: description, Args, Returns, Raises
- [ ] Exemples d'utilisation pour fonctions complexes

### 9.5 Gestion d'erreurs

- [ ] Pas de `except Exception` générique (utilisé `try-except` spécifiques)
- [ ] Pas de `except:` (catch all)
- [ ] Pas d'exceptions ignorées silencieusement (`pass`)
- [ ] Exceptions loggées avec message clair
- [ ] Le programme ne crashe jamais avec traceback
- [ ] Erreurs utilisateur → messages clairs, pas techniques

### 9.6 Logging

- [ ] Utilisé `logger` au lieu de `print()`
- [ ] Niveaux de log corrects:
  - [ ] `logger.debug()` pour infos de développement
  - [ ] `logger.info()` pour infos importantes
  - [ ] `logger.warning()` pour avertissements
  - [ ] `logger.error()` pour erreurs
- [ ] Messages clairs et informatifs

### 9.7 Context managers et ressources

- [ ] Fichiers ouverts avec `with open():`
- [ ] Pas de file handles non-fermés
- [ ] Pas de memory leaks
- [ ] Ressources nettoyées proprement

---

## ✅ PARTIE 10: Tests

### 10.1 Tests unitaires

```bash
make test
```

- [ ] Tests unitaires pour chaque module (pytest)
- [ ] Au moins les modules critiques testés:
  - [ ] Config loader
  - [ ] Pacman mouvement/collision
  - [ ] Ghost IA
  - [ ] Maze generation
  - [ ] Highscore system
- [ ] Coverage > 50% du code critique
- [ ] Tous les tests passent (`make test`)

### 10.2 Edge cases

- [ ] Coin avec Pacman + Ghost + Super-Pacgum
- [ ] Niveau avec peu de pacgums
- [ ] Ghost au coin quand Pacman arrive
- [ ] Multiple super-pacgums proches
- [ ] Timer très court
- [ ] Fichier config minimal (tous les defaults)

---

## ✅ PARTIE 11: Commandes Makefile

```bash
make install
```

- [ ] Installe toutes les dépendances
- [ ] Pas d'erreurs
- [ ] Le projet est prêt à être lancé

```bash
make run
```

- [ ] Lance le jeu
- [ ] Le jeu démarre correctement
- [ ] Pas d'erreurs

```bash
make debug
```

- [ ] Lance le jeu en mode debug (pdb)
- [ ] Points de break fonctionnent

```bash
make clean
```

- [ ] Supprime les caches (`__pycache__`, `.mypy_cache`, `.pytest_cache`)
- [ ] Le projet reste fonctionnel après

```bash
make lint
```

- [ ] Exécute `flake8 .`
- [ ] Exécute `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
- [ ] Retourne 0 erreurs

```bash
make lint-strict
```

- [ ] Exécute `mypy . --strict` (si implémenté)
- [ ] Mode strict plus rigoureux

---

## ✅ PARTIE 12: Documentation

### 12.1 README.md

Le README doit contenir:
- [ ] Première ligne italicisée: "*This project has been created as part of the 42 curriculum by [student names]*"
- [ ] Section "Description": Présentation du projet et goal
- [ ] Section "Instructions": Compilation, installation, exécution
- [ ] Section "Resources": Références, documentation, comment AI a été utilisé
- [ ] Section "Configuration": Structure du config.json et defaults
- [ ] Section "Highscore": Explication du système et justification
- [ ] Section "Maze Generation": Comment A-Maze-ing est utilisé
- [ ] Section "Implementation": Résumé technique
- [ ] Section "General Software Architecture": Vue d'ensemble (modules, classes, relations)
- [ ] Section "Project Management": Suivi du projet + lien vers doc/PROJECT_MANAGEMENT/

### 12.2 Documentation technique

- [ ] [doc/ARCHITECTURE.md](../doc/ARCHITECTURE.md): Architecture complète ✓ (déjà fait)
- [ ] [doc/API.md](../doc/API.md): Documentation des APIs (créé)
- [ ] [doc/DESIGN.md](../doc/DESIGN.md): Décisions de design (créé)

### 12.3 Project Management

Dossier [doc/PROJECT_MANAGEMENT/](../doc/PROJECT_MANAGEMENT/):
- [ ] timeline.md: Timeline du projet
- [ ] progress.md: Progress réel vs timeline
- [ ] risk_analysis.md: Analyse des risques
- [ ] team_notes.md: Notes sur la collaboration

---

## ✅ PARTIE 13: Fichiers et structure

### 13.1 Fichiers obligatoires

- [ ] `pac-man.py` existe à la racine
- [ ] `config.json` existe à la racine (ou template)
- [ ] `Makefile` existe et valide
- [ ] `requirements.txt` existe avec dépendances
- [ ] `README.md` existe et complet
- [ ] `.gitignore` existe
- [ ] `.copilot-instructions.md` existe

### 13.2 Structure src/

- [ ] `src/config/` - Config management ✓
- [ ] `src/game/` - Game logic ✓
- [ ] `src/entities/` - Entities + AI ✓
- [ ] `src/maze/` - Maze generation ✓
- [ ] `src/ui/` - UI + rendering ✓
- [ ] `src/input/` - Input handling ✓
- [ ] `src/highscore/` - Highscores ✓
- [ ] `src/cheat/` - Cheat mode ✓
- [ ] `src/utils/` - Utilities ✓

### 13.3 Dossiers générés (ignorés)

- [ ] `.data/` - Data persistantes (highscores.json)
- [ ] `__pycache__/` - Caches Python
- [ ] `.mypy_cache/` - Cache mypy
- [ ] `.pytest_cache/` - Cache pytest
- [ ] `dist/` - Distribution empaquetée

---

## ✅ PARTIE 14: Performance

### 14.1 FPS et smoothness

- [ ] Jeu tourne à ~60 FPS (stable)
- [ ] Pas de lag visible
- [ ] Pas de freezes pendant gameplay
- [ ] Animations fluides

### 14.2 Temps de démarrage

- [ ] Programme démarre < 2 secondes
- [ ] Chargement de labyrinthe < 1 seconde
- [ ] Pas d'attente perceptible

### 14.3 Mémoire

- [ ] Pas d'augmentation de mémoire pendant le jeu
- [ ] Pas de fuites mémoire
- [ ] Usage mémoire raisonnable (< 200MB)

---

## ✅ PARTIE 15: Packaging et Deployment

### 15.1 Package build

- [ ] Script de packaging à la racine ou doc/
- [ ] Génère un exécutable standalone
- [ ] Exécutable fonctionne sans Python installé
- [ ] Exécutable fonctionne sur Linux/macOS/Windows (cross-platform)

### 15.2 Déploiement Itch.io ou Steam

- [ ] Jeu publié sur Itch.io ou Steam (unlisted/private)
- [ ] URL fournie et fonctionnelle
- [ ] Build complète et jouable
- [ ] Instructions minimales incluses

### 15.3 Instruction d'installation

- [ ] README clair sur comment installer et lancer
- [ ] Commande simple: `python3 pac-man.py config.json`
- [ ] Pas d'étapes compliquées
- [ ] Avec make: `make install && make run`

---

## ✅ PARTIE 16: Respect des requirements du sujet

### Mandatory Part

- [ ] Jeu complet et jouable ✓
- [ ] Utilise MLX ou librairie similaire ✓
- [ ] OOP et architecture modulaire ✓
- [ ] Configuration via fichier JSON ✓
- [ ] Gestion robuste d'erreurs ✓
- [ ] A-Maze-ing package intégré ✓
- [ ] Système de highscores persistant ✓
- [ ] UI polished (menu, game view, game-over) ✓
- [ ] Mode triche pour évaluation ✓
- [ ] Déployé sur Itch.io/Steam ✓

### General Rules

- [ ] Python 3.10+ ✓
- [ ] Adhère à flake8 (`make lint`) ✓
- [ ] Gestion d'exceptions complète ✓
- [ ] Ressources gérées correctement ✓
- [ ] Type hints sur tout (`mypy`) ✓
- [ ] Docstrings (PEP 257) ✓

### Makefile

- [ ] `make install` ✓
- [ ] `make run` ✓
- [ ] `make debug` ✓
- [ ] `make clean` ✓
- [ ] `make lint` ✓
- [ ] `make lint-strict` (optionnel) ✓
- [ ] `make test` ✓

### Game Loop

- [ ] Main Menu > Start > Win/Lose > Highscore > Menu ✓

### Project Management

- [ ] Timeline, progress tracking ✓
- [ ] Risk analysis ✓
- [ ] Team organization ✓
- [ ] Acceptance test plan (CE DOCUMENT) ✓

### README Requirements

- [ ] Premier ligne italicisée (42 curriculum) ✓
- [ ] Description ✓
- [ ] Instructions ✓
- [ ] Resources ✓
- [ ] Configuration ✓
- [ ] Highscore ✓
- [ ] Maze Generation ✓
- [ ] Implementation ✓
- [ ] General Software Architecture ✓
- [ ] Project Management ✓

---

## 🚀 Processus de test avant défense

### Phase 1: Automated tests
```bash
make clean
make lint
make test
```
✅ Tous les tests doivent passer

### Phase 2: Manual gameplay
- [ ] Parcourir tous les niveaux
- [ ] Tester toutes les interactions
- [ ] Vérifier le scoring
- [ ] Vérifier les highscores

### Phase 3: Edge cases
- [ ] Config invalide
- [ ] Fichier manquant
- [ ] Coins spéciaux
- [ ] Rapidité extrême
- [ ] Pas de pacgums

### Phase 4: Code review
- [ ] Lire tout le code
- [ ] Vérifier la cohérence
- [ ] Vérifier les docstrings
- [ ] Vérifier les erreurs

### Phase 5: Documentation review
- [ ] README complet et à jour
- [ ] Architecture documentée
- [ ] Decisions explicites
- [ ] Exemples clairs

---

## 📊 Scoring de défense

**Objectif**: Avoir ✅ sur ~95% de cette checklist

- **95-100%**: Excellent 🌟
- **85-94%**: Bon ✅
- **75-84%**: Acceptable ⚠️
- **< 75%**: À retravailler ❌

---

## 📝 Notes pour la défense

Printez/emportez cette checklist. Pendant la défense:

1. Demander accès au code + repo
2. Lancer: `make install && make run`
3. Tester en direct chaque section
4. Cocher ✅ ou ❌
5. Noter les bugs trouvés
6. Documenter les déviations au sujet

**Déviation acceptable**: Si justifiée et documentée dans README

**Déviation non-acceptable**: Si brise des requirements critiques du sujet

---

## 🔗 Références

- [subject.md](../subject.md) - Requirements officiels
- [doc/ARCHITECTURE.md](../doc/ARCHITECTURE.md) - Architecture complète
- [.copilot-instructions.md](../.copilot-instructions.md) - Instructions Copilot

---

**Dernière mise à jour**: 1 Mai 2026
**Status**: Ready for use

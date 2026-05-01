# Test Checklist - Pac-Man Project

## 📋 Plan d'acceptation des tests

Ce document fournit une **checklist complète** pour valider que le projet respecte tous les requirements du sujet et de l'architecture.

À utiliser lors de la défense pour vérifier que **aucune feature n'a été oubliée**.

---

## ✅ PARTIE 1: Configuration et Démarrage

### 1.1 Lancement du programme

- [x] Le programme se lance avec: `python3 pac-man.py config.json`
- [x] Le programme refuse de se lancer sans argument
- [x] Le programme refuse de se lancer avec plus d'un argument
- [x] Le programme refuse de se lancer avec un fichier qui n'existe pas (message clair, pas de traceback)
- [x] Le programme refuse de se lancer avec un fichier non-JSON (message clair)
- [x] Le programme affiche un message d'erreur clair pour JSON invalide
- [x] Le programme démarre immédiatement après avec la config valide

### 1.2 Configuration (config.json)

- [x] Le fichier `config.json` existe et est valid JSON
- [x] Les commentaires `#` sont supportés et ignorés
- [x] Les commentaires C++ `//` sont supportés (bonus)
- [x] Les clés recommandées sont présentes:
  - [x] `highscore_filename` (défaut: `.data/highscores.json`)
  - [x] `levels` (array avec width, height, seed, max_time)
  - [x] `lives` (défaut: 3)
  - [x] `pacgum_count` (défaut: 42)
  - [x] `points_per_pacgum` (défaut: 10)
  - [x] `points_per_super_pacgum` (défaut: 50)
  - [x] `points_per_ghost` (défaut: 200)
  - [x] `ghost_respawn_time` (défaut: 10s)
  - [x] `super_pacgum_duration` (défaut: 10s)

### 1.3 Gestion des erreurs de configuration

- [x] Configuration manquante → defaults appliqués, log clair
- [x] Clés invalides → ignorées, pas de crash
- [x] Valeurs invalides → clamped aux defaults, log clair
- [x] Aucun traceback Python affiché
- [x] Le jeu continue avec config partiellement valide

### 1.4 Configuration du labyrinthe

- [x] Au moins 10 niveaux configurés
- [x] Premier niveau utilise seed fixe (ex: 42)
- [x] Niveaux suivants utilisent seeds aléatoires
- [x] Chaque niveau a width, height, max_time définis

---

## ✅ PARTIE 2: Intégration du générateur de labyrinthe (A-Maze-ing)

### 2.1 Utilisation du package

- [x] Le package A-Maze-ing est importé et utilisé
- [x] Le package est utilisé AS-IS (pas modifié)
- [x] Le paramètre `PERFECT=False` est utilisé
- [x] La génération produit des labyrinthes jouables (corridors)
- [x] Les murs ne bloquent pas tous les passages

### 2.2 Gestion des erreurs de génération

- [x] Si la génération échoue → message clair, pas de crash
- [x] Un fallback/labyrinthe par défaut est utilisé
- [x] Le jeu est toujours jouable

### 2.3 Placement des entités

- [x] Les pacgums sont placés dans les corridors
- [x] 4 super-pacgums sont placés aux 4 coins
- [x] 4 fantômes sont placés aux 4 coins
- [x] Pac-Man démarre au centre du labyrinthe
- [x] Les positions de spawn sont valides (corridors, pas murs)

---

## ✅ PARTIE 3: Jouabilité - Pac-Man

### 3.1 Mouvement

- [x] Pac-Man se déplace avec les touches FLÉCHE UP/DOWN/LEFT/RIGHT
- [x] Pac-Man se déplace avec les touches WASD (W=up, A=left, S=down, D=right)
- [x] Pac-Man se déplace uniquement dans les corridors
- [x] Pac-Man ne traverse pas les murs
- [x] La vitesse est constante
- [x] Les mouvements se font carreau par carreau (pas de mouvement fluide/pixel-perfect)

### 3.2 Manger les pacgums

- [x] Pac-Man mange les pacgums au contact
- [x] Le score augmente de `points_per_pacgum` (config)
- [x] Le pacgum disparaît
- [x] Le compteur de pacgums restants diminue

### 3.3 Manger les super-pacgums

- [x] Pac-Man mange les super-pacgums au contact
- [x] Le score augmente de `points_per_super_pacgum` (config)
- [x] Le super-pacgum disparaît
- [x] Les fantômes deviennent comestibles
- [x] L'effet dure `super_pacgum_duration` secondes (config)
- [x] Après l'effet, les fantômes redeviennent normaux

### 3.4 Manger les fantômes

- [x] Pac-Man peut manger les fantômes quand ils sont comestibles (edible)
- [x] Le score augmente de `points_per_ghost` (config) par fantôme mangé
- [x] Le fantôme mangé disparaît et respawn après `ghost_respawn_time` secondes
- [x] Le fantôme respawn à son coin d'origine

### 3.5 Vies et game-over

- [x] Pac-Man commence avec `lives` vies (config, défaut: 3)
- [x] Toucher un fantôme non-comestible = perte de 1 vie
- [x] Après perte de vie, Pac-Man respawn au centre
- [x] Quand lives = 0, affichage "Game Over"
- [x] Le jeu ne continue pas après game-over

### 3.6 Respawn

- [x] Après perte de vie, Pac-Man respawn au centre du labyrinthe
- [x] Les fantômes ne respawn pas immédiatement (restent à leur position)
- [x] Les pacgums qui ont été mangés restent mangés

---

## ✅ PARTIE 4: Jouabilité - Fantômes

### 4.1 Mouvement autonome

- [x] Les 4 fantômes se déplacent automatiquement
- [x] Les fantômes se déplacent uniquement dans les corridors
- [x] Les fantômes ne traversent pas les murs
- [x] Les fantômes changent de direction régulièrement

### 4.2 Comportement Chase (normal)

- [x] Blinky (rouge): Chasse Pac-Man directement via BFS/pathfinding
- [x] Pinky (rose): Ambush - cible position + 4 tuiles devant Pac-Man
- [x] Inky (cyan): Imprévisible - mix entre chasse et random
- [x] Clyde (orange): Scatter si Pac-Man trop proche, sinon retour au coin

### 4.3 Comportement Edible (après super-pacgum)

- [x] Les fantômes fuient Pac-Man dans la direction opposée
- [x] Les fantômes continuent à fuir pendant `super_pacgum_duration` secondes
- [x] Une fois l'effet expiré, les fantômes redeviennent normaux
- [x] Le temps restant de mode edible est visible pour le joueur (bonus)

### 4.4 Respawn après être mangé

- [x] Fantôme mangé: timer de `ghost_respawn_time` secondes (config, défaut: 10s)
- [x] Après le timer, le fantôme respawn à son coin d'origine
- [x] Les autres fantômes continuent normalement pendant le respawn

### 4.5 Identification des fantômes

- [x] Blinky est rouge
- [x] Pinky est rose/magenta
- [x] Inky est cyan/turquoise
- [x] Clyde est orange/jaune
- [x] Les couleurs sont clairement distinguables

---

## ✅ PARTIE 5: Progression et niveaux

### 5.1 Conditions de victoire par niveau

- [x] Quand tous les pacgums sont mangés → niveau complété
- [x] Affichage "Level Complete" ou transition vers niveau suivant
- [x] Score et vies conservés pour le niveau suivant
- [x] Pas de reset du score entre niveaux

### 5.2 Génération des niveaux

- [x] Niveau 1: Généré avec seed fixe (42) → reproductible
- [x] Niveaux 2-10+: Générés avec seeds aléatoires → variété
- [x] Chaque niveau a un labyrinthe différent (visuellement)
- [x] Chaque niveau est jouable

### 5.3 Gestion du temps par niveau

- [x] Timer affiché: `max_time` secondes (config, ex: 90s)
- [x] Timer diminue en continu
- [ ] Quand timer atteint 0:
  - [x] OPTION A: Niveau redémarré
  - [ ] OPTION B: Jeu terminé
  - [x] (Comportement documenté dans README)

### 5.4 Fin du jeu

- [x] Quand tous les niveaux (10+) sont complétés → affichage "Victory"
- [x] Quand le joueur perd toutes ses vies → affichage "Game Over"
- [x] À la fin, affichage du score final
- [x] Prompt pour entrer le nom du joueur

---

## ✅ PARTIE 6: Système de Highscores

### 6.1 Stockage

- [x] Les highscores sont stockés dans un fichier (chemin config)
- [x] Fichier existe et est valid JSON
- [x] Le fichier est créé s'il n'existe pas
- [x] Le fichier persiste entre redémarrages

### 6.2 Gestion des scores

- [x] Quand le jeu se termine (victoire ou défaite), prompt pour entrer le nom
- [x] Maximum 10 caractères alphanumériques + espaces
- [x] Si le score est top 10, il est sauvegardé
- [x] Les 10 meilleurs scores sont conservés
- [x] Les anciens scores sont supprimés (si > 10 entrées)

### 6.3 Affichage des highscores

- [x] Menu principal affiche option "View Highscores"
- [x] Cliquer affiche les top 10 scores avec noms
- [x] Format clair: Rank | Name | Score
- [x] Classement par score décroissant
- [x] Retour au menu principal depuis highscores

### 6.4 Robustesse

- [x] Si fichier highscores manquant → liste vide, pas de crash
- [x] Si fichier corromptu → liste vide, pas de crash
- [x] Si nom invalide (> 10 chars ou caractères spéciaux) → rejeté, re-prompt
- [x] Scores toujours non-négatifs

---

## ✅ PARTIE 7: Interface Utilisateur

### 7.1 Menu principal

- [x] Menu visible au démarrage
- [x] Options claires et lisibles:
  - [x] "Start Game"
  - [x] "View Highscores"
  - [x] "Instructions"
  - [x] "Exit"
- [x] Navigation avec flèches haut/bas
- [x] Sélection avec Entrée
- [x] "Exit" ferme le jeu correctement

### 7.2 Vue de jeu

- [x] Labyrinthe affiché à l'écran
- [x] Pac-Man visible et animé
- [x] 4 fantômes visibles et distinguables
- [x] Pacgums visibles
- [x] Super-pacgums visibles et différents des pacgums
- [ ] Pas de flickering ou lag

### 7.3 HUD en jeu

Visible en permanence pendant le jeu:
- [x] Score actuel
- [x] Vies restantes
- [x] Niveau actuel
- [x] Temps restant pour le niveau

### 7.4 Menu de pause

- [x] Accessible avec la touche P (ou définie)
- [x] Affichage clair: "PAUSED"
- [x] Options:
  - [x] Resume
  - [x] Return to Main Menu
- [x] Le jeu ne se met pas à jour quand en pause
- [x] Les entités sont figées

### 7.5 Écran de game-over

- [x] Affichage clair du score final
- [x] Message: "Game Over" ou "You Lost"
- [x] Prompt pour entrer le nom
- [x] Après saisie du nom, retour au menu principal

### 7.6 Écran de victoire

- [x] Affichage clair du score final
- [x] Message de félicitations: "Victory!" ou "You Won!"
- [x] Prompt pour entrer le nom
- [x] Après saisie du nom, retour au menu principal

### 7.7 Instructions

- [x] Menu principal affiche option "Instructions"
- [x] Explique les contrôles
- [x] Explique l'objectif du jeu
- [x] Explique les règles basiques
- [x] Retour au menu avec une touche

---

## ✅ PARTIE 8: Mode Triche (Cheat Mode)

### 8.1 Activation

- [x] Mode triche activable via touche (ex: Ctrl+H)
- [x] Activé pendant la phase d'évaluation
- [x] Facilite l'évaluation

### 8.2 Fonctionnalités de triche

Au moins 3-4 parmi:
- [x] **Invincibilité**: Pac-Man ne peut pas être mangé
- [x] **Level Skip**: Passer au niveau suivant instantanément
- [x] **Ghost Freeze**: Les fantômes ne se déplacent plus
- [x] **Extra Lives**: Ajouter des vies
- [x] **Speed Boost**: Pac-Man se déplace plus vite
- [x] **Show All Paths**: Afficher les chemins de pathfinding
- [x] **No Time Limit**: Le timer disparaît/est infini

### 8.3 Interface du mode triche

- [x] Menu accessible en jeu avec touche dédiée
- [x] Affichage des commandes disponibles
- [x] Activation/désactivation des cheats
- [x] Visible mais non-intrusif

---

## ✅ PARTIE 9: Code Quality

### 9.1 Structure et architecture

- [x] Code organisé en modules selon [doc/ARCHITECTURE.md](../doc/ARCHITECTURE.md)
- [x] Chaque module a une responsabilité claire
- [x] Pas de dépendances circulaires
- [x] Imports organisés et clairs
- [x] Fichiers de taille raisonnable (< 500 lignes)

### 9.2 Style de code - PEP 8 + flake8

```bash
make lint
```

- [x] `flake8 .` retourne 0 erreurs
- [x] Pas de ligne trop longue (> 79 caractères)
- [x] Pas de trailing whitespace
- [x] Indentation cohérente (4 espaces)
- [x] Imports au début du fichier

### 9.3 Type hints - mypy

```bash
make lint
```

- [x] `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` retourne 0 erreurs
- [x] Toutes les fonctions ont des type hints sur paramètres et retour
- [x] Toutes les variables ont des type hints
- [ ] Pas de `Any` non-justifié

### 9.4 Docstrings - PEP 257

- [ ] Toutes les fonctions ont des docstrings
- [ ] Toutes les classes ont des docstrings
- [ ] Format Google style (ou NumPy, cohérent)
- [ ] Docstrings incluent: description, Args, Returns, Raises
- [ ] Exemples d'utilisation pour fonctions complexes

### 9.5 Gestion d'erreurs

- [x] Pas de `except Exception` générique (utilisé `try-except` spécifiques)
- [x] Pas de `except:` (catch all)
- [x] Pas d'exceptions ignorées silencieusement (`pass`)
- [x] Exceptions loggées avec message clair
- [ ] Le programme ne crashe jamais avec traceback
- [x] Erreurs utilisateur → messages clairs, pas techniques

### 9.6 Logging

- [x] Utilisé `logger` au lieu de `print()`
- [x] Niveaux de log corrects:
  - [x] `logger.debug()` pour infos de développement
  - [x] `logger.info()` pour infos importantes
  - [x] `logger.warning()` pour avertissements
  - [x] `logger.error()` pour erreurs
- [x] Messages clairs et informatifs

### 9.7 Context managers et ressources

- [x] Fichiers ouverts avec `with open():`
- [ ] Pas de file handles non-fermés
- [ ] Pas de memory leaks
- [ ] Ressources nettoyées proprement

---

## ✅ PARTIE 10: Tests

### 10.1 Tests unitaires

```bash
make test
```

- [x] Tests unitaires pour chaque module (pytest)
- [x] Au moins les modules critiques testés:
  - [x] Config loader
  - [x] Pacman mouvement/collision
  - [x] Ghost IA
  - [x] Maze generation
  - [x] Highscore system
- [x] Coverage > 50% du code critique
- [x] Tous les tests passent (`make test`)

### 10.2 Edge cases

- [x] Coin avec Pacman + Ghost + Super-Pacgum
- [x] Niveau avec peu de pacgums
- [x] Ghost au coin quand Pacman arrive
- [x] Multiple super-pacgums proches
- [x] Timer très court
- [x] Fichier config minimal (tous les defaults)

---

## ✅ PARTIE 11: Commandes Makefile

```bash
make install
```

- [x] Installe toutes les dépendances
- [x] Pas d'erreurs
- [x] Le projet est prêt à être lancé

```bash
make run
```

- [x] Lance le jeu
- [x] Le jeu démarre correctement
- [x] Pas d'erreurs

```bash
make debug
```

- [x] Lance le jeu en mode debug (pdb)
- [x] Points de break fonctionnent

```bash
make clean
```

- [x] Supprime les caches (`__pycache__`, `.mypy_cache`, `.pytest_cache`)
- [x] Le projet reste fonctionnel après

```bash
make lint
```

- [x] Exécute `flake8 .`
- [x] Exécute `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
- [x] Retourne 0 erreurs

```bash
make lint-strict
```

- [x] Exécute `mypy . --strict` (si implémenté)
- [x] Mode strict plus rigoureux

---

## ✅ PARTIE 12: Documentation

### 12.1 README.md

Le README doit contenir:
- [x] Première ligne italicisée: "*This project has been created as part of the 42 curriculum by [student names]*"
- [x] Section "Description": Présentation du projet et goal
- [x] Section "Instructions": Compilation, installation, exécution
- [x] Section "Resources": Références, documentation, comment AI a été utilisé
- [x] Section "Configuration": Structure du config.json et defaults
- [x] Section "Highscore": Explication du système et justification
- [x] Section "Maze Generation": Comment A-Maze-ing est utilisé
- [x] Section "Implementation": Résumé technique
- [x] Section "General Software Architecture": Vue d'ensemble (modules, classes, relations)
- [x] Section "Project Management": Suivi du projet + lien vers doc/PROJECT_MANAGEMENT/

### 12.2 Documentation technique

- [x] [doc/ARCHITECTURE.md](../doc/ARCHITECTURE.md): Architecture complète ✓ (déjà fait)
- [x] [doc/API.md](../doc/API.md): Documentation des APIs (créé)
- [x] [doc/DESIGN.md](../doc/DESIGN.md): Décisions de design (créé)

### 12.3 Project Management

Dossier [doc/PROJECT_MANAGEMENT/](../doc/PROJECT_MANAGEMENT/):
- [x] timeline.md: Timeline du projet
- [x] progress.md: Progress réel vs timeline
- [x] risk_analysis.md: Analyse des risques
- [x] team_notes.md: Notes sur la collaboration

---

## ✅ PARTIE 13: Fichiers et structure

### 13.1 Fichiers obligatoires

- [x] `pac-man.py` existe à la racine
- [x] `config.json` existe à la racine (ou template)
- [x] `Makefile` existe et valide
- [x] `requirements.txt` existe avec dépendances
- [x] `README.md` existe et complet
- [x] `.gitignore` existe
- [x] `.copilot-instructions.md` existe

### 13.2 Structure src/

- [x] `src/config/` - Config management ✓
- [x] `src/game/` - Game logic ✓
- [x] `src/entities/` - Entities + AI ✓
- [x] `src/maze/` - Maze generation ✓
- [x] `src/ui/` - UI + rendering ✓
- [x] `src/input/` - Input handling ✓
- [x] `src/highscore/` - Highscores ✓
- [x] `src/cheat/` - Cheat mode ✓
- [x] `src/utils/` - Utilities ✓

### 13.3 Dossiers générés (ignorés)

- [x] `.data/` - Data persistantes (highscores.json)
- [x] `__pycache__/` - Caches Python
- [x] `.mypy_cache/` - Cache mypy
- [x] `.pytest_cache/` - Cache pytest
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

- [x] README clair sur comment installer et lancer
- [x] Commande simple: `python3 pac-man.py config.json`
- [x] Pas d'étapes compliquées
- [x] Avec make: `make install && make run`

---

## ✅ PARTIE 16: Respect des requirements du sujet

### Mandatory Part

- [x] Jeu complet et jouable ✓
- [x] Utilise MLX ou librairie similaire ✓
- [x] OOP et architecture modulaire ✓
- [x] Configuration via fichier JSON ✓
- [x] Gestion robuste d'erreurs ✓
- [x] A-Maze-ing package intégré ✓
- [x] Système de highscores persistant ✓
- [x] UI polished (menu, game view, game-over) ✓
- [x] Mode triche pour évaluation ✓
- [ ] Déployé sur Itch.io/Steam ✓

### General Rules

- [x] Python 3.10+ ✓
- [x] Adhère à flake8 (`make lint`) ✓
- [x] Gestion d'exceptions complète ✓
- [x] Ressources gérées correctement ✓
- [x] Type hints sur tout (`mypy`) ✓
- [ ] Docstrings (PEP 257) ✓

### Makefile

- [x] `make install` ✓
- [x] `make run` ✓
- [x] `make debug` ✓
- [x] `make clean` ✓
- [x] `make lint` ✓
- [x] `make lint-strict` (optionnel) ✓
- [x] `make test` ✓

### Game Loop

- [x] Main Menu > Start > Win/Lose > Highscore > Menu ✓

### Project Management

- [x] Timeline, progress tracking ✓
- [x] Risk analysis ✓
- [x] Team organization ✓
- [x] Acceptance test plan (CE DOCUMENT) ✓

### README Requirements

- [x] Premier ligne italicisée (42 curriculum) ✓
- [x] Description ✓
- [x] Instructions ✓
- [x] Resources ✓
- [x] Configuration ✓
- [x] Highscore ✓
- [x] Maze Generation ✓
- [x] Implementation ✓
- [x] General Software Architecture ✓
- [x] Project Management ✓

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

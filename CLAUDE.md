# CLAUDE.md — Guide IA pour le projet Pacman

## 1) Objectif
Ce fichier définit le **mode opératoire recommandé pour une IA de développement** (Claude, Copilot, etc.) sur ce dépôt.
Priorités:
1. Corriger/implémenter avec le **minimum de changements**.
2. Respecter l’architecture modulaire existante.
3. Valider avec des tests ciblés puis globaux.

---

## 2) Contexte technique
- Langage: **Python 3.10+**
- UI: **pygame 2.5.2**
- Typage/lint: **mypy**, **flake8**
- Tests: **pytest**
- Gestion env/exec: **uv** + `.venv`
- Entrée principale: `pac-man.py`

Commandes utiles:
- Installation: `make install`
- Lancer le jeu: `make run`
- Tests complets: `make test`
- Lint: `make lint`
- Lint strict: `make lint-strict`

---

## 3) Carte rapide du code
- `src/config/` : chargement/validation de configuration JSON (avec commentaires)
- `src/game/` : orchestration globale, boucle, état, niveaux, collisions
- `src/entities/` : Pac-Man, fantômes, pellets, IA fantômes
- `src/maze/` : génération/adaptation labyrinthe, tiles
- `src/ui/` : renderer + scènes (menu, jeu, pause, game over, highscores)
- `src/input/` : gestion clavier + mapping touches
- `src/highscore/` : persistance des scores
- `src/cheat/` : mode triche
- `src/utils/` : constantes, exceptions, logger, types
- `tests/` : suites unitaires par module

---

## 4) Workflow IA recommandé (obligatoire)
### Étape A — Comprendre avant d’éditer
1. Lire le module cible + ses dépendances directes.
2. Identifier les tests existants liés (`tests/test_*.py`).
3. Vérifier si la modification touche API, état global, ou rendu.

### Étape B — Modifier proprement
1. Changer le moins de fichiers possible.
2. Préserver les signatures publiques sauf demande explicite.
3. Éviter le refactor large non demandé.
4. Conserver style/naming/organisation déjà en place.

### Étape C — Valider
1. Exécuter d’abord les tests ciblés (ex: `pytest tests/test_ui.py -q`).
2. Exécuter ensuite une passe plus large (`make test`) si impact transverse.
3. Si pertinent: `make lint`.

### Étape D — Livrer
Toujours fournir:
- ce qui a été modifié,
- pourquoi,
- quels tests ont été exécutés,
- risques restants éventuels.

---

## 5) Contraintes fonctionnelles importantes
1. **Config JSON commentée**: support de `#` et `//`.
2. **Génération labyrinthe**: dépend d’une wheel externe assignée; comportement attendu stable et jouable.
3. **Seed niveau 1 fixe**, niveaux suivants variables (selon config/gestion niveau).
4. **Timer niveau**: à `0`, perte de vie et redémarrage niveau si vies restantes (comportement documenté README).
5. **Highscores**: robustes aux fichiers manquants/corrompus, top 10, validation nom.
6. **Mouvement grille**: déplacements par tuiles, collisions murs strictes.

---

## 6) Règles qualité code
- Favoriser petites fonctions testables.
- Éviter la logique dupliquée (factoriser localement si nécessaire).
- Ajouter des annotations de types sur nouveau code.
- Lever des exceptions métier explicites plutôt que des erreurs silencieuses.
- Logs utiles pour erreurs de config/IO, sans bruit excessif.

---

## 7) Stratégie de test rapide par zone
- Config: `tests/test_config.py`
- IA/fantômes: `tests/test_ai.py`
- Entités: `tests/test_entities.py`
- Boucle/état: `tests/test_game_loop.py`, `tests/test_gamestate.py`
- UI: `tests/test_ui.py`
- Labyrinthe: `tests/test_maze.py`
- Highscore: `tests/test_highscore.py`
- Input: `tests/test_input.py`
- Cheat mode: `tests/test_cheat_mode.py`

Règle: exécuter au minimum la/les suite(s) impactée(s), puis élargir en cas de doute.

---

## 8) Anti-patterns à éviter
- Changer simultanément gameplay + UI + persistance sans nécessité.
- Introduire des dépendances externes non nécessaires.
- Casser la compatibilité de `config.json`.
- Modifier les tests pour “forcer le vert” sans corriger la cause.
- Coupler fortement la logique de jeu à pygame (préserver testabilité).

---

## 9) Définition de “task done” pour l’IA
Une tâche est terminée seulement si:
1. Le comportement demandé est implémenté.
2. Les tests pertinents passent.
3. Aucun effet de bord évident n’est introduit.
4. Le diff reste minimal et cohérent avec l’architecture.
5. Le compte-rendu final est clair et actionnable.

---

## 10) Format de réponse recommandé pour l’IA
1. **Résumé** (1-3 lignes)
2. **Fichiers modifiés**
3. **Validation** (tests/lint exécutés)
4. **Risques ou next steps** (si applicable)

---

## 11) Notes pratiques
- En cas d’ambiguïté produit, se référer d’abord à:
  1) `README.md`
  2) `doc/ACCEPTANCE_TEST_PLAN.md`
  3) `doc/ARCHITECTURE.md`
- Préférer des correctifs incrémentaux à faible risque.
- Si un bug n’est pas reproductible: ajouter instrumentation/logging minimal avant refactor.

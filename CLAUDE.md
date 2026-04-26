# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate

# Load initial data
python manage.py loaddata apps/content/fixtures/initial_vocabulary.json
python manage.py loaddata apps/games/fixtures/logros_iniciales.json

# Dev server
python manage.py runserver  # http://127.0.0.1:8000/

# Tests
python manage.py test
python manage.py test apps.games  # single app
```

## Architecture Overview

**Project layout:** `config/` holds settings and root URLs; `apps/` holds all Django apps; `manage.py` is at the root.

**Settings:** `config/settings/base.py` (shared) + `config/settings/development.py` (SQLite, DEBUG=True). `config/settings/__init__.py` imports from development by default.

**Apps:**
- `accounts` — custom user model with profesor/estudiante roles, profiles, salones (classrooms)
- `content` — bilingual (ES/EN) vocabulary categories and items with images/audio
- `games` — all game logic: scoring, achievements, store (tienda), virtual room (habitación), artwork gallery (museo)
- `core` — abstract base models, context processors, static pages

**URL prefixes:**
```
/accounts/   → auth, dashboards, profiles, salones
/contenido/  → vocabulary categories
/juegos/     → games, ranking, tienda, habitacion, museo, logros
/admin/      → Django admin
```

## Key Patterns

**Custom user model:** `accounts.CustomUser` (extends AbstractUser). Fields: `role` (profesor/estudiante), `huesos` (virtual currency "Milo bones"), `avatar`. Always use `AUTH_USER_MODEL` / `get_user_model()`.

**Auto-created profiles via signals** (`apps/accounts/signals.py`): When a `CustomUser` is saved, a `ProfesorProfile` or `EstudianteProfile` is auto-created based on `role`. Never create profiles manually.

**Role-based access:** Use `@profesor_required` / `@estudiante_required` decorators from `apps.accounts.decorators`. Both redirect with error messages if the role doesn't match.

**Leveling system:** Students earn points → levels (non-linear scaling). Level-up awards 5 bones and logs a `HuesoTransaccion`. Max level: 50. Points per level scale in four tiers — Principiante (1–10): 20–380 pts, Intermedio (11–20): 460–1640 pts, Avanzado (21–30): 1840–4540 pts, Experto (31–40): 5000–11300 pts, Maestro (41–49): 12300–24000 pts. All values are defined in `EstudianteProfile.PUNTOS_POR_NIVEL`.

**Game types** (defined in `Game.GAME_TYPES`): `drag_and_drop`, `word_search`, `puzzle`, `audio_matching`, `painting`, `memoria`, `ahorcado`, `quiz`, `ordenar_letras`, `globos`. Each type maps to its own template in `apps/games/templates/games/`. Professors select the type when creating a game; `game_detail` view routes to the correct template via `template_map`.

**Game scoring utilities** (in `apps/games/`): `clasificar_puntaje()` converts score% to letter grade; `pct_to_nota()` converts to Colombian 1–5 scale.

**Abstract base models** (`apps/core/models.py`): `TimeStampedModel` (adds `created_at`/`updated_at`) and `ActiveModel` (adds `is_active` + custom manager). Most models inherit from one or both.

**Context processors** (registered globally): `milo_messages` (random Milo character greetings) and `global_context` (app name, slogan, user role) — available in all templates.

**Static/media:** WhiteNoise serves static files. Media root is `/media/` (avatars, vocabulary images, artwork). Run `collectstatic` before deploying.

**Language/locale:** Spanish (es-co), timezone America/Bogota. All user-facing strings should be in Spanish.

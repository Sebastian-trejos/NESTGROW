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
python manage.py loaddata apps/games/fixtures/tienda_inicial.json
python manage.py loaddata apps/historia/fixtures/logros_historia.json
python manage.py loaddata apps/historia/fixtures/modo_historia.json

# Seed historia content
python manage.py seed_historia

# Dev server
python manage.py runserver  # http://127.0.0.1:8000/

# Tests
python manage.py test
python manage.py test apps.games
```

## Architecture Overview

**Project layout:** `config/` holds settings and root URLs; `apps/` holds all Django apps; `manage.py` is at the root.

**Settings:** `config/settings/base.py` (shared) + `config/settings/development.py` (SQLite, DEBUG=True).
`config/settings/__init__.py` imports from development by default.
Environment variables loaded from `.env` via `django-environ`. External API keys: `GEMINI_API_KEY`, `GROQ_API_KEY`, `MYMEMORY_API_KEY`.

**Apps:**
- `accounts` — custom user model with profesor/estudiante roles, profiles, salones (classrooms)
- `content` — bilingual (ES/EN) vocabulary categories and items with images/audio
- `games` — all minigame logic: scoring, achievements, store (tienda), virtual room (habitación), artwork gallery (museo)
- `talleres` — professor-created workshops + Períodos system for activity management
- `historia` — story mode with unlockable sections, lessons, and per-activity progress tracking
- `core` — abstract base models, context processors, static pages

**URL prefixes:**
```
/accounts/   → auth, dashboards, profiles, salones
/contenido/  → vocabulary categories
/juegos/     → minigames catalog, ranking, tienda, habitacion, museo, logros
/talleres/   → workshops (CRUD) + Períodos management + student "Mis Actividades" panel
/historia/   → story mode map, lesson player, professor unlock panel
/admin/      → Django admin
```

## Key Patterns

**Custom user model:** `accounts.CustomUser` (extends AbstractUser).
Fields: `role` (profesor/estudiante), `huesos` (virtual currency "Milo bones"), `avatar`.
Always use `AUTH_USER_MODEL` / `get_user_model()`.

**Auto-created profiles via signals** (`apps/accounts/signals.py`):
When a `CustomUser` is saved, a `ProfesorProfile` or `EstudianteProfile` is auto-created.
Never create profiles manually.

**Role-based access:** Use `@profesor_required` / `@estudiante_required` decorators from `apps.accounts.decorators`.

**Leveling system:** Students earn points → levels (non-linear scaling). Level-up awards 5 bones and logs a `HuesoTransaccion`.
Max level: 50. Points per level defined in `EstudianteProfile.PUNTOS_POR_NIVEL`.
Tiers: Principiante (1–10), Intermedio (11–20), Avanzado (21–30), Experto (31–40), Maestro (41–49).

**Minigame types** (defined in `Game.GAME_TYPES`):
`drag_and_drop`, `word_search`, `puzzle`, `audio_matching`, `painting`,
`memoria`, `ahorcado`, `quiz`, `ordenar_letras`, `globos`.
Each type maps to its own template in `apps/games/templates/games/`.
The `game_detail` and `game_embed` views route to the correct template via `template_map`.

**Minigame completion flow:**
1. Student plays → JS calls `save_score` (AJAX POST to `/juegos/save-score/`)
2. `save_score` saves `Score` + `UserProgress`, creates `RegistroMinijuegoPeriodo` if game belongs to active period, returns `registro_pk`
3. Win overlay shows single button "✔️ Volver al panel" → redirects to `/talleres/mis-talleres/?revisado=<pk>`
4. `mis_talleres` view marks `RegistroMinijuegoPeriodo.revisado = True` → game disappears from both the panel and `/juegos/` list

**Game scoring utilities** (`apps/games/models.py`):
`clasificar_puntaje()` converts score% to letter grade; `pct_to_nota()` converts to Colombian 1–5 scale.

**Abstract base models** (`apps/core/models.py`):
`TimeStampedModel` (adds `created_at`/`updated_at`) and `ActiveModel` (adds `is_active` + custom manager).
Most models inherit from one or both.

**Context processors** (registered globally):
`milo_messages` (random Milo character greetings) and `global_context` (app name, slogan, user role).

**WebSockets (Django Channels):** `apps/core/consumers.py` — `NotificationConsumer` pushes real-time events per user via group `usuario_<pk>`.
Events: `nivel_subido`, `huesos_ganados`, `taller_disponible`, `seccion_desbloqueada`.

**Talleres (Workshops):**
A `Taller` has ordered `BloqueTaller` records. Each bloque is `pregunta` or `minijuego`.
`BloquePregunta` supports opcion_multiple / casillas / parrafo.
`BloqueMinijuego` embeds an existing `Game`.
Student answers → `RespuestaEstudiante`; session state → `SesionTaller` (fields: `completada`, `revisado`, `puntos_obtenidos`, `bloque_actual`).
Completing a taller unlocks vocabulary from `categorias_vocabulario`.
After completion, student is redirected to `resultado_sesion` — clicking "Entendido" marks `SesionTaller.revisado = True` and the taller disappears from the panel.

**Períodos (Periods system) — `apps/talleres/`:**
A `Periodo` belongs to a `Salon` and has a `fecha_fin` deadline.
It assigns up to 5 talleres (`AsignacionTaller`) and up to 5 minigames (`AsignacionMinijuego`), plus an optional `meta_historia` (star target).
`RegistroMinijuegoPeriodo` tracks per-student minigame completion within a period.
Student panel (`/talleres/mis-talleres/`) shows only the active period's pending activities.
Completed + revisited activities disappear automatically.
Professor results (`/talleres/periodos/<pk>/resultados/`) shows a table: student × taller grade + minigame % + history stars.
Period is closed manually by professor (sets `cerrado=True`, freezes results).

Professor URL routes:
- `GET/POST /talleres/periodos/crear/` → `crear_periodo`
- `GET /talleres/periodos/` → `lista_periodos`
- `GET /talleres/periodos/<pk>/resultados/` → `resultados_periodo`
- `POST /talleres/periodos/<pk>/cerrar/` → `cerrar_periodo`

Student URL routes:
- `GET /talleres/mis-talleres/` → `mis_talleres` (filtered by active period)
- `GET/POST /talleres/sesion/<pk>/resultado/` → `resultado_sesion` (marks taller as revisado)

**Historia (Story Mode):**
Content hierarchy: `SeccionHistoria` → `Leccion` → `ActividadLeccion`.
Sections unlocked per `Salon` by professor (`SeccionDesbloqueada`) or flagged `is_desbloqueada_por_defecto`.
Activity `datos` is a free-form JSONField (schema depends on `tipo`: introduccion, vocabulario, listening, reading, writing, minijuego_embed, dialogo, pronunciacion).
Progress: `ProgresoLeccion` (per student × lesson, estrellas 1–3) + `RespuestaActividad`.
Achievement logic: `apps/historia/services.py` (`verificar_logros_historia`); PKs 101–118 must match `logros_historia.json`.

**Tienda (Store):** `TiendaItem` — items with `precio_huesos`, `imagen`, `posicion_habitacion`, optional `juego_desbloqueado`.
`InventarioEstudiante` tracks purchased items. Items loaded via `tienda_inicial.json` (13 items, PKs 1–13).
Items 9–13 correspond to the 5 newer minigames (Memoria, Ordenar Letras, Quiz, Globos, Ahorcado).

**Naming conventions (UI):**
- "Minijuegos" = the learning games at `/juegos/` (NOT "Juegos")
- "Mis Actividades" = the student panel at `/talleres/mis-talleres/` (NOT "Talleres")
- "Juegos de la Habitación" = the decoration/entertainment games in Habitación de Milo

**Custom password validator:** `apps/accounts/validators.ContainsNumberValidator` — enforces at least one digit.

**Static/media:** WhiteNoise serves static files. Media root is `/media/`.
Run `collectstatic` before deploying.

**Language/locale:** Spanish (es-co), timezone America/Bogota. All user-facing strings must be in Spanish.

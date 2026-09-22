# awake/world — Build 0.4.1 · Living City

**Canonical identity:** `awake/world — THE LIVING NETWORK`

This is the consolidated **Build 0.4.1**. It is not a patch package and does not require any previous Awake World folder.

## Start on Windows

1. Extract the entire ZIP to a normal folder.
2. Open that folder.
3. Double-click **`RUN_AWAKE_WORLD.cmd`**.

The launcher does the rest automatically:

- finds Python 3;
- requires Python 3.11+;
- creates a project-local `.venv`;
- installs the pinned PySide6 runtime if needed;
- validates the project;
- runs pure core-system tests;
- runs an offscreen Qt/world smoke test;
- launches Awake World only if validation succeeds.

No PowerShell execution-policy change is required when using `RUN_AWAKE_WORLD.cmd`.

> The first launch needs internet access only if PySide6 6.11.2 is not already available in the local `.venv`/pip cache.

## Alternate commands

- `start_awake.cmd` — same launcher, shorter filename.
- `verify_awake.cmd` — installs/checks dependencies and runs validation without opening the game.
- `start_awake.ps1` — fallback PowerShell entry point; the `.cmd` launcher remains recommended.

## Controls

- `WASD` / arrows — move
- `Shift` — run
- `E` — contextual interaction
- `T` — cycle world-light phase
- `I` — field notes
- `F3` — WORLD DEBUG
- mouse wheel — zoom

## Build 0.4.1 world

The new default entry is **Awake Quarter**, a district rather than a menu/hub. The current district contains:

- Central Plaza
- The Observatory — Caio / Monks
- The Grid — Bx
- Twin Core — Bruno Kuss + Vitor Kuss
- Trinity Lab — Felipe Gomes + Fifz + Tapita
- The Garage — Thaynan Arruda
- Kawaii Garden — Theus
- The Pit — Cabessa + Danilo Pilsen
- The Glasshouse — Pure Rodrigo Valerio

The four authored Build 0.4 spaces are retained for compatibility:

- Headquarters
- Plaza
- Rooftop
- Home

## Living City systems

The consolidated runtime contains:

- `WorldState` save schema v5
- `EventBus`
- `WorldRuntime`
- `TimeSystem`
- `WeatherSystem`
- `LightingSystem`
- `AudioZoneSystem`
- `InteractionSystem`
- `PresenceSystem`
- `MicroEventSystem`
- `NPCSystem`
- `SpaceSystem`
- `PerformanceSystem`
- Simulation LOD foundation
- data-driven space catalog

Space contracts:

- `PersonalSpace`
- `SharedStudio`
- `SocialSpace`
- `PublicBuilding`

### Weather

Initial systemic loop:

- CLEAR
- CLOUDY
- RAIN

Weather is persisted and propagated through the runtime/EventBus. Scenes render a weather wash and rain layer while simulation state remains presentation-independent.

### Microevents

Current catalog:

- delivery
- dog in plaza
- rooftop session
- power flicker
- server issue
- street musician

Active microevents persist across saves.

### Time / day-night

World time is simulation state, not a widget-only value. The runtime publishes time and sunset events while scene presentation continues to use the existing efficient 2.5D lighting implementation.

### Presence

The local-player presence record is represented physically by the runtime and persisted in v5 state. The API already separates presence state from presentation so it can later become server-authoritative without rewriting room rendering.

### NPC foundation

Logical schedules exist for the first Living City residents/services, including barista, courier, maintenance and Momo. Distant simulation can remain logical-only while nearby authored NPCs continue to use the existing scene animation/path routines.

## WORLD DEBUG — F3

The debug panel mutates the actual simulation state. It currently includes:

- time: 06:00 / 12:00 / 18:00 / 00:00
- weather: CLEAR / CLOUDY / RAIN
- events: DELIVERY / BLACKOUT / DOG / ROOFTOP
- teleport: Quarter / Observatory / Twin Core / Trinity / Pit / Garden / Plaza / Glasshouse

## Persistence

Default save path:

```text
C:\Users\<you>\.awake_world\single_player_save.json
```

Build 0.4.1 preserves/migrates the earlier single-player fields and adds:

- weather + intensity
- active microevents
- per-space state
- NPC logical state
- presence state

Writes use a temporary file followed by replace to reduce partial-save corruption.

## Performance baseline

Current engineering budgets:

- target: 60 FPS
- CPU simulation budget: 8 ms/frame
- render/GPU target: 12 ms/frame
- RAM target: 900 MB
- VRAM assumption: 768 MB baseline
- active full-simulation NPC budget: 18
- dynamic/key light budget: 10
- audio-source budget: 20
- rain-streak budget: 64
- NPC simulation LOD: `full / reduced / logical_only`

The strategy is perceived complexity over brute-force simulation: vector/procedural composition, grouped lighting, deterministic routines, state-driven variation and graceful fallbacks.

## Validation pipeline

Every normal launch runs three gates before opening the game:

1. `tools/static_validate.py`
2. `tools/core_test.py`
3. `tools/smoke_test.py` with Qt in offscreen mode

The smoke test constructs all legacy rooms and Awake Quarter spaces, applies night/rain state, advances ambient animation, creates the main window, changes time and emits a runtime snapshot.

## Architecture boundary

Build 0.4.1 remains **single-player first**. FastAPI, SQLAlchemy async, PostgreSQL, Redis, WebSockets and WebRTC remain future network/server layers. The current client architecture avoids placing authoritative simulation logic exclusively inside widgets so those systems can be replicated later.

See `ARCHITECTURE_BUILD_04_LIVING_CITY.md` for the migration boundary and module map.

# awake/world — 0.6.0-dev · THE LIVING QUARTER

**Canonical identity:** `awake/world — THE LIVING NETWORK`

Awake World is now in the **0.6 MVD development cycle**, built on the frozen **v0.5.0 GLOBAL** release. The Interaction + Experience Bible v1 remains normative. 0.6 evolves the entire world as one coherent visual and spatial system: one language, multiple local dialects.

## Windows release

The stable public baseline remains **v0.5.0 GLOBAL** while 0.6 is under development.

1. Download `AwakeWorld_0.5_GLOBAL_Windows.zip` from the GitHub release.
2. Extract the full ZIP.
3. Run **`AWAKE_WORLD.exe`**.

The packaged Windows build does **not** require a local Python installation.

## Source / development launch

Python 3.11+ is required when running from source.

- `RUN_AWAKE_WORLD.cmd` — canonical Windows source launcher.
- `start_awake.cmd` — equivalent short launcher.
- `verify_awake.cmd` — validates the source build without opening the world.
- `python run.py` — direct Python entry point in a prepared environment.

## 0.6 MVD — THE LIVING QUARTER

0.6 shifts the center of effort from infrastructure to world quality. The method is transversal: every MVD cycle improves all applicable environments through shared systems rather than polishing one room at a time.

Current sequence:

- **MVD-0:** visual grammar foundation;
- **MVD-1:** massing + scale;
- **MVD-2:** materials + light;
- **MVD-3:** subtle life;
- **MVD-4:** spatial interaction integration;
- **MVD-5:** human acceptance + golden freeze.

See `docs/AWAKE_WORLD_06_MVD_CANON.md`.

## 0.5 GLOBAL — frozen baseline

The release promotes Awake World from a Living City foundation into a deterministic interaction/runtime architecture.

### Experience contract

The canonical laws are:

- **THE SPACE IS THE INTERFACE**
- **SUBTLE LIFE**
- **PERCEIVED COMPLEXITY > RAW COMPLEXITY**
- stylized premium presentation;
- high-end experience with low-cost architecture;
- contextual proximity interaction instead of menu-first interaction;
- restrained motion, diegetic feedback and authored environmental life.

See `docs/AWAKE_WORLD_INTERACTION_EXPERIENCE_BIBLE_v1.md`.

### Simulation and movement

- deterministic fixed-step simulation at **60 Hz**;
- controllable world seed;
- replay recorder/player and deterministic gameplay drivers;
- acceleration/deceleration, normalized diagonals, smooth reversal and collision slide;
- explicit walk/run state and presentation interpolation.

### Camera and transitions

- contextual camera profiles;
- camera behavior separated from simulation state;
- authored space-transition orchestration instead of abrupt teleport presentation;
- deterministic transition timing suitable for tests and replay.

### NPCs, pets and ambient life

- schedule + FSM + utility-scoring actor behavior;
- context from time, weather, space and deterministic variation;
- simulation LOD for nearby versus distant actors;
- pet behavior integrated into the same runtime boundary;
- seeded ambient-life system for authored environmental motion.

### World systems

- Awake Quarter plus the authored legacy rooms;
- weather, lighting, time, audio zones, presence and microevents;
- interaction target scoring with contextual proximity behavior;
- diagnostics and world-state inspection through the F3 tools;
- spatial profiles remain data-driven and multiplayer-ready.

### Save and recovery

- **WorldState schema 6**;
- migration from schema 5;
- atomic save writes;
- backup/recovery path;
- corruption handling;
- deterministic state boundaries suitable for replay and future authoritative networking.

## Awake Quarter

Current connected district spaces:

- Central Plaza
- The Observatory — Caio / Monks
- The Grid — Bx
- Twin Core — Bruno Kuss + Vitor Kuss
- Trinity Lab — Felipe Gomes + Fifz + Tapita
- The Garage — Thaynan Arruda
- Kawaii Garden — Theus
- The Pit — Cabessa + Danilo Pilsen
- The Glasshouse — Pure Rodrigo Valerio

The earlier Headquarters, Plaza, Rooftop and Home spaces remain available for compatibility.

## Controls

- `WASD` / arrows — move
- `Shift` — run
- `E` — contextual interaction
- `T` — cycle world-light phase
- `I` — field notes
- `F3` — World Inspector / debug controls
- mouse wheel — zoom

## Validation and release gates

Every development or release candidate must pass:

- Python syntax and authored invariants;
- Ruff critical-error gate;
- mypy checks on pure boundaries;
- unit + deterministic simulation tests;
- save migration/recovery tests;
- core systems and gameplay drivers;
- Windows Qt offscreen smoke;
- deterministic visual regression;
- PyInstaller Windows build;
- packaged executable smoke;
- release ZIP integrity + SHA-256.

The release artifact is generated in GitHub Actions from the release source.

## Architecture

The main boundary is:

```text
SIMULATION → PRESENTATION ADAPTER → RENDERER
```

The current renderer remains PySide6 / QGraphicsScene. Simulation, presentation and future network authority are intentionally separated so multiplayer/server layers can be added without moving game rules into widgets.

## Persistence

Default local save path:

```text
C:\Users\<you>\.awake_world\single_player_save.json
```

## Canonical identifiers

- development version: **0.6.0-dev**
- frozen release baseline: **v0.5.0 GLOBAL**
- channel: **DEVELOPMENT**
- save schema: **6**
- simulation: **60 Hz fixed-step**
- Windows entry: **AWAKE_WORLD.exe**

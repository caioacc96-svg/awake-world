# awake/world — Build 0.4.1 Living City architecture

## Migration decision

Build 0.4.1 is an incremental migration, not a renderer rewrite. The existing PySide6/QGraphicsScene 2.5D layer, avatar, authored interactions, deterministic scene NPCs, Qt Multimedia fallback, design tokens and persistent progression remain useful and are preserved.

The structural change is the introduction of a simulation/runtime layer beneath presentation.

## State boundaries

```text
Simulation state
  WorldState v5
  WorldRuntime
    EventBus
    TimeSystem
    WeatherSystem
    PresenceSystem
    MicroEventSystem
    NPCSystem
    SpaceSystem
    LightingSystem
    AudioZoneSystem
    InteractionSystem
    PerformanceSystem

Presentation state
  QGraphicsScene / QGraphicsView
  BaseRoomScene + Awake Quarter scenes
  vector/procedural environment objects
  weather/light washes
  Qt Multimedia playback

Future network state
  FastAPI / WebSockets
  server-authoritative presence/events
  replicated state snapshots
  WebRTC media
```

No networking dependency is required for the current single-player build.

## Runtime ownership

`WorldRuntime` owns systemic state transitions and derived simulation state. Presentation subscribes to events and renders consequences. A weather system never imports Kawaii Garden; it publishes `WEATHER_CHANGED`, and scene/runtime consumers react independently.

`TimeSystem` is pure simulation code and exposes the API needed by the existing view while publishing `TIME_CHANGED` and `SUNSET_STARTED`.

`SpaceSystem` owns the data-driven Awake Quarter registry and current-space state. Legacy Build 0.4 rooms remain supported during migration.

`PresenceSystem`, `MicroEventSystem` and logical NPC state are serialized into `WorldState` so save/load restores more than a room identifier.

## Space architecture

Typed space contracts:

```text
SpaceDefinition
  PersonalSpace
  SharedStudio
  SocialSpace
  PublicBuilding
```

Current data-driven Awake Quarter registry:

```text
quarter
central_plaza
observatory
grid
twin_core
trinity_lab
garage
kawaii_garden
pit
glasshouse
```

Authored rooms use reusable modular geometry and distinct composition/palettes rather than one OfficeBuilding class or asset-store prefabs.

## Performance

Baseline budget:

```text
60 FPS target
8 ms CPU simulation
12 ms render/GPU target
900 MB RAM target
768 MB baseline VRAM assumption
18 nearby/full NPCs
10 dynamic/key lights
20 audio sources
64 rain streaks
```

Simulation LOD:

```text
< 12 tiles     full
12–32 tiles    reduced
> 32 tiles     logical_only
```

The intended scaling model is state/routine simulation at distance, full visual/path simulation only when perception requires it.

## Persistence

Save schema v5 retains earlier discoveries, toggles, visits, inventory, decor, journal and progression state, and adds:

```text
weather
weather_intensity
active_events
space_states
npc_states
presence
```

The write path remains temporary-file then replace.

## Launcher boundary

`RUN_AWAKE_WORLD.cmd` is the canonical Windows entry point. It invokes `launch_awake.py` directly through Python, avoiding PowerShell execution-policy dependence. The bootstrap creates a local `.venv`, installs the pinned Qt runtime if missing, then requires static validation, core-system tests and a Qt offscreen smoke test before launch.

This consolidates the earlier launcher/import fixes into the build itself rather than requiring external hotfix steps.

# AWAKE WORLD — INTERACTION + EXPERIENCE BIBLE v1

**Status:** CANONICAL  
**Applies to:** Awake World 0.5 GLOBAL and all future versions unless explicitly superseded  
**Identity:** `awake/world — THE LIVING NETWORK`  
**Primary Law:** **THE SPACE IS THE INTERFACE.**  
**Secondary Laws:** **SUBTLE LIFE.** · **PERCEIVED COMPLEXITY > RAW COMPLEXITY.**  
**Product Constraint:** **HIGH-END EXPERIENCE / LOW-COST ARCHITECTURE.**

---

## 0. Purpose

This document is the normative contract for how Awake World must **feel, respond, move, communicate and remain alive**.

It is not a feature list.  
It is not a visual moodboard.  
It is not an implementation plan.

It defines the standard that every system must satisfy before it is considered part of Awake World.

Any implementation that technically works but violates this Bible is incomplete.

The intended effect is:

- entering a place should feel like entering a place;
- interacting should feel spatial, not menu-driven;
- movement should feel deliberate, fluid and responsive;
- the city should remain interesting when the player stops;
- architecture, lighting, sound, NPCs, pets and interfaces should behave as one system;
- productivity features should emerge from the world instead of replacing it;
- the world should communicate presence without depending on sidebars;
- complexity should be perceived through coherent consequences, not brute-force simulation.

---

# 1. Product Experience Doctrine

## 1.1 The Space Is the Interface

Default interaction model:

```text
walk toward thing
→ thing becomes contextually legible
→ world acknowledges player
→ small prompt appears
→ interaction happens in-place
→ interface appears only if the task genuinely requires it
```

Examples:

```text
desk          → work
meeting table → meeting
TV/display    → screen sharing
project wall  → projects/tasks
sofa          → conversation
arcade        → play
door          → enter
physical file → documents
stage         → event
coffee counter→ social interaction
dog           → pet
```

A conventional panel may appear after interaction, but it must feel anchored to a physical source.

---

## 1.2 The World Must Exist Without the Player

The world must not look paused while waiting for input.

At any time, some low-intensity activity should be observable:

- vegetation motion;
- screen changes;
- light changes;
- environmental audio;
- NPC route;
- door use;
- pet behavior;
- server activity;
- coffee preparation;
- distant movement;
- window illumination;
- weather transition;
- microevent;
- subtle prop animation.

The rule is not “everything moves.”

The rule is:

> **Something is always quietly continuing.**

---

## 1.3 Subtle Life

Ambient activity must stay below the threshold of spectacle unless an event is intentionally important.

Avoid:

- constant flashing;
- excessive particle systems;
- every object animating;
- loud random events;
- NPCs pathing everywhere;
- UI animation competing with the world;
- environmental motion at identical timing.

Preferred:

- asynchronous small movements;
- staggered timing;
- occasional pauses;
- slow transitions;
- low-frequency environmental events;
- different rhythms by space and time of day.

---

## 1.4 Perceived Complexity > Raw Complexity

Always prefer:

```text
small coherent system
+ layered presentation
+ contextual variation
```

over:

```text
large expensive simulation
+ weak presentation
```

Examples:

- 10 recognizable NPCs > 100 meaningless NPCs;
- 15 modular props + composition > 100 unique props;
- stateful rain response > physically simulated weather;
- utility/FSM pet behavior > AI agent per pet;
- grouped lighting + emissives > hundreds of dynamic lights;
- contextual room tone > expensive acoustic simulation.

---

# 2. Core Experience Pillars

Every feature must strengthen at least one pillar.

## 2.1 Presence

The player should feel that people and systems occupy real places.

Presence is communicated by:

- physical location;
- doors;
- lights;
- occupancy;
- props in use;
- sound leakage;
- signage;
- meeting state;
- personal objects;
- NPC recognition;
- world reactions.

---

## 2.2 Continuity

Closing and reopening Awake World should feel like returning somewhere, not starting a fresh scene.

The world should preserve:

- time coherence;
- weather coherence;
- NPC state;
- meaningful space state;
- presence state;
- active/recent events;
- player position when appropriate;
- environment continuity.

---

## 2.3 Intimacy

Awake World should support small-scale human presence.

Preferred:

- small rooms;
- visible desks;
- recognizable personal spaces;
- quiet corners;
- believable seating;
- nearby sound;
- subtle environmental details.

Avoid monumental scale unless intentionally used for contrast.

---

## 2.4 Serendipity

Awake World must create unplanned encounters.

The city should allow:

- crossing paths;
- hearing activity before seeing it;
- seeing someone through glass;
- finding someone at the cafe;
- encountering a dog in the plaza;
- noticing a rooftop session;
- seeing a delivery arrive.

The system must reward wandering without turning wandering into a quest loop.

---

## 2.5 Legibility

The player should usually understand:

- what is interactive;
- what is private;
- where a path leads;
- who is present;
- whether a space is active;
- whether an interaction is available;
- what state the world is in.

Legibility should come primarily from world cues, not HUD.

---

# 3. Interaction Grammar

## 3.1 Default Interaction Sequence

Every contextual interaction should follow this model:

```text
DISCOVER
→ APPROACH
→ ACKNOWLEDGE
→ OFFER
→ COMMIT
→ RESPOND
→ SETTLE
```

### Discover
Object looks usable through form, placement, lighting, animation or context.

### Approach
Player enters a soft interaction radius.

### Acknowledge
Object subtly reacts before text appears where appropriate.

Examples:

- desk screen wakes;
- door light activates;
- dog looks toward player;
- chair highlight subtly increases;
- TV status LED activates.

### Offer
Minimal interaction prompt appears.

Example:

```text
E
WORK
```

### Commit
The player presses the interaction key.

### Respond
World reacts immediately.

### Settle
Final state is established without abrupt UI discontinuity.

---

## 3.2 Interaction Prompt Rules

Prompts must be:

- small;
- contextual;
- stable;
- near the relevant world object or in a consistent unobtrusive screen region;
- visible only when actionable.

Avoid:

- giant floating labels;
- prompts for distant objects;
- multiple competing prompts;
- constantly flickering target changes;
- tutorial paragraphs during normal play.

---

## 3.3 Target Selection

InteractionSystem must score candidates using:

```text
distance
+ facing alignment
+ screen relevance
+ interaction priority
+ line-of-sight when required
+ current context
```

Use hysteresis.

Once a target is selected, a slightly better candidate must not immediately steal focus.

Recommended behavior:

```text
candidate must exceed current target score by threshold
before focus changes
```

This prevents prompt flicker.

---

## 3.4 Forgiveness

Interaction radius should be slightly more forgiving than visible geometry.

Do not require pixel-perfect positioning.

Recommended principles:

- target may remain active briefly while player drifts away;
- interaction can still complete during a short movement transition;
- chairs, doors and desks use generous contextual zones;
- precise positioning happens after commit, not before it.

---

## 3.5 Interaction Types

### TAP

For immediate actions:

- pet;
- open door;
- sit;
- inspect;
- activate;
- enter.

### HOLD

Use sparingly.

Only where sustained intention matters:

- destructive action;
- leaving a meeting while presenting;
- privacy-sensitive action;
- long system operation.

Hold should not be default interaction design.

---

## 3.6 Cancel

Interaction cancellation must be predictable.

Default:

```text
Esc / movement away / contextual cancel
```

Cancellation should not trap the player in modal UI unless technically necessary.

---

# 4. Interaction Classes

## 4.1 Door

Door is one of the most important Awake interactions.

Sequence:

```text
approach
→ proximity state
→ subtle architectural response
→ prompt
→ commit
→ door movement
→ camera adjustment
→ audio crossfade
→ space handoff
→ placement
→ door settles
```

No instant teleport unless:

- emergency fallback;
- debug mode;
- technically unavoidable and hidden by transition.

---

## 4.2 Desk

Approach:

- monitor wakes;
- desk lamp may respond;
- prompt appears.

Commit:

```text
E
WORK
```

Then:

- player aligns naturally;
- chair or standing state resolves;
- workspace UI appears anchored to the desk;
- environment remains visible where possible.

Exit returns naturally to the room.

---

## 4.3 Meeting Table

Approach:

```text
E
JOIN
```

If inactive:

```text
E
START MEETING
```

Meeting state may affect:

- lighting;
- privacy;
- exterior status;
- display;
- audio routing;
- seat occupancy.

---

## 4.4 TV / Display

Possible actions:

```text
E
PRESENT

E
WATCH

E
SHARE SCREEN
```

Large interface should emerge from the display itself.

---

## 4.5 Project Wall

Interaction opens:

- projects;
- tasks;
- status;
- shared notes.

But the wall must maintain visible physical state even without opening UI.

Examples:

- active project cards;
- progress;
- latest build;
- upcoming event.

---

## 4.6 Sofa / Social Seating

Primary behavior:

```text
E
SIT
```

Sitting should:

- modify camera slightly;
- reduce locomotion noise;
- create a social-ready state;
- potentially affect presence.

Avoid automatically launching chat UI.

---

## 4.7 Coffee

Coffee is a social object first, productivity object second.

Possible:

```text
E
ORDER

E
SIT

E
TALK
```

Coffee interactions should support ambient social behavior, not become a minigame.

---

## 4.8 Arcade

Arcade may launch a minigame.

Transition:

```text
approach machine
→ machine wakes
→ E PLAY
→ player anchors
→ minigame surface expands
```

Return must be immediate and preserve world continuity.

---

## 4.9 File / Document Object

Physical file, cabinet or terminal may expose documents.

Use:

```text
E
OPEN
```

Document UI may be conventional once opened.

The physical source must remain clear.

---

## 4.10 Pet

Preferred:

```text
E
PET
```

Response should be immediate.

Possible reactions:

- look;
- approach;
- tail movement;
- sit;
- brief follow;
- continue activity.

No mandatory reward loop.

---

# 5. Movement Feel Contract

Movement is a product feature.

A technically correct controller that feels rigid fails acceptance.

## 5.1 Movement Pipeline

```text
INPUT
→ desired_direction
→ desired_velocity
→ acceleration
→ velocity smoothing
→ collision
→ actor state
→ animation
→ camera response
→ footstep response
```

---

## 5.2 Required Qualities

Movement must feel:

- responsive;
- deliberate;
- smooth;
- grounded;
- readable;
- predictable.

It must not feel:

- slippery;
- binary;
- delayed;
- floaty;
- grid-locked;
- like a UI cursor.

---

## 5.3 Starting Tuning Ranges

These are baseline tuning ranges, not permanent constants.

### Walk

```text
target speed:       115–150 px/s equivalent
accel to target:    120–220 ms
deceleration:       140–260 ms
```

### Run

```text
target speed:       190–250 px/s equivalent
ramp-up:            160–300 ms
```

### Direction Change

Sharp reversal should not instantly flip full velocity.

Use controlled transition:

```text
old velocity
→ decelerate
→ redirect
→ accelerate
```

but preserve responsiveness.

---

## 5.4 Diagonal Movement

Normalize diagonal magnitude.

The player must not move faster diagonally.

---

## 5.5 Stop Precision

When input stops:

- player should settle accurately;
- no excessive sliding;
- interaction targets should remain stable;
- camera should settle shortly after.

---

## 5.6 Fixed-Step Simulation

Simulation tick must be independent of render FPS.

Suggested baseline:

```text
simulation: 60 Hz
```

If performance requires:

```text
30 Hz simulation + interpolation
```

may be accepted only if movement remains fluid.

---

## 5.7 Input Buffer

A very short interaction buffer may be used.

Example:

```text
player presses E slightly before entering valid range
→ action can trigger when valid within ~100–150 ms
```

Use only where it improves feel.

---

# 6. Camera Grammar

Camera should be invisible as a system.

## 6.1 Priorities

Order:

1. responsiveness;
2. clarity;
3. comfort;
4. atmosphere.

Never sacrifice responsiveness for cinematic float.

---

## 6.2 Camera Follow

Use:

- soft follow;
- damping;
- small dead zone;
- subtle look-ahead.

Avoid:

- large lag;
- overshoot;
- continuous bobbing;
- aggressive zooming.

---

## 6.3 Open Areas

Central Plaza / streets:

- slightly wider framing;
- more look-ahead;
- preserve landmarks;
- allow anticipation of movement.

---

## 6.4 Interior

Interior:

- tighter framing;
- less look-ahead;
- stronger stability;
- preserve interactable readability.

---

## 6.5 Contextual Camera

Camera may subtly adjust for:

- sitting;
- working;
- entering building;
- rooftop;
- meeting;
- arcade;
- stage/event.

Transitions should usually be:

```text
180–600 ms
```

depending on magnitude.

---

# 7. Space Transition Grammar

Transitions define whether Awake feels like one world or disconnected rooms.

## 7.1 Standard Interior Entry

```text
1. player approaches entrance
2. building acknowledges presence
3. door animates
4. exterior sound begins fading
5. camera reframes
6. lighting profile shifts
7. scene/state handoff occurs
8. player appears at coherent interior entry point
9. room tone becomes dominant
10. door settles
```

Target duration:

```text
500–1200 ms
```

---

## 7.2 Transition Profiles

Required profiles:

- exterior → interior;
- interior → exterior;
- rooftop;
- subterranean;
- garden;
- laboratory;
- social venue.

Each profile may define:

- camera;
- audio crossfade;
- light adaptation;
- door timing;
- spawn offset;
- weather attenuation;
- movement lock duration.

---

## 7.3 Movement Lock

Never freeze longer than necessary.

If movement must temporarily lock:

- keep duration short;
- preserve animation;
- preserve camera motion;
- preserve world activity.

---

# 8. Ambient Life System

## 8.1 Categories

### Vegetation

- leaves;
- grass;
- branch sway;
- rain response.

### Architecture

- doors;
- blinds;
- windows;
- signs;
- elevators;
- fans.

### Technology

- monitors;
- LEDs;
- servers;
- displays;
- printers;
- status panels.

### Atmosphere

- clouds;
- shadows;
- reflections;
- steam;
- smoke;
- distant traffic;
- rain.

### Social

- NPC movement;
- seating;
- coffee;
- conversation gestures;
- deliveries;
- maintenance.

### Animals

- wandering;
- sleeping;
- observing;
- following;
- shelter seeking.

---

## 8.2 Timing

Ambient effects must avoid synchronized loops.

Use:

- random offsets with fixed seed;
- event windows;
- state-based variation;
- low-frequency changes;
- staggered activation.

---

# 9. NPC Experience Contract

NPCs must be coherent before being numerous.

## 9.1 Behavior Stack

Preferred:

```text
schedule
+ FSM
+ utility scoring
+ context
+ weather
+ space state
+ small seeded variation
```

---

## 9.2 Required NPC States

Baseline:

- Idle;
- Walk;
- Observe;
- Work;
- Sit;
- Socialize;
- Eat/Drink;
- EnterSpace;
- LeaveSpace;
- WeatherResponse;
- NightBehavior.

Role-specific states extend this set.

---

## 9.3 Schedules

Schedules should create recognizable behavior.

Example:

```text
BARISTA

07:40 arrive
08:00 open
10:12 wipe counter
12:30 lunch
14:03 short conversation
17:30 clean
18:00 close
18:10 leave
```

Small jitter is allowed.

The core routine remains recognizable.

---

## 9.4 Pauses Matter

NPCs must not move continuously.

Useful behaviors:

- stop;
- look;
- wait;
- check device;
- sit;
- drink;
- observe player;
- turn toward sound;
- resume.

Pauses create perceived intentionality.

---

## 9.5 Recognition

Player should eventually recognize:

- the barista;
- delivery NPC;
- maintenance NPC;
- recurring passerby.

Identity > crowd size.

---

# 10. Pet Experience Contract

Kawaii Garden pets are a major emotional-life system.

## 10.1 Baseline States

```text
Idle
Wander
Sniff
Observe
Follow
Sit
Play
Eat
Sleep
SeekShelter
```

---

## 10.2 Utility Influences

Examples:

```text
RAIN
→ SeekShelter ↑

NIGHT
→ Sleep ↑

PLAYER NEAR
→ Observe / Follow ↑

FOOD
→ Eat ↑

OWNER SPACE
→ proximity preference ↑
```

---

## 10.3 Pet Rhythm

Dogs should not constantly seek the player.

They should appear to have their own life.

---

# 11. Weather Experience Contract

Weather is a global system with local consequences.

## 11.1 Initial States

```text
CLEAR
CLOUDY
RAIN
```

---

## 11.2 Rain Must Affect

At minimum:

- sky;
- ambient tint;
- ground;
- reflections;
- audio;
- windows;
- NPC behavior;
- pet behavior;
- outdoor density;
- cafe occupancy tendency;
- material response;
- visibility;
- rooftop activity.

Rain that only draws particles fails acceptance.

---

## 11.3 Local Rain Audio

Different surfaces must have distinct rain character:

```text
glass
metal roof
vegetation
concrete
open air
```

No advanced acoustic simulation required.

---

# 12. Time + Lighting Experience Contract

## 12.1 Time Bands

Suggested canonical rhythm:

```text
07:00 city waking
08:00 cafe opens
09:00 professional activity
12:00 lunch flow
14:00 normal activity
17:00 sunset begins
19:00 urban lighting
21:00 social activity
00:00 low activity
03:00 near empty
```

---

## 12.2 Sunset

Sunset is a signature Awake moment.

It must create:

- strong light transition;
- changed window color;
- longer shadows;
- warmer interiors;
- increased rooftop/plaza appeal;
- subtle audio shift;
- visible city transformation.

---

## 12.3 Night

Night should not equal “dark daytime.”

Night changes:

- circulation;
- social behavior;
- active spaces;
- building lights;
- room tones;
- signage;
- exterior color temperature;
- visual focus.

---

# 13. Audio Grammar

Audio is structural.

## 13.1 Layers

Use:

```text
global city bed
+ district bed
+ space room tone
+ local object emitters
+ actor sounds
+ weather layer
+ event layer
```

---

## 13.2 Crossfades

Indoor/outdoor transitions must crossfade.

No hard cut unless stylistically intentional.

---

## 13.3 Footsteps

At minimum distinguish:

- concrete;
- wood;
- grass;
- interior hard floor;
- wet surface where relevant.

Footstep timing must follow movement state.

---

## 13.4 Distance

Use simple attenuation.

Avoid expensive acoustic systems unless proven necessary.

---

# 14. Diegetic UI Grammar

## 14.1 UI Priority

Order:

1. world signal;
2. contextual prompt;
3. anchored panel;
4. conventional full UI only when necessary.

---

## 14.2 Presence

Presence should appear physically.

Examples:

```text
● CABESSA
AVAILABLE
```

```text
● CABESSA
IN MEETING
3 PEOPLE
```

```text
○ CABESSA
AWAY
```

Display through:

- entrance signage;
- room light;
- door panel;
- desk status;
- subtle building indicator.

Sidebars may exist as utility fallback, not primary spatial experience.

---

## 14.3 Privacy

Supported concepts:

- Everyone;
- Awake Members;
- Invite Only;
- Do Not Disturb.

Closed spaces should communicate state physically.

---

# 15. Social Interaction Grammar

Social systems should emerge from co-presence.

## 15.1 Encounter

Default flow:

```text
see person
→ approach
→ proximity presence
→ optional interaction
```

Not:

```text
open user list
→ click person
→ teleport/chat
```

---

## 15.2 Conversation Zones

Spaces may influence conversation naturally:

- sofa;
- coffee table;
- meeting table;
- rooftop;
- garden bench.

Do not force all conversation into explicit “chat rooms.”

---

# 16. Visual Language Contract

## 16.1 Awake Visual Identity

Must feel:

```text
contemporary architecture
+ integrated nature
+ calm technology
+ game-world readability
+ digital nostalgia
+ subtle personality
```

---

## 16.2 Avoid

- photoreal uncanny;
- generic low-poly;
- cyberpunk neon;
- corporate metaverse;
- asset-store collage;
- excessive bloom;
- UI everywhere;
- random sci-fi decoration.

---

## 16.3 Material Family

Preferred base:

- concrete;
- warm wood;
- smoked glass;
- matte metals;
- vegetation;
- water;
- diffused fabric;
- controlled emissive elements.

---

## 16.4 Variation

Use modular assets varied through:

- material;
- transform;
- prop arrangement;
- lighting;
- decal;
- vegetation;
- clutter;
- layout;
- occupancy state.

Major spaces must retain unique composition.

---

# 17. Space Identity Contract

## 17.1 Central Plaza

Role:

**social heart + serendipity engine**

Must support:

- circulation;
- coffee;
- sitting;
- vegetation;
- water;
- art;
- NPC routes;
- shelter;
- microevents;
- deliveries;
- street musician;
- dogs;
- sunset gathering.

---

## 17.2 The Observatory

Role:

**Caio / Monks — iconic but earned**

Must communicate:

- elevation;
- view;
- concrete;
- wood;
- smoked glass;
- integrated nature;
- indirect light;
- projects;
- meetings;
- rooftop;
- strong morning/sunset/night identity.

Must not look like admin VIP room.

---

## 17.3 The Grid

Role:

**operation / control / precision**

Traits:

- modular;
- geometric;
- organized;
- quiet technology;
- system visibility.

---

## 17.4 Twin Core

Role:

**premium game-tech studio**

Traits:

- dual workstations;
- dev hardware;
- build wall;
- servers;
- prototypes;
- high-tech elegance.

Diegetic states may include:

```text
BUILD RUNNING
BUILD SUCCESSFUL
BUILD FAILED
SERVER ACTIVITY
```

---

## 17.5 Trinity Lab

Role:

**major R&D space**

Traits:

- development floor;
- research floor;
- paper wall;
- experiment room;
- collaboration table;
- terrace;
- warm/open environmental identity.

---

## 17.6 The Garage

Role:

**creative construction space**

Must always feel like something is being built.

Traits:

- workbench;
- components;
- boxes;
- tools;
- computers;
- unfinished projects;
- large door.

---

## 17.7 Kawaii Garden

Role:

**comfort + nature + gentle technology**

Traits:

- modern Japanese restraint;
- water;
- wood;
- stones;
- vegetation;
- soft light;
- kawaii objects;
- pets.

Rain/night must be especially strong here.

---

## 17.8 The Pit

Role:

**premium gaming dungeon + controlled chaos**

Traits:

- semi-underground;
- low natural light;
- absurd PCs;
- multiple screens;
- cables;
- damaged sofa;
- boxes;
- strange objects;
- original RPG references;
- punctual internal humor.

Humor must not dominate Awake as a whole.

---

## 17.9 The Glasshouse

Role:

**minimal / vegetal / luminous / contemplative**

Traits:

- glass;
- natural light;
- vegetation;
- restraint;
- silence;
- clean spatial hierarchy.

---

# 18. Response-Time Budget

Perceived latency matters.

## 18.1 Immediate World Feedback

For button press / interaction acknowledgement:

```text
target: < 100 ms perceived
```

Even if underlying operation takes longer, acknowledge immediately.

---

## 18.2 Interaction Panel

Target:

```text
< 250 ms perceived
```

If data loads slower:

- animate world response first;
- show progressive state;
- do not freeze.

---

## 18.3 Door / Space Transition

Target:

```text
500–1200 ms total perceptual transition
```

Longer transitions require a specific artistic reason.

---

# 19. Performance Experience Contract

Performance must protect feel.

## 19.1 Targets

Baseline:

```text
60 FPS target
```

Temporary dips may occur during exceptional transitions, but sustained movement must remain smooth.

---

## 19.2 Priority Under Load

If resources are constrained, degrade in this order:

1. distant ambient animation;
2. distant NPC full simulation;
3. decorative effects;
4. shadow/detail quality;
5. nonessential audio emitters.

Do not degrade first:

- player input;
- collision;
- interaction;
- camera responsiveness;
- current-space feedback.

---

# 20. Simulation LOD Contract

Actors use:

```text
FULL
REDUCED
LOGICAL_ONLY
SLEEP
```

### FULL
Near player / current relevant space.

### REDUCED
Visible or moderately near.

### LOGICAL_ONLY
State continues without pathfinding/render detail.

### SLEEP
No active simulation until trigger.

---

# 21. Debug + Observability Contract

F3 is not a cheat panel.  
It is the world debugger.

Must expose:

## Player
- position;
- velocity;
- desired velocity;
- state;
- space;
- target;
- camera state.

## NPC
- state;
- schedule;
- destination;
- utility scores;
- simulation LOD;
- current action.

## World
- time;
- weather;
- seed;
- tick;
- active events.

## Space
- occupants;
- lighting;
- audio;
- weather response;
- NPC count;
- interaction count.

## Performance
- FPS;
- frame time;
- simulation time;
- render time;
- active actors;
- sleeping actors;
- light count;
- audio source count.

Required controls:

- pause;
- single tick;
- 0.25x;
- 1x;
- 4x;
- teleport;
- force weather;
- force event;
- follow NPC;
- inspect actor;
- show collision;
- show interaction zones;
- show paths;
- show LOD.

---

# 22. Experience Benchmark Matrix — 0.5 GLOBAL

| Area | PASS condition | FAIL signal |
|---|---|---|
| Movement | Responsive, smooth start/stop, deliberate direction changes | Binary, sliding, grid-like, cursor feeling |
| Camera | Stable, soft, contextual, no nausea | Laggy, floaty, excessive zoom |
| Interaction | Clear target, forgiving proximity, instant acknowledgement | Flicker, precision requirement, delayed response |
| Doors | Feels like entering a place | Instant teleport / hard scene cut |
| Plaza | Feels socially central even when idle | Empty hub / decorative void |
| NPCs | Recognizable routines and pauses | Random walkers |
| Pets | Independent life + contextual reaction | Constant player-following decoration |
| Weather | Multiple systems react coherently | Rain particles only |
| Time | City behavior changes with time | Lighting-only clock |
| Audio | Space and weather are audible | Flat global loop |
| Lighting | Time/weather/occupancy affect atmosphere | Static lighting |
| UI | Mostly contextual and anchored | Sidebar/menu-first experience |
| Presence | Physical/diegetic presence cues | User-list dependency |
| Save/Load | Returning feels continuous | World resets perceptually |
| Idle Life | 30–120 sec of observation remains interesting | Dead scene when player stops |
| Performance | Input/camera remain stable at target load | Responsiveness degrades first |
| Identity | Immediately feels like Awake | Generic metaverse / asset-store scene |

---

# 23. Human Acceptance Journeys

These scenarios are mandatory experiential tests.

They are not unit tests.  
They are product acceptance.

---

## A01 — Stand Still in Central Plaza

### Procedure

1. enter Central Plaza;
2. do not move for 2 minutes;
3. do not open UI.

### PASS

During the 2 minutes, the player should perceive multiple subtle independent events, for example:

- NPC passes;
- vegetation moves;
- cafe emits activity;
- light changes slightly;
- screen updates;
- dog appears or moves;
- distant sound changes;
- delivery/maintenance occurs;
- door opens;
- water/ambient motion continues.

No event needs to demand attention.

### FAIL

The world looks paused.

---

## A02 — Cross the Quarter

### Procedure

Walk continuously from one side of Awake Quarter to the other.

### PASS

- movement is pleasurable;
- camera remains stable;
- paths have visual hierarchy;
- landmarks guide movement;
- no repeated hard geometry rhythm;
- no interaction prompt flicker;
- NPCs do not obstruct irrationally;
- transitions in ambience are perceptible.

### FAIL

Feels like moving a sprite across a board.

---

## A03 — Observatory Entry at Sunset

### Procedure

1. set time to sunset;
2. approach Observatory;
3. enter;
4. move toward workspace;
5. interact with desk.

### PASS

- building acknowledges proximity;
- entry has transition;
- exterior/interior audio crossfades;
- camera reframes;
- sunset character persists through glass;
- interior lighting becomes warmer;
- desk wakes before/at interaction;
- work UI feels physically sourced.

---

## A04 — Twin Core at Night

### Procedure

Enter Twin Core at night.

### PASS

Player perceives:

- active machines;
- server ambience;
- display state;
- dual-station identity;
- low-key technical motion;
- high-tech without cyberpunk cliché.

At least one diegetic build/server state should be legible.

---

## A05 — Trinity Lab Workday

### Procedure

Visit Trinity Lab during professional-hours activity.

### PASS

- space feels research-oriented;
- multiple functional zones are distinguishable;
- NPC activity has purpose;
- terrace/open architecture changes ambience;
- no generic “office room” feeling.

---

## A06 — Kawaii Garden in Rain

### Procedure

1. force rain;
2. enter Kawaii Garden;
3. observe pets for 2 minutes;
4. interact with one pet.

### PASS

- rain is audible differently across surfaces;
- dogs alter behavior;
- at least one seeks shelter/rest;
- interior/window behavior feels cozy;
- pet reaction is immediate;
- garden remains calm.

### FAIL

Pets ignore rain and environment is unchanged beyond particles.

---

## A07 — The Pit Late Night

### Procedure

Enter The Pit after 00:00.

### PASS

- space feels active but enclosed;
- gaming/dev ambience;
- low exterior influence;
- screens/PCs provide life;
- humor exists but does not become UI spam;
- sound profile differs strongly from Plaza.

---

## A08 — Rain Across the District

### Procedure

1. stand outside in clear weather;
2. transition to cloudy;
3. transition to rain;
4. walk across Plaza;
5. enter Cafe/space;
6. enter Kawaii Garden;
7. observe NPCs.

### PASS

Rain triggers coherent changes across:

- sky;
- light;
- ground;
- sound;
- NPC behavior;
- pet behavior;
- shelter use;
- indoor/outdoor audio;
- window behavior;
- circulation.

---

## A09 — Follow One NPC

### Procedure

Choose a recurring NPC and observe/follow for a substantial period.

### PASS

NPC:

- has a destination;
- pauses naturally;
- performs role-appropriate actions;
- uses spaces;
- reacts to time/weather;
- does not endlessly wander;
- remains coherent if player disengages and returns.

---

## A10 — Sit and Observe

### Procedure

Sit on a bench/sofa and remain idle.

### PASS

- camera changes subtly;
- movement state changes;
- player feels anchored;
- world continues;
- nearby sound becomes more noticeable;
- no forced UI.

---

## A11 — Interaction Target Stress

### Procedure

Stand near 3–4 interactables.

Move slightly between them.

### PASS

- target remains stable;
- hysteresis prevents flicker;
- chosen object feels intuitive;
- player can select intended object without pixel-perfect positioning.

---

## A12 — Save / Exit / Return

### Procedure

1. enter a specific space;
2. change weather/time;
3. observe NPC state;
4. save;
5. exit;
6. relaunch;
7. load.

### PASS

Return preserves believable coherence.

Exact micro-animation phase need not persist.

Meaningful state must.

---

## A13 — 15 Minutes Without Menus

### Procedure

Play for 15 minutes using only world interactions.

### PASS

Player can:

- navigate;
- enter spaces;
- sit;
- inspect;
- interact with objects;
- observe NPCs;
- use at least one productivity surface;
- experience weather/time;

without relying on a permanent sidebar.

---

## A14 — Debug Reproduction

### Procedure

1. create deterministic seed;
2. record a short input/world sequence;
3. replay in diagnostics/test mode.

### PASS

Relevant actor states, world events and interactions reproduce consistently enough to debug.

---

## A15 — Low-Activity Night

### Procedure

Set 03:00 and walk through the district.

### PASS

The city becomes quieter, not dead.

Expected:

- fewer NPCs;
- selected lights remain;
- distant systems still operate;
- active spaces become obvious;
- atmosphere changes significantly.

---

# 24. Red Flags — Automatic Rejection

Reject an implementation if any of these becomes the dominant experience:

- instant room teleport without contextual transition;
- UI sidebar as primary navigation;
- every interactable covered by labels;
- random NPC wandering;
- camera lag greater than player control confidence;
- pets acting like follower drones;
- weather as particles only;
- neon used to manufacture “technology”;
- every room built from same prop pattern;
- excessive motion;
- excessive sound;
- dead idle scenes;
- repeated hard modal transitions;
- debug tooling unable to explain actor state;
- features that exist visually but do nothing;
- “TODO” replacing core behavior;
- local-machine-only validation for systems that can run in cloud CI.

---

# 25. Acceptance Gate for 0.5 GLOBAL

0.5 GLOBAL is not accepted because it launches.

It is accepted when all of the following are true:

```text
COHERENCE
IDENTITY
ATMOSPHERE
FLUIDITY
RESPONSIVENESS
LIFE
PERFORMANCE
EXTENSIBILITY
PLAYABILITY
```

Mandatory experiential conditions:

- player movement no longer feels rigid;
- camera feels controlled and natural;
- entering a building feels spatial;
- Central Plaza feels alive at rest;
- NPCs have recognizable behavior;
- pets behave independently;
- rain changes the district systemically;
- day/night meaningfully changes activity;
- audio differentiates places;
- major spaces possess unique identity;
- interaction targets are stable and forgiving;
- the city remains interesting when the player stops;
- diagnostics can explain state;
- core bugs can be reproduced deterministically;
- save/load preserves continuity;
- Windows build is validated in cloud before delivery;
- user does not need a manual patch loop.

---

# 26. Implementation Priority When Tradeoffs Exist

When two tasks compete, prioritize in this order:

```text
1. player responsiveness
2. interaction reliability
3. camera clarity
4. transition coherence
5. environmental life
6. NPC/pet coherence
7. audio/lighting richness
8. decorative content
9. feature count
```

Never sacrifice categories 1–4 to add more content.

---

# 27. Decision Rule

Before implementing any feature, ask:

```text
Does this make Awake World feel more like a place?
```

If no:

It is probably not a 0.5 priority.

Second question:

```text
Can the same perceived result be achieved with a smaller coherent system?
```

If yes:

Use the smaller system.

---

# 28. Canonical Closing Standard

The intended player reaction is not:

> “There are many features.”

It is:

> “This place feels alive.”

The intended technical result is not:

> “The simulation is complex.”

It is:

> “The systems are coherent.”

The intended product identity is:

```text
awake/world
THE LIVING NETWORK
```

A digital place where:

- work is spatial;
- presence is physical;
- technology is quiet;
- architecture communicates state;
- people cross paths;
- weather matters;
- time matters;
- spaces have memory;
- the world keeps going.

**THE SPACE IS THE INTERFACE.**

**SUBTLE LIFE.**

**PERCEIVED COMPLEXITY > RAW COMPLEXITY.**

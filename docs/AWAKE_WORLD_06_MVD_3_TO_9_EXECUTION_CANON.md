# AWAKE WORLD 0.6 — MVD-3 → MVD-9 EXECUTION CANON

**Status:** CANONICAL EXECUTION CONTRACT  
**Milestone:** `0.6.0-dev — THE LIVING QUARTER`  
**Parent canon:** `docs/AWAKE_WORLD_06_MVD_CANON.md`  
**Baseline:** frozen release `v0.5.0 GLOBAL`  
**Identity:** `awake/world — THE LIVING NETWORK`  
**Execution horizon:** MVD-3 through MVD-9  
**Rule:** no phase advances on CI alone; automated gates + human visual/product acceptance are both required.

This document is the authoritative execution roadmap for the remainder of Awake World 0.6 after MVD-2.2.

It extends the Interaction + Experience Bible v1 and the Awake World 0.6 MVD Canon. Where an implementation detail conflicts with the permanent product laws, the permanent laws win.

---

## 0. Canonical checkpoint entering this roadmap

### Frozen baseline

- `v0.5.0 GLOBAL` is immutable.
- No 0.6 work may rewrite, retag or replace the released 0.5 baseline.

### Completed and merged

- **MVD-1 — Massing + Scale**: merged through PR #10.
- **MVD-2 — Material + Light**: merged through PR #11.
- MVD-1 footprints, scale, circulation, negative space and landmark hierarchy remain canonical.
- MVD-2 material/light response remains canonical.

### Current acceptance branch

PR #12 carries the visual-foundation work that must be human-accepted before MVD-3:

- **MVD-2.1 — Visual Foundation**
  - continuous architectural ground;
  - architectural assemblies instead of raw cuboids;
  - directional face response;
  - contact shadow;
  - framed glass;
  - architectural thresholds;
  - integrated planting;
  - tighter composition;
  - space-specific microarchitecture.

- **MVD-2.2 — Spatial Depth**
  - raised platforms, decks and terraces;
  - visible stepped stair flights;
  - stair nosings for isometric legibility;
  - structural piers;
  - multi-part building masses;
  - lower mass + floor reveal + recessed upper mass;
  - setbacks and stronger overlap;
  - distinct vertical composition per space.

Latest Windows/Qt evidence for the MVD-2.2 implementation passed:

- MVD-1 silhouette gate;
- MVD-2 material/light gate;
- MVD-2.1 visual-foundation gate;
- MVD-2.2 spatial-depth gate;
- static/type/unit/simulation;
- deterministic replay;
- gameplay drivers;
- Windows Qt render;
- packaged executable smoke;
- artifact integrity.

### Important limitation entering MVD-3

MVD-2.2 introduces **architectural depth**, not a silent traversal rewrite.

The player navigation model is still the canonical MVD-1 plane. True multi-level traversal is explicitly reserved for MVD-6.

---

## 1. Permanent laws for MVD-3 → MVD-9

Every phase must preserve:

- **THE SPACE IS THE INTERFACE**
- **SUBTLE LIFE**
- **PERCEIVED COMPLEXITY > RAW COMPLEXITY**
- **HIGH-END EXPERIENCE / LOW-COST ARCHITECTURE**
- single-player first / multiplayer-ready
- stylized premium
- contemporary architecture + integrated nature + quiet technology + subtle digital nostalgia
- contextual interaction instead of menu-first interaction
- restrained motion
- coherent authored spaces instead of procedural noise
- local dialects inside one global visual language
- no neon/cyberpunk shorthand
- no corporate-metaverse language
- no asset-store salad
- no AI slop
- no random NPC wandering used as a substitute for authored life
- no technical gate may substitute for human acceptance.

---

## 2. Operating protocol for every remaining MVD

Each MVD follows exactly this loop:

```text
CANON
→ SYSTEM DESIGN
→ TRANSVERSAL IMPLEMENTATION
→ STATIC/UNIT/BEHAVIORAL GATES
→ WINDOWS/QT RENDER
→ PACKAGED BUILD
→ HUMAN REVIEW
→ REVISE IF NEEDED
→ FREEZE PHASE
```

### Required evidence before phase closure

Every phase must produce, where applicable:

1. deterministic tests;
2. deterministic screenshots/goldens;
3. Windows packaged build;
4. packaged smoke;
5. visual artifact archive;
6. before/after evidence for material visual changes;
7. a human acceptance decision;
8. an updated build manifest;
9. updated canonical documentation when the system contract changes.

### Merge discipline

- Never merge merely because CI is green.
- Never merge a visually weak state to "fix later".
- Never hide a foundation problem under props, animation or effects.
- Each MVD must improve the **shared system** first and local exceptions only when the local dialect genuinely requires them.

---

# MVD-3 — SUBTLE LIFE

## Purpose

Make the world feel occupied and continuous **without spectacle**.

The player should be able to stop moving and still perceive that the place continues to exist.

## System scope

Implement one shared ambient-life system with per-space authored profiles.

### Environmental life

- low-amplitude vegetation motion;
- asynchronous leaf/canopy sway;
- localized rain response;
- subtle glass/weather response;
- interior screen state;
- small mechanical states;
- restrained light breathing where architecturally justified;
- vents, fans, workshop indicators, research instruments and similar function-driven micro-motion.

### Occupancy evidence

- coffee cups, open notebooks, active workstations, tools, charging devices, project boards, packages, instruments and context-specific traces;
- no generic clutter scatter;
- every prop implies a plausible recent or current activity.

### NPC purpose

- recurring authored routes;
- destinations tied to function;
- short pauses at meaningful anchors;
- no meaningless random wandering;
- clear role identity through behavior rather than floating labels.

### Pets

- only where contextually justified;
- small autonomous loops;
- no attention-demanding gimmicks.

### Ambient audio

- room tone;
- material-appropriate footstep/acoustic response;
- distant local activity;
- weather contribution;
- restrained spatial events.

### Microevents

Examples:

- courier arrival;
- maintenance pass;
- screen refresh;
- coffee preparation;
- lab instrument cycle;
- garage tool state;
- garden watering;
- short social gathering.

Events must be authored, sparse and non-blocking.

## Space dialect targets

| Space | MVD-3 life dialect |
| --- | --- |
| Quarter | quiet circulation, courier/maintenance rhythm, civic continuity |
| Central Plaza | social pauses, crossing patterns, café/garden activity |
| Observatory | sparse contemplative activity, horizon/instrument states |
| Grid | operational screens, precise recurring routes, system checks |
| Twin Core | active dev stations, hardware states, dual-work rhythm |
| Trinity Lab | research cycles, collaborative pauses, instruments |
| Garage | workshop tools, service rhythm, utility motion |
| Kawaii Garden | foliage, pet/character intimacy, gentle garden activity |
| Pit | social occupancy, restrained pulse, denser but controlled movement |
| Glasshouse | plant response, irrigation/ventilation states, diffuse life |

## Non-goals

- crowds;
- cinematic spectacle;
- particles everywhere;
- random animation for its own sake;
- cutscenes;
- behavior that obscures interaction targets.

## Automated acceptance

Add a dedicated `AWAKE_MVD3_SUBTLE_LIFE_OK` gate proving:

- every registered space owns an ambient-life profile;
- motion amplitudes remain bounded;
- deterministic seeded ambient simulation;
- NPC loops have purpose anchors;
- no ambient actor crosses forbidden collision/portal regions;
- idle simulation remains stable over extended deterministic runs.

## Human acceptance

When the player stands still for 20–30 seconds:

- the space feels alive;
- nothing demands attention unnecessarily;
- motion remains secondary to architecture;
- each space expresses a distinct behavior dialect;
- the world does not look like a screensaver.

**Exit condition:** MVD-3 is frozen only when subtle life strengthens the architecture rather than compensating for weak architecture.

---

# MVD-4 — SPATIAL INTERACTION INTEGRATION

## Purpose

Make interaction feel like a property of the world, not a UI layer placed on top of it.

## System scope

### Contextual targeting

- target scoring;
- distance weighting;
- facing/intent weighting;
- hysteresis;
- forgiving target retention;
- target priority rules;
- predictable conflict resolution between nearby interactables.

### World acknowledgment

- architectural/object response before text;
- restrained outline, light, material, posture or screen-state change;
- interaction feedback anchored to the object;
- no giant floating prompt as the primary affordance.

### Thresholds and transitions

- contextual doorway/threshold response;
- camera anticipation;
- short spatial transition;
- no unexplained instant teleport;
- preserve location continuity.

### Camera grammar

- movement framing;
- interaction framing;
- threshold framing;
- social framing;
- recovery to navigation frame;
- damping bounded to avoid floaty camera behavior.

### Anchored UI

- only when the world cannot carry the information alone;
- spatial attachment first;
- compact typography;
- minimal persistent HUD;
- prompt content remains contextual and short.

## Required interaction surfaces

At minimum:

- desk/workstation;
- project/task board;
- display/TV;
- meeting table;
- sofa/social anchor;
- threshold/door;
- media/document surface;
- arcade/minigame anchor where appropriate.

## Automated acceptance

Add `AWAKE_MVD4_SPATIAL_INTERACTION_OK` proving:

- target selection deterministic for known layouts;
- hysteresis prevents rapid target flicker;
- interaction zones remain reachable;
- transition state machines terminate correctly;
- camera returns to valid navigation state;
- every required surface exposes canonical interaction metadata.

## Human acceptance

With conventional HUD minimized:

- the player still understands what can be interacted with;
- interaction intent is predictable;
- approaching an object feels sufficient to reveal its function;
- transitions preserve spatial orientation.

**Exit condition:** the space itself successfully communicates primary interaction.

---

# MVD-5 — HUMAN ACCEPTANCE + FOUNDATION GOLDEN FREEZE

## Purpose

Freeze the **foundation** before advanced traversal and product-surface integration.

MVD-5 does **not** freeze all future 0.6 development. It freezes the accepted visual, interaction and ambient grammar established by MVD-1 through MVD-4.

## Golden matrix

Create a deterministic review matrix covering:

- all 10 spaces;
- day;
- dusk/night;
- clear;
- rain where materially relevant;
- representative navigation frame;
- representative interaction frame;
- representative idle-life frame.

## Review dimensions

Human review must explicitly judge:

- silhouette;
- architecture;
- scale;
- depth;
- material response;
- glass;
- vegetation;
- subtle life;
- camera;
- interaction;
- local identity;
- global coherence;
- visual noise;
- premium read;
- avatar/world compatibility.

## Performance freeze

Record foundation budgets:

- scene item count;
- average/frame worst-case update cost;
- ambient actor count;
- active animation count;
- render time on Windows CI;
- packaged startup/smoke behavior.

## Automated acceptance

Add `AWAKE_MVD5_FOUNDATION_FREEZE_OK` and freeze accepted goldens.

After MVD-5:

- accidental changes to MVD-1→4 goldens fail CI;
- deliberate changes require an explicit human reacceptance/update;
- visual-regression deferral from earlier MVD phases ends.

## Human acceptance question

> Does this already feel like a place worth inhabiting even before the remaining product systems are layered in?

**Exit condition:** accepted foundation goldens become the reference contract for MVD-6→9.

---

# MVD-6 — MULTI-LEVEL TRAVERSAL

## Purpose

Convert selected MVD-2.2 architectural depth from visual-only geometry into **real, legible traversal** without destabilizing the existing movement model.

This phase is explicit because stairs and elevation must never silently alter navigation.

## Traversal model

Introduce an authored lightweight elevation layer:

- canonical floor/level identifier;
- walkable raised planes;
- stair connectors;
- ramps only where architecturally justified;
- bridge/mezzanine connectors;
- safe transition between elevation layers;
- height-aware interaction anchors;
- height-aware avatar projection and shadow.

Do not introduce general-purpose 3D physics.

## Priority traversal spaces

First-class elevation traversal must be proven in:

1. Observatory;
2. Central Plaza;
3. Twin Core;
4. Pit;
5. Glasshouse.

Then apply the same system, at appropriate complexity, to the remaining spaces.

## Architecture

Add or refine:

- stairs integrated into building entries;
- mezzanines;
- balconies/terraces;
- suspended walkways;
- retaining walls;
- guardrails;
- parapets;
- split-level interiors/exteriors where visible;
- roof or upper platform access only when it adds meaningful use.

## Navigation safety

- no ambiguous walkable/non-walkable surfaces;
- no avatar clipping through elevation edges;
- no interaction through floors;
- no hidden collision walls pretending to be stairs;
- every traversable level has a clear entry/exit.

## Automated acceptance

Add `AWAKE_MVD6_MULTI_LEVEL_TRAVERSAL_OK` proving:

- stair connector graph validity;
- all raised walkable planes reachable where intended;
- no orphan elevation levels;
- deterministic transition between levels;
- interaction height binding;
- save/load restores current level safely;
- replay driver traverses representative multi-level routes.

## Human acceptance

- stairs read visually before the player uses them;
- climbing feels continuous rather than teleport-like;
- camera preserves orientation;
- upper levels reveal new spatial composition, not redundant floor area.

**Exit condition:** elevation becomes a genuine part of spatial experience.

---

# MVD-7 — SOCIAL + WORK SURFACES

## Purpose

Make Awake World useful as the shared Awake environment while preserving `THE SPACE IS THE INTERFACE`.

The world must support work and social behavior without splitting into "game mode" and "work mode".

## Canonical spatial surfaces

### Work

- desk → personal/work context;
- project wall/board → tasks/projects;
- file/document surface → files;
- display/TV → media and screen-sharing entry;
- meeting table → meeting context;
- lab/workbench → domain-specific tools where appropriate.

### Social

- sofa/bench → proximity conversation;
- plaza/pit → informal gathering;
- private room/office → focused session;
- arcade/social object → lightweight entertainment.

## Product behavior

- opening a work surface retains spatial context;
- overlays are temporary and anchored;
- leaving the surface returns naturally to the world;
- surface ownership and permissions are explicit;
- single-player local implementation remains valid;
- interfaces are structured so multiplayer/realtime backends can attach later.

## Presence readiness

Define shared contracts for future multiplayer:

- user identity;
- avatar state;
- room presence;
- interaction state;
- surface occupancy;
- ephemeral activity state;
- voice/video readiness;
- file/media references.

Do not require production multiplayer to close 0.6 unless separately authorized.

## Automated acceptance

Add `AWAKE_MVD7_SPATIAL_UTILITY_OK` proving:

- every required work/social surface has a canonical action;
- surface state opens/closes deterministically;
- focus does not strand movement/camera state;
- save schema remains compatible;
- permissions/ownership interfaces are explicit even if local-only.

## Human acceptance

A user should understand:

- where to work;
- where to meet;
- where to socialize;
- where media/files belong;

without navigating a conventional dashboard first.

**Exit condition:** Awake World functions as a place, not a themed launcher.

---

# MVD-8 — WORLD COHERENCE + PRODUCTION HARDENING

## Purpose

Make the complete 0.6 system reliable, performant and coherent enough to survive normal use.

## Perceived-complexity optimization

Before adding any new expensive system, ask:

> Can the same perceived richness be achieved through authored reuse, state variation, timing or composition?

Prioritize:

- shared architectural primitives;
- shared ambient actors;
- deterministic state variation;
- pooled visual items where useful;
- bounded animation;
- update throttling for non-critical ambience;
- low-cost screen/state simulation.

## Performance

Establish budgets for:

- startup;
- room transition;
- render frame;
- ambient update;
- NPC update;
- interaction resolution;
- save/load;
- packaged build size.

## Reliability

- deterministic replay regression;
- long idle soak;
- repeated room-transition soak;
- save/load cycles;
- weather/time changes;
- resize/display-scale behavior;
- audio-device absence;
- missing optional media;
- graceful fallback for unsupported integrations.

## UX hardening

- prompt consistency;
- accessibility of contrast/legibility;
- focus/keyboard behavior;
- no dead-end modal state;
- no hidden primary action;
- no camera seizure after interrupted interaction.

## Automated acceptance

Add `AWAKE_MVD8_PRODUCTION_HARDENING_OK`.

Required gates include:

- soak simulation;
- navigation/transition stress;
- interaction stress;
- save/load stress;
- performance-budget check;
- packaged startup and shutdown;
- Windows Qt smoke;
- artifact integrity.

## Human acceptance

The product must feel calm and intentional even under edge cases.

**Exit condition:** no known systemic defect is being deferred merely because the happy path looks good.

---

# MVD-9 — 0.6 RELEASE CANDIDATE + FINAL GOLDEN FREEZE

## Purpose

Close `0.6.0 — THE LIVING QUARTER` as a coherent product milestone.

MVD-9 is the final acceptance phase for this sequence.

## Final review matrix

Review the entire product across:

- all 10 spaces;
- representative day/night/weather states;
- navigation;
- multi-level traversal;
- idle life;
- interaction;
- work surfaces;
- social surfaces;
- transitions;
- save/load;
- packaged Windows build.

## Final visual freeze

Create the authoritative 0.6 golden set.

No deferred authored-space visual regression remains.

## Final product questions

The build must answer **yes** to all of the following:

1. Does every screenshot belong unmistakably to Awake World?
2. Does every major space have a unique functional and visual identity?
3. Does the world feel inhabited when the player stops?
4. Does interaction emerge from space rather than menus?
5. Do stairs, terraces and multi-level spaces feel architecturally real?
6. Does navigation remain clear?
7. Does work feel native to the world rather than bolted on?
8. Does social presence have obvious spatial anchors?
9. Does the build remain performant and stable?
10. Does the product feel authored rather than generated?
11. Would showing a static screenshot or short gameplay capture represent the project confidently?
12. Is the experience meaningfully beyond the `v0.5.0 GLOBAL` baseline without violating its released state?

## Release gates

Add `AWAKE_MVD9_RELEASE_CANDIDATE_OK`.

Required closure:

- all MVD-3→8 gates green;
- final golden regression green;
- packaged Windows smoke green;
- deterministic replay green;
- save schema validated;
- build manifest exact;
- no blocking review issue;
- human visual acceptance;
- human product acceptance.

## Freeze rule

After MVD-9 acceptance:

- tag/release procedure may begin;
- the accepted commit becomes the canonical 0.6 release candidate;
- subsequent visual/system changes belong to a new development line unless they are release-blocking fixes.

**Exit condition:** `0.6.0 — THE LIVING QUARTER` is a releasable, coherent Awake World milestone.

---

# 3. Phase dependency graph

```text
MVD-2.2 SPATIAL DEPTH
        ↓
MVD-3 SUBTLE LIFE
        ↓
MVD-4 SPATIAL INTERACTION
        ↓
MVD-5 FOUNDATION GOLDEN FREEZE
        ↓
MVD-6 MULTI-LEVEL TRAVERSAL
        ↓
MVD-7 SOCIAL + WORK SURFACES
        ↓
MVD-8 PRODUCTION HARDENING
        ↓
MVD-9 RELEASE CANDIDATE + FINAL FREEZE
```

No phase may be skipped because a later feature appears more exciting.

---

# 4. Cross-phase invariants

## Architecture

- MVD-1 footprint changes require explicit canon revision.
- Spatial depth must remain legible.
- New geometry must have purpose.
- Verticality cannot become visual clutter.

## Motion

- ambient motion stays low-amplitude;
- interaction feedback may be stronger but short;
- no universal pulsing/glowing language.

## NPCs

- purpose before population;
- route quality before count;
- authored behavior before randomness.

## UI

- spatial first;
- anchored second;
- conventional overlay only when required;
- persistent HUD is the last resort.

## Performance

- adding complexity requires a measured budget;
- expensive visual systems must justify their perceptual gain;
- offscreen/idle systems should throttle where appropriate.

## Testing

Every new phase adds a dedicated gate. Existing gates are never removed merely because a new phase supersedes them.

---

# 5. Session execution rule

For the current development session, work proceeds in strict order:

1. close human acceptance of MVD-2.1/MVD-2.2;
2. execute MVD-3;
3. review and freeze MVD-3;
4. execute MVD-4;
5. review and freeze MVD-4;
6. execute MVD-5 foundation freeze;
7. execute MVD-6;
8. review and freeze MVD-6;
9. execute MVD-7;
10. review and freeze MVD-7;
11. execute MVD-8;
12. harden until its acceptance gates pass;
13. execute MVD-9;
14. perform final human acceptance;
15. only then create/finalize the 0.6 release candidate.

If session limits prevent full completion, the repository must be left at the last fully accepted phase with the next phase clearly identified. No partial phase may be represented as complete.

---

# 6. Definition of “done”

A phase is **done** only when all are true:

- implementation exists across the intended world scope;
- tests/gates pass;
- Windows packaged build passes;
- evidence artifact exists;
- human review has occurred;
- known visual regressions are resolved;
- canon reflects the final system;
- merge/freeze state is explicit.

A green pipeline is necessary but never sufficient.

---

# 7. North-star statement

> Awake World 0.6 must feel like a small, premium, living place whose architecture, behavior, interaction and utility all belong to the same authored world.

The project succeeds when complexity is perceived through coherent spatial design — not through raw feature count.

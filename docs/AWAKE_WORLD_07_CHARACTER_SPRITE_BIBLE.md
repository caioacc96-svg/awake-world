# Awake World 0.7 — Character + Sprite Bible v1

## Status
Canonical development contract for `0.7.0-dev — THE LIVING CAST`.

Frozen parent: `v0.6.0 — THE LIVING QUARTER`. The 0.6 release is immutable.

## North star
**THE PEOPLE MUST BELONG TO THE PLACE.**

Characters must look authored for the same world as the architecture. They are not stickers, generic game avatars, mascot art, social-metaverse dolls or asset-store characters.

## Permanent laws
1. **WORLD SCALE FIRST** — scale derives from the accepted 96×48 isometric tile.
2. **SILHOUETTE BEFORE FACE** — role, clothing and accessory silhouette read before facial detail.
3. **EIGHT-DIRECTION LOGIC** — presentation resolves continuous facing into eight authored sectors.
4. **POSES ARE UTILITY** — sit/work/listen/rest/phone exist because spatial surfaces demand them.
5. **NO FLOATING SPRITES** — shadow, elevation projection, depth sorting and anchors are mandatory.
6. **NO PORTRAIT CLAIMS WITHOUT REFERENCE** — brand/role identity is allowed; physical likeness requires deliberate visual reference.
7. **SUBTLE MOTION** — idle, stride and lean remain bounded.
8. **QUIET UI** — pose and world response communicate state before labels/HUD.
9. **MODULARITY WITHOUT DOLLMAKER AESTHETICS** — layers are an engine contract, not a customization-screen language.
10. **PERFORMANCE IS A VISUAL RULE** — deterministic Qt/PyInstaller remains the runtime target.

## Canonical dimensions
The authored reference canvas is approximately **82×126 px**, then rendered into the world at a canonical **0.64 scale**.

Effective in-world pilot envelope:
- rendered height: ~81 px
- rendered width: ~52 px
- reference head: ~39 px
- reference shoulders: ~47 px
- reference shadow: ~44 px
- outline: <= 1.6 px before world scaling
- projected feet remain attached to the world anchor
- elevation stays on the canonical `IsoProjector`

The separation between reference canvas and world scale is intentional: review sheets may enlarge the sprite for inspection without changing architectural proportion in gameplay.

## Direction grammar
`east · north_east · north · north_west · west · south_west · south · south_east`

Continuous simulation facing is preserved. Only presentation is quantized. Rear sectors suppress front facial detail. Profile sectors reduce visible facial information.

## Pose grammar
Required: `standing`, locomotion through standing+motion, `seated`, `working`, `listening`, `resting`, `phone`.

Future poses must correspond to a real surface or behavior.

## Pilot 01 — Caio / MONKS
Home context: **The Observatory**.

The pilot identity is authored through:
- dark technical outer layer;
- off-white inner layer and shoes;
- restrained aged-gold accent;
- persistent over-ear headphone silhouette;
- geometric micro-mark rather than a large logo;
- selector/host posture rather than sci-fi operator posture.

This is a role/brand-authored identity, **not a claim of physical facial likeness**.

## Observatory vertical slice
The Observatory is the proving ground because it combines personal HQ, glass/stone/wood, quiet technology, work surfaces, project wall, review table and multi-level depth.

0.7 adds a restrained selector console around the existing work anchor. It must read as native architecture, not a pasted DJ booth.

## Animation budget
- idle: one slow breathing/bob cycle around 3.4 s
- walk: bounded stride, no mascot bounce
- run: modest lean and rate increase
- working: hands converge toward the physical surface
- listening: quiet posture; headphones remain the cue

## Layer contract
1. ground shadow
2. legs/shoes
3. torso/inner shirt
4. arms/held object
5. neck/head
6. hair
7. accessory
8. micro-mark/accent

This order is deterministic and can later be baked into atlases.

## LC-1 acceptance
LC-1 closes only when:
- pilot profile validates;
- eight directions resolve deterministically;
- required poses exist;
- avatar remains elevation-aware;
- Observatory contains the selector-console visual anchor;
- deterministic direction + pose sheets render at inspection scale while world-context frames preserve true gameplay scale;
- real Observatory context frames render;
- inherited Linux/Windows/visual/package gates stay green;
- human review confirms the character belongs to the world.

Technical gate: `AWAKE_LIVING_CAST_LC1_OK`.

Human acceptance remains separate from CI.

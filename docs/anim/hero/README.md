# Hero acrobatics — 3d-animations-astra

A playable main-character animation pass, built on Mac Studio. Existing crowds and animals were outside scope.

## Try it

In the air, press **X** or **L3 / left-stick click**:
- Forward: tuck flip.
- Back: backward layout flip.
- Left/right: mirrored corkscrew.
- Neutral: alternate forward layout and scissor spin.

Automatic swing-release tricks remain enabled. The existing double-Space shortcut remains available. Clearance accounts for the selected clip duration and vertical speed. Manual tricks add no speed impulse. Fresh web attach and dive inputs can interrupt.

Open **Suits** for the side-entry flip, landing, and breathing showcase idle. **R** replays the entrance. Drag still rotates the preview; selection and equipment rules remain unchanged. Closing the menu restores the saved hero transforms, position, velocity and traversal state.

## Sources and previews

- Editable scene: [hero.blend](../../../art/anim/hero.blend), eight named Blender Actions.
- Pose authoring: [author_hero.py](../../../tools/heroanim/author_hero.py).
- Coordinate conversion/baking: [bake_hero.py](../../../tools/heroanim/bake_hero.py).
- Runtime library: [hero-acrobatics.json](../../../public/assets/animations/hero-acrobatics.json).
- [Actual in-game suit entrance](motion/game-suit-entrance.mp4).
- [Two-angle normal-speed motion videos](motion/README.md); one MP4 per clip.
- On the Vite development server, open **/tools/heroanim/review.html** for an interactive clip selector, play/pause, and synchronized side/three-quarter views.

The original hero GLB, its 79 animations, meshes, textures, and all five custom skin GLBs are unchanged. New clips use the existing 58-joint skeleton. Existing custom skins inherit their existing materials and weights; this pass does not remodel them.

## Verification

- 19 automated tests, including clip identity/binding, real full-body rotation, keyboard/controller edge behavior and exact menu restoration.
- [Runtime checks](runtime-checks.json): all directional manual tricks and a real automatic web-release trick.
- [Extended checks](extended-runtime.json): all five custom meshes during entry and idle, rapid card changes, clearance rejection, dive/web interruption, held-key behavior, airborne menu restoration and ground jump.
- [Impact and fallback checks](impact-fallback-checks.json): actual ground landing, facade collision, and a deliberately missing clip library.
- [Export comparison](export-verification.json): 112 Blender/Three.js poses across 58 bones, sampled between animation keys. Maximum joint-position difference about 3.8 mm; exported at 120 samples/second. Sampling rate is not a performance claim.
- [Performance ledger](PERFORMANCE.md): real desktop rendering, with frame times and limitations.
- Blender phase contact sheets and in-game captures are in this directory.

## Visual iteration and limits

Fixed a pose-authoring error that lost the hip rotation; every authored key now asserts its intended root orientation. Added unique stable clip IDs after a real mixer-cache collision was caught by the independent export check. Raised baking precision after 60 Hz samples missed the fast launch by 13 mm. Refined leg IK to reduce foot sliding: settled idle foot travel is below 0.6 mm, landing recovery below 7 mm at the measured samples.

The first menu route hid the flip behind the cards. The revised route enters from the clear side, and the camera follows the arc to keep inverted feet below the header. Pose sheets cover both angles for all eight actions; denser exported-motion frames were inspected for the tuck flip and entrance.

Original imported Actions agree at their original key timestamps, but the importer has a known off-grid interpolation discrepancy (worst previously observed matrix component difference 0.088). Those imported legacy Actions are not re-exported into the game. The new authored export has its own passing numerical comparison.

The existing renderer still reports a 17-texture-unit request on a 16-unit limit. This warning was present before this animation pass. Existing generated skins can show texture/weight imperfections, especially at the shoulders and hands. Automated checks and captured poses do not establish owner acceptance of animation feel.

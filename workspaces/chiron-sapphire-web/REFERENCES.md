# Reference, approximation and rights register — R02

Contract SHA256: d84a8f87d8aa60a8d381416fbf152017e7d7ab7fce5d4497d98bc74dede521d9.
Review date: 2026-09-11. Assurance: SEQUENTIAL_SELF_REVIEW, actual tools; no independently isolated evaluator.

## VERIFIED_SOURCE

S01 Japan official Clear specification: https://jacobandco.jp/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/

Baseline BU210.80.AA.AA.B; JCAM37, manual winding; original movement 578 parts; case 57.8 × 44.4 × 21.5 mm; 3 Hz / 21,600 vph; approximately 60 hours; 30° flying tourbillon; 16-piston automaton; one approximately 15-second cycle; clear sapphire shell, translucent rubber strap and titanium deployant. Left crown sets hands; centre clockwise timekeeping/counterclockwise automaton; right starts automaton. 578 is NOT this digital model's measured part count. Do not import other case dimensions or colours.

S02 International Clear identity: https://jacobandco.com/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/clear
Dynamic page body limited; not an engineering drawing or 3D asset acquisition.

S03 Bugatti, 2020-04-20: https://newsroom.bugatti.com/press-releases/an-exclusive-timepiece-with-its-own-tiny-w16-engine
Family-level W16 automaton, crankshaft, turbines and suspension descriptions; not Clear-specific dimensions.

S04 family reserve/crown index: https://newsroom.bugatti.com/en/press-releases/luxury-like-no-other-new-bugatti-chiron-tourbillon-timepiece-limited-editions
Contract's family-level approximately three starts is used only as a disclosed normalized digital reserve, not an exact all-version claim.

## OBSERVED photo references (not redistributed production textures)

Clear three-quarter:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/1711638416-bu210-80-aa-aa-bbrua.webp

Bare movement/front:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/43dc6fe4-f63d-43e6-a654-58719342b716.jpg

Back:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/6b1b2d2c-c3ba-42c1-b483-d498c7971e38.jpg

These show upper tourbillon, upper-centre skeleton dial, lower W16 with longitudinal shaft, four mount points, three lower crowns, tonneau clear enclosure and curved translucent strap. Gallery images in other colours were rejected. No official product photo is used as an animated surface or substitute for a 3D part. No frame-accurate observation of an official mechanism video is claimed; exact hidden drive arrangement remains UNKNOWN.

## Reused mature tools

- Three.js 0.180.0, MIT: WebGLRenderer, OrbitControls, MeshPhysicalMaterial, RoundedBoxGeometry, BufferGeometryUtils, GLTFExporter, GTAOPass. https://threejs.org/docs/pages/MeshPhysicalMaterial.html and https://threejs.org/docs/pages/OrbitControls.html
- GTAOPass source in the locked `node_modules/three/examples/jsm/postprocessing/GTAOPass.js` was read. Current AO blend uses the pinned version's `_renderPass`; a Three upgrade requires regression, because that helper is not a stable public API.
- esbuild 0.25.10, MIT; Playwright 1.55.1, Apache-2.0. Lock file retains registry/integrity records. Relevant license texts are packaged in `THIRD-PARTY-NOTICES.txt`.
- No React/Next.js/GSAP added to this plain JavaScript workspace. No external HDRI/texture/font/sound pack bought or bundled. Environment and click sounds are generated locally; only installed system fonts are referenced.
- Casquette production case, layout/360/information organization reference: https://immersive-g.com/projects/girard-perregaux-casquette-1 . Read case material, not a complete live interaction or performance test. No case assets/code copied.
- Mechanical-watch explanatory reference in the original contract: https://ciechanow.ski/mechanical-watch/ . No source code copied or its movement dimensions substituted.

## ENGINEERING_APPROXIMATION / UNKNOWN

The digital model does not contain 578 verified original manufacturing parts. Unknown original tooth counts, tolerances, pin assignments, connecting rod dimensions, crank phasing, stroke, internal gearing and coupling dimensions are NOT stated as factory facts. The deterministic digital architecture uses eight shared crankpins and sixteen separately connected rods; all parameters/labels are editable in mechanics.mjs. It is not an automotive combustion simulation; there is no exhaust flame or car-engine sound.

3 Hz balance oscillation is distinct from the cage. Cage period 60 seconds is a display approximation, not a verified product specification. Pallet/escape stepping, hair-spring deformation and balance amplitude are visual kinematic approximations, not validated factory elastic dynamics. Real-time hand setting, reserve, slow regulator inspection and W16 action have independent state domains.

Four springs support a common carrier with bounded, damped displacement. Absolute travel, impact rating, original flex couplings and proprietary attachment details remain UNKNOWN. No sensor collection.

All disassembly is explicitly digital, not a factory assembly sequence or physical user-openable case. Rear crystal exits down while front/side enclosure exits up; functional assemblies remain intact internally. A static GLB export does not replace the source model/kinematics.

Real-time sapphire uses hybrid optical approximation: physical-transmission edge/body volumes plus lightly alpha-blended cover and cylinder surfaces to avoid nested transmission hiding internal components. This is NOT a physically exact light-transport simulation. Strong full front-cover screen-space transmission was rejected after actual screenshots visibly blurred mechanics.

## Rights and distribution boundary

All production geometry, locally generated studio environment and procedural sounds are authored in this workspace. No hidden brand GLB extraction, paid model, Editorial Uses Only asset or official image file is bundled. TurboSquid 1933410 was not acquired. Model creation does not grant trademark, trade dress or publicity rights. Text explicitly identifies this as an independent, unofficial digital study. No brand commission/endorsement or public commercial-use permission is claimed. The authorized scope is source/asset development and repository storage; public deployment remains unapproved.

The fonts used are local Arial/Georgia/system fallbacks. No font bytes are included in the release or source archive. Geometry/texture source and exported-asset SHA256 are recorded in the build/evidence manifest and asset export result, respectively.

## R04 actual structural / optical rework

Directly inspected official bare front:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/43dc6fe4-f63d-43e6-a654-58719342b716.jpg
Directly inspected official bare rear:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/6b1b2d2c-c3ba-42c1-b483-d498c7971e38.jpg
Directly inspected Clear case/crowns/strap:
https://jacobandco.jp/assets/timepieces/bugatti-chiron-tourbillon-sapphire-crystal/1711638416-bu210-80-aa-aa-bbrua.webp
These photographs are comparison references only, not redistributed production
textures or extracted meshes. Visible landmarks informed authored bridge/axle/
barrel/cage geometry. Hidden topology and exact mechanical dimensions remain
ENGINEERING_APPROXIMATION. 578 refers to the original watch, not our mesh count.

Generic 12:1 motion-works explanation:
https://ciechanow.ski/mechanical-watch/
Only the generic explanation was consulted. No author code/mesh copied and no
assertion that our 12/36 and 12/48 tooth counts are JCAM37 specifications.

Production illumination: Studio Small 03 by Greg Zaal / Poly Haven, CC0:
https://polyhaven.com/a/studio_small_03
https://polyhaven.com/license
Source and conversion SHA256 in generated/STUDIO-SOURCE.json. This supersedes any
older statement in this file that the environment contains only authored panels.
The source EXR is converted by cad/prepare_studio.py. It is not product imagery.

Original continuous CAD is made with CadQuery 2.8.0 / OpenCascade 7.9.3.1.1.
The web uses generated vertices, not the Python runtime. Author and license
notices for the tooling do not grant watch brand or design rights.

Optical probe: https://github.com/gkjohnson/three-gpu-pathtracer (MIT), 0.0.24,
three-mesh-bvh 0.9.5 / xatlas-web 0.1.0. This was tested as an optional challenger
and NOT adopted into the production dependency tree or default page. The
standalone probe is not a production FPS measurement or visual acceptance.

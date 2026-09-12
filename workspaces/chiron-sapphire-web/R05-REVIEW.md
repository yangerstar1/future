# R05 production repair

Resume baseline: `23649dc33121d117dbe4e1c6aa1c335d9601fe68`, branch
`codex/chiron-sapphire-web`, clean clone. No AGENTS.md exists in this repository
or its workspace ancestors. Changes are restricted to this workspace and its
existing production workflow. The user has authorized continuing implementation,
GitHub persistence and standard Actions. No public deployment or new fees.

## G0 delta

Existing plain ES modules, Three 0.180.0, esbuild 0.25.10, Playwright 1.55.1 reused.
Local Node 24.19.0 / Python 3.12.14 differs from CI Node 22.16.0. `npm ci`, seven
solver checks, build and all 15 existing geometry checks passed locally. CI retains
the pinned Node version. Source, generated CAD meshes/STEP and CC0 HDR recovered.
Actual paths and commands are documented in README.md. No dependency added.

The Cloud Browser rejects local HTTP navigation by URL policy; no local alternate
browser or navigation workaround is used. The already-authorized GitHub Actions
pipeline is the execution environment for repository browser tests. Its previous
run 34631875311 generated real HTTP screenshots/video at build hash
608ad4c8c8577f13ef3350d4f5d13a9390c02e00a955a6d11ae031d252896a82.
The downloaded ZIP was missing its tail; only complete entries verified against
their ZIP CRC32 were recovered. The incomplete generated-model.mjs was rejected.
These observations certify only the R04 baseline, not R05.

## Highest impact baseline defects

- GLB export: r180 GLTFExporter draws DataTexture.image as a DOM image when packing
  metal/rough channels, throwing TypeError. Retain live data; convert export copies.
- O25: the prior test waited for document.hidden with RAF polling, which itself
  stops when the page hides. Use timer polling after disabling focus emulation;
  keep the real hidden-state requirement and record both pages for diagnosis.
- VR04-01: stale camera projection on resize and landscape CTA below fixed bar.
- VR04-02: sparse side support, under-described graphite frame and bearing bridges.
- VR04-03/04: weak sapphire boundary and blurred internal W16 from nested refraction.
- VR04-05/06: crude clasp ends and poorly differentiated tourbillon macro scales.

Independent visual review: separate agent, reference front/back/Clear photos and
the baseline screenshots, no author self-score. Verdict REVISE; CU01/CU06/CU08 Q1
overall, desktop static page approximately Q2. No motion or hardware PASS inferred.

Status: IN_PROGRESS. Implementation is not closure. R05 observations and regressions
must bind to its final build hash before promotion; all nine gates remain required.


## b1d4de99 observation — 2026-09-12

Actions run 34672504478 built the exact source commit. Build hash:
`9b1ae9ef7c83c20c75111b56f0c002d8e1790d71b9e4c8aed85683451c28ec7a`.
All 16 HTTP visual observations completed without JavaScript/console errors.
Visual ZIP SHA256: 93180f75674966b89d022560309148244ebea51f9159624c4f865188d94a60c9.
Assets ZIP SHA256: 8c4c041e4a967b8e23ce20b73de705a6fa096e389d690315a8d5bbc53fb5e47b.
Both downloaded archives matched the runner's upload hash and passed ZIP CRC checks.
GLB export and normal GLTFLoader re-import PASSED: 29,079,208 bytes, SHA256
6cff48848019429d680c4c70724802271b71fba0999ba7be52df70877c48a9dc.
All 16 piston and 16 rod nodes retained independent editable geometry and transforms.

Separate-context visual evaluator reviewed all 16 frames. Actual result: REVISE.
Mobile projection/CTA defects and static W16 blur were resolved in this sample.
CU01 Q1; CU06 Q1 approaching Q2; covered static CU08 Q2, full seven chapters not yet observed.
Remaining MAJORs: black-reading sapphire shell; side cavity and bridge relationships;
shell fasteners suspended in crystal-off state; coarse regulator hub/arch/feet;
insufficient sapphire/metal finish distinction. Minor: hero strap clipping and
small portrait product scale. Numerical/asset checks did not raise visual scores.

## Next bounded repair

- Case fasteners belong to the front/rear case assemblies and share their visibility
  and explosion transform; do not leave shell screws in space when removing glass.
- Bored upper carrier webs connect existing side rails to index/suspension forks,
  with rear clearance around the existing barrel sweep. No random gears added.
- Lower-profile, counterbored cage cap; finer protective arch, bearing rim and
  tapered/bored support feet. Front cap appearance is informed by the official
  photo; dimensions remain ENGINEERING_APPROXIMATION.
- Authored reflection cards are composited over the credited CC0 HDR to reveal
  curved sapphire boundaries. The existing opaque compatibility prepass is reduced
  because all outer transmission samples the full-resolution live capture.
- Frame zoom follows the updated assembly state; portrait/landscape/desktop
  complete-object framing is adjusted, and all seven story sections are observed.

Art iterations run build + observation. Full lifecycle checks run on an explicitly
labelled [full-check] commit or workflow_dispatch; SKIPPED is not PASS. The prior
full run is preserved. No final quality or physical-GPU gate has been awarded.


Observation-condition correction: 02a634e briefly changed the explorer's Object
and Tourbillon presets while fixing story framing. These changed inspection
cameras cannot close fixed-view defects. The next candidate restores the b1d4de99
Object/Tourbillon inspector poses and keeps the intentional story-only framing
repair. Front/back/sides/W16 inspector poses were unchanged. No Q increase is
inferred from a smaller regulator image.

02a634e optical study was rejected: high-radiance cards covered the front lens
with a broad white veil and washed out the rhodium. The next study narrows and
reduces those sources, with a declared lower-reflection front-lens approximation.
No exposure or fixed inspector-camera change is used to claim this correction.
Its front case fasteners are also batched inside their actual assembly, preserving
individual source records, visibility and explosion behavior.

Independent b2 full-page review covered seven desktop chapters and three narrow /
landscape Hero+Explore pairs. CU08 remained Q1 because of the optical regression
and two story camera defects: the W16 chapter did not centre its mechanism; the
suspension chapter clipped the lower two seats. Story-only shot definitions are
revised accordingly, without changing fixed inspector presets. The observer now
also records all six remaining chapters at 390 x 844; absent phone hardware and
continuous transition evidence are not inferred from those static captures.

b1 final regression (run 34672504478): 14/14 ordinary-UI checks passed; 5/6 health
checks passed. O25 failed because both pages actually stayed visible. The next
probe opens a same-window tab with window.open, records actual browser window IDs
and retains document.hidden as a hard assertion. It does not fake Page Visibility.
Full W16-cycle and slow-regulator traces now supplement the existing four phase
screenshots and actual video. Independent health/performance jobs consume the same
immutable build and upload results on failure, without waiting for the long UI suite.

b1 actual software performance at 1920 x 1080 / DPR 1: whole-watch 0.164–0.178 FPS,
W16 0.465–0.472 FPS, exploded 0.211 FPS across three samples each. All miss the frozen
project budget; no physical-device guarantee is awarded. The unused transmission
prepass reduction requires measurement on the new build before an improvement claim.

5d70cab health exposed two remaining observation failures. O25 reported the SAME
real browser window ID for both tabs, but both stayed visible, disproving the
separate-window diagnosis as the remaining cause. The next probe removes video
capture for O25 only (the other health cases retain video), keeps actual tab
activation and all hidden-state assertions, and records the result. No visibility
property or event is synthesized. This is a test-environment hypothesis until run.
O11's fixed 3.6-second polling window ended before the software-rendered simulation
returned. The corrected observer keeps the >3-second simulated-time assertion,
records every sample before asserting, and bounds completion at 30 real seconds.
That wall-time allowance never awards the performance gate.

The [health-check] run rebuilds the unchanged render inputs and reruns health only;
b4's visual, full ordinary-UI and performance runs remain in progress/preserved.
Do not describe skipped jobs as passing. Both source SHAs and their shared app
build hash must be retained in the final evidence record.


b4 independent review closed the four-seat story framing defect, but detected a
new CH02 product/text collision and a phone CH03 note touching the strap. The
candidate increases only CH02 story-camera distance along the same sightline and
reduces two CH03 mobile text margins. All frozen inspector cameras stay unchanged.
The final-build observer repeats all 28 frames; a separate ordinary-UI O32 route
records actual video and state. It does not relabel b4's 100-step/50-cycle suite or
performance samples with the new build hash.

b5 O25 still failed without capture. Locked Playwright 1.55.1 source was inspected:
lib/server/chromium/crPage.js sends focus emulation TRUE from its OWN main-frame
session. The prior NEW-session false calls did not remove this override. The new
health-runner disables that single default override before importing the driver,
records package version, exact change and both hashes, then restores the disposable
test file. No app source, document.hidden, events or test thresholds are changed.
The CDP reference describes this as simulating a focused/active page:
https://chromedevtools.github.io/devtools-protocol/tot/Emulation/#method-setFocusEmulationEnabled
Real same-window activation and document.hidden remain mandatory. This diagnosis
still needs the real run; old failures remain in their original artifacts.

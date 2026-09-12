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

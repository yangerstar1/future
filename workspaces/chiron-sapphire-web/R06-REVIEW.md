# R06 continuation — 2026-09-12

Resume source: `1493516d1e7b080acae2803d269608bdd0aac42d` (b12 challenger).
Preserved prior functional checkpoint: `e56471017a7e1aefde65defb5067676b0fe46ef2` (b11).
The uploaded HTML's entire visible conversation was read. It ends after a handoff
progress message; no final handoff or new main-case CAD is present in this commit.
Do not pretend those missing files were recovered.

G0: clean sparse checkout of `codex/chiron-sapphire-web`; no AGENTS.md in tree.
Plain ES modules; locked Three 0.180.0, esbuild 0.25.10, Playwright 1.55.1.
Local Node 24.19.0 / Python 3.12.14; CI Node 22.16.0 retained. Eight state tests,
build and fifteen geometry tests passed on the unmodified source. Entry and
module responsibilities remain those in README. Only this workspace and its
existing workflow are in scope. Git source persistence and standard Actions are
authorized by the resumed task; no public deployment, new fees or other projects.

Browser: the advertised Cloud Browser returned ERR_BLOCKED_BY_CLIENT for local
HTTP. No alternative local browser is used to evade that restriction. Existing
authorized Actions execute the repository's browser validation. No physical GPU
or phone is available in the local runtime.

Baseline evidence: run 34677282189; build hash
`5043358cbd1f37c3f27d2f9087faadd801b5f3eed6f41dca20d99cd025e74734`.
All 28 PNGs and the health report were recovered from their original artifacts;
both ZIP archives passed CRC validation. Independent visual review remains
REVISE: CU06 Q1, CU08 static Q2, continuous motion not qualified. Measured bright
pixels do not support a claim of widespread clipped exposure; the prominent
defects are flat metal response, coarse curved silhouettes and case volume.

## First repair: redundant drawing and native visibility observation

Baseline whole-watch rendering reports 928 draw calls / 3,237,201 submitted
triangles per frame. The inner watch was shaded in the HDR capture, again in
the final scene, and again in Three's compatibility transmission prepass.
The candidate reuses the live HDR colour AND depth, then shades only the sapphire
surfaces above it. No production geometry, movement nodes or fixed camera changed.
The opaque AO pass is applied to the live inner radiance before presentation.
Visual comparison, resource recovery and timing on the changed build are required.

O25's raw native trace contains a visible event but no hidden event. Its observer
switched back only 1.2 seconds after reading document.hidden, while a software GPU
frame could take several seconds. The candidate waits for the original mandatory
native hidden-event counter before measuring the hidden interval. Assertions are
not weakened, events/properties are not fabricated, old failures remain preserved.
This is a pending diagnosis until a real browser run proves or rejects it.

Status: IN_PROGRESS. No new visual or performance gate is awarded by these edits.

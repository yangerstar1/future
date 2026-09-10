# R03 near-pier visibility repair — predeclared scope

Read-only resume verified production commit 9694cabf4df9c5f4caec57dec3eee3ba6ff46294, R02 artifact and all 26 delivery hashes. The old production state incorrectly listed completed R02/calibration runs as active; this is corrected before starting R03.

## Reuse and true entry points
Blender 4.5.13 LTS / native bpy and mathutils / Cycles CPU. Existing provision.sh pins the G0-verified official archive SHA256. revise_r03.py loads the exact R02 .blend and reuses only AST-selected definitions from the hash-locked build_scene_r01.py. render_r03.py derives the exact existing render_r02.py with explicit output-version substitutions. No package installation, new rendering framework, fee-bearing service, or local Blender render is introduced. Modifications are confined to this workspace and .github/workflows/skyfold-r03.yml; main and other projects are unchanged.

## One root cause
Lower the camera-side working pier by 240m; preserve the high freighter/far berth and original lens/matrices, city geometry, human-scale near area, lighting and material inputs. Shorten pier supports from their grounded end; preserve loader interface tops and extend their lower ends; carry cargo and rail to the new level. Shorten incoming lift, keep real low/high landings, and add a return lift with an aperture through the high rear cross-dock rather than a fake uninterrupted rail.

The 240m shift is a candidate, not a proven solution. Geometric signatures and sparse first-hit rays check intervention integrity. Ray counts are not a percentage of visible screen area, do not grade art, and cannot auto-close defects.

## Execution and acceptance
1. Load fixed R02; verify scene/helper hashes and version; save separate R03.
2. Verify protected collection geometry/transforms and material/world node inputs unchanged.
3. New Blender process: same R02 rendering presets, 16 retained observations plus one additional lift diagnostic.
4. Retrieve and decode originals; inspect primary, neutral, route/interfaces, old primary and five displacement frames for improvement/regression.
5. Update R03 review, production state, evidence index and latest handoff with actual results. No workflow marks art PASS.

## Boundaries
One standard public ubuntu-24.04 job, max 25 minutes, no matrix/farm. Existing 48 runner-hour ceiling, 9.6-hour closing reserve, max concurrency 2 remain ceilings rather than spend targets. Prior turns account for actual usage; tally all runs from job timestamps before delivery. Artifact transport is bounded and retained one day, with recoverable source/checkpoint in the repository and a downloadable conversation package. Account-wide billing/storage remains unexposed; no zero-storage claim.

GitHub official Actions terms and hosted-runner reference rechecked on 2026-09-10. This bounded job builds and regression-tests the repository's native procedural scene code. It is not a standalone CGI service, render farm, or circumvention. Platform acceptance is not guaranteed; stop on restriction. No Release, Pages, paid API or visibility change.

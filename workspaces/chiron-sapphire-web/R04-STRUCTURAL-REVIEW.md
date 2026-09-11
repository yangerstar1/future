# R04 structural rework — inspection ledger

Status: G3 REVISE, not a qualified release. Assurance: SEQUENTIAL_SELF_REVIEW.
User rejected R02's sparse/inaccurate construction and floating components. This is
not an original factory asset with a failed import: R02 was our own incomplete
procedural reconstruction. Its endpoint-only tests did not test solid fitting.

## Source baseline

Official bare-front and bare-back photographs of JCAM37 on the Japanese Sapphire
page inform visible architecture. They are not 578 manufacturing drawings. The
Clear low frontal product photograph informs the case/crowns/strap. Sources are
listed in REFERENCES.md. Hidden topology and all specific bore/pin dimensions are
our digital engineering approximation, not verified manufacturer specifications.

## Actual source changes

| Issue | Root cause | Implemented repair | Evidence / remaining boundary |
|---|---|---|---|
| S01 unsupported internal architecture | R02 used floating wheels and generic bars | Continuous chassis/decks, supported barrels, rear bridges, lower winding region, actual through-arbors | R04 front/back/left/right rendered observations; resemblance still needs stricter improvement |
| S02 floating turbines | Rotating rings without fixed journals | Fixed bearing housing, pedestal and rim; separate 12-vane rotating impeller | Isolated W16 and side views; volute silhouette remains approximate |
| S03 missing cylinder-block body | Four translucent independent plates | Two valid CadQuery solids, eight radial bores each; real STEP solids in mm | generated/sapphire-banks-audit.json plus geometry-audit/report.json |
| S04 crankpin/rod clash | Endpoint constraints passed while radii conflicted | Smaller crankpins, bored eyes/bushes, flat webs, nine bored journal saddles | 721-phase instance/endpoints and actual piston-mesh-in-bore checks |
| S05 disappearing/nil glass | Almost invisible alpha cover and nested transmission exclusions | Closed curved case and lenses; live inner-watch linear HDR capture feeds outer physical transmission | Same-view whole and isolated renders; screen-space approximation, not exact sapphire optics |
| S06 haze in inner glass | Transparent clear alpha makes Three r180 fill transmission target white | Opaque graphite clear color and front-face closed bank material | pass9/pass10 fixed-view comparison; no reference image used as texture |
| S07 ungrounded dial | Three unsupported washer-like discs | Grounded generic 12:1 compound motion works, paired bearing bridges, retaining joints | Geometry and world-node tests; ratios labelled generic, not JCAM37 tooth counts |
| S08 suspension interference | Identical seats for unlike shaft radii; pad/nut overlap | Stepped journal/neck, bored pad, separate lower/upper spring seats, retainer clearances | Measured mesh bore/facet radii and all four endpoint checks at 601 displacement samples |
| S09 flying cage axle collision | Solid shaft/gear/balance parts overlapping | Rear-supported hollow rotating journal, bored gear, thrust seat, stepped cage cap | Registered interface audit; not an exhaustive collision certificate |
| S10 inaccurate exposed metal lugs | Metal L brackets outside sapphire | Curved sapphire horns and continuous cross-pins at the strap origin | Both side views; clasp/strap moulding still require refinement |
| S11 draw-call duplication | Repeated machined parts uploaded separately | Identical piston/rod geometry instanced, preserving all 16+16 solved logical nodes | 721-phase actual instance matrix comparison; no part removed |
| S12 obsolete frame backlog | Software renderer accumulated GPU work while UI advanced | At most one outstanding software GPU fence; visibility/context cleanup | Seven normal-UI views run; full lifecycle regression still required |

## Actually observed

`evidence/R04/pass10` contains the same model, 1440x1000 / DPR1:
front, back, left, right, isolated engine, isolated tourbillon (neutral) and
hero (studio). The fixed inspector views were reached by normal buttons. Their
observations.json binds source/build hashes, camera, state and software backend.
They are not physical-phone tests or an HTTP cold start.

`evidence/R04/geometry-audit/report.json` is a generated-geometry audit with 15
checks, including 223 measured annular interfaces, every actual piston mesh in its
CAD bore, all 16+16 render-instance transforms and all four shock endpoints. The
canvas stub supplies only inscription metadata: this is explicitly NOT a rendered
visual acceptance report. Fifty transform cycles do NOT certify fifty user-input
cycles. Repeated instance geometry does not prove product accuracy.

The optional 800x900/12-sample path-tracing comparison completed in ~404 seconds
on software SwiftShader. It was noisy and too slow for the default experience.
It is retained as a rejected optical challenger, not a website FPS result.

## Still blocking

CU01/CU06/CU08 are NOT Q3. The side profile, macro finish, part-to-reference layout,
strap/clasp detail and full assembly-space collision coverage still need work.
No 55 FPS desktop or 30 FPS real-phone qualification exists. Full normal-UI
reassembly, cross-state, context-loss, mobile and HTTP cold-start evidence must be
rerun after rendering/asset changes. Do not inherit an R02 test result.

## Resume

Do not rebuild the old R02 approximation. Read this ledger, current source,
REFERENCES.md, generated asset audits and the exact build manifest. Continue from
R04 and compare both neutral and studio, including case-off oblique and macro
views. Keep source/asset versions together. Never close a visual issue solely
because a numeric test passes; never add random gears to improve density.

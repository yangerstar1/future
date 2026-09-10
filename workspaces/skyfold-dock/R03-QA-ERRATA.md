# R03 QA errata and bounded R03B correction

R03 source c507467ccf7b24ab513184279b2b57673145d7e3; Actions 34498166928; scene e1f8815c36bb30b8c245715fb56fd9c3a38c77955535ea99b4011170a95d4787. Artifact 10160965303 ZIP c76d105fe41962763d85df18cee6535dd5d261e3cfc5398b9543e74caba19723 retrieved. 28 file hashes and 17 decoded original PNGs checked. Protected collection signatures agree. Render process elapsed 371.47 seconds; not full-job or billing time.

Actual primary, legacy R01 primary, route, craft and interface images inspected: lowering the near pier exposes the freighter in the unchanged primary; city and craft quality still need work. No G2 promotion.

Two implementation issues were found before checkpoint delivery:
1. The added O05_LIFT_R03_DIAGNOSTIC build-manifest matrix is stale because the dependency graph was not flushed after creating that camera. The actual OBSERVATIONS matrix is correct. This is a metadata defect; no image was fabricated.
2. The return lift upper rail starts at the shaft centre y=1608 instead of terminating on the supported rear slab beyond the aperture edge y=1615. Move the two upper endpoints to y=1615.25; do not move the scene/cameras to hide it.

R03B applies only these QA corrections and adds one return-lift diagnostic. Original 17 observations remain and camera matrices/lenses are now checked against the build manifest in a new process. The prior R03 snapshots remain in their immutable run/evidence branch. R03B cannot auto-pass art. Actual result must be retrieved/reviewed and written to production state and latest handoff.

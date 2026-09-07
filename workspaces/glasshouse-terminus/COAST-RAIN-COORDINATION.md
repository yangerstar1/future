# Coast / rain continuation coordination

The user explicitly rejected image generation and requests actual rain/materials, realistic ocean and rocky coast in the existing project. Generated images are not project evidence.

## Completed native coast source, do not rebuild or discard

COAST-R01 has been modeled from the exact R03 rain/material checkpoint. Actual packed master is 105,907,206 bytes, SHA-256 `1be3507f7c31ed2f8e5431aefaf787ff414a29fdce696b596a2baff68b0789c6`. Native JONSWAP Ocean geometry and OceanFoam/CoastalWash attributes evaluate and replay at frames451/460/451. Licensed coastal_cliff_04 scan and seaside_rock maps are integrated; original building/train/rain objects preserved.

Persistent source: **84570c8224f709784b580a23d330b2a0f522fcf9**, `workspaces/glasshouse-terminus/output/g4-coast-r01`. This Git archive uses verified lossless master-parts because the native .blend exceeds the chosen per-file cap. Run `python3 restore_master.py restore .` inside that output folder. Actions checkpoint artifact10028760007 contains the complete native .blend; no quality-reducing save or rebuild needed. Asset source commit01ba5eb4464fac76450cf68f2eccb0b0366bb840.

Original build34149137700 saved successfully, then stopped at the98MB storage guard; no images rendered. Transport recovery34149501788 saved exact parts successfully. Its pending native-review job101828652348 was canceled before starting when R04 optics34149669782 entered the default single-pending concurrency queue. No coast image was rendered or reviewed yet; do not call this a visual pass.

## Queue policy for subsequent native rendering

Preserve active R03 and pending R04. Future shared production concurrency should use:

```yaml
concurrency:
  group: glasshouse-production
  cancel-in-progress: false
  queue: max
```

GitHub.com now supports this natively (official May7,2026 changelog and current docs). It keeps one production renderer but avoids replacing older pending jobs. Do not trigger a new request using the old default single-pending queue, since that cancels another valid observation job. Do not modify currently running snapshots, cancel R04, or create substitute parallel production rendering groups.

Primary sources: https://github.blog/changelog/2026-05-07-github-actions-concurrency-groups-now-allow-larger-queues/ ; https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

## Integration boundary

R04 `correct_g4_rain_optics.py` correctly targets the two owned R03 rain node groups and native shutter settings. Once its saved checkpoint is available, the next coast candidate should import only those actual corrected node groups/settings onto the preserved coast master, rather than revert sea/cliffs to R03 or rerun the entire environment build. Assert their measured prototype/lifetime-ID configuration and preserve all coast geometry/materials/cameras. New native combined renders still decide quality; no automatic R04 or G4 acceptance.

Keep original R03 needle-rain images, all checkpoints and failures. State/handoff must distinguish coast/source preservation from native-image acceptance, and distinguish inherited rain/material observations from newly rendered combined coast observations.

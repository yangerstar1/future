# Forecast outage: completed E0/E1/E2 research

Status: all nine model-stage jobs completed; independent numerical audit PASS; publication readiness NOT established.

Read `RESEARCH-RESULTS.md` and `DELIVERY-STATE.json` first. Do not restart from an empty workspace or describe the initial fallback hypothesis as proven.

## Executed evidence

| Stage | Run | Source commit |
|---|---|---|
| E0 | 34237152841 | 959f0d955b09b2b7257a4b691f36d6417bce13ae |
| E1 | 34238612233 | 3e9222c327d38dbee9d55ca7dcfd17dff9e63308 |
| E2 | 34242688274 | b1e4a5aa828c7b2cdbc822c68d47851a5b20f2b0 |

For each stage/model, the immutable evidence branch is `evidence/forecast-<stage>-<model>-<run>`, with model keys `bolt-tiny`, `chronos2-small`, `chronos2-synth`. Raw arrays, cases, masks, targets, choices, package versions, hashes, and logs are preserved there. The scripts and frozen protocols are in this workspace.

Only standard CPU GitHub Actions and the current ChatGPT computation environment were used. No GPU, paid runner, scheduled workflow, or foundation-model training was introduced. Lightweight selectors were fitted. Main and the Glasshouse Terminus production branch were not changed by this research.

## Results and boundaries

The original adaptive-fallback candidate does not show consistent improvement. The synthesized-data checkpoint benefits more from a simple equal ensemble than from the full gate. Outage-matched three-window historical selection worsens Bolt and Small. Horizon alignment helps some checkpoints but is not a novel algorithm or evidence of a Chronos implementation bug. E2 training-regime ablations do not rescue a universal fallback claim.

The independent audit recomputes losses and causal inputs from saved arrays; it does not rerun checkpoint inference. E2 separately reproduces 131328 original gate choices exactly. Bootstrap intervals condition on the fixed selected datasets/channels and fitted gates. E1 and E2 reuse an inspected test cohort and are exploratory.

An approximately 4700-word English paper draft, its PDF, full analysis code, tables, figures, and reproduction packages were produced as conversation attachments. They are not all stored on this branch. This branch stores the executed research source, evidence pointers, result report, and audit summary; do not invent a repository PDF path.

Before further implementation, read the executed code, protocols, amendments, and evidence. A stronger publication claim requires distinct novelty, comparison with closest work, independent model families, a genuinely unused cohort, stronger fitted baselines, and/or real outage validation. Do not tune these test outputs and call the result confirmation.

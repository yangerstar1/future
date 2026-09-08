# Forecast-outage research: read-only reconnaissance

Status: reconnaissance, no experimental claims yet.

## Authorization and isolation
The user authorized execution using only the current ChatGPT computation environment and standard GitHub Actions in yangerstar1/future. No paid compute, external services requiring payment, schedules, infinite loops, account multiplexing, or changes to the Glasshouse Terminus project are authorized by this workspace.

GitHub reconnaissance on 2026-09-08 verified main at 96f6321e6cef2ef37b97c85b460025079f006c12, tree 01acff908de2b644b0a056d891a75e11b139bfd5. The complete main tree contains only README.md. That README identifies the existing production branch as codex/glasshouse-terminus. Research is isolated on research/forecast-outage, branched from main; main and all existing production/evidence branches remain untouched.

There is no existing research entry point, dependency manifest, or test command on main. New paths under workspaces/forecast-outage and a uniquely named workflow are intentional additions, not inferred existing structure. Existing Actions filenames on the production branch were inspected read-only.

## Local environment
Measured: Python 3.13.5; torch 2.10.0+cpu; CUDA unavailable; CPU quota 4 cores; cgroup memory limit 4 GiB. Public DNS requests fail in this environment. Therefore model/data download and model inference will run on ordinary ubuntu-24.04 Actions runners; local computation is used for code validation and analysis of returned evidence.

## Reuse audit
Use official chronos-forecasting inference rather than implementing a foundation model. Evaluate simple mature fallback rules before learning selectors. Reuse upstream ETT/Time-Series-Library data and SensorFault-Bench's input-corruption/unchanged-target distinction. This project is NOT a complete reproduction of SensorFault-Bench or GIFT-Eval.

Closest verified work: SensorFault-Bench, arXiv:2605.10822 (2026), already studies Chronos-2, sensor faults and fault-transfer evaluation. Incomplete-series conformal prediction and selective forecasting also exist. Merely observing degradation or adding a gate is not claimed novel. The initial candidate concerns equal-count missingness placement and deployable fallback decisions; novelty remains unverified.

## Execution gates
1. Inspect actual Actions environment, public dataset manifests, model revisions and prediction signatures; fail visibly on incompatibility.
2. Freeze an exploratory protocol before reading its evaluation results. Keep all failures and negative results.
3. Only observed input histories may influence forecasts, scales and selectors. Never fill using evaluation targets. Preserve timestamps when handling NaNs.
4. Save source/version hashes, masks, origins, predictions, metrics and logs. Report synthetic missingness as controlled stress tests, not real fault validation.
5. No SCI/CCF-A readiness claim without adequate novelty and evidence. No autonomous background promise; workflows are finite, with explicit timeouts.

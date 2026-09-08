# E0 execution amendments

## A1: before any E0 forecasting results were produced

Original frozen source: 595624c7b5ee916bc5878075d8e771a58e4fc93d.
Failed run: 34236223177. All three model jobs stopped in data acquisition, before loading a forecasting checkpoint or producing performance results. Failure evidence is retained on the per-model evidence branches.
Diagnostic run: 34236652582, evidence/forecast-data-api-34236652582.

Verified facts and narrow repairs:

1. The pinned weather CSV has 52,696 rows and one exactly duplicated record at 2020-05-12 06:00:00 (all numeric values identical). Remove only exact whole-row duplicates before timestamp uniqueness validation; still fail for conflicting duplicate timestamps or descending timestamps. Record original row count and removal count in the manifest. The existing hourly reindex/resampling and original-missingness rules are unchanged. A 100-minute gap also exists in the original weather timeline and is not synthetically filled with hidden targets.
2. Installed Chronos2Pipeline rejects a 2-D tensor and requires (n_series, n_variates, history_length). Add a singleton variate dimension only for that verified pipeline class, preserving independent univariate groups. ChronosBolt's 2-D input is unchanged. Existing batched-versus-individual and finite-output guards remain mandatory.
3. Preserve the selected resampled series and timestamp arrays in selected-series.npz so an independent audit can reconstruct contexts, past-only replay labels and all baseline predictions without relying on source code claims.
4. Exclude the actively written run.log from in-process SHA256.json. All stable result files remain hashed; downloaded ZIPs receive a separate final hash.

No changes to datasets, model revisions, channel selection, origins, masks, forecast horizon/context, selector features/hyperparameters or method comparisons. No performance-based dataset exclusion.

## Independent statistics clarification, before E0 performance inspection
The frozen primary analysis remains 10,000 paired circular moving-block bootstrap replicates with block length 4 test origins. All methods/channels/masks share draws. ETTh1 and ETTh2 additionally share draws because their dates align; this preserves cross-transformer temporal dependence rather than treating them as independent datasets. Domains are fixed, not a random sample of possible deployment domains. Intervals condition on fitted selectors, are descriptive and unadjusted for multiple comparisons; they are not familywise-error-controlled novelty claims.

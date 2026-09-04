#!/usr/bin/env bash
set -euo pipefail
# Publish data under existing contents:write only; do not copy or modify workflows.
# Source code remains at the recorded GITHUB_SHA on the production branch.
ROOT="${1:?relative evidence root required}"
STAGE="${2:?stage label required}"
case "$ROOT" in workspaces/glasshouse-terminus/output/*|evidence/asset-recon) ;; *) echo 'Unapproved evidence path'; exit 2;; esac
case "$STAGE" in *[!a-z0-9-]*|'') echo 'Invalid stage label'; exit 2;; esac
TARGET="evidence/${STAGE}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
if git ls-remote --heads origin "$TARGET" | grep -q .; then echo 'Evidence ref already exists; refusing overwrite'; exit 1; fi
git fetch --depth=1 origin main
BASE=$(git rev-parse FETCH_HEAD)
if git ls-tree -r --name-only "$BASE" .github/workflows | grep -q .; then echo 'Unexpected main workflows; stop and inspect permissions'; exit 1; fi
export GIT_INDEX_FILE="$RUNNER_TEMP/evidence-${STAGE}-${GITHUB_RUN_ID}.index"
if [ -e "$GIT_INDEX_FILE" ]; then echo 'Temporary index exists; refusing overwrite'; exit 1; fi
trap 'rm -f "$GIT_INDEX_FILE"' EXIT
git read-tree "$BASE"
git add -- "$ROOT"
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
TREE=$(git write-tree)
if git ls-tree -r --name-only "$TREE" .github/workflows | grep -q .; then echo 'Evidence contains workflows; refusing push'; exit 1; fi
COMMIT=$(printf 'evidence: %s run %s; source %s\n' "$STAGE" "$GITHUB_RUN_ID" "$GITHUB_SHA" | git commit-tree "$TREE" -p "$BASE")
git push origin "$COMMIT:refs/heads/$TARGET"
printf 'PERSISTED_EVIDENCE_REF=%s\nPERSISTED_EVIDENCE_COMMIT=%s\n' "$TARGET" "$COMMIT"

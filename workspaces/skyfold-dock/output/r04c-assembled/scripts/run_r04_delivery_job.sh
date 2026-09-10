#!/usr/bin/env bash
set -euo pipefail
REF="${1:?immutable scene commit}"; ROLE="${2:?role}"
[[ "$REF" =~ ^[0-9a-f]{40}$ ]] || exit 2
case "$ROLE" in stills|motion_a|motion_b) ;; *) exit 2;; esac
ROOT="$PWD/workspaces/skyfold-dock"
OUT="$ROOT/output/r04c-final/$ROLE"
TMP="${RUNNER_TEMP:?}/skyfold-r04c-$ROLE-frames"
mkdir -p "$OUT" "$TMP"
export SKYFOLD_OUT="$OUT"
export R04_ROLE="$ROLE"
collect() {
  local code="${1:-0}"
  if [ "$ROLE" != stills ]; then
    mkdir -p "$OUT/samples"
    for p in "$TMP"/*.json "$TMP"/*.mp4 "$TMP"/*.log "$TMP"/*time.txt; do [ ! -f "$p" ] || cp "$p" "$OUT/"; done
    for f in 0001 0005 0025 0049 0073 0096 0097 0121 0145 0169 0192; do
      [ ! -f "$TMP/frame_$f.png" ] || cp "$TMP/frame_$f.png" "$OUT/samples/"
    done
    LAST=$(find "$TMP" -maxdepth 1 -name 'frame_*.png' | sort | tail -1)
    [ -z "$LAST" ] || cp "$LAST" "$OUT/samples/"
  fi
  python3 - "$OUT" "$code" <<'PY'
import sys,json,hashlib,os
from pathlib import Path
p=Path(sys.argv[1]);rows={}
for f in p.rglob('*'):
 if f.is_file() and f.name!='CHECKSUMS.json':
  assert f.stat().st_size<80_000_000,(f.name,f.stat().st_size)
  rows[str(f.relative_to(p))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
assert sum(v['bytes'] for v in rows.values())<120_000_000
(p/'CHECKSUMS.json').write_text(json.dumps({'role':os.environ['R04_ROLE'],'run_id':os.environ['GITHUB_RUN_ID'],'source_sha':os.environ['GITHUB_SHA'],'exit_code':int(sys.argv[2]),'files':rows,'visual_verdict':'REVIEW_REQUIRED','full_movie_frames':'Rendered in temporary job directory; encoded video, all frame hashes and selected PNGs retained'},indent=2))
PY
}
trap 'r=$?; set +e; collect "$r"; exit "$r"' EXIT
git fetch --depth=1 origin "$REF"
git restore --source=FETCH_HEAD -- workspaces/skyfold-dock/output/r04c-final/source
SOURCE="$ROOT/output/r04c-final/source"
python3 - "$SOURCE" "$REF" > "$OUT/INPUT.json" <<'PY'
import sys,json,hashlib,os
from pathlib import Path
p=Path(sys.argv[1]);m=json.loads((p/'BUILD-MANIFEST.json').read_text());h=hashlib.sha256((p/'skyfold-r04c.blend').read_bytes()).hexdigest();assert h==m['scene_sha256']
print(json.dumps({'scene_archive_commit':sys.argv[2],'scene_sha256':h,'scene_source_sha':m['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'role':os.environ['R04_ROLE'],'motion_preview_resolution':[1280,720],'P2_1080_pass':False},indent=2))
PY
python3 -m py_compile "$ROOT/render_r04.py" "$ROOT/encode_actual_frames.py"
(date -u; free -b; df -B1 .; sha256sum "$ROOT/render_r04.py" "$ROOT/encode_actual_frames.py") > "$OUT/environment.txt"
bash "$ROOT/provision.sh" > "$OUT/provision.log" 2>&1
# GITHUB_PATH applies only to later steps; use the already-inspected binary path in this step.
export PATH="$RUNNER_TEMP/skyfold-tools/blender-4.5.13-linux-x64:$PATH"
if [ "$ROLE" = stills ]; then
  export R04_MODE=stills
  /usr/bin/time -v -o "$OUT/render-time.txt" blender -b "$SOURCE/skyfold-r04c.blend" -t 4 --python-exit-code 1 -P "$ROOT/render_r04.py" > "$OUT/render.log" 2>&1
  collect 0
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
  git switch -c "evidence/skyfold-r04c-stills-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
  git add "$SOURCE"
  for f in R04_HERO_f001.png R04_SECOND_f001.png R04_GALLERY_CRAFT_f001.png R04_HERO_NEUTRAL_f001.png R04_ROUTE_FULL_f001.png R04_RETURN_LIFT_FULL_f001.png OBSERVATIONS.json COMPLETE.json CHECKSUMS.json INPUT.json render-time.txt render.log environment.txt; do [ ! -f "$OUT/$f" ] || git add "$OUT/$f"; done
  git commit -m "skyfold R04C actual target-size stills ${GITHUB_RUN_ID}; artistic review pending"
  git push origin HEAD
else
  export R04_MODE=motion SKYFOLD_OUT="$TMP" FRAME_DIR="$TMP" MOTION_WIDTH=1280 MOTION_SAMPLES=12
  if [ "$ROLE" = motion_a ]; then export FRAME_START=1 FRAME_END=96; else export FRAME_START=97 FRAME_END=192; fi
  /usr/bin/time -v -o "$TMP/render-time.txt" blender -b "$SOURCE/skyfold-r04c.blend" -t 4 --python-exit-code 1 -P "$ROOT/render_r04.py" > "$TMP/render.log" 2>&1
  /usr/bin/time -v -o "$TMP/encode-time.txt" blender -b --factory-startup -t 4 --python-exit-code 1 -P "$ROOT/encode_actual_frames.py" > "$TMP/encode.log" 2>&1
  collect 0
fi

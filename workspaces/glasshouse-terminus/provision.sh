#!/usr/bin/env bash
set -euo pipefail
# Default behavior retained for existing movie/QA workflows. Render-only is opt-in.
# R04 log101832302810 verified Blender downloaded and checksum passed, but97 apt
# dependencies for codecs stalled at the mirror before any actual art execution.
VERSION=4.5.13
PROFILE="${BLENDER_PROVISION_PROFILE:-full}"
case "$PROFILE" in full|render-only) ;; *) echo 'Unknown BLENDER_PROVISION_PROFILE'; exit 2;; esac
ROOT="${RUNNER_TEMP:?}/glasshouse-tools"
mkdir -p "$ROOT"
cd "$ROOT"
ARCHIVE="blender-${VERSION}-linux-x64.tar.xz"
BASE="https://download.blender.org/release/Blender4.5"
curl --fail --location --retry 1 --max-time 90 "$BASE/blender-${VERSION}.sha256" -o official.sha256
curl --fail --location --retry 1 --max-time 300 --max-filesize 650000000 "$BASE/$ARCHIVE" -o "$ARCHIVE"
grep " $ARCHIVE$" official.sha256 > selected.sha256
sha256sum --check selected.sha256
tar -xf "$ARCHIVE"
rm "$ARCHIVE"
BIN="$ROOT/blender-${VERSION}-linux-x64/blender"
if [ "$PROFILE" = full ]; then
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends ffmpeg libxi6 libxrender1 libxkbcommon0 libsm6 libgl1 python3-pil mesa-utils
else
  # Reuse installed runner libraries; no assumed missing-package list or mirror swap.
  # Stop with evidence if this actual runner differs from the inspected one.
  ldd "$BIN" | tee "$ROOT/blender-linked-libraries.txt"
  if grep -q 'not found' "$ROOT/blender-linked-libraries.txt"; then
    echo 'Render-only prerequisites differ: inspect linked-libraries before adapting.'; exit 3
  fi
  "$BIN" --background --factory-startup --python-exit-code 1 --python-expr "import bpy; assert bpy.app.version[:3]==(4,5,13); bpy.context.scene.render.engine='CYCLES'; print('RENDER_ONLY_NATIVE_CYCLES_STARTUP_OK',bpy.app.version_string)"
  echo 'No FFmpeg/Pillow/mesa-utils installation: this profile renders PNGs; encode actual frames separately or explicitly use full.'
fi
printf '%s\n' "$ROOT/blender-${VERSION}-linux-x64" >> "$GITHUB_PATH"
"$BIN" --background --factory-startup --version

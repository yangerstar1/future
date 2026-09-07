#!/usr/bin/env bash
set -euo pipefail
# Ephemeral public runner only. No cache, private assets, services, or paid API.
VERSION=4.5.13
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
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends ffmpeg libxi6 libxrender1 libxkbcommon0 libsm6 libgl1 python3-pil mesa-utils
printf '%s\n' "$ROOT/blender-${VERSION}-linux-x64" >> "$GITHUB_PATH"
"$ROOT/blender-${VERSION}-linux-x64/blender" --background --factory-startup --version

#!/usr/bin/env bash
set -euo pipefail
ROOT="${RUNNER_TEMP:?}/skyfold-tools"; mkdir -p "$ROOT"; cd "$ROOT"
V=4.5.13; ARCHIVE="blender-${V}-linux-x64.tar.xz"
curl --fail --location --retry 1 --max-time 300 --max-filesize 650000000 "https://download.blender.org/release/Blender4.5/$ARCHIVE" -o "$ARCHIVE"
printf '%s  %s\n' da4e69b06b75b9e642d106496c50e7e240218b411d2f6e18271c1d1d819cef91 "$ARCHIVE" | sha256sum --check
# Digest above came from official SHA256 file actually validated in G0 run34486735492.
tar -xf "$ARCHIVE";rm "$ARCHIVE"
BIN="$ROOT/blender-${V}-linux-x64/blender"
ldd "$BIN" | tee "${SKYFOLD_OUT:?}/libraries.log"
if grep -q 'not found' "$SKYFOLD_OUT/libraries.log";then echo 'Runtime mismatch: stop before adapting';exit 3;fi
"$BIN" --background --factory-startup --version
printf '%s\n' "$ROOT/blender-${V}-linux-x64" >> "${GITHUB_PATH:?}"

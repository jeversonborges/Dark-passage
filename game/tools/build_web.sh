#!/bin/bash
# Build Web completo a partir desta pasta: cópia com áudio re-encodado (cabe no limite do claude.ai),
# export do Godot e divisão em partes < 15 MB.   bash tools/build_web.sh [saida=dist/artifact]
set -e
G=$(cd "$(dirname "$0")/.." && pwd)
GODOT=${GODOT:-godot}
OUT=${1:-$G/dist/artifact}
W=${WEB_TMP:-/tmp/dark_passage_web}
mkdir -p "$W"
(cd "$G" && tar cf - --exclude=.godot --exclude=build --exclude=dist --exclude=fontes --exclude=assets/ext/audio .) | (cd "$W" && tar xf -)
# áudio: só re-encoda o que mudou desde a última vez
mkdir -p "$W/assets/ext/audio"
cd "$G/assets/ext/audio"
find . -type f | while IFS= read -r f; do
  t="$W/assets/ext/audio/$f"
  if [ ! -f "$t" ] || [ "$f" -nt "$t" ]; then
    mkdir -p "$(dirname "$t")"; cp "$f" "$t"
    case "$f" in *.ogg) (cd "$W/assets/ext/audio" && bash "$G/tools/web_audio_enc.sh" "$f");; esac
  fi
done
cd "$W"
"$GODOT" --headless --path . --import > /dev/null 2>&1 || true
mkdir -p build/web
"$GODOT" --headless --path . --export-release "Web" build/web/index.html
rm -rf "$OUT"
python3 tools/make_artifact.py build/web "$OUT"

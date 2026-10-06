#!/bin/bash
cd /home/claude/work/amb
SAMPLES=32 blender -b -P src/tiles.py -- tiles_raw > tiles.log 2>&1
python3 src/post.py tiles tiles_raw tiles_out >> tiles.log 2>&1
SAMPLE_SCALE=0.6 blender -b -P src/render_assets.py -- assets_raw > assets.log 2>&1
mkdir -p assets_out
for f in assets_raw/*_raw.png; do b=$(basename $f _raw.png); python3 src/post.py asset $f assets_out/$b.png; cp assets_raw/$b.json assets_out/ 2>/dev/null; done
python3 src/luzes.py luzes_out
echo DONE > done.flag

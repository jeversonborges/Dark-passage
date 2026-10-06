cd /home/claude/work/amb
SAMPLES=32 blender -b -P src/tiles.py -- tiles2_raw areia duna cinza vidro leito lama barranca musgo brejo mata vala cascalho > tiles2.log 2>&1
python3 src/post.py tiles tiles2_raw tiles2_out >> tiles2.log 2>&1
echo DONE > solos.flag

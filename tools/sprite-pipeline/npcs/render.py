# Render dos NPCs: usa o render.py dos monstros (mesma câmera, luz e quadros brutos em 2x), procurando o módulo
# do NPC nesta pasta. Uso (bpy 4.2 em venv, ver LEIAME.md):
#   /opt/bpy42/bin/python render.py -- capita_odete /tmp/brutos/capita_odete            # tudo
#   /opt/bpy42/bin/python render.py -- capita_odete /tmp/brutos/capita_odete teste      # conferência rápida
import os, sys, runpy
H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [H, os.path.join(H, "..", "monstros")]
if "--" not in sys.argv: sys.argv = ["blender", "--"] + sys.argv[1:]
runpy.run_path(os.path.join(H, "..", "monstros", "render.py"), run_name="__main__")

# Rua em ruínas da prévia Dark Eden (darkeden/dp_render.py), com o Anjo e o Humano novos.
# Uso: blender -b -P cena.py -- <saida.png>
import bpy, sys, os, math
from mathutils import Vector
here = os.path.dirname(os.path.abspath(__file__)); de = os.path.join(here, "..", "darkeden")
sys.path.insert(0, here); sys.path.insert(0, de)
out = sys.argv[sys.argv.index("--")+1]
src = open(os.path.join(de, "dp_render.py")).read()
# troca os personagens antigos pelos novos (armaduras com animação)
src = src.replace('rc = M.make_root("cadaver", (2.0,-.2,.17)); rc.rotation_euler = (math.radians(-88), 0, math.radians(110)); M.humano(rc)',
                  'NEW_CADAVER()')
src = src.replace('ra = M.make_root("anjo", pa, face(pa, ph + toward_cam)); M.anjo(ra)', 'NEW_CHARS(pa, ph, face, toward_cam)')
src = src.replace('rh = M.make_root("humano", ph, face(ph, pa + toward_cam)); M.humano(rh)', '')
src = src.replace('sc.render.filepath = out; bpy.ops.render.render(write_still=True)',
                  'sc.frame_set(FRAME); sc.render.filepath = out; bpy.ops.render.render(write_still=True)')

import classes, anims
def NEW_CHARS(pa, ph, face, toward_cam):
    a, _ = classes.anjo(); acts = anims.anjo_anims(a); a.animation_data.action = acts["idle"]
    a.location = pa; a.rotation_euler = (0, 0, face(pa, ph + toward_cam))
    h, info = classes.humano(); hacts, _ = anims.humano_anims(h, info["flash"]); h.animation_data.action = hacts["idle"]
    info["flash"].hide_render = True
    h.location = ph; h.rotation_euler = (0, 0, face(ph, pa + toward_cam))
def NEW_CADAVER():
    c, info = classes.humano(); acts, _ = anims.humano_anims(c, info["flash"]); c.animation_data.action = acts["idle"]
    info["flash"].hide_render = True
    c.location = (2.0, -.2, .17); c.rotation_euler = (math.radians(-88), 0, math.radians(110))
src = src.replace('point(ph + Vector((.25,-.1,.9)), (.4,1,.15), 25, .05)', 'point(ph + Vector((.2,-.15,.95)), (.45,.75,1), 4, .05)')  # brilho fraco da água benta
sys.argv = [sys.argv[0], "--", "scene", out]
g = {"__name__": "__main__", "NEW_CHARS": NEW_CHARS, "NEW_CADAVER": NEW_CADAVER, "FRAME": 1, "__file__": os.path.join(de, "dp_render.py")}
exec(compile(src, "dp_render.py", "exec"), g)

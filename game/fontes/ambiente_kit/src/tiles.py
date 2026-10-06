# Renderiza blocos periódicos de chão (4x4 tiles) para cada tipo de piso.
# Uso: blender -b -P tiles.py -- <saida_dir> [tipo ...]
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit as K
from mathutils import Vector

argv = sys.argv[sys.argv.index("--")+1:]
out = argv[0]; os.makedirs(out, exist_ok=True)
KINDS = {  # tipo: (material, dungeon?)
    "calcamento": ("calcamento", False), "terra": ("terra", False), "cemiterio": ("cemiterio", False),
    "laje_capela": ("capela", False), "cripta": ("cripta", True), "ossario": ("ossos", True),
    "chapa_matadouro": ("grade", True), "laje_trombeta": ("laje", True),
}
for _k in K.SOLOS: KINDS[_k] = (_k, False)
kinds = argv[1:] or list(KINDS)
N = 4; P = N * K.T
for kind in kinds:
    mk, dung = KINDS[kind]
    sc = K.reset(); sc.render.film_transparent = False
    cam = K.make_cam(); K.lights(dung)
    bpy.ops.mesh.primitive_plane_add(size=P*3, location=(P/2, P/2, 0))
    pl = bpy.context.object
    pl.data.materials.append(K.mat_ground(mk, (P, P), {"cripta": 3.0, "laje": 5.0}.get(mk, 1.0)))
    # enquadra o bloco 4x4 com 1 tile de margem
    corners = [Vector((x, y, 0)) for x in (-K.T, P+K.T) for y in (-K.T, P+K.T)]
    meta = K.render_asset(f"{out}/{kind}", [], anchor=(0, 0, 0), samples=int(os.environ.get("SAMPLES", 64)), pad=0, shadows=False, extra=corners)
    centers = {}
    for i in range(N):
        for j in range(N):
            x, y = K.screen_xy(((i+.5)*K.T, (j+.5)*K.T, 0)); ax, ay = K.screen_xy((0, 0, 0))
            centers[f"{i}_{j}"] = [meta["anchor"][0] + (x-ax)*K.PX_M, meta["anchor"][1] - (y-ay)*K.PX_M]
    meta["centers"] = centers
    json.dump(meta, open(f"{out}/{kind}.json", "w"))

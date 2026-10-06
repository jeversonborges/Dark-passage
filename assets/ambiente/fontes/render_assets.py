# Renderiza assets do kit. Uso:
#   blender42 -b -P render_assets.py -- <raw_dir> [nome ...]   (sem nomes = todos)
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit as K
import assets as A

argv = sys.argv[sys.argv.index("--")+1:]
out = argv[0]; os.makedirs(out, exist_ok=True)
names = argv[1:] or list(A.REG)
scale_samples = float(os.environ.get("SAMPLE_SCALE", 1))
import traceback
def run(name):
    info = A.REG[name]
    for orient in (("a", "b") if info["walls"] else ("",)):
        K._cache.clear(); K.DUST = (.05, .045, .04) if info["dungeon"] else (.26, .19, .115); K.reset(); K.make_cam(); K.lights(info["dungeon"])
        K.CLAMP = not info.get("no_catcher")
        if K.CLAMP: K.shadow_catcher()
        before = set(bpy.data.objects)
        meta = info["fn"](A.M()) or {}
        new = [o for o in bpy.data.objects if o not in before]
        if info.get("bury"):
            for o in new:
                if o.parent is None and not o.name.startswith("dt"):
                    o.location.z -= info["bury"]
            # dunas criadas pela função ficam na linha da areia: sobe de volta
            for o in new:
                if o.parent is None and o.data and getattr(o.data, "materials", None) and len(o.data.materials) and o.data.materials[0].name.startswith("areia_monte"):
                    o.location.z += info["bury"]
            bpy.context.view_layer.update()
        if orient == "b":
            piv = bpy.data.objects.new("piv", None); bpy.context.scene.collection.objects.link(piv)
            for o in new:
                if o.parent is None: o.parent = piv
            piv.rotation_euler = (0, 0, math.radians(90))
            bpy.context.view_layer.update()
        tag = name + (f"_{orient}" if orient else "")
        r = K.render_asset(f"{out}/{tag}", [o for o in new if o.type == 'MESH'], samples=int(info["samples"]*scale_samples))
        r.update(meta); r["categoria"] = info["cat"]; r["footprint_tiles"] = list(info["fp"])
        if orient: r["orientacao"] = {"a": "ao longo do eixo X do mapa (face voltada para baixo-esquerda)", "b": "ao longo do eixo Y do mapa (face voltada para baixo-direita)"}[orient]
        r["descricao"] = (info["fn"].__doc__ or "").strip().replace("\n", " ")
        json.dump(r, open(f"{out}/{tag}.json", "w"), ensure_ascii=False)
        print("OK", tag, r["w"], r["h"], flush=True)

for name in names:
    if os.environ.get("SKIP_DONE") and os.path.exists(f"{out}/{name}.json") or os.environ.get("SKIP_DONE") and os.path.exists(f"{out}/{name}_a.json"):
        print("JA", name, flush=True); continue
    try: run(name)
    except Exception:
        print("ERRO", name, traceback.format_exc().strip().splitlines()[-1], flush=True)

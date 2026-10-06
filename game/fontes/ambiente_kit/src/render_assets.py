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
for name in names:
    info = A.REG[name]
    for orient in (("a", "b") if info["walls"] else ("",)):
        K._cache.clear(); K.reset(); K.make_cam(); K.lights(info["dungeon"]); K.shadow_catcher()
        before = set(bpy.data.objects)
        meta = info["fn"](A.M()) or {}
        new = [o for o in bpy.data.objects if o not in before]
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

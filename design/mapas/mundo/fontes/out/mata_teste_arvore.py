import sys, os, bpy
sys.path.insert(0, "/mnt/project-files/design/mapas/mundo/fontes")
src = open("/mnt/project-files/design/mapas/mundo/fontes/area_mata_do_granizo.py").read()
src = src.split("# ================================================================ cena")[0]
sys.argv = ["x"]
exec(compile(src, "area", "exec"))
C.iniciar(luzes=False)
root, R0, FACE = arvore_mae(0, 0)
o = bpy.data.objects["mae_casca"]
dg = bpy.context.evaluated_depsgraph_get()
e = o.evaluated_get(dg)
print("FACES", len(o.data.polygons), len(e.data.polygons))
for md in o.modifiers: md.show_viewport = md.name in ("sol",)
dg.update(); e = o.evaluated_get(dg); print("SEM BOOL", len(e.data.polygons))
for md in o.modifiers: md.show_viewport = True
C.sol((1,1,1), 3, K.KEY_ROT)
C.chao("cinza", 60)
C.render("/mnt/project-files/design/mapas/mundo/fontes/out/mata_teste_arvore", centro=(0,0), largura=30, W=480, H=270, samples=8)

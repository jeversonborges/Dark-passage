# Checa o orçamento de triângulos de um asset low-poly antes de exportar.
# Roda dentro do Blender (bpy), em arquivo .blend ou .glb já aberto, ou como módulo do bpy 4.2.
# Avisa quando passa do máximo do tipo e quando o asset tem objetos sem material (cor chapada).
# Uso: /opt/bpy42/bin/python tools/sprite-pipeline/check_lowpoly.py -- <arquivo.blend|.glb> <tipo>
# Tipos: montaria, chefe, monstro, npc, arma, escudo, prop (ver skills_lib.ORCAMENTO). Saída 1 se estourar.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skills_lib import orcamento

def main():
    import bpy
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    arquivo, tipo = args[0], args[1]
    lo, hi = orcamento(tipo)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if arquivo.lower().endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=arquivo)
    else:
        bpy.ops.import_scene.gltf(filepath=arquivo)
    malhas = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    total = 0
    sem_material = []
    for o in malhas:
        # tris com modificadores aplicados (o que o jogo recebe), sem alterar a cena
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        ev.to_mesh_clear()
        if not o.data.materials:
            sem_material.append(o.name)
    print(f"tipo={tipo} alvo={lo}-{hi} tris={total} objetos={len(malhas)}")
    ok = total <= hi
    if total > hi:
        print(f"AVISO: passou do máximo em {total - hi} triângulos. Reduza a malha ou a subdivisão.")
    elif total < lo:
        print(f"Abaixo do mínimo ({lo}); confira se o detalhe não foi perdido.")
    if sem_material:
        print("AVISO: objetos sem material (cor chapada): " + ", ".join(sem_material))
        ok = False
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

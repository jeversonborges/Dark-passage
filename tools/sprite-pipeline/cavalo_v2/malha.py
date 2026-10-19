# Malha do cavalo v2: anatomia equina construída por seções (sem primitivas soltas).
# Convenção do pipeline (igual a monstros/quad.py): cavalo olha para -Y, Z para cima, 1 unidade = 1 m,
# pés no chão (Z=0). Altura de cernelha ~1,62 m.
# Partes separadas (corpo, pescoço, cabeça, pernas, cascos, cauda) para o rig pesar cada uma.
# Uso: from malha import build_malha; partes = build_malha()  (cada parte é um objeto no bpy)
import math
import bmesh
import bpy
from mathutils import Vector

UP = Vector((0, 0, 1))


def _frame(t, fixed):
    """Base lateral (side) e vertical (up) de uma seção, perpendicular à tangente t."""
    if fixed:
        return Vector((1, 0, 0)), Vector((0, 0, 1))
    up = UP if abs(t.z) < .95 else Vector((0, 1, 0))
    side = t.cross(up).normalized()
    return side, side.cross(t).normalized()


def _superellipse(a, b, n, sides):
    """Pontos de uma superelipse com raio a (X) e b (Z); n = 2 é elipse, maior é mais quadrada."""
    pts = []
    for i in range(sides):
        t = 2*math.pi*i/sides
        c, s = math.cos(t), math.sin(t)
        pts.append((a*math.copysign(abs(c)**(2/n), c), b*math.copysign(abs(s)**(2/n), s)))
    return pts


def _reamostra(valores, n):
    """Interpola a lista de tamanhos (sx, sz) para n seções, para a curva e a lista de raios não precisarem bater."""
    if len(valores) == n:
        return valores
    out = []
    for i in range(n):
        f = i/(n - 1)*(len(valores) - 1)
        k = min(int(f), len(valores) - 2)
        t = f - k
        a, b = valores[k], valores[k + 1]
        out.append((a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t))
    return out


def loft(nome, centros, tamanhos, material, fixed=False, sides=20, power=2.0, cap=True):
    """Malha por seções: centros (Vector) e tamanhos (sx, sz) em cada seção.
    fixed=True usa o plano XZ (seção do corpo, quadro a quadro); senão a seção segue a tangente (membros)."""
    n = len(centros)
    tamanhos = _reamostra(tamanhos, n)
    mesh = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    rings = []
    for i, c in enumerate(centros):
        a = centros[min(i + 1, n - 1)] - centros[max(i - 1, 0)]
        side, up = _frame(a.normalized(), fixed)
        sx, sz = tamanhos[i]
        ring = []
        for x, z in _superellipse(sx, sz, power, sides):
            ring.append(bm.verts.new(c + side*x + up*z))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1) % sides], r1[k]))
    if cap:
        for ring, c in ((rings[0], centros[0]), (rings[-1], centros[-1])):
            ctr = bm.verts.new(c)
            for k in range(sides):
                bm.faces.new((ring[k], ring[(k + 1) % sides], ctr) if ring is rings[0]
                             else (ring[(k + 1) % sides], ring[k], ctr))
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(nome, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = True
    return obj


def _curva(pontos, passos):
    """Curva suave (Catmull-Rom) pelos pontos de controle; devolve `passos` centros."""
    out = []
    m = len(pontos)
    for i in range(passos):
        f = i/(passos - 1)*(m - 1)
        k = min(int(f), m - 2)
        t = f - k
        p0 = pontos[max(k - 1, 0)]; p1 = pontos[k]; p2 = pontos[k + 1]; p3 = pontos[min(k + 2, m - 1)]
        out.append(0.5*((2*p1) + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t*t + (-p0 + 3*p1 - 3*p2 + p3)*t**3))
    return out


def _mat(nome, cor, rug=.7, metal=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*cor, 1)
    bsdf.inputs["Roughness"].default_value = rug
    bsdf.inputs["Metallic"].default_value = metal
    return m


def build_malha():
    """Cria as partes do cavalo e devolve {nome: objeto}."""
    pele = _mat("cv_pele", (.09, .075, .06), .75)
    casco = _mat("cv_casco", (.035, .03, .028), .45)
    partes = {}

    # ---- corpo: seções do peito (-Y) à garupa (+Y); peito fundo, ventre recolhido, garupa acima da coluna
    estacoes = [  # (y, centro z, meia-altura, meia-largura)
        (-1.04, 1.14, .26, .13),   # peitoral, arredondado na ponta
        (-.88, 1.17, .38, .25),    # peito dianteiro
        (-.66, 1.19, .42, .30),    # cilha, ponto mais fundo
        (-.30, 1.24, .39, .30),    # costelas, cernelha em z~1,62
        (.10, 1.22, .36, .29),     # lombo
        (.45, 1.26, .36, .28),     # rim
        (.72, 1.30, .39, .30),     # garupa, pico acima da linha da coluna
        (.92, 1.28, .34, .22),     # fim da garupa
        (1.02, 1.24, .22, .12),    # anca, arredondada
    ]
    centros = [Vector((0, y, z)) for y, z, _, _ in estacoes]
    tamanhos = [(w, h) for _, _, h, w in estacoes]
    partes["corpo"] = loft("cv_corpo", centros, tamanhos, pele, fixed=True, power=2.2)

    # ---- pescoço: sai da cernelha e sobe em ângulo (não vertical)
    pn = _curva([Vector((0, -.70, 1.45)), Vector((0, -.88, 1.70)), Vector((0, -1.12, 1.90)), Vector((0, -1.36, 2.02))], 8)
    rn = [(.15, .12), (.14, .11), (.12, .10), (.10, .085), (.09, .075), (.085, .07), (.08, .065), (.075, .06)]
    partes["pescoço"] = loft("cv_pescoco", pn, rn, pele)

    # ---- cabeça: crânio, focinho e mandíbula (crânio largo atrás, afinando até o focinho)
    pc = _curva([Vector((0, -1.36, 2.04)), Vector((0, -1.60, 2.09)), Vector((0, -1.85, 2.02)), Vector((0, -2.02, 1.93))], 6)
    rc = [(.085, .11), (.075, .095), (.06, .075), (.05, .06)]
    partes["cabeça"] = loft("cv_cabeca", pc, rc, pele)

    # ---- pernas: dianteiras (escápula, úmero, antebraço, carpo, canela) e traseiras (coxa, perna, jarrete, canela)
    def perna(lado, x, pontos, raios, nome):
        c = _curva([Vector((x*lado, y, z)) for y, z in pontos], len(pontos)*2)
        r = [(raios[min(int(i/2), len(raios) - 1)]) for i in range(len(c))]
        partes[nome + (" D" if lado > 0 else " E")] = loft(f"cv_{nome}_{'D' if lado > 0 else 'E'}", c, r, pele, sides=14)

    for lado in (-1, 1):
        perna(lado, .19, [(-.78, 1.30), (-.80, 1.00), (-.86, .72), (-.88, .50), (-.86, .24), (-.86, .10)],
              [(.085, .085), (.07, .07), (.058, .058), (.05, .05), (.035, .035), (.04, .04)], "perna_dianteira")
        perna(lado, .18, [(.62, 1.10), (.42, .92), (.22, .72), (.66, .48), (.86, .35), (.84, .16), (.84, .08)],
              [(.12, .12), (.075, .075), (.07, .07), (.055, .055), (.05, .05), (.035, .035), (.04, .04)], "perna_traseira")

    # ---- cascos (no fim de cada canela)
    for nome, lado, y in (("casco_dianteiro", -1, -.86), ("casco_dianteiro", 1, -.86),
                          ("casco_traseiro", -1, .84), ("casco_traseiro", 1, .84)):
        for ladoxz in (lado,):
            c = [Vector((.19*ladoxz, y, .00)), Vector((.19*ladoxz, y, .05)), Vector((.19*ladoxz, y, .10))]
            partes[f"{nome} {'D' if ladoxz > 0 else 'E'} {'frente' if nome.endswith('dianteiro') else 'tras'}"] = \
                loft(f"cv_{nome}", c, [(.035, .045), (.05, .06), (.03, .03)], casco, sides=12)

    # ---- cauda: sai da garupa e cai em arco
    pt = _curva([Vector((0, .98, 1.47)), Vector((0, 1.08, 1.30)), Vector((0, 1.16, 1.02)), Vector((0, 1.15, .72))], 8)
    rt = [(.045, .045), (.04, .04), (.035, .035), (.03, .03), (.025, .025), (.02, .02), (.018, .018), (.015, .015)]
    partes["cauda"] = loft("cv_cauda", pt, rt, pele, sides=10)
    return partes


if __name__ == "__main__":
    for o in build_malha().values():
        print(o.name, len(o.data.vertices))

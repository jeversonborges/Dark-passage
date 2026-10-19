# Muralha da Cidade de São Lázaro (0.9.8.2): troca a Cerca antiga por uma muralha contínua em volta do perímetro.
# Edita ../area_inicial.json no lugar (o gerador de origem não está no repositório). Uso: python3 muralha.py
# Coordenadas do JSON (já com a moldura de 20 tiles). Retângulo da muralha: x 40..98, y 66..128.
import json, os, math
AQUI = os.path.dirname(os.path.abspath(__file__))
CAM = os.path.join(AQUI, "..", "area_inicial.json")
M = json.load(open(CAM))
X0, X1, Y0, Y1 = 40, 98, 66, 128
PORTOES = [("portao_sul_mercado", 77, Y0, "x"), ("portao_sul_ramal", 50, Y0, "x"), ("portao_leste_direita", X1, 90, "y"),
           ("portao_leste_trilhos", X1, 78, "y"), ("portao_norte_mercado", 77, Y1, "x"), ("portao_oeste_cima", X0, 125, "y"),
           ("portao_oeste_trilhos", X0, 78, "y")]
TORRES = [(X0 + 1.2, Y0 + 1.2), (X1 - 1.2, Y0 + 1.2), (X1 - 1.2, Y1 - 1.2), (X0 + 1.2, Y1 - 1.2)]
ANTIGOS = ("muro_tijolo", "portao_cidade", "torre_vigia")
velhos = [p for p in M["props"] if p["kind"] in ANTIGOS]
M["props"] = [p for p in M["props"] if p["kind"] not in ANTIGOS]
# libera as células que só as peças antigas bloqueavam
def celulas(base):
    x0, y0, x1, y1 = base
    return {(x, y) for x in range(int(math.floor(x0)), int(math.ceil(x1))) for y in range(int(math.floor(y0)), int(math.ceil(y1)))
            if x + .5 >= x0 and x + .5 <= x1 and y + .5 >= y0 and y + .5 <= y1}
antigas = set().union(*[celulas(p["base"]) for p in velhos if p.get("base")])
ainda = set().union(*[celulas(p["base"]) for p in M["props"] if p.get("base")])
B = set(map(tuple, M["blocked"]))
B -= (antigas - ainda)
def trecho(a, b, orient):
    """Segmentos de muro entre a e b, pulando os vãos dos portões (1 m de vão em volta do portão)."""
    (ax, ay), (bx, by) = a, b
    pulos = [(gx, gy) for _, gx, gy, o in PORTOES if (o == orient) and ((orient == "x" and ay == gy) or (orient == "y" and ax == gx))]
    comp = (bx - ax) if orient == "x" else (by - ay)
    pos = 0.0
    for c in range(int(math.floor(abs(comp)))):
        pass
    ini = min(ax + ay * 0 if orient == "x" else ay, bx if orient == "x" else by)
    fim = max(bx if orient == "x" else by, ax if orient == "x" else ay)
    x = ini
    segs = []
    marcas = sorted({(gx if orient == "x" else gy) for gx, gy in pulos})
    t = ini
    for m in marcas + [fim]:
        if m - 1.6 - t > 0.01:
            segs.append((t, m - 1.6 if m != fim else fim))
        t = m + 1.6
    return segs
ADD = []
for a, b, o in [((X0, Y0), (X1, Y0), "x"), ((X0, Y1), (X1, Y1), "x"), ((X0, Y0), (X0, Y1), "y"), ((X1, Y0), (X1, Y1), "y")]:
    for s, e in trecho(a, b, o):
        # uma peça de 1 m por tile, como o kit: cada peça tem a sua base de 1 m x 1 m
        n = max(1, int(round(e - s)))
        for i in range(n):
            p = s + (i + .5) * (e - s) / n
            if o == "x":
                base = [p - .5, a[1] - .5, p + .5, a[1] + .5]; cx, cy = p, a[1]
            else:
                base = [a[0] - .5, p - .5, a[0] + .5, p + .5]; cx, cy = a[0], p
            ADD.append({"kind": "muro_tijolo", "x": round(cx, 2), "y": round(cy, 2), "orient": o, "base": base})
            for c in celulas(base): B.add(c)
for (tx, ty) in TORRES:
    ADD.append({"kind": "torre_vigia", "x": tx, "y": ty, "light": [.75, .85, 1, 6], "base": [tx - 1, ty - 1, tx + 1, ty + 1]})
    for c in celulas([tx - 1, ty - 1, tx + 1, ty + 1]): B.add(c)
for pid, gx, gy, o in PORTOES:
    # vão livre de 3,2 m entre as pontas do muro; o portão é só o arco de cima (sem base: não bloqueia)
    ADD.append({"kind": "portao_cidade", "x": gx, "y": gy, "orient": o, "light": [1, .5, .15, 5], "ponto": "portao_" + pid, "passagem": True})
M["props"] += ADD
M["blocked"] = sorted([list(c) for c in B])
json.dump(M, open(CAM, "w"), ensure_ascii=False, separators=(",", ":"))
print("muralha:", len([p for p in ADD if p['kind'] == 'muro_tijolo']), "trechos,", len(PORTOES), "portões,", len(TORRES), "torres")

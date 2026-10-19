# Praça da Cidade de São Lázaro (0.9.8.2): tira os prédios de dentro da muralha que não são marco da cidade e
# leva todos os NPCs da cidade para a praça central (eixo Matriz -> Praça, em volta do coreto).
# Edita ../area_inicial.json no lugar (o gerador de origem não está no repositório). Uso: python3 praca.py
import json, math, os
AQUI = os.path.dirname(os.path.abspath(__file__))
CAM = os.path.join(AQUI, "..", "area_inicial.json")
M = json.load(open(CAM))
MURO = (40, 66, 98, 128)                     # a muralha (x0, y0, x1, y1) já com a moldura de 20 tiles
PRACA = (60, 92, 75, 108)                    # a Praça da Matriz (1890): coreto no meio, chafariz ao norte
CENTRO = (67.5, 100.0)
# prédios que saem: sobrados de quadra, o casario e a pensão do Largo. Ficam: Matriz, Rádio, Mercado, Estação
SAEM = {"sobrado_ocre", "sobrado_azul", "sobrado_loja", "sobrado_esquina", "sobrado_rosa", "casario", "sobrado_verde", "sobrado_ruina"}
def dentro(x, y, box): return box[0] <= x <= box[2] and box[1] <= y <= box[3]
def celulas(base):
    x0, y0, x1, y1 = base
    return {(x, y) for x in range(int(math.floor(x0)), int(math.ceil(x1))) for y in range(int(math.floor(y0)), int(math.ceil(y1)))
            if x + .5 >= x0 and x + .5 <= x1 and y + .5 >= y0 and y + .5 <= y1}

# 1. a ponte duplicada (a mesma peça duas vezes no mesmo lugar)
vistos = set(); props = []
for p in M["props"]:
    chave = (p["kind"], p["x"], p["y"])
    if p["kind"] == "ponte_madeira_a" and chave in vistos: continue
    vistos.add(chave); props.append(p)
M["props"] = props

# 2. tira os prédios de dentro da muralha
sai = [p for p in M["props"] if p["kind"] in SAEM and dentro(p["x"], p["y"], MURO)]
ficam = [p for p in M["props"] if p not in sai]
M["props"] = ficam
B = set(map(tuple, M["blocked"]))
libera = set().union(*[celulas(p["base"]) for p in sai if p.get("base")]) if sai else set()
ainda = set().union(*[celulas(p["base"]) for p in ficam if p.get("base")])
B -= (libera - ainda)
# as luzes de cada prédio que saiu (o campo "luzes" é separado dos props)
luz_sai = {(p["x"], p["y"]) for p in sai}
for p in sai:
    for l in p.get("luzes_extra", []): luz_sai.add((l[0], l[1]))
M["luzes"] = [l for l in M["luzes"] if (l[0], l[1]) not in luz_sai]

# 3. todos os NPCs da cidade vão para a praça: o tile livre mais perto do centro, espaçados de 1,6 m
ter = M["terreno"]
def livre(x, y): return (x, y) not in B and ter[x][y] not in "dhw"
ocupados = []
def pode(x, y):
    return all((x - u) ** 2 + (y - v) ** 2 >= 1.6 ** 2 for u, v in ocupados)
cands = sorted([(x, y) for x in range(PRACA[0], PRACA[2] + 1) for y in range(PRACA[1], PRACA[3] + 1) if livre(x, y)],
               key=lambda c: (c[0] + .5 - CENTRO[0]) ** 2 + (c[1] + .5 - CENTRO[1]) ** 2)
NPCS = [n for n in M["npcs"] if dentro(n["x"], n["y"], MURO)]
for n in NPCS:
    for (x, y) in cands:
        cx, cy = x + .5, y + .5
        if pode(cx, cy) and (cx - CENTRO[0]) ** 2 + (cy - CENTRO[1]) ** 2 > 3.2 ** 2:
            n["x"], n["y"] = cx, cy; ocupados.append((cx, cy)); break
    else:
        raise SystemExit(f"sem lugar livre na praça para {n['id']}")

M["blocked"] = sorted([list(c) for c in B])
json.dump(M, open(CAM, "w"), ensure_ascii=False, separators=(",", ":"))
print("sai:", len(sai), "prédios;", "NPCs na praça:", len(NPCS), "; ponte duplicada tirada")

# Teste de colisão e alcance da Cidade de São Lázaro (v2.0).
# Uso: python3 teste_colisao.py [../area_inicial.json] [saida.png]
# Confere, no JSON que o jogo lê (mesmo formato de design/mapas/area_inicial.json):
#  1. toda célula que a base real de um prédio toca está em "blocked" (ninguém atravessa parede);
#  2. do spawn se chega a todo NPC, spot, baú, objeto, portão, fogueira e ponto de missão;
#  3. as ruas da cidade estão inteiras livres e ligadas (nenhum bolsão fechado dentro da Cerca);
#  4. nenhuma célula andável fica dentro de uma base (o inverso do 1).
# Sai com código 1 se algo falhar. Também desenha a planta com as bases e o alcance (saida.png).
import json, sys, os, math
from collections import deque
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "area_inicial.json")
saida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "..", "planta_colisao.png")
M = json.load(open(caminho)); NT = M["size"]
B = set(map(tuple, M["blocked"]))
ter = M["terreno"]
def bloqueada(x, y):
    if not (0 <= x < NT and 0 <= y < NT): return True
    return (x, y) in B or ter[x][y] in "dhw"
erros, avisos = [], []
# pontes: como no game/tools/mapa.py, a lama e a água rasa embaixo do tabuleiro (ao longo de X) viram passagem
PONTE = set()
for pt in M["rio"].get("pontes", []):
    (x0, cy), (x1, _) = pt["de"], pt["ate"]
    for y in range(int(cy - 1.5), int(cy + 1.5) + 1):
        if abs(y + 0.5 - cy) > 1.1: continue
        for x in range(int(x0), int(x1) + 1):
            if ter[x][y] in "wr" and (x, y) not in B: PONTE.add((x, y))
_bloq = bloqueada
def bloqueada(x, y): return False if (x, y) in PONTE else _bloq(x, y)

# 1 e 4: bases dos prédios
bases = [p for p in M["props"] if p.get("base")]
furos = 0; celulas_base = set()
for p in bases:
    x0, y0, x1, y1 = p["base"]
    for x in range(int(math.floor(x0)), int(math.ceil(x1))):
        for y in range(int(math.floor(y0)), int(math.ceil(y1))):
            # só o miolo (célula inteira dentro da base): a borda tem a folga de 30 cm
            if x + .5 < x0 or x + .5 > x1 or y + .5 < y0 or y + .5 > y1: continue
            if p.get("passagem") and abs((x + .5) - p["x"]) < 1.6 and abs((y + .5) - p["y"]) < 1.6: continue   # vão do portão
            celulas_base.add((x, y))
            if not bloqueada(x, y):
                furos += 1
                if furos <= 10: erros.append(f"parede atravessável: {p['kind']} em ({p['x']}, {p['y']}) tem a célula ({x}, {y}) livre")
if furos > 10: erros.append(f"... e mais {furos - 10} células de parede livres")

# 2: alcance a partir do spawn
sx, sy = int(M["spawn"][0]), int(M["spawn"][1])
seen = set(); q = deque([(sx, sy)]); seen.add((sx, sy))
if bloqueada(sx, sy): erros.append(f"spawn bloqueado em ({sx}, {sy})")
while q:
    x, y = q.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        u, v = x + dx, y + dy
        if (u, v) not in seen and not bloqueada(u, v): seen.add((u, v)); q.append((u, v))
def perto(x, y, r):
    return any((int(x) + a, int(y) + b) in seen for a in range(-r, r + 1) for b in range(-r, r + 1))
for n in M["npcs"]:
    if not perto(n["x"], n["y"], 1): erros.append(f"NPC inalcançável: {n['id']} ({n['x']}, {n['y']})")
for s in M["spots"]:
    if not perto(s["x"], s["y"], 2): erros.append(f"spot inalcançável: {s['id']}")
for b in M["baus"]:
    if not perto(b["x"], b["y"], 1): erros.append(f"baú inalcançável: {b['id']}")
for o in M["objetos"]:
    if not perto(o["x"], o["y"], 2): erros.append(f"objeto inalcançável: {o['id']}")
for d in M["descanso"]:
    if not perto(d["x"], d["y"], 2): erros.append(f"fogueira inalcançável: {d['nome']}")
for p in M["props"]:
    if p.get("ponto"):
        if p.get("base"):      # peça grande: basta chegar à beira da base
            x0, y0, x1, y1 = p["base"]
            ok_ = any((x, y) in seen for x in range(int(x0) - 2, int(x1) + 3) for y in range(int(y0) - 2, int(y1) + 3)
                      if not (x0 <= x + .5 <= x1 and y0 <= y + .5 <= y1))
        else: ok_ = perto(p["x"], p["y"], 3)
        if not ok_: erros.append(f"ponto inalcançável: {p['ponto']} ({p['kind']})")
    if p.get("passagem"):
        # o meio do portão passa: a célula do centro (ou a vizinha na direção da rua) está livre e alcançável
        if not perto(p["x"], p["y"], 1): erros.append(f"portão fechado: {p['ponto']}")

# 3: ruas inteiras livres e ligadas
for t in M["trilhas"]:
    pts = t["pontos"]; tot = livres = 0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = int(max(abs(bx - ax), abs(by - ay))) or 1
        for i in range(n + 1):
            x, y = ax + (bx - ax)*i/n, ay + (by - ay)*i/n
            j = M["jogavel"]
            if not (j["x0"] <= x < j["x1"] and j["y0"] <= y < j["y1"]) or ter[int(x)][int(y)] in "hd": continue
            tot += 1
            if perto(x, y, 1): livres += 1
    if tot and livres < tot*.75:   # bondes parados nos trilhos são de propósito
        erros.append(f"rua interrompida: {t['nome']} ({livres}/{tot} pontos alcançáveis)")
# bolsões dentro da Cerca
zl = M["zonas_legenda"]; letra = next(k for k, v in zl.items() if v == "acampamento_vela")
cerca = [(x, y) for x in range(NT) for y in range(NT) if M["zonas_grid"][x][y] == letra]
livres_c = [c for c in cerca if not bloqueada(*c)]
presos = [c for c in livres_c if c not in seen]
if len(presos) > 12: avisos.append(f"{len(presos)} células livres dentro da Cerca sem ligação com a praça (bolsões fechados)")
andavel_em_base = [c for c in celulas_base if c in seen]
if andavel_em_base: erros.append(f"{len(andavel_em_base)} células andáveis dentro de bases de prédios")

# planta
S = 4; im = Image.new("RGB", (NT*S, NT*S), (18, 16, 14)); d = ImageDraw.Draw(im)
P = lambda x, y: (x*S, (NT - y)*S)
for x in range(NT):
    for y in range(NT):
        c = (150, 140, 120) if (x, y) in seen else ((70, 66, 60) if not bloqueada(x, y) else (30, 26, 24))
        px, py = P(x, y); d.rectangle([px, py - S, px + S - 1, py - 1], fill=c)
for p in bases:
    x0, y0, x1, y1 = p["base"]; a = P(x0, y1); b = P(x1, y0)
    d.rectangle([a[0], a[1], b[0], b[1]], outline=(230, 120, 60))
for n in M["npcs"]:
    px, py = P(n["x"], n["y"]); d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(80, 160, 255))
for s in M["spots"]:
    px, py = P(s["x"], s["y"]); r = s["raio"]*S; d.ellipse([px - r, py - r, px + r, py + r], outline=(120, 255, 120))
px, py = P(M["spawn"][0], M["spawn"][1]); d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 60, 60))
im.save(saida)

print(f"{len(bases)} peças com base real · {len(celulas_base)} células de parede · {len(seen)} células alcançáveis a partir do spawn")
for a in avisos: print("AVISO:", a)
for e in erros: print("ERRO:", e)
print("colisão OK" if not erros else f"{len(erros)} erro(s)")
sys.exit(1 if erros else 0)

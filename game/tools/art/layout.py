# Layout da área inicial "Ruínas de Velgrad, Portão Leste" (48x48 m, 1 tile = 1 m).
# Gera data/area_inicial.json (objetos, colisão, spawns) e a máscara do chão usada pelo Blender.
# O mesmo JSON é lido pelo render (dp_world.py) e pelo jogo (Godot), então tudo fica alinhado.
# Uso: python3 layout.py <saida_json> <saida_mascara_png>
# Eixos: +x desce para a direita na tela, +y sobe para a direita. (0,0) é o canto esquerdo.
import json, random, sys, math
from PIL import Image, ImageDraw, ImageFilter
N = 48; R = random.Random(7)
props = []; blocked = set()
def add(kind, x, y, block=True, **kw):
    props.append({"kind": kind, "x": round(x, 2), "y": round(y, 2), **kw})
    if block: blocked.add((int(x), int(y)))

CAMP = (8.5, 8.5); CEM = (13, 35); CHAPEL = (35, 13); SLAUGHTER = (39, 39)

# --- borda: muros altos ao fundo (x=0 e y=47), entulho baixo perto da câmera
for i in range(N):
    for (x, y, far) in [(0.5, i+.5, True), (i+.5, N-.5, True), (N-.5, i+.5, False), (i+.5, .5, False)]:
        if far: add("wall_" + ("y" if x == .5 else "x") + str(R.choice([1,2,2,3])), x, y)
        else: add(R.choice(["rubble", "rubble", "sandbag_" + ("y" if x == N-.5 else "x"), "wire_" + ("y" if x == N-.5 else "x")]), x, y)

# --- acampamento (zona segura): sacos de areia em volta, fogueira, tendas, postes
cx, cy = CAMP
for a in range(0, 360, 12):
    r = 6.2; x, y = cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a))
    if 30 < a < 60 or 195 < a < 255: continue      # aberturas para a estrada
    add("sandbag_x" if abs(math.cos(math.radians(a))) < .7 else "sandbag_y", x, y)
add("bonfire", cx, cy, light=[1, .5, .15, 7])
for (x, y) in [(cx-3, cy+2.5), (cx+2.5, cy-3)]: add("tent", x, y)
for (x, y) in [(cx-3.5, cy-2.5), (cx+3, cy+3), (cx+5, cy+5.5)]: add("barrel_fire", x, y, light=[1, .45, .12, 4.5])
add("crate", cx+.8, cy+3.2); add("crate", cx-1.5, cy-4); add("crate", cx+1.7, cy+3.4)

# --- estrada de pedra do acampamento ao abatedouro, e ramais para cemitério e capela
road = []
def path(a, b, w):
    L = int(math.dist(a, b)*2)
    for k in range(L+1):
        t = k/L; road.append((a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, w))
path(CAMP, SLAUGHTER, 2.2); path((20, 20), CEM, 1.4); path((22, 22), CHAPEL, 1.4)
for t in range(5, 42, 7):
    p = (t + R.uniform(-.3, .3), t + 3.2)
    if math.dist(p, CAMP) > 7: add("lamp", p[0], p[1], light=[.95, .75, .4, 4])

# --- cemitério: cruzes e túmulos em fileiras, árvores mortas, cerca de ferro
for row in range(5):
    for col in range(6):
        x, y = CEM[0]-5 + col*2 + R.uniform(-.3, .3), CEM[1]-3 + row*1.6 + R.uniform(-.2, .2)
        if R.random() < .2: continue
        add(R.choice(["cross1", "cross2", "cross3", "grave1", "grave2"]), x, y)
for (x, y) in [(CEM[0]-7, CEM[1]+5), (CEM[0]+6, CEM[1]+6), (CEM[0]-6, CEM[1]-5), (CEM[0]+7, CEM[1]-1)]:
    add(R.choice(["tree1", "tree2"]), x, y)
add("gibbet", CEM[0]+1, CEM[1]+7, light=[.5, 1, .2, 3])

# --- capela em ruínas: paredes quebradas, vitral vermelho, bancos
for i in range(-5, 6):
    add("wall_x" + str(R.choice([2, 3, 3])), CHAPEL[0]+i+.5, CHAPEL[1]+6.5)      # parede do fundo (longe da câmera)
    if i not in (3, 4): add("wall_x1", CHAPEL[0]+i+.5, CHAPEL[1]-6.5)            # parede da frente, baixa e quebrada
for i in range(-6, 6):
    if i in (-1, 0): continue
    add("wall_y" + str(R.choice([1, 2, 3])), CHAPEL[0]-5.5, CHAPEL[1]+i+.5)
add("window_y", CHAPEL[0]-5.5, CHAPEL[1]-.5, light=[1, .1, .05, 5])
add("window_y", CHAPEL[0]-5.5, CHAPEL[1]+.5, block=True)
for row in range(4):
    for s in (-1, 1):
        add("pew", CHAPEL[0]-3+row*2, CHAPEL[1]+s*2.2)
add("altar", CHAPEL[0]+4.5, CHAPEL[1], light=[1, .55, .2, 4])
for k in range(10): add("rubble", CHAPEL[0]+R.uniform(-5, 5), CHAPEL[1]+R.uniform(-6, 6))

# --- abatedouro (chefe): ganchos de carne, cercado de madeira, sangue
for i in range(9):
    add("hooks", SLAUGHTER[0]-4+i, SLAUGHTER[1]+4.5)
for i in range(7):
    add("fence_y", SLAUGHTER[0]-5, SLAUGHTER[1]-3+i)
add("barrel_fire", SLAUGHTER[0]+2, SLAUGHTER[1]-3, light=[1, .45, .12, 4.5])
add("cart", SLAUGHTER[0]-2, SLAUGHTER[1]-4)

# --- espalhados: árvores, entulho, carroças, cadáveres
for k in range(40):
    x, y = R.uniform(3, 45), R.uniform(3, 45)
    if math.dist((x, y), CAMP) < 8 or any(math.dist((x, y), (r[0], r[1])) < r[2]+1 for r in road[::3]): continue
    if math.dist((x, y), CHAPEL) < 8 or math.dist((x, y), SLAUGHTER) < 7 or math.dist((x, y), CEM) < 8: continue
    add(R.choice(["tree1", "tree2", "rubble", "rubble", "cart", "corpse", "corpse"]), x, y)
for p in props:
    if p["kind"] == "corpse": blocked.discard((int(p["x"]), int(p["y"])))

# --- spawns de monstros: tipo, nível, quantidade, raio
spawns = [
    {"kind": "cao_praga", "level": 1, "x": 16, "y": 12, "count": 4, "radius": 3},
    {"kind": "carnical", "level": 1, "x": 18, "y": 22, "count": 4, "radius": 4},
    {"kind": "cao_praga", "level": 3, "x": 22, "y": 38, "count": 4, "radius": 3},
    {"kind": "automato", "level": 6, "x": 42, "y": 26, "count": 3, "radius": 3},
    {"kind": "automato", "level": 7, "x": 30, "y": 42, "count": 2, "radius": 2},
    {"kind": "carnical", "level": 2, "x": 24, "y": 30, "count": 4, "radius": 4},
    {"kind": "carnical", "level": 3, "x": CEM[0], "y": CEM[1], "count": 6, "radius": 5},
    {"kind": "flagelado", "level": 4, "x": 27, "y": 17, "count": 3, "radius": 3},
    {"kind": "flagelado", "level": 5, "x": CHAPEL[0], "y": CHAPEL[1], "count": 5, "radius": 4},
    {"kind": "carnical", "level": 5, "x": 33, "y": 30, "count": 4, "radius": 4},
    {"kind": "flagelado", "level": 6, "x": 36, "y": 34, "count": 3, "radius": 3},
    {"kind": "acougueiro", "level": 8, "x": SLAUGHTER[0], "y": SLAUGHTER[1], "count": 1, "radius": 1},
]
data = {"name": "Ruínas de Velgrad · Portão Leste", "size": N, "spawn": [CAMP[0]+1.5, CAMP[1]-1.5],
        "safe_zone": {"x": CAMP[0], "y": CAMP[1], "radius": 6.5},
        "props": props, "blocked": sorted([list(c) for c in blocked]), "spawns": spawns}
json.dump(data, open(sys.argv[1], "w"), ensure_ascii=False)

# máscara do chão (16 px por metro): R = pedra da estrada, G = terra de cova, B = sangue
S = 16; img = Image.new("RGB", (N*S, N*S)); d = ImageDraw.Draw(img)
for (x, y, w) in road:
    d.ellipse([(x-w)*S, (y-w)*S, (x+w)*S, (y+w)*S], fill=(255, 0, 0))
d.ellipse([(CAMP[0]-5.5)*S, (CAMP[1]-5.5)*S, (CAMP[0]+5.5)*S, (CAMP[1]+5.5)*S], fill=(255, 0, 0))
d.rectangle([(CHAPEL[0]-5)*S, (CHAPEL[1]-6)*S, (CHAPEL[0]+5)*S, (CHAPEL[1]+6)*S], fill=(255, 0, 0))
r, g, b = img.split(); gd = ImageDraw.Draw(g); bd = ImageDraw.Draw(b)
gd.ellipse([(CEM[0]-8)*S, (CEM[1]-6)*S, (CEM[0]+8)*S, (CEM[1]+8)*S], fill=255)
for k in range(30):
    x, y, rr = R.uniform(4, 44), R.uniform(4, 44), R.uniform(.3, 1.2)
    bd.ellipse([(x-rr)*S, (y-rr*.7)*S, (x+rr)*S, (y+rr*.7)*S], fill=255)
for k in range(12):
    x, y, rr = SLAUGHTER[0]+R.uniform(-4, 4), SLAUGHTER[1]+R.uniform(-4, 4), R.uniform(.5, 1.5)
    bd.ellipse([(x-rr)*S, (y-rr*.7)*S, (x+rr)*S, (y+rr*.7)*S], fill=255)
r = r.filter(ImageFilter.GaussianBlur(6)); g = g.filter(ImageFilter.GaussianBlur(10)); b = b.filter(ImageFilter.GaussianBlur(2))
Image.merge("RGB", (r, g, b)).save(sys.argv[2])
print(len(props), "objetos,", len(blocked), "tiles bloqueados")

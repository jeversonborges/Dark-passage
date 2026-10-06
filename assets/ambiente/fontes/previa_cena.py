# Monta uma cena de prévia do Deserto de Absinto com os pisos, objetos e luzes do kit,
# do jeito que o jogo monta (tiles 64x32, objetos ancorados e ordenados por profundidade).
# Uso: python3 previa_cena.py <saida.png>
import sys, os, json, random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]
N = 34                       # tiles por lado
W, H = 1600, 900
OX, OY = -260, 450           # origem da tela para o tile (0,0)
rnd = random.Random(7)

def scr(x, y):              # centro do tile (x,y) na tela; +X baixo-direita, +Y cima-direita
    return OX + (x + y)*32 + 32, OY + (x - y)*16 + 16

atlas = {k: Image.open(f"{B}/tiles/{k}.png").convert("RGBA") for k in ("areia", "asfalto_rachado", "leito_rachado", "areia_vitrificada", "agua_toxica", "cascalho")}
def cell(k, x, y): return atlas[k].crop(((x % 4)*64, (y % 4)*32, (x % 4)*64 + 64, (y % 4)*32 + 32))

def piso(x, y):
    if 12 <= x - y + 10 <= 14: return "asfalto_rachado"              # estrada antiga
    if 26 <= x + y <= 30:
        return "agua_toxica" if 27.5 <= x + y <= 28.5 else "leito_rachado"   # rio seco
    if (x - 22)**2 + (y - 8)**2 < 14: return "areia_vitrificada"
    if (x - 8)**2 + (y - 20)**2 < 9: return "cascalho"
    return "areia"

img = Image.new("RGBA", (W, H), (8, 7, 7, 255))
for x in range(N):
    for y in range(N):
        cx, cy = scr(x, y)
        if -64 < cx < W + 64 and -32 < cy < H + 32:
            img.alpha_composite(cell(piso(x, y), x, y), (cx - 32, cy - 16))

objs = []
def put(kind, x, y):
    p = f"{B}/objetos/{kind}.png"
    if not os.path.exists(p): return
    m = json.load(open(f"{B}/objetos/{kind}.json")); objs.append((x - y, x, y, kind, m))

put("predio_enterrado", 9, 25); put("cupula_estacao", 7, 9); put("capela_enterrada", 24, 26)
put("bonde_veleiro", 15, 14); put("torre_relogio_enterrada", 18, 31)
for k in range(9): put("trilho_bonde_a", 6 + k, 14)
put("poste_mastro", 13, 18); put("poste_mastro", 19, 12); put("chamine_enterrada", 3, 29)
put("mar_de_lapides", 27, 18); put("arvore_morta_grande", 20, 6); put("arvore_morta", 29, 12)
put("tambores_radioativos", 22, 9); put("planta_mutante", 23, 10); put("planta_mutante", 17, 9)
put("moita_cardo", 12, 22); put("moita_cardo", 25, 13); put("juncos", 14, 15 - 1); put("juncos", 16, 12)
put("pedras_rio", 18, 10); put("barco_afundado", 13, 15); put("roda_dagua_bomba", 21, 7)
put("ossada_gigante", 30, 4); put("poste_telegrafo", 4, 18); put("poste_telegrafo", 5, 22)
put("cratera_cinza", 26, 9); put("elmo_espada_fincada", 25, 7); put("estandarte_rasgado", 27, 8)
put("lampada_arco", 3, 12); put("tenda_vigilia", 10, 6); put("barraco_sucata", 4, 6); put("fogueira", 9, 11)
put("tonel_fogo", 6, 13); put("varal_roupas", 12, 9); put("caixas", 11, 12); put("barris", 3, 9)
for k in range(26):
    x, y = rnd.uniform(2, 32), rnd.uniform(2, 32)
    put(rnd.choice(["mato_seco", "mato_seco_2", "arbusto_seco", "arbusto_seco_2", "cacto_seco", "ossada_animal", "vidro_estilhacos"]), x, y)
objs.sort(key=lambda o: (o[1] - o[2], o[1] + o[2]))
for _, x, y, kind, m in sorted(objs, key=lambda o: -(o[2] - o[1])):
    cx, cy = scr(x, y)
    im = Image.open(f"{B}/objetos/{kind}.png").convert("RGBA")
    img.alpha_composite(im, (int(cx - m["anchor"][0]), int(cy - m["anchor"][1])))

# luzes somadas (como o jogo faria com blend add)
arr = np.asarray(img).astype(np.float32)
def luz(nome, x, y, k=1.0, s=1.0):
    l = Image.open(f"{B}/luzes/{nome}.png")
    if s != 1: l = l.resize((int(l.width*s), int(l.height*s)))
    la = np.asarray(l).astype(np.float32)
    cx, cy = scr(x, y); x0, y0 = int(cx - l.width/2), int(cy - l.height/2)
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + l.width), min(H, y0 + l.height)
    if xa >= xb or ya >= yb: return
    sub = la[ya - y0:yb - y0, xa - x0:xb - x0]
    arr[ya:yb, xa:xb, :3] += sub[..., :3] * (sub[..., 3:4]/255) * .55 * k
luz("luz_arco", 3, 12, 1.0, 1.4); luz("luz_fogo", 9, 11); luz("luz_fogo", 6, 13, .8)
luz("luz_lampiao", 13, 18, .7); luz("luz_lampiao", 19, 12, .7); luz("luz_vitral", 24, 26, .7, 1.4)
luz("luz_lampiao", 9, 25, .6, 1.2)
for x, y in [(22, 9), (17, 9), (23, 10)]: luz("luz_porao", x, y, 0)  # (sem luz vermelha aqui)
# poças verdes do rio
for k in range(10):
    t = rnd.uniform(0, 1); luz("luz_lua", 14 + t*14, 14 - t*14 + 0, 0)
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
# névoa baixa esverdeada (Amargo) e vinheta
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W/2)/(W*.62))**2 + ((yy - H/2)/(H*.62))**2)
v = np.clip(1.15 - d**1.6, .15, 1)[..., None]
a = np.asarray(img.convert("RGB")).astype(np.float32)
fog = np.array([28, 34, 24], np.float32)
a = a*v + fog*(1 - v)*.6
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGB")
img.save(out); print(out, img.size)

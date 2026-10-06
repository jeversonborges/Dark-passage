"""Spots de farm do Deserto de Absinto (estilo MU), no ritmo "mais WoW".
Lê ../area_inicial.json (grade 160x160) e grava ../spots.json e ../spots.png.
Cada spot é uma clareira aberta (espaço para a skill em leque do nível 5), longe das trilhas
principais e das zonas seguras, com grupos pequenos espaçados e respawn de farm."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, "..", "area_inicial.json")
M = json.load(open(ARQ))
if "spots" in M: raise SystemExit("area_inicial.json já tem spots: rode layout.py antes de spots.py")
N = M["size"]
BLOQ = np.zeros((N, N), bool)
for x, y in M["blocked"]: BLOQ[x, y] = True
TER = M["terreno"]
for x in range(N):
    for y in range(N):
        if TER[x][y] in "dhwr": BLOQ[x, y] = True
ALTOS = np.zeros((N, N), int)       # props que atrapalham a mira em área
for p in M["props"]:
    if p.get("camada") == "chao" or p.get("decor_moldura"): continue
    ALTOS[min(N-1, int(p["x"])), min(N-1, int(p["y"]))] += 1
SEG = [(s["x"], s["y"], s["radius"]) for s in M["safe_zones"]]
PRINC = ("estrada_paroquia", "rua_do_sino", "trilha_procissao", "estrada_gado", "linha_7")
def dist_trilha(x, y, so=None):
    d = 1e9
    for t in M["trilhas"]:
        if so is not None and (t["id"] in PRINC) != so: continue
        P = t["pontos"]
        for (ax, ay), (bx, by) in zip(P, P[1:]):
            vx, vy = bx-ax, by-ay; L2 = vx*vx+vy*vy or 1
            u = max(0, min(1, ((x-ax)*vx + (y-ay)*vy)/L2))
            d = min(d, math.hypot(x-ax-u*vx, y-ay-u*vy))
    return d
def nota(cx, cy, r):
    livre = tot = obst = 0
    for x in range(int(cx-r), int(cx+r)+1):
        for y in range(int(cy-r), int(cy+r)+1):
            if (x-cx)**2 + (y-cy)**2 > r*r or not (0 <= x < N and 0 <= y < N): continue
            tot += 1; livre += not BLOQ[x, y]; obst += ALTOS[x, y]
    return livre/tot - obst*.002
ZL = {v: k for k, v in M["zonas_legenda"].items()}
def acha(cx, cy, r, busca=13, zona=None, folga=1.5):
    best = None
    for dx in range(-busca, busca+1):
        for dy in range(-busca, busca+1):
            x, y = cx+dx, cy+dy
            if any(math.hypot(x-sx, y-sy) < sr + 14 for sx, sy, sr in SEG): continue
            if zona and M["zonas_grid"][x][y] != ZL[zona]: continue
            dt = dist_trilha(x, y, True)
            if dt < r + folga or dist_trilha(x, y, False) < r*.6: continue
            if any(math.hypot(x-o["x"], y-o["y"]) < r + o["raio"] + 3 for o in saida): continue
            n = nota(x, y, r) - .002*math.hypot(dx, dy)
            if BLOQ[x, y]: continue
            if best is None or n > best[0]: best = (n, x, y, dt)
    return best

# temperamento: neutro (só reage se apanhar), territorial (raio curto em volta da âncora),
# agressivo (só onde a lore pede). aggro_social dentro do spot: 0 entre subgrupos.
# Ids, nomes, subzonas e monstros vêm da thread de Missões (design/missoes/dados/locais.json, "spots");
# posição, raio, quantidade, temperamento e respawn são daqui. "antigo" = id da primeira versão deste arquivo.
SPOTS = [
 dict(id="spot_campo_vidro", antigo="covas_rasas", nome="Campo de Vidro", nivel=[1, 3], zona="campos_cinza", semente=(66, 62), raio=10,
      mobs=[{"kind": "carnical", "nivel": [1, 2], "qtd": 6, "temperamento": "neutro"}, {"kind": "corvo_de_cinza", "nivel": [2, 3], "qtd": 3, "temperamento": "neutro"}],
      lore="Carniçais revirando os mortos da Grande Batalha no vidro derretido; os corvos esperam a vez. Ninguém aqui ataca primeiro.",
      missao="primeiros abates para a Vigília (Odete)"),
 dict(id="spot_becos_afogados", antigo="telhados_dos_corvos", nome="Becos Afogados", nivel=[3, 5], zona="bairro_afogado", semente=(31, 86), raio=8,
      mobs=[{"kind": "cao_de_vala", "nivel": [3, 5], "qtd": 6, "temperamento": "territorial", "ancora": "toca_caes", "raio_territorio": 4},
            {"kind": "corvo_de_cinza", "nivel": [3, 4], "qtd": 6, "temperamento": "neutro"}],
      lore="A matilha caça ratos entre os telhados enterrados, no caminho da Rádio; os corvos ficam nas chaminés.",
      missao="linha D: chegar à Rádio da Isaura"),
 dict(id="spot_toca_vala", antigo="fosso_dos_caes", nome="Toca da Matilha", nivel=[3, 5], zona="vala_comum", semente=(80, 44), raio=10,
      mobs=[{"kind": "cao_de_vala", "nivel": [3, 5], "qtd": 9, "temperamento": "territorial", "ancora": "toca_caes", "raio_territorio": 4},
            {"kind": "carnical", "nivel": [3, 4], "qtd": 3, "temperamento": "neutro"}],
      lore="O bueiro desabado onde a matilha dorme. De dia ela defende a toca; à noite caça.",
      missao="limpar a vala para os coveiros"),
 dict(id="spot_fila_julgamento", antigo="procissao_parada", nome="A Fila do Juízo", nivel=[4, 6], zona="cemiterio_sao_lazaro", semente=(74, 108), raio=10, busca=7,
      mobs=[{"kind": "nao_julgado", "nivel": [4, 6], "qtd": 12, "temperamento": "neutro"}],
      lore="A fila de Não-Julgados parada diante da torre do sino, esperando o Juízo. Não atacam ninguém, só revidam: o spot feito para o leque.",
      missao="lacres de cera para a Madre Ivone ou o Frei Anacleto"),
 dict(id="spot_chiqueiros", antigo="chiqueiro_do_carnica", nome="Chiqueiros do Carniça", nivel=[4, 6], zona="abatedouro_carnica", semente=(124, 78), raio=9,
      mobs=[{"kind": "porco_pestilento", "nivel": [4, 6], "qtd": 12, "temperamento": "neutro"}],
      lore="Os porcos gordos fuçam a lama atrás das cercas de chapa; o rastro de arrasto passa por aqui.",
      missao="linha E: o rastro de arrasto"),
 dict(id="spot_vila_viuvas", antigo="margem_das_viuvas", nome="Vila das Viúvas", nivel=[5, 7], zona="bosque_viuvas", semente=(110, 108), raio=9,
      mobs=[{"kind": "nao_julgado", "nivel": [5, 6], "qtd": 8, "temperamento": "neutro"},
            {"kind": "sangrador_apostata", "substituto": "nao_julgado", "nivel": [6, 7], "qtd": 4, "temperamento": "territorial", "ancora": "vila_militar", "raio_territorio": 5}],
      lore="As viúvas da vila militar do silo ainda andam entre as casas afundadas; uma célula de cultistas apóstatas se esconde entre elas e só ataca quem chega perto do esconderijo.",
      missao="linha D: a vila militar do silo"),
 dict(id="spot_acampamento_desertores", nome="Acampamento dos Desertores", nivel=[6, 8], zona="rio_amargo", semente=(96, 66), raio=9,
      mobs=[{"kind": "desertor_legiao", "substituto": "acougueiro_oco", "nivel": [6, 8], "qtd": 12, "temperamento": "territorial", "ancora": "tenda_demonio", "raio_territorio": 5}],
      lore="Demônios da Legião Blasfema que largaram a bandeira quando o general sumiu. Defendem o acampamento, mas não caçam ninguém lá fora.",
      missao="linha E: o sumiço do general"),
 dict(id="spot_marco_corte", nome="Marco do Corte", nivel=[7, 9], zona="campos_cinza", semente=(66, 80), raio=9,
      mobs=[{"kind": "desertor_legiao", "substituto": "acougueiro_oco", "nivel": [7, 9], "qtd": 6, "temperamento": "territorial", "ancora": "marco_do_corte", "raio_territorio": 5},
            {"kind": "carnical", "nivel": [7, 8], "qtd": 6, "temperamento": "neutro"}],
      lore="O bonde tombado onde Andras foi partido. Desertores vêm procurar o corpo do general e guardam o lugar.",
      missao="linha E: o Marco do Corte"),
 dict(id="spot_margem_amarga", nome="Margem Amarga", nivel=[7, 9], zona="rio_amargo", semente=(108, 52), raio=9,
      mobs=[{"kind": "cao_de_vala", "nivel": [7, 8], "qtd": 6, "temperamento": "neutro"},
            {"kind": "desertor_legiao", "substituto": "acougueiro_oco", "nivel": [8, 9], "qtd": 6, "temperamento": "territorial", "ancora": "pocas_amargas", "raio_territorio": 4}],
      lore="A matilha bebe nas poças verdes do oásis; os desertores cobram pedágio da água.",
      missao="linha D: encher o frasco nas poças amargas"),
 dict(id="spot_patio_abatedouro", antigo="patio_do_abatedouro", nome="Pátio do Abatedouro", nivel=[7, 9], zona="abatedouro_carnica", semente=(120, 56), raio=10,
      mobs=[{"kind": "acougueiro_oco", "nivel": [7, 9], "qtd": 11, "temperamento": "agressivo"},
            {"kind": "capataz_gancho", "nivel": [9, 9], "qtd": 1, "temperamento": "agressivo", "elite": True, "respawn_s": 300}],
      lore="Os açougueiros ainda trabalham para o patrão morto e atacam quem entra no pátio. O único spot agressivo de verdade, e a porta da Cripta.",
      missao="linha principal: a entrada da Cripta da Trombeta Calada"),
 dict(id="spot_muro_sombras", antigo="beira_da_tempestade", nome="Muro das Sombras", nivel=[9, 12], zona="tempestade_areia", semente=(100, 128), raio=10,
      mobs=[{"kind": "sombra_gravada", "substituto": "nao_julgado", "nivel": [9, 12], "qtd": 12, "temperamento": "territorial", "ancora": "muro_sombras", "raio_territorio": 4}],
      lore="As sombras que o clarão da bomba gravou no muro da vila militar descolam à noite e defendem o muro. Na borda da tempestade o contador não para de estalar.",
      missao="linha D: o Silo São Lázaro"),
]
REGRAS = {
    "respawn_s": "14 por mob nos spots de farm (padrão do Combate, combate.md seção 9); 18 nos dois spots de nível 1 a 3; 25 fora dos spots",
    "subgrupos": "2 ou 3 mobs, a pelo menos 5 m um do outro; aggro_social 0 entre subgrupos",
    "afastamento": "spot a mais de 14 m da borda de uma zona segura e fora da faixa das trilhas principais; quem só passa não puxa nada",
    "skill_em_area": "clareira de 8 a 11 m de raio sem objetos altos, para o leque do nível 5 e o modo automático",
    "descanso": "um ponto de descanso (fogueira + carrinho do Tobias vendendo poção) perto de cada par de spots",
}
saida = []
for s in SPOTS:
    res = acha(*s["semente"], s["raio"], s.get("busca", 13), zona=s["zona"])
    if res is None: print("trilha passa na borda:", s["id"]); res = acha(*s["semente"], s["raio"], s.get("busca", 13), zona=s["zona"], folga=-s["raio"]*.4)
    n, x, y, dt = res
    s2 = {k: v for k, v in s.items() if k not in ("semente", "busca")}
    s2.update(x=float(x), y=float(y), livre=round(float(n), 2), dist_trilha=round(float(dt), 1))
    s2.setdefault("respawn_s", 14 if s["nivel"][1] > 4 else 18)   # spot padrão do Combate: 12 mobs, 14 s
    s2["abrir_clareira"] = bool(n < .75)   # a revisão do layout tira os objetos altos de dentro do spot
    saida.append(s2)
# pontos de descanso: entre pares de spots próximos, em tile livre
DESC = []
for a, b, nome in [("spot_campo_vidro", "spot_becos_afogados", "Fogueira do Espantalho"), ("spot_toca_vala", "spot_patio_abatedouro", "Fogueira da Vala"),
                   ("spot_fila_julgamento", "spot_vila_viuvas", "Fogueira das Lápides"), ("spot_chiqueiros", "spot_margem_amarga", "Fogueira do Vau"),
                   ("spot_marco_corte", "spot_acampamento_desertores", "Fogueira do Bonde"), ("spot_muro_sombras", "spot_vila_viuvas", "Fogueira da Tempestade")]:
    A = next(s for s in saida if s["id"] == a); B = next(s for s in saida if s["id"] == b)
    mx, my = (A["x"] + B["x"])/2, (A["y"] + B["y"])/2
    best = min(((abs(dx)+abs(dy), mx+dx, my+dy) for dx in range(-14, 15) for dy in range(-14, 15)
                if not BLOQ[int(mx+dx), int(my+dy)] and all(math.hypot(mx+dx-s["x"], my+dy-s["y"]) > s["raio"] + 2 for s in saida)))
    DESC.append({"nome": nome, "x": best[1], "y": best[2], "props": ["fogueira", "carrinho_tobias"], "npc": "tobias (vende poção)", "entre": [a, b]})
out = {"_doc": "Spots de farm do Deserto de Absinto. Coordenadas na grade de area_inicial.json (160x160). Lido pela thread de Missões para as linhas de quest e pela thread do jogo para os spawns.",
       "regras": REGRAS, "spots": saida, "descanso": DESC}
json.dump(out, open(os.path.join(AQUI, "..", "spots.json"), "w"), ensure_ascii=False, indent=1)
for s in saida: print(f'{s["nome"]:22s} nv{s["nivel"]} ({s["x"]:.0f},{s["y"]:.0f}) livre={s["livre"]} trilha={s["dist_trilha"]}')
for d in DESC: print(d["nome"], d["x"], d["y"])

# ---------------------------------------------------------------- aplica os spots no mapa
import random
RND = random.Random(6)
TERR_BLOQ = set("dhwr")
TEMP_PADRAO = {"cao_de_vala": "territorial", "acougueiro_oco": "agressivo", "capataz_gancho": "agressivo"}
def dentro(x, y, s, f=1.0): return math.hypot(x - s["x"], y - s["y"]) < s["raio"]*f
removidos = 0
OBJ = "/mnt/project-files/assets/ambiente/objetos"
_fp = {}
def grande(kind):
    """Prédios e marcos não saem da clareira: o spot se acomoda em volta deles."""
    if kind not in _fp:
        f = os.path.join(OBJ, kind + ".json") if os.path.exists(os.path.join(OBJ, kind + ".json")) else os.path.join(OBJ, kind + "_a.json")
        try: fp = json.load(open(f)).get("footprint_tiles", [1, 1])
        except Exception: fp = [1, 1]
        _fp[kind] = fp[0]*fp[1] >= 6
    return _fp[kind]
for s in saida:
    # 1. clareira: tira os objetos altos (menos objetos de missão) e libera o chão
    if s["abrir_clareira"] or True:
        antes = len(M["props"])
        M["props"] = [p for p in M["props"] if not (dentro(p["x"], p["y"], s, .85) and p.get("camada") != "chao" and not p.get("ponto") and not grande(p["kind"]))]
        removidos += antes - len(M["props"])
# chão liberado onde não sobrou objeto e o terreno não bloqueia
ocupado = set()
for p in M["props"]:
    if p.get("camada") != "chao": ocupado.add((int(p["x"]), int(p["y"])))
bl = set(map(tuple, M["blocked"]))
for s in saida:
    for x in range(int(s["x"] - s["raio"]), int(s["x"] + s["raio"]) + 1):
        for y in range(int(s["y"] - s["raio"]), int(s["y"] + s["raio"]) + 1):
            if dentro(x + .5, y + .5, s, .7) and (x, y) in bl and TER[x][y] not in TERR_BLOQ and (x, y) not in ocupado:
                bl.discard((x, y)); BLOQ[x, y] = False
M["blocked"] = sorted([list(c) for c in bl])
# 2. spawns: os grupos soltos dentro de um spot saem; o spot entra em subgrupos de 2 a 3
velhos = M["spawns"]; novos = []
for g in velhos:
    if g.get("so_para") or g.get("so_por_missao"): novos.append(g); continue
    if any(dentro(g["x"], g["y"], s, 1.0) or math.hypot(g["x"] - s["x"], g["y"] - s["y"]) < s["raio"] + 5 for s in saida): continue
    g = dict(g); g["temperamento"] = TEMP_PADRAO.get(g["kind"], "neutro")
    # longe da porta das zonas seguras (avaliação v0.3)
    if any(math.hypot(g["x"] - z["x"], g["y"] - z["y"]) < z["radius"] + 15 for z in M["safe_zones"]): continue
    novos.append(g)
def livre_perto(x, y):
    for r in range(0, 6):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                u, v = int(x + dx), int(y + dy)
                if 0 <= u < N and 0 <= v < N and not BLOQ[u, v]: return u + .5, v + .5
    return x, y
for s in saida:
    for mdef in s["mobs"]:
        qtd = mdef["qtd"]; grupos = []
        while qtd > 0:
            k = 3 if qtd >= 5 or qtd == 3 else 2 if qtd >= 2 else 1
            if mdef.get("elite"): k = 1
            grupos.append(k); qtd -= k
        mdef["subgrupos"] = len(grupos)
    # posições em anel, espaçadas, uma por subgrupo de todo o spot
    todos = [(mdef, k) for mdef in s["mobs"] for k in ([1] if mdef.get("elite") else [])] +             [(mdef, k) for mdef in s["mobs"] if not mdef.get("elite") for k in ([3]*(mdef["qtd"]//3) + ([mdef["qtd"] % 3] if mdef["qtd"] % 3 else []))]
    n = len(todos); a0 = RND.uniform(0, 6.28)
    for i, (mdef, k) in enumerate(todos):
        if mdef.get("elite"): px, py = s["x"], s["y"]
        else:
            rr = s["raio"]*(.62 if i % 2 else .38) if n > 6 else s["raio"]*.5
            a = a0 + i/n*2*math.pi
            px, py = s["x"] + math.cos(a)*rr, s["y"] + math.sin(a)*rr
        px, py = livre_perto(px, py)
        lv = mdef["nivel"]; nivel = lv[0] + round((lv[1] - lv[0])*i/max(1, n - 1))
        g = {"kind": mdef["kind"], "level": int(nivel), "x": round(px, 1), "y": round(py, 1),
             "count": k, "radius": 1.5, "temperamento": mdef["temperamento"], "spot": s["id"], "respawn_s": s.get("respawn_s", 20) if not mdef.get("elite") else mdef.get("respawn_s", 300),
             "motivo": s["lore"]}
        if mdef.get("substituto"): g["substituto"] = mdef["substituto"]
        if mdef.get("ancora"): g["ancora"] = mdef["ancora"]; g["raio_territorio"] = mdef.get("raio_territorio", 4)
        if mdef.get("elite"): g["elite"] = True
        novos.append(g)
M["spawns"] = novos
# 3. descanso: fogueira + carrinho de poções
for de in DESC:
    M["props"].append({"kind": "fogueira", "x": de["x"], "y": de["y"] + 1, "light": [1, .5, .18, 6], "ponto": "descanso"})
    M["props"].append({"kind": "carrinho_tobias", "x": de["x"] + 1.5, "y": de["y"] - .5, "ponto": "descanso"})

# ---------------------------------------------------------------- lugares das linhas de quest D e E (Missões)
SP = {s["id"]: s for s in saida}
ZLG = {v: k for k, v in M["zonas_legenda"].items()}
def ponto_livre(cx, cy, zona=None, longe=(), r0=0, rmax=14):
    for r in range(r0, rmax + 1):
        cand = [(cx + dx, cy + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]
        RND.shuffle(cand)
        for x, y in cand:
            x, y = int(x), int(y)
            if not (0 <= x < N and 0 <= y < N) or BLOQ[x, y]: continue
            if zona and M["zonas_grid"][x][y] != ZLG[zona]: continue
            if any(math.hypot(x - a, y - b) < d for a, b, d in longe): continue
            return x + .5, y + .5
    return cx, cy
def fora_spots(f=1.0): return [(s["x"], s["y"], s["raio"]*f + 2) for s in saida]
def prop(kind, x, y, **kw):
    p = {"kind": kind, "x": round(x, 2), "y": round(y, 2)}; p.update(kw)
    if not os.path.exists(os.path.join(OBJ, kind + ".png")) and not os.path.exists(os.path.join(OBJ, kind + "_a.png")):
        p["pendente"] = True
        if kind not in M["props_pendentes"]: M["props_pendentes"].append(kind)
    M["props"].append(p); return p
def objeto(oid, x, y): M["objetos"].append({"id": oid, "x": round(x, 1), "y": round(y, 1)})
def npc(nid, ponto, x, y): M["npcs"].append({"id": nid, "ponto": ponto, "x": round(x, 1), "y": round(y, 1)})
LUG = []
# Rádio São Lázaro (Isaura Valente) no Bairro Afogado
rx, ry = ponto_livre(30, 68, "bairro_afogado", fora_spots())
prop("predio_enterrado", rx, ry, ponto="radio_sao_lazaro", light=[1, .6, .3, 5])
ax, ay = ponto_livre(rx + 2, ry + 2, "bairro_afogado", fora_spots(), 1)
prop("antena_radio", ax, ay, ponto="antena_radio", light=[1, .25, .15, 3]); objeto("antena_radio", ax, ay)
nx, ny = ponto_livre(rx + 2, ry - 1, "bairro_afogado", fora_spots(), 1); npc("isaura_radialista", "radio_sao_lazaro", nx, ny)
LUG.append({"id": "radio_sao_lazaro", "nome": "Rádio São Lázaro", "x": rx, "y": ry, "zona": "bairro_afogado"})
# loja da Corvina no sótão afogado
sot = next((p for p in M["props"] if p.get("ponto") == "sotao_afogado"), None)
cx0, cy0 = (sot["x"], sot["y"]) if sot else (33.5, 76)
lx, ly = ponto_livre(cx0 + 1, cy0 + 1, None, fora_spots(), 1)
prop("barraco_sucata", lx + 1, ly + 1, ponto="loja_corvina"); prop("caixas", lx - 1, ly + .5); prop("varal_lanternas", lx, ly - 1.5, ponto="loja_corvina")
npc("corvina_atravessadora", "sotao_afogado", lx, ly)
LUG.append({"id": "loja_corvina", "nome": "Loja da Corvina", "x": lx, "y": ly, "zona": "bairro_afogado"})
# Marco do Corte: o bonde tombado nos Campos de Cinza, estandartes caídos em volta
mc = SP["spot_marco_corte"]
bq = min((p for p in M["props"] if p["kind"] == "bonde_queimado"), key=lambda p: math.hypot(p["x"] - mc["x"], p["y"] - mc["y"]))
bq["ponto"] = "marco_do_corte"; objeto("marco_do_corte", bq["x"], bq["y"])
for i in range(4):
    a = i/4*2*math.pi + .4
    ex, ey = ponto_livre(bq["x"] + math.cos(a)*7, bq["y"] + math.sin(a)*7, "campos_cinza", [], 0, 5)
    prop("estandarte_rasgado", ex, ey, ponto="estandartes_caidos"); prop("ossos_espalhados", ex + .8, ey - .6, camada="chao"); objeto("estandartes_caidos", ex, ey)
LUG.append({"id": "marco_do_corte", "nome": "Marco do Corte", "x": bq["x"], "y": bq["y"], "zona": "campos_cinza"})
# Rastro de arrasto: do Marco, passando pelos Chiqueiros, até a porta do porão do Abatedouro
pg = next(o for o in M["objetos"] if o["id"] == "porta_ganchos"); ch = SP["spot_chiqueiros"]
cam = [(bq["x"], bq["y"]), (ch["x"] - 2, ch["y"] - 3), (pg["x"], pg["y"] + 2)]
pts = []
for (x0_, y0_), (x1_, y1_) in zip(cam, cam[1:]):
    L = math.hypot(x1_ - x0_, y1_ - y0_)
    for k in range(int(L/2.5)):
        t = k*2.5/L; pts.append((x0_ + (x1_ - x0_)*t, y0_ + (y1_ - y0_)*t))
for x, y in pts:
    if 0 <= int(x) < N and 0 <= int(y) < N and TER[int(x)][int(y)] not in "wr": prop("rastro_arrasto", x, y, camada="chao", visivel_se_missao=["e05a", "e05v"])
seg2 = [p for p in pts if math.hypot(p[0] - ch["x"], p[1] - ch["y"]) < ch["raio"] + 12]
for i in (0, len(seg2)//2, len(seg2) - 1):
    objeto("rastro_arrasto", *ponto_livre(seg2[i][0], seg2[i][1], None, [], 0, 3))
# Poças amargas: 5 poças verdes na margem do oásis, perto da Margem Amarga
agua_r = [(x, y) for x in range(N) for y in range(N) if TER[x][y] in "wr" and M["zonas_grid"][x][y] == ZLG["rio_amargo"]]
ma = SP["spot_margem_amarga"]; agua_r.sort(key=lambda c: math.hypot(c[0] - ma["x"], c[1] - ma["y"]))
pocas = []
for x, y in agua_r:
    if len(pocas) == 5: break
    if all(math.hypot(x - a, y - b) > 8 for a, b in pocas):
        px_, py_ = ponto_livre(x, y, None, [], 1, 3); pocas.append((px_, py_))
        prop("poca_toxica", px_, py_, ponto="pocas_amargas", camada="chao", light=[.4, 1, .3, 2]); objeto("pocas_amargas", px_, py_)
# Acampamento dos Desertores no centro do spot
ad = SP["spot_acampamento_desertores"]
for (dx, dy, k) in [(0, 0, "tenda_demonio"), (2.5, -1.5, "braseiro_ferro"), (-2.5, 1.5, "estandarte_rasgado"), (1.5, 2.5, "trono_sucata"), (-2, -2.5, "caixas")]:
    x, y = ponto_livre(ad["x"] + dx, ad["y"] + dy, None, [], 0, 3)
    prop(k, x, y, ponto="acampamento_desertores" if k == "tenda_demonio" else None, light=[1, .3, .1, 5] if k == "braseiro_ferro" else None)
LUG.append({"id": "acampamento_desertores", "nome": "Acampamento dos Desertores", "x": ad["x"], "y": ad["y"], "zona": "rio_amargo"})
# Vila militar do silo, no Bosque das Viúvas
vv = SP["spot_vila_viuvas"]
for (dx, dy, k) in [(vv["raio"] + 2, 0, "casa_ruina"), (vv["raio"] + 1, 4, "casa_ruina"), (vv["raio"], -4, "varal_roupas")]:
    x, y = ponto_livre(vv["x"] + dx, vv["y"] + dy, None, [], 0, 4); prop(k, x, y, ponto="vila_militar")
LUG.append({"id": "vila_militar", "nome": "Vila militar do silo", "x": vv["x"], "y": vv["y"], "zona": "bosque_viuvas"})
# Muro das Sombras (âncora do spot) e a escotilha do Silo São Lázaro, na borda da tempestade
ms = SP["spot_muro_sombras"]
for k in range(-4, 5):
    x, y = ms["x"] + k*1.0, ms["y"] + ms["raio"]*.75
    if 0 <= int(x) < N and 0 <= int(y) < N and not BLOQ[int(x), int(y)]: prop("muro_tijolo_quebrado" if k % 3 else "muro_tijolo", x, y, orient="x", ponto="muro_sombras")
ex_, ey_ = ponto_livre(ms["x"] + ms["raio"] + 6, ms["y"], "tempestade_areia", fora_spots(), 0, 12)
prop("escotilha_silo", ex_, ey_, ponto="escotilha_silo", fp=[3, 3]); prop("placa_aviso", ex_ - 2, ey_ - 2); objeto("escotilha_silo", ex_, ey_)
LUG.append({"id": "silo_sao_lazaro", "nome": "Silo São Lázaro (escotilha)", "x": ex_, "y": ey_, "zona": "tempestade_areia"})
for p in M["props"]:
    for k in [k for k, v in p.items() if v is None]: del p[k]
# subzona Chiqueiros (Missões): pedaço do Abatedouro em volta do spot
zg = [list(c) for c in M["zonas_grid"]]
for x in range(N):
    for y in range(N):
        if zg[x][y] == ZLG["abatedouro_carnica"] and math.hypot(x - ch["x"], y - ch["y"]) < ch["raio"] + 5: zg[x][y] = "l"
M["zonas_grid"] = ["".join(c) for c in zg]; M["zonas_legenda"]["l"] = "chiqueiros"
M["zonas"].append({"id": "chiqueiros", "nome": "Chiqueiros", "tipo": "caca", "nivel": [4, 6], "musica": "musica/sao_lazaro", "ambiente": "ambiente/abatedouro",
                   "eco": {"clima": "cercas de chapa e lama na frente do abatedouro; o rastro de arrasto passa por baixo da cerca", "neblina": .3}})
for z in M["zonas"]:
    if z["id"] == "rio_amargo":
        z["nivel"] = [6, 8]; z["tipo"] = "caca"
        z["eco"]["clima"] = "o oásis: o Jordão quase secou e sobrou um fio de água verde e amarga correndo no leito rachado, a única água do deserto; nas margens, a flor-de-absinto abre à noite"
    if z["id"] == "tempestade_areia": z["nivel"] = [9, 12]; z["tipo"] = "caca"
M["lugares"] = LUG

# 4. oásis do Rio Amargo (escolha do Jefin): flor-de-absinto nas margens, a vida torta só ali
agua = [(x, y) for x in range(N) for y in range(N) if TER[x][y] in "wr"]
margem = set()
for x, y in agua:
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            u, v = x + dx, y + dy
            if 0 <= u < N and 0 <= v < N and TER[u][v] not in "wrdh" and not BLOQ[u, v] and M["zonas_grid"][u][v] != "#": margem.add((u, v))
margem = sorted(margem); RND.shuffle(margem); flores = []
for u, v in margem:
    if all(abs(u - a) + abs(v - b) > 3 for a, b in flores): flores.append((u, v))
for u, v in flores:
    M["props"].append({"kind": "flor_absinto", "x": u + RND.uniform(.2, .8), "y": v + RND.uniform(.2, .8), "pendente": True, "luz_fraca": [.45, 1, .75, 1.5]})
if "flor_absinto" not in M["props_pendentes"]: M["props_pendentes"].append("flor_absinto")
M["spots"] = saida; M["descanso"] = DESC; M["spots_regras"] = REGRAS
M["versao"] = "0.4 (spots de farm, temperamento, oásis)"
json.dump(M, open(ARQ, "w"), ensure_ascii=False, separators=(",", ":"))
# validação: todo spawn em tile livre e alcançável a partir do spawn do jogador
from collections import deque
B = set(map(tuple, M["blocked"]))
sx, sy = int(M["spawn"][0]), int(M["spawn"][1]); vis = {(sx, sy)}; q = deque([(sx, sy)])
while q:
    x, y = q.popleft()
    for u, v in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
        if 0 <= u < N and 0 <= v < N and (u, v) not in vis and (u, v) not in B: vis.add((u, v)); q.append((u, v))
ruins = [g["kind"] + "@" + str((g["x"], g["y"])) for g in M["spawns"] if (int(g["x"]), int(g["y"])) not in vis]
print("lugares:", [l["id"] for l in LUG]); print(f"props tirados das clareiras: {removidos}; flores: {len(flores)}; spawns: {len(M['spawns'])} grupos, {sum(g['count'] for g in M['spawns'])} mobs")
print("spawns inalcançáveis:", ruins or "nenhum")
from collections import Counter
print(Counter(g.get("temperamento", "-") for g in M["spawns"] for _ in range(g["count"])))

# ---------------------------------------------------------------- imagem dos spots (vista de cima)
J = M["jogavel"]; S = 9; PAD = 40
x0, y0, x1, y1 = J["x0"] - 4, J["y0"] - 4, J["x1"] + 4, J["y1"] + 4
Wd, Hd = (x1-x0)*S, (y1-y0)*S
COR = {"a": (92, 78, 58), "u": (104, 88, 64), "d": (122, 104, 76), "h": (12, 10, 10), "y": (40, 62, 46), "q": (60, 70, 80),
       "s": (78, 64, 48), "t": (84, 70, 54), "z": (54, 52, 50), "c": (70, 66, 60), "g": (66, 66, 52), "l": (90, 86, 80),
       "m": (74, 54, 48), "w": (40, 90, 30), "r": (60, 120, 50), "b": (72, 58, 44), "e": (66, 74, 46), "p": (52, 70, 40),
       "f": (58, 54, 42), "v": (70, 56, 44), "k": (80, 76, 70)}
img = Image.new("RGB", (Wd + 2*PAD, Hd + 2*PAD + 160), (14, 12, 11)); d = ImageDraw.Draw(img)
def P(x, y):   # tela: x do mundo para a direita, y do mundo para cima
    return PAD + (x - x0)*S, PAD + (y1 - y)*S
for x in range(x0, x1):
    for y in range(y0, y1):
        c = COR.get(TER[x][y], (40, 40, 40))
        if M["amargo"][x][y] not in "0123" and TER[x][y] not in "hd": c = tuple(int(v*.8) for v in c)
        px, py = P(x, y); d.rectangle([px, py - S, px + S, py], fill=c)
for t in M["trilhas"]:
    d.line([P(*p) for p in t["pontos"]], fill=(150, 130, 96), width=max(2, int(t.get("largura", 2)*S*.5)))
for sz in M["safe_zones"]:
    px, py = P(sz["x"], sz["y"]); r = sz["radius"]*S
    d.ellipse([px-r, py-r, px+r, py+r], outline=(120, 170, 255), width=3)
F = os.path.join(AQUI, "PirataOne-Regular.ttf"); FI = os.path.join(AQUI, "IMFeENsc28P.ttf")
fT = ImageFont.truetype(F, 30); fS = ImageFont.truetype(FI, 20); fG = ImageFont.truetype(F, 46)
TEMP = {"neutro": (120, 200, 120), "territorial": (230, 190, 80), "agressivo": (230, 80, 60)}
for s in saida:
    px, py = P(s["x"], s["y"]); r = s["raio"]*S
    pior = "agressivo" if any(m["temperamento"] == "agressivo" for m in s["mobs"]) else ("territorial" if any(m["temperamento"] == "territorial" for m in s["mobs"]) else "neutro")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.ellipse([px-r, py-r, px+r, py+r], fill=TEMP[pior] + (60,), outline=TEMP[pior] + (255,), width=4)
    img = Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"); d = ImageDraw.Draw(img)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((px+dx, py - 18 + dy), s["nome"], font=fT, fill=(0, 0, 0), anchor="mm")
    d.text((px, py - 18), s["nome"], font=fT, fill=(240, 230, 205), anchor="mm")
    tot = sum(m["qtd"] for m in s["mobs"])
    txt = f'Nv {s["nivel"][0]}-{s["nivel"][1]} · {tot} mobs'
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((px+dx, py + 14 + dy), txt, font=fS, fill=(0, 0, 0), anchor="mm")
    d.text((px, py + 14), txt, font=fS, fill=TEMP[pior], anchor="mm")
for de in DESC:
    px, py = P(de["x"], de["y"])
    d.ellipse([px-9, py-9, px+9, py+9], fill=(255, 150, 50), outline=(40, 20, 10), width=2)
    d.text((px, py + 22), de["nome"], font=fS, fill=(255, 190, 120), anchor="mm")
for sz, nome in zip(M["safe_zones"], ["Acampamento da Vela", "Capela de São Lázaro"]):
    px, py = P(sz["x"], sz["y"]); d.text((px, py), nome, font=fS, fill=(150, 190, 255), anchor="mm")
yL = Hd + 2*PAD + 10
d.text((PAD, yL), "Spots de farm do Deserto de Absinto", font=fG, fill=(232, 220, 196))
x = PAD
for k, nome in [("neutro", "neutros (só revidam)"), ("territorial", "territoriais (defendem a toca)"), ("agressivo", "agressivos (lore)")]:
    d.ellipse([x, yL + 72, x + 22, yL + 94], fill=TEMP[k]); d.text((x + 30, yL + 70), nome, font=fS, fill=(220, 210, 190)); x += 330
x = PAD; yL += 34
d.ellipse([x, yL + 72, x + 22, yL + 94], fill=(255, 150, 50)); d.text((x + 30, yL + 70), "descanso: fogueira e poção", font=fS, fill=(220, 210, 190))
img.save(os.path.join(AQUI, "..", "spots.png"), optimize=True); print("spots.png")

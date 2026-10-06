"""Gera data/mapas/*.json no formato que o WorldSim e o cliente leem.

- area_inicial: convertido do mapa aprovado (data/design/mapas/area_inicial.json, que vem de design/mapas/ pelo sync).
- porao_matadouro, ossario_carpideiras, camara_trombeta: os 3 andares da Cripta da Trombeta Calada,
  montados aqui com o kit de ambiente (paredes, arenas, props e luzes).

Formato de saída (linhas indexadas por y, um caractere por x):
  grade        '#' bloqueado, '.' livre
  terreno      caractere do piso (legenda em PISOS)
  zona_grade   'A'+índice em zonas, '.' sem zona
  props        [{k, x, y, chao?, luz?}]   k = nome do objeto do kit (já com _a/_b)
  objetos      baús, interativos, portais (lidos pelo servidor)
"""
import json, math, os, random

G = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{G}/data/mapas"
os.makedirs(OUT, exist_ok=True)
MIS = f"{G}/data/design/missoes"
OBJ = {o["id"]: o for o in json.load(open(f"{MIS}/objetos.json"))["objetos"]}
BAUS = {b["id"]: b for b in json.load(open(f"{MIS}/objetos.json"))["baus"]}
KIT = set(json.load(open(f"{G}/data/ext/ambiente.json"))["objetos"].keys())

# caractere -> piso (atlas em assets/ext/ambiente/tiles). ' ' e 'h' = vazio (escuro)
PISOS = {"a": "areia", "u": "duna", "d": "duna", "y": "areia_vitrificada", "q": "vidro", "s": "leito_rachado",
         "t": "terra", "z": "cinza", "c": "calcamento", "g": "cemiterio", "l": "laje_capela", "m": "chapa_matadouro",
         "w": "lama", "r": "agua_toxica", "b": "barranca", "e": "musgo", "p": "brejo", "f": "mata_morta", "v": "vala",
         "k": "cascalho", "x": "cripta", "o": "ossario", "j": "laje_trombeta", "n": "entulho", "i": "asfalto_rachado"}

def kit_nome(kind, orient=None):
    """Nome do objeto do kit para o kind do mapa (paredes e cercas têm variante _a ao longo de X, _b ao longo de Y)."""
    if kind in KIT: return kind
    suf = "_b" if orient == "y" else "_a"
    if kind + suf in KIT: return kind + suf
    if kind + "_a" in KIT: return kind + "_a"
    return kind  # sem arte ainda: o cliente esconde até o kit chegar

def salvar(m):
    m["pisos"] = PISOS
    json.dump(m, open(f"{OUT}/{m['id']}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(m["id"], m["w"], "x", m["h"], "props", len(m["props"]), "spawns", len(m["spawns"]), "objetos", len(m["objetos"]))

# ====================================================================== área inicial (deserto)
def area_inicial():
    d = json.load(open(f"{G}/data/design/mapas/area_inicial.json"))
    n = d["size"]
    ter = [[d["terreno"][x][y] for x in range(n)] for y in range(n)]
    blk = [[False] * n for _ in range(n)]
    for x, y in d["blocked"]: blk[y][x] = True
    for y in range(n):
        for x in range(n):
            if ter[y][x] in "dhw": blk[y][x] = True
    # zonas
    leg = d["zonas_legenda"]; zinfo = {z["id"]: z for z in d["zonas"]}
    zonas, zidx = [], {}
    for ch, zid in leg.items():
        if ch == "#": continue
        z = zinfo.get(zid, {"id": zid})
        zidx[ch] = len(zonas)
        zonas.append({"id": zid, "nome": z.get("nome", zid), "seguro": bool(z.get("seguro", False)), "nivel": z.get("nivel"),
                      "musica": z.get("musica"), "ambiente": z.get("ambiente"), "faccao": z.get("faccao"),
                      "neblina": z.get("eco", {}).get("neblina", 0.0) if isinstance(z.get("eco"), dict) else 0.0})
    zg = ["".join(chr(65 + zidx[d["zonas_grid"][x][y]]) if d["zonas_grid"][x][y] in zidx else "." for x in range(n)) for y in range(n)]
    amargo = ["".join(d["amargo"][x][y] for x in range(n)) for y in range(n)]
    props, luzes = [], [list(l) for l in d["luzes"]]
    for p in d["props"]:
        if p.get("invisivel"): continue
        q = {"k": kit_nome(p["kind"], p.get("orient")), "x": p["x"], "y": p["y"]}
        if p.get("camada") in ("chao", "agua"): q["chao"] = 1
        if p.get("objeto") or p.get("bau"): q["obj"] = 1   # o servidor cria a entidade; o prop é só o visual
        if p.get("texto"): q["texto"] = p["texto"]
        props.append(q)
    objetos = []
    for b in d["baus"]:
        h = BAUS.get(b["id"], {})
        o = {"kind": "bau", "pos": [b["x"], b["y"]], "bau": "bau_de_ferro" if b.get("kind") == "bau_raro" else "caixote_podre",
             "visual": b.get("kind", "bau_comum"), "id_mapa": b["id"]}
        if b.get("tipo") == "trancado" or h.get("tipo") == "trancado": o["trancado"] = True
        if h: o["hist"] = b["id"]
        if h.get("visivel_se"): o["visivel_se"] = h["visivel_se"]
        if "texto_ao_abrir" in b and not h: o["texto_ao_abrir"] = b["texto_ao_abrir"]
        if "nome" in b: o["nome"] = b["nome"]
        objetos.append(o)
        for p in props:
            if p.get("obj") and abs(p["x"] - b["x"]) < 0.6 and abs(p["y"] - b["y"]) < 0.6: p["oculto_por_obj"] = 1
    cont = {}
    for ob in d["objetos"]:
        i = cont.get(ob["id"], 0); cont[ob["id"]] = i + 1
        o = {"kind": "interativo", "obj": ob["id"], "pos": [ob["x"], ob["y"]], "i": i}
        if ob["id"] == "porta_ganchos":
            o["mapa"] = "porao_matadouro"; o["chegada"] = [12.5, 50.5]
        objetos.append(o)
    # baús do mundo extras (sistema de baús: caixotes podres espalhados nas zonas de caça, alguns são Baú Faminto)
    rng = random.Random(7)
    livres = []
    for y in range(22, 138):
        for x in range(22, 138):
            if blk[y][x] or zg[y][x] == "." or zonas[ord(zg[y][x]) - 65]["seguro"]: continue
            if all(not blk[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)): livres.append((x, y))
    escolhidos = []
    while len(escolhidos) < 14 and livres:
        c = rng.choice(livres)
        if all(math.dist(c, e) > 12 for e in escolhidos) and all(math.dist(c, (b["x"], b["y"])) > 8 for b in d["baus"]):
            escolhidos.append(c)
    for i, (x, y) in enumerate(escolhidos):
        o = {"kind": "bau", "pos": [x + 0.5, y + 0.5], "bau": "caixote_podre", "visual": "bau_comum", "id_mapa": f"caixote_{i}"}
        if i % 5 == 3: o["mimico"] = True
        if i % 4 == 1: o["bau"] = "bau_de_ferro"; o["visual"] = "bau_raro"
        objetos.append(o)
    def livre_perto(x, y, r=4):
        """Centro da célula livre mais perto de (x, y) (objetos e NPCs não podem cair dentro de parede)."""
        best = None
        for yy in range(int(y) - r, int(y) + r + 1):
            for xx in range(int(x) - r, int(x) + r + 1):
                if 0 <= xx < n and 0 <= yy < n and not blk[yy][xx]:
                    dd = math.dist((xx + 0.5, yy + 0.5), (x, y))
                    if best is None or dd < best[0]: best = (dd, xx + 0.5, yy + 0.5)
        return [round(best[1], 2), round(best[2], 2)] if best else [x, y]
    pontos = {}
    for p in d["props"]:
        if p.get("ponto") and p["ponto"] not in pontos: pontos[p["ponto"]] = (p["x"], p["y"])
    # objetos de missão que o mapa ainda não posiciona (linhas D e E da v0.6 e o escritório do capataz):
    # ficam no ponto de mesmo nome quando existe, senão nas posições abaixo (perto dos spots que as missões usam)
    ja = {o.get("obj") for o in objetos if o["kind"] == "interativo"}
    POS_OBJ = {
        "escritorio_capataz": [(121.0, 59.5)],
        "estandartes_caidos": [(58.0, 70.0), (62.5, 87.0), (52.0, 63.0), (68.0, 79.5)],
        "marco_do_corte": [(66.5, 79.0)],
        "rastro_arrasto": [(118.5, 70.0), (121.5, 66.0), (119.0, 61.5)],
        "pocas_amargas": [(106.0, 93.0), (104.5, 97.5), (108.0, 89.0), (103.0, 101.0), (107.5, 95.5)],
        "escotilha_silo": [(97.0, 128.5)],
        "antena_radio": [(30.5, 80.5)],
    }
    VIS_OBJ = {"estandartes_caidos": "estandarte_rasgado", "pocas_amargas": "poca_toxica", "escotilha_silo": "tambores_radioativos",
               "antena_radio": "poste_telegrafo", "rastro_arrasto": "poca_sangue"}
    for oid, lst in POS_OBJ.items():
        if oid in ja or oid not in OBJ: continue
        for i, (x, y) in enumerate(lst):
            pp = livre_perto(x, y)
            objetos.append({"kind": "interativo", "obj": oid, "pos": pp, "i": i})
            if oid in VIS_OBJ and VIS_OBJ[oid] in KIT:
                props.append({"k": VIS_OBJ[oid], "x": pp[0], "y": pp[1] - 0.6, "obj": 1, **({"chao": 1} if VIS_OBJ[oid].startswith("poca") else {})})
    # flores do oásis sem arte ainda: planta mutante no lugar
    for p in props:
        if p["k"] not in KIT and p["k"] == "flor_absinto" and "planta_mutante" in KIT: p["k"] = "planta_mutante"
    # spots de farm (v0.4 do mapa): spawns com temperamento, respawn e spot
    spots = [{"id": sp["id"], "nome": sp["nome"], "nivel": sp["nivel"], "pos": [sp["x"], sp["y"]], "raio": sp["raio"],
              "respawn_s": sp.get("respawn_s", 14)} for sp in d.get("spots", [])]
    spawns = []
    for s in d["spawns"]:
        if s.get("so_para") or s.get("so_por_missao"): continue   # patrulhas de facção = PvP depois; Filho de Cardo nasce pela missão
        mob = s.get("variante") or s.get("kind_design") or s["kind"]   # kind = substituto antigo; kind_design/variante = o monstro de verdade
        g = {"mob": mob, "pos": [s["x"], s["y"]], "raio": s.get("radius", 2), "qtd": s.get("count", 1), "nivel": s.get("level")}
        for k in ("patrulha", "formacao", "direcao", "elite", "ancora", "temperamento", "respawn_s", "spot", "raio_territorio"):
            if k in s: g[k] = s[k]
        spawns.append(g)
    # monstros novos das linhas D e E (pedidos da thread de Missões em locais.json -> spots): enquanto a Level design
    # não os põe no mapa, entram nos spots existentes mais perto do que foi pedido
    EXTRA = [
        # acampamento_desertores (Rio Amargo) -> margem_das_viuvas, na beira do rio
        ("desertor_legiao", 105.5, 95.0, 3, 7, "territorial", "margem_das_viuvas"),
        ("desertor_legiao", 108.5, 99.0, 3, 8, "territorial", "margem_das_viuvas"),
        ("sangrador_apostata", 112.5, 108.0, 2, 6, "neutro", "margem_das_viuvas"),
        ("sangrador_apostata", 117.0, 106.5, 2, 7, "neutro", "margem_das_viuvas"),
        # marco_do_corte (bonde tombado, Campos de Cinza) -> covas_rasas
        ("desertor_legiao", 67.5, 72.5, 3, 8, "territorial", "covas_rasas"),
        ("desertor_legiao", 64.0, 70.0, 2, 9, "territorial", "covas_rasas"),
        # sombras do muro da vila militar -> beira_da_tempestade
        ("sombra_gravada", 101.0, 125.5, 3, 10, "neutro", "beira_da_tempestade"),
        ("sombra_gravada", 106.0, 129.0, 3, 11, "neutro", "beira_da_tempestade"),
    ]
    for mob, x, y, q, lv, temp, spot in EXTRA:
        pp = livre_perto(x, y)
        g = {"mob": mob, "pos": pp, "raio": 1.5, "qtd": q, "nivel": lv, "temperamento": temp, "spot": spot, "respawn_s": 14}
        if temp == "territorial": g["raio_territorio"] = 4
        spawns.append(g)
    # spots que as missões pedem e o mapa não tem: apelido para o spot existente mais perto
    spot_alias = {"acampamento_desertores": "margem_das_viuvas", "marco_do_corte": "covas_rasas"}
    npcs = [{"id": p["id"], "pos": [p["x"], p["y"]], "dir": [1, 0]} for p in d["npcs"]]
    ids_npc = {p["id"] for p in d["npcs"]}
    for nid, ponto, off in (("isaura_radialista", "relogio_afogado", (1.8, 1.6)), ("corvina_atravessadora", "sotao_afogado", (1.6, 0.8))):
        if nid in ids_npc: continue
        x, y = pontos.get(ponto, (32.0, 78.0))
        npcs.append({"id": nid, "pos": livre_perto(x + off[0], y + off[1]), "dir": [0, 1]})
    # pontos de descanso: o carrinho do Tobias em cada fogueira vende poção
    for i, ds in enumerate(d.get("descanso", [])):
        car = next((p for p in d["props"] if p.get("ponto") == "descanso" and p["kind"] == "carrinho_tobias"
                    and math.dist((p["x"], p["y"]), (ds["x"], ds["y"])) < 4), None)
        x, y = (car["x"] + 1.2, car["y"] + 1.0) if car else (ds["x"] + 2, ds["y"])
        npcs.append({"id": "tobias_carrinho", "pos": livre_perto(x, y), "dir": [-1, 1], "descanso": ds["nome"]})
    cl = d["camera_limite"]
    m = {"id": "area_inicial", "nome": d["name"], "w": n, "h": n,
         "grade": ["".join("#" if blk[y][x] else "." for x in range(n)) for y in range(n)],
         "terreno": ["".join(ter[y]) for y in range(n)], "zona_grade": zg, "zonas": zonas, "amargo": amargo,
         "npcs": npcs, "objetos": objetos, "spawns": spawns, "spots": spots, "spot_alias": spot_alias, "props": props, "luzes": luzes,
         "sons": d.get("sons_pontuais", []), "camera": [cl["x0"], cl["y0"], cl["x1"], cl["y1"]],
         "spawn": d["spawn"], "spawn_por_faccao": d["spawn_por_faccao"],
         "rio": {"centro": d["rio"]["centro"], "largura": d["rio"]["largura"]},
         "ceu": {"escuro": 0.35, "cor": [0.78, 0.82, 0.74], "neblina": [0.55, 0.62, 0.48]}, "exterior": True}
    salvar(m)

# ====================================================================== masmorra
class Andar:
    def __init__(s, id, nome, w, h, piso, parede, zona):
        s.id, s.nome, s.w, s.h, s.piso, s.parede = id, nome, w, h, piso, parede
        s.ter = [[" "] * w for _ in range(h)]
        s.blk = [[True] * w for _ in range(h)]
        s.props, s.luzes, s.objetos, s.spawns, s.npcs = [], [], [], [], []
        s.zona = zona
        s.rng = random.Random(hash(id) & 0xffff)
        s.extra_blk = set()

    def sala(s, x0, y0, x1, y1, piso=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.ter[y][x] = piso or s.piso; s.blk[y][x] = False

    def circulo(s, cx, cy, r, piso=None):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r:
                    s.ter[y][x] = piso or s.piso; s.blk[y][x] = False

    def corredor(s, pts, larg=3, piso=None):
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = int(max(abs(bx - ax), abs(by - ay)) * 2) + 1
            for i in range(n + 1):
                t = i / n; cx = ax + (bx - ax) * t; cy = ay + (by - ay) * t
                for y in range(int(cy - larg / 2), int(cy + larg / 2) + 1):
                    for x in range(int(cx - larg / 2), int(cx + larg / 2) + 1):
                        if 0 <= x < s.w and 0 <= y < s.h:
                            s.ter[y][x] = piso or s.piso; s.blk[y][x] = False

    def prop(s, k, x, y, bloqueia=0, chao=False, luz=None):
        q = {"k": k, "x": x, "y": y}
        if chao: q["chao"] = 1
        s.props.append(q)
        if luz: s.luzes.append([x, y] + luz)
        if bloqueia:
            r = bloqueia
            for yy in range(int(y - r), int(y + r) + 1):
                for xx in range(int(x - r), int(x + r) + 1):
                    if math.hypot(xx + 0.5 - x, yy + 0.5 - y) <= r + 0.2: s.extra_blk.add((xx, yy))

    def livre(s, x, y):
        return 0 <= x < s.w and 0 <= y < s.h and not s.blk[y][x]

    def paredes(s):
        """Paredes só nas bordas de trás (lado de cima da tela): vazio em x-1 -> parede ao longo de Y (_b); vazio em y+1 -> ao longo de X (_a).
        As bordas da frente ficam abertas para não esconder o personagem; o escuro do vazio fecha a sala."""
        for y in range(s.h):
            for x in range(s.w):
                if not s.blk[y][x]: continue
                if s.livre(x + 1, y) and not s.livre(x, y - 1):
                    s.prop(s.parede + "_b", x + 0.5, y + 0.5)
                elif s.livre(x, y - 1) and not s.livre(x + 1, y):
                    s.prop(s.parede + "_a", x + 0.5, y + 0.5)
                elif s.livre(x + 1, y) and s.livre(x, y - 1):
                    s.prop(s.parede + "_a", x + 0.5, y + 0.5)
                elif s.livre(x + 1, y - 1) and not s.livre(x + 1, y) and not s.livre(x, y - 1):
                    s.prop(s.parede + "_a", x + 0.5, y + 0.5)

    def espalhar(s, kinds, n, area, chao=True, bloq=0, dist=1.5):
        x0, y0, x1, y1 = area
        feitos = 0; tent = 0
        while feitos < n and tent < 400:
            tent += 1
            x = s.rng.uniform(x0, x1); y = s.rng.uniform(y0, y1)
            if not s.livre(int(x), int(y)) or (int(x), int(y)) in s.extra_blk: continue
            if any(math.dist((x, y), (p["x"], p["y"])) < dist for p in s.props if not p.get("chao") or chao): continue
            s.prop(s.rng.choice(kinds), round(x, 2), round(y, 2), bloqueia=bloq, chao=chao); feitos += 1

    def spawn(s, mob, x, y, qtd=1, raio=1.5, nivel=None):
        s.spawns.append({"mob": mob, "pos": [x, y], "raio": raio, "qtd": qtd, "nivel": nivel})

    def portal(s, x, y, para, chegada, nome, visual="escada_descida", **kw):
        o = {"kind": "portal", "pos": [x, y], "para": para, "chegada": chegada, "nome": nome, "visual": visual}
        o.update(kw); s.objetos.append(o)

    def exportar(s, chefe=None, ceu=None, spawn=None):
        for (x, y) in s.extra_blk:
            if 0 <= x < s.w and 0 <= y < s.h: s.blk[y][x] = True
        xs = [x for y in range(s.h) for x in range(s.w) if s.ter[y][x] != " "]
        ys = [y for y in range(s.h) for x in range(s.w) if s.ter[y][x] != " "]
        m = {"id": s.id, "nome": s.nome, "w": s.w, "h": s.h,
             "grade": ["".join("#" if s.blk[y][x] else "." for x in range(s.w)) for y in range(s.h)],
             "terreno": ["".join(s.ter[y]) for y in range(s.h)],
             "zona_grade": ["".join("A" if s.ter[y][x] != " " else "." for x in range(s.w)) for y in range(s.h)],
             "zonas": [s.zona], "npcs": s.npcs, "objetos": s.objetos, "spawns": s.spawns, "props": s.props, "luzes": s.luzes,
             "camera": [min(xs) - 4, min(ys) - 4, max(xs) + 5, max(ys) + 5], "spawn": spawn,
             "ceu": ceu or {"escuro": 0.86, "cor": [0.5, 0.42, 0.4], "neblina": [0.1, 0.07, 0.06]}, "exterior": False}
        if chefe: m["chefe"] = chefe
        salvar(m)

def porta_da_arena(a, cx, cy, r):
    cel = []
    for y in range(a.h):
        for x in range(a.w):
            dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r + 0.6 < dd < r + 2.2 and a.livre(x, y): cel.append([x, y])
    return cel

def porao_matadouro():
    a = Andar("porao_matadouro", "Porão do Matadouro", 72, 64, "m", "parede_matadouro",
              {"id": "porao_matadouro", "nome": "Porão do Matadouro", "seguro": False, "nivel": [6, 8],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_porao"})
    a.sala(8, 46, 17, 55)                       # chegada (pé da escada)
    a.corredor([(17, 50.5), (25, 50.5)])
    a.sala(25, 42, 38, 57)                      # câmara fria
    a.corredor([(31.5, 42), (31.5, 33)])
    a.sala(24, 22, 38, 33)                      # casa das caldeiras
    a.corredor([(38, 27.5), (47, 27.5)], larg=3)
    a.circulo(56, 27.5, 8.5, piso="v")          # fosso da Grande Batalha
    a.sala(53, 14, 59, 18, piso="x")            # nicho do baú e da escada (atrás da arena)
    a.corredor([(56, 18), (56, 20)], larg=3, piso="x")
    a.corredor([(38, 50), (44, 50), (44, 41)], larg=3)
    a.sala(39, 37, 47, 41, piso="n")            # depósito desabado (atalho cego com baú)
    # chegada
    a.portal(10.5, 48.5, "area_inicial", [121.5, 47.5], "Escada para o Abatedouro", visual="escada_subida")
    a.prop("caixas", 15.2, 47.2, bloqueia=0.4); a.prop("barris", 9.5, 54.0, bloqueia=0.4)
    a.prop("braseiro_ferro", 13.5, 52.5, bloqueia=0.4, luz=[1, 0.45, 0.15, 6])
    a.prop("poca_sangue_rastro", 18.5, 50.5, chao=True)
    # câmara fria
    for gx in (27.5, 31.5, 35.5):
        for gy in (45.5, 49.5, 53.5):
            if (gx, gy) != (31.5, 49.5): a.prop("ganchos_carne", gx, gy, bloqueia=0.4)
    a.prop("mesa_acougue", 31.5, 49.5, bloqueia=0.7)
    a.luzes += [[31.5, 44.0, 1, 0.3, 0.15, 6], [31.5, 55.0, 1, 0.3, 0.15, 6], [26.5, 50, 0.9, 0.35, 0.2, 4], [37, 50, 0.9, 0.35, 0.2, 4]]
    a.espalhar(["poca_sangue", "poca_sangue_rastro", "ralo_ferro"], 9, (25, 42, 38, 57))
    a.spawn("larva_de_carne", 29, 47, 3, 2.0, 6); a.spawn("acougueiro_oco", 34, 54, 1, 0.5, 6); a.spawn("larva_de_carne", 35, 45, 2, 1.5, 6)
    # caldeiras
    a.prop("caldeira_vapor", 27.5, 25.0, bloqueia=1.2, luz=[1, 0.4, 0.1, 7]); a.prop("caldeira_vapor", 35.5, 25.0, bloqueia=1.2, luz=[1, 0.4, 0.1, 7])
    a.prop("canos_parede", 31.0, 23.0, bloqueia=0.5); a.prop("tonel_fogo", 30.0, 31.0, bloqueia=0.4, luz=[1, 0.5, 0.15, 5])
    a.espalhar(["poca_agua", "ralo_ferro", "poca_sangue"], 6, (24, 22, 38, 33))
    a.spawn("gancheiro", 31, 29, 2, 2.0, 7); a.spawn("acougueiro_oco", 26, 31, 1, 0.5, 7); a.spawn("larva_de_carne", 36, 31, 2, 1.0, 7)
    # depósito com baú
    a.prop("entulho", 40.5, 38.0, bloqueia=0.6); a.prop("caixas", 46.5, 38.0, bloqueia=0.4)
    a.objetos.append({"kind": "bau", "pos": [43.5, 38.0], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "deposito"})
    a.spawn("gancheiro", 43, 40, 1, 0.5, 7); a.luzes.append([43, 39, 1, 0.5, 0.2, 4])
    # corredor ao fosso
    a.prop("gaiola_suspensa", 42.5, 26.5); a.prop("poca_sangue_rastro", 44.5, 27.5, chao=True)
    a.spawn("soldado_caido", 44, 28, 2, 1.0, 8)
    # arena do General: fosso com 6 Pilhas de Mortos
    cx, cy, r = 56.0, 27.5, 8.5
    a.prop("arena_moedor", 60.5, 22.5, bloqueia=1.8, luz=[1, 0.25, 0.08, 9])
    a.espalhar(["ossos_espalhados", "pilha_cranios", "poca_sangue"], 14, (cx - 7, cy - 7, cx + 7, cy + 7))
    pilhas = [[cx + 6 * math.cos(t), cy + 6 * math.sin(t)] for t in [i * math.tau / 6 + 0.4 for i in range(6)]]
    pilhas = [[round(x, 1), round(y, 1)] for x, y in pilhas if a.livre(int(x), int(y)) and (int(x), int(y)) not in a.extra_blk]
    for ang in range(0, 360, 45):
        t = math.radians(ang); a.luzes.append([cx + 7.5 * math.cos(t), cy + 7.5 * math.sin(t), 1, 0.3, 0.12, 4])
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 55.0, 16.0)
    a.objetos.append({"kind": "bau", "pos": [55.0, 16.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_general", "requer_chefe": "general_partido", "id_mapa": "bau_general"})
    a.portal(57.5, 15.5, "ossario_carpideiras", [12.5, 32.5], "Escada para o Ossário", requer_flag="venceu_general_partido",
             texto_trancado="Os ossos do fosso tapam a escada. O General está sentado em cima.")
    a.luzes += [[56, 16, 0.9, 0.5, 0.25, 5], [13, 48, 0.8, 0.6, 0.4, 5]]
    a.paredes()
    a.exportar(chefe={"id": "general_partido", "pos": [cx + 1.5, cy - 2.5], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta, "pilhas": pilhas},
               spawn=[12.5, 50.5])

def ossario_carpideiras():
    a = Andar("ossario_carpideiras", "Ossário das Carpideiras", 72, 66, "o", "parede_ossario",
              {"id": "ossario_carpideiras", "nome": "Ossário das Carpideiras", "seguro": False, "nivel": [8, 10],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_ossario"})
    a.sala(8, 28, 16, 37)                       # chegada
    a.corredor([(16, 32.5), (30, 32.5)], larg=3)
    a.sala(22, 40, 34, 50)                      # galeria das celas
    a.corredor([(26.5, 34), (26.5, 40)], larg=3)
    a.sala(30, 12, 42, 24)                      # capela das velas
    a.corredor([(26.5, 32), (26.5, 18), (30, 18)], larg=3)
    a.corredor([(34, 45), (44, 45)], larg=3)
    a.circulo(52, 45.5, 8.0, piso="x")          # capela redonda da Irmã Celeste
    a.corredor([(52, 53), (52, 58)], larg=3, piso="x")
    a.sala(48, 58, 56, 62, piso="x")            # antecâmara da porta da Câmara
    # chegada
    a.portal(10.5, 30.5, "porao_matadouro", [56.5, 18.5], "Escada para o Porão", visual="escada_subida")
    a.prop("candelabro_ossos", 14.5, 35.5, bloqueia=0.4, luz=[1, 0.75, 0.4, 6])
    a.espalhar(["ossos_espalhados", "pilha_cranios"], 5, (8, 28, 16, 37))
    # celas dos monges (objeto da missão + monstros)
    celas = [(23.0, 41.0), (26.0, 41.0), (29.0, 41.0), (32.0, 41.0), (23.0, 49.0), (27.0, 49.0), (31.0, 49.0)]
    for i, (x, y) in enumerate(celas):
        a.prop("monge_emparedado", x + 0.5, y + 0.5, bloqueia=0.5)
        a.objetos.append({"kind": "interativo", "obj": "cela_monge", "pos": [x + 0.5, y + 1.5 if y < 45 else y - 0.5], "i": i})
    a.prop("sarcofago", 28.0, 45.0, bloqueia=0.8)
    a.objetos.append({"kind": "bau", "pos": [33.0, 45.0], "bau": "bau_de_ferro", "visual": "bau_raro", "hist": "bau_amaldicoado_ossario", "id_mapa": "caixao"})
    a.luzes += [[24, 45, 1, 0.75, 0.4, 5], [32, 45, 1, 0.75, 0.4, 5]]
    a.spawn("monge_emparedado", 26, 45, 2, 2.0, 8); a.spawn("fogo_de_vela", 30, 47, 3, 2.0, 8)
    # capela das velas
    a.prop("candelabro_ossos", 32.5, 14.5, bloqueia=0.4, luz=[1, 0.75, 0.4, 7]); a.prop("candelabro_ossos", 40.5, 22.5, bloqueia=0.4, luz=[1, 0.75, 0.4, 7])
    a.prop("estatua_anjo_quebrada", 36.5, 13.5, bloqueia=0.8)
    a.espalhar(["ossos_espalhados", "pilha_cranios", "folhas_papeis"], 9, (30, 12, 42, 24))
    a.spawn("carpideira_de_ossos", 36, 18, 2, 2.0, 9); a.spawn("fogo_de_vela", 33, 21, 3, 1.5, 9); a.spawn("monge_emparedado", 39, 15, 1, 1.0, 9)
    a.objetos.append({"kind": "bau", "pos": [41.0, 13.0], "bau": "caixote_podre", "visual": "bau_comum", "id_mapa": "capela"})
    a.spawn("monge_emparedado", 40, 45, 1, 0.5, 9); a.spawn("carpideira_de_ossos", 42, 44, 1, 0.5, 9)
    # arena de Celeste: trono, 4 coristas, velas
    cx, cy, r = 52.0, 45.5, 8.0
    a.prop("arena_carpideiras", 57.5, 40.0, bloqueia=1.5, luz=[1, 0.8, 0.5, 8])
    coristas = [[cx - 5.5, cy - 5.5], [cx + 5.5, cy - 5.5], [cx - 5.5, cy + 5.5], [cx + 5.5, cy + 5.5]]
    coristas = [[x, y] for x, y in coristas if a.livre(int(x), int(y))]
    a.espalhar(["ossos_espalhados", "poca_agua"], 8, (cx - 6, cy - 6, cx + 6, cy + 6))
    for ang in range(0, 360, 60):
        t = math.radians(ang); a.luzes.append([cx + 7 * math.cos(t), cy + 7 * math.sin(t), 1, 0.75, 0.45, 4])
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 50.0, 59.5)
    a.objetos.append({"kind": "bau", "pos": [50.0, 59.5], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_celeste", "requer_chefe": "irma_celeste", "id_mapa": "bau_celeste"})
    a.prop("portao_ferro", 52.5, 61.5)
    a.objetos.append({"kind": "interativo", "obj": "porta_camara", "pos": [52.5, 61.0], "mapa": "camara_trombeta", "chegada": [12.5, 34.5]})
    a.luzes += [[52, 60, 0.8, 0.85, 1, 5], [12, 32, 1, 0.75, 0.4, 5]]
    a.paredes()
    a.exportar(chefe={"id": "irma_celeste", "pos": [cx + 3, cy - 3], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta, "coristas": coristas},
               ceu={"escuro": 0.9, "cor": [0.55, 0.5, 0.45], "neblina": [0.08, 0.07, 0.06]}, spawn=[12.5, 32.5])

def camara_trombeta():
    a = Andar("camara_trombeta", "Câmara da Trombeta", 70, 70, "j", "parede_trombeta",
              {"id": "camara_trombeta", "nome": "Câmara da Trombeta", "seguro": False, "nivel": [10, 12],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_camara"})
    a.sala(8, 30, 16, 39)                       # chegada
    a.corredor([(16, 34.5), (24, 34.5)], larg=4)
    a.sala(24, 26, 36, 43)                      # nave de pilares
    a.corredor([(36, 34.5), (42, 34.5)], larg=4)
    a.circulo(52, 34.5, 10.0)                   # Salão da Trombeta
    a.sala(48, 47, 56, 52, piso="x")            # cripta do relicário (abre depois do chefe)
    a.corredor([(52, 44), (52, 47)], larg=3, piso="x")
    a.portal(10.5, 32.5, "ossario_carpideiras", [52.5, 59.5], "Escada para o Ossário", visual="escada_subida")
    a.prop("braseiro_ferro", 14.5, 37.5, bloqueia=0.4, luz=[1, 0.9, 0.6, 6])
    for y in (28.5, 40.5):
        for x in (27.5, 33.5):
            a.prop("pilar_porcelana", x, y, bloqueia=0.7)
    a.luzes += [[30.5, 30, 1, 0.9, 0.6, 6], [30.5, 39, 1, 0.9, 0.6, 6]]
    a.espalhar(["folhas_papeis", "ossos_espalhados"], 6, (24, 26, 36, 43))
    a.spawn("querubim_desfeito", 30, 32, 2, 2.0, 10); a.spawn("eco_da_trombeta", 31, 38, 2, 1.5, 11)
    a.spawn("querubim_desfeito", 39, 34, 1, 0.5, 11)
    cx, cy, r = 52.0, 34.5, 10.0
    a.prop("arena_trombeta", 58.5, 29.5, bloqueia=1.8, luz=[1, 0.92, 0.6, 10])
    pilares = [[cx - 4.5, cy - 4.5], [cx + 4.5, cy - 4.5], [cx - 4.5, cy + 4.5], [cx + 4.5, cy + 4.5]]
    for x, y in pilares: a.prop("pilar_porcelana", x, y, bloqueia=0.7)
    for ang in range(0, 360, 45):
        t = math.radians(ang); a.luzes.append([cx + 8.5 * math.cos(t), cy + 8.5 * math.sin(t), 1, 0.85, 0.55, 4])
    a.espalhar(["folhas_papeis", "ossos_espalhados"], 8, (cx - 8, cy - 8, cx + 8, cy + 8))
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 50.0, 50.0)
    a.objetos.append({"kind": "bau", "pos": [50.0, 50.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_zacarias", "requer_chefe": "zacarias_arauto", "id_mapa": "bau_zacarias"})
    a.objetos.append({"kind": "bau", "pos": [54.0, 50.0], "bau": "relicario_da_trombeta", "visual": "bau_chefe", "requer_chefe": "zacarias_arauto", "id_mapa": "relicario"})
    a.portal(52.5, 51.5, "area_inicial", [121.5, 47.5], "Subir à superfície", visual="escada_subida", requer_flag="venceu_zacarias_arauto",
             texto_trancado="A escada sobe para a luz, mas o Arauto ainda guarda o caminho.")
    a.luzes += [[52, 50, 1, 0.9, 0.6, 5], [12, 34, 1, 0.9, 0.6, 5]]
    a.paredes()
    a.exportar(chefe={"id": "zacarias_arauto", "pos": [cx + 3, cy - 3], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta,
                      "trombeta": [cx + 5.5, cy - 5.0]},
               ceu={"escuro": 0.84, "cor": [0.7, 0.62, 0.45], "neblina": [0.12, 0.1, 0.06]}, spawn=[12.5, 34.5])

if __name__ == "__main__":
    area_inicial(); porao_matadouro(); ossario_carpideiras(); camara_trombeta()

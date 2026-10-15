"""Novo Éden · revisão "Gênesis" (Jefin, 15/10/2026: "revisando Novo Éden, deixando lindo, exuberante, com
referências bíblicas do Éden; melhores mobs; a forma que o spot funciona bem feita").

Gera mata_do_granizo.json no mesmo formato de antes (chamado por gerar.py). O que mudou:
- A Nascente dos Quatro Rios no meio do Viveiro (Gn 2:10): dali saem Pisom (para Havilá, "onde há ouro"), Giom (o lago),
  Hidéquel (para a Frente de Queimada, onde a água seca) e Eufrates (para o Coração). Água limpa, ciano, com vaus e pontes.
- Portão do Oriente (Gn 3:24): arco de pedra, querubins de pedra sem cabeça e a Espada Flamejante na entrada que vem do deserto.
- Árvore da Vida = Árvore-Mãe (catacumba embaixo). Árvore do Conhecimento na Clareira do Conhecimento, com a Serpente (elite).
- Kit "Gênesis" (assets/ambiente/fontes/eden.py): copas verdes, figueiras, salgueiros, samambaias, flores, pedras com musgo.
- Spots: clareira limpa, anel de grupos em célula livre, fogueira + carrinho do Tobias na beira do caminho, marco atrás.
"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import importlib.util
_spec = importlib.util.spec_from_file_location("gerar_mata", os.path.join(AQUI, "gerar.py"))
G = sys.modules.get("__main__") if getattr(sys.modules.get("__main__"), "MOTIVO", None) else None
if G is None:
    G = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(G)
Andar, MOBS, MOTIVO, SPAWN_MATA, PORTA_TORRE, CHEGADA_DESERTO, ARVORE_MAE, PORTA_CATACUMBA = (
    G.Andar, G.MOBS, G.MOTIVO, G.SPAWN_MATA, G.PORTA_TORRE, G.CHEGADA_DESERTO, G.ARVORE_MAE, G.PORTA_CATACUMBA)
CHEGADA_CATACUMBA_DENTRO, FOGO, SEIVA, LUME, ruido, dist_seg = G.CHEGADA_CATACUMBA_DENTRO, G.FOGO, G.SEIVA, G.LUME, G.ruido, G.dist_seg

NASCENTE = [60.0, 71.0]
AMBAR = [1, .62, .22]
PISOS_EDEN = {"e": "relva_eden", "m": "musgo_pedra", "g": "margem_rio", "j": "terra_jardim", "l": "musgo_lume",
              "z": "cinza", "f": "mata_morta", "t": "terra", "w": "margem_rio", "r": "margem_rio", "k": "cascalho"}
G.G.COR_PISO.update({"e": (52, 74, 40), "m": (62, 70, 54), "g": (104, 92, 70), "j": (46, 36, 26), "l": (40, 66, 60),
                   "w": (40, 70, 86), "r": (70, 110, 120), "z": (40, 38, 36), "f": (58, 50, 40), "t": (82, 64, 46), "k": (72, 66, 58)})

ZONAS = [  # id, nome, seguro, nível, piso
    ("portao_oriente", "Portão do Oriente", False, [12, 13], "z"),
    ("viveiro", "O Viveiro", True, None, "m"),
    ("havila", "Havilá", False, [12, 14], "e"),
    ("bordas_do_jardim", "Bordas do Jardim", False, [13, 15], "e"),
    ("lago_de_giom", "Lago de Giom", False, [15, 17], "e"),
    ("frente_de_queimada", "Frente de Queimada", False, [16, 18], "z"),
    ("bosque_dos_enxertos", "Bosque dos Enxertos", False, [18, 21], "e"),
    ("estrada_da_torre", "Estrada da Torre", False, [20, 22], "m"),
    ("clareira_do_conhecimento", "Clareira do Conhecimento", False, [24, 27], "e"),
    ("coracao_do_eden", "Coração do Éden", False, [22, 30], "l"),
]
VIVAS = {1, 2, 3, 4, 6, 8}          # verde do jardim
LUMES = {9}                         # o coração acende em ciano (kit lume antigo + Gênesis)
QUEIMADAS = {0, 5}                  # cinza e brasa: a entrada que vem do deserto e a frente dos Arautos
# x, y, raio, zona, spot (id, nome, nível, [(mob, qtd)], temperamento)
BLOBS = [
    (72, 86, 7, 0, None),
    (60, 71, 9, 1, None),
    (84, 63, 9, 2, ("havila", "Havilá", [12, 14], [("cervo_de_lume", 2), ("corvo_de_brasa", 2)], "neutro")),
    (40, 81, 9, 3, ("toca_dos_javalis", "Toca dos Javalis", [13, 15], [("javali_brasa", 2), ("lobo_de_cinza", 2)], "territorial")),
    (64, 45, 9, 4, ("lago_de_giom", "Lago de Giom", [15, 17], [("enxame_de_fagulhas", 2), ("lobo_de_cinza", 2)], "neutro")),
    (37, 57, 10, 5, ("frente_de_queimada", "Frente de Queimada", [16, 18], [("legionario_desgarrado", 3), ("incendiaria_da_comunhao", 3)], "agressivo")),
    (42, 33, 10, 6, ("bosque_dos_enxertos", "Bosque dos Enxertos", [18, 20], [("enxerto_errado", 2), ("querubim_da_espada", 2)], "neutro")),
    (77, 25, 9, 6, ("clareira_do_ent", "Clareira do Ent", [19, 21], [("enxerto_errado", 2), ("cao_de_brasa", 2)], "neutro")),
    (24, 21, 7, 7, ("estrada_da_torre", "Estrada da Torre", [20, 22], [("querubim_da_espada", 2), ("cao_de_brasa", 2)], "neutro")),
    (14, 11, 6, 7, None),
    (52, 14, 8, 9, ("ruinas_do_coro", "Ruínas do Coro", [22, 25], [("vitral_andante", 2), ("legionario_desgarrado", 2)], "neutro")),
    (88, 42, 8, 9, ("charco_dos_querubins", "Charco dos Querubins", [25, 28], [("querubim_queimado", 2), ("sapo_sacristao", 2)], "neutro")),
    (27, 40, 8, 9, ("acampamento_da_legiao", "Acampamento da Legião", [28, 30], [("centuriao_sem_bandeira", 2), ("bombardeiro_legiao", 2)], "territorial")),
    (57, 31, 8, 8, ("ninho_da_serpente", "Ninho da Serpente", [24, 27], [("serpente_do_eden", 2), ("vitral_andante", 2)], "neutro")),
]
ARESTAS = [(0, 1), (1, 2), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5), (4, 13), (5, 6), (4, 6), (6, 8), (13, 7), (8, 9),
           (6, 13), (13, 10), (2, 11), (7, 11), (6, 12), (5, 12)]
# os quatro rios (Gn 2:10-14): polilinhas a partir da Nascente; largura em tiles
RIOS = {
    "pisom": ([(60, 71), (66, 70.5), (72, 69), (78, 69.5), (84, 70.5), (89, 70.5)], 2.6),      # rodeia Havilá, "onde há ouro"
    "giom": ([(60, 71), (61.5, 64), (64, 58), (66.5, 53), (68.5, 48.5)], 2.8),                   # desce para o lago
    "hidequel": ([(60, 71), (54, 69), (48, 65.5), (42, 61.5), (38, 58.5)], 2.4),             # corre para a Frente e seca lá
    "eufrates": ([(68.5, 48.5), (67.5, 42), (65, 36), (63, 30), (61, 24)], 3.0),       # do lago para o Coração
}
LAGO = (68.5, 48.5, 4.2)
POCO_HAVILA = (89.5, 70.5, 2.2)
POCO_EUFRATES = (61, 24, 2.6)
ARVORE_CONHECIMENTO = [53.5, 36.0]
A_SERPENTE = [55.0, 34.0]


def dist_poli(px, py, pts):
    return min(dist_seg(px, py, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def mata():
    a = Andar("mata_do_granizo", "Novo Éden", 100, 100, "e", None, {})
    W, H = a.w, a.h
    zona_de = [[None]*W for _ in range(H)]
    trilha = [[False]*W for _ in range(H)]
    rio_d = [[99.0]*W for _ in range(H)]
    # ---- chão aberto: blobs + trilhas entre eles
    for y in range(4, H - 4):
        for x in range(4, W - 4):
            best, bz = 1e9, None
            for (bx, by, r, zi, sp) in BLOBS:
                d = math.hypot(x + .5 - bx, y + .5 - by) / (r*(1 + .16*ruido(x, y, bx)))
                if d < best: best, bz = d, zi
            dc = min(dist_seg(x + .5, y + .5, BLOBS[i][:2], BLOBS[j][:2]) for i, j in ARESTAS)
            if best < 1 or dc < 2.6 + .9*ruido(x, y, 3.1):
                a.blk[y][x] = False
                zona_de[y][x] = bz
                piso = ZONAS[bz][4]
                if dc < 1.1 and best > .55: piso = "t"; trilha[y][x] = True
                a.ter[y][x] = piso
    # ---- os quatro rios, o lago e o poço de Havilá
    fundo, raso = set(), set()
    for y in range(H):
        for x in range(W):
            if a.blk[y][x]: continue
            px, py = x + .5, y + .5
            dmin, lw = 99, 0
            for nome, (pts, larg) in RIOS.items():
                d = dist_poli(px, py, pts)
                if nome == "hidequel":   # seca chegando na Frente: estreita e vira lama
                    t = max(0, min(1, (px - 44)/16)); larg = larg*(.5 + .5*t)
                dnasc = math.hypot(px - NASCENTE[0], py - NASCENTE[1])
                if dnasc < 11: larg = larg*(.55 + .45*dnasc/11)        # no Viveiro são calhas rasas entre as tendas
                if d < dmin: dmin, lw = d, larg
            dl = math.hypot(px - LAGO[0], py - LAGO[1]) - LAGO[2]
            dp = min(math.hypot(px - POCO_HAVILA[0], py - POCO_HAVILA[1]) - POCO_HAVILA[2], math.hypot(px - POCO_EUFRATES[0], py - POCO_EUFRATES[1]) - POCO_EUFRATES[2])
            rio_d[y][x] = min(dmin - lw/2, dl, dp)
            r_ = ruido(x*1.5, y*1.5, 9)*.5
            if dl < r_ or dp < r_ or dmin < lw/2 + r_*.4:
                prof = min(dl, dp, dmin - lw/2)
                vau = trilha[y][x] or any(trilha[yy][xx] for xx in range(max(0, x - 1), min(W, x + 2)) for yy in range(max(0, y - 1), min(H, y + 2)))
                if prof < -1.3 and not vau and math.hypot(px - NASCENTE[0], py - NASCENTE[1]) > 11: fundo.add((x, y))
                else: raso.add((x, y))
            elif rio_d[y][x] < 1.4 + r_ and not trilha[y][x]:
                a.ter[y][x] = "g"                      # margem de areia e seixos
    for (x, y) in raso: a.ter[y][x] = "r"
    for (x, y) in fundo: a.ter[y][x] = "w"; a.blk[y][x] = True
    # a Frente de Queimada e o Portão: manchas de mata morta; o Viveiro tem canteiros de terra
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or a.ter[y][x] in "trw": continue
            z = zona_de[y][x]
            if z in QUEIMADAS and ruido(x*1.7, y*1.7, 2) > .4: a.ter[y][x] = "f"
            if z == 1 and ruido(x*2.2, y*2.2, 5) > .58: a.ter[y][x] = "j"
            if z in VIVAS and z != 1 and ruido(x*1.1, y*1.1, 6) > .62: a.ter[y][x] = "m"   # lajes velhas engolidas
            if z == 0 and math.hypot(x - 60, y - 71) < 20: a.ter[y][x] = "e"              # o verde começa logo depois do Portão
    # Portão do Oriente: o verde avança sobre a cinza perto da entrada do jardim (transição irregular)
    for y in range(H):
        for x in range(W):
            if zona_de[y][x] == 0 and not a.blk[y][x] and a.ter[y][x] in "zf" and math.hypot(x - 72, y - 86) > 6.5 + 2*ruido(x, y, 11): a.ter[y][x] = "e"

    rng = a.rng
    spots, descanso = [], []
    area_spot = [(bx, by, r*.78) for (bx, by, r, zi, sp) in BLOBS if sp]
    def em_spot(x, y, folga=0): return any(math.hypot(x - sx, y - sy) < sr + folga for sx, sy, sr in area_spot)
    def agua(x, y): return 0 <= x < W and 0 <= y < H and a.ter[y][x] in "rw"
    def livre3(x, y): return all(a.livre(x + dx, y + dy) and not agua(x + dx, y + dy) and (x + dx, y + dy) not in a.extra_blk for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    def perto_prop(x, y, d): return any(math.dist((x, y), (p["x"], p["y"])) < d for p in a.props if not p.get("chao"))

    # ---- borda: a mata fecha o jardim (copas altas só atrás das clareiras, vegetação baixa na frente)
    alta_viva = ["arvore_eden", "arvore_eden_2", "arvore_eden_3", "arvore_eden", "figueira", "figueira_2", "arvore_eden_2"]
    baixa_viva = ["samambaia", "samambaia_2", "samambaia_3", "moita_florida", "moita_florida_2", "moita_florida_3", "pedra_coberta_3", "folha_larga", "samambaia"]
    alta_lume = ["arvore_lume", "arvore_lume_2", "arvore_eden_3", "palmeira_lume", "arvore_lume"]
    baixa_lume = ["moita_lume", "flor_lume", "flor_lume_2", "samambaia_2", "folha_larga", "moita_lume"]
    alta_morta = ["arvore_morta", "arvore_morta_2", "arvore_morta_grande", "arvore_morta"]
    baixa_morta = ["toco_arvore", "arbusto_seco", "arbusto_seco_2", "mato_seco", "samambaia_3", "toco_arvore"]
    feitas = []
    for y in range(H):
        for x in range(W):
            if not a.blk[y][x] or a.ter[y][x] == "w": continue
            viz = any(0 <= x + dx < W and 0 <= y + dy < H and not a.blk[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
            if not viz: continue
            px, py = x + rng.uniform(.2, .8), y + rng.uniform(.2, .8)
            if any(math.dist((px, py), f) < 1.9 for f in feitas[-80:]): continue
            zv = [zona_de[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                  if 0 <= x + dx < W and 0 <= y + dy < H and zona_de[y + dy][x + dx] is not None]
            z = zv[0] if zv else 3
            # câmera: subir na tela = (x-1, y+1). Copa alta só onde não há chão aberto "abaixo" na tela (na frente)
            frente = any(0 <= x + k + d < W and 0 <= y - k < H and not a.blk[y - k][x + k + d] for k in range(1, 9) for d in (-1, 0, 1))
            if z in QUEIMADAS: kinds = baixa_morta if frente else alta_morta
            elif z in LUMES: kinds = baixa_lume if frente else alta_lume
            else: kinds = baixa_viva if frente else alta_viva
            k = rng.choice(kinds)
            feitas.append((px, py)); a.prop(k, px, py, decor_moldura=True)
            if z in LUMES and rng.random() < .1: a.luzes.append([round(px, 2), round(py, 2)] + LUME + [4])
            if not frente and z in VIVAS and rng.random() < .35:   # segunda fileira atrás, para a mata ficar fechada
                qx, qy = px - rng.uniform(1.2, 2.2), py + rng.uniform(1.2, 2.2)
                if 0 <= int(qx) < W and 0 <= int(qy) < H and a.blk[int(qy)][int(qx)]: a.prop(rng.choice(alta_viva), qx, qy, decor_moldura=True)

    # ---- spots estilo MU, bem feitos: anel de grupos em célula livre, fogueira do Tobias na beira do caminho, marco atrás
    for (bx, by, r, zi, sp) in BLOBS:
        if not sp: continue
        sid, nome, niv, mobs, temp = sp
        spots.append({"id": sid, "nome": nome, "nivel": niv, "pos": [bx, by], "raio": round(r*.8, 1), "respawn_s": 14})
        q = mobs[0][1]; ng = 12 // q
        dv = (NASCENTE[0] - bx, NASCENTE[1] - by); dn = math.hypot(*dv); dv = (dv[0]/dn, dv[1]/dn)
        ang_cam = math.atan2(dv[1], dv[0])       # lado por onde o jogador chega (fogueira fica aí, fora do anel)
        postos = []
        cands = []
        for ia in range(36):
            ang = ang_cam + math.pi + (ia - 18)/36*2*math.pi*.86      # anel aberto do lado da chegada
            for rr in (r*.36, r*.52, r*.66, r*.22, r*.76):
                x, y = bx + math.cos(ang)*rr, by + math.sin(ang)*rr
                cands.append((abs(ia - 18) % 7, x, y))
        cands.sort(key=lambda c: c[0])
        for (_, x, y) in cands:
            if len(postos) >= ng: break
            if not livre3(int(x), int(y)) or perto_prop(x, y, 1.6): continue
            if any(math.dist((x, y), p) < 2.7 for p in postos): continue
            g = len(postos); mob, qtd = mobs[g % len(mobs)]
            s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.2, "qtd": qtd, "nivel": niv[0] + g % (niv[1] - niv[0] + 1),
                  "spot": sid, "temperamento": temp, "respawn_s": 14, "motivo": MOTIVO[mob]}
            if temp == "territorial": s_.update({"ancora": [bx, by], "raio_territorio": 4.0})
            a.spawns.append(s_); postos.append((x, y))
        if len(postos) < ng: print("SPOT INCOMPLETO", sid, len(postos), "de", ng)
        # fogueira + carrinho do Tobias na beira do caminho de chegada (fora do anel de mobs), se ainda não há descanso perto
        fx_, fy_ = bx + dv[0]*r*.82, by + dv[1]*r*.82
        if not any(math.dist((fx_, fy_), d) < 14 for d in descanso):
            for k in range(12):
                qx_, qy_ = fx_ + rng.uniform(-2, 2), fy_ + rng.uniform(-2, 2)
                if livre3(int(qx_), int(qy_)) and not trilha[int(qy_)][int(qx_)] and not perto_prop(qx_, qy_, 2.0):
                    a.prop("fogueira", qx_, qy_, bloqueia=.5, luz=FOGO + [6])
                    a.prop("carrinho_tobias", qx_ + 1.8, qy_ + .8, bloqueia=.5, ponto="descanso"); descanso.append([qx_, qy_]); break
        # marco do spot atrás (subir na tela = (-1, +1)), para o lugar ter cara própria
        marco = {"havila": "arvore_frutos", "toca_dos_javalis": "tronco_caido_eden", "lago_de_giom": "salgueiro",
                 "frente_de_queimada": "arvore_morta_grande", "bosque_dos_enxertos": "figueira_2", "clareira_do_ent": "arvore_eden_2",
                 "estrada_da_torre": "pilar_porcelana", "ruinas_do_coro": "pilar_porcelana", "charco_dos_querubins": "salgueiro_2",
                 "acampamento_da_legiao": "tenda_demonio", "ninho_da_serpente": "pedra_coberta_2"}[sid]
        mx, my = bx - r*.55, by + r*.55
        if a.livre(int(mx), int(my)) and not agua(int(mx), int(my)): a.prop(marco, mx, my, bloqueia=1.0)
    # ---- margens: salgueiros, juncos, nenúfares, pedras
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or trilha[y][x]: continue
            d = rio_d[y][x]; px, py = x + .5, y + .5
            if a.ter[y][x] == "r" and rng.random() < .07 and not em_spot(px, py, -2): a.prop(rng.choice(["nenufares", "nenufares_2"]), px, py, chao=True)
            elif a.ter[y][x] == "g" and rng.random() < .16 and not em_spot(px, py, 0):
                a.prop(rng.choice(["juncos_eden", "juncos_eden", "pedras_rio", "samambaia_3", "cogumelos_eden"]), px, py)
            elif a.ter[y][x] == "g" and rng.random() < .05 and not em_spot(px, py, 2) and not perto_prop(px, py, 5):
                a.prop(rng.choice(["salgueiro", "salgueiro_2"]), px, py, bloqueia=.6)
    # ---- dentro: tapetes de flores, samambaias, pedras, troncos caídos, árvores de fruto, cogumelos
    def solto(kinds, n, bloq, dist, zonas=None, spot_ok=False, chao=False, luz=None, pisos="emgjl"):
        f = t = 0
        while f < n and t < 8000:
            t += 1
            x, y = rng.uniform(5, W - 5), rng.uniform(5, H - 5); ix, iy = int(x), int(y)
            if a.blk[iy][ix] or trilha[iy][ix] or a.ter[iy][ix] not in pisos: continue
            if zonas is not None and zona_de[iy][ix] not in zonas: continue
            if not spot_ok and em_spot(x, y, 1.5): continue
            if bloq and not livre3(ix, iy): continue
            if perto_prop(x, y, dist): continue
            if math.dist((x, y), SPAWN_MATA) < 4 or math.dist((x, y), PORTA_TORRE) < 4 or math.dist((x, y), NASCENTE) < 6: continue
            a.prop(rng.choice(kinds), x, y, bloqueia=bloq, chao=chao); f += 1
            if luz and rng.random() < luz[0]: a.luzes.append([round(x, 2), round(y, 2)] + luz[1:])
    vivas = list(VIVAS)
    solto(["tapete_flores", "tapete_flores_2", "tapete_flores_3", "tapete_flores"], 110, 0, 1.6, zonas=vivas, spot_ok=True, chao=True)
    solto(["samambaia", "samambaia_2", "samambaia_3", "folha_larga"], 90, 0, 2.0, zonas=vivas, spot_ok=True)
    solto(["moita_florida", "moita_florida_2", "moita_florida_3"], 40, .4, 2.6, zonas=vivas)
    solto(["cogumelos_eden", "cogumelos_palidos"], 40, 0, 2.2, zonas=vivas + list(LUMES), spot_ok=True)
    solto(["pedra_coberta", "pedra_coberta_2", "pedra_coberta_3"], 34, .7, 3.5, zonas=vivas + list(LUMES))
    solto(["tronco_caido_eden", "tronco_caido_eden_2"], 16, .8, 5.0, zonas=vivas)
    solto(["arvore_frutos", "arvore_frutos_2"], 22, .7, 6.0, zonas=vivas, luz=[1.0] + AMBAR + [5])
    solto(["flor_lume", "flor_lume_2", "moita_lume", "tapete_flores"], 40, 0, 1.8, zonas=list(LUMES), spot_ok=True)
    solto(["arbusto_seco", "arbusto_seco_2", "mato_seco", "pilha_carvao", "toco_arvore"], 40, 0, 1.8, zonas=list(QUEIMADAS), spot_ok=True, pisos="zft")
    solto(["cratera_cinza", "soldado_morto", "pilha_carvao"], 8, .5, 4.0, zonas=[5], pisos="zf")
    # lanternas de seiva ao longo das trilhas (uma a cada ~9 m), nas zonas vivas
    ult = []
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if not trilha[y][x] or zona_de[y][x] not in VIVAS | LUMES: continue
            if any(math.dist((x, y), u) < 9 for u in ult): continue
            # pé da lanterna fora da trilha, na beira
            for (dx, dy) in [(-1.5, 1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, -1.5)]:
                qx, qy = x + .5 + dx, y + .5 + dy
                if a.livre(int(qx), int(qy)) and not trilha[int(qy)][int(qx)] and not agua(int(qx), int(qy)) and not perto_prop(qx, qy, 1.5):
                    a.prop("lanterna_eden", qx, qy, bloqueia=.2, luz=AMBAR + [5]); ult.append((x, y)); break

    # ---- pontes de tábuas onde a trilha cruza um rio (o vau fica raso, a ponte é o enfeite que mostra o caminho)
    pontes = []
    for (i, j) in ARESTAS:
        (x0, y0), (x1, y1) = BLOBS[i][:2], BLOBS[j][:2]
        n = int(math.hypot(x1 - x0, y1 - y0))
        for k in range(n):
            t = k/n; x, y = x0 + (x1 - x0)*t, y0 + (y1 - y0)*t
            if a.ter[int(y)][int(x)] == "r" and not any(math.dist((x, y), p) < 6 for p in pontes):
                pontes.append((x, y)); a.prop("ponte_tabuas", x, y, chao=True); break

    # ---- Portão do Oriente (entrada que vem do deserto)
    a.portal(SPAWN_MATA[0] + 2, SPAWN_MATA[1] + 3, "area_inicial", CHEGADA_DESERTO, "Trilha para o Deserto de Absinto", visual="escada_subida")
    a.prop("arco_eden", 66.5, 79.0, bloqueia=0, marco="portao_oriente")
    for (x, y) in [(64.5, 79.0), (68.5, 79.0)]: a.extra_blk.add((int(x), int(y)))
    a.prop("pilar_portao", 70.5, 82.5, bloqueia=.8); a.prop("pilar_portao_2", 63.0, 75.5, bloqueia=.8)
    a.prop("espada_flamejante", 68.5, 76.5, bloqueia=.9, luz=FOGO + [8], marco="espada_flamejante")
    a.prop("placa_versiculo", 70.0, 88.0, bloqueia=.3, texto="E plantou o Senhor Deus um jardim no Éden, do lado oriental. Gn 2:8")
    a.prop("trilho_retorcido", 76.5, 84.5, bloqueia=.4); a.prop("poste_telegrafo", 75.5, 81.0, bloqueia=.3)
    a.prop("estatua_anjo_quebrada", 74.0, 89.5, bloqueia=.8)
    # ---- o Viveiro: a Nascente dos Quatro Rios e a vila da Enxertia
    vx, vy = NASCENTE
    a.prop("fonte_quatro_rios", vx, vy, bloqueia=0, luz=LUME + [9], marco="nascente")
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if math.hypot(dx, dy) < 2.6: a.extra_blk.add((int(vx) + dx, int(vy) + dy))
    a.prop("fogueira", vx + 5.5, vy + 3.0, bloqueia=.5, luz=FOGO + [7])
    a.prop("carrinho_tobias", vx + 7.5, vy + 3.8, bloqueia=.5, ponto="descanso"); descanso.append([vx + 5.5, vy + 3.0])
    a.prop("tenda_vigilia", vx - 6.0, vy - 3.5, bloqueia=1.4); a.prop("tenda_vigilia", vx + 2.0, vy - 6.5, bloqueia=1.4)
    a.prop("trelica_videira", vx - 3.0, vy - 6.5, bloqueia=.8); a.prop("trelica_videira", vx + 6.5, vy - 2.0, bloqueia=.8)
    a.prop("colmeia", vx - 7.5, vy + 1.0, bloqueia=.4); a.prop("colmeia", vx - 6.5, vy + 2.5, bloqueia=.4)
    a.prop("caixas", vx - 5.0, vy + 4.5, bloqueia=.5); a.prop("barris", vx - 3.5, vy + 5.5, bloqueia=.5)
    a.prop("bancada_ferreiro", vx + 4.5, vy + 6.0, bloqueia=.6); a.prop("tanque_latao", vx + 7.5, vy - 5.0, bloqueia=1.0)
    a.prop("caixa_dagua_sucata", vx - 8.0, vy - 5.5, bloqueia=1.2)
    for (dx, dy) in [(-3.5, -3.5), (3.5, -3.5), (3.5, 3.5), (-3.5, 3.5)]: a.prop("lanterna_eden", vx + dx, vy + dy, bloqueia=.2, luz=AMBAR + [5])
    for (dx, dy) in [(-1.0, -7.5), (0.5, -7.8), (4.0, 7.0), (-4.5, 6.5)]: a.prop("campanula", vx + dx, vy + dy, bloqueia=.3, luz=LUME + [3])
    for (dx, dy) in [(-7.0, -1.5), (6.0, 6.0), (1.5, 7.5)]: a.prop("placa_versiculo", vx + dx, vy + dy, bloqueia=.3)
    a.prop("figueira", vx - 9.5, vy + 4.0, bloqueia=1.2); a.prop("arvore_frutos", vx + 9.0, vy + 1.0, bloqueia=.7, luz=AMBAR + [5])
    # ---- a Árvore da Vida (Árvore-Mãe, o primeiro enxerto de Simão) e a Catacumba das Raízes
    a.prop("arvore_mae", ARVORE_MAE[0], ARVORE_MAE[1], bloqueia=1.4, marco="arvore_mae", luz=LUME + [9])
    a.prop("portal_dungeon_lume", PORTA_CATACUMBA[0], PORTA_CATACUMBA[1] + .4, bloqueia=0, luz=LUME + [6])
    a.portal(PORTA_CATACUMBA[0], PORTA_CATACUMBA[1], "catacumba_das_raizes", CHEGADA_CATACUMBA_DENTRO,
             "Catacumba das Raízes · dungeon (nv 18-22)", visual="portal_dungeon_lume")
    a.prop("placa_versiculo", ARVORE_MAE[0] + 2.5, ARVORE_MAE[1] - 2.5, bloqueia=.3, texto="A árvore da vida no meio do jardim. Gn 2:9")
    # ---- Havilá: "onde há ouro; o bdélio e a pedra de ônix" (pomar dourado e pedras negras em volta do poço do Pisom)
    hx, hy = BLOBS[2][:2]
    for (dx, dy) in [(-5.5, 6.0), (2.5, 7.5), (-7.5, 1.5)]: a.prop(rng.choice(["arvore_frutos", "arvore_frutos_2"]), hx + dx, hy + dy, bloqueia=.7, luz=AMBAR + [5])
    for (dx, dy) in [(3.0, 5.8), (5.5, 4.0), (1.0, 6.8)]: a.prop("pedras_rio", hx + dx, hy + dy)
    a.prop("placa_versiculo", hx - 6.5, hy - 5.0, bloqueia=.3, texto="O ouro dessa terra é bom; ali há o bdélio e a pedra de ônix. Gn 2:12")
    # ---- Lago de Giom: a margem de descanso
    lx, ly = LAGO[:2]
    a.prop("fogueira", lx + 8.0, ly - 5.0, bloqueia=.5, luz=FOGO + [6])
    a.prop("carrinho_tobias", lx + 9.8, ly - 4.2, bloqueia=.5, ponto="descanso"); descanso.append([lx + 8.0, ly - 5.0])
    a.prop("salgueiro", lx - 6.5, ly + 4.5, bloqueia=.6); a.prop("salgueiro_2", lx + 4.0, ly + 6.5, bloqueia=.6)
    # ---- Frente de Queimada: o acampamento dos Arautos, onde o Hidéquel seca
    fx, fy = BLOBS[5][:2]
    a.prop("tenda_demonio", fx - 6.5, fy - 3.0, bloqueia=1.4); a.prop("estandarte_rasgado", fx - 4.5, fy + 5.5, bloqueia=.3)
    a.prop("estandarte_rasgado", fx + 6.0, fy - 4.0, bloqueia=.3)
    for (dx, dy) in [(-7, 2), (6.5, 3.5), (0, -7)]: a.prop("tonel_fogo", fx + dx, fy + dy, bloqueia=.4, luz=FOGO + [5])
    # ---- Estrada da Torre: postes, descanso
    for i in range(5):
        t = i/4; a.prop("poste_telegrafo", 33 + (18 - 33)*t + 1.6, 30 + (15 - 30)*t - 1.2, bloqueia=.3)
    ex, ey = BLOBS[8][:2]
    a.prop("fogueira", ex + 5.0, ey + 4.5, bloqueia=.5, luz=FOGO + [6])
    a.prop("carrinho_tobias", ex + 6.8, ey + 5.4, bloqueia=.5, ponto="descanso"); descanso.append([ex + 5.0, ey + 4.5])
    # ---- Clareira do Conhecimento: a árvore proibida e a Serpente
    a.prop("arvore_conhecimento", ARVORE_CONHECIMENTO[0], ARVORE_CONHECIMENTO[1], bloqueia=1.6, marco="conhecimento", luz=[.35, 1.0, .25, 7])
    # ---- Coração do Éden (22-30): ruínas do Coro, charco, acampamento da Legião
    rx, ry = BLOBS[10][:2]
    a.prop("pilar_porcelana", rx - 4.5, ry - 3.0, bloqueia=.7); a.prop("anjo_porcelana_caido", rx + 4.0, ry + 3.5, bloqueia=.8)
    a.prop("fogueira", rx - 6.0, ry + 4.5, bloqueia=.5, luz=FOGO + [6])
    a.prop("carrinho_tobias", rx - 4.2, ry + 5.4, bloqueia=.5, ponto="descanso"); descanso.append([rx - 6.0, ry + 4.5])
    qx, qy = BLOBS[11][:2]
    for k in range(8):
        ang = k/8*2*math.pi; a.prop("juncos_eden" if k % 2 else "pedras_rio", qx + math.cos(ang)*2.6, qy + math.sin(ang)*2.6)
    cxl, cyl_ = BLOBS[12][:2]
    a.prop("tenda_demonio", cxl - 5.0, cyl_ - 4.0, bloqueia=1.4); a.prop("estandarte_rasgado", cxl + 5.0, cyl_ - 3.5, bloqueia=.3)
    a.prop("tonel_fogo", cxl - 5.5, cyl_ + 4.0, bloqueia=.4, luz=FOGO + [5])
    # ---- A Torre (marco e entrada da dungeon, trancada)
    a.prop("torre_vigia", 11.5, 9.0, bloqueia=2.6, luz=FOGO + [9], marco="a_torre")
    a.prop("portao_ferro", PORTA_TORRE[0] - 1.0, PORTA_TORRE[1] - 1.5, bloqueia=.4)
    a.prop("braseiro_ferro", PORTA_TORRE[0] + 2.0, PORTA_TORRE[1] - 2.0, bloqueia=.4, luz=FOGO + [6])
    a.prop("estandarte_rasgado", PORTA_TORRE[0] - 3.0, PORTA_TORRE[1] + 1.0, bloqueia=.3)
    a.portal(PORTA_TORRE[0], PORTA_TORRE[1], "torre_1", [11.5, 25.5], "A Torre · elevador de carga", visual="portal_dungeon",
             requer_flag="torre_aberta", texto_trancado="A porta da Torre está acorrentada por dentro. Ainda não.")

    # ---- fora dos spots: poucos pares neutros nos caminhos, com espaço para respirar
    for (i, j, mob, niv) in [(1, 2, "cervo_de_lume", 12), (1, 3, "corvo_de_brasa", 12), (2, 4, "javali_brasa", 14), (4, 13, "enxame_de_fagulhas", 16),
                             (6, 8, "querubim_da_espada", 19), (13, 10, "serpente_do_eden", 24), (4, 6, "cervo_de_lume", 14)]:
        (x0, y0), (x1, y1) = BLOBS[i][:2], BLOBS[j][:2]
        ok = False
        for t in (.5, .38, .62, .3, .7, .44, .56):
            for (ox, oy) in [(1.5, -1.5), (0, 0), (-1.5, 1.5), (2.5, 0), (0, 2.5)]:
                x, y = x0 + (x1 - x0)*t + ox, y0 + (y1 - y0)*t + oy
                if livre3(int(x), int(y)): ok = True; break
            if ok: break
        if not ok: continue
        a.spawns.append({"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.0, "qtd": 2, "nivel": niv,
                         "temperamento": "territorial" if mob == "javali_brasa" else "neutro", "respawn_s": 30, "motivo": MOTIVO[mob]})
    # ---- elites: o Ent-de-Cinza (na sua árvore) e A Serpente (enrolada na Árvore do Conhecimento)
    a.prop("arvore_eden_2", 82.5, 20.0, bloqueia=1.0)
    a.spawns.append({"mob": "ent_de_cinza", "pos": [81.0, 22.0], "raio": .5, "qtd": 1, "nivel": 22, "elite": True, "temperamento": "neutro",
                     "respawn_s": 300, "ancora": [82.5, 20.0], "motivo": MOTIVO["ent_de_cinza"]})
    a.spawns.append({"mob": "a_serpente", "pos": A_SERPENTE, "raio": .5, "qtd": 1, "nivel": 27, "elite": True, "temperamento": "neutro",
                     "respawn_s": 300, "ancora": ARVORE_CONHECIMENTO, "motivo": MOTIVO["a_serpente"]})
    # ---- baús
    for (x, y, b, vis, idm) in [(46.5, 88.0, "caixote_podre", "bau_comum", "mata_toca"), (29.5, 52.0, "bau_de_ferro", "bau_raro", "mata_frente"),
                                (35.0, 27.5, "caixote_podre", "bau_comum", "mata_bosque"), (86.0, 27.0, "bau_de_ferro", "bau_raro", "mata_ent"),
                                (88.5, 60.0, "caixote_podre", "bau_comum", "eden_havila"), (50.0, 36.5, "bau_de_ferro", "bau_raro", "eden_conhecimento")]:
        if a.livre(int(x), int(y)) and not agua(int(x), int(y)): a.objetos.append({"kind": "bau", "pos": [x, y], "bau": b, "visual": vis, "id_mapa": idm})

    # ---- passada final: todo grupo em célula livre (3x3) e longe de prop que bloqueia; senão desloca até 3 tiles
    for sp in a.spawns:
        x, y = sp["pos"]
        if livre3(int(x), int(y)) and not perto_prop(x, y, 1.3): continue
        melhor = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                qx, qy = x + dx, y + dy
                if livre3(int(qx), int(qy)) and not perto_prop(qx, qy, 1.3) and (melhor is None or math.hypot(dx, dy) < melhor[0]): melhor = (math.hypot(dx, dy), qx, qy)
        if melhor: sp["pos"] = [round(melhor[1], 1), round(melhor[2], 1)]
        else: print("SPAWN SEM LUGAR", sp["mob"], sp["pos"])
    m = a.exportar(spawn=SPAWN_MATA, ceu={"escuro": 0.6, "cor": [0.62, 0.78, 0.68], "neblina": [0.06, 0.12, 0.1]})
    m["pisos"] = dict(m["pisos"], **PISOS_EDEN)
    # água limpa do Éden (o shader do chão usa estas cores no lugar das do Rio Amargo quando o mapa traz `agua`)
    m["agua"] = {"fundo": [0.02, 0.09, 0.13], "raso": [0.1, 0.3, 0.32], "reflexo": [0.3, 0.5, 0.52], "brilho": [0.5, 0.9, 1.0],
                 "lume": [0.0, 0.05, 0.07], "espuma": [0.55, 0.7, 0.72]}
    # correnteza: cada rio vai e volta pelo mesmo traçado (a volta nunca ganha o desempate), tudo numa polilinha só
    centro = []
    for nome in ("pisom", "giom", "hidequel", "eufrates"):
        pts = [list(map(float, p)) for p in RIOS[nome][0]]
        centro += pts + pts[::-1]
    m["rio"] = {"id": "quatro_rios", "nome": "Os Quatro Rios", "nota": "Gn 2:10: um rio saía do Éden para regar o jardim e dali se dividia em quatro",
                "centro": centro, "ramos": {k: v[0] for k, v in RIOS.items()}, "nascente": NASCENTE}
    letras = "ABCDEFGHIJ"
    m["zona_grade"] = ["".join("." if zona_de[y][x] is None else letras[zona_de[y][x]] for x in range(W)) for y in range(H)]
    m["zonas"] = [{"id": i, "nome": n, "seguro": s, "nivel": nv, "musica": "musica/sao_lazaro",
                   "ambiente": "ambiente/noite_vento", "faccao": None, "neblina": .32 if i != "viveiro" else .2} for (i, n, s, nv, _) in ZONAS]
    m["exterior"] = True
    m["spots"] = spots
    m["descanso"] = descanso
    m["salas"] = [{"nome": ("A Torre" if (bx, by) == (14, 11) else ZONAS[zi][1]) if not sp else sp[1], "ret": [bx - 3, by - 2, bx + 3, by + 2]} for (bx, by, r, zi, sp) in BLOBS]
    m["lugares"] = [{"id": "nascente", "nome": "A Nascente dos Quatro Rios", "pos": NASCENTE}, {"id": "portao_oriente", "nome": "Portão do Oriente", "pos": [66.5, 79.0]},
                    {"id": "arvore_da_vida", "nome": "Árvore da Vida", "pos": ARVORE_MAE}, {"id": "arvore_do_conhecimento", "nome": "Árvore do Conhecimento", "pos": ARVORE_CONHECIMENTO},
                    {"id": "havila", "nome": "Havilá", "pos": list(POCO_HAVILA[:2])}, {"id": "lago_de_giom", "nome": "Lago de Giom", "pos": list(LAGO[:2])}]
    json.dump(m, open(f"{AQUI}/mata_do_granizo.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return m

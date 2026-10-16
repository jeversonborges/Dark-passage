"""O Labirinto de Hawara (dungeon nível 50 a 54, 3 andares, 3 chefes) e O Coração Endurecido (raid nível 60, 6 salões).
Chamado por gerar.py (`python3 gerar.py hawara` / `raid`). Mesmo formato dos andares da cripta (classe Andar).

Princípios (dungeon e raid modernas): cada andar é uma sequência legível (entrada, 3 ou 4 grupos de lixo com um papel
cada, um evento ou atalho, a arena), sem labirinto vazio; grupos de 2 a 3, todos agressivos (é tumba); a arena guarda no
JSON do chefe os objetos da mecânica (`arena.ilhas`, `arena.pedestais`, ... lidos por chefe_egito.gd); baú do chefe e
escada depois da arena, trancada até `venceu_<chefe>`; um caminho lateral opcional com baú e registro de lore.
Tela: +X desce para a direita, +Y sobe para a direita; "frente" (perto da câmera) = +x -y.
"""
import json, math, os
import gerar as G            # já carregado por egito/gerar.py: é o gerar da cripta (classe Andar)
from dados_egito import TODOS_MOBS

Andar, porta_da_arena = G.Andar, G.porta_da_arena
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = G.AQUI
FOGO = [1, 0.5, 0.2]; OLEO = [1, 0.72, 0.38]; TURQ = [0.25, 0.85, 0.85]; SANGUE = [1, 0.25, 0.12]; OURO = [1, 0.8, 0.4]; NOITE = [0.35, 0.45, 0.8]
PISOS_D = {"x": "laje_hawara", "o": "laje_duat", "j": "laje_tura", "s": "laje_ocre", "w": "lodo_negro", "r": "margem_nilo", "n": "entulho",
           "a": "areia_calcario", "q": "quartzito", "b": "convés_barca"}
G.COR_PISO.update({"x": (110, 98, 80), "o": (40, 44, 52), "j": (150, 138, 112), "s": (150, 100, 60), "q": (150, 110, 90), "b": (96, 70, 44), "w": (40, 58, 56), "r": (70, 92, 84)})
AGUA_HAWARA = {"fundo": [0.02, 0.05, 0.04], "raso": [0.12, 0.18, 0.13], "reflexo": [0.5, 0.42, 0.3], "brilho": [0.9, 0.7, 0.45], "lume": [0.05, 0.2, 0.2], "espuma": [0.5, 0.46, 0.38]}
AGUA_DUAT = {"fundo": [0.0, 0.01, 0.03], "raso": [0.03, 0.05, 0.1], "reflexo": [0.3, 0.35, 0.55], "brilho": [0.6, 0.7, 1.0], "lume": [0.1, 0.2, 0.4], "espuma": [0.3, 0.32, 0.4]}
CEU_TUMBA = {"escuro": 0.84, "cor": [0.6, 0.48, 0.36], "neblina": [0.12, 0.09, 0.06]}
CEU_DUAT = {"escuro": 0.9, "cor": [0.4, 0.45, 0.65], "neblina": [0.04, 0.05, 0.1]}


def chegada_egito(px, py):
    """Ponto livre mais perto (no mapa aberto já gerado) para a volta da dungeon."""
    try:
        g = json.load(open(os.path.join(SAIDA, "egito.json")))["grade"]
    except Exception:
        return [px, py]
    best = None
    for y in range(int(py) - 6, int(py) + 7):
        for x in range(int(px) - 6, int(px) + 7):
            if 0 <= y < len(g) and 0 <= x < len(g[0]) and all(g[y + dy][x + dx] == "." for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                                                  if 0 <= y + dy < len(g) and 0 <= x + dx < len(g[0])):
                d = math.dist((x + .5, y + .5), (px, py))
                if d > 1.5 and (best is None or d < best[0]): best = (d, x + .5, y + .5)
    return [best[1], best[2]] if best else [px, py]


def grupo(a, mob, x, y, qtd, nivel, raio=1.5, papel=None):
    s = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": raio, "qtd": qtd, "nivel": nivel, "temperamento": "agressivo",
         "motivo": TODOS_MOBS[mob]["motivo"]}
    if papel: s["papel"] = papel
    a.spawns.append(s)


def anel(cx, cy, r, n, a0=0.0):
    return [[round(cx + r*math.cos(a0 + i*math.tau/n), 1), round(cy + r*math.sin(a0 + i*math.tau/n), 1)] for i in range(n)]


def arena_redonda(a, cx, cy, r, piso=None, cantos=True):
    a.sala(int(cx - r), int(cy - r), int(cx + r), int(cy + r), piso)
    if cantos:
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if math.hypot(x + .5 - cx, y + .5 - cy) > r + .9: a.fechar(x, y)


def fim(a, chefe, spawn, ceu=CEU_TUMBA, agua=None):
    a.paredes()
    m = a.exportar(chefe=chefe, ceu=ceu, spawn=spawn)
    m["pisos"] = PISOS_D
    if agua: m["agua"] = agua
    json.dump(m, open(f"{SAIDA}/{a.id}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return m


def zona(id_, nome, nivel, amb, mus="musica/egito_tumba"):
    return {"id": id_, "nome": nome, "seguro": False, "nivel": nivel, "musica": mus, "ambiente": amb}


# ====================================================================================== HAWARA 1
def hawara_1():
    """Galerias Alagadas. A cheia invadiu o Labirinto pelo canal do Bahr Yussef: as galerias de baixo viraram o
    santuário de Petsuchos. Fluxo: escada -> canal dos crocodilos (aprende a fugir de investida em corredor) ->
    sala de embalsamar (sacerdote cura: interromper) -> ponte de pedra -> arena alagada com 4 ilhas."""
    a = Andar("hawara_1", "Labirinto de Hawara · Galerias Alagadas", 84, 70, "x", "parede_hawara",
              zona("hawara_1", "Galerias Alagadas", [50, 51], "ambiente/egito_hawara_agua"))
    a.sala(6, 48, 15, 58, nome="Escada do Faium")
    a.corredor(16, 51, 20, 54)
    a.sala(21, 45, 46, 59, nome="Canal dos Crocodilos")
    a.pisar(21, 50, 46, 53, "r"); a.pisar(24, 51, 43, 52, "w")
    a.corredor(30, 38, 33, 44)
    a.sala(24, 26, 39, 37, nome="Sala de Embalsamar")
    a.corredor(14, 30, 23, 33)
    a.sala(6, 26, 13, 36, nome="Depósito de Múmias de Crocodilo")
    a.corredor(47, 50, 52, 53, "q")
    a.sala(53, 44, 66, 58, nome="Átrio de Sobek")
    a.corredor(58, 39, 61, 43, "q")
    cx, cy, r = 60.5, 24.5, 11.0
    arena_redonda(a, cx, cy, r, "r")
    a.salas.append(("Santuário de Petsuchos", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    a.corredor(59, 9, 62, 12, "x")
    a.sala(56, 4, 65, 8, nome="Escada do Fundo")
    # ---- escada do Faium (chegada): pé da escada seco, lamparinas, o rastro molhado
    a.portal(8.5, 55.5, "egito", chegada_egito(60.5, 32.5), "Subir para o Faium", visual="escada_subida")
    a.prop("lamparina_parede", 7.5, 50.0, luz=OLEO + [5]); a.prop("lamparina_parede", 13.5, 57.5, luz=OLEO + [5])
    a.prop("jarros", 14.0, 49.5, bloqueia=.4); a.prop("entulho", 7.5, 57.5, bloqueia=.5)
    a.prop("estela_heródoto", 12.0, 53.0, bloqueia=.4)
    a.objetos.append({"kind": "interativo", "obj": "estela_herodoto", "pos": [11.5, 53.0], "i": 0})
    a.prop("poca_agua", 15.5, 52.5, chao=True); a.prop("rastro_molhado", 18.0, 52.5, chao=True)
    # ---- canal: a água funda no meio, passarelas dos dois lados; crocodilos nas duas margens
    a.ao_longo("coluna_papiro_hawara", 23.5, 46.5, 44.5, 46.5, 5, bloqueia=.6)
    a.ao_longo("coluna_papiro_hawara", 23.5, 57.5, 44.5, 57.5, 5, bloqueia=.6)
    for x in (26, 34, 42): a.luzes.append([x, 52, *TURQ, 4])
    a.prop("estatua_sobek", 45.0, 55.5, bloqueia=.8); a.prop("estatua_sobek", 45.0, 47.5, bloqueia=.8)
    a.espalhar(["juncos_nilo", "lotus_azul", "poca_agua"], 10, (21, 45, 46, 59), chao=True)
    grupo(a, "crocodilo_sagrado", 27.0, 55.5, 2, 50, papel="investida no corredor")
    grupo(a, "crocodilo_sagrado", 38.0, 48.0, 2, 50)
    grupo(a, "escaravelho_do_labirinto", 43.0, 55.0, 3, 50, papel="enxame no chão")
    # ---- sala de embalsamar crocodilos: mesas, natrão, os sacerdotes de Sobek
    for x, y in [(27.5, 29.5), (31.5, 29.5), (35.5, 29.5), (27.5, 33.5), (35.5, 33.5)]: a.prop("mesa_embalsamar", x, y, bloqueia=.7)
    a.prop("bacia_natrao", 31.5, 34.0, bloqueia=.7); a.prop("braseiro_bronze", 25.5, 36.0, bloqueia=.4, luz=FOGO + [6])
    a.prop("braseiro_bronze", 38.0, 27.5, bloqueia=.4, luz=FOGO + [6]); a.prop("vasos_canopicos", 38.0, 35.5, bloqueia=.5)
    a.espalhar(["linho_no_chao", "poca_natrao"], 6, (24, 26, 39, 37))
    grupo(a, "sacerdote_de_sobek", 31.5, 31.5, 2, 51, papel="cura: interromper")
    grupo(a, "guarda_do_labirinto", 28.5, 35.5, 1, 51)
    # ---- depósito (opcional): pilhas de crocodilos mumificados, baú e registro
    for y in (27.5, 30.5, 33.5): a.prop("mumias_crocodilo", 7.5, y, bloqueia=.7)
    a.prop("mumias_crocodilo", 12.0, 35.0, bloqueia=.6); a.prop("lamparina_parede", 12.5, 27.0, luz=OLEO + [4])
    a.objetos.append({"kind": "bau", "pos": [10.5, 31.0], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "hw_deposito"})
    a.objetos.append({"kind": "interativo", "obj": "oferenda_dos_sacerdotes", "pos": [10.0, 34.5], "i": 0})
    grupo(a, "escaravelho_do_labirinto", 11.0, 28.5, 2, 51)
    # ---- átrio de Sobek: antes da arena; a ponte de quartzito e o ouro que os sacerdotes deixavam
    a.prop("estatua_sobek", 55.0, 56.5, bloqueia=.9, luz=TURQ + [3]); a.prop("estatua_sobek", 65.0, 56.5, bloqueia=.9, luz=TURQ + [3])
    a.prop("mesa_oferenda", 60.0, 55.5, bloqueia=.6); a.prop("braseiro_bronze", 54.5, 45.5, bloqueia=.4, luz=FOGO + [6])
    a.prop("braseiro_bronze", 65.5, 45.5, bloqueia=.4, luz=FOGO + [6])
    a.espalhar(["entulho", "jarros"], 4, (53, 44, 66, 58), chao=False, bloq=.4, dist=2.5)
    grupo(a, "guarda_do_labirinto", 58.0, 50.0, 2, 51, papel="porteiros")
    grupo(a, "crocodilo_sagrado", 63.0, 47.0, 1, 51)
    # ---- arena: piso de água rasa, 4 ilhas de pedra, 4 mesas de oferenda na borda
    ilhas = anel(cx, cy, 6.0, 4, math.pi/4)
    for (ix, iy) in ilhas:
        a.pisar(int(ix - 1.6), int(iy - 1.6), int(ix + 1.6), int(iy + 1.6), "x"); a.prop("ilha_pedra", ix, iy, chao=True)
    oferendas = anel(cx, cy, 9.2, 4, 0.0)
    for (ox, oy) in oferendas: a.prop("mesa_oferenda", ox, oy, bloqueia=.5)
    for p in anel(cx, cy, 10.2, 8, math.pi/8): a.prop("coluna_papiro_hawara", p[0], p[1], bloqueia=.6)
    for p in anel(cx, cy, 8.0, 6, .3): a.luzes.append(p + TURQ + [4])
    a.luzes.append([cx, cy, *OURO, 7])
    a.prop("trono_de_sobek", cx - 8.5, cy + 6.0, bloqueia=1.0)
    porta = porta_da_arena(a, cx, cy, r)
    a.objetos.append({"kind": "bau", "pos": [60.5, 6.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": "petsuchos", "id_mapa": "bau_petsuchos"})
    a.portal(62.5, 6.0, "hawara_2", [10.5, 38.5], "Descer aos Doze Pátios", requer_flag="venceu_petsuchos",
             texto_trancado="A água tapa a escada. Alguma coisa grande dorme embaixo dela.")
    a.prop("lamparina_parede", 57.0, 7.5, luz=OLEO + [5])
    return fim(a, {"id": "petsuchos", "pos": [cx, cy], "arena": {"centro": [cx, cy], "raio": r, "ilhas": ilhas, "raio_ilha": 1.8, "oferendas": oferendas},
                   "porta": porta}, [10.5, 53.5], agua=AGUA_HAWARA)


# ====================================================================================== HAWARA 2
def hawara_2():
    """Os Doze Pátios (Heródoto II.148: doze pátios cobertos, seis para o norte e seis para o sul, portas de frente
    umas para as outras, 1500 salas em cima e 1500 embaixo). Duas fileiras de seis pátios ligadas por um salão
    longo; só uma porta de cada pátio leva adiante (a pista é o glifo pintado na verga). Três pátios têm desvio
    com baú/registro. A arena da Esfinge tem os 6 pedestais de glifo."""
    a = Andar("hawara_2", "Labirinto de Hawara · Os Doze Pátios", 96, 64, "x", "parede_hawara",
              zona("hawara_2", "Os Doze Pátios", [52, 53], "ambiente/egito_hawara_patios"))
    a.sala(4, 34, 13, 43, nome="Pé da escada")
    a.corredor(14, 37, 17, 40)
    a.sala(18, 30, 76, 34, "j", nome="Salão Longo")
    a.corredor(14, 31, 17, 33)
    norte, sul = [], []
    for i in range(6):
        x0 = 18 + i*10
        a.sala(x0, 36, x0 + 7, 43, nome=f"Pátio Norte {i + 1}"); norte.append((x0 + 3.5, 39.5))
        a.sala(x0, 21, x0 + 7, 28, nome=f"Pátio Sul {i + 1}"); sul.append((x0 + 3.5, 24.5))
        a.corredor(x0 + 3, 35, x0 + 4, 35); a.corredor(x0 + 3, 29, x0 + 4, 29)
        for (px, py) in ((x0 + .5, 36.5), (x0 + 7.5, 36.5), (x0 + .5, 43.5), (x0 + 7.5, 43.5), (x0 + .5, 21.5), (x0 + 7.5, 21.5), (x0 + .5, 28.5), (x0 + 7.5, 28.5)):
            a.prop("coluna_hawara", px, py, bloqueia=.5)
        a.prop("verga_glifo", x0 + 3.5, 35.5, glifo=["junco", "olho", "escaravelho", "ankh", "pena", "djed"][i])
    # pátios fechados no meio do salão: o caminho certo serpenteia (fecha trechos do salão para obrigar a passar por pátios)
    for (x0, x1) in ((37, 38), (57, 58)):
        for y in range(30, 35): a.fechar(x0, y); a.fechar(x1, y)
    a.corredor(35, 40, 40, 41); a.corredor(55, 22, 60, 23)   # passagens pelos pátios 2-3 norte e 4-5 sul
    a.corredor(77, 31, 80, 33)
    cx, cy, r = 87.0, 32.0, 8.5
    a.sala(int(cx - r), int(cy - r), int(cx + r), int(cy + r), "j")
    a.salas.append(("Pátio da Esfinge", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    a.corredor(86, 41, 88, 46, "x"); a.sala(83, 47, 92, 54, nome="Escada da Câmara")
    # ---- pé da escada
    a.portal(6.5, 40.5, "hawara_1", [60.5, 9.5], "Subir às Galerias Alagadas", visual="escada_subida")
    a.prop("lamparina_parede", 5.5, 35.0, luz=OLEO + [5]); a.prop("estela", 12.5, 42.5, bloqueia=.4)
    a.objetos.append({"kind": "interativo", "obj": "estela_dos_doze", "pos": [11.5, 41.5], "i": 0})
    # ---- salão longo: teto de pedra única, lamparinas turquesa, relevos de Amenemés
    for x in range(20, 76, 4): a.prop("lamparina_parede", x + .5, 34.4, luz=TURQ + [3]) if x % 8 == 0 else a.prop("relevo_amenemes", x + .5, 34.4)
    # ---- pátios: cada um com seu motivo e no máximo um grupo
    motivos = ["altar_doze", "estatua_amenemes", "mesa_oferenda", "estatua_sobek", "altar_doze", "estatua_amenemes"]
    for i, ((nx, ny), (sx, sy)) in enumerate(zip(norte, sul)):
        a.prop(motivos[i], nx, ny + 2.5, bloqueia=.8); a.prop(motivos[5 - i], sx, sy - 2.5, bloqueia=.8)
        a.luzes += [[nx, ny, *OLEO, 4], [sx, sy, *OLEO, 4]]
    grupo(a, "esfinge_do_patio", *norte[0], 1, 52, papel="investida: sair da linha")
    grupo(a, "guarda_do_labirinto", *sul[1], 2, 52)
    grupo(a, "escaravelho_do_labirinto", *norte[2], 3, 52)
    grupo(a, "sacerdote_de_sobek", *sul[3], 2, 53, papel="cura: interromper")
    grupo(a, "esfinge_do_patio", *norte[4], 2, 53, papel="duas investidas cruzadas")
    grupo(a, "guarda_do_labirinto", *sul[5], 2, 53)
    grupo(a, "naja_do_labirinto", 47.5, 32.0, 2, 53, papel="atiradores no salão")
    # desvios opcionais: pátio sul 1 (baú), pátio norte 6 (registro de Heródoto), pátio sul 4 (atalho de volta)
    a.objetos.append({"kind": "bau", "pos": [sul[0][0], sul[0][1] - 1.0], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "hw_patio_sul"})
    a.objetos.append({"kind": "interativo", "obj": "rolo_de_herodoto", "pos": [norte[5][0] - 1.5, norte[5][1]], "i": 0})
    # ---- arena: pátio quadrado, 6 pedestais de glifo num anel, a Esfinge sentada atrás
    glifos = ["escaravelho", "olho", "ankh", "pena", "djed", "junco"]
    pedestais = []
    for i, p in enumerate(anel(cx, cy, 5.5, 6, math.pi/6)):
        a.prop("pedestal_glifo", p[0], p[1], chao=True, glifo=glifos[i]); pedestais.append({"pos": p, "glifo": glifos[i]})
    for p in anel(cx, cy, 8.0, 8, math.pi/8): a.prop("coluna_hawara", p[0], p[1], bloqueia=.5)
    for p in anel(cx, cy, 7.0, 4, math.pi/4): a.luzes.append(p + OLEO + [5])
    a.luzes.append([cx, cy, *TURQ, 5])
    porta = porta_da_arena(a, cx, cy, r)
    a.objetos.append({"kind": "bau", "pos": [87.5, 51.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": "esfinge_de_hawara", "id_mapa": "bau_esfinge"})
    a.portal(89.5, 51.0, "hawara_3", [10.5, 40.5], "Descer à Câmara de Amenemés", requer_flag="venceu_esfinge_de_hawara",
             texto_trancado="Na porta há seis glifos e nenhum é o certo, ainda.")
    a.prop("lamparina_parede", 84.0, 52.5, luz=OLEO + [5])
    return fim(a, {"id": "esfinge_de_hawara", "pos": [cx + 4.0, cy], "arena": {"centro": [cx, cy], "raio": r, "pedestais": pedestais, "raio_pedestal": 1.0},
                   "porta": porta}, [8.5, 38.5])


# ====================================================================================== HAWARA 3
def hawara_3():
    """Câmara de Amenemés. Corredor das portas falsas (as najas dos construtores), galeria dos ninhos de Serket,
    a câmara de quartzito de um bloco só (Petrie, 1889) onde Serket guarda o rei. Depois da luta, a volta ao Faium."""
    a = Andar("hawara_3", "Labirinto de Hawara · Câmara de Amenemés", 80, 72, "x", "parede_hawara",
              zona("hawara_3", "Câmara de Amenemés", [53, 54], "ambiente/egito_hawara_camara"))
    a.sala(5, 36, 14, 45, nome="Pé da escada")
    a.corredor(15, 39, 34, 42)
    a.salas.append(("Corredor das Portas Falsas", 15, 39, 34, 42))
    a.sala(35, 34, 48, 47, nome="Câmara do Alçapão")
    a.corredor(40, 48, 43, 53)
    a.sala(34, 54, 52, 64, "n", nome="Galeria dos Ninhos")
    a.corredor(49, 38, 55, 41)
    a.sala(56, 31, 63, 48, "q", nome="Antecâmara de Quartzito")
    a.corredor(58, 26, 61, 30, "q")
    cx, cy, r = 59.5, 15.5, 9.5
    arena_redonda(a, cx, cy, r, "q")
    a.salas.append(("Câmara de Amenemés", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    a.corredor(69, 14, 72, 17, "q"); a.sala(73, 10, 78, 21, "q", nome="Saída do Faraó")
    # ---- pé da escada
    a.portal(7.5, 42.5, "hawara_2", [87.5, 50.0], "Subir aos Doze Pátios", visual="escada_subida")
    a.prop("lamparina_parede", 6.5, 37.0, luz=OLEO + [5]); a.prop("sarcofago_aberto", 12.0, 37.5, bloqueia=.8)
    # ---- corredor das portas falsas: najas nas portas, o chão marcado de pedras soltas
    for x in range(17, 34, 4):
        a.prop("porta_falsa", x + .5, 42.4); a.prop("porta_falsa", x + 2.5, 39.6, frente=True)
    grupo(a, "naja_do_labirinto", 22.5, 41.0, 2, 53, papel="atiradores: aproximar")
    grupo(a, "naja_do_labirinto", 31.0, 40.0, 2, 53)
    a.luzes += [[18, 41, *TURQ, 3], [26, 41, *TURQ, 3], [33, 41, *TURQ, 3]]
    # ---- câmara do alçapão (a pedra que fechava a tumba, girada; a Heródoto não deixaram entrar)
    a.prop("bloco_alcapao", 41.5, 45.0, bloqueia=1.4); a.prop("braseiro_bronze", 36.5, 35.5, bloqueia=.4, luz=FOGO + [6])
    a.prop("braseiro_bronze", 47.0, 46.0, bloqueia=.4, luz=FOGO + [6]); a.prop("estatua_amenemes", 47.0, 36.0, bloqueia=.8)
    a.espalhar(["entulho", "jarros"], 4, (35, 34, 48, 47), chao=False, bloq=.4, dist=2.5)
    grupo(a, "guarda_do_labirinto", 40.5, 40.5, 2, 53); grupo(a, "sacerdote_de_sobek", 44.5, 38.0, 1, 53, papel="cura")
    # ---- galeria dos ninhos (opcional): ovos de escorpião, o baú do ninho e o registro de Petrie
    for p in [(37.5, 57.5), (45.0, 61.5), (50.0, 56.5)]: a.prop("ninho_serket", p[0], p[1], bloqueia=.7, luz=TURQ + [2])
    a.espalhar(["ossos_espalhados", "casca_escaravelho"], 10, (34, 54, 52, 64))
    grupo(a, "filha_de_serket", 41.0, 58.0, 3, 54, papel="veneno em pilha: ankh")
    grupo(a, "filha_de_serket", 48.0, 61.0, 2, 54)
    a.objetos.append({"kind": "bau", "pos": [51.0, 63.0], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "hw_ninhos"})
    a.objetos.append({"kind": "interativo", "obj": "caderno_de_petrie", "pos": [35.5, 63.0], "i": 0})
    # ---- antecâmara: o primeiro ankh (ensina a mecânica antes da luta)
    a.prop("ankh_aceso", 59.5, 44.5, chao=True, luz=TURQ + [4])
    a.objetos.append({"kind": "interativo", "obj": "ankh_de_serket", "pos": [59.5, 44.5], "i": 0, "efeito": "limpa_veneno"})
    a.prop("estatua_serket", 57.0, 34.0, bloqueia=.8); a.prop("estatua_serket", 62.5, 34.0, bloqueia=.8)
    grupo(a, "filha_de_serket", 60.0, 38.0, 2, 54); grupo(a, "guarda_do_labirinto", 58.0, 41.5, 1, 54)
    # ---- arena: sala de quartzito, sarcófago do rei ao fundo, 4 ankhs nos cantos, 3 ninhos
    a.prop("sarcofago_quartzito", cx - 6.0, cy + 5.5, bloqueia=1.4)
    ankhs = anel(cx, cy, 6.5, 4, math.pi/4)
    for p in ankhs: a.prop("ankh_aceso", p[0], p[1], chao=True, luz=TURQ + [4])
    ninhos = anel(cx, cy, 8.0, 3, math.pi/2)
    for p in ninhos: a.prop("ninho_serket", p[0], p[1], bloqueia=.6)
    for p in anel(cx, cy, 8.8, 6, 0.2): a.luzes.append(p + OLEO + [4])
    porta = porta_da_arena(a, cx, cy, r)
    a.objetos.append({"kind": "bau", "pos": [75.5, 18.5], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": "serket", "id_mapa": "bau_serket"})
    a.objetos.append({"kind": "interativo", "obj": "sarcofago_de_amenemes", "pos": [cx - 4.5, cy + 4.0], "i": 0, "requer_chefe": "serket"})
    a.portal(76.5, 12.5, "egito", chegada_egito(60.5, 32.5), "Voltar ao Faium", visual="escada_subida", requer_flag="venceu_serket",
             texto_trancado="A passagem do faraó só abre quando a guardiã deixa.")
    a.prop("lamparina_parede", 74.0, 20.5, luz=OLEO + [5])
    return fim(a, {"id": "serket", "pos": [cx, cy], "arena": {"centro": [cx, cy], "raio": r, "ankhs": ankhs, "raio_ankh": 1.0, "ninhos": ninhos},
                   "porta": porta}, [9.5, 40.5])


HAWARA = [(hawara_1, "Labirinto de Hawara · 1 · Galerias Alagadas (Petsuchos, nv 51)"),
          (hawara_2, "Labirinto de Hawara · 2 · Os Doze Pátios (Esfinge de Hawara, nv 53)"),
          (hawara_3, "Labirinto de Hawara · 3 · Câmara de Amenemés (Serket, nv 54)")]


# ====================================================================================== RAID
def salao(id_, nome, amb, w, h, piso, parede="parede_duat"):
    return Andar(id_, f"O Coração Endurecido · {nome}", w, h, piso, parede, zona(id_, nome, [60, 60], amb, "musica/egito_raid"))


def entrada_raid(a, n, x0, y0, volta):
    """Pé de cada salão: a escada de volta (ao anterior ou ao Vale), a lamparina, e a pedra de sintonia."""
    a.sala(x0, y0, x0 + 9, y0 + 9, nome="Escada")
    a.portal(x0 + 2.5, y0 + 6.5, *volta, visual="escada_subida")
    a.prop("lamparina_parede", x0 + 1.5, y0 + 1.0, luz=OLEO + [5]); a.prop("lamparina_parede", x0 + 8.5, y0 + 8.5, luz=OLEO + [5])
    a.objetos.append({"kind": "interativo", "obj": "pedra_de_retorno", "pos": [x0 + 6.5, y0 + 6.5], "i": n, "_doc": "ressurreição/reunião do grupo neste salão"})


def saida_raid(a, x, y, chefe, prox, chegada, nome, trancado):
    a.objetos.append({"kind": "bau", "pos": [x - 2.0, y], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": chefe, "id_mapa": f"bau_{chefe}",
                      "loot_de_grupo": True})
    a.portal(x, y, prox, chegada, nome, requer_flag=f"venceu_{chefe}", texto_trancado=trancado)


def coracao_1():
    """Pátio do Sol Terço: a tumba sem cartucho abre num pátio a céu aberto, cercado de estátuas de Sekhmet (como no
    templo de Mut, onde Amenófis III pôs 730). Lixo: leoas (caçam em trio) e sacerdotisas (cura). Arena com 8 jarras."""
    a = salao("coracao_1", "Pátio do Sol Terço", "ambiente/egito_raid_patio", 84, 76, "s")
    entrada_raid(a, 1, 4, 40, ("egito", chegada_egito(12.5, 192.0), "Subir ao Vale dos Reis"))
    a.corredor(14, 43, 19, 46, "j")
    a.sala(20, 36, 44, 52, "j", nome="Corredor das Leoas")
    for x in range(22, 44, 3):
        a.prop("estatua_sekhmet", x + .5, 51.3, bloqueia=.5); a.prop("estatua_sekhmet", x + 1.5, 36.7, bloqueia=.5)
    for x in (24, 32, 40): a.luzes.append([x, 44, *FOGO, 5])
    grupo(a, "leoa_de_sekhmet", 27.0, 44.0, 3, 60, papel="matilha: segurar no tanque")
    grupo(a, "sacerdotisa_de_sekhmet", 36.0, 41.0, 2, 60, papel="cura: interromper")
    grupo(a, "leoa_de_sekhmet", 41.0, 47.5, 2, 60)
    a.corredor(45, 42, 49, 46, "j")
    a.sala(50, 38, 60, 50, "s", nome="Cervejaria de Dendera")
    for p in [(52, 40), (52, 48), (58, 40), (58, 48)]: a.prop("jarra_cerveja", p[0] + .5, p[1] + .5, bloqueia=.4)
    a.prop("tonel_cerveja", 55.0, 49.0, bloqueia=.8); a.prop("braseiro_bronze", 59.0, 44.0, bloqueia=.4, luz=FOGO + [6])
    a.objetos.append({"kind": "interativo", "obj": "relevo_da_destruicao", "pos": [55.0, 39.0], "i": 0})
    grupo(a, "sacerdotisa_de_sekhmet", 55.0, 44.0, 3, 60, papel="três curas: separar")
    a.corredor(53, 30, 57, 37, "j")
    cx, cy, r = 55.0, 18.0, 13.0
    arena_redonda(a, cx, cy, r, "s")
    a.salas.append(("Pátio de Sekhmet", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    jarras = anel(cx, cy, 9.0, 8, math.pi/8)
    for p in jarras: a.prop("jarra_cerveja", p[0], p[1], bloqueia=.3)
    for p in anel(cx, cy, 12.0, 12, 0): a.prop("estatua_sekhmet", p[0], p[1], bloqueia=.5)
    for p in anel(cx, cy, 10.5, 6, .2): a.luzes.append(p + FOGO + [5])
    a.prop("altar_do_sol", cx - 10.0, cy + 4.0, bloqueia=1.0, luz=OURO + [8])
    a.espalhar(["mancha_ocre", "mancha_ocre", "ossos_espalhados"], 14, (cx - 9, cy - 9, cx + 9, cy + 9))
    porta = porta_da_arena(a, cx, cy, r)
    a.corredor(68, 16, 72, 19, "o"); a.sala(73, 12, 80, 23, "o", nome="Descida")
    saida_raid(a, 78.5, 17.5, "sekhmet", "coracao_2", [7.5, 46.5], "Descer ao Salão dos Magos", "As leoas de pedra olham para a escada.")
    return fim(a, {"id": "sekhmet", "pos": [cx, cy], "arena": {"centro": [cx, cy], "raio": r, "jarras": jarras}, "porta": porta}, [7.5, 44.5],
               ceu={"escuro": 0.55, "cor": [1, 0.66, 0.4], "neblina": [0.3, 0.2, 0.12]})


def coracao_2():
    """Salão dos Magos: a sala do trono do Êxodo, com o chão de lápis e as varas pintadas na parede. Lixo: serpentes
    de bastão e guardiões. Arena retangular com dois estrados (um para cada mago) e o Rio de Sangue no meio."""
    a = salao("coracao_2", "Salão dos Magos", "ambiente/egito_raid_magos", 86, 70, "o")
    entrada_raid(a, 2, 4, 40, ("coracao_1", [76.5, 17.5], "Subir ao Pátio do Sol Terço"))
    a.corredor(14, 43, 19, 46)
    a.sala(20, 38, 40, 50, nome="Galeria das Varas")
    for x in range(22, 40, 4): a.prop("relevo_vara_serpente", x + .5, 49.6); a.luzes.append([x + 1, 44, *TURQ, 3])
    grupo(a, "serpente_de_bastao", 26.0, 44.0, 3, 60, papel="atiradores: espalhar")
    grupo(a, "guardiao_do_duat", 35.0, 42.0, 2, 60, papel="atordoa: girar")
    a.corredor(41, 42, 45, 46)
    a.sala(46, 36, 56, 52, "j", nome="Antessala do Trono")
    a.prop("braseiro_bronze", 47.5, 37.5, bloqueia=.4, luz=FOGO + [6]); a.prop("braseiro_bronze", 54.5, 51.0, bloqueia=.4, luz=FOGO + [6])
    a.objetos.append({"kind": "interativo", "obj": "rolo_dos_magos", "pos": [48.0, 50.5], "i": 0})
    grupo(a, "serpente_de_bastao", 51.0, 44.0, 2, 60); grupo(a, "guardiao_do_duat", 53.0, 40.0, 1, 60)
    a.corredor(57, 42, 60, 46)
    x0, y0, x1, y1 = 61, 30, 82, 58
    a.sala(x0, y0, x1, y1, "o"); a.salas.append(("Salão do Trono", x0, y0, x1, y1))
    cx, cy = (x0 + x1 + 1)/2, (y0 + y1 + 1)/2
    est_j, est_b = [cx - 4.0, cy + 8.0], [cx + 4.0, cy - 8.0]
    for p in (est_j, est_b): a.pisar(int(p[0] - 2), int(p[1] - 2), int(p[0] + 2), int(p[1] + 2), "j"); a.prop("estrado_mago", p[0], p[1], chao=True)
    a.prop("trono_do_farao_vazio", x0 + 1.5, cy, bloqueia=1.0)
    for y in range(y0 + 2, y1, 4): a.prop("coluna_hator", x0 + .8, y + .5, bloqueia=.5); a.prop("coluna_hator", x1 - .2, y + .5, bloqueia=.5)
    for p in [(x0 + 3, y0 + 3), (x1 - 2, y0 + 3), (x0 + 3, y1 - 2), (x1 - 2, y1 - 2)]: a.luzes.append([p[0], p[1], *TURQ, 6])
    a.luzes.append([cx, cy, *SANGUE, 4])
    a.prop("poca_sangue_centro", cx, cy, chao=True)
    porta = porta_da_arena(a, cx, cy, 13.0)
    a.corredor(70, 59, 73, 62); a.sala(68, 63, 76, 68, nome="Descida")
    saida_raid(a, 74.5, 66.0, "janes", "coracao_3", [7.5, 46.5], "Descer à Câmara Canópica", "Duas serpentes de pedra cruzam a escada.")
    return fim(a, {"id": "janes", "pos": est_j, "adicionais": [{"id": "jambres", "pos": est_b}],
                   "arena": {"centro": [cx, cy], "raio": 13.0, "ret": [x0, y0, x1, y1], "estrados": [est_j, est_b], "rio": [cx, cy]}, "porta": porta}, [7.5, 44.5])


def coracao_3():
    """Câmara Canópica: os quatro vasos, um em cada ponto cardeal, e os quatro filhos de Hórus nos pedestais."""
    a = salao("coracao_3", "Câmara Canópica", "ambiente/egito_raid_canopo", 80, 76, "o")
    entrada_raid(a, 3, 4, 40, ("coracao_2", [72.5, 66.0], "Subir ao Salão dos Magos"))
    a.corredor(14, 43, 19, 46)
    a.sala(20, 36, 34, 52, nome="Sala do Natrão")
    a.prop("bacia_natrao", 27.0, 44.0, bloqueia=.8); a.espalhar(["linho_no_chao", "poca_natrao"], 6, (20, 36, 34, 52))
    for p in [(21.5, 37.5), (33, 37.5), (21.5, 51), (33, 51)]: a.luzes.append([p[0], p[1], *OLEO, 4])
    grupo(a, "anubita_do_duat", 25.0, 40.0, 2, 60, papel="golpe em círculo"); grupo(a, "falcao_do_duat", 31.0, 48.0, 2, 60, papel="atiradores")
    a.corredor(35, 42, 40, 46)
    a.sala(41, 36, 52, 52, nome="Corredor dos Olhos de Hórus")
    for y in range(37, 52, 3): a.prop("relevo_olho_horus", 41.4, y + .5)
    grupo(a, "anubita_do_duat", 46.0, 44.0, 2, 60); grupo(a, "falcao_do_duat", 50.0, 39.0, 1, 60)
    a.objetos.append({"kind": "bau", "pos": [50.5, 50.5], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "cr_canopo"})
    a.corredor(45, 30, 48, 35)
    cx, cy, r = 46.5, 17.5, 12.5
    arena_redonda(a, cx, cy, r, "o")
    a.salas.append(("Câmara dos Quatro Vasos", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    nomes = ["imseti", "qebehsenuef", "hapi", "duamutef"]       # sul (frente), oeste, norte, leste (rótulos de lore)
    pedestais = []
    for i, p in enumerate(anel(cx, cy, 9.5, 4, -math.pi/4)):
        a.prop("pedestal_canopo", p[0], p[1], bloqueia=.8, vaso=nomes[i], luz=TURQ + [4]); pedestais.append({"pos": p, "membro": nomes[i]})
    for p in anel(cx, cy, 11.5, 8, math.pi/8): a.prop("coluna_hator", p[0], p[1], bloqueia=.5)
    a.prop("santuario_canopico", cx - 3.0, cy + 3.0, bloqueia=1.4, luz=OURO + [6])
    porta = porta_da_arena(a, cx, cy, r)
    a.corredor(59, 16, 63, 19); a.sala(64, 12, 72, 23, nome="Descida")
    saida_raid(a, 70.5, 17.5, "imseti", "coracao_4", [7.5, 46.5], "Descer ao Rio do Duat", "Quatro selos de barro fecham a escada.")
    adic = [{"id": n, "pos": [pedestais[i]["pos"][0] + (cx - pedestais[i]["pos"][0])*.15, pedestais[i]["pos"][1] + (cy - pedestais[i]["pos"][1])*.15]}
            for i, n in enumerate(nomes) if n != "imseti"]
    return fim(a, {"id": "imseti", "pos": [pedestais[0]["pos"][0] + (cx - pedestais[0]["pos"][0])*.15, pedestais[0]["pos"][1] + (cy - pedestais[0]["pos"][1])*.15],
                   "adicionais": adic, "arena": {"centro": [cx, cy], "raio": r, "pedestais": pedestais}, "porta": porta}, [7.5, 44.5])


def coracao_4():
    """O Rio do Duat: a sétima hora do Amduat. Um cais de pedra e, no rio escuro, a barca da noite (o convés é a arena).
    Apófis fica na água ao lado da barca (imóvel); a lanterna no meio do convés, os dois braseiros na proa."""
    a = salao("coracao_4", "O Rio do Duat", "ambiente/egito_raid_duat", 90, 72, "o")
    entrada_raid(a, 4, 4, 40, ("coracao_3", [68.5, 17.5], "Subir à Câmara Canópica"))
    a.corredor(14, 43, 19, 46)
    a.sala(20, 34, 42, 54, "o", nome="Cais das Horas")
    a.pisar(20, 34, 42, 37, "r")
    for x in range(22, 42, 5): a.prop("estatua_hora", x + .5, 53.4, bloqueia=.5); a.luzes.append([x + 1, 45, *NOITE, 4])
    grupo(a, "cria_do_duat", 26.0, 40.0, 3, 60, papel="atordoa: interromper"); grupo(a, "guardiao_do_duat", 37.0, 47.0, 2, 60)
    # o rio: tudo de água funda, a barca no meio, uma prancha do cais até ela
    for y in range(4, 34):
        for x in range(20, 88): a.ter[y][x] = "w"; a.blk[y][x] = False
    a.salas.append(("O Rio Escuro", 20, 4, 87, 33))
    bx0, by0, bx1, by1 = 40, 12, 70, 24                      # convés
    a.pisar(bx0, by0, bx1, by1, "b")
    a.pisar(30, 22, 39, 24, "b")                            # prancha
    a.pisar(30, 25, 33, 33, "b")
    for y in range(4, 34):
        for x in range(20, 88):
            if a.ter[y][x] == "w": a.extra_blk.add((x, y))     # água funda bloqueia (a barca e a prancha não)
    a.prop("barca_de_ra", (bx0 + bx1 + 1)/2, (by0 + by1 + 1)/2, chao=True)
    a.prop("proa_barca", bx1 + 1.5, (by0 + by1 + 1)/2, bloqueia=0); a.prop("popa_barca", bx0 - 1.0, (by0 + by1 + 1)/2, bloqueia=0)
    cx, cy = (bx0 + bx1 + 1)/2, (by0 + by1 + 1)/2
    lanterna = [cx - 2.0, cy]
    a.prop("lanterna_de_ra", *lanterna, bloqueia=.6, luz=OURO + [10])
    braseiros = [[bx1 - 2.0, by0 + 2.0], [bx1 - 2.0, by1 - 1.0]]
    for p in braseiros: a.prop("braseiro_proa", p[0], p[1], bloqueia=.5, luz=FOGO + [6])
    for x in range(bx0 + 2, bx1, 5): a.prop("remo_barca", x + .5, by0 + .3); a.prop("remo_barca", x + .5, by1 + .7)
    a.prop("trono_de_ra", bx0 + 2.5, cy, bloqueia=.8)
    apofis = [cx + 2.0, by1 + 1.6]           # na água colada à amurada: a cabeça alcança o convés
    porta = [[x, y] for x in range(30, 34) for y in range(25, 27)]
    a.sala(74, 14, 84, 22, "o", nome="Margem da Oitava Hora")
    a.pisar(71, 16, 73, 20, "b")
    saida_raid(a, 81.5, 18.5, "apofis", "coracao_5", [7.5, 46.5], "Descer ao Salão das Duas Verdades", "A barca não chega à margem enquanto a serpente estiver no rio.")
    for x in range(71, 74):
        for y in range(16, 21): a.extra_blk.discard((x, y))
    return fim(a, {"id": "apofis", "pos": apofis, "imovel": True,
                   "arena": {"centro": [cx, cy], "raio": 15.0, "ret": [bx0, by0, bx1, by1], "lanterna": lanterna, "braseiros": braseiros}, "porta": porta},
               [7.5, 44.5], ceu=CEU_DUAT, agua=AGUA_DUAT)


def coracao_5():
    """Salão das Duas Verdades: os 42 assessores nas paredes, Thoth com a paleta, a balança no centro com dois pratos."""
    a = salao("coracao_5", "Salão das Duas Verdades", "ambiente/egito_raid_maat", 82, 76, "o")
    entrada_raid(a, 5, 4, 40, ("coracao_4", [79.5, 18.5], "Subir ao Rio do Duat"))
    a.corredor(14, 43, 19, 46)
    a.sala(20, 36, 44, 52, "j", nome="Corredor das Confissões")
    for i, x in enumerate(range(21, 44, 2)):
        a.prop("estatua_assessor", x + .5, 51.4 if i % 2 == 0 else 36.6, bloqueia=.4)
    for x in (24, 32, 40): a.luzes.append([x, 44, *OURO, 4])
    a.objetos.append({"kind": "interativo", "obj": "confissao_negativa", "pos": [32.0, 50.5], "i": 0})
    grupo(a, "anubita_do_duat", 27.0, 44.0, 2, 60); grupo(a, "escaravelho_do_coracao", 35.0, 41.0, 3, 60, papel="mentem pelo morto")
    grupo(a, "guardiao_do_duat", 41.0, 47.0, 2, 60)
    a.corredor(45, 42, 49, 46, "j")
    cx, cy, r = 60.5, 30.0, 13.0
    a.corredor(58, 44, 62, 46, "j")
    arena_redonda(a, cx, cy, r, "j")
    a.salas.append(("A Pesagem", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    a.sala(50, 41, 57, 47, "j")
    a.prop("balanca_de_maat", cx, cy, bloqueia=.9, luz=OURO + [8])
    pratos = [[cx - 4.5, cy + 4.5], [cx + 4.5, cy - 4.5]]
    for i, p in enumerate(pratos): a.prop("prato_balanca", p[0], p[1], chao=True, lado=["coracao", "pena"][i])
    a.prop("estatua_thoth_escriba", cx - 10.0, cy - 4.0, bloqueia=.8); a.prop("estatua_ammit", cx + 9.0, cy + 6.0, bloqueia=.8)
    for p in anel(cx, cy, 12.0, 14, 0): a.prop("estatua_assessor", p[0], p[1], bloqueia=.4)
    for p in anel(cx, cy, 10.0, 6, .4): a.luzes.append(p + TURQ + [4])
    porta = porta_da_arena(a, cx, cy, r)
    a.corredor(58, 13, 62, 16, "j"); a.sala(55, 6, 66, 12, "o", nome="Descida")
    saida_raid(a, 63.5, 9.0, "anubis_pesador", "coracao_6", [7.5, 46.5], "Descer à Câmara do Coração", "O prato da pena ainda não pesou.")
    return fim(a, {"id": "anubis_pesador", "pos": [cx + 2.0, cy + 2.0], "arena": {"centro": [cx, cy], "raio": r, "pratos": pratos, "raio_prato": 3.0,
                                                                              "ammit_nasce": [cx + 8.0, cy + 5.0]}, "porta": porta}, [7.5, 44.5])


def coracao_6():
    """Câmara do Coração: o sarcófago sem nome e o coração que bate. Quatro portas na parede da arena (a 10ª praga),
    quatro lamparinas (as Trevas), manchas de sangue que crescem (1ª praga)."""
    a = salao("coracao_6", "Câmara do Coração", "ambiente/egito_raid_farao", 84, 80, "o")
    entrada_raid(a, 6, 4, 42, ("coracao_5", [61.5, 9.0], "Subir ao Salão das Duas Verdades"))
    a.corredor(14, 45, 19, 48)
    a.sala(20, 40, 36, 54, "j", nome="Corredor dos Nomes Raspados")
    for x in range(22, 36, 3): a.prop("cartucho_raspado_parede", x + .5, 53.4)
    a.objetos.append({"kind": "interativo", "obj": "ultima_parede", "pos": [28.0, 53.0], "i": 0})
    grupo(a, "guardiao_do_duat", 25.0, 47.0, 3, 60); grupo(a, "anubita_do_duat", 33.0, 44.0, 2, 60)
    a.corredor(37, 45, 41, 48, "j")
    cx, cy, r = 55.5, 46.5, 14.0
    arena_redonda(a, cx, cy, r, "o")
    a.salas.append(("Câmara do Coração", int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    a.prop("sarcofago_sem_nome", cx + 9.5, cy - 6.0, bloqueia=1.4, luz=TURQ + [5])
    portas = anel(cx, cy, 12.5, 4, math.pi/4)
    for p in portas: a.prop("porta_lintel", p[0], p[1], bloqueia=0)
    lamparinas = anel(cx, cy, 7.0, 4, 0.0)
    for p in lamparinas: a.prop("lamparina_trevas", p[0], p[1], bloqueia=.3, luz=OLEO + [5])
    for p in anel(cx, cy, 13.4, 10, .1): a.prop("coluna_hator", p[0], p[1], bloqueia=.5)
    braseiros = anel(cx, cy, 10.0, 2, math.pi/2)
    for p in braseiros: a.prop("braseiro_bronze", p[0], p[1], bloqueia=.4, luz=FOGO + [6])
    a.luzes.append([cx, cy, *SANGUE, 5])
    porta = porta_da_arena(a, cx, cy, r)
    a.corredor(54, 61, 57, 66, "j"); a.sala(50, 67, 61, 74, "j", nome="Saída do Êxodo")
    a.objetos.append({"kind": "interativo", "obj": "coracao_do_farao", "pos": [cx, cy], "i": 0, "requer_chefe": "farao_sem_nome",
                      "_doc": "a escolha da linha N (destruir, pesar ou devolver ao Coro)"})
    saida_raid(a, 57.5, 71.5, "farao_sem_nome", "egito", chegada_egito(12.5, 192.0), "Sair para o Vale dos Reis", "A porta não abre enquanto o coração bate.")
    return fim(a, {"id": "farao_sem_nome", "pos": [cx + 6.0, cy - 3.0], "arena": {"centro": [cx, cy], "raio": r, "portas": portas, "lamparinas": lamparinas,
                                                                             "braseiros": braseiros}, "porta": porta}, [7.5, 46.5])


RAID = [(coracao_1, "O Coração Endurecido · 1 · Pátio do Sol Terço (Sekhmet)"),
        (coracao_2, "O Coração Endurecido · 2 · Salão dos Magos (Janes e Jambres)"),
        (coracao_3, "O Coração Endurecido · 3 · Câmara Canópica (Quatro Filhos de Hórus)"),
        (coracao_4, "O Coração Endurecido · 4 · O Rio do Duat (Apófis)"),
        (coracao_5, "O Coração Endurecido · 5 · Salão das Duas Verdades (Anúbis, o Pesador)"),
        (coracao_6, "O Coração Endurecido · 6 · Câmara do Coração (O Faraó Sem Nome)")]

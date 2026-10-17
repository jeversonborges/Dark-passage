"""Salões de Amenti · gerador do mapa da dungeon (16/10/2026). Conceito: conceito.md nesta pasta.

Mesmo formato dos andares da cripta (classe Andar de design/mapas/cripta/gerar.py). O mapa inteiro é um só JSON
(saloes_de_amenti.json): seis salas em fila, de sul para norte, ligadas por corredores curtos. Não é para upar: sem
farm, sem missão. Cada sala é um universo (um chão, uma luz, um vocabulário), todas dentro da paleta de Amenti
(preto, esmeralda, ouro velho; o azul de estrela só no Salão do Universo).

  1. Vestíbulo do Livro        x 54..65,  y 4..25    degraus de esmeralda descendo; estelas que acendem com trechos da Tábua
  2. O Salão do Universo       x 36..83,  y 30..55   vidro negro com o céu embaixo, pontes de luz, Arcontes de Luz passando
  3. O Vazio                   x 34..85,  y 60..83   ilhas sobre o nada, placas que somem, vento, O Que Não Tem Rosto
  4. As Câmaras Sombrias       x 34..85,  y 88..107  corredores em ângulo reto, tochas verdes, lâminas, fogo frio, Cães
  5. O Salão da Flor da Vida   x 38..81,  y 112..145 nove tronos em volta da Flor da Vida ardendo
  6. A Antecâmara dos Portões  x 40..79,  y 150..189 os dois Lordes, os dois Guardiões, o Portão que não abre
  7. A Sala do Juízo           x 98..104, y 192..197 "atrás do Portão": cela sem passagem a pé (só teleporte); saída para o egito

Bússola (igual à Atlântida): norte = alto da tela. Numa sala de grade o "fundo" é a parede de +Y (cima-direita na
tela); a entrada de cada sala fica na parede de -Y (baixo-esquerda), que é parede da frente, baixa.
Tela: +X desce para a direita, +Y sobe para a direita.

O que o jogo ainda precisa implementar está em PENDENCIAS_JOGO (no fim deste arquivo e no JSON, `pendencias_jogo`).

Uso: python3 gerar.py   -> saloes_de_amenti.json + planta_saloes_de_amenti.png nesta pasta
Mapas são gerados, nunca editados à mão.
"""
import json, math, os, sys, zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "cripta"))
import gerar as G          # noqa: E402  (Andar, planta)

G.AQUI = AQUI
G.PISOS = {"n": "pedra_negra_veios", "v": "pedra_negra_veios_2", "w": "pedra_negra_veios_3", "u": "ouro_mosaico",
           "e": "esmeralda_lapidada", "g": "vidro_estrelado", "p": "ponte_luz", "i": "pedra_ilha", "r": "placa_runica",
           "s": "laje_sombria", "f": "ouro_flor"}
G.COR_PISO.update({"n": (34, 44, 40), "v": (34, 44, 40), "w": (34, 44, 40), "u": (150, 120, 60), "e": (30, 90, 60),
                   "g": (20, 24, 50), "p": (80, 200, 150), "i": (60, 60, 58), "r": (70, 90, 80), "s": (44, 46, 46), "f": (90, 75, 40)})

T = 1 / math.sqrt(2)
ESM = [0.3, 1.0, 0.65]; AZUL = [0.45, 0.62, 1.0]; QUENTE = [1.0, 0.7, 0.4]
W, H = 120, 200
X0, Y0, LADO = 40, 150, 40          # Antecâmara: x 40..79, y 150..189
RET = {1: (54, 4, 65, 25), 2: (36, 30, 83, 55), 3: (34, 60, 85, 83), 4: (34, 88, 85, 107), 5: (38, 112, 81, 145),
       6: (X0, Y0, X0 + LADO - 1, Y0 + LADO - 1), 7: (98, 192, 104, 197)}
NOMES = {7: "A Sala do Juízo", 1: "Vestíbulo do Livro", 2: "O Salão do Universo", 3: "O Vazio", 4: "As Câmaras Sombrias",
         5: "O Salão da Flor da Vida", 6: "A Antecâmara dos Portões"}
TABUA = [  # Tábua de Esmeralda (Tabula Smaragdina, tradição hermética medieval), em português nosso
    "É verdade, sem mentira, certo e muito verdadeiro.",
    "O que está embaixo é como o que está em cima, e o que está em cima é como o que está embaixo, para fazer os milagres de uma só coisa.",
    "O Sol é seu pai, a Lua é sua mãe; o vento o levou no ventre; a terra é sua ama.",
    "Separarás a terra do fogo, o sutil do espesso, docemente e com grande engenho.",
    "Sobe da terra ao céu e desce de novo à terra, e recebe a força das coisas de cima e das de baixo.",
    "Assim terás a glória do mundo inteiro, e toda a escuridão fugirá de ti.",
]
SALA_DE = {}                          # (x, y) -> número da sala (0 = corredor), para escolher o kit de parede


def abrir(a, x0, y0, x1, y1, piso, n, nome=None):
    a.sala(x0, y0, x1, y1, piso, nome=nome)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): SALA_DE[(x, y)] = n


def grupo_neutro(a, mob, x, y, nivel, motivo, **extra):
    s = {"mob": mob, "pos": [round(x, 2), round(y, 2)], "raio": 0.5, "qtd": 1, "nivel": nivel, "postura": "neutro",
         "temperamento": "neutro", "motivo": motivo}
    s.update(extra); a.spawns.append(s)


def armadilha(a, tipo, area, ciclo_s, dano, **extra):
    o = {"kind": "armadilha", "tipo": tipo, "pos": [round((area[0] + area[2] + 1) / 2, 2), round((area[1] + area[3] + 1) / 2, 2)],
         "area": list(area), "ciclo_s": ciclo_s, "dano": dano}
    o.update(extra); a.objetos.append(o)


def manchas_de_pedra(a, x0, y0, x1, y1):
    """Troca a pedra negra por variantes em manchas (quebra a repetição 4x4 do atlas)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if a.blk[y][x] or a.ter[y][x] != "n": continue
            k = (zlib.crc32(f"{(x + int(2 * math.sin(y * .45))) // 5},{(y + int(2 * math.sin(x * .38))) // 5}".encode()) % 3)
            a.ter[y][x] = "nvw"[k]


# ====================================================================== 1. Vestíbulo do Livro
def vestibulo(a):
    x0, y0, x1, y1 = RET[1]
    abrir(a, x0, y0, x1, y1, "e", 1, nome=NOMES[1])
    abrir(a, 57, 26, 62, 29, "n", 0)
    # a laje que se fecha atrás de quem entra (vem da Esfinge, no Egito)
    a.prop("porta_selada_amenti", 60, y0 - .5)
    a.objetos.append({"kind": "porta_selada", "pos": [60, y0 + 1.0], "visual": "porta_selada_amenti", "fecha_ao_entrar": True,
                      "nome": "A laje sob a pata", "texto": "A laje subiu atrás de você. Daqui só se sai pelo fim, ou morrendo."})
    # estelas do Livro, alternando dos dois lados da escadaria; acendem quando o jogador passa
    for i, (x, y) in enumerate([(56, 7.5), (64, 10.5), (56, 13.5), (64, 16.5), (56, 19.5), (64, 22.5)]):
        a.prop("estela_livro", x, y, bloqueia=0.6)
        a.objetos.append({"kind": "leitura", "pos": [x, y], "nome": f"Estela do Livro ({i + 1} de 6)", "texto": TABUA[i],
                          "visual": "estela_livro", "visual_acesa": "estela_livro_acesa", "acende_raio": 3.0, "fica_acesa": True})
        a.luzes.append([x + (1.2 if x < 60 else -1.2), y, *ESM, 2.5])
    for (x, y) in ((60, 9), (60, 21)):
        a.prop("poeira_luz_2", x, y)
    a.luzes += [[60, 5.5, *ESM, 4], [60, 26, *ESM, 5]]
    return (60, y0 + 2.5)


# ====================================================================== 2. O Salão do Universo
def linha(a, p0, p1, larg, piso):
    """Pinta uma faixa reta (ponte) de largura `larg` entre dois pontos, só onde já é chão."""
    n = int(math.dist(p0, p1) * 2) + 1
    for i in range(n + 1):
        t = i / n; cx, cy = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        for y in range(int(cy - larg / 2), int(cy + larg / 2) + 1):
            for x in range(int(cx - larg / 2), int(cx + larg / 2) + 1):
                if math.hypot(x + .5 - cx, y + .5 - cy) <= larg / 2 + .2 and a.livre(x, y): a.ter[y][x] = piso


def universo(a):
    x0, y0, x1, y1 = RET[2]
    abrir(a, x0, y0, x1, y1, "g", 2, nome=NOMES[2])
    abrir(a, 57, 56, 62, 59, "n", 0)
    centro, oeste, leste = (60, 42.5), (45.5, 42.5), (74.5, 42.5)       # pontes só em ângulo reto (diagonal vira escada no tile)
    for (p0, p1) in (((60, 30), (60, 55.9)), (oeste, leste), (oeste, (45.5, 53)), (leste, (74.5, 32))):
        linha(a, p0, p1, 3, "p")
    for (x, y) in (centro, oeste, leste):
        a.prop("plataforma_astral", x, y, bloqueia=2.4)
        a.luzes.append([x, y, *AZUL, 7])
    for (x, y) in ((68, 50), (40.5, 34)):
        a.prop("anel_astral", x, y)
        a.luzes.append([x, y, *AZUL, 5])
    for (x, y) in ((67, 37), (52, 46), (70, 52)):
        a.prop("poeira_luz", x, y)
    # Arcontes de Luz: seres astrais imensos que passam devagar, sem agredir (sem sprite ainda)
    for i, rota in enumerate(([(40, 34), (80, 34), (80, 40), (40, 40)], [(78, 53), (40, 53), (40, 46), (78, 46)],
                             [(50, 44), (70, 36), (70, 50), (50, 50)])):
        grupo_neutro(a, "arconte_de_luz", *rota[0], 150, "Passa pelo Salão como passa pelo céu: não vê ninguém.",
                     rota=[list(p) for p in rota], velocidade=0.35)
    a.luzes += [[60, 31, *ESM, 4], [60, 55, *ESM, 4]]


# ====================================================================== 3. O Vazio
def ilha(a, cx, cy, r):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x + .5 - cx, y + .5 - cy) + .3 * math.sin(math.atan2(y - cy, x - cx) * 3 + cx)
            if d <= r: a.ter[y][x] = "i"; a.blk[y][x] = False; SALA_DE[(x, y)] = 3


def placas(a, p0, p1, volta):
    """Caminho de placas soltas (2 de largura) entre duas ilhas; cada trecho é uma armadilha placa_que_some."""
    pts = []
    n = int(math.dist(p0, p1) * 1.5) + 1
    for i in range(n + 1):
        t = i / n; cx, cy = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        for (x, y) in ((int(cx), int(cy)), (int(cx + .7), int(cy)), (int(cx), int(cy + .7))):
            if a.blk[y][x]:
                a.ter[y][x] = "r"; a.blk[y][x] = False; SALA_DE[(x, y)] = 3; pts.append((x, y))
                a.prop("laje_pendurada", x + .5, y + .5, pendurado=1)              # a espessura da laje, vista por baixo
    if pts:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        armadilha(a, "placa_que_some", [min(xs), min(ys), max(xs), max(ys)], 6.0,
                  {"tipo": "queda", "pct_vida": 30, "volta_para": list(volta)},
                  celulas=[list(p) for p in sorted(set(pts))], aviso_s=1.0, some_s=2.5, defasagem_por_celula_s=0.25,
                  texto_aviso="A placa treme.")
    return pts


ILHAS = {"A": (59.5, 62.5, 2.8), "B": (73, 67, 3.2), "C": (58, 72, 3.6), "D": (44, 77, 3.0), "E": (60, 81.5, 2.6)}


def vazio(a):
    """Cinco ilhas de basalto bem separadas sobre o nada, ligadas por lajes de esmeralda que somem. A parte de baixo
    de cada ilha é um prop 'pendurado' (base_ilha_*), desenhado numa camada abaixo do chão de todas as ilhas."""
    x0, y0, x1, y1 = RET[3]
    abrir(a, 57, 84, 62, 87, "n", 0)
    for (cx, cy, r) in ILHAS.values():
        ilha(a, cx, cy, r)
        a.prop(f"base_ilha_{int(round(r * 10))}", cx, cy, pendurado=1)
    for (y, xs) in ((60, range(58, 62)), (83, range(58, 62))):                # as ilhas A e E encostam nos corredores
        for x in xs: a.ter[y][x] = "i"; a.blk[y][x] = False; SALA_DE[(x, y)] = 3
    a.salas.append((NOMES[3], x0, y0, x1, y1))
    caminhos = []
    for (i0, i1) in (("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")):
        (ax, ay, ar), (bx, by, br) = ILHAS[i0], ILHAS[i1]
        d = math.dist((ax, ay), (bx, by)); ux, uy = (bx - ax) / d, (by - ay) / d
        p0, p1 = (ax + ux * (ar - .4), ay + uy * (ar - .4)), (bx - ux * (br - .4), by - uy * (br - .4))
        placas(a, p0, p1, (ax, ay)); caminhos.append((p0, p1, (ux, uy)))
    # vento que puxa para a beira nos dois trechos mais longos (rajadas de lado)
    for (p0, p1, (ux, uy)) in sorted(caminhos, key=lambda c: -math.dist(c[0], c[1]))[:2]:
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        area = [int(mx - 3), int(my - 2), int(mx + 2), int(my + 2)]
        armadilha(a, "vento", area, 8.0, {"tipo": "empurrao", "pct_vida": 0}, direcao=[round(-uy, 2), round(ux, 2)], forca_tiles_s=1.6,
                  ativo_s=3.0, aviso_s=1.0, texto_aviso="O vento do Vazio sopra para a beira.")
        a.prop("vento_vazio", mx, my)
    grupo_neutro(a, "o_que_nao_tem_rosto", 58, 72, 150, "Está no meio do Vazio desde antes do Vazio. Não se mexe.",
                 imovel=True)
    # lascas soltas no abismo, longe das ilhas e dos caminhos (também na camada de baixo)
    for (x, y, k) in ((67, 61, "lasca_abismo"), (80, 61.5, "lasca_abismo_2"), (49, 64, "lasca_abismo_2"), (40, 69, "lasca_abismo"),
                      (68, 77, "lasca_abismo_2"), (79, 79, "lasca_abismo"), (38, 82, "lasca_abismo"), (51, 83, "lasca_abismo"),
                      (66, 71.5, "lasca_abismo"), (48, 71, "lasca_abismo")):
        if all(math.dist((x, y), (cx, cy)) > r + 1.8 for (cx, cy, r) in ILHAS.values()) and a.blk[int(y)][int(x)]:
            a.prop(k, x, y, pendurado=1)
    for (cx, cy, r) in ILHAS.values(): a.luzes.append([cx, cy, *ESM, round(r + 2.5, 1)])
    a.prop("poeira_luz_2", 58, 72)


# ====================================================================== 4. As Câmaras Sombrias
def camaras(a):
    abrir(a, 57, 108, 62, 111, "n", 0)
    tr = [(58, 88, 61, 95), (36, 93, 61, 95), (36, 93, 39, 103), (36, 101, 81, 103), (78, 101, 81, 107), (58, 105, 81, 107)]
    for r in tr: abrir(a, *r, "s", 4)
    for r in ((35, 90, 41, 96), (35, 98, 41, 104), (76, 99, 83, 104)): abrir(a, *r, "s", 4)    # câmaras dos cantos
    a.salas.append((NOMES[4], *RET[4]))
    mot = "Os Cães da Barreira só andam em ângulos: guardam os cantos por onde ninguém deveria passar."
    for (x, y, q) in ((38.5, 93.5, 2), (38.5, 101.5, 3), (60.5, 102, 2), (79.5, 101.5, 3)):
        a.spawns.append({"mob": "cao_da_barreira", "pos": [x, y], "raio": 1.5, "qtd": q, "nivel": 145, "temperamento": "agressivo",
                         "postura": "agressivo", "motivo": mot, "respawn_s": 1800})
    # lâminas que varrem o corredor de parede a parede
    for (x, y0) in ((50, 93), (47, 101), (70, 101)):
        armadilha(a, "lamina", [x, y0, x, y0 + 2], 3.0, {"tipo": "golpe", "pct_vida": 25}, aviso_s=0.6, eixo="y")
        a.prop("armadilha_lamina", x + .5, y0 + 1.5)
    # respiros de fogo frio no chão
    for (x, y) in ((59, 90), (60, 92), (66, 106), (72, 105), (40, 99)):
        armadilha(a, "fogo_frio", [x, y, x, y], 5.0, {"tipo": "por_segundo", "pct_vida": 8}, ativo_s=1.5, aviso_s=0.8)
        a.prop("armadilha_fogo", x + .5, y + .5)
        a.luzes.append([x + .5, y + .5, *ESM, 3.5])
    for (x, y) in ((36, 91), (40.8, 96), (36, 104), (82.8, 99.6), (76.5, 104)):
        a.prop("tocha_verde", x + .5, y + .5, bloqueia=0.3, luz=ESM + [6])
    a.luzes += [[60, 89, *ESM, 3], [60, 110, *ESM, 3]]


# ====================================================================== 5. O Salão da Flor da Vida
def flor(a):
    x0, y0, x1, y1 = RET[5]
    abrir(a, x0, y0, x1, y1, "f", 5, nome=NOMES[5])
    abrir(a, 57, 146, 62, 149, "n", 0)
    cx, cy = 60, 129
    a.prop("flor_da_vida_ardente", cx, cy, bloqueia=5.6)
    a.luzes += [[cx, cy, *ESM, 16], [cx, cy - 3, *ESM, 8]]
    # nove tronos em arco, abertos para quem chega (o lado da câmera fica livre para ver a Flor). Os Senhores dos Ciclos
    # são estátuas de pedra sentadas, parte do prop de cada trono (trono_senhor_1..9, numerados no sentido horário a
    # partir do norte da tela): pares de mãos abertas; 2 livro de pedra, 4 sete degraus nos braços, 6 a pena, 8 cabeça baixa.
    R = 12.5; senhores = []
    for n in range(1, 10):
        k = (4 - (n - 1)) % 9                                 # mesmo cálculo de angulo_trono() em amenti.py
        ang = math.radians(10 + k * 31.25)
        x, y = round(cx + R * math.cos(ang), 2), round(cy + R * math.sin(ang), 2)
        a.prop(f"trono_senhor_{n}", x, y, bloqueia=1.6)
        frente = [round(x - 2.2 * math.cos(ang), 2), round(y - 2.2 * math.sin(ang), 2)]
        a.objetos.append({"kind": "interativo", "obj": f"trono_senhor_{n}", "pos": frente, "visual": f"trono_senhor_{n}",
                          "nome": "Trono de um Senhor dos Ciclos", "texto_servidor": f"trono_senhor_{n}", "trono": n})
        a.luzes.append([x, y, *ESM, 4]); senhores.append({"n": n, "trono": [x, y], "interagir": frente})
    for (x, y) in ((44, 114), (79.5, 134), (43, 142.5), (77, 142.5)):
        a.prop("coluna_amenti", x, y, bloqueia=1.1)
    for (x, y) in ((56, 114.5), (64, 114.5)):
        a.prop("braseiro_frio", x, y, bloqueia=0.4, luz=ESM + [5])
    for (x, y) in ((52, 122), (68, 136), (60, 140), (48, 132)):
        a.prop("poeira_luz", x, y)
    return senhores


# ====================================================================== 6. A Antecâmara dos Portões
def P(u, v):
    """Coordenada local da Antecâmara (u ao longo de X, v ao longo de Y, a partir do canto x0,y0) para o mapa."""
    return X0 + u, Y0 + v


def antecamara(a):
    abrir(a, X0, Y0, X0 + LADO - 1, Y0 + LADO - 1, "n", 6, nome="Antecâmara dos Portões")
    for x in range(57, 63): a.ter[Y0 - 1][x] = "n"; a.blk[Y0 - 1][x] = False; SALA_DE[(x, Y0 - 1)] = 0   # vão da porta
    a.pisar(*P(17, 0), *P(22, 35), "u")                                    # nave de ouro: centro em u = 20

    gx, gy = P(20, LADO)
    frente = gy - 2.6 / T                                                    # frente do estrado (metadado do kit)
    a.prop("portao_amenti_salao", gx, gy)
    a.prop("degraus_amenti", gx, frente - 1.0 / T)                          # degrau de cima encosta no estrado
    for y in range(int(frente), Y0 + LADO):
        for x in range(X0 + 10, X0 + 30):
            a.extra_blk.add((x, y))
    a.luzes += [[gx, frente - 1.5, *ESM, 12], [gx - 6.8, frente, *ESM, 6], [gx + 6.8, frente, *ESM, 6]]

    for v in (3.5, 9.0, 26.5):
        for u in (13.5, 26.5):
            k = "coluna_amenti_quebrada" if (u, v) == (26.5, 9.0) else "coluna_amenti"
            a.prop(k, *P(u, v), bloqueia=1.1)

    pa, pd = P(8, 18.5), P(32, 18.5)
    a.prop("palco_lorde", *pa)
    a.prop("palco_lorde_b", *pd)
    for (cx, cy) in (pa, pd):
        for y in range(int(cy - 3), int(cy + 3)):
            for x in range(int(cx - 3), int(cx + 3)):
                a.extra_blk.add((x, y))
    a.luzes += [[pa[0], pa[1] - 2, *ESM, 4], [pd[0], pd[1] - 2, *ESM, 4]]
    lugares = {"palco_lider_dos_anjos": [round(pa[0] - .475 / T, 2), pa[1]],
               "palco_lider_dos_demonios": [round(pd[0] + .475 / T, 2), pd[1]]}
    # os dois Lordes intocáveis (arte e def de NPC da thread do Egito, entregas/warlord/lordes/objetos_lordes.json; diálogos em dialogos.py)
    a.npcs.append({"id": "lider_dos_anjos", "ponto": "palco_lider_dos_anjos", "x": lugares["palco_lider_dos_anjos"][0],
                   "y": lugares["palco_lider_dos_anjos"][1], "dir": [1, 0], "alvejavel": False})
    a.npcs.append({"id": "lider_dos_demonios", "ponto": "palco_lider_dos_demonios", "x": lugares["palco_lider_dos_demonios"][0],
                   "y": lugares["palco_lider_dos_demonios"][1], "dir": [-1, 0], "alvejavel": False})

    for (u, v) in ((16, 6.25), (24, 6.25), (16, 13), (24, 13), (16, 24), (24, 24), (14.5, 32.5), (25.5, 32.5)):
        a.prop("braseiro_frio", *P(u, v), bloqueia=0.4, luz=ESM + [5])
    for u in (3.5, 36.5):
        a.prop("obelisco_glifos", *P(u, 33.5), bloqueia=1.0, luz=ESM + [4])
    for (u, v, k) in ((20, 30, "poeira_luz"), (9, 22, "poeira_luz_2"), (31, 15, "poeira_luz_2"), (20, 16, "poeira_luz"),
                      (11, 6, "poeira_luz_2"), (30, 30, "poeira_luz_2")):
        a.prop(k, *P(u, v))

    # a Inscrição gasta: pedra pequena num canto da escadaria, fora da nave, com uma vela acesa ao lado
    px, py = round(gx + 9.8, 2), round(frente - 2.1, 2)
    a.prop("pedra_gasta_amenti", px, py, bloqueia=0.3)
    a.prop("velas_chao", round(px + .6, 2), round(py - .4, 2), chao=True)
    a.luzes.append([round(px + .6, 2), round(py - .4, 2), *QUENTE, 1.5])
    a.objetos.append({"kind": "leitura", "pos": [px, py], "nome": "Inscrição gasta", "visual": "pedra_gasta_amenti",
                      "texto": "\"Mesmo no fim do mundo, alguém acendeu uma vela para o próximo que viesse.\"\n— Dlauce, 2026"})
    # ao lado, outra pedra, mais nova e de letra funda (o texto vem do servidor)
    qx, qy = round(px + 1.4, 2), round(py + .7, 2)
    a.prop("pedra_gravada_amenti", qx, qy, bloqueia=0.3)
    a.objetos.append({"kind": "interativo", "obj": "inscricao_07", "tipo": "inscricao", "pos": [qx, qy], "nome": "Pedra Gravada",
                      "visual": "pedra_gravada_amenti", "texto_servidor": "inscricao_07"})
    # o Portão também se usa: não abre, mas alguém responde
    a.objetos.append({"kind": "interativo", "obj": "portao_amenti", "pos": [gx, round(frente - 2.0 / T, 2)], "visual": "portao_amenti_salao",
                      "nome": "O Portão de Amenti", "abre": False, "texto_ao_usar": "(Uma voz, de dentro, sem pressa: Quem bate?)"})

    for mob, u, motivo in (("guardiao_da_aurora", 8.5, "Guarda o lado da aurora do Portão; não ataca quem não o toca."),
                           ("guardiao_do_crepusculo", 31.5, "Guarda o lado do crepúsculo do Portão; não ataca quem não o toca.")):
        x, y = P(u, 36)
        a.spawns.append({"mob": mob, "pos": [x, y], "raio": 0.5, "qtd": 1, "nivel": 150, "postura": "neutro",
                         "temperamento": "neutro", "motivo": motivo})

    ex, ey = P(20, 0)
    a.prop("porta_selada_amenti", ex, ey - .5)
    a.objetos.append({"kind": "porta_selada", "pos": [ex, ey + 1.0], "visual": "porta_selada_amenti", "fecha_ao_entrar": True,
                      "nome": "A laje que se fecha", "texto": "A pedra desceu atrás de você. Daqui só se sai pelo fim."})
    a.luzes += [[ex, ey + 1.5, *ESM, 4]]
    return lugares, (gx, frente)


# ====================================================================== 7. A Sala do Juízo (atrás do Portão)
JUIZO = RET[7]                        # cela de frade, longe de tudo: não há passagem a pé, só o teleporte do servidor


def sala_do_juizo(a):
    import importlib.util
    spec = importlib.util.spec_from_file_location("textos_atlantida", os.path.join(os.path.dirname(AQUI), "atlantida", "textos.py"))
    tx = importlib.util.module_from_spec(spec); spec.loader.exec_module(tx)
    tabua = tx.TEXTOS["tabua_de_esmeralda"]
    x0, y0, x1, y1 = JUIZO
    abrir(a, x0, y0, x1, y1, "n", 7, nome="Sala do Juízo")
    # a Tábua inteira na parede do fundo (+Y), o espelho de obsidiana na parede de -X, a cadeira vazia olhando para ele
    a.prop("tabua_esmeralda_parede", 100.8, y1 + .85)
    a.objetos.append({"kind": "leitura", "obj": "tabua_de_esmeralda", "pos": [100.8, y1 - .3], "nome": tabua["nome"],
                      "texto": tabua["texto"], "visual": "tabua_esmeralda_parede"})
    a.prop("espelho_obsidiana", x0 + .45, 194.6, bloqueia=0.5)
    a.prop("cadeira_ibis", 100.1, 194.6, bloqueia=0.4)
    # a única saída: a porta de luz quente que dá no Egito, diante da Esfinge
    a.prop("portal_egito", 103.5, y1 + .85)
    a.portal(103.5, y1 - .2, "egito", [79.5, 129.0], "A porta de luz quente", visual="portal_egito")
    a.prop("poeira_luz_2", 101.5, 194.5)
    a.luzes += [[100.8, y1 - .4, *ESM, 3.5], [103.5, y1 - .6, *QUENTE, 3], [99.3, 194.6, *ESM, 1.8]]
    return [101.5, 194.0]


# ====================================================================== paredes por sala
def kit_de_parede(k, x, y):
    """Troca o kit de parede padrão (glifos) pelo da sala vizinha. Devolve a lista de props (pode ser vazia)."""
    base = "parede_glifos_amenti"
    if not k.startswith(base): return [k]
    suf = k[len(base):]                                   # _a, _b, _v2_a, _frente_a, _canto, _frente_canto...
    viz = [SALA_DE.get((int(x) + dx, int(y) + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))]
    salas = [v for v in viz if v is not None]
    n = max(set(salas), key=salas.count) if salas else 0
    if n == 1:
        return ["parede_livro_amenti" + suf] if suf in ("_a", "_b", "_v2_a", "_v2_b") else [k]
    if n == 2:
        return ["borda_astral_canto"] if "canto" in suf else ["borda_astral" + suf[-2:]]
    if n == 3:
        return []                                           # o Vazio não tem parede: a beira é o nada (a rocha vem da base_ilha)
    if n == 4:
        if suf in ("_a", "_b", "_v2_a", "_v2_b"):
            lado = suf[-2:]
            if (int(x) + int(y)) % 4 == 0: return ["parede_sombria_amenti_v2" + lado]           # tocha a cada quatro
            tema = ["", "_anubis", "_caes", "_grade", "_nicho", "_anubis"][zlib.crc32(f"c{x},{y}".encode()) % 6]
            return ["parede_sombria_amenti" + tema + lado]
        return ["parede_sombria_amenti" + suf]
    return [k]


def construir():
    SALA_DE.clear()
    a = G.Andar("saloes_de_amenti", "Salões de Amenti", W, H, "n", "parede_glifos_amenti",
                {"id": "saloes_de_amenti", "nome": "Salões de Amenti", "seguro": False, "nivel": [150, 150],
                 "musica": "musica/amenti", "ambiente": "ambiente/amenti"})
    chegada = vestibulo(a)
    universo(a)
    vazio(a)
    camaras(a)
    senhores = flor(a)
    lugares, (gx, gfrente) = antecamara(a)
    juizo = sala_do_juizo(a)
    for (x0, y0, x1, y1) in (RET[6], (57, 26, 62, 29), (57, 56, 62, 59), (57, 84, 62, 87), (57, 108, 62, 111), (57, 146, 62, 149)):
        manchas_de_pedra(a, x0, y0, x1, y1)
    a.paredes()
    props = []
    for p in a.props:
        k = p["k"]
        if k.startswith("sujeira_rodape"): continue                         # Amenti é limpo
        if k.startswith("parede_") and p["y"] > Y0 + LADO - .1 and X0 + 10 <= p["x"] <= X0 + 30: continue   # o Portão
        if k.startswith("parede_") and int(p["y"]) in (Y0 - 1, RET[1][1] - 1) and 55 <= p["x"] <= 65: continue   # as lajes
        for k2 in kit_de_parede(k, p["x"], p["y"]):
            q = dict(p); q["k"] = k2; props.append(q)
    a.props = props
    for p in props:                                          # cada tocha de parede das Câmaras deixa uma poça de luz no chão
        if p["k"].startswith("parede_sombria_amenti_v2_"):
            dx, dy = (0, -1.2) if p["k"].endswith("_a") else (1.2, 0)
            a.luzes.append([round(p["x"] + dx, 2), round(p["y"] + dy, 2), *ESM, 5])
    m = a.exportar(ceu={"escuro": 0.9, "cor": [0.42, 0.62, 0.52], "neblina": [0.02, 0.06, 0.05]}, spawn=list(chegada))
    m["lugares"] = dict(lugares, senhores_dos_ciclos=senhores, flor_da_vida=[60, 129], sala_do_juizo=juizo)
    m["salas_ordem"] = [dict({"n": n, "nome": NOMES[n], "ret": list(RET[n])}, **({"so_teleporte": True} if n == 7 else {})) for n in sorted(RET)]
    m["portao"] = {"pos": [gx, Y0 + LADO], "frente_do_estrado": round(gfrente, 2), "abre": False}
    m["sem_farm"] = True
    m["fundos"] = [{"sala": 3, "ret": list(RET[3]), "estrelas": 0.3, "nevoa_abismo": [0.05, 0.32, 0.2]},
                   {"sala": 4, "ret": list(RET[4]), "fumaca_baixa": [0.07, 0.085, 0.08]}]
    m["pendencias_jogo"] = PENDENCIAS_JOGO
    json.dump(m, open(os.path.join(AQUI, m["id"] + ".json"), "w"), ensure_ascii=False, separators=(",", ":"))
    return m


PENDENCIAS_JOGO = [
    "porta_selada: laje que fecha atrás ao entrar (Vestíbulo e Antecâmara); não reabre por dentro.",
    "leitura: mostrar nome + texto; estelas trocam visual -> visual_acesa quando o jogador chega a acende_raio e ficam acesas.",
    "armadilha placa_que_some: por célula, treme (aviso_s), some (some_s) em ciclo_s, defasada por célula; quem está em cima cai: perde pct_vida e volta para volta_para.",
    "armadilha vento: rajada de ativo_s a cada ciclo_s, empurra forca_tiles_s na direcao dentro da área; se empurrar para o vão, conta como queda.",
    "armadilha lamina: varre a área (eixo) a cada ciclo_s, aviso_s antes; acerto tira pct_vida.",
    "armadilha fogo_frio: jato por ativo_s a cada ciclo_s; pct_vida por segundo dentro da célula.",
    "spawns com rota/velocidade (arconte_de_luz), imovel (o_que_nao_tem_rosto). Os Senhores dos Ciclos são estátuas (parte do prop trono_senhor_N).",
    "interativo: tronos trono_senhor_1..9, portao_amenti (texto_ao_usar, não abre) e inscricao_07 (texto do servidor).",
    "sala_do_juizo: sem passagem a pé; o servidor teleporta para lugares.sala_do_juizo; o portal de lá leva ao egito [79.5, 129.0].",
    "respawn_s por grupo (cao_da_barreira: 1800 s, sem farm).",
    "props com pendurado=1 (base_ilha_*, laje_pendurada, lasca_abismo*): desenhar numa camada ABAIXO do chão de todas as ilhas, antes dos tiles, sem bloquear.",
    "props de sobreposição (poeira_luz, vento_vazio, anel_astral): sem bloquear e sem sombra.",
    "fundos: na sala 3 estrelas tênues ao fundo e névoa verde subindo do abismo; na sala 4 fumaça baixa (ver previa.py).",
    "armadilha_fogo (jato) e armadilha_fogo_parada: trocar conforme o ciclo; armadilha_lamina é o quadro do meio do golpe (animar o balanço).",
    "vão do Vazio: células bloqueadas sem piso são o nada (fundo preto), não parede.",
]


if __name__ == "__main__":
    m = construir()
    G.planta(m, os.path.join(AQUI, "planta_saloes_de_amenti.png"), "Salões de Amenti")
    print("lugares:", {k: v for k, v in m["lugares"].items() if k != "senhores_dos_ciclos"})
    print("guardiões:", [(s["mob"], s["pos"]) for s in m["spawns"] if s["mob"].startswith("guardiao")])
    print("spawns:", sorted({s["mob"] for s in m["spawns"]}), "armadilhas:", sum(1 for o in m["objetos"] if o["kind"] == "armadilha"))

"""Mata do Granizo (pedaço simples) + A Torre (5 andares). Pedido do Jefin, 11/10/2026:
"vamos começar a fazer a floresta, faz um pedaço acima simples, e a torre pra gente upar, coloca uns mobs 12+ lá até o 30".

Gera no MESMO formato de game/data/mapas/*.json (usa a classe Andar de design/mapas/cripta/gerar.py):
  mata_do_granizo.json          a mata, ligada ao norte do deserto (spots estilo MU, nível 12 a 22)
  torre_1.json ... torre_5.json os andares da Torre (horda + chefe, elevador sobe ao vencer), nível 18 a 30
  dados.json                    mobs (formato v06_extra), sprites substitutos (recolor), chefes, drops, ligação com o deserto
  planta_*.png                  plantas de cima para conferir
Uso: python3 gerar.py
"""
import json, math, os, random, sys, zlib
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "cripta"))
import gerar as G
G.AQUI = AQUI
Andar, porta_da_arena, planta = G.Andar, G.porta_da_arena, G.planta
G.COR_PISO.update({"f": (58, 50, 40), "e": (48, 60, 38), "z": (40, 38, 36), "p": (46, 56, 50), "k": (72, 66, 58),
                   "t": (82, 64, 46), "l": (88, 80, 70), "w": (50, 44, 36)})

FOGO = [1, 0.45, 0.15]; SEIVA = [1, 0.62, 0.25]; FRIO = [0.55, 0.62, 0.8]; SANTO = [1, 0.9, 0.6]

# ===================================================================================== mobs (variantes estilo MU)
# base = id de design/combate/mobs.json (o jogo herda tudo dela); usa/tint/escala = folha recolorida até ter arte própria
MOBS = {
    "lobo_de_cinza":          dict(nome="Lobo de Cinza", base="cao_de_vala", niveis=[12, 14], ajuste={"hp": 1.1}, tags=["animal"],
                                   usa="cao_de_vala", tint="#9a948c", escala=1.2, drop="mata_animal"),
    "corvo_de_brasa":         dict(nome="Corvo de Brasa", base="corvo_de_cinza", niveis=[12, 15], ajuste={"dano": 1.1}, tags=["animal", "voador"],
                                   res={"fogo": 0.3}, usa="corvo_de_cinza", tint="#e08a50", escala=1.15, drop="mata_animal"),
    "javali_brasa":           dict(nome="Javali-Brasa", base="porco_pestilento", niveis=[13, 16], ajuste={"hp": 1.2}, tags=["animal"],
                                   res={"fogo": 0.4}, usa="porco_pestilento", tint="#c07040", escala=1.1, drop="mata_animal"),
    "enxame_de_fagulhas":     dict(nome="Enxame de Fagulhas", base="fogo_de_vela", niveis=[15, 17], ajuste={}, tags=["espectro"],
                                   res={"fogo": 0.8, "gelo": -0.5}, usa="fogo_de_vela", tint="#ff7a2a", escala=0.9, drop="mata_arauto"),
    "legionario_desgarrado":  dict(nome="Legionário Desgarrado", base="soldado_caido", niveis=[16, 18], ajuste={"hp": 1.2, "dano": 1.1},
                                   tags=["demonio"], res={"fogo": 0.4, "sagrado": -0.3}, usa="soldado_escudeiro", tint="#b04a3a", escala=1.05, drop="mata_arauto"),
    "incendiaria_da_comunhao": dict(nome="Incendiária da Comunhão", base="carpideira_de_ossos", niveis=[16, 18], ajuste={"dano": 1.15},
                                   tags=["humano"], res={"fogo": 0.5}, usa="carpideira_de_ossos_viuva", tint="#e07a40", escala=1.0, drop="mata_arauto"),
    "cao_de_brasa":           dict(nome="Cão de Brasa da Legião", base="cao_de_vala", niveis=[17, 20], ajuste={"hp": 1.15, "dano": 1.15},
                                   tags=["animal", "demonio"], res={"fogo": 0.6}, usa="cao_de_vala_alfa", tint="#ff6a3a", escala=1.1, drop="mata_arauto"),
    "escudeiro_sem_hoste":    dict(nome="Escudeiro sem Hoste", base="soldado_caido", niveis=[18, 21], ajuste={"hp": 1.35}, tags=["celestial"],
                                   res={"sagrado": 0.5, "fogo": -0.2}, usa="soldado_escudeiro", tint="#e0d4b0", escala=1.1, drop="mata_arauto"),
    "enxerto_errado":         dict(nome="Enxerto Errado", base="monge_emparedado", niveis=[18, 21], ajuste={"hp": 1.3, "mov": 0.8},
                                   tags=["planta"], res={"fogo": -0.5, "veneno": 0.5}, usa="filho_de_cardo", tint="#8aa060", escala=1.2, drop="mata_animal"),
    "ent_de_cinza":           dict(nome="Ent-de-Cinza", base="capataz_gancho", niveis=[21, 22], ajuste={"hp": 1.6}, tags=["planta"],
                                   res={"fogo": -0.4, "fisico": 0.2}, usa="acougueiro_oco", tint="#6a6058", escala=1.6, drop="elite_mata"),
    # só na Torre
    "corista_da_torre":       dict(nome="Corista da Torre", base="eco_da_trombeta", niveis=[24, 26], ajuste={"hp": 1.2}, tags=["celestial", "espectro"],
                                   usa="corista_de_osso", tint="#c8a878", escala=1.0, drop="torre_horda"),
    "querubim_queimado":      dict(nome="Querubim Queimado", base="querubim_desfeito", niveis=[26, 28], ajuste={"hp": 1.2, "dano": 1.1},
                                   tags=["celestial", "voador"], res={"fogo": 0.5}, usa="querubim_desfeito", tint="#d07840", escala=1.0, drop="torre_horda"),
    "centuriao_sem_bandeira": dict(nome="Centurião sem Bandeira", base="acougueiro_oco", niveis=[27, 30], ajuste={"hp": 1.4, "dano": 1.2},
                                   tags=["demonio"], res={"fogo": 0.5, "sagrado": -0.3}, usa="capataz_gancho", tint="#a03a2a", escala=1.2, drop="torre_horda"),
    # 0.8.3: monstros NOVOS da thread "Monstros e chefes" (até a folha própria chegar, usam recolor)
    "vitral_andante":         dict(nome="Vitral Andante", base="querubim_desfeito", niveis=[22, 25], ajuste={"hp": 1.3}, tags=["celestial"],
                                   res={"sagrado": 0.5, "fisico": -0.2}, usa="vitral_andante", tint=None, escala=1.0, drop="mata_arauto"),
    "sapo_sacristao":         dict(nome="Sapo-Sacristão", base="porco_pestilento", niveis=[25, 28], ajuste={"hp": 1.45, "dano": 1.1}, tags=["animal"],
                                   res={"veneno": 0.5}, usa="sapo_sacristao", tint=None, escala=1.0, drop="mata_animal"),
    "bombardeiro_legiao":     dict(nome="Bombardeiro da Legião", base="gancheiro", niveis=[28, 30], ajuste={"hp": 1.5, "dano": 1.25}, tags=["demonio"],
                                   res={"fogo": 0.5, "sagrado": -0.3}, usa="bombardeiro_legiao", tint=None, escala=1.0, drop="mata_arauto"),
    # Novo Éden "Gênesis" (15/10): monstros novos com arte própria (tools/sprite-pipeline/monstros/cervo_de_lume.py,
    # querubim_da_espada.py, serpente_do_eden.py); a_serpente é a variante elite da serpente (estilo MU)
    "cervo_de_lume":          dict(nome="Cervo de Lume", base="cao_de_vala", niveis=[12, 14], ajuste={"hp": 1.15, "dano": .9, "mov": 1.1}, tags=["animal"],
                                   res={"sagrado": 0.2}, usa="cervo_de_lume", tint=None, escala=1.0, drop="mata_animal"),
    "querubim_da_espada":     dict(nome="Querubim da Espada", base="soldado_caido", niveis=[18, 22], ajuste={"hp": 1.3, "dano": 1.15},
                                   tags=["celestial"], res={"sagrado": 0.5, "fogo": 0.3}, usa="querubim_da_espada", tint=None, escala=1.0, drop="mata_arauto"),
    "serpente_do_eden":       dict(nome="Serpente do Éden", base="cao_de_vala", niveis=[24, 27], ajuste={"hp": 1.35, "dano": 1.25},
                                   tags=["animal", "demonio"], res={"veneno": 0.7, "sagrado": -0.3}, usa="serpente_do_eden", tint=None, escala=1.0, drop="mata_arauto"),
    "a_serpente":             dict(nome="A Serpente", base="cao_de_vala", niveis=[27, 27], ajuste={"hp": 2.2, "dano": 1.5},
                                   tags=["animal", "demonio"], res={"veneno": 0.8, "sagrado": -0.3}, usa="serpente_do_eden", tint="#c8ffb0", escala=1.6, drop="elite_mata"),
    # 0.8.3: Catacumba das Raízes (1 andar, embaixo da Árvore-Mãe; dungeon, toda agressiva)
    "raiz_ossuda":            dict(nome="Raiz Ossuda", base="filho_de_cardo", niveis=[18, 20], ajuste={"hp": 1.25}, tags=["planta"],
                                   res={"veneno": 0.4, "fogo": -0.4}, usa="filho_de_cardo", tint="#7fb8b0", escala=1.15, drop="catacumba"),
    "enterrado_florido":      dict(nome="Enterrado Florido", base="nao_julgado", niveis=[19, 21], ajuste={"hp": 1.3, "dano": 1.1},
                                   tags=["morto_vivo", "planta"], res={"veneno": 0.3}, usa="nao_julgado", tint="#9cc8b0", escala=1.08, drop="catacumba"),
    "envenenador_da_comunhao": dict(nome="Envenenador da Comunhão", base="carpideira_de_ossos", niveis=[20, 22], ajuste={"dano": 1.2},
                                   tags=["humano"], res={"veneno": 0.6}, usa="carpideira_de_ossos", tint="#78c058", escala=1.0, drop="catacumba"),
}
MOTIVO = {
    "lobo_de_cinza": "voltaram a caçar quando a mata voltou a ter bicho",
    "corvo_de_brasa": "comem o granizo de sangue e o que os Arautos deixam",
    "javali_brasa": "fuçam as raízes quentes das bordas; guardam a toca",
    "enxame_de_fagulhas": "nascem dos tocos em brasa em volta do lago",
    "legionario_desgarrado": "remanescentes da Legião queimando a mata nova",
    "incendiaria_da_comunhao": "a Comunhão põe fogo nos enxertos: a 1ª trombeta tocou, o que queimou tem de ficar queimado",
    "cao_de_brasa": "rastreiam o restaurador para a Torre",
    "escudeiro_sem_hoste": "anjos sem hoste vigiando a estrada da Torre",
    "enxerto_errado": "brotaram em cima de mortos e saíram andando",
    "ent_de_cinza": "só acorda se mexerem na árvore dele",
    "querubim_queimado": "caíram do topo da Torre quando o braseiro acendeu",
    "corista_da_torre": "cantam o versículo do fogo para chamar o granizo",
    "centuriao_sem_bandeira": "o que sobrou da Legião guarda o acampamento perto da Torre",
    "vitral_andante": "os vitrais da capela do Coro se levantaram quando a mata acendeu",
    "sapo_sacristao": "bebeu o sangue dos querubins caídos no charco",
    "bombardeiro_legiao": "bombardeia a mata nova a partir do acampamento",
    "cervo_de_lume": "pastam no verde de Havilá; os chifres acendem à noite e só reagem se atacados",
    "querubim_da_espada": "querubins do Coro postos ao oriente do jardim para guardar o caminho da Árvore da Vida; ainda guardam",
    "serpente_do_eden": "crias da Serpente, enroscadas nas raízes da Clareira do Conhecimento",
    "a_serpente": "a mais astuta de todos os animais: enrolada na Árvore do Conhecimento, espera alguém provar do fruto",
    "raiz_ossuda": "a raiz da Árvore-Mãe abraçou os ossos que Simão enterrou e agora defende a cova",
    "enterrado_florido": "mortos que Simão enterrou; floriram no lacre de cera e não deixam ninguém descer",
    "envenenador_da_comunhao": "a Comunhão desceu para derramar Amargo na raiz e matar a Árvore-Mãe por baixo",
}

# ===================================================================================== a mata
ZONAS = [  # id, nome, seguro, nível, piso
    ("linha_de_cinza", "Linha de Cinza", False, [12, 13], "z"),
    ("viveiro", "O Viveiro", True, None, "e"),
    ("bordas_queimadas", "Bordas Queimadas", False, [12, 16], "f"),
    ("lago_de_granizo", "Lago de Granizo", False, [15, 17], "e"),
    ("frente_de_queimada", "Frente de Queimada", False, [16, 18], "z"),
    ("fundo_da_mata", "Fundo da Mata", False, [18, 22], "e"),
    ("estrada_da_torre", "Estrada da Torre", False, [20, 22], "k"),
    ("coracao_da_mata", "Coração da Mata", False, [22, 30], "e"),
]
# x, y, raio, zona, spot (id, nome, nível, [(mob, qtd)], temperamento)
BLOBS = [
    (72, 86, 7, 0, None),
    (60, 71, 8, 1, None),
    (84, 63, 9, 2, ("clareira_dos_lobos", "Clareira dos Lobos", [12, 14], [("lobo_de_cinza", 2), ("corvo_de_brasa", 2)], "neutro")),
    (40, 81, 9, 2, ("toca_dos_javalis", "Toca dos Javalis", [13, 15], [("javali_brasa", 2), ("corvo_de_brasa", 2)], "territorial")),
    (64, 45, 9, 3, ("lago_de_granizo", "Lago de Granizo", [15, 17], [("enxame_de_fagulhas", 2), ("lobo_de_cinza", 2)], "neutro")),
    (37, 57, 10, 4, ("frente_de_queimada", "Frente de Queimada", [16, 18], [("legionario_desgarrado", 3), ("incendiaria_da_comunhao", 3)], "agressivo")),
    (42, 33, 10, 5, ("bosque_dos_enxertos", "Bosque dos Enxertos Errados", [18, 20], [("enxerto_errado", 2), ("escudeiro_sem_hoste", 2)], "neutro")),
    (77, 25, 9, 5, ("clareira_do_ent", "Clareira do Ent", [19, 21], [("enxerto_errado", 2), ("cao_de_brasa", 2)], "neutro")),
    (24, 21, 7, 6, ("estrada_da_torre", "Estrada da Torre", [20, 22], [("escudeiro_sem_hoste", 2), ("cao_de_brasa", 2)], "neutro")),
    (14, 11, 6, 6, None),
    # 0.8.3 (Jefin: "Novo Éden levará o player até o lvl 30"): 3 spots no fundo, perto da Torre, do 22 ao 30
    (52, 14, 8, 7, ("ruinas_do_coro", "Ruínas do Coro", [22, 25], [("vitral_andante", 2), ("legionario_desgarrado", 2)], "neutro")),
    (90, 42, 8, 7, ("charco_dos_querubins", "Charco dos Querubins", [25, 28], [("querubim_queimado", 2), ("sapo_sacristao", 2)], "neutro")),
    (27, 40, 8, 7, ("acampamento_da_legiao", "Acampamento da Legião", [28, 30], [("centuriao_sem_bandeira", 2), ("bombardeiro_legiao", 2)], "territorial")),
]
ARESTAS = [(0, 1), (1, 2), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5), (4, 7), (5, 6), (4, 6), (6, 8), (7, 6), (8, 9),
           (6, 10), (7, 10), (2, 11), (7, 11), (6, 12), (5, 12)]
ENTRADA_DESERTO = [87.5, 24.5]      # onde fica a passagem no area_inicial (fresta aberta na borda norte)
CHEGADA_DESERTO = [87.5, 27.5]      # onde o jogador aparece ao voltar
SPAWN_MATA = [72.5, 84.5]
PORTA_TORRE = [15.5, 13.5]          # entrada da Torre na mata
CHEGADA_TORRE = [16.5, 15.5]        # onde o jogador aparece ao sair da Torre
ARVORE_MAE = [55.5, 77.0]           # a sequoia oca da Enxertia, no fundo do Viveiro (atrás na tela, não tampa a vila)
PORTA_CATACUMBA = [57.5, 75.0]      # o arco aceso entre as raízes, na frente da árvore
CHEGADA_CATACUMBA = [58.5, 74.0]    # onde o jogador aparece ao sair da catacumba
CHEGADA_CATACUMBA_DENTRO = [8.5, 24.5]
LUME = [0.1, 0.85, 1.0]
VIVAS = {1, 3, 5, 7}                 # zonas do miolo vivo (Viveiro, Lago, Fundo, Coração): musgo aceso, árvores de lume


def ruido(x, y, s=0.0):
    return (.5*math.sin(x*.37 + y*.21 + s) + .3*math.sin(x*.13 - y*.29 + 1.7 + s) + .2*math.sin(x*.71 + y*.53 + 2.9*s))


def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)


def mata():
    """Novo Éden "Gênesis" (15/10/2026): o gerador novo está em eden_mapa.py (quatro rios, Nascente, Portão do Oriente)."""
    import eden_mapa
    return eden_mapa.mata()


# ===================================================================================== A Torre
ANDARES = [  # nome, piso, parede, nível, chefe, horda (ondas), tema
    ("Casa de Máquinas", "m", "parede_matadouro", [12, 15], "centuriao_ferrabras",
     [{"legionario_desgarrado": 3}, {"cao_de_brasa": 3}, {"legionario_desgarrado": 2, "cao_de_brasa": 2}], "maquinas"),
    ("Depósito de Sementes", "o", "parede_ossario", [16, 19], "madre_brasilia",
     [{"incendiaria_da_comunhao": 3}, {"enxame_de_fagulhas": 4}, {"incendiaria_da_comunhao": 2, "legionario_desgarrado": 2}], "sementes"),
    ("Sala do Rádio", "n", "parede_matadouro", [20, 23], "o_telegrafista",
     [{"corista_da_torre": 3}, {"escudeiro_sem_hoste": 3}, {"corista_da_torre": 2, "escudeiro_sem_hoste": 2}], "radio"),
    ("Mirante de Incêndio", "j", "parede_trombeta", [24, 27], "malaquias_escudeiro_cego",
     [{"querubim_queimado": 3}, {"escudeiro_sem_hoste": 3, "cao_de_brasa": 1}, {"querubim_queimado": 2, "centuriao_sem_bandeira": 1}], "mirante"),
    ("O Braseiro", "l", "parede_trombeta", [28, 30], "baraquiel_arauto_do_granizo",
     [{"centuriao_sem_bandeira": 2, "legionario_desgarrado": 2}, {"incendiaria_da_comunhao": 3, "querubim_queimado": 2},
      {"corista_da_torre": 2, "escudeiro_sem_hoste": 2, "centuriao_sem_bandeira": 1}], "braseiro"),
]
CHEGADA_ANDAR = [11.5, 25.5]
FASE2 = "fase2" in sys.argv   # fase 2: a mata entra no jogo e a Torre passa a ficar dentro dela
SAIDA, SAIDA_CHEGADA = ("mata_do_granizo", CHEGADA_TORRE) if FASE2 else ("area_inicial", CHEGADA_DESERTO)


def torre(n):
    nome, piso, parede, niv, chefe_id, ondas, tema = ANDARES[n - 1]
    a = Andar(f"torre_{n}", f"A Torre · {n}º andar · {nome}", 58, 52, piso, parede,
              {"id": f"torre_{n}", "nome": f"A Torre · {nome}", "seguro": False, "nivel": niv,
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_porao" if n < 4 else "ambiente/cripta_camara"})
    a.sala(7, 21, 15, 30, nome="Patamar do elevador")
    a.corredor(16, 23, 19, 28)
    a.sala(20, 12, 41, 39, nome=nome)
    for (x, y) in [(20, 12), (21, 12), (20, 13), (41, 12), (40, 12), (41, 13), (20, 39), (21, 39), (20, 38), (41, 39), (40, 39), (41, 38)]:
        a.fechar(x, y)
    a.corredor(42, 23, 45, 28)
    a.sala(46, 21, 52, 30, nome="Elevador de carga")
    cx, cy, r = 31.0, 26.0, 9.5
    # ---- patamar de chegada: a gaiola que trouxe o jogador
    a.prop("gaiola_suspensa", 9.5, 23.0, bloqueia=.9)
    a.prop("braseiro_ferro", 13.5, 29.0, bloqueia=.4, luz=FOGO + [6])
    a.luzes.append([11, 25, 1, .8, .5, 5])
    if n == 1:
        a.portal(8.5, 27.5, SAIDA, SAIDA_CHEGADA, "Sair da Torre", visual="escada_subida")
    else:
        a.portal(8.5, 27.5, SAIDA, SAIDA_CHEGADA, "Elevador · descer e sair da Torre", visual="escada_subida")
    # ---- arena: tema do andar
    if tema == "maquinas":
        for (x, y) in [(23.5, 15.5), (38.5, 15.5)]: a.prop("caldeira_vapor", x, y, bloqueia=1.2, luz=FOGO + [6])
        a.prop("moedor_vapor", 38.0, 36.0, bloqueia=1.0); a.prop("canos_parede", 30.5, 13.0, bloqueia=.5)
        a.espalhar(["pilha_carvao", "barris", "caixas"], 5, (21, 13, 40, 38), chao=False, bloq=.5, dist=4)
    elif tema == "sementes":
        a.espalhar(["sacos_sal", "caixas", "barris"], 9, (21, 13, 40, 38), chao=False, bloq=.5, dist=3.5)
        a.espalhar(["folhas_papeis"], 8, (21, 13, 40, 38))
        for (x, y) in [(23.5, 15.5), (38.5, 36.5)]: a.prop("tonel_fogo", x, y, bloqueia=.4, luz=FOGO + [5])
    elif tema == "radio":
        a.prop("bancada_ferreiro", 24.0, 14.5, bloqueia=.6); a.prop("lampada_arco", 38.0, 15.0, bloqueia=.4, luz=FRIO + [7])
        for (x, y) in [(23.0, 35.0), (39.0, 35.0)]: a.prop("poste_telegrafo", x, y, bloqueia=.3)
        a.espalhar(["folhas_papeis", "caixas"], 10, (21, 13, 40, 38), dist=2.5)
    elif tema == "mirante":
        for y in (16.5, 35.5):
            for x in (24.5, 37.5): a.prop("pilar_porcelana", x, y, bloqueia=.7)
        a.prop("estandarte_rasgado", 30.5, 13.5, bloqueia=.3); a.prop("anjo_porcelana_caido", 25.5, 26.0, bloqueia=.8)
        a.espalhar(["penas_espalhadas", "folhas_papeis"], 8, (21, 13, 40, 38))
    else:
        a.prop("braseiro_sagrado", cx + 4.0, cy - 4.0, bloqueia=1.2, luz=[1, .4, .12, 11])
        for ang in range(0, 360, 60):
            t = math.radians(ang); a.prop("pilar_porcelana", cx + 7.5*math.cos(t), cy + 7.5*math.sin(t), bloqueia=.7)
        a.espalhar(["penas_espalhadas", "ossos_espalhados"], 10, (21, 13, 40, 38))
    for ang in range(0, 360, 60):
        t = math.radians(ang + 30); a.luzes.append([round(cx + 8*math.cos(t), 2), round(cy + 8*math.sin(t), 2), 1, .55, .25, 4])
    porta = porta_da_arena(a, cx, cy, r)
    # ---- saída: elevador de carga (só funciona depois do chefe)
    a.prop("gaiola_suspensa", 50.5, 23.5, bloqueia=.9); a.prop("guindaste_sucata", 51.0, 29.0, bloqueia=1.0)
    a.luzes.append([49, 26, 1, .8, .5, 5])
    a.prop("bau_chefe", 48.0, 28.5)
    a.objetos.append({"kind": "bau", "pos": [48.0, 28.5], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": chefe_id, "id_mapa": f"bau_torre_{n}"})
    if n < 5:
        a.portal(49.5, 25.5, f"torre_{n + 1}", CHEGADA_ANDAR, f"Elevador · subir ao {n + 1}º andar", visual="escada_subida",
                 requer_flag=f"venceu_{chefe_id}", texto_trancado="A gaiola está acorrentada. A chave está com quem manda neste andar.")
    else:
        a.portal(49.5, 25.5, SAIDA, SAIDA_CHEGADA, "Elevador · descer e sair da Torre", visual="escada_subida",
                 requer_flag=f"venceu_{chefe_id}", texto_trancado="O braseiro ainda queima. O Arauto não deixa ninguém descer.")
    a.paredes()
    pontos = [[cx - 7, cy - 7], [cx + 7, cy - 7], [cx - 7, cy + 7], [cx + 7, cy + 7]]
    return a.exportar(chefe={"id": chefe_id, "pos": [cx + 6, cy], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta,
                             "horda": {"ondas": ondas, "nivel": niv, "pontos": pontos, "pausa_s": 3.0, "chefe_depois": True}},
                      ceu={"escuro": 0.8, "cor": [0.72, 0.56, 0.42], "neblina": [0.12, 0.08, 0.05]}, spawn=CHEGADA_ANDAR)


# ===================================================================================== Catacumba das Raízes (0.8.3)
def catacumba():
    """Um andar embaixo da Árvore-Mãe: as covas que Simão cavou, abraçadas pela raiz. A Comunhão desceu para
    derramar Amargo na raiz-mestra e matar a árvore por baixo. Dungeon: toda agressiva, grupos de 3, sem renascer rápido."""
    niv = [18, 22]
    a = Andar("catacumba_das_raizes", "Catacumba das Raízes", 70, 48, "o", "parede_gotica",   # gótico inglês (kit do Cenário)
              {"id": "catacumba_das_raizes", "nome": "Catacumba das Raízes", "seguro": False, "nivel": niv,
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_camara"})
    a.sala(4, 19, 12, 29, nome="Escada das Raízes")
    a.corredor(13, 22, 16, 26)
    a.sala(17, 12, 29, 36, nome="Ossário das Raízes")
    a.corredor(22, 8, 24, 11); a.sala(19, 3, 27, 7, nome="Nicho do Primeiro Enterro")
    a.corredor(22, 37, 24, 39); a.sala(19, 40, 27, 44, nome="Covas sem Nome")
    a.corredor(30, 22, 32, 26)
    a.sala(33, 15, 40, 33, nome="Poço do Amargo")
    a.corredor(41, 22, 43, 26)
    a.sala(44, 14, 63, 33, nome="A Raiz-Mestra")
    for (x, y) in [(44, 14), (45, 14), (44, 15), (63, 14), (62, 14), (63, 15), (44, 33), (45, 33), (44, 32), (63, 33), (62, 33), (63, 32)]:
        a.fechar(x, y)
    a.pisar(35, 21, 38, 27, "w")                       # a poça de Amargo no meio do Poço
    cx, cy, r = 54.0, 24.0, 8.5
    # ---- escada de chegada: raízes descendo pela parede, lanternas de seiva da Enxertia
    a.portal(6.5, 22.5, "mata_do_granizo", CHEGADA_CATACUMBA, "Subir para o Novo Éden", visual="escada_subida")
    for (x, y) in [(5.5, 27.5), (11.5, 20.5)]: a.prop("lanterna_procissao", x, y, bloqueia=.2, luz=SEIVA + [5])
    a.luzes.append([9, 24, .3, .85, 1.0, 5])
    # ---- ossário: ossos nas paredes, raízes com flor acesa
    a.espalhar(["ossos_espalhados", "folhas_papeis"], 10, (18, 13, 28, 35))
    a.espalhar(["tumulo_vitoriano", "lapide_vitoriana", "lapide_obelisco", "lapide_cruz_vitoriana"], 7, (18, 13, 28, 35), chao=False, bloq=.5, dist=3.5)
    for (x, y) in [(20.5, 24.5), (26.5, 24.5)]: a.prop("lampiao_gas", x, y, bloqueia=.3, luz=[1, .66, .36, 5])
    a.prop("grade_ferro_batido_a", 23.0, 11.6, bloqueia=0); a.prop("grade_ferro_batido_a", 23.0, 37.4, bloqueia=0)
    for (x, y) in [(18.5, 13.5), (28.5, 13.5), (18.5, 35.5), (28.5, 35.5)]: a.luzes.append([x, y, .1, .85, 1.0, 4])
    a.spawn("raiz_ossuda", 21.5, 17.5, qtd=3, nivel=18); a.spawn("enterrado_florido", 25.5, 30.5, qtd=3, nivel=19)
    a.spawn("raiz_ossuda", 23.0, 5.0, qtd=3, nivel=19); a.spawn("enterrado_florido", 23.0, 42.0, qtd=3, nivel=20)
    for (x, y, b, vis, idm) in [(25.5, 4.5, "bau_de_ferro", "bau_raro", "catacumba_nicho"), (20.5, 42.5, "caixote_podre", "bau_comum", "catacumba_covas")]:
        a.prop(vis, x, y); a.objetos.append({"kind": "bau", "pos": [x, y], "bau": b, "visual": vis, "id_mapa": idm})
    # ---- poço do Amargo: o acampamento dos envenenadores
    for (x, y) in [(34.5, 16.5), (39.5, 31.5)]: a.prop("tonel_fogo", x, y, bloqueia=.4, luz=FOGO + [5])
    a.espalhar(["barris", "sacos_sal"], 5, (34, 16, 39, 32), chao=False, bloq=.5, dist=3)
    a.luzes.append([36.5, 24.5, .45, 1.0, .3, 6])      # o verde do Amargo na poça
    a.spawn("envenenador_da_comunhao", 36.5, 18.5, qtd=3, nivel=21); a.spawn("envenenador_da_comunhao", 37.5, 30.0, qtd=2, nivel=21)
    a.spawn("raiz_ossuda", 39.0, 24.5, qtd=2, nivel=21)
    # ---- a raiz-mestra (arena): a raiz que segura a árvore inteira, com o chefe cavando
    a.prop("arvore_morta_grande", cx + 5.5, cy - .5, bloqueia=1.6, escala=1.4)
    a.espalhar(["ossos_espalhados", "lapide_cruz_vitoriana"], 10, (45, 15, 62, 32))
    for ang in range(0, 360, 60):
        t = math.radians(ang + 30); a.luzes.append([round(cx + 7*math.cos(t), 2), round(cy + 7*math.sin(t), 2), .1, .85, 1.0, 4])
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 60.5, 30.0)
    a.objetos.append({"kind": "bau", "pos": [60.5, 30.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "requer_chefe": "bento_fel", "id_mapa": "bau_catacumba"})
    a.portal(60.5, 18.5, "mata_do_granizo", CHEGADA_CATACUMBA, "Subir pela raiz para o Novo Éden", visual="portal_dungeon_lume",
             requer_flag="venceu_bento_fel", texto_trancado="A raiz não deixa passar enquanto o Amargo escorre por ela.")
    a.paredes()
    # ~30% das paredes de trás viram a variante com arco Tudor e lampião a gás aceso (cada uma com luz)
    ult = None
    for p in a.props:
        k = p["k"]
        if k in ("parede_gotica_a", "parede_gotica_b"):
            if zlib.crc32(f"cat{p['x']},{p['y']}".encode()) % 10 < 4 and ult != (p["x"], p["y"]):
                p["k"] = k.replace("parede_gotica", "parede_gotica_v2")
                a.luzes.append([p["x"], p["y"], 1, .66, .36, 5])
                ult = (p["x"] + (1 if k.endswith("_a") else 0), p["y"] + (0 if k.endswith("_a") else 1))
    m = a.exportar(chefe={"id": "bento_fel", "pos": [cx + 3, cy], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta},
                   ceu={"escuro": 0.3, "cor": [0.95, 0.92, 0.85], "neblina": [0.1, 0.1, 0.1]}, spawn=CHEGADA_CATACUMBA_DENTRO)
    for sp in m["spawns"]:
        sp.update({"temperamento": "agressivo", "motivo": MOTIVO[sp["mob"]]})
    json.dump(m, open(f"{AQUI}/catacumba_das_raizes.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return m


# ===================================================================================== chefes (formato design/combate/chefes.json)
def chefe(nome, andar, nivel, tags, res, fases, fala, conceito, drop):
    # HP linear no nivel (revisao de balanceamento 2026-10-15): 26*L^2 deixava o ultimo andar com 4 a 8 min de luta solo
    # e o Anjo batia na furia (360 s). 350*L da cerca de 150 s para a classe media; o andar 5 tem 15% a mais (170 s).
    hp = 350*nivel if andar < 5 else 400*nivel
    return {"nome": nome, "andar": andar, "nivel": nivel, "tags": tags, "hp": hp, "defesa": 2*nivel + 4,
            "dano_base": 2*nivel + 12, "intervalo_ataque": 1.8, "velocidade_mov": 2.2, "postura_max": 300 + 10*nivel, "res": res,
            "duracao_alvo_s": 150 if andar < 5 else 170, "furia_tempo_s": 360, "dungeon": "a_torre", "conceito": conceito, "fala_entrada": fala,
            "fases": fases, "drop": drop}


def F(nn, hp, nome, ataques): return {"n": nn, "hp": hp, "nome": nome, "ataques": ataques}


CHEFES = {
    "centuriao_ferrabras": chefe("Centurião Ferrabrás", 1, 15, ["demonio", "infernal"], {"fogo": 0.4, "sagrado": -0.3}, [
        F(1, [1.0, 0.5], "A Corrente", [{"id": "golpe_de_corrente", "mult": 1.0, "preparo": 0.6, "alcance": 1.9},
                                         {"id": "giro_de_corrente", "mult": 1.5, "preparo": 0.9, "telegrafo": {"forma": "circulo", "raio": 3.2}, "recarga": 8},
                                         {"id": "arrasto", "nome": "Puxão de Corrente", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "linha", "comprimento": 6, "largura": 1.2}, "deslocamento": 5, "recarga": 10}]),
        F(2, [0.5, 0.0], "Soltem os Cães", [{"id": "giro_de_corrente", "recarga": 6}, {"id": "chamar_caes", "invoca": {"cao_de_brasa": 2}, "uma_vez": True}])],
        "Quem acorrentou o elevador fui eu. Quer subir? Paga o pedágio.",
        "Centurião da Legião Blasfema que perdeu a bandeira na Batalha do Impasse; acorrentou a gaiola de carga e cobra pedágio em carne.", "chefe_torre_1"),
    "madre_brasilia": chefe("Madre Brasília da Comunhão", 2, 19, ["humano", "cultista"], {"fogo": 0.6, "gelo": -0.3}, [
        F(1, [1.0, 0.5], "Incenso", [{"id": "pavio", "mult": 1.0, "preparo": 0.6, "alcance": 1.6},
                                      {"id": "vomito_de_brasa", "nome": "Sopro de Incenso", "mult": 1.3, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 4.5, "angulo": 60}, "ticks": 3, "intervalo_tick": 0.4, "recarga": 9},
                                      {"id": "semente_ardente", "mult": 1.4, "preparo": 1.0, "telegrafo": {"forma": "circulo", "raio": 2.6}, "rastro_fogo": {"duracao": 4}, "recarga": 7}]),
        F(2, [0.5, 0.0], "Tudo Vira Cinza", [{"id": "semente_ardente", "recarga": 5}, {"id": "chamar_incendiarias", "invoca": {"incendiaria_da_comunhao": 2}, "uma_vez": True}])],
        "Cada semente que vocês plantam eu queimo como incenso. O cheiro sobe direto para o Coro.",
        "Madre da Comunhão do Amargo que queima o banco de sementes da Enxertia, uma por uma, como oração.", "chefe_torre_2"),
    "o_telegrafista": chefe("O Telegrafista", 3, 23, ["humano", "cultista"], {"eletrico": 0.6, "fisico": -0.2}, [
        F(1, [1.0, 0.5], "Ponto e Traço", [{"id": "chave_de_telegrafo", "mult": 1.0, "preparo": 0.6, "alcance": 1.6},
                                            {"id": "linha_de_telegrafo", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 9, "largura": 1.0}, "recarga": 7},
                                            {"id": "estatica", "mult": 1.2, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 5, "angulo": 80}, "efeito": {"silenciado": 2}, "recarga": 10}]),
        F(2, [0.5, 0.0], "Versículo em Loop", [{"id": "linha_de_telegrafo", "recarga": 5}, {"id": "chamar_coristas", "invoca": {"corista_da_torre": 2}, "uma_vez": True}])],
        "...--- ...--- Ouvinte: o fogo vem. O fogo vem. O fogo vem.",
        "Cultista que tomou o rádio de vigia da torre e transmite o versículo da 1ª trombeta em loop há onze mil noites; responde à Rádio São Lázaro.", "chefe_torre_3"),
    "malaquias_escudeiro_cego": chefe("Malaquias, o Escudeiro Cego", 4, 27, ["celestial", "anjo"], {"sagrado": 0.6, "fogo": 0.2, "trevas": -0.3}, [
        F(1, [1.0, 0.5], "O Mirante", [{"id": "escudo_de_vigia", "mult": 1.0, "preparo": 0.6, "alcance": 1.9},
                                        {"id": "marca_do_juizo", "nome": "Olhar que Arde", "mult": 1.6, "preparo": 1.6, "telegrafo": {"forma": "circulo", "raio": 1.8}, "recarga": 8},
                                        {"id": "investida_de_escudo", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "linha", "comprimento": 6, "largura": 1.6}, "recarga": 9}]),
        F(2, [0.5, 0.0], "Ele Não Vê, Ele Ouve", [{"id": "marca_do_juizo", "recarga": 5}, {"id": "chamar_querubins", "invoca": {"querubim_queimado": 2}, "uma_vez": True}])],
        "Trinta e um anos olhando o fogo daqui de cima. Fiquei cego. Mas o seu passo eu ouço.",
        "Escudeiro do Coro deixado de vigia no mirante de incêndio; olhou para a mata queimando até cegar e ainda guarda a escada do topo.", "chefe_torre_4"),
    "baraquiel_arauto_do_granizo": chefe("Baraquiel, o Arauto do Granizo", 5, 30, ["celestial", "anjo"], {"sagrado": 0.6, "fogo": 0.5, "gelo": 0.3}, [
        F(1, [1.0, 0.65], "A Primeira Nota", [{"id": "lamina_de_granizo", "mult": 1.0, "preparo": 0.6, "alcance": 2.0},
                                               {"id": "lanca_do_juizo", "nome": "Lança de Granizo", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 8, "largura": 1.2}, "recarga": 7},
                                               {"id": "pranto_que_cai", "nome": "Granizo e Fogo", "mult": 1.2, "quantidade": 4, "intervalo": 0.5, "preparo": 0.8, "telegrafo": {"forma": "circulo", "raio": 1.4}, "recarga": 9}]),
        F(2, [0.65, 0.3], "Misturado com Sangue", [{"id": "lanca_do_juizo", "dupla": True, "angulo_entre": 35, "recarga": 6}, {"id": "pranto_que_cai", "quantidade": 6},
                                                   {"id": "chamar_escudeiros", "invoca": {"escudeiro_sem_hoste": 2}, "uma_vez": True}]),
        F(3, [0.3, 0.0], "Um Terço das Árvores", [{"id": "marca_do_juizo", "nome": "Nota Final", "mult": 2.0, "preparo": 1.8, "telegrafo": {"forma": "circulo", "raio": 2.4}, "recarga": 8},
                                                  {"id": "pranto_que_cai", "quantidade": 8, "recarga": 7}])],
        "Eu toquei a primeira. Um terço das árvores queimou. Ele plantou de novo? Então eu toco de novo.",
        "O anjo que tocou a 1ª trombeta sobre a mata. Ficou no topo da Torre depois da Retirada, alimentando o braseiro para chamar o granizo outra vez sobre o que o Desertor do Coro replanta.", "chefe_torre_5"),
}

CHEFES["bento_fel"] = dict(chefe("Bento Fel, o Coveiro do Amargo", 1, 22, ["humano", "cultista"], {"veneno": 0.6, "fogo": -0.2}, [
    F(1, [1.0, 0.5], "A Pá", [{"id": "golpe_de_pa", "mult": 1.0, "preparo": 0.6, "alcance": 1.8},
                               {"id": "arrasto", "nome": "Pá que Puxa", "mult": 1.3, "preparo": 0.9, "telegrafo": {"forma": "linha", "comprimento": 6, "largura": 1.2}, "deslocamento": 4, "recarga": 9},
                               {"id": "vomito_de_brasa", "nome": "Jorro de Amargo", "mult": 1.2, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 4.5, "angulo": 60}, "ticks": 3, "intervalo_tick": 0.4, "recarga": 8}]),
    F(2, [0.5, 0.0], "A Raiz Grita", [{"id": "pranto_que_cai", "nome": "Chuva de Terra", "mult": 1.1, "quantidade": 5, "intervalo": 0.5, "preparo": 0.8, "telegrafo": {"forma": "circulo", "raio": 1.4}, "recarga": 8},
                                      {"id": "chamar_raizes", "invoca": {"raiz_ossuda": 2}, "uma_vez": True}])],
    "Ele enterra, a coisa brota. Eu desenterro, a coisa morre. Alguém tem de fazer o serviço ao contrário.",
    "Coveiro da Comunhão do Amargo que inveja o dom de Simão: cava por baixo da Árvore-Mãe e derrama Amargo na raiz-mestra para matá-la de dentro.",
    "chefe_catacumba"), dungeon="catacumba_das_raizes")

SPR_CHEFES = {
    "bento_fel": {"usa": "acougueiro_oco", "escala": 1.45, "tint": "#7ab060"},
    "centuriao_ferrabras": {"usa": "capataz_gancho", "escala": 1.5, "tint": "#c04a30"},
    "madre_brasilia": {"usa": "cultista", "escala": 1.4, "tint": "#ff9050"},
    "o_telegrafista": {"usa": "monge_emparedado", "escala": 1.45, "tint": "#9ab8c8"},
    "malaquias_escudeiro_cego": {"usa": "anjo", "escala": 1.5, "tint": "#b8aa90"},
    "baraquiel_arauto_do_granizo": {"usa": "anjo", "escala": 1.75, "tint": "#ff7050"},
}

DROPS = {
    "mata_animal": {"item_chance": 0.16, "rolagens": [{"tag": "material:pena_suja", "peso": 35}, {"tag": "equip:faixa2", "peso": 55}, {"tag": "joia:refino", "peso": 10}]},
    "mata_arauto": {"item_chance": 0.2, "rolagens": [{"tag": "equip:faixa2", "peso": 80}, {"tag": "joia:refino", "peso": 20}]},
    "elite_mata": {"rolagens_garantidas": 2, "raridade_minima": "magico", "ouro_mult": 8, "rolagens": [{"tag": "equip:faixa2", "peso": 80}, {"tag": "joia:refino", "peso": 20}]},
    "torre_horda": {"item_chance": 0.22, "rolagens": [{"tag": "equip:faixa2", "peso": 78}, {"tag": "joia:refino", "peso": 22}]},
}
DROPS["catacumba"] = {"item_chance": 0.22, "rolagens": [{"tag": "equip:faixa2", "peso": 78}, {"tag": "joia:refino", "peso": 22}]}
DROPS["chefe_catacumba"] = {"rolagens_garantidas": 3, "raridade_minima": "raro", "ouro_mult": 18,
                            "rolagens": [{"tag": "equip:faixa2", "peso": 80}, {"tag": "joia:refino", "peso": 20}]}
for i in range(1, 6):
    DROPS[f"chefe_torre_{i}"] = {"rolagens_garantidas": 3 + (i >= 3) + (i == 5), "raridade_minima": "raro", "ouro_mult": 15 + 5*i,
                                 "rolagens": [{"tag": "equip:faixa2", "peso": 76 - 2*i}, {"tag": "joia:refino", "peso": 18}] + ([{"tag": "lendario:zacarias", "peso": 2*i + 4}] if i >= 4 else [])}


def dados():
    mobs, spr = {}, {}
    for k, v in MOBS.items():
        d = {x: v[x] for x in ("nome", "base", "niveis", "ajuste", "tags", "drop")}
        if "res" in v: d["res"] = v["res"]
        d["renascimento_s"] = 14
        if k in ("ent_de_cinza", "a_serpente"): d.update({"arquetipo": "elite", "renascimento_s": 300})
        mobs[k] = d
        spr[k] = {"usa": v["usa"], "escala": v["escala"], **({"tint": v["tint"]} if v["tint"] else {})}   # sem tint = folha própria
    spr.update(SPR_CHEFES)
    out = {
        "_doc": "Mata do Granizo + A Torre (pedido do Jefin 11/10/2026). mobs: formato de game/data/v06_extra.json (base = id de design/combate/mobs.json). "
                "sprites: formato de game/data/sprites_substitutos.json (recolor estilo MU até a arte própria). chefes: formato de design/combate/chefes.json. "
                "drops: formato das tabelas de design/combate/drops.json (faixa2 até existir faixa3). Gerado por gerar.py.",
        "mobs": mobs, "sprites": spr, "chefes": CHEFES, "drops": DROPS,
        "ligacao_area_inicial": {"_doc": "Objeto a acrescentar em area_inicial.json (fresta aberta na borda norte, x 81-92, y 23-24).",
                                 "objeto": {"kind": "portal", "pos": ENTRADA_DESERTO, "para": "mata_do_granizo", "chegada": [SPAWN_MATA[0], SPAWN_MATA[1] + 1],
                                            "nome": "Linha de Cinza · para a Mata do Granizo", "visual": "escada_subida"}} if FASE2 else
                                {"_doc": "Objeto a acrescentar em area_inicial.json (fresta aberta na borda norte, x 81-92, y 23-24).",
                                 "objeto": {"kind": "portal", "pos": ENTRADA_DESERTO, "para": "torre_1", "chegada": CHEGADA_ANDAR,
                                            "nome": "A Torre · elevador de carga", "visual": "escada_descida"},
                                 "props": [{"k": "torre_vigia", "x": 85.5, "y": 22.0, "decor_moldura": True}, {"k": "braseiro_ferro", "x": 90.0, "y": 24.0}],
                                 "luzes": [[90.0, 24.0, 1, 0.45, 0.15, 6]]},
        "nomes_mapa_hud": {"mata_do_granizo": "Novo Éden (nv 12-30)", "catacumba_das_raizes": "Catacumba das Raízes (chefe nv 22)", **{f"torre_{i}": f"A Torre · {i}º andar (chefe nv {ANDARES[i-1][3][1]})" for i in range(1, 6)}},
    }
    json.dump(out, open(f"{AQUI}/dados.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    # python3 gerar.py       -> os 5 andares da Torre + dados.json
    # python3 gerar.py mata  -> só a Mata do Granizo (aprovada pelo Jefin em 11/10 10:15; entra depois da 0.8.1)
    so_mata = "mata" in sys.argv
    if so_mata:
        m = mata(); planta(m, f"{AQUI}/planta_mata_do_granizo.png", "Novo Éden · nível 12 a 30")
        c = catacumba(); planta(c, f"{AQUI}/planta_catacumba_das_raizes.png", "Catacumba das Raízes · embaixo da Árvore-Mãe · nível 18 a 22")
    else:
        for i in range(1, 6):
            t = torre(i); planta(t, f"{AQUI}/planta_torre_{i}.png", f"A Torre · {i}º andar · {ANDARES[i-1][0]} · nível {ANDARES[i-1][3][0]} a {ANDARES[i-1][3][1]}")
        dados()
    # conferências: spawn, portais e grupos em célula livre
    for f in (["mata_do_granizo", "catacumba_das_raizes"] if so_mata else [f"torre_{i}" for i in range(1, 6)]):
        d = json.load(open(f"{AQUI}/{f}.json")); g = d["grade"]
        livre = lambda p: g[int(p[1])][int(p[0])] == "."
        ruins = [("spawn", d["spawn"])] if not livre(d["spawn"]) else []
        ruins += [(o["nome"], o["pos"]) for o in d["objetos"] if o["kind"] == "portal" and not livre(o["pos"])]
        ruins += [(s["mob"], s["pos"]) for s in d["spawns"] if not livre(s["pos"])]
        print(f, "OK" if not ruins else f"FORA DO CHÃO: {ruins}")

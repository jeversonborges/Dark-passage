# Monta layout.py a partir do layout.py da cidade anterior (design/mapas/sao_lazaro/fontes) + cidade_1890.py.
# Uso: python3 montar.py  (gera layout.py ao lado). Mantém os spots, NPCs, pontos de missão, zonas e o resto do deserto.
import re, os
AQUI = os.path.dirname(os.path.abspath(__file__))
s = open(f"{AQUI}/../../sao_lazaro/fontes/layout.py", encoding="utf-8").read()
def rep(old, new, count=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, count)

rep("# Cidade de São Lázaro (Vigília) · área inicial níveis 1 a 12 · v1.0 (16/10/2026)",
    "# Cidade de São Lázaro (Vigília) · área inicial níveis 1 a 12 · v2.0 (18/10/2026): a cidade de 1890\n"
    "# GERADO por montar.py a partir de design/mapas/sao_lazaro/fontes/layout.py + cidade_1890.py. Edite esses dois, não este.\n"
    "# v2.0: cidade refeita como uma cidade do século XIX (sobrados do kit sao_lazaro_1890, praça com coreto e chafariz,\n"
    "# ruas em grade, Cerca de tijolo com portões); colisão pelas bases reais das peças (campo 'base' do kit).")
# constantes
rep("""CITY = (50, 80); CITY_R = 24                  # Cidade de São Lázaro (zona segura da Vigília)
PRACA = (48, 78)                              # Praça da Vela, em frente à porta da matriz
MATRIZ = (48, 92)                             # Igreja Matriz de São Lázaro (nave ao longo de y, porta no sul)
RADIO = (35, 92)                              # Rádio São Lázaro (prédio de concreto na beira do precipício)
ESTACAO = (64, 76)                            # Estação da Linha 7 (cúpula de vidro)""",
"""CITY = (49, 77); CITY_R = 32                  # Cidade de São Lázaro (zona segura da Vigília; a Cerca é o retângulo 20..78 x 46..108)
PRACA = (47.5, 80)                            # Praça da Matriz (coreto, chafariz, a Vela)
MATRIZ = (48, 96)                             # Igreja Matriz de São Lázaro (nave ao longo de y, porta no sul, no alto do eixo)
RADIO = (31.5, 77.2)                          # Rádio São Lázaro (sobrado de platibanda com o mastro, na Rua Direita)
ESTACAO = (47.5, 63.2)                        # Estação da Linha 7 (cúpula de vidro, entre a Rua Direita e os trilhos)""")
rep("TRAM = (92, 58)                               # Marco do Corte (o bonde tombado)\nLY = 70",
    "TRAM = (92, 52)                               # Marco do Corte (o bonde tombado)\nLY = 58")
rep("ZCARDOS = ellip((63, 108), 8, 6, 1.0) & ~ZCITY", "ZCARDOS = ellip((64, 118), 7, 5, 1.0) & ~ZCITY")
# trilhas
i0 = s.index("TRILHAS = ["); i1 = s.index("]\nD_TRILHA", i0) + 1
s = s[:i0] + '''TRILHAS = [
    # id, nome, piso, largura, pontos
    ("estrada_sul", "Estrada do Sul", "c", 3.0, [(57, 45), (56, 36), (58, 26), (62, 14), (64, -2)]),
    ("rua_direita", "Rua Direita", "c", 4.5, [(22, 70), (50, 70), (79, 70)]),
    ("rua_bondes", "Rua dos Bondes", "c", 4.0, [(21, 58), (50, 58), (79, 58)]),
    ("rua_cima", "Rua de Cima", "c", 3.0, [(19, 105), (48, 105), (76, 105)]),
    ("rua_matriz", "Rua da Matriz", "c", 3.5, [(38, 47), (38, 78), (38, 107)]),
    ("rua_mercado", "Rua do Mercado", "c", 3.5, [(57, 45), (57, 78), (57, 109)]),
    ("beco_radio", "Beco da Rádio", "c", 3.0, [(22, 56), (22, 80), (22, 106)]),
    ("travessa_forja", "Travessa da Forja", "c", 3.0, [(75, 56), (75, 75), (75, 93)]),
    ("estrada_leste", "Estrada do Leste", "c", 2.6, [(79, 70), (88, 72), (97, 73), (104, 71)]),
    ("rua_sino", "Rua do Sino", "c", 2.4, [(57, 109), (61, 112), (66, 115), (70, 117), (74, 118)]),
    ("trilha_telhados", "Trilha dos Telhados", "t", 1.8, [(19, 105), (17, 112), (19, 120)]),
    ("trilha_patio", "Trilha do Pátio", "t", 2.0, [(30, 45), (28, 40), (26, 34)]),
    ("trilha_vala", "Trilha da Vala", "t", 1.8, [(58, 30), (68, 30), (80, 31), (90, 29)]),
    ("caminho_margem", "Caminho da Margem", "t", 1.6, [(104, 69), (107, 60), (109, 50), (110, 42), (113, 36)]),
    ("vau_do_sebo", "Vau do Sebo", "t", 1.6, [(113, 36), (119, 36), (125, 36), (130, 39)]),
    ("estrada_gado", "Estrada do Gado", "c", 2.4, [(126, 68), (130, 62), (133, 57), (135, 54)]),
    ("trilha_chiqueiros", "Trilha dos Chiqueiros", "t", 1.8, [(126, 70), (132, 75), (137, 80)]),
    ("trilha_procissao", "Trilha das Procissões", "t", 1.8, [(74, 118), (80, 120), (86, 121)]),
    ("cemiterio_alameda", "Alameda dos Ciprestes", "t", 1.5, [(74, 118), (72, 124), (70, 130), (72, 137)]),
    ("trilha_enforcados", "Trilha dos Enforcados", "t", 1.6, [(86, 121), (92, 117), (98, 114)]),
    ("trilha_viuvas", "Trilha das Viúvas", "t", 1.5, [(115, 113), (121, 116), (126, 113), (134, 112), (140, 120), (144, 130)]),
    ("trilha_desertor", "Caminho do Desertor", "t", 1.4, [(115, 113), (116, 108)]),
    ("trilha_tempestade", "Trilha da Tempestade", "t", 1.4, [(140, 120), (136, 132), (132, 140)]),
    ("trilha_campos", "Trilha dos Espantalhos", "t", 1.4, [(79, 70), (82, 80), (84, 92), (80, 102)]),
]''' + s[i1:]
# Linha 7 reta e o ramal; sai a praça/adro antigos (a cidade nova define os seus)
i0 = s.index("# Linha 7: reta ao longo de x"); i1 = s.index("# ------------------------------------------------------------------ água e pontes")
s = s[:i0] + '''# Linha 7: reta ao longo de x na Rua dos Bondes (y=58), do precipício ao matadouro; ramal morto para o Pátio dos Bondes
LINHA7 = poli([(-2, LY), (124, LY), (133, LY)])
RAMAL = poli([(30, LY), (30, 42), (12, 42)])
D_L7 = np.minimum(dist_to(LINHA7), dist_to(RAMAL))
T[(D_L7 < 1.4) & ~AGUA] = "k"
ROAD |= D_L7 < 2.2; MAIN |= D_L7 < 2
trilhas_json.append({"id": "linha_7", "nome": "Trilhos da Linha 7", "piso": "trilho", "largura": 2.0, "pontos": [[-2, LY], [124, LY], [133, LY]]})
trilhas_json.append({"id": "ramal_patio", "nome": "Ramal do Pátio", "piso": "trilho", "largura": 2.0, "pontos": [[30, LY], [30, 42], [12, 42]]})

''' + s[i1:]
# bases reais do kit (campo "base" dos JSON novos) + bases à mão das peças antigas
rep('''    fp = m.get("footprint_tiles", [1, 1])
    KFP[k] = (max(1, round(fp[0] * .7071)), max(1, round(fp[1] * .7071)))''',
'''    fp = m.get("footprint_tiles", [1, 1])
    KFP[k] = (max(1, round(fp[0] * .7071)), max(1, round(fp[1] * .7071)))
    if m.get("base"): BASE[k] = m["base"]''')
rep("KFP, BOX, MASK = {}, {}, {}", '''KFP, BOX, MASK, BASE = {}, {}, {}, {}
# bases (em metros, no eixo da peça: xmin, ymin, xmax, ymax) das peças antigas que não trazem o campo "base"
BASE_FIX = {"cupula_estacao": [-4.4, -4.4, 4.4, 4.4], "capela_sao_lazaro": [-4.3, -5.7, 4.3, 5.7], "torre_relogio_enterrada": [-1.3, -1.3, 1.3, 1.3],
            "posto_odete": [-1.4, -1.4, 1.4, 1.4], "casa_ruina": [-2.5, -2.5, 2.5, 2.5], "frigorifico_enterrado": [-5, -4.2, 5, 4.2],
            "predio_concreto": [-3.4, -2.6, 3.4, 2.6], "predio_enterrado": [-3.4, -2.6, 3.4, 2.6], "torre_vigia": [-1, -1, 1, 1],
            "moinho_ruina": [-1.5, -1.5, 1.5, 1.5], "bonde_veleiro": [-3.5, -1.1, 3.5, 1.1], "bonde_queimado": [-3.5, -1.1, 3.5, 1.1],
            "ruina_concreto": [-1.4, -1, 1.4, 1], "barraco_sucata": [-1.4, -1.4, 1.4, 1.4], "chamine_enterrada": [-.9, -.9, .9, .9],
            "caixa_dagua_sucata": [-1, -1, 1, 1], "guindaste_sucata": [-1.2, -1.2, 1.2, 1.2], "torre_sino": [-.9, -.9, .9, .9],
            "mausoleu": [-1.1, -1.1, 1.1, 1.1], "casa_coveiro": [-1.1, -1.1, 1.1, 1.1], "torre_tombada": [-2, -2, 2, 2],
            "tenda_vigilia": [-1.6, -1.6, 1.6, 1.6], "tenda_demonio": [-1.4, -1.4, 1.4, 1.4], "lampada_arco": [-.7, -.7, .7, .7],
            "caldeira_vapor": [-.8, -.8, .8, .8], "arca_primarca": [-.9, -.5, .9, .5], "entrada_cripta": [-1.4, -1.4, 1.4, 1.4]}
def base_de(kind, orient=None):
    k = arte(kind, orient)
    if k in BASE: return BASE[k]
    if kind in BASE_FIX:
        b = BASE_FIX[kind]
        return [-b[3], b[0], -b[1], b[2]] if orient == "y" else b
    return None''')
rep('''    f = fp or (None if camada == "chao" else fp_de(kind, kw.get("orient")))
    if f and (f[0] > 1 or f[1] > 1):''',
'''    b = None if (fp or camada == "chao") else base_de(kind, kw.get("orient"))
    f = fp or (None if camada == "chao" else fp_de(kind, kw.get("orient")))
    if b is not None:
        # colisão pela base real da peça (+30 cm de folga): toda célula que a base toca fica bloqueada
        x0, y0, x1, y1 = x + b[0] - .3, y + b[1] - .3, x + b[2] + .3, y + b[3] + .3
        sl = (slice(max(0, int(math.floor(x0))), max(0, int(math.ceil(x1)))), slice(max(0, int(math.floor(y0))), max(0, int(math.ceil(y1)))))
        ocup[sl] = True
        if block: blocked[sl] = True
        if kw.get("passagem"):                          # portão: o meio passa (só os pilares bloqueiam)
            if kw.get("orient") == "y": ps = (slice(int(math.floor(x - .9)), int(math.ceil(x + .9))), slice(int(math.floor(y - 1.4)), int(math.ceil(y + 1.4))))
            else: ps = (slice(int(math.floor(x - 1.4)), int(math.ceil(x + 1.4))), slice(int(math.floor(y - .9)), int(math.ceil(y + .9))))
            blocked[ps] = False; ocup[ps] = False
        p["base"] = [round(x + b[0], 2), round(y + b[1], 2), round(x + b[2], 2), round(y + b[3], 2)]
    elif f and (f[0] > 1 or f[1] > 1):''')
# a cidade inteira
i0 = s.index("# =================================================================== A CIDADE DE SÃO LÁZARO")
i1 = s.index("# ---- trilhos (peças do kit a cada 0,707 m) e o bonde")
s = s[:i0] + open(f"{AQUI}/cidade_1890.py", encoding="utf-8").read() + "\n" + s[i1:]
# pátio, bairro, vila, deserto: sem prédios gigantes
rep('add("bonde_veleiro", 22.5, 46.2, fp=(7, 3)', 'add("bonde_veleiro", 22.5, 42.2, fp=(7, 3)')
rep('''for (k, x, y) in [("predio_enterrado", 14, 112), ("casa_ruina", 26, 140), ("predio_enterrado", 12, 140), ("casa_ruina", 30, 118),''',
    '''for (k, x, y) in [("sobrado_ruina", 14, 112), ("casa_ruina", 26, 140), ("sobrado_azul", 12, 140), ("casa_ruina", 30, 118),''')
rep('if livre(x, y, .2, fp=fp_de(k)): add(k, x, y, light=L("vela", 3) if k == "predio_enterrado" else None)',
    'if livre(x, y, .2, fp=fp_de(k)): add(k, x, y, light=L("vela", 3) if k in ("sobrado_ruina", "sobrado_azul") else None)')
rep('espalhar(BAI_OK, ["predio_enterrado", "casa_ruina"], 3, sep=2)', 'espalhar(BAI_OK, ["casa_ruina", "sobrado_ruina"], 3, sep=2)')
rep('("casa_ruina", 140, 144), ("casa_ruina", 154, 132), ("ruina_concreto", 140, 132), ("predio_concreto", 152, 146)',
    '("casa_ruina", 140, 144), ("casa_ruina", 154, 132), ("ruina_concreto", 140, 132), ("sobrado_ruina", 152, 146)')
rep('espalhar(SECO, ["predio_enterrado", "casa_ruina"], 6, sep=5)', 'espalhar(SECO, ["casa_ruina", "sobrado_ruina", "chamine_enterrada"], 6, sep=5)')
rep('dict(id="covas_rasas", nome="Covas Rasas", nivel=[1, 3], zona="campos_cinza", x=88, y=92,', 'dict(id="covas_rasas", nome="Covas Rasas", nivel=[1, 3], zona="campos_cinza", x=94, y=94,')
rep('dict(id="cemiterio_bondes", nome="Cemitério de Bondes", nivel=[2, 4], zona="patio_bondes", x=26, y=40,', 'dict(id="cemiterio_bondes", nome="Cemitério de Bondes", nivel=[2, 4], zona="patio_bondes", x=24, y=31,')
rep('dict(id="marco_do_corte", nome="Marco do Corte", nivel=[7, 9], zona="campos_cinza", x=92, y=58,', 'dict(id="marco_do_corte", nome="Marco do Corte", nivel=[7, 9], zona="campos_cinza", x=92, y=52,')
rep('("Fogueira do Espantalho", 82, 78,', '("Fogueira do Espantalho", 88, 82,')
rep('("Fogueira do Pátio", 40, 52,', '("Fogueira do Pátio", 36, 36,')
# cartaz do Agrak já está na praça nova
i0 = s.index("# Cartaz do Agrak"); i1 = s.index("# Ilha do Exilado: a oficina do Pedro")
s = s[:i0] + s[i1:]
# zona da cidade = retângulo da Cerca
rep('Z("acampamento_vela", "Cidade de São Lázaro", "base", ZCITY,', 'Z("acampamento_vela", "Cidade de São Lázaro", "base", CERCA_M,')
rep("ZID[ZCITY] = LETRAS[0]", "ZID[CERCA_M] = LETRAS[0]")
rep("# ------------------------------------------------------------------ zonas\n", "# ------------------------------------------------------------------ zonas\nCERCA_M = (XX > QX0) & (XX < QX1) & (YY > QY0) & (YY < QY1)\n")
# NPCs nos pontos novos
rep('npc("capita_odete", "posto_odete", -2.6, -.6)', 'npc("capita_odete", "posto_odete", 2.6, -.4)')
rep('npc("doutor_anselmo", "barraca_anselmo", 2.6, -.6)', 'npc("doutor_anselmo", "barraca_anselmo", 0, 0)')
rep('npc("isaura_radialista", "radio_sao_lazaro", 4.6, -.8)', 'npc("isaura_radialista", "porta_radio", 0, 0)')
rep('npc("celina_vidraceira", "forno_vidro", -1.4, -1.2)', 'npc("celina_vidraceira", "forno_vidro", -1.0, -2.2)')
rep('npc("lindalva_parteira", "enfermaria_lindalva", 2.6, -.6)', 'npc("lindalva_parteira", "enfermaria_lindalva", 0, 0)')
# spot perto da cidade: distância até a Cerca
rep('    d_seg = math.hypot(s["x"] - CITY[0], s["y"] - CITY[1]) - CITY_R',
    '    d_seg = max(QX0 - s["x"], s["x"] - QX1, QY0 - s["y"], s["y"] - QY1)')
rep('"name": "Cidade de São Lázaro", "versao": "1.0 (cidade da Vigília)"', '"name": "Cidade de São Lázaro", "versao": "2.0 (cidade de 1890)"')
rep('SPAWN = (PRACA[0] + 2, PRACA[1] - 4)', 'SPAWN = (51.0, 79.0)')
rep('add("poste_ninho_gigante", 30, 42, ponto="poste_torto", objeto="ninhos_corvo")', 'add("poste_ninho_gigante", 33.5, 39.5, ponto="poste_torto", objeto="ninhos_corvo")')
rep('add("bau_comum", 31.0, 41.0, bau="bau_tobias_1", block=False)', 'add("bau_comum", 34.6, 38.4, bau="bau_tobias_1", block=False)')
rep('{"kind": "corvo_de_cinza_carnica", "substituto": "corvo_de_cinza", ', '{"kind": "corvo_de_cinza", ')
rep('add("mausoleu", ex + 6, ey - 8)', 'add("mausoleu", ex + 7, ey - 3.5)')
rep('    if "luzes_extra" in q: q["luzes_extra"] = [shp(e) for e in q["luzes_extra"]]',
    '    if "luzes_extra" in q: q["luzes_extra"] = [shp(e) for e in q["luzes_extra"]]\n    if "base" in q: q["base"] = [SH(q["base"][0]), SH(q["base"][1]), SH(q["base"][2]), SH(q["base"][3])]')
rep('SAIDA = os.path.join(AQUI, "..")', 'SAIDA = os.path.join(AQUI, "..")   # design/mapas/sao_lazaro_refeito/')
rep('objetos = [{"id": p["objeto"], "x": p["x"], "y": p["y"]} for p in props if p.get("objeto")]',
    'objetos = [{"id": p["objeto"], "x": p["x"], "y": (p["base"][1] - .7 if p.get("base") else p["y"])} for p in props if p.get("objeto")]   # objeto numa peça com base fica na beira, do lado do jogador')
open(f"{AQUI}/layout.py", "w", encoding="utf-8").write(s)
print("layout.py montado:", len(s.splitlines()), "linhas")

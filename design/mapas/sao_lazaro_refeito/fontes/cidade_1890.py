# =================================================================== A CIDADE DE SÃO LÁZARO (1890)
# Versão 2.0 (18/10/2026). Pedido do Jefin: a região inicial da Vigília refeita como uma cidade do século XIX, soturna
# mas bonita, legível em isométrico, sem prédios gigantes, com ruas, praça e focos claros. Nada de props empilhados.
# Composição (um eixo só, lido de cima para baixo na tela):
#   Igreja Matriz (no alto) -> adro -> Praça da Matriz (coreto, chafariz, a Vela) -> Rua Direita -> Cúpula da Estação
#   -> Rua dos Bondes (trilhos da Linha 7) -> Largo dos Bondes -> Cerca sul.
# Ruas em grade (as fachadas olham para -Y e +X, os lados que a câmera vê):
#   leste-oeste: Rua de Cima (y=105), Rua Direita (y=70), Rua dos Bondes (y=58)
#   norte-sul:   Beco da Rádio (x=22), Rua da Matriz (x=38), Rua do Mercado (x=57), Travessa da Forja (x=75)
# Quadras: NW Rádio + Enfermaria · N Matriz e jardins · NE Casario + Mercado de Ferro · SW sobrados · S Estação · SE Armazém
#   e o Sobrado de Esquina · Largo dos Bondes ao sul dos trilhos. A Cerca é um muro de tijolo retangular com 6 portões.
cx_, cy_ = CITY
QX0, QX1, QY0, QY1 = 20, 78, 46, 108          # a Cerca
RESERVA |= (XX > QX0 - 2) & (XX < QX1 + 2) & (YY > QY0 - 2) & (YY < QY1 + 2)   # dentro da Cerca nada é sorteado: tudo é posto à mão
PRACA_M = (XX > 40) & (XX < 55) & (YY > 72) & (YY < 88)
T[PRACA_M] = "l"
ADRO = (XX > 39) & (XX < 57) & (YY > 88) & (YY < 103.5)
T[ADRO] = "l"
JARDIM_W = (XX > 24.5) & (XX < 38.5) & (YY > 90.5) & (YY < 103); JARDIM_E = (XX > 57.5) & (XX < 71.5) & (YY > 90.5) & (YY < 103)
T[JARDIM_W | JARDIM_E] = "t"
CALC = (XX > QX0) & (XX < QX1) & (YY > QY0) & (YY < QY1) & ~PRACA_M & ~ADRO & ~JARDIM_W & ~JARDIM_E & ~(T == "c") & ~(T == "k")
T[CALC & (T == "t")] = "n"                     # entulho de telhado entre as casas
T[CALC & (T == "n") & (NZ2 < .45)] = "t"
VISTA = (np.abs((XX + YY) - (MATRIZ[0] + MATRIZ[1])) < 12.5) & ((XX - YY) - (MATRIZ[0] - MATRIZ[1]) > -2) & \
        ((XX - YY) - (MATRIZ[0] - MATRIZ[1]) < 26)

# ---- a Matriz: a nave gótica inteira de pé no alto do eixo, vitrais vermelhos acesos
qx, qy = MATRIZ
LUZ["vitral_rubro"] = [1, .15, .08]
add("capela_sao_lazaro", qx, qy, light=L("vitral_rubro", 9), ponto="matriz_sao_lazaro",
    luzes_extra=[[qx + 4.5, qy - 2] + L("vitral_rubro", 5), [qx + 4.5, qy + 3] + L("vitral_rubro", 5), [qx - 1.5, qy - 6.5] + L("vitral_rubro", 4),
                 [qx - 1, qy - 9.5] + L("sagrada", 8)],
    nota="Igreja Matriz de São Lázaro: a nave que a areia não engoliu; os Sineiros da Vigília tocam o sino e fundem os outros em bala")
add("marcador_npc", qx, qy - 7.4, block=False, invisivel=True, ponto="porta_matriz", objeto="matriz_sao_lazaro", silhueta=False, nota="porta da matriz")
for (dx, dy) in [(-2.4, -6.8), (2.4, -6.8)]: add("braseiro_sagrado", qx + dx, qy + dy, light=L("sagrada", 4.5))
for (dx, dy) in [(-1.6, -7.6), (1.3, -7.9), (2.0, -7.3), (-.8, -8.2), (.4, -7.5)]:
    add("velas_chao", qx + dx, qy + dy, block=False, light=L("vela", 1.6), silhueta=False)
add("braseiro_holofote", qx + 13.5, qy - 1.5, light=L("sagrada", 10), nota="holofote da matriz (lado dos vitrais)")
add("braseiro_holofote", qx - 12.5, qy - 10.5, light=L("sagrada", 9), nota="holofote da matriz (lado da praça)")
# Jardim de São Lázaro: canteiros de ferro batido dos dois lados do adro, alamedas de ciprestes, a oliveira e o poço
JR = random.Random(77)
def canteiro(b, kinds, passo, grade_lados):
    bx0, by0, bx1, by1 = b
    for lado in grade_lados:
        if lado in "nN":
            for x in np.arange(bx0 + .35, bx1, .7): add("grade_ferro_batido", x, by0 + .1 if lado == "n" else by1 - .1, orient="x", block=False, silhueta=False)
        else:
            for y in np.arange(by0 + .35, by1, .7): add("grade_ferro_batido", bx0 + .1 if lado == "w" else bx1 - .1, y, orient="y", block=False, silhueta=False)
    for x in np.arange(bx0 + .9, bx1 - .5, passo):
        for y in np.arange(by0 + .9, by1 - .5, passo):
            add(JR.choice(kinds), x + JR.uniform(-.25, .25), y + JR.uniform(-.25, .25), block=False, silhueta=False)
BAIXAS = ["tapete_flores", "tapete_flores_2", "tapete_flores_3", "moita_florida_3", "moita_florida_3", "planta_mutante"]
canteiro((26.5, 92.0, 31.5, 97.0), BAIXAS, 1.3, "nw"); canteiro((26.5, 98.0, 31.5, 102.5), ["mirto", "moita_florida", "tapete_flores_2"], 1.6, "wN")
canteiro((59.5, 92.0, 64.5, 97.0), BAIXAS + ["campanula"], 1.4, "ne"); canteiro((59.5, 98.0, 64.5, 102.5), ["mirto", "moita_florida_2", "tapete_flores"], 1.6, "eN")
for y in np.arange(91.5, 103.0, 2.8):                                  # alamedas de ciprestes ao longo do adro
    add("cipreste" if int(y) % 2 else "cipreste_2", 36.6, y); add("cipreste_2" if int(y) % 2 else "cipreste", 59.0 - .4, y) if y > 100 else None
for x in (41.0, 46.0, 50.0, 55.0): add("cipreste_2" if x in (46.0,) else "cipreste", x, 104.0)
add("oliveira", 68.0, 100.0, nota="a oliveira de São Lázaro, plantada no dia em que a areia parou no 4º andar")
add("trelica_videira", 68.5, 94.5, block=False)
add("banco_capela", 43.0, 90.5); add("banco_capela", 53.0, 90.5); add("banco_praca", 33.5, 95.0, orient="y"); add("banco_praca", 66.0, 95.0, orient="y")
add("poco", 33.5, 100.5, objeto="poco_jardim", nota="poço que rega o jardim")
add("lapide_cruz_vitoriana", 34.0, 91.5); add("tumulo_vitoriano", 67.0, 91.8); add("vela_tumulo", 34.6, 92.3, block=False, silhueta=False)
add("torre_relogio_enterrada", 25.5, 97.5, ponto="relogio_matriz", light=L("vela", 3), nota="a torre do relógio da prefeitura, enterrada até o mostrador")
for (x, y) in [(38.5, 89.5), (57.5, 89.5), (38.5, 103.0), (57.5, 103.0)]: add("lampiao_gas", x, y, light=L("gas", 3.5))

# ---- Praça da Matriz: coreto no meio, chafariz no eixo, a Vela (lâmpada de arco) e a Arca do Gustavo
px_, py_ = PRACA
add("coreto", 47.5, 82.0, light=L("gas", 7), ponto="coreto", nota="coreto da praça: a banda da Vigília toca aos domingos; a Vela fica pendurada aqui ao lado")
add("chafariz", 47.5, 75.0, light=[.4, 1, .35, 3], ponto="chafariz", objeto="poco_praca", nota="chafariz de 1888, seco; a água do Amargo brilha no fundo")
add("lampada_arco", 52.6, 76.6, light=L("arco", 11), ponto="a_vela")
add("quiosque", 41.6, 85.6, light=L("gas", 3.5), ponto="quiosque_velas", nota="quiosque de jornal que hoje vende velas")
add("poste_relogio", 53.6, 85.6, nota="relógio de rua parado nas 3 e 12")
def praca_primarca(ax, ay, ponto):
    """Gustavo, o Primarca (armazém), em evidência na praça: Arca com as válvulas roxas, caldeira atrás, velas na frente."""
    add("marcador_npc", ax + 1.6, ay - 1.6, block=False, fp=(4, 4), invisivel=True, nota="praça do Primarca (livre)", silhueta=False)
    add("arca_primarca", ax, ay, fp=(2, 1), ponto=ponto, objeto="arca_primarca", light=L("valvula", 6))
    add("caldeira_vapor", ax - 1.6, ay + 1.6, light=L("fornalha", 3))
    for (dx, dy) in [(.4, -1.3), (-.9, -1.6), (1.5, .2)]:
        add("velas_chao", ax + dx, ay + dy, block=False, light=L("vela", 1.5), silhueta=False)
praca_primarca(42.4, 77.4, "arca_primarca")
for (x, y, o) in [(44.0, 73.4, "x"), (51.0, 73.4, "x"), (41.0, 80.0, "y"), (54.2, 80.0, "y"), (44.0, 86.6, "x"), (51.0, 86.6, "x")]:
    add("banco_praca", x, y, orient=o)
for (x, y) in [(40.8, 72.8), (54.2, 72.8), (40.8, 87.2), (54.2, 87.2), (47.5, 72.8), (40.8, 80.0), (54.2, 83.5)]:
    add("lampiao_gas", x, y, light=L("gas", 3.5))
add("placa_aviso", 44.6, 72.9, texto="ENQUANTO HOUVER VELA, NÃO É NOITE.")
add("placa_aviso", 50.4, 72.9, objeto="cartaz_agrak", ponto="cartaz_agrak_vela", silhueta=False, texto="O AGRAK CHAMA · INSCRIÇÃO 100 OURO · NV 25+")
for (x, y) in [(43.0, 83.5), (52.2, 80.8), (42.2, 81.6)]: add("moita_florida_2" if x > 50 else "moita_florida", x, y, block=False, silhueta=False)

# ---- Quadra NW: Rádio São Lázaro na Rua Direita e a Enfermaria (Anselmo e Lindalva) na Rua da Matriz
rx_, ry_ = RADIO
add("radio_sao_lazaro", rx_, ry_, ponto="radio_sao_lazaro", light=L("gas", 5), luzes_extra=[[rx_ + 1.2, ry_ + .6] + L("radio", 3)],
    nota="Rádio São Lázaro: Isaura transmite do estúdio do 1º andar, que já foi o 5º")
add("marcador_npc", rx_ + 2.2, ry_ - 3.6, block=False, invisivel=True, ponto="porta_radio", silhueta=False)
add("tambores_radioativos", 24.6, 80.6); add("caixas", 35.0, 81.2); add("varal_roupas", 33.5, 73.5)
add("sobrado_verde", 26.8, 86.5, orient="y", light=L("vela", 4), nota="a Enfermaria da Vigília, no sobrado verde da antiga farmácia")
add("marcador_npc", 38.4, 83.8, block=False, invisivel=True, ponto="barraca_anselmo", silhueta=False, nota="o Doutor atende na praça, em frente à enfermaria")
add("marcador_npc", 30.8, 88.8, block=False, invisivel=True, ponto="enfermaria_lindalva", silhueta=False)
add("bau_comum", 31.0, 82.6, bau="bau_barraca_anselmo", tipo_bau="trancado")
add("placa_aviso", 33.4, 89.0, texto="ENFERMARIA · O DOUTOR ATENDE DE GRAÇA")
add("tonel_fogo", 35.6, 77.6, light=L("tonel", 4)); add("barris", 23.0, 84.0)

# ---- Quadra NE: o Casario na Rua Direita e o Mercado de Ferro (Gaspar, Mãe Cardo, Tobias e Celina)
add("casario", 65.2, 76.6, light=L("gas", 5), nota="casario geminado: as três casas dos Sineiros")
add("mercado_ferro", 65.5, 88.0, ponto="mercado_ferro", light=L("gas", 8), luzes_extra=[[61.5, 86] + L("gas", 4), [69.5, 86] + L("gas", 4)],
    nota="Mercado Municipal (1890): pavilhão de ferro e vidro; hoje a Rua do Mercado inteira cabe debaixo dele")
add("bancada_ferreiro", 61.6, 81.6, light=L("fornalha", 5), ponto="forja_bigorna"); add("pilha_carvao", 59.8, 82.6); add("tonel_fogo", 63.6, 82.6, light=L("tonel", 4))
add("caldeirao_cardo", 66.2, 81.4, light=L("fogo", 4), ponto="caldeirao_cardo"); add("moita_cardo", 67.8, 82.4, block=False)
add("carrinho_tobias", 70.2, 81.4, ponto="carrinho_tobias", light=L("vela", 2.5))
add("caldeira_vapor", 72.6, 87.6, ponto="forno_vidro", light=L("fornalha", 4)); add("tanque_latao", 72.6, 91.2)
add("varal_roupas", 71.8, 79.6); add("sacos_sal", 60.2, 92.4); add("caixas", 62.6, 92.6); add("barris", 69.6, 92.8)
for (x, y) in [(60.2, 72.8), (70.2, 72.8), (60.2, 83.6), (71.0, 83.6)]: add("lampiao_gas", x, y, light=L("gas", 3.5))
add("placa_aviso", 70.6, 73.2, texto="MERCADO MUNICIPAL · 1890 · HOJE: A VIGÍLIA")

# ---- Quadra S: a Cúpula da Estação no eixo, o bonde-veleiro atracado na Rua dos Bondes, o posto da Odete
ex, ey = ESTACAO
add("cupula_estacao", ex, ey, ponto="portao_cupula", light=L("arco", 5))
add("bonde_veleiro", 41.0, LY + .2, fp=(7, 3), block=True, ponto="plataforma_bondes", light=L("gas", 4))
add("posto_odete", 53.4, 65.0, orient="y", ponto="posto_odete", light=L("gas", 4))
add("caixas", 42.6, 62.0); add("sacos_sal", 53.8, 61.2); add("barris", 43.2, 66.2); add("lampiao_gas", 43.0, 60.6, light=L("gas", 3.5)); add("lampiao_gas", 52.6, 60.6, light=L("gas", 3.5))
add("placa_aviso", 44.2, 67.0, texto="LINHA 7 · ESTAÇÃO SÃO LÁZARO · PRÓXIMO BONDE: QUANDO O VENTO QUISER")
# ---- Quadras SW e SE: sobrados de fachada para a Rua dos Bondes; o Armazém e o Sobrado de Esquina
add("sobrado_ocre", 27.3, 64.0, light=L("gas", 4)); add("sobrado_azul", 33.2, 64.3, orient="y", light=L("gas", 4))
add("sobrado_loja", 63.2, 64.0, light=L("gas", 5), nota="Armazém Primarca & Cia: o Gustavo mora em cima")
add("sobrado_esquina", 70.6, 64.5, light=L("gas", 5), nota="o Sobrado de Esquina, com o relógio de rua parado")
add("caixas", 60.4, 60.9); add("barris", 66.4, 60.9); add("carroca_quebrada", 30.6, 60.5); add("varal_roupas", 30.5, 67.0); add("tonel_fogo", 36.4, 68.8, light=L("tonel", 3))
for (x, y) in [(24.6, 60.6), (31.4, 60.6), (37.0, 60.6), (59.6, 60.6), (75.0, 60.6), (24.6, 72.8), (36.2, 72.8), (58.8, 72.8), (74.0, 72.8), (75.0, 69.0)]:
    add("lampiao_gas", x, y, light=L("gas", 3.5))
# ---- Largo dos Bondes (sul dos trilhos): dois sobrados, o guindaste e a caixa d'água da Vigília
add("sobrado_rosa", 58.5, 51.6, light=L("gas", 4), nota="Pensão da Linha 7")
add("sobrado_ruina", 70.5, 50.5, light=None, nota="a casa que ninguém quis de volta")
add("guindaste_sucata", 36.0, 52.0, light=L("tonel", 3)); add("caixa_dagua_sucata", 34.6, 50.2); add("tanque_latao", 33.0, 54.2)
add("carroca_quebrada", 53.6, 50.0); add("barris", 40.2, 50.8); add("caixas", 61.2, 49.0)
add("trilho_retorcido", 26.0, 50.6)
for (x, y) in [(42.0, 48.6), (56.0, 47.6), (62.0, 48.6), (75.0, 48.6), (24.6, 55.4), (74.6, 55.4)]: add("lampiao_gas", x, y, light=L("gas", 3.5))
# ---- Rua de Cima (atrás da Matriz): pouca coisa, só lampiões e a oficina do vidro
for x in (28.0, 46.0, 66.0): add("poste_gas", x, 106.6, light=L("gas", 3.5))
add("caixa_dagua_sucata", 72.5, 104.0); add("moinho_ruina", 26.0, 104.5, nota="o moinho do antigo quartel")

# ---- a Cerca: muro de tijolo retangular com 6 portões (os pilares bloqueiam, o meio passa) e torres nos cantos
PORTOES_XY = [("sul_mercado", 57, QY0, "x"), ("sul_ramal", 30, QY0, "x"), ("leste_direita", QX1, 70, "y"), ("leste_trilhos", QX1, LY, "y"),
              ("norte_mercado", 57, QY1, "x"), ("oeste_cima", QX0, 105, "y"), ("oeste_trilhos", QX0, LY, "y")]
def muro(a, b, orient):
    pula = [(gx, gy, 3.6) for _, gx, gy, _ in PORTOES_XY]
    BASE_FIX["muro_tijolo"] = [-.5, -.5, .5, .5]     # o trecho bloqueia 1 m de espessura: nada de passar por cima do muro
    linha_de("muro_tijolo", a, b, .7, orient=orient, pula=pula, silhueta=False)
muro((QX0, QY0), (QX1, QY0), "x"); muro((QX0, QY1), (QX1, QY1), "x"); muro((QX0, QY0), (QX0, QY1), "y"); muro((QX1, QY0), (QX1, QY1), "y")
for pid, gx, gy, o in PORTOES_XY:
    add("portao_cidade", gx, gy, orient=o, light=L("fogo", 5), ponto="portao_" + pid, passagem=True)
for (x, y) in [(QX0 + 1.2, QY0 + 1.2), (QX1 - 1.2, QY0 + 1.2), (QX1 - 1.2, QY1 - 1.2), (QX0 + 4.6, QY1 - 1.2), (QX1 - 1.4, 64.0)]:
    add("torre_vigia", x, y, light=L("arco", 6))
add("marcador_npc", QX1 - 2.6, 72.6, block=False, invisivel=True, ponto="costelas_cupula", nota="Damião vigia o portão leste", silhueta=False)
# ruas livres de novo depois dos muros (os portões só bloqueiam nos pilares)

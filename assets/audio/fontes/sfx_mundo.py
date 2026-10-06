"""Passos, itens, baus, forja e interface."""
from kit import *  # noqa
from registro import som


# ======================================================== passos
def _passo(superficie, peso=1.0):
    d = 0.35
    t = tt(d)
    heel = thump(ru(70, 95) / peso, d, 0.8, 0.03 * peso, 0.0) * 0.6
    if superficie == 'pedra':
        y = heel + bbp(white(d), 900, 7000, 2) * env_exp(d, 0.008) * 1.2
        y += debris(d, 40, 1500, 6000, 0.04) * 0.4
    elif superficie == 'cinza':
        y = heel * 0.7 + lp(bp(white(d) * (1 + 3 * np.abs(lp(white(d), 200) * 10)), 1500, 0.7), 5000) * env_exp(d, 0.05, 0.004) * 1.4
    elif superficie == 'terra':
        y = heel + lp(white(d), 1800) * env_exp(d, 0.025) * 1.2 + debris(d, 30, 400, 3000, 0.05) * 0.5
    elif superficie == 'madeira':
        y = wood_knock(ru(110, 150), d) * 1.2 + heel * 0.5
    elif superficie == 'metal':
        y = heel * 0.6 + metal(d, ru(350, 450), n=16, decay=0.12, bright=1.0) * 0.6
        y += bp(white(d), 3000, 1) * env_exp(d, 0.004) * 0.6
    elif superficie == 'osso':
        y = heel * 0.5 + bones_rattle(d, 40) * 0.8 + crunch(d, 200, 900, 5000, 0.6) * 0.6
    elif superficie == 'molhado':
        y = heel * 0.8 + splat(d, 0.8) * 0.6 + lp(white(d), 3000) * env_exp(d, 0.02) * 0.6
    y += cloth(d, 0.15, 2500)
    return y


for _s, _esp in [('pedra', 'rua'), ('cinza', 'rua'), ('terra', 'rua'), ('madeira', 'quarto'),
                 ('metal', 'abatedouro'), ('osso', 'ossario'), ('molhado', 'abatedouro')]:
    def _mk(s):
        return lambda v: _passo(s, ru(0.9, 1.1))
    som(f'passos/{_s}', var=6, lufs=-24, espaco=_esp, mix=0.08,
        desc=f'passo em {_s} (sortear uma variacao por passo)')(_mk(_s))


@som('passos/pesado', var=4, lufs=-16, espaco='cripta', mix=0.2, desc='passo de criatura gigante/chefe (faz o chao tremer)')
def _(v):
    d = 1.2
    y = sat(thump(ru(32, 40), d, 1.5, 0.3, 0.4), 2) * 1.2
    y += debris(d, 50, 300, 3000, 0.25) * 0.6
    y += lp(brown(d), 200) * env_exp(d, 0.3)
    return y


# ======================================================== itens e baus
@som('itens/bau_madeira', var=2, lufs=-17, espaco='rua', mix=0.15, desc='abre bau de madeira: trinco + rangido')
def _(v):
    d = 1.6
    y = np.zeros(ns(d))
    y = place(y, metal(0.15, 1400, 10, decay=0.03, bright=1.3) + wood_knock(260, 0.15)[:ns(0.15)] * 0.5, 0)
    y = place(y, creak(0.9, 35, 80, (280, 640, 1400)) * 0.9, 0.15)
    y = place(y, add(wood_knock(150, 0.4) * 1.0, thump(80, 0.4, 0.5, 0.07, 0.1) * 0.5), 1.05)
    return y


@som('itens/bau_ferro', var=2, lufs=-16, espaco='cripta', mix=0.2, desc='abre bau de ferro: chave, ferrolho pesado, tampa de ferro')
def _(v):
    d = 2.2
    y = np.zeros(ns(d))
    y = place(y, gears(0.25, 20, 2200) * 0.6, 0)
    y = place(y, clang(500, 0.5, 1.0, 0.08, 0.6) * 0.8, 0.3)
    y = place(y, creak(1.0, 25, 50, (400, 950, 2100), 1.3) * 0.7, 0.45)
    y = place(y, add(clang(260, 1.0, 0.9, 0.25, 0.5) * 0.9, thump(70, 0.6, 0.8, 0.1, 0.3)), 1.45)
    return y


@som('itens/bau_reliquia', var=1, lufs=-14, espaco='catedral', mix=0.3, desc='abre bau raro/de chefe: ferrolho + coro e sinos subindo')
def _(v):
    d = 4.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(clang(400, 0.6, 1.0, 0.1, 0.7)), 0)
    y = place(y, to_stereo(creak(0.9, 25, 50, (400, 950, 2100), 1.2) * 0.6), 0.2)
    y = place(y, choir(['D4', 'A4', 'D5', 'F#5'], 3.0, 'a', 'soprano', 4, 0.6, 1.5) * 0.7, 0.8)
    for i, nt in enumerate(['D5', 'A5', 'D6', 'F#6']):
        y = place(y, pan(bell(hz(nt), 2.5, 1.2, 1.3) * 0.25, -0.6 + 0.4 * i), 1.0 + i * 0.1)
    return y


@som('itens/moedas', var=3, lufs=-18, espaco='rua', mix=0.1, desc='pega ouro / moedas')
def _(v):
    return coins(0.8, int(ru(5, 9)))


@som('itens/moedas_muitas', var=1, lufs=-16, espaco='rua', mix=0.12, desc='pilha grande de ouro (bau, venda grande)')
def _(v):
    return add(coins(1.4, 30), coins(1.4, 20) * 0.6)


@som('itens/drop_comum', var=3, lufs=-20, espaco='rua', mix=0.1, desc='item cai no chao (comum)')
def _(v):
    d = 0.5
    return add(wood_knock(ru(300, 450), d) * 0.8, cloth(0.2, 0.6), thump(110, d, 0.3, 0.04, 0.2) * 0.4)


@som('itens/drop_metal', var=3, lufs=-19, espaco='rua', mix=0.1, desc='arma/armadura cai no chao')
def _(v):
    d = 0.9
    y = clang(ru(500, 800), d, 1.1, 0.12, 0.6) * 0.7
    y = place(y, clang(ru(700, 1000), 0.5, 1.1, 0.08, 0.5) * 0.35, 0.09)
    return add(y, thump(100, 0.4, 0.3, 0.05, 0.2) * 0.5)


@som('itens/drop_excelente', var=1, lufs=-16, espaco='catedral', mix=0.25, desc='drop excelente (azul): brilho eletrico + nota')
def _(v):
    d = 2.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(clang(700, 0.6, 1.1, 0.1, 0.5) * 0.5), 0)
    y = place(y, widen(zap(0.4, 0.4) * env_exp(0.4, 0.1)), 0.02)
    for i, nt in enumerate(['E5', 'B5', 'E6']):
        y = place(y, pan(bell(hz(nt), 1.6, 0.8, 1.4) * 0.3, -0.4 + 0.4 * i), 0.05 + 0.06 * i)
    return y


@som('itens/drop_reliquia', var=1, lufs=-15, espaco='catedral', mix=0.3, desc='drop reliquia (dourado): sinos + coro curto')
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(clang(600, 0.6, 1.1, 0.1, 0.5) * 0.5), 0)
    y = place(y, choir(['D4', 'A4', 'D5'], 2.0, 'a', 'soprano', 4, 0.05, 1.2) * 0.6, 0.02)
    for i, nt in enumerate(['D5', 'F#5', 'A5', 'D6']):
        y = place(y, pan(bell(hz(nt), 2.0, 1.0, 1.3) * 0.28, -0.5 + 0.33 * i), 0.04 + 0.07 * i)
    return y


@som('itens/drop_profano', var=1, lufs=-13, espaco='catedral', mix=0.3, desc='drop profano (unico do chefe): brasa, coro grave dissonante e sino')
def _(v):
    d = 4.5
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(whoomp(1.4, 50)), 0)
    y = place(y, choir(['D3', 'Ab3', 'D4', 'Eb4'], 3.5, 'o', 'baixo', 5, 0.05, 2.5, vowel2='a') * 0.9, 0.05)
    y = place(y, to_stereo(bell(hz('D3'), 4, 3, 1.0) * 0.7), 0.05)
    y = place(y, to_stereo(bell(hz('Ab3'), 3.5, 2.5, 1.0) * 0.4), 0.08)
    y = place(y, to_stereo(fire(3.5, 0.3, 40) * env_exp(3.5, 1.0)), 0.2)
    return y


@som('itens/pocao_beber', var=3, lufs=-19, espaco='quarto', mix=0.08, desc='bebe pocao: rolha + goles')
def _(v):
    d = 1.2
    y = np.zeros(ns(d))
    pop = bp(white(0.05), 900, 3) * env_exp(0.05, 0.006) * 1.5 + sine(500, 0.05) * env_exp(0.05, 0.01) * 0.5
    y = place(y, pop, 0)
    for i in range(int(ru(2, 4))):
        g = lp(liquid(0.22, 30, 200, 450), 2500) * env_pts(0.22, [(0, 0), (0.05, 1), (0.22, 0)])
        g = add(g, thump(90, 0.18, 0.5, 0.05, 0) * 0.5)
        y = place(y, g * 1.2, 0.25 + i * ru(0.22, 0.3))
    y = place(y, lp(breath(0.3, 'a', 'baixo', False, 0.12), 2500), 1.0 if len(y) > ns(1.0) else 0.85)
    return y


@som('itens/pocao_cair', var=2, lufs=-19, espaco='rua', mix=0.1, desc='frasco de vidro cai / pega pocao')
def _(v):
    return add(glass(ru(2000, 2600), 0.5) * 0.6, liquid(0.3, 20, 400, 900) * 0.3, thump(160, 0.2, 0.3, 0.03, 0.2) * 0.3)


@som('itens/equipar_arma', var=3, lufs=-18, espaco='quarto', mix=0.1, desc='equipa arma: lamina saindo/entrando na bainha')
def _(v):
    d = 0.7
    t = tt(d)
    f = np.linspace(2500, 4500, ns(d))
    y = bp(white(d) * (1 + 2 * np.abs(lp(white(d), 80) * 8)), f, 3) * env_pts(d, [(0, 0), (0.05, 1), (0.45, 0.8), (0.5, 0)]) * 0.8
    return place(y, clang(ru(1600, 2000), 0.5, 1.6, 0.15, 0.4) * 0.3, 0.45)


@som('itens/equipar_armadura', var=3, lufs=-18, espaco='quarto', mix=0.1, desc='equipa armadura/roupa: couro, fivelas e placas')
def _(v):
    d = 0.8
    y = cloth(d, 1.2, 2500)
    y = place(y, clink(ru(1600, 2200)) * 0.5, ru(0.2, 0.3))
    y = place(y, clink(ru(1600, 2200)) * 0.4, ru(0.45, 0.55))
    y = place(y, clang(ru(500, 700), 0.4, 1.0, 0.06, 0.3) * 0.3, 0.6)
    return y


@som('itens/equipar_joia', var=2, lufs=-19, espaco='quarto', mix=0.12, desc='equipa anel/colar')
def _(v):
    return add(coin(ru(3000, 4000), 0.6) * 0.6, glass(ru(4000, 5000), 0.5) * 0.3, chain(0.3, 30) * 0.3)


@som('itens/joia_aplicar', var=1, lufs=-17, espaco='catedral', mix=0.25, desc='usa joia de refino (Lagrima de Anjo / Fragmento de Alma): carga subindo')
def _(v):
    d = 1.6
    t = tt(d)
    env = env_pts(d, [(0, 0), (1.4, 1), (d, 0)], 1.5)
    y = bp(white(d), 300 + 5000 * env, 4) * env * 0.8
    y += sine(400 + 800 * env, d) * env * 0.08
    y = add(y, glass(3200, 0.6) * 0.4)
    return y


@som('itens/refino_sucesso', var=1, lufs=-14, espaco='catedral', mix=0.3, desc='refino deu certo (+N): martelo + sino + brilho')
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(anvil(1100, 1.2)), 0)
    for i, nt in enumerate(['A4', 'E5', 'A5', 'C#6', 'E6']):
        y = place(y, pan(bell(hz(nt), 2.2, 1.1, 1.3) * 0.28, -0.6 + 0.3 * i), 0.08 + 0.06 * i)
    y = place(y, widen(bp(white(1.5), np.linspace(2000, 9000, ns(1.5)), 3) * env_exp(1.5, 0.5) * 0.5), 0.05)
    return y


@som('itens/refino_falha', var=1, lufs=-15, espaco='abatedouro', mix=0.25, desc='refino falhou (volta 1 nivel): estilhaco e queda')
def _(v):
    d = 2.5
    y = np.zeros(ns(d))
    y = place(y, anvil(900, 0.8) * 0.6, 0)
    y = place(y, add(glass(1800, 1.0), glass(1300, 1.2) * 0.6), 0.05)
    y = place(y, debris(1.0, 200, 1500, 8000, 0.3) * 0.7, 0.06)
    t = tt(1.8)
    y = place(y, sat(np.sin(2 * np.pi * np.cumsum(200 * np.exp(-t / 0.4) + 40) / SR) * env_exp(1.8, 0.5), 2) * 0.6, 0.06)
    y = place(y, bell(hz('C3'), 2.0, 1.5, 0.8) * 0.4, 0.1)
    return y


@som('itens/forja_martelo', var=3, lufs=-15, espaco='rua', mix=0.15, desc='martelada na bigorna (ferreiro / reparar)')
def _(v):
    return anvil(ru(950, 1250), 1.4)


@som('itens/reparar', var=1, lufs=-16, espaco='rua', mix=0.15, desc='reparar equipamento: tres marteladas e chiado de tempera')
def _(v):
    d = 2.6
    y = np.zeros(ns(d))
    for i in range(3):
        y = place(y, anvil(ru(1000, 1200), 0.7) * (0.8 + 0.1 * i), i * 0.38)
    y = place(y, steam(1.2, 4000, 0.01, 0.4) * 0.7, 1.3)
    return y


@som('itens/chave_usar', var=1, lufs=-18, espaco='cripta', mix=0.2, desc='usar chave em porta/bau')
def _(v):
    d = 1.0
    y = np.zeros(ns(d))
    y = place(y, chain(0.25, 30) * 0.5, 0)
    y = place(y, gears(0.3, 16, 1800) * 0.7, 0.25)
    y = place(y, clang(450, 0.5, 1.0, 0.08, 0.6) * 0.7, 0.6)
    return y


@som('itens/porta_ferro', var=1, lufs=-15, espaco='cripta', mix=0.3, desc='porta pesada de ferro abrindo (entrada da cripta)')
def _(v):
    d = 3.5
    y = np.zeros(ns(d))
    y = place(y, clang(300, 0.8, 0.9, 0.2, 0.6), 0)
    y = place(y, creak(2.2, 18, 30, (220, 540, 1300), 1.4) * 0.9, 0.3)
    y = place(y, chain(1.5, 25, 0.3, 1.5) * 0.4, 0.4)
    y = place(y, add(sat(thump(45, 1.2, 1, 0.3, 0.5), 2), clang(180, 1.2, 0.8, 0.4, 0.3) * 0.6), 2.6)
    return y


@som('itens/porta_madeira', var=2, lufs=-17, espaco='quarto', mix=0.2, desc='porta de madeira abrindo')
def _(v):
    d = 1.8
    y = np.zeros(ns(d))
    y = place(y, metal(0.12, 1500, 8, decay=0.02, bright=1.3), 0)
    y = place(y, creak(1.2, 45, 110, (300, 720, 1600)), 0.1)
    return y


# ======================================================== interface
@som('ui/clique', var=3, lufs=-24, espaco=None, desc='clique de botao (metal seco)')
def _(v):
    d = 0.12
    return add(metal(d, ru(1800, 2200), 8, decay=0.012, bright=1.5) * 0.6,
               bp(white(d), 3000, 1.5) * env_exp(d, 0.002), thump(220, 0.06, 0.3, 0.01, 0) * 0.3)


@som('ui/passar_mouse', var=2, lufs=-30, espaco=None, desc='mouse passando por cima de botao/item')
def _(v):
    d = 0.06
    return bp(white(d), ru(4000, 5000), 3) * env_exp(d, 0.006) + metal(d, 3500, 4, decay=0.005, bright=2) * 0.2


@som('ui/abrir_inventario', var=1, lufs=-20, espaco='quarto', mix=0.08, desc='abre inventario (mochila de couro + fivela)')
def _(v):
    d = 0.6
    y = cloth(0.45, 1.3, 2200)
    y = place(np.zeros(ns(d)), y, 0.0)
    y = place(y, clink(1900) * 0.5, 0.05)
    y = place(y, wood_knock(220, 0.2) * 0.3, 0.35)
    return y


@som('ui/fechar_inventario', var=1, lufs=-21, espaco='quarto', mix=0.08, desc='fecha inventario')
def _(v):
    d = 0.45
    y = reverse(cloth(0.35, 1.1, 2000))
    y = place(np.zeros(ns(d)), y, 0)
    y = place(y, clink(1700) * 0.5, 0.3)
    return y


@som('ui/abrir_janela', var=1, lufs=-21, espaco='quarto', mix=0.08, desc='abre janela/painel (pergaminho de couro)')
def _(v):
    d = 0.4
    return bbp(white(d) * (1 + 3 * np.abs(lp(white(d), 60) * 8)), 1200, 6000) * env_pts(d, [(0, 0), (0.05, 1), (d, 0)]) * 0.8


@som('ui/fechar_janela', var=1, lufs=-22, espaco='quarto', mix=0.08, desc='fecha janela/painel')
def _(v):
    d = 0.3
    return add(bbp(white(d), 900, 4000) * env_exp(d, 0.05) * 0.6, wood_knock(260, 0.2) * 0.4)


@som('ui/abrir_mapa', var=1, lufs=-21, espaco='quarto', mix=0.08, desc='abre mapa (papel grosso desenrolando)')
def _(v):
    d = 0.9
    crink = bbp(crackle(d, 300, 0.002), 1500, 8000) * env_pts(d, [(0, 0), (0.1, 1), (0.7, 0.6), (d, 0)])
    return crink + cloth(d, 0.6, 3000)


@som('ui/pegar_item', var=2, lufs=-23, espaco=None, desc='pega item no inventario (arrastar)')
def _(v):
    d = 0.15
    return add(cloth(d, 0.8, 3000), clink(ru(2200, 2800), 0.1) * 0.3)


@som('ui/soltar_item', var=2, lufs=-22, espaco=None, desc='solta item no slot')
def _(v):
    d = 0.2
    return add(wood_knock(ru(240, 300), d) * 0.8, thump(150, 0.1, 0.3, 0.02, 0.2) * 0.4, clink(ru(1600, 2000), 0.1) * 0.2)


@som('ui/erro', var=1, lufs=-20, espaco=None, desc='acao negada (sem mana, sem espaco, sem alcance)')
def _(v):
    d = 0.35
    y = add(wood_knock(110, d) * 1.0, thump(80, 0.3, 0.2, 0.06, 0.2) * 0.6)
    y = place(y, wood_knock(100, 0.25) * 0.8, 0.11)
    return y


@som('ui/sem_recurso', var=1, lufs=-20, espaco='quarto', mix=0.1, desc='skill sem recurso/mana: estalo falho')
def _(v):
    d = 0.5
    t = tt(d)
    y = lp(saw(220 * np.exp(-t / 0.15) + 60, d), 1200) * env_exp(d, 0.1) * 0.6
    y += zap(d, 0.25) * env_exp(d, 0.06)
    return y


@som('ui/skill_pronta', var=1, lufs=-22, espaco='rua', mix=0.15, desc='recarga da skill terminou')
def _(v):
    return add(coin(3600, 0.5) * 0.5, sine(hz('A5'), 0.4) * env_exp(0.4, 0.12) * 0.15)


@som('ui/missao_aceita', var=1, lufs=-18, espaco='catedral', mix=0.25, desc='aceitou missao: sino grave + pena')
def _(v):
    d = 2.5
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(bell(hz('D4'), 2.4, 1.6, 1.0) * 0.6), 0)
    y = place(y, to_stereo(bell(hz('A4'), 2.0, 1.2, 1.0) * 0.3), 0.12)
    y = place(y, to_stereo(bbp(crackle(0.4, 200, 0.002), 2000, 8000) * env_exp(0.4, 0.15) * 0.4), 0.05)
    return y


@som('ui/missao_atualizada', var=1, lufs=-21, espaco='rua', mix=0.2, desc='progresso de missao (3/10 Corvos)')
def _(v):
    return add(bell(hz('A5'), 1.0, 0.5, 1.2) * 0.4, bell(hz('D6'), 0.8, 0.4, 1.2) * 0.2)


@som('ui/missao_concluida', var=1, lufs=-15, espaco='catedral', mix=0.3, desc='missao concluida: fanfarra curta de orgao e sinos')
def _(v):
    d = 4.0
    y = np.zeros((ns(d), 2))
    y = place(y, organ(['D3', 'A3', 'D4', 'F4'], 0.5, 'pleno', 0.002, 0.03, 0.15) * 1.0, 0)
    y = place(y, organ(['C3', 'G3', 'C4', 'E4'], 0.5, 'pleno', 0.002, 0.03, 0.15) * 1.0, 0.45)
    y = place(y, organ(['D3', 'A3', 'D4', 'F#4', 'A4'], 2.8, 'pleno', 0.002, 0.03, 1.8) * 1.1, 0.9)
    y = place(y, to_stereo(bell(hz('D5'), 3.0, 2.0, 1.2) * 0.5), 0.9)
    y = place(y, to_stereo(bell(hz('A5'), 2.5, 1.6, 1.2) * 0.3), 0.95)
    y = place(y, to_stereo(drum(55, 1.5, 0.5)) * 0.5, 0.9)
    return y


@som('ui/nivel_sobe', var=1, lufs=-13, espaco='catedral', mix=0.3, desc='level up: subida de coro, sinos e explosao de luz')
def _(v):
    d = 5.5
    y = np.zeros((ns(d), 2))
    sw = bp(white(1.2), np.linspace(300, 6000, ns(1.2)), 4) * env_pts(1.2, [(0, 0), (1.1, 1), (1.2, 0)], 2)
    y = place(y, widen(sw * 0.8), 0)
    y = place(y, choir(['D3', 'A3', 'D4', 'F#4', 'A4', 'D5'], 4.0, 'o', 'tenor', 4, 0.05, 2.5, vowel2='a') * 1.0, 1.1)
    y = place(y, to_stereo(sat(thump(40, 2, 2, 0.5, 0.3), 2) * 0.9), 1.1)
    y = place(y, to_stereo(drum(50, 2.0, 0.8)) * 0.6, 1.1)
    for i, nt in enumerate(['D5', 'F#5', 'A5', 'D6', 'F#6', 'A6']):
        y = place(y, pan(bell(hz(nt), 3, 1.6, 1.3) * 0.22, -0.7 + 0.28 * i), 1.1 + i * 0.07)
    return y


@som('ui/notificacao', var=1, lufs=-22, espaco='rua', mix=0.2, desc='notificacao generica / mensagem de sistema')
def _(v):
    return add(bell(hz('E5'), 1.0, 0.5, 1.1) * 0.4, wood_knock(400, 0.1) * 0.2)


@som('ui/chat', var=1, lufs=-26, espaco=None, desc='mensagem de chat chegou')
def _(v):
    return add(wood_knock(500, 0.12) * 0.6, clink(3000, 0.1) * 0.2)


@som('ui/comprar', var=1, lufs=-18, espaco='quarto', mix=0.1, desc='compra no vendedor: moedas no balcao')
def _(v):
    y = coins(0.7, 5)
    return place(y, wood_knock(180, 0.2) * 0.6, 0.0)


@som('ui/vender', var=1, lufs=-18, espaco='quarto', mix=0.1, desc='venda: moedas caindo na bolsa')
def _(v):
    y = coins(0.8, 7)
    return place(y, cloth(0.2, 0.6), 0.5)


@som('ui/confirmar', var=1, lufs=-20, espaco='rua', mix=0.15, desc='confirmar / entrar no jogo')
def _(v):
    d = 1.2
    return add(clang(800, 0.5, 1.1, 0.1, 0.5) * 0.4, bell(hz('D5'), d, 0.6, 1.2) * 0.4, thump(70, 0.4, 0.8, 0.08, 0.2) * 0.5)


@som('ui/vida_baixa', var=1, lufs=-18, espaco=None, loop=True, desc='loop de coracao acelerado quando HP < 30%')
def _(v):
    return lp(heartbeat(4.0, 90, 1.0), 400)


@som('ui/tela_morte', var=1, lufs=-15, espaco='infinito', mix=0.4, desc='tela "voce morreu": sino funebre e coro grave')
def _(v):
    d = 8.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(bell(hz('C3'), 7, 5, 0.8) * 0.8), 0)
    y = place(y, choir(['C2', 'G2', 'C3', 'Eb3'], 6.5, 'u', 'baixo', 6, 2.0, 3.0, vowel2='o') * 0.9, 0.3)
    y = place(y, organ(['C2', 'G2', 'Eb3'], 6, 'grave', 0.004, 1.5, 3) * 0.7, 0.3)
    return y


@som('ui/ressuscitar', var=1, lufs=-16, espaco='catedral', mix=0.3, desc='renasce no acampamento: respiracao funda + luz')
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(breath(1.0, 'a', 'baixo', True, 1.0)), 0)
    y = place(y, choir(['A3', 'E4', 'A4', 'C#5'], 2.4, 'a', 'alto', 4, 0.6, 1.4) * 0.6, 0.6)
    y = place(y, to_stereo(bell(hz('A5'), 2, 1.2, 1.2) * 0.3), 0.9)
    return y

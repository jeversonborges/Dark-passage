# Vinheta do Deserto de Absinto revisado: um chão só (areia cinza-ocre com veios do Amargo),
# o mesmo vocabulário de props em toda parte (prédio enterrado, mastro, trilho, duna, lápide,
# árvore morta) e as zonas diferenciadas só por densidade e por um marco.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cena as C
from cena import por
Q = os.environ.get("Q") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "deserto")
C.iniciar(ceu=(.02, .022, .03), luzes=False)
C.sol((.62, .7, .95), 1.15, C.K.KEY_ROT, .05, "lua")
C.sol((.9, .45, .2), .55, (-55, 0, 165), .1, "rim")
C.sol((.3, .34, .45), .3, (70, 0, 110), .2, "fill")
r = random.Random(11)
RX = lambda x: 10 + 4.5*math.sin(x*.11) + 1.5*math.sin(x*.31)      # curso do leito seco
rio = [(x, RX(x)) for x in range(-44, 46, 3)]
C.faixa("leito", rio, [6.5 + 1.5*math.sin(i*.9) for i in range(len(rio))], seed=5, nome="leito")
for (x, rr) in [(-14, 1.0), (-8, 1.3), (7, .9), (15, 1.5), (24, 1.0)]:
    C.mancha("agua_toxica", (x, RX(x)), rr, seed=int(abs(x)*7) % 50, nome="poca")
for x in range(-40, 40, 3):
    if r.random() < .55: por(r.choice(["pedras_rio", "juncos", "tronco_margem"]), x + r.uniform(-1, 1), RX(x) + r.choice([-1, 1])*r.uniform(2.6, 3.6), r.uniform(0, 360))
for x in (-8, 7, 15): por("planta_mutante", x + 1.6, RX(x) + 1.2, r.uniform(0, 360))
# vidro: uma mancha só (eco dos Campos de Cinza)
C.mancha("vitrificada", (27, -6), 6.5, seed=9, irregular=.45, nome="vidro")
por("cratera_cinza", 27, -6); por("estandarte_rasgado", 25, -3.5, 20); por("elmo_espada_fincada", 29.5, -4)
# a Linha 7 atravessa a cena e cruza o leito pela ponte de ferro
XR = -4
for k in range(-40, 50):
    y = k*C.T
    if abs(y - RX(XR)) < 3.2: continue
    por("trilho_bonde", XR, y, 90)
por("ponte_ferro_bonde", XR, RX(XR), 0)
por("bonde_veleiro", XR, -8, 90)
for y in (-20, -2, 20, 30): por("poste_mastro", XR + 1.4, y)
# a cidade enterrada no fundo (mesmas palavras em toda parte)
por("predio_enterrado", -14, 26, 0); por("predio_enterrado", 0, 33, 90); por("predio_enterrado", -28, 16, 0)
por("predio_enterrado", 14, 30, 0)
por("torre_relogio_enterrada", 26, 22, 0)
por("chamine_enterrada", -6, 38); por("chamine_enterrada", 22, 34); por("chamine_enterrada", -22, 30)
por("janela_na_areia", -9, 18, 0); por("placa_rua_enterrada", 4, 21, 0); por("telhado_no_abismo", 8, 24, 0) if "telhado_no_abismo" in C.A.REG else None
por("cupula_estacao", -24, -2, 0)
# acampamento da vela em primeiro plano, perto do trilho
por("tenda_vigilia", 6, -16, 20); por("tenda_vigilia", 1, -20, -30); por("barraco_sucata", -10, -16, 0)
por("lampada_arco", 3, -12); por("fogueira", 5, -12.5); por("tonel_fogo", -6, -13); por("tonel_fogo", 9, -20)
por("varal_roupas", 10, -15, 30); por("caixas", 8.5, -11); por("barris", -7, -18); por("sacos_areia", 11, -11, 90)
por("sacos_areia", -1, -10.5, 0); por("caixa_dagua_sucata", -12, -21)
C.ponto((5, -12.5, 1.2), (1, .5, .18), 1400, .5); C.ponto((-6, -13, 1.4), (1, .45, .15), 500, .3); C.ponto((9, -20, 1.4), (1, .45, .15), 500, .3)
# cemitério: lápides saindo da mesma areia, com a torre do sino
for (x, y) in [(18, 6), (22, 9), (25, 4), (20, 1)]: por("mar_de_lapides", x, y, r.uniform(0, 360))
por("torre_sino", 25, 12, 0)
# vida seca e mutante, igual em toda parte
for k in range(110):
    x, y = r.uniform(-42, 42), r.uniform(-34, 40)
    if abs(x - XR) < 2 or abs(y - RX(x)) < 4 or (-14 < x < 13 and -23 < y < -9): continue
    por(r.choice(["mato_seco", "mato_seco_2", "arbusto_seco", "arbusto_seco_2", "cacto_seco", "moita_cardo", "ossada_animal", "vidro_estilhacos"]), x, y, r.uniform(0, 360))
for (x, y) in [(-16, 6), (10, 17), (-32, 24), (34, -18), (-20, -26), (16, -26), (-34, 2)]: por(r.choice(["arvore_morta", "arvore_morta_2"]), x, y, r.uniform(0, 360))
por("arvore_morta_grande", -11, 4, 40)
por("ossada_gigante", -22, -12, 30); por("placa_radiacao", -6, -6, 0); por("tambores_radioativos", -15, 0)
for k in range(16):
    por(r.choice(["duna_areia", "duna_ondulacao"]), r.uniform(-42, 42), r.uniform(-34, 40), r.uniform(0, 360), r.uniform(1.0, 1.6))

# ---- beleza: o fim do mundo também floresce
K = C.K
def flor_absinto(m, seed=0):
    """Touceira de flor-de-absinto: hastes finas e pétalas que brilham verde-água (comem o Amargo)."""
    r = random.Random(seed)
    haste = K.mat_solid("haste", (.05, .07, .04), 0, .7)
    petala = K.mat_emit("petala_absinto", (.45, 1, .75), 6)
    miolo = K.mat_emit("miolo_absinto", (1, .95, .6), 10)
    for k in range(r.randint(7, 12)):
        a, d = r.uniform(0, 6.28), r.uniform(0, .35); x, y = math.cos(a)*d, math.sin(a)*d
        h = r.uniform(.25, .6); tx, ty = x + r.uniform(-.08, .08), y + r.uniform(-.08, .08)
        K.along(haste, (x, y, 0), (tx, ty, h), .008, verts=4)
        for p in range(5):
            t = p/5*6.28
            K.sphere(petala, (tx + math.cos(t)*.035, ty + math.sin(t)*.035, h), (.03, .03, .008), segs=6)
        K.sphere(miolo, (tx, ty, h + .01), (.015, .015, .015), segs=6)
def lanternas(m, n=9, L=8.0, sag=.9, h=3.2, seed=0):
    """Varal de lanternas de lata entre dois mastros: a luz que os sobreviventes penduram."""
    r = random.Random(seed); fio = K.mat_solid("fio", (.03, .03, .03), .3, .6)
    cores = [(1, .55, .2), (1, .7, .35), (.95, .35, .15), (1, .8, .5)]
    pts = [(-L/2 + i*L/20, 0, h - sag*math.sin(math.pi*i/20)) for i in range(21)]
    for a, b in zip(pts, pts[1:]): K.along(fio, a, b, .01, verts=4)
    for x0 in (-L/2, L/2): K.along(m["wood_d"], (x0, 0, 0), (x0, 0, h + .2), .05, verts=6)
    for i in range(1, n+1):
        t = i/(n+1); x = -L/2 + t*L; z = h - sag*math.sin(math.pi*t) - .15
        c = r.choice(cores)
        K.cyl(K.mat_emit("lant%d" % cores.index(c), c, 9), (x, 0, z), .06, .14, verts=8)
        K.cyl(m["tin"], (x, 0, z + .09), .07, .03, verts=8)
for (x, y, s) in [(-12, 10, 1), (-10, 12.5, 1.2), (-6, 13, .9), (5, 7.5, 1.1), (8, 8.5, 1), (13, 8, 1.2), (16, 9.5, 1), (22, 12, .9), (-18, 12, 1), (1, 11.5, .8)]:
    C.grupo(lambda m, s_=int(abs(x))*13: flor_absinto(m, s_), x, y, 0, s*1.8, chave="flor%d" % (int(abs(x)) % 4))
for (x, y, s) in [(-3, -17, 1.1), (7, -9, .9), (-9, -12, 1), (12, -14, .8)]:
    C.grupo(lambda m, s_=int(abs(x))*7: flor_absinto(m, s_), x, y, 0, s*1.6, chave="florc%d" % (int(abs(x)) % 3))
C.grupo(lambda m: lanternas(m, 9, 9, .9, 3.4, 1), 2, -14, 30, chave="lant1")
C.grupo(lambda m: lanternas(m, 7, 7, .7, 3.0, 2), -6, -18, -40, chave="lant2")
C.grupo(lambda m: lanternas(m, 8, 8, .8, 3.6, 3), 9.5, -17, 75, chave="lant3")
for (x, y) in [(-2.5, -11), (6.5, -17), (13.5, -15)]: C.ponto((x, y, 2.6), (1, .6, .3), 120, .4)
for (x, y) in [(-8, 11.5), (8, 8.5), (16, 9.5)]: C.ponto((x, y, .6), (.45, 1, .75), 40, .3)
C.chao("areia", 180, ondula=.12, seed=3, z=-.07)
C.render(OUT, centro=(0, 6), largura=56, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)

# Mãe Cardo, Cozinheira do Acampamento da Vela. Senhora baixinha e corcunda; o braço esquerdo enorme, coberto de
# placas verdes de praga (anos bebendo a água amarga do deserto), é o que mexe o caldeirão do tamanho de uma
# banheira: ela anda com a concha de pau comprida no ombro. Lenço florido na cabeça, vestido de chita desbotado,
# avental remendado, chinelos de corda. Único brilho: o verde do Amargo nas frestas das placas.
from kit import *

INFO = info("vigilia", tz=.82, escala=.86)

def build():
    R = rig("mae_cardo")
    skin = pele("mc_pele", (.4, .28, .21), sujo=.4, rubor_amt=.35)
    praga = stained("mc_placas", (.13, .2, .1), stain=(.05, .07, .03), amount=.5, scale=9, rough=.4, blotch=(.2, .26, .12),
                    blotch_amt=.6, grime=.4)
    amargo = glow("mc_amargo", (.35, 1.0, .35), 2.2)
    vestido = pano("mc_vestido", (.2, .11, .08), vinco=.4, desbote=.45, pintas=[((.32, .26, .12), 22, .12)], grime=1.1)
    lenco_m = pano("mc_lenco", (.3, .07, .06), vinco=.2, desbote=.35, pintas=[((.45, .4, .18), 30, .14), ((.1, .2, .1), 24, .1)])
    avent = pano("mc_avental", (.32, .3, .25), vinco=.3, desbote=.2, remendo=(.18, .14, .09), rem_amt=.25, mancha=(.08, .05, .02), mancha_amt=.6)
    corda = mat("mc_corda", (.24, .18, .1), 0, .9, dirt=.5)
    mad = madeira("mc_madeira", (.2, .12, .06))
    cab = cabelo("mc_cabelo", (.2, .19, .18), grisalho=.7)
    corpo(R, skin, vestido, vestido, mangas=vestido, mulher=True, busto=.7, barriga=.5, massa=1.05, corcunda=.9, descalco=True,
          punho=1.1)
    aba(R, vestido, z0=1.05, z1=.2, aberto=0, rodado=1.1, jag=.02, seed=2, folds=9, famp=.05)
    avental(R, avent, z1=.45, w0=.15, w1=.18, y=-.17, curva=.05, seed=5, tiras=avent)
    # mangas arregaçadas na direita, braço esquerdo de praga: placas sobrepostas, saliências, frestas acesas
    o_, ax, u, sd = R.frame("upper_arm.L"); pl = []
    rr = random.Random(9)
    for bn, n_, r0 in (("upper_arm.L", 9, .085), ("forearm.L", 9, .075)):
        a, b = R.P(bn), R.P(bn, 1); d = (b - a).normalized()
        side = d.cross(Vector((0, 1, 0))).normalized(); up = d.cross(side).normalized()
        for k in range(n_):
            t = (k + .5)/n_; ang = rr.uniform(0, 2*math.pi); c = a.lerp(b, t)
            nrm = (side*math.cos(ang) + up*math.sin(ang))
            pp = prim("primitive_uv_sphere_add", praga, c + nrm*r0*.75, (.05, .045, .022), segments=10, ring_count=6)
            pp.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); pl.append(pp)
        R.rigid(pl, bn); pl = []
        frestas = []
        for k in range(5):
            t = rr.uniform(.15, .85); ang = rr.uniform(0, 2*math.pi); c = a.lerp(b, t)
            nrm = (side*math.cos(ang) + up*math.sin(ang))
            frestas.append(along("primitive_cylinder_add", amargo, c + nrm*r0*.95 - d*.03, c + nrm*r0*.95 + d*.03, .005, vertices=4))
        R.rigid(frestas, bn)
    # braço grande: volume por cima da manga (pele de praga) e mão enorme
    a, el, wr = R.P("upper_arm.L"), R.P("forearm.L"), R.P("hand.L")
    bj = {"s": (*a, .085), "b": (*a.lerp(el, .5), .095), "e": (*el, .075), "f": (*el.lerp(wr, .5), .085), "w": (*wr, .065)}
    R.bind(skin_mesh("mc_bracao", bj, [("s", "b"), ("b", "e"), ("e", "f"), ("f", "w")], praga), ["chest", "upper_arm.L", "forearm.L"])
    o_, ax, u, sd_ = R.frame("hand.L")
    mg = [prim("primitive_uv_sphere_add", praga, o_ + ax*.06, (.06, .065, .075), segments=12, ring_count=8)]
    for f in range(4):
        mg.append(along("primitive_cone_add", praga, o_ + ax*.1 + sd_*(-.04 + .027*f), o_ + ax*.17 + sd_*(-.045 + .03*f) + u*.02, .02,
                        vertices=6, radius1=1, radius2=.6))
    R.rigid(mg, "hand.L")
    # concha de pau comprida apoiada no ombro (cabo de remo, cuia de cabaça)
    G = grip(R, "L"); top = G + Vector((0, -.05, .0)); cs = []
    cs.append(along("primitive_cylinder_add", mad, G + Vector((0, .25, 0)), G + Vector((0, -.95, 0)), .018, vertices=8))
    cb = G + Vector((0, -1.0, 0))
    cs.append(prim("primitive_uv_sphere_add", mad, cb, (.09, .09, .06), segments=12, ring_count=8))
    cs.append(prim("primitive_torus_add", corda, G + Vector((0, -.2, 0)), (1, 1, 1), major_radius=.022, minor_radius=.006, rot=(90, 0, 0)))
    R.rigid(cs, "prop.L")
    # chinelos de corda
    for n in "LR":
        R.rigid([prim("primitive_cube_add", corda, R.P(f"foot.{n}") + Vector((0, -.05, -.075)), (.045, .1, .008))], f"foot.{n}")
    # cabeça: rosto redondo e enrugado, lenço florido com nó, mechas brancas escapando
    hd = cabeca(R, skin, mulher=True, idade=.85, queixo=1.05, nariz=1.1, sobrancelha=cab)
    hd += lenco(lenco_m)
    for sd in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", cab, HC + Vector((.08*sd, -.03, -.02)), (.018, .03, .03), segments=8, ring_count=6))
    R.rigid(hd, "head")
    return fim(R, INFO)

# concha no ombro esquerdo (braço de praga erguido), direita na cintura dobrada sobre o avental
BASE = {"upper_arm.L": {"y": 14, "x": -22}, "forearm.L": {"bend": -128}, "aim": {"prop.L": (-.05, .75, .6)},
        "upper_arm.R": {"y": -30, "x": -14}, "forearm.R": {"bend": -60},
        "spine": {"x": 8}, "chest": {"x": 10}, "neck": {"x": -8}, "head": {"x": -12}}

def anims(R):
    def ex(i, n):  # balança a cabeça rindo baixinho
        return {"head": {"x": 4*max(0, wave(i, n*.5))}, "chest": {"x": 2*wave(i, n, ph=1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, .8), passo=14)

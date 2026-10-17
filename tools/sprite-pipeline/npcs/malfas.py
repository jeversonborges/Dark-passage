# Malfas, Penhorista do Abismo (Arautos, pátio da Capela). Demônio que veio pela promessa da Terra arruinada e montou
# uma casa de penhores. Baixo e largo, pele de brasa apagada (vermelho-tijolo com fissuras escuras), chifres grossos
# curvos com argolas de latão, sobretudo de couro sem mangas cheio de bolsos costurados por dentro (forro à mostra),
# colete listrado, monóculo de vidro verde tirado das dunas da batalha, corrente de etiquetas de penhor no pescoço
# (cada uma com um nome), rabo com argola, garras com anéis. Pesa uma etiqueta na mão e sorri. Sem brilho (o
# monóculo é vidro, reflete).
from kit import *

INFO = info("arautos", tz=.86, escala=.95)

def build():
    R = rig("malfas")
    skin = pele("mf_pele", (.28, .08, .05), sujo=.5, rubor=(.12, .03, .02), rubor_amt=.5, marcas=(.06, .02, .015), marcas_amt=.7, rough=.5)
    cou = couro("mf_sobretudo", (.07, .04, .025), rachado=.7, gasto=.5)
    forro = pano("mf_forro", (.2, .05, .05), vinco=.3, listra=(.25, .17, .06), listra_per=.02)
    colete = pano("mf_colete", (.16, .12, .06), listra=(.08, .06, .03), listra_per=.014, vinco=.25)
    calca = pano("mf_calca", (.05, .045, .04), vinco=.4)
    chif = stained("mf_chifre", (.08, .06, .045), stain=(.25, .2, .14), amount=.4, scale=12, rough=.5, grime=.3)
    lat = latao("mf_latao", amount=.3); fer = ferro("mf_ferro")
    papel = pano("mf_etiqueta", (.45, .4, .3), vinco=.05, mancha_amt=.4)
    corpo(R, skin, colete, calca, mangas=skin, maos=skin, botas=couro("mf_bota", (.03, .02, .015)), massa=1.12, larg=1.2, barriga=.6, cano=.25)
    # sobretudo sem mangas, aberto, com o forro e os bolsos internos aparecendo
    aba(R, cou, z0=1.45, z1=.32, aberto=.75, rodado=1.15, larg=1.15, jag=.05, seed=4, folds=9, famp=.06,
        ossos=("chest", "spine", "hips", "thigh.L", "thigh.R"), nome="mf_casaco")
    aba(R, forro, z0=1.42, z1=.36, aberto=.78, rodado=1.1, larg=1.12, jag=.03, seed=4, folds=9, famp=.06, thick=.004,
        ossos=("chest", "spine", "hips", "thigh.L", "thigh.R"), nome="mf_forro")
    bl = []
    for sd in (1, -1):
        for k in range(3):
            bl.append(prim("primitive_cube_add", cou, (.16*sd, -.15 + .02*k, 1.25 - .17*k), (.008, .035, .04), rot=(0, 0, 35*sd)))
    R.rigid(bl, "spine")
    gola(R, cou, alta=.05, lapela=False)
    # corrente de etiquetas de penhor no pescoço
    pts = [Vector((.09, -.04, 1.5)), Vector((.08, -.13, 1.38)), Vector((0, -.17, 1.3)), Vector((-.08, -.13, 1.38)), Vector((-.09, -.04, 1.5))]
    ch = chain_links(fer, pts, r=.01, thick=.0028)
    rr = random.Random(2)
    for k in range(9):
        t = (k + .5)/9; p = pts[0].lerp(pts[-1], t); p.z = 1.5 - .2*math.sin(t*math.pi); p.y = -.04 - .13*math.sin(t*math.pi)
        ch.append(prim("primitive_cube_add", papel, p + Vector((0, -.012, -.035)), (.014, .002, .022), rot=(rr.uniform(-8, 8), 0, rr.uniform(-15, 15))))
    R.rigid(ch, "chest")
    # rabo com argola de latão
    rb = [p for p in catmull([(0, .1, .95), (0, .25, .75), (.05, .38, .45), (.12, .45, .2), (.2, .42, .08)], .03)]
    o, S = tube("mf_rabo", rb, [.035*(1 - .8*i/len(rb)) for i in range(len(rb))], skin)
    R.rigid([o, prim("primitive_torus_add", lat, Vector(rb[len(rb)*2//3]), (1, 1, 1), major_radius=.022, minor_radius=.005, rot=(60, 0, 0))], "hips")
    # garras com anéis e a etiqueta erguida na direita
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"hand.{n}")
        R.rigid([along("primitive_cone_add", chif, o_ + ax*.1 + sd_*(-.025 + .017*f), o_ + ax*.13 + sd_*(-.025 + .017*f) - u*.02, .007, vertices=5,
                       radius1=1, radius2=0) for f in range(4)]
                + [prim("primitive_torus_add", lat, o_ + ax*.085 + sd_*.0, (1, 1, 1), major_radius=.011, minor_radius=.003)], f"hand.{n}")
    G = grip(R, "R")
    R.rigid([prim("primitive_cube_add", papel, G + Vector((0, -.03, .07)), (.022, .002, .032)),
             along("primitive_cylinder_add", mat("mf_fio", (.3, .25, .15), 0, .8), G + Vector((0, -.03, .1)), G + Vector((0, -.03, .02)), .0015, vertices=4)], "prop.R")
    # cabeça: cara larga, sorriso, orelhas pontudas, chifres com argolas, monóculo verde no olho direito
    hd = cabeca(R, skin, idade=.5, queixo=1.2, nariz=1.2, esc=1.05, orelhas=False)
    for sd in (1, -1):
        hd.append(along("primitive_cone_add", skin, HC + Vector((.085*sd, .0, -.0)), HC + Vector((.15*sd, .03, .04)), .02, vertices=6, radius1=1, radius2=0))
        hd += chifre(chif, HC + Vector((.05*sd, -.02, .08)), (sd*.7, -.2, .7), comp=.22, r=.03, curva=Vector((sd*.3, .7, -.4)), n=7, aneis=lat)
    hd.append(prim("primitive_torus_add", lat, HC + Vector((-.034, -.113, .0)), (1, 1, 1), rot=(90, 0, 0), major_radius=.02, minor_radius=.003))
    hd.append(prim("primitive_cylinder_add", vidro("mf_monoculo", (.1, .35, .15), .05), HC + Vector((-.034, -.114, .0)), (.018, .018, .002), rot=(90, 0, 0), vertices=14))
    hd += chain_links(lat, [HC + Vector((-.05, -.11, -.01)), HC + Vector((-.09, -.08, -.1)), HC + Vector((-.08, -.04, -.17))], r=.005, thick=.0012)
    R.rigid(hd, "head")
    return fim(R, INFO)

CORES_EXTRA = "3a9a52"

# ergue a etiqueta contra a luz; a esquerda no bolso do colete
BASE = {"upper_arm.R": {"y": -16, "x": -46}, "forearm.R": {"bend": -100}, "hand.R": {"x": -20},
        "upper_arm.L": {"y": 34, "x": 6}, "forearm.L": {"bend": -55}, "head": {"z": -8, "x": -4}}

def anims(R):
    def ex(i, n):  # balança a etiqueta e mexe o rabo
        return {"hand.R": {"z": 14*wave(i, n)}, "head": {"y": 4*wave(i, n, ph=1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.2, 0), passo=16)

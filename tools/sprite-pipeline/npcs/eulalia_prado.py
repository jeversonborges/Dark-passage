# Eulália Prado, a Bibliotecária (neutra, Biblioteca Soterrada). Não-Julgada: morreu de febre do Amargo no Ano 3,
# levantou para um Juízo que não veio e voltou ao trabalho. Mulher magra de uns cinquenta anos, pele cinza de cera
# com veias escuras, coque preso com dois lápis, vestido de lã preto abotoado até o pescoço, mangas de proteção de
# cetim cinza até o cotovelo, óculos sem lentes pendurados numa corrente, crachá "BIBLIOTECA PÚBLICA · E. PRADO" e,
# por cima dele, o lacre de cera vermelha da trombeta intacto no peito. Carimbo de borracha na mão direita, fichas
# de empréstimo na esquerda. Sem brilho.
from kit import *

INFO = info("neutro", tz=.9, escala=.97)

def build():
    R = rig("eulalia_prado")
    cera = pele("eu_cera", (.26, .26, .24), sujo=.3, rubor=(.12, .13, .14), rubor_amt=.5, marcas=(.1, .1, .12), marcas_amt=.4, rough=.4)
    la = pano("eu_vestido", (.03, .029, .03), vinco=.45, desbote=.35, trama=110, grime=.9)
    cetim = pano("eu_cetim", (.22, .21, .21), vinco=.5, desbote=.2, rough=.35)
    bot = couro("eu_sapato", (.03, .025, .02), gasto=.6)
    lat = latao("eu_latao"); fer = ferro("eu_ferro")
    cab = cabelo("eu_cabelo", (.12, .11, .1), grisalho=.55)
    corpo(R, cera, la, la, mangas=la, botas=bot, maos=cera, mulher=True, magro=.84, busto=.35, cano=.1, punho=.95)
    aba(R, la, z0=1.05, z1=.14, aberto=0, rodado=.75, jag=.015, seed=2, folds=10, famp=.04)
    # gola alta abotoada e fileira de botões
    R.rigid([prim("primitive_cylinder_add", la, (0, -.008, 1.5), (.062, .058, .035), vertices=20)]
            + [prim("primitive_uv_sphere_add", fer, (0, -.12 + .0, 1.43 - .055*k), (.007,)*3, segments=6, ring_count=4) for k in range(6)], "chest")
    # mangas de proteção de cetim (antebraços)
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([along("primitive_cone_add", cetim, o_ + ax*.0, o_ + ax*.2, .066, vertices=16, radius1=1, radius2=.8),
                 prim("primitive_torus_add", cetim, o_ + ax*.19, (1, 1, 1), rot=tuple(math.degrees(v) for v in ax.to_track_quat('Z', 'Y').to_euler()),
                      major_radius=.05, minor_radius=.008)], f"forearm.{n}")
    # crachá de latão e o lacre de cera da trombeta por cima
    R.rigid([prim("primitive_cube_add", lat, (-.06, -.122, 1.33), (.035, .004, .016)),
             prim("primitive_cylinder_add", mat("eu_lacre", (.32, .03, .02), 0, .35), (-.045, -.128, 1.33), (.024, .024, .008), rot=(90, 0, 0), vertices=14),
             prim("primitive_cylinder_add", mat("eu_lacre2", (.22, .02, .015), 0, .35), (-.045, -.133, 1.33), (.014, .014, .004), rot=(90, 0, 0), vertices=10)]
            + chain_links(fer, [Vector((-.06, -.08, 1.47)), Vector((-.03, -.13, 1.36)), Vector((.03, -.13, 1.36)), Vector((.06, -.08, 1.47))], r=.007, thick=.0018)
            + [prim("primitive_torus_add", fer, Vector((.028*k, -.135, 1.35)), (1, 1, .7), rot=(90, 0, 0), major_radius=.014, minor_radius=.002) for k in (-1, 1)],
            "chest")
    # carimbo na direita, fichas na esquerda
    mad = madeira("eu_madeira", (.15, .08, .04)); bor = mat("eu_borracha", (.06, .04, .04), 0, .7)
    G = grip(R, "R")
    R.rigid([prim("primitive_uv_sphere_add", mad, G + Vector((0, -.02, .04)), (.02, .02, .025)),
             along("primitive_cylinder_add", mad, G + Vector((0, -.02, .02)), G + Vector((0, -.02, -.04)), .01, vertices=8),
             prim("primitive_cube_add", bor, G + Vector((0, -.02, -.05)), (.025, .018, .008))], "prop.R")
    papel = pano("eu_fichas", (.5, .47, .4), vinco=.05, mancha_amt=.3)
    G = grip(R, "L")
    R.rigid([prim("primitive_cube_add", papel, G + Vector((0, -.03, .02 + .005*k)), (.04, .028, .002), rot=(0, 0, 8*k)) for k in range(4)], "prop.L")
    # cabeça: rosto fino de cera, olheiras, coque com dois lápis
    hd = cabeca(R, cera, mulher=True, idade=.6, magro=.82, sobrancelha=cab)
    hd += coque(cab, lapis=mat("eu_lapis", (.4, .3, .05), 0, .6))
    R.rigid(hd, "head")
    return fim(R, INFO)

# carimbo erguido pronto para bater, fichas na esquerda
BASE = {"upper_arm.R": {"y": -22, "x": -28}, "forearm.R": {"bend": -70}, "upper_arm.L": {"y": 22, "x": -30}, "forearm.L": {"bend": -78},
        "head": {"x": 8}, "chest": {"x": -2}}

def anims(R):
    def ex(i, n):  # bate o carimbo uma vez por ciclo (seco), olha por cima dos óculos
        u = 1.0 if i in (4, 5) else 0.0
        return {"forearm.R": {"bend": 22*u}, "upper_arm.R": {"x": 8*u}, "head": {"x": 4*u}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=14)

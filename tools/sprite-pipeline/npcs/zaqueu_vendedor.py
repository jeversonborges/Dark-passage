# Zaqueu, Vendedor de Convites (Vigília). Contador de paróquia que virou corretor de tudo que sobe o Hermon; vende o
# convite dos Vigilantes e diz que não sabe quem o compra depois. Homem magro de colarinho sujo, colete de lã com
# corrente de relógio, mangas de camisa presas com ligas, braçadeira com a vela da Vigília, caderno de capa de couro
# preso ao cinto por corrente, lápis atrás da orelha. Na mão, um maço de convites lacrados (lacre vermelho) que ele
# abana como leque; óculos de meia-lua na ponta do nariz. Sem brilho.
from kit import *

INFO = info("vigilia", tz=.9)

def build():
    R = rig("zaqueu_vendedor")
    skin = pele("zq_pele", (.38, .27, .21), sujo=.35)
    camisa = pano("zq_camisa", (.34, .29, .21), vinco=.35, desbote=.2, mancha_amt=.45)
    colete = pano("zq_colete", (.13, .075, .04), vinco=.35, desbote=.35, remendo=(.08, .06, .04), rem_amt=.12)
    calca = pano("zq_calca", (.07, .065, .06), listra=(.1, .095, .085), listra_per=.03, vinco=.4)
    cou = couro("zq_couro", (.11, .06, .03)); bot = couro("zq_sapato", (.04, .03, .022), gasto=.6)
    lat = latao("zq_latao"); ver = pano("zq_lacre", (.35, .04, .03), vinco=0, desbote=0, mancha_amt=0)
    papel = pano("zq_papel", (.5, .46, .37), vinco=.1, mancha=(.12, .09, .05), mancha_amt=.4)
    cab = cabelo("zq_cabelo", (.05, .04, .035), grisalho=.15)
    corpo(R, skin, colete, calca, mangas=camisa, botas=bot, magro=.95, larg=.95, cano=.12, punho=1.05, manga_r=1.12, perna_r=1.16)
    # colete curto (sem aba), camisa por baixo, colarinho sujo, gravata fina
    R.rigid([prim("primitive_cylinder_add", camisa, (0, -.008, 1.49), (.068, .064, .026), vertices=20),
             along("primitive_cube_add", mat("zq_gravata", (.12, .03, .03), 0, .7, dirt=.6), (0, -.12, 1.46), (0, -.135, 1.3), .012),
             prim("primitive_uv_sphere_add", lat, (.0, -.132, 1.25), (.006,)*3), prim("primitive_uv_sphere_add", lat, (.0, -.13, 1.18), (.006,)*3)]
            + chain_links(lat, [Vector((.0, -.13, 1.15)), Vector((.06, -.135, 1.12)), Vector((.1, -.12, 1.13))], r=.007, thick=.002), "chest")
    # ligas nas mangas e braçadeira da Vigília (vela pintada)
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"upper_arm.{n}")
        R.rigid([prim("primitive_torus_add", cou, o_ + ax*.17, (1, 1, 1), major_radius=.066, minor_radius=.008,
                      rot=tuple(math.degrees(v) for v in ax.to_track_quat('Z', 'Y').to_euler()))], f"upper_arm.{n}")
    o_, ax, u, sd_ = R.frame("upper_arm.L")
    R.rigid([along("primitive_cylinder_add", pano("zq_bracadeira", (.32, .3, .26), vinco=.1), o_ + ax*.06, o_ + ax*.12, .07, vertices=14)], "upper_arm.L")
    cinto(R, cou, fivela=lat, z=1.0, r=.17, ry=.8, grosso=.016)
    # caderno de couro preso por corrente
    cd = [prim("primitive_cube_add", cou, (-.17, -.06, .9), (.012, .055, .075)),
          prim("primitive_cube_add", papel, (-.163, -.06, .9), (.006, .05, .07))]
    cd += chain_links(fer := ferro("zq_ferro"), [Vector((-.15, -.07, .99)), Vector((-.17, -.08, .95)), Vector((-.17, -.07, .975))], r=.008, thick=.002)
    R.rigid(cd, "hips")
    # maço de convites lacrados na mão direita
    G = grip(R, "R"); cv = []
    for k in range(5):
        p = prim("primitive_cube_add", papel, G + Vector((-.01 + .006*k, -.03 - .01*k, .03 + .006*k)), (.04, .003, .055), rot=(0, 0, -20 + 10*k))
        cv.append(p)
        cv.append(prim("primitive_cylinder_add", ver, G + Vector((-.01 + .006*k, -.034 - .01*k, .03 + .006*k)), (.01, .01, .003),
                       rot=(90, 0, -20 + 10*k), vertices=10))
    R.rigid(cv, "prop.R")
    # cabeça: rosto fino, cabelo emplastrado repartido, lápis atrás da orelha, óculos de meia-lua
    hd = cabeca(R, skin, idade=.45, magro=.85, nariz=1.15, queixo=.9, sobrancelha=cab)
    hd += cabelo_curto(cab, .97)
    hd.append(along("primitive_cylinder_add", mat("zq_lapis", (.4, .3, .05), 0, .6), HC + Vector((-.085, .0, .04)), HC + Vector((-.092, -.07, -.01)), .005, vertices=6))
    for sd in (1, -1):
        hd.append(prim("primitive_torus_add", lat, HC + Vector((.032*sd, -.112, -.02)), (1, 1, .6), rot=(90, 0, 0), major_radius=.016, minor_radius=.0025))
    R.rigid(hd, "head")
    return fim(R, INFO)

# convites erguidos na direita (oferecendo), esquerda no bolso do colete
BASE = {"upper_arm.R": {"y": -22, "x": -36}, "forearm.R": {"bend": -78}, "hand.R": {"x": -10},
        "upper_arm.L": {"y": 34, "x": 4}, "forearm.L": {"bend": -40}, "head": {"x": 4, "z": -6}}

def anims(R):
    def ex(i, n):  # abana os convites como leque
        return {"hand.R": {"z": 18*wave(i, n)}, "forearm.R": {"bend": 6*wave(i, n, ph=.7)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.3, .2))

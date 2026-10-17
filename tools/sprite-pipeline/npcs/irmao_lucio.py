# Lúcio, Irmão Acólito (Arautos, sacristia da Capela). Rapaz de uns dezoito anos que entrou no culto porque era o
# único lugar com comida durante o cerco; a irmã, Rosa, foi para a Vigília e ele escreve cartas para ela toda
# semana. Túnica vinho grande demais (mangas até os dedos, barra arrastando), capuz caído, cordão com nós, rosto
# magro cheio de espinhas e olheiras, cabelo escuro curto e despenteado. Balança o incensário quando fica nervoso,
# o que é sempre (a brasa do incensário é o único brilho); uma carta dobrada aparece no bolso.
from kit import *

INFO = info("arautos", tz=.88, escala=.97)

def build():
    R = rig("irmao_lucio")
    skin = pele("lu_pele", (.36, .26, .21), sujo=.3, marcas=(.38, .12, .1), marcas_amt=.5)
    vinho = pano("lu_tunica", (.15, .03, .035), vinco=.55, desbote=.4, remendo=(.1, .04, .04), rem_amt=.1, grime=1.1)
    corda = mat("lu_cordao", (.28, .22, .14), 0, .9, dirt=.5)
    lat = latao("lu_latao", amount=.45); fer = ferro("lu_ferro")
    cab = cabelo("lu_cabelo", (.04, .03, .025))
    corpo(R, skin, vinho, vinho, mangas=vinho, botas=couro("lu_sandalia", (.08, .05, .03)), maos=skin, magro=.82, larg=.88,
          punho=1.8, manga_r=1.25, cano=.06)
    aba(R, vinho, z0=1.05, z1=.03, aberto=0, rodado=.85, jag=.06, seed=8, folds=10, famp=.06)
    R.rigid(capuz(vinho, caido=True), "chest")
    co = [prim("primitive_torus_add", corda, (0, 0, 1.03), (1, .78, 1.3), major_radius=.15, minor_radius=.01)]
    co += tira(corda, [Vector((.06, -.12, 1.0)), Vector((.07, -.14, .8)), Vector((.065, -.15, .62))], w=.012, t=.01)
    for z in (.9, .75): co.append(prim("primitive_uv_sphere_add", corda, (.068, -.145, z), (.014,)*3))
    papel = pano("lu_carta", (.45, .42, .35), vinco=.05)
    co.append(prim("primitive_cube_add", papel, (-.1, -.135, 1.04), (.03, .004, .04), rot=(0, 0, 15)))
    R.rigid(co, "hips")
    # incensário pendurado em correntes na mão direita, com a brasa acesa
    G = grip(R, "R"); ic = []
    for sd in (1, -1):
        ic += chain_links(fer, [G + Vector((0, -.02, 0)), G + Vector((.02*sd, -.02, -.28))], r=.007, thick=.002)
    c = G + Vector((0, -.02, -.33))
    ic.append(prim("primitive_uv_sphere_add", lat, c, (.05, .05, .045), segments=14, ring_count=8))
    ic.append(prim("primitive_cone_add", lat, c + Vector((0, 0, .055)), (.04, .04, .03), vertices=12))
    for k in range(6):
        a = k*math.pi/3
        ic.append(prim("primitive_uv_sphere_add", glow("lu_brasa", (1.0, .45, .15), 3.5), c + Vector((.045*math.cos(a), .045*math.sin(a), .0)), (.008,)*3, segments=6, ring_count=4))
    ic.append(prim("primitive_cylinder_add", lat, c + Vector((0, 0, -.05)), (.025, .025, .01), vertices=10))
    R.rigid(ic, "prop.R")
    # cabeça: rosto magro, olheiras, espinhas, cabelo despenteado
    hd = cabeca(R, skin, idade=.05, magro=.82, queixo=.9, sobrancelha=cab)
    for sd in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", mat("lu_olheira", (.12, .06, .07), 0, .6), HC + Vector((.032*sd, -.097, -.02)), (.018, .006, .008)))
    hd += cabelo_curto(cab, 1.02)
    rr = random.Random(6)
    for k in range(8):
        a = rr.uniform(-1.5, 1.5)
        hd.append(along("primitive_cone_add", cab, HC + Vector((.06*math.sin(a), -.07*math.cos(a), .07)), HC + Vector((.09*math.sin(a), -.1*math.cos(a), .03)),
                        .014, vertices=4, radius1=1, radius2=0))
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -20, "x": -22}, "forearm.R": {"bend": -50}, "upper_arm.L": {"y": 30, "x": -24}, "forearm.L": {"bend": -88},
        "chest": {"x": 6}, "head": {"x": 10}, "spine": {"x": 4}}

def anims(R):
    def ex(i, n):  # balança o incensário (nervoso) e olha para trás
        return {"hand.R": {"x": 30*wave(i, n)}, "forearm.R": {"bend": 8*wave(i, n)}, "head": {"z": 10*wave(i, n, ph=2)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.4, .4), passo=17)

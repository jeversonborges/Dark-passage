# Corvina, Atravessadora de Segredos (neutra, linha E). Ex-cultista da Capela que descobriu que segredo vale mais
# que fé. Mulher jovem de capa de penas pretas costuradas em couro (do pescoço até a canela, gola alta de penas),
# metade do rosto pintada de branco osso e metade limpa, um olho de vidro verde (único brilho, fraco), cabelo preto
# curto com mecha caindo no olho, corpete de couro com fivelas, saia de couro rasgada, botas de cano alto. Entre os
# dedos, uma carta lacrada com cera dos dois lados (preta e vermelha); no cinto, um molho de chaves e um tinteiro.
from kit import *

INFO = info("neutro", tz=.9, escala=.97)

def build():
    R = rig("corvina_atravessadora")
    skin = pele("cv_pele", (.35, .27, .23), sujo=.2)
    osso = pele("cv_pintura", (.55, .52, .45), sujo=.3, rubor_amt=0)
    pena_m = pano("cv_penas", (.022, .022, .028), vinco=.2, desbote=.15, trama=200, rough=.45)
    pena_c = pano("cv_penas2", (.05, .05, .065), vinco=.2, desbote=.2, trama=200, rough=.4)
    cou = couro("cv_couro", (.05, .03, .025), rachado=.5)
    saia = couro("cv_saia", (.08, .035, .03), rachado=.4)
    bot = couro("cv_bota", (.03, .025, .02))
    lat = latao("cv_latao"); fer = ferro("cv_ferro")
    cab = cabelo("cv_cabelo", (.02, .02, .025), fios=120)
    corpo(R, skin, cou, saia, mangas=pena_m, botas=bot, maos=skin, mulher=True, magro=.88, busto=.55, cano=.45, punho=1.1)
    aba(R, saia, z0=1.03, z1=.55, aberto=.25, rodado=.8, jag=.08, seed=3, folds=7, famp=.06)
    # corpete: fivelas na frente
    R.rigid([prim("primitive_cube_add", lat, (0, -.11 - .005*k, 1.12 + .06*k), (.018, .005, .006)) for k in range(4)], "spine")
    # capa de penas: base de couro + fileiras de penas sobrepostas
    capa(R, pena_m, z1=.38, aberto=1.3, jag=.1, seed=8, gola_alta=.05)
    rr = random.Random(4); pn = []; bm = bmesh.new()
    for row in range(9):
        z = 1.48 - row*.12; ang0 = .5; rad = .2 + row*.016
        for k in range(16):
            a = -math.pi/2 + ang0 + (2*math.pi - 2*ang0)*(k + .5*(row % 2))/16
            if math.sin(a) < -.2 and row > 1: continue
            base = Vector((rad*math.cos(a)*1.12, .03 + rad*math.sin(a)*.8, z))
            out = Vector((math.cos(a)*.06, math.sin(a)*.06, -1)).normalized(); nrm = Vector((math.cos(a), math.sin(a)*.75, 0)).normalized()
            pena(bm, base, out, nrm, .2*rr.uniform(.85, 1.15), .05, rr, curl=.01)
    o = obj_from_bm("cv_penas_capa", bm, pena_c); o.modifiers.new("s", 'SOLIDIFY').thickness = .006; apply_mods(o)
    R.bind(o, ["chest", "spine", "hips", "thigh.L", "thigh.R"], power=3)
    # gola alta de penas
    gp = []; bm = bmesh.new()
    for k in range(18):
        a = -math.pi/2 + .7 + (2*math.pi - 1.4)*k/17
        base = Vector((.09*math.cos(a), -.01 + .085*math.sin(a), 1.47)); up = Vector((math.cos(a)*.35, math.sin(a)*.35, 1)).normalized()
        pena(bm, base, up, Vector((math.cos(a), math.sin(a), 0)), .12, .03, rr, curl=-.02)
    o = obj_from_bm("cv_gola", bm, pena_m); o.modifiers.new("s", 'SOLIDIFY').thickness = .006; apply_mods(o)
    R.rigid([o], "chest")
    cinto(R, cou, fivela=lat, z=1.0, r=.16, ry=.8, grosso=.016)
    R.rigid(chain_links(fer, [Vector((.15, -.06, .98)), Vector((.16, -.07, .9)), Vector((.15, -.05, .85))], r=.012, thick=.003)
            + [prim("primitive_cylinder_add", vidro("cv_tinteiro", (.02, .03, .06)), (-.15, -.06, .94), (.022, .022, .03), vertices=10)], "hips")
    # carta lacrada com cera dos dois lados entre os dedos da direita
    G = grip(R, "R"); papel = pano("cv_carta", (.45, .4, .32), vinco=.1)
    R.rigid([prim("primitive_cube_add", papel, G + Vector((0, -.04, .04)), (.05, .003, .035), rot=(0, 0, 25)),
             prim("primitive_cylinder_add", mat("cv_cera_v", (.3, .03, .02), 0, .4), G + Vector((0, -.045, .04)), (.012, .012, .004), rot=(90, 0, 0), vertices=10),
             prim("primitive_cylinder_add", mat("cv_cera_p", (.02, .02, .02), 0, .3), G + Vector((0, -.035, .04)), (.012, .012, .004), rot=(90, 0, 0), vertices=10)],
            "prop.R")
    # cabeça: metade direita pintada de branco osso com a órbita preta, olho esquerdo de vidro verde
    olho = glow("cv_olho", (.4, 1.0, .5), 1.6)
    hd = cabeca(R, skin, mulher=True, idade=.1, queixo=.9, olho_vidro=(1, olho), sobrancelha=cab)
    pt = prim("primitive_uv_sphere_add", osso, HC + Vector((-.004, -.003, -.01)), (.081, .099, .112), segments=18, ring_count=12)
    me = pt.data
    for v in me.vertices:
        if v.co.x > 0: v.co.x = -.001   # meia esfera: só o lado direito do rosto
    hd.append(pt)
    hd.append(prim("primitive_uv_sphere_add", escuro(), HC + Vector((-.032, -.094, .0)), (.026, .01, .022), segments=10, ring_count=6))
    hd += cabelo_curto(cab, 1.0)
    hd.append(along("primitive_cone_add", cab, HC + Vector((.03, -.08, .09)), HC + Vector((.05, -.11, -.01)), .028, vertices=6, radius1=1, radius2=.2))
    R.rigid(hd, "head")
    return fim(R, INFO)

# carta na direita perto do rosto (oferecendo um segredo), esquerda escondida na capa
BASE = {"upper_arm.R": {"y": -18, "x": -40}, "forearm.R": {"bend": -110}, "hand.R": {"x": -20, "z": 20},
        "upper_arm.L": {"y": 30, "x": -4}, "forearm.L": {"bend": -55}, "head": {"z": 10, "y": 6}}

def anims(R):
    def ex(i, n):  # gira a carta entre os dedos
        return {"hand.R": {"y": 25*wave(i, n)}, "head": {"y": 3*wave(i, n, ph=1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.4, .2))

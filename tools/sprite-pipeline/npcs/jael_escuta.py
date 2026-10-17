# Jael, a Escuta (Jerusalém, Arautos). Mulher jovem de batina do Coro rasgada nas mangas, fone de latão sempre num ouvido,
# cabos enrolados nos braços como terço; ouve o rádio do Coro numa caixa de válvulas pendurada no ombro. Sem brilho
# próprio: a válvula fica apagada (escuta no escuro).
from kit import *

INFO = info("arautos", tz=.88)

def build():
    R = rig("jael_escuta")
    skin = pele("ja_pele", (.4, .28, .21), sujo=.3)
    bat = pano("ja_batina", (.05, .045, .05), vinco=.45, desbote=.45, mancha_amt=.4, grime=1.0)
    lat = latao("ja_latao"); cou = couro("ja_couro", (.1, .06, .03)); fio = mat("ja_cabo", (.06, .03, .02), 0, .5)
    cab = cabelo("ja_cabelo", (.06, .04, .03), fios=110)
    corpo(R, skin, bat, bat, mangas=skin, botas=couro("ja_bota", (.04, .03, .02)), maos=skin, mulher=True, magro=.9, busto=.45)
    aba(R, bat, z0=1.05, z1=.12, aberto=0, rodado=.95, jag=.06, seed=17, folds=12, famp=.03)
    # mangas rasgadas: tiras penduradas
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"upper_arm.{n}")
        R.rigid(tira(bat, [o_ + ax*.05, o_ + ax*.2 - u*.03], w=.08, t=.005), f"upper_arm.{n}")
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        cb = []
        for k in range(5): cb.append(prim("primitive_torus_add", fio, o_ + ax*(.05 + .035*k), (1, 1, 1), rot=(90, 0, 0), major_radius=.042, minor_radius=.004))
        R.rigid(cb, f"forearm.{n}")
    # caixa de válvulas no quadril presa por alça
    cx = [prim("primitive_cube_add", cou, (.18, .02, .92), (.04, .07, .06)), prim("primitive_cube_add", lat, (.222, .02, .94), (.003, .055, .04))]
    for k in range(2): cx.append(prim("primitive_cylinder_add", vidro("ja_valvula", (.1, .08, .05)), (.19, -.02 + .04*k, 1.0), (.012, .012, .025), vertices=8))
    cx += tira(cou, [Vector((-.13, -.06, 1.46)), Vector((0, -.14, 1.25)), Vector((.17, -.04, .97))], w=.025, t=.005)
    R.rigid(cx, "chest")
    hd = cabeca(R, skin, mulher=True, idade=.1, queixo=.95, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0)
    hd.append(prim("primitive_cylinder_add", lat, HC + Vector((.09, 0, -.01)), (.028, .028, .012), rot=(0, 90, 0), vertices=14))
    hd.append(prim("primitive_torus_add", lat, HC + Vector((0, 0, .06)), (1, 1.05, 1), rot=(0, 0, 0), major_radius=.095, minor_radius=.004))
    R.rigid(hd, "head")
    return fim(R, INFO)

# a mão esquerda aperta o fone no ouvido; cabeça inclinada escutando
BASE = {"upper_arm.L": {"y": 10, "x": -45, "z": -20}, "forearm.L": {"bend": -135}, "upper_arm.R": {"y": -32, "x": -2}, "forearm.R": {"bend": -20},
        "head": {"y": 10, "x": 6}}

def anims(R):
    def ex(i, n): return {"head": {"y": 3*wave(i, n), "z": 3*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 1), passo=18)

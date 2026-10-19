# Estandarte do Warlord: haste de guerra com travessa de ferro, placa de caveira com chifres no meio, panos vermelhos
# rasgados pendendo da travessa e ponta de lança no pé. Vigilantes (Warlord).
#
# Uso: /root/bpy42/bin/python arma_estandarte_warlord.py -- <saida_dir>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import M, add, plate, cilindro, cone

def build():
    objs = []
    # haste e ponta de lança
    objs.append(cilindro(M["ferro"], (0, 0, -.62), (0, 0, .7), .02, verts=10))
    objs.append(cilindro(M["couro"], (0, 0, -.26), (0, 0, -.06), .026, verts=10))
    for k in range(4):
        objs.append(add("primitive_torus_add", M["cobre"], (0, 0, -.24 + k * .06), major_radius=.027,
                        minor_radius=.0045, major_segments=14, minor_segments=4))
    objs.append(cone(M["ferro"], (0, 0, .72), raio=.034, comp=.18, lados=6))
    objs.append(cone(M["cobre"], (0, 0, -.66), rot_x=180, raio=.026, comp=.12))
    # travessa com espinhos nas pontas
    objs.append(cilindro(M["ferro"], (-.36, 0, .6), (.36, 0, .6), .016, verts=8))
    for s in (-1, 1):
        cone(M["cobre"], (s * .38, 0, .6), direcao_deg_y=s * 90, raio=.024, comp=.1, lados=5)
    # placa de caveira com chifres
    placa = [(-.13, .82), (-.08, .92), (0, .88), (.08, .92), (.13, .82), (.11, .62), (0, .54), (-.11, .62)]
    objs.append(plate("placa", placa, M["ferro"], .045))
    objs.append(plate("placa_borda", [(x * .9, z - .01) for x, z in placa], M["cobre"], .05, y=-.002))
    objs.append(add("primitive_ico_sphere_add", M["osso"], (0, -.03, .7), scale=(.07, .05, .075), subdivisions=2))
    for s in (-1, 1):
        objs.append(add("primitive_ico_sphere_add", M["olho"], (s * .026, -.06, .71), scale=(.012, .009, .011), subdivisions=1))
        cone(M["osso"], (s * .07, 0, .79), direcao_deg_y=s * 42, raio=.024, comp=.12, lados=5)
    # panos rasgados penduradas da travessa
    for x0, comp, larg in ((-.22, .42, .14), (.2, .36, .12)):
        pano = [(x0 - larg / 2, .58), (x0 + larg / 2, .58), (x0 + larg * .3, .58 - comp + .06), (x0, .58 - comp),
                (x0 - larg * .25, .58 - comp + .05), (x0 - larg / 2, .58 - comp + .1)]
        objs.append(plate("pano", pano, M["pano"], .006, y=-.03))
    return objs

if __name__ == "__main__":
    lib.main(build, "estandarte_do_warlord", alvo=(0, 0, .12), ortho=1.5)

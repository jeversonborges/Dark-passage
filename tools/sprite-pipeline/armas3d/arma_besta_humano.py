# Besta do Humano: arco de lâminas em crescente com ganchos, cabo-riser com caveira de chifres, corda de aço
# esticada entre as pontas e espinhos de cobre nas pontas. Arma à distância da Vigília (Humano).
#
# Uso: /root/bpy42/bin/python arma_besta_humano.py -- <saida_dir>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import M, add, plate, cilindro, cone, corrente, ring, caveira

def build():
    objs = []
    # braço do arco: crescente grosso, abaulado para a frente (+X), pontas voltadas para o atirador
    for side in (1, -1):
        pts = ring(-.42, 0, .46, .4, -1.0, 1.0, steps=16, tip=.03)
        if side < 0:
            pts = [(x, -z) for x, z in pts]   # braço de baixo: espelha em Z
        objs.append(plate(f"braco_{'c' if side > 0 else 'b'}", pts, M["ferro"], .034))
    # o arco é um único crescente: ponta de cobre em cada extremidade
    for s in (-1, 1):
        cone(M["cobre"], (-.17, 0, s * .39), direcao_deg_y=0, rot_x=(0 if s > 0 else 180), raio=.02, comp=.07, lados=5)
    # corda de aço: duas metades que se encontram num ponto de apoio atrás do cabo
    objs.append(cilindro(M["cobre"], (-.17, 0, .39), (-.23, 0, 0), .0045, verts=6))
    objs.append(cilindro(M["cobre"], (-.23, 0, 0), (-.17, 0, -.39), .0045, verts=6))
    # cabo-riser: barra de ferro com caveira de chifres
    objs.append(cilindro(M["couro"], (.03, 0, -.14), (.03, 0, .14), .024, verts=10))
    for k in range(4):
        objs.append(add("primitive_torus_add", M["cobre"], (.03, 0, -.12 + k * .08), major_radius=.026,
                        minor_radius=.0045, major_segments=14, minor_segments=4))
    objs += caveira((.04, 0, 0), .24, M["osso"], M["olho"])
    for s in (-1, 1):
        cone(M["ferro"], (.04 + .02, 0, s * .05), direcao_deg_y=s * 40, raio=.013, comp=.06, lados=5)
    objs += corrente(M["cobre"], (.06, 0, -.07), (.1, 0, -.3), elos=7)
    objs.append(add("primitive_ico_sphere_add", M["osso"], (.1, 0, -.32), scale=(.016, .014, .018), subdivisions=1))
    return objs

if __name__ == "__main__":
    lib.main(build, "besta_do_humano", alvo=(-.05, 0, 0), ortho=1.1)

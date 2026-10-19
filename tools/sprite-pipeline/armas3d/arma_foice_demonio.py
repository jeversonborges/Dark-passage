# Foice longa do Demônio: haste comprida com lâmina de foice em crescente (borda de corte externa, serrilhada),
# caveira na ponta da haste, corrente pendendo e pano vermelho. Lava correndo no fio da lâmina (emissivo).
#
# Uso: /root/bpy42/bin/python arma_foice_demonio.py -- <saida_dir>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import M, add, plate, cilindro, cone, corrente, ring, caveira

def build():
    objs = []
    # haste longa com enrolamento de couro
    objs.append(cilindro(M["ferro"], (0, 0, -.62), (0, 0, .92), .02, verts=10))
    objs.append(cilindro(M["couro"], (0, 0, -.3), (0, 0, .05), .026, verts=10))
    for k in range(6):
        objs.append(add("primitive_torus_add", M["cobre"], (0, 0, -.28 + k * .05), major_radius=.028,
                        minor_radius=.0045, major_segments=14, minor_segments=4))
    objs.append(cone(M["cobre"], (0, 0, -.66), rot_x=180, raio=.026, comp=.11))
    # lâmina de foice: crescente à direita da haste, com a borda de corte por fora
    objs.append(plate("lamina", ring(-.5, .6, .55, .44, -.72, .72, steps=14, tip=.04), M["ferro"], .03))
    objs.append(plate("fio_lava", ring(-.5, .6, .53, .505, -.6, .6, steps=10), M["lava"], .036))
    for a in (-.45, -.15, .15, .45):   # serras na borda de fora
        px, pz = -.5 + .56 * __import__("math").cos(a), .6 + .56 * __import__("math").sin(a)
        cone(M["cobre"], (px, 0, pz), direcao_deg_y=__import__("math").degrees(__import__("math").atan2(__import__("math").cos(a), __import__("math").sin(a))),
             raio=.018, comp=.07, lados=5)
    # caveira no topo da haste
    objs += caveira((0, 0, .98), .28, M["osso"], M["olho"])
    # corrente e pano
    objs += corrente(M["cobre"], (-.04, 0, .8), (-.04, 0, .42), elos=8)
    objs.append(add("primitive_ico_sphere_add", M["osso"], (-.04, 0, .38), scale=(.018, .016, .02), subdivisions=1))
    pano = [(-.02, .3), (.06, .28), (.05, -.04), (.03, .02), (.01, -.12), (-.02, -.02), (-.05, -.16), (-.06, .1)]
    objs.append(plate("pano", pano, M["pano"], .006, y=-.03))
    return objs

if __name__ == "__main__":
    lib.main(build, "foice_longa_do_demonio", alvo=(0, 0, .2), ortho=1.75)

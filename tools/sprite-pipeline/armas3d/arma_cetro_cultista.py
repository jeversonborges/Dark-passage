# Cetro do Cultista: cajado da sheet (3ª peça da linha de cima). Haste de ferro, coroa de três lâminas em espinho
# (uma reta e duas abertas para os lados), caveira no meio da coroa com brasas nos olhos, corrente com caveirinha
# e pano vermelho rasgado descendo pela haste. Ponta de cobre no pé.
#
# Uso: /root/bpy42/bin/python arma_cetro_cultista.py -- <saida_dir>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import M, add, plate, cilindro, cone, corrente

def build():
    objs = []
    # haste e pegada de couro com enrolamento
    objs.append(cilindro(M["ferro"], (0, 0, -.6), (0, 0, .78), .02, verts=10))
    objs.append(cilindro(M["couro"], (0, 0, -.24), (0, 0, -.02), .026, verts=10))
    for k in range(5):
        objs.append(add("primitive_torus_add", M["cobre"], (0, 0, -.22 + k * .045), major_radius=.027,
                        minor_radius=.004, major_segments=14, minor_segments=4))
    objs.append(cone(M["cobre"], (0, 0, -.62), rot_x=180, raio=.024, comp=.1))   # ponta de cobre
    # coroa: espinho central e duas lâminas abertas
    objs.append(cone(M["ferro"], (0, 0, .8), raio=.036, comp=.26, lados=6))
    ala = [(.01, .74), (.06, .8), (.14, .9), (.18, .99), (.1, .93), (.05, .9), (.0, .84)]
    objs.append(plate("ala_d", ala, M["ferro"], .03))
    objs.append(plate("ala_e", [(-x, z) for x, z in ala], M["ferro"], .03))
    objs.append(plate("ala_d_borda", [(x * .8, z) for x, z in ala], M["cobre"], .036, y=0))
    objs.append(plate("ala_e_borda", [(-x * .8, z) for x, z in ala], M["cobre"], .036, y=0))
    # caveira com brasas nos olhos e chifrinhos
    objs.append(add("primitive_ico_sphere_add", M["osso"], (0, 0, .86), scale=(.04, .032, .046), subdivisions=2))
    for s in (-1, 1):
        objs.append(add("primitive_ico_sphere_add", M["olho"], (s * .015, -.03, .872), scale=(.009, .007, .008), subdivisions=1))
        cone(M["ferro"], (s * .04, 0, .9), direcao_deg_y=s * 40, raio=.014, comp=.06, lados=5)
    # corrente com caveirinha e pano rasgado
    objs += corrente(M["cobre"], (.05, 0, .6), (.05, 0, .36), elos=8)
    objs.append(add("primitive_ico_sphere_add", M["osso"], (.05, 0, .33), scale=(.018, .016, .02), subdivisions=1))
    objs += corrente(M["cobre"], (-.05, 0, .58), (-.05, 0, .42), elos=5)
    pano = [(.02, .5), (.09, .42), (.08, .16), (.06, .22), (.04, .02), (.01, .1), (-.02, -.06), (-.01, .2), (-.04, .3)]
    objs.append(plate("pano", pano, M["pano"], .006, y=-.03))
    return objs

if __name__ == "__main__":
    lib.main(build, "cetro_do_cultista", alvo=(0, 0, .3), ortho=1.45)

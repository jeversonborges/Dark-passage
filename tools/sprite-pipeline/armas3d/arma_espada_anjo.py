# Espada do Anjo: espada larga da sheet (1ª peça da linha de cima). Lâmina com dentes de serra nas duas bordas,
# fenda de lava no centro (emissiva), guarda de chifres que se curvam para cima e caveira no meio, cabo de ferro
# com enrolamento de cobre, pomo de caveira, tira de pano vermelho pendendo da guarda.
#
# Uso: /root/bpy42/bin/python arma_espada_anjo.py -- <saida_dir>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import M, add, plate, cilindro, lado

def meia_largura(z):
    if z < .35:
        return .075 + .05 * (z - .02) / .33
    return .13 * max(0.0, 1 - (z - .35) / .65) ** .8

def lamina_pts():
    N = 42
    direita = []
    for k in range(N + 1):
        z = .02 + .98 * k / N
        w = meia_largura(z)
        if k % 2 == 1 and .1 < z < .9:   # dente de serra
            w += .02
        direita.append((w, z))
    esquerda = [(-x, z) for x, z in direita[::-1]]
    return direita + [(0.0, 1.0)] + esquerda

def build():
    objs = []
    # lâmina com dentes e fenda de lava
    objs.append(plate("lamina", lamina_pts(), M["ferro"], .022))
    objs.append(plate("fenda_lava", [(-.012, .12), (.012, .12), (.007, .85), (-.007, .85)], M["lava"], .03))
    # guarda: barra com chifres que sobem nas pontas
    guarda = [(-.2, 0), (.2, 0), (.24, .11), (.19, .075), (.16, .035), (-.16, .035), (-.19, .075), (-.24, .11)]
    objs.append(plate("guarda", guarda, M["cobre"], .04, y=0))
    objs.append(add("primitive_ico_sphere_add", M["osso"], (0, 0, .05), scale=(.042, .03, .042), subdivisions=2))
    for s in (-1, 1):
        objs.append(add("primitive_ico_sphere_add", M["olho"], (s * .016, -.03, .058), scale=(.01, .008, .009), subdivisions=1))
    # cabo com enrolamento
    objs.append(cilindro(M["couro"], (0, 0, -.2), (0, 0, -.01), .018, verts=10))
    for k in range(6):
        z = -.18 + k * .033
        objs.append(add("primitive_torus_add", M["cobre"], (0, 0, z), major_radius=.02, minor_radius=.0038,
                        major_segments=14, minor_segments=4))
    # pomo de caveira
    objs.append(add("primitive_ico_sphere_add", M["osso"], (0, 0, -.225), scale=(.03, .028, .032), subdivisions=2))
    # tira de pano vermelho rasgado (atrás da lâmina)
    pano = [(.12, .02), (.2, -.02), (.19, -.1), (.16, -.07), (.14, -.15), (.11, -.09), (.09, -.13), (.1, .0)]
    objs.append(plate("pano", pano, M["pano"], .006, y=-.035))
    return objs

if __name__ == "__main__":
    lib.main(build, "espada_do_anjo", alvo=(0, 0, .42), ortho=1.3)

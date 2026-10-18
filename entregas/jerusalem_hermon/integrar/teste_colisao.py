#!/usr/bin/env python3
"""Confere que nenhuma construção de Jerusalém deixa atravessar: prédios e muros (categoria do manifesto) têm que
tер a pegada (footprint_tiles) toda bloqueada na grade. Uso: python3 integrar/teste_colisao.py [mapa.json]"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
# os manifestos completos ficam na pasta compartilhada; o repositório tem só parte deles (416 de 1.444), e a pegada
# muda de tamanho entre as duas (cupula_estacao: 5x5 contra 14x14)
MANIFESTO = "/mnt/project-files/assets/ambiente/objetos" if os.path.isdir("/mnt/project-files/assets/ambiente/objetos") \
    else os.path.join(AQUI, "..", "..", "..", "assets", "ambiente", "objetos")
MAPA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "jerusalem_hermon.json")


CONSTRUCOES = ("predios", "paredes")          # categorias do manifesto: prédio e muro (o resto é decoração)


def pegada(k):
    f = os.path.join(MANIFESTO, k + ".json")
    if not os.path.exists(f): return None
    j = json.load(open(f))
    return j.get("footprint_tiles") if j.get("categoria") in CONSTRUCOES else None


def main():
    m = json.load(open(MAPA)); g = m["grade"]; ruins = []; n = 0
    for p in m["props"]:
        fp = pegada(p["k"])
        if not fp or fp == [1, 1] or p.get("chao"): continue
        fw, fh = fp; x0 = int(p["x"] - fw/2 + .5); y0 = int(p["y"] - fh/2 + .5)
        livres = [(xx, yy) for yy in range(y0, y0 + fh) for xx in range(x0, x0 + fw) if g[yy][xx] != "#"]
        n += 1
        if livres: ruins.append((p["k"], p["x"], p["y"], len(livres), fw * fh))
    for r in ruins: print("  ATRAVESSA", r)
    print("prédios conferidos: %d, com célula livre: %d" % (n, len(ruins)))
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()

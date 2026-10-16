# Visão geral e close-ups da Cidade de São Lázaro com a arte do kit: python3 overview.py <pasta_saida>
import json, sys, os, cena2d
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "area_inicial.json")))
o = 20
R = [(50, 80, "São Lázaro", "a cidade da Vigília · zona segura"), (90, 82, "Campos de Cinza", "nível 1 a 3 · Marco do Corte 7 a 9"),
     (26, 40, "Pátio dos Bondes", "nível 2 a 4"), (20, 127, "Bairro Afogado", "nível 3 a 5"), (102, 26, "A Vala", "nível 3 a 5"),
     (78, 128, "Cemitério de São Lázaro", "nível 4 a 7"), (142, 84, "Chiqueiros", "nível 4 a 6"), (128, 121, "Bosque das Viúvas", "nível 5 a 7"),
     (118, 100, "Desertores", "nível 6 a 9"), (140, 47, "Abatedouro Carniça", "nível 7 a 9 · porta da Cripta"),
     (148, 138, "Vila Militar", "nível 8 a 10"), (120, 150, "Beira da Tempestade", "nível 9 a 12"), (4, 70, "Precipício da Cidade Velha", ""),
     (114, 64, "Rio Amargo", "o oásis")]
rot = [(x + o, y + o, n, s) for x, y, n, s in R]
cena2d.render(M, (14, 14, 186, 186), .2, f"{OUT}/visao_geral.jpg", mobs=False, npcs=False, rotulos=rot, luz_amb=(.6, .6, .7),
              titulo="Cidade de São Lázaro", subtitulo="área inicial da Vigília · níveis 1 a 12 · 160 x 160 m jogáveis", max_lado=3200)
for nome, caixa, s in [("igreja", (54, 94, 80, 124), .9), ("cidade", (46, 76, 94, 124), .55), ("cemiterio", (78, 128, 120, 168), .55), ("abatedouro_rio", (122, 50, 168, 100), .55),
                       ("campos_marco", (96, 66, 132, 116), .55), ("patio_bondes", (28, 42, 64, 78), .6)]:
    cena2d.render(M, caixa, s, f"{OUT}/{nome}.jpg", max_lado=2400); print(nome)

"""Biblioteca Soterrada no mapa da cidade (Bairro Afogado) e o mapa interior. Thread "Biblioteca e mistérios", 17/10/2026.

Chamado por tools/mapa.py:
  - rua(objetos, props, npcs, blk): põe a lanterna da cúpula (portal para dentro), o poço do lintel (inscricao_01) e o
    quarto da Nina (esconderijo_nina + NPC) no Bairro Afogado. Posições conferidas contra o mapa da cidade 1.0.
  - interior(G, OUT): copia o mapa interior gerado (data/design/mapas/biblioteca_soterrada.json, que o sync traz de
    design/mapas/biblioteca/) para data/mapas, mantendo os pisos próprios do mapa (assoalho da biblioteca).
"""
import json, math, os

LANTERNA = (47.5, 131.5)        # célula 47,131: livre num raio de 2
LINTEL = (49.5, 133.5)          # o funil de areia ao lado da lanterna, com o lintel da porta (inscricao_01)
JANELA_NINA = (44.5, 137.5)     # a janela_na_areia que já existe ali vira o quarto da Nina
CHEGADA_DENTRO = [15.5, 13.5]   # ao pé da escada de corda, na Sala de Leitura


def _livre_perto(blk, x, y, r=4):
    n = len(blk); best = None
    for yy in range(int(y) - r, int(y) + r + 1):
        for xx in range(int(x) - r, int(x) + r + 1):
            if 0 <= xx < n and 0 <= yy < n and not blk[yy][xx]:
                d = math.dist((xx + .5, yy + .5), (x, y))
                if best is None or d < best[0]: best = (d, xx + .5, yy + .5)
    return [best[1], best[2]] if best else [x, y]


def rua(objetos, props, npcs, blk):
    ja = {o.get("obj") for o in objetos if o.get("kind") == "interativo"}
    if "lanterna_da_biblioteca" not in ja:
        x, y = LANTERNA
        props.append({"k": "lanterna_biblioteca", "x": x, "y": y, "obj": 1})
        objetos.append({"kind": "interativo", "obj": "lanterna_da_biblioteca", "pos": [x, y], "i": 0,
                        "mapa": "biblioteca_soterrada", "chegada": CHEGADA_DENTRO})
        for yy in range(int(y) - 1, int(y) + 2):
            for xx in range(int(x) - 1, int(x) + 2): blk[yy][xx] = True
    if "inscricao_01" not in ja:
        x, y = LINTEL
        props.append({"k": "lintel_biblioteca", "x": x, "y": y, "obj": 1})
        objetos.append({"kind": "interativo", "obj": "inscricao_01", "pos": [x, y], "i": 0})
    if "esconderijo_nina" not in ja:
        x, y = JANELA_NINA
        for p in props:
            if p["k"] == "janela_na_areia" and abs(p["x"] - x) < .6 and abs(p["y"] - y) < .6: p["k"] = "janela_nina"; p["obj"] = 1
        if not any(p["k"] == "janela_nina" for p in props): props.append({"k": "janela_nina", "x": x, "y": y, "obj": 1})
        objetos.append({"kind": "interativo", "obj": "esconderijo_nina", "pos": [x, y], "i": 0})
        if not any(n.get("id") == "nina" for n in npcs):
            npcs.append({"id": "nina", "pos": _livre_perto(blk, x + 1.6, y - 1.2), "dir": [-1, 0]})
    # luz de vela subindo pela lanterna e a brasa da lata da Nina
    return [[LANTERNA[0], LANTERNA[1], 1, .62, .3, 5], [JANELA_NINA[0] - .2, JANELA_NINA[1] - .4, 1, .4, .12, 2.5]]


def interior(G, OUT):
    src = f"{G}/data/design/mapas/biblioteca_soterrada.json"
    if not os.path.exists(src): return None
    m = json.load(open(src)); m.pop("salas", None)
    json.dump(m, open(f"{OUT}/{m['id']}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(m["id"], "(Biblioteca Soterrada)", m["w"], "x", m["h"], "props", len(m["props"]), "objetos", len(m["objetos"]))
    return m

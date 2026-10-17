#!/usr/bin/env python3
"""Ligações a pé entre os mapas externos (o grafo do mundo).

Passo final depois dos geradores de cada área (como o spots.py): lê os mapas do jogo, põe ou corrige os portais de
estrada declarados em ESTRADAS e confere que cada ponta fica numa célula andável ligada ao spawn do mapa. Não mexe
na grade (não exige subir rede.VERSAO), não mexe em dungeons nem em portas trancadas por missão ou mistério.

    python3 ligacoes.py [pasta_dos_mapas]        # padrão: /mnt/project-files/game/data/mapas
    python3 ligacoes.py --checar [pasta]         # só confere, não grava

Portal de estrada = {"kind": "portal", "estrada": true, "visual": <prop do kit>}: o cliente desenha o prop
(portão, marco, placa) no lugar da escada (ver entregas/mapas_interligados/jogo.patch).
"""
import json, math, sys
from collections import deque
from pathlib import Path

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
CHECAR = "--checar" in sys.argv
PASTA = Path(ARGS[0]) if ARGS else Path("/mnt/project-files/game/data/mapas")

# Cada estrada liga duas pontas; cada ponta é (mapa, posição do portal, ponto de chegada de quem vem do outro lado).
# A posição é um alvo: o script procura a célula livre mais próxima, ligada ao spawn.
ESTRADAS = [
    {   # já existia; a trava de nível 12 saiu: quem nasce em Jerusalém pode descer ao deserto quando quiser
        "id": "estrada_dos_peregrinos",
        "a": {"mapa": "jerusalem_hermon", "pos": [101.5, 32.0], "chegada": [101.5, 34.5], "visual": "torre_portao",
              "nome": "Estrada dos Peregrinos · para o Deserto de Absinto (São Lázaro)"},
        "b": {"mapa": "area_inicial", "pos": [56.5, 126.5], "chegada": [56.5, 128.5], "visual": "placa_rua_enterrada",
              "nome": "Estrada dos Peregrinos · para Jerusalém"},
    },
    {   # já existia; só ganha o visual de estrada
        "id": "linha_de_cinza",
        "a": {"mapa": "area_inicial", "pos": [87.5, 24.5], "chegada": [87.5, 27.5], "visual": "placa_aviso",
              "nome": "Linha de Cinza · para o Novo Éden"},
        "b": {"mapa": "mata_do_granizo", "pos": [74.5, 87.5], "chegada": [72.5, 85.5], "visual": "pilar_portao",
              "nome": "Trilha para o Deserto de Absinto"},
    },
    {   # nova: o caminho do Êxodo ao contrário, da Cidade de Davi ao deserto de Shur e ao Nilo
        "id": "estrada_do_exodo",
        "a": {"mapa": "jerusalem_hermon", "pos": [131.5, 17.5], "chegada": [131.5, 20.5], "visual": "placa_versiculo",
              "nome": "Estrada do Êxodo · para o Egito (nível 45)", "nivel_minimo": 45,
              "texto_trancado": "O deserto de Shur come quem atravessa fraco. Volte no nível 45."},
        "b": {"mapa": "egito", "pos": [153.5, 106.5], "chegada": [151.5, 106.5], "visual": "obelisco",
              "nome": "Estrada do Êxodo · para Jerusalém"},
    },
]
# Atlântida entra pela Fenda do Novo Éden (portal dela, não é estrada). Quando atlantida.json estiver no jogo,
# conferir aqui que a Fenda usa "nivel_minimo" (o servidor ignora "requer_nivel").
CORRIGIR_CHAVE = {"requer_nivel": "nivel_minimo"}


def ler(m):
    p = PASTA / f"{m}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def alcancaveis(d):
    g, W, H = d["grade"], d["w"], d["h"]
    sx, sy = int(d["spawn"][0]), int(d["spawn"][1])
    vistos, fila = {(sx, sy)}, deque([(sx, sy)])
    while fila:
        x, y = fila.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in vistos and g[n[1]][n[0]] != "#":
                vistos.add(n); fila.append(n)
    return vistos


def celula(ok, alvo, longe_de=()):
    """Célula livre ligada ao spawn mais perto do alvo, longe de outros objetos."""
    cands = [c for c in ok if all(math.dist((c[0] + .5, c[1] + .5), p) >= 1.5 for p in longe_de)]
    x, y = min(cands, key=lambda c: math.dist((c[0] + .5, c[1] + .5), alvo))
    return [x + .5, y + .5]


def _desta_estrada(o, e, p, q):
    """O portal antigo desta estrada (mesmo id, ou mesmo destino a menos de 3 tiles do alvo), que será trocado."""
    return o.get("kind") == "portal" and (o.get("estrada_id") == e["id"] or (
        o.get("para") == q["mapa"] and math.dist(o["pos"], p["pos"]) < 3.0))


def aplicar():
    mapas, erros = {}, []
    for e in ESTRADAS:
        for lado, outro in (("a", "b"), ("b", "a")):
            m = e[lado]["mapa"]
            if m not in mapas: mapas[m] = ler(m)
            if mapas[m] is None: erros.append(f"{e['id']}: mapa {m} não está no jogo")
    if erros: return mapas, erros
    alc = {m: alcancaveis(d) for m, d in mapas.items()}
    ponta = {}
    for e in ESTRADAS:
        for lado in ("a", "b"):
            p = e[lado]; d = mapas[p["mapa"]]
            q = e["b" if lado == "a" else "a"]
            outros = [o["pos"] for o in d["objetos"] if "pos" in o and not _desta_estrada(o, e, p, q)]
            pos = celula(alc[p["mapa"]], p["pos"], outros)
            cheg = celula(alc[p["mapa"]], p["chegada"])
            if math.dist(pos, cheg) < 1.5: erros.append(f"{e['id']}/{lado}: chegada em cima do portal")
            ponta[(e["id"], lado)] = (pos, cheg)
    for e in ESTRADAS:
        for lado, outro in (("a", "b"), ("b", "a")):
            p, q = e[lado], e[outro]
            d = mapas[p["mapa"]]
            pos = ponta[(e["id"], lado)][0]
            cheg_do_outro = ponta[(e["id"], outro)][1]
            novo = {"kind": "portal", "pos": pos, "para": q["mapa"], "chegada": cheg_do_outro, "nome": p["nome"],
                    "visual": p["visual"], "estrada": True, "estrada_id": e["id"]}
            for k in ("nivel_minimo", "texto_trancado"):
                if k in p: novo[k] = p[k]
            d["objetos"] = [o for o in d["objetos"] if not _desta_estrada(o, e, p, q)]
            d["objetos"].append(novo)
    for m, d in mapas.items():
        for o in d["objetos"]:
            for velho, certo in CORRIGIR_CHAVE.items():
                if o.get("kind") == "portal" and velho in o: o[certo] = o.pop(velho)
    return mapas, erros


def main():
    mapas, erros = aplicar()
    for e in ESTRADAS:
        for lado in ("a", "b"):
            p = e[lado]; d = mapas.get(p["mapa"])
            if d is None: continue
            o = next(o for o in d["objetos"] if o.get("estrada_id") == e["id"] and o["para"] == e["b" if lado == "a" else "a"]["mapa"])
            print(f"  {e['id']:24s} {p['mapa']:18s} portal {o['pos']} -> {o['para']} {o['chegada']}"
                  + (f"  (nível {o['nivel_minimo']})" if "nivel_minimo" in o else ""))
    if erros:
        print("ERROS:\n  " + "\n  ".join(erros)); sys.exit(1)
    if CHECAR: return
    for m, d in mapas.items():
        (PASTA / f"{m}.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"ok: {len(mapas)} mapas gravados em {PASTA}")


if __name__ == "__main__":
    main()

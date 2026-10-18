#!/usr/bin/env python3
"""Põe os dois vendedores de pets (0.9.6) nos mapas: Dulce Gaiola na Vela (Vigília) e Caetano Ninho em Jerusalém (Arautos).

Idempotente: quem já está no mapa é deixado como está. Mexe só em data/mapas/area_inicial.json e
data/mapas/jerusalem_hermon.json (o que o jogo lê). Os NPCs e as falas vêm de design/missoes/dados (copiados para
data/design/missoes pelo tools/sync.sh ou pela Prévia).
Uso:  python3 tools/patch_vendedores_pets.py          (a partir da pasta game/)
"""
import json
import math
import pathlib

MAPAS = pathlib.Path(__file__).resolve().parent.parent / "data" / "mapas"

# (mapa, id do NPC, ponto de partida, direção). Pontos conferidos pela Prévia.
VENDEDORES = [
    ("area_inicial.json", "dulce_gaiola", (88.5, 102.5), [1, 0]),
    ("jerusalem_hermon.json", "caetano_ninho", (93.5, 46.5), [1, 0]),
]
ALCANCE_LIVRE = 2.0   # não nasce a menos de 2 tiles de outro NPC
BUSCA = 10


def livre(grade: list, x: int, y: int) -> bool:
    return 0 <= y < len(grade) and 0 <= x < len(grade[0]) and grade[y][x] == "."


def ponto_livre(mapa: dict, alvo: tuple) -> list:
    """Célula '.' mais perto do alvo que não fique colada em outro NPC."""
    grade = mapa["grade"]
    ocupados = [tuple(n["pos"]) for n in mapa["npcs"]]
    melhor, dmin = None, 1e9
    for dy in range(-BUSCA, BUSCA + 1):
        for dx in range(-BUSCA, BUSCA + 1):
            x, y = int(alvo[0]) + dx, int(alvo[1]) + dy
            if not livre(grade, x, y): continue
            if any(math.dist((x + 0.5, y + 0.5), o) < ALCANCE_LIVRE for o in ocupados): continue
            d = math.dist((x + 0.5, y + 0.5), alvo)
            if d < dmin: dmin, melhor = d, [x + 0.5, y + 0.5]
    if melhor is None: raise SystemExit(f"sem lugar livre perto de {alvo}")
    return melhor


def main() -> None:
    for arq, npc_id, alvo, direcao in VENDEDORES:
        caminho = MAPAS / arq
        mapa = json.loads(caminho.read_text(encoding="utf8"))
        if any(n["id"] == npc_id for n in mapa["npcs"]):
            print(f"ja existe: {npc_id} em {arq}")
            continue
        pos = ponto_livre(mapa, alvo)
        mapa["npcs"].append({"id": npc_id, "pos": pos, "dir": direcao})
        caminho.write_text(json.dumps(mapa, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
        print(f"{npc_id} em {pos} ({arq})")


if __name__ == "__main__":
    main()

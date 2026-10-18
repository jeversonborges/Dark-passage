#!/usr/bin/env python3
"""Põe os dois vendedores de pets (0.9.6) no mapa inicial, perto da praça de cada lado.

Idempotente: quem já está no mapa é deixado como está. Mexe só em data/mapas/area_inicial.json (o que o jogo lê).
Uso:  python3 tools/patch_vendedores_pets.py          (a partir da pasta game/)
"""
import json
import math
import pathlib

MAPA = pathlib.Path(__file__).resolve().parent.parent / "data" / "mapas" / "area_inicial.json"

# (id do NPC, ponto de partida no mapa, direção). Vigília: Acampamento da Vela; Arautos: Capela de São Lázaro.
VENDEDORES = [
    ("rute_abelheira", (80.0, 86.0), [1, 0]),
    ("joana_enxertadeira", (64.0, 122.0), [-1, 0]),
]
ALCANCE_LIVRE = 2.0   # não nasce a menos de 2 tiles de outro NPC ou de um vendedor já posto
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
    mapa = json.loads(MAPA.read_text(encoding="utf8"))
    existentes = {n["id"] for n in mapa["npcs"]}
    for npc_id, alvo, direcao in VENDEDORES:
        if npc_id in existentes:
            print(f"ja existe: {npc_id}")
            continue
        pos = ponto_livre(mapa, alvo)
        mapa["npcs"].append({"id": npc_id, "pos": pos, "dir": direcao})
        print(f"{npc_id} em {pos}")
    MAPA.write_text(json.dumps(mapa, ensure_ascii=False, separators=(",", ":")), encoding="utf8")


if __name__ == "__main__":
    main()

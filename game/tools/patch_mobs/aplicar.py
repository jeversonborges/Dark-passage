#!/usr/bin/env python3
# Aplica um patch de spawns por cima dos mapas do jogo (game/data/mapas). Só mexe em spawns.
# Uso: python3 aplicar.py [patch.json] [--dry-run]
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MAPAS = os.path.join(AQUI, "..", "..", "data", "mapas")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    patch = json.load(open(args[0] if args else os.path.join(AQUI, "reducao_mobs_096.json"), encoding="utf-8"))
    for mapa, cfg in patch["mapas"].items():
        arq = os.path.join(MAPAS, mapa + ".json")
        raw = open(arq, encoding="utf-8").read()
        d = json.loads(raw)
        spawns = d["spawns"]
        n0 = len(spawns)
        for r in cfg["remover"]:
            achados = [s for s in spawns if s["mob"] == r["mob"] and s["pos"] == r["pos"] and s.get("qtd", 1) == r["qtd"]]
            if len(achados) != 1:
                print("AVISO", mapa, r["mob"], r["pos"], "encontrados:", len(achados), "(ja aplicado ou mapa mudou)")
                continue
            spawns.remove(achados[0])
        out = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        print(mapa, "spawns", n0, "->", len(spawns))
        if not dry and out != raw:
            open(arq, "w", encoding="utf-8").write(out)

if __name__ == "__main__":
    main()

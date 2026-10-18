# Aplica a faxina de props (limpeza_096.json) nos mapas de game/data/mapas.
# Uso: python3 aplicar.py [--relatorio]   (sem --relatorio, grava os mapas)
# Cada remoção é conferida pelo trio (tipo, x, y): se algum prop não existir, o script para sem gravar nada.
import json, os, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
MAPAS = os.path.join(AQUI, "..", "..", "data", "mapas")

def main():
    relatorio = "--relatorio" in sys.argv
    lista = json.load(open(os.path.join(AQUI, "limpeza_096.json"), encoding="utf-8"))["remocoes"]
    gravar = {}
    for mapa, remover in lista.items():
        caminho = os.path.join(MAPAS, mapa + ".json")
        raw = open(caminho, encoding="utf-8").read()
        d = json.loads(raw)
        props = d["props"]
        pendentes = collections.Counter((k, float(x), float(y)) for k, x, y in remover)
        manter = []
        for p in props:
            chave = (p["k"], float(p["x"]), float(p["y"]))
            if pendentes[chave] > 0:
                pendentes[chave] -= 1
                continue
            manter.append(p)
        faltam = sum(pendentes.values())
        if faltam:
            sys.exit(f"{mapa}: {faltam} remoções não encontradas; nada foi gravado")
        print(f"{mapa:28s} props {len(props):5d} -> {len(manter):5d}")
        d["props"] = manter
        gravar[caminho] = (json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ("\n" if raw.endswith("\n") else ""))
    if relatorio: return
    for caminho, texto in gravar.items():
        open(caminho, "w", encoding="utf-8").write(texto)
    print("gravado:", len(gravar), "mapas")

if __name__ == "__main__":
    main()

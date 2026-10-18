# Faxina de props nos mapas entregues (patch versionado, só props).
# Uso: python3 limpar.py [--relatorio]   (roda sobre game/data/mapas/*.json; sem --relatorio, grava os arquivos)
# Regras, sempre sobre props SEM marcação de jogo (ver PROTEGIDOS):
#   1. duplicado: mesmo kind a menos de 0,25 m de outro mesmo kind -> sai o segundo;
#   2. pilha: mais de 3 props decorativos numa mesma célula de 1 m -> ficam 3 (ordem fixa de x, y);
#   3. desbaste: tipo decorativo repetido (>= REPETIDO_MIN no mapa) perde uma fração do mapa
#      (POLITICA: área inicial 50%, Egito 30%, Jerusalém 30%, demais 20%). A escolha é por hash do id e da
#      posição, então roda igual sempre. Tipo estrutural (muro, casa, ponte, trilho, lápide...) nunca desbasta.
# Não toca em spawns, luzes, objetos, npcs, colisão nem props com marcação de jogo.
import json, glob, os, sys, collections, math, zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
MAPAS = os.path.join(RAIZ, "game", "data", "mapas")

# props com qualquer destas chaves têm papel de jogo (marco, ponto, texto, glifo, portão, jaula, plateia...)
PROTEGIDOS = {"obj", "anel", "marco", "ponto", "texto", "glifo", "oculto_por_obj", "frente", "lado", "portao",
              "jaula", "plateia", "abismo", "espelho", "escala", "invisivel", "nota", "objeto", "vaso", "pendente",
              "racha", "pendurado", "luz", "bloqueia", "chao"}
# palavras no nome do kind que indicam mistério, porta, baú, chave, selo, altar ou portal: nunca saem
PALAVRAS = ("porta", "portao", "grade", "bau", "glifo", "runa", "selo", "enigma", "chave", "cofre", "altar",
            "portal", "trilha", "esfinge", "arca", "marco", "pedra_", "lapide_nome", "tabua", "inscric")

# tipos que formam o lugar (paredes, prédios, caminhos, túmulos, fontes de luz): nunca desbastam
ESTRUTURAL = ("muro", "parede", "casa", "casario", "predio", "ponte", "trilho", "bonde", "cerca", "grade",
              "barricada", "lapide", "cruz", "cova", "mausoleu", "tumulo", "sarcofago", "piramide", "mastaba",
              "pilono", "obelisco", "esfinge", "colosso", "estatua", "entrada", "poste", "tenda", "banca",
              "carrinho", "guincho", "fogueira", "braseiro", "lampiao", "lampada", "chafariz", "coreto",
              "capela", "altar", "placa", "andaime", "cais", "barca", "portao", "portal", "muralha", "torre",
              "chamine", "silo", "escotilha", "caldeira", "moedor", "tanque", "cupula", "guindaste", "forca",
              "ganchos", "cano", "janela", "cocho", "cratera", "entulho_", "mesa", "bancada", "oficina")
POLITICA = {"area_inicial": 0.5, "egito": 0.3, "jerusalem_hermon": 0.3}
PADRAO = 0.2
REPETIDO_MIN = 30

def estrutural(k):
    return any(w in k for w in ESTRUTURAL)

def protegido(p):
    if any(c in p for c in PROTEGIDOS): return True
    return any(w in p["k"] for w in PALAVRAS)

def limpar(props, mapa):
    sai = set()
    cand = [i for i, p in enumerate(props) if not protegido(p)]
    # 3. desbaste de tipos repetidos (feito antes das regras 1 e 2, para elas pegarem o que sobrou)
    fracao = POLITICA.get(mapa, PADRAO)
    contagem = collections.Counter(props[i]["k"] for i in cand)
    for i in cand:
        k = props[i]["k"]
        if contagem[k] < REPETIDO_MIN or estrutural(k): continue
        h = zlib.crc32(f"{mapa}|{k}|{props[i]['x']},{props[i]['y']}".encode()) % 1000
        if h < fracao * 1000: sai.add(i)
    cand = [i for i in cand if i not in sai]
    # 1. duplicados
    por_kind = collections.defaultdict(list)
    for i in cand: por_kind[props[i]["k"]].append(i)
    for k, ids in por_kind.items():
        ids.sort(key=lambda i: (props[i]["x"], props[i]["y"]))
        for a_pos, a in enumerate(ids):
            if a in sai: continue
            for b in ids[a_pos + 1:]:
                if b in sai: continue
                if math.hypot(props[a]["x"] - props[b]["x"], props[a]["y"] - props[b]["y"]) < 0.25:
                    sai.add(b)
    # 2. pilhas por célula de 1 m
    celula = collections.defaultdict(list)
    for i in cand:
        if i not in sai: celula[(int(props[i]["x"] // 1), int(props[i]["y"] // 1))].append(i)
    for ids in celula.values():
        if len(ids) > 3:
            ids.sort(key=lambda i: (props[i]["x"], props[i]["y"]))
            sai.update(ids[3:])
    return sai

def main():
    relatorio = "--relatorio" in sys.argv
    total = {"antes": 0, "sai": 0}
    for f in sorted(glob.glob(os.path.join(MAPAS, "*.json"))):
        raw = open(f, encoding="utf-8").read()
        d = json.loads(raw)
        props = d.get("props", [])
        sai = limpar(props, d.get("id", os.path.basename(f)[:-5]))
        total["antes"] += len(props); total["sai"] += len(sai)
        print(f"{os.path.basename(f):28s} props {len(props):5d} -> {len(props) - len(sai):5d}  (sai {len(sai)})")
        if relatorio or not sai: continue
        d["props"] = [p for i, p in enumerate(props) if i not in sai]
        out = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        open(f, "w", encoding="utf-8").write(out + ("\n" if raw.endswith("\n") else ""))
    print(f"total: {total['antes']} props, sai {total['sai']}")

if __name__ == "__main__":
    main()

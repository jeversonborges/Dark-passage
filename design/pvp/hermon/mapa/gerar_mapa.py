"""O Cume dos Vigilantes: o topo do Monte Hermon onde os duzentos juraram (mapa de instância do evento).

Gera cume_dos_vigilantes.json no MESMO formato de game/data/mapas/*.json (classe Andar de design/mapas/cripta/gerar.py)
e a planta planta_cume_dos_vigilantes.png. Regras e números: ../dados.json (o JSON vale mais que este texto).

O cume é um disco de cinza e cinza vitrificada (o mesmo chão e os mesmos props do Cume do Hermon em
entregas/jerusalem_hermon/), cercado de abismo e nevasca. Cinco anéis caem um a um durante o evento; no centro fica
a Laje do Juramento (raio 3), que nunca cai. Nas divisas dos anéis correm as fendas que acendem antes da queda.
Os Vigilantes começam ajoelhados em círculos, virados para a laje (estátuas até o juramento começar).
Uso: python3 gerar_mapa.py
"""
import json, math, os, sys, zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "design", "mapas", "cripta"))
import gerar as G

DADOS = json.load(open(os.path.join(AQUI, "..", "dados.json")))
ANEIS = DADOS["evento"]["desmoronamento"]["aneis"]
W = H = 60
CX = CY = 30.0
R_MAX = ANEIS[0]["raio_max"]
LAJE = 3.0
FOGO = [1, .55, .22]; SANTO = [1, .9, .6]; LUA = [.55, .62, .85]


def ruido(x, y, s):
    return (zlib.crc32(f"{s}:{x},{y}".encode()) % 1000) / 1000


def raio_borda(ang):
    """Borda de fora irregular (rochas soltas), sempre >= raio_min do anel 1 + 2."""
    return R_MAX - .6 + .9 * math.sin(ang * 3 + .7) + .6 * math.sin(ang * 7 + 2.1) + .4 * math.sin(ang * 13)


def anel_de(d):
    for a in ANEIS:
        if a["raio_min"] < d <= a["raio_max"] + 2: return a["id"] if d > a["raio_min"] else None
    return None


def main():
    a = G.Andar("cume_dos_vigilantes", "O Cume dos Vigilantes", W, H, "z", None,
                {"id": "cume_dos_vigilantes", "nome": "O Cume dos Vigilantes", "seguro": False, "nivel": [15, 400],
                 "pvp_evento": True, "musica": "musica/cripta", "ambiente": "ambiente/noite_vento"})
    celula_anel = {}
    for y in range(H):
        for x in range(W):
            dx, dy = x + .5 - CX, y + .5 - CY
            d = math.hypot(dx, dy)
            if d > raio_borda(math.atan2(dy, dx)): continue
            a.ter[y][x] = "z"; a.blk[y][x] = False
            if d <= LAJE: a.ter[y][x] = "h"; continue
            if d <= ANEIS[-1]["raio_max"]: a.ter[y][x] = "l"
            elif ruido(x // 2, y // 2, "vidro") > .72: a.ter[y][x] = "y"
            elif ruido(x // 3, y // 3, "casc") > .8: a.ter[y][x] = "k"
            an = next((r["id"] for r in ANEIS if r["raio_min"] < d <= (r["raio_max"] if r is not ANEIS[0] else 99)), None)
            celula_anel[(x, y)] = an
    # faixa de terra rachada nas divisas dos anéis (onde a fenda corre)
    for r in ANEIS[1:]:
        for y in range(H):
            for x in range(W):
                if a.blk[y][x]: continue
                d = math.hypot(x + .5 - CX, y + .5 - CY)
                if abs(d - r["raio_max"]) < .55 and a.ter[y][x] != "h": a.ter[y][x] = "f"
    a.salas.append(("Laje do Juramento", int(CX - 3), int(CY - 3), int(CX + 2), int(CY + 2)))

    # ---- fendas nas divisas (acendem 20 s antes da queda; tag "racha" = anel que cai do lado de fora dela)
    for i, r in enumerate(ANEIS):
        rr = r["raio_min"]
        n = max(8, int(2 * math.pi * rr / 2.2))
        for k in range(n):
            ang = 2 * math.pi * (k + .5 * (i % 2)) / n
            a.prop("fenda", CX + rr * math.cos(ang), CY + rr * math.sin(ang), chao=True, racha=r["id"])

    # ---- a Laje do Juramento: anel de pilares partidos, braseiros sagrados, velas e o lacre no chão
    for k in range(6):
        ang = 2 * math.pi * k / 6 + .26
        a.prop("pilar_porcelana", CX + 4.1 * math.cos(ang), CY + 4.1 * math.sin(ang), bloqueia=.45, anel="anel_5")
    for k in range(4):
        ang = 2 * math.pi * k / 4 + math.pi / 4
        a.prop("braseiro_sagrado", CX + 2.3 * math.cos(ang), CY + 2.3 * math.sin(ang), bloqueia=.35, luz=SANTO + [6])
    a.prop("velas_chao", CX + .9, CY - .4, chao=True); a.prop("velas_chao", CX - .8, CY + .7, chao=True)
    a.prop("penas_espalhadas", CX - .2, CY - .9, chao=True)

    # ---- os duzentos ajoelhados (posições dos Vigilantes): em círculos, virados para a laje, por área de anel
    vig = []
    raios = [20.0, 18.0, 15.0, 11.0, 7.0]
    nos = [16, 14, 12, 10, 8]       # 60 lugares; o controle usa os primeiros N, espalhados
    for rr, n in zip(raios, nos):
        for k in range(n):
            ang = 2 * math.pi * (k + .37 * rr) / n
            x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
            if a.blk[int(y)][int(x)]: continue
            vig.append({"pos": [round(x, 2), round(y, 2)], "olha": [round(-math.cos(ang), 3), round(-math.sin(ang), 3)],
                        "anel": celula_anel.get((int(x), int(y)))})
    # intercala para que os primeiros N fiquem espalhados por todos os anéis
    ordem = sorted(range(len(vig)), key=lambda i: (zlib.crc32(f"v{i}".encode()) % 997))
    vig = [vig[i] for i in ordem]

    # ---- chegadas (onde o jogador aparece ao romper o convite): no anel 2 e 3, longe dos Vigilantes
    chegadas = []
    for k in range(24):
        ang = 2 * math.pi * (k + .5) / 24
        rr = 13.0 if k % 2 else 16.2
        x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
        if any(math.dist((x, y), v["pos"]) < 1.6 for v in vig): x, y = CX + (rr - 1.2) * math.cos(ang), CY + (rr - 1.2) * math.sin(ang)
        chegadas.append([round(x, 2), round(y, 2)])

    # ---- props do Cume do Hermon (mesmo vocabulário do mapa aberto): estátuas, asas, elmos, crateras, ossada
    def livre_de_props(x, y, d):
        return all(math.dist((x, y), (p["x"], p["y"])) >= d for p in a.props if not p.get("chao")) and \
               all(math.dist((x, y), v["pos"]) >= 1.4 for v in vig) and all(math.dist((x, y), c) >= 1.4 for c in chegadas)
    def soltar(kinds, n, rmin, rmax, bloq, dist, seed, chao=False):
        feitos = t = 0
        while feitos < n and t < 900:
            t += 1
            ang = ruido(t, n, seed + "a") * 2 * math.pi; rr = rmin + (rmax - rmin) * math.sqrt(ruido(t, n, seed + "r"))
            x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
            if not a.livre(int(x), int(y)) or not livre_de_props(x, y, dist): continue
            if any(abs(math.hypot(x - CX, y - CY) - r["raio_min"]) < .8 for r in ANEIS): continue   # longe das fendas
            k = kinds[(zlib.crc32(f"{seed}{t}".encode())) % len(kinds)]
            a.prop(k, x, y, bloqueia=bloq, chao=chao, anel=celula_anel.get((int(x), int(y))))
            feitos += 1
    soltar(["estatua_anjo_quebrada"], 7, 6.5, 19.5, .6, 5.0, "est")
    soltar(["ossada_gigante"], 1, 14, 16, .9, 6.0, "oss")
    soltar(["laje_rolada", "pedra_coberta", "pedra_coberta_2"], 9, 6, 20.5, .5, 3.0, "laje")
    soltar(["asa_anjo_caida", "elmo_espada_fincada", "cratera_cinza", "penas_espalhadas"], 26, 5.5, 21, 0, 2.2, "chao", chao=True)
    # braseiros de ferro na borda (luz quente local; caem com o anel 1)
    for k in range(6):
        ang = 2 * math.pi * k / 6 + .5
        rr = 19.2
        x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
        if a.livre(int(x), int(y)): a.prop("braseiro_ferro", x, y, bloqueia=.35, luz=FOGO + [5], anel="anel_1")
    # torres no abismo, fora do disco (só cenário, longe na nevasca)
    for (x, y) in [(5.5, 10.0), (52.0, 47.0), (9.0, 53.0)]:
        a.prop("torre_no_abismo", x, y, abismo=1)
    a.luzes.append([CX, CY] + LUA + [3])

    m = a.exportar(ceu={"escuro": 0.3, "cor": [0.72, 0.72, 0.82], "neblina": [0.26, 0.27, 0.32]},
                   spawn=chegadas[0])
    m["pisos"] = dict(G.PISOS, h="marmore_templo", f="terra_fenda")
    m["exterior"] = True
    m["sem_penalidade"] = True
    aneis = []
    for r in ANEIS:
        cels = sorted([list(c) for c, an in celula_anel.items() if an == r["id"]])
        aneis.append({"id": r["id"], "raio_min": r["raio_min"], "raio_max": r["raio_max"], "cai_em": r["cai_em"], "celulas": cels})
    m["hermon"] = {
        "centro": [CX, CY], "laje_raio": LAJE, "aneis": aneis, "chegadas": chegadas, "vigilantes": vig,
        "abismo": "células fora do disco e as de cada anel que caiu: sem chão (nevasca e escuro). Ver LEIAME.md",
        "props_por_anel": "props com 'anel' somem/caem junto com o anel; 'racha' = fenda que acende no aviso daquele anel",
    }
    json.dump(m, open(os.path.join(AQUI, "cume_dos_vigilantes.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    try: os.remove(os.path.join(os.path.dirname(G.__file__), "cume_dos_vigilantes.json"))
    except OSError: pass
    G.planta(m, os.path.join(AQUI, "planta_cume_dos_vigilantes.png"), "O Cume dos Vigilantes · evento nv 15+ · 5 anéis caem")
    print("células por anel:", {r["id"]: len(r["celulas"]) for r in aneis}, "vigilantes:", len(vig), "chegadas:", len(chegadas))
    return m


if __name__ == "__main__":
    main()

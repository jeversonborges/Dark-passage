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


MANIFESTO = "/mnt/project-files/assets/ambiente/objetos"   # pasta compartilhada (o repositório tem só parte dos manifestos)


def pegada(k):
    f = os.path.join(MANIFESTO, k + ".json")
    return json.load(open(f)).get("footprint_tiles", [1, 1]) if os.path.exists(f) else [1, 1]


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
        # fendas esparsas: trechos de racha, não um trilho contínuo (4 tiles de cada, pulam conforme o sorteio)
        n = max(6, int(2 * math.pi * rr / 5.5))
        for k in range(n):
            if zlib.crc32(f"f{i}_{k}".encode()) % 100 < 35: continue
            ang = 2 * math.pi * (k + .5 * (i % 2)) / n + .05 * math.sin(k * 1.7)
            a.prop("fenda", CX + rr * math.cos(ang), CY + rr * math.sin(ang), chao=True, racha=r["id"])

    # ---- a Laje do Juramento: anel de pilares partidos, braseiros sagrados, velas e o lacre no chão
    for k in range(6):
        ang = 2 * math.pi * k / 6 + .26
        px_, py_ = CX + 4.1 * math.cos(ang), CY + 4.1 * math.sin(ang)     # pilar de 2x2: trava a pegada toda
        a.prop("pilar_porcelana", px_, py_, anel="anel_5")
        for yy in range(int(py_ - 1), int(py_ + 1)):
            for xx in range(int(px_ - 1), int(px_ + 1)): a.extra_blk.add((xx, yy))
    for k in range(4):
        ang = 2 * math.pi * k / 4 + math.pi / 4
        a.prop("braseiro_sagrado", CX + 2.3 * math.cos(ang), CY + 2.3 * math.sin(ang), bloqueia=.35, luz=SANTO + [6])
    a.prop("velas_chao", CX + .9, CY - .4, chao=True); a.prop("velas_chao", CX - .8, CY + .7, chao=True)
    a.prop("penas_espalhadas", CX - .2, CY - .9, chao=True)

    # ---- os duzentos ajoelhados (posições dos Vigilantes): em círculos, virados para a laje, por área de anel
    vig = []
    raios = [15.0, 12.0, 9.0, 6.5]  # longe da muralha (anel_1 cai de 17 a 22)
    nos = [24, 18, 14, 10]          # candidatos; 3 tiles entre um e outro deixam uns 56 lugares (teto do inicio_max 50)
    for rr, n in zip(raios, nos):
        for k in range(n):
            ang = 2 * math.pi * (k + .37 * rr) / n
            x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
            if a.blk[int(y)][int(x)]: continue
            if any(math.dist((x, y), v["pos"]) < 3.0 for v in vig): continue     # 3 tiles entre um e outro
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

    # ---- o cume: muro baixo de tijolo de lama na beira (a câmera vê o círculo inteiro) e blocos de pedra do Egito
    # (rochas, colunas tombadas, um paredão). Tudo que se vê trava: a pegada do manifesto é bloqueada toda.
    def bloqueia(k, x, y, fp=None):
        fw, fh = fp or pegada(k)
        for yy in range(int(y - fh/2 + .5), int(y - fh/2 + .5) + fh):
            for xx in range(int(x - fw/2 + .5), int(x - fw/2 + .5) + fw): a.extra_blk.add((xx, yy))
    def pode(x, y, fp):
        fw, fh = fp
        for yy in range(int(y - fh/2 + .5), int(y - fh/2 + .5) + fh):
            for xx in range(int(x - fw/2 + .5), int(x - fw/2 + .5) + fw):
                if not a.livre(xx, yy) or (xx, yy) in a.extra_blk: return False
                if any(math.dist((xx + .5, yy + .5), v["pos"]) < 1.2 for v in vig): return False
                if any(math.dist((xx + .5, yy + .5), c) < 1.0 for c in chegadas): return False
                if any(abs(math.hypot(xx + .5 - CX, yy + .5 - CY) - r["raio_min"]) < 0.9 for r in ANEIS): return False
        return True
    def colocar(k, x, y, fp=None):
        fp = fp or pegada(k)
        if not pode(x, y, fp): return False
        a.prop(k, x, y, anel=celula_anel.get((int(x), int(y))))
        bloqueia(k, x, y, fp); return True
    # muro na beira interna: a última faixa de células andáveis vira parede (bloqueia, o abismo já está fora)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x]: continue
            d = math.hypot(x + .5 - CX, y + .5 - CY)
            if d > raio_borda(math.atan2(y + .5 - CY, x + .5 - CX)) - 1.1:
                a.prop("muro_lama_a" if (x + y) % 2 else "muro_lama_b", x + .5, y + .5, anel=celula_anel.get((x, y)))
                a.extra_blk.add((x, y))
    # blocos de pedra: rochas e colunas tombadas entre os anéis (cada uma com a pegada travada)
    n_rocha = n_col = n_par = 0
    for t in range(1500):
        if n_rocha + n_col + n_par >= 12: break
        ang = ruido(t, 7, "bloco_a") * 2 * math.pi
        rr = 17.0 + 3.0 * ruido(t, 9, "bloco_r")
        x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
        if n_par < 2 and rr > 19.2 and colocar("paredao_arenito", x, y): n_par += 1; continue
        if n_col < 4 and colocar("coluna_tombada", x, y): n_col += 1; continue
        if n_rocha < 6 and colocar("rocha_granito", x, y): n_rocha += 1
    # asas e elmos no chão, sem bloquear (são sinais, não paredes)
    for t in range(4000):
        if sum(1 for p in a.props if p["k"] in ("asa_anjo_caida", "elmo_espada_fincada")) >= 4: break
        ang = ruido(t, 3, "chao_a") * 2 * math.pi
        rr = 9.0 + 8.0 * ruido(t, 5, "chao_r")
        x, y = CX + rr * math.cos(ang), CY + rr * math.sin(ang)
        k = "asa_anjo_caida" if t % 2 else "elmo_espada_fincada"
        if all(math.dist((x, y), (p["x"], p["y"])) >= 4.0 for p in a.props if not p.get("chao")) and all(math.dist((x, y), v["pos"]) >= 1.6 for v in vig) \
                and all(math.dist((x, y), c) >= 1.4 for c in chegadas) and a.livre(int(x), int(y)) \
                and not any(abs(math.hypot(x - CX, y - CY) - r["raio_min"]) < .8 for r in ANEIS):
            a.prop(k, x, y, chao=True, anel=celula_anel.get((int(x), int(y))))
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
    m["pisos"] = dict(G.PISOS, h="marmore_templo", f="cinza")
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

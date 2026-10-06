"""Simulacao de balanceamento do DARK PASSAGE (v0.1).
Le os JSON desta pasta e imprime: golpes para matar mobs, golpes que o jogador aguenta,
duracao das lutas de chefe e quanto do HP um golpe grande de chefe tira.
Uso: python3 simular.py
"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(f"{D}/classes_base.json"))["classes"]
M = json.load(open(f"{D}/mobs.json"))
B = json.load(open(f"{D}/chefes.json"))["chefes"]

def stats(cls, L):
    c = C[cls]; a = dict(c["atributos_iniciais"])
    for k, v in c["build_sugerida_por_nivel"].items(): a[k] += v * (L - 1)
    return a

def player(cls, L):
    c = C[cls]; a = stats(cls, L); F, A, V, E = a["FOR"], a["AGI"], a["VIT"], a["ESP"]
    p = c["perfil_dano"]
    mn, mx = {"corpo_a_corpo": (F/6, F/4), "corpo_a_corpo_agil": (F/6 + A/10, F/4 + A/10),
              "distancia": (A/7 + F/14, A/4 + F/8), "magico": (E/9, E/4),
              "sagrado": (E/10 + F/12, E/5 + F/8),
              "hibrido": ((F/6 + A/7 + F/14) / 2, (F/4 + A/4 + F/8) / 2)}[p]  # metade espada, metade tiro
    gear = max(1, L - 1)
    if L <= 2:
        w = c["arma_inicial"]; wmin, wmax = w["min"], w["max"]
    else:
        avg = 5 + 1.2 * gear; wmin, wmax = avg * 0.8, avg * 1.2
    hp = c["hp"]["base"] + c["hp"]["por_nivel"] * L + c["hp"]["por_vit"] * V
    deff = V/5 + A/10 + 1.5 * gear
    crit = min(0.4, 0.05 + A * 0.0008); cm = 1.75 if cls == "humano" else 1.5
    aspd = min(2.0, 1 + A * 0.004)
    interval = c["arma_inicial"]["intervalo"] / aspd
    avg = (mn + mx) / 2 + (wmin + wmax) / 2
    ar = L*3 + (E/2 + A/2 if p == "magico" else A + F/4)
    # hibrido: arma media entre espada larga e escopeta (intervalo medio)
    if p == "hibrido": interval = (c["arma_inicial"]["intervalo"] + c["arma_secundaria"]["intervalo"]) / 2 / aspd
    er = L*2 + A/2
    return dict(hp=hp, avg=avg, deff=deff, crit=crit, cm=cm, interval=interval, ar=ar, er=er)

def mitig(deff, Latk): return min(0.7, deff / (deff + 40 + 8 * Latk))
def hitch(ar, er, dl=0): return max(0.55, min(0.98, 0.90 + 0.25 * (ar - er) / (ar + er) - 0.03 * max(0, dl)))

cb = M["curva_base"]
def mob(L, arq="normal", aj=None):
    m = M["arquetipos"][arq]; aj = aj or {}
    hp = (32 + 7*L) * m["hp"] * aj.get("hp", 1)
    dmg = ((5 + 1.6*L) + (8 + 2.2*L)) / 2 * m["dano"] * aj.get("dano", 1)
    deff = (2 + 1.5*L) * m["defesa"] * aj.get("defesa", 1)
    return dict(hp=hp, dmg=dmg, deff=deff, interval=m["intervalo"], ar=L*4 + 10, er=L*3 + 5)

# ganho medio de dano usando habilidades em rotacao vs so ataque basico (inclui DoT, invocacoes, Furia, Brasa)
ROTS = {"anjo": 1.25, "cultista": 1.55, "mutante": 1.45, "demonio": 1.4, "humano": 1.35, "tecnomancer": 1.5}

def per_hit(p, L, tdeff, tL):
    raw = p["avg"] * (1 + p["crit"] * (p["cm"] - 1))
    return raw * (1 - mitig(tdeff, L))

print("=== Golpes basicos para matar um mob 'normal' do mesmo nivel / golpes de mob que o jogador aguenta ===")
print("nivel " + " ".join(f"{c:>18}" for c in C))
for L in [1, 3, 5, 7, 9, 11, 13]:
    row = []
    for cls in C:
        p = player(cls, L); m = mob(L)
        h = per_hit(p, L, m["deff"], L) * hitch(p["ar"], m["er"])
        taken = m["dmg"] * (1 - mitig(p["deff"], L)) * hitch(m["ar"], p["er"])
        row.append(f"{m['hp']/h:5.1f} / {p['hp']/taken:5.1f} ({p['hp']:.0f}hp)")
    print(f"{L:5} " + " ".join(f"{r:>18}" for r in row))

print("\n=== Chefes (solo, jogador no nivel do chefe, rotacao por classe) ===")
for bid, b in B.items():
    L = b["nivel"]; print(f"\n{b['nome']} (nivel {L}, HP {b['hp']}, alvo ~{b['duracao_alvo_s']}s)")
    for cls in C:
        p = player(cls, L)
        dps = per_hit(p, L, b["defesa"], L) * hitch(p["ar"], b["nivel"]*3+5) / p["interval"] * ROTS[cls]
        # 75% do tempo batendo (resto desviando de telegrafos)
        t = b["hp"] / (dps * 0.75)
        auto = b["dano_base"] * (1 - mitig(p["deff"], L))
        big = auto * 2.2
        print(f"  {cls:12} dps {dps:5.1f}  luta ~{t:4.0f}s  basico {auto/p['hp']*100:4.1f}% HP  golpe grande x2.2 {big/p['hp']*100:4.1f}% HP")

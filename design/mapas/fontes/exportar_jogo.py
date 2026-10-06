"""Gera para_o_jogo/area_inicial.json: o mapa aprovado num formato que o jogo atual
(game/scripts/sim/world_sim.gd) já carrega sem travar.
Uso: python3 exportar_jogo.py  (rodar depois de layout.py)"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, "..", "area_inicial.json")
DST = os.path.join(AQUI, "..", "para_o_jogo", "area_inicial.json")
MON = "/mnt/project-files/game/data/monstros.json"

# Mob do design (design/combate/mobs.json) -> monstro que já existe em game/data/monstros.json.
# Só vale até o jogo ganhar os mobs novos; o id original fica em "kind_design".
SUBSTITUTO = {
    "carnical": "carnical", "cao_de_vala": "cao_praga", "corvo_de_cinza": "cao_praga",
    "porco_pestilento": "cao_praga", "nao_julgado": "flagelado",
    "acougueiro_oco": "acougueiro", "capataz_gancho": "acougueiro", "filho_de_cardo": "automato",
}

m = json.load(open(SRC))
existentes = set(json.load(open(MON)))
spawns, fora = [], []
for s in m["spawns"]:
    if s.get("so_para") or s.get("so_por_missao"):
        fora.append(s["kind"]); continue          # patrulhas de facção (PvP) e mob de missão
    s = dict(s)
    s.pop("_dist_trilha", None)
    if s["kind"] not in existentes:
        s["kind_design"] = s["kind"]
        s["kind"] = SUBSTITUTO[s["kind"]]
    s["radius"] = max(1, s["radius"])
    spawns.append(s)
m["spawns"] = spawns
m["_export"] = {"origem": "design/mapas/area_inicial.json", "fora_do_export": fora,
                "nota": "kind_design = mob final; kind = substituto até o monstro existir no jogo"}
os.makedirs(os.path.dirname(DST), exist_ok=True)
json.dump(m, open(DST, "w"), ensure_ascii=False, separators=(",", ":"))
assert all(s["kind"] in existentes for s in m["spawns"])
print(f"{len(spawns)} grupos, {sum(s['count'] for s in spawns)} mobs; fora: {fora}")

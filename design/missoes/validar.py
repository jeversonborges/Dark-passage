#!/usr/bin/env python3
"""Confere se os JSONs de missões, NPCs, diálogos, itens, monstros e objetos se referenciam corretamente.
Uso: python3 validar.py   (sai com código 1 se achar erro)"""
import json, os, sys

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
def load(n): return json.load(open(os.path.join(D, n), encoding="utf-8"))

locais, npcs, mons, itens, missoes, dlgs, objs, lojas = (load(f) for f in
    ["locais.json", "npcs.json", "monstros.json", "itens.json", "missoes.json", "dialogos.json", "objetos.json", "lojas.json"])

erros = []
def err(m): erros.append(m)

sub = {s["id"] for a in locais["areas"] for s in a["subzonas"]}
sub |= {f["id"] for d in locais["dungeons"] for f in d["andares"]}
NPC = {n["id"]: n for n in npcs["npcs"]}
MON = {m["id"]: m for m in mons["monstros"]}
IT = {i["id"]: i for i in itens["itens"]}
MS = {q["id"]: q for q in missoes["missoes"]}
DL = {d["id"]: d for d in dlgs["dialogos"]}
OB = {o["id"] for o in objs["objetos"]} | {b["id"] for b in objs["baus"]}
SPOT = {}
_sp = os.path.join(os.path.dirname(D), "..", "mapas", "spots.json")
if os.path.exists(_sp):
    for sp in json.load(open(_sp, encoding="utf-8"))["spots"]: SPOT[sp["id"]] = sp
for sp in locais.get("spots", {}).get("pedidos", []):
    SPOT.setdefault(sp["id"], sp)
    for mm in sp.get("monstros", []) + sp.get("acrescentar_monstros", []):
        if mm not in MON: err(f"spot pedido {sp['id']}: monstro '{mm}'")
for nome, col in [("npc", npcs["npcs"]), ("monstro", mons["monstros"]), ("item", itens["itens"]),
                  ("missao", missoes["missoes"]), ("dialogo", dlgs["dialogos"])]:
    ids = [x["id"] for x in col]
    for i in set(ids):
        if ids.count(i) > 1: err(f"{nome} duplicado: {i}")

def chk_item(i, ctx):
    if i not in IT: err(f"{ctx}: item inexistente '{i}'")
def chk_npc(n, ctx):
    for x in (n if isinstance(n, list) else [n]):
        if x != "automatico" and x not in NPC: err(f"{ctx}: npc inexistente '{x}'")
def chk_ms(q, ctx):
    for x in (q if isinstance(q, list) else [q]):
        if x not in MS: err(f"{ctx}: missão inexistente '{x}'")
def chk_rec(r, ctx):
    for it in r.get("itens", []): chk_item(it["id"], ctx)
    for cl, it in r.get("escolha_por_classe", {}).items():
        chk_item(it, ctx)
        if cl not in IT.get(it, {}).get("classe", [cl]): err(f"{ctx}: {it} não é da classe {cl}")

for n in NPC.values():
    if n["local"]["subzona"] not in sub: err(f"npc {n['id']}: subzona '{n['local']['subzona']}'")
    if n["dialogo"] not in DL: err(f"npc {n['id']}: diálogo '{n['dialogo']}' não existe")
for m in MON.values():
    for l in m["locais"]:
        if l not in sub: err(f"monstro {m['id']}: local '{l}'")
    for dr in m.get("drops_missao", []):
        chk_item(dr["item"], f"monstro {m['id']}"); chk_ms(dr["missao"], f"monstro {m['id']}")
for i in IT.values():
    if "leitura" in i: chk_item(i["leitura"], f"item {i['id']}")

for q in MS.values():
    c = f"missão {q['id']}"
    chk_npc(q["doador"], c); chk_npc(q["entrega"], c)
    for r in q.get("requer", []) + q.get("requer_qualquer", []) + q.get("falha_ao_aceitar", []): chk_ms(r, c)
    if "ao_concluir_inicia" in q: chk_ms(q["ao_concluir_inicia"], c)
    for it in q.get("ao_aceitar_recebe", []): chk_item(it["id"], c)
    chk_rec(q.get("recompensas", {}), c)
    for e in q.get("escolhas", []): chk_rec(e["recompensas"], f"{c}/{e['id']}")
    for o in q["objetivos"]:
        t = o["tipo"]
        if t == "matar" and o["alvo"] not in MON: err(f"{c}: monstro '{o['alvo']}'")
        if t in ("coletar", "usar_item"): chk_item(o["item"], c)
        if t in ("falar", "decidir"): chk_npc(o["npc"], c)
        if t in ("interagir", "usar_item"):
            if o["objeto"] not in OB: err(f"{c}: objeto '{o['objeto']}'")
            if o["subzona"] not in sub: err(f"{c}: subzona '{o['subzona']}'")
        if t == "explorar" and o["subzona"] not in sub: err(f"{c}: subzona '{o['subzona']}'")
        if t == "farmar_spot" and o["spot"] not in SPOT: err(f"{c}: spot '{o['spot']}'")
        for it in o.get("concede", []): chk_item(it["id"], c)
        if t == "coletar":
            fontes = [m["id"] for m in MON.values() for dr in m.get("drops_missao", []) if dr["item"] == o["item"] and dr["missao"] == q["id"]]
            fontes += [1 for oo in q["objetivos"] for it in oo.get("concede", []) if it["id"] == o["item"]]
            fontes += [1 for b in objs["baus"] for it in b.get("fixo", []) if it["id"] == o["item"]]
            if not fontes: err(f"{c}: nada dropa '{o['item']}' para esta missão")
    if q["tipo"] in ("principal", "dungeon", "secundaria", "repetivel") and q["doador"] != "automatico" and not q.get("oculta"):
        d = DL[NPC[q["doador"]]["dialogo"]]
        if f'"aceitar_missao": "{q["id"]}"' not in json.dumps(d, ensure_ascii=False):
            err(f"{c}: diálogo de {q['doador']} não oferece a missão")
    entregas = q["entrega"] if isinstance(q["entrega"], list) else [q["entrega"]]
    if entregas != ["automatico"]:
        if not any(f'"concluir_missao": "{q["id"]}"' in json.dumps(DL[NPC[e]["dialogo"]], ensure_ascii=False) for e in entregas):
            err(f"{c}: nenhum diálogo de entrega conclui a missão")
    for e in q.get("escolhas", []):
        if not any(f'"escolha": "{e["id"]}"' in json.dumps(DL[NPC[x]["dialogo"]], ensure_ascii=False) for x in entregas):
            err(f"{c}: escolha '{e['id']}' não aparece em diálogo")

CONDS = {"missao_disponivel", "missao_ativa", "missao_pronta", "missao_concluida", "missao_nao_iniciada", "faccao", "flag", "sem_flag", "tem_item"}
ACOES = {"aceitar_missao", "concluir_missao", "escolha", "falhar_missao", "cumprir_falar", "abrir_loja", "abrir_ferreiro",
         "abrir_armazem", "abrir_treinador", "dar_item", "remover_item", "definir_flag"}
SERV = {"abrir_loja": {x["id"] for x in lojas["lojas"]}, "abrir_ferreiro": {x["id"] for x in lojas["ferreiros"]},
        "abrir_treinador": {x["id"] for x in lojas["treinadores"]}}
for s_ in lojas["lojas"]:
    for i in s_["itens"]: chk_item(i, f"loja {s_['id']}")
def chk_se(se, ctx):
    for k, v in se.items():
        if k not in CONDS: err(f"{ctx}: condição desconhecida '{k}'")
        if k.startswith("missao"): chk_ms(v, ctx)
        if k == "tem_item": chk_item(v if isinstance(v, str) else v["id"], ctx)
for d in DL.values():
    if d["npc"] not in NPC: err(f"{d['id']}: npc '{d['npc']}'")
    nos = d["nos"]
    if d["inicio"] not in nos: err(f"{d['id']}: nó inicial ausente")
    alcancados = {d["inicio"]}
    for nid, no in nos.items():
        ctx = f"{d['id']}/{nid}"
        if isinstance(no["fala"], list):
            for v in no["fala"]: chk_se(v.get("se", {}), ctx)
        for op in no["opcoes"]:
            chk_se(op.get("se", {}), ctx)
            if "ir" in op:
                if op["ir"] not in nos: err(f"{ctx}: vai para nó inexistente '{op['ir']}'")
                alcancados.add(op["ir"])
            for a in op.get("acoes", []):
                for k, v in a.items():
                    if k not in ACOES: err(f"{ctx}: ação desconhecida '{k}'")
                    if k in ("aceitar_missao", "concluir_missao", "falhar_missao", "cumprir_falar"): chk_ms(v, ctx)
                    if k in ("dar_item", "remover_item"): chk_item(v["id"], ctx)
                    if k in SERV and v not in SERV[k]: err(f"{ctx}: {k} '{v}' não existe em lojas.json")
    for nid in set(nos) - alcancados: err(f"{d['id']}: nó '{nid}' nunca é alcançado")

for o in objs["objetos"] + objs["baus"]:
    if o["subzona"] not in sub: err(f"objeto {o['id']}: subzona '{o['subzona']}'")
    for it in o.get("fixo", []): chk_item(it["id"], f"objeto {o['id']}")
    for k in ("requer_item", "leitura"):
        if k in o: chk_item(o[k], f"objeto {o['id']}")
    for it in o.get("requer_itens", []): chk_item(it, f"objeto {o['id']}")

if erros:
    print(f"{len(erros)} problema(s):"); [print(" -", e) for e in erros]; sys.exit(1)
print(f"OK: {len(MS)} missões, {len(NPC)} NPCs, {len(DL)} diálogos, {len(IT)} itens, {len(MON)} monstros, {len(OB)} objetos/baús.")

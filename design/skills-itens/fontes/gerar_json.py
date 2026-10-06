# Gera ../skills.json e ../itens.json. Lê também design/combate/classes_base.json e design/missoes/dados/itens.json (sem editá-los).
import json, os, unicodedata
from skills_data import S, RECURSOS, MODO_AUTO, ID_COMBATE_N5
import itens_data as I
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(AQUI, ".."); DES = os.path.join(AQUI, "../..")
AVISO = "Números PROVISÓRIOS. Fonte de verdade do balanceamento: design/combate/ (classes_base.json, drops.json, formulas.json)."

# ---------------- skills ----------------
base = json.load(open(f"{DES}/combate/classes_base.json"))
def norm(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
skills = []
for s in S:
    s = dict(s); cls = s["classe"]
    hab = base["classes"][cls]["habilidades"]
    if s["id"] in ID_COMBATE_N5:
        comb = next((h for h in hab if h["id"] == ID_COMBATE_N5[s["id"]]), None)
    else:
        comb = next((h for h in hab if norm(h["nome"]) == norm(s["nome"])), None)
        if comb and comb["id"] in ID_COMBATE_N5.values(): comb = None   # a Rajada do combate agora é o slot do Coquetel
    if s.get("area_nivel5") and comb:
        s["id_combate"] = comb["id"]
        s["substitui_no_combate"] = ("mesmo id em classes_base.json; números de lá, nome, descrição, FX e ícone daqui." if comb["id"] == s["id"] else f"classes_base.json '{comb['id']}' ({comb['nome']}) = esta skill. Use o id e os números de lá; nome, descrição, FX e ícone daqui.")
        s.pop("economia_auto", None)
        f = s["formato_area"]
        if f["forma"] == "cone": f.update(angulo_graus=comb.get("cone_graus", f["angulo_graus"]), raio_tiles=comb.get("raio", f["raio_tiles"]))
        else: f["raio_tiles"] = comb.get("raio", f["raio_tiles"])
        s["area"] = f"leque de {f['angulo_graus']}°, {f['raio_tiles']} tiles" if f["forma"] == "cone" else f"círculo de {f['raio_tiles']} tiles" + (" no ponto do mouse" if f.get("origem") == "ponto_alvo" else " em volta")
        s["dano"] = {"mult": comb.get("mult")} | {k: comb[k] for k in ("queimadura","sangramento","veneno","chao_em_chamas_s","chance_atordoar","atordoar_s") if k in comb}
        s["economia"] = "ver design/combate/farm_auto.json e combate.md seção 9"
    if comb:
        s["combate"] = comb
        for k in ("nivel", "custo", "recarga", "alcance", "conjuracao", "preparo"):
            if k in comb: s[k] = comb[k]
        if isinstance(comb.get("custo"), float) and comb["custo"] < 1: s["custo"] = (f"{comb['custo']*100:.1f}".rstrip("0").rstrip(".").replace(".", ",") + "% HP")
        if not s.get("area_nivel5"):
            for k in ("dano", "cura", "escudo", "invocacao"): s.pop(k, None)   # números de dano ficam no bloco 'combate'
        s["fonte_numeros"] = "design/combate/classes_base.json"
    else:
        s["fonte_numeros"] = "provisório: skill de área do nível 5, aguardando Design do combate" if s.get("area_nivel5") else "provisório (suprema, fora da 1ª entrega)"
    s["provisorio"] = True
    s["icone"] = {t: f"assets/icones/skills/{t}/{s['id']}.png" for t in (64, 40, 32)}
    skills.append(s)
skills.sort(key=lambda s: (["anjo","cultista","mutante","demonio","humano","tecnomancer"].index(s["classe"]), s["nivel"]))
json.dump({"versao":"0.3","aviso":AVISO,"recursos":RECURSOS,"modo_automatico":MODO_AUTO,"skills":skills}, open(f"{OUT}/skills.json","w"), ensure_ascii=False, indent=1)

# ---------------- itens ----------------
drops = json.load(open(f"{DES}/combate/drops.json"))
apf = base["armas_por_faixa"]
def dano(n, mult=1.0):
    m = (5 + 1.2*n) * mult; return [max(1, round(m*(1-apf["spread_min_max"]/2))), round(m*(1+apf["spread_min_max"]/2))]
def faixa(n): return "faixa1" if n < 7 else "faixa2"
INTERVALO = {"espada":1.05,"adaga":1.0,"lanca":1.15,"machado":1.2,"foice":0.95,"escopeta":1.3,"cajado":1.1,"punhos":1.0}
itens = []
def add(cat, d, **extra):
    d = dict(d); d.update(extra); d["categoria"] = cat
    d["icone"] = {t: f"assets/icones/itens/{t}/{d['id']}.png" for t in (64, 40, 32)}
    d["icone_mochila"] = f"assets/icones/itens/mochila/{d['id']}.png"
    d.setdefault("grade", [1,1]); itens.append(d)

for (iid, nome, cls, tipo, maos, n, intervalo, grade, mot, tint, em, lore) in I.ARMAS:
    d = dict(id=iid, nome=nome, classes=cls, tipo=tipo, slot="arma" if tipo not in ("escudo","grimorio") else "segunda_mao", maos=maos,
             nivel=n, raridade="rolada", tags=[f"equip:{faixa(n)}"], grade=grade, motivo=mot, tint=tint, emissivo=em, lore=lore)
    if tipo == "escudo": d.update(defesa=round(1.5*n*0.3+2), bloqueio=0.12)
    elif tipo == "grimorio": d.update(dano_magico_extra=round(0.4*(5+1.2*n)))
    else: d.update(dano=dano(n), intervalo=intervalo)
    add("arma", d)
# armas iniciais e secundárias do combate: usam os números de lá
for cls, cv in base["classes"].items():
    for chave in ("arma_inicial", "arma_secundaria"):
        ai = cv.get(chave)
        if not ai: continue
        for it in itens:
            if it["nome"] == ai["nome"] or norm(it["nome"]) == norm(ai["nome"]):
                it.update(dano=[ai["min"], ai["max"]], intervalo=ai["intervalo"], arma_de=f"{cls}:{chave}", fonte_numeros="design/combate/classes_base.json")
for c in I.CONJUNTOS:
    for slot, nome in c["pecas"].items():
        add("armadura", dict(id=f"{c['id']}_{slot}", nome=nome, slot=slot, conjunto=c["id"], peso=c["peso"], classes=I.PESOS[c["peso"]],
            nivel=c["nivel"], raridade="rolada", tags=[f"equip:{faixa(c['nivel'])}"],
            defesa=max(1, round(1.5*c["nivel"]*I.FRACAO_DEF[slot]*I.MULT_PESO[c["peso"]])), grade=I.GRADE_SLOT[slot],
            motivo=f"{ {'cabeca':'elmo'}.get(slot, slot) }_{c['peso']}", tint=c["tint"], emissivo=c.get("emissivo"), lore=c["lore"]))
for a in I.ACESSORIOS:
    a = dict(a); f = a.pop("faixa"); add("acessorio", a, raridade="rolada", tags=[f"equip:faixa{f}"])
for a in I.CONSUMIVEIS: add("consumivel", dict(a, tags=[a.pop("tag")] if "tag" in a else []))
for a in I.MATERIAIS: add("material", dict(a, tags=[a.pop("tag")], pilha=99))
for a in I.JOIAS: add("joia", dict(a, tags=[a.pop("tag")], raridade="excelente", pilha=20))
for a in I.CHAVES_BAUS:
    a = dict(a); t = a.pop("tag", None); add(a["tipo"], dict(a, tags=[t] if t else []))

# itens com nome da thread Missões
mis = json.load(open(f"{DES}/missoes/dados/itens.json"))["itens"]
em_pool = {i: tag for tag, ids in I.POOLS_LENDARIOS.items() for i in ids}
MULT_RAR = {"comum":1.0,"magico":1.0,"raro":1.1,"lendario":1.25}
SLOT = {"cabeca":"cabeca","peito":"peito","amuleto":"amuleto","arma":"arma"}
for m in mis:
    if m["id"] not in I.MISSOES:
        print("AVISO: item novo de Missões sem ícone definido, usando papel:", m["id"]); I.MISSOES[m["id"]] = ("papel", "pano", None, [1,1])
    mot, tint, em, grade = I.MISSOES[m["id"]]
    nome = m["nome"]
    d = {"id": m["id"], "nome": nome, "fonte": "design/missoes/dados/itens.json", "motivo": mot, "tint": tint, "emissivo": em, "grade": grade}
    if m["tipo"] == "equipamento":
        rar = I.RARIDADE_MISSAO[m["raridade"]]; tags = []
        if m["id"] in em_pool:
            tags.append(em_pool[m["id"]])
            if rar != "lendario": d["nota_raridade"] = f"Missões marcou '{m['raridade']}'; como sai pela tag {em_pool[m['id']]} de drops.json, vira Relíquia (lendário)."
            rar = "lendario"
        slot = m.get("slot")
        if slot == "acessorio": slot = "anel" if m["id"] in ("selo_madre","faixa_vigilia","fita_juizo") else "amuleto"
        d.update(raridade=rar, slot=slot, nivel=m["nivel"], tags=tags, classes=m.get("classe"), faccao=m.get("faccao"))
        at = dict(m.get("atributos", {}))
        if "dano" in at:
            d["dano_sugerido_missoes"] = at.pop("dano"); d["dano"] = dano(m["nivel"], MULT_RAR[rar])
            d["intervalo"] = INTERVALO.get({"escopeta_badalada":"escopeta","machado_bonde":"machado","cajado_lampiao":"cajado","espada_escudeiro":"espada",
                "foice_penhor":"foice","adaga_chaga":"adaga","gancho_capataz":"machado","estandarte_legiao":"lanca","bacula_femur":"cajado"}.get(m["id"]), 1.0)
        if "defesa" in at:
            frac = I.FRACAO_DEF.get(slot, 0.2)
            d["defesa_sugerida_missoes"] = at.pop("defesa"); d["defesa"] = max(1, round(1.5*m["nivel"]*frac*MULT_RAR[rar]*1.2))
        d["atributos"] = at
        if "efeito" in m: d["efeito"] = m["efeito"]
        add("arma" if slot == "arma" else ("armadura" if slot in ("cabeca","peito") else "acessorio"), d)
    else:
        d["tipo_missao"] = m["tipo"]
        add({"missao":"missao","consumivel":"consumivel","leitura":"leitura"}[m["tipo"]], d)

ids = [i["id"] for i in itens]; assert len(ids) == len(set(ids)), [x for x in ids if ids.count(x) > 1]
tags_drops = sorted({r["tag"] for t in drops["tabelas"].values() for r in t.get("rolagens", [])})
cobertura = {t: [i["id"] for i in itens if t in i.get("tags", [])] for t in tags_drops}
json.dump({"versao":"0.2","aviso":AVISO,
  "raridades":"ver design/combate/drops.json (comum, magico, raro, excelente, lendario = Relíquia). Itens BASE têm raridade 'rolada' no drop.",
  "refino":{"no_drop":"+0 a +3 (drops.json, +8% de dano/defesa base por nível)", "joias":{"+1..+6":"Lágrima de Anjo, 100%", "+7..+9":"Fragmento de Alma, 55%; falha volta 1 nível"},
            "brilho":{"+0..+4":"nenhum","+5..+6":"brilho fraco na cor da raridade","+7..+8":"brilho forte","+9":"brilho forte + partículas (assinatura MU)"}},
  "formulas_usadas":{"dano_arma":"média 5 + 1,2 × nível (classes_base.json), mín/máx ±30%; itens com nome: ×1,1 raro, ×1,25 Relíquia",
                     "defesa_conjunto":"1,5 × nível no conjunto inteiro; cabeça 16%, peito 34%, luvas 12%, calças 22%, botas 16%; leve ×0,8, pesado ×1,25"},
  "grade_mochila":"células de 30 px (UI); grade = [largura, altura]",
  "conjuntos":[{k:v for k,v in c.items() if k != "pecas"} | {"pecas":[f"{c['id']}_{s}" for s in c["pecas"]]} for c in I.CONJUNTOS],
  "pools_lendarios":I.POOLS_LENDARIOS, "cobertura_tags_drops":cobertura, "itens":itens}, open(f"{OUT}/itens.json","w"), ensure_ascii=False, indent=1)
print(len(skills), "skills;", len(itens), "itens"); print({t: len(v) for t, v in cobertura.items()})

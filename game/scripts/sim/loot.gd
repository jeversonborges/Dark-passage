class_name Loot
## Drops de monstros e baús (design/combate/drops.json). Loot pessoal: cada jogador rola o seu.

static func tabela_por_nivel(nivel: int) -> String:
	return "inicial_humanoide" if nivel < 6 else "cripta_humanoide"

## Escolhe um item que satisfaz uma tag de drop.
static func item_da_tag(sim: WorldSim, tag: String, nivel: int, minima: String, jog: Ent) -> Dictionary:
	if tag.begins_with("equip:"):
		var ids: Array = Defs.POR_TAG.get(tag, [])
		# prefere itens que a classe do jogador usa (70%)
		var meus := ids.filter(func(i):
			var cl = Defs.ITENS[i].get("classes")
			return cl == null or (cl is Array and (cl.is_empty() or jog.classe in cl)))
		var pool: Array = meus if (meus.size() > 0 and sim.rng.randf() < 0.7) else ids
		if pool.is_empty(): return {}
		var id: String = pool[sim.rng.randi_range(0, pool.size() - 1)]
		var f := 1 if tag.ends_with("1") else 2
		return Itens.gerar_equip(id, sim.rng, minima, f)
	if tag.begins_with("lendario:"):
		var pool: Array = Defs.ITENS_DOC["pools_lendarios"].get(tag, [])
		if pool.is_empty(): return {}
		var it := Itens.novo(pool[sim.rng.randi_range(0, pool.size() - 1)])
		it["raridade"] = "lendario"
		return it
	if tag.begins_with("missao:"):
		return Itens.novo(tag.substr(7))
	var ids2: Array = Defs.POR_TAG.get(tag, [])
	if ids2.is_empty(): return {}
	var it2 := Itens.novo(ids2[sim.rng.randi_range(0, ids2.size() - 1)])
	if tag == "consumivel:municao":
		var arma_tipo: String = Regras.Ent_arma(jog).get("tipo", "")
		for i in ids2:
			if str(Defs.ITENS[i].get("efeito", {}).get("municao", "")) == arma_tipo: it2 = Itens.novo(i)
		it2["qtd"] = sim.rng.randi_range(20, 45)
	return it2

static func _peso(sim: WorldSim, rolagens: Array) -> Dictionary:
	var tot := 0.0
	for r in rolagens: tot += float(r["peso"])
	var x := sim.rng.randf() * tot
	for r in rolagens:
		x -= float(r["peso"])
		if x <= 0.0: return r
	return rolagens[0]

static func dropar_mob(sim: WorldSim, e: Ent, jog: Ent) -> void:
	var m: Dictionary = Defs.MOBS.get(e.kind, {})
	var tab_id = m.get("drop")
	if e.tipo == "chefe": tab_id = Defs.CHEFES[e.kind].get("drop")
	var tab: Dictionary = Defs.DROPS["tabelas"].get(tab_id, {}) if tab_id != null else {}
	var arq: Dictionary = Defs.MOBS_BASE["arquetipos"].get(e.arquetipo, {"xp": 1.0})
	var bonus_ouro := 1.0 + float(jog.aux.get("bonus", {}).get("ouro", 0.0))
	# ouro
	if sim.rng.randf() < float(Defs.DROPS["regras"]["ouro_chance"]) or tab.has("ouro_mult") or e.tipo == "chefe":
		var g := sim.rng.randi_range(2 * e.nivel, 5 * e.nivel) * float(arq.get("xp", 1.0)) * float(tab.get("ouro_mult", 1.0)) * bonus_ouro
		if e.tipo == "chefe": g = sim.rng.randi_range(2 * e.nivel, 5 * e.nivel) * float(tab.get("ouro_mult", 20))
		_soltar_ouro(sim, int(g), e.pos, jog)
	# itens de missão (só para quem tem a missão ativa e ainda precisa)
	var txt: Dictionary = Defs.MON_TXT.get(e.kind, {})
	var ja := {}
	for dm in txt.get("drops_missao", []):
		if ja.has(dm["item"]): continue
		# a Chave de Gancho (porão -> chefes) cai sempre para quem ainda não tem e não abriu a porta
		var chave: bool = dm["item"] == "chave_gancho" and Itens.contar(jog.inv, "chave_gancho") == 0 and not jog.flags.has("aberto_porta_ganchos")
		if (chave or Missoes.precisa_item(jog, dm["missao"], dm["item"])) and sim.rng.randf() < float(dm["chance"]):
			ja[dm["item"]] = true
			sim.soltar_no_chao(Itens.novo(dm["item"]), e.pos, jog.id, e.pos)
	# spot de farm (farm_auto.json): 10% de chance extra de poção
	if e.tipo == "monstro" and (str(e.aux.get("spot", "")) != "" or sim.spot_em(e.pos) != "") and sim.rng.randf() < 0.1:
		var r0 := sim.rng.randf() * 100.0
		var pid := "pocao_vida_p" if r0 < 50.0 else ("pocao_recurso_p" if r0 < 90.0 else ("pocao_vida_m" if r0 < 96.0 else "pocao_recurso_m"))
		if Defs.ITENS.has(pid): sim.soltar_no_chao(Itens.novo(pid), e.pos, jog.id, e.pos)
	if tab.is_empty(): return
	var muito_abaixo := jog.nivel - e.nivel >= 6
	for gid in tab.get("garantido", []):
		var it := item_da_tag(sim, gid, e.nivel, "comum", jog)
		if not it.is_empty(): sim.soltar_no_chao(it, e.pos, jog.id, e.pos)
	var n := 0
	if tab.has("rolagens_garantidas"): n = int(tab["rolagens_garantidas"])
	elif sim.rng.randf() < float(tab.get("item_chance", 0.0)): n = 1
	var minima: String = tab.get("raridade_minima", "comum")
	jog.pity_raro += 1
	for i in n:
		var r := _peso(sim, tab["rolagens"])
		var tag: String = r["tag"]
		if muito_abaixo and tag.begins_with("equip"): continue
		var mn := minima
		if jog.pity_raro >= int(Defs.DROPS["pity"]["raro_garantido_apos_abates_sem_raro"]) and tag.begins_with("equip"): mn = "raro"
		var it := item_da_tag(sim, tag, e.nivel, mn, jog)
		if it.is_empty(): continue
		if it.get("raridade", "comum") in ["raro", "excelente", "lendario"]: jog.pity_raro = 0
		sim.soltar_no_chao(it, e.pos, jog.id, e.pos)

static func _soltar_ouro(sim: WorldSim, g: int, p: Vector2, jog: Ent) -> void:
	if g <= 0: return
	var it := {"uid": -1, "id": "_ouro", "qtd": g, "raridade": "comum"}
	sim.soltar_no_chao(it, p, jog.id, p)

## Abre um baú (já validado). tipo: caixote_podre | bau_de_ferro | relicario_da_trombeta | bau_chefe
static func abrir_bau(sim: WorldSim, b: Ent, jog: Ent) -> void:
	var t: String = b.aux.get("bau", "caixote_podre")
	var nivel: int = int(b.aux.get("nivel", maxi(1, jog.nivel)))
	var regra: Dictionary = Defs.DROPS["baus"].get(t, Defs.DROPS["baus"]["caixote_podre"])
	var hist: Dictionary = Defs.BAUS_HIST.get(b.aux.get("hist", ""), {})
	for f in hist.get("fixo", []):
		sim.soltar_no_chao(Itens.novo(f["id"], int(f.get("qtd", 1))), b.pos, jog.id, b.pos)
	if hist.has("texto_ao_abrir"): sim.emitir_a(jog, "texto", {"titulo": hist.get("nome", b.nome), "texto": hist["texto_ao_abrir"]})
	elif b.aux.has("texto_ao_abrir"): sim.emitir_a(jog, "texto", {"titulo": b.nome, "texto": b.aux["texto_ao_abrir"]})
	var rol = regra.get("rolagens", [1, 2])
	var n := sim.rng.randi_range(int(rol[0]), int(rol[1]))
	var minima: String = regra.get("raridade_minima", "comum")
	var f := 1 if nivel < 7 else 2
	for i in n:
		var x := sim.rng.randf()
		var it: Dictionary
		if t == "relicario_da_trombeta" and sim.rng.randf() < float(regra.get("reliquia_chance", 0.2)):
			it = item_da_tag(sim, "lendario:zacarias", nivel, "raro", jog)
		elif x < 0.55:
			it = item_da_tag(sim, "equip:faixa%d" % f, nivel, minima, jog)
		elif x < 0.8:
			it = item_da_tag(sim, ["consumivel:pocao_vida_p", "consumivel:pocao_recurso_p", "consumivel:pocao_vida_m"][sim.rng.randi_range(0, 2 if f == 2 else 1)], nivel, "comum", jog)
			it["qtd"] = sim.rng.randi_range(1, 3)
		else:
			it = item_da_tag(sim, "consumivel:municao" if jog.classe == "humano" else "consumivel:extra", nivel, "comum", jog)
		if not it.is_empty(): sim.soltar_no_chao(it, b.pos, jog.id, b.pos)
	if sim.rng.randf() < float(regra.get("joia_refino_chance", 0.0)):
		sim.soltar_no_chao(Itens.novo("lagrima_anjo"), b.pos, jog.id, b.pos)
	_soltar_ouro(sim, int(sim.rng.randi_range(2 * nivel, 5 * nivel) * float(regra.get("ouro_mult", 1))), b.pos, jog)

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
		var tot := 0.0
		for i in pool: tot += float(Defs.ITENS[i].get("peso_drop", 1.0))
		var x := sim.rng.randf() * tot
		var id: String = pool[pool.size() - 1]
		for i in pool:
			x -= float(Defs.ITENS[i].get("peso_drop", 1.0))
			if x <= 0.0: id = i; break
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

## Variante Deus (balanco.variante_deus): quando a arma-base cai, esta chance a troca pela versão Deus (atributos x1,35).
static func _trocar_por_deus(sim: WorldSim, it: Dictionary) -> Dictionary:
	if it.is_empty(): return it
	var vid := Itens.deus_de(str(it.get("id", "")))
	if vid == "" or sim.rng.randf() >= float(Defs.DROPS["balanco"]["variante_deus"]): return it
	return Itens.novo(vid)

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
		var g := sim.rng.randf_range(2.6 * e.nivel, 6.5 * e.nivel) * float(arq.get("xp", 1.0)) * float(tab.get("ouro_mult", 1.0)) * bonus_ouro
		if e.tipo == "chefe": g = sim.rng.randi_range(2 * e.nivel, 5 * e.nivel) * float(tab.get("ouro_mult", 20))
		_soltar_ouro(sim, int(g), e.pos, jog)
	# itens de missão (só para quem tem a missão ativa e ainda precisa)
	var txt: Dictionary = Defs.MON_TXT.get(e.kind, {})
	var ja := {}
	for dm in txt.get("drops_missao", []):
		if ja.has(dm["item"]): continue
		# a Chave de Gancho (porão -> chefes) e a Chave de Pã (Fontes do Jordão -> Fosso) caem sempre para quem ainda não tem e não abriu a porta
		var porta_da_chave := {"chave_gancho": "porta_ganchos", "chave_de_pa": "porta_de_pa"}
		var chave: bool = porta_da_chave.has(dm["item"]) and Itens.contar(jog.inv, dm["item"]) == 0 and not jog.flags.has("aberto_" + porta_da_chave[dm["item"]])
		if (chave or Missoes.precisa_item(jog, dm["missao"], dm["item"])) and sim.rng.randf() < float(dm["chance"]):
			ja[dm["item"]] = true
			sim.soltar_no_chao(Itens.novo(dm["item"]), e.pos, jog.id, e.pos)
	# spot de farm (farm_auto.json): 10% de chance extra de poção
	if e.tipo == "monstro" and (str(e.aux.get("spot", "")) != "" or sim.spot_em(e.pos) != "") and sim.rng.randf() < 0.1:
		var r0 := sim.rng.randf() * 100.0
		var pid := "pocao_vida_p" if r0 < 50.0 else ("pocao_recurso_p" if r0 < 90.0 else ("pocao_vida_m" if r0 < 96.0 else "pocao_recurso_m"))
		if Defs.ITENS.has(pid): sim.soltar_no_chao(Itens.novo(pid), e.pos, jog.id, e.pos)
	_rolar_lagrimas(sim, e, jog, tab_id)
	if sim.rng.randf() < chance_bau_dourado(e): sim.soltar_no_chao(Itens.novo("bau_dourado"), e.pos, jog.id, e.pos)
	_rolar_materiais_asa(sim, e, jog)
	if tab.is_empty(): return
	var muito_abaixo := jog.nivel - e.nivel >= 6
	# chefe de andar com curva própria: um item garantido, sorteado por raridade_pesos (vermelho só em 5%)
	if tab.has("raridade_pesos"):
		var rar := _sorteia_pesos(sim, tab["raridade_pesos"])
		var it_p := {}
		if rar == "lendario":
			for r in tab["rolagens"]:
				if str(r["tag"]).begins_with("lendario:"): it_p = item_da_tag(sim, str(r["tag"]), e.nivel, "comum", jog); break
		else:
			it_p = _equip_qualquer(sim, rar, e.nivel)
		it_p = _trocar_por_deus(sim, it_p)
		if not it_p.is_empty(): sim.soltar_no_chao(it_p, e.pos, jog.id, e.pos)
	for gid in tab.get("garantido", []):
		# item de missão vermelho só cai se alguma missão ativa precisa dele; lendario: só com a chance de vermelho
		if gid.begins_with("missao:"):
			var mi: String = gid.substr(7)
			if str(Defs.ITENS.get(mi, {}).get("raridade", "")) == "lendario" and not Missoes.precisa_item_qualquer(jog, mi): continue
		elif gid.begins_with("lendario:") and not _vermelho_sai(sim, tab): continue
		var it := _trocar_por_deus(sim, item_da_tag(sim, gid, e.nivel, "comum", jog))
		if not it.is_empty(): sim.soltar_no_chao(it, e.pos, jog.id, e.pos)
	var n := 0
	if tab.has("rolagens_garantidas"): n = int(tab["rolagens_garantidas"])
	elif sim.rng.randf() < float(tab.get("item_chance", 0.0)): n = 1
	var minima: String = tab.get("raridade_minima", "comum")
	jog.pity_raro += 1
	# mob comum: equipamento sai por chance absoluta de raridade (chance_mob_comum), de qualquer item equipavel
	if _mob_comum(e):
		var rar := Itens.rolar_raridade_mob(sim.rng, e.nivel)
		if rar != "":
			var eq := _equip_qualquer(sim, rar, e.nivel)
			if not eq.is_empty(): sim.soltar_no_chao(_trocar_por_deus(sim, eq), e.pos, jog.id, e.pos)
	var f_itens := float(Defs.DROPS["balanco"]["itens_de_mob"])   # balanço 18/10: cada rolagem de item tem 65% (drop mais baixo)
	var f_joias := float(Defs.DROPS["balanco"]["joias"])
	for i in n:
		if sim.rng.randf() >= f_itens: continue
		var r := _peso(sim, tab["rolagens"])
		var tag: String = r["tag"]
		if muito_abaixo and tag.begins_with("equip"): continue
		if _mob_comum(e) and tag.begins_with("equip"): continue   # o equipamento de mob comum vem da chance_mob_comum acima
		if tab.has("raridade_pesos") and tag.begins_with("equip"): continue   # chefe de andar: o equipamento vem de raridade_pesos
		if tag.begins_with("lendario:") and not _vermelho_sai(sim, tab): continue
		if tag.begins_with("joia:") and sim.rng.randf() >= f_joias: continue   # joias de refino pela metade
		var mn := minima
		if jog.pity_raro >= int(Defs.DROPS["pity"]["raro_garantido_apos_abates_sem_raro"]) and tag.begins_with("equip"): mn = "raro"
		var it := _trocar_por_deus(sim, item_da_tag(sim, tag, e.nivel, mn, jog))
		if it.is_empty(): continue
		if it.get("raridade", "comum") in ["raro", "excelente", "lendario"]: jog.pity_raro = 0
		sim.soltar_no_chao(it, e.pos, jog.id, e.pos)

## Vermelho sai quando a tabela é de raid (vermelho_garantido) ou pela chance de balanco.lendario_chance.
static func _vermelho_sai(sim: WorldSim, tab: Dictionary) -> bool:
	return bool(tab.get("vermelho_garantido", false)) or sim.rng.randf() < float(Defs.DROPS["balanco"].get("lendario_chance", 1.0))

## Sorteia uma chave de um dicionário de pesos (ex.: {"magico": 40, "lendario": 5}).
static func _sorteia_pesos(sim: WorldSim, pesos: Dictionary) -> String:
	var tot := 0.0
	for k in pesos: tot += float(pesos[k])
	var x := sim.rng.randf() * tot
	for k in pesos:
		x -= float(pesos[k])
		if x <= 0.0: return str(k)
	return str(pesos.keys()[0])

## Pool de equipamento base (qualquer item equipavel, sem variante Deus, sem vinculado), sorteado com peso_drop.
static func _equip_qualquer(sim: WorldSim, rar: String, nivel_mob: int) -> Dictionary:
	var ids := []
	for i in Defs.ITENS:
		var d: Dictionary = Defs.ITENS[i]
		var fixa := str(d.get("raridade", "rolada")) != "rolada"
		# raridade fixa (ex.: as espadas roxas) só cai no sorteio roxo e até o nível do mob
		if fixa and (rar != "excelente" or int(d.get("nivel", 1)) > nivel_mob): continue
		if str(d.get("slot", "")) == "" or d.has("variante_de"): continue
		if Itens.vinculado(Itens.novo(i)): continue
		ids.append(i)
	if ids.is_empty(): return {}
	var tot := 0.0
	for i in ids: tot += float(Defs.ITENS[i].get("peso_drop", 1.0))
	var x := sim.rng.randf() * tot
	var id: String = ids[ids.size() - 1]
	for i in ids:
		x -= float(Defs.ITENS[i].get("peso_drop", 1.0))
		if x <= 0.0: id = i; break
	if str(Defs.ITENS[id].get("raridade", "rolada")) != "rolada": return Itens.novo(id)
	return Itens.gerar_equip(id, sim.rng, "comum", Itens.faixa(nivel_mob, sim.rng), rar)

static func _mob_comum(e: Ent) -> bool:
	return e.tipo == "monstro" and e.arquetipo in ["rasteiro", "normal", "bruto", "atirador", "conjurador"]

## Chance base da curva das lágrimas (drops.json "lagrimas"): 0,08% no nível 1 -> 0,8% no 50, depois sobe devagar até o teto.
static func chance_lagrima(nivel: int) -> float:
	var c: Dictionary = Defs.DROPS["lagrimas"]["curva"]
	var a := float(c["nivel_1"]); var b := float(c["nivel_50"])
	var p := a + (b - a) * float(clampi(nivel, 1, 50) - 1) / 49.0
	if nivel > 50: p += float(c["por_nivel_acima_50"]) * float(nivel - 50)
	return minf(p, float(c["teto"]))

## Lágrima Angélica / Sanguínea: qualquer mob, rolagem própria por abate (estilo Bless/Soul do MU).
static func _rolar_lagrimas(sim: WorldSim, e: Ent, jog: Ent, tab_id) -> void:
	var L: Dictionary = Defs.DROPS.get("lagrimas", {})
	if L.is_empty(): return
	var m: Dictionary = L["multiplicadores"]
	var mult := 1.0
	if e.tipo == "chefe": mult *= float(m.get("chefe", 1.0))
	elif e.arquetipo == "elite" or e.arquetipo == "raro": mult *= float(m.get("elite", 1.0))
	if e.tipo == "monstro" and (str(e.aux.get("spot", "")) != "" or sim.spot_em(e.pos) != ""): mult *= float(m.get("spot_de_farm", 1.0))
	var base := chance_lagrima(e.nivel) * mult * float(Defs.DROPS["balanco"]["joias"])
	for id in L["itens"]:
		var p := base * float(L["itens"][id])
		if id == "lagrima_angelica" and str(tab_id) == "cripta_celestial": p *= float(m.get("angelica_de_celestial", 1.0))
		if Defs.ITENS.has(id) and sim.rng.randf() < p:
			sim.soltar_no_chao(Itens.novo(id), e.pos, jog.id, e.pos)

## Baú dourado (balanço 18/10): chance por abate. Mob comum 0,01%; elite, raro e chefe 5%; chefe de nível alto (Boss top) 30%.
static func chance_bau_dourado(e: Ent) -> float:
	var C: Dictionary = Defs.DROPS["balanco"]["bau_dourado"]
	if e.tipo == "chefe":
		return float(C["chefe_top"]) if e.nivel >= int(C["nivel_chefe_top"]) else float(C["elite_ou_chefe"])
	if e.arquetipo == "elite" or e.arquetipo == "raro": return float(C["elite_ou_chefe"])
	return float(C["mob_comum"])

## Abre o baú dourado pelo inventário: só equipamento, nunca abaixo do piso da regra (Excelente).
static func abrir_dourado(sim: WorldSim, jog: Ent) -> void:
	var regra: Dictionary = Defs.DROPS["baus"]["bau_dourado"]
	var rol: Array = regra["rolagens"]
	var n := sim.rng.randi_range(int(rol[0]), int(rol[1]))
	var f := 1 if jog.nivel < 7 else 2
	for i in n:
		var it := item_da_tag(sim, "equip:faixa%d" % f, jog.nivel, str(regra["raridade_minima"]), jog)
		if not it.is_empty(): sim.soltar_no_chao(it, jog.pos, jog.id, jog.pos)

## Materiais de asa (drops.json "materiais_asa"): pena de ave, pele de demônio, engrenagem; rolagem pessoal pela tag do mob.
## Chefes rolam também a asa pronta da tabela "asas_de_chefe".
static func _rolar_materiais_asa(sim: WorldSim, e: Ent, jog: Ent) -> void:
	var M: Dictionary = Defs.DROPS.get("materiais_asa", {})
	if not M.is_empty() and jog.nivel - e.nivel < 10:
		var mm: Dictionary = M.get("mult", {})
		var mult := 1.0
		if e.tipo == "chefe": mult *= float(mm.get("chefe", 1.0))
		elif e.arquetipo == "elite" or e.arquetipo == "raro": mult *= float(mm.get("elite", 1.0))
		if e.tipo == "monstro" and (str(e.aux.get("spot", "")) != "" or sim.spot_em(e.pos) != ""): mult *= float(mm.get("spot", 1.0))
		var tags: Array = e.tags if not e.tags.is_empty() else Defs.MOBS.get(e.kind, {}).get("tags", [])
		for id in M["itens"]:
			var p := 0.0
			var por_tag: Dictionary = M["itens"][id]["tags"]
			for t in tags:
				p = maxf(p, float(por_tag.get(t, 0.0)))
			if p > 0.0 and Defs.ITENS.has(id) and sim.rng.randf() < p * mult:
				sim.soltar_no_chao(Itens.novo(id), e.pos, jog.id, e.pos)
	if e.tipo == "chefe":
		for a in Defs.DROPS.get("asas_de_chefe", {}).get(e.kind, []):
			if Defs.ITENS.has(a["item"]) and sim.rng.randf() < float(a["chance"]):
				sim.soltar_no_chao(Itens.novo(a["item"]), e.pos, jog.id, e.pos)

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
	if sim.rng.randf() < float(regra.get("joia_refino_chance", 0.0)) * float(Defs.DROPS["balanco"]["joias"]):
		var jid := "lagrima_sanguinea" if sim.rng.randf() < float(regra.get("joia_sanguinea_fracao", 0.0)) else "lagrima_angelica"
		sim.soltar_no_chao(Itens.novo(jid), b.pos, jog.id, b.pos)
	_soltar_ouro(sim, int(sim.rng.randf_range(2.6 * nivel, 6.5 * nivel) * float(regra.get("ouro_mult", 1))), b.pos, jog)

class_name Missoes
## Missões e diálogos (design/missoes/dados). Segue as regras do README da thread de missões.

static func estado(jog: Ent, mid: String) -> String:
	var m: Dictionary = jog.missoes.get(mid, {})
	return m.get("estado", "nao_iniciada")

static func def(mid: String) -> Dictionary:
	return Defs.MISSOES.get(mid, {})

static func faccao_ok(jog: Ent, f) -> bool:
	return f == null or f == "ambas" or f == "" or f == "neutro" or f == jog.faccao

static func disponivel(jog: Ent, mid: String) -> bool:
	var d := def(mid)
	if d.is_empty() or not faccao_ok(jog, d.get("faccao")): return false
	var st := estado(jog, mid)
	if st == "concluida" and d.get("tipo") == "repetivel":
		st = "nao_iniciada" if int(jog.missoes[mid].get("dia", -1)) != int(jog.aux.get("dia", 0)) else st
	if st != "nao_iniciada": return false
	for r in d.get("requer", []):
		if estado(jog, r) != "concluida": return false
	var rq: Array = d.get("requer_qualquer", [])
	if rq.size() > 0 and not rq.any(func(r): return estado(jog, r) == "concluida"): return false
	if jog.nivel < int(d.get("nivel", 1)) - 2: return false
	return true

## Etapa atual: o menor número de etapa que ainda tem objetivo pendente.
static func _etapa_atual(jog: Ent, mid: String) -> int:
	var d := def(mid)
	var objs: Array = d["objetivos"]
	var menor := 999
	for i in objs.size():
		if not _obj_feito(jog, mid, i, ""): menor = mini(menor, int(objs[i].get("etapa", 1)))
	return menor

static func _obj_feito(jog: Ent, mid: String, i: int, npc_ignora: String) -> bool:
	var o: Dictionary = def(mid)["objetivos"][i]
	var prog: Array = jog.missoes.get(mid, {}).get("prog", [])
	match o["tipo"]:
		"coletar":
			return Itens.contar(jog.inv, o["item"]) >= int(o.get("qtd", 1))
		"falar", "decidir":
			if npc_ignora != "":
				var alvo = o.get("npc")
				if (alvo is Array and npc_ignora in alvo) or alvo == npc_ignora: return true
			return i < prog.size() and int(prog[i]) >= 1
	return i < prog.size() and int(prog[i]) >= int(o.get("qtd", 1))

static func progresso(jog: Ent, mid: String, i: int) -> Array:
	var o: Dictionary = def(mid)["objetivos"][i]
	var prog: Array = jog.missoes.get(mid, {}).get("prog", [])
	var tot := int(o.get("qtd", 1))
	if o["tipo"] == "coletar": return [mini(Itens.contar(jog.inv, o["item"]), tot), tot]
	return [mini(int(prog[i]) if i < prog.size() else 0, tot), tot]

static func pronta(jog: Ent, mid: String, npc: String = "") -> bool:
	if estado(jog, mid) != "ativa": return false
	var objs: Array = def(mid)["objetivos"]
	for i in objs.size():
		if not _obj_feito(jog, mid, i, npc): return false
	return true

static func precisa_item(jog: Ent, mid: String, item: String) -> bool:
	if estado(jog, mid) != "ativa": return false
	for o in def(mid)["objetivos"]:
		if o["tipo"] == "coletar" and o["item"] == item:
			return Itens.contar(jog.inv, item) < int(o.get("qtd", 1))
	return false

static func aceitar(sim: WorldSim, jog: Ent, mid: String) -> void:
	var d := def(mid)
	if d.is_empty(): return
	var prog := []
	prog.resize(d["objetivos"].size()); prog.fill(0)
	jog.missoes[mid] = {"estado": "ativa", "prog": prog}
	for it in d.get("ao_aceitar_recebe", []):
		Jogador.dar_item(sim, jog, Itens.novo(it["id"], int(it.get("qtd", 1))))
	for f in d.get("falha_ao_aceitar", []):
		if estado(jog, f) == "ativa": jog.missoes[f]["estado"] = "falhou"
	sim.emitir_a(jog, "missao", {"id": mid, "estado": "aceita", "titulo": d["titulo"]})
	# objetivos já cumpridos (explorar a zona em que já está, itens já na mochila)
	evento(sim, jog, "explorar", jog.zona)
	_checar_auto(sim, jog, mid)

static func concluir(sim: WorldSim, jog: Ent, mid: String, escolha: String = "") -> void:
	var d := def(mid)
	if estado(jog, mid) != "ativa": return
	for o in d["objetivos"]:
		if o["tipo"] == "coletar": Itens.remover(jog.inv, o["item"], int(o.get("qtd", 1)))
	var rec: Dictionary = d.get("recompensas", {}).duplicate(true)
	for e in d.get("escolhas", []):
		if e["id"] == escolha:
			rec = e.get("recompensas", {})
			for f in e.get("flags", []): jog.flags[f] = true
	jog.missoes[mid]["estado"] = "concluida"
	jog.missoes[mid]["dia"] = int(jog.aux.get("dia", 0))
	jog.missoes[mid]["escolha"] = escolha
	sim.emitir_a(jog, "missao", {"id": mid, "estado": "concluida", "titulo": d["titulo"], "texto": d.get("texto_conclusao", "")})
	if rec.has("ouro") and int(rec["ouro"]) > 0:
		jog.ouro += int(rec["ouro"]); sim.emitir_a(jog, "ouro", {"valor": int(rec["ouro"])})
	for it in rec.get("itens", []):
		Jogador.dar_item(sim, jog, Itens.novo(it["id"], int(it.get("qtd", 1))))
	var epc: Dictionary = rec.get("escolha_por_classe", {})
	if epc.has(jog.classe): Jogador.dar_item(sim, jog, Itens.novo(epc[jog.classe]))
	if rec.has("xp"): Jogador.ganhar_xp(sim, jog, int(rec["xp"]), "missão")
	var prox = d.get("ao_concluir_inicia")
	if prox != null and prox != "" and disponivel(jog, prox): aceitar(sim, jog, prox)
	sim.emitir_a(jog, "inventario", {})

## Conta progresso: tipo = matar|interagir|usar_item|explorar|falar|decidir|coletar ; chave = id do alvo/objeto/zona.
static func evento(sim: WorldSim, jog: Ent, tipo: String, chave: String, extra: String = "") -> void:
	for mid in jog.missoes.keys():
		if estado(jog, mid) != "ativa": continue
		var objs: Array = def(mid)["objetivos"]
		var etapa := _etapa_atual(jog, mid)
		var mudou := false
		var txt := ""
		for i in objs.size():
			var o: Dictionary = objs[i]
			if o["tipo"] != tipo or int(o.get("etapa", 1)) > etapa: continue
			var ok := false
			match tipo:
				"matar": ok = o["alvo"] == chave
				"interagir": ok = o["objeto"] == chave
				"usar_item": ok = o["objeto"] == chave and o["item"] == extra
				"explorar": ok = o["subzona"] == chave
				"farmar_spot": ok = spot_real(sim, str(o.get("spot", ""))) == chave
				"falar", "decidir":
					var n = o.get("npc")
					ok = (n is Array and chave in n) or n == chave
			if not ok: continue
			var prog: Array = jog.missoes[mid]["prog"]
			if int(prog[i]) < int(o.get("qtd", 1)):
				prog[i] = int(prog[i]) + 1; mudou = true
				txt = texto_objetivo(o) + ((" %d/%d" % [int(prog[i]), int(o.get("qtd", 1))]) if int(o.get("qtd", 1)) > 1 else " ✓")
				if o.has("concede"):
					var cc = o["concede"]
					for c in (cc if cc is Array else [cc]):
						if c is Dictionary: Jogador.dar_item(sim, jog, Itens.novo(c["id"], int(c.get("qtd", 1))))
						else: Jogador.dar_item(sim, jog, Itens.novo(str(c)))
		if mudou:
			if pronta(jog, mid) and str(def(mid).get("entrega")) != "automatico":
				txt = "%s: volte a %s" % [def(mid)["titulo"], nome_entrega(mid)]
			sim.emitir_a(jog, "missao", {"id": mid, "estado": "progresso", "titulo": def(mid)["titulo"], "texto": txt})
			_checar_auto(sim, jog, mid)

static func checar_coleta(sim: WorldSim, jog: Ent) -> void:
	for mid in jog.missoes.keys():
		if estado(jog, mid) == "ativa": _checar_auto(sim, jog, mid)

static func _checar_auto(sim: WorldSim, jog: Ent, mid: String) -> void:
	var d := def(mid)
	if str(d.get("entrega")) == "automatico" and pronta(jog, mid):
		concluir(sim, jog, mid)

## Quem tem algo para o jogador: "!" missão nova, "?" pronta para entregar.
static func marcador_npc(jog: Ent, npc: String) -> String:
	var tem_nova := false
	for m in Defs.MISSOES_LISTA:
		if m.get("oculta", false): continue
		var en = m.get("entrega")
		if ((en is Array and npc in en) or (en is String and en == npc)) and pronta(jog, m["id"], npc): return "?"
		if m.get("doador") == npc and disponivel(jog, m["id"]): tem_nova = true
	return "!" if tem_nova else ""

# =================================================================== diálogos
static func cond(jog: Ent, se: Dictionary, npc: String) -> bool:
	for k in se:
		var v = se[k]
		var lista: Array = v if v is Array else [v]
		var ok := false
		match k:
			"missao_disponivel": ok = lista.any(func(m): return disponivel(jog, m))
			"missao_ativa": ok = lista.any(func(m): return estado(jog, m) == "ativa")
			"missao_pronta": ok = lista.any(func(m): return pronta(jog, m, npc))
			"missao_concluida": ok = lista.any(func(m): return estado(jog, m) == "concluida")
			"missao_nao_iniciada": ok = lista.any(func(m): return estado(jog, m) == "nao_iniciada")
			"faccao": ok = jog.faccao in lista
			"flag": ok = lista.any(func(f): return jog.flags.has(f))
			"sem_flag": ok = not lista.any(func(f): return jog.flags.has(f))
			"tem_item":
				ok = lista.any(func(t):
					if t is Dictionary: return Itens.contar(jog.inv, t["id"]) >= int(t.get("qtd", 1))
					return Itens.contar(jog.inv, str(t)) >= 1)
			_: ok = true
		if not ok: return false
	return true

static func abrir(sim: WorldSim, jog: Ent, npc: Ent) -> void:
	var dn: Dictionary = Defs.NPCS.get(npc.kind, {})
	if not faccao_ok(jog, dn.get("faccao")):
		var frase := "A Vigília não fala com quem carrega a trombeta." if dn.get("faccao") == "vigilia" else "Os Arautos não abrem a boca para quem ainda reza pela cerca."
		sim.emitir("fala", {"id": npc.id, "texto": frase})
		return
	var dlg: Dictionary = Defs.DIALOGOS.get(dn.get("dialogo", ""), {})
	if dlg.is_empty(): return
	jog.aux["dialogo"] = {"npc": npc.id, "dlg": dlg["id"], "no": dlg["inicio"]}
	mostrar(sim, jog)

static func mostrar(sim: WorldSim, jog: Ent) -> void:
	var st: Dictionary = jog.aux.get("dialogo", {})
	if st.is_empty(): return
	var npc: Ent = sim.ents.get(st["npc"])
	var dlg: Dictionary = Defs.DIALOGOS[st["dlg"]]
	var no: Dictionary = dlg["nos"].get(st["no"], {})
	var fala = no.get("fala", "")
	var texto := ""
	if fala is Array:
		for f in fala:
			if not f.has("se") or cond(jog, f["se"], npc.kind):
				texto = f["texto"]; break
	else: texto = str(fala)
	var ops: Array = []
	var vis: Array = []
	var lista: Array = no.get("opcoes", [])
	for i in lista.size():
		var o: Dictionary = lista[i]
		if o.has("se") and not cond(jog, o["se"], npc.kind): continue
		vis.append(i)
		var tipo := ""
		for a in o.get("acoes", []):
			if a.has("aceitar_missao"): tipo = "aceitar"
			elif a.has("concluir_missao"): tipo = "concluir"
			elif a.has("abrir_loja") or a.has("abrir_ferreiro") or a.has("abrir_armazem") or a.has("abrir_treinador"): tipo = "servico"
		if o.has("se") and (o["se"].has("missao_disponivel") or o["se"].has("missao_pronta")) and tipo == "":
			tipo = "missao"
		ops.append({"texto": o["texto"], "tipo": tipo})
	st["vis"] = vis
	sim.emitir_a(jog, "dialogo", {"npc": npc.id, "nome": npc.nome, "titulo": npc.aux.get("titulo", ""), "texto": texto, "opcoes": ops, "visual": npc.aux.get("visual", "humano")})

static func escolher(sim: WorldSim, jog: Ent, idx: int) -> void:
	var st: Dictionary = jog.aux.get("dialogo", {})
	if st.is_empty() or idx < 0 or idx >= st.get("vis", []).size(): return
	var npc: Ent = sim.ents.get(st["npc"])
	var dlg: Dictionary = Defs.DIALOGOS[st["dlg"]]
	var o: Dictionary = dlg["nos"][st["no"]]["opcoes"][st["vis"][idx]]
	var fecha := not o.has("ir")
	if not fecha: st["no"] = o["ir"]
	var servico := {}
	for a in o.get("acoes", []):
		if a.has("aceitar_missao"): aceitar(sim, jog, a["aceitar_missao"])
		if a.has("cumprir_falar"): evento(sim, jog, "falar", npc.kind)
		if a.has("concluir_missao"):
			var mid: String = a["concluir_missao"]
			evento(sim, jog, "falar", npc.kind)
			if a.has("escolha"): evento(sim, jog, "decidir", npc.kind)
			if pronta(jog, mid, npc.kind) or pronta(jog, mid): concluir(sim, jog, mid, a.get("escolha", ""))
		if a.has("falhar_missao") and estado(jog, a["falhar_missao"]) == "ativa": jog.missoes[a["falhar_missao"]]["estado"] = "falhou"
		if a.has("dar_item"): Jogador.dar_item(sim, jog, Itens.novo(a["dar_item"]["id"], int(a["dar_item"].get("qtd", 1))))
		if a.has("remover_item"): Itens.remover(jog.inv, a["remover_item"]["id"], int(a["remover_item"].get("qtd", 1))); sim.emitir_a(jog, "inventario", {})
		if a.has("definir_flag"): jog.flags[a["definir_flag"]] = true
		if a.has("abrir_loja"): servico = {"tipo": "loja", "id": a["abrir_loja"]}
		if a.has("abrir_ferreiro"): servico = {"tipo": "ferreiro", "id": a["abrir_ferreiro"]}
		if a.has("abrir_armazem"): servico = {"tipo": "armazem"}
		if a.has("abrir_treinador"): servico = {"tipo": "treinador", "id": a["abrir_treinador"]}
	if fecha or not servico.is_empty():
		jog.aux.erase("dialogo")
		sim.emitir_a(jog, "dialogo_fim", {})
	else:
		mostrar(sim, jog)
	if not servico.is_empty():
		jog.aux["servico"] = servico.merged({"npc": npc.id})
		Jogador.abrir_servico(sim, jog, servico, npc)

## Spot de farm que vale para um id pedido pelas missões: spots que ainda não existem no mapa
## (acampamento_desertores, marco_do_corte) usam o spot existente mais perto (spot_alias do mapa).
static func spot_real(sim: WorldSim, id: String) -> String:
	if sim != null:
		var al: Dictionary = sim.mapa.get("spot_alias", {})
		if al.has(id): return al[id]
	return {"acampamento_desertores": "margem_das_viuvas", "marco_do_corte": "covas_rasas"}.get(id, id)

## Texto de um objetivo para o rastreador e o diário.
static func texto_objetivo(o: Dictionary) -> String:
	var q := int(o.get("qtd", 1))
	match o["tipo"]:
		"matar":
			var nm: String = Defs.MON_TXT.get(o["alvo"], {}).get("nome", Defs.MOBS.get(o["alvo"], {}).get("nome", o["alvo"]))
			return "Mate %s" % nm if q <= 1 else "Mate %d × %s" % [q, nm]
		"coletar": return "Consiga %s" % Defs.ITENS.get(o["item"], {}).get("nome", o["item"])
		"interagir":
			var nm2: String = Defs.OBJETOS.get(o.get("objeto", ""), {}).get("nome", Defs.BAUS_HIST.get(o.get("objeto", ""), {}).get("nome", str(o.get("objeto", "")).replace("_", " ")))
			return "Examine %s" % nm2
		"falar":
			var n = o.get("npc")
			if n is Array: n = n[0]
			return "Fale com %s" % Defs.NPCS.get(n, {}).get("nome", str(n))
		"decidir":
			var n2 = o.get("npc")
			if n2 is Array: n2 = n2[0]
			return "Decida com %s" % Defs.NPCS.get(n2, {}).get("nome", str(n2))
		"usar_item":
			return "Use %s em %s" % [Defs.ITENS.get(o["item"], {}).get("nome", o["item"]), Defs.OBJETOS.get(o.get("objeto", ""), {}).get("nome", str(o.get("objeto", "")).replace("_", " "))]
		"explorar": return "Chegue a %s" % Defs.nome_local(o.get("subzona", ""))
		"farmar_spot":
			var sid := spot_real(null, str(o.get("spot", "")))
			var nm3: String = Defs.SPOTS.get(sid, {}).get("nome", sid.replace("_", " "))
			return "Cace %d monstros em %s" % [q, nm3]
	return o["tipo"]

static func nome_entrega(mid: String) -> String:
	var en = def(mid).get("entrega", "")
	if en is Array: en = en[0] if en.size() > 0 else ""
	return Defs.NPCS.get(str(en), {}).get("nome", "quem pediu")

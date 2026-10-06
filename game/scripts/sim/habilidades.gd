class_name Habilidades
## Efeito de cada habilidade das 6 classes (números de design/combate/classes_base.json).

static func _op(e: Ent, h: Dictionary, extra: Dictionary = {}) -> Dictionary:
	var op := {"mult": float(h.get("mult", 1.0)), "postura": float(h.get("postura", 10)), "sensacao": h.get("sensacao", "golpe_pesado"),
		"magico": Defs.CLASSES[e.classe]["perfil_dano"] == "magico", "skill": h["id"]}
	if h.has("elemento"): op["elemento"] = h["elemento"]
	if h.has("bonus_vs"): op["bonus_vs"] = h["bonus_vs"]
	if h.has("efeito"): op["efeito"] = h["efeito"]
	if h.has("critico_extra"): op["crit_extra"] = h["critico_extra"]
	if h.has("empurrao"): op["empurrao"] = float(h["empurrao"]) * 22.0
	op.merge(extra, true)
	return op

static func cura_valor(e: Ent, mult: float) -> float:
	var esp: float = e.aux.get("ef", e.stats)["ESP"]
	var v := (esp / 3.0 + e.nivel * 2.0) * mult
	if "pena_zacarias" in e.aux.get("bonus", {}).get("efeitos", []): v *= 1.12
	return v

static func usar(sim: WorldSim, e: Ent, h: Dictionary, alvo: Ent, ponto: Vector2) -> void:
	var id: String = h["id"]
	var conj := float(h.get("conjuracao", 0.0))
	var prep := maxf(conj, 0.18)
	var aid := alvo.id if alvo != null else -1
	var vfx := e.classe + "/" + id
	match id:
		# ---------------------------------------------------------- golpes em alvo
		"lamina_veredito", "golpe_purulento":
			sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "alvo": aid, "skill": id, "impacto": func():
				var a := sim.valido(aid)
				if a != null and e.pos.distance_to(a.pos) - a.raio <= float(h["alcance"]) + 0.8:
					sim.aplicar_golpe(e, a, _op(e, h))
					sim.emitir("vfx", {"skill": vfx, "alvo": aid, "de": e.id})
			})
		"tiro_certeiro":
			sim.iniciar_acao(e, {"preparo": conj, "rec": 0.25, "alvo": aid, "skill": id, "conj": true, "impacto": func():
				sim.lancar(e, {"vel": 20.0, "alvo": aid, "vfx": "tiro_certeiro"}, _op(e, h))
				sim.emitir("vfx", {"skill": vfx, "de": e.id, "alvo": aid})
			})
		"sangria":
			sim.iniciar_acao(e, {"preparo": prep, "rec": 0.25, "alvo": aid, "skill": id, "impacto": func():
				sim.lancar(e, {"vel": float(h.get("projetil_vel", 10)), "alvo": aid, "vfx": "sangria"}, _op(e, h))
			})
		"corrente_danacao":
			sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "alvo": aid, "skill": id, "impacto": func():
				sim.lancar(e, {"vel": 16.0, "alvo": aid, "vfx": "corrente"}, _op(e, h, {"puxa_para": float(h["puxa_para"])}))
				sim.emitir("vfx", {"skill": vfx, "de": e.id, "alvo": aid})
			})
		"garra_abismo":
			sim.iniciar_acao(e, {"preparo": 0.12, "rec": 0.45, "alvo": aid, "skill": id, "impacto": func():
				sim.emitir("vfx", {"skill": vfx, "alvo": aid, "de": e.id})
				for i in int(h["golpes"]):
					var ult: bool = i == int(h["golpes"]) - 1
					var op := _op(e, h, {"mult": float(h["mult_por_golpe"]), "postura": float(h["postura_por_golpe"]), "sensacao": "golpe_pesado" if ult else "combo"})
					if i == 0:
						var a := sim.valido(aid)
						if a != null: sim.aplicar_golpe(e, a, op)
					else:
						sim.atrasar(float(h["intervalo_golpes"]) * i, func():
							var a2 := sim.valido(aid)
							if a2 != null and e.vivo and e.pos.distance_to(a2.pos) < 2.5: sim.aplicar_golpe(e, a2, op))
			})
		"arco_voltaico":
			sim.iniciar_acao(e, {"preparo": prep, "rec": 0.25, "alvo": aid, "skill": id, "impacto": func():
				var atual := sim.valido(aid)
				var ja := []
				var mult := float(h["mult"])
				var de := e.pos
				for s in int(h["saltos"]) + 1:
					if atual == null: break
					ja.append(atual.id)
					sim.emitir("raio", {"de": de, "para": atual.pos, "cor": "#9fd8ff"})
					sim.aplicar_golpe(e, atual, _op(e, h, {"mult": mult, "sensacao": "raio"}))
					de = atual.pos
					mult *= 1.0 - float(h["queda_por_salto"])
					var prox: Ent = null
					for o in sim.inimigos_de(e, de, float(h["raio_salto"])):
						if not o.id in ja and (prox == null or o.pos.distance_to(de) < prox.pos.distance_to(de)): prox = o
					atual = prox
			})
		"sentenca", "profecia_sombria":
			sim.iniciar_acao(e, {"preparo": prep, "rec": 0.25, "alvo": aid, "skill": id, "impacto": func():
				var a := sim.valido(aid)
				if a == null: return
				for s in h["efeito"]: sim.aplicar_status(a, s, h["efeito"][s], e)
				sim.emitir("vfx", {"skill": vfx, "alvo": aid, "de": e.id, "fica": float(h["efeito"].values()[0])})
			})
		"passo_sombrio":
			var a := alvo
			var atras := a.pos - (e.pos - a.pos).normalized() * (a.raio + 0.6)
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "de": e.id})
			e.pos = sim.celula_livre_perto(atras, 1.5)
			e.facing = (a.pos - e.pos).normalized()
			e.aux["prox_critico"] = true
			sim.emitir("teleporte", {"id": e.id, "pos": e.pos})
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "de": e.id})
		# ---------------------------------------------------------- cura e suporte
		"toque_graca":
			var a2: Ent = alvo if alvo != null else e
			var a2id := a2.id
			sim.iniciar_acao(e, {"preparo": conj, "rec": 0.25, "alvo": a2id, "skill": id, "conj": true, "impacto": func():
				var a := sim.valido(a2id)
				if a != null:
					sim.curar(a, cura_valor(e, float(h["cura_mult"])), e)
					sim.emitir("vfx", {"skill": vfx, "alvo": a2id, "de": e.id})
			})
		"nanoreparo":
			var a3: Ent = alvo if alvo != null else e
			var a3id := a3.id
			sim.emitir("vfx", {"skill": vfx, "alvo": a3id, "de": e.id, "fica": float(h["ticks"]) * float(h["intervalo_tick"])})
			sim.criar_area({"pos": a3.pos, "raio": 0.0, "dur": float(h["ticks"]) * float(h["intervalo_tick"]) + 0.05, "tick": float(h["intervalo_tick"]), "tipo": "hot",
				"cada_tick": func(_a):
					var a := sim.valido(a3id)
					if a != null: sim.curar(a, cura_valor(e, float(h["cura_mult_por_tick"])), e)})
		"campo_forca":
			var esp: float = e.aux.get("ef", e.stats)["ESP"]
			var v := esp * 1.5 + e.nivel * 8.0
			for a in sim.aliados_de(e, e.pos, float(h["area_raio"])):
				a.escudo = v; a.escudo_t = float(h["duracao"])
				sim.emitir("escudo", {"id": a.id, "valor": v, "t": float(h["duracao"])})
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "de": e.id})
		"pacto_rubro", "carapaca", "pele_enxofre", "agua_benta_polvora":
			var bf: Dictionary = h["buff"]
			var mods := {}
			for k in bf:
				if k in ["dano_magico", "dano_recebido"]: mods[k] = float(bf[k])
				if k == "reflete_frac": mods["reflete"] = float(bf[k])
				if k == "dano_extra_elemental": mods["dano"] = float(bf[k])
			Jogador.add_buff(sim, e, id, float(bf["duracao"]), mods)
			if bf.get("imune_derrubar", false): e.aux["imune_cc"] = true
			if id == "agua_benta_polvora": e.aux["municao_especial"] = "sagrado"
			sim.emitir("vfx", {"skill": vfx, "alvo": e.id, "de": e.id, "fica": float(bf["duracao"])})
			sim.atrasar(float(bf["duracao"]), func(): e.aux.erase("imune_cc"); e.aux.erase("municao_especial"))
		# ---------------------------------------------------------- skills em área do nível 5 (farm_auto.json; usadas pelo modo automático)
		"anjo_leque_juizo", "demonio_ceifa_infernal", "mutante_terremoto_putrido", "tecnomancer_tempestade_bobina", "cultista_espinhos_sangue", "humano_coquetel_querosene":
			var forma: String = h.get("forma", "circulo_em_volta")
			var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
			if alvo != null and forma == "cone" and ponto.distance_to(e.pos) <= 0.3: dir = (alvo.pos - e.pos).normalized()
			var centro := e.pos
			if forma == "circulo_no_mouse":
				centro = ponto if ponto.distance_to(e.pos) > 0.3 else (alvo.pos if alvo != null else e.pos + e.facing * 2.0)
				if centro.distance_to(e.pos) > float(h.get("alcance", 7)): centro = e.pos + (centro - e.pos).normalized() * float(h.get("alcance", 7))
			if forma == "cone": e.facing = dir
			sim.iniciar_acao(e, {"preparo": float(h.get("preparo", 0.25)), "rec": 0.25, "dir": dir, "ponto": centro, "skill": id,
				"anim": "attack" if forma == "cone" else ("spin" if forma == "circulo_em_volta" else "attack"), "impacto": func():
				area_nivel5(sim, e, h, forma, centro, dir)
			})
		# ---------------------------------------------------------- áreas
		"halo_ardente", "pulso_anti_divino", "rugido_praga":
			sim.iniciar_acao(e, {"preparo": 0.25, "rec": 0.3, "skill": id, "impacto": func():
				sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "de": e.id})
				for a in sim.inimigos_de(e, e.pos, float(h["area_raio"])):
					if h.has("mult"): sim.aplicar_golpe(e, a, _op(e, h, {"area": true, "empurrao": 8.0, "empurrao_de": e.pos}))
					elif h.has("efeito"):
						for s in h["efeito"]: sim.aplicar_status(a, s, h["efeito"][s], e)
						sim.aplicar_postura(a, float(h.get("postura", 0)), e)
					if id == "rugido_praga":
						var mx := 100.0
						for v in a.ameaca.values(): mx = maxf(mx, v)
						a.ameaca[e.id] = a.ameaca.get(e.id, 0.0) + mx
						if a.estado in ["ocioso", "vagar"]: IA.acordar(sim, a, e)
				if h.has("cura_mult"):
					for a in sim.aliados_de(e, e.pos, float(h["area_raio"])): sim.curar(a, cura_valor(e, float(h["cura_mult"])), e)
			})
		"chuva_cinzas":
			var p := ponto
			sim.iniciar_acao(e, {"preparo": 0.3, "rec": 0.2, "ponto": p, "skill": id, "impacto": func():
				sim.emitir("vfx", {"skill": vfx, "pos": p, "de": e.id, "fica": float(h["ticks"]) * float(h["intervalo_tick"])})
				sim.criar_area({"pos": p, "raio": float(h["area_raio"]), "dur": float(h["ticks"]) * float(h["intervalo_tick"]), "tick": float(h["intervalo_tick"]),
					"dono": e.id, "tipo": "cinzas", "op": _op(e, h, {"mult": float(h["mult_por_tick"]), "area": true, "sensacao": "projetil",
						"efeito": {"cura_reduzida": float(h["efeito"]["duracao"])}})})
			})
		"rajada":
			var dir := (ponto - e.pos).normalized() if ponto != e.pos else e.facing
			sim.iniciar_acao(e, {"preparo": 0.2, "rec": 0.3, "dir": dir, "ponto": e.pos + dir, "skill": id, "impacto": func():
				var n := int(h["projeteis"])
				var cone := deg_to_rad(float(h["cone_graus"]))
				sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "dir": dir, "de": e.id})
				for i in n:
					var a := dir.angle() - cone * 0.5 + cone * (float(i) / maxf(n - 1, 1))
					sim.lancar(e, {"vel": 18.0, "dir": Vector2.from_angle(a), "alcance": float(h["alcance"]), "vfx": "bala"},
						_op(e, h, {"mult": float(h["mult_por_projetil"]), "postura": float(h["postura_por_projetil"]), "area": true, "sensacao": "projetil"}))
			})
		"armadilha_prata":
			var p2 := ponto
			sim.criar_area({"pos": p2, "raio": 1.0, "dur": float(h["dura_s"]), "arma_s": float(h["arma_s"]), "dono": e.id, "tipo": "armadilha",
				"op": _op(e, h, {"area": true})})
			sim.emitir("vfx", {"skill": vfx, "pos": p2, "de": e.id, "fica": float(h["dura_s"])})
		"corte_largo":
			sim.iniciar_acao(e, {"preparo": 0.12, "rec": 0.33, "skill": id, "anim": "spin", "impacto": func():
				sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "de": e.id})
				for o in sim.inimigos_de(e, e.pos, float(h["area_raio"]) + 0.3):
					sim.aplicar_golpe(e, o, _op(e, h, {"area": true, "empurrao_de": e.pos}))
			})
		"arrancada":
			var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
			e.invuln_t = float(h.get("invulneravel", 0.2))
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "dir": dir, "de": e.id})
			e.aux["bonus_prox"] = float(h["proximo_ataque_extra"]); e.aux["bonus_prox_t"] = float(h["janela_bonus_s"])
			sim.deslocar(e, e.pos + dir * float(h["deslocamento"]), float(h["duracao_s"]) + 0.1, {"tipo": id, "anim": "dash",
				"golpeia": _op(e, h, {"area": true, "empurrao": float(h.get("empurrao_lateral", 0.5)) * 22.0})})
		# ---------------------------------------------------------- mobilidade
		"asas_ascensao", "rolamento":
			var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
			e.invuln_t = float(h.get("invulneravel", 0.3))
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "dir": dir, "de": e.id})
			sim.deslocar(e, e.pos + dir * float(h["deslocamento"]), 0.32 if id == "rolamento" else 0.4, {"atravessa": h.get("atravessa", false), "tipo": id})
		"investida_bestial":
			var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
			if alvo != null: dir = (alvo.pos - e.pos).normalized()
			sim.emitir("vfx", {"skill": vfx, "pos": e.pos, "dir": dir, "de": e.id})
			sim.deslocar(e, e.pos + dir * float(h["deslocamento"]), 0.35, {"tipo": id,
				"golpeia": _op(e, h, {"area": true, "empurrao_de": e.pos})})
		# ---------------------------------------------------------- invocações
		"servo_carne", "torreta_sentinela":
			var tipo_inv: String = h["invoca"]
			for o in sim.ents.values():
				if o.tipo == "invocacao" and o.dono == e.id and o.kind == tipo_inv: sim.matar(o, null)
			var d: Dictionary = Defs.CLASSES[e.classe]["invocacoes"][tipo_inv]
			var inv := Ent.new()
			inv.id = sim.novo_id(); inv.tipo = "invocacao"; inv.kind = tipo_inv; inv.dono = e.id
			inv.nome = "Servo de Carne" if tipo_inv == "servo_de_carne" else "Torreta Sentinela"
			inv.pos = sim.celula_livre_perto(e.pos + e.facing * 1.2)
			inv.casa = inv.pos
			inv.hp_max = e.hp_max * (0.6 if tipo_inv == "servo_de_carne" else 0.5); inv.hp = inv.hp_max
			var m := 0.5 if tipo_inv == "servo_de_carne" else 0.45
			inv.dano_min = e.dano_min * m; inv.dano_max = e.dano_max * m
			inv.intervalo = float(d["intervalo"]); inv.alcance = float(d.get("alcance", 1.3))
			inv.vel = 2.8 if tipo_inv == "servo_de_carne" else 0.0
			inv.nivel = e.nivel; inv.ar = e.ar; inv.er = e.er; inv.critico = 0.05; inv.crit_mult = 1.5
			inv.defesa = e.defesa; inv.tags = d.get("tags", []).duplicate()
			inv.aux["ameaca_mult"] = float(d.get("ameaca_mult", 1.0))
			inv.elemento = "sangue" if tipo_inv == "servo_de_carne" else "eletrico"
			inv.dura_t = float(h["duracao"])
			inv.raio = 0.45
			sim.ents[inv.id] = inv
			sim.emitir("surgiu", {"id": inv.id})
			sim.emitir("vfx", {"skill": vfx, "pos": inv.pos, "de": e.id})


## Alvos e golpe das skills em área do nível 5. Só o primeiro alvo gera recurso (formulas.json: recurso_em_area).
static func alvos_area5(sim: WorldSim, e: Ent, h: Dictionary, forma: String, centro: Vector2, dir: Vector2) -> Array:
	var raio := float(h.get("raio", 2.5))
	var out: Array = []
	if forma == "cone":
		var meio := deg_to_rad(float(h.get("cone_graus", 90))) * 0.5
		for o in sim.inimigos_de(e, e.pos, raio + 0.4):
			var v: Vector2 = o.pos - e.pos
			if v.length() < 0.6 or absf(dir.angle_to(v)) <= meio + 0.1: out.append(o)
	else:
		out = sim.inimigos_de(e, centro, raio + 0.3)
	out.sort_custom(func(a, b): return a.pos.distance_squared_to(centro) < b.pos.distance_squared_to(centro))
	return out

static func area_nivel5(sim: WorldSim, e: Ent, h: Dictionary, forma: String, centro: Vector2, dir: Vector2) -> void:
	var id: String = h["id"]
	var vfx_pos := centro if forma != "cone" else e.pos + dir * float(h.get("raio", 3.0)) * 0.45
	sim.emitir("vfx", {"skill": e.classe + "/" + id, "pos": vfx_pos, "dir": dir, "de": e.id})
	var efeito := {}
	for k in ["queimadura", "sangramento", "veneno"]:
		if h.has(k): efeito[k] = h[k]
	var primeiro := true
	e.aux["area5_t"] = sim.tempo
	for a in alvos_area5(sim, e, h, forma, centro, dir):
		var op := _op(e, h, {"area": true, "nunca_erra": true, "empurrao": float(h.get("empurrao_px", 6)), "empurrao_de": e.pos if forma != "circulo_no_mouse" else centro})
		if not efeito.is_empty(): op["efeito"] = efeito
		if not primeiro: op["sem_recurso"] = true
		primeiro = false
		sim.aplicar_golpe(e, a, op)
		if h.has("chance_atordoar") and a.vivo and sim.rng.randf() < float(h["chance_atordoar"]):
			sim.aplicar_status(a, "atordoado", float(h.get("atordoar_s", 0.5)), e)
	if h.has("chao_em_chamas_s"):
		var pc := centro if forma != "cone" else e.pos + dir * float(h.get("raio", 3.0)) * 0.55
		sim.criar_area({"pos": pc, "raio": float(h.get("raio", 2.0)) * (0.8 if forma != "cone" else 0.6), "dur": float(h["chao_em_chamas_s"]), "tick": 0.5,
			"dono": e.id, "tipo": "fogo", "op": _op(e, h, {"mult": 0.12, "area": true, "nunca_erra": true, "sensacao": "dano_tempo", "postura": 0.0, "sem_recurso": true})})

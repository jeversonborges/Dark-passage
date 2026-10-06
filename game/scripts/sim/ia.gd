class_name IA
## Máquina de estados dos monstros (design/combate/mobs.json: ia_estados) e das invocações do jogador.

static func _alvo_valido(sim: WorldSim, e: Ent, o: Ent) -> bool:
	if o == null or not o.vivo or not o.alvejavel or o.invisivel: return false
	if o.tipo == "jogador":
		if o.imune_t > 0.0: return false
		if sim.zona_segura(o.pos): return false
		if e.kind == "nao_julgado" and o.buffs.any(func(b): return b["id"] == "repele_nao_julgado"): return false
	return e.eh_inimigo_de(o)

static func acordar(sim: WorldSim, e: Ent, por: Ent) -> void:
	if e.tipo != "monstro" or not e.vivo: return
	if e.estado == "voltar": return
	if por != null:
		var quem := por
		e.ameaca[quem.id] = e.ameaca.get(quem.id, 0.0) + 1.0
	if e.estado in ["ocioso", "vagar"]:
		e.estado = "alerta"; e.ia_t = 0.4
		e.invisivel = false
		e.aux["combate_t"] = 0.0
		sim.emitir("alerta", {"id": e.id})
		var social := minf(float(e.ia.get("aggro_social", 4)), 3.0 if e.aux.get("neutro", false) else 5.0)
		for o in sim.ents.values():
			if o != e and o.tipo == "monstro" and o.kind == e.kind and o.vivo and o.estado in ["ocioso", "vagar"] and o.pos.distance_to(e.pos) <= social \
				and (o.spawn_ref == e.spawn_ref or not e.aux.get("neutro", false)):
				if por != null: o.ameaca[por.id] = 0.5
				o.estado = "alerta"; o.ia_t = 0.4 + sim.rng.randf() * 0.3
				sim.emitir("alerta", {"id": o.id})

static func _alvo_maior_ameaca(sim: WorldSim, e: Ent) -> Ent:
	if e.tem("provocado"):
		var p := sim.valido(e.alvo)
		if p != null: return p
	var melhor: Ent = null
	var mv := -1.0
	for id in e.ameaca.keys():
		var o: Ent = sim.ents.get(id)
		if not _alvo_valido(sim, e, o):
			e.ameaca.erase(id); continue
		if e.pos.distance_to(o.pos) > e.raio_coleira + 6.0: continue
		if e.ameaca[id] > mv: mv = e.ameaca[id]; melhor = o
	var atual := sim.valido(e.alvo)
	if atual != null and melhor != null and atual != melhor and _alvo_valido(sim, e, atual):
		var lim := 1.3 if e.alcance > 2.0 else 1.1
		if e.ameaca.get(melhor.id, 0.0) < e.ameaca.get(atual.id, 0.0) * lim: return atual
	return melhor

static func passo(sim: WorldSim, e: Ent, dt: float) -> void:
	if not e.pronto(): return
	e.ia_t -= dt
	match e.estado:
		"ocioso", "vagar": _ocioso(sim, e, dt)
		"alerta":
			var a := _alvo_maior_ameaca(sim, e)
			if a != null: e.facing = (a.pos - e.pos).normalized() if a.pos != e.pos else e.facing
			if e.ia_t <= 0.0:
				e.estado = "combate" if a != null else "voltar"
				if e.estado == "voltar": _voltar(sim, e)
		"combate": _combate(sim, e, dt)
		"voltar":
			if not sim.mover_ao_longo(e, dt, 1.5):
				if e.pos.distance_to(e.casa) > 1.0: sim.ir_para(e, e.casa, _voa(e))
				else:
					e.estado = "ocioso"; e.aux.erase("imune"); e.hp = e.hp_max; e.postura = e.postura_max
					e.ameaca.clear(); e.alvo = -1
					sim.emitir("dano", {"id": e.id, "valor": 0, "estilo": "nada", "hp": e.hp, "hp_max": e.hp_max})
					if e.ia.get("padrao", "") == "emboscada": e.invisivel = true; sim.emitir("some", {"id": e.id})
		"fugir":
			if not sim.mover_ao_longo(e, dt, 1.1) or e.ia_t <= 0.0:
				e.estado = "combate"
	if e.estado != "ocioso" and e.estado != "vagar": _separar(sim, e, dt)

static func _voa(e: Ent) -> bool:
	return "voador" in e.tags

static func _ocioso(sim: WorldSim, e: Ent, dt: float) -> void:
	# procura alvo a cada ~0.25 s (neutros não procuram: só reagem quando apanham)
	if e.ia_t <= 0.0 and not e.aux.get("neutro", false):
		e.ia_t = 0.25
		for o: Ent in sim.alvos_ia:
			if _alvo_valido(sim, e, o) and e.pos.distance_to(o.pos) <= e.raio_aggro and sim.visao(e.pos, o.pos):
				acordar(sim, e, o)
				return
	elif e.ia_t <= 0.0 and e.aux.has("territorio"):
		# territorial: neutro que também ataca quem entra no território do grupo (toca da matilha, árvore das viúvas)
		e.ia_t = 0.3
		var t: Array = e.aux["territorio"]
		var c := Vector2(float(t[0]), float(t[1]))
		for o: Ent in sim.alvos_ia:
			if o.pos.distance_to(c) <= float(t[2]) and _alvo_valido(sim, e, o) and sim.visao(e.pos, o.pos):
				acordar(sim, e, o)
				return
	# patrulha ou vagar
	var pat: Array = e.aux.get("patrulha", [])
	if pat.size() > 0:
		if not sim.mover_ao_longo(e, dt, 0.6):
			var i := (int(e.aux.get("pat_i", 0)) + 1) % pat.size()
			e.aux["pat_i"] = i
			sim.ir_para(e, Vector2(pat[i][0], pat[i][1]))
		return
	if sim.mover_ao_longo(e, dt, 0.45): return
	e.aux["vagar_t"] = e.aux.get("vagar_t", sim.rng.randf_range(2, 5)) - dt
	if e.aux["vagar_t"] <= 0.0:
		e.aux["vagar_t"] = sim.rng.randf_range(2.0, 5.0)
		var p := e.casa + Vector2(sim.rng.randf_range(-1, 1), sim.rng.randf_range(-1, 1)) * e.raio_vagar
		if sim.andavel(p) and not sim.zona_segura(p): sim.ir_para(e, p, _voa(e))

static func _voltar(sim: WorldSim, e: Ent) -> void:
	e.estado = "voltar"; e.aux["imune"] = true
	sim.cancelar_acao(e)
	e.alvo = -1
	sim.ir_para(e, e.casa, _voa(e))
	sim.emitir("voltar", {"id": e.id})

static func _ataque_def(e: Ent, id: String) -> Dictionary:
	for a in Defs.MOBS.get(e.kind, {}).get("ataques", []):
		if a["id"] == id: return a
	return {}

static func alcance_ataque(e: Ent, a: Dictionary) -> float:
	if a.has("teleporte"): return 12.0
	if a.has("salto"): return float(a["salto"]) + 0.5
	if a.has("telegrafo"):
		var t: Dictionary = a["telegrafo"]
		match t["forma"]:
			"linha": return float(t["comprimento"]) * 0.85
			"cone": return float(t["raio"]) * 0.8
			"circulo": return float(t["raio"]) * 0.8 if a["id"] != "brotar" else 8.0
			"anel": return float(t["raio_final"]) * 0.7
	if a.has("projetil_vel") or a.has("projeteis"): return e.alcance
	if a.has("invoca") or a.has("buff") or a.has("cura_frac_hp_alvo"): return 99.0
	return e.alcance

static func _combate(sim: WorldSim, e: Ent, dt: float) -> void:
	var a := _alvo_maior_ameaca(sim, e)
	e.aux["combate_t"] = e.aux.get("combate_t", 0.0) + dt
	if a == null or e.pos.distance_to(e.casa) > e.raio_coleira or sim.zona_segura(e.pos):
		_voltar(sim, e); return
	e.alvo = a.id
	var m: Dictionary = Defs.MOBS.get(e.kind, {})
	var ataques: Array = m.get("ataques", [])
	var d := e.pos.distance_to(a.pos) - a.raio
	# fuga com pouca vida (matilha)
	if e.ia.has("foge_abaixo_de") and e.frac_hp() < float(e.ia["foge_abaixo_de"]) and not e.aux.get("fugiu", false):
		e.aux["fugiu"] = true; e.estado = "fugir"; e.ia_t = 3.0
		var longe := e.pos + (e.pos - a.pos).normalized() * 6.0
		sim.ir_para(e, sim.celula_livre_perto(longe))
		sim.emitir("som_evento", {"ev": "uivo", "pos": e.pos, "id": e.id})
		for o in sim.ents.values():
			if o.tipo == "monstro" and o.kind == e.kind and o.vivo and o.pos.distance_to(e.pos) <= 8.0 and o.estado in ["ocioso", "vagar"]:
				acordar(sim, o, a)
		return
	# efeitos periódicos (poça de cera do Fogo-de-Vela)
	for at in ataques:
		if at.has("a_cada_s"):
			e.aux["periodico_t"] = e.aux.get("periodico_t", float(at["a_cada_s"])) - dt
			if e.aux["periodico_t"] <= 0.0:
				e.aux["periodico_t"] = float(at["a_cada_s"])
				var ar: Dictionary = at["area"]
				sim.criar_area({"pos": e.pos, "raio": float(ar["raio"]), "dur": float(ar["duracao"]), "tick": 0.5, "dono": e.id, "tipo": "cera",
					"op": {"mult": 0.25, "area": true, "efeito": at.get("efeito", {}), "elemento": "fogo", "postura": 0}})
				var p := a.pos + Vector2(sim.rng.randf_range(-3, 3), sim.rng.randf_range(-3, 3))
				if sim.andavel(p):
					e.pos = p; sim.emitir("teleporte", {"id": e.id, "pos": p})
	# escolhe um especial pronto
	for at in ataques.slice(1):
		if at.get("ao_morrer", false) or at.has("a_cada_s") or at.has("a_cada"): continue
		if e.cds.has(at["id"]): continue
		if at.has("em_hp"):
			if e.frac_hp() > float(at["em_hp"]) or e.aux.get("usou_" + at["id"], false): continue
		if at.get("so_primeiro", false) and e.aux.get("usou_" + at["id"], false): continue
		if at.has("gatilho") and d > 3.0: continue
		if at.has("cura_frac_hp_alvo"):
			var ferido := _aliado_ferido(sim, e)
			if ferido == null: continue
			usar_ataque(sim, e, at, ferido); return
		if at.has("conjuracao") and at.has("invoca") and _aliados_perto(sim, e) > 0: continue
		if d <= alcance_ataque(e, at) and (d > 1.5 or not at.has("teleporte")):
			if at.has("telegrafo") or at.has("projetil_vel") or at.has("teleporte") or at.has("salto"):
				if not sim.visao(e.pos, a.pos) and not _voa(e): continue
			usar_ataque(sim, e, at, a); return
	# básico (ou o "a cada N golpes")
	var basico: Dictionary = ataques[0] if ataques.size() > 0 else {"id": "golpe", "mult": 1.0, "preparo": 0.5}
	for at in ataques:
		if at.has("a_cada") and (e.golpes + 1) % int(at["a_cada"]) == 0: basico = at
	var alc := e.alcance
	var ranged := alc > 2.0
	# reposicionar (atirador/conjurador)
	if ranged and e.ia.has("distancia_minima") and d < float(e.ia["distancia_minima"]) and e.aux.get("repos_cd", 0.0) <= 0.0:
		e.aux["repos_cd"] = 4.0
		var longe := e.pos + (e.pos - a.pos).normalized() * (float(e.ia.get("distancia_ideal", 5)) - d)
		longe = sim.celula_livre_perto(longe)
		if e.kind == "filho_de_cardo":
			_enterrar(sim, e, longe); return
		sim.ir_para(e, longe, _voa(e))
	e.aux["repos_cd"] = e.aux.get("repos_cd", 0.0) - dt
	if not e.caminho.is_empty() and e.aux.get("repos_cd", 0.0) > 3.0:
		sim.mover_ao_longo(e, dt); return
	if d <= alc and (not ranged or sim.visao(e.pos, a.pos)):
		e.caminho.clear()
		e.aux["combate_t"] = 0.0
		if e.cd_basico <= 0.0:
			usar_ataque(sim, e, basico, a)
		elif e.ia.get("padrao", "") == "enxame":
			_circular(sim, e, a, dt)
		else:
			e.facing = (a.pos - e.pos).normalized() if a.pos != e.pos else e.facing
		return
	# persegue (8 s sem conseguir atacar: desiste)
	if e.aux["combate_t"] > 8.0 and not e.ia.get("padrao", "") == "teimoso":
		_voltar(sim, e); return
	var destino := a.pos
	if e.ia.get("padrao", "") in ["matilha", "enxame"]:
		var ang := float(e.id % 7) / 7.0 * TAU
		destino = a.pos + Vector2.from_angle(ang) * minf(alc, 1.0)
	if ranged: destino = a.pos + (e.pos - a.pos).normalized() * minf(float(e.ia.get("distancia_ideal", alc * 0.8)), alc * 0.9)
	e.aux["repath"] = e.aux.get("repath", 0.0) - dt
	if e.caminho.is_empty() or e.aux["repath"] <= 0.0:
		e.aux["repath"] = 0.5
		sim.ir_para(e, destino, _voa(e))
	sim.mover_ao_longo(e, dt)

## Filho de Cardo: some na terra e brota em outro ponto (anim burrow/emerge; invisível no meio).
static func _enterrar(sim: WorldSim, e: Ent, para: Vector2) -> void:
	e.caminho.clear()
	e.cd_basico = 2.2
	sim.iniciar_acao(e, {"preparo": 1.6, "rec": 0.0, "nome": "enterrar", "anim": "burrow"})
	sim.atrasar(0.75, func():
		if not e.vivo: return
		e.invisivel = true; e.alvejavel = false)
	sim.atrasar(1.0, func():
		if not e.vivo: return
		e.pos = para
		sim.emitir("teleporte", {"id": e.id, "pos": para, "sem_fx": true})
		sim.emitir("anim", {"id": e.id, "anim": "emerge", "dur": 0.6}))
	sim.atrasar(1.3, func():
		e.invisivel = false; e.alvejavel = true)

static func _circular(sim: WorldSim, e: Ent, a: Ent, dt: float) -> void:
	var rel := e.pos - a.pos
	var ang := rel.angle() + dt * 1.6
	var p := a.pos + Vector2.from_angle(ang) * 2.0
	e.caminho = [p]
	sim.mover_ao_longo(e, dt, 0.8)

static func _aliado_ferido(sim: WorldSim, e: Ent) -> Ent:
	for o in sim.ents.values():
		if o.tipo == "monstro" and o.vivo and o != e and o.frac_hp() < 0.5 and o.pos.distance_to(e.pos) < 7.0: return o
	return null

static func _aliados_perto(sim: WorldSim, e: Ent) -> int:
	var n := 0
	for o in sim.ents.values():
		if o.tipo == "monstro" and o.vivo and o != e and o.pos.distance_to(e.pos) < 7.0: n += 1
	return n

## Executa um ataque de mob (básico ou especial) contra o alvo.
static func usar_ataque(sim: WorldSim, e: Ent, at: Dictionary, a: Ent) -> void:
	var id: String = at["id"]
	e.cd_basico = e.intervalo
	if at.has("recarga"): e.cds[id] = float(at["recarga"])
	if at.has("em_hp") or at.get("so_primeiro", false): e.aux["usou_" + id] = true
	e.golpes += 1
	var prep := float(at.get("preparo", at.get("conjuracao", 0.5)))
	var rec := float(at.get("recuperacao", 0.35))
	var op := {"mult": float(at.get("mult", 1.0)), "sensacao": "golpe_pesado" if float(at.get("mult", 1.0)) >= 1.5 else "golpe_leve",
		"postura": 0.0, "ataque": id}
	if at.has("efeito"): op["efeito"] = at["efeito"]
	if at.has("empurrao_px"): op["empurrao"] = float(at["empurrao_px"])
	if at.has("telegrafo"): op["area"] = true
	var aid := a.id
	var dir := (a.pos - e.pos).normalized() if a.pos != e.pos else e.facing
	var acao := {"preparo": prep, "rec": rec, "alvo": aid, "def": at, "op": op, "dir": dir, "nome": id}
	if at.has("conjuracao") and not at.has("preparo"): acao["conj"] = true
	if at.has("telegrafo") and at["telegrafo"]["forma"] == "circulo":
		acao["ponto_tele"] = a.pos if id in ["brotar"] else e.pos
	# especiais
	if at.has("teleporte"):
		var p := sim.celula_livre_perto(a.pos + Vector2.from_angle(sim.rng.randf() * TAU) * float(at["teleporte"]))
		sim.emitir("teleporte", {"id": e.id, "pos": p, "de": e.pos})
		e.pos = p
		return
	if at.has("buff"):
		var b: Dictionary = at["buff"]
		e.buffs.append({"id": id, "t": float(b.get("duracao", 4)), "mods": {"dano_recebido": float(b.get("dano_recebido", 0)), "postura_regen": 1.0}})
		sim.emitir("fala", {"id": e.id, "texto": "…", "cor": "#c99a3e"})
		sim.iniciar_acao(e, {"preparo": 0.6, "rec": 0.2, "nome": id, "conj": true})
		return
	if at.has("cura_frac_hp_alvo"):
		acao["conj"] = true
		acao["preparo"] = float(at.get("conjuracao", 1.2))
		acao["impacto"] = func():
			var al := sim.valido(aid)
			if al != null: sim.curar(al, al.hp_max * float(at["cura_frac_hp_alvo"]), e)
		sim.iniciar_acao(e, acao)
		return
	if at.has("invoca"):
		acao["conj"] = at.has("conjuracao")
		acao["preparo"] = float(at.get("conjuracao", 0.8))
		acao["impacto"] = func():
			for k in at["invoca"]:
				for i in int(at["invoca"][k]):
					var m := sim.criar_mob(k, sim.celula_livre_perto(e.pos + Vector2.from_angle(sim.rng.randf() * TAU) * 1.5), e.nivel)
					m.renasce_s = 0
					m.casa = e.casa; m.raio_coleira = e.raio_coleira
					var al := sim.valido(aid)
					if al != null: acordar(sim, m, al)
			sim.emitir("fala", {"id": e.id, "texto": "Venham!" if e.kind == "capataz_gancho" else "…", "cor": "#c8302a"})
		sim.iniciar_acao(e, acao)
		return
	var ranged := e.alcance > 2.0 and not at.has("telegrafo")
	acao["impacto"] = func():
		var al := sim.valido(aid)
		if at.has("salto") and al != null:
			sim.deslocar(e, al.pos - (al.pos - e.pos).normalized() * 0.8, 0.25, {"tipo": "salto"})
			sim.atrasar(0.25, func():
				var a3 := sim.valido(aid)
				if a3 != null and e.vivo and e.pos.distance_to(a3.pos) < 1.8: sim.aplicar_golpe(e, a3, op))
			return
		if at.has("telegrafo"):
			var t: Dictionary = at["telegrafo"]
			if t["forma"] == "linha" and (id in ["investida", "arrasto"]):
				sim.deslocar(e, e.pos + dir * float(t["comprimento"]), 0.35, {"tipo": "investida", "ao_fim": func():
					if not sim.andavel(e.pos + dir * 0.8) and e.tipo == "monstro":
						e.quebrado_t = 1.5; sim.emitir("dano", {"id": e.id, "valor": 0, "estilo": "postura_quebrada"})})
			return  # o dano sai pelo telegrafo
		if al == null: return
		if ranged or at.has("projetil_vel"):
			var n := int(at.get("projeteis", 1))
			var cone := deg_to_rad(float(at.get("cone_graus", 0)))
			for i in n:
				var ang := dir.angle() + (0.0 if n == 1 else -cone * 0.5 + cone * float(i) / (n - 1))
				if n == 1: sim.lancar(e, {"vel": float(at.get("projetil_vel", 9)), "alvo": aid, "vfx": "mob_" + e.kind}, op)
				else: sim.lancar(e, {"vel": float(at.get("projetil_vel", 9)), "dir": Vector2.from_angle(ang), "alcance": e.alcance + 1.0, "vfx": "mob_" + e.kind}, op)
		elif e.pos.distance_to(al.pos) - al.raio <= e.alcance + 0.6:
			sim.aplicar_golpe(e, al, op)
		else:
			sim.emitir("dano", {"id": al.id, "de": e.id, "valor": 0, "estilo": "esquivou"})
		if at.get("morre_ao_usar", false): sim.matar(e, null)
	if at.has("telegrafo"):
		if at.get("puxa", false): op["puxa_para"] = 1.2
		if at.get("morre_ao_usar", false): op["ao_impacto"] = func(_tg): sim.matar(e, null)
		acao["op"] = op
	sim.iniciar_acao(e, acao)

static func explosao_morte(sim: WorldSim, e: Ent, at: Dictionary) -> void:
	var t: Dictionary = at.get("telegrafo", {"forma": "circulo", "raio": 1.5})
	var p := e.pos
	var tid := sim.novo_id()
	var r := float(t.get("raio", 1.5))
	sim.emitir("telegrafo", {"id": tid, "forma": "circulo", "origem": p, "dir": Vector2.RIGHT, "p": t, "dur": float(at.get("preparo", 1.0)), "segue": -1, "dono": e.id})
	var fantasma := Ent.new()
	fantasma.id = -1; fantasma.tipo = "monstro"; fantasma.nivel = e.nivel; fantasma.dano_min = e.dano_min; fantasma.dano_max = e.dano_max
	fantasma.ar = e.ar; fantasma.critico = 0.0; fantasma.crit_mult = 1.5
	sim.atrasar(float(at.get("preparo", 1.0)), func():
		sim.emitir("telegrafo_fim", {"id": tid, "impacto": true})
		sim.emitir("vfx", {"nome": "chefe_onda_choque", "pos": p})
		for o in sim.ents.values():
			if o.vivo and o.tipo in ["jogador", "invocacao"] and o.pos.distance_to(p) <= r + o.raio:
				sim.aplicar_golpe(fantasma, o, {"mult": float(at.get("mult", 1.0)), "area": true, "efeito": at.get("efeito", {}), "elemento": "veneno", "sensacao": "area"}))

static func _separar(sim: WorldSim, e: Ent, dt: float) -> void:
	if _voa(e): return
	for o: Ent in sim.ents.values():
		if o == e or not o.vivo or o.tipo not in ["monstro", "jogador"] : continue
		var d := e.pos - o.pos
		var l := d.length()
		var minimo := (e.raio + o.raio) * 0.9
		if l < minimo and l > 0.001:
			var np := e.pos + d / l * minf(minimo - l, 2.0 * dt)
			if sim.andavel(np): e.pos = np

# =================================================================== invocações do jogador
static func passo_invocacao(sim: WorldSim, e: Ent, dt: float) -> void:
	if not e.pronto(): return
	var dono: Ent = sim.ents.get(e.dono)
	if dono == null or not dono.vivo:
		sim.matar(e, null); return
	var alvo := sim.valido(e.alvo)
	if alvo == null or not alvo.alvejavel or alvo.pos.distance_to(dono.pos) > 10.0:
		alvo = sim.valido(dono.alvo)
		if alvo == null:
			var melhor: Ent = null
			for o in sim.inimigos_de(e, e.pos, 6.0):
				if o.tipo != "objeto" and (melhor == null or o.pos.distance_to(e.pos) < melhor.pos.distance_to(e.pos)): melhor = o
			alvo = melhor
		e.alvo = alvo.id if alvo != null else -1
	if alvo == null:
		if e.vel > 0.0 and e.pos.distance_to(dono.pos) > 2.5:
			if e.caminho.is_empty(): sim.ir_para(e, dono.pos)
			sim.mover_ao_longo(e, dt)
		return
	var d := e.pos.distance_to(alvo.pos) - alvo.raio
	if d <= e.alcance:
		e.caminho.clear()
		if e.cd_basico <= 0.0:
			e.cd_basico = e.intervalo
			var aid := alvo.id
			sim.iniciar_acao(e, {"preparo": 0.25, "rec": 0.2, "alvo": aid, "impacto": func():
				var a := sim.valido(aid)
				if a == null: return
				if e.alcance > 2.0: sim.lancar(e, {"vel": 16.0, "alvo": aid, "vfx": "torreta"}, {"mult": 1.0, "elemento": e.elemento, "nunca_erra": true})
				else: sim.aplicar_golpe(e, a, {"mult": 1.0, "nunca_erra": true})
			})
	elif e.vel > 0.0:
		if e.caminho.is_empty(): sim.ir_para(e, alvo.pos)
		sim.mover_ao_longo(e, dt)

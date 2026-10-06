class_name ChefeCtl
extends RefCounted
## Luta de chefe: arena, porta, fases, telegrafos e as mecânicas de cada um (design/combate/chefes.json).

var sim: WorldSim
var cfg: Dictionary
var d: Dictionary
var boss: Ent
var estado := "dormindo"     # dormindo | luta | transicao | morto
var fase := 1
var luta_t := 0.0
var trans_t := 0.0
var centro := Vector2.ZERO
var raio_arena := 8.0
var pilhas: Array = []       # ids
var coristas: Array = []
var luzes: Array = []        # fase 3 da Celeste: [pos]
var luzes_t := 0.0
var coro_t := 0.0
var onda_t := 0.0
var onda_ang := 0.0
var nota_t := 0.0
var encolhe_t := 0.0
var raio_fogo := 99.0
var esp := {}                # memória livre

func _init(p_sim: WorldSim, c: Dictionary) -> void:
	sim = p_sim; cfg = c
	d = Defs.CHEFES[c["id"]]
	centro = Vector2(c["arena"]["centro"][0], c["arena"]["centro"][1])
	raio_arena = float(c["arena"]["raio"])
	if c.get("derrotado", false):
		estado = "morto"; return
	_criar_chefe()

func _criar_chefe() -> void:
	var e := Ent.new()
	e.id = sim.novo_id(); e.tipo = "chefe"; e.kind = cfg["id"]; e.nome = d["nome"]
	e.pos = Vector2(cfg["pos"][0], cfg["pos"][1]); e.casa = e.pos
	e.nivel = int(d["nivel"]); e.hp_max = float(d["hp"]); e.hp = e.hp_max
	e.defesa = float(d["defesa"]); e.dano_min = float(d["dano_base"]) * 0.9; e.dano_max = float(d["dano_base"]) * 1.1
	e.intervalo = float(d["intervalo_ataque"]); e.vel = float(d["velocidade_mov"])
	e.postura_max = float(d["postura_max"]); e.postura = e.postura_max
	e.res = d.get("res", {}).duplicate(); e.tags = d.get("tags", []).duplicate()
	e.ar = e.nivel * 4.0 + 20.0; e.er = e.nivel * 3.0 + 5.0; e.critico = 0.05; e.crit_mult = 1.5
	e.arquetipo = "chefe"; e.raio = 0.9; e.escala = 1.0
	e.alcance = 1.8
	e.facing = (centro - e.pos).normalized() if centro != e.pos else Vector2(-1, 0)
	boss = e
	sim.ents[e.id] = e
	sim.emitir("surgiu", {"id": e.id})
	# objetos da arena
	for p in cfg.get("pilhas", []): pilhas.append(_objeto_arena("pilha_de_mortos", "Pilha de Mortos", Vector2(p[0], p[1]), 160.0, {"fogo": -1.0, "sagrado": -1.0}))
	for p in cfg.get("coristas", []):
		var c := _objeto_arena("corista", "Corista de Osso", Vector2(p[0], p[1]), 220.0, {})
		sim.ents[c].alvejavel = false; sim.ents[c].defesa = 10.0
		coristas.append(c)

func _objeto_arena(kind: String, nome: String, p: Vector2, hp: float, res: Dictionary) -> int:
	var o := Ent.new()
	o.id = sim.novo_id(); o.tipo = "objeto"; o.kind = kind; o.nome = nome; o.pos = p; o.casa = p
	o.hp_max = hp; o.hp = hp; o.res = res; o.alvejavel = true; o.raio = 0.6; o.nivel = int(d["nivel"])
	o.er = 1.0; o.tags = ["objeto"]
	sim.ents[o.id] = o
	sim.emitir("surgiu", {"id": o.id})
	return o.id

func porta_fechada() -> bool:
	return estado in ["luta", "transicao"]

## O alvo do chefe: na arena, vivo, com mais ameaça (no solo, o jogador; null se ninguém está na luta).
func _jog() -> Ent:
	var melhor: Ent = null
	var ma := -1.0
	for e: Ent in sim.jogadores():
		if not e.vivo or e.pos.distance_to(centro) > raio_arena + 3.0: continue
		var a := float(boss.ameaca.get(e.id, 0.0)) if boss != null else 0.0
		if a > ma: ma = a; melhor = e
	return melhor

# =================================================================== fases e ataques
func _ataques_fase(n: int) -> Array:
	var base := {}
	var lista: Array = []
	for f in d["fases"]:
		for a in f["ataques"]:
			if not base.has(a["id"]): base[a["id"]] = a.duplicate(true)
			else:
				var m: Dictionary = base[a["id"]].duplicate(true)
				m.merge(a, true); base[a["id"]] = m
		if int(f["n"]) == n:
			for a in f["ataques"]:
				var m2: Dictionary = base[a["id"]].duplicate(true)
				m2.merge(a, true)
				lista.append(m2)
			break
	return lista

func _fase_def() -> Dictionary:
	return d["fases"][fase - 1]

func passo(dt: float) -> void:
	var j := _jog()
	if estado == "morto" or boss == null: return
	if estado == "dormindo":
		if j != null and j.vivo and j.pos.distance_to(centro) < raio_arena - 0.5:
			_comecar()
		return
	if j == null or not j.vivo or j.pos.distance_to(centro) > raio_arena + 3.0:
		_resetar(); return
	luta_t += dt
	if luta_t > float(d["furia_tempo_s"]) and not boss.aux.has("enrage"):
		boss.aux["enrage"] = true; boss.vel *= 1.3
		sim.emitir("chefe_fala", {"id": boss.id, "texto": "FÚRIA!"}); sim.emitir("vfx", {"nome": "chefe_furia", "alvo": boss.id})
	if estado == "transicao":
		trans_t -= dt
		if trans_t <= 0.0:
			estado = "luta"; boss.aux.erase("imune")
		return
	# troca de fase pelo HP
	var f := boss.frac_hp()
	if fase < d["fases"].size() and f <= float(d["fases"][fase]["hp"][0]) + 0.0001:
		_nova_fase(fase + 1); return
	_mecanicas(dt, j)
	if not boss.vivo: return
	if boss.quebrado_t > 0.0 or boss.tem("exausto"): return
	if not boss.acao.is_empty() or not boss.deslocando.is_empty(): return
	if esp.has("comendo") or esp.has("canalizando") or esp.has("levitando"): return
	_decidir(dt, j)

func _comecar() -> void:
	estado = "luta"; luta_t = 0.0; fase = 1
	sim.definir_bloqueio(cfg.get("porta", []), 2)
	sim.emitir("chefe", {"id": boss.id, "nome": d["nome"], "fase": 1, "marcas": d["fases"].map(func(x): return x["hp"][0]), "inicio": true})
	sim.emitir("porta", {"fechada": true, "celulas": cfg.get("porta", [])})
	sim.emitir("chefe_fala", {"id": boss.id, "texto": d.get("fala_entrada", "")})
	boss.ameaca[_jog().id] = 1.0
	boss.cd_basico = 1.0
	esp["devorar_t"] = 20.0

func _resetar() -> void:
	for id in sim.ents.keys():
		var o: Ent = sim.ents[id]
		if o.tipo == "monstro" and o.renasce_s == 0 and o.pos.distance_to(centro) < raio_arena + 6: sim.remover(id)
	for t in sim.telegrafos.duplicate(): sim.remover_telegrafo(t["id"])
	sim.cancelar_acao(boss)
	boss.hp = boss.hp_max; boss.postura = boss.postura_max; boss.pos = boss.casa; boss.status.clear(); boss.buffs.clear()
	boss.aux.erase("enrage"); boss.aux.erase("imune"); boss.aux.erase("agarrando"); boss.escala = 1.0
	boss.vel = float(d["velocidade_mov"])
	esp.clear(); fase = 1; estado = "dormindo"; luzes.clear(); raio_fogo = 99.0
	# arena volta ao normal (pilhas e coristas inteiras)
	for id in pilhas + coristas: sim.remover(id)
	pilhas.clear(); coristas.clear()
	for p in cfg.get("pilhas", []): pilhas.append(_objeto_arena("pilha_de_mortos", "Pilha de Mortos", Vector2(p[0], p[1]), 160.0, {"fogo": -1.0, "sagrado": -1.0}))
	for p in cfg.get("coristas", []):
		var c := _objeto_arena("corista", "Corista de Osso", Vector2(p[0], p[1]), 220.0, {})
		sim.ents[c].alvejavel = false
		coristas.append(c)
	sim.definir_bloqueio(cfg.get("porta", []), 0)
	sim.emitir("porta", {"fechada": false, "celulas": cfg.get("porta", [])})
	sim.emitir("chefe", {"id": boss.id, "fim": true, "reset": true})
	sim.emitir("teleporte", {"id": boss.id, "pos": boss.pos})

func jogador_morreu() -> void:
	# em grupo a luta continua enquanto alguém estiver de pé na arena
	if estado in ["luta", "transicao"] and _jog() == null: sim.atrasar(1.0, _resetar)

func _nova_fase(n: int) -> void:
	fase = n
	estado = "transicao"; trans_t = 1.5
	boss.aux["imune"] = true
	sim.cancelar_acao(boss)
	for t in sim.telegrafos.duplicate():
		if t["dono"] == boss.id: sim.remover_telegrafo(t["id"])
	var fd := _fase_def()
	sim.emitir("chefe", {"id": boss.id, "fase": n, "nome_fase": fd.get("nome", "")})
	sim.emitir("chefe_fala", {"id": boss.id, "texto": fd.get("fala", "")})
	sim.emitir("som_evento", {"ev": "chefe_fase", "chefe": boss.kind})
	match boss.kind:
		"irma_celeste":
			if n == 2: _coro_comecar()
			if n == 3: _apagar_velas()
		"zacarias_arauto":
			if n == 2: nota_t = 2.0
			if n == 3: encolhe_t = 25.0; raio_fogo = raio_arena; nota_t = 45.0; esp["querubim_t"] = 5.0
		"general_partido":
			if n == 3: boss.vel_ataque = 1.25; boss.intervalo /= 1.25

func ao_quebrar(interrompeu: bool) -> void:
	if esp.has("comendo"):
		esp.erase("comendo")
		sim.aplicar_status(boss, "exausto", 4.0, null)
		sim.emitir("canal_fim", {"id": boss.id, "ok": false})
		sim.emitir("chefe_fala", {"id": boss.id, "texto": "Grrh... minha comida..."})
	if esp.has("canalizando"):
		esp.erase("canalizando")
		boss.postura_max = float(d["postura_max"])
		sim.aplicar_status(boss, "exausto", 4.0, null)
		sim.emitir("canal_fim", {"id": boss.id, "ok": false})
		sim.emitir("som_evento", {"ev": "zacarias_nota_interrompida"})
		sim.emitir("chefe_fala", {"id": boss.id, "texto": "NÃO! A nota... a nota!"})
	if boss.aux.get("agarrando", false): _soltar_agarrado()

func ao_morrer_ent(e: Ent, killer: Ent) -> void:
	if e == boss:
		estado = "morto"
		sim.definir_bloqueio(cfg.get("porta", []), 0)
		sim.emitir("porta", {"fechada": false, "celulas": cfg.get("porta", [])})
		sim.emitir("chefe", {"id": boss.id, "fim": true, "morto": true})
		sim.emitir("chefe_fala", {"id": boss.id, "texto": d.get("morte", "")})
		for id in sim.ents.keys():
			var o: Ent = sim.ents[id]
			if o.tipo == "monstro" and o.renasce_s == 0 and o.pos.distance_to(centro) < raio_arena + 6: sim.matar(o, null)
		for id in coristas: sim.remover(id)
		for t in sim.telegrafos.duplicate(): sim.remover_telegrafo(t["id"])
		sim.areas = sim.areas.filter(func(a): return a.get("dono", -1) != boss.id)
		if killer != null:
			killer.flags["venceu_" + boss.kind] = true
			for j: Ent in sim.jogadores():
				if j.pos.distance_to(centro) < raio_arena + 6.0: j.flags["venceu_" + boss.kind] = true
			sim.emitir("chefe_derrotado", {"id": boss.kind})
		return
	if e.id in pilhas:
		pilhas.erase(e.id)
		sim.emitir("aviso", {"texto": "Pilha de Mortos destruída: menos comida para o General."})
	if e.id in coristas:
		sim.aplicar_status(e, "exausto", 999, null)
		e.vivo = true; e.hp = e.hp_max; e.alvejavel = false
		e.aux["morta"] = true
		sim.emitir("corista", {"id": e.id, "canta": false, "morta": true})
		if esp.has("regencia") and esp["regencia"] == e.id:
			esp.erase("regencia")
			sim.emitir("aviso", {"texto": "A corista calou antes do fim do canto."})
		if estado == "luta" and fase == 2 and esp.has("coro"):
			coro_t -= 4.0
	if e.kind == "soldado_caido":
		# vira cadáver fresco que o General pode comer
		var c := _objeto_arena("cadaver_fresco", "Cadáver Fresco", e.pos, 1.0, {})
		sim.ents[c].alvejavel = false
		esp["cadaveres"] = esp.get("cadaveres", []) + [c]
		sim.atrasar(10.0, func():
			esp["cadaveres"] = esp.get("cadaveres", []).filter(func(x): return x != c)
			sim.remover(c))

# =================================================================== decisão (movimento + ataques)
func _decidir(dt: float, j: Ent) -> void:
	var lista := _ataques_fase(fase)
	var dist := boss.pos.distance_to(j.pos) - j.raio
	boss.alvo = j.id
	for a in lista.slice(1):
		var id: String = a["id"]
		if boss.cds.has(id) or _passivo(id): continue
		if a.has("gatilho"): continue
		if a.get("uma_vez", false) and esp.has("usou_" + id): continue
		if not _no_alcance(a, dist): continue
		_usar(a, j); return
	var basico: Dictionary = lista[0]
	var alc := float(basico.get("alcance", 1.8))
	if dist <= alc:
		boss.caminho.clear()
		if boss.cd_basico <= 0.0: _usar(basico, j)
		else: _virar(j.pos, dt)
		return
	boss.aux["repath"] = boss.aux.get("repath", 0.0) - dt
	if boss.caminho.is_empty() or boss.aux["repath"] <= 0.0:
		boss.aux["repath"] = 0.4
		sim.ir_para(boss, j.pos)
	sim.mover_ao_longo(boss, dt)

func _passivo(id: String) -> bool:
	return id in ["devorar", "escuridao", "arena_encolhe", "primeira_nota", "nota_final", "chamar_ecos", "onda_do_coro", "regencia", "chamar_querubim", "ordem_de_levantar"]

func _no_alcance(a: Dictionary, dist: float) -> bool:
	if a.has("telegrafo"):
		var t: Dictionary = a["telegrafo"]
		match t["forma"]:
			"cone": return dist <= float(t["raio"]) * 0.85
			"linha": return dist <= float(t["comprimento"]) * 0.85
			"circulo": return dist <= float(t["raio"]) + 0.3 or a["id"] == "pranto_que_cai"
			"circulo_segue_jogador": return true
	if a.has("invoca"): return true
	return dist <= float(a.get("alcance", 2.0))

func _virar(p: Vector2, dt: float) -> void:
	var alvo := (p - boss.pos).normalized()
	if boss.kind == "general_partido":
		var ang := boss.facing.angle()
		var diff := angle_difference(ang, alvo.angle())
		var mx := deg_to_rad(120.0) * dt
		boss.facing = Vector2.from_angle(ang + clampf(diff, -mx, mx))
	else: boss.facing = alvo

func _op(a: Dictionary, extra: Dictionary = {}) -> Dictionary:
	var op := {"mult": float(a.get("mult", 1.0)), "sensacao": "golpe_pesado", "postura": 0.0, "ataque": a["id"]}
	if a.has("efeito"): op["efeito"] = a["efeito"]
	if a.has("empurrao_px"): op["empurrao"] = float(a["empurrao_px"])
	if a.has("telegrafo"): op["area"] = true
	op["elemento"] = "sagrado" if boss.kind == "zacarias_arauto" else ("fogo" if a["id"] == "vomito_de_brasa" else "fisico")
	op.merge(extra, true)
	return op

func _usar(a: Dictionary, j: Ent) -> void:
	var id: String = a["id"]
	boss.cd_basico = boss.intervalo
	if a.has("recarga"): boss.cds[id] = float(a["recarga"])
	if a.get("uma_vez", false): esp["usou_" + id] = true
	var prep := maxf(float(a.get("preparo", 0.6)), 0.6 if a.has("telegrafo") else 0.3)
	var jid := j.id
	var dir := (j.pos - boss.pos).normalized()
	if boss.kind == "general_partido": dir = boss.facing.slerp(dir, 0.5).normalized()
	sim.emitir("som_evento", {"ev": "telegrafo_inicio"}) if a.has("telegrafo") else null
	match id:
		"arrasto", "lanca_do_juizo":
			var n := int(a.get("encadeia", 1))
			_linha(a, j, prep, dir, n)
			if a.get("dupla", false):
				var ang := deg_to_rad(float(a.get("angulo_entre", 35)))
				_linha_extra(a, dir.rotated(ang), prep)
				_linha_extra(a, dir.rotated(-ang), prep)
		"pranto_que_cai":
			var q := int(a.get("quantidade", 3))
			sim.iniciar_acao(boss, {"preparo": 0.5, "rec": 0.3, "alvo": jid, "nome": id, "conj": true})
			for i in q:
				sim.atrasar(float(a.get("intervalo", 0.5)) * i + 0.2, func():
					var jj := sim.valido(jid)
					if jj == null or not boss.vivo: return
					_circulo_em(jj.pos, a, float(a["telegrafo"]["raio"]), prep))
		"vomito_de_brasa":
			var op := _op(a, {"mult": float(a["mult"])})
			sim.iniciar_acao(boss, {"preparo": prep, "rec": 0.6, "alvo": jid, "def": a, "op": op, "dir": dir, "nome": id, "impacto": func():
				for k in range(1, int(a.get("ticks", 3))):
					sim.atrasar(float(a.get("intervalo_tick", 0.4)) * k, func():
						var tg := {"forma": "cone", "origem": boss.pos, "dir": dir, "p": a["telegrafo"]}
						for o in sim.alvos_na_forma(boss, tg): sim.aplicar_golpe(boss, o, op))
				for k in 4:
					sim.criar_area({"pos": boss.pos + dir * (1.0 + k * 0.9), "raio": 0.9, "dur": 4.0, "tick": 0.5, "dono": boss.id, "tipo": "fogo",
						"op": {"mult": 0.25, "area": true, "elemento": "fogo", "efeito": {"queimadura": {"duracao": 2, "dano_por_s_mult": 0.25}}}})
			})
		"banquete":
			var op2 := _op(a)
			op2["ao_impacto"] = func(tg):
				for o in sim.alvos_na_forma(boss, tg):
					if o.tipo == "jogador": _agarrar(o, a); break
				if not boss.aux.get("agarrando", false): sim.aplicar_status(boss, "exausto", float(a["depois"]["exausto"]), null)
			op2["mult"] = 0.0001
			sim.iniciar_acao(boss, {"preparo": prep, "rec": 0.4, "alvo": jid, "def": a, "op": op2, "dir": dir, "nome": id})
		"marca_do_juizo":
			var op3 := _op(a)
			sim.iniciar_acao(boss, {"preparo": 0.3, "rec": 0.2, "nome": id, "conj": true})
			var tg_def := a.duplicate(); tg_def["telegrafo"] = a["telegrafo"]
			var tid := sim.novo_id()
			var tg := {"id": tid, "dono": boss.id, "forma": "circulo_segue_jogador", "origem": j.pos, "dir": Vector2.RIGHT, "p": a["telegrafo"],
				"dur": float(a["preparo"]), "t": 0.0, "def": a, "op": op3, "segue": jid, "ativo": false}
			sim.telegrafos.append(tg)
			sim.emitir("telegrafo", {"id": tid, "forma": tg["forma"], "origem": tg["origem"], "dir": tg["dir"], "p": tg["p"], "dur": tg["dur"], "segue": jid, "dono": boss.id})
			sim.atrasar(float(a["preparo"]), func():
				sim.emitir("raio", {"de": tg["origem"] + Vector2(-3, -3), "para": tg["origem"], "cor": "#ffe7a0", "coluna": true})
				sim.disparar_telegrafo(tid))
		"chamar_carpideiras", "chamar_ecos":
			sim.iniciar_acao(boss, {"preparo": 0.8, "rec": 0.3, "nome": id, "conj": true, "impacto": func(): _invocar(a["invoca"])})
		_:
			# golpe padrão (básico, cone, círculo, lamento...)
			var op4 := _op(a)
			if not a.has("telegrafo"):
				sim.iniciar_acao(boss, {"preparo": prep, "rec": 0.35, "alvo": jid, "nome": id, "impacto": func():
					var jj := sim.valido(jid)
					if jj != null and boss.pos.distance_to(jj.pos) - jj.raio <= float(a.get("alcance", 1.8)) + 0.7:
						sim.aplicar_golpe(boss, jj, op4)
					elif jj != null: sim.emitir("dano", {"id": jj.id, "de": boss.id, "valor": 0, "estilo": "esquivou"})
				})
			else:
				var acao := {"preparo": prep, "rec": 0.45, "alvo": jid, "def": a, "op": op4, "dir": dir, "nome": id}
				if a["telegrafo"]["forma"] == "circulo": acao["ponto_tele"] = boss.pos
				if a.has("rastro_fogo"):
					op4["ao_impacto"] = func(_tg):
						sim.criar_area({"pos": boss.pos, "raio": float(a["telegrafo"].get("raio", 2)), "dur": float(a["rastro_fogo"]["duracao"]), "tick": 0.5, "dono": boss.id, "tipo": "fogo",
							"op": {"mult": 0.2, "area": true, "elemento": "fogo"}})
				sim.iniciar_acao(boss, acao)

func _linha(a: Dictionary, j: Ent, prep: float, dir: Vector2, n: int) -> void:
	var op := _op(a)
	var jid := j.id
	var acao := {"preparo": prep, "rec": 0.4, "alvo": jid, "def": a, "op": op, "dir": dir, "nome": a["id"]}
	if a.has("deslocamento"):
		acao["impacto"] = func():
			sim.deslocar(boss, boss.pos + dir * float(a["deslocamento"]), 0.35, {"tipo": "arrasto"})
			if n > 1:
				sim.atrasar(0.5, func():
					var jj := sim.valido(jid)
					if jj != null and boss.vivo and estado == "luta": _linha(a, jj, prep * 0.8, (jj.pos - boss.pos).normalized(), n - 1))
	sim.iniciar_acao(boss, acao)

func _linha_extra(a: Dictionary, dir: Vector2, prep: float) -> void:
	var tid := sim.novo_id()
	var tg := {"id": tid, "dono": boss.id, "forma": "linha", "origem": boss.pos, "dir": dir, "p": a["telegrafo"], "dur": prep, "t": 0.0, "def": a, "op": _op(a), "segue": -1, "ativo": false}
	sim.telegrafos.append(tg)
	sim.emitir("telegrafo", {"id": tid, "forma": "linha", "origem": boss.pos, "dir": dir, "p": a["telegrafo"], "dur": prep, "segue": -1, "dono": boss.id})
	sim.atrasar(prep, func(): sim.disparar_telegrafo(tid))

func _circulo_em(p: Vector2, a: Dictionary, r: float, prep: float) -> void:
	var tid := sim.novo_id()
	var t := {"forma": "circulo", "raio": r}
	var tg := {"id": tid, "dono": boss.id, "forma": "circulo", "origem": p, "dir": Vector2.RIGHT, "p": t, "dur": prep, "t": 0.0, "def": a, "op": _op(a), "segue": -1, "ativo": false}
	sim.telegrafos.append(tg)
	sim.emitir("telegrafo", {"id": tid, "forma": "circulo", "origem": p, "dir": Vector2.RIGHT, "p": t, "dur": prep, "segue": -1, "dono": boss.id})
	sim.atrasar(prep, func(): sim.disparar_telegrafo(tid))

func _anel(a: Dictionary, ang: float) -> void:
	var tid := sim.novo_id()
	var t: Dictionary = a["telegrafo"]
	var prep := float(a.get("preparo", 1.0))
	var tg := {"id": tid, "dono": boss.id, "forma": "anel", "origem": boss.pos, "dir": Vector2.from_angle(ang), "p": t, "dur": prep, "t": 0.0, "def": a, "op": _op(a), "segue": -1, "ativo": false}
	sim.telegrafos.append(tg)
	sim.emitir("telegrafo", {"id": tid, "forma": "anel", "origem": boss.pos, "dir": tg["dir"], "p": t, "dur": prep, "segue": -1, "dono": boss.id})
	sim.atrasar(prep, func(): sim.disparar_telegrafo(tid))

func _invocar(inv: Dictionary, de: Array = []) -> void:
	var i := 0
	for k in inv:
		for n in int(inv[k]):
			var p: Vector2 = de[i % de.size()] if de.size() > 0 else boss.pos + Vector2.from_angle(sim.rng.randf() * TAU) * 2.5
			i += 1
			var m := sim.criar_mob(k, sim.celula_livre_perto(p), int(Defs.MOBS.get(k, {}).get("niveis", [boss.nivel])[0]))
			m.renasce_s = 0; m.casa = centro; m.raio_coleira = raio_arena + 4
			sim.emitir("vfx", {"nome": "chefe_portal", "pos": m.pos})
			IA.acordar(sim, m, _jog())

# =================================================================== mecânicas especiais por chefe
func _mecanicas(dt: float, j: Ent) -> void:
	match boss.kind:
		"general_partido": _general(dt, j)
		"irma_celeste": _celeste(dt, j)
		"zacarias_arauto": _zacarias(dt, j)

# --- Andras: Pilhas de Mortos, devorar, ordem aos mortos, banquete
func _general(dt: float, j: Ent) -> void:
	if esp.has("comendo"):
		var c: Dictionary = esp["comendo"]
		c["t"] += dt
		if c["t"] >= c["dur"]:
			esp.erase("comendo")
			var alvo: Ent = sim.ents.get(c["pilha"])
			sim.curar(boss, boss.hp_max * float(c["cura"]), boss)
			if c.get("pilha_real", false):
				var st := int(boss.aux.get("fome", 0)) + 1
				if st <= 6:
					boss.aux["fome"] = st
					boss.escala = 1.0 + 0.06 * st
					boss.dano_min = float(d["dano_base"]) * 0.9 * (1.0 + 0.1 * st); boss.dano_max = float(d["dano_base"]) * 1.1 * (1.0 + 0.1 * st)
					sim.emitir("chefe_buff", {"id": boss.id, "fome": st})
				if alvo != null: pilhas.erase(alvo.id); sim.remover(alvo.id)
			elif alvo != null: sim.remover(alvo.id)
			sim.emitir("canal_fim", {"id": boss.id, "ok": true})
			sim.emitir("chefe_fala", {"id": boss.id, "texto": "Mmmh... mais forte."})
		return
	if esp.has("indo_comer"):
		var alvo2: Ent = sim.ents.get(esp["indo_comer"])
		if alvo2 == null: esp.erase("indo_comer"); return
		if boss.pos.distance_to(alvo2.pos) < 1.4:
			esp.erase("indo_comer")
			var real := alvo2.kind == "pilha_de_mortos"
			var fd := _ataques_fase(fase)
			var conj := 4.0
			for a in fd:
				if a["id"] == "devorar": conj = float(a.get("conjuracao", 4.0))
			esp["comendo"] = {"t": 0.0, "dur": conj if real else 2.0, "pilha": alvo2.id, "cura": 0.08 if real else 0.04, "pilha_real": real}
			boss.caminho.clear()
			sim.emitir("canal", {"id": boss.id, "dur": esp["comendo"]["dur"], "texto": "Devorando"})
			sim.emitir("som_evento", {"ev": "general_come"})
		else:
			if boss.caminho.is_empty(): sim.ir_para(boss, alvo2.pos)
			sim.mover_ao_longo(boss, dt)
		return
	esp["devorar_t"] = esp.get("devorar_t", 20.0) - dt
	var comida: Array = pilhas + esp.get("cadaveres", [])
	if not boss.acao.is_empty() or comida.is_empty(): return
	if esp["devorar_t"] <= 0.0 or (boss.frac_hp() < 0.75 and not esp.has("comeu_75")):
		esp["comeu_75"] = true
		esp["devorar_t"] = 20.0
		var melhor := -1
		var md := 1e9
		for id in comida:
			var o: Ent = sim.ents.get(id)
			if o != null and o.pos.distance_to(boss.pos) < md: md = o.pos.distance_to(boss.pos); melhor = id
		if melhor != -1:
			esp["indo_comer"] = melhor
			sim.ir_para(boss, sim.ents[melhor].pos)
			sim.emitir("chefe_fala", {"id": boss.id, "texto": "Fome..."})
	# fase 2: levanta soldados das pilhas
	if fase >= 2 and not boss.cds.has("ordem_de_levantar"):
		boss.cds["ordem_de_levantar"] = 18.0
		var de: Array = []
		for id in pilhas: de.append(sim.ents[id].pos)
		sim.iniciar_acao(boss, {"preparo": 0.8, "rec": 0.3, "nome": "ordem_de_levantar", "conj": true, "impacto": func(): _invocar({"soldado_caido": 2}, de)})
		sim.emitir("chefe_fala", {"id": boss.id, "texto": "DE PÉ, SOLDADOS!"})

func _agarrar(o: Ent, a: Dictionary) -> void:
	boss.aux["agarrando"] = true
	o.status["atordoado"] = {"t": 2.5, "dados": {}, "de": boss.id, "tick": 1.0, "pilhas": 1}
	sim.emitir("status", {"id": o.id, "s": "agarrado", "on": true, "t": 2.5})
	sim.emitir("aviso", {"texto": "Agarrado! Quebre a postura dele para escapar."})
	var oid := o.id
	for k in int(a.get("ticks", 5)):
		sim.atrasar(float(a.get("intervalo_tick", 0.5)) * (k + 1), func():
			var oo := sim.valido(oid)
			if oo == null or not boss.aux.get("agarrando", false): return
			var r := sim.aplicar_golpe(boss, oo, {"mult": float(a.get("mult_por_tick", 0.45)), "nunca_erra": true, "sensacao": "golpe_pesado"})
			if r.has("dano"): sim.curar(boss, float(r["dano"]), boss))
	sim.atrasar(2.5, func(): if boss.aux.get("agarrando", false): _soltar_agarrado())

func _soltar_agarrado() -> void:
	boss.aux.erase("agarrando")
	var j := _jog()
	if j != null:
		j.status.erase("atordoado"); sim.emitir("status", {"id": j.id, "s": "agarrado", "on": false})
	sim.aplicar_status(boss, "exausto", 3.0, null)

# --- Irmã Celeste: regência das coristas, coro em anel, escuridão
func _celeste(dt: float, j: Ent) -> void:
	if fase == 1 or fase == 3:
		if not boss.cds.has("regencia") and fase == 1 and not esp.has("regencia"):
			var vivas := coristas.filter(func(c): return not sim.ents[c].aux.get("morta", false))
			if vivas.size() > 0:
				boss.cds["regencia"] = 15.0
				var c: int = vivas[sim.rng.randi_range(0, vivas.size() - 1)]
				esp["regencia"] = c; esp["regencia_t"] = 6.0
				sim.ents[c].alvejavel = true
				sim.emitir("corista", {"id": c, "canta": true, "t": 6.0})
				sim.emitir("chefe_fala", {"id": boss.id, "texto": "Cante, irmã."})
		if esp.has("regencia"):
			esp["regencia_t"] -= dt
			if esp["regencia_t"] <= 0.0:
				var c2: Ent = sim.ents.get(esp["regencia"])
				esp.erase("regencia")
				if c2 != null:
					c2.alvejavel = false
					sim.emitir("corista", {"id": c2.id, "canta": false})
				boss.escudo = boss.hp_max * 0.12; boss.escudo_t = 30.0
				sim.emitir("escudo", {"id": boss.id, "valor": boss.escudo, "t": 30.0})
				sim.emitir("vfx", {"nome": "chefe_escudo", "alvo": boss.id})
	if fase == 2 and esp.has("coro"):
		coro_t -= dt; onda_t -= dt
		if onda_t <= 0.0:
			onda_t = 3.0
			var a := {}
			for x in _ataques_fase(2):
				if x["id"] == "onda_do_coro": a = x
			_anel(a, onda_ang); onda_ang += deg_to_rad(45.0)
		if coro_t <= 0.0 or coristas.all(func(c): return sim.ents[c].aux.get("morta", false)):
			esp.erase("coro"); esp.erase("levitando")
			boss.aux.erase("imune")
			for c in coristas:
				if sim.ents.has(c) and not sim.ents[c].aux.get("morta", false):
					sim.ents[c].alvejavel = false; sim.emitir("corista", {"id": c, "canta": false})
			sim.aplicar_status(boss, "exausto", 5.0, null)
			sim.emitir("levita", {"id": boss.id, "on": false})
			sim.emitir("chefe_fala", {"id": boss.id, "texto": "O coro... calou..."})
			boss.intervalo *= 0.8
	if fase == 3:
		luzes_t -= dt
		if luzes_t <= 0.0: _mover_luzes()
		var dentro := luzes.any(func(p): return j.pos.distance_to(p) < 2.0)
		esp["luto_t"] = esp.get("luto_t", 0.0) - dt
		if not dentro and esp["luto_t"] <= 0.0:
			esp["luto_t"] = 1.0
			sim.aplicar_dano_puro(j, j.hp_max * 0.02, "profano", boss)
		if not esp.has("usou_chamar_carpideiras"):
			esp["usou_chamar_carpideiras"] = true
			_invocar({"carpideira_de_ossos": 2})

func _coro_comecar() -> void:
	esp["coro"] = true; esp["levitando"] = true
	coro_t = 16.0; onda_t = 1.6
	boss.aux["imune"] = true
	boss.pos = centro
	sim.emitir("teleporte", {"id": boss.id, "pos": centro})
	sim.emitir("levita", {"id": boss.id, "on": true})
	for c in coristas:
		if not sim.ents[c].aux.get("morta", false):
			sim.ents[c].alvejavel = true
			sim.emitir("corista", {"id": c, "canta": true, "t": 16.0})

func _apagar_velas() -> void:
	sim.emitir("escuridao", {"on": true})
	sim.emitir("som_evento", {"ev": "celeste_candelabro_apaga"})
	_mover_luzes()

func _mover_luzes() -> void:
	luzes_t = 20.0
	luzes.clear()
	for i in 3:
		var a := sim.rng.randf() * TAU
		luzes.append(sim.celula_livre_perto(centro + Vector2.from_angle(a) * sim.rng.randf_range(2.0, raio_arena - 2.0)))
	sim.emitir("luzes_arena", {"pos": luzes, "raio": 2.0})

# --- Zacarias: a nota (canalização interrompível), pilares, arena que encolhe
func _zacarias(dt: float, j: Ent) -> void:
	if esp.has("canalizando"):
		var c: Dictionary = esp["canalizando"]
		c["t"] += dt
		if c["t"] >= c["dur"]:
			esp.erase("canalizando")
			boss.postura_max = float(d["postura_max"]); boss.postura = minf(boss.postura, boss.postura_max)
			sim.emitir("canal_fim", {"id": boss.id, "ok": true})
			sim.emitir("som_evento", {"ev": "zacarias_a_nota"})
			sim.emitir("nota", {"pos": boss.pos})
			# atrás de pilar = protegido (linha de visão bloqueada)
			if j.vivo and sim.visao(boss.pos, j.pos):
				sim.aplicar_dano_puro(j, j.hp_max * float(c["frac"]), "sagrado", boss, "normal")
			else:
				sim.emitir("aviso", {"texto": "O pilar segurou a nota."})
			esp.erase("levitando")
			boss.pos = esp.get("pos_volta", centro)
			sim.emitir("teleporte", {"id": boss.id, "pos": boss.pos})
			sim.emitir("levita", {"id": boss.id, "on": false})
		return
	if fase >= 2:
		nota_t -= dt
		if nota_t <= 0.0 and boss.acao.is_empty():
			var nome := "primeira_nota" if fase == 2 else "nota_final"
			var a := {}
			for x in _ataques_fase(fase):
				if x["id"] == nome: a = x
			nota_t = float(a.get("repete_a_cada_s", 40))
			esp["pos_volta"] = boss.pos
			var trombeta: Array = cfg.get("trombeta", [centro.x, centro.y])
			boss.pos = sim.celula_livre_perto(Vector2(trombeta[0], trombeta[1]))
			esp["levitando"] = true
			sim.emitir("teleporte", {"id": boss.id, "pos": boss.pos})
			sim.emitir("levita", {"id": boss.id, "on": true})
			boss.postura_max = float(a.get("postura_durante", 160)); boss.postura = boss.postura_max
			esp["canalizando"] = {"t": 0.0, "dur": float(a.get("conjuracao", 10.0)), "frac": float(a.get("dano_frac_hp_max_jogador", 0.6))}
			sim.emitir("canal", {"id": boss.id, "dur": esp["canalizando"]["dur"], "texto": "A Nota", "chefe": true})
			sim.emitir("chefe_fala", {"id": boss.id, "texto": "Silêncio... SILÊNCIO! Agora eu toco!" if fase == 2 else "Eu SOU o fim!"})
			sim.emitir("aviso", {"texto": "Quebre a postura dele ou se esconda atrás de um pilar!"})
			if fase == 2: _invocar({"eco_da_trombeta": 3})
	if fase == 3:
		encolhe_t -= dt
		if encolhe_t <= 0.0 and raio_fogo > 5.0:
			encolhe_t = 25.0
			raio_fogo = maxf(5.0, raio_fogo - 1.5)
			sim.emitir("anel_fogo", {"centro": centro, "raio": raio_fogo})
			sim.emitir("aviso", {"texto": "O fogo sagrado fecha a arena!"})
		if raio_fogo < 90.0 and j.pos.distance_to(centro) > raio_fogo:
			esp["fogo_t"] = esp.get("fogo_t", 0.0) - dt
			if esp["fogo_t"] <= 0.0:
				esp["fogo_t"] = 0.5
				sim.aplicar_dano_puro(j, j.hp_max * 0.04, "sagrado", boss)
		esp["querubim_t"] = esp.get("querubim_t", 30.0) - dt
		if esp["querubim_t"] <= 0.0:
			esp["querubim_t"] = 30.0
			_invocar({"querubim_desfeito": 1})

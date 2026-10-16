class_name ChefeEgito
extends RefCounted
## Mecânicas dos chefes do Egito (Labirinto de Hawara e raid O Coração Endurecido).
## Lê `mecanica_egito` do chefe (design/combate/chefes.json) e os objetos da arena do mapa (chefe.arena.*).
## Criado pelo ChefeCtl quando o chefe tem `mecanica_egito`; o ChefeCtl chama iniciar/passo/nova_fase/morreu/resetar.
## Eventos novos para o cliente (todos opcionais; sem eles a luta funciona, só fica menos legível):
##   chefe_barra {id, nome, valor, max}      barra extra embaixo da vida do chefe (Sede, Luz)
##   enigma {glifos, dica, t}                os três glifos no peito da Esfinge
##   marca_egito {id, marca, t}              Coração/Pena sobre a cabeça, Brasa na mão, Veneno de Serket (pilhas)
##   portas_marcadas {pos, t}                a décima praga: portas com sangue no lintel
##   luzes_arena {pos, raio}                 (já existe, da Celeste) lamparinas das Trevas
##   agua_arena {sobe, ilhas, raio}          a água de Petsuchos subindo/descendo

var ctl: ChefeCtl
var sim: WorldSim
var boss: Ent
var d: Dictionary
var m: Dictionary
var arena: Dictionary
var t := {}                 # cronômetros
var objs: Array = []        # ids de objetos da arena criados por nós
var adic: Dictionary = {}   # kind -> id dos adicionais vivos
var adic_mortos: Array = []
var areas: Array = []       # áreas nossas (para limpar no reset)
var pilhas := {}            # Serket: jogador -> pilhas
var marcas := {}            # Anúbis: jogador -> "coracao"|"pena"
var hp_base := 0.0
var mult_grupo := 1.0
var ativo := false
var ecoados := {}           # Janes/Jambres: telegrafos já ecoados
var quero_imune := false    # a transição de fase do ChefeCtl tira o "imune"; reafirmamos a cada passo

func _init(p_ctl: ChefeCtl) -> void:
	ctl = p_ctl; sim = p_ctl.sim; boss = p_ctl.boss; d = p_ctl.d
	m = d.get("mecanica_egito", {})
	arena = p_ctl.cfg.get("arena", {})
	hp_base = boss.hp_max
	sim.evento.connect(_ao_evento)

# ======================================================================= utilidades
func _v(p) -> Vector2:
	return Vector2(float(p[0]), float(p[1]))

func _jogs() -> Array:
	return sim.jogadores().filter(func(e: Ent): return e.vivo and e.pos.distance_to(ctl.centro) <= ctl.raio_arena + 3.0)

func _aviso(txt: String) -> void:
	sim.emitir("aviso", {"texto": txt})

func _fala(txt: String) -> void:
	sim.emitir("chefe_fala", {"id": boss.id, "texto": txt})

func _dano_frac(e: Ent, frac: float, elem := "sagrado") -> void:
	sim.aplicar_dano_puro(e, e.hp_max * frac, elem, boss, "normal")

func _buff(e: Ent, id: String, dur: float, mods: Dictionary) -> void:
	if e.tipo == "jogador": Jogador.add_buff(sim, e, id, dur, mods); return
	for b in e.buffs:
		if b["id"] == id: e.buffs.erase(b); break
	e.buffs.append({"id": id, "t": dur, "dur": dur, "mods": mods, "egito": true})
	sim.emitir("buff", {"id": e.id, "buff": id, "on": true, "t": dur})

func _tirar_buff(e: Ent, id: String) -> void:
	for b in e.buffs:
		if b["id"] == id: e.buffs.erase(b); sim.emitir("buff", {"id": e.id, "buff": id, "on": false}); return

func _tick_buffs(dt: float) -> void:
	# buffs nossos em chefe e adicionais (jogadores já têm o próprio relógio)
	var lista: Array = [boss]
	for k in adic:
		if sim.ents.has(adic[k]): lista.append(sim.ents[adic[k]])
	for e: Ent in lista:
		for b in e.buffs.duplicate():
			if b.get("egito", false):
				b["t"] -= dt
				if b["t"] <= 0.0: e.buffs.erase(b); sim.emitir("buff", {"id": e.id, "buff": b["id"], "on": false})

func _cron(nome: String, dt: float, periodo: float) -> bool:
	## true uma vez a cada `periodo` segundos (o primeiro disparo vem depois de um período inteiro)
	var k := "_c_" + nome
	t[k] = float(t.get(k, periodo)) - dt
	if t[k] <= 0.0:
		t[k] += periodo
		return true
	return false

func _objeto(kind: String, nome: String, p: Vector2, hp: float) -> int:
	var id := ctl._objeto_arena(kind, nome, p, hp * mult_grupo, {})
	objs.append(id)
	return id

func _area(pos: Vector2, raio: float, dur: float, tipo: String, cada_tick: Callable, tick := 1.0) -> Dictionary:
	var a := sim.criar_area({"pos": pos, "raio": raio, "dur": dur, "tick": tick, "dono": boss.id, "tipo": tipo, "cada_tick": cada_tick})
	areas.append(a)
	return a

func _remover_area(a: Dictionary) -> void:
	if a in sim.areas: sim.areas.erase(a); sim.emitir("area_fim", {"id": a["id"]})
	areas.erase(a)

func _na_area(a: Dictionary) -> Array:
	return _jogs().filter(func(e: Ent): return e.pos.distance_to(a["pos"]) <= float(a["raio"]))

func _ataque(id: String) -> Dictionary:
	for f in d["fases"]:
		for a in f["ataques"]:
			if a["id"] == id: return ctl._ataques_fase(int(f["n"])).filter(func(x): return x["id"] == id)[0]
	return {}

func _sumir(sim_: bool) -> void:
	quero_imune = sim_
	boss.aux["imune"] = sim_
	boss.alvejavel = not sim_
	boss.invisivel = sim_
	if sim_:
		sim.cancelar_acao(boss)
		ctl.esp["levitando"] = true
	else:
		ctl.esp.erase("levitando")
	sim.emitir("chefe_some", {"id": boss.id, "some": sim_})

func _criar_adicional(kind: String, p: Vector2) -> Ent:
	var e := sim.criar_mob(kind, sim.celula_livre_perto(p), int(boss.nivel))
	e.renasce_s = 0; e.casa = ctl.centro; e.raio_coleira = ctl.raio_arena + 6.0
	e.hp_max *= mult_grupo; e.hp = e.hp_max
	e.aux["adicional_egito"] = true
	adic[kind] = e.id
	sim.emitir("vfx", {"nome": "chefe_portal", "pos": e.pos})
	IA.acordar(sim, e, ctl._jog())
	return e

func _adicional(kind: String) -> Ent:
	if not adic.has(kind): return null
	var e: Ent = sim.ents.get(adic[kind])
	return e if e != null and e.vivo else null

# ======================================================================= ciclo da luta (chamado pelo ChefeCtl)
func iniciar() -> void:
	ativo = true
	t.clear(); pilhas.clear(); marcas.clear(); adic.clear(); adic_mortos.clear(); ecoados.clear()
	# vida pelo tamanho do grupo (dungeon: base 1 jogador; raid: base 5, até 10)
	var eg: Dictionary = d.get("escala_grupo", {})
	var n := _jogs().size()
	mult_grupo = 1.0 + float(eg.get("por_jogador", 0.0)) * maxf(0.0, float(mini(n, int(eg.get("max", 99)))) - float(eg.get("base", 1)))
	boss.hp_max = hp_base * mult_grupo; boss.hp = boss.hp_max
	for k in ctl.cfg.get("adicionais", []):
		_criar_adicional(k["id"], _v(k["pos"]))
	match m.get("tipo", ""):
		"agua_que_sobe":
			for p in arena.get("oferendas", []): _objeto("mesa_oferenda", "Mesa de Oferenda", _v(p), float(m.get("oferenda_hp", 600)))
		"veneno_e_ankh":
			for p in arena.get("ninhos", []): _objeto("ninho_serket", "Ninho de Serket", _v(p), float(m.get("ninho_hp", 800)))
			t["ankhs_off"] = {}
		"sede":
			t["sede"] = 0.0
			for p in arena.get("jarras", []): _objeto("jarra_cerveja", "Jarra de Cerveja Ocre", _v(p), 1.0 / mult_grupo)
		"conselho":
			t["ordem"] = 0
		"lanterna_de_ra":
			t["luz"] = 100.0
		"dez_pragas":
			t["sangue"] = []; t["parado"] = {}
	if m.get("tipo", "") == "conselho": _conselho_trocar()


func resetar() -> void:
	ativo = false
	for id in objs: sim.remover(id)
	objs.clear()
	for a in areas.duplicate(): _remover_area(a)
	for k in adic:
		if sim.ents.has(adic[k]): sim.remover(adic[k])
	adic.clear()
	for e: Ent in sim.jogadores():
		for b in ["brasa", "maat", "sol_de_ra", "veneno_serket"]: _tirar_buff(e, b)
	boss.hp_max = hp_base; boss.hp = boss.hp_max
	boss.alvejavel = true; boss.invisivel = false
	t.clear(); pilhas.clear(); marcas.clear()

func encerrar() -> void:
	## o chefe morreu: limpa as áreas e objetos da luta (os adicionais o ChefeCtl já mata)
	ativo = false
	for id in objs: sim.remover(id)
	objs.clear()
	for a in areas.duplicate(): _remover_area(a)
	for e: Ent in sim.jogadores():
		for b in ["brasa", "veneno_serket"]: _tirar_buff(e, b)


func nova_fase(n: int) -> void:
	match m.get("tipo", ""):
		"agua_que_sobe":
			if n == 2: _fala("(a água chega aos joelhos)")
		"balanca":
			if n == 2 and _adicional("ammit") == null:
				_criar_adicional("ammit", _v(arena.get("ammit_nasce", [ctl.centro.x + 6, ctl.centro.y])))
				_aviso("Ammit, a Devoradora, entrou no salão: alguém resistente precisa segurá-la.")
		"dez_pragas":
			var pr: Array = m["por_fase"][mini(n - 1, m["por_fase"].size() - 1)]
			_aviso("Pragas: " + ", ".join(pr.map(func(x): return {"sangue": "Sangue", "ras": "Rãs", "piolhos": "Piolhos", "moscas": "Moscas", "peste": "Peste",
				"ulceras": "Úlceras", "granizo": "Granizo", "gafanhotos": "Gafanhotos", "trevas": "Trevas", "decima": "A Décima"}.get(x, x))))
			if "trevas" in pr: _trevas_mover()

## Morte de um objeto da arena ou de um adicional (a do chefe o ChefeCtl trata; Janes não morre com o irmão de pé, ver _magos).
func morreu(e: Ent, killer: Ent) -> void:
	if e.id in objs:
		objs.erase(e.id)
		match e.kind:
			"mesa_oferenda": _aviso("Mesa de Oferenda quebrada: menos comida para Petsuchos.")
			"ninho_serket": _aviso("Um ninho de Serket foi destruído.")
			"jarra_cerveja": _jarra_quebrou(e)
		return
	for k in adic.keys():
		if adic[k] == e.id:
			adic_mortos.append(k)
			match m.get("tipo", ""):
				"imitacao": _irmao_caiu(k)
				"conselho": _vaso_derramado(k, e.pos); _conselho_trocar()
			return

func passo(dt: float, j: Ent) -> void:
	if not ativo: return
	if quero_imune: boss.aux["imune"] = true
	_tick_buffs(dt)
	match m.get("tipo", ""):
		"agua_que_sobe": _petsuchos(dt)
		"enigma": _esfinge(dt)
		"veneno_e_ankh": _serket(dt)
		"sede": _sekhmet(dt)
		"imitacao": _magos(dt)
		"conselho": _conselho(dt)
		"lanterna_de_ra": _apofis(dt)
		"balanca": _anubis(dt)
		"dez_pragas": _farao(dt)

func _ao_evento(tipo: String, ev: Dictionary) -> void:
	if not ativo or boss == null: return
	if tipo == "dano" and int(ev.get("de", -1)) == boss.id and int(ev.get("valor", 0)) > 0:
		var alvo: Ent = sim.ents.get(int(ev.get("id", -1)))
		if alvo == null or alvo.tipo != "jogador": return
		match m.get("tipo", ""):
			"sede": t["sede"] = minf(100.0, float(t.get("sede", 0.0)) + float(m.get("sede_por_golpe", 6)))
			"veneno_e_ankh": _pilha(alvo, 1)
	elif tipo == "telegrafo":
		var dono := int(ev.get("dono", -1))
		var tg := sim.achar_tele(int(ev.get("id", -1)))
		if tg.is_empty(): return
		match m.get("tipo", ""):
			"imitacao": _ecoar(tg, dono)
			"lanterna_de_ra":
				if dono == boss.id and tg.get("def", {}).get("id", "") == "vomito_de_brasa":
					t["luz"] = maxf(0.0, float(t.get("luz", 100.0)) - float(m.get("cuspe_tira", 25)))
					_aviso("O Cuspe da Treva atingiu a Lanterna de Rá.")

# ======================================================================= Petsuchos: a água que sobe
func _petsuchos(dt: float) -> void:
	var ciclo: float = float(m["ciclo_s"][mini(ctl.fase - 1, m["ciclo_s"].size() - 1)])
	if t.has("submerso"):
		t["submerso"] -= dt
		if _cron("agua_tick", dt, 1.0):
			var r_ilha := float(arena.get("raio_ilha", 1.8))
			for e: Ent in _jogs():
				var seco: bool = arena.get("ilhas", []).any(func(p): return e.pos.distance_to(_v(p)) <= r_ilha)
				if not seco: _dano_frac(e, float(m.get("dano_fora_ilha_frac", 0.03)), "fisico")
		if t["submerso"] <= 0.0:
			t.erase("submerso"); t.erase("_c_agua_tick")
			sim.emitir("agua_arena", {"sobe": false})
			# volta: cura pelas mesas que sobraram e investe contra alguém
			var mesas := objs.filter(func(id): return sim.ents.has(id) and sim.ents[id].kind == "mesa_oferenda" and sim.ents[id].vivo).size()
			if mesas > 0:
				sim.curar(boss, boss.hp_max * float(m.get("cura_por_oferenda", 0.06)) * mesas, boss)
				_aviso("Petsuchos comeu %d oferenda(s)." % mesas)
			var js := _jogs()
			if js.size() > 0:
				var alvo: Ent = js[sim.rng.randi() % js.size()]
				boss.pos = sim.celula_livre_perto(ctl.centro + (ctl.centro - alvo.pos).normalized() * 6.0)
				sim.emitir("teleporte", {"id": boss.id, "pos": boss.pos})
				_sumir(false)
				var a := _ataque("lanca_do_juizo")
				if not a.is_empty(): ctl._linha(a, alvo, 1.1, (alvo.pos - boss.pos).normalized(), 1)
			else:
				_sumir(false)
		return
	if _cron("agua", dt, ciclo):
		t["submerso"] = float(m.get("duracao_s", 8))
		_sumir(true)
		sim.emitir("agua_arena", {"sobe": true, "ilhas": arena.get("ilhas", []), "raio": arena.get("raio_ilha", 1.8), "t": t["submerso"]})
		_aviso("A água está subindo! Suba numa ilha de pedra.")

# ======================================================================= Esfinge: o enigma
const GLIFOS := ["escaravelho", "olho", "ankh", "pena", "djed", "junco"]

func _esfinge(dt: float) -> void:
	if t.has("enigma"):
		var en: Dictionary = t["enigma"]
		en["t"] -= dt
		var r := float(arena.get("raio_pedestal", 1.0))
		var certo := false
		for e: Ent in _jogs():
			for p in arena.get("pedestais", []):
				if e.pos.distance_to(_v(p["pos"])) <= r + 0.3:
					if p["glifo"] == en["resposta"]: certo = true
					else:
						en["errado"] = float(en.get("errado", 0.0)) + dt
		en["ficou"] = float(en.get("ficou", 0.0)) + dt if certo else 0.0
		if en["ficou"] >= float(m.get("ficar_s", 3)):
			t.erase("enigma"); _sumir(false)
			var q: Dictionary = m.get("quebrada", {"dano_recebido": 0.5, "duracao": 10})
			_buff(boss, "quebrada", float(q["duracao"]), {"dano_recebido": float(q["dano_recebido"])})
			boss.quebrado_t = 2.0
			_fala("CERTO. CERTO DEMAIS."); _aviso("A Esfinge está Quebrada: +50% de dano por 10 s.")
		elif en["t"] <= 0.0 or float(en.get("errado", 0.0)) >= 1.0:
			t.erase("enigma"); _sumir(false)
			_fala("ERRADO É SÓ OUTRO CAMINHO.")
			sim.emitir("vfx", {"nome": "onda_pedra", "pos": boss.pos})
			for e: Ent in _jogs():
				var salvo: bool = arena.get("pedestais", []).any(func(p): return p["glifo"] == en["resposta"] and e.pos.distance_to(_v(p["pos"])) <= r + 0.3)
				if not salvo: _dano_frac(e, float(m.get("erro_frac_hp_max", 0.6)), "fisico")
		return
	var gat: Array = m.get("gatilhos_hp", [])
	var feitos := int(t.get("enigmas", 0))
	if feitos < gat.size() and boss.frac_hp() <= float(gat[feitos]):
		t["enigmas"] = feitos + 1
		_sumir(true); boss.invisivel = false; boss.alvejavel = true   # senta, mas fica à vista
		var g := GLIFOS.duplicate(); g.shuffle()
		var seq: Array; var resp: String; var dica: String
		match feitos % 3:
			0: seq = [g[0], g[1], g[0]]; resp = g[1]; dica = "A vem, B vem, A volta..."
			1:   # o que falta da tríade (a tríade é a fileira de pedestais: escaravelho-olho-ankh / pena-djed-junco)
				var tri: Array = [GLIFOS.slice(0, 3), GLIFOS.slice(3, 6)][sim.rng.randi() % 2]
				var tt := tri.duplicate(); tt.shuffle()
				seq = [tt[0], tt[1], tt[0]]; resp = tt[2]; dica = "Três irmãos, um sumiu."
			_:   # o oposto: cada glifo tem o seu par do outro lado do anel
				var i := sim.rng.randi() % 6
				seq = [GLIFOS[i], GLIFOS[i], GLIFOS[i]]; resp = GLIFOS[(i + 3) % 6]; dica = "O que está do outro lado?"
		t["enigma"] = {"t": float(m.get("tempo_s", 12)), "resposta": resp}
		sim.emitir("enigma", {"id": boss.id, "glifos": seq, "dica": dica, "t": float(m.get("tempo_s", 12))})
		_fala("RESPONDA.")

# ======================================================================= Serket: veneno em pilha e ankhs
func _pilha(e: Ent, n: int) -> void:
	var p := mini(int(pilhas.get(e.id, 0)) + n, int(m.get("pilha_max", 10)))
	pilhas[e.id] = p
	sim.emitir("marca_egito", {"id": e.id, "marca": "veneno_serket", "pilhas": p})
	var red := float(m.get("cura_reduzida_por_pilha", 0.04)) * p
	if p >= 5: sim.aplicar_status(e, "cura_reduzida", 2.0, boss)
	if p > 0: _buff(e, "veneno_serket", 3.0, {"cura_recebida": -red})

func _serket(dt: float) -> void:
	if _cron("veneno_tick", dt, 1.0):
		for e: Ent in _jogs():
			var p := int(pilhas.get(e.id, 0))
			if e.tem("veneno") and p < int(m.get("pilha_max", 10)): _pilha(e, 1); p += 1
			if p > 0:
				_dano_frac(e, float(m.get("dano_por_pilha_frac", 0.006)) * p, "veneno")
				_buff(e, "veneno_serket", 2.0, {"cura_recebida": -float(m.get("cura_reduzida_por_pilha", 0.04)) * p})
	# ankhs: limpam tudo e apagam por um tempo
	var off: Dictionary = t.get("ankhs_off", {})
	for k in off.keys():
		off[k] -= dt
		if off[k] <= 0.0: off.erase(k); sim.emitir("ankh", {"i": k, "aceso": true})
	var ankhs: Array = arena.get("ankhs", [])
	for i in ankhs.size():
		if off.has(i): continue
		for e: Ent in _jogs():
			if int(pilhas.get(e.id, 0)) > 0 and e.pos.distance_to(_v(ankhs[i])) <= float(arena.get("raio_ankh", 1.0)) + 0.3:
				pilhas[e.id] = 0; e.status.erase("veneno"); e.status.erase("cura_reduzida"); _tirar_buff(e, "veneno_serket")
				sim.emitir("status", {"id": e.id, "s": "veneno", "on": false})
				sim.emitir("marca_egito", {"id": e.id, "marca": "veneno_serket", "pilhas": 0})
				sim.emitir("ankh", {"i": i, "aceso": false}); sim.emitir("vfx", {"nome": "cura_ankh", "pos": _v(ankhs[i])})
				off[i] = float(m.get("ankh_recarga_s", 25)); break
	t["ankhs_off"] = off
	# os ninhos chamam filhas
	if ctl.fase >= 2 and _cron("ninhos", dt, 30.0):
		for id in objs:
			var n: Ent = sim.ents.get(id)
			if n != null and n.vivo and n.kind == "ninho_serket": ctl._invocar({"filha_de_serket": 1}, [n.pos])
	# enterra e reaparece embaixo de alguém
	var en: Dictionary = m.get("enterra", {})
	if ctl.fase >= int(en.get("desde_fase", 2)):
		if t.has("enterrada"):
			t["enterrada"] -= dt
			if t["enterrada"] <= 0.0:
				t.erase("enterrada")
				var js := _jogs()
				var alvo: Ent = js[sim.rng.randi() % js.size()] if js.size() > 0 else null
				if alvo != null:
					var p := alvo.pos
					ctl._circulo_em(p, {"id": "emergir", "mult": 1.6, "telegrafo": {"forma": "circulo", "raio": 2.2},
						"efeito": {"veneno": {"duracao": 8, "dano_por_s_mult": 0.25}}}, 2.2, 1.4)
					sim.atrasar(1.4, func():
						boss.pos = sim.celula_livre_perto(p); sim.emitir("teleporte", {"id": boss.id, "pos": boss.pos}); _sumir(false)
						for e: Ent in _jogs():
							if e.pos.distance_to(p) <= 2.4: _pilha(e, 3))
				else: _sumir(false)
		elif _cron("enterra", dt, float(en.get("a_cada_s", 40))):
			t["enterrada"] = float(en.get("dur_s", 6)); _sumir(true)
			_aviso("Serket se enterrou. Ela vai sair embaixo de alguém.")

# ======================================================================= Sekhmet: sede e as jarras de cerveja
func _sekhmet(dt: float) -> void:
	var porS: Array = m.get("sede_por_s", [0, 2, 3])
	t["sede"] = minf(100.0, float(t.get("sede", 0.0)) + float(porS[mini(ctl.fase - 1, porS.size() - 1)]) * dt)
	if t.has("massacre"):
		t["massacre"] -= dt
		if t["massacre"] <= 0.0:
			t.erase("massacre"); boss.vel = float(d["velocidade_mov"]) * (1.3 if boss.aux.has("enrage") else 1.0); boss.intervalo = float(d["intervalo_ataque"])
	elif float(t["sede"]) >= 100.0:
		var ms: Dictionary = m.get("massacre", {"dano": 0.8, "vel": 0.4, "dur_s": 8})
		t["massacre"] = float(ms["dur_s"]); t["sede"] = 0.0
		_buff(boss, "massacre", float(ms["dur_s"]), {"dano": float(ms["dano"])})
		boss.vel *= 1.0 + float(ms["vel"]); boss.intervalo *= 0.6
		_fala("SANGUE!"); _aviso("Sekhmet entrou em Massacre!")
	if _cron("barra", dt, 0.5):
		sim.emitir("chefe_barra", {"id": boss.id, "nome": "Sede", "valor": roundi(float(t["sede"])), "max": 100})

func _jarra_quebrou(e: Ent) -> void:
	var pos := e.pos
	if boss.pos.distance_to(pos) <= float(m.get("jarra_raio", 4.0)):
		t["sede"] = maxf(0.0, float(t.get("sede", 0.0)) - float(m.get("jarra_reduz", 35)))
		var em: Dictionary = m.get("embriagada", {"dano_recebido": 0.2, "dur_s": 4})
		_buff(boss, "embriagada", float(em["dur_s"]), {"dano_recebido": float(em["dano_recebido"])})
		sim.emitir("vfx", {"nome": "cerveja_ocre", "pos": pos})
		_fala("...sangue? Tem gosto de... cevada.")
	else:
		_aviso("A cerveja derramou longe dela.")
	sim.atrasar(float(m.get("jarra_renasce_s", 45)), func():
		if ativo: _objeto("jarra_cerveja", "Jarra de Cerveja Ocre", pos, 1.0 / mult_grupo))

# ======================================================================= Janes e Jambres: imitação, vínculo, rio de sangue
func _ecoar(tg: Dictionary, dono: int) -> void:
	var jam := _adicional(m.get("segundo", "jambres"))
	if jam == null or ecoados.has(tg["id"]): return
	var de: Ent; var por: Ent
	if dono == boss.id: de = boss; por = jam
	elif dono == jam.id: de = jam; por = boss
	else: return
	if not por.vivo or por.aux.get("imune", false): return
	ecoados[tg["id"]] = true
	var forma: String = tg["forma"]; var p: Dictionary = tg["p"]; var def: Dictionary = tg.get("def", {})
	sim.atrasar(float(m.get("eco_s", 2.0)), func():
		if not ativo or not por.vivo: return
		var js := _jogs()
		if js.is_empty(): return
		var alvo: Ent = js[sim.rng.randi() % js.size()]
		var origem := alvo.pos if forma in ["circulo", "circulo_segue_jogador"] else por.pos
		var dir := (alvo.pos - por.pos).normalized()
		var tid := sim.novo_id()
		var ntg := {"id": tid, "dono": boss.id, "forma": "circulo" if forma == "circulo_segue_jogador" else forma, "origem": origem, "dir": dir, "p": p,
			"dur": 1.2, "t": 0.0, "def": def, "op": ctl._op(def) if not def.is_empty() else {"mult": 1.0}, "segue": -1, "ativo": false}
		ecoados[tid] = true
		sim.telegrafos.append(ntg)
		sim.emitir("telegrafo", {"id": tid, "forma": ntg["forma"], "origem": origem, "dir": dir, "p": p, "dur": 1.2, "segue": -1, "dono": por.id})
		sim.atrasar(1.2, func(): sim.disparar_telegrafo(tid)))

func _irmao_caiu(k: String) -> void:
	_aviso("Jambres caiu. Janes tem %d s para cair também." % int(m.get("vinculo_s", 10)))
	t["vinculo_jambres"] = float(m.get("vinculo_s", 10))

func _magos(dt: float) -> void:
	var jam := _adicional(m.get("segundo", "jambres"))
	# Janes não morre com o irmão de pé: cai de joelhos (imune) e conta o vínculo
	if jam != null and boss.frac_hp() <= 0.04 and not t.has("vinculo_janes"):
		t["vinculo_janes"] = float(m.get("vinculo_s", 10)); boss.hp = boss.hp_max * 0.04
		_sumir(true); boss.invisivel = false
		_fala("Irmão... levanta-me."); _aviso("Janes caiu de joelhos. Derrubem Jambres em 10 s!")
	if t.has("vinculo_janes"):
		t["vinculo_janes"] -= dt
		if jam == null:   # os dois caíram juntos: fim
			t.erase("vinculo_janes"); _sumir(false)
			var js := _jogs()
			sim.matar(boss, js[0] if js.size() > 0 else null)
			return
		if t["vinculo_janes"] <= 0.0:
			t.erase("vinculo_janes"); _sumir(false)
			boss.hp = boss.hp_max * float(m.get("ressuscita_frac", 0.4))
			_fala("Juntos. Sempre juntos."); _aviso("Jambres ergueu o irmão.")
	if t.has("vinculo_jambres"):
		t["vinculo_jambres"] -= dt
		if boss.frac_hp() <= 0.04:
			t.erase("vinculo_jambres")   # Janes também caiu dentro do prazo: a morte normal do chefe encerra
			boss.aux.erase("imune"); var js2 := _jogs(); sim.matar(boss, js2[0] if js2.size() > 0 else null); return
		if t["vinculo_jambres"] <= 0.0 and not t.has("canal"):
			t.erase("vinculo_jambres")
			t["canal"] = float(m.get("canal_s", 4.0)); ctl.esp["levitando"] = true; sim.cancelar_acao(boss)
			sim.emitir("canal", {"id": boss.id, "t": t["canal"], "nome": "Erguer o Irmão"})
			_fala("Levanta, irmão.")
	if t.has("canal"):
		t["canal"] -= dt
		if boss.quebrado_t > 0.0:
			t.erase("canal"); ctl.esp.erase("levitando"); sim.emitir("canal_fim", {"id": boss.id, "ok": false})
			_aviso("O canal de Janes foi interrompido. Jambres continua morto.")
		elif t["canal"] <= 0.0:
			t.erase("canal"); ctl.esp.erase("levitando"); sim.emitir("canal_fim", {"id": boss.id, "ok": true})
			var e := _criar_adicional(m.get("segundo", "jambres"), boss.pos + Vector2(2, 0))
			e.hp = e.hp_max * float(m.get("ressuscita_frac", 0.4))
	# Pacto: juntos demais ficam mais fortes
	if jam != null:
		var pc: Dictionary = m.get("pacto", {"dist": 6.0, "apos_s": 3.0, "dano": 0.3})
		if boss.pos.distance_to(jam.pos) < float(pc["dist"]):
			t["perto"] = float(t.get("perto", 0.0)) + dt
			if float(t["perto"]) >= float(pc["apos_s"]):
				_buff(boss, "pacto", 1.0, {"dano": float(pc["dano"])}); _buff(jam, "pacto", 1.0, {"dano": float(pc["dano"])})
		else: t["perto"] = 0.0
	# Rio de Sangue (fase 2)
	var rio: Dictionary = m.get("rio", {})
	if ctl.fase >= int(rio.get("desde_fase", 2)) and _cron("rio", dt, 10.0):
		var r := 1.5 + float(rio.get("cresce_por_10s", 0.5)) * float(t.get("rio_n", 0))
		t["rio_n"] = int(t.get("rio_n", 0)) + 1
		if t.has("rio_area"): _remover_area(t["rio_area"])
		t["rio_area"] = _area(_v(arena.get("rio", [ctl.centro.x, ctl.centro.y])), r, 999.0, "sangue", func(a):
			for e: Ent in _na_area(a): sim.aplicar_status(e, "cura_reduzida", 1.5, boss))

# ======================================================================= Quatro Filhos de Hórus: conselho
func _membros_vivos() -> Array:
	var v: Array = []
	for k in ["hapi", "duamutef", "qebehsenuef"]:
		if _adicional(k) != null: v.append(k)
	return v

func _selar(e: Ent, sim_: bool, pedestal: Vector2) -> void:
	e.aux["imune"] = sim_; e.alvejavel = not sim_
	if sim_:
		sim.cancelar_acao(e); e.caminho.clear()
		e.pos = sim.celula_livre_perto(pedestal); sim.emitir("teleporte", {"id": e.id, "pos": e.pos})
		e.status["atordoado"] = {"t": 999.0, "dados": {}, "de": -1, "tick": 1.0, "pilhas": 1}
		sim.emitir("status", {"id": e.id, "s": "selado", "on": true, "t": 999.0})
	elif e.status.has("atordoado"):
		e.status.erase("atordoado"); sim.emitir("status", {"id": e.id, "s": "selado", "on": false})
		IA.acordar(sim, e, ctl._jog())

func _pedestal(k: String) -> Vector2:
	for p in arena.get("pedestais", []):
		if p["membro"] == k: return _v(p["pos"])
	return ctl.centro

func _conselho_trocar() -> void:
	var vivos := _membros_vivos()
	var ordem := int(t.get("ordem", 0))
	var lutam: Array = []
	if vivos.size() > 0:
		for i in mini(2, vivos.size()): lutam.append(vivos[(ordem + i) % vivos.size()])
	t["ordem"] = ordem + 1
	t["lutam"] = lutam
	for k in vivos:
		_selar(sim.ents[adic[k]], not (k in lutam), _pedestal(k))
	# Imseti (o chefe) fica imune no pedestal até os três caírem
	if vivos.is_empty():
		boss.aux.erase("imune"); ctl.esp.erase("levitando"); quero_imune = false
		_fala("IMSETI: Então eu desço."); _aviso("Imseti desceu do pedestal: agora ele pode ser ferido.")
	else:
		boss.aux["imune"] = true; ctl.esp["levitando"] = true; quero_imune = true
		boss.pos = sim.celula_livre_perto(_pedestal("imseti"))
		sim.emitir("aviso", {"texto": "Lutam: " + " e ".join(lutam.map(func(x): return Defs.MOBS.get(x, {}).get("nome", x)))})

func _vaso_derramado(k: String, pos: Vector2) -> void:
	var vaso: String = m.get("vasos", {}).get(k, "")
	var nomes := {"figado_dano": "o fígado (dano)", "pulmoes_lento": "os pulmões (lentidão)", "estomago_sem_cura": "o estômago (sem cura)", "intestinos_veneno": "os intestinos (veneno)"}
	_aviso("O vaso de %s se quebrou: %s no chão." % [Defs.MOBS.get(k, {}).get("nome", k), nomes.get(vaso, vaso)])
	_area(pos, 2.6, 9999.0, "vaso_" + vaso, _vaso_tick.bind(vaso))

func _vaso_tick(a: Dictionary, vaso: String) -> void:
	for e: Ent in _na_area(a):
		match vaso:
			"figado_dano": _dano_frac(e, 0.04, "sombra")
			"pulmoes_lento": sim.aplicar_status(e, "lento", 1.5, boss)
			"estomago_sem_cura": sim.aplicar_status(e, "cura_reduzida", 1.5, boss)
			"intestinos_veneno": sim.aplicar_status(e, "veneno", {"duracao": 4, "dano_por_s_mult": 0.25}, boss)

func _conselho(dt: float) -> void:
	if ctl.esp.has("levitando") and not _membros_vivos().is_empty():
		boss.caminho.clear()
	if _cron("troca", dt, float(m.get("troca_s", 30))): _conselho_trocar()
	if not _cron("aura", dt, 1.0): return
	var vivos := _membros_vivos()
	var lutam: Array = t.get("lutam", [])
	var parados := vivos.filter(func(k): return not (k in lutam))
	if not vivos.is_empty(): parados.append("imseti")
	var au: Dictionary = m.get("auras", {})
	for k in lutam:
		var e := _adicional(k)
		if e == null: continue
		if "hapi" in parados: _buff(e, "aura_hapi", 1.5, {"dano": float(au.get("hapi", {}).get("dano", 0.25))})
		if "imseti" in parados: _buff(e, "aura_imseti", 1.5, {"dano_recebido": -float(au.get("imseti", {}).get("reducao_dano", 0.25))})
		if "duamutef" in parados: sim.curar(e, e.hp_max * float(au.get("duamutef", {}).get("cura_frac_s", 0.01)), e, true)
	if "qebehsenuef" in parados:
		var q := _adicional("qebehsenuef")
		for j: Ent in _jogs():
			if q != null and j.pos.distance_to(ctl.centro) > float(au.get("qebehsenuef", {}).get("flechas_longe", 8.0)) and sim.rng.randf() < 0.35:
				sim.aplicar_golpe(q, j, {"mult": 0.6, "elemento": "fisico"})

# ======================================================================= Apófis: a Lanterna de Rá
func _apofis(dt: float) -> void:
	var luz := float(t.get("luz", 100.0))
	luz = maxf(0.0, luz - float(m.get("perde_por_s", 3)) * dt)
	var lant := _v(arena.get("lanterna", [ctl.centro.x, ctl.centro.y]))
	var br: Dictionary = m.get("brasa", {"da": 30})
	for e: Ent in _jogs():
		var tem_brasa := e.buffs.any(func(b): return b["id"] == "brasa")
		if not tem_brasa:
			for p in arena.get("braseiros", []):
				if e.pos.distance_to(_v(p)) <= 1.6:
					var k := "pega_%d" % e.id
					t[k] = float(t.get(k, 0.0)) + dt
					if float(t[k]) >= 1.0:
						t.erase(k); _buff(e, "brasa", 30.0, {"vel_mov": -float(br.get("lento", 0.3))})
						sim.emitir("marca_egito", {"id": e.id, "marca": "brasa", "t": 30.0})
		elif e.pos.distance_to(lant) <= 1.9:
			_tirar_buff(e, "brasa"); sim.emitir("marca_egito", {"id": e.id, "marca": "", "t": 0})
			luz = minf(float(m.get("luz_max", 100)), luz + float(br.get("da", 30)))
			sim.emitir("vfx", {"nome": "lanterna_acende", "pos": lant})
	t["luz"] = luz
	if _cron("luz_tick", dt, 1.0):
		var sr: Dictionary = m.get("sol_de_ra", {"acima": 50, "dano": 0.15})
		for e: Ent in _jogs():
			if luz > float(sr["acima"]): _buff(e, "sol_de_ra", 1.5, {"dano": float(sr["dano"])})
			elif luz <= 0.0: _dano_frac(e, float(m.get("escuro_frac_s", 0.08)), "sombra")
		if luz <= 0.0 and not t.has("avisou_escuro"):
			t["avisou_escuro"] = true; _fala("(a luz apaga; a serpente abre a boca)"); _aviso("A Lanterna apagou: Apófis engole a luz. Levem brasa!")
		elif luz > 0.0: t.erase("avisou_escuro")
		sim.emitir("chefe_barra", {"id": boss.id, "nome": "Luz de Rá", "valor": roundi(luz), "max": int(m.get("luz_max", 100))})
	# Olhar (fase 3): de costas para ele
	var ol: Dictionary = m.get("olhar", {})
	if ctl.fase >= int(ol.get("desde_fase", 3)):
		if t.has("olhar"):
			t["olhar"] -= dt
			if t["olhar"] <= 0.0:
				t.erase("olhar")
				for e: Ent in _jogs():
					if e.facing.dot((boss.pos - e.pos).normalized()) > 0.2:
						sim.aplicar_status(e, "atordoado", float(ol.get("petrifica_s", 4)), boss)
						sim.emitir("marca_egito", {"id": e.id, "marca": "petrificado", "t": float(ol.get("petrifica_s", 4))})
		elif _cron("olhar_cd", dt, float(ol.get("a_cada_s", 25))):
			t["olhar"] = float(ol.get("aviso_s", 3)); _fala("(os olhos acendem)"); _aviso("Não olhe para Apófis! Vire de costas.")
			sim.emitir("vfx", {"nome": "olhos_apofis", "alvo": boss.id})

# ======================================================================= Anúbis: a balança
func _anubis(dt: float) -> void:
	if t.has("pesagem"):
		t["pesagem"] -= dt
		if t["pesagem"] > 0.0: return
		t.erase("pesagem")
		var pratos: Array = arena.get("pratos", [])
		var r := float(arena.get("raio_prato", 3.0))
		var lado := {"coracao": [], "pena": []}
		var fora: Array = []
		for e: Ent in _jogs():
			var mk: String = marcas.get(e.id, "")
			var noC := e.pos.distance_to(_v(pratos[0])) <= r
			var noP := e.pos.distance_to(_v(pratos[1])) <= r
			if (mk == "coracao" and noC) or (mk == "pena" and noP): lado[mk].append(e)
			else: fora.append(e)
			sim.emitir("marca_egito", {"id": e.id, "marca": "", "t": 0})
		marcas.clear()
		for e: Ent in fora: _dano_frac(e, float(m.get("fora_frac", 0.7)))
		var dif: int = lado["coracao"].size() - lado["pena"].size()
		if absi(dif) <= int(m.get("tolerancia", 1)):
			var mt: Dictionary = m.get("maat", {"dano": 0.2, "dur_s": 15})
			for e: Ent in lado["coracao"] + lado["pena"]: _buff(e, "maat", float(mt["dur_s"]), {"dano": float(mt["dano"])})
			_fala("Equilibrada. Por enquanto."); _aviso("A balança ficou equilibrada: Maat (+20% de dano).")
		else:
			var pesado: String = "coracao" if dif > 0 else "pena"
			for e: Ent in lado[pesado]: _dano_frac(e, float(m.get("pesado_frac", 0.5)))
			_fala("PESADO."); _aviso("A balança pendeu para o lado do %s." % ("Coração" if pesado == "coracao" else "Pena"))
			var am := _adicional("ammit")
			if am != null:
				var pp := _v(pratos[0] if pesado == "coracao" else pratos[1])
				sim.deslocar(am, sim.celula_livre_perto(pp), 0.4, {"tipo": "salto"})
		return
	if _cron("balanca", dt, float(m.get("a_cada_s", 30))):
		var js := _jogs(); js.shuffle()
		for i in js.size():
			var mk := "coracao" if i % 2 == 0 else "pena"
			marcas[js[i].id] = mk
			sim.emitir("marca_egito", {"id": js[i].id, "marca": mk, "t": float(m.get("prazo_s", 8))})
		t["pesagem"] = float(m.get("prazo_s", 8))
		_fala("Coração. Pena. Para os pratos."); _aviso("A Pesagem! Vá para o prato da sua marca.")

# ======================================================================= O Faraó Sem Nome: as dez pragas
func _pragas() -> Array:
	var pf: Array = m.get("por_fase", [])
	var v: Array = []
	for i in mini(ctl.fase, pf.size()): v += pf[i]   # as pragas se acumulam (o Egito não melhora)
	return v

func _trevas_mover() -> void:
	var ls: Array = []
	for i in 4:
		ls.append(sim.celula_livre_perto(ctl.centro + Vector2.from_angle(sim.rng.randf() * TAU) * sim.rng.randf_range(2.0, ctl.raio_arena - 3.0)))
	t["lamparinas"] = ls
	sim.emitir("luzes_arena", {"pos": ls, "raio": float(m.get("trevas", {}).get("raio_luz", 3.0))})

func _farao(dt: float) -> void:
	var pr := _pragas()
	if "sangue" in pr and _cron("sangue", dt, float(m.get("sangue", {}).get("cresce_s", 15))) and t["sangue"].size() < 6:
		var p := sim.celula_livre_perto(ctl.centro + Vector2.from_angle(sim.rng.randf() * TAU) * sim.rng.randf_range(2.0, ctl.raio_arena - 3.0))
		t["sangue"].append(_area(p, 2.4, 9999.0, "sangue", func(a):
			for e: Ent in _na_area(a): sim.aplicar_status(e, "cura_reduzida", 1.5, boss)))
	if "piolhos" in pr and _cron("piolhos", dt, 20.0):
		var js := _jogs(); js.shuffle()
		for i in mini(int(m.get("piolhos", {}).get("alvos", 2)), js.size()):
			js[i].status["cegueira"] = {"t": 30.0, "dados": {}, "de": boss.id, "tick": 1.0, "pilhas": 1}
			sim.emitir("status", {"id": js[i].id, "s": "cegueira", "on": true, "t": 30.0})
			sim.emitir_a(js[i], "aviso", {"texto": "Piolhos! Vá para perto de um braseiro."})
	if "piolhos" in pr:
		for e: Ent in _jogs():
			if e.tem("cegueira") and arena.get("braseiros", []).any(func(p): return e.pos.distance_to(_v(p)) <= 2.2):
				e.status.erase("cegueira"); sim.emitir("status", {"id": e.id, "s": "cegueira", "on": false})
	if "peste" in pr:
		# Peste: um jogador por vez fica doente (2% do HP máx por s, 8 s); quem chegar a 2 m dele pega também
		var pe: Dictionary = m.get("peste", {})
		var doentes: Dictionary = t.get("doentes", {})
		if _cron("peste_nova", dt, float(pe.get("a_cada_s", 15))):
			var js := _jogs().filter(func(e: Ent): return not doentes.has(e.id))
			if js.size() > 0:
				var e0: Ent = js[sim.rng.randi() % js.size()]
				doentes[e0.id] = float(pe.get("dur_s", 8)); sim.emitir("marca_egito", {"id": e0.id, "marca": "peste", "t": doentes[e0.id]})
				sim.emitir_a(e0, "aviso", {"texto": "Peste! Fique longe dos outros até passar."})
		if _cron("peste", dt, 1.0):
			for id in doentes.keys():
				var e: Ent = sim.ents.get(id)
				doentes[id] -= 1.0
				if e == null or not e.vivo or doentes[id] <= 0.0:
					doentes.erase(id)
					if e != null: sim.emitir("marca_egito", {"id": e.id, "marca": "", "t": 0})
					continue
				_dano_frac(e, float(pe.get("dano_frac_s", 0.02)), "veneno")
				for o: Ent in _jogs():
					if not doentes.has(o.id) and o.pos.distance_to(e.pos) <= float(pe.get("raio", 2.0)):
						doentes[o.id] = float(pe.get("dur_s", 8)); sim.emitir("marca_egito", {"id": o.id, "marca": "peste", "t": doentes[o.id]})
		t["doentes"] = doentes
	if "trevas" in pr:
		var tv: Dictionary = m.get("trevas", {})
		if _cron("trevas_move", dt, float(tv.get("move_s", 20))): _trevas_mover()
		if _cron("trevas", dt, 1.0):
			for e: Ent in _jogs():
				var luz: bool = t.get("lamparinas", []).any(func(p): return e.pos.distance_to(p) <= float(tv.get("raio_luz", 3.0)))
				if not luz: _dano_frac(e, float(tv.get("fora_frac_s", 0.02)), "sombra")
	if "decima" in pr:
		var dc: Dictionary = m.get("decima", {})
		if t.has("decima"):
			t["decima"] -= dt
			if t["decima"] <= 0.0:
				t.erase("decima")
				var portas: Array = t.get("portas_marcadas", [])
				var cap := {}
				_fala("(o Anjo Destruidor passa)")
				sim.emitir("vfx", {"nome": "anjo_destruidor", "pos": ctl.centro})
				var js := _jogs()
				js.sort_custom(func(a, b): return a.pos.distance_to(ctl.centro) > b.pos.distance_to(ctl.centro))
				for e: Ent in js:
					var salvo := false
					for i in portas.size():
						if e.pos.distance_to(portas[i]) <= 1.9 and int(cap.get(i, 0)) < int(dc.get("por_porta", 3)):
							cap[i] = int(cap.get(i, 0)) + 1; salvo = true; break
					if not salvo: sim.aplicar_dano_puro(e, e.hp_max * 5.0, "sagrado", boss, "normal")
		elif _cron("decima_cd", dt, float(dc.get("a_cada_s", 40))):
			var todas: Array = arena.get("portas", []).map(func(p): return _v(p))
			todas.shuffle()
			var k := clampi(ceili(_jogs().size() / float(dc.get("por_porta", 3))), 1, todas.size())
			t["portas_marcadas"] = todas.slice(0, k)
			t["decima"] = float(dc.get("aviso_s", 6))
			sim.emitir("portas_marcadas", {"pos": t["portas_marcadas"], "t": t["decima"], "por_porta": int(dc.get("por_porta", 3))})
			_fala("Quem vai passar esta noite por cima das portas de vocês?")
			_aviso("A Décima Praga! Fiquem sob uma porta com sangue no lintel (até 3 por porta).")

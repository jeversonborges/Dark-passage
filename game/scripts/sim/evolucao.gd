class_name Evolucao
## Evoluções de classe do nível 50 (design/combate/evolucoes.json). A classe base continua em e.classe
## (recurso, ataque básico e skills base seguem iguais); e.evolucao guarda o caminho escolhido com o Pedro, o Exilado.
## Aqui ficam: escolha e validação, bônus do caminho (atributos e multiplicadores), barra de skills e o efeito
## das 60 skills novas, montado a partir dos campos do JSON (forma, área, alcance, buff...).

const STATUS := {"atordoar": "atordoado", "provocar": "provocado", "preso": "enraizado", "enraizar": "enraizado",
	"lentidao": "lento", "silencio": "silenciado", "marcado": "marcado", "cegueira": "cegueira", "cegueira_inimigos": "cegueira",
	"medo": "atordoado", "medo_fracos": "atordoado", "derrubar_voo": "derrubado"}
const SLOT_EVO := 10      # as skills da evolução ficam nos slots 10..14 (segunda fileira da barra, Shift+1..5)

static var _skills_cache := {}

static func doc() -> Dictionary:
	return Defs.EVOLUCOES

static func defn(id: String) -> Dictionary:
	return Defs.EVOLUCOES.get("evolucoes", {}).get(id, {})

static func de(e: Ent) -> Dictionary:
	return defn(e.evolucao) if e.evolucao != "" else {}

static func nivel_exigido() -> int:
	return int(Defs.EVOLUCOES.get("nivel_evolucao", 50))

static func opcoes(classe: String) -> Array:
	var out: Array = []
	for id in Defs.EVOLUCOES.get("evolucoes", {}):
		if Defs.EVOLUCOES["evolucoes"][id]["classe_base"] == classe: out.append(id)
	return out

static func nome_classe(e: Ent) -> String:
	var d := de(e)
	return d.get("nome", "") if not d.is_empty() else e.classe.capitalize()

## Motivo para recusar a evolução, ou "" se pode.
static func recusa(e: Ent, id: String) -> String:
	var d := defn(id)
	if d.is_empty(): return "Caminho desconhecido."
	if e.evolucao != "": return "Um caminho a gente não desescolhe."
	if d["classe_base"] != e.classe: return "Esse caminho não é da sua classe."
	if e.nivel < nivel_exigido(): return "Volte no nível %d." % nivel_exigido()
	return ""

static func aplicar(sim: WorldSim, e: Ent, id: String) -> bool:
	var r := recusa(e, id)
	if r != "":
		sim.emitir_a(e, "aviso", {"texto": r}); return false
	e.evolucao = id
	e.pontos += int(Defs.EVOLUCOES.get("bonus_ao_evoluir", {}).get("pontos_atributo_extra", 0))
	montar_slots(e)
	Regras.recalc_jogador(e)
	e.hp = e.hp_max
	if e.rec_max > 0.0 and e.classe in ["anjo", "tecnomancer", "humano"]: e.rec = e.rec_max
	sim.emitir("evolucao", {"id": e.id, "evolucao": id, "nome": defn(id)["nome"], "sprite": defn(id).get("sprite", id)})
	sim.emitir_a(e, "aviso", {"texto": "Você agora é %s." % defn(id)["nome"]})
	sim.emitir_a(e, "stats", {"id": e.id})
	return true

# =================================================================== bônus do caminho
## Multiplicador (bônus de toda evolução x bônus do caminho). 1.0 sem evolução.
static func mult(e: Ent, chave: String) -> float:
	if e.evolucao == "": return 1.0
	var base: Dictionary = Defs.EVOLUCOES.get("bonus_ao_evoluir", {})
	return float(base.get(chave, 1.0)) * float(de(e).get("bonus", {}).get(chave, 1.0))

## Soma (crítico, bloqueio, roubo de vida...). 0 sem evolução.
static func soma(e: Ent, chave: String) -> float:
	if e.evolucao == "": return 0.0
	return float(de(e).get("bonus", {}).get(chave, 0.0))

static func atributo(e: Ent, k: String) -> float:
	return soma(e, k)

# =================================================================== barra de skills
## Skills da classe base + as da evolução (cópias marcadas com "_evo").
static func habilidades(e: Ent) -> Array:
	var base: Array = Defs.CLASSES[e.classe]["habilidades"]
	if e.evolucao == "": return base
	if not _skills_cache.has(e.evolucao):
		var lst: Array = []
		for h in de(e).get("habilidades", []):
			var c: Dictionary = h.duplicate(true)
			c["_evo"] = e.evolucao
			if e.classe == "cultista": c["custo"] = float(h.get("custo", 0)) * 0.0025   # o Cultista paga em fração do HP
			lst.append(c)
		_skills_cache[e.evolucao] = lst
	return base + _skills_cache[e.evolucao]

static func montar_slots(e: Ent) -> void:
	e.skills_slots = []
	for h in Defs.CLASSES[e.classe]["habilidades"]: e.skills_slots.append(h["id"])
	if e.evolucao == "": return
	while e.skills_slots.size() < SLOT_EVO: e.skills_slots.append("")
	for h in de(e).get("habilidades", []): e.skills_slots.append(h["id"])

static func tipo(h: Dictionary) -> String:
	if h.get("transformacao", false) or h.has("buff") or h.get("sensacao", "") == "buff": return "proprio"
	if h.has("cura_mult") and not h.has("mult"): return "alvo_aliado" if not h.has("area_raio") else "proprio"
	if h.has("ressuscitar_hp"): return "alvo_aliado"
	if h.has("invocacao") or h.has("invoca"): return "proprio"
	if h.get("forma", "") == "cone" or h.has("espiritos"): return "ponto"
	if h.has("dano") or h.has("meteoros") or h.has("virotes") or h.has("deslocamento"): return "ponto"
	if h.has("area_raio") and h.has("alcance") and not h.has("puxar"): return "ponto"
	if h.has("area_raio") and not h.has("alcance"): return "proprio"
	if h.has("mult") or h.has("efeito") or h.has("mult_por_s"): return "alvo_inimigo"
	return "proprio"

# =================================================================== efeito das skills
static func _vfx(sim: WorldSim, e: Ent, h: Dictionary, d: Dictionary) -> void:
	if h.has("vfx"): d["nome"] = h["vfx"]
	else: d["skill"] = e.evolucao + "/" + h["id"]
	d["de"] = e.id
	sim.emitir("vfx", d)

static func _op(e: Ent, h: Dictionary, extra: Dictionary = {}) -> Dictionary:
	var hb := h
	if h.has("empurrao") and typeof(h["empurrao"]) == TYPE_DICTIONARY:
		hb = h.duplicate(); hb.erase("empurrao")
	var op := Habilidades._op(e, hb, extra)
	var ef := {}
	for k in h.get("efeito", {}):
		if STATUS.has(k): ef[STATUS[k]] = h["efeito"][k]
	for k in ["sangramento", "veneno", "queimadura"]:
		if h.has(k): ef[k] = h[k]
	if h.has("queima"): ef["queimadura"] = h["queima"]
	if extra.has("efeito"): ef.merge(extra["efeito"], true)
	if ef.is_empty(): op.erase("efeito")
	else: op["efeito"] = ef
	if float(h.get("dano_vs_alados_mult", 0)) > 0.0: op["bonus_vs"] = {"tag:alado": float(h["dano_vs_alados_mult"])}
	return op

static func _status_em(sim: WorldSim, e: Ent, a: Ent, h: Dictionary) -> void:
	for k in h.get("efeito", {}):
		if STATUS.has(k): sim.aplicar_status(a, STATUS[k], h["efeito"][k], e)
	if h.has("dano_recebido_extra") and a.vivo:
		var mods := {"dano_recebido": float(h["dano_recebido_extra"])}
		a.buffs.append({"id": "evo_" + h["id"], "t": float(h["efeito"].values()[0]) if h.has("efeito") else 6.0, "dur": 6.0, "mods": mods})

static func _alvos_pt(sim: WorldSim, e: Ent, c: Vector2, raio: float) -> Array:
	return sim.inimigos_de(e, c, raio + 0.3)

static func _ponto(e: Ent, h: Dictionary, alvo: Ent, ponto: Vector2) -> Vector2:
	var p := ponto
	if p.distance_to(e.pos) < 0.3: p = alvo.pos if alvo != null else e.pos + e.facing * 2.0
	var alc := float(h.get("alcance", 0))
	if alc > 0.0 and p.distance_to(e.pos) > alc: p = e.pos + (p - e.pos).normalized() * alc
	return p

static func _buff_mods(bf: Dictionary) -> Dictionary:
	var m := {}
	for k in bf:
		var v = bf[k]
		if typeof(v) == TYPE_BOOL: continue
		match k:
			"dano_mult": m["dano"] = float(v) - 1.0
			"dano_magico_mult": m["dano_magico"] = float(v) - 1.0
			"defesa_mult": m["defesa_pct"] = float(v) - 1.0
			"hp_mult": m["hp_pct"] = float(v) - 1.0
			"velocidade_mult": m["vel"] = float(v) - 1.0
			"velocidade_ataque_mult": m["velocidade_ataque"] = float(v) - 1.0
			"velocidade_ataque": m["vel_ataque_fixa"] = float(v)
			"critico": m["critico"] = float(v)
			"recarga_mult": m["recarga_mult"] = float(v) - 1.0
	return m

static func _invocar(sim: WorldSim, e: Ent, kind: String, nome: String, dur: float, n: int = 1) -> void:
	var dt: Dictionary = Defs.CLASSES["tecnomancer"].get("invocacoes", {}).get("torreta_sentinela", {"intervalo": 1.2, "alcance": 7})
	var mlt := mult(e, "invocacoes_mult")
	for i in n:
		var inv := Ent.new()
		inv.id = sim.novo_id(); inv.tipo = "invocacao"; inv.kind = kind; inv.dono = e.id; inv.nome = nome
		inv.pos = sim.celula_livre_perto(e.pos + Vector2.from_angle(TAU * i / maxf(n, 1)) * 1.4)
		inv.casa = inv.pos
		inv.hp_max = e.hp_max * 0.5 * mlt; inv.hp = inv.hp_max
		inv.dano_min = e.dano_min * 0.45 * mlt; inv.dano_max = e.dano_max * 0.45 * mlt
		inv.intervalo = float(dt.get("intervalo", 1.2)); inv.alcance = float(dt.get("alcance", 7.0))
		inv.vel = 2.8 if kind == "cranio_servo" else 0.0
		inv.nivel = e.nivel; inv.ar = e.ar; inv.er = e.er; inv.critico = 0.05; inv.crit_mult = 1.5
		inv.defesa = e.defesa; inv.elemento = "eletrico"; inv.dura_t = dur; inv.raio = 0.45
		sim.ents[inv.id] = inv
		sim.emitir("surgiu", {"id": inv.id})

## Solta uma skill da evolução. Chamado por Habilidades.usar quando a skill tem "_evo".
static func usar(sim: WorldSim, e: Ent, h: Dictionary, alvo: Ent, ponto: Vector2) -> void:
	var id: String = h["id"]
	var prep := maxf(float(h.get("preparo", h.get("conjuracao", h.get("canalizacao", 0.0)))) * mult(e, "conjuracao_mult"), 0.18)
	var aid := alvo.id if alvo != null else -1
	var dur := float(h.get("duracao", 0.0))
	# ------------------------------------------------ transformações (Forma Vingativa, Forma Colossal)
	if h.get("transformacao", false):
		var mods := _buff_mods(h.get("buff", {}))
		Jogador.add_buff(sim, e, id, dur, mods)
		if h.get("buff", {}).get("imune_controle", false): e.aux["imune_cc"] = true
		if h.get("buff", {}).get("tiros_atravessam", false): e.aux["tiros_atravessam"] = true
		if h.get("buff", {}).has("area_ataque_basico"): e.aux["area_basico"] = float(h["buff"]["area_ataque_basico"])
		var esc0 := e.escala
		e.escala = float(h.get("escala", 1.0)) * esc0
		e.aux["forma"] = id
		e.hp = e.hp_max * e.frac_hp() if e.hp > 0.0 else e.hp
		_vfx(sim, e, h, {"pos": e.pos, "fica": dur})
		sim.emitir("forma", {"id": e.id, "forma": id, "on": true, "escala": e.escala, "t": dur})
		sim.atrasar(dur, func():
			e.escala = esc0; e.aux.erase("forma"); e.aux.erase("imune_cc"); e.aux.erase("tiros_atravessam"); e.aux.erase("area_basico")
			sim.emitir("forma", {"id": e.id, "forma": id, "on": false, "escala": e.escala}))
		return
	# ------------------------------------------------ invocações
	if h.has("invocacao") or h.has("invoca"):
		var lst: Dictionary = h["invoca"] if h.has("invoca") else {h["invocacao"]: 1}
		for k in lst:
			_invocar(sim, e, k, {"torreta_relicario": "Torreta-Relicário", "cranio_servo": "Crânio-Servo"}.get(k, k), dur, int(lst[k]))
		if h.has("sobrecarga"): Jogador.add_buff(sim, e, id, float(h["sobrecarga"]["duracao"]), {"velocidade_ataque": float(h["sobrecarga"]["cadencia_mult"]) - 1.0})
		_vfx(sim, e, h, {"pos": e.pos, "fica": dur})
		return
	# ------------------------------------------------ buffs (próprio ou aliados em volta)
	if h.has("buff") or (h.get("sensacao", "") == "buff" and not h.has("mult")):
		var mods := _buff_mods(h.get("buff", {}))
		if h.has("reducao_dano"): mods["dano_recebido"] = -float(h["reducao_dano"])
		if h.has("reflete") or h.has("reflete_dano"): mods["reflete"] = float(h.get("reflete", h.get("reflete_dano", 0.0)))
		if h.has("bloqueio_frontal"): mods["bloqueio"] = float(h["bloqueio_frontal"]) * 0.5   # de frente bloqueia, pelas costas não: na média, metade
		if h.has("dano_por_inimigo"):   # Ave, Arena!: cada inimigo na arena dá dano ao Gladiador
			var n_in := _alvos_pt(sim, e, e.pos, float(h.get("area_raio", 7))).size()
			mods["dano"] = float(h["dano_por_inimigo"]) * mini(n_in, 6)
			mods["cura_por_abate"] = float(h.get("cura_por_abate", 0.0))
			sim.criar_area({"pos": e.pos, "raio": float(h.get("area_raio", 7)), "dur": dur, "tick": 99.0, "dono": e.id, "tipo": "arena"})
		var quem: Array = [e]
		if h.has("area_raio") and not h.has("provoca_todos"): quem = sim.aliados_de(e, e.pos, float(h["area_raio"]))
		if h.get("ressuscita_todos", false):   # Coro dos Seis Ais: levanta os aliados mortos por perto
			for m: Ent in mortos_perto(sim, e, e.pos, float(h.get("area_raio", 10))):
				ressuscitar(sim, m, float(h.get("hp_ao_voltar", 0.6))); quem.append(m)
		if not e in quem: quem.append(e)
		var bdur := dur if dur > 0.0 else 6.0
		for a: Ent in quem:
			if not mods.is_empty():
				if a.tipo == "jogador": Jogador.add_buff(sim, a, id, bdur, mods)
				else: a.buffs.append({"id": id, "t": bdur, "dur": bdur, "mods": mods})
			if h.has("escudo_mult"):
				var esp: float = e.aux.get("ef", e.stats)["ESP"]
				a.escudo = (esp * 1.5 + e.nivel * 8.0) * float(h["escudo_mult"]) * 0.5; a.escudo_t = bdur
				sim.emitir("escudo", {"id": a.id, "valor": a.escudo, "t": bdur})
			if h.get("cura_total", false): sim.curar(a, a.hp_max, e)
			if h.has("invulneravel"): a.invuln_t = maxf(a.invuln_t, float(h["invulneravel"]))
			if h.get("imune_controle", false):
				a.aux["imune_cc"] = true
				sim.atrasar(bdur, func(): a.aux.erase("imune_cc"))
		if h.has("regen_hp_por_s"):
			var eid := e.id
			sim.criar_area({"pos": e.pos, "raio": 0.0, "dur": bdur, "tick": 1.0, "tipo": "hot", "cada_tick": func(_a):
				var me := sim.valido(eid)
				if me != null: sim.curar(me, me.hp_max * float(h["regen_hp_por_s"]), me, true)})
		if h.has("custo_hp_por_s"):
			var eid2 := e.id
			sim.criar_area({"pos": e.pos, "raio": 0.0, "dur": bdur, "tick": 1.0, "tipo": "dreno", "cada_tick": func(_a):
				var me := sim.valido(eid2)
				if me != null and me.hp > me.hp_max * 0.1: me.hp -= me.hp_max * float(h["custo_hp_por_s"])})
		if h.has("escala"):
			var esc1 := e.escala
			e.escala *= float(h["escala"])
			sim.atrasar(bdur, func(): e.escala = esc1)
		# quem provoca: Trono da Legião, Muro de Vela
		var rp := float(h.get("area_raio", 0.0)) if h.get("provoca_todos", false) else float(h.get("provocar_area_raio", 0.0))
		if rp > 0.0:
			for o in _alvos_pt(sim, e, e.pos, rp): sim.aplicar_status(o, "provocado", minf(bdur, 5.0), e)
		if h.get("imovel", false): e.aux["imovel_t"] = bdur
		_vfx(sim, e, h, {"pos": e.pos, "fica": bdur})
		return
	# ------------------------------------------------ cura e ressurreição
	if h.has("ressuscitar_hp"):   # Levanta-te: o aliado morto mais perto do cursor; sem morto, cura o alvo
		var a2: Ent = alvo if alvo != null else e
		var cand := mortos_perto(sim, e, e.pos, float(h.get("alcance", 6)) + 1.0)
		cand.sort_custom(func(x, y): return x.pos.distance_to(ponto) < y.pos.distance_to(ponto))
		var morto: Ent = cand[0] if cand.size() > 0 else null
		sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "skill": id, "conj": true, "impacto": func():
			if morto != null and not morto.vivo:
				ressuscitar(sim, morto, float(h["ressuscitar_hp"]))
				_vfx(sim, e, h, {"alvo": morto.id})
			elif a2.vivo:
				sim.curar(a2, a2.hp_max * float(h["ressuscitar_hp"]), e)
				_vfx(sim, e, h, {"alvo": a2.id})
		})
		return
	if h.has("cura_mult") and not h.has("mult"):
		var quem2: Array = [alvo if alvo != null else e]
		if h.has("area_raio"):
			quem2 = sim.aliados_de(e, e.pos, float(h["area_raio"]))
			if not e in quem2: quem2.append(e)
		sim.iniciar_acao(e, {"preparo": prep, "rec": 0.25, "skill": id, "conj": true, "impacto": func():
			for a: Ent in quem2:
				if a.vivo: sim.curar(a, Habilidades.cura_valor(e, float(h["cura_mult"])), e)
			if h.has("reparo_invocacoes_mult"):
				for o: Ent in sim.ents.values():
					if o.tipo == "invocacao" and o.dono == e.id: sim.curar(o, Habilidades.cura_valor(e, float(h["reparo_invocacoes_mult"])), e)
			_vfx(sim, e, h, {"pos": e.pos})
		})
		return
	# ------------------------------------------------ Bomba Atômica: centro mata, borda arranha, radiação fica
	if h.has("dano"):
		var p := _ponto(e, h, alvo, ponto)
		sim.iniciar_acao(e, {"preparo": 0.3, "rec": 0.3, "ponto": p, "skill": id, "impacto": func():
			sim.emitir("vfx", {"nome": h.get("vfx_projetil", "herege_bomba_arremesso"), "pos": e.pos, "para": p, "de": e.id})
			sim.atrasar(float(h.get("voo", 0.9)), func(): _explodir(sim, e, h, p))
		})
		return
	# ------------------------------------------------ Espíritos Malignos: voam em volta, cada alvo leva até N acertos
	if h.has("espiritos"):
		var raio := float(h.get("raio", 4.5))
		var n := int(h["espiritos"])
		var porm := int(h.get("acertos_max_por_alvo", 2))
		var cont := {}
		_vfx(sim, e, h, {"pos": e.pos, "fica": 1.6})
		for i in n:
			sim.atrasar(0.08 * i, func(): _espirito(sim, e, h, i, n, raio, porm, cont))
		return
	# ------------------------------------------------ chuvas (meteoros, virotes, sete espadas): N impactos na área
	var chuva := int(h.get("meteoros", h.get("virotes", h.get("golpes", 0) if h.has("area_raio") and h.has("alcance") else 0)))
	if chuva > 1:
		var p2 := _ponto(e, h, alvo, ponto)
		if h.has("area_raio") and not h.has("alcance"): p2 = e.pos
		var ar := float(h["area_raio"])
		var mx := float(h["mult"]) if not h.has("virotes") else float(h["mult"])
		var ivl := 1.6 / chuva
		sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "ponto": p2, "skill": id, "conj": prep > 0.4, "impacto": func():
			_vfx(sim, e, h, {"pos": p2, "fica": 1.8})
			for i in chuva:
				var q := p2 + Vector2.from_angle(sim.rng.randf() * TAU) * sqrt(sim.rng.randf()) * ar
				var r_imp := maxf(1.2, ar * 0.35)
				if h.has("golpes"):   # Sete Espadas: em círculo, uma por vez, a última no centro
					q = p2 if i == chuva - 1 else p2 + Vector2.from_angle(TAU * i / (chuva - 1)) * ar * 0.6
					r_imp = ar * 0.45
				sim.atrasar(ivl * i, func(): _impacto_chuva(sim, e, h, q, r_imp, p2, ar, mx, i))
		})
		return
	# ------------------------------------------------ leque (cone)
	if h.get("forma", "") == "cone":
		var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
		if alvo != null and ponto.distance_to(e.pos) <= 0.3: dir = (alvo.pos - e.pos).normalized()
		e.facing = dir
		var vezes := maxi(1, int(h.get("golpes", 1)))
		sim.iniciar_acao(e, {"preparo": maxf(prep, 0.22), "rec": 0.3, "dir": dir, "ponto": e.pos + dir, "skill": id, "anim": "attack", "impacto": func():
			for i in vezes:
				sim.atrasar(0.07 * i, func(): Habilidades.area_nivel5(sim, e, h, "cone", e.pos, dir))
			if h.has("cura_aliados_mult"):
				for a: Ent in sim.aliados_de(e, e.pos, float(h.get("raio", 3.0)) + 2.0): sim.curar(a, Habilidades.cura_valor(e, float(h["cura_aliados_mult"])), e)
		})
		return
	# ------------------------------------------------ dano contínuo (turíbulo, órbitas, sacos de ácido, enxame)
	if h.has("mult_por_s"):
		var segue: Ent = e if not h.has("alcance") else alvo
		if segue == null: segue = e
		var sid := segue.id
		var r3 := float(h.get("area_raio", 1.2))
		var t3 := dur if dur > 0.0 else 6.0
		_vfx(sim, e, h, {"alvo": sid, "fica": t3})
		var segue_f := func(a):
			var s := sim.valido(sid)
			if s != null: a["pos"] = s.pos
		sim.criar_area({"pos": segue.pos, "raio": r3, "dur": t3, "tick": 1.0, "dono": e.id, "tipo": "evo_" + id, "cada_tick": segue_f,
			"op": _op(e, h, {"mult": float(h["mult_por_s"]) * mult(e, "dano_continuo_mult"), "area": true, "nunca_erra": true, "sensacao": "dano_tempo", "postura": 0.0, "sem_recurso": true})})
		return
	# ------------------------------------------------ área no ponto (orbe, canhão, estrela, versículo, dobre)
	if h.has("area_raio") and h.has("mult"):
		var p4 := _ponto(e, h, alvo, ponto) if h.has("alcance") else e.pos
		if h.has("deslocamento"):   # Queda do Arcanjo: salta até o ponto (no máximo o deslocamento) e cai em cima
			p4 = _ponto(e, {"alcance": h["deslocamento"]}, alvo, ponto)
			sim.deslocar(e, p4, 0.35, {"tipo": id, "anim": "dash", "atravessa": true})
			p4 = e.deslocando.get("para", p4)
		var ar4 := float(h["area_raio"])
		sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "ponto": p4, "skill": id, "conj": prep > 0.4, "impacto": func():
			_vfx(sim, e, h, {"pos": p4})
			var primeiro := true
			for o: Ent in _alvos_pt(sim, e, p4, ar4):
				sim.aplicar_golpe(e, o, _op(e, h, {"area": true, "empurrao_de": p4, "sem_recurso": not primeiro}))
				primeiro = false
			if h.has("chao_amargo_s") or h.has("chao_em_chamas_s"):
				var dch := float(h.get("chao_amargo_s", h.get("chao_em_chamas_s", 3.0)))
				sim.criar_area({"pos": p4, "raio": ar4 * 0.8, "dur": dch, "tick": 0.5, "dono": e.id, "tipo": "radiacao" if h.has("chao_amargo_s") else "fogo",
					"op": _op(e, h, {"mult": 0.15, "area": true, "nunca_erra": true, "sensacao": "dano_tempo", "postura": 0.0, "sem_recurso": true})})
		})
		return
	# ------------------------------------------------ debuff em área (provocação, sermão, grito, rede)
	if h.has("efeito") and not h.has("mult") and h.has("area_raio"):
		var p5 := _ponto(e, h, alvo, ponto) if h.has("alcance") else e.pos
		for o: Ent in _alvos_pt(sim, e, p5, float(h["area_raio"])): _status_em(sim, e, o, h)
		if h.has("reducao_dano"): Jogador.add_buff(sim, e, id, 4.0, {"dano_recebido": -float(h["reducao_dano"])})
		_vfx(sim, e, h, {"pos": p5})
		return
	# ------------------------------------------------ mobilidade/furtividade (Manto de Sombra)
	if h.get("sensacao", "") == "mobilidade" and not h.has("mult"):
		e.aux["bonus_prox"] = float(h.get("primeiro_golpe_mult", 1.5)) - 1.0; e.aux["bonus_prox_t"] = dur if dur > 0.0 else 4.0
		e.invuln_t = maxf(e.invuln_t, 0.4)
		Jogador.add_buff(sim, e, id, dur if dur > 0.0 else 4.0, {"vel": 0.2})
		_vfx(sim, e, h, {"pos": e.pos})
		return
	# ------------------------------------------------ alvo único (golpe, tiro, arpão, marca)
	if alvo == null: return
	if not h.has("mult"):
		_status_em(sim, e, alvo, h)
		if h.get("puxar", false) and alvo.tipo != "chefe" and alvo.arquetipo != "elite":
			sim.deslocar(alvo, e.pos + (alvo.pos - e.pos).normalized() * 1.2, 0.2, {"tipo": "puxao"})
		_vfx(sim, e, h, {"alvo": aid})
		return
	if h.get("teleporte_atras", false):
		var atras := alvo.pos - (e.pos - alvo.pos).normalized() * (alvo.raio + 0.6)
		e.pos = sim.celula_livre_perto(atras, 1.5)
		e.facing = (alvo.pos - e.pos).normalized()
		sim.emitir("teleporte", {"id": e.id, "pos": e.pos})
	var vezes2 := maxi(1, int(h.get("golpes", 1)))
	var dist := float(h.get("alcance", 1.5)) > 2.5
	sim.iniciar_acao(e, {"preparo": prep, "rec": 0.3, "alvo": aid, "skill": id, "conj": prep > 0.4, "impacto": func():
		for i in vezes2:
			sim.atrasar(0.11 * i, func(): _golpe_unico(sim, e, h, aid, i, dist))
		_vfx(sim, e, h, {"alvo": aid})
	})


static func _explodir(sim: WorldSim, e: Ent, h: Dictionary, p: Vector2) -> void:
	var dn: Dictionary = h["dano"]
	sim.emitir("vfx", {"nome": h.get("vfx", "herege_bomba_explosao"), "pos": p, "de": e.id})
	for o: Ent in _alvos_pt(sim, e, p, float(dn["raio"])):
		var d := o.pos.distance_to(p)
		var t := clampf((d - float(dn["raio_centro"])) / maxf(float(dn["raio"]) - float(dn["raio_centro"]), 0.1), 0.0, 1.0)
		var m := lerpf(float(dn["mult_centro"]), float(dn["mult_borda"]), t)
		sim.aplicar_golpe(e, o, _op(e, h, {"mult": m, "area": true, "nunca_erra": true, "empurrao": 14.0 * (1.0 - t), "empurrao_de": p}))
	if h.has("radiacao"):
		var rd: Dictionary = h["radiacao"]
		sim.criar_area({"pos": p, "raio": float(rd["raio"]), "dur": float(rd["duracao"]), "tick": 1.0, "dono": e.id, "tipo": "radiacao",
			"op": _op(e, h, {"mult": float(rd.get("dano_por_s_mult", 0.3)), "area": true, "nunca_erra": true, "sensacao": "dano_tempo", "postura": 0.0, "sem_recurso": true, "elemento": "radiacao",
				"efeito": {"cura_reduzida": 1.5}})})
		sim.emitir("vfx", {"nome": h.get("vfx_chao", "herege_radiacao"), "pos": p, "de": e.id, "fica": float(rd["duracao"])})

static func _espirito(sim: WorldSim, e: Ent, h: Dictionary, i: int, n: int, raio: float, porm: int, cont: Dictionary) -> void:
	if not e.vivo: return
	var c := e.pos + Vector2.from_angle(TAU * i / n) * raio * 0.6
	for o: Ent in _alvos_pt(sim, e, c, raio * 0.55):
		if int(cont.get(o.id, 0)) >= porm: continue
		cont[o.id] = int(cont.get(o.id, 0)) + 1
		sim.aplicar_golpe(e, o, _op(e, h, {"area": true, "nunca_erra": true, "sem_recurso": true}))
		if h.has("vfx_impacto"): sim.emitir("vfx", {"nome": h["vfx_impacto"], "alvo": o.id, "de": e.id})
		break

static func _impacto_chuva(sim: WorldSim, e: Ent, h: Dictionary, q: Vector2, r_imp: float, p2: Vector2, ar: float, mx: float, i: int) -> void:
	if not e.vivo: return
	for o: Ent in _alvos_pt(sim, e, q, r_imp):
		sim.aplicar_golpe(e, o, _op(e, h, {"mult": mx, "area": true, "nunca_erra": true, "sem_recurso": i > 0}))
		if h.has("derruba_voadores") and "alado" in o.tags: sim.aplicar_status(o, "derrubado", float(h["derruba_voadores"]), e)
	if h.has("cura_aliados_por_golpe"):
		for a: Ent in sim.aliados_de(e, p2, ar + 2.0): sim.curar(a, a.hp_max * float(h["cura_aliados_por_golpe"]), e, true)

static func _golpe_unico(sim: WorldSim, e: Ent, h: Dictionary, aid: int, i: int, dist: bool) -> void:
	var a := sim.valido(aid)
	if a == null or not e.vivo: return
	var ex := {"sem_recurso": i > 0}
	if h.get("puxar", false): ex["puxa_para"] = 1.2
	if h.has("execucao_abaixo_hp") and a.tipo != "chefe" and a.frac_hp() <= float(h["execucao_abaixo_hp"]): ex["mult"] = 999.0
	if dist: sim.lancar(e, {"vel": 20.0, "alvo": aid, "vfx": "bala", "perfura": h.get("atravessa", false)}, _op(e, h, ex))
	else: sim.aplicar_golpe(e, a, _op(e, h, ex))
	if h.has("dano_recebido_extra"): _status_em(sim, e, a, h)


# =================================================================== passivas (uma por caminho, "passiva" no JSON)
static func passiva(e: Ent) -> String:
	return de(e).get("passiva", {}).get("id", "") if e.evolucao != "" else ""

## Buff sem aviso ao cliente (passivas renovadas a cada segundo).
static func _buff_quieto(e: Ent, id: String, dur: float, mods: Dictionary) -> void:
	for b in e.buffs:
		if b["id"] == id:
			b["t"] = dur
			if b["mods"] != mods:
				b["mods"] = mods
				if e.tipo == "jogador": Regras.recalc_jogador(e)
			return
	e.buffs.append({"id": id, "t": dur, "dur": dur, "mods": mods})
	if e.tipo == "jogador": Regras.recalc_jogador(e)

static func _sagrado(a: Ent) -> bool:
	return a.classe == "anjo" or a.kind.begins_with("nao_julgado") or "sagrado" in a.tags

static func _alado(a: Ent) -> bool:
	return "alado" in a.tags or a.classe in ["anjo", "demonio"]

## Chamado todo passo do jogador; as auras rodam 1 vez por segundo.
static func passo(sim: WorldSim, e: Ent, dt: float) -> void:
	if e.evolucao == "" or not e.vivo: return
	e.aux["evo_t"] = float(e.aux.get("evo_t", 0.0)) + dt
	if e.aux["evo_t"] < 1.0: return
	e.aux["evo_t"] = 0.0
	match passiva(e):
		"hoste_em_marcha":   # aliados a 6 m: +8% de defesa e 1% de HP/s em combate
			if e.em_combate_t < 5.0:
				for a: Ent in sim.aliados_de(e, e.pos, 6.0):
					if a.tipo in ["jogador", "invocacao"]:
						_buff_quieto(a, "hoste_em_marcha", 1.6, {"defesa_pct": 0.08})
						sim.curar(a, a.hp_max * 0.01, e, true)
		"trono_vazio":   # +3% de redução por inimigo a 4 m, até 15%
			var n := sim.inimigos_de(e, e.pos, 4.0).size()
			if n > 0: _buff_quieto(e, "trono_vazio", 1.6, {"dano_recebido": -minf(0.15, 0.03 * n)})
		"agua_amarga":   # alvos com Amargo curam 30% menos; cada acúmulo cura o Profeta 0,5%/s
			var st: Dictionary = e.aux.get("amargo_alvos", {})
			var tot := 0
			for id in st.keys():
				var a := sim.valido(id)
				if a == null or float(st[id]["ate"]) < sim.tempo: st.erase(id); continue
				tot += int(st[id]["n"])
				sim.aplicar_status(a, "cura_reduzida", 1.5, e)
			if tot > 0: sim.curar(e, e.hp_max * 0.005 * tot, e, true)
		"o_amargo_venceu":   # abaixo de 50%: +20% de dano e 5% de roubo de vida
			if e.frac_hp() < 0.5: _buff_quieto(e, "o_amargo_venceu", 1.6, {"dano": 0.2, "roubo_vida": 0.05})
		"liturgia_da_maquina":   # 2%/s nas invocações dele e nos aliados a 6 m
			for o: Ent in sim.ents.values():
				if o.vivo and ((o.tipo == "invocacao" and o.dono == e.id) or (o.tipo == "jogador" and o.lado() == e.lado() and o.pos.distance_to(e.pos) <= 6.0)):
					sim.curar(o, o.hp_max * 0.02, e, true)

## Defesa do alvo que o golpe ignora (Balas Bentas).
static func pen_defesa(atk: Ent, op: Dictionary) -> float:
	return 0.15 if passiva(atk) == "balas_bentas" and not op.get("magico", false) else 0.0

## Multiplicador de dano das passivas do atacante.
static func mult_golpe(atk: Ent, alvo: Ent, op: Dictionary) -> float:
	match passiva(atk):
		"colheita": return 1.25 if alvo.frac_hp() < 0.3 else 1.0
		"balas_bentas": return 1.3 if _alado(alvo) else 1.0
		"sino_derretido": return 1.2 if op.get("area", false) and _sagrado(alvo) else 1.0
	return 1.0

## Depois de um golpe que acertou (efeitos de controle e marcas das passivas).
static func apos_golpe(sim: WorldSim, atk: Ent, alvo: Ent, op: Dictionary) -> void:
	if not alvo.vivo: return
	match passiva(atk):
		"sino_derretido":
			if op.get("area", false) and _sagrado(alvo): sim.aplicar_status(alvo, "atordoado", 0.3, atk)
		"a_plateia":   # Fúria cheia: o próximo golpe atordoa (gasta metade da Fúria)
			if atk.rec >= atk.rec_max and not op.get("sem_recurso", false):
				sim.aplicar_status(alvo, "atordoado", 1.0, atk); atk.rec -= atk.rec_max * 0.5
		"agua_amarga":
			for h in de(atk).get("habilidades", []):
				if h["id"] == op.get("skill", "") and h.has("acumulos_amargo"):
					var st: Dictionary = atk.aux.get("amargo_alvos", {})
					var cur: Dictionary = st.get(alvo.id, {"n": 0})
					st[alvo.id] = {"n": mini(10, int(cur["n"]) + int(h["acumulos_amargo"])), "ate": sim.tempo + 8.0}
					atk.aux["amargo_alvos"] = st

## O jogador bloqueou um golpe (bloqueio do caminho ou Muro de Vela).
static func bloqueou(sim: WorldSim, e: Ent, atk: Ent) -> void:
	match passiva(e):
		"trono_vazio":
			if atk != null and atk.vivo: sim.aplicar_dano_puro(atk, atk.dano_medio() * 0.2, "fogo", e, "normal")
		"a_plateia":
			e.rec = minf(e.rec_max, e.rec + 5.0)

## Cura que passa do HP máximo vira escudo (Seis Asas).
static func sobrecura(sim: WorldSim, alvo: Ent, de_quem: Ent, sobra: float) -> void:
	if passiva(de_quem) != "seis_asas" or sobra < 1.0: return
	alvo.escudo = minf(alvo.hp_max * 0.2, alvo.escudo + sobra); alvo.escudo_t = 6.0
	sim.emitir("escudo", {"id": alvo.id, "valor": alvo.escudo, "t": 6.0})

## Custo de uma skill depois das passivas (Três Auréolas: a cada 3 magias, a próxima sai de graça e com +40%).
static func custo(e: Ent, cst: float) -> float:
	if passiva(e) != "tres_aureolas" or cst <= 0.0: return cst
	var n := int(e.aux.get("aureolas", 0)) + 1
	if n > 3:
		e.aux["aureolas"] = 0
		e.aux["bonus_prox"] = 0.4; e.aux["bonus_prox_t"] = 4.0
		return 0.0
	e.aux["aureolas"] = n
	return cst

static func abateu(sim: WorldSim, e: Ent, morto: Ent) -> void:
	match passiva(e):
		"colheita": e.cds.erase("passo_sombrio")
		"trofeu":   # alvo marcado (preso, lento ou marcado pelo Caçador) vira troféu: +2% de dano por 30 s, até 10
			if morto.tem("marcado") or morto.tem("lento") or morto.tem("enraizado"):
				var n := 1
				for b in e.buffs:
					if b["id"] == "trofeu": n = mini(10, int(roundf(float(b["mods"].get("dano", 0.0)) / 0.02)) + 1)
				Jogador.add_buff(sim, e, "trofeu", 30.0, {"dano": 0.02 * n})

# =================================================================== ressurreição (Coro dos Seis Ais, Levanta-te)
static func mortos_perto(sim: WorldSim, e: Ent, p: Vector2, r: float) -> Array:
	var out: Array = []
	for o: Ent in sim.ents.values():
		if o.tipo == "jogador" and not o.vivo and o.lado() == e.lado() and o.pos.distance_to(p) <= r: out.append(o)
	return out

static func ressuscitar(sim: WorldSim, a: Ent, frac: float) -> void:
	if a.vivo: return
	a.vivo = true; a.renascer_t = 0.0
	a.hp = maxf(1.0, a.hp_max * frac); a.invuln_t = maxf(a.invuln_t, 2.0)
	a.acao = {}; a.caminho.clear()
	sim.emitir("reviveu", {"id": a.id, "no_lugar": true})

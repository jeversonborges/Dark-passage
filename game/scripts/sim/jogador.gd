class_name Jogador
## Tudo que é do jogador no servidor: comandos, ataque básico, habilidades, recursos, itens, morte, XP e save.

const NIVEIS_SKILL := [1, 3, 5, 6, 9, 12]
const CD_POCAO := 1.0          # recarga compartilhada das poções (farm_auto.json)
# modo automático (farm_auto.json -> modo_automatico)
const AUTO_RAIO := 6.0
const AUTO_VIDA := 0.5
const AUTO_RECURSO := 0.25
const AUTO_RETOMA := 0.5
const POCOES_VIDA := ["pocao_vida_m", "pocao_vida_p", "tonico_graxa", "hostia_negra", "caldo_cardo_comum", "pao_duro"]
const POCOES_RECURSO := ["pocao_recurso_m", "pocao_recurso_p"]

static func criar(sim: WorldSim, classe: String, nome: String, salvo: Dictionary = {}) -> Ent:
	var c: Dictionary = Defs.CLASSES[classe]
	var e := Ent.new()
	e.id = sim.novo_id(); e.tipo = "jogador"; e.kind = classe; e.classe = classe; e.nome = nome
	e.faccao = "arautos" if c["faccao"] == "arautos" else "vigilia"
	e.stats = c["atributos_iniciais"].duplicate()
	for k in e.stats: e.stats[k] = float(e.stats[k])
	e.raio = 0.35
	Evolucao.montar_slots(e)
	if salvo.is_empty():
		var arma := _arma_inicial(classe)
		if arma != "": e.equip["arma"] = Itens.novo(arma)
		if c.get("escudo_inicial") is Dictionary:   # Warlord: escudo de ferro pintado na mão de trás
			var esc := _id_por_nome(c["escudo_inicial"]["nome"])
			if esc != "": e.equip["segunda_mao"] = Itens.novo(esc)
		e.inv = []
		# kit inicial do farm_auto.json: 20 de vida e 10 de recurso (o Cultista paga em HP: mais vida no lugar)
		for it in [["pocao_vida_p", 20], ["pocao_recurso_p", 10] if classe != "cultista" else ["pocao_vida_p", 10]]:
			Itens.guardar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, Itens.novo(it[0], it[1]))
		if classe == "humano": e.municao = int(c["recurso"]["municao"]["inicial"])
		e.ouro = 30
	else:
		carregar(e, salvo)
		Evolucao.montar_slots(e)
	Regras.recalc_jogador(e)
	e.hp = e.hp_max
	if salvo.is_empty():
		match classe:
			"anjo": e.rec = 50.0
			"tecnomancer", "humano": e.rec = e.rec_max
			_: e.rec = 0.0
	else:
		e.rec = e.rec_max if classe in ["anjo", "tecnomancer", "humano"] else 0.0
	return e

static func _id_por_nome(nome: String) -> String:
	var n := _norm(nome)
	for id in Defs.ITENS:
		if _norm(str(Defs.ITENS[id].get("nome", ""))) == n: return id
	return ""

static func _arma_inicial(classe: String) -> String:
	var alvo: String = Defs.CLASSES[classe]["arma_inicial"]["nome"]
	var por_nome := _id_por_nome(alvo)
	if por_nome != "": return por_nome
	for id in Defs.POR_TAG.get("equip:faixa1", []):
		var cl = Defs.ITENS[id].get("classes")
		if cl is Array and classe in cl and Defs.ITENS[id].get("slot") == "arma" and int(Defs.ITENS[id].get("nivel", 1)) == 1: return id
	return ""

static func _norm(s: String) -> String:
	var r := s.to_lower()
	for p in [["á", "a"], ["à", "a"], ["ã", "a"], ["â", "a"], ["é", "e"], ["ê", "e"], ["í", "i"], ["ó", "o"], ["õ", "o"], ["ô", "o"], ["ú", "u"], ["ç", "c"]]:
		r = r.replace(p[0], p[1])
	return r

static func entrar(sim: WorldSim, e: Ent, mapa: String, pos: Vector2) -> void:
	sim.jogador_id = e.id
	sim.ents[e.id] = e
	e.pos = pos
	sim.carregar_mapa(mapa)
	e.pos = sim.celula_livre_perto(pos)
	Familiar.criar(sim, e)   # o familiar do Cultista nasce com ele (0.8.9); criar() não duplica
	e.caminho.clear(); e.acao = {}; e.alvo = -1
	sim.emitir("surgiu", {"id": e.id})
	_checar_zona(sim, e)

# =================================================================== passo
static func passo(sim: WorldSim, e: Ent, dt: float) -> void:
	_regen(sim, e, dt)
	Demiurgo.aura(sim, e, dt)   # Aura Demiúrgica (tick de 1 s)
	Habilidades.estandarte_tick(sim, e, dt)   # Estandarte da Ruína (Warlord)
	if e.buffs.size() > 0:
		var mudou := false
		for b in e.buffs.duplicate():
			b["t"] -= dt
			if b["t"] <= 0.0: e.buffs.erase(b); mudou = true; sim.emitir_a(e, "buff", {"id": e.id, "buff": b["id"], "on": false})
		if mudou: Regras.recalc_jogador(e)
	for k in ["pocao"]:
		if e.aux.has("cd_" + k): e.aux["cd_" + k] -= dt
	if e.aux.get("bonus_prox_t", 0.0) > 0.0: e.aux["bonus_prox_t"] -= dt
	if e.aux.get("imovel_t", 0.0) > 0.0: e.aux["imovel_t"] -= dt   # Trono da Legião: sentado no trono
	Evolucao.passo(sim, e, dt)
	Evasao.passo(e, dt)
	for h in Defs.CLASSES[e.classe]["habilidades"]:
		if h.has("cargas"):
			var k: String = "cargas_" + h["id"]
			if e.cds.has(h["id"]): e.aux[k] = int(h["cargas"]) if e.cds[h["id"]] <= dt else 0
			elif int(e.aux.get(k, h["cargas"])) < int(h["cargas"]):
				e.aux["recarga_carga_" + h["id"]] = e.aux.get("recarga_carga_" + h["id"], 0.0) - dt
				if e.aux["recarga_carga_" + h["id"]] <= 0.0: e.aux[k] = int(e.aux.get(k, 0)) + 1
	_checar_zona(sim, e)
	# Amargo: a partir de 7 fere; na tempestade da borda o vento segura o passo
	var am := sim.amargo_em(e.pos)
	if am != int(e.aux.get("amargo", 0)):
		e.aux["amargo"] = am
		sim.emitir_a(e, "amargo", {"nivel": am})
	if am >= 7 and e.vivo:
		e.aux["amargo_t"] = float(e.aux.get("amargo_t", 0.0)) + dt
		if e.aux["amargo_t"] >= 1.0:
			e.aux["amargo_t"] = 0.0
			var dv := e.hp_max * 0.025 * (am - 6) * (1.0 - Evolucao.soma(e, "resistencia_amargo"))   # Profeta do Amargo resiste
			if dv > 0.0: sim.aplicar_dano_puro(e, dv, "veneno", null, "dano_tempo")
	# canalização (baú, vela de retorno)
	if not e.interagindo.is_empty():
		e.interagindo["t"] += dt
		if e.interagindo["t"] >= e.interagindo["dur"]:
			var it := e.interagindo
			e.interagindo = {}
			sim.emitir("canal_fim", {"id": e.id, "ok": true})
			(it["fim"] as Callable).call()
		return
	var auto_on: bool = e.aux.get("auto", false)
	if auto_on or cfg_auto(e)["pocao_sempre"]: _auto_pocoes(sim, e, auto_on)
	if not e.pronto():
		return
	if e.tem("provocado") and false: pass
	# habilidade pedida fora de alcance: anda até o alcance (buffer de 2 s)
	if not e.buffer_skill.is_empty():
		e.buffer_skill["t"] -= dt
		if e.buffer_skill["t"] <= 0.0: e.buffer_skill = {}
		elif _tentar_skill(sim, e, e.buffer_skill["slot"], e.buffer_skill["alvo"], e.buffer_skill["ponto"], true): e.buffer_skill = {}
	# interação pendente (NPC, baú, objeto, portal)
	if e.aux.has("interagir"):
		var o: Ent = sim.ents.get(e.aux["interagir"])
		if o == null: e.aux.erase("interagir")
		elif e.pos.distance_to(o.pos) <= 1.4 + o.raio:
			e.aux.erase("interagir"); e.caminho.clear()
			e.facing = (o.pos - e.pos).normalized() if o.pos != e.pos else e.facing
			interagir(sim, e, o)
			return
		elif e.caminho.is_empty(): sim.ir_para(e, o.pos)
	if e.aux.has("pegar"):
		var c: Dictionary = sim.chao.get(e.aux["pegar"], {})
		if c.is_empty(): e.aux.erase("pegar")
		elif e.pos.distance_to(c["pos"]) <= 1.0:
			e.aux.erase("pegar"); e.caminho.clear(); pegar_chao(sim, e, c["id"])
		elif e.caminho.is_empty(): sim.ir_para(e, c["pos"])
	if e.aux.get("auto", false): _auto(sim, e, dt)
	elif e.aux.has("auto_centro"): e.aux.erase("auto_centro")
	# ataque básico em loop
	if e.alvo != -1:
		var al := sim.valido(e.alvo)
		if al == null or not al.alvejavel:
			e.alvo = -1
		else:
			var alc := alcance_basico(e)
			var d := e.pos.distance_to(al.pos) - al.raio
			if d <= alc and (alc < 2.0 or sim.visao(e.pos, al.pos)):
				e.caminho.clear()
				if e.cd_basico <= 0.0: ataque_basico(sim, e, al)
				return
			elif not e.no_lugar:
				if e.caminho.is_empty() or e.aux.get("repath", 0.0) <= 0.0:
					sim.ir_para(e, al.pos); e.aux["repath"] = 0.4
				e.aux["repath"] = e.aux.get("repath", 0.0) - dt
	sim.mover_ao_longo(e, dt, 1.0 - clampf((am - 5) * 0.13, 0.0, 0.55))

static func _checar_zona(sim: WorldSim, e: Ent) -> void:
	var z := sim.zona_em(e.pos)
	if z != e.zona:
		e.zona = z
		var primeira := not e.vistas.has(z)
		e.vistas[z] = true
		sim.emitir_a(e, "zona", {"id": z, "primeira": primeira})
		Missoes.evento(sim, e, "explorar", z)

static func _regen(sim: WorldSim, e: Ent, dt: float) -> void:
	Demiurgo.sopro(e, dt)   # Sopro do Primeiro Dia
	var c: Dictionary = Defs.CLASSES[e.classe]
	var rc: Dictionary = c["recurso"]
	var fora := e.em_combate_t >= float(Defs.FORM["regeneracao"]["segundos_para_sair_de_combate"])
	if fora and e.hp < e.hp_max:
		var mult := 2.5 if e.classe == "mutante" and e.nivel >= 12 else 1.0
		if sim.zona_segura(e.pos): mult *= 3.0
		e.hp = minf(e.hp_max, e.hp + e.hp_max * 0.02 * mult * dt)
	match e.classe:
		"anjo": e.rec = minf(e.rec_max, e.rec + float(rc["regen_por_s"]) * dt)
		"tecnomancer":
			var r := float(rc["regen_por_s"])
			if e.caminho.is_empty() and e.acao.is_empty():
				e.aux["parado_t"] = e.aux.get("parado_t", 0.0) + dt
				if e.aux["parado_t"] >= 2.0: r += float(rc["regen_extra_por_s"])
			else: e.aux["parado_t"] = 0.0
			e.rec = minf(e.rec_max, e.rec + r * dt)
		"humano": e.rec = minf(e.rec_max, e.rec + float(rc["folego"]["regen_por_s"]) * dt)
		"mutante", "demonio":
			if fora: e.rec = maxf(0.0, e.rec - float(rc["decai_por_s_fora_de_combate"]) * dt)
		"warlord":
			if fora: e.rec = maxf(0.0, e.rec - float(rc["decai_por_s_fora_de_combate"]) * dt)
			# Coroa de Ferro (nível 20): conta os inimigos a até 3 m, até 5, para a defesa (regras.gd)
			e.aux["coroa_n"] = mini(5, sim.inimigos_de(e, e.pos, 3.0).size()) if e.nivel >= 20 else 0

static func alcance_basico(e: Ent) -> float:
	if e.classe == "humano":
		var ab: Dictionary = Defs.CLASSES["humano"]["alcance_basico"]
		return float(ab["tiro"]) if e.municao > 0 else float(ab["espada"])
	return e.alcance

# =================================================================== modo automático (tecla Z)
## Ajudante de farm em spot (farm_auto.json): caça no raio escolhido em volta de onde foi ligado, usa as skills que o
## jogador marcou (clique direito no slot), junta os drops e bebe poção sozinho. Liga/desliga com o comando "auto";
## clicar para andar ou atacar desliga. Shift+Z abre a janela de ajustes (comando "auto_cfg").
## Esta lógica nunca chama cmd_mover/cmd_atacar (que desligam o modo): mexe em e.alvo e no caminho direto.
const AUTO_PADRAO := {"vida": AUTO_VIDA, "recurso": AUTO_RECURSO, "raio": AUTO_RAIO, "juntar": "tudo", "pocao_sempre": true, "area_min": 2}
const AUTO_LIMITES := {"vida": [0.2, 0.8], "recurso": [0.1, 0.6], "raio": [3.0, 10.0], "area_min": [1, 3]}
const AUTO_JUNTAR := ["tudo", "bons", "ouro", "joias", "baus", "nada"]   # joias = só lágrimas/jóias de refino; baus = só baús dourados (18/10)

## Ajustes do modo automático do personagem (vão no save). "skills" = ids marcados; sem nada marcado, vale a do nível 5.
static func cfg_auto(e: Ent) -> Dictionary:
	if not (e.aux.get("auto_cfg") is Dictionary): e.aux["auto_cfg"] = {}
	var c: Dictionary = e.aux["auto_cfg"]
	for k in AUTO_PADRAO:
		if not c.has(k): c[k] = AUTO_PADRAO[k]
	if not (c.get("skills") is Array):
		c["skills"] = []
		for h in Defs.CLASSES[e.classe]["habilidades"]:
			if h.get("auto", false): c["skills"].append(h["id"])
	return c

static func skill_no_auto(e: Ent, slot: int) -> bool:
	var h := skill_def(e, slot)
	return not h.is_empty() and h["id"] in cfg_auto(e)["skills"]

## Clique direito no slot: põe ou tira a skill do automático.
static func cmd_auto_skill(sim: WorldSim, e: Ent, slot: int) -> void:
	var h := skill_def(e, slot)
	if h.is_empty(): return
	var nome: String = Defs.skill(e.classe, h["id"]).get("nome", h["nome"])
	if h.get("passiva", false):
		sim.emitir_a(e, "aviso", {"texto": "%s é passiva: já está sempre ativa." % nome}); return
	var lst: Array = cfg_auto(e)["skills"]
	if h["id"] in lst:
		lst.erase(h["id"])
		sim.emitir_a(e, "aviso", {"texto": "%s saiu do automático." % nome})
	else:
		lst.append(h["id"])
		sim.emitir_a(e, "aviso", {"texto": "%s no automático%s." % [nome, "" if e.nivel >= int(h["nivel"]) else " (quando liberar no nível %d)" % int(h["nivel"])]})
	sim.emitir_a(e, "auto_cfg", {})

## Janela de ajustes: cada valor é conferido aqui (vem da rede).
static func cmd_auto_cfg(sim: WorldSim, e: Ent, chave: String, valor) -> void:
	var c := cfg_auto(e)
	match chave:
		"vida", "recurso", "raio":
			if not (valor is float or valor is int): return
			var lim: Array = AUTO_LIMITES[chave]
			c[chave] = clampf(float(valor), lim[0], lim[1])
			if chave == "raio" and e.aux.has("auto_centro") and e.pos.distance_to(e.aux["auto_centro"]) > c["raio"]: e.aux["auto_centro"] = e.pos
		"area_min":
			if not (valor is int): return
			c[chave] = clampi(valor, AUTO_LIMITES[chave][0], AUTO_LIMITES[chave][1])
		"juntar":
			if not (valor is String and valor in AUTO_JUNTAR): return
			c[chave] = valor
		"pocao_sempre":
			if not (valor is bool): return
			c[chave] = valor
		_: return
	sim.emitir_a(e, "auto_cfg", {})

static func _cfg_do_save(e: Ent, s) -> void:
	if not (s is Dictionary): return
	var c := cfg_auto(e)
	for k in ["vida", "recurso", "raio"]:
		if s.get(k) is float or s.get(k) is int: c[k] = clampf(float(s[k]), AUTO_LIMITES[k][0], AUTO_LIMITES[k][1])
	if s.get("area_min") is float or s.get("area_min") is int: c["area_min"] = clampi(int(s["area_min"]), 1, 3)
	if s.get("juntar") in AUTO_JUNTAR: c["juntar"] = s["juntar"]
	if s.get("pocao_sempre") is bool: c["pocao_sempre"] = s["pocao_sempre"]
	if s.get("skills") is Array:
		var ids: Array = []
		for h in Defs.CLASSES[e.classe]["habilidades"]:
			if h["id"] in s["skills"] and not h.get("passiva", false): ids.append(h["id"])
		c["skills"] = ids

static func desligar_auto(sim: WorldSim, e: Ent, motivo: String = "") -> void:
	if not e.aux.get("auto", false): return
	e.aux["auto"] = false
	e.aux.erase("auto_centro"); e.aux.erase("auto_poupa"); e.aux.erase("auto_ocioso_t"); e.aux.erase("auto_nao_cabe")
	if motivo != "": sim.emitir_a(e, "aviso", {"texto": motivo})
	else: sim.emitir_a(e, "aviso", {"texto": "Modo automático desligado."})

static func _tem_algum(e: Ent, ids: Array) -> bool:
	for id in ids:
		if Itens.contar(e.inv, id) > 0: return true
	return false

## Poção sozinha: no modo automático sempre; fora dele só em combate e se "pocao_sempre" estiver ligado.
static func _auto_pocoes(sim: WorldSim, e: Ent, ligado: bool) -> void:
	if not e.vivo: return
	var c := cfg_auto(e)
	if not _tem_algum(e, POCOES_VIDA):
		if ligado and e.frac_hp() < 0.2: desligar_auto(sim, e, "SEM POÇÕES DE VIDA: modo automático desligado.")
		elif ligado and not e.aux.get("auto_avisou_pocao", false):
			e.aux["auto_avisou_pocao"] = true
			sim.emitir_a(e, "aviso", {"texto": "Acabaram as poções de vida: o automático para se a vida cair a 20%."})
	else: e.aux.erase("auto_avisou_pocao")
	if not ligado and e.em_combate_t >= 5.0: return
	# veneno (e o Amargo do Cultista não conta): antídoto sem recarga compartilhada
	if e.tem("veneno") and e.em_combate_t < 5.0 and _tem_algum(e, ["antidoto_querosene", "agua_benta"]) and e.aux.get("auto_antidoto_t", 0.0) <= sim.tempo:
		e.aux["auto_antidoto_t"] = sim.tempo + 3.0
		cmd_pocao(sim, e, "antidoto")
	if e.aux.get("cd_pocao", 0.0) > 0.0: return
	if e.frac_hp() < float(c["vida"]) and _tem_algum(e, POCOES_VIDA):
		cmd_pocao(sim, e, "vida"); return
	if e.rec_max > 0.0 and e.rec / e.rec_max < float(c["recurso"]) and e.em_combate_t < 5.0:
		if _tem_algum(e, POCOES_RECURSO): cmd_pocao(sim, e, "recurso")
		elif ligado: e.aux["auto_poupa"] = true   # sem elixir: só ataque básico até o recurso voltar a 50%

## Primeiro slot marcado para o automático, ou -1 (o HUD usa para o brilho).
static func slot_auto(e: Ent) -> int:
	for i in e.skills_slots.size():
		if skill_no_auto(e, i): return i
	return -1

static func _auto_pode_skill(e: Ent, h: Dictionary) -> bool:
	if h.is_empty() or h.get("passiva", false) or e.nivel < int(h["nivel"]) or e.cds.has(h["id"]) or e.tem("silenciado"): return false
	var cst := custo(e, h)
	if e.classe == "cultista": return cst <= 0.0 or (e.frac_hp() >= float(h.get("nao_usa_abaixo_de_hp", 0.25)) and e.hp - cst >= 1.0)
	if e.aux.get("auto_poupa", false) and cst > 0.0:
		if e.rec / maxf(1.0, e.rec_max) < AUTO_RETOMA: return false
		e.aux.erase("auto_poupa")
	return e.rec >= cst

## Papel de cada skill no automático, pela forma dela nos dados (classes_base.json). A ordem é a prioridade.
const AUTO_ORDEM := ["cura", "buff", "invoca", "area", "volta", "alvo"]
static func _papel_auto(h: Dictionary) -> String:
	if h.has("forma"): return "area"
	if h.has("buff") or h["id"] == "campo_forca": return "buff"
	if h.has("invoca"): return "invoca"
	var tipo := _tipo_skill(h)
	if tipo == "alvo_aliado": return "cura"
	if tipo == "proprio": return "volta"
	return "alvo"

## Tenta uma das skills marcadas contra o alvo do automático. true = soltou (ou começou a andar para soltar).
static func _auto_skills(sim: WorldSim, e: Ent, alvo: Ent, c: Dictionary) -> bool:
	if not e.buffer_skill.is_empty() or not e.pronto(): return false
	var marcadas: Array = c["skills"]
	if marcadas.is_empty(): return false
	var dist := e.pos.distance_to(alvo.pos) - alvo.raio
	for papel in AUTO_ORDEM:
		for slot in e.skills_slots.size():
			var h := skill_def(e, slot)
			if h.is_empty() or not h["id"] in marcadas or _papel_auto(h) != papel or not _auto_pode_skill(e, h): continue
			var ok := false
			var alvo_id := alvo.id
			match papel:
				"cura":
					ok = e.frac_hp() < 0.6; alvo_id = e.id
				"buff":
					ok = dist <= 5.0
					for b in e.buffs:
						if b["id"] == h["id"]: ok = false
					if h["id"] == "campo_forca" and e.escudo > 0.0: ok = false
				"invoca":
					var n := 0
					for o: Ent in sim.ents.values():
						if o.tipo == "invocacao" and o.dono == e.id and o.kind == h["invoca"] and o.vivo: n += 1
					ok = dist <= 6.0 and n < maxi(1, int(h.get("max", 1)))
				"area":
					var forma: String = h.get("forma", "circulo_em_volta")
					var dir := (alvo.pos - e.pos).normalized() if alvo.pos != e.pos else e.facing
					var centro := alvo.pos if forma == "circulo_no_mouse" else e.pos
					if forma != "circulo_no_mouse" or e.pos.distance_to(alvo.pos) <= float(h.get("alcance", 0.0)):
						ok = Habilidades.alvos_area5(sim, e, h, forma, centro, dir).size() >= int(c["area_min"])
				"volta":
					ok = dist <= float(h.get("area_raio", 2.5))
				"alvo":
					var alc := _alcance_skill(h)
					ok = alc <= 0.0 or dist <= alc + 3.0   # um pouco fora do alcance: anda até lá (buffer)
			if not ok: continue
			if papel != "cura": e.alvo = alvo.id
			if _tentar_skill(sim, e, slot, alvo_id, alvo.pos, true): return true
			if not e.buffer_skill.is_empty(): return true
	return false

## Mob que já está brigando com outro jogador (fora do meu grupo) não é meu: o automático não rouba.
static func _de_outro(sim: WorldSim, e: Ent, o: Ent) -> bool:
	if o.alvo == -1 or o.alvo == e.id: return false
	var dono := sim.valido(o.alvo)
	if dono != null and dono.tipo == "invocacao": dono = sim.valido(dono.dono)
	if dono == null or dono.tipo != "jogador" or dono == e: return false
	var g := int(e.aux.get("grupo", -1))
	return g < 0 or int(dono.aux.get("grupo", -1)) != g

## Drop no chão que o automático pode juntar (filtro da janela; ouro sempre).
static func _drop_para_juntar(sim: WorldSim, e: Ent, centro: Vector2, raio: float, modo: String) -> Dictionary:
	var melhor := {}
	var dmin := 1e9
	var nao_cabe: Array = e.aux.get("auto_nao_cabe", [])
	var dono_s := float(Defs.DROPS["regras"]["dono_do_drop_s"])
	for c: Dictionary in sim.chao.values():
		if c["pos"].distance_to(centro) > raio + 1.0 or c["id"] in nao_cabe: continue
		if c["dono"] != e.id and c["t"] < dono_s: continue
		var it: Dictionary = c["item"]
		if it["id"] != "_ouro":
			if modo == "ouro": continue
			if modo == "joias" and not it["id"] in Defs.POR_TAG.get("joia:refino", []): continue
			if modo == "baus" and it["id"] != "bau_dourado": continue
			if modo == "bons" and str(it.get("raridade", "comum")) == "comum" and not it["id"] in POCOES_VIDA + POCOES_RECURSO: continue
			var empilha := Itens.pilha(it) > 1 and e.inv.any(func(o): return o["id"] == it["id"])
			if not empilha and Itens.achar_lugar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it).x < 0:
				nao_cabe.append(c["id"]); e.aux["auto_nao_cabe"] = nao_cabe
				sim.emitir_a(e, "aviso", {"texto": "Mochila cheia: o automático parou de juntar itens."})
				continue
		var d: float = c["pos"].distance_to(e.pos)
		if d < dmin: dmin = d; melhor = c
	return melhor

static func _auto(sim: WorldSim, e: Ent, dt: float) -> void:
	if not e.vivo: return
	var c := cfg_auto(e)
	var raio := float(c["raio"])
	if not e.aux.has("auto_centro"): e.aux["auto_centro"] = e.pos
	var centro: Vector2 = e.aux["auto_centro"]
	# chefe ou elite por perto: desliga (não morrer sozinho)
	var perto: Ent = null
	var dmin := 1e9
	for o: Ent in sim.inimigos_de(e, centro, raio + 2.0):
		if o.invisivel or not o.alvejavel: continue
		if o.tipo == "chefe" or o.arquetipo in ["elite", "raro"]:
			desligar_auto(sim, e, "CHEFE! Modo automático desligado."); return
		if o.pos.distance_to(centro) > raio or _de_outro(sim, e, o): continue
		var d := o.pos.distance_to(e.pos)
		if o.alvo == e.id: d -= 3.0   # quem já está me batendo vem primeiro
		if d < dmin: dmin = d; perto = o
	var atual := sim.valido(e.alvo)
	if atual != null and atual.vivo and atual.pos.distance_to(centro) <= raio + 1.0 and e.eh_inimigo_de(atual): perto = atual
	if perto == null:
		e.alvo = -1
		# sem briga: junta o que caiu no raio, depois volta ao centro
		if c["juntar"] != "nada" and not e.aux.has("pegar"):
			var drop := _drop_para_juntar(sim, e, centro, raio, c["juntar"])
			if not drop.is_empty():
				e.aux["pegar"] = drop["id"]; sim.ir_para(e, drop["pos"])
				e.aux["auto_ocioso_t"] = 0.0
				return
		if e.aux.has("pegar"): return
		e.aux["auto_ocioso_t"] = float(e.aux.get("auto_ocioso_t", 0.0)) + dt
		if e.aux["auto_ocioso_t"] >= 3.0 and e.pos.distance_to(centro) > 1.5 and e.caminho.is_empty():
			sim.ir_para(e, centro)
		return
	e.aux["auto_ocioso_t"] = 0.0
	e.aux.erase("pegar")
	if _auto_skills(sim, e, perto, c): return
	# nenhuma skill serve agora: ataque básico (o laço do passo anda até o alcance)
	e.alvo = perto.id

# =================================================================== árvore de talentos (tecla T)
## A cada TALENTO_NIVEIS níveis o jogador ganha 1 ponto para pôr numa skill ativa já liberada. Cada ponto (até
## TALENTO_MAX por skill) dá +TALENTO_DANO de dano/cura, +TALENTO_DURACAO de duração (buffs, escudos, invocações) e
## -TALENTO_RECARGA de recarga. A regra entra num lugar só: talentos_em(e, h) devolve a cópia ajustada da skill.
const TALENTO_NIVEIS := 5
const TALENTO_MAX := 10
const TALENTO_DANO := 0.06
const TALENTO_DURACAO := 0.05
const TALENTO_RECARGA := 0.03
const TALENTO_OURO_POR_PONTO := 25   # esquecer talentos: preço por ponto gasto

static func talentos(e: Ent) -> Dictionary:
	if not (e.aux.get("talentos") is Dictionary): e.aux["talentos"] = {}
	return e.aux["talentos"]

static func talento(e: Ent, id: String) -> int:
	return int(talentos(e).get(id, 0))

static func talentos_gastos(e: Ent) -> int:
	var n := 0
	for k in talentos(e): n += int(talentos(e)[k])
	return n

static func talentos_livres(e: Ent) -> int:
	return maxi(0, e.nivel / TALENTO_NIVEIS - talentos_gastos(e))

const _CHAVES_DANO := ["mult", "mult_por_tick", "mult_por_projetil", "mult_por_golpe", "cura_mult", "cura_mult_por_tick"]
## Skill com os talentos aplicados (cópia; os dados originais não mudam).
static func talentos_em(e: Ent, h: Dictionary) -> Dictionary:
	var r := talento(e, str(h.get("id", "")))
	if r <= 0: return h
	var c := h.duplicate(true)
	for k in _CHAVES_DANO:
		if c.has(k) and (c[k] is float or c[k] is int): c[k] = float(c[k]) * (1.0 + TALENTO_DANO * r)
	if c.has("recarga"): c["recarga"] = float(c["recarga"]) * (1.0 - TALENTO_RECARGA * r)
	if c.has("duracao") and (c["duracao"] is float or c["duracao"] is int): c["duracao"] = float(c["duracao"]) * (1.0 + TALENTO_DURACAO * r)
	if c.get("buff") is Dictionary and c["buff"].has("duracao"): c["buff"]["duracao"] = float(c["buff"]["duracao"]) * (1.0 + TALENTO_DURACAO * r)
	c["talento"] = r
	return c

static func cmd_talento(sim: WorldSim, e: Ent, id: String) -> void:
	var h := {}
	for x in Defs.CLASSES[e.classe]["habilidades"]:
		if x["id"] == id: h = x
	if h.is_empty() or h.get("passiva", false): return
	var nome: String = Defs.skill(e.classe, id).get("nome", h["nome"])
	if e.nivel < int(h["nivel"]):
		sim.emitir_a(e, "aviso", {"texto": "%s libera no nível %d." % [nome, int(h["nivel"])]}); return
	if talentos_livres(e) <= 0:
		sim.emitir_a(e, "aviso", {"texto": "Sem pontos de talento: ganha 1 a cada %d níveis." % TALENTO_NIVEIS}); return
	if talento(e, id) >= TALENTO_MAX:
		sim.emitir_a(e, "aviso", {"texto": "%s já está no máximo." % nome}); return
	talentos(e)[id] = talento(e, id) + 1
	sim.emitir_a(e, "som_evento", {"ev": "nivel_sobe"})
	sim.emitir_a(e, "aviso", {"texto": "%s %d/%d" % [nome, talento(e, id), TALENTO_MAX]})
	sim.emitir_a(e, "talentos", {})

static func cmd_esquecer_talentos(sim: WorldSim, e: Ent) -> void:
	var gastos := talentos_gastos(e)
	if gastos == 0: return
	var preco := gastos * TALENTO_OURO_POR_PONTO
	if e.ouro < preco:
		sim.emitir_a(e, "aviso", {"texto": "Esquecer os talentos custa %d de ouro." % preco}); return
	e.ouro -= preco
	e.aux["talentos"] = {}
	sim.emitir_a(e, "aviso", {"texto": "Talentos esquecidos: %d pontos de volta (%d de ouro)." % [gastos, preco]})
	sim.emitir_a(e, "talentos", {})

static func _talentos_do_save(e: Ent, s) -> void:
	if not (s is Dictionary): return
	var t := {}
	for h in Defs.CLASSES[e.classe]["habilidades"]:
		if s.has(h["id"]) and not h.get("passiva", false): t[h["id"]] = clampi(int(s[h["id"]]), 0, TALENTO_MAX)
	e.aux["talentos"] = t
	# save mexido à mão não passa do que o nível permite
	while talentos_gastos(e) > e.nivel / TALENTO_NIVEIS:
		for k in t.keys():
			if t[k] > 0: t[k] -= 1; break

# =================================================================== comandos
static func cmd_mover(sim: WorldSim, e: Ent, p: Vector2) -> void:
	if not e.vivo: return
	if e.aux.get("imovel_t", 0.0) > 0.0: return
	desligar_auto(sim, e)
	e.alvo = -1; e.aux.erase("interagir"); e.aux.erase("pegar"); e.buffer_skill = {}
	if not e.interagindo.is_empty(): cancelar_canal(sim, e)
	if not e.acao.is_empty() and e.acao["fase"] == "rec": e.acao = {}
	sim.ir_para(e, p)

static func cmd_atacar(sim: WorldSim, e: Ent, alvo_id: int) -> void:
	var al := sim.valido(alvo_id)
	if al == null or not e.vivo or not e.eh_inimigo_de(al): return
	desligar_auto(sim, e)
	e.aux.erase("interagir"); e.aux.erase("pegar")
	if not e.interagindo.is_empty(): cancelar_canal(sim, e)
	e.alvo = alvo_id

static func cmd_interagir(sim: WorldSim, e: Ent, id: int) -> void:
	var o: Ent = sim.ents.get(id)
	if o == null or not e.vivo: return
	desligar_auto(sim, e)
	e.alvo = -1; e.aux.erase("pegar")
	e.aux["interagir"] = id
	sim.ir_para(e, o.pos)

static func cmd_pegar(sim: WorldSim, e: Ent, chao_id: int) -> void:
	if not sim.chao.has(chao_id) or not e.vivo: return
	e.alvo = -1; e.aux.erase("interagir")
	e.aux["pegar"] = chao_id
	sim.ir_para(e, sim.chao[chao_id]["pos"])

static func cmd_ponto(sim: WorldSim, e: Ent, stat: String) -> void:
	if e.pontos <= 0 or not e.stats.has(stat): return
	e.pontos -= 1
	e.stats[stat] = float(e.stats[stat]) + float(Defs.FORM["peso_por_ponto"])
	Regras.recalc_jogador(e)
	sim.emitir_a(e, "stats", {"id": e.id})

static func cmd_skill(sim: WorldSim, e: Ent, slot: int, alvo: int, ponto: Vector2) -> void:
	if not e.vivo: return
	if not _tentar_skill(sim, e, slot, alvo, ponto, false):
		pass

# =================================================================== ataque básico
static func ataque_basico(sim: WorldSim, e: Ent, al: Ent) -> void:
	var arma := Regras.Ent_arma(e)
	e.cd_basico = e.intervalo
	var prep := e.intervalo * 0.4
	var corpo_a_corpo := alcance_basico(e) < 2.0
	var op := {"postura": e.postura_arma, "sensacao": "golpe_leve", "magico": Defs.CLASSES[e.classe]["perfil_dano"] == "magico", "basico": true}
	if e.classe == "humano" and e.municao <= 0:
		op["mult"] = 0.6
	if e.classe == "humano" and e.municao > 0 and e.aux.has("municao_especial"):
		op["elemento"] = e.aux["municao_especial"]; op["mult"] = 1.2
	if e.aux.get("prox_critico", false):
		op["forca_crit"] = true; e.aux.erase("prox_critico")
	for ef in e.aux.get("bonus", {}).get("efeitos", []):
		if ef == "estandarte_legiao": op["efeito"] = {"sangramento": {"duracao": 4.0, "dano_por_s_mult": 0.15}}
	var alvo_id := al.id
	if e.classe == "humano":
		_basico_humano(sim, e, al, op); return
	sim.iniciar_acao(e, {"preparo": prep, "rec": maxf(0.05, e.intervalo * 0.6 - 0.15), "alvo": alvo_id, "anim": "attack",
		"impacto": func():
			var a2 := sim.valido(alvo_id)
			if a2 == null: return
			if corpo_a_corpo:
				if e.pos.distance_to(a2.pos) - a2.raio <= alcance_basico(e) + 0.8:
					sim.aplicar_golpe(e, a2, op)
					if e.aux.has("area_basico"):   # Forma Colossal: o tentáculo varre tudo em volta do alvo
						for o in sim.inimigos_de(e, a2.pos, float(e.aux["area_basico"])):
							if o != a2: sim.aplicar_golpe(e, o, op.merged({"area": true, "sem_recurso": true}))
			else:
				if e.classe == "humano": e.municao -= 1
				sim.lancar(e, {"vel": float(arma.get("projetil_vel", 12)) if float(arma.get("projetil_vel", 0)) > 0 else 12.0, "alvo": alvo_id, "vfx": "basico_" + e.classe}, op)
	})

## Humano híbrido: de perto a espada larga (arco de 120°, até 2 alvos, o segundo com 50%); de longe a escopeta (gasta munição).
static func _basico_humano(sim: WorldSim, e: Ent, al: Ent, op: Dictionary) -> void:
	var c: Dictionary = Defs.CLASSES["humano"]
	var dist := e.pos.distance_to(al.pos) - al.raio
	var espada: bool = dist <= float(c["perfil_hibrido"]["distancia_troca"]) or e.municao <= 0
	var alvo_id := al.id
	if espada:
		var arma := Regras.Ent_arma(e)
		e.cd_basico = e.intervalo
		op["sensacao"] = "golpe_pesado"
		sim.iniciar_acao(e, {"preparo": e.intervalo * 0.35, "rec": maxf(0.05, e.intervalo * 0.6 - 0.15), "alvo": alvo_id, "anim": "attack", "impacto": func():
			var a2 := sim.valido(alvo_id)
			if a2 == null: return
			var frente := (a2.pos - e.pos).normalized()
			var alvos := [a2]
			for o in sim.inimigos_de(e, e.pos, float(c["alcance_basico"]["espada"]) + 0.9):
				if o != a2 and alvos.size() < 2 and frente.dot((o.pos - e.pos).normalized()) > 0.5: alvos.append(o)
			if e.pos.distance_to(a2.pos) - a2.raio <= float(c["alcance_basico"]["espada"]) + 0.8:
				sim.aplicar_golpe(e, a2, op)
			if alvos.size() > 1:
				var op2 := op.duplicate(); op2["mult"] = float(op.get("mult", 1.0)) * 0.5; op2.erase("basico")   # o Verbo do Cetro só sai no golpe principal
				sim.aplicar_golpe(e, alvos[1], op2)
			sim.emitir("vfx", {"nome": "golpe_corte", "alvo": alvo_id, "de": e.id})
		})
	else:
		var sec: Dictionary = c["arma_secundaria"]
		var iv := float(sec["intervalo"]) / e.vel_ataque
		e.cd_basico = iv
		op["faixa"] = e.aux.get("tiro", [4, 7]); op["sensacao"] = "tiro_pesado"; op["postura"] = float(sec["postura"])
		if e.aux.has("municao_especial"): op["elemento"] = e.aux["municao_especial"]; op["mult"] = 1.2
		sim.iniciar_acao(e, {"preparo": 0.12 + float(c["perfil_hibrido"]["tempo_troca_s"]) * (1.0 if e.aux.get("arma_mao", "") != "tiro" else 0.0),
			"rec": maxf(0.05, iv * 0.55), "alvo": alvo_id, "anim": "shoot", "impacto": func():
			e.municao -= 1
			sim.emitir("vfx", {"nome": "disparo_cano", "de": e.id, "alvo": alvo_id})
			sim.lancar(e, {"vel": float(sec["projetil_vel"]), "alvo": alvo_id, "vfx": "projetil_bala", "perfura": e.aux.has("tiros_atravessam")}, op)
		})
	e.aux["arma_mao"] = "espada" if espada else "tiro"

# =================================================================== habilidades
static func skill_def(e: Ent, slot: int) -> Dictionary:
	if slot < 0 or slot >= e.skills_slots.size(): return {}
	var id: String = e.skills_slots[slot]
	if id == "": return {}
	for h in Evolucao.habilidades(e):
		if h["id"] == id: return h
	return {}

static func custo(e: Ent, h: Dictionary) -> float:
	if Demiurgo.tem(e): return 0.0   # A Mão que Mede: custo zero
	var c := float(h.get("custo", 0))
	if e.classe == "cultista": return c * e.hp_max
	return c

static func _alcance_skill(h: Dictionary) -> float:
	if h.has("alcance"): return float(h["alcance"])
	return 0.0

## Tenta soltar a habilidade agora. Se o alvo está longe, anda e guarda no buffer.
static func _tentar_skill(sim: WorldSim, e: Ent, slot: int, alvo_id: int, ponto: Vector2, do_buffer: bool) -> bool:
	var h := talentos_em(e, skill_def(e, slot))
	if h.is_empty(): return true
	if h.get("passiva", false):
		sim.emitir_a(e, "aviso", {"texto": "%s é passiva: já está ativa." % h["nome"]}); return true
	if e.nivel < int(h["nivel"]):
		sim.emitir_a(e, "aviso", {"texto": "Libera no nível %d." % int(h["nivel"])}); return true
	if e.cds.has(h["id"]):
		if not do_buffer: sim.emitir_a(e, "aviso", {"texto": "Ainda recarregando."})
		return true
	if e.tem("silenciado"):
		sim.emitir_a(e, "aviso", {"texto": "Silenciado."}); return true
	var cst := custo(e, h)
	if e.classe == "cultista":
		if e.hp - cst < 1.0: sim.emitir_a(e, "aviso", {"texto": "Sangue insuficiente."}); return true
		# skill que custa HP não sai abaixo de 25% de HP (classes_base: nao_usa_abaixo_de_hp)
		if cst > 0.0 and e.frac_hp() < float(h.get("nao_usa_abaixo_de_hp", 0.25)):
			sim.emitir_a(e, "aviso", {"texto": "Sangue fraco demais: beba uma poção de vida."}); return true
	elif e.rec < cst:
		sim.emitir_a(e, "som_evento", {"ev": "sem_recurso"})
		sim.emitir_a(e, "aviso", {"texto": "%s insuficiente." % Defs.CLASSES[e.classe]["recurso"]["nome"].split(" ")[0]}); return true
	if not e.pronto():
		if not do_buffer: e.buffer_skill = {"slot": slot, "alvo": alvo_id, "ponto": ponto, "t": 2.0}
		return false
	var tipo := _tipo_skill(h)
	var alvo: Ent = sim.valido(alvo_id)
	if tipo == "alvo_inimigo":
		if alvo == null or not e.eh_inimigo_de(alvo): alvo = sim.valido(e.alvo)
		if alvo == null:
			sim.emitir_a(e, "aviso", {"texto": "Sem alvo."}); return true
		var alc := _alcance_skill(h)
		if e.pos.distance_to(alvo.pos) - alvo.raio > alc or (alc > 2.0 and not sim.visao(e.pos, alvo.pos)):
			e.buffer_skill = {"slot": slot, "alvo": alvo.id, "ponto": ponto, "t": 2.0}
			sim.ir_para(e, alvo.pos)
			return false
		e.alvo = alvo.id
	elif tipo == "alvo_aliado":
		if alvo == null or alvo.lado() != e.lado(): alvo = e
		if e.pos.distance_to(alvo.pos) > _alcance_skill(h) + 0.5:
			alvo = e
	elif tipo == "ponto":
		var alc := _alcance_skill(h)
		if alc > 0.0 and e.pos.distance_to(ponto) > alc:
			ponto = e.pos + (ponto - e.pos).normalized() * alc
	# paga e solta
	cst = Evolucao.custo(e, cst)   # Três Auréolas do Arquimago
	if h.get("consome_todo_odio", false):   # Eclipse do Senhor da Guerra: gasta tudo e o dano cresce com o gasto
		cst = e.rec; e.aux["odio_usado"] = cst
	if e.classe == "cultista": e.hp -= cst
	else: e.rec -= cst
	var recarga := float(h.get("recarga", 1.0)) * Demiurgo.mult_recarga(e)   # A Mão que Mede: -90%
	if h.has("cargas"):
		var k: String = "cargas_" + h["id"]
		e.aux[k] = int(e.aux.get(k, int(h["cargas"]))) - 1
		if e.aux[k] <= 0: e.cds[h["id"]] = recarga
		else: e.aux["recarga_carga_" + h["id"]] = recarga
	else: e.cds[h["id"]] = recarga
	e.buffer_skill = {}
	if h.has("gera"): e.rec = minf(e.rec_max, e.rec + float(h["gera"]))
	e.em_combate_t = minf(e.em_combate_t, 4.0)
	Habilidades.usar(sim, e, h, alvo, ponto)
	sim.emitir_a(e, "skill", {"id": e.id, "skill": h["id"], "slot": slot, "recarga": recarga})
	return true

static func _tipo_skill(h: Dictionary) -> String:
	if h.has("_evo"): return Evolucao.tipo(h)
	match h["id"]:
		"toque_graca", "nanoreparo": return "alvo_aliado"
		"asas_ascensao", "rolamento", "arrancada", "chuva_cinzas", "armadilha_prata", "investida_bestial", "rajada": return "ponto"
		"warlord_fenda_na_terra", "investida_de_ferro": return "ponto"
		"juramento_de_odio", "muralha_de_escudo", "redemoinho_de_aco", "marca_do_desprezo", "estandarte_da_ruina", "eclipse_do_senhor_da_guerra": return "proprio"
		"anjo_leque_juizo", "demonio_ceifa_infernal", "cultista_espinhos_sangue", "humano_coquetel_querosene": return "ponto"
		"mutante_terremoto_putrido", "tecnomancer_tempestade_bobina": return "proprio"
		"halo_ardente", "corte_largo", "pacto_rubro", "servo_carne", "rugido_praga", "carapaca", "pele_enxofre", "agua_benta_polvora", "torreta_sentinela", "campo_forca", "pulso_anti_divino": return "proprio"
	return "alvo_inimigo"

# =================================================================== recursos e gatilhos de combate
static func ao_acertar(sim: WorldSim, e: Ent, alvo: Ent, r: Dictionary, op: Dictionary) -> void:
	Demiurgo.ao_acertar(sim, e, alvo, op)   # Cetro do Demiurgo: Golpe, Verbo e Juízo
	if op.get("sem_recurso", false): return   # skill em área: só o primeiro alvo gera recurso
	var rc: Dictionary = Defs.CLASSES[e.classe]["recurso"]
	match e.classe:
		"anjo": e.rec = minf(e.rec_max, e.rec + float(rc["ganho"]["golpe_acertado"]))
		"mutante", "warlord": e.rec = minf(e.rec_max, e.rec + float(rc["ganho"]["golpe_acertado"]))
		"demonio":
			var g := float(rc["ganho"]["golpe_acertado"]) + (float(rc["ganho"]["critico_extra"]) if r.get("crit", false) else 0.0)
			var novo := e.rec + g
			if novo > 100.0:
				var sobra := novo - 100.0
				novo = 100.0
				sim.aplicar_dano_puro(e, e.hp_max * 0.005 * sobra, "fogo", e)
			e.rec = novo

static func ao_ser_atingido(sim: WorldSim, e: Ent, atk: Ent, dano: float, r: Dictionary) -> void:
	if e.classe == "mutante":
		e.rec = minf(e.rec_max, e.rec + dano / e.hp_max * 100.0)
	if e.classe == "warlord":
		e.rec = minf(e.rec_max, e.rec + float(Defs.CLASSES["warlord"]["recurso"]["ganho"]["golpe_recebido"]))
	if not e.interagindo.is_empty() and dano > 0: cancelar_canal(sim, e)
	Demiurgo.refletir(sim, e, atk, dano)   # Como em Cima, Assim Embaixo
	# Pele de Enxofre: reflete
	for b in e.buffs:
		if b["mods"].has("reflete") and atk != null and atk.vivo and atk != e:
			sim.aplicar_dano_puro(atk, dano * float(b["mods"]["reflete"]), "fogo", e, "normal")

static func abateu(sim: WorldSim, e: Ent, morto: Ent) -> void:
	Evolucao.abateu(sim, e, morto)
	if e.mod("cura_por_abate") > 0.0: sim.curar(e, e.hp_max * e.mod("cura_por_abate"), e)   # Ave, Arena!
	var xp := Regras.xp_mob(morto) * Regras.mod_xp_nivel(morto.nivel, e.nivel)
	if morto.tipo == "chefe":
		xp = (10.0 + 5.0 * morto.nivel) * (25.0 if not e.flags.has("venceu_" + morto.kind) else 8.0)
		e.flags["venceu_" + morto.kind] = true
	xp *= float(Defs.DROPS["balanco"]["xp"])   # balanço 18/10: XP do abate +50%
	var grupo := membros_grupo(sim, e)
	if grupo.size() > 1:   # grupo: a XP do abate vai para quem está perto (+10% por membro extra), dividida igualmente
		var parte := int(round(xp * (1.0 + 0.1 * (grupo.size() - 1)) / grupo.size()))
		for m: Ent in grupo: ganhar_xp(sim, m, parte)
	else: ganhar_xp(sim, e, int(round(xp)))
	e.abates[morto.kind] = e.abates.get(morto.kind, 0) + 1
	Missoes.evento(sim, e, "matar", morto.kind)
	# farmar_spot: qualquer monstro morto dentro do spot conta
	var spot: String = str(morto.aux.get("spot", ""))
	if spot == "": spot = sim.spot_em(morto.pos)
	if spot != "": Missoes.evento(sim, e, "farmar_spot", spot)
	if e.classe == "cultista":
		var g := 0.1 if morto.tem("sangramento") else 0.06
		if sim.tempo - float(e.aux.get("area5_t", -9.0)) < 0.05: g = float(Defs.CLASSES["cultista"]["recurso"].get("ganho", {}).get("abate_por_area", 0.02))
		sim.curar(e, e.hp_max * g, e)
	if e.classe == "mutante" and e.nivel >= 12: sim.curar(e, e.hp_max * 0.05, e)
	for ef in e.aux.get("bonus", {}).get("efeitos", []):
		if ef == "dragonas_general": sim.curar(e, e.hp_max * 0.03, e)

static func ganhar_xp(sim: WorldSim, e: Ent, q: int, fonte: String = "") -> void:
	if q <= 0: return
	q = int(round(q * (1.0 + e.mod("xp"))))   # Aura Demiúrgica: +50% de XP
	e.xp += q
	sim.emitir_a(e, "xp", {"valor": q, "fonte": fonte})
	while e.xp >= Defs.xp_para_proximo(e.nivel):
		e.xp -= Defs.xp_para_proximo(e.nivel)
		e.nivel += 1
		e.pontos += int(Defs.FORM["pontos_por_nivel"])
		Regras.recalc_jogador(e)
		e.hp = e.hp_max
		if e.classe in ["anjo", "tecnomancer", "humano"]: e.rec = e.rec_max
		var nova := ""
		for h in Evolucao.habilidades(e):
			if int(h["nivel"]) == e.nivel: nova = h["nome"]
		sim.emitir("nivel", {"id": e.id, "nivel": e.nivel, "skill_nova": nova})   # o cliente abre os cards da evolução ao ver o nível 30
		if e.nivel % TALENTO_NIVEIS == 0: sim.emitir_a(e, "aviso", {"texto": "Ponto de talento novo! Aperte T para usar."})

# =================================================================== morte
static func morreu(sim: WorldSim, e: Ent) -> void:
	var perda := 0
	if e.nivel > int(Defs.FORM["morte"]["sem_perda_ate_nivel"]):
		perda = int(Defs.xp_para_proximo(e.nivel) * float(Defs.FORM["morte"]["perda_xp_frac_do_nivel"]))
		e.xp = maxi(0, e.xp - perda)
	e.renascer_t = float(Defs.FORM["morte"]["tempo_para_renascer_s"])
	e.alvo = -1; e.buffer_skill = {}; e.interagindo = {}
	desligar_auto(sim, e)
	sim.emitir_a(e, "jogador_morreu", {"perda": perda, "t": e.renascer_t})
	if sim.chefe != null: sim.chefe.jogador_morreu()

static func renascer(sim: WorldSim, e: Ent) -> void:
	e.vivo = true
	e.hp = e.hp_max
	e.rec = e.rec_max if e.classe in ["anjo", "tecnomancer", "humano"] else 0.0
	e.imune_t = 3.0; e.invuln_t = 3.0
	var p: Vector2 = ponto_renascer(sim, e)
	e.pos = sim.celula_livre_perto(p)
	e.caminho.clear()
	sim.emitir("reviveu", {"id": e.id})

static func ponto_renascer(sim: WorldSim, e: Ent) -> Vector2:
	var spf: Dictionary = sim.mapa.get("spawn_por_faccao", {})
	if spf.has(e.faccao): return Vector2(spf[e.faccao][0], spf[e.faccao][1])
	var s: Array = sim.mapa.get("spawn", [10, 10])
	return Vector2(s[0], s[1])

# =================================================================== interação com o mundo
static func interagir(sim: WorldSim, e: Ent, o: Ent) -> void:
	Biblioteca.tocar(sim, e, o)
	match o.tipo:
		"npc": Missoes.abrir(sim, e, o)
		"objeto":
			match o.kind:
				"bau": _bau(sim, e, o)
				"interativo": _objeto(sim, e, o)
				"portal": _portal(sim, e, o)
				"leitura": sim.emitir_a(e, "texto", {"titulo": o.nome, "texto": o.aux.get("texto", "")})

static func cancelar_canal(sim: WorldSim, e: Ent) -> void:
	if e.interagindo.is_empty(): return
	e.interagindo = {}
	sim.emitir("canal_fim", {"id": e.id, "ok": false})

static func canalizar(sim: WorldSim, e: Ent, dur: float, texto: String, fim: Callable) -> void:
	e.interagindo = {"t": 0.0, "dur": dur, "fim": fim}
	e.caminho.clear()
	sim.emitir("canal", {"id": e.id, "dur": dur, "texto": texto})

## Teleporte de volta à base da facção (Vigília: São Lázaro; Arautos: Jerusalém): grátis, sem item. Fica parado 3 s.
static func voltar_acampamento(sim: WorldSim, e: Ent) -> void:
	if not e.vivo or e.interagindo.has("t"): return
	canalizar(sim, e, 3.0, "Voltando ao acampamento", func(): _ir_para_casa(sim, e))

static func _ir_para_casa(sim: WorldSim, e: Ent) -> void:
	var casa := Defs.mapa_casa(e.faccao)
	sim.emitir_a(e, "trocar_mapa", {"mapa": casa, "pos": ponto_renascer(sim, e) if sim.mapa_id == casa else Vector2(-1, -1)})

static func _bau(sim: WorldSim, e: Ent, b: Ent) -> void:
	if b.aux.get("aberto", false):
		sim.emitir_a(e, "aviso", {"texto": "Vazio."}); return
	var t: String = b.aux.get("bau", "caixote_podre")
	if b.aux.has("visivel_se") and not Missoes.cond(e, b.aux["visivel_se"], ""): return
	if b.aux.get("requer_chefe", "") != "" and (sim.chefe == null or sim.chefe.estado != "morto"):
		sim.emitir_a(e, "aviso", {"texto": "Trancado por algo maior que uma fechadura."}); return
	if b.aux.get("loot_de_grupo", false) and not ChefeEgito.pode_abrir_bau(sim, e, b): return
	var trancado: bool = t == "bau_de_ferro" or b.aux.get("trancado", false)
	var usou_gazua := false
	if trancado:
		if Itens.contar(e.inv, "chave_bau_ferro") > 0:
			Itens.remover(e.inv, "chave_bau_ferro", 1); sim.emitir_a(e, "som_evento", {"ev": "chave"})
		elif Itens.contar(e.inv, "gazua") > 0:
			Itens.remover(e.inv, "gazua", 1); usou_gazua = true
		else:
			sim.emitir_a(e, "aviso", {"texto": "Trancado. Precisa de uma Chave Enferrujada ou de uma Gazua."}); return
		sim.emitir_a(e, "inventario", {})
	if b.aux.get("mimico", false):
		# Baú Faminto: morde e vira monstro
		b.aux["aberto"] = true
		var m := sim.criar_mob("carnical", b.pos, int(b.aux.get("nivel", e.nivel)))
		m.nome = "Baú Faminto"; m.kind = "bau_faminto"; m.arquetipo = "elite"; m.hp_max *= 3.0; m.hp = m.hp_max
		m.aux["drop_bau"] = true; m.tags = ["mimico"]
		sim.remover(b.id)
		sim.emitir("fala", {"id": m.id, "texto": "NHAC!", "cor": "#c8302a"})
		sim.aplicar_golpe(m, e, {"mult": 1.5, "sensacao": "golpe_pesado"})
		IA.acordar(sim, m, e)
		return
	canalizar(sim, e, 1.0, "Abrindo %s" % b.nome, func():
		if usou_gazua and sim.rng.randf() > 0.6:
			sim.emitir_a(e, "aviso", {"texto": "A gazua quebrou na fechadura."}); return
		if b.aux.get("armadilha", false) or (t == "caixote_podre" and sim.rng.randf() < 0.1):
			sim.criar_area({"pos": b.pos, "raio": 1.5, "dur": 4.0, "tick": 0.5, "tipo": "veneno",
				"op": {"dano_frac": 0.03, "elemento": "veneno"}})
			sim.emitir_a(e, "aviso", {"texto": "Uma nuvem verde sobe do caixote!"})
		b.aux["aberto"] = not b.aux.get("loot_de_grupo", false)   # baú de chefe do Egito: cada um abre a sua parte
		if b.aux.get("loot_de_grupo", false): ChefeEgito.marcar_bau(e, b)
		sim.emitir("bau", {"id": b.id, "aberto": true, "tipo": t})
		Loot.abrir_bau(sim, b, e)
		if b.aux.has("hist"): Missoes.evento(sim, e, "interagir", b.aux["hist"])
		Missoes.evento(sim, e, "interagir", b.aux.get("obj", t))
	)

static func _objeto(sim: WorldSim, e: Ent, o: Ent) -> void:
	var d: Dictionary = Defs.OBJETOS.get(o.aux["obj"], {})
	if d.get("abre", "") == "estante":   # estante da Biblioteca: lista de livros (Biblioteca.abrir_estante)
		Biblioteca.abrir_estante(sim, e, o); return
	if d.has("texto_servidor") and not d.has("leva_para"):   # inscrição, fichário: o texto já veio por Biblioteca.tocar
		Missoes.evento(sim, e, "interagir", o.aux["obj"]); return
	if o.aux.get("obj", "") == "cartaz_agrak":   # Cartaz do Agrak: a inscrição é no servidor (o cliente manda)
		sim.emitir_a(e, "agrak_pedido", {"a": "inscrever"}); return
	if d.has("visivel_se") and not Missoes.cond(e, d["visivel_se"], ""):
		sim.emitir_a(e, "aviso", {"texto": "Nada de útil agora."}); return
	# objeto que chama um elite (escotilha do silo -> Último Operador) pode ser usado de novo se o elite não está mais vivo
	var reinvoca := false
	if d.has("invoca") and str(Defs.MOBS.get(d["invoca"], {}).get("arquetipo", "")) in ["elite", "raro"]:
		reinvoca = not sim.ents.values().any(func(m): return m.tipo == "monstro" and m.vivo and m.kind == d["invoca"])
	if o.aux.get("usado_por", -1) == e.id and not d.has("leva_para") and not reinvoca:
		sim.emitir_a(e, "aviso", {"texto": "Já fez isto aqui."}); return
	# requer item (chave, pá...) ou vários (lacres)
	var precisa: Array = []
	if d.has("requer_item"): precisa.append(d["requer_item"])
	precisa.append_array(d.get("requer_itens", []))
	var abre_porta := d.has("leva_para") and e.flags.has("aberto_" + o.aux["obj"])
	if d.has("leva_para") and o.aux["obj"] in ["porta_camara", "porta_do_altar"]:   # pedido do Jefin: a Câmara do Zacarias (e o Altar, espelho dela) abre sem os lacres
		precisa = precisa.filter(func(it): return Itens.contar(e.inv, it) > 0)
	if not abre_porta:
		for it in precisa:
			if Itens.contar(e.inv, it) <= 0:
				sim.emitir_a(e, "texto", {"titulo": d.get("nome", o.nome), "texto": d.get("texto_trancado", "Falta alguma coisa.")}); return
	var dur := 1.2 if not abre_porta else 0.3
	canalizar(sim, e, dur, d.get("nome", o.nome), func():
		o.aux["usado_por"] = e.id
		if not abre_porta:
			for it in precisa: Missoes.evento(sim, e, "usar_item", o.aux["obj"], it)
			var txt: String = d.get("texto_ao_usar", "")
			if d.has("textos_variados"): txt = d["textos_variados"][int(o.aux.get("i", 0)) % d["textos_variados"].size()]
			if txt != "": sim.emitir_a(e, "texto", {"titulo": d.get("nome", o.nome), "texto": txt})
			Missoes.evento(sim, e, "interagir", o.aux["obj"])
			if d.has("leitura"): dar_item(sim, e, Itens.novo(d["leitura"]))
			if d.has("tabela"): Loot.abrir_bau(sim, o, e)
			if d.has("invoca"):
				var m := sim.criar_mob(d["invoca"], sim.celula_livre_perto(o.pos + Vector2(1.5, 1.0)), int(Defs.MOBS.get(d["invoca"], {}).get("niveis", [e.nivel])[0]))
				IA.acordar(sim, m, e)
			if d.has("leva_para"): e.flags["aberto_" + o.aux["obj"]] = true
		if d.has("leva_para"):
			_portal_para(sim, e, o.aux.get("mapa", d["leva_para"]), o.aux.get("chegada", []))
	)

static func _portal(sim: WorldSim, e: Ent, o: Ent) -> void:
	if o.aux.has("requer_flag") and not e.flags.has(o.aux["requer_flag"]):
		sim.emitir_a(e, "aviso", {"texto": o.aux.get("texto_trancado", "Fechado.")}); return
	if e.nivel < int(o.aux.get("nivel_minimo", 0)):   # Estrada do Sul (Jerusalém -> deserto): só no nível 12
		sim.emitir_a(e, "aviso", {"texto": o.aux.get("texto_trancado", "Volte no nível %d." % int(o.aux["nivel_minimo"]))}); return
	if sim.chefe != null and sim.chefe.porta_fechada():
		sim.emitir_a(e, "aviso", {"texto": "A grade não se mexe enquanto o chefe estiver vivo."}); return
	canalizar(sim, e, 0.6, o.nome, func(): _portal_para(sim, e, o.aux["para"], o.aux.get("chegada", [])))

const CHAT_MAX := 120
## Quem divide a XP com o matador: do mesmo grupo, vivo, no mesmo mapa e perto dele (ent.aux["grupo"] é posto pelo servidor).
static func membros_grupo(sim: WorldSim, e: Ent) -> Array:
	var gid: int = int(e.aux.get("grupo", -1))
	if gid < 0: return [e]
	var out: Array = []
	for o: Ent in sim.ents.values():
		if o.tipo == "jogador" and o.vivo and int(o.aux.get("grupo", -1)) == gid and o.pos.distance_to(e.pos) <= CHAT_PERTO:
			out.append(o)
	if not out.has(e): out.append(e)
	return out

## O que a janela de inspecionar mostra de outro jogador.
static func inspecao(e: Ent) -> Dictionary:
	var eq := {}
	for slot in e.equip:
		var it: Dictionary = e.equip[slot]
		eq[slot] = {"nome": Itens.nome(it), "raridade": str(it.get("raridade", "comum"))}
	return {"nome": e.nome, "classe": e.classe, "nivel": e.nivel, "hp": e.hp, "hp_max": e.hp_max, "stats": e.stats.duplicate(), "equip": eq}
const CHAT_PERTO := 24.0   # tiles: alcance do canal "perto" (quem vê o balão)
## Chat: limpa o texto, segura spam (até 4 falas a cada 5 s) e emite. Canais: "perto" (balão + quem está perto),
## "global" (todo mundo online) e "pm" (só o destinatário; o servidor acha o nome em qualquer mapa).
static func falar(sim: WorldSim, e: Ent, txt: String, canal := "perto", para := "") -> void:
	var t := ""
	for ch in txt.strip_edges():
		if ch.unicode_at(0) >= 32: t += ch
	t = t.strip_edges().left(CHAT_MAX)
	para = para.strip_edges()
	if t == "" or (canal == "pm" and para == "") or not canal in ["perto", "global", "pm", "grupo"]: return
	var h: Array = e.aux.get("chat_h", [])
	h = h.filter(func(x): return sim.tempo - float(x) < 5.0)
	if h.size() >= 4:
		sim.emitir_a(e, "aviso", {"texto": "Calma: espere um pouco para falar de novo."}); return
	h.append(sim.tempo); e.aux["chat_h"] = h
	if canal == "perto" or canal == "global": sim.emitir("fala", {"id": e.id, "texto": t, "chat": true})
	sim.emitir("chat", {"id": e.id, "nome": e.nome, "classe": e.classe, "texto": t, "canal": canal, "para": para, "pos": e.pos})

static func _portal_para(sim: WorldSim, e: Ent, mapa: String, chegada: Array) -> void:
	var p := Vector2(chegada[0], chegada[1]) if chegada.size() == 2 else Vector2(-1, -1)
	sim.emitir_a(e, "trocar_mapa", {"mapa": mapa, "pos": p})

# =================================================================== itens
static func dar_item(sim: WorldSim, e: Ent, it: Dictionary) -> bool:
	if it["id"] == "_ouro":
		e.ouro += int(it["qtd"]); sim.emitir_a(e, "ouro", {"valor": int(it["qtd"])}); return true
	var cat := Itens.categoria(it)
	if cat == "consumivel" and Defs.ITENS.get(it["id"], {}).get("efeito", {}) is Dictionary and Defs.ITENS[it["id"]].get("efeito", {}).has("municao") and e.classe == "humano":
		var q: int = int(Defs.ITENS[it["id"]]["efeito"].get("qtd", 100)) if int(it.get("qtd", 1)) <= 1 else int(it["qtd"])
		e.municao = mini(int(Defs.CLASSES["humano"]["recurso"]["municao"]["pilha_max"]), e.municao + q)
		sim.emitir_a(e, "log", {"texto": "+%d de munição" % q})
		return true
	var sobra := Itens.guardar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
	if sobra > 0:
		var resto := it.duplicate(); resto["qtd"] = sobra
		sim.soltar_no_chao(resto, e.pos, e.id, e.pos)
		sim.emitir_a(e, "aviso", {"texto": "Mochila cheia."})
		return false
	sim.emitir_a(e, "item_ganho", {"id": it["id"], "qtd": int(it.get("qtd", 1)), "raridade": it.get("raridade", "comum"), "nome": Itens.nome(it)})
	sim.emitir_a(e, "inventario", {})
	Missoes.checar_coleta(sim, e)
	return true

static func pegar_chao(sim: WorldSim, e: Ent, id: int) -> void:
	var c: Dictionary = sim.chao.get(id, {})
	if c.is_empty(): return
	if c["dono"] != e.id and c["t"] < float(Defs.DROPS["regras"]["dono_do_drop_s"]): return
	var it: Dictionary = c["item"]
	if it["id"] != "_ouro":
		var p := Itens.achar_lugar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
		var empilha := Itens.pilha(it) > 1 and e.inv.any(func(o): return o["id"] == it["id"])
		if p.x < 0 and not empilha and not (e.classe == "humano" and Defs.ITENS.get(it["id"], {}).get("efeito") is Dictionary and Defs.ITENS[it["id"]]["efeito"].has("municao")):
			sim.emitir_a(e, "aviso", {"texto": "Mochila cheia."}); return
	sim.chao.erase(id)
	sim.emitir("chao_sumiu", {"id": id, "pego": true, "por": e.id})
	sim.emitir_a(e, "som_evento", {"ev": "moedas" if it["id"] == "_ouro" else "pegar"})
	dar_item(sim, e, it)

static func usar_item(sim: WorldSim, e: Ent, uid: int) -> void:
	var it := Itens.por_uid(e.inv, uid)
	if it.is_empty() or not e.vivo: return
	var d := Itens.defn(it["id"])
	var cat := Itens.categoria(it)
	if cat == "leitura" or d.get("tipo_missao") == "leitura":
		sim.emitir_a(e, "texto", {"titulo": d.get("nome", ""), "texto": d.get("texto", d.get("descricao", d.get("lore", "")))}); return
	if Itens.equipavel(it):
		equipar(sim, e, uid, ""); return
	if str(d.get("uso", "")).begins_with("evento:"):   # Convite dos Vigilantes: o servidor decide (EventoHermon)
		sim.emitir_a(e, "usar_evento", {"uso": d["uso"], "uid": uid, "item": it["id"]}); return
	var ef = d.get("efeito")
	if not (ef is Dictionary):
		sim.emitir_a(e, "aviso", {"texto": "Não dá para usar isto assim."}); return
	if e.aux.get("cd_pocao", 0.0) > 0.0 and (ef.has("cura_hp") or ef.has("recurso_pct")): return
	var bonus_comida := 1.25 if "lenco_cardo" in e.aux.get("bonus", {}).get("efeitos", []) and d.get("tipo") == "consumivel" else 1.0
	var usou := true
	if ef.has("cura_hp"):
		if ef.has("duracao_s"):
			var por_s := float(ef["cura_hp"]) / float(ef["duracao_s"])
			sim.criar_area({"pos": e.pos, "raio": 0.0, "dur": float(ef["duracao_s"]), "tick": 1.0, "tipo": "regen",
				"cada_tick": func(_a): sim.curar(e, por_s * bonus_comida, e)})
		else: sim.curar(e, float(ef["cura_hp"]) * bonus_comida, e)
		e.aux["cd_pocao"] = CD_POCAO
	if ef.has("xp_pct"):   # Livro do Olho Roxo: 10% do XP do nível, uma vez por personagem
		if e.flags.has("livro_olho_roxo"):
			usou = false; sim.emitir_a(e, "aviso", {"texto": "Você já leu este livro."})
		else:
			e.flags["livro_olho_roxo"] = true
			ganhar_xp(sim, e, int(Defs.xp_para_proximo(e.nivel) * float(ef["xp_pct"]) / 100.0), "livro")
	if ef.has("cura_hp_pct"):
		var total := e.hp_max * float(ef["cura_hp_pct"]) / 100.0
		if ef.has("duracao_s"):   # Frasco de Bílis Dourado: a cura vem ao longo do tempo
			var por_s := total / float(ef["duracao_s"])
			sim.criar_area({"pos": e.pos, "raio": 0.0, "dur": float(ef["duracao_s"]), "tick": 1.0, "tipo": "regen",
				"cada_tick": func(_a): sim.curar(e, por_s, e)})
		else: sim.curar(e, total, e)
	if ef.has("recurso_pct"):
		if e.classe == "cultista": sim.curar(e, e.hp_max * float(ef["recurso_pct"]) * 0.5, e)
		else: e.rec = clampf(e.rec + e.rec_max * float(ef["recurso_pct"]), 0.0, e.rec_max)   # negativo: Coração de Vidro tira recurso
		e.aux["cd_pocao"] = CD_POCAO
	if ef.has("remove"):
		for s in ef["remove"]:
			if e.status.erase(s): sim.emitir("status", {"id": e.id, "s": s, "on": false})
	if ef.has("res_veneno"): add_buff(sim, e, "antidoto", float(ef.get("duracao_s", 60)), {})
	if ef.has("buff"):
		var bf: Dictionary = ef["buff"]
		var mods := {}
		for k in bf:
			if Itens.ATTR.has(k): mods[Itens.ATTR[k]] = float(bf[k])
		add_buff(sim, e, it["id"], float(bf.get("duracao_s", 300)), mods)
	if ef.has("teleporta"):
		canalizar(sim, e, float(ef.get("canalizar_s", 3)), "Vela de Retorno", func(): _ir_para_casa(sim, e))
	if ef.has("arremesso"):
		var alvo := sim.valido(e.alvo)
		var p: Vector2 = alvo.pos if alvo != null else e.pos + e.facing * 4.0
		var dmg: Array = ef.get("dano_area", [30, 45])
		sim.lancar(e, {"vel": 10.0, "dir": (p - e.pos).normalized(), "alcance": e.pos.distance_to(p), "vfx": "frasco"},
			{"base_fixa": (float(dmg[0]) + float(dmg[1])) * 0.5, "area": true, "elemento": "sagrado", "sensacao": "area"})
	if ef.has("repele"): add_buff(sim, e, "repele_" + str(ef["repele"]), float(ef.get("duracao_s", 30)), {})
	if ef.has("abre") and it["id"] == "bau_dourado": Loot.abrir_dourado(sim, e)   # baú dourado: abre no inventário (18/10)
	elif ef.has("abre"): usou = false; sim.emitir_a(e, "aviso", {"texto": "Use num baú de ferro."})
	if usou:
		Itens.remover(e.inv, it["id"], 1)
		sim.emitir_a(e, "som_evento", {"ev": "pocao"})
		sim.emitir_a(e, "inventario", {})

static func cmd_pocao(sim: WorldSim, e: Ent, tipo: String) -> void:
	var ordem: Array
	match tipo:
		"vida": ordem = POCOES_VIDA
		"recurso": ordem = POCOES_RECURSO
		"antidoto": ordem = ["antidoto_querosene", "agua_benta"]
	for id in ordem:
		for it in e.inv:
			if it["id"] == id:
				usar_item(sim, e, it["uid"]); return
	sim.emitir_a(e, "aviso", {"texto": "Sem %s na mochila." % {"vida": "poção de vida", "recurso": "poção de recurso", "antidoto": "antídoto"}[tipo]})

static func add_buff(sim: WorldSim, e: Ent, id: String, dur: float, mods: Dictionary) -> void:
	for b in e.buffs:
		if b["id"] == id: e.buffs.erase(b); break
	e.buffs.append({"id": id, "t": dur, "dur": dur, "mods": mods})
	if e.tipo == "jogador": Regras.recalc_jogador(e)
	sim.emitir_a(e, "buff", {"id": e.id, "buff": id, "on": true, "t": dur})

static func slot_para(e: Ent, it: Dictionary) -> String:
	var s := Itens.slot_de(it)
	if s == "anel": return "anel2" if e.equip.has("anel1") and not e.equip.has("anel2") else "anel1"
	return s

static func equipar(sim: WorldSim, e: Ent, uid: int, slot: String) -> void:
	var it := Itens.por_uid(e.inv, uid)
	if it.is_empty(): return
	var erro := Itens.pode_usar(it, e)
	if erro != "":
		sim.emitir_a(e, "aviso", {"texto": erro}); return
	var s := slot if slot != "" else slot_para(e, it)
	if Itens.slot_de(it) == "anel" and not s in ["anel1", "anel2"]: s = "anel1"
	elif Itens.slot_de(it) != "anel" and s != Itens.slot_de(it): return
	var d := Itens.defn(it["id"])
	e.inv.erase(it)
	var tirar: Array = []
	if e.equip.has(s): tirar.append(e.equip[s])
	if s == "arma" and int(d.get("maos", 1)) == 2 and e.equip.has("segunda_mao"): tirar.append(e.equip["segunda_mao"]); e.equip.erase("segunda_mao")
	if s == "segunda_mao" and e.equip.has("arma") and int(Itens.defn(e.equip["arma"]["id"]).get("maos", 1)) == 2: tirar.append(e.equip["arma"]); e.equip.erase("arma")
	e.equip[s] = it
	for t in tirar:
		if Itens.guardar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, t) > 0:
			sim.soltar_no_chao(t, e.pos, e.id, e.pos)
	Regras.recalc_jogador(e)
	var cat := Itens.categoria(it)
	sim.emitir_a(e, "som_evento", {"ev": "equipar_arma" if s == "arma" else ("equipar_joia" if cat == "acessorio" else "equipar_armadura")})
	sim.emitir_a(e, "inventario", {}); sim.emitir_a(e, "stats", {"id": e.id})

static func desequipar(sim: WorldSim, e: Ent, slot: String, x: int = -1, y: int = -1) -> void:
	if not e.equip.has(slot): return
	var it: Dictionary = e.equip[slot]
	if x >= 0 and Itens.cabe_em(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it, x, y):
		it["x"] = x; it["y"] = y; e.inv.append(it)
	else:
		var p := Itens.achar_lugar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
		if p.x < 0: sim.emitir_a(e, "aviso", {"texto": "Mochila cheia."}); return
		it["x"] = p.x; it["y"] = p.y; e.inv.append(it)
	e.equip.erase(slot)
	Regras.recalc_jogador(e)
	sim.emitir_a(e, "inventario", {}); sim.emitir_a(e, "stats", {"id": e.id})

static func mover_item(sim: WorldSim, e: Ent, uid: int, de: String, para: String, x: int, y: int) -> void:
	var src: Array = e.inv if de == "mochila" else e.armazem
	var dst: Array = e.inv if para == "mochila" else e.armazem
	var it := Itens.por_uid(src, uid)
	if it.is_empty(): return
	var W := Itens.MOCHILA_W if para == "mochila" else Itens.ARMAZEM_W
	var H := Itens.MOCHILA_H if para == "mochila" else Itens.ARMAZEM_H
	if not Itens.cabe_em(dst, W, H, it, x, y, uid if src == dst else -1): return
	src.erase(it)
	it["x"] = x; it["y"] = y
	dst.append(it)
	sim.emitir_a(e, "inventario", {})

static func soltar_item(sim: WorldSim, e: Ent, uid: int) -> void:
	var it := Itens.por_uid(e.inv, uid)
	if it.is_empty(): return
	if Itens.categoria(it) == "missao" or Itens.vinculado(it):
		sim.emitir_a(e, "aviso", {"texto": "Item de missão: melhor não jogar fora."}); return
	e.inv.erase(it)
	sim.soltar_no_chao(it, e.pos, e.id, e.pos)
	sim.emitir_a(e, "som_evento", {"ev": "soltar"})
	sim.emitir_a(e, "inventario", {})

# =================================================================== serviços (loja, ferreiro, armazém, treinador)
const ESTOQUE_GERAL := {
	"vigilia": ["pocao_vida_p", "pocao_vida_m", "pocao_recurso_p", "pocao_recurso_m", "antidoto_querosene", "agua_benta", "vela_retorno", "gazua"],
	"arautos": ["pocao_vida_p", "pocao_vida_m", "pocao_recurso_p", "pocao_recurso_m", "antidoto_querosene", "agua_benta", "vela_retorno", "gazua"],
}

static func estoque(e: Ent, loja_id: String) -> Array:
	var l: Dictionary = Defs.LOJAS.get(loja_id, {})
	var ids: Array = l.get("itens", []).duplicate()
	# poção tem que ser fácil de comprar (farm_auto.json): todo vendedor tem o básico
	if loja_id in ["loja_anselmo", "loja_lucio", "loja_malfas", "loja_tobias", "loja_cardo", "loja_corvina",
			"loja_hulda", "loja_zilpa", "loja_bartimeu", "loja_carrinho_bartimeu", "loja_zaqueu_cobrador"]:
		for i in ESTOQUE_GERAL.get(e.faccao, ESTOQUE_GERAL["vigilia"]):
			if not i in ids: ids.append(i)
	if loja_id in ["loja_tobias", "loja_malfas", "loja_bartimeu", "loja_carrinho_bartimeu"]:
		for i in ["cartuchos_sal", "virotes_prata", "balas_chumbo", "gazua"]:
			if not i in ids: ids.append(i)
	# armas e armaduras de nível baixo para a classe do jogador
	if loja_id in ["loja_tobias", "loja_malfas", "loja_bartimeu", "loja_carrinho_bartimeu"]:
		for id in Defs.POR_TAG.get("equip:faixa1", []):
			var d: Dictionary = Defs.ITENS[id]
			var cl = d.get("classes")
			if (cl == null or (cl is Array and e.classe in cl)) and int(d.get("nivel", 1)) <= maxi(3, e.nivel): ids.append(id)
	return ids.filter(func(i): return Defs.ITENS.has(i))

static func abrir_servico(sim: WorldSim, e: Ent, s: Dictionary, npc: Ent) -> void:
	var d := {"tipo": s["tipo"], "npc": npc.id, "nome": npc.nome}
	match s["tipo"]:
		"loja":
			var l: Dictionary = Defs.LOJAS.get(s["id"], {})
			d["titulo"] = l.get("nome", npc.nome); d["fala"] = l.get("fala_ao_abrir", "")
			d["itens"] = estoque(e, s["id"])
			d["loja"] = s["id"]
		"ferreiro":
			d["titulo"] = "Forja de " + npc.nome.split(" ")[0]; d["fala"] = Defs.FERREIROS.get(npc.kind, {}).get("fala_ao_abrir", "")
		"armazem":
			var ar: Dictionary = Defs.NPCS.get(npc.kind, {}).get("armazem", {})   # Gustavo, o Primarca (0.8.3) traz o próprio título
			d["titulo"] = ar.get("titulo", "Armazém do Coveiro"); d["fala"] = ar.get("fala", "O que é guardado com os mortos não some.")
		"treinador":
			d["titulo"] = "Treino com " + npc.nome; d["fala"] = "Mostre o que aprendeu. Depois esqueça e aprenda direito."
	sim.emitir_a(e, "servico", d)

static func comprar(sim: WorldSim, e: Ent, id: String, qtd: int = 1) -> void:
	var serv: Dictionary = e.aux.get("servico", {})
	if serv.get("tipo") != "loja" or not id in estoque(e, serv["id"]): return
	var it := Itens.novo(id, qtd)
	if Defs.ITENS[id].get("raridade", "") == "rolada":
		it = Itens.gerar_equip(id, sim.rng, "comum", 1); it["raridade"] = "comum"; it["opcoes"] = []; it["refino"] = 0
	var p := Itens.preco(it) * qtd
	if e.ouro < p:
		sim.emitir_a(e, "aviso", {"texto": "Ouro insuficiente."}); sim.emitir_a(e, "som_evento", {"ev": "erro"}); return
	e.ouro -= p
	dar_item(sim, e, it)
	sim.emitir_a(e, "som_evento", {"ev": "comprar"})
	sim.emitir_a(e, "ouro", {"valor": -p})

static func vender(sim: WorldSim, e: Ent, uid: int) -> void:
	if e.aux.get("servico", {}).get("tipo") != "loja": return
	var it := Itens.por_uid(e.inv, uid)
	if it.is_empty(): return
	var v := Itens.preco_venda(it)
	if v <= 0 or Itens.categoria(it) == "missao" or Itens.vinculado(it):
		sim.emitir_a(e, "aviso", {"texto": "Ninguém compra isto."}); return
	e.inv.erase(it)
	e.ouro += v
	sim.emitir_a(e, "som_evento", {"ev": "vender"})
	sim.emitir_a(e, "ouro", {"valor": v})
	sim.emitir_a(e, "inventario", {})

## Refino com lágrimas (drops.json "refino_com_lagrimas"): Angélica +0..+6 sempre dá certo;
## Sanguínea +6..+15 com chance caindo; falha tira 1 nível (2 do +11 em diante, nunca abaixo de +6). Nunca quebra.
static func refinar(sim: WorldSim, e: Ent, uid_item: int, onde: String) -> void:
	var it: Dictionary = e.equip.get(onde, {}) if onde != "mochila" else Itens.por_uid(e.inv, uid_item)
	if it.is_empty() or not Itens.equipavel(it): return
	var R: Dictionary = Defs.DROPS["refino_com_lagrimas"]
	var r := int(it.get("refino", 0))
	var maximo := int(R.get("maximo", 15))
	if r >= maximo:
		sim.emitir_a(e, "aviso", {"texto": "Já está no +%d." % maximo}); return
	var joia := "lagrima_angelica" if r < int(R["lagrima_angelica"]["ate"]) else "lagrima_sanguinea"
	var n_joias := custo_joias(r)
	if Itens.contar(e.inv, joia) < n_joias:
		sim.emitir_a(e, "aviso", {"texto": "Precisa de %d %s." % [n_joias, Defs.ITENS[joia]["nome"]]}); return
	var custo_ouro := 50 * (r + 1)
	if e.ouro < custo_ouro:
		sim.emitir_a(e, "aviso", {"texto": "O ferreiro cobra %d de ouro." % custo_ouro}); return
	e.ouro -= custo_ouro
	Itens.remover(e.inv, joia, n_joias)
	if r >= 10 and sim.rng.randf() < 0.15:   # acima do +10 o item pode quebrar (15%, Jefin 17/10): a lágrima e o ouro já foram
		if onde == "mochila": e.inv.erase(it)
		else: e.equip.erase(onde)
		Regras.recalc_jogador(e)
		sim.emitir_a(e, "aviso", {"texto": "%s quebrou ao passar do +10." % Itens.nome(it)})
		sim.emitir_a(e, "som_evento", {"ev": "refino_falha"})
		sim.emitir_a(e, "inventario", {}); sim.emitir_a(e, "stats", {"id": e.id})
		return
	var ok := joia == "lagrima_angelica" or sim.rng.randf() < chance_refino(r + 1)
	if ok: it["refino"] = r + 1
	else: it["refino"] = maxi(mini(r, 6), r - (2 if r + 1 >= 11 else 1))
	Regras.recalc_jogador(e)
	sim.emitir_a(e, "refino", {"ok": ok, "nivel": int(it["refino"]), "nome": Itens.nome(it)})
	sim.emitir_a(e, "som_evento", {"ev": "refino_sucesso" if ok else "refino_falha"})
	sim.emitir_a(e, "inventario", {}); sim.emitir_a(e, "stats", {"id": e.id})

## Lágrimas por tentativa de refino (balanco.refino_joias, 18/10): de 1 no +0 até 10 no último nível.
static func custo_joias(r: int) -> int:
	var J: Dictionary = Defs.DROPS["balanco"]["refino_joias"]
	var maximo := int(Defs.DROPS["refino_com_lagrimas"].get("maximo", 15))
	var lo := int(J["min"]); var hi := int(J["max"])
	return lo + r * (hi - lo) / maxi(1, maximo - 1)

## Chance de chegar ao nível alvo (1.0 até o +6).
static func chance_refino(alvo: int) -> float:
	var t: Dictionary = Defs.DROPS["refino_com_lagrimas"]["lagrima_sanguinea"]["chance_para"]
	return float(t.get("+%d" % alvo, 1.0))

## Treinador: redistribui os pontos de atributo (custa ouro).
static func redistribuir(sim: WorldSim, e: Ent) -> void:
	var custo_t := 20 * e.nivel
	if e.ouro < custo_t:
		sim.emitir_a(e, "aviso", {"texto": "Custa %d de ouro." % custo_t}); return
	e.ouro -= custo_t
	var base: Dictionary = Defs.CLASSES[e.classe]["atributos_iniciais"]
	var gasto := 0
	for k in e.stats:
		gasto += roundi((float(e.stats[k]) - float(base[k])) / float(Defs.FORM["peso_por_ponto"])); e.stats[k] = float(base[k])
	e.pontos += gasto
	Regras.recalc_jogador(e)
	sim.emitir_a(e, "stats", {"id": e.id}); sim.emitir_a(e, "aviso", {"texto": "Pontos devolvidos: %d." % gasto})

# =================================================================== save
static func salvar(e: Ent, sim: WorldSim) -> Dictionary:
	return {"v": 2, "classe": e.classe, "evolucao": e.evolucao, "nome": e.nome, "nivel": e.nivel, "xp": e.xp, "pontos": e.pontos, "stats": e.stats,
		"ouro": e.ouro, "municao": e.municao, "inv": e.inv, "equip": e.equip, "armazem": e.armazem, "missoes": e.missoes,
		"flags": e.flags, "vistas": e.vistas, "mapa": sim.mapa_id if Defs.eh_mapa_casa(sim.mapa_id) else Defs.mapa_casa(e.faccao),
		"pos": [e.pos.x, e.pos.y] if Defs.eh_mapa_casa(sim.mapa_id) else [], "abates": e.abates, "pity": e.pity_raro, "uid": Itens._uid,
		"auto": cfg_auto(e), "talentos": talentos(e)}

static func carregar(e: Ent, s: Dictionary) -> void:
	e.nivel = int(s.get("nivel", 1)); e.xp = int(s.get("xp", 0)); e.pontos = int(s.get("pontos", 0))
	e.evolucao = str(s.get("evolucao", ""))
	if e.evolucao != "" and Evolucao.defn(e.evolucao).get("classe_base", "") != e.classe: e.evolucao = ""   # save adulterado ou JSON mudou
	for k in s.get("stats", {}): e.stats[k] = float(s["stats"][k])
	e.ouro = int(s.get("ouro", 0)); e.municao = int(s.get("municao", 0))
	e.inv = s.get("inv", []); e.equip = s.get("equip", {}); e.armazem = s.get("armazem", [])
	for lst in [e.inv, e.armazem]:
		for it in lst:
			it["uid"] = int(it["uid"]); it["x"] = int(it.get("x", 0)); it["y"] = int(it.get("y", 0)); it["qtd"] = int(it.get("qtd", 1)); it["refino"] = int(it.get("refino", 0))
			it["id"] = {"lagrima_anjo": "lagrima_angelica", "fragmento_alma": "lagrima_sanguinea"}.get(it["id"], it["id"])   # joias antigas (até a 0.8.x)
	for k in e.equip:
		e.equip[k]["uid"] = int(e.equip[k]["uid"]); e.equip[k]["refino"] = int(e.equip[k].get("refino", 0))
	e.missoes = s.get("missoes", {}); e.flags = s.get("flags", {}); e.vistas = s.get("vistas", {})
	Biblioteca.restaurar(e)
	for mid in e.missoes:
		var p: Array = e.missoes[mid].get("prog", [])
		for i in p.size(): p[i] = int(p[i])
	e.abates = s.get("abates", {}); e.pity_raro = int(s.get("pity", 0))
	_cfg_do_save(e, s.get("auto"))
	_talentos_do_save(e, s.get("talentos"))
	Itens._uid = maxi(Itens._uid, int(s.get("uid", 1000)))

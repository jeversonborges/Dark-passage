class_name Familiar
## Familiar do Cultista (racial "Pacto do Familiar", 0.8.9): um demônio que anda com o dono, evolui pelo nível
## dele e ataca quem bateu no dono. Números em classes_base.json > cultista > racial > familiar.
## Não ganha XP nem solta loot. Sem tecla e sem slot: nasce com o Cultista.
## 0.9.3 (Jefin, 2026-10-17): é invulnerável (não recebe dano, não morre, monstros não o miram), é DPS e todas as
## formas batem em área (ataque.area_raio). Última forma: Líder dos Demônios no nível 60.

const DONO_VAR := ["max_hp_dono", "defesa_dono", "dano_magico_dono"]
const SEGUE_MAX := 12.0       ## acima disso teleporta para perto do dono
const VOLTA_S := 30.0         ## tempo para voltar sozinho depois de morrer (só se algo matar à força)
const INVULN := 1.0e9         ## invuln_t "para sempre"

static func dados() -> Dictionary:
	return Defs.CLASSES["cultista"]["racial"]["familiar"]

## Forma que o nível atual do dono pede (a de maior nivel_dono que ele já alcançou).
static func forma_para(nivel: int) -> Dictionary:
	var escolhida := {}
	for f in dados()["formas"]:
		if nivel >= int(f["nivel_dono"]): escolhida = f
	return escolhida

## Valor de um campo de forma ("max_hp_dono * 0.35") com os números do dono.
static func _valor(txt: String, dono: Ent) -> float:
	return Defs.expr(txt, PackedStringArray(DONO_VAR), [dono.hp_max, dono.defesa, dono.dano_max])

static func criar(sim: WorldSim, dono: Ent) -> void:
	if dono.classe != "cultista" or dados().is_empty(): return
	var antigo: Ent = sim.ents.get(int(dono.aux.get("familiar_id", -1)))
	if antigo != null: return
	var f := forma_para(dono.nivel)
	if f.is_empty(): return
	var fam := Ent.new()
	fam.id = sim.novo_id(); fam.tipo = "invocacao"; fam.dono = dono.id
	fam.aux["familiar"] = true
	fam.pos = sim.celula_livre_perto(dono.pos + Vector2(-1.2, 0.6))
	fam.casa = fam.pos
	fam.nivel = dono.nivel
	fam.raio = 0.45
	sim.ents[fam.id] = fam
	dono.aux["familiar_id"] = fam.id
	_aplicar_forma(fam, dono, f, true)

## Põe os números e o nome da forma no familiar. cheio = cura total (nascer, evoluir).
static func _aplicar_forma(fam: Ent, dono: Ent, f: Dictionary, cheio: bool) -> void:
	fam.kind = f["id"]
	fam.nome = f["nome"]
	fam.tags = (f.get("tags", []) as Array).duplicate()
	fam.hp_max = maxf(1.0, _valor(f["hp"], dono))
	fam.hp = fam.hp_max if cheio else minf(fam.hp, fam.hp_max)
	fam.defesa = _valor(f["defesa"], dono)
	var dano := _valor(f["dano"], dono)
	fam.dano_max = maxf(1.0, dano); fam.dano_min = fam.dano_max * 0.8
	fam.intervalo = float(f["intervalo"])
	fam.alcance = float(f["alcance"])
	fam.elemento = str(f.get("elemento", "fogo"))
	fam.vel = dono.vel * float(dados()["segue"]["vel_mult_dono"])
	fam.ar = dono.ar; fam.er = dono.er
	fam.aux["ameaca_mult"] = float(f.get("ameaca_mult", 1.0))
	fam.aux["forma"] = f["id"]
	fam.aux["passiva"] = f.get("passiva", {})
	fam.aux["area_raio"] = float((f.get("ataque", {}) as Dictionary).get("area_raio", 0.0))
	_blindar(fam)

## Invulnerável (0.9.3): fora do alcance de golpes e áreas (alvejavel = false) e sem dano por tempo (invuln_t).
static func _blindar(fam: Ent) -> void:
	fam.alvejavel = false
	fam.invuln_t = INVULN
	fam.hp = fam.hp_max
	fam.status.clear()

## Passo do familiar (chamado pelo world_sim para invocações com aux["familiar"]).
static func passo(sim: WorldSim, fam: Ent, dt: float) -> void:
	var dono: Ent = sim.ents.get(fam.dono)
	if dono == null or not dono.vivo: return
	if fam.alvejavel or fam.invuln_t < 1000.0 or fam.hp < fam.hp_max: _blindar(fam)
	if not fam.pronto(): return
	var f := forma_para(dono.nivel)
	if not f.is_empty() and f["id"] != fam.kind:
		_evoluir(fam, dono, f); return
	var d := fam.pos.distance_to(dono.pos)
	if d > SEGUE_MAX:
		fam.pos = sim.celula_livre_perto(dono.pos + Vector2(-1.2, 0.6)); fam.caminho.clear(); return
	# só ataca quem bateu no dono; sem isso, fica seguindo o dono sem puxar nada
	var alvo := sim.valido(fam.alvo)
	if alvo != null and dono.pos.distance_to(alvo.pos) > float(dados()["alvo"]["larga_alvo_se_dono_a_mais_de_tiles"]):
		alvo = null
	if alvo == null:
		alvo = sim.valido(int(dono.aux.get("ultimo_agressor", -1)))
		if alvo != null and (not alvo.alvejavel or alvo.id == dono.id or dono.pos.distance_to(alvo.pos) > float(dados()["alvo"]["larga_alvo_se_dono_a_mais_de_tiles"])):
			alvo = null
	fam.alvo = alvo.id if alvo != null else -1
	if alvo == null:
		if d > 2.0:
			if fam.caminho.is_empty(): sim.ir_para(fam, dono.pos)
			sim.mover_ao_longo(fam, dt)
		return
	if _especiais(sim, fam, dono, alvo, dt): return
	var dist := fam.pos.distance_to(alvo.pos) - alvo.raio
	if dist <= fam.alcance:
		fam.caminho.clear()
		if fam.cd_basico <= 0.0:
			fam.cd_basico = fam.intervalo
			var aid := alvo.id
			sim.iniciar_acao(fam, {"preparo": 0.25, "rec": 0.2, "alvo": aid, "impacto": func():
				var a := sim.valido(aid)
				if a == null: return
				if fam.alcance > 2.5:
					sim.lancar(fam, {"vel": 9.0, "alvo": aid, "vfx": "torreta", "ao_atingir": func(o: Ent): _respingo(sim, fam, o)},
						{"mult": 1.0, "elemento": fam.elemento, "nunca_erra": true})
				else:
					sim.aplicar_golpe(fam, a, {"mult": 1.0, "nunca_erra": true})
					_respingo(sim, fam, a)
			})
	else:
		if fam.caminho.is_empty(): sim.ir_para(fam, alvo.pos)
		sim.mover_ao_longo(fam, dt)

## Ataque em área (0.9.3): o golpe básico também acerta os outros inimigos em volta do alvo (ataque.area_raio).
static func _respingo(sim: WorldSim, fam: Ent, alvo: Ent) -> void:
	var r := float(fam.aux.get("area_raio", 0.0))
	if r <= 0.0 or alvo == null: return
	for o in sim.inimigos_de(fam, alvo.pos, r):
		if o.id == alvo.id or o.tipo == "jogador" or o.tipo == "npc" or o.tipo == "objeto": continue
		sim.aplicar_golpe(fam, o, {"mult": 1.0, "nunca_erra": true})

## Troca de forma: casulo de 2 s, e sai com vida cheia (continua invulnerável).
static func _evoluir(fam: Ent, dono: Ent, f: Dictionary) -> void:
	_aplicar_forma(fam, dono, f, true)
	fam.caminho.clear()

## Guarda-Costas (passiva de Algoz e Tirano): parte do dano que ia para o dono vai para o familiar, se ele estiver perto.
## Devolve o dano que sobra para o dono.
static func desviar(sim: WorldSim, dono: Ent, dano: float, atk: Ent) -> float:
	var fam: Ent = sim.ents.get(int(dono.aux.get("familiar_id", -1)))
	if fam == null or not fam.vivo or dano <= 0.0: return dano
	var passiva: Dictionary = fam.aux.get("passiva", {})
	if passiva.get("id", "") != "guarda_costas": return dano   # 0.9.3: nenhuma forma tem mais (o familiar é DPS)
	if fam.pos.distance_to(dono.pos) > float(passiva.get("raio_tiles", 4.0)): return dano
	var parte := dano * float(passiva.get("desvia_dano_do_dono", 0.0))
	sim.emitir("dano", {"id": fam.id, "de": atk.id, "valor": roundi(parte), "estilo": "escudo"})
	return dano - parte   # invulnerável: absorve sem perder vida

## Especiais do familiar (Algoz: Puxão de Corrente; Tirano: Canhão de Brasa e Rugido da Legião; Líder: Decreto do Lorde).
## Usam recarga própria, e só miram quem bateu no dono (o alvo atual do familiar).
static func _especiais(sim: WorldSim, fam: Ent, dono: Ent, alvo: Ent, dt: float) -> bool:
	fam.aux["esp_cd"] = float(fam.aux.get("esp_cd", 0.0)) - dt
	if float(fam.aux["esp_cd"]) > 0.0: return false
	var f: Dictionary = forma_para(dono.nivel)
	var dist := fam.pos.distance_to(alvo.pos)
	if fam.kind == "familiar_algoz" and dist <= 5.0 and f.has("especial"):
		fam.aux["esp_cd"] = float(f["especial"]["recarga"])
		var dir := (fam.pos - alvo.pos).normalized()
		if alvo.tipo != "chefe" and alvo.arquetipo != "elite":
			sim.deslocar(alvo, alvo.pos + dir * maxf(0.0, dist - 1.2), 0.3, {"tipo": "puxao"})
		sim.aplicar_golpe(fam, alvo, {"mult": 0.8, "nunca_erra": true})
		_respingo(sim, fam, alvo)
		return true
	if fam.kind == "familiar_tirano" and f.has("especial_2") and sim.inimigos_de(fam, dono.pos, 3.0).size() >= 2:
		fam.aux["esp_cd"] = float(f["especial_2"]["recarga"])
		for o in sim.inimigos_de(fam, fam.pos, float(f["especial_2"]["area_raio"])):
			if o.tipo == "jogador" or o.tipo == "npc" or o.tipo == "objeto": continue
			sim.aplicar_golpe(fam, o, {"mult": float(f["especial_2"].get("mult", 0.6)), "nunca_erra": true})
		return true
	if (fam.kind == "familiar_tirano" or fam.kind == "familiar_lider") and f.has("especial") and dist <= float(f["especial"].get("alcance", 6.0)):
		fam.aux["esp_cd"] = float(f["especial"]["recarga"])
		for o in sim.inimigos_de(fam, alvo.pos, float(f["especial"]["area_raio"])):
			if o.tipo == "jogador" or o.tipo == "npc" or o.tipo == "objeto": continue
			sim.aplicar_golpe(fam, o, {"mult": float(f["especial"]["mult"]), "nunca_erra": true})
		return true
	return false

## Volta sozinho depois de morrer, ao lado do dono (chamado pelo world_sim quando passa VOLTA_S).
static func renascer(sim: WorldSim, fam: Ent) -> void:
	var dono: Ent = sim.ents.get(fam.dono)
	if dono == null or not dono.vivo: return
	fam.vivo = true; fam.morto_t = 0.0
	fam.pos = sim.celula_livre_perto(dono.pos + Vector2(-1.2, 0.6)); fam.casa = fam.pos
	fam.caminho.clear(); fam.alvo = -1
	_aplicar_forma(fam, dono, forma_para(dono.nivel), true)

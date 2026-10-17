class_name Demiurgo
## Cetro do Demiurgo (entregas/cetro_demiurgo): a arma única do administrador, fora do balanceamento de propósito.
## Cada efeito é um gancho chamado com uma linha de onde acontece (jogador.gd, world_sim.gd, ia.gd, regras.gd);
## a lógica fica toda aqui. O item só existe na conta GM (servidor.gd: _cetro_demiurgo).

const ITEM := "cetro_do_demiurgo"
const RAIO_VERBO := 8.0        # Verbo: o ataque básico atinge todos os inimigos neste raio
const CHANCE_JUIZO := 0.10     # Juízo do Demiurgo: por golpe
const JUIZO_CHEFE := 0.10      # fração da vida máxima que um chefe perde
const SOPRO := 0.10            # Sopro do Primeiro Dia: fração de HP e recurso por segundo
const RECARGA := 0.1           # A Mão que Mede: recarga ×0,1 (-90%)
const RAIO_AURA := 10.0
const DUR_AURA := 1.5          # o buff é renovado a cada segundo
const AURA := "aura_demiurgica"
const AURA_FRAQUEZA := "aura_demiurgica_fraqueza"

## Está com o Cetro equipado? (Itens.bonus registra o id do item em bonus.efeitos; o cliente recebe aux.bonus do próprio jogador)
static func tem(e: Ent) -> bool:
	return e != null and ITEM in e.aux.get("bonus", {}).get("efeitos", [])

# =================================================================== golpes
## Chamado de Jogador.ao_acertar: Golpe (efeito no alvo), Verbo (só no ataque básico) e Juízo (10% por golpe).
static func ao_acertar(sim: WorldSim, e: Ent, alvo: Ent, op: Dictionary) -> void:
	if not tem(e): return
	sim.emitir("vfx", {"nome": "demiurgo_golpe", "alvo": alvo.id})
	if op.get("basico", false) and not op.get("area", false): verbo(sim, e, alvo, op)
	juizo(sim, e, alvo)

## Verbo: todo ataque básico atinge todos os inimigos a 8 m com 100% do dano (mesmo esquema da Forma Colossal).
static func verbo(sim: WorldSim, e: Ent, alvo: Ent, op: Dictionary) -> void:
	for o in sim.inimigos_de(e, e.pos, RAIO_VERBO):
		if o != alvo: sim.aplicar_golpe(e, o, op.merged({"area": true, "sem_recurso": true}))
	sim.emitir("vfx", {"nome": "demiurgo_verbo", "pos": e.pos})
	sim.emitir("som_evento", {"ev": "itens/cetro_golpe", "pos": alvo.pos})

## Juízo do Demiurgo: 10% por golpe. Monstro comum morre na hora pelo caminho normal de abate (XP e saque);
## chefe perde 10% da vida máxima. Nunca em jogador, invocação ou NPC; respeita invulnerável/imune.
static func juizo(sim: WorldSim, e: Ent, alvo: Ent) -> void:
	if not alvo.vivo or not alvo.tipo in ["monstro", "chefe"] or sim.rng.randf() >= CHANCE_JUIZO: return
	if alvo.invuln_t > 0.0 or alvo.aux.get("imune", false): return
	sim.emitir("vfx", {"nome": "demiurgo_juizo", "alvo": alvo.id})
	sim.emitir("som_evento", {"ev": "itens/cetro_juizo", "pos": alvo.pos})
	sim.emitir("fala", {"id": alvo.id, "texto": "JUÍZO", "cor": "#9dffc8"})
	if alvo.tipo == "chefe":
		sim.aplicar_dano_puro(alvo, alvo.hp_max * JUIZO_CHEFE, "sagrado", e, "normal")
	else:
		alvo.hp = 0.0
		sim.matar(alvo, e)

# =================================================================== defesa
## Como em Cima, Assim Embaixo: devolve 100% do dano recebido a quem bateu (a imunidade a status fica em WorldSim.aplicar_status).
static func refletir(sim: WorldSim, e: Ent, atk: Ent, dano: float) -> void:
	if not tem(e) or atk == null or atk == e or not atk.vivo or dano <= 0.0 or tem(atk): return
	sim.aplicar_dano_puro(atk, dano, "sagrado", e, "normal")

## Sopro do Primeiro Dia: +10% da vida máxima e do recurso por segundo.
static func sopro(e: Ent, dt: float) -> void:
	if not tem(e) or not e.vivo: return
	e.hp = minf(e.hp_max, e.hp + e.hp_max * SOPRO * dt)
	e.rec = minf(e.rec_max, e.rec + e.rec_max * SOPRO * dt)

## A Mão que Mede: as skills recarregam em 10% do tempo (o custo zero fica em Jogador.custo).
static func mult_recarga(e: Ent) -> float:
	return RECARGA if tem(e) else 1.0

# =================================================================== aura
## Aura Demiúrgica (tick de 1 s): aliados a 10 m (ele incluído) ganham +50% de dano e de XP; monstros e chefes
## a 10 m batem 50% mais fraco. Renova o buff pelo id em vez de empilhar.
static func aura(sim: WorldSim, e: Ent, dt: float) -> void:
	if not tem(e) or not e.vivo or floori(sim.tempo) == floori(sim.tempo - dt): return
	for o: Ent in sim.ents.values():
		if not o.vivo or o.pos.distance_to(e.pos) > RAIO_AURA: continue
		if o.tipo == "jogador" and not e.eh_inimigo_de(o): _renovar(sim, o, AURA, {"dano": 0.5, "xp": 0.5})
		elif o.tipo in ["monstro", "chefe"]: _renovar(sim, o, AURA_FRAQUEZA, {"dano": -0.5})

static func _renovar(sim: WorldSim, o: Ent, id: String, mods: Dictionary) -> void:
	for b in o.buffs:
		if b["id"] == id: b["t"] = DUR_AURA; return
	o.buffs.append({"id": id, "t": DUR_AURA, "dur": DUR_AURA, "mods": mods})
	if o.tipo == "jogador":
		Regras.recalc_jogador(o)
		sim.emitir_a(o, "buff", {"id": o.id, "buff": id, "on": true, "t": DUR_AURA})

## Buff de monstro ninguém decrementa (só o dos jogadores, em Jogador.passo): a fraqueza da aura expira aqui (WorldSim._passo_ent).
static func expirar(e: Ent, dt: float) -> void:
	for b in e.buffs.duplicate():
		if b["id"] == AURA_FRAQUEZA:
			b["t"] -= dt
			if b["t"] <= 0.0: e.buffs.erase(b)

## Enquanto o Cetro está equipado, aux.aura = "demiurgo" (chave pública: todos veem). Ao tirar, volta a aura da
## Biblioteca (flags.bib_aura) ou some; a aura da Biblioteca nunca é apagada por aqui. Chamado de Regras.recalc_jogador.
static func atualizar_aura(e: Ent) -> void:
	if tem(e): e.aux["aura"] = "demiurgo"
	elif str(e.aux.get("aura", "")) == "demiurgo":
		if e.flags.has("bib_aura"): e.aux["aura"] = str(e.flags["bib_aura"])
		else: e.aux.erase("aura")

# =================================================================== servidor
## Tira o Cetro de quem não é mais GM (mochila, equipamento e armazém). Devolve true se tirou algo.
## A flag de entrega é apagada: se a conta voltar a ser GM, recebe de novo.
static func tirar(sim: WorldSim, e: Ent) -> bool:
	var tirou := false
	for lst in [e.inv, e.armazem]:
		for it in lst.duplicate():
			if it.get("id", "") == ITEM: lst.erase(it); tirou = true
	for s in e.equip.keys():
		if e.equip[s].get("id", "") == ITEM: e.equip.erase(s); tirou = true
	if tirou:
		e.flags.erase("cetro_demiurgo")
		Regras.recalc_jogador(e)
		sim.emitir_a(e, "inventario", {}); sim.emitir_a(e, "stats", {"id": e.id})
	return tirou

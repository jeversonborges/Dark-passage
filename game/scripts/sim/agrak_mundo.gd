class_name AgrakMundo
extends RefCounted
## Liga o controlador da Arena do Agrak (agrak_ctl.gd) ao mundo: cria os chefes como monstros comuns (a IA e os
## golpes são os de sempre), fecha e abre os portões, prende os gladiadores no Círculo de Ferro, troca de lado
## na luta final e manda os derrotados para o camarote. Roda dentro de uma instância do mapa "agrak".

var sim: WorldSim
var ctl: AgrakCtl
var dados: Dictionary
var geo: Dictionary              # mapa["agrak"] do mapa agrak (centro, camarote, portoes, pontos de chefe)
var jogadores_ids: Array = []    # entrada original (não muda)
var chefes: Dictionary = {}      # id da entidade -> kind (só os vivos)
var raio_anel := -1.0
var _fila: Array = []
var leoes_nascidos := 0
var encerrado := false

func _init(p_sim: WorldSim, p_dados: Dictionary, ids: Array) -> void:
	sim = p_sim; dados = p_dados
	jogadores_ids = ids.duplicate()
	geo = sim.mapa.get("agrak", {})
	_registrar_chefes()
	ctl = AgrakCtl.new(dados, self)
	sim.evento.connect(_ao_evento)
	for i in jogadores_ids:
		var e: Ent = sim.ents.get(i)
		if e != null: e.aux.erase("agrak_espectador")

## Começa a Arena com os inscritos. Abaixo do mínimo, a ctl cancela e devolve o ouro.
func iniciar() -> bool:
	for g in ["portao_leoes", "portao_gigante", "portao_gladiadores"]: portao(g, false)
	return ctl.iniciar(jogadores_ids)

func passo(dt: float) -> void:
	_tick_fila(dt)
	if encerrado: return
	ctl.passo(dt)
	if ctl.etapa_atual() == "luta_gigante": _passo_piao(dt)
	else: piao = {"estado": "", "t": 0.0, "tick": 0.0, "proximo": 15.0, "gig_t": 0.0}
	_leoes_separados(dt)

## Pião do Golias (README): anel vermelho 0,7 s; depois gira 10 s andando devagar atrás de quem tem mais
## ameaça, tirando 5% do HP máximo a cada 0,25 s de quem está no anel (ignora defesa); depois fica tonto 4 s.
## Primeiro aos 15 s, depois a cada 30 s (20 s e raio 4 com o Golias abaixo de 40%). Não dá para interromper.
var piao := {"estado": "", "t": 0.0, "tick": 0.0, "proximo": 15.0, "gig_t": 0.0}

func _golias() -> Ent:
	for id in chefes.keys():
		if chefes[id] == "golias": return sim.ents.get(id)
	return null

func _passo_piao(dt: float) -> void:
	var g := _golias()
	if g == null or not g.vivo: return
	piao["gig_t"] += dt
	var fase2 := g.frac_hp() <= 0.4
	var raio := 4.0 if fase2 else 3.5
	match piao["estado"]:
		"":
			if piao["gig_t"] >= piao["proximo"]:
				piao["estado"] = "telegrafo"; piao["t"] = 0.0
				sim.emitir("agrak_piao", {"id": g.id, "raio": raio, "fase": "telegrafo"})
		"telegrafo":
			piao["t"] += dt
			if piao["t"] >= 0.7:
				piao["estado"] = "girando"; piao["t"] = 0.0; piao["tick"] = 0.0
				g.status["atordoado"] = {"t": 10.0}    # a IA não age enquanto gira (pronto() exige sem atordoado)
				sim.emitir("agrak_piao", {"id": g.id, "raio": raio, "fase": "girando"})
		"girando":
			piao["t"] += dt; piao["tick"] += dt
			var alvo := _mais_perto_vivo(g.pos)
			if alvo != null:
				var dir := (alvo.pos - g.pos).normalized()
				var np := g.pos + dir * (1.6 if fase2 else 1.2) * dt
				if sim.andavel(np): g.pos = np
				g.facing = dir
			if piao["tick"] >= 0.25:
				piao["tick"] = 0.0
				for p in sim.jogadores():
					if p.vivo and p.pos.distance_to(g.pos) <= raio:
						var dano: float = p.hp_max * 0.05
						if p.escudo > 0.0:   # o escudo absorve o giro
							var absorvido := minf(p.escudo, dano)
							p.escudo -= absorvido; dano -= absorvido
						if dano > 0.0: sim.aplicar_dano_puro(p, dano, "fisico", g, "piao")
			if piao["t"] >= 10.0:
				g.status.erase("atordoado")
				g.status["agrak_tonto"] = {"t": 4.0}   # tonto 4 s: +50% de dano recebido (regras.gd)
				piao["estado"] = "tonto"; piao["t"] = 0.0
				piao["proximo"] = piao["gig_t"] + (20.0 if fase2 else 30.0)
				sim.emitir("agrak_piao", {"id": g.id, "raio": raio, "fase": "fim"})
		"tonto":
			piao["t"] += dt
			if piao["t"] >= 4.0: piao["estado"] = ""

func _mais_perto_vivo(p: Vector2) -> Ent:
	var melhor: Ent = null
	for j in sim.jogadores():
		if j.vivo and (melhor == null or j.pos.distance_to(p) < melhor.pos.distance_to(p)): melhor = j
	return melhor

## Os chefes da arena são monstros comuns: convertidos do formato de chefes.json para o de mobs.json.
func _registrar_chefes() -> void:
	for k in dados["chefes"]:
		if String(k).begins_with("_"): continue
		var c: Dictionary = dados["chefes"][k].duplicate(true)
		var nv := int(c.get("nivel", 30))
		Defs.MOBS[k] = {
			"nome": c["nome"], "niveis": [nv, nv], "arquetipo": "elite", "tags": c.get("tags", []),
			"res": c.get("res", {}), "alcance": float(c.get("alcance", 1.8)), "ataques": _ataques(c),
			"ia": {"raio_aggro": 30, "raio_coleira": 60, "renascimento_s": 99999},
		}

## Golias traz os golpes dentro das fases; a fase 2 (ruge, Pião mais rápido) ainda não está ligada.
func _ataques(c: Dictionary) -> Array:
	if c.has("ataques"): return c["ataques"]
	return c["fases"][0]["ataques"]

## Cada leão caça um alvo diferente quando dá: a cada 2 s, o alvo que outro leão já persegue perde ameaça.
var t_leoes := 0.0
func _leoes_separados(dt: float) -> void:
	t_leoes += dt
	if t_leoes < 2.0: return
	t_leoes = 0.0
	var leoes: Array = []
	for id in chefes.keys():
		if String(chefes[id]).begins_with("leao_") and sim.ents.has(id) and sim.ents[id].vivo: leoes.append(sim.ents[id])
	var caca := {}
	for l in leoes:
		var alvo := -1
		for k in l.ameaca.keys(): if alvo == -1 or l.ameaca[k] > l.ameaca[alvo]: alvo = k
		if alvo != -1 and caca.has(alvo):
			for j in jogadores_ids:
				if j != alvo and not caca.has(j) and sim.ents.has(j) and sim.ents[j].vivo:
					l.ameaca[alvo] = maxf(0.0, float(l.ameaca[alvo]) - 1.0)
					l.ameaca[j] = maxf(float(l.ameaca.get(j, 0.0)), float(l.ameaca[alvo]) + 0.5)
					alvo = j
					break
		if alvo != -1: caca[alvo] = true

## O bando se vinga (README): quando um leão morre, os outros ganham +15% de dano e +10% de velocidade (acumula).
func _bando() -> void:
	for id in chefes.keys():
		if not String(chefes[id]).begins_with("leao_"): continue
		var l: Ent = sim.ents.get(id)
		if l == null: continue
		l.dano_min *= 1.15; l.dano_max *= 1.15; l.vel *= 1.10
		sim.emitir("agrak_bando", {"id": id})

func _ao_evento(tipo: String, d: Dictionary) -> void:
	if encerrado or tipo != "morreu": return
	var id := int(d.get("id", -1))
	if chefes.has(id):
		var kind: String = chefes[id]
		chefes.erase(id)
		if kind.begins_with("leao_"): _bando()
		ctl.chefe_morreu(kind)
	elif d.get("tipo", "") == "jogador" and jogadores_ids.has(id):
		ctl.jogador_saiu(id)

# ----------------------------------------------------------------- host (o que o controlador pede)

func etapa(id: String, dur: float) -> void:
	sim.emitir("agrak_etapa", {"id": id, "dur": dur})

func prender(ids: Array) -> void:
	var c := _v2(geo.get("centro", [0, 0]))
	var raio := float(dados["evento"]["etapas"][0].get("raio_circulo", 3.5))
	for k in range(ids.size()):
		var e: Ent = sim.ents.get(ids[k])
		if e == null: continue
		var a := TAU * k / float(maxi(1, ids.size()))
		e.caminho.clear(); e.acao = {}; e.alvo = -1
		e.pos = sim.celula_livre_perto(c + Vector2(cos(a), sin(a)) * raio * 0.6)
		e.lado_forcado = "agrak"    # na Chamada e nas lutas 1 e 2 os gladiadores são do mesmo lado
		sim.emitir("teleporte", {"id": e.id, "pos": e.pos})

func fala(quem: String, texto: String) -> void:
	sim.emitir("agrak_fala", {"quem": quem, "texto": texto})

func portao(id: String, aberto: bool) -> void:
	var celulas: Array = geo.get("portoes", {}).get(id, {}).get("celulas", [])
	sim.definir_bloqueio(celulas, 0 if aberto else 2)
	sim.emitir("porta", {"fechada": not aberto, "celulas": celulas})

func spawn_chefe(kind: String, hp: float) -> void:
	var nascem: Dictionary = geo.get("chefes_nascem", {})
	var p: Vector2
	if kind == "golias":
		p = _v2(nascem.get("portao_gigante", [[28, 39]])[0])
	else:
		var lst: Array = nascem.get("portao_leoes", [[7, 23]])
		p = _v2(lst[leoes_nascidos % lst.size()]); leoes_nascidos += 1
	var nv := int(dados["chefes"][kind].get("nivel", 30))
	var m := sim.criar_mob(kind, sim.celula_livre_perto(p), nv)
	m.renasce_s = 0; m.casa = _v2(geo.get("centro", [0, 0])); m.raio_coleira = 60.0
	m.hp_max = hp; m.hp = hp
	chefes[m.id] = kind
	sim.emitir("agrak_chefe", {"id": m.id, "kind": kind, "nome": m.nome, "hp_max": hp})
	# entrada em cena (apresentação): leões correm da jaula até a borda do círculo e rugem; o Golias anda até o meio
	var centro := _v2(geo.get("centro", [28, 23]))
	if kind == "golias":
		var alvo_g := centro + Vector2(0, -7)
		sim.deslocar(m, alvo_g, 3.0, {"anim": "walk"})
		_agendar(3.0, func(): _animar(m.id, "roar", 2.2))
	else:
		# sai pelo portão (12, 23) e depois corre até a borda do círculo, em duas pernas
		var portao_c := Vector2(12.5, 23.0)
		var alvo := centro + (Vector2(-9, 0) if p.x < centro.x else Vector2(9, 0)) + Vector2(0, randf_range(-3.0, 3.0))
		sim.deslocar(m, portao_c, 1.0, {"anim": "run"})
		_agendar(1.25, func(): if m.vivo: sim.deslocar(m, alvo, 1.6, {"anim": "run", "atravessa": true}))
		_agendar(3.0, func(): _animar(m.id, "roar", 2.2))

func _animar(id: int, nome: String, dur: float) -> void:
	sim.emitir("agrak_anim", {"id": id, "anim": nome, "dur": dur})

func _agendar(em_s: float, fn: Callable) -> void:
	_fila.append([em_s, fn])

func _tick_fila(dt: float) -> void:
	for i in range(_fila.size() - 1, -1, -1):
		_fila[i][0] -= dt
		if _fila[i][0] <= 0.0:
			var fn: Callable = _fila[i][1]
			_fila.remove_at(i)
			fn.call()

func recuar_chefes() -> void:
	for id in chefes.keys():
		sim.remover(id)
	chefes.clear()

func recuperar(ids: Array, frac: float) -> void:
	for i in ids:
		var e: Ent = sim.ents.get(i)
		if e == null or not e.vivo: continue
		e.hp = minf(e.hp_max, e.hp + e.hp_max * frac)
		if e.rec_max > 0.0: e.rec = minf(e.rec_max, e.rec + e.rec_max * frac)

func trancar_pocoes(v: bool) -> void:
	for i in jogadores_ids:
		var e: Ent = sim.ents.get(i)
		if e != null: e.aux["sem_pocoes"] = v

func definir_lados(mapa_lados: Dictionary) -> void:
	for i in mapa_lados:
		var e: Ent = sim.ents.get(i)
		if e != null: e.lado_forcado = mapa_lados[i]

func anel(raio: float) -> void:
	raio_anel = raio
	sim.emitir("agrak_anel", {"raio": raio, "centro": geo.get("centro", [0, 0])})

func fora_do_anel(id: int, raio: float) -> bool:
	var e: Ent = sim.ents.get(id)
	return e != null and e.vivo and e.pos.distance_to(_v2(geo.get("centro", [0, 0]))) > raio

func dano_anel(id: int, frac: float) -> void:
	var e: Ent = sim.ents.get(id)
	if e == null or not e.vivo: return
	sim.aplicar_dano_puro(e, e.hp_max * frac, "veneno", null, "anel_amargo")

## Derrotado: fica no camarote como espectador. Sem respawn, sem ação, invisível para os monstros.
func espectador(id: int) -> void:
	var e: Ent = sim.ents.get(id)
	if e == null: return
	e.vivo = true; e.hp = e.hp_max
	e.aux["agrak_espectador"] = true
	e.alvejavel = false
	e.caminho.clear(); e.acao = {}; e.alvo = -1
	e.pos = sim.celula_livre_perto(_v2(geo.get("camarote_derrotados", {}).get("pos", [6.5, 16])))
	sim.emitir("teleporte", {"id": e.id, "pos": e.pos})

func premiar(id: int, qtd: int) -> void:
	var e: Ent = sim.ents.get(id)
	if e == null: return
	Jogador.dar_item(sim, e, Itens.novo("ficha_sangue", qtd))

func hp_frac(id: int) -> float:
	var e: Ent = sim.ents.get(id)
	if e == null or e.hp_max <= 0.0: return 0.0
	return e.hp / e.hp_max

## Evento não começou (menos de 4 inscritos): devolve o ouro de cada inscrito.
func cancelar(ids: Array) -> void:
	for i in ids:
		var e: Ent = sim.ents.get(i)
		if e == null: continue
		e.ouro += int(dados["evento"]["inscricao"]["custo_ouro"])
		sim.emitir_a(e, "ouro", {"valor": int(dados["evento"]["inscricao"]["custo_ouro"])})
		sim.emitir_a(e, "aviso", {"texto": "Agrak cancelado: ouro devolvido."})

func encerrar() -> void:
	encerrado = true
	for id in chefes.keys(): sim.remover(id)
	chefes.clear()
	for i in jogadores_ids:
		var e: Ent = sim.ents.get(i)
		if e != null:
			e.aux.erase("sem_pocoes"); e.lado_forcado = ""; e.aux.erase("agrak_espectador")
	sim.emitir("agrak_fim", {})

func _v2(a) -> Vector2:
	return Vector2(float(a[0]), float(a[1]))

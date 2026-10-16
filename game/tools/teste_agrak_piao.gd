extends SceneTree
## Pião do Golias e bando dos leões (scripts/sim/agrak_mundo.gd), com o mapa oficial.
## Uso: godot --headless --path . --script res://tools/teste_agrak_piao.gd

var falhas := 0

func check(cond: bool, msg: String) -> void:
	if not cond:
		falhas += 1
		print("[teste_agrak_piao] FALHA ", msg)
	else:
		print("[teste_agrak_piao] ok    ", msg)

func correr(sim: WorldSim, segundos: float) -> void:
	for i in int(segundos / 0.1):
		sim.passo(0.1)

func _initialize() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	var ids: Array = []
	var jogs: Array = []
	for k in 4:
		var e := Jogador.criar(sim, "humano", "G%d" % (k + 1))
		jogs.append(e); ids.append(e.id)
	Jogador.entrar(sim, jogs[0], "agrak", Vector2(23, 13.5))
	for k in range(1, 4): sim.adicionar_jogador(jogs[k], Vector2(23 + k, 13.5))
	for e in jogs: e.invuln_t = 1e9
	var ag := AgrakMundo.new(sim, Defs.AGRAK, ids)
	sim.agrak = ag
	ag.iniciar()
	correr(sim, 45.5)
	# bando: matar o Sansão e ver os outros dois ficarem mais fortes
	var sansao := -1; var dalila := -1
	for id in ag.chefes.keys():
		if ag.chefes[id] == "leao_sansao": sansao = id
		if ag.chefes[id] == "leao_dalila": dalila = id
	var dano_antes: float = sim.ents[dalila].dano_min
	sim.matar(sim.ents[sansao], null)
	correr(sim, 0.2)
	check(absf(sim.ents[dalila].dano_min - dano_antes * 1.15) < 0.01, "bando: leão vivo ganha +15% de dano quando um morre")
	for id in ag.chefes.keys().duplicate(): sim.matar(sim.ents[id], null)
	correr(sim, 20.5)
	check(ag.ctl.etapa_atual() == "luta_gigante", "Golias entra")
	var g: Ent = null
	for id in ag.chefes.keys(): g = sim.ents[id]
	check(ag.piao["estado"] == "", "Pião ainda não começou")
	correr(sim, 15.2)
	check(ag.piao["estado"] == "telegrafo" or ag.piao["estado"] == "girando", "Pião começa aos 15 s")
	correr(sim, 1.0)
	check(ag.piao["estado"] == "girando" and g.tem("atordoado"), "gira com o Golias travado")
	correr(sim, 10.0)
	check(ag.piao["estado"] == "tonto" or ag.piao["estado"] == "", "Pião termina depois de 10 s")
	check(float(ag.piao["proximo"]) >= 30.0 + 15.0 - 0.5 or ag.piao["proximo"] > 0.0, "próximo Pião marcado")
	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

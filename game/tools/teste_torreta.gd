extends SceneTree
## Torreta do Tecnomancer: até 2 ao mesmo tempo, 40 s cada, recarga 10 s.
## godot --headless --path . --script res://tools/teste_torreta.gd
func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(3)
	var j := Jogador.criar(sim, "tecnomancer", "Teste")
	Jogador.entrar(sim, j, "area_inicial", Vector2(70, 92))
	j.nivel = 10
	var slot := j.skills_slots.find("torreta_sentinela")
	var h := Jogador.skill_def(j, slot)
	print("torreta: recarga=%s duracao=%s max=%s" % [h.get("recarga"), h.get("duracao"), h.get("max")])
	var conta := func() -> Array:
		return sim.ents.values().filter(func(o): return o.tipo == "invocacao" and o.dono == j.id and o.vivo).map(func(o): return o.id)
	for k in 3:
		j.rec = j.rec_max; j.cds.clear(); j.acao = {}
		Jogador.cmd_skill(sim, j, slot, -1, j.pos + Vector2(1, 0))
		for i in 30: sim.passo(WorldSim.TICK)
		print("depois da %da: torretas %s, recarga restante %.1f" % [k + 1, conta.call(), float(j.cds.get("torreta_sentinela", 0.0))])
	for i in int(41.0 / WorldSim.TICK): sim.passo(WorldSim.TICK)
	print("41 s depois: torretas ", conta.call())
	quit()

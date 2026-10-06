extends SceneTree
## Teste headless: confere os eventos especiais dos mobs (alfa, uivo, investida, enterrar do Filho de Cardo).

var registro: Array = []

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(5)
	var j := Jogador.criar(sim, "demonio", "Teste")
	Jogador.entrar(sim, j, "area_inicial", Vector2(66, 104))
	j.hp_max = 999999.0; j.hp = j.hp_max
	var alfas := 0
	for e: Ent in sim.ents.values():
		if e.aux.get("alfa", false): alfas += 1
	print("alfas: ", alfas)
	var cont := {}
	sim.evento.connect(func(t, d): cont[t] = cont.get(t, 0) + 1)
	sim.evento.connect(func(t, d):
		if t == "ataque" and d.get("nome", "") in ["enterrar", "brotar", "investida", "bote"]: registro.append("%s %s" % [t, d["nome"]])
		if t in ["anim", "visual"] or (t == "som_evento" and d.get("ev") == "uivo"): registro.append("%s %s" % [t, str(d)]))
	print("criando filho")
	var f := sim.criar_mob("filho_de_cardo", sim.celula_livre_perto(j.pos + Vector2(2, 1)), 5)
	IA.acordar(sim, f, j)
	for i in 30 * 25:
		if i % 15 == 0 and j.acao.is_empty() and f.vivo and not f.invisivel: Jogador.cmd_atacar(sim, j, f.id)
		sim.passo(WorldSim.TICK)
	print("filho vivo=", f.vivo, " hp=", f.hp, " pos=", f.pos, " j=", j.pos, " ", f.estado, " ", cont)
	# porco e cães
	for k in ["porco_pestilento", "cao_de_vala"]:
		var alvo: Ent = null
		for e: Ent in sim.ents.values():
			if e.tipo == "monstro" and e.vivo and e.kind == k: alvo = e
		j.pos = sim.celula_livre_perto(alvo.pos + Vector2(4, 0))
		IA.acordar(sim, alvo, j)
		for i in 30 * 15: sim.passo(WorldSim.TICK)
	for l in registro: print(l)
	quit()

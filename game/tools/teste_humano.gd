extends SceneTree
## Teste headless do Humano (0.9.8.2): alcance x2, leque de 3 balas, segunda arma de fogo (dois leques),
## esquiva para trás. godot --headless --path . --script res://tools/teste_humano.gd

var cont := {}

func _ev(t: String, _d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(11)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "humano", "Teste")
	var mi: Dictionary = Defs.ler("res://data/mapas/area_inicial.json")
	var sp: Array = mi["spawn_por_faccao"].get(j.faccao, mi["spawn"])
	Jogador.entrar(sim, j, "area_inicial", Vector2(sp[0], sp[1]))
	rodar(sim, 1.0)

	var alcance := float(Defs.CLASSES["humano"]["alcance_basico"]["tiro"])
	print("alcance do tiro: %.1f (esperado 14)" % alcance)
	if alcance != 14.0: falhas += 1

	# alvo: um inimigo qualquer da área; o Humano para bem perto dele
	var alvo: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.vivo: alvo = e; break
	if alvo == null:
		print("sem monstro na área"); quit(1); return
	var grupo := func(): j.pos = sim.celula_livre_perto(alvo.pos + Vector2(4.0, 0.0))

	# 1) uma arma de fogo: um básico = um leque de 3 balas
	grupo.call()
	cont.clear()
	j.municao = 20
	Jogador.cmd_atacar(sim, j, alvo.id)
	rodar(sim, 0.6); j.alvo = -1   # só o primeiro golpe: o básico se repete sozinho com o alvo marcado
	var um := int(cont.get("projetil", 0))
	print("um leque (uma arma): %d balas (esperado 3)" % um)
	if um != 3: falhas += 1

	# 2) segunda pistola/escopeta de uma mão na 2ª mão: dois leques em sequência
	var id_arma := ""
	for id in Defs.ITENS:
		if Itens.arma_de_fogo_uma_mao(Itens.novo(id)): id_arma = id; break
	if id_arma == "":
		print("nenhuma arma de fogo de uma mão no catálogo"); falhas += 1
	else:
		var a1 := Itens.novo(id_arma); var a2 := Itens.novo(id_arma)
		Itens.guardar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, a1); Itens.guardar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, a2)
		Jogador.equipar(sim, j, a1["uid"], "arma")
		Jogador.equipar(sim, j, a2["uid"], "segunda_mao")
		print("2ª mão ocupada: %s, dois leques: %s" % [j.equip.has("segunda_mao"), Jogador.segunda_arma_de_fogo(j)])
		if not Jogador.segunda_arma_de_fogo(j): falhas += 1
		grupo.call()
		cont.clear()
		j.municao = 20
		Jogador.cmd_atacar(sim, j, alvo.id)
		rodar(sim, 0.6); j.alvo = -1   # só o primeiro golpe: o básico se repete sozinho com o alvo marcado
		var dois := int(cont.get("projetil", 0))
		print("dois leques (duas armas): %d balas (esperado 6), munição gasta %d (esperado 2)" % [dois, 20 - j.municao])
		if dois != 6: falhas += 1

	# 3) esquiva para trás: o Humano pula para o lado oposto de onde olha, não para o mouse
	j.facing = Vector2(1, 0)
	j.pos = sim.celula_livre_perto(j.pos)
	var antes := j.pos
	Evasao.evadir(sim, j, antes + Vector2(0, 5))
	var para: Vector2 = j.deslocando.get("para", j.pos) if not j.deslocando.is_empty() else j.pos
	print("esquiva: de %s para %s (olhando para +x: deve recuar em x)" % [antes, para])
	if para.x >= antes.x: falhas += 1

	print("FALHAS: %d" % falhas)
	quit(falhas)

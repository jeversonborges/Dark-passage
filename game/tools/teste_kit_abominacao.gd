extends SceneTree
## A Forma Abominável liga, cada skill do kit dispara e fere, e a forma desliga.
var falhas := 0
func falha(t: String) -> void: falhas += 1; printerr("FALHA: ", t)
func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

func _campo_aberto(sim: WorldSim, perto: Vector2) -> Vector2:
	for r in range(4, 80, 2):
		for k in 16:
			var p := perto + Vector2.from_angle(TAU * k / 16.0) * r
			if not sim.andavel(p) or sim.zona_segura(p) or sim.amargo_em(p) >= 4: continue
			var ok := true
			for q in [Vector2(3, 0), Vector2(-3, 0), Vector2(0, 3), Vector2(0, -3), Vector2(2.5, 1)]:
				if not sim.andavel(p + q) or sim.zona_segura(p + q): ok = false
			if ok: return p
	return perto

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(5)
	var j := Jogador.criar(sim, "mutante", "Teste_kit")
	Jogador.entrar(sim, j, "area_inicial", Vector2(44.5, 44))
	while j.nivel < 50: Jogador.ganhar_xp(sim, j, Defs.xp_para_proximo(j.nivel) - j.xp)
	j.evolucao = "abominacao"; Evolucao.montar_slots(j); Regras.recalc_jogador(j)
	j.pos = _campo_aberto(sim, j.pos)
	var slot_forma := j.skills_slots.find("forma_abominacao")
	if slot_forma < 0: falha("forma_abominacao fora da barra"); quit(1); return
	Jogador.cmd_skill(sim, j, slot_forma, -1, j.pos); rodar(sim, 1.2)
	if not j.aux.has("kit"): falha("a forma não ligou")
	print("barra com a forma ligada: ", j.skills_slots)
	var kit: Array = []
	for h in Evolucao._kit(j): kit.append(str(h["id"]))
	if kit.size() != 6: falha("kit com %d skills" % kit.size())
	var slot_teste := 0 if slot_forma != 0 else 1
	for id in kit:
		Evolucao.cmd_hotbar(sim, j, slot_teste, id)   # Livro de Skills: põe a skill do kit na barra
		if j.skills_slots[slot_teste] != id: falha("%s não entrou na barra pelo livro" % id); continue
		for o: Ent in sim.ents.values():
			if o.tipo in ["monstro", "invocacao"] and o.pos.distance_to(j.pos) < 30.0: sim.remover(o.id)
		var m := sim.criar_mob(Defs.MOBS.keys()[0], sim.celula_livre_perto(j.pos + Vector2(1.5, 0.0)), 70)
		m.hp_max = 1e7; m.hp = 1e7; m.dano_min = 0.0; m.dano_max = 0.0
		j.rec = 9999.0; j.cds.clear(); if not j.vivo: Jogador.renascer(sim, j)
		Jogador.cmd_skill(sim, j, slot_teste, m.id, m.pos); rodar(sim, 4.0)
		var feriu := m.hp < 1e7
		print("  %-14s %s" % [id, "feriu" if feriu else "NÃO feriu"])
		if not feriu: falha("%s não feriu" % id)
	slot_forma = j.skills_slots.find("forma_abominacao")
	Jogador.cmd_skill(sim, j, slot_forma, -1, j.pos); rodar(sim, 1.2)
	if j.aux.has("kit"): falha("a forma não desligou")
	print("RESULTADO: ", "OK" if falhas == 0 else "%d falhas" % falhas)
	quit(1 if falhas else 0)

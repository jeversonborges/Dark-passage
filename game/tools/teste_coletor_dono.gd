extends SceneTree
## Pet coletor (0.9.8): o pet pega loot do chão (abate, baú) mas não o que o próprio dono jogou fora,
## desequipou ou deixou cair com a mochila cheia. Roda só no sim, sem janela.

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(1)
	var dono: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	dono.inv.clear()
	dono.pos = Vector2.ZERO
	var pet := Ent.new()
	pet.pos = Vector2.ZERO
	var f := Coletor.filtro_padrao()
	var pot := "pocao_vida_m"

	# jogou fora da mochila: o pet não junta
	sim.soltar_no_chao(Itens.novo(pot), dono.pos, dono.id, dono.pos, true)
	if not Coletor._proximo(sim, dono, pet).is_empty(): print("FALHA: pet pegou item que o dono jogou fora"); falhas += 1
	sim.chao.clear()

	# drop de abate (dono = quem matou): o pet junta
	sim.soltar_no_chao(Itens.novo(pot), dono.pos, dono.id, dono.pos)
	if Coletor._proximo(sim, dono, pet).is_empty(): print("FALHA: pet não pegou drop de abate do dono"); falhas += 1
	sim.chao.clear()

	# drop de outro jogador (ainda na janela de dono): o pet não junta
	sim.soltar_no_chao(Itens.novo(pot), dono.pos, dono.id + 999, dono.pos)
	if not Coletor._proximo(sim, dono, pet).is_empty(): print("FALHA: pet pegou drop de outro jogador"); falhas += 1
	sim.chao.clear()

	# sem dono (chão livre, depois do prazo): o pet junta
	sim.soltar_no_chao(Itens.novo(pot), dono.pos, -1, dono.pos)
	if not Coletor._proximo(sim, dono, pet).is_empty(): print("FALHA: pet pegou drop sem dono antes do prazo"); falhas += 1
	for c: Dictionary in sim.chao.values(): c["t"] = float(Defs.DROPS["regras"]["dono_do_drop_s"]) + 1.0
	if Coletor._proximo(sim, dono, pet).is_empty(): print("FALHA: pet não pegou drop sem dono depois do prazo"); falhas += 1
	sim.chao.clear()

	print("teste_coletor: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

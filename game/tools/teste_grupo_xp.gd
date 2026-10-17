extends SceneTree
## Divisão de XP do grupo: dois personagens do mesmo grupo perto um do outro dividem o abate; o longe não recebe.
## godot --headless --path . --script res://tools/teste_grupo_xp.gd
func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(5)
	var a := Jogador.criar(sim, "anjo", "Ana", {})
	var b := Jogador.criar(sim, "humano", "Bia", {})
	var c := Jogador.criar(sim, "humano", "Caio", {})
	Jogador.entrar(sim, a, "area_inicial", Vector2(44, 44))
	sim.adicionar_jogador(b, a.pos + Vector2(3, 0))
	sim.adicionar_jogador(c, a.pos + Vector2(60, 0))
	a.aux["grupo"] = 1; b.aux["grupo"] = 1
	var m: Ent = sim.criar_mob("cao_de_vala", a.pos + Vector2(1, 1), 3)
	var xp_a0 := a.xp; var xp_b0 := b.xp; var xp_c0 := c.xp
	var sozinho := Jogador.membros_grupo(sim, c)
	Jogador.abateu(sim, a, m)
	print("[xp] membros de Ana: ", Jogador.membros_grupo(sim, a).size(), "  de Caio (sozinho): ", sozinho.size())
	print("[xp] ganhos Ana=%d Bia=%d Caio=%d (Caio está longe, não recebe)" % [a.xp - xp_a0, b.xp - xp_b0, c.xp - xp_c0])
	quit()

extends SceneTree
## Teste headless da poção na arena PvP de evento: a cura de HP cai para a metade no Agrak e volta ao normal fora dela.
## godot --headless --path . -s tools/teste_pocao_arena.gd

func curar_com(sim: WorldSim, p: Ent, id: String, frac_hp: float) -> float:
	p.hp_max = 1000.0      # sem o teto: a cura da poção média (300) não pode ser cortada pela vida máxima
	p.hp = p.hp_max * frac_hp
	p.aux.erase("cd_pocao")
	var it := Itens.novo(id, 1)
	Jogador.dar_item(sim, p, it)
	var uid := -1
	for x in p.inv:
		if x["id"] == id: uid = x["uid"]
	var antes := p.hp
	Jogador.usar_item(sim, p, uid)
	return p.hp - antes

func _init() -> void:
	Defs.carregar()
	var falhas := 0

	var sim_arena := WorldSim.new(7)
	var arena := Jogador.criar(sim_arena, "humano", "Arena")
	Jogador.entrar(sim_arena, arena, "agrak", Vector2(23, 9))
	var sim_fora := WorldSim.new(7)
	var fora := Jogador.criar(sim_fora, "humano", "Fora")
	Jogador.entrar(sim_fora, fora, "area_inicial", sim_fora.celula_livre_perto(Vector2(114, 114)))

	if not sim_arena.zona_pvp_evento(arena.pos): falhas += 1; print("FALHA: o Agrak deveria ser arena PvP de evento")
	if sim_fora.zona_pvp_evento(fora.pos): falhas += 1; print("FALHA: a área inicial não é arena PvP")

	for id in ["pocao_vida_p", "pocao_vida_m"]:
		var normal := curar_com(sim_fora, fora, id, 0.1)
		var na_arena := curar_com(sim_arena, arena, id, 0.1)
		print("%s: fora %.1f, na arena %.1f" % [id, normal, na_arena])
		if normal <= 0.0: falhas += 1; print("FALHA: %s não curou fora da arena" % id)
		if absf(na_arena - normal * 0.5) > 0.01: falhas += 1; print("FALHA: %s na arena deveria curar a metade" % id)

	# só a cura de HP: o recurso (mana) da poção segue igual dentro da arena
	var rec_fora := fora.rec
	var rec_arena := arena.rec
	arena.rec = 0.0; fora.rec = 0.0
	curar_com(sim_arena, arena, "pocao_recurso_p", 1.0)
	curar_com(sim_fora, fora, "pocao_recurso_p", 1.0)
	if absf(arena.rec - fora.rec) > 0.01: falhas += 1; print("FALHA: poção de recurso mudou na arena (%.2f x %.2f)" % [arena.rec, fora.rec])
	print("recurso restaurado: fora %.2f, arena %.2f (antes %.2f / %.2f)" % [fora.rec, arena.rec, rec_fora, rec_arena])

	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

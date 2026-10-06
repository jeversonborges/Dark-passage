extends SceneTree
func _init() -> void:
	Defs.carregar()
	print("defs ok: mobs=", Defs.MOBS.size(), " skills=", Defs.SKILLS.size(), " itens=", Defs.ITENS.size(), " missoes=", Defs.MISSOES.size())
	var s := WorldSim.new(1)
	print("sim ok ", s)
	for c in [ChefeCtl, Ent, Itens, Regras, Loot, Missoes, Jogador, Habilidades, IA]: print(c)
	quit()

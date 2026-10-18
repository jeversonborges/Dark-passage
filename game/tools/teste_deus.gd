extends SceneTree
## Variantes Deus (18/10): 10 armas lendario:deus, 0,1% de cada rolagem de equipamento trocar por uma delas.
## Rodar: godot --headless -s tools/teste_deus.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var pool: Array = Defs.ITENS_DOC["pools_lendarios"].get("lendario:deus", [])
	if pool.size() != 10: print("FALHA: pool lendario:deus com %d itens" % pool.size()); falhas += 1
	for id in pool:
		var d: Dictionary = Defs.ITENS.get(id, {})
		if d.is_empty() or str(d.get("variante_de", "")) == "" or not d.has("dano"):
			print("FALHA: variante %s sem dados" % id); falhas += 1
	if absf(float(Defs.DROPS["balanco"]["variante_deus"]) - 0.001) > 0.000001: print("FALHA: chance da variante Deus"); falhas += 1
	var sim := WorldSim.new(1)
	var jog: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	var it := Loot.item_da_tag(sim, "lendario:deus", 10, "comum", jog)
	if it.is_empty() or it.get("raridade") != "lendario" or not (it["id"] in pool): print("FALHA: item_da_tag lendario:deus"); falhas += 1
	print("teste_deus: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(1 if falhas > 0 else 0)

extends SceneTree
## Tubal (18/10): material de forja (Casca de Lava etc.) paga o refino no lugar do ouro; sem material, cobra ouro.
## Rodar: godot --headless -s tools/teste_forja_tubal.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(1)
	var e: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	e.equip["cabeca"] = Itens.novo("veu_carpideira")
	e.aux["servico"] = {"tipo": "ferreiro", "kind": "tubal_malho"}
	e.ouro = 0
	e.inv.append(Itens.novo("lagrima_angelica", 2))
	e.inv.append(Itens.novo("casca_de_lava"))
	var r0 := int(e.equip["cabeca"].get("refino", 0))
	Jogador.refinar(sim, e, 0, "cabeca")
	if Itens.contar(e.inv, "casca_de_lava") != 0: print("FALHA: casca não foi usada no refino do Tubal"); falhas += 1
	if e.ouro != 0: print("FALHA: Tubal cobrou ouro mesmo com material"); falhas += 1
	if int(e.equip["cabeca"].get("refino", 0)) != r0 + 1: print("FALHA: refino não subiu com o material"); falhas += 1
	# sem material e sem ouro: recusa
	e.aux["servico"] = {"tipo": "ferreiro", "kind": "tubal_malho"}
	Jogador.refinar(sim, e, 0, "cabeca")
	if int(e.equip["cabeca"].get("refino", 0)) != r0 + 1: print("FALHA: refinou sem material e sem ouro"); falhas += 1
	print("teste_forja_tubal: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(1 if falhas > 0 else 0)

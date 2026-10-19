extends SceneTree
## Equipamento e mochila (0.9.8): ocupação por tipo, organizar (pilhas + grade), vender lixo por raridade
## e pontos com quantidade. Roda só no sim, sem janela.

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(1)
	var e: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	e.inv.clear()
	# ocupação por tipo
	var espada := Itens.novo("espada_vigilia_rachada")
	if Itens.grade(espada) != Vector2i(1, 3) and Itens.grade(espada) != Vector2i(2, 4): print("FALHA: arma sem tamanho"); falhas += 1
	if Itens.grade(Itens.novo("lanca_procissao")) != Vector2i(2, 4): print("FALHA: arma de 2 mãos devia ser 2x4"); falhas += 1
	for id in Defs.ITENS:
		var it := Itens.novo(id)
		var s := Itens.slot_de(it)
		if s == "peito" and Itens.grade(it) != Vector2i(2, 2): print("FALHA: peitoral %s não é 2x2" % id); falhas += 1; break
	# organizar: junta pilhas e não perde nada
	var pot := "pocao_cura" if Defs.ITENS.has("pocao_cura") else ""
	if pot == "":
		for id in Defs.ITENS:
			if Itens.pilha(Itens.novo(id)) > 1: pot = id; break
	if pot != "":
		var a := Itens.novo(pot, 3); var b := Itens.novo(pot, 4)
		a["x"] = 11; a["y"] = 5; b["x"] = 0; b["y"] = 0
		e.inv = [a, b]
		var total := 0
		for it in e.inv: total += int(it["qtd"])
		Jogador.organizar(sim, e)
		var soma := 0
		for it in e.inv: soma += int(it["qtd"])
		if soma != total: print("FALHA: organizar perdeu quantidade (%d -> %d)" % [total, soma]); falhas += 1
		if e.inv.size() != 1 and Itens.pilha(a) >= total: print("FALHA: pilhas não foram juntadas"); falhas += 1
	# organizar sem espaço não mexe em nada
	e.inv.clear()
	for i in Itens.MOCHILA_W * Itens.MOCHILA_H:
		var p := Itens.novo("espada_vigilia_rachada"); p["x"] = i % Itens.MOCHILA_W; p["y"] = i / Itens.MOCHILA_W
		e.inv.append(p)
	var antes := e.inv.size()
	var nova := Itens.organizar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H)
	if antes > 0 and not nova.is_empty() and nova.size() != antes: print("FALHA: organizar mudou a quantidade de peças"); falhas += 1
	# vender lixo: só no vendedor e só nas raridades marcadas
	e.inv.clear(); e.ouro = 0
	var comum := Itens.novo("espada_vigilia_rachada"); comum["raridade"] = "comum"
	var raro := Itens.novo("espada_vigilia_rachada"); raro["raridade"] = "raro"
	e.inv = [comum, raro]
	Jogador.vender_lixo(sim, e, ["comum"])
	if e.inv.size() != 2: print("FALHA: vendeu fora do vendedor"); falhas += 1
	e.aux["servico"] = {"tipo": "loja"}
	Jogador.vender_lixo(sim, e, ["comum"])
	if e.inv.size() != 1 or e.inv[0]["raridade"] != "raro": print("FALHA: vender lixo não tirou só o comum"); falhas += 1
	if e.ouro <= 0: print("FALHA: vender lixo não pagou"); falhas += 1
	# pontos com quantidade
	e.pontos = 5
	var antes_for: float = float(e.stats["FOR"])
	Jogador.cmd_ponto(sim, e, "FOR", 3)
	if e.pontos != 2 or float(e.stats["FOR"]) <= antes_for: print("FALHA: ponto com quantidade"); falhas += 1
	Jogador.cmd_ponto(sim, e, "FOR", 99)
	if e.pontos != 0: print("FALHA: passou dos pontos disponíveis"); falhas += 1
	print("teste_equipamento: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

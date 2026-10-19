extends SceneTree
## Teste headless do pet coletor (0.9.6): compra, filtro, pega só o que passa, até 5 por passo, segue o dono, salva.
## godot --headless --path . -s tools/teste_coletor.gd

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(7)
	var p := Jogador.criar(sim, "humano", "Coleta")
	Jogador.entrar(sim, p, "area_inicial", Vector2(44.5, 44))
	p.ouro = 20000
	var pet_id := -1
	# sem vendedor: a compra não acontece
	Coletor.comprar(sim, p, "cao_de_vala")
	if p.ouro != 20000 or not Coletor.cfg(p)["especie"].is_empty(): falhas += 1; print("FALHA: comprou sem vendedor")
	p.aux["servico"] = {"tipo": "coletor"}
	Coletor.comprar(sim, p, "cao_de_vala")
	if Coletor.cfg(p)["especie"] != "cao_de_vala" or p.ouro != 20000 - 4000: falhas += 1; print("FALHA: compra do pet")
	var pet := Coletor._meu(sim, p)
	if pet == null or pet.alvejavel: falhas += 1; print("FALHA: pet não criado ou alvo do mapa")
	pet_id = pet.id if pet != null else -1
	# filtro padrão: junta tudo
	if not Coletor.deve_pegar({"id": "pocao_vida_m", "raridade": "comum"}, Coletor.filtro(p)): falhas += 1; print("FALHA: padrão deveria pegar poção")
	# desmarca ouro, poções, joia de lágrima anjo, baú dourado, asas, missão; raridade mínima de armadura e de arma
	Coletor.cmd_cfg(sim, p, "ouro", false)
	Coletor.cmd_cfg(sim, p, "pocoes", false)
	Coletor.cmd_cfg(sim, p, "joia", ["lagrima_angelica", false])
	Coletor.cmd_cfg(sim, p, "baus", false)
	Coletor.cmd_cfg(sim, p, "asas", false)
	Coletor.cmd_cfg(sim, p, "missao", false)
	Coletor.cmd_cfg(sim, p, "armadura_min", "raro")
	Coletor.cmd_cfg(sim, p, "arma_min", "laranja")
	Coletor.cmd_cfg(sim, p, "armadura_min", "nao_existe")   # inválido: ignorado
	Coletor.cmd_cfg(sim, p, "joia", ["nao_existe", false])   # inválido: ignorado
	var f := Coletor.filtro(p)
	for c in [
		[{"id": "_ouro", "raridade": "comum"}, false],
		[{"id": "pocao_vida_m", "raridade": "comum"}, false],
		[{"id": "lagrima_angelica", "raridade": "comum"}, false],
		[{"id": "bau_dourado", "raridade": "comum"}, false],
		[{"id": "bobina_cobre", "raridade": "comum"}, false],
		[{"id": "batina_remendada_peito", "raridade": "comum"}, false],
		[{"id": "batina_remendada_peito", "raridade": "raro"}, true],
		[{"id": "batina_remendada_peito", "raridade": "laranja"}, true],
		[{"id": "espada_vigilia_rachada", "raridade": "excelente"}, false],
		[{"id": "espada_vigilia_rachada", "raridade": "laranja"}, true],
		[{"id": "espada_vigilia_rachada", "raridade": "lendario"}, true],
	]:
		if Coletor.deve_pegar(c[0], f) != c[1]: falhas += 1; print("FALHA: filtro %s deveria ser %s" % [c[0], c[1]])
	# saves antigos (filtro por raridade) ganham as chaves novas com o padrão
	p.aux["coletor"] = {"especie": "cao_de_vala", "filtro": {"raridade": {"comum": false}, "pocoes": false}}
	if Coletor.filtro(p)["pocoes"] != false or Coletor.filtro(p)["ouro"] != true or Coletor.filtro(p)["arma_min"] != "comum": falhas += 1; print("FALHA: migração do filtro antigo")
	Coletor.cmd_cfg(sim, p, "ouro", false)
	Coletor.cmd_cfg(sim, p, "pocoes", true)
	Coletor.cmd_cfg(sim, p, "armadura_min", "comum")
	Coletor.cmd_cfg(sim, p, "asas", false)
	Comandos.executar(sim, p, "coletor", ["filtro", "pocoes", true])
	Comandos.executar(sim, p, "coletor", ["filtro", "pocoes", false])
	Comandos.executar(sim, p, "coletor", ["filtro", 42, true])   # chave inválida: ignorada
	if Coletor.filtro(p)["pocoes"] != false: falhas += 1; print("FALHA: comando coletor filtro")
	# até 5 por passo: 8 poções que passam, um passo do pet junta só 5
	Coletor.cmd_cfg(sim, p, "pocoes", true)
	for i in 8: sim.soltar_no_chao(Itens.novo("pocao_recurso_p"), p.pos + Vector2(0.3, 0), p.id, p.pos)
	var antes := Itens.contar(p.inv, "pocao_recurso_p")
	Coletor.passo(sim, Coletor._meu(sim, p), WorldSim.TICK)
	var pegas := Itens.contar(p.inv, "pocao_recurso_p") - antes
	if pegas != Coletor.PEGAR_POR_PASSO: falhas += 1; print("FALHA: pet deveria pegar 5 por passo, pegou %d" % pegas)
	# drops reais perto do dono: ouro (passa) e poção (o filtro recusa)
	Coletor.cmd_cfg(sim, p, "pocoes", false)
	Coletor.cmd_cfg(sim, p, "ouro", true)
	var ouro_antes := p.ouro
	var nao := Itens.novo("pocao_vida_m")
	sim.soltar_no_chao({"uid": -1, "id": "_ouro", "qtd": 50, "raridade": "comum"}, p.pos + Vector2(2, 0), p.id, p.pos)
	sim.soltar_no_chao(nao, p.pos + Vector2(2.5, 0), p.id, p.pos)
	rodar(sim, 12.0)
	var n_nao := Itens.contar(p.inv, "pocao_vida_m")
	if p.ouro <= ouro_antes: falhas += 1; print("FALHA: pet não pegou o ouro que passa")
	if n_nao != 0: falhas += 1; print("FALHA: pet pegou poção que o filtro recusa")
	if pet_id >= 0 and sim.ents.has(pet_id) and sim.ents[pet_id].pos.distance_to(p.pos) > Coletor.SEGUE_MAX: falhas += 1; print("FALHA: pet não segue o dono")
	# invulnerável: golpe e dano por tempo não tocam o pet (hp 1, então qualquer dano mataria)
	var pet_vivo: Ent = sim.ents.get(pet_id)
	if pet_vivo != null:
		sim.aplicar_golpe(p, pet_vivo, {"dano": 999.0})
		sim.aplicar_dano_puro(pet_vivo, 999.0, "fogo", p)
		if not pet_vivo.vivo or pet_vivo.hp != 1.0: falhas += 1; print("FALHA: pet tomou dano")
		if not pet_vivo.aux.get("coletor", false): falhas += 1; print("FALHA: pet sem a flag coletor (sem nome/barra no cliente)")
	# sumiu do chão só o que foi pego
	var sobrou := sim.chao.values().filter(func(c): return c["item"]["id"] == "pocao_vida_m").size()
	if sobrou != 1: falhas += 1; print("FALHA: drop recusado deveria continuar no chão")
	# dispensar tira o pet, o filtro fica
	Coletor.dispensar(sim, p)
	if Coletor._meu(sim, p) != null or Coletor.cfg(p)["filtro"]["asas"] != false: falhas += 1; print("FALHA: dispensar")
	# pet volta ao entrar de novo no mapa, se tinha espécie
	Coletor.comprar(sim, p, "corvo_de_cinza")
	var sim2 := WorldSim.new(8)
	if Coletor._meu(sim2, p) != null: falhas += 1; print("FALHA: pet apareceu em outro mapa sem entrar")
	Coletor.garantir(sim2, p)   # ao entrar no mapa 2, o pet da espécie escolhida nasce lá
	if Coletor._meu(sim2, p) == null: falhas += 1; print("FALHA: pet não nasceu ao entrar no mapa")
	print("TESTE COLETOR: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

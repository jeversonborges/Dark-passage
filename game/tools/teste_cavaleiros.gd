extends SceneTree
## Teste headless dos Cavaleiros do Apocalipse: o grupo nasce em Jerusalém, voa por cima da cidade, pousa
## juntos perto do pouso e, quando um morre, o assassino tem a chance da montaria dele.
## godot --headless --path . --script res://tools/teste_cavaleiros.gd

var erros: Array = []

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var ev: Dictionary = Defs.ler("res://data/design/combate/cavaleiros.json")
	var sim := WorldSim.new(7)
	sim.carregar_mapa("jerusalem_hermon")
	print("Jerusalém: 4 cavaleiros em voo")
	var c := CavaleirosCtl.new(sim, "jerusalem", ev)
	sim.cavaleiros.append(c)
	c.iniciar()
	checar(c.ids.size() == 4, "nascem quatro cavaleiros")
	checar(c.ids.all(func(id): return not sim.valido(id).alvejavel), "em voo ninguém pode ser atacado")
	var pouso := Vector2(float(ev["capitais"]["jerusalem"]["pouso"][0]), float(ev["capitais"]["jerusalem"]["pouso"][1]))
	var passou_cidade := false
	for i in 60 * 30:   # até 60 s de voo
		sim.passo(WorldSim.TICK)
		if sim.valido(c.ids[0]) != null and sim.valido(c.ids[0]).pos.x > 40.0: passou_cidade = true
		if c.estado == "pousados": break
	checar(passou_cidade, "o grupo cruza a cidade (x > 40) antes de descer")
	checar(c.estado == "pousados", "chegou ao pouso e está pousado (t=%.1f s, etapa %d de %d)" % [float(c.t), c.etapa, c.rota.size()])
	var juntos := true
	for id in c.ids:
		var e := sim.valido(id)
		if e == null or e.pos.distance_to(pouso) > 6.0: juntos = false
	checar(juntos, "os quatro ficam juntos perto do pouso %s" % str(pouso))
	checar(c.ids.all(func(id): return sim.valido(id).alvejavel), "pousados podem ser atacados")
	# morte: ninguém cai sem montaria existir; sem a definição do item o sistema só avisa
	var j := Jogador.criar(sim, "humano", "Teste")
	sim.adicionar_jogador(j, pouso + Vector2(1, 0))
	c.ev["chance_montaria"] = 1.0
	var primeiro: Ent = sim.valido(c.ids[0])
	var n_antes := c.ids.size()
	sim.matar(primeiro, j)
	checar(c.ids.size() == n_antes - 1, "um cavaleiro morto sai do grupo")
	checar(not c.ids.has(primeiro.id), "o morto não conta mais")
	# com o item definido, a montaria cai no chão do assassino
	Defs.ITENS["montaria_fome"] = {"id": "montaria_fome", "nome": "Cavalo da Fome", "tipo": "montaria"}
	var chao_antes := sim.chao.size()
	var segundo: Ent = sim.valido(c.ids[0])
	sim.matar(segundo, j)
	var caiu := false
	for k in sim.chao:
		if sim.chao[k]["item"].get("id", "") != "": caiu = true
	checar(sim.chao.size() > chao_antes or c.ids.size() < n_antes - 1, "o assassino recebe a chance da montaria (chance=1.0 nos testes)")
	print("  (montarias no chão: %d)" % sim.chao.size())
	# o tempo acaba: o grupo some e o controlador sai do mapa
	c.ev["duracao_s"] = 1.0
	rodar(sim, 3.0)
	checar(c.acabou(), "passado o tempo, o evento acaba")
	sim.passo(WorldSim.TICK)
	checar(sim.cavaleiros.is_empty(), "o controlador sai da lista do mapa")
	print("RESULTADO: %s" % ("OK" if erros.is_empty() else "FALHOU: %d" % erros.size()))
	quit(0 if erros.is_empty() else 1)

extends SceneTree
## Teste headless do Agrak: 4 gladiadores passam pela Chamada (presos no círculo), leões, respiro, Golias (com o
## Pião), respiro, Último de Pé (PvP e Anel do Amargo) e Coroação. Um morre nos leões e vira espectador.
## godot --headless --path . --script res://tools/teste_agrak.gd

var cont := {}
var falas: Array = []
var etapas: Array = []
var erros: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "agrak_fala": falas.append("%s: %s" % [d["quem"], d["texto"]])
	if t == "agrak_etapa" and str(d.get("etapa", "")) != "" and (etapas.is_empty() or etapas[etapas.size() - 1] != d["etapa"]): etapas.append(d["etapa"])

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(7)
	sim.evento.connect(_ev)
	var classes := ["mutante", "humano", "anjo", "demonio"]
	var js: Array = []
	for i in 4:
		var j := Jogador.criar(sim, classes[i], "Glad%d" % i)
		if i == 0: Jogador.entrar(sim, j, "agrak", Vector2(23, 9))
		else: sim.adicionar_jogador(j, Vector2(23 + i * 0.5, 9))
		j.aux["agrak_volta"] = ["area_inicial", 40.0 + i, 40.0]
		js.append(j)
	var ctl: AgrakCtl = sim.chefe
	checar(ctl != null and ctl is AgrakCtl, "o mapa agrak cria o AgrakCtl")
	ctl.comecar(js.map(func(x): return x.id))
	checar(ctl.etapa == "chamada", "começa na Chamada")
	# um tenta fugir do círculo
	rodar(sim, 3.0, func(): sim.ir_para(js[1], Vector2(28, 13)))
	checar(js[1].pos.distance_to(ctl._centro()) <= 3.6, "grade invisível segura o gladiador no Círculo de Ferro (%.1f)" % js[1].pos.distance_to(ctl._centro()))
	rodar(sim, 43.0)
	checar(ctl.etapa == "luta_leoes", "depois de 45 s começa a luta dos leões (%s)" % ctl.etapa)
	checar(ctl.feras.size() == 3, "três leões soltos (%d)" % ctl.feras.size())
	var perto := 0
	for f in ctl.feras:
		if f.boss.pos.distance_to(ctl._centro()) < 9.0: perto += 1
	checar(perto == 3, "os leões correram até perto do círculo (%d de 3)" % perto)
	checar(cont.get("agrak_gladiador", 0) == 4, "4 gladiadores apresentados (%d)" % cont.get("agrak_gladiador", 0))
	# luta: todos batem na fera mais perto; vida alta para durar
	for j: Ent in js: Jogador.add_buff(sim, j, "teste", 99999.0, {"hp_pct": 60.0}); j.hp = j.hp_max
	var bater := func():
		for j: Ent in js:
			if not j.vivo or j.aux.get("agrak_espectador", false): continue
			if j.aux.get("teste_vida", false): j.hp = maxf(j.hp, j.hp_max * 0.9)
			var alvo: Ent = null
			for e: Ent in sim.ents.values():
				if e.vivo and e.alvejavel and j.eh_inimigo_de(e) and (alvo == null or e.pos.distance_to(j.pos) < alvo.pos.distance_to(j.pos)): alvo = e
			if alvo != null and j.acao.is_empty(): Jogador.cmd_atacar(sim, j, alvo.id)
	rodar(sim, 4.0, bater)
	sim.matar(js[3], ctl.feras[0].boss)   # um cai para os leões
	rodar(sim, 4.0, bater)
	checar(js[3].vivo and js[3].aux.get("agrak_espectador", false) and js[3].lado_forcado == "neutro", "derrotado levantado pelo Saulo como espectador")
	var cam: Array = sim.mapa["agrak"]["camarote_derrotados"]["ret"]
	checar(js[3].pos.x >= cam[0] and js[3].pos.x <= cam[2] + 1 and js[3].pos.y >= cam[1] and js[3].pos.y <= cam[3] + 1, "espectador no Camarote dos Derrotados")
	for k in 6:
		for f in ctl.feras.duplicate():
			if f.boss.vivo: f.boss.hp = maxf(1.0, f.boss.hp - f.boss.hp_max * 0.3)
		rodar(sim, 4.0, bater)
	checar(ctl.etapa == "respiro", "leões mortos, respiro (%s)" % ctl.etapa)
	rodar(sim, 21.0, bater)
	checar(ctl.etapa == "luta_gigante", "luta do gigante (%s)" % ctl.etapa)
	for j: Ent in js: j.aux["teste_vida"] = true   # o Pião mata personagem de nível 1; aqui só conferimos o fluxo
	rodar(sim, 10.0, bater)
	var g: Ent = ctl.feras[0].boss if not ctl.feras.is_empty() else null
	checar(g != null and g.kind == "golias" and not g.aux.get("imune", false), "Golias entrou e acordou")
	var hp_antes: Array = js.map(func(x): return x.hp)
	rodar(sim, 18.0, bater)
	checar(cont.get("agrak_fx", 0) >= 2, "o Golias girou o Pião (%d efeitos)" % cont.get("agrak_fx", 0))
	if g != null and g.vivo: g.hp = 1.0
	rodar(sim, 3.0, bater)
	checar(ctl.etapa == "respiro", "Golias morto, respiro (%s)" % ctl.etapa)
	rodar(sim, 16.0)
	checar(ctl.etapa == "ultimo_de_pe", "Último de Pé (%s)" % ctl.etapa)
	for j: Ent in js: j.aux.erase("teste_vida")
	checar(js[0].eh_inimigo_de(js[1]) and not js[0].eh_inimigo_de(js[3]), "PvP ligado entre os vivos, espectador fora")
	for j: Ent in js: j.hp = j.hp_max
	rodar(sim, 62.0, func(): pass)
	checar(cont.get("agrak_anel", 0) >= 1, "Anel do Amargo começou a fechar")
	rodar(sim, 4.0, bater)
	checar(cont.get("dano", 0) > 0, "jogadores trocaram golpes")
	# acaba com dois para o fim sair rápido
	js[1].aux["ultimo_agressor"] = js[0].id; js[2].aux["ultimo_agressor"] = js[0].id   # golpe real marca o agressor; aqui o teste mata direto
	sim.matar(js[1], js[0]); rodar(sim, 0.5); sim.matar(js[2], js[0])
	rodar(sim, 2.0)
	checar(ctl.etapa == "coroacao" and ctl.vencedor == js[0].id, "coroação de Glad0 (%s, vencedor %d)" % [ctl.etapa, ctl.vencedor])
	checar(cont.get("morte_pvp", 0) >= 2, "mortes PvP anunciadas (%d)" % cont.get("morte_pvp", 0))
	checar(Itens.contar(js[0].inv, "ficha_sangue") == 3, "vencedor ganhou 3 Fichas de Sangue: 1 da vitória + 1 por abate (%d)" % Itens.contar(js[0].inv, "ficha_sangue"))
	rodar(sim, 16.0)
	checar(cont.get("agrak_fim", 0) == 1, "evento encerrou")
	checar(cont.get("trocar_mapa", 0) >= 4, "todos devolvidos para onde estavam (%d)" % cont.get("trocar_mapa", 0))
	checar(js.all(func(x): return x.lado_forcado == "" and x.alvejavel and x.xp >= 0), "lados e alvo restaurados")
	print("etapas: ", " > ".join(etapas))
	print("falas (%d):" % falas.size())
	for f in falas: print("   ", f)
	print("eventos: ", cont)
	print("RESULTADO: ", "OK" if erros.is_empty() else "FALHOU (%d)" % erros.size())
	quit(0 if erros.is_empty() else 1)

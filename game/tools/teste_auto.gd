extends SceneTree
## Teste headless do modo automático novo: skills escolhidas, juntar drops, poções e ajustes no save.
## godot --headless --path . -s tools/teste_auto.gd

var avisos: Array = []

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	for c in ["anjo", "cultista", "mutante", "demonio", "humano", "tecnomancer"]:
		var sim := WorldSim.new(11)
		var usos := {}
		var pegou := {"n": 0}
		avisos = []
		var p := Jogador.criar(sim, c, "Auto")
		Jogador.entrar(sim, p, "area_inicial", Vector2(44.5, 44))
		sim.evento.connect(func(t, d):
			if t == "skill" and int(d.get("id", -1)) == p.id: usos[d["skill"]] = usos.get(d["skill"], 0) + 1
			if t == "chao_sumiu" and d.get("pego", false) and int(d.get("por", -1)) == p.id: pegou["n"] += 1
			if t == "aviso" and avisos.size() < 12: avisos.append(str(d.get("texto", ""))))
		# padrão: só a skill do nível 5 marcada
		var marcadas: Array = Jogador.cfg_auto(p)["skills"]
		if marcadas.size() != 1: falhas += 1; print("FALHA: %s padrão deveria ter 1 skill marcada: %s" % [c, marcadas])
		while p.nivel < 12: Jogador.ganhar_xp(sim, p, Defs.xp_para_proximo(p.nivel) - p.xp)
		p.hp = p.hp_max
		# marca todas as ativas pelo comando (como o clique direito)
		for i in p.skills_slots.size():
			var h := Jogador.skill_def(p, i)
			if not h.get("passiva", false) and not Jogador.skill_no_auto(p, i): Comandos.executar(sim, p, "auto_skill", [i])
		Comandos.executar(sim, p, "auto_cfg", ["raio", 10.0])
		Comandos.executar(sim, p, "auto_cfg", ["raio", "lixo"])      # inválido: ignora
		Comandos.executar(sim, p, "auto_cfg", ["vida", 5.0])         # fora do limite: prende em 0.8
		Comandos.executar(sim, p, "auto_cfg", ["vida", 0.6])
		Comandos.executar(sim, p, "auto_cfg", ["juntar", "tudo"])
		var cfg := Jogador.cfg_auto(p)
		if float(cfg["raio"]) != 10.0 or absf(float(cfg["vida"]) - 0.6) > 0.001: falhas += 1; print("FALHA: cfg ", cfg)
		p.pos = sim.celula_livre_perto(Vector2(84, 115))
		rodar(sim, 0.5)
		var v0 := Itens.contar(p.inv, "pocao_vida_p")
		var o0 := p.ouro
		Comandos.executar(sim, p, "auto", [true])
		rodar(sim, 90.0)
		var ativas := 0
		for h in Defs.CLASSES[c]["habilidades"]:
			if not h.get("passiva", false): ativas += 1
		print("[%s] auto=%s skills usadas %d/%d %s | pegou do chão %d (ouro %d->%d) | poção vida %d->%d | hp %d/%d" % [c, str(p.aux.get("auto", false)),
			usos.size(), ativas, usos, pegou["n"], o0, p.ouro, v0, Itens.contar(p.inv, "pocao_vida_p"), p.hp, p.hp_max])
		print("   avisos: ", avisos)
		if usos.size() < 3: falhas += 1; print("FALHA: %s usou poucas skills" % c)
		# save guarda os ajustes
		var s := Jogador.salvar(p, sim)
		var q := Jogador.criar(sim, c, "Volta", JSON.parse_string(JSON.stringify(s)))
		var cq := Jogador.cfg_auto(q)
		if cq["skills"].size() != cfg["skills"].size() or float(cq["raio"]) != 10.0: falhas += 1; print("FALHA: save não guardou ", cq)
		# tirar do automático
		Comandos.executar(sim, p, "auto_skill", [0])
		if Jogador.skill_no_auto(p, 0): falhas += 1; print("FALHA: auto_skill não tirou")
	# ---------------------------------------------------------------- árvore de talentos
	var st := WorldSim.new(3)
	var a := Jogador.criar(st, "demonio", "Talento")
	Jogador.entrar(st, a, "area_inicial", Vector2(44.5, 44))
	while a.nivel < 12: Jogador.ganhar_xp(st, a, Defs.xp_para_proximo(a.nivel) - a.xp)
	if Jogador.talentos_livres(a) != 2: falhas += 1; print("FALHA: nível 12 deveria ter 2 pontos, tem ", Jogador.talentos_livres(a))
	var base: Dictionary = Jogador.skill_def(a, 0)
	Comandos.executar(st, a, "talento", [base["id"]])
	Comandos.executar(st, a, "talento", [base["id"]])
	Comandos.executar(st, a, "talento", [base["id"]])   # sem ponto: ignora
	Comandos.executar(st, a, "talento", ["banquete"])     # passiva: ignora
	var aj := Jogador.talentos_em(a, base)
	print("talento %s rank %d: mult %.2f -> %.2f, recarga %.2f -> %.2f" % [base["id"], Jogador.talento(a, base["id"]), float(base.get("mult_por_golpe", 1)), float(aj.get("mult_por_golpe", 1)), float(base["recarga"]), float(aj["recarga"])])
	if Jogador.talento(a, base["id"]) != 2 or float(aj.get("mult_por_golpe", 1)) <= float(base.get("mult_por_golpe", 1)): falhas += 1; print("FALHA: talento não aplicou")
	var sv := Jogador.salvar(a, st)
	var b := Jogador.criar(st, "demonio", "Volta", JSON.parse_string(JSON.stringify(sv)))
	if Jogador.talento(b, base["id"]) != 2: falhas += 1; print("FALHA: save não guardou talentos")
	a.ouro = 1000
	Comandos.executar(st, a, "esquecer_talentos", [])
	if Jogador.talentos_livres(a) != 2 or a.ouro != 950: falhas += 1; print("FALHA: esquecer talentos ", a.ouro)
	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

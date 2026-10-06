extends SceneTree
## Teste headless da v0.6: spots e temperamento, NPCs novos, farmar_spot, skill em área do nível 5 e modo automático.
## godot --headless --path . -s tools/teste_v06.gd

var cont := {}
var avisos: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "aviso" and avisos.size() < 30: avisos.append(str(d.get("texto", "")))

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func subir(sim: WorldSim, j: Ent, nivel: int) -> void:
	while j.nivel < nivel: Jogador.ganhar_xp(sim, j, Defs.xp_para_proximo(j.nivel) - j.xp)

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	# ---------------------------------------------------------------- mapa: spots, temperamento, NPCs
	var sim := WorldSim.new(5)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "anjo", "Teste")
	Jogador.entrar(sim, j, "area_inicial", Vector2(44.5, 44))
	var por_spot := {}
	var neutros := 0; var agress := 0; var territ := 0
	var kinds := {}
	for e: Ent in sim.ents.values():
		if e.tipo != "monstro": continue
		kinds[e.kind] = kinds.get(e.kind, 0) + 1
		var s: String = e.aux.get("spot", "")
		if s != "": por_spot[s] = por_spot.get(s, 0) + 1
		if e.aux.get("neutro", false): neutros += 1
		else: agress += 1
		if e.aux.has("territorio"): territ += 1
	print("monstros por spot: ", por_spot)
	print("neutros=%d agressivos=%d territoriais=%d" % [neutros, agress, territ])
	print("tipos: ", kinds)
	var npcs := {}
	for e: Ent in sim.ents.values():
		if e.tipo == "npc": npcs[e.kind] = npcs.get(e.kind, 0) + 1
	print("npcs: ", npcs)
	for k in ["isaura_radialista", "corvina_atravessadora", "tobias_carrinho"]:
		if not npcs.has(k): print("FALHA: falta NPC ", k); falhas += 1
	if npcs.get("tobias_carrinho", 0) != 4: print("FALHA: carrinhos de poção = ", npcs.get("tobias_carrinho", 0)); falhas += 1
	for k in ["nao_julgado_da_tempestade", "carnical_inchado", "desertor_legiao", "sangrador_apostata", "sombra_gravada"]:
		if not kinds.has(k): print("FALHA: falta monstro ", k); falhas += 1
	if por_spot.size() != 8: print("FALHA: spots com monstros = ", por_spot.size()); falhas += 1
	var objs := {}
	for e: Ent in sim.ents.values():
		if e.tipo == "objeto" and e.kind == "interativo": objs[e.aux["obj"]] = objs.get(e.aux["obj"], 0) + 1
	print("objetos: ", objs)
	for k in ["estandartes_caidos", "marco_do_corte", "rastro_arrasto", "pocas_amargas", "escotilha_silo", "antena_radio"]:
		if not objs.has(k): print("FALHA: falta objeto ", k); falhas += 1
	# loja do carrinho
	var est := Jogador.estoque(j, "loja_carrinho")
	print("loja_carrinho: ", est)
	if not "pocao_vida_p" in est: falhas += 1; print("FALHA: carrinho sem poção")
	print("xp nível 1->2: %d, 5->6: %d" % [Defs.xp_para_proximo(1), Defs.xp_para_proximo(5)])
	# ---------------------------------------------------------------- farmar_spot (d01v) e alias
	j.faccao = "vigilia"
	for m in ["v01", "v02", "v03"]: j.missoes[m] = {"estado": "concluida", "prog": []}
	subir(sim, j, 5)
	Missoes.aceitar(sim, j, "d01v")
	var tel: Dictionary = {}
	for s in sim.mapa["spots"]:
		if s["id"] == "telhados_dos_corvos": tel = s
	var alvo: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.aux.get("spot", "") == "telhados_dos_corvos": alvo = e; break
	sim.matar(alvo, j)
	print("d01v prog após 1 abate no spot: ", j.missoes["d01v"]["prog"], "  texto: ", Missoes.texto_objetivo(Defs.MISSOES["d01v"]["objetivos"][0]))
	if int(j.missoes["d01v"]["prog"][0]) != 1: falhas += 1; print("FALHA: farmar_spot não contou")
	print("alias acampamento_desertores -> ", Missoes.spot_real(sim, "acampamento_desertores"), "; marco_do_corte -> ", Missoes.spot_real(sim, "marco_do_corte"))
	# ---------------------------------------------------------------- d06: escotilha do silo chama o Último Operador
	j.missoes["d06"] = {"estado": "ativa", "prog": [0, 0, 0, 0]}
	var esc: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "objeto" and e.aux.get("obj", "") == "escotilha_silo": esc = e
	j.pos = sim.celula_livre_perto(esc.pos + Vector2(1, 0))
	Jogador.cmd_interagir(sim, j, esc.id)
	rodar(sim, 2.0)
	var op: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.kind == "ultimo_operador": op = e
	print("escotilha: prog d06=", j.missoes["d06"]["prog"], " operador=", op.nome if op else "nenhum", " nivel=", op.nivel if op else 0)
	if op == null: falhas += 1; print("FALHA: Último Operador não apareceu")
	else:
		sim.matar(op, j)
		var chave := false
		for c in sim.chao.values(): if c["item"]["id"] == "chave_lancamento": chave = true
		print("chave_lancamento no chão: ", chave)
		if not chave: falhas += 1
	# ---------------------------------------------------------------- skill em área e modo automático, por classe
	for c in ["anjo", "cultista", "mutante", "demonio", "humano", "tecnomancer"]:
		cont.clear(); avisos.clear()
		var s2 := WorldSim.new(11)
		s2.evento.connect(_ev)
		var p := Jogador.criar(s2, c, "Auto")
		Jogador.entrar(s2, p, "area_inicial", Vector2(44.5, 44))
		subir(s2, p, 6)
		p.hp = p.hp_max
		# procissão parada (3-5) e margem das viúvas (5-7)
		p.pos = s2.celula_livre_perto(Vector2(75, 101))
		rodar(s2, 0.5)
		var vida0 := Itens.contar(p.inv, "pocao_vida_p"); var rec0 := Itens.contar(p.inv, "pocao_recurso_p")
		var xp0 := p.xp + Defs.xp_para_proximo(p.nivel)
		Comandos.executar(s2, p, "auto", [true])
		var usos := {"n": 0}
		var sa := Jogador.slot_auto(p)
		var h := Jogador.skill_def(p, sa)
		s2.evento.connect(func(t, d): if t == "skill" and d.get("skill", "") == h.get("id", ""): usos["n"] += 1)
		rodar(s2, 60.0)
		print("[%s] auto=%s slot_auto=%d (%s) usos_area=%d abates=%d nivel=%d hp=%d/%d mortes=%d pocoes vida %d->%d recurso %d->%d" % [c, str(p.aux.get("auto", false)), sa, h.get("id", "?"),
			usos["n"], cont.get("morreu", 0), p.nivel, p.hp, p.hp_max, cont.get("jogador_morreu", 0), vida0, Itens.contar(p.inv, "pocao_vida_p"), rec0, Itens.contar(p.inv, "pocao_recurso_p")])
		if avisos.size() > 0: print("   avisos: ", avisos.slice(0, 8))
		if usos["n"] == 0: falhas += 1; print("FALHA: %s não usou a skill em área" % c)
		# clicar para andar desliga
		Comandos.executar(s2, p, "auto", [true])
		Jogador.cmd_mover(s2, p, p.pos + Vector2(1, 0))
		if p.aux.get("auto", false): falhas += 1; print("FALHA: cmd_mover não desligou o auto")
	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

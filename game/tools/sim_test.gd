extends SceneTree
## Teste headless do servidor: todas as classes lutam no deserto, abrem baú, falam com NPC e enfrentam os 3 chefes.
## godot --headless --path . --script res://tools/sim_test.gd

var cont := {}
var falas: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t in ["chefe", "chefe_fala", "chefe_derrotado", "trocar_mapa", "dialogo", "texto", "nivel"] and falas.size() < 400:
		falas.append("%s %s" % [t, str(d).left(140)])

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	var n := int(seg * 30)
	for i in n:
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func mais_perto(sim: WorldSim, j: Ent, tipo: String) -> Ent:
	var m: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == tipo and e.vivo and e.alvejavel and (m == null or e.pos.distance_to(j.pos) < m.pos.distance_to(j.pos)): m = e
	return m

func lutar(sim: WorldSim, j: Ent, tipo: String) -> void:
	var a := mais_perto(sim, j, tipo)
	if a == null: return
	if j.acao.is_empty():
		var slot := randi_range(0, 4)
		if randf() < 0.3: Jogador.cmd_skill(sim, j, slot, a.id, a.pos)
		else: Jogador.cmd_atacar(sim, j, a.id)
	if j.frac_hp() < 0.4: Jogador.cmd_pocao(sim, j, "vida")

func _init() -> void:
	Defs.carregar()
	var classes := ["humano", "anjo", "demonio", "cultista", "mutante", "tecnomancer"]
	for c in classes:
		cont.clear()
		var sim := WorldSim.new(42)
		sim.evento.connect(_ev)
		var j := Jogador.criar(sim, c, "Teste")
		var sp: Array = Defs.ler("res://data/mapas/area_inicial.json")["spawn_por_faccao"][j.faccao]
		Jogador.entrar(sim, j, "area_inicial", Vector2(sp[0], sp[1]))
		rodar(sim, 1.0)
		j.pos = sim.celula_livre_perto(Vector2(57, 53))
		var t0 := Time.get_ticks_msec()
		rodar(sim, 90.0, func(): lutar(sim, j, "monstro"))
		var ms := Time.get_ticks_msec() - t0
		print("[%s] fac=%s nivel=%d xp=%d hp=%d/%d mortos=%d abates=%s chao=%d ouro=%d  (%d ms p/ 90 s)" % [c, j.faccao, j.nivel, j.xp, j.hp, j.hp_max, cont.get("jogador_morreu", 0), str(cont.get("morreu", 0)), sim.chao.size(), j.ouro, ms])
		print("   eventos: ", cont)
	# baú, NPC, missão, troca de mapa e chefes com um personagem
	cont.clear(); falas.clear()
	var sim := WorldSim.new(7)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "humano", "Teste")
	Jogador.entrar(sim, j, "area_inicial", Vector2(44.5, 44))
	rodar(sim, 0.5)
	var npc: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "npc" and e.kind == "capita_odete": npc = e
	j.pos = npc.pos + Vector2(0.8, 0.3)
	Jogador.cmd_interagir(sim, j, npc.id)
	rodar(sim, 1.0)
	for i in 3:
		Missoes.escolher(sim, j, 0); rodar(sim, 0.2)
	print("missoes do jogador: ", j.missoes.keys())
	var bau: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "objeto" and e.kind == "bau" and not e.aux.get("trancado", false) and not e.aux.has("visivel_se") and not e.aux.get("mimico", false) and e.aux.get("bau") == "caixote_podre": bau = e; break
	j.pos = sim.celula_livre_perto(bau.pos + Vector2(1, 0))
	var antes := sim.chao.size()
	Jogador.cmd_interagir(sim, j, bau.id)
	rodar(sim, 3.0)
	print("baú %s aberto=%s itens no chão %d -> %d" % [bau.nome, bau.aux.get("aberto"), antes, sim.chao.size()])
	for k in sim.chao.keys(): Jogador.cmd_pegar(sim, j, k); rodar(sim, 0.5)
	print("mochila: ", j.inv.map(func(it): return it["id"]))
	for chefe in [["porao_matadouro", Vector2(50, 27.5)], ["ossario_carpideiras", Vector2(46, 45.5)], ["camara_trombeta", Vector2(44, 34.5)]]:
		cont.clear()
		Jogador.entrar(sim, j, chefe[0], chefe[1])
		j.nivel = 12; j.hp_max = 5000; j.hp = 5000; j.stats["FOR"] = 120; j.stats["AGI"] = 60
		Regras.recalc_jogador(j); j.hp_max = 9000; j.hp = 9000
		for m: Ent in sim.ents.values():
			if m.tipo == "monstro" and m.pos.distance_to(chefe[1]) > 14: m.vivo = false
		var t1 := Time.get_ticks_msec()
		rodar(sim, 240.0, func():
			if not j.vivo: return
			j.hp = maxf(j.hp, j.hp_max * 0.5)
			var b: Ent = null
			for e: Ent in sim.ents.values():
				if e.tipo == "chefe" and e.vivo: b = e
			if b != null:
				for e: Ent in sim.ents.values():
					if e.kind in ["pilha_de_mortos"] and e.vivo: b = e if randf() < 0.3 else b
				if j.acao.is_empty(): Jogador.cmd_atacar(sim, j, b.id)
			else: lutar(sim, j, "monstro"))
		var st: String = sim.chefe.estado if sim.chefe else "?"
		print("[%s] chefe=%s fase=%d hp=%s  eventos=%s (%d ms)" % [chefe[0], st, sim.chefe.fase, str(sim.chefe.boss.hp).left(7), str(cont), Time.get_ticks_msec() - t1])
	for f in falas.slice(0, 120): print("  ", f)
	quit()

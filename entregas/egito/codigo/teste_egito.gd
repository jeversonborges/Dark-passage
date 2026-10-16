extends SceneTree
## Teste headless dos 9 chefes do Egito: cada luta roda com jogadores batendo, a vida do chefe é forçada a cair
## em degraus para passar por todas as fases, e no fim o chefe (e os adicionais) morrem.
## godot --headless --path . --script res://tools/teste_egito.gd

var cont := {}
var log: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t in ["chefe", "chefe_fala", "chefe_derrotado", "aviso", "enigma", "portas_marcadas", "agua_arena", "chefe_some", "canal"] and log.size() < 4000:
		log.append("   %s %s" % [t, str(d).left(150)])

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var lutas := [["hawara_1", 1], ["hawara_2", 1], ["hawara_3", 1], ["coracao_1", 5], ["coracao_2", 5], ["coracao_3", 5], ["coracao_4", 5], ["coracao_5", 5], ["coracao_6", 6]]
	var classes := ["mutante", "humano", "anjo", "cultista", "tecnomancer", "demonio"]
	for l in lutas:
		cont.clear(); log.clear()
		var sim := WorldSim.new(11)
		sim.evento.connect(_ev)
		var mp: Dictionary = Defs.ler("res://data/mapas/%s.json" % l[0])
		var c: Vector2 = Vector2(mp["chefe"]["arena"]["centro"][0], mp["chefe"]["arena"]["centro"][1])
		var js: Array = []
		for i in int(l[1]):
			var j := Jogador.criar(sim, classes[i % 6], "T%d" % i)
			if i == 0: Jogador.entrar(sim, j, l[0], c + Vector2(2, 1))
			else: sim.adicionar_jogador(j, c + Vector2(2 + i * 0.5, 1))
			Jogador.add_buff(sim, j, "teste", 99999.0, {"hp_pct": 8000.0})
			j.hp = j.hp_max
			js.append(j)
		var ch: ChefeCtl = sim.chefe
		rodar(sim, 0.5)
		var boss := ch.boss
		print("egito=", ch.egito != null, " ativo=", ch.egito.ativo if ch.egito else false, " mec=", Defs.CHEFES[boss.kind].has("mecanica_egito"))
		var hp0 := boss.hp_max
		var bater := func():
			for j: Ent in js:
				j.hp = maxf(j.hp, j.hp_max * 0.85)
				if not j.vivo: continue
				var alvo: Ent = null
				for e: Ent in sim.ents.values():
					if e.vivo and e.alvejavel and e.tipo in ["chefe", "monstro"] and (alvo == null or e.pos.distance_to(j.pos) < alvo.pos.distance_to(j.pos)): alvo = e
				if alvo != null and j.acao.is_empty(): Jogador.cmd_atacar(sim, j, alvo.id)
		rodar(sim, 5.0, bater)
		var escala := boss.hp_max / maxf(hp0, 1.0)
		# degraus de vida: 92%, 78%, ... até 5%
		for alvo_frac in [0.92, 0.78, 0.62, 0.5, 0.38, 0.26, 0.15, 0.05]:
			if not boss.vivo: break
			if boss.frac_hp() > alvo_frac and not boss.aux.get("imune", false): boss.hp = boss.hp_max * alvo_frac
			rodar(sim, 22.0, bater)
		# mata os adicionais e o chefe
		for e: Ent in sim.ents.values():
			if e.vivo and e.tipo == "monstro" and e.aux.get("adicional_egito", false): sim.matar(e, js[0])
		rodar(sim, 1.0, bater)
		for k in 12:
			if not boss.vivo: break
			boss.aux.erase("imune"); boss.hp = 1.0
			sim.aplicar_dano_puro(boss, 50.0, "fisico", js[0])
			rodar(sim, 1.0, bater)
		var mortos := 0
		for j: Ent in js:
			if not j.vivo: mortos += 1
		print("[%s] chefe=%s vivo=%s fase=%d escala_hp=%.2f estado=%s jogadores_caidos=%d tele=%d areas=%d avisos=%d derrotado=%s" % [l[0], boss.kind, str(boss.vivo), ch.fase, escala, ch.estado,
			cont.get("jogador_morreu", 0), cont.get("telegrafo", 0), cont.get("area", 0), cont.get("aviso", 0), str(cont.get("chefe_derrotado", 0))])
		var vistos := {}
		for s in log:
			var k: String = s.left(70)
			if vistos.has(k): continue
			vistos[k] = true
			print(s)
	quit()

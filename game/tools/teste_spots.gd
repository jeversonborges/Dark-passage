extends SceneTree
## Teste headless (0.9.5): spot de farm renasce com o jogador parado no meio, longe dele, e mais rápido.

func _init() -> void:
	Defs.carregar()
	var R: Dictionary = Defs.MOBS_BASE.get("spots", {})
	var sim := WorldSim.new(7)
	var j := Jogador.criar(sim, "demonio", "Teste")
	Jogador.entrar(sim, j, "area_inicial", Vector2(66, 104))
	j.hp_max = 999999.0; j.hp = j.hp_max
	var colados_ao_nascer := [0]
	sim.evento.connect(func(t, d):
		if t == "surgiu" and sim.ents.has(d["id"]) and sim.ents[d["id"]].pos.distance_to(j.pos) < float(R.get("dist_min_jogador", 3.0)) - 0.75: colados_ao_nascer[0] += 1)
	var falhas := 0
	var testados := 0
	for i in sim.spawns.size():
		var g: Dictionary = sim.spawns[i]
		if str(g["spot"]) == "" or float(g["respawn_s"]) >= 60.0: continue
		if not Defs.MOBS.has(g["mob"]):
			print("aviso %s grupo %d: mob %s não existe em mobs.json (grupo nunca nasce)" % [g["spot"], i, g["mob"]]); continue
		testados += 1
		j.pos = sim.celula_livre_perto(g["pos"])
		var qtd := int(g["qtd"])
		for id in g["ents"].duplicate():
			var e: Ent = sim.ents.get(id)
			if e != null and e.vivo: sim.matar(e, j)
		for t in int((float(R.get("respawn_s", 6)) + 1.0) / WorldSim.TICK): 
			j.pos = sim.celula_livre_perto(g["pos"]); j.hp = j.hp_max
			sim.passo(WorldSim.TICK)
		var vivos := 0
		var antes: int = colados_ao_nascer[0]
		for id in g["ents"]:
			var e: Ent = sim.ents.get(id)
			if e != null and e.vivo:
				vivos += 1
		var perto: int = colados_ao_nascer[0] - antes
		var ok := vivos == qtd and perto == 0
		if not ok: falhas += 1
		print("%s %s grupo %d: qtd=%d renasce=%.0fs vivos=%d colados=%d %s" % ["ok" if ok else "FALHA", g["spot"], i, qtd, g["respawn_s"], vivos, perto, g["mob"]])
	print("spots testados=%d falhas=%d" % [testados, falhas])
	quit(1 if falhas > 0 or testados == 0 else 0)

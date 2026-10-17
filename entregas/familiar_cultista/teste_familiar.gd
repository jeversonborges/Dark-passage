extends SceneTree
## Teste headless do familiar 0.9.3: invulnerável, bate em área, forma por nível.

func _init() -> void:
	Defs.carregar()
	for nivel in [1, 6, 16, 60]:
		var sim := WorldSim.new(7)
		var j := Jogador.criar(sim, "cultista", "Teste")
		j.nivel = nivel
		Jogador.entrar(sim, j, "area_inicial", Vector2(66, 104))
		j.hp_max = 9999999.0; j.hp = j.hp_max
		var fam: Ent = sim.ents.get(int(j.aux.get("familiar_id", -1)))
		var mobs := []
		for k in 3:
			var m := sim.criar_mob("cao_de_vala", sim.celula_livre_perto(j.pos + Vector2(2.5 + k * 0.4, 0.6 * k)), 5)
			m.hp_max = 99999.0; m.hp = m.hp_max
			mobs.append(m); IA.acordar(sim, m, j)
		var atingidos := {}
		var dano_fam := 0
		var mortes_fam := 0
		sim.evento.connect(func(t, d):
			if t == "dano" and int(d.get("de", -1)) == fam.id and int(d.get("valor", 0)) > 0: atingidos[int(d["id"])] = true
			if t == "dano" and int(d.get("id", -1)) == fam.id and int(d.get("valor", 0)) > 0 and d.get("estilo", "") != "escudo": dano_fam += 1
			if t == "morreu" and int(d["id"]) == fam.id: mortes_fam += 1)
		# um monstro bate no familiar à força (área sem alvo e dano puro)
		for i in 30 * 20:
			# os mobs batem no dono (a IA de hoje deixa o cão voltar a ocioso na área inicial; o golpe direto garante o agressor)
			if i % 30 == 0:
				for m in mobs: sim.aplicar_golpe(m, j, {"mult": 1.0, "nunca_erra": true})
			if i == 60: sim.aplicar_dano_puro(fam, 999999.0, "fogo", mobs[0])
			if i == 90: sim.aplicar_golpe(mobs[0], fam, {"mult": 50.0, "nunca_erra": true})
			sim.passo(WorldSim.TICK)
		print("nivel=%d forma=%s vivo=%s hp=%d/%d alvejavel=%s atingidos=%d dano_no_familiar=%d mortes=%d" % [nivel, fam.kind, fam.vivo, fam.hp, fam.hp_max, fam.alvejavel, atingidos.size(), dano_fam, mortes_fam])
	quit()

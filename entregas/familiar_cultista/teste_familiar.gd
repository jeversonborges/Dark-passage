extends SceneTree
## Teste headless do familiar 0.9.3: forma por nível, ataque em área, 3x vida/defesa (apanha e morre),
## volta sozinho em 30 s com o evento "reviveu", cura 10% do dano do dono e modos da barra do pet.

func _init() -> void:
	Defs.carregar()
	for nivel in [1, 6, 16, 30, 60]:
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
			mobs.append(m)
		var atingidos := {}
		var r := {"apanhou": 0, "morreu": 0, "reviveu": 0, "curou": false}
		sim.evento.connect(func(t, d):
			if t == "dano" and int(d.get("de", -1)) == fam.id and int(d.get("valor", 0)) > 0: atingidos[int(d["id"])] = true
			if t == "dano" and int(d.get("id", -1)) == fam.id and int(d.get("valor", 0)) > 0: r["apanhou"] += 1
			if t == "morreu" and int(d["id"]) == fam.id: r["morreu"] += 1
			if t == "reviveu" and int(d["id"]) == fam.id: r["reviveu"] += 1)
		# 1) proteger: os mobs batem no dono e o familiar bate em área
		for i in 30 * 12:
			if i % 30 == 0:
				for m in mobs: sim.aplicar_golpe(m, j, {"mult": 1.0, "nunca_erra": true})
			sim.passo(WorldSim.TICK)
		var area := atingidos.size()
		# 2) cura: o familiar ferido recupera 10% do dano do dono
		fam.hp = fam.hp_max * 0.5
		var antes := fam.hp
		sim.aplicar_golpe(j, mobs[0], {"mult": 1.0, "nunca_erra": true})
		r["curou"] = fam.hp > antes
		# 3) passivo: não ataca
		Comandos.executar(sim, j, "pet", ["passivo"])
		for i in 30: sim.passo(WorldSim.TICK)   # deixa cair o cuspe que já estava no ar
		atingidos.clear()
		for i in 30 * 4:
			if i % 30 == 0: sim.aplicar_golpe(mobs[0], j, {"mult": 1.0, "nunca_erra": true})
			sim.passo(WorldSim.TICK)
		var passivo_ok := atingidos.is_empty()
		Comandos.executar(sim, j, "pet", ["proteger"])
		# 4) apanha, morre e volta sozinho em 30 s
		sim.aplicar_golpe(mobs[0], fam, {"mult": 1.0, "nunca_erra": true})
		sim.matar(fam, mobs[0])
		for i in 30 * 31: sim.passo(WorldSim.TICK)
		print("nivel=%d forma=%s hp=%d/%d atingidos=%d apanhou=%s curou=%s passivo_ok=%s morreu=%d reviveu=%d vivo=%s" % [
			nivel, fam.kind, fam.hp, fam.hp_max, area, r["apanhou"] > 0, r["curou"], passivo_ok, r["morreu"], r["reviveu"], fam.vivo])
	quit()

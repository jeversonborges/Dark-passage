extends SceneTree
## Teste headless do familiar 0.9.3: forma por nível, ataque em área, 3x vida/defesa (apanha e morre),
## volta sozinho em 30 s com o evento "reviveu", cura 10% do dano do dono e modos da barra do pet.

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
	# 5) servidor: troca de mapa / relogar. Cada mapa é um WorldSim com ids próprios; o familiar_id guardado no
	#    dono pode cair num monstro do mapa novo. O familiar tem que nascer mesmo assim.
	var a := WorldSim.new(3)
	var jc := Jogador.criar(a, "cultista", "Teste2")
	jc.nivel = 20
	Jogador.entrar(a, jc, "area_inicial", Vector2(66, 104))
	var fid := int(jc.aux.get("familiar_id", -1))
	a.remover_jogador(jc)
	var b := WorldSim.new(4)
	b.carregar_mapa("area_inicial")
	var intruso := b.criar_mob("cao_de_vala", b.celula_livre_perto(Vector2(80, 100)), 5)
	b.ents.erase(intruso.id); intruso.id = fid; b.ents[fid] = intruso   # monstro com o mesmo id do familiar antigo
	b.adicionar_jogador(jc, Vector2(66, 104))
	var novo: Ent = b.ents.get(int(jc.aux.get("familiar_id", -1)))
	print("troca_de_mapa: familiar=%s forma=%s monstro_intacto=%s" % [novo != null and novo.aux.get("familiar", false), novo.kind if novo else "-", intruso.tipo == "monstro" and intruso.dono != jc.id])
	quit()

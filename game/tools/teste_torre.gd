extends SceneTree
## Teste headless da raid A Torre: em cada andar, horda + chefe com um personagem forte; conta as animações dos golpes,
## a troca de folha do Baraquiel na fase 3, o drop do chefe e a flag que abre o elevador.
## godot --headless --path . --script res://tools/teste_torre.gd

var cont := {}
var anims := {}
var visuais: Array = []
var derrotado := ""
var fase_max := 1
var sim_ref: WorldSim = null

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "ataque" and str(d.get("anim", "")) != "" and sim_ref != null and sim_ref.ents.has(int(d["id"])) and sim_ref.ents[int(d["id"])].tipo == "chefe": anims[d["anim"]] = anims.get(d["anim"], 0) + 1
	if t == "visual": visuais.append(d["kind"])
	if t == "chefe_derrotado": derrotado = str(d)
	if t == "chefe" and d.has("fase"): fase_max = maxi(fase_max, int(d["fase"]))

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	for n in range(1, 6):
		var id := "torre_%d" % n
		cont.clear(); anims.clear(); visuais.clear(); derrotado = ""; fase_max = 1
		var sim := WorldSim.new(100 + n)
		sim.evento.connect(_ev); sim_ref = sim
		var j := Jogador.criar(sim, "demonio", "Teste")
		Jogador.entrar(sim, j, id, Vector2(11.5, 25.5))
		var mapa: Dictionary = Defs.ler("res://data/mapas/%s.json" % id)
		var kinds := {}
		for e: Ent in sim.ents.values():
			if e.tipo == "monstro": kinds[e.kind] = kinds.get(e.kind, 0) + 1
		var chefe_id: String = mapa["chefe"]["id"]
		j.nivel = 30; j.stats["FOR"] = 160; j.stats["AGI"] = 90; j.stats["VIT"] = 120
		Regras.recalc_jogador(j); j.hp_max = 40000; j.hp = 40000
		for m: Ent in sim.ents.values():
			if m.tipo == "monstro": m.vivo = false
		j.pos = sim.celula_livre_perto(Vector2(42.5, 25.5))
		var chao0 := sim.chao.size()
		var t1 := Time.get_ticks_msec()
		for i in int(900.0 * 30):
			if i % 6 == 0 and j.vivo:
				j.hp = maxf(j.hp, j.hp_max * 0.6)
				var alvo: Ent = null
				for e: Ent in sim.ents.values():
					var tipos := ["monstro"] if sim.chefe.estado != "luta" else ["monstro", "chefe"]   # na horda, só os mobs
					if e.vivo and e.alvejavel and e.tipo in tipos and (alvo == null or e.pos.distance_to(j.pos) < alvo.pos.distance_to(j.pos)): alvo = e
				for e: Ent in sim.ents.values():   # o Locutor cura a horda: morre primeiro, como pede o design
					if e.vivo and e.kind == "sintonizado_locutor": alvo = e; break
				if alvo != null and j.acao.is_empty(): Jogador.cmd_atacar(sim, j, alvo.id)
			sim.passo(WorldSim.TICK)
			if derrotado != "": break
		var flag := j.flags.has("venceu_" + chefe_id)
		var ok := derrotado != "" and flag and fase_max == (Defs.CHEFES[chefe_id]["fases"] as Array).size() and not anims.is_empty() and (chefe_id != "baraquiel" or visuais.has("baraquiel_sinal_pleno"))
		if not ok: falhas += 1
		print("[%s] %s chefe=%s estado=%s fase=%d/%d derrotado=%s flag=%s drops=%d  mobs_no_mapa=%s" % [id, "OK" if ok else "FALHOU", chefe_id, sim.chefe.estado, fase_max, (Defs.CHEFES[chefe_id]["fases"] as Array).size(), derrotado != "", flag, sim.chao.size() - chao0, str(kinds)])
		if sim.chefe.estado == "horda":
			for hid in sim.chefe.horda_ids:
				var hm: Ent = sim.ents.get(hid)
				if hm: print("    horda viva: %s pos=%s hp=%d alvejavel=%s estado=%s" % [hm.kind, str(hm.pos), hm.hp, hm.alvejavel, hm.estado])
			print("    jogador vivo=%s pos=%s acao=%s status=%s eventos=%s" % [j.vivo, str(j.pos), str(j.acao.keys()), str(j.status.keys()), str(cont)])
		print("    anims dos golpes=%s visuais=%s ondas=%d (%d ms)" % [str(anims), str(visuais), sim.chefe.horda_onda, Time.get_ticks_msec() - t1])
	print("teste_torre: ", "tudo certo" if falhas == 0 else "%d andar(es) com falha" % falhas)
	quit(1 if falhas > 0 else 0)

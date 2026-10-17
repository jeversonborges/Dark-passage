extends SceneTree
## Teste headless de Jerusalém e Monte Hermon (Arautos, 0.9.3): casa por facção, portais, lojas, chave de Pã
## e os 3 chefes do Fosso dos Vigilantes com o roteiro dos chefes da Cripta.
## godot --headless --path . --script res://tools/teste_jerusalem.gd

var falhas := 0
var oks := 0
var evs: Array = []

func ok(cond: bool, txt: String) -> void:
	if cond: oks += 1; print("  ok   ", txt)
	else: falhas += 1; print("  FALHA ", txt)

func _ev(t: String, d: Dictionary) -> void:
	evs.append([t, d])

func conta(t: String, f: Callable = Callable()) -> int:
	var n := 0
	for x in evs:
		if x[0] == t and (not f.is_valid() or f.call(x[1])): n += 1
	return n

func ultimo(t: String) -> Dictionary:
	for i in range(evs.size() - 1, -1, -1):
		if evs[i][0] == t: return evs[i][1]
	return {}

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	teste_dados()
	teste_casa()
	teste_portais()
	teste_lojas_e_chave()
	for c in [["minas_dos_gigantes", "ohya_gigante", "general_partido", "soldado_de_pedra"],
			["salao_das_noivas", "naama_noiva", "irma_celeste", "noiva_afogada"],
			["altar_do_juramento", "semyaza_juramento", "zacarias_arauto", "eco_do_juramento"]]:
		teste_chefe(c[0], c[1], c[2], c[3])
	print("\nteste_jerusalem: %d ok, %d falhas" % [oks, falhas])
	quit(1 if falhas > 0 else 0)

func teste_dados() -> void:
	print("[dados]")
	for m in ["jerusalem_hermon", "minas_dos_gigantes", "salao_das_noivas", "altar_do_juramento", "cume_dos_vigilantes"]:
		ok(FileAccess.file_exists("res://data/mapas/%s.json" % m), "mapa %s" % m)
	for k in ["peregrino_ressecado", "kokabiel_contador", "vigilante_desfeito"]:
		ok(Defs.MOBS.has(k) and Defs.MOBS[k].has("hp_base") or Defs.MOBS[k].size() > 5, "mob %s com números do espelho" % k)
	for k in ["drop_ohya", "drop_naama", "drop_semyaza"]:
		ok(Defs.DROPS["tabelas"].has(k), "tabela de drop %s" % k)
	ok(Defs.mecanica_chefe("ohya_gigante") == "general_partido" and Defs.mecanica_chefe("general_partido") == "general_partido", "mecanica_de")
	ok(Defs.ITENS.has("martelo_de_tubal") and Defs.ITENS.has("malho_de_tubal"), "martelo_de_tubal (Jerusalém) e malho_de_tubal (Hermon) separados")
	var g02: Dictionary = Missoes.def("g02")
	ok(g02.get("requer_qualquer", []) == ["g01", "jg01"], "g02 abre com g01 ou jg01")

func teste_casa() -> void:
	print("[casa por facção]")
	ok(Defs.mapa_casa_classe("anjo") == "jerusalem_hermon" and Defs.mapa_casa_classe("cultista") == "jerusalem_hermon", "Arautos nascem em Jerusalém")
	ok(Defs.mapa_casa_classe("humano") == "area_inicial" and Defs.mapa_casa_classe("tecnomancer") == "area_inicial", "Vigília nasce no deserto")
	var sim := WorldSim.new(3); sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "demonio", "Teste")
	var sp: Array = Defs.ler("res://data/mapas/jerusalem_hermon.json")["spawn_por_faccao"]["arautos"]
	Jogador.entrar(sim, j, "jerusalem_hermon", Vector2(sp[0], sp[1]))
	rodar(sim, 0.5)
	ok(j.pos.distance_to(Vector2(sp[0], sp[1])) < 2.0, "nasce na Brasa do Altar")
	var cheg := 0
	for s in sim.spawns:
		if not sim.caminho(j.pos, s["pos"]).is_empty(): cheg += 1
	ok(cheg == sim.spawns.size(), "a pé, da cidade até todos os grupos de mobs (%d de %d)" % [cheg, sim.spawns.size()])
	var sv := Jogador.salvar(j, sim)
	ok(sv["mapa"] == "jerusalem_hermon" and sv["pos"].size() == 2, "save guarda Jerusalém e a posição")
	Jogador.entrar(sim, j, "minas_dos_gigantes", Vector2(12.5, 50.5))
	sv = Jogador.salvar(j, sim)
	ok(sv["mapa"] == "jerusalem_hermon" and sv["pos"].is_empty(), "save dentro do Fosso volta para Jerusalém")
	evs.clear()
	Jogador.voltar_acampamento(sim, j); rodar(sim, 3.5)
	ok(ultimo("trocar_mapa").get("mapa", "") == "jerusalem_hermon", "teleporte para a base leva o Arauto a Jerusalém")
	var h := Jogador.criar(sim, "humano", "Teste2")
	ok(Jogador.salvar(h, sim)["mapa"] == "area_inicial", "Vigília fora de casa salva no deserto")

func _portal(sim: WorldSim, para: String) -> Ent:
	for e: Ent in sim.ents.values():
		if e.tipo == "objeto" and e.kind == "portal" and e.aux.get("para", "") == para: return e
	return null

func teste_portais() -> void:
	print("[portais]")
	var sim := WorldSim.new(4); sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "anjo", "Teste")
	Jogador.entrar(sim, j, "jerusalem_hermon", Vector2(101.5, 42.5))
	var p := _portal(sim, "area_inicial")
	ok(p != null, "Estrada do Sul em Jerusalém")
	ok(not sim.caminho(j.pos, p.pos).is_empty() or j.pos.distance_to(p.pos) < 2, "dá para andar até a Estrada do Sul")
	evs.clear()
	j.pos = sim.celula_livre_perto(p.pos)
	Jogador.interagir(sim, j, p); rodar(sim, 1.0)
	ok(conta("trocar_mapa") == 0 and conta("aviso") > 0, "nível 1 não desce para o deserto")
	j.nivel = 12; evs.clear()
	Jogador.interagir(sim, j, p); rodar(sim, 1.0)
	var t := ultimo("trocar_mapa")
	ok(t.get("mapa", "") == "area_inicial", "nível 12 desce para o deserto")
	Jogador.entrar(sim, j, "area_inicial", t["pos"])
	ok(j.pos.distance_to(t["pos"]) < 2.5, "chega andável no deserto (%s)" % str(j.pos))
	var v := _portal(sim, "jerusalem_hermon")
	ok(v != null and j.pos.distance_to(v.pos) < 4.0, "Estrada dos Peregrinos ao lado da chegada")
	ok(not sim.caminho(j.pos, Vector2(70, 94)).is_empty(), "da Estrada dos Peregrinos até o centro de São Lázaro a pé")
	evs.clear(); j.pos = sim.celula_livre_perto(v.pos)
	Jogador.interagir(sim, j, v); rodar(sim, 1.0)
	ok(ultimo("trocar_mapa").get("mapa", "") == "jerusalem_hermon", "volta para Jerusalém")
	var tp: Array = Defs.ler("res://data/teleporte.json")["destinos"].filter(func(d): return d["mapa"] == "jerusalem_hermon")
	ok(tp.size() >= 8, "menu de teleporte com %d destinos em Jerusalém" % tp.size())

func teste_lojas_e_chave() -> void:
	print("[lojas e chave de Pã]")
	var sim := WorldSim.new(5)
	var j := Jogador.criar(sim, "cultista", "Teste")
	Jogador.entrar(sim, j, "jerusalem_hermon", Vector2(101.5, 42.5))
	for l in ["loja_hulda", "loja_zilpa", "loja_bartimeu", "loja_carrinho_bartimeu", "loja_zaqueu_cobrador"]:
		ok(Defs.LOJAS.has(l) and Jogador.estoque(j, l).has("pocao_vida_p"), "%s vende poção" % l)
	ok(Jogador.estoque(j, "loja_bartimeu").size() > Defs.LOJAS["loja_bartimeu"]["itens"].size() + 3, "Bartimeu vende munição e armas da faixa 1")
	var cap: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.kind == "capataz_de_tofete": cap = e
	ok(cap != null, "Capataz de Tofete no mapa")
	if cap == null: return
	var achou := false
	for i in 6:
		Loot.dropar_mob(sim, cap, j)
		for k in sim.chao.keys():
			if sim.chao[k]["item"]["id"] == "chave_de_pa": achou = true
		if achou: break
	ok(achou, "Chave de Pã cai do Capataz")

func teste_chefe(mapa: String, id: String, mec: String, invocado: String) -> void:
	print("[%s]" % mapa)
	evs.clear()
	var sim := WorldSim.new(11); sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "demonio", "Teste")
	var c: Dictionary = Defs.ler("res://data/mapas/%s.json" % mapa)["chefe"]
	Jogador.entrar(sim, j, mapa, Vector2(c["arena"]["centro"][0], c["arena"]["centro"][1]))
	ok(sim.chefe != null and sim.chefe.boss.kind == id and sim.chefe.mec == mec, "%s usa o roteiro de %s" % [id, mec])
	j.nivel = 12; j.stats["FOR"] = 120; j.stats["AGI"] = 60
	Regras.recalc_jogador(j); j.hp_max = 9000; j.hp = 9000
	for m: Ent in sim.ents.values():
		if m.tipo == "monstro": m.vivo = false
	var t0 := Time.get_ticks_msec()
	var vistos := {}
	rodar(sim, 240.0, func():
		for e: Ent in sim.ents.values():
			if e.tipo == "monstro" and e.vivo: vistos[e.kind] = true
		if not j.vivo: return
		j.hp = maxf(j.hp, j.hp_max * 0.5)
		var b: Ent = sim.chefe.boss if sim.chefe != null and sim.chefe.boss.vivo else null
		if b != null and j.acao.is_empty(): Jogador.cmd_atacar(sim, j, b.id))
	var invocou := 1 if vistos.has(invocado) else 0
	var errado := 0
	for k in ["soldado_caido", "carpideira_de_ossos", "eco_da_trombeta", "querubim_desfeito"]:
		if vistos.has(k): errado += 1
	print("    mobs na luta: ", vistos.keys())
	print("    estado=%s fase=%d hp=%d  (%d ms)" % [sim.chefe.estado, sim.chefe.fase, int(sim.chefe.boss.hp), Time.get_ticks_msec() - t0])
	ok(sim.chefe.fase >= 2, "%s passou da fase 1" % id)
	ok(errado == 0, "%s não chama mobs da Cripta" % id)
	if mec != "irma_celeste": ok(invocou > 0, "%s chamou %s" % [id, invocado])

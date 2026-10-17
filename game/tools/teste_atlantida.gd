extends SceneTree
## Teste headless da Atlântida e dos Salões de Amenti (0.9.4): entra pela Fenda do Novo Éden (nível 30; no 20 ela não abre),
## anda pelo mapa até cada spot e volta, fala com os NPCs, confere monstros e o Gadiro; depois a Esfinge no Egito, a laje
## (fechada sem a flag) e os Salões. Sai com 1 se algo falhar.
## godot --headless --path . -s tools/teste_atlantida.gd

var troca := {}
var avisos: Array = []
var falhas := 0

func _ev(t: String, d: Dictionary) -> void:
	if t == "trocar_mapa": troca = d
	if t == "aviso": avisos.append(str(d.get("texto", "")))

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

func falha(t: String) -> void:
	print("FALHA: ", t); falhas += 1

func usar_portal(sim: WorldSim, j: Ent, para: String) -> Ent:
	for o: Ent in sim.ents.values():
		if o.tipo == "objeto" and o.kind == "portal" and str(o.aux.get("para", "")) == para:
			j.pos = sim.celula_livre_perto(o.pos + Vector2(0.6, 0.6)); troca = {}
			for m: Ent in sim.ents.values():   # ninguém por perto bate e corta a canalização
				if m.tipo == "monstro" and m.pos.distance_to(j.pos) < 20.0: m.vivo = false; m.renasce_s = 9999.0
			Jogador.interagir(sim, j, o)
			rodar(sim, 1.0)
			return o
	falha("%s: sem portal para %s" % [sim.mapa_id, para]); return null

func andar(sim: WorldSim, j: Ent, alvo: Vector2) -> bool:
	var cam := sim.caminho(j.pos, alvo)
	if cam.is_empty() and j.pos.distance_to(alvo) > 2.0: return false
	for p in cam: j.pos = p   # teleporta pelo caminho (o que importa é a grade ligar os pontos)
	return true

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(7)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "humano", "Teste")
	Jogador.entrar(sim, j, "mata_do_granizo", Vector2(72.5, 84.5))
	Jogador.add_buff(sim, j, "teste", 99999.0, {"hp_pct": 8000.0}); j.hp = j.hp_max
	# nível 20: a Fenda não abre
	j.nivel = 20
	usar_portal(sim, j, "atlantida")
	if not troca.is_empty(): falha("a Fenda abriu no nível 20")
	j.nivel = 30
	usar_portal(sim, j, "atlantida")
	if troca.get("mapa", "") != "atlantida": falha("a Fenda não levou à Atlântida: %s / %s" % [str(troca), str(avisos)]); quit(1); return
	Jogador.entrar(sim, j, "atlantida", troca["pos"])
	rodar(sim, 1.0)
	if not sim.andavel(j.pos): falha("chegada da Atlântida fora do chão")
	var mobs := 0; var npcs := []; var semdef := {}
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro": mobs += 1
		if e.tipo == "monstro" and not Defs.MOBS.has(e.kind): semdef[e.kind] = true
		if e.tipo == "npc": npcs.append(e)
	print("atlantida: %d monstros, %d NPCs, chefe=%s" % [mobs, npcs.size(), sim.chefe.boss.kind if sim.chefe and sim.chefe.boss else "nenhum"])
	if mobs < 100: falha("poucos monstros na Atlântida (%d)" % mobs)
	if not semdef.is_empty(): falha("monstros sem definição: %s" % str(semdef.keys()))
	if sim.chefe == null: falha("Gadiro não está no mapa")
	for n: Ent in npcs:
		if not Defs.NPCS.has(n.kind): falha("NPC sem definição: " + n.kind); continue
		if not Missoes.faccao_ok(j, Defs.NPCS[n.kind].get("faccao")): continue   # Arautos não falam com a Vigília
		j.aux.erase("dialogo")
		Missoes.abrir(sim, j, n)
		if j.aux.get("dialogo", {}).is_empty() and Defs.NPCS[n.kind].has("dialogo"): falha("diálogo não abriu: " + n.kind)
	var chegada := j.pos
	var spots: Array = sim.mapa.get("spots", [])
	var ok := 0
	for sp in spots:
		if andar(sim, j, Vector2(sp["pos"][0], sp["pos"][1])): ok += 1
		else: falha("spot %s inalcançável a pé" % sp["id"])
		j.pos = chegada
	print("atlantida: %d/%d spots alcançados a pé" % [ok, spots.size()])
	usar_portal(sim, j, "mata_do_granizo")
	if troca.get("mapa", "") != "mata_do_granizo": falha("a Fenda de volta não levou ao Éden")
	else:
		Jogador.entrar(sim, j, "mata_do_granizo", troca["pos"]); rodar(sim, 0.5)
		if not sim.andavel(j.pos): falha("volta da Fenda fora do chão do Éden")
	# Egito: a Esfinge e a laje
	Jogador.entrar(sim, j, "egito", Vector2(140.5, 99.5)); rodar(sim, 0.5)
	var esf: Ent = null
	for e: Ent in sim.ents.values():
		if e.tipo == "npc" and e.kind == "esfinge_amenti": esf = e
	if esf == null: falha("Esfinge não está no Egito")
	else:
		Missoes.abrir(sim, j, esf)
		if j.aux.get("dialogo", {}).is_empty(): falha("a Esfinge não fala")
	j.flags.erase("amenti_aberto")
	usar_portal(sim, j, "saloes_de_amenti")
	if not troca.is_empty(): falha("a laje abriu sem a flag")
	j.flags["amenti_aberto"] = true
	usar_portal(sim, j, "saloes_de_amenti")
	if troca.get("mapa", "") != "saloes_de_amenti": falha("a laje não levou aos Salões")
	else:
		Jogador.entrar(sim, j, "saloes_de_amenti", troca["pos"]); rodar(sim, 1.0)
		if not sim.andavel(j.pos): falha("chegada em Amenti fora do chão")
		var m2 := 0
		for e: Ent in sim.ents.values():
			if e.tipo == "monstro":
				m2 += 1
				if not Defs.MOBS.has(e.kind): falha("Amenti: monstro sem definição " + e.kind)
		print("amenti: %d monstros" % m2)
		if not andar(sim, j, Vector2(60, 140)): print("amenti: a Antecâmara não liga a pé ao Vestíbulo (armadilhas e o Vazio ainda pendentes)")
	print("teste_atlantida: ", "OK" if falhas == 0 else "%d falha(s)" % falhas)
	quit(1 if falhas > 0 else 0)

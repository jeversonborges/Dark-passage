extends SceneTree
## Teste do Livro de Skills (0.9.8): por classe e evolução, o que o livro tem, a barra de 9 slots, a troca de slots,
## as recusas (fora do livro, nível baixo, alternar a forma), o save e a Forma Abominável (kit entra e sai da barra).
## godot --headless --path . -s tools/teste_livro_skills.gd

var falhas := 0

func conferir(ok: bool, msg: String) -> void:
	if not ok:
		falhas += 1
		print("   FALHA: ", msg)

func ids_livro(j: Ent) -> Array:
	return Evolucao.pool(j)

func ids_barra(j: Ent) -> Array:
	var out: Array = []
	for id in j.skills_slots: if id != "": out.append(id)
	return out

func _init() -> void:
	Defs.carregar()
	var classes := ["anjo", "demonio", "cultista", "humano", "mutante", "tecnomancer", "warlord"]
	print("| classe / evolução | no livro | na barra (slots 1..9) |")
	print("|---|---|---|")
	for c in classes:
		for ev in [""] + Evolucao.opcoes(c):
			var sim := WorldSim.new(1)
			var j := Jogador.criar(sim, c, "Teste")
			j.nivel = 50
			if ev != "": Evolucao.aplicar(sim, j, ev)
			var rot := "%s / %s" % [c, ev if ev != "" else "base"]
			var livro := ids_livro(j)
			conferir(j.skills_slots.size() == Evolucao.N_SLOTS, "%s: barra não tem 9 slots" % rot)
			conferir(_sem_repetidas(j.skills_slots), "%s: skill repetida na barra" % rot)
			for id in ids_barra(j): conferir(id in livro, "%s: %s na barra e fora do livro" % [rot, id])
			if ev != "":
				var evo_n := 0
				for h in Defs.EVOLUCOES["evolucoes"][ev]["habilidades"]: if h["id"] in livro: evo_n += 1
				conferir(evo_n == 5, "%s: o livro deveria ter as 5 da evolução" % rot)
			print("| %s | %d | %s |" % [rot, livro.size(), ", ".join(ids_barra(j))])
			_testar_troca(sim, j, rot)
			_testar_recusas(sim, j, rot)
			_testar_save(sim, c, j, rot)
	_testar_forma()
	print("FALHAS: %d" % falhas)
	quit(1 if falhas > 0 else 0)

func _sem_repetidas(slots: Array) -> bool:
	var vistos := {}
	for id in slots:
		if id == "": continue
		if vistos.has(id): return false
		vistos[id] = true
	return true

func _testar_troca(sim: WorldSim, j: Ent, rot: String) -> void:
	var a: String = j.skills_slots[0]
	var b: String = j.skills_slots[1]
	Evolucao.cmd_hotbar(sim, j, 0, b)
	conferir(j.skills_slots[0] == b and j.skills_slots[1] == a, "%s: troca de slots não trocou (%s, %s)" % [rot, a, b])
	conferir(_sem_repetidas(j.skills_slots), "%s: troca criou repetição" % rot)
	Evolucao.cmd_hotbar(sim, j, 1, b)   # de volta ao normal
	conferir(j.skills_slots[1] == b and j.skills_slots[0] == a, "%s: não voltou a troca" % rot)

func _testar_recusas(sim: WorldSim, j: Ent, rot: String) -> void:
	var antes := j.skills_slots.duplicate()
	Evolucao.cmd_hotbar(sim, j, 2, "skill_que_nao_existe")
	conferir(j.skills_slots == antes, "%s: aceitou skill fora do livro" % rot)
	if j.evolucao != "":
		var alto := ""
		for h in Evolucao.habilidades(j):
			if h.has("_evo") and int(h["nivel"]) > 40: alto = h["id"]; break
		var ja := alto in j.skills_slots
		j.nivel = 35
		Evolucao.cmd_hotbar(sim, j, 2, alto)
		conferir(ja or not alto in j.skills_slots, "%s: pôs skill de nível alto (%s)" % [rot, alto])
		j.nivel = 50

func _testar_save(sim: WorldSim, c: String, j: Ent, rot: String) -> void:
	var s := Jogador.salvar(j, sim)
	var j2 := Jogador.criar(sim, c, "Teste2", s)
	j2.nivel = 50
	conferir(j2.skills_slots == j.skills_slots, "%s: barra não voltou igual do save" % rot)

func _testar_forma() -> void:
	var sim := WorldSim.new(2)
	var j := Jogador.criar(sim, "mutante", "Abom")
	j.nivel = 50
	Evolucao.aplicar(sim, j, "abominacao")
	var toggle := {}
	for h in Evolucao.habilidades(j):
		if h.get("alterna", false): toggle = h
	Evolucao._alternar_forma(sim, j, toggle)
	var kit := ["tentaculos", "garras", "bocas", "vomito_acido", "olho", "devorar"]
	var barra := ids_barra(j)
	for k in kit: conferir(k in barra, "forma: %s não entrou na barra" % k)
	conferir(toggle["id"] in barra, "forma: a skill de alternar saiu da barra")
	conferir(_sem_repetidas(j.skills_slots), "forma: kit repetido na barra")
	print("| forma abominável ligada | %d | %s |" % [ids_livro(j).size(), ", ".join(barra)])
	Evolucao._alternar_forma(sim, j, toggle)
	barra = ids_barra(j)
	for k in kit: conferir(not k in barra, "forma off: %s ficou na barra" % k)
	conferir(toggle["id"] in barra, "forma off: alternar sumiu da barra")
	conferir(j.skills_slots.size() == Evolucao.N_SLOTS, "forma off: barra com %d slots" % j.skills_slots.size())

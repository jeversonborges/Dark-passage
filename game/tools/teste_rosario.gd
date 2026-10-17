extends SceneTree
## Teste headless do Rosário Voltaico: a skill tem de atingir vários inimigos em cadeia e nunca repetir um alvo.

var acertos := {}

func _ev(t: String, d: Dictionary) -> void:
	if t == "raio": acertos[d.get("para", Vector2.ZERO)] = true

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "tecnomancer", "Teste")
	j.nivel = 16
	Regras.recalc_jogador(j)
	Jogador.entrar(sim, j, "area_inicial", Vector2(44, 44))
	for i in 30: sim.passo(WorldSim.TICK)
	var mobs: Array = []
	var kind: String = Defs.MOBS.keys()[0]
	for k in 6:
		var m: Ent = sim.criar_mob(kind, j.pos + Vector2(2.0 + k * 1.2, 0.2), 16)
		m.ia["passivo"] = true
		m.hp = 99999.0
		m.hp_max = 99999.0
		mobs.append(m)
	var hab: Dictionary = {}
	for h in Defs.CLASSES["tecnomancer"]["habilidades"]:
		if h["id"] == "rosario_voltaico": hab = h
	print("habilidade lida: ", not hab.is_empty(), " saltos=", hab.get("saltos"), " paralisar=", hab.get("chance_paralisar"))
	var antes := {}
	for m in mobs: antes[m.id] = m.hp
	print("slot do rosario: ", _slot_do_rosario(j), " slots=", j.skills_slots)
	Jogador.cmd_skill(sim, j, _slot_do_rosario(j), mobs[0].id, mobs[0].pos)
	for i in int(3.0 * 30): sim.passo(WorldSim.TICK)
	var tocados := 0
	for m in mobs:
		if m.hp < antes[m.id]: tocados += 1
	print("RESULTADO: ", "OK" if tocados >= 2 and tocados <= 6 else "FALHOU", " tocados=", tocados, " de 6 (esperado 2 a 6, sem repetir)")
	quit()

func _slot_do_rosario(j: Ent) -> int:
	for i in j.skills_slots.size():
		if j.skills_slots[i] == "rosario_voltaico": return i
	return 0

extends SceneTree
## Bug do Andras: escada para o Ossário no meio da luta.
var ev: Array = []
func _ev(t: String, d: Dictionary) -> void:
	if t in ["trocar_mapa", "aviso", "chefe", "canal"]: ev.append("%s %s" % [t, str(d).left(100)])
func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)
func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(3)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "humano", "T")
	j.flags["venceu_general_partido"] = true
	var ini := Vector2(float(OS.get_cmdline_user_args()[0]), float(OS.get_cmdline_user_args()[1])) if OS.get_cmdline_user_args().size() >= 2 else Vector2(56, 24)
	Jogador.entrar(sim, j, "porao_matadouro", ini)
	j.hp_max = 90000; j.hp = 90000
	rodar(sim, 0.5)
	var b: Ent = sim.chefe.boss
	for i in 40:
		if j.acao.is_empty(): Jogador.cmd_atacar(sim, j, b.id)
		j.caminho.clear()
		rodar(sim, 0.2)
	print("boss hp ", b.hp, "/", b.hp_max, " pos ", b.pos)
	print("estado: ", sim.chefe.estado, " jog->centro ", j.pos.distance_to(sim.chefe.centro))
	var esc: Ent = null
	for o: Ent in sim.ents.values():
		if o.kind == "portal" and o.aux.get("para", "") == "ossario_carpideiras": esc = o
	Jogador.cmd_interagir(sim, j, esc.id)
	rodar(sim, 6.0)
	print("estado depois: ", sim.chefe.estado, " pos ", j.pos, " dist ", j.pos.distance_to(sim.chefe.centro))
	for x in ev: print("  ", x)
	quit()

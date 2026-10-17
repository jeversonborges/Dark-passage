extends SceneTree
## Trava diária/semanal dos chefes do Egito: quem já matou é empurrado da arena quando há gente sem trava;
## se só há gente travada, o chefe não acorda e não é alvejável. Baú: cada participante abre a sua parte uma vez.
var avisos: Array = []
var log: Array = []
func _ev(t: String, d: Dictionary) -> void:
	if t == "aviso": avisos.append(str(d.get("texto", "")))
	if t in ["dano", "morreu"] and log.size() < 8: log.append(t + " " + str(d).left(160))
func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(3)
	sim.evento.connect(_ev)
	var mp: Dictionary = Defs.ler("res://data/mapas/hawara_1.json")
	var c := Vector2(mp["chefe"]["arena"]["centro"][0], mp["chefe"]["arena"]["centro"][1])
	var a := Jogador.criar(sim, "mutante", "Travado")
	Jogador.entrar(sim, a, "hawara_1", c + Vector2(1, 1))
	var ch: ChefeCtl = sim.chefe
	a.flags["trava_petsuchos"] = ChefeEgito.proximo_reset("diaria")
	for i in 60: sim.passo(WorldSim.TICK)
	print("so_travado: estado=", ch.estado, " alvejavel=", ch.boss.alvejavel, " dentro=", a.pos.distance_to(c) < ch.raio_arena)
	var b := Jogador.criar(sim, "humano", "Livre")
	sim.adicionar_jogador(b, c + Vector2(2, 1))
	for j in [a, b]: Jogador.add_buff(sim, j, "teste", 99999.0, {"hp_pct": 8000.0})
	b.hp = b.hp_max; a.hp = a.hp_max
	print("b hp=", b.hp, "/", b.hp_max, " vivo=", b.vivo)
	log.clear()
	for i in 60: sim.passo(WorldSim.TICK)
	print("b vivo=", b.vivo, " dist=", b.pos.distance_to(c), " raio=", ch.raio_arena, " jogs=", sim.jogadores().size(), " travado_b=", ch.egito.travado(b))
	print("com_livre: estado=", ch.estado, " travado_fora=", a.pos.distance_to(c) >= ch.raio_arena, " alvo_e_livre=", ch._jog() == b)
	print(log)
	print("avisos: ", avisos.slice(0, 3))
	# mata o chefe com o livre: ele ganha a trava; o baú abre uma vez para ele e não para quem não lutou
	ch.boss.aux.erase("imune"); ch.boss.hp = 1.0
	sim.aplicar_dano_puro(ch.boss, 50.0, "fisico", b)
	for i in 10: sim.passo(WorldSim.TICK)
	print("morto=", not ch.boss.vivo, " trava_livre=", b.flags.has("trava_petsuchos"), " reset_em_h=", (float(b.flags.get("trava_petsuchos", 0)) - Time.get_unix_time_from_system()) / 3600.0)
	var bau: Ent = null
	for e: Ent in sim.ents.values():
		if e.aux.get("requer_chefe", "") == "petsuchos" and e.aux.get("kind", "") == "bau": bau = e
	print("pode_abrir livre=", ChefeEgito.pode_abrir_bau(sim, b, bau))
	ChefeEgito.marcar_bau(b, bau)
	print("pode_abrir de novo=", ChefeEgito.pode_abrir_bau(sim, b, bau), " semanal_em_dias=", (ChefeEgito.proximo_reset("semanal") - Time.get_unix_time_from_system()) / 86400.0)
	quit()

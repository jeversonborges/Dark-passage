extends SceneTree
## Arena do Agrak no mundo (scripts/sim/agrak_mundo.gd) com o mapa de verdade (data/mapas/agrak.json).
## Uso: godot --headless --path . --script res://tools/teste_agrak_mundo.gd
## Quatro gladiadores invulneráveis; os chefes morrem à força (matar) para testar a sequência, o espectador e o prêmio.

var falhas := 0

func check(cond: bool, msg: String) -> void:
	if not cond:
		falhas += 1
		print("[teste_agrak_mundo] FALHA ", msg)
	else:
		print("[teste_agrak_mundo] ok    ", msg)

func correr(sim: WorldSim, ag: AgrakMundo, segundos: float) -> void:
	var n := int(segundos / 0.1)
	for i in n:
		sim.passo(0.1)
		if ag.encerrado: return

func _initialize() -> void:
	Defs.carregar()
	var sim := WorldSim.new(7)
	var ids: Array = []
	var jogs: Array = []
	for k in 4:
		var e := Jogador.criar(sim, "humano", "G%d" % (k + 1))
		jogs.append(e); ids.append(e.id)
	Jogador.entrar(sim, jogs[0], "agrak", Vector2(23, 13.5))
	for k in range(1, 4):
		sim.adicionar_jogador(jogs[k], Vector2(23 + k, 13.5))
	for e in jogs: e.invuln_t = 1e9
	var ag := AgrakMundo.new(sim, Defs.AGRAK, ids)
	sim.agrak = ag
	check(ag.iniciar(), "arena começa com 4 gladiadores")
	check(sim.mapa_id == "agrak", "mapa agrak carregado")

	correr(sim, ag, 45.5)
	check(ag.ctl.etapa_atual() == "luta_leoes", "chamada termina e abre a luta dos leões")
	check(ag.chefes.size() == 3, "três leões nascem")
	var kinds := ag.chefes.values()
	check(kinds.has("leao_sansao") and kinds.has("leao_dalila") and kinds.has("leao_nabucodonosor"), "os três leões certos")
	check(jogs[0].lado_forcado == "agrak", "gladiadores são do mesmo lado na luta 1")

	for id in ag.chefes.keys().duplicate():
		sim.matar(sim.ents[id], null)
	correr(sim, ag, 0.2)
	check(ag.ctl.etapa_atual() == "respiro", "leões mortos: respiro")
	correr(sim, ag, 20.5)
	check(ag.ctl.etapa_atual() == "luta_gigante", "respiro acaba e o Golias entra")
	check(ag.chefes.size() == 1 and ag.chefes.values()[0] == "golias", "Golias nasce sozinho")

	for id in ag.chefes.keys().duplicate():
		sim.matar(sim.ents[id], null)
	correr(sim, ag, 15.5)
	check(ag.ctl.etapa_atual() == "ultimo_de_pe", "luta final")
	check(jogs[1].lado_forcado == "g_%d" % jogs[1].id, "cada um vira o próprio lado na luta final")

	sim.matar(jogs[1], null); sim.matar(jogs[2], null)
	correr(sim, ag, 0.2)
	check(jogs[1].aux.get("agrak_espectador", false), "derrotado vira espectador")
	check(jogs[1].pos.distance_to(Vector2(6.5, 16)) < 3.0, "espectador vai para o camarote")
	check(ag.ctl.vivos.size() == 2, "dois de pé na luta final")

	sim.matar(jogs[3], null)
	correr(sim, ag, 0.2)
	check(ag.ctl.etapa_atual() == "coroacao", "último de pé: coroação")
	var fichas := 0
	for it in jogs[0].inv:
		if it.get("id", "") == "ficha_sangue": fichas += int(it.get("qtd", 1))
	check(fichas == 1, "vencedor leva 1 ficha de sangue")
	correr(sim, ag, 15.5)
	check(ag.encerrado, "evento encerra depois da coroação")
	check(not jogs[0].aux.has("agrak_espectador"), "vencedor não fica como espectador")

	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

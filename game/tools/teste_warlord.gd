extends SceneTree
## Teste headless do Warlord (Vigília): criação, equipamento inicial, Ódio e as 10 habilidades, no nível 50.
## godot --headless --path . --script res://tools/teste_warlord.gd

var cont := {}
var avisos: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "aviso": avisos.append(str(d.get("texto", "")))

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "warlord", "Teste")
	var mi: Dictionary = Defs.ler("res://data/mapas/area_inicial.json")
	var sp: Array = mi["spawn_por_faccao"].get(j.faccao, mi["spawn"])
	Jogador.entrar(sim, j, "area_inicial", Vector2(sp[0], sp[1]))
	rodar(sim, 0.5)
	print("fac=%s evolucao='%s' arma=%s escudo=%s rec=%.1f hp=%d defesa=%.1f bloqueio_escudo=%.2f" % [j.faccao, j.evolucao,
		str(j.equip.get("arma", {}).get("id", "-")), str(j.equip.get("segunda_mao", {}).get("id", "-")), j.rec, j.hp_max, j.defesa,
		float(j.aux.get("bloqueio_escudo", 0.0))])
	# nível 50: todas as habilidades liberadas; Ódio cheio para testar o gasto do Eclipse
	j.nivel = 50; Regras.recalc_jogador(j)
	var alvos: Array = []
	for k in 6:
		var m := sim.criar_mob("nao_julgado", sim.celula_livre_perto(j.pos + Vector2(2.0 + k * 0.4, 1.0)), 50)
		if m != null: alvos.append(m)
	print("monstros criados: %d" % alvos.size())
	for slot in j.skills_slots.size():
		var h := Jogador.skill_def(j, slot)
		j.rec = 100.0; j.cds.clear(); j.em_combate_t = 0.0
		cont.clear(); avisos.clear()
		var alvo: Ent = alvos[0] if alvos.size() > 0 else null
		Jogador.cmd_skill(sim, j, slot, alvo.id if alvo != null else -1, alvo.pos if alvo != null else j.pos + Vector2(1, 0))
		rodar(sim, 2.5)
		print("slot %d %-28s usou=%s eventos_dano=%s avisos=%s rec=%.1f odio_usado=%s" % [slot, h.get("id", "?"),
			cont.get("skill", 0), cont.get("dano", 0), str(avisos.slice(0, 2)), j.rec, str(j.aux.get("odio_usado", "-"))])
	# Ódio decai fora de combate e se mantém em combate
	j.rec = 60.0; j.em_combate_t = 0.0; rodar(sim, 2.0)
	print("ódio fora de combate 2 s: %.1f (esperado ~48)" % j.rec)
	j.rec = 60.0; j.em_combate_t = 0.0
	print("defesa do Warlord com 60 de Ódio: %.3f (bônus %.3f)" % [j.defesa * (1.0 + Regras.defesa_warlord(j)), Regras.defesa_warlord(j)])
	quit(0)

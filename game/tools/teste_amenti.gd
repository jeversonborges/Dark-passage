extends SceneTree
## Teste headless da raid dos Salões de Amenti: um personagem forte entra na arena, o chefe O Perfeito
## precisa acordar, passar pelas fases e cair. O mínimo de jogadores vem do chefe (minimo_jogadores).
## godot --headless --path . --script res://tools/teste_amenti.gd

var derrotado := ""
var fase_max := 1
var acordou := false

var cont := {}
var sim_ref: WorldSim = null
var dano_chefe := 0.0
var dano_chefe_n := 0

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "dano" and sim_ref != null and sim_ref.chefe.boss != null and int(d.get("id", -1)) == sim_ref.chefe.boss.id:
		dano_chefe += float(d.get("valor", 0)); dano_chefe_n += 1
	if t == "chefe_derrotado": derrotado = str(d)
	if t == "chefe" and d.has("fase"): fase_max = maxi(fase_max, int(d["fase"]))
	if t == "chefe" and d.has("inicio"): acordou = true

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(777)
	sim.evento.connect(_ev); sim_ref = sim
	var j := Jogador.criar(sim, "demonio", "Teste")
	Jogador.entrar(sim, j, "saloes_de_amenti", Vector2(60.0, 6.5))
	var chefe_id: String = (Defs.ler("res://data/mapas/saloes_de_amenti.json") as Dictionary)["chefe"]["id"]
	j.nivel = 150; j.stats["FOR"] = 400; j.stats["AGI"] = 200; j.stats["VIT"] = 300
	Regras.recalc_jogador(j); j.hp_max = 400000; j.hp = 400000
	for m: Ent in sim.ents.values():
		if m.tipo == "monstro": m.vivo = false
	j.pos = sim.celula_livre_perto(Vector2(56.5, 46.5))   # chão livre perto do chefe (a célula do centro é pilar)
	var n_fases: int = (Defs.CHEFES[chefe_id]["fases"] as Array).size()
	for i in int(2700.0 * 30):
		if i % 6 == 0 and j.vivo:
			j.hp = maxf(j.hp, j.hp_max * 0.6)
			var alvo: Ent = null
			for e: Ent in sim.ents.values():
				if e.vivo and e.alvejavel and e.tipo == "chefe": alvo = e
			if alvo != null and j.acao.is_empty(): Jogador.cmd_atacar(sim, j, alvo.id)
		sim.passo(WorldSim.TICK)
		if derrotado != "": break
	var ok := acordou and derrotado != "" and fase_max == n_fases
	if not ok: falhas += 1
	print("[saloes_de_amenti] %s chefe=%s acordou=%s fase=%d/%d derrotado=%s" % ["OK" if ok else "FALHOU", chefe_id, acordou, fase_max, n_fases, derrotado])
	var boss_ent: Ent = sim.ents.get(sim.chefe.boss.id) if sim.chefe.boss != null else null
	print("    estado=%s hp_chefe=%s/%s jogador_vivo=%s pos=%s" % [sim.chefe.estado, str(boss_ent.hp) if boss_ent else "-", str(boss_ent.hp_max) if boss_ent else "-", j.vivo, str(j.pos)])
	print("    boss_id=%d dano_no_chefe=%.0f (%d eventos)" % [sim.chefe.boss.id if sim.chefe.boss else -1, dano_chefe, dano_chefe_n])
	if boss_ent: print("    alvo_jogador=%s acao=%s aux_chefe=%s status_chefe=%s eventos=%s" % [str(j.alvo), str(j.acao.keys()), str(boss_ent.aux.keys()), str(boss_ent.status.keys()), str(cont)])
	print("teste_amenti: ", "tudo certo" if falhas == 0 else "%d falha(s)" % falhas)
	quit(1 if falhas > 0 else 0)

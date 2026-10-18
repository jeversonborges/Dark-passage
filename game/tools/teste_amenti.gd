extends SceneTree
## Teste headless da raid dos Salões de Amenti: um personagem forte entra na arena, o chefe O Perfeito
## precisa acordar, passar pelas fases e cair. O mínimo de jogadores vem do chefe (minimo_jogadores).
## godot --headless --path . --script res://tools/teste_amenti.gd

var derrotado := ""
var fase_max := 1
var acordou := false

func _ev(t: String, d: Dictionary) -> void:
	if t == "chefe_derrotado": derrotado = str(d)
	if t == "chefe" and d.has("fase"): fase_max = maxi(fase_max, int(d["fase"]))
	if t == "chefe" and d.has("inicio"): acordou = true

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(777)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "demonio", "Teste")
	Jogador.entrar(sim, j, "saloes_de_amenti", Vector2(60.0, 6.5))
	var chefe_id: String = (Defs.ler("res://data/mapas/saloes_de_amenti.json") as Dictionary)["chefe"]["id"]
	j.nivel = 150; j.stats["FOR"] = 400; j.stats["AGI"] = 200; j.stats["VIT"] = 300
	Regras.recalc_jogador(j); j.hp_max = 400000; j.hp = 400000
	for m: Ent in sim.ents.values():
		if m.tipo == "monstro": m.vivo = false
	j.pos = sim.celula_livre_perto(Vector2(52.0, 43.0))
	var n_fases: int = (Defs.CHEFES[chefe_id]["fases"] as Array).size()
	for i in int(900.0 * 30):
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
	print("teste_amenti: ", "tudo certo" if falhas == 0 else "%d falha(s)" % falhas)
	quit(1 if falhas > 0 else 0)

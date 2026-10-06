extends Node
## Teste da rede: depois de entrar no mundo, anda, ataca o monstro mais perto, tira fotos e sai.
## Uso: godot -- conectar=127.0.0.1 usuario=ana senha=1234 classe=anjo teste_rede=/pasta [tempo=25] [prefixo=a]

var jogo: Node2D
var args := {}
var t := 0.0
var fotos := 0
var passo := 0.0

func _process(dt: float) -> void:
	t += dt
	passo -= dt
	if jogo == null or jogo.jog == null: return
	var j: Ent = jogo.jog
	if passo <= 0.0:
		passo = 2.0
		var alvo: Ent = null
		var md := 12.0
		for e: Ent in jogo.sim.ents.values():
			if e.vivo and e.tipo == "monstro" and e.pos.distance_to(j.pos) < md: md = e.pos.distance_to(j.pos); alvo = e
		if alvo != null and t > 8.0: jogo.cmd("atacar", [alvo.id, false])
		else: jogo.cmd("mover", [j.pos + Vector2(randf_range(-4, 4), randf_range(-4, 4))])
	var tempo := float(args.get("tempo", 25))
	if fotos < 3 and t > tempo * (fotos + 1) / 4.0:
		fotos += 1
		var img := get_viewport().get_texture().get_image()
		var dir: String = args["teste_rede"]
		DirAccess.make_dir_recursive_absolute(dir)
		img.save_png("%s/%s_%d.png" % [dir, args.get("prefixo", args.get("usuario", "x")), fotos])
		var outros := 0; var mobs := 0
		for e: Ent in jogo.sim.ents.values():
			if e.tipo == "jogador" and e.id != j.id: outros += 1
			if e.tipo == "monstro": mobs += 1
		print("[teste_rede] %s t=%.0f pos=%s hp=%d/%d nivel=%d xp=%d ents=%d mobs=%d outros_jogadores=%d alvo=%d" % [j.nome, t, j.pos, j.hp, j.hp_max, j.nivel, j.xp, jogo.sim.ents.size(), mobs, outros, j.alvo])
	if t > tempo:
		print("[teste_rede] fim ", j.nome, " inv=", j.inv.size(), " ouro=", j.ouro)
		get_tree().quit()

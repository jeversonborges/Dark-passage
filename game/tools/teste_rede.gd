extends Node
## Teste da rede: depois de entrar no mundo, anda, ataca o monstro mais perto, tira fotos e sai.
## Uso: godot -- conectar=127.0.0.1 usuario=ana senha=1234 classe=anjo teste_rede=/pasta [tempo=25] [prefixo=a]

var jogo: Node2D
var args := {}
var t := 0.0
var fotos := 0
var passo := 0.0
var feitos := {}
const Troca := preload("res://scripts/net/troca.gd")

func _process(dt: float) -> void:
	t += dt
	passo -= dt
	if jogo == null or jogo.jog == null: return
	var j: Ent = jogo.jog
	if args.has("falas"):   # teste do chat/grupo: "t:texto;t:texto" (espaços viram _), mesmo caminho do Enter
		for f in str(args["falas"]).split(";"):
			var k := f.get_slice(":", 0)
			if not feitos.has(k) and t > float(k):
				feitos[k] = true
				jogo.hud.abrir_chat(); jogo.hud.chat_entrada.text = f.get_slice(":", 1).replace("_", " "); jogo.hud._chat_enviar(jogo.hud.chat_entrada.text)
	if args.has("aceitar_em") and not feitos.has("aceitar") and t > float(args["aceitar_em"]):
		feitos["aceitar"] = true
		jogo.grupo_cmd("aceitar")
	if args.has("inspecionar_em") and not feitos.has("inspecionar") and t > float(args["inspecionar_em"]):
		feitos["inspecionar"] = true
		for e: Ent in jogo.sim.ents.values():
			if e.tipo == "jogador" and e.id != j.id: jogo.inspecionar(e.id); break
	if args.has("inspecao_em") and not feitos.has("inspecao_print") and t > float(args["inspecao_em"]):
		feitos["inspecao_print"] = true
		var ib = jogo.hud.inspecao_box
		print("[teste_rede] %s inspecao visivel=%s texto=%s" % [j.nome, str(ib != null), str(ib.get_child(0).get_child(0).text) if ib != null else "-"])
		print("[teste_rede] %s grupo_box visivel=%s linhas=%d" % [j.nome, str(jogo.hud.grupo_box.visible), jogo.hud.grupo_box.get_child_count()])
	# teste da troca: troca_pedir_em / troca_aceitar_em / troca_por_em (põe o 1º item da mochila e 25 de ouro) /
	# troca_ok_em / troca_foto_em (tira foto da janela de troca)
	for k in ["troca_pedir_em", "troca_aceitar_em", "troca_por_em", "troca_ok_em", "troca_foto_em"]:
		if not args.has(k) or feitos.has(k) or t <= float(args[k]): continue
		feitos[k] = true
		match k:
			"troca_pedir_em":
				for e: Ent in jogo.sim.ents.values():
					if e.tipo == "jogador" and e.id != j.id: jogo.troca_cmd("pedir", {"id": e.id}); break
			"troca_aceitar_em": jogo.troca_cmd("aceitar")
			"troca_por_em":
				for it in j.inv:
					if Troca.pode_negociar(it) == "": jogo.janelas._acao_direita(it, "mochila"); break
				jogo.troca_cmd("ouro", {"valor": mini(25, j.ouro)})
			"troca_ok_em": jogo.troca_cmd("ok")
			"troca_foto_em":
				var dir2: String = args["teste_rede"]
				DirAccess.make_dir_recursive_absolute(dir2)
				get_viewport().get_texture().get_image().save_png("%s/%s_troca.png" % [dir2, args.get("prefixo", args.get("usuario", "x"))])
				print("[teste_rede] %s troca=%s inv=%d ouro=%d" % [j.nome, str(jogo.janelas.troca_d.get("eu", {})), j.inv.size(), j.ouro])
	passo = 99.0
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
		print("[teste_rede] chat de ", j.nome, ": ", jogo.hud.chat_texto.get_parsed_text().replace("\n", " | "))
		print("[teste_rede] fim grupo_box visivel=%s linhas=%d" % [str(jogo.hud.grupo_box.visible), jogo.hud.grupo_box.get_child_count()])
		get_tree().quit()

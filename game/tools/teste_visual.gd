extends Node
## Roteiro de teste visual: espera o mundo montar, anda, luta, abre janelas e salva prints em args.fotos.

var jogo
var args := {}
var t := 0.0
var passo := 0
var pasta := ""
var roteiro: Array = []

func _ready() -> void:
	pasta = args["fotos"]
	DirAccess.make_dir_recursive_absolute(pasta)
	if args.has("sem_hud"):
		jogo.hud.visible = false
	var r: String = args.get("roteiro", "geral")
	match r:
		"geral":
			roteiro = [
				[2.5, "foto", "1_chegada"],
				[0.1, "janela", "inventario"], [0.6, "foto", "2_inventario"], [0.1, "janela", "inventario"],
				[0.1, "lutar", ""], [5.0, "foto", "3_combate"],
				[0.1, "lutar", ""], [4.0, "foto", "4_combate2"],
				[0.1, "mapa", ""], [0.5, "foto", "5_mapa"], [0.1, "mapa", ""],
				[0.1, "npc", ""], [2.5, "foto", "6_dialogo"],
				[0.5, "fim", ""]]
		"chefe":
			roteiro = [[1.5, "forte", ""], [0.1, "lutar_chefe", ""], [6.0, "foto", "c1"], [6.0, "foto", "c2"], [8.0, "foto", "c3"], [0.5, "fim", ""]]
		"tour":
			var i := 0
			for par in str(args.get("pontos", "")).split(";"):
				var xy := par.split(",")
				roteiro.append([0.2, "ir", Vector2(float(xy[0]), float(xy[1]))])
				roteiro.append([2.2, "foto", "t%d_%s_%s" % [i, xy[0], xy[1]]])
				i += 1
			roteiro.append([0.3, "fim", ""])
		"bichos":
			for k in str(args.get("kinds", "cao_de_vala,porco_pestilento,corvo_de_cinza,filho_de_cardo")).split(","):
				roteiro.append([0.3, "perto_de", k])
				for i in 10: roteiro.append([0.45, "foto", k + "_%d" % i])
			roteiro.append([0.3, "fim", ""])
		"itens":   # itens no chão: brilho, hover de item e de NPC
			roteiro = [[2.5, "afastar", ""], [1.5, "soltar_itens", ""], [1.5, "foto", "i1_chao"], [0.1, "mouse_item", 2], [0.4, "foto", "i2_hover_item"],
				[0.1, "mouse_item", 0], [0.4, "foto", "i3_hover_ouro"], [0.1, "mouse_npc", "ir"], [1.5, "mouse_npc", ""], [0.5, "foto", "i4_hover_npc"], [0.3, "fim", ""]]
		"pontes":   # atravessa as duas pontes do Rio Amargo andando (prova visual e de colisão)
			roteiro = [[2.0, "zoom", 0.8],
				[0.2, "ir", Vector2(95.5, 71.5)], [2.0, "foto", "p1_ponte_bonde_margem_oeste"],
				[0.1, "mover", Vector2(107.5, 71.5)], [1.6, "foto", "p1_ponte_bonde_no_meio"], [3.0, "foto", "p1_ponte_bonde_margem_leste"],
				[0.2, "ir", Vector2(88.5, 106.5)], [2.0, "foto", "p2_ponte_enforcados_margem_oeste"],
				[0.1, "mover", Vector2(102.5, 106.5)], [1.8, "foto", "p2_ponte_enforcados_no_meio"], [3.2, "foto", "p2_ponte_enforcados_margem_leste"],
				[0.3, "fim", ""]]
		"so_foto":
			roteiro = [[float(args.get("espera", "3")), "foto", args.get("nome", "foto")], [0.3, "fim", ""]]

func _process(dt: float) -> void:
	t += dt
	if passo >= roteiro.size(): return
	var p: Array = roteiro[passo]
	if t < p[0]: return
	t = 0.0
	passo += 1
	match p[1]:
		"foto":
			print("pos ", p[2], " ", jogo.jog.pos)
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			img.save_png(pasta + "/" + p[2] + ".png")
			print("foto ", p[2])
		"janela": jogo.janelas.alternar(p[2])
		"zoom": jogo.cam.zoom = Vector2(p[2], p[2])
		"mover":
			Jogador.cmd_mover(jogo.sim, jogo.jog, p[2])
			print("andando para ", p[2], " de ", jogo.jog.pos)
		"afastar":   # sai do acampamento para um descampado
			var d := Vector2(float(args.get("dx", "12")), float(args.get("dy", "-6")))
			jogo.jog.pos = jogo.sim.celula_livre_perto(jogo.jog.pos + d)
			for e: Ent in jogo.sim.ents.values():   # tira os bichos de perto para a foto ficar limpa
				if e.tipo == "monstro" and e.pos.distance_to(jogo.jog.pos) < 14.0:
					e.pos = jogo.sim.celula_livre_perto(e.pos + (e.pos - jogo.jog.pos).normalized() * 25.0)
		"soltar_itens":
			var base: Vector2 = jogo.jog.pos
			jogo.sim.soltar_no_chao(Itens.novo("_ouro", 37), base + Vector2(0.5, 3.5), -1, base)
			var lista := [["espada_vigilia_rachada", "comum"], ["couro_sobrevivente_peito", "magico"], ["cajado_valvulas", "raro"], ["escopeta_cano_duplo", "excelente"]]
			for i in lista.size():
				var it := Itens.novo(lista[i][0]); it["raridade"] = lista[i][1]
				jogo.sim.soltar_no_chao(it, base + Vector2(2.0 + i * 1.6, 2.5 - i * 0.6), -1, base)
		"mouse_item":
			var ids: Array = jogo.itens_chao.keys(); ids.sort()
			var n = jogo.itens_chao[ids[mini(int(p[2]), ids.size() - 1)]]
			var tela: Vector2 = get_viewport().get_canvas_transform() * n.global_position
			print("item_tela ", int(tela.x), " ", int(tela.y))
			get_viewport().warp_mouse(get_viewport().get_canvas_transform() * (n.global_position + Vector2(18, -4)))
		"mouse_npc":
			var npc: Ent = null
			for e: Ent in jogo.sim.ents.values():
				if e.tipo == "npc" and (npc == null or e.pos.distance_to(jogo.jog.pos) < npc.pos.distance_to(jogo.jog.pos)): npc = e
			if npc and p[2] == "ir":
				jogo.jog.pos = jogo.sim.celula_livre_perto(npc.pos + Vector2(2.5, 1.5))
			elif npc and jogo.views.has(npc.id):
				var v = jogo.views[npc.id]
				get_viewport().warp_mouse(get_viewport().get_canvas_transform() * (v.global_position + Vector2(0, -50)))
		"ir":
			jogo.jog.pos = jogo.sim.celula_livre_perto(p[2])
			jogo.jog.invuln_t = 999.0; jogo.jog.imune_t = 999.0
		"mapa": jogo.hud.alternar_mapa()
		"perto_de":
			var alvo: Ent = null
			for e: Ent in jogo.sim.ents.values():
				if e.tipo == "monstro" and e.vivo and e.kind == p[2] and (alvo == null or e.aux.get("alfa", false)): alvo = e
			if alvo == null:   # mob de missão (Filho de Cardo): cria do lado
				alvo = jogo.sim.criar_mob(p[2], jogo.sim.celula_livre_perto(jogo.jog.pos + Vector2(3, 3)), 5)
			if alvo:
				jogo.jog.pos = jogo.sim.celula_livre_perto(alvo.pos + Vector2(3.5, 1.0))
				jogo.jog.hp_max = 999999.0; jogo.jog.hp = jogo.jog.hp_max
				Jogador.cmd_atacar(jogo.sim, jogo.jog, alvo.id)
		"lutar":
			var melhor: Ent = null
			for e: Ent in jogo.sim.ents.values():
				if e.tipo == "monstro" and e.vivo and (melhor == null or e.pos.distance_to(jogo.jog.pos) < melhor.pos.distance_to(jogo.jog.pos)): melhor = e
			if melhor:
				jogo.jog.pos = jogo.sim.celula_livre_perto(melhor.pos + Vector2(2.5, 0.5))
				Jogador.cmd_atacar(jogo.sim, jogo.jog, melhor.id)
				get_tree().create_timer(1.5).timeout.connect(func(): Jogador.cmd_skill(jogo.sim, jogo.jog, 0, melhor.id, melhor.pos))
				get_tree().create_timer(2.6).timeout.connect(func(): Jogador.cmd_skill(jogo.sim, jogo.jog, 1, melhor.id, melhor.pos))
		"forte":
			jogo.jog.nivel = 20; jogo.jog.stats = {"FOR": 60.0, "AGI": 60.0, "VIT": 80.0, "ESP": 40.0}
			Regras.recalc_jogador(jogo.jog); jogo.jog.hp = jogo.jog.hp_max
		"lutar_chefe":
			var b: Ent = null
			for e: Ent in jogo.sim.ents.values():
				if e.tipo == "chefe": b = e
			if b:
				jogo.jog.pos = jogo.sim.celula_livre_perto(b.pos + Vector2(3, 1))
				Jogador.cmd_atacar(jogo.sim, jogo.jog, b.id)
		"npc":
			for e: Ent in jogo.sim.ents.values():
				if e.tipo == "npc" and Missoes.marcador_npc(jogo.jog, e.kind) == "!":
					jogo.jog.pos = jogo.sim.celula_livre_perto(e.pos + Vector2(1.2, 0.6))
					Jogador.cmd_interagir(jogo.sim, jogo.jog, e.id)
					break
		"fim": get_tree().quit()

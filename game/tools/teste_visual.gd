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
		"menu":   # menu do personagem: equipamento, melhorias na mochila, comparação e a arca
			roteiro = [[2.0, "preparar_menu", ""], [0.2, "janela", "inventario"], [0.2, "abrir_arca", ""], [1.0, "foto", "menu_1"],
				[0.1, "tip_melhoria", ""], [0.5, "foto", "menu_2_tip"], [0.1, "tip_slot", ""], [0.5, "foto", "menu_3_slot"],
				[0.1, "janela", "missoes"], [0.6, "foto", "menu_4_diario"], [0.3, "fim", ""]]
		"revista":   # tecla G: a Gazeta do Impasse com os drops das masmorras e raids
			roteiro = [[2.5, "foto", "1_mundo"], [0.2, "janela", "revista"], [1.0, "foto", "revista_1"],
				[0.2, "fim", ""]]
		"teleporte":   # menu V: lista, tooltip, viagem paga e o ouro cobrado
			roteiro = [[2.5, "preparar_tp", ""], [0.2, "janela", "teleporte"], [0.8, "foto", "tp_1_menu"],
				[0.1, "tip_tp", "rio_amargo"], [0.5, "foto", "tp_2_tip"], [0.1, "janela", "teleporte"],
				[0.1, "tp", "rio_amargo"], [1.5, "foto", "tp_3_canal"], [3.5, "foto", "tp_4_chegou"],
				[0.1, "janela", "teleporte"], [0.8, "foto", "tp_5_menu_depois"], [0.3, "fim", ""]]
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
		"cripta":   # andares da cripta: troca de mapa e fotografa cada ponto (mapa,x,y;...)
			roteiro = [[2.0, "zoom", float(args.get("zoom", "1.0"))]]
			var i := 0
			for par in str(args.get("pontos", "porao_matadouro,30,30")).split(";"):
				var q := par.split(",")
				roteiro.append([0.2, "trocar", [q[0], Vector2(float(q[1]), float(q[2]))]])
				roteiro.append([3.0, "foto", "%s%d_%s" % [args.get("prefixo", "c"), i, q[0]]])
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
		"panorama":   # vistas largas do deserto para o fundo do menu (sem HUD, sem o jogador)
			roteiro = [[1.5, "zoom", float(args.get("zoom", "0.55"))]]
			var i := 0
			for par in str(args.get("pontos", "95,90")).split(";"):
				var xy := par.split(",")
				roteiro.append([0.2, "ir", Vector2(float(xy[0]), float(xy[1]))])
				roteiro.append([0.1, "sumir_jogador", ""])
				roteiro.append([6.5, "foto", "pan%d_%s_%s" % [i, xy[0], xy[1]]])
				i += 1
			roteiro.append([0.3, "fim", ""])
		"leque":   # skill em área do nível 5 lançada para várias direções: arte virada para onde mira e fogo no caminho
			roteiro = [[2.0, "ir", Vector2(70, 92)], [0.1, "forte", ""], [0.3, "zoom", 1.3]]
			for d in [["sudeste", Vector2(1, 0)], ["norte", Vector2(-1, 1)], ["noroeste", Vector2(-1, 0)], ["sul", Vector2(1, -1)]]:
				roteiro.append([0.3, "skill_area", d[1]])
				roteiro.append([0.3, "foto", "l_%s_golpe" % d[0]])
				roteiro.append([1.2, "foto", "l_%s_fogo" % d[0]])
				roteiro.append([2.6, "foto", "l_%s_fim" % d[0]])
				roteiro.append([0.8, "nada", ""])
			roteiro.append([0.3, "skill_area", Vector2(1, 0), true])
			roteiro.append([1.2, "foto", "l_com_bichos"])
			roteiro.append([0.3, "fim", ""])
		"voo":   # personagem parado e andando de perto, num descampado (prova das folhas novas)
			roteiro = [[2.0, "ir", Vector2(70, 92)], [0.2, "zoom", 1.8], [1.5, "foto", "v1_parado"], [0.35, "foto", "v2_parado"],
				[0.1, "mover", Vector2(76, 92)], [0.5, "foto", "v3_andando"], [0.25, "foto", "v4_andando"], [2.5, "mover", Vector2(70, 98)], [0.6, "foto", "v5_andando"], [0.3, "fim", ""]]
		"auto":   # modo automático novo: skills marcadas na barra, farm no spot e a janela de ajustes (Shift+Z)
			roteiro = [[2.0, "ir", Vector2(84, 115)], [0.1, "forte", ""], [0.3, "auto_marcar", [0, 3]], [0.2, "auto_ligar", ""],
				[7.0, "foto", "a1_farm"], [0.2, "janela", "auto"], [0.6, "foto", "a2_janela"], [0.3, "fim", ""]]
		"talentos":
			roteiro = [[2.0, "forte", ""], [0.2, "talentos_por", ""], [0.3, "janela", "talentos"], [0.8, "foto", "t1_arvore"], [0.3, "fim", ""]]
		"molduras":   # caixas soltas no kit Ferrugem Sagrada: convite, troca, inspeção, menu do jogador, ajuda, texto e mapa
			roteiro = [[2.5, "popup", "convite"], [0.6, "foto", "m1_convite"], [0.1, "popup", "troca"], [0.6, "foto", "m2_troca"],
				[0.1, "popup", "inspecao"], [0.2, "popup", "menu_jogador"], [0.6, "foto", "m3_inspecao_menu"], [0.1, "popup", "limpar"],
				[0.1, "popup", "ajuda"], [0.6, "foto", "m4_ajuda"], [0.1, "popup", "limpar"],
				[0.1, "popup", "texto"], [0.6, "foto", "m5_texto"], [0.1, "popup", "limpar"],
				[0.1, "mapa", ""], [0.6, "foto", "m6_mapa"], [0.3, "fim", ""]]
		"item_tip":   # detalhes de item: relíquia de duas mãos e anel raro com atributo, pela mochila
			roteiro = [[2.0, "item_tip", "lendario"], [0.4, "foto", "item_lendario"], [0.1, "item_tip", "anel"], [0.4, "foto", "item_anel"], [0.3, "fim", ""]]
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
			print("pos ", p[2], " ", jogo.jog.pos, " mapa ", jogo.sim.mapa_id, " ouro ", jogo.jog.ouro)
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			img.save_png(pasta + "/" + p[2] + ".png")
			print("foto ", p[2])
		"janela": jogo.janelas.alternar(p[2])
		"auto_marcar":
			for s in p[2]: jogo.cmd("auto_skill", [s])
		"auto_ligar": jogo.cmd("auto", [true])
		"talentos_por":
			var hs: Array = []
			for h in Defs.CLASSES[jogo.jog.classe]["habilidades"]:
				if not h.get("passiva", false) and int(h["nivel"]) <= jogo.jog.nivel: hs.append(h["id"])
			for k in 3: for id in hs.slice(0, 2): jogo.cmd("talento", [id])
		"preparar_menu": _preparar_menu()
		"abrir_arca":
			jogo.janelas.servico({"tipo": "armazem", "titulo": "Arca do Primarca", "fala": "O que entra na arca não enferruja. Nem a memória.", "npc": jogo.jog.id})
		"tip_melhoria":
			var jn = jogo.janelas
			for it in jogo.jog.inv:
				if jn.ganho(it) > 0:
					var g: Control = jn._grade_mochila
					var mp: Vector2 = g.get_global_rect().position + Vector2(int(it["x"]) * 30 + 14, int(it["y"]) * 30 + 14)
					get_viewport().warp_mouse(mp)
					jogo.hud.mostrar_tip(jn.tip_item(it, "mochila")); break
		"tip_slot":
			var jn2 = jogo.janelas
			for a in jn2.alvos_soltar:
				if is_instance_valid(a) and a.dados.has("slot") and not jogo.jog.equip.has(a.dados["slot"]):
					get_viewport().warp_mouse(a.get_global_rect().get_center())
					a.dados["hover"] = true
					jogo.hud.mostrar_tip(jn2._tip_slot_vazio(a.dados["slot"])); break
		"zoom": jogo.cam.zoom = Vector2(p[2], p[2])
		"sumir_jogador":
			if jogo.views.has(jogo.jog.id): jogo.views[jogo.jog.id].visible = false
			jogo.jog.invuln_t = 999.0; jogo.jog.imune_t = 999.0
			if jogo.get("titulo_zona") != null: jogo.titulo_zona.visible = false
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
		"trocar":
			jogo.jog.invuln_t = 999.0; jogo.jog.imune_t = 999.0
			jogo._trocar_mapa(p[2][0], p[2][1])
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
		"preparar_tp":
			jogo.jog.nivel = int(args.get("nivel", "14")); Regras.recalc_jogador(jogo.jog); jogo.jog.hp = jogo.jog.hp_max
			jogo.jog.ouro = int(args.get("ouro", "10000"))
		"tip_tp":
			var j: Control = jogo.janelas.jan["teleporte"]
			for b in j.find_children("*", "Button", true, false):
				if (b as Button).text.contains("Bairro"):
					var bb := b as Button
					print("btn min ", bb.get_combined_minimum_size(), " size ", bb.size, " sb ", bb.get_theme_stylebox("normal").get_minimum_size(), " font h ", bb.get_theme_font("font").get_height(bb.get_theme_font_size("font_size")))
					for ch in bb.get_children(): print("  ch ", ch.get_combined_minimum_size())
				if (b as Button).text.contains("Rio Amargo"):
					b.mouse_entered.emit()
					var mm := (b as Button).get_global_rect().get_center()
					get_viewport().warp_mouse(mm)
		"tp":
			jogo.cmd("teleportar", [p[2]])
			jogo.janelas.fechar("teleporte")
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
		"skill_area":   # bonecos em volta para o leque acertar e a skill do nível 5 na direção pedida
			var j: Ent = jogo.jog
			j.rec = j.rec_max; j.cds.clear()
			var dir: Vector2 = (p[2] as Vector2).normalized()
			for k in (3 if p.size() > 3 else 0):
				var m: Ent = jogo.sim.criar_mob("cao_de_vala", j.pos + dir.rotated((k - 1) * 0.6) * 2.4, 5)
				if m: m.hp_max = 99999.0; m.hp = m.hp_max
			Jogador.cmd_skill(jogo.sim, j, Jogador.slot_auto(j), -1, j.pos + dir * 3.0)
		"popup": _popup(p[2])
		"item_tip":
			var it: Dictionary = Itens.novo("anel_prego_caixao" if p[2] == "anel" else "lanca_procissao")
			it["raridade"] = "lendario" if p[2] == "lendario" else ("raro" if p[2] == "anel" else "comum")
			it["opcoes"] = [] if p[2] != "lendario" else [{"tipo": "dano_plano", "valor": 35}, {"tipo": "atributo", "valor": 25, "attr": "FOR"}, {"tipo": "excelente_golpe", "valor": 0.12}]
			jogo.hud.mostrar_tip_item(it, jogo.janelas.tip_item(it, "mochila"))
		"nada": pass
		"fim": get_tree().quit()

## Equipamento modesto no corpo, peças melhores na mochila, materiais para guardar e alguns itens na arca.
func _preparar_menu() -> void:
	var j: Ent = jogo.jog
	j.nivel = int(args.get("nivel", "14")); j.ouro = 4812
	var rng := RandomNumberGenerator.new(); rng.seed = 7
	var por_slot := {}
	for id in Defs.ITENS:
		var d: Dictionary = Defs.ITENS[id]
		if d.get("slot") == null or str(d.get("raridade", "rolada")) != "rolada": continue
		if Itens.pode_usar(Itens.novo(id), j) != "": continue
		if Tema.icone_mochila(id) == null and Tema.icone_item(id, true).is_empty(): continue
		if not por_slot.has(str(d["slot"])): por_slot[str(d["slot"])] = []
		por_slot[str(d["slot"])].append(id)
	j.inv.clear(); j.equip.clear(); j.armazem.clear()
	var vestir := {"arma": "arma", "peito": "peito", "cabeca": "cabeca", "botas": "botas", "anel": "anel1", "luvas": "luvas"}
	for s in por_slot:
		var ids: Array = por_slot[s]
		ids.sort_custom(func(a, b): return int(Defs.ITENS[a].get("nivel", 1)) < int(Defs.ITENS[b].get("nivel", 1)))
		if vestir.has(s): j.equip[vestir[s]] = Itens.gerar_equip(ids[0], rng, "comum", 1)
		if s in ["arma", "peito", "calcas", "anel", "amuleto"]:
			Itens.guardar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, Itens.gerar_equip(ids[-1], rng, "raro", 2))
	for id in Defs.ITENS:
		var c := Itens.categoria(Itens.novo(id))
		if c in ["material", "joia"] and j.inv.size() < 14: Itens.guardar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, Itens.novo(id, 3 if c == "material" else 1))
		if c == "consumivel" and j.armazem.size() < 6: Itens.guardar(j.armazem, Itens.ARMAZEM_W, Itens.ARMAZEM_H, Itens.novo(id, 5))
	Regras.recalc_jogador(j)
	jogo.janelas.atualizar()

func _popup(qual: String) -> void:
	var h = jogo.hud
	match qual:
		"convite": h.convite_mostrar({"de": "Odete"})
		"troca": h.troca_pedido_mostrar({"de": "Anselmo"})
		"inspecao":
			h.inspecao_mostrar({"nome": "Isaura Valente", "classe": "humano", "nivel": 34, "hp": 812, "hp_max": 940,
				"stats": {"FOR": 70, "AGI": 120, "VIT": 60, "ESP": 20},
				"equip": {"arma": {"nome": "Escopeta do Silo", "raridade": "rara"}, "peito": {"nome": "Sobretudo de Lona", "raridade": "magica"}}})
		"menu_jogador": h.menu_jogador(jogo.jog.id, Vector2(560, 300))
		"ajuda": h.mostrar_ajuda()
		"texto": jogo.janelas.texto("Carta de Simão", "Se esta carta chegou até você, a areia ainda não me engoliu de todo.\n\nNo Silo São Lázaro há uma porta que não abre por chave. Abre por nome.")
		"limpar":
			for n in ["convite_box", "troca_box", "inspecao_box"]:
				var c = h.get(n)
				if c != null and is_instance_valid(c): c.queue_free()
			h.fechar_menu_jogador()
			if h.ajuda_ui: h.ajuda_ui.visible = false
			jogo.janelas.fechar_texto()

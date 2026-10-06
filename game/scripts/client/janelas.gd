extends CanvasLayer
## Janelas: mochila e equipamento, personagem, habilidades, diário de missões, diálogo, loja, forja, armazém,
## treinador, textos de lore e menu. Itens se movem MU-style: clique pega, clique solta (ou arraste).

var game
var raiz := Control.new()
var jan := {}                 # nome -> PanelContainer
var corpo := {}               # nome -> Control de conteúdo
var servico_d := {}
var dialogo_d := {}
var dialogo_t := 0.0
var mao := {}                 # item na mão: {it, de, slot}
var mao_ui: Control
var alvos_soltar: Array = []  # Controls que aceitam item (grades e slots)
var missao_sel := ""
var _sel_aba := "ativas"

const CEL := 30
const POS_EQUIP := {
	"arma": Rect2(8, 8, 62, 126), "cabeca": Rect2(80, 8, 52, 52), "peito": Rect2(80, 66, 52, 68),
	"amuleto": Rect2(250, 8, 52, 52), "luvas": Rect2(250, 66, 52, 52), "segunda_mao": Rect2(312, 8, 62, 126),
	"anel1": Rect2(8, 146, 40, 40), "anel2": Rect2(54, 146, 40, 40), "calcas": Rect2(140, 140, 52, 52), "botas": Rect2(250, 140, 52, 52)}

func _ready() -> void:
	layer = 20
	raiz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = Tema.tema_janelas()
	add_child(raiz)
	var cl := CanvasLayer.new(); cl.layer = 25; add_child(cl)
	mao_ui = Desenho.new()
	mao_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mao_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mao_ui.desenhar = _desenhar_mao
	cl.add_child(mao_ui)

func _jog() -> Ent: return game.jog
func _sim() -> WorldSim: return game.sim

class Desenho extends Control:
	var desenhar: Callable
	var entrada: Callable
	var dados := {}
	func _draw() -> void:
		if desenhar.is_valid(): desenhar.call(self)
	func _gui_input(ev: InputEvent) -> void:
		if entrada.is_valid(): entrada.call(self, ev)

# =================================================================== base das janelas
func _janela(nome: String, titulo: String, tam: Vector2, onde: String) -> VBoxContainer:
	if game.hud.mapa_ui and game.hud.mapa_ui.visible: game.hud.mapa_ui.visible = false
	if jan.has(nome):
		jan[nome].visible = true
		return corpo[nome]
	var p := PanelContainer.new()
	var sb := Tema.caixa(Color(0.065, 0.052, 0.045, 0.96), Color(0.42, 0.34, 0.2), 2, 3)
	sb.set_content_margin_all(12)
	p.add_theme_stylebox_override("panel", sb)
	p.custom_minimum_size = tam
	p.mouse_filter = Control.MOUSE_FILTER_STOP
	match onde:
		"direita":
			p.set_anchors_preset(Control.PRESET_TOP_RIGHT)
			p.offset_left = -tam.x - 14; p.offset_right = -14; p.offset_top = 56; p.offset_bottom = 56 + tam.y
		"esquerda":
			p.set_anchors_preset(Control.PRESET_TOP_LEFT)
			p.offset_left = 14; p.offset_right = 14 + tam.x; p.offset_top = 56; p.offset_bottom = 56 + tam.y
		"centro":
			p.set_anchors_preset(Control.PRESET_CENTER)
			p.offset_left = -tam.x * 0.5; p.offset_right = tam.x * 0.5; p.offset_top = -tam.y * 0.5 - 40; p.offset_bottom = tam.y * 0.5 - 40
		"baixo":
			p.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
			p.offset_left = -tam.x * 0.5; p.offset_right = tam.x * 0.5; p.offset_top = -tam.y - 168; p.offset_bottom = -168
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	p.add_child(v)
	var topo := HBoxContainer.new()
	var tl := Tema.rotulo(titulo, 20, Color("#e0c890"), Tema.FONTE_TITULO, 3)
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tl.name = "Titulo"
	topo.add_child(tl)
	var x := Button.new(); x.text = "✕"; x.custom_minimum_size = Vector2(26, 24)
	x.add_theme_font_override("font", Tema.FONTE_TEXTO)
	x.pressed.connect(func(): fechar(nome))
	topo.add_child(x)
	v.add_child(topo)
	var linha := ColorRect.new(); linha.color = Color(0.42, 0.34, 0.2, 0.6); linha.custom_minimum_size.y = 1
	v.add_child(linha)
	var c := VBoxContainer.new()
	c.add_theme_constant_override("separation", 8)
	c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(c)
	raiz.add_child(p)
	jan[nome] = p; corpo[nome] = c
	game.audio.tocar("ui/abrir_janela", null, -6.0)
	return c

func _titulo(nome: String, txt: String) -> void:
	if jan.has(nome): jan[nome].get_child(0).get_child(0).get_node("Titulo").text = txt

func aberta(nome: String) -> bool:
	return jan.has(nome) and jan[nome].visible

func alternar(nome: String) -> void:
	if aberta(nome): fechar(nome); return
	match nome:
		"inventario": abrir_inventario()
		"personagem": abrir_personagem()
		"habilidades": abrir_habilidades()
		"missoes": abrir_missoes()
		"menu": abrir_menu()

func fechar(nome: String) -> void:
	if not jan.has(nome): return
	if jan[nome].visible: game.audio.tocar("ui/fechar_janela", null, -6.0)
	jan[nome].visible = false
	game.hud.esconder_tip()
	match nome:
		"dialogo":
			_jog().aux.erase("dialogo"); dialogo_d = {}; game.cmd("fechar", ["dialogo"])
		"servico":
			_jog().aux.erase("servico"); servico_d = {}; game.cmd("fechar", ["servico"])
			if aberta("armazem"): fechar("armazem")
		"armazem":
			if not servico_d.is_empty() and servico_d.get("tipo") == "armazem": fechar("servico")
		"inventario":
			if not mao.is_empty(): _devolver_mao()

func fechar_tudo() -> bool:
	var algum := false
	if not mao.is_empty(): _devolver_mao(); return true
	for n in jan.keys():
		if jan[n].visible: fechar(n); algum = true
	if game.hud.mapa_ui and game.hud.mapa_ui.visible: game.hud.mapa_ui.visible = false; algum = true
	if game.hud.ajuda_ui and game.hud.ajuda_ui.visible: game.hud.ajuda_ui.visible = false; algum = true
	return algum

func _limpar(c: Control) -> void:
	for f in c.get_children(): c.remove_child(f); f.queue_free()

func atualizar() -> void:
	if aberta("inventario"): _atualizar_inventario()
	if aberta("personagem"): abrir_personagem()
	if aberta("servico") and servico_d.get("tipo") == "ferreiro": _corpo_ferreiro()
	for n in ["inventario", "armazem"]:
		if jan.has(n): _redesenhar(jan[n])

func _redesenhar(n: Node) -> void:
	if n is CanvasItem: n.queue_redraw()
	for c in n.get_children(): _redesenhar(c)

# =================================================================== tooltip de item
func tip_item(it: Dictionary, contexto := "") -> String:
	var d := Itens.defn(it["id"])
	var j := _jog()
	var rar: String = it.get("raridade", "comum")
	var cor := Defs.cor_raridade(rar).to_html(false)
	var s := "[font_size=17][color=#%s]%s[/color][/font_size]\n" % [cor, Itens.nome(it)]
	var cat := Itens.categoria(it)
	var sub: Array = []
	var slot := Itens.slot_de(it)
	if slot != "": sub.append(Itens.NOME_SLOT.get(slot if slot != "anel" else "anel1", slot))
	else: sub.append({"consumivel": "Consumível", "material": "Material", "joia": "Joia", "missao": "Item de missão", "leitura": "Escrito", "chave": "Chave", "bau": "Baú"}.get(cat, cat.capitalize()))
	if slot != "" or rar != "comum": sub.append(Defs.nome_raridade(rar))
	s += "[i][color=#a89f8c]%s[/color][/i]\n" % " · ".join(sub)
	if slot == "arma":
		var dn := Itens.dano_arma(it)
		s += "Dano [b]%d–%d[/b]" % [roundi(dn[0]), roundi(dn[1])]
		if d.has("intervalo"): s += "   ·   %.2f ataques/s" % (1.0 / float(d["intervalo"]))
		s += "\n"
		if int(d.get("maos", 1)) == 2: s += "[color=#a89f8c]Duas mãos[/color]\n"
	if d.has("defesa") and slot != "arma":
		s += "Defesa [b]%d[/b]\n" % roundi(float(d["defesa"]) * (1.0 + 0.08 * int(it.get("refino", 0))))
	if d.has("bloqueio"): s += "Bloqueio %d%%\n" % roundi(float(d["bloqueio"]) * 100.0)
	for src in ["atributos", "atributo_base"]:
		var at = d.get(src)
		if at is Dictionary:
			for k in at: s += "[color=#9cc8ff]+%d %s[/color]\n" % [int(at[k]), Itens.ATTR.get(k, str(k).to_upper())]
	for o in it.get("opcoes", []):
		var exc: bool = str(o["tipo"]).begins_with("excelente")
		s += "[color=%s]%s[/color]\n" % ["#9cff3a" if exc else "#9cc8ff", Itens.texto_opcao(o)]
	var ef = d.get("efeito")
	if ef is String: s += "[color=#e0b84a]%s[/color]\n" % ef
	elif ef is Dictionary:
		var partes: Array = []
		if ef.has("cura_hp"): partes.append("Recupera %d de vida%s" % [int(ef["cura_hp"]), (" em %ds" % int(ef["duracao_s"])) if ef.has("duracao_s") else ""])
		if ef.has("cura_hp_pct"): partes.append("Recupera %d%% da vida" % int(ef["cura_hp_pct"]))
		if ef.has("recurso_pct"): partes.append("Recupera %d%% do recurso" % roundi(float(ef["recurso_pct"]) * 100.0))
		if ef.has("remove"): partes.append("Cura " + ", ".join(ef["remove"]))
		if ef.has("teleporta"): partes.append("Leva de volta ao acampamento")
		if ef.has("municao"): partes.append("Munição para a escopeta")
		if ef.has("arremesso"): partes.append("Arremessa e explode em área")
		if ef.has("buff"): partes.append("Fortalece por um tempo")
		if ef.has("repele"): partes.append("Afasta %s" % str(ef["repele"]).replace("_", " "))
		for p in partes: s += "[color=#c8f08a]%s[/color]\n" % p
	if d.has("conjunto"):
		var cj: Dictionary = {}
		for c in Defs.ITENS_DOC.get("conjuntos", []):
			if c is Dictionary and c.get("id") == d["conjunto"]: cj = c
		s += "[color=#3ad0a0]Conjunto: %s[/color]\n" % cj.get("nome", str(d["conjunto"]).replace("_", " ").capitalize())
	var lore: String = d.get("lore", d.get("descricao", ""))
	if lore != "": s += "[i][color=#b8ab90]%s[/color][/i]\n" % lore
	var req := Itens.pode_usar(it, j) if slot != "" else ""
	var nv := int(d.get("nivel", 1))
	if slot != "" and nv > 1: s += "[color=%s]Requer nível %d[/color]\n" % ["#ff6a4a" if j.nivel < nv else "#a89f8c", nv]
	if req != "" and not req.begins_with("Requer"): s += "[color=#ff6a4a]%s[/color]\n" % req
	var cl = d.get("classes")
	if cl is Array and cl.size() > 0 and cl.size() < 6:
		s += "[color=#8a8070]%s[/color]\n" % ", ".join(cl.map(func(x): return {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}.get(x, x)))
	match contexto:
		"loja_compra": s += "[color=#e0b84a]Preço: %d de ouro[/color]" % Itens.preco(it)
		"mochila":
			if servico_d.get("tipo") == "loja":
				var v := Itens.preco_venda(it)
				s += ("[color=#e0b84a]Vende por %d · botão direito vende[/color]" % v) if v > 0 else "[color=#8a8070]Não se vende[/color]"
			elif servico_d.get("tipo") == "armazem": s += "[color=#8a8070]Botão direito guarda no armazém[/color]"
			elif slot != "": s += "[color=#8a8070]Botão direito equipa[/color]"
			elif cat in ["consumivel", "leitura"] or d.get("tipo_missao") == "leitura": s += "[color=#8a8070]Botão direito usa[/color]"
		"equip": s += "[color=#8a8070]Botão direito tira[/color]"
		"armazem": s += "[color=#8a8070]Botão direito leva para a mochila[/color]"
	return s.strip_edges()

func _desenhar_icone(c: CanvasItem, it: Dictionary, r: Rect2, mod := Color.WHITE) -> void:
	var tm := Tema.icone_mochila(it["id"])
	var g := Itens.grade(it)
	if tm != null and absf(float(tm.get_width()) / tm.get_height() - float(g.x) / g.y) < 0.2:
		var esc := minf(r.size.x / tm.get_width(), r.size.y / tm.get_height())
		var sz := Vector2(tm.get_size()) * esc
		c.draw_texture_rect(tm, Rect2(r.get_center() - sz * 0.5, sz), false, mod)
		return
	var ic := Tema.icone_item(it["id"], true)
	if ic.size() == 2:
		var rr: Rect2 = ic[1]
		var esc2 := minf(r.size.x / rr.size.x, r.size.y / rr.size.y)
		var sz2 := rr.size * esc2
		c.draw_texture_rect_region(ic[0], Rect2(r.get_center() - sz2 * 0.5, sz2), rr, mod)
	else:
		c.draw_rect(r.grow(-4), Defs.cor_raridade(it.get("raridade", "comum")).darkened(0.5))

# =================================================================== grade (mochila e armazém)
func _grade(onde: String) -> Desenho:
	var g := Desenho.new()
	var W := Itens.MOCHILA_W if onde == "mochila" else Itens.ARMAZEM_W
	var H := Itens.MOCHILA_H if onde == "mochila" else Itens.ARMAZEM_H
	g.custom_minimum_size = Vector2(W * CEL, H * CEL)
	g.mouse_filter = Control.MOUSE_FILTER_STOP
	g.dados = {"onde": onde, "W": W, "H": H, "hover": -1, "cel": Vector2i(-1, -1)}
	g.desenhar = _desenhar_grade
	g.entrada = _entrada_grade
	g.mouse_exited.connect(func(): g.dados["hover"] = -1; g.dados["cel"] = Vector2i(-1, -1); game.hud.esconder_tip(); g.queue_redraw())
	alvos_soltar.append(g)
	return g

func _lista(onde: String) -> Array:
	return _jog().inv if onde == "mochila" else _jog().armazem

func _desenhar_grade(g: Desenho) -> void:
	var W: int = g.dados["W"]; var H: int = g.dados["H"]
	var lista := _lista(g.dados["onde"])
	g.draw_rect(Rect2(Vector2.ZERO, g.size), Color(0.03, 0.025, 0.02, 0.9))
	for y in H:
		for x in W:
			var r := Rect2(x * CEL + 1, y * CEL + 1, CEL - 2, CEL - 2)
			g.draw_rect(r, Color(0.075, 0.065, 0.055))
			g.draw_rect(r, Color(0.16, 0.13, 0.1), false, 1.0)
	for it in lista:
		if not mao.is_empty() and mao["it"] == it: continue
		var gr := Itens.grade(it)
		var r := Rect2(int(it["x"]) * CEL + 1, int(it["y"]) * CEL + 1, gr.x * CEL - 2, gr.y * CEL - 2)
		var cor := Defs.cor_raridade(it.get("raridade", "comum"))
		var bg := Color(cor.r, cor.g, cor.b, 0.13 if it.get("raridade", "comum") != "comum" else 0.05)
		if Itens.equipavel(it) and Itens.pode_usar(it, _jog()) != "": bg = Color(0.6, 0.08, 0.05, 0.3)
		if int(it["uid"]) == g.dados["hover"]: bg = bg.lightened(0.15); bg.a += 0.12
		g.draw_rect(r, bg)
		if it.get("raridade", "comum") != "comum": g.draw_rect(r, Color(cor.r, cor.g, cor.b, 0.45), false, 1.0)
		_desenhar_icone(g, it, r.grow(-1))
		if int(it.get("qtd", 1)) > 1:
			var q := str(int(it["qtd"]))
			var p := r.end - Vector2(2, 3)
			var w := Tema.FONTE_PIXEL.get_string_size(q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
			g.draw_string_outline(Tema.FONTE_PIXEL, p - Vector2(w, 0), q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 3, Color(0, 0, 0))
			g.draw_string(Tema.FONTE_PIXEL, p - Vector2(w, 0), q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#f6ead0"))
	# prévia de onde o item da mão cai
	if not mao.is_empty() and g.dados["cel"].x >= 0:
		var gr2 := Itens.grade(mao["it"])
		var c0 := _canto_mao(g)
		var ok := Itens.cabe_em(lista, W, H, mao["it"], c0.x, c0.y, int(mao["it"]["uid"]))
		g.draw_rect(Rect2(c0.x * CEL, c0.y * CEL, gr2.x * CEL, gr2.y * CEL), Color(0.3, 0.8, 0.3, 0.25) if ok else Color(0.9, 0.2, 0.15, 0.25))

func _canto_mao(g: Desenho) -> Vector2i:
	var gr := Itens.grade(mao["it"])
	var lp := g.get_local_mouse_position()
	return Vector2i(clampi(roundi(lp.x / CEL - gr.x * 0.5), 0, int(g.dados["W"]) - gr.x), clampi(roundi(lp.y / CEL - gr.y * 0.5), 0, int(g.dados["H"]) - gr.y))

func _item_em(lista: Array, c: Vector2i) -> Dictionary:
	for it in lista:
		var gr := Itens.grade(it)
		if c.x >= int(it["x"]) and c.x < int(it["x"]) + gr.x and c.y >= int(it["y"]) and c.y < int(it["y"]) + gr.y: return it
	return {}

func _entrada_grade(g: Desenho, ev: InputEvent) -> void:
	var onde: String = g.dados["onde"]
	var lista := _lista(onde)
	if ev is InputEventMouseMotion:
		var c := Vector2i(floori(ev.position.x / CEL), floori(ev.position.y / CEL))
		g.dados["cel"] = c
		var it := _item_em(lista, c)
		var uid := int(it.get("uid", -1))
		if uid != g.dados["hover"]:
			g.dados["hover"] = uid
			if uid >= 0 and mao.is_empty(): game.hud.mostrar_tip(tip_item(it, onde))
			else: game.hud.esconder_tip()
		g.queue_redraw()
	elif ev is InputEventMouseButton and ev.pressed:
		var c2 := Vector2i(floori(ev.position.x / CEL), floori(ev.position.y / CEL))
		var it2 := _item_em(lista, c2)
		if ev.button_index == MOUSE_BUTTON_LEFT:
			if mao.is_empty():
				if not it2.is_empty():
					mao = {"it": it2, "de": onde, "pos": ev.global_position}
					game.hud.esconder_tip()
					game.audio.tocar("ui/pegar_item", null, -8.0)
			else:
				_soltar_em_grade(g)
		elif ev.button_index == MOUSE_BUTTON_RIGHT and mao.is_empty() and not it2.is_empty():
			_acao_direita(it2, onde)
		g.accept_event()
		_redesenhar_tudo()
	elif ev is InputEventMouseButton and not ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT and not mao.is_empty():
		# arrastou e soltou: resolve onde caiu
		if ev.global_position.distance_to(mao.get("pos", ev.global_position)) > 10.0:
			soltar_mao_em(ev.global_position)
		g.accept_event()

func _soltar_em_grade(g: Desenho) -> void:
	var onde: String = g.dados["onde"]
	var c0 := _canto_mao(g)
	var it: Dictionary = mao["it"]
	var j := _jog()
	if mao["de"] == "equip":
		game.cmd("desequipar", [mao["slot"], c0.x, c0.y, onde])
	else:
		game.cmd("mover_item", [int(it["uid"]), mao["de"], onde, c0.x, c0.y])
	game.audio.tocar("ui/soltar_item", null, -8.0)
	mao = {}

func soltar_mao_em(gp: Vector2) -> void:
	if mao.is_empty(): return
	for a in alvos_soltar:
		if not is_instance_valid(a) or not a.is_visible_in_tree(): continue
		if a.get_global_rect().has_point(gp):
			if a.dados.has("slot"): _soltar_em_slot(a.dados["slot"])
			else: _soltar_em_grade(a)
			_redesenhar_tudo()
			return
	# fora de qualquer janela: joga no chão (só da mochila)
	var dentro_janela := false
	for n in jan:
		if jan[n].visible and jan[n].get_global_rect().has_point(gp): dentro_janela = true
	if not dentro_janela and mao["de"] == "mochila":
		game.cmd("soltar_item", [int(mao["it"]["uid"])])
	mao = {}
	_redesenhar_tudo()

func soltar_no_mundo() -> void:
	soltar_mao_em(Vector2(-99999, -99999))

func mao_ativa() -> bool:
	return not mao.is_empty()

func _devolver_mao() -> void:
	mao = {}
	_redesenhar_tudo()

func _redesenhar_tudo() -> void:
	for n in jan:
		if jan[n].visible: _redesenhar(jan[n])
	mao_ui.queue_redraw()

func _acao_direita(it: Dictionary, onde: String) -> void:
	var j := _jog()
	var uid := int(it["uid"])
	if onde == "armazem":
		var p := Itens.achar_lugar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
		if p.x >= 0: game.cmd("mover_item", [uid, "armazem", "mochila", p.x, p.y])
		else: game.hud.aviso("Mochila cheia.")
		return
	match servico_d.get("tipo", ""):
		"loja": game.cmd("vender", [uid]); return
		"armazem":
			var p2 := Itens.achar_lugar(j.armazem, Itens.ARMAZEM_W, Itens.ARMAZEM_H, it)
			if p2.x >= 0: game.cmd("mover_item", [uid, "mochila", "armazem", p2.x, p2.y])
			else: game.hud.aviso("Armazém cheio.")
			return
	game.cmd("usar_item", [uid])

func _desenhar_mao(c: Desenho) -> void:
	if mao.is_empty(): return
	var gr := Itens.grade(mao["it"])
	var mp := c.get_local_mouse_position()
	var r := Rect2(mp - Vector2(gr.x * CEL, gr.y * CEL) * 0.5, Vector2(gr.x * CEL, gr.y * CEL))
	c.draw_rect(r, Color(0, 0, 0, 0.35))
	_desenhar_icone(c, mao["it"], r, Color(1, 1, 1, 0.92))

func _process(dt: float) -> void:
	if not mao.is_empty(): mao_ui.queue_redraw()
	if dialogo_t < 1.0 and aberta("dialogo"):
		dialogo_t += dt * 2.5
		var rl: RichTextLabel = jan["dialogo"].find_child("Fala", true, false)
		if rl: rl.visible_ratio = clampf(dialogo_t, 0.0, 1.0)
	# serviço fecha se o jogador se afastar do NPC
	if not servico_d.is_empty() and game.jog:
		var npc: Ent = game.sim.ents.get(int(servico_d.get("npc", -1)))
		if npc == null or npc.pos.distance_to(game.jog.pos) > 6.0: fechar("servico")
	if not dialogo_d.is_empty() and game.jog:
		var npc2: Ent = game.sim.ents.get(int(dialogo_d.get("npc", -1)))
		if npc2 == null or npc2.pos.distance_to(game.jog.pos) > 6.0: fechar("dialogo")

func _input(ev: InputEvent) -> void:
	# números escolhem a opção do diálogo
	if aberta("dialogo") and ev is InputEventKey and ev.pressed and not ev.echo:
		var k: int = ev.keycode - KEY_1
		if k >= 0 and k < 9 and k < dialogo_d.get("opcoes", []).size():
			_escolher(k); get_viewport().set_input_as_handled()

# =================================================================== equipamento
func _slot_equip(slot: String) -> Desenho:
	var s := Desenho.new()
	var r: Rect2 = POS_EQUIP[slot]
	s.position = r.position; s.size = r.size
	s.mouse_filter = Control.MOUSE_FILTER_STOP
	s.dados = {"slot": slot, "hover": false}
	s.desenhar = func(c: Desenho):
		var it: Dictionary = _jog().equip.get(slot, {})
		var rr := Rect2(Vector2.ZERO, c.size)
		c.draw_rect(rr, Color(0.03, 0.025, 0.02, 0.95))
		var borda := Color(0.42, 0.34, 0.2) if not c.dados["hover"] else Color(0.8, 0.65, 0.35)
		if not mao.is_empty() and mao["de"] != "equip" and Jogador.slot_para(_jog(), mao["it"]) .begins_with(slot.substr(0, 4)):
			borda = Color(0.4, 0.85, 0.35) if Itens.pode_usar(mao["it"], _jog()) == "" else Color(0.9, 0.25, 0.2)
		if not it.is_empty() and not (not mao.is_empty() and mao["it"] == it):
			var cor := Defs.cor_raridade(it.get("raridade", "comum"))
			if it.get("raridade", "comum") != "comum": c.draw_rect(rr, Color(cor.r, cor.g, cor.b, 0.12))
			_desenhar_icone(c, it, rr.grow(-4))
			if int(it.get("refino", 0)) > 0:
				c.draw_string_outline(Tema.FONTE_PIXEL, Vector2(3, 10), "+%d" % int(it["refino"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 3, Color.BLACK)
				c.draw_string(Tema.FONTE_PIXEL, Vector2(3, 10), "+%d" % int(it["refino"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#e0b84a"))
		else:
			var nome: String = Itens.NOME_SLOT[slot].to_upper()
			var w := Tema.FONTE_PIXEL.get_string_size(nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 7).x
			c.draw_string(Tema.FONTE_PIXEL, Vector2((c.size.x - w) * 0.5, c.size.y * 0.5 + 3), nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 7, Color(0.42, 0.37, 0.3))
		c.draw_rect(rr, borda, false, 1.5)
	s.entrada = func(c: Desenho, ev: InputEvent):
		var it: Dictionary = _jog().equip.get(slot, {})
		if ev is InputEventMouseMotion:
			if not c.dados["hover"]:
				c.dados["hover"] = true; c.queue_redraw()
				if not it.is_empty() and mao.is_empty(): game.hud.mostrar_tip(tip_item(it, "equip"))
		elif ev is InputEventMouseButton and ev.pressed:
			if ev.button_index == MOUSE_BUTTON_LEFT:
				if mao.is_empty():
					if not it.is_empty(): mao = {"it": it, "de": "equip", "slot": slot, "pos": ev.global_position}; game.hud.esconder_tip()
				else: _soltar_em_slot(slot)
			elif ev.button_index == MOUSE_BUTTON_RIGHT and not it.is_empty() and mao.is_empty():
				game.cmd("desequipar", [slot])
			c.accept_event()
			_redesenhar_tudo()
		elif ev is InputEventMouseButton and not ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT and not mao.is_empty():
			if ev.global_position.distance_to(mao.get("pos", ev.global_position)) > 10.0: soltar_mao_em(ev.global_position)
			c.accept_event()
	s.mouse_exited.connect(func(): s.dados["hover"] = false; s.queue_redraw(); game.hud.esconder_tip())
	alvos_soltar.append(s)
	return s

func _soltar_em_slot(slot: String) -> void:
	if mao.is_empty(): return
	var j := _jog()
	if mao["de"] == "mochila":
		var sd := Itens.slot_de(mao["it"])
		var alvo := slot
		if sd == "anel" and slot in ["anel1", "anel2"]: alvo = slot
		elif sd != slot: game.hud.aviso("Não vai aí."); mao = {}; return
		game.cmd("equipar", [int(mao["it"]["uid"]), alvo])
	mao = {}

# =================================================================== mochila + equipamento
func abrir_inventario() -> void:
	var c := _janela("inventario", "EQUIPAMENTO", Vector2(400, 590), "direita")
	if c.get_child_count() > 0: _atualizar_inventario(); return
	var eq := Desenho.new()
	eq.custom_minimum_size = Vector2(376, 192)
	eq.desenhar = func(cc: Desenho):
		# figura do personagem no meio
		var j := _jog()
		var meta: Dictionary = Defs.SPR.get(j.classe, {})
		if meta.is_empty(): return
		var tex := Tema.tex(meta["anims"]["idle"]["file"])
		var fr: Array = meta["frame"]; var anc: Array = meta["anchor"]
		var f := int(Time.get_ticks_msec() / 160) % int(meta["anims"]["idle"]["frames"])
		cc.draw_rect(Rect2(140, 6, 104, 130), Color(0.03, 0.025, 0.02, 0.5))
		var esc := 1.15
		var pe := Vector2(192, 128)
		if tex: cc.draw_texture_rect_region(tex, Rect2(pe - Vector2(anc[0], anc[1]) * esc, Vector2(fr[0], fr[1]) * esc), Rect2(f * fr[0], 0, fr[0], fr[1]))
		cc.queue_redraw()
	for slot in POS_EQUIP: eq.add_child(_slot_equip(slot))
	c.add_child(eq)
	# atributos
	var at := GridContainer.new(); at.columns = 4; at.name = "Atributos"
	at.add_theme_constant_override("h_separation", 6)
	c.add_child(at)
	var der := Tema.rotulo("", 13, Color("#c8bfa8")); der.name = "Derivados"
	c.add_child(der)
	var tm := Tema.rotulo("MOCHILA", 15, Color("#e0c890"), Tema.FONTE_TITULO, 2)
	tm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(tm)
	var cg := CenterContainer.new(); cg.add_child(_grade("mochila")); c.add_child(cg)
	var rod := HBoxContainer.new(); rod.name = "Rodape"
	var ouro := Tema.rotulo("", 15, Tema.COR_OURO, Tema.FONTE_TITULO, 2); ouro.name = "Ouro"
	ouro.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rod.add_child(ouro)
	var dica := Tema.rotulo("arraste para fora para jogar no chão", 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	rod.add_child(dica)
	c.add_child(rod)
	_atualizar_inventario()

func _atualizar_inventario() -> void:
	if not jan.has("inventario"): return
	var c: Control = corpo["inventario"]
	var j := _jog()
	var at: GridContainer = c.get_node("Atributos")
	_limpar(at)
	for k in ["FOR", "AGI", "VIT", "ESP"]:
		var b := PanelContainer.new()
		var sb := Tema.caixa(Color(0.09, 0.075, 0.06), Color(0.3, 0.25, 0.17), 1, 2); sb.set_content_margin_all(4); sb.shadow_size = 0
		b.add_theme_stylebox_override("panel", sb)
		b.custom_minimum_size = Vector2(88, 44)
		var h := HBoxContainer.new()
		var v := VBoxContainer.new(); v.add_theme_constant_override("separation", -2)
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var l1 := Tema.rotulo(k, 10, Color("#a89f8c"), Tema.FONTE_PIXEL); l1.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		var bonus := float(j.aux.get("bonus", {}).get(k, 0.0))
		var l2 := Tema.rotulo("%d" % roundi(float(j.stats[k]) + bonus), 18, Color("#9cc8ff") if bonus > 0 else Color("#f0dca0"), Tema.FONTE_TITULO); l2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(l1); v.add_child(l2); h.add_child(v)
		if j.pontos > 0:
			var mais := Button.new(); mais.text = "+"; mais.custom_minimum_size = Vector2(22, 22)
			mais.pressed.connect(func(): game.cmd("ponto", [k]); game.audio.tocar("ui/clique", null, -6.0))
			h.add_child(mais)
		b.add_child(h)
		at.add_child(b)
	var der: Label = c.get_node("Derivados")
	var txt := "Dano %d–%d    Defesa %d    Crítico %d%%" % [roundi(j.dano_min), roundi(j.dano_max), roundi(j.defesa), roundi(j.critico * 100.0)]
	if j.pontos > 0: txt += "\n[%d pontos para distribuir]" % j.pontos
	der.text = txt
	der.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	(c.get_node("Rodape/Ouro") as Label).text = "◉ %d ouro" % j.ouro + (("    %d balas" % j.municao) if j.classe == "humano" else "")
	_redesenhar(jan["inventario"])

# =================================================================== personagem
func abrir_personagem() -> void:
	var c := _janela("personagem", "PERSONAGEM", Vector2(360, 520), "esquerda")
	_limpar(c)
	var j := _jog()
	var cls: Dictionary = Defs.CLASSES[j.classe]
	var nomes := {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}
	var t1 := Tema.rotulo(j.nome, 24, Color("#f0dca0"), Tema.FONTE_GOTICA, 3); t1.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; c.add_child(t1)
	var t2 := Tema.rotulo("%s de nível %d · %s" % [nomes[j.classe], j.nivel, "Vigília" if j.faccao == "vigilia" else "Arautos do Juízo"], 14, Color("#a89f8c"), Tema.FONTE_ITALICO)
	t2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; c.add_child(t2)
	var xpb := ProgressBar.new(); xpb.max_value = Defs.xp_para_proximo(j.nivel); xpb.value = j.xp; xpb.show_percentage = false; xpb.custom_minimum_size.y = 8
	var sbf := StyleBoxFlat.new(); sbf.bg_color = Color(0.55, 0.75, 0.25); xpb.add_theme_stylebox_override("fill", sbf)
	var sbb := StyleBoxFlat.new(); sbb.bg_color = Color(0.05, 0.04, 0.03); xpb.add_theme_stylebox_override("background", sbb)
	c.add_child(xpb)
	c.add_child(Tema.rotulo("Experiência %d / %d" % [j.xp, Defs.xp_para_proximo(j.nivel)], 12, Color("#8a8070")))
	var desc := {"FOR": "dano corpo a corpo e postura", "AGI": "precisão, esquiva e velocidade", "VIT": "vida e defesa", "ESP": "poder das habilidades e recurso"}
	for k in ["FOR", "AGI", "VIT", "ESP"]:
		var h := HBoxContainer.new()
		var l := Tema.rotulo(k, 15, Color("#e0c890"), Tema.FONTE_TITULO); l.custom_minimum_size.x = 46
		h.add_child(l)
		var bonus := float(j.aux.get("bonus", {}).get(k, 0.0))
		var v := Tema.rotulo("%d" % roundi(float(j.stats[k]) + bonus) + ((" (+%d)" % roundi(bonus)) if bonus > 0 else ""), 15, Color("#f0dca0"), Tema.FONTE_TITULO); v.custom_minimum_size.x = 70
		h.add_child(v)
		var d := Tema.rotulo(desc[k], 12, Color("#8a8070"), Tema.FONTE_ITALICO); d.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		h.add_child(d)
		if j.pontos > 0:
			var b := Button.new(); b.text = "+"; b.custom_minimum_size = Vector2(26, 24)
			b.pressed.connect(func(): game.cmd("ponto", [k]))
			h.add_child(b)
		c.add_child(h)
	if j.pontos > 0: c.add_child(Tema.rotulo("Pontos livres: %d" % j.pontos, 15, Color("#ffd27a"), Tema.FONTE_TITULO))
	var linha := ColorRect.new(); linha.color = Color(0.42, 0.34, 0.2, 0.5); linha.custom_minimum_size.y = 1; c.add_child(linha)
	var g := GridContainer.new(); g.columns = 2
	g.add_theme_constant_override("h_separation", 24)
	var pares := [["Vida", "%d" % roundi(j.hp_max)], [cls["recurso"]["nome"].split(" ")[0], "%d" % roundi(j.rec_max) if j.rec_max > 0 else "a própria vida"],
		["Dano", "%d–%d" % [roundi(j.dano_min), roundi(j.dano_max)]], ["Defesa", "%d" % roundi(j.defesa)],
		["Precisão", "%d" % roundi(j.ar)], ["Esquiva", "%d" % roundi(j.er)],
		["Crítico", "%d%% (×%.1f)" % [roundi(j.critico * 100.0), j.crit_mult]], ["Golpe excelente", "%d%%" % roundi(j.excelente * 100.0)],
		["Ataques por s", "%.2f" % (j.vel_ataque / maxf(0.1, j.intervalo))], ["Roubo de vida", "%d%%" % roundi(j.roubo_vida * 100.0)],
		["Velocidade", "%.1f" % j.vel], ["Abates", "%d" % j.abates.values().reduce(func(a, b): return a + b, 0)]]
	if j.classe == "humano": pares.append_array([["Munição", "%d" % j.municao], ["", ""]])
	for p in pares:
		g.add_child(Tema.rotulo(p[0], 14, Color("#a89f8c")))
		g.add_child(Tema.rotulo(p[1], 14, Color("#e8dfc9"), Tema.FONTE_TITULO))
	c.add_child(g)
	var res: Array = []
	for el in j.res:
		if absf(float(j.res[el])) > 0.001: res.append("%s %+d%%" % [el.capitalize(), roundi(float(j.res[el]) * 100.0)])
	if not res.is_empty(): c.add_child(Tema.rotulo("Resistências: " + ", ".join(res), 13, Color("#9cc8ff")))

# =================================================================== habilidades
func abrir_habilidades() -> void:
	var c := _janela("habilidades", "HABILIDADES", Vector2(460, 560), "esquerda")
	_limpar(c)
	var j := _jog()
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 10)
	sc.add_child(v); c.add_child(sc)
	var i := 0
	for h in Defs.CLASSES[j.classe]["habilidades"]:
		var sk := Defs.skill(j.classe, h["id"])
		var linha := HBoxContainer.new()
		linha.add_theme_constant_override("separation", 10)
		var ic := Tema.icone_skill(j.classe, h["id"], true)
		var tr := TextureRect.new(); tr.custom_minimum_size = Vector2(56, 56)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		if ic.size() == 2:
			var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]; tr.texture = at
		var bloq := j.nivel < int(h["nivel"])
		if bloq: tr.modulate = Color(0.35, 0.35, 0.35)
		tr.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		linha.add_child(tr)
		var col := VBoxContainer.new(); col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.add_theme_constant_override("separation", 2)
		var nm := Tema.rotulo("%d · %s" % [i + 1, sk.get("nome", h["nome"])], 16, Color("#f0dca0") if not bloq else Color("#7d7466"), Tema.FONTE_TITULO)
		col.add_child(nm)
		var meta: Array = []
		if bloq: meta.append("nível %d" % int(h["nivel"]))
		var cst := Jogador.custo(j, h)
		if cst > 0: meta.append(("%d de vida" % roundi(cst)) if j.classe == "cultista" else ("custa %d" % roundi(cst)))
		if h.has("recarga"): meta.append("recarga %.1fs" % float(h["recarga"]))
		if h.has("cargas"): meta.append("%d cargas" % int(h["cargas"]))
		col.add_child(Tema.rotulo(" · ".join(meta), 12, Color("#a89f8c"), Tema.FONTE_ITALICO))
		var d := Tema.rotulo(sk.get("descricao", ""), 13, Color("#d8cfb8"))
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; d.custom_minimum_size.x = 340
		col.add_child(d)
		for ef in sk.get("efeitos", []):
			var e2 := Tema.rotulo("• " + ef, 12, Color("#9cc8ff")); e2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; e2.custom_minimum_size.x = 340
			col.add_child(e2)
		linha.add_child(col)
		v.add_child(linha)
		i += 1
	# passiva da classe (6ª habilidade do livro, ainda sem número de combate)
	for sk2 in Defs.SKILLS.values():
		if sk2.get("classe") == j.classe and not sk2.has("combate"):
			var l := Tema.rotulo("Definitiva: %s (nível %d) — chega numa próxima versão." % [sk2["nome"], int(sk2.get("nivel", 20))], 12, Color("#7d7466"), Tema.FONTE_ITALICO)
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; l.custom_minimum_size.x = 400
			v.add_child(l)

# =================================================================== missões
func abrir_missoes() -> void:
	var c := _janela("missoes", "DIÁRIO", Vector2(640, 520), "centro")
	_limpar(c)
	var j := _jog()
	var abas := HBoxContainer.new()
	for a in [["ativas", "Em andamento"], ["concluidas", "Concluídas"]]:
		var b := Button.new(); b.text = a[1]; b.toggle_mode = true; b.button_pressed = _sel_aba == a[0]
		b.pressed.connect(func(): _sel_aba = a[0]; missao_sel = ""; abrir_missoes())
		abas.add_child(b)
	c.add_child(abas)
	var h := HBoxContainer.new(); h.size_flags_vertical = Control.SIZE_EXPAND_FILL
	h.add_theme_constant_override("separation", 12)
	c.add_child(h)
	var sc := ScrollContainer.new(); sc.custom_minimum_size.x = 220; sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var lista := VBoxContainer.new(); sc.add_child(lista); h.add_child(sc)
	var ids: Array = []
	for mid in j.missoes:
		var st := Missoes.estado(j, mid)
		if (_sel_aba == "ativas" and st == "ativa") or (_sel_aba == "concluidas" and st in ["concluida", "falhou"]): ids.append(mid)
	ids.sort_custom(func(a, b): return int(Missoes.def(a).get("tipo") == "principal") > int(Missoes.def(b).get("tipo") == "principal"))
	if missao_sel == "" and not ids.is_empty(): missao_sel = ids[0]
	if ids.is_empty(): lista.add_child(Tema.rotulo("Nada aqui ainda.", 14, Color("#7d7466"), Tema.FONTE_ITALICO))
	for mid in ids:
		var d := Missoes.def(mid)
		var b := Button.new()
		b.text = ("★ " if d.get("tipo") == "principal" else "") + d.get("titulo", mid) + (" ✓" if Missoes.pronta(j, mid) else "")
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.toggle_mode = true; b.button_pressed = mid == missao_sel
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(func(): missao_sel = mid; abrir_missoes())
		lista.add_child(b)
	var sep := ColorRect.new(); sep.color = Color(0.42, 0.34, 0.2, 0.5); sep.custom_minimum_size.x = 1; h.add_child(sep)
	var det := RichTextLabel.new(); det.bbcode_enabled = true; det.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	det.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	det.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	det.add_theme_font_size_override("normal_font_size", 15)
	h.add_child(det)
	if missao_sel != "":
		var d := Missoes.def(missao_sel)
		var s := "[font_size=22][color=#f0dca0]%s[/color][/font_size]\n" % d.get("titulo", "")
		var doador: String = Defs.NPCS.get(d.get("doador", ""), {}).get("nome", "")
		s += "[i][color=#a89f8c]%s%s[/color][/i]\n\n" % [{"principal": "Principal", "secundaria": "Secundária", "repetivel": "Repetível"}.get(d.get("tipo", ""), "Missão"), (" · de " + doador) if doador != "" else ""]
		s += "%s\n\n" % d.get("descricao", d.get("resumo", ""))
		s += "[b][color=#e0c890]Objetivos[/color][/b]\n"
		var objs: Array = d.get("objetivos", [])
		var etapa := Missoes._etapa_atual(j, missao_sel) if Missoes.estado(j, missao_sel) == "ativa" else 999
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) > etapa: s += "[color=#5d564c]◆ ???[/color]\n"; continue
			var pr := Missoes.progresso(j, missao_sel, i)
			var feito: bool = pr[0] >= pr[1] or Missoes.estado(j, missao_sel) == "concluida"
			var tx := Missoes.texto_objetivo(o) + ((" %d/%d" % pr) if pr[1] > 1 else "")
			s += ("[color=#9cd870]◆ %s ✓[/color]\n" % tx) if feito else ("◆ %s\n" % tx)
		var rec: Dictionary = d.get("recompensas", {})
		var rs: Array = []
		if rec.has("xp"): rs.append("%d de experiência" % int(rec["xp"]))
		if rec.has("ouro"): rs.append("%d de ouro" % int(rec["ouro"]))
		for it in rec.get("itens", []): rs.append(("%d× " % int(it.get("qtd", 1)) if int(it.get("qtd", 1)) > 1 else "") + Defs.ITENS.get(it["id"], {}).get("nome", it["id"]))
		if not rs.is_empty(): s += "\n[b][color=#e0c890]Recompensa[/color][/b]\n[color=#e0b84a]%s[/color]\n" % ", ".join(rs)
		if Missoes.estado(j, missao_sel) == "concluida" and d.get("texto_conclusao", "") != "": s += "\n[i][color=#b8ab90]%s[/color][/i]" % d["texto_conclusao"]
		det.text = s

# =================================================================== diálogo
func dialogo(d: Dictionary) -> void:
	dialogo_d = d
	var c := _janela("dialogo", "", Vector2(680, 250), "baixo")
	_limpar(c)
	_titulo("dialogo", d.get("nome", ""))
	if d.get("titulo", "") != "":
		var st := Tema.rotulo(d["titulo"], 14, Color("#a89f8c"), Tema.FONTE_ITALICO); st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		c.add_child(st)
	var fala := RichTextLabel.new(); fala.name = "Fala"
	fala.bbcode_enabled = true; fala.fit_content = true; fala.scroll_active = false
	fala.add_theme_font_size_override("normal_font_size", 17)
	fala.add_theme_color_override("default_color", Color("#efe4c8"))
	fala.text = d.get("texto", "")
	fala.visible_ratio = 0.0
	dialogo_t = 0.0
	c.add_child(fala)
	var ops := VBoxContainer.new(); ops.add_theme_constant_override("separation", 2)
	var i := 0
	for o in d.get("opcoes", []):
		var b := Button.new()
		var cor := Color("#d8cfb8")
		var pre := ""
		match o.get("tipo", ""):
			"aceitar": cor = Color("#ffd27a"); pre = "[!] "
			"concluir": cor = Color("#c8f08a"); pre = "[?] "
			"servico": cor = Color("#9cc8ff")
			"missao": cor = Color("#ffd27a")
		b.text = "%d.  %s%s" % [i + 1, pre, o["texto"]]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.flat = true
		b.add_theme_font_override("font", Tema.FONTE_TEXTO)
		b.add_theme_font_size_override("font_size", 16)
		b.add_theme_color_override("font_color", cor)
		b.add_theme_color_override("font_hover_color", cor.lightened(0.35))
		var idx := i
		b.pressed.connect(func(): _escolher(idx))
		ops.add_child(b)
		i += 1
	c.add_child(ops)
	jan["dialogo"].reset_size()
	var p: PanelContainer = jan["dialogo"]
	p.offset_top = p.offset_bottom - p.get_combined_minimum_size().y

func _escolher(i: int) -> void:
	if dialogo_t < 1.0:
		dialogo_t = 1.0; return
	game.audio.tocar("ui/clique", null, -6.0)
	game.cmd("escolher", [i])

# =================================================================== serviços
func servico(d: Dictionary) -> void:
	servico_d = d.duplicate()
	servico_d["npc"] = d.get("npc", -1)
	if aberta("dialogo"): jan["dialogo"].visible = false
	match d["tipo"]:
		"loja": _abrir_loja(d)
		"ferreiro":
			_janela("servico", d.get("titulo", "Forja"), Vector2(420, 480), "esquerda")
			_titulo("servico", d.get("titulo", "Forja"))
			_corpo_ferreiro()
			abrir_inventario()
		"armazem": _abrir_armazem(d)
		"treinador": _abrir_treinador(d)

func _fala_servico(c: Control, d: Dictionary) -> void:
	if d.get("fala", "") != "":
		var f := Tema.rotulo("“%s”" % d["fala"], 14, Color("#b8ab90"), Tema.FONTE_ITALICO)
		f.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; f.custom_minimum_size.x = 380
		c.add_child(f)

func _abrir_loja(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Loja"), Vector2(420, 560), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Loja"))
	_fala_servico(c, d)
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v); c.add_child(sc)
	for id in d.get("itens", []):
		var it := Itens.novo(id)
		var b := Button.new()
		b.custom_minimum_size = Vector2(0, 40)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var ic := Tema.icone_item(id)
		if ic.size() == 2:
			var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]
			b.icon = at; b.expand_icon = false
			b.add_theme_constant_override("icon_max_width", 32)
		var preco := Itens.preco(it)
		b.text = "  %s   —   %d ouro" % [Itens.nome(it), preco]
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 15)
		var cor := Defs.cor_raridade(it.get("raridade", "comum"))
		b.add_theme_color_override("font_color", cor if it.get("raridade", "comum") != "comum" else Color("#e8dfc9"))
		b.mouse_entered.connect(func(): game.hud.mostrar_tip(tip_item(it, "loja_compra")))
		b.mouse_exited.connect(func(): game.hud.esconder_tip())
		b.pressed.connect(func():
			var q := 10 if Input.is_key_pressed(KEY_SHIFT) and Itens.pilha(it) > 1 else 1
			game.cmd("comprar", [id, q])
			_atualizar_inventario())
		v.add_child(b)
	c.add_child(Tema.rotulo("Clique compra (Shift compra 10). Botão direito na mochila vende.", 12, Color("#7d7466"), Tema.FONTE_ITALICO))
	abrir_inventario()

func _corpo_ferreiro() -> void:
	if not jan.has("servico"): return
	var c: Control = corpo["servico"]
	_limpar(c)
	_fala_servico(c, servico_d)
	var j := _jog()
	c.add_child(Tema.rotulo("Lágrima de Anjo: +0 a +6, sempre dá certo.\nFragmento de Alma: +6 a +9, 55%; se falhar, volta um nível.", 13, Color("#c8bfa8")))
	c.add_child(Tema.rotulo("Lágrimas: %d    Fragmentos: %d    Ouro: %d" % [Itens.contar(j.inv, "lagrima_anjo"), Itens.contar(j.inv, "fragmento_alma"), j.ouro], 14, Tema.COR_OURO, Tema.FONTE_TITULO))
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v); c.add_child(sc)
	var itens: Array = []
	for s in Itens.SLOTS:
		if j.equip.has(s): itens.append([j.equip[s], s])
	for it in j.inv:
		if Itens.equipavel(it): itens.append([it, "mochila"])
	if itens.is_empty(): v.add_child(Tema.rotulo("Nada para refinar.", 14, Color("#7d7466"), Tema.FONTE_ITALICO))
	for par in itens:
		var it: Dictionary = par[0]
		var r := int(it.get("refino", 0))
		var b := Button.new()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.text = "%s%s   →  +%d  (%d ouro)" % [Itens.nome(it), "  [equipado]" if par[1] != "mochila" else "", r + 1, 50 * (r + 1)] if r < 9 else "%s   (máximo)" % Itens.nome(it)
		b.disabled = r >= 9
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		b.mouse_entered.connect(func(): game.hud.mostrar_tip(tip_item(it)))
		b.mouse_exited.connect(func(): game.hud.esconder_tip())
		b.pressed.connect(func(): game.cmd("refinar", [int(it["uid"]), par[1]]))
		v.add_child(b)

func _abrir_armazem(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Armazém"), Vector2(400, 360), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Armazém"))
	_fala_servico(c, d)
	var cg := CenterContainer.new(); cg.add_child(_grade("armazem")); c.add_child(cg)
	c.add_child(Tema.rotulo("Arraste entre o armazém e a mochila, ou use o botão direito.", 12, Color("#7d7466"), Tema.FONTE_ITALICO))
	abrir_inventario()

func _abrir_treinador(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Treino"), Vector2(380, 220), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Treino"))
	_fala_servico(c, d)
	var j := _jog()
	c.add_child(Tema.rotulo("Devolve todos os pontos de atributo para você distribuir de novo.", 14, Color("#c8bfa8")))
	var b := Button.new(); b.text = "Redistribuir (%d ouro)" % (20 * j.nivel)
	b.pressed.connect(func(): game.cmd("redistribuir"); abrir_personagem())
	c.add_child(b)

# =================================================================== textos de lore
func texto(titulo: String, txt: String) -> void:
	var c := _janela("texto", titulo, Vector2(520, 380), "centro")
	_limpar(c)
	_titulo("texto", titulo)
	var p: PanelContainer = jan["texto"]
	var sb := Tema.caixa(Color(0.16, 0.13, 0.095, 0.97), Color(0.45, 0.36, 0.22), 2, 3)
	sb.set_content_margin_all(18)
	p.add_theme_stylebox_override("panel", sb)
	var r := RichTextLabel.new(); r.bbcode_enabled = true; r.size_flags_vertical = Control.SIZE_EXPAND_FILL
	r.add_theme_font_override("normal_font", Tema.FONTE_ITALICO)
	r.add_theme_font_size_override("normal_font_size", 17)
	r.add_theme_color_override("default_color", Color("#e8dcc0"))
	r.text = txt
	c.add_child(r)
	game.audio.tocar("ui/pagina", null, -4.0)

func fechar_texto() -> void:
	fechar("texto")

# =================================================================== menu
func abrir_menu() -> void:
	var c := _janela("menu", "DARK PASSAGE", Vector2(300, 330), "centro")
	if game.hud.mapa_ui: game.hud.mapa_ui.visible = false
	_limpar(c)
	var itens := [
		["Continuar", func(): fechar("menu")],
		["Como jogar (H)", func(): fechar("menu"); game.hud.mostrar_ajuda()],
		["Som: " + ("desligado" if game.audio.mudo else "ligado"), func(): game.audio.alternar_mudo(); abrir_menu()],
		["Tremor de tela: " + ("ligado" if game.hud.mult_tremor > 0.0 else "desligado"), func(): game.hud.mult_tremor = 0.0 if game.hud.mult_tremor > 0.0 else 1.0; abrir_menu()],
		["Salvar e voltar ao início" if game.rede == null else "Sair da partida", func(): game._salvar(); game.sair_rede(); get_tree().reload_current_scene()],
	]
	for it in itens:
		var b := Button.new(); b.text = it[0]; b.custom_minimum_size = Vector2(0, 40)
		b.add_theme_font_size_override("font_size", 15)
		b.pressed.connect(it[1])
		c.add_child(b)
	var v := Tema.rotulo("Prévia v0.6 · " + ("jogo pausado · salva sozinho" if game.rede == null else "em rede o mundo não pausa · o servidor salva"), 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	v.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(v)

func fechar_dialogo() -> void:
	fechar("dialogo")

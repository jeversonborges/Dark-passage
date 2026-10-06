extends CanvasLayer
## HUD: barra de baixo (orbes, XP, skills, cinto, menu), retrato, alvo, chefe, minimapa, missões, avisos e morte.
## Peças de assets/ext/ui (thread de Interface e HUD), posições do layout.json.

var game
var raiz := Control.new()
var barra: Control
var topo_esq: Control
var alvo_ui: Control
var minimapa: Control
var rastreador: RichTextLabel
var log_box: VBoxContainer
var aviso_lbl: Label
var aviso_t := 0.0
var banner: Control
var banner_t := 0.0
var banner_txt := ""
var banner_sub := ""
var canal_ui: Control
var canal_d := {}
var canal_t := 0.0
var morte_ui: Control
var ajuda_ui: Control
var mapa_ui: Control
var tooltip: PanelContainer
var tip_lbl: RichTextLabel
var ganhos: VBoxContainer
var chefe_d := {}
var mult_tremor := 1.0
var mini_tex: ImageTexture
var mini_zoom := 3.0
var t := 0.0
var xp_flash := 0.0
var hover_slot := -1
var hover_cinto := -1
var hover_menu := -1
var pressionado := {}         # slot -> tempo do flash
var status_jog := {}          # s -> fim

const MENU := ["personagem", "mochila", "habilidades", "missoes", "mapa", "menu"]
const MENU_JANELA := {"personagem": "personagem", "mochila": "inventario", "habilidades": "habilidades", "missoes": "missoes"}
const MENU_NOME := {"personagem": "Personagem (C)", "mochila": "Mochila (I)", "habilidades": "Habilidades (K)", "missoes": "Missões (J)", "mapa": "Mapa (M)", "menu": "Menu (Esc)"}
const CINTO := [["vida", "Q"], ["recurso", "W"], ["antidoto", "E"], ["vela", "R"]]
const STATUS_NOME := {"atordoado": "Atordoado", "lento": "Lento", "queimadura": "Queimando", "sangramento": "Sangrando", "veneno": "Envenenado",
	"agarrado": "Agarrado", "silenciado": "Silenciado", "derrubado": "Derrubado", "medo": "Medo", "cego": "Cego", "enraizado": "Preso"}

func _ready() -> void:
	layer = 10
	raiz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = Tema.tema_janelas()
	add_child(raiz)
	_montar_barra()
	_montar_topo()
	_montar_alvo()
	_montar_minimapa()
	_montar_log()
	_montar_centro()
	_montar_tooltip()

# =================================================================== helpers
func _jog() -> Ent:
	return game.jog

func _txt(c: CanvasItem, p: Vector2, s: String, tam: int, cor: Color, fonte: Font = null, alinhar := 0, contorno := 3) -> void:
	var f := fonte if fonte else Tema.FONTE_TITULO
	var w := f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var x := p.x - (w * 0.5 if alinhar == 0 else (w if alinhar == 1 else 0.0))
	if contorno > 0: c.draw_string_outline(f, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, contorno, Color(0.03, 0.02, 0.02, 0.95))
	c.draw_string(f, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

func _barra(c: CanvasItem, r: Rect2, frac: float, cor: Color, fundo := Color(0.05, 0.04, 0.04, 0.9)) -> void:
	c.draw_rect(r.grow(1), Color(0.0, 0.0, 0.0, 0.85))
	c.draw_rect(r, fundo)
	var f := Rect2(r.position, Vector2(r.size.x * clampf(frac, 0.0, 1.0), r.size.y))
	c.draw_rect(f, cor)
	c.draw_rect(Rect2(f.position, Vector2(f.size.x, maxf(1.0, r.size.y * 0.35))), Color(1, 1, 1, 0.12))
	c.draw_rect(r.grow(1), Color(0.42, 0.34, 0.2, 0.9), false, 1.0)

class Painel extends Control:
	var desenhar: Callable
	var dentro: Callable
	var entrada: Callable
	func _draw() -> void:
		if desenhar.is_valid(): desenhar.call(self)
	func _has_point(p: Vector2) -> bool:
		if dentro.is_valid(): return dentro.call(p)
		return Rect2(Vector2.ZERO, size).has_point(p)
	func _gui_input(ev: InputEvent) -> void:
		if entrada.is_valid(): entrada.call(ev)

func _painel(desenhar: Callable) -> Painel:
	var p := Painel.new()
	p.desenhar = desenhar
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p

# =================================================================== barra de baixo
func _montar_barra() -> void:
	barra = _painel(_desenhar_barra)
	barra.size = Vector2(1280, 150)
	barra.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	barra.offset_left = -640; barra.offset_right = 640; barra.offset_top = -150; barra.offset_bottom = 0
	barra.mouse_filter = Control.MOUSE_FILTER_STOP
	barra.dentro = func(p: Vector2) -> bool:
		if p.y > 66 and p.x > 0 and p.x < 1280: return true
		return p.distance_to(Vector2(78, 78)) < 66 or p.distance_to(Vector2(1202, 78)) < 66
	barra.entrada = _entrada_barra
	barra.mouse_exited.connect(func(): hover_slot = -1; hover_cinto = -1; hover_menu = -1; esconder_tip())
	raiz.add_child(barra)

func _slot_rect(i: int) -> Rect2:
	return Rect2(222 + 54 * i, 90, 52, 52)

func _cinto_rect(i: int) -> Rect2:
	return Rect2(792 + 52 * i, 94, 46, 46)

func _menu_rect(i: int) -> Rect2:
	return Rect2(1023 + 36 * (i % 3), 92 + 27 * (i / 3), 34, 24)

func _entrada_barra(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var p: Vector2 = ev.position
		var hs := -1; var hc := -1; var hm := -1
		for i in 10: if _slot_rect(i).has_point(p): hs = i
		for i in 4: if _cinto_rect(i).has_point(p): hc = i
		for i in 6: if _menu_rect(i).has_point(p): hm = i
		if hs != hover_slot or hc != hover_cinto or hm != hover_menu:
			hover_slot = hs; hover_cinto = hc; hover_menu = hm
			if hs >= 0: mostrar_tip(_tip_skill(hs))
			elif hc >= 0: mostrar_tip(_tip_cinto(hc))
			elif hm >= 0: mostrar_tip("[font_size=14]%s[/font_size]" % MENU_NOME[MENU[hm]])
			else: esconder_tip()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if hover_slot >= 0: game.usar_skill(hover_slot)
		elif hover_cinto >= 0:
			var tipo: String = CINTO[hover_cinto][0]
			if tipo == "vela": game.usar_vela()
			else: game.cmd("pocao", [tipo])
		elif hover_menu >= 0:
			var nm: String = MENU[hover_menu]
			game.audio.tocar("ui/clique", null, -6.0)
			if nm == "mapa": alternar_mapa()
			elif nm == "menu": game.janelas.alternar("menu")
			else: game.janelas.alternar(MENU_JANELA[nm])
		barra.accept_event()

func _liquido_recurso() -> String:
	var j := _jog()
	if j.rec_max <= 0.0: return "sangue"
	var m: Dictionary = Tema.LAYOUT.get("orbes", {}).get("recurso", {}).get("liquido_por_classe", {})
	return m.get(j.classe, "neutro")

func _nome_recurso() -> String:
	var j := _jog()
	match j.classe:
		"humano": return "FÔLEGO"
		"cultista": return "SANGUE"
		"anjo": return "GRAÇA"
		"mutante": return "FÚRIA"
		"demonio": return "BRASA"
		"tecnomancer": return "CARGA"
	return ""

func _orbe(c: CanvasItem, centro: Vector2, frac: float, liquido: String, moldura: String, valor: String, nome: String, pulsar := false) -> void:
	var o := centro - Vector2(70, 70)
	c.draw_texture(Tema.ui("orbe_fundo"), o)
	var top := 17.0; var alt := 106.0
	var y0 := top + alt * (1.0 - clampf(frac, 0.0, 1.0))
	var liq := Tema.ui("orbe_liquido_" + liquido)
	if liq and y0 < top + alt:
		var cor := Color(1, 1, 1)
		if pulsar: cor = Color(1.0 + 0.25 * sin(t * 6.0), 1, 1)
		c.draw_texture_rect_region(liq, Rect2(o + Vector2(0, y0), Vector2(140, top + alt - y0)), Rect2(0, y0, 140, top + alt - y0), cor)
		if frac > 0.02 and frac < 0.99:
			var dy := y0 - 70.0
			var meia := sqrt(maxf(0.0, 53.0 * 53.0 - dy * dy))
			var sup := Tema.ui("orbe_superficie")
			if sup: c.draw_texture_rect(sup, Rect2(centro.x - meia, o.y + y0 - 8 + sin(t * 2.0) * 0.8, meia * 2.0, 16), false)
	c.draw_texture(Tema.ui("orbe_vidro"), o)
	c.draw_texture(Tema.ui("orbe_moldura_" + moldura), o)
	_txt(c, centro + Vector2(0, 4), valor, 15, Color("#f6ead0"), Tema.FONTE_TITULO, 0, 4)
	_txt(c, centro + Vector2(0, 62), nome, 9, Color("#d8c8a0"), Tema.FONTE_TITULO, 0, 3)

func _desenhar_barra(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	# extensão nas laterais (telas mais largas que 1280)
	var ext := Tema.ui("barra_extensao")
	var larg_tela := raiz.size.x
	if ext and larg_tela > 1280:
		var sobra := (larg_tela - 1280) * 0.5 + 2
		var x := -sobra
		while x < 0:
			c.draw_texture(ext, Vector2(x, 66)); x += 512
		x = 1280 - 4
		while x < 1280 + sobra:
			c.draw_texture(ext, Vector2(x, 66)); x += 512
	c.draw_texture(Tema.ui("barra_base"), Vector2.ZERO)
	# XP
	var xp_frac := float(j.xp) / float(maxi(1, Defs.xp_para_proximo(j.nivel)))
	var xr := Rect2(176, 75, 932, 8)
	var fill := Tema.ui("xp_preenchimento")
	if fill and xp_frac > 0.0:
		var wx := xr.size.x * clampf(xp_frac, 0.0, 1.0)
		c.draw_texture_rect(fill, Rect2(xr.position, Vector2(wx, xr.size.y)), true, Color(1, 1, 1) * (1.0 + xp_flash * 0.8))
		var ponta := Tema.ui("xp_ponta")
		if ponta: c.draw_texture(ponta, Vector2(xr.position.x + wx - 6, 71))
	c.draw_texture(Tema.ui("xp_vidro"), Vector2(170, 70))
	_txt(c, Vector2(640, 66), "EXP %.1f%%" % (xp_frac * 100.0), 8, Color("#e8ffb0"), Tema.FONTE_PIXEL, 0, 3)
	# orbes
	var envenenado := j.tem("veneno")
	_orbe(c, Vector2(78, 78), j.frac_hp(), "amargo" if envenenado else "vida", "vida", "%d" % ceili(j.hp), "VIDA", j.frac_hp() < 0.3)
	if j.rec_max > 0.0:
		_orbe(c, Vector2(1202, 78), j.rec / j.rec_max, _liquido_recurso(), "recurso", "%d" % floori(j.rec), _nome_recurso())
	else:
		_orbe(c, Vector2(1202, 78), j.frac_hp(), "sangue", "recurso", "%d%%" % roundi(j.frac_hp() * 100.0), "SANGUE")
	# info
	_txt(c, Vector2(186, 113), "%d" % j.nivel, 18, Color("#f0dca0"), Tema.FONTE_TITULO, 0, 3)
	_txt(c, Vector2(186, 124), "NÍVEL", 7, Color("#a89f8c"), Tema.FONTE_PIXEL, 0, 2)
	if j.classe == "humano":
		_txt(c, Vector2(186, 134), "%d BALAS" % j.municao, 7, Color("#e0b84a") if j.municao > 30 else Color("#ff6a4a"), Tema.FONTE_PIXEL, 0, 2)
	else:
		_txt(c, Vector2(186, 134), "%d OURO" % j.ouro, 7, Color("#e0b84a"), Tema.FONTE_PIXEL, 0, 2)
	# skills
	for i in 10:
		var r := _slot_rect(i)
		var h: Dictionary = Jogador.skill_def(j, i) if i < j.skills_slots.size() else {}
		if not h.is_empty():
			var ic := Tema.icone_skill(j.classe, h["id"])
			var bloq := j.nivel < int(h["nivel"])
			var falta: bool = not bloq and not h.get("passiva", false) and ((j.classe == "cultista" and j.hp <= Jogador.custo(j, h)) or (j.classe != "cultista" and j.rec < Jogador.custo(j, h)))
			var mod := Color(0.3, 0.3, 0.3) if bloq else (Color(0.55, 0.6, 0.85) if falta else Color.WHITE)
			if ic.size() == 2: c.draw_texture_rect_region(ic[0], Rect2(r.position + Vector2(6, 6), Vector2(40, 40)), ic[1], mod)
			if bloq: _txt(c, r.position + Vector2(26, 32), "%d" % int(h["nivel"]), 13, Color("#a89f8c"))
			var cd := float(j.cds.get(h["id"], 0.0))
			if cd > 0.0:
				var tot := float(h.get("recarga", 1.0))
				_setor(c, r.position + Vector2(26, 26), 20.0, cd / maxf(0.1, tot), Color(0, 0, 0, 0.72))
				_txt(c, r.position + Vector2(26, 31), ("%.1f" % cd) if cd < 3.0 else ("%d" % ceili(cd)), 13, Color("#f6ead0"))
			if h.has("cargas"):
				var cg := int(j.aux.get("cargas_" + h["id"], int(h["cargas"])))
				_txt(c, r.position + Vector2(44, 46), "%d" % cg, 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 1, 2)
				var rc := float(j.aux.get("recarga_carga_" + h["id"], 0.0))
				if rc > 0.0 and cd <= 0.0: c.draw_rect(Rect2(r.position + Vector2(6, 44), Vector2(40.0 * (1.0 - rc / float(h["recarga"])), 2)), Color(0.9, 0.75, 0.3, 0.9))
		c.draw_texture(Tema.ui("slot_sombra"), r.position)
		var mold := "slot_moldura"
		if pressionado.get(i, 0.0) > t: mold = "slot_pressionado"
		elif i == hover_slot: mold = "slot_hover"
		elif not h.is_empty() and j.buffer_skill.get("slot", -1) == i: mold = "slot_ativo"
		c.draw_texture(Tema.ui(mold), r.position)
		c.draw_texture(Tema.ui("tecla_%d" % ((i + 1) % 10)), r.position + Vector2(-4, -5))
	# modo automático (tecla Z): "AUTO" dourado sobre a barra de skills e moldura pulsando no slot da skill automática
	if j.aux.get("auto", false):
		var pulso := 0.65 + 0.35 * sin(t * 4.0)
		var ca := Vector2(500, 50)
		c.draw_arc(ca, 9.0, t * 3.0, t * 3.0 + TAU * 0.75, 18, Color(0.94, 0.78, 0.32, pulso), 2.0)
		c.draw_circle(ca, 3.0, Color(0.94, 0.78, 0.32, pulso))
		_txt(c, Vector2(540, 56), "AUTO", 16, Color(0.98, 0.82, 0.35, 0.75 + 0.25 * pulso), Tema.FONTE_TITULO, 0, 4)
		var sa := Jogador.slot_auto(j)
		if sa >= 0 and sa < 10:
			c.draw_rect(_slot_rect(sa).grow(1.0 + 2.0 * pulso), Color(0.98, 0.8, 0.3, 0.5 + 0.4 * pulso), false, 2.0)
	# cinto
	for i in 4:
		var r := _cinto_rect(i)
		var info := _cinto_item(i)
		if info[0] != "":
			var tx := Tema.icone_item(info[0])
			if tx.size() == 2: c.draw_texture_rect_region(tx[0], Rect2(r.position + Vector2(5, 5), Vector2(36, 36)), tx[1], Color.WHITE if info[1] > 0 else Color(0.35, 0.35, 0.35))
			_txt(c, r.position + Vector2(42, 42), "%d" % info[1], 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 1, 2)
		var cdp := float(j.aux.get("cd_pocao", 0.0))
		if cdp > 0.0 and i < 2: _setor(c, r.position + Vector2(23, 23), 18.0, cdp / Jogador.CD_POCAO, Color(0, 0, 0, 0.6))
		c.draw_texture(Tema.ui("cinto_sombra"), r.position)
		c.draw_texture(Tema.ui("cinto_hover" if i == hover_cinto else "cinto_moldura"), r.position)
		c.draw_texture(Tema.ui("tecla_" + CINTO[i][1].to_lower()), r.position + Vector2(-4, -5))
	# menu
	for i in 6:
		var r := _menu_rect(i)
		var nm: String = MENU[i]
		var aberto: bool = MENU_JANELA.has(nm) and game.janelas.aberta(MENU_JANELA[nm])
		c.draw_texture(Tema.ui("botao_%s_%s" % [nm, "hover" if i == hover_menu or aberto else "normal"]), r.position)
		if nm == "personagem" and j.pontos > 0:
			c.draw_circle(r.position + Vector2(31, 3), 4.0, Color(1.0, 0.75, 0.2, 0.7 + 0.3 * sin(t * 5.0)))

func _cinto_item(i: int) -> Array:
	var j := _jog()
	var ordem: Array
	match CINTO[i][0]:
		"vida": ordem = ["pocao_vida_m", "pocao_vida_p", "tonico_graxa", "hostia_negra", "caldo_cardo_comum", "pao_duro"]
		"recurso": ordem = ["pocao_recurso_m", "pocao_recurso_p"]
		"antidoto": ordem = ["antidoto_querosene", "agua_benta"]
		"vela": ordem = ["vela_retorno"]
	var total := 0
	var primeiro := ""
	for id in ordem:
		var q := Itens.contar(j.inv, id)
		if q > 0 and primeiro == "": primeiro = id
		total += q
	if primeiro == "": primeiro = ordem[0] if j.classe != "cultista" or CINTO[i][0] != "recurso" else ""
	return [primeiro, total]

func _setor(c: CanvasItem, centro: Vector2, r: float, frac: float, cor: Color) -> void:
	if frac <= 0.0: return
	var pts := PackedVector2Array([centro])
	var n := 24
	for k in n + 1:
		var a := -PI * 0.5 + TAU * frac * float(k) / n
		pts.append(centro + Vector2(cos(a), sin(a)) * r * 1.42)
	var clip := Rect2(centro - Vector2(r, r), Vector2(r, r) * 2.0)
	for k in pts.size(): pts[k] = pts[k].clamp(clip.position, clip.end)
	c.draw_colored_polygon(pts, cor)

func _tip_skill(i: int) -> String:
	var j := _jog()
	var h := Jogador.skill_def(j, i)
	if h.is_empty(): return ""
	var sk := Defs.skill(j.classe, h["id"])
	var nome: String = sk.get("nome", h["nome"])
	var s := "[font_size=17][color=#f0dca0]%s[/color][/font_size]\n" % nome
	var linha: Array = []
	if h.get("passiva", false): linha.append("Passiva")
	else:
		var cst := Jogador.custo(j, h)
		if cst > 0: linha.append(("%d de vida" % roundi(cst)) if j.classe == "cultista" else ("%d de %s" % [roundi(cst), _nome_recurso().to_lower()]))
		linha.append("recarga %.1fs" % float(h.get("recarga", 0)))
		if h.has("alcance") and float(h["alcance"]) > 2.0: linha.append("alcance %d" % int(h["alcance"]))
		if h.has("cargas"): linha.append("%d cargas" % int(h["cargas"]))
	s += "[color=#a89f8c][i]%s[/i][/color]\n" % " · ".join(linha)
	s += "[color=#e8dfc9]%s[/color]" % sk.get("descricao", "")
	for ef in sk.get("efeitos", []):
		s += "\n[color=#9cc8ff]• %s[/color]" % ef
	if j.nivel < int(h["nivel"]): s += "\n[color=#ff6a4a]Libera no nível %d[/color]" % int(h["nivel"])
	return s

func _tip_cinto(i: int) -> String:
	var info := _cinto_item(i)
	var nomes := {"vida": "Poção de vida", "recurso": "Poção de recurso", "antidoto": "Antídoto", "vela": "Vela de Retorno"}
	var s := "[font_size=16][color=#f0dca0]%s[/color][/font_size]  [color=#a89f8c](%s)[/color]\n" % [Defs.ITENS.get(info[0], {}).get("nome", nomes[CINTO[i][0]]), CINTO[i][1]]
	s += "Na mochila: %d" % info[1]
	if CINTO[i][0] == "vela": s += "\n[color=#a89f8c]Volta ao acampamento depois de 3 s parado.[/color]"
	return s

# =================================================================== retrato, buffs
func _montar_topo() -> void:
	topo_esq = _painel(_desenhar_topo)
	topo_esq.position = Vector2(10, 10)
	topo_esq.size = Vector2(270, 110)
	raiz.add_child(topo_esq)

func _desenhar_topo(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	var r := Rect2(0, 0, 262, 76)
	c.draw_style_box(Tema.caixa(Color(0.07, 0.055, 0.045, 0.9), Color(0.42, 0.34, 0.2), 2, 3), r)
	# retrato: primeiro quadro do idle virado para o sul
	var cen := Vector2(38, 38)
	c.draw_circle(cen, 30, Color(0.03, 0.025, 0.02))
	var meta: Dictionary = Defs.SPR.get(j.classe, {})
	if not meta.is_empty():
		var tex := Tema.tex(meta["anims"]["idle"]["file"])
		var fr: Array = meta["frame"]
		var anc: Array = meta["anchor"]
		if tex:
			var src := Rect2(anc[0] - 30, anc[1] - 118, 60, 70)
			c.draw_texture_rect_region(tex, Rect2(cen - Vector2(27, 31), Vector2(54, 63)), src)
	_arco(c, cen, 31, Color(0.69, 0.55, 0.31), 2.0)
	c.draw_circle(Vector2(62, 62), 11, Color(0.08, 0.06, 0.05))
	_arco(c, Vector2(62, 62), 11, Color(0.69, 0.55, 0.31), 1.5)
	_txt(c, Vector2(62, 67), "%d" % j.nivel, 12, Color("#f0dca0"))
	_txt(c, Vector2(82, 24), j.nome, 15, Color("#f0dca0"), Tema.FONTE_TITULO, -1)
	var cls: Dictionary = {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}
	_txt(c, Vector2(82, 40), "%s · %s" % [cls.get(j.classe, j.classe), "Vigília" if j.faccao == "vigilia" else "Arautos do Juízo"], 12, Color("#a89f8c"), Tema.FONTE_ITALICO, -1, 2)
	_barra(c, Rect2(82, 48, 168, 8), j.frac_hp(), Color(0.72, 0.1, 0.08))
	if j.rec_max > 0.0:
		var cr := {"folego": Color(0.3, 0.55, 0.9), "graca": Color(0.95, 0.85, 0.45), "furia": Color(0.85, 0.35, 0.1), "brasa": Color(1.0, 0.45, 0.1), "carga": Color(0.35, 0.8, 1.0)}
		_barra(c, Rect2(82, 60, 168, 5), j.rec / j.rec_max, cr.get(_liquido_recurso(), Color(0.5, 0.5, 0.8)))
	# buffs e status
	var x := 0.0
	var agora := []
	for b in j.buffs: agora.append([b["id"], float(b["t"]), Color(0.4, 0.75, 0.35)])
	for s in j.status: agora.append([s, float(j.status[s].get("t", 0.0)), Color(0.85, 0.25, 0.2)])
	for a in agora:
		var nome: String = STATUS_NOME.get(a[0], Defs.ITENS.get(a[0], {}).get("nome", str(a[0]).replace("_", " ").capitalize()))
		var w := Tema.FONTE_TEXTO.get_string_size(nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 30
		var rr := Rect2(x, 82, w, 18)
		c.draw_rect(rr, Color(0.06, 0.05, 0.04, 0.85))
		c.draw_rect(rr, a[2], false, 1.0)
		c.draw_string(Tema.FONTE_TEXTO, Vector2(x + 5, 96), nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, a[2].lightened(0.35))
		c.draw_string(Tema.FONTE_PIXEL, Vector2(x + w - 22, 95), "%d" % ceili(a[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#e8dfc9"))
		x += w + 4

func _arco(c: CanvasItem, cen: Vector2, r: float, cor: Color, w: float) -> void:
	c.draw_arc(cen, r, 0, TAU, 48, cor, w, true)

# =================================================================== alvo e chefe
func _montar_alvo() -> void:
	alvo_ui = _painel(_desenhar_alvo)
	alvo_ui.set_anchors_preset(Control.PRESET_CENTER_TOP)
	alvo_ui.offset_left = -200; alvo_ui.offset_right = 200; alvo_ui.offset_top = 10; alvo_ui.offset_bottom = 90
	raiz.add_child(alvo_ui)

func _desenhar_alvo(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	var sim: WorldSim = game.sim
	if not chefe_d.is_empty():
		var b: Ent = sim.ents.get(int(chefe_d.get("id", -1)))
		if b != null and b.vivo:
			_desenhar_chefe(c, b); return
	var id: int = j.alvo if j.alvo != -1 else game.hover_id
	var e: Ent = sim.ents.get(id)
	if e == null or not e.vivo or e.tipo in ["npc", "jogador"] or (e.tipo == "objeto" and not e.alvejavel): return
	if e.tipo == "objeto" and e.kind != "pilha_de_mortos": return
	var r := Rect2(40, 0, 320, 48)
	c.draw_style_box(Tema.caixa(Color(0.07, 0.055, 0.045, 0.88), Color(0.42, 0.34, 0.2), 2, 3), r)
	var cn := Color("#e8dfc9")
	if e.arquetipo == "elite": cn = Color("#e0b84a")
	elif e.arquetipo == "raro": cn = Color("#7fb8ff")
	_txt(c, Vector2(52, 19), e.nome, 15, cn, Tema.FONTE_TITULO, -1)
	var sub := "Nv. %d" % e.nivel
	if e.arquetipo in ["elite", "raro"]: sub = ("Elite · " if e.arquetipo == "elite" else "Raro · ") + sub
	_txt(c, Vector2(348, 19), sub, 12, Color("#a89f8c"), Tema.FONTE_ITALICO, 1, 2)
	_barra(c, Rect2(52, 27, 296, 9), e.frac_hp(), Color(0.7, 0.09, 0.06))
	_txt(c, Vector2(200, 35), "%d%%" % ceili(e.frac_hp() * 100.0), 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 0, 2)
	if e.postura_max > 0:
		var pf := 1.0 - e.postura / e.postura_max
		if e.quebrado_t > 0.0: pf = 1.0
		_barra(c, Rect2(52, 39, 296, 3), pf, Color(0.95, 0.7, 0.2) if e.quebrado_t <= 0.0 else Color(1, 1, 1))

func _desenhar_chefe(c: Painel, b: Ent) -> void:
	var r := Rect2(-80, 0, 560, 70)
	c.draw_style_box(Tema.caixa(Color(0.06, 0.03, 0.03, 0.92), Color(0.55, 0.16, 0.1), 2, 3), r)
	var tit: String = chefe_d.get("nome", b.nome)
	_txt(c, Vector2(200, 28), tit, 26, Color("#ffcf9a"), Tema.FONTE_GOTICA, 0, 4)
	var nf: String = chefe_d.get("nome_fase", "")
	_txt(c, Vector2(462, 22), ("Fase %d" % int(chefe_d.get("fase", 1))) + ((" · " + nf) if nf != "" else ""), 11, Color("#c8a080"), Tema.FONTE_ITALICO, 1, 2)
	var br := Rect2(-62, 36, 524, 14)
	_barra(c, br, b.frac_hp(), Color(0.62, 0.06, 0.04))
	for m in chefe_d.get("marcas", []):
		var f := float(m)
		if f >= 1.0 or f <= 0.0: continue
		var x := br.position.x + br.size.x * f
		c.draw_line(Vector2(x, br.position.y - 2), Vector2(x, br.end.y + 2), Color(0.95, 0.85, 0.6, 0.9), 2.0)
	_txt(c, Vector2(200, 48), "%d / %d" % [ceili(b.hp), ceili(b.hp_max)], 9, Color("#f6ead0"), Tema.FONTE_PIXEL, 0, 2)
	if b.postura_max > 0:
		var pf := 1.0 - b.postura / b.postura_max
		if b.quebrado_t > 0.0: pf = 1.0
		_barra(c, Rect2(-62, 55, 524, 4), pf, Color(0.95, 0.7, 0.2) if b.quebrado_t <= 0.0 else Color(1, 1, 1))
	if b.escudo > 0.0:
		_barra(c, Rect2(-62, 62, 524, 3), b.escudo / maxf(1.0, b.hp_max * 0.15), Color(0.85, 0.85, 1.0))

func chefe(d: Dictionary) -> void:
	if d.get("fim", false):
		if d.get("morto", false): banner_mostrar("INIMIGO ABATIDO", chefe_d.get("nome", ""), Color("#ffcf9a"))
		chefe_d = {}
		return
	if d.get("inicio", false):
		chefe_d = d.duplicate()
		banner_mostrar(d.get("nome", ""), "", Color("#ff8a6a"))
	else:
		chefe_d["fase"] = d.get("fase", 1)
		chefe_d["nome_fase"] = d.get("nome_fase", "")
		if d.get("nome_fase", "") != "": aviso(d["nome_fase"], Color("#ff9a6a"))

# =================================================================== minimapa
func ao_trocar_mapa() -> void:
	chefe_d = {}
	var m: Dictionary = game.mapa
	var w := int(m["w"]); var h := int(m["h"])
	var img := Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	var grade: Array = m["grade"]
	var ter: Array = m["terreno"]
	for y in h:
		var gl: String = grade[y]
		var tl: String = ter[y]
		for x in w:
			var ch := tl[x]
			var parede := gl[x] == "#"
			if ch == " " or ch == "h":
				continue
			var cor: Color = game.cores_piso.get(ch, Color(0.3, 0.27, 0.22))
			cor = cor.lerp(Color(0.5, 0.45, 0.35), 0.15) * 1.35
			if parede: cor = cor.darkened(0.6)
			cor.a = 1.0
			img.set_pixel(x + 1, y + 1, cor)
	mini_tex = ImageTexture.create_from_image(img)
	mini_zoom = 3.0 if m.get("exterior", false) else 4.0
	if mapa_ui: mapa_ui.queue_redraw()

func _montar_minimapa() -> void:
	minimapa = _painel(_desenhar_minimapa)
	minimapa.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	minimapa.offset_left = -180; minimapa.offset_right = -10; minimapa.offset_top = 10; minimapa.offset_bottom = 200
	minimapa.mouse_filter = Control.MOUSE_FILTER_STOP
	minimapa.dentro = func(p: Vector2) -> bool: return p.distance_to(Vector2(85, 85)) < 80
	minimapa.entrada = func(ev: InputEvent):
		if ev is InputEventMouseButton and ev.pressed:
			if ev.button_index == MOUSE_BUTTON_WHEEL_UP: mini_zoom = minf(8.0, mini_zoom * 1.2)
			elif ev.button_index == MOUSE_BUTTON_WHEEL_DOWN: mini_zoom = maxf(1.5, mini_zoom / 1.2)
			elif ev.button_index == MOUSE_BUTTON_LEFT: alternar_mapa()
			minimapa.accept_event()
	raiz.add_child(minimapa)
	rastreador = RichTextLabel.new()
	rastreador.bbcode_enabled = true
	rastreador.fit_content = true
	rastreador.scroll_active = false
	rastreador.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rastreador.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	rastreador.offset_left = -270; rastreador.offset_right = -14; rastreador.offset_top = 212; rastreador.offset_bottom = 520
	rastreador.add_theme_font_override("normal_font", Tema.FONTE_TEXTO)
	rastreador.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	rastreador.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	rastreador.add_theme_font_size_override("normal_font_size", 14)
	rastreador.add_theme_font_size_override("bold_font_size", 13)
	rastreador.add_theme_constant_override("outline_size", 4)
	rastreador.add_theme_color_override("font_outline_color", Color(0.02, 0.015, 0.015, 0.9))
	raiz.add_child(rastreador)

## Desenha o mapa em losango (iso) dentro de um polígono qualquer: cada vértice ganha a UV do tile embaixo dele.
func _desenhar_mapa_iso(c: CanvasItem, pts: PackedVector2Array, centro_tela: Vector2, centro_mundo: Vector2, px_por_tile: float) -> void:
	if mini_tex == null: return
	var uvs := PackedVector2Array()
	var w := float(mini_tex.get_width()); var h := float(mini_tex.get_height())
	for p in pts:
		var d := (p - centro_tela) / px_por_tile
		# tela iso: sx = (x+y), sy = (x-y)/2  ->  x = (sx + 2sy)/2, y = (sx - 2sy)/2
		var wx := centro_mundo.x + (d.x + 2.0 * d.y) * 0.5 + 1.0
		var wy := centro_mundo.y + (d.x - 2.0 * d.y) * 0.5 + 1.0
		uvs.append(Vector2(wx / w, wy / h))
	var cores := PackedColorArray(); cores.resize(pts.size()); cores.fill(Color.WHITE)
	c.draw_polygon(pts, cores, uvs, mini_tex)

func _mundo_para_mini(p: Vector2, centro_tela: Vector2, centro_mundo: Vector2, k: float) -> Vector2:
	var d := p - centro_mundo
	return centro_tela + Vector2(d.x + d.y, (d.x - d.y) * 0.5) * k

func _desenhar_minimapa(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	var cen := Vector2(85, 85)
	var r := 70.0
	c.draw_circle(cen, r + 8, Color(0.03, 0.025, 0.02, 0.92))
	var pts := PackedVector2Array()
	for i in 48: pts.append(cen + Vector2(cos(TAU * i / 48.0), sin(TAU * i / 48.0)) * r)
	_desenhar_mapa_iso(c, pts, cen, j.pos, mini_zoom)
	_marcadores(c, cen, j.pos, mini_zoom, r)
	_arco(c, cen, r + 1, Color(0.2, 0.15, 0.1), 3.0)
	_arco(c, cen, r + 5, Color(0.69, 0.55, 0.31), 4.0)
	_arco(c, cen, r + 8, Color(0.25, 0.19, 0.12), 2.0)
	for i in 8:
		var a := TAU * i / 8.0
		c.draw_circle(cen + Vector2(cos(a), sin(a)) * (r + 5), 2.2, Color(0.85, 0.72, 0.45))
	# norte iso: +x-y fica para cima-direita; o "N" marca o topo da tela
	_txt(c, cen + Vector2(0, -r - 1), "N", 11, Color("#ff8a6a"), Tema.FONTE_TITULO, 0, 3)
	var zn: String = Defs.nome_local(j.zona) if j.zona != "" else game.mapa.get("nome", "")
	var placa := Rect2(cen.x - 82, cen.y + r + 10, 164, 20)
	c.draw_style_box(Tema.caixa(Color(0.08, 0.06, 0.05, 0.92), Color(0.42, 0.34, 0.2), 1, 2), placa)
	var nz: String = zn.to_upper()
	var tam := 10
	while Tema.FONTE_TITULO.get_string_size(nz, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x > 156 and tam > 7: tam -= 1
	_txt(c, Vector2(cen.x, placa.position.y + 14), nz, tam, Color("#e0c890"), Tema.FONTE_TITULO, 0, 2)

func _marcadores(c: CanvasItem, cen: Vector2, cm: Vector2, k: float, raio: float) -> void:
	var sim: WorldSim = game.sim
	var j := _jog()
	for e: Ent in sim.ents.values():
		if not e.vivo or e.invisivel: continue
		var p := _mundo_para_mini(e.pos, cen, cm, k)
		if p.distance_to(cen) > raio - 3: continue
		match e.tipo:
			"monstro":
				var cm2 := Color(0.85, 0.15, 0.1)
				if e.aux.get("neutro", false) and e.estado in ["ocioso", "vagar"]: cm2 = Color(0.9, 0.78, 0.2)
				c.draw_circle(p, 2.2 if e.arquetipo == "normal" else 3.0, cm2 if e.arquetipo == "normal" else Color(1.0, 0.55, 0.15))
			"chefe":
				c.draw_circle(p, 4.5, Color(0.1, 0, 0)); c.draw_circle(p, 3.5, Color(1.0, 0.25, 0.1))
			"jogador":   # outros jogadores da rede
				if e.id != j.id: c.draw_circle(p, 3.6, Color(0.05, 0.1, 0.15)); c.draw_circle(p, 2.8, Color(0.55, 0.85, 1.0))
			"npc":
				var mk := Missoes.marcador_npc(j, e.kind)
				if mk != "": _txt(c, p + Vector2(0, 5), mk, 14, Color(1, 0.82, 0.25) if mk == "!" else Color(0.75, 0.95, 0.4), Tema.FONTE_GOTICA, 0, 2)
				else: c.draw_circle(p, 2.5, Color(0.95, 0.85, 0.5))
			"objeto":
				if e.kind == "bau" and not e.aux.get("aberto", false) and game.objs.has(e.id) and game.objs[e.id].visible:
					c.draw_rect(Rect2(p - Vector2(2.5, 2), Vector2(5, 4)), Color(0.95, 0.75, 0.3))
				elif e.kind == "portal" or (e.kind == "interativo" and Defs.OBJETOS.get(e.aux.get("obj", ""), {}).has("leva_para")):
					c.draw_circle(p, 3.5, Color(0.4, 0.7, 1.0)); c.draw_circle(p, 1.5, Color(0.9, 0.95, 1.0))
	for cid in sim.chao:
		var p2 := _mundo_para_mini(sim.chao[cid]["pos"], cen, cm, k)
		if p2.distance_to(cen) < raio - 3: c.draw_rect(Rect2(p2 - Vector2(1, 1), Vector2(2, 2)), Color(1, 1, 1, 0.8))
	# jogador: seta na direção em que olha
	var pj := _mundo_para_mini(j.pos, cen, cm, k)
	var f := Iso.to_screen(j.facing).normalized()
	var lado := Vector2(-f.y, f.x)
	c.draw_colored_polygon(PackedVector2Array([pj + f * 6, pj - f * 4 + lado * 4, pj - f * 2, pj - f * 4 - lado * 4]), Color(1, 1, 1))

# =================================================================== mapa grande
func alternar_mapa() -> void:
	if mapa_ui == null:
		mapa_ui = _painel(_desenhar_mapa_grande)
		mapa_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mapa_ui.mouse_filter = Control.MOUSE_FILTER_STOP
		mapa_ui.entrada = func(ev: InputEvent):
			if ev is InputEventMouseButton and ev.pressed: mapa_ui.visible = false; mapa_ui.accept_event()
		var cl := CanvasLayer.new(); cl.layer = 15
		add_child(cl)
		var r2 := Control.new(); r2.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); r2.mouse_filter = Control.MOUSE_FILTER_IGNORE
		r2.theme = raiz.theme
		cl.add_child(r2)
		r2.add_child(mapa_ui)
		mapa_ui.visible = false
	var abrir := not mapa_ui.visible
	if abrir: game.janelas.fechar_tudo()
	mapa_ui.visible = abrir
	game.audio.tocar("ui/abrir_janela" if mapa_ui.visible else "ui/fechar_janela", null, -6.0)

func _desenhar_mapa_grande(c: Painel) -> void:
	var j := _jog()
	var s := c.size
	c.draw_rect(Rect2(Vector2.ZERO, s), Color(0.03, 0.025, 0.02, 0.94))
	var m: Dictionary = game.mapa
	var w := float(m["w"]); var h := float(m["h"])
	var cam: Array = m.get("camera", [0, 0, w, h])
	var cm := Vector2((cam[0] + cam[2]) * 0.5, (cam[1] + cam[3]) * 0.5)
	var lw: float = (cam[2] - cam[0]) + (cam[3] - cam[1])
	var k := minf((s.x - 340) / lw, (s.y - 150) / (lw * 0.5))
	var cen := Vector2((s.x - 260) * 0.5 + 20, s.y * 0.5 + 16)
	var pts := PackedVector2Array([Vector2(20, 70), Vector2(s.x - 280, 70), Vector2(s.x - 280, s.y - 40), Vector2(20, s.y - 40)])
	if mapa_tex == null or mapa_tex_id != m.get("id", ""): _gerar_mapa_claro()
	var guarda := mini_tex
	mini_tex = mapa_tex
	_desenhar_mapa_iso(c, pts, cen, cm, k)
	mini_tex = guarda
	_marcadores(c, cen, cm, k, 99999.0)
	# objetivos das missões ativas: estrela dourada com o nome
	var legenda: Array = []
	for alvo in _alvos_missoes(j):
		var p := _mundo_para_mini(alvo[0], cen, cm, k)
		_estrela(c, p, 9.0, Color(1.0, 0.82, 0.3))
		_txt(c, p + Vector2(0, -14), alvo[1], 12, Color("#ffe6a0"), Tema.FONTE_TITULO, 0, 4)
		if not legenda.has(alvo[2]): legenda.append(alvo[2])
	# nomes das zonas: conhecidas em dourado, as outras em cinza (o nome aparece, a cor diz que você ainda não esteve lá)
	var somas := {}
	var zg: Array = m.get("zona_grade", [])
	for y in range(0, zg.size(), 3):
		var ln: String = zg[y]
		for x in range(0, ln.length(), 3):
			if ln[x] == ".": continue
			var i := ln.unicode_at(x) - 65
			if not somas.has(i): somas[i] = [Vector2.ZERO, 0]
			somas[i][0] += Vector2(x, y); somas[i][1] += 1
	var zonas: Array = m.get("zonas", [])
	for i in somas:
		if i >= zonas.size() or somas[i][1] < 6: continue
		var p := _mundo_para_mini(somas[i][0] / float(somas[i][1]), cen, cm, k)
		var conhecida: bool = j.vistas.has(zonas[i]["id"]) or zonas[i]["id"] == j.zona
		var niv = zonas[i].get("nivel")
		_txt(c, p, zonas[i]["nome"], 15, Color("#f6e2a8") if conhecida else Color("#a49a86"), Tema.FONTE_TITULO, 0, 5)
		if niv is Array: _txt(c, p + Vector2(0, 15), "nível %d–%d" % [int(niv[0]), int(niv[1])], 11, Color("#c8b890") if conhecida else Color("#8a8070"), Tema.FONTE_ITALICO, 0, 3)
		elif zonas[i].get("seguro", false): _txt(c, p + Vector2(0, 15), "área segura", 11, Color("#a8d890"), Tema.FONTE_ITALICO, 0, 3)
	# passagens: para onde levam (a cripta e os chefes ficam atrás delas)
	for e: Ent in game.sim.ents.values():
		if e.tipo != "objeto": continue
		var dest := ""
		if e.kind == "portal": dest = str(e.aux.get("para", ""))
		elif e.kind == "interativo": dest = str(Defs.OBJETOS.get(e.aux.get("obj", ""), {}).get("leva_para", ""))
		if dest == "" or not DESTINOS.has(dest): continue
		var pp := _mundo_para_mini(e.pos, cen, cm, k)
		_txt(c, pp + Vector2(0, 16), DESTINOS[dest], 12, Color("#9fd0ff"), Tema.FONTE_TITULO, 0, 4)
	_txt(c, Vector2((s.x - 260) * 0.5 + 20, 46), m.get("nome", ""), 30, Color("#ffcf9a"), Tema.FONTE_GOTICA, 0, 5)
	# legenda à direita
	var lx := s.x - 250.0
	var caixa := Rect2(lx, 70, 230, s.y - 110)
	c.draw_style_box(Tema.caixa(Color(0.07, 0.055, 0.045, 0.95), Color(0.42, 0.34, 0.2), 1, 3), caixa)
	var y0 := 100.0
	_txt_esq(c, Vector2(lx + 16, y0), "LEGENDA", 14, Color("#e0c890"), Tema.FONTE_TITULO); y0 += 26
	var itens := [["voce", "Você"], ["estrela", "Objetivo de missão"], ["!", "Missão nova"], ["?", "Entregar missão"],
		["chefe", "Chefe"], ["mob", "Monstro agressivo"], ["neutro", "Monstro neutro"], ["portal", "Passagem"], ["bau", "Baú"]]
	for it in itens:
		var p2 := Vector2(lx + 26, y0 - 4)
		match it[0]:
			"voce": c.draw_colored_polygon(PackedVector2Array([p2 + Vector2(6, 0), p2 + Vector2(-4, 4), p2 + Vector2(-2, 0), p2 + Vector2(-4, -4)]), Color.WHITE)
			"estrela": _estrela(c, p2, 7.0, Color(1.0, 0.82, 0.3))
			"!": _txt(c, p2 + Vector2(0, 5), "!", 15, Color(1, 0.82, 0.25), Tema.FONTE_GOTICA, 0, 2)
			"?": _txt(c, p2 + Vector2(0, 5), "?", 15, Color(0.75, 0.95, 0.4), Tema.FONTE_GOTICA, 0, 2)
			"chefe": c.draw_circle(p2, 4.5, Color(0.1, 0, 0)); c.draw_circle(p2, 3.5, Color(1.0, 0.25, 0.1))
			"mob": c.draw_circle(p2, 2.6, Color(0.85, 0.15, 0.1))
			"neutro": c.draw_circle(p2, 2.6, Color(0.9, 0.78, 0.2))
			"portal": c.draw_circle(p2, 3.5, Color(0.4, 0.7, 1.0)); c.draw_circle(p2, 1.5, Color(0.9, 0.95, 1.0))
			"bau": c.draw_rect(Rect2(p2 - Vector2(3, 2.5), Vector2(6, 5)), Color(0.95, 0.75, 0.3))
		_txt_esq(c, Vector2(lx + 42, y0), it[1], 13, Color("#d8cfb8"), Tema.FONTE_TEXTO)
		y0 += 24
	if not legenda.is_empty():
		y0 += 12
		_txt_esq(c, Vector2(lx + 16, y0), "MISSÕES", 14, Color("#e0c890"), Tema.FONTE_TITULO); y0 += 24
		for tl in legenda:
			_txt_esq(c, Vector2(lx + 16, y0), "• " + str(tl), 13, Color("#ffe6a0"), Tema.FONTE_TEXTO); y0 += 22
	_txt(c, Vector2((s.x - 260) * 0.5 + 20, s.y - 14), "Clique ou M para fechar", 12, Color("#a89f8c"), Tema.FONTE_ITALICO, 0, 2)

const DESTINOS := {
	"porao_matadouro": "Porão · Cripta (chefe Andras, nv 8)",
	"ossario_carpideiras": "Ossário (chefe Irmã Celeste, nv 10)",
	"camara_trombeta": "Câmara (chefe Zacarias, nv 12)",
	"area_inicial": "Saída para a Paróquia",
}
var mapa_tex: ImageTexture
var mapa_tex_id := ""
## Versão clara do mapa para a tela grande: chão em sépia legível, caminhos claros, paredes escuras, rio em verde.
func _gerar_mapa_claro() -> void:
	var m: Dictionary = game.mapa
	mapa_tex_id = m.get("id", "")
	var w := int(m["w"]); var h := int(m["h"])
	var img := Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	var grade: Array = m["grade"]
	var ter: Array = m["terreno"]
	for y in h:
		var gl: String = grade[y]
		var tl: String = ter[y]
		for x in w:
			var ch := tl[x]
			if ch == " " or ch == "h": continue
			var base: Color = game.cores_piso.get(ch, Color(0.3, 0.27, 0.22))
			var lum := clampf(base.get_luminance() * 2.2, 0.0, 1.0)
			var cor := Color(0.36, 0.3, 0.22).lerp(Color(0.78, 0.68, 0.5), lum)
			if base.g > base.r * 1.08: cor = cor.lerp(Color(0.42, 0.55, 0.3), 0.6)
			if gl[x] == "#": cor = Color(0.16, 0.13, 0.1)
			img.set_pixel(x + 1, y + 1, cor)
	mapa_tex = ImageTexture.create_from_image(img)

## [pos, rótulo curto, título da missão] para cada objetivo pendente das missões ativas.
func _alvos_missoes(j: Ent) -> Array:
	var out: Array = []
	var sim: WorldSim = game.sim
	for mid in j.missoes:
		if Missoes.estado(j, mid) != "ativa": continue
		var d := Missoes.def(mid)
		if d.is_empty(): continue
		var tit: String = d.get("titulo", mid)
		if Missoes.pronta(j, mid):
			var en = d.get("entrega", "")
			if en is Array: en = en[0] if en.size() > 0 else ""
			for e: Ent in sim.ents.values():
				if e.tipo == "npc" and e.kind == en: out.append([e.pos, "Entregar", tit])
			continue
		var etapa := Missoes._etapa_atual(j, mid)
		var objs: Array = d["objetivos"]
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) != etapa: continue
			var pr := Missoes.progresso(j, mid, i)
			if pr[0] >= pr[1]: continue
			var pos = null
			match o["tipo"]:
				"matar":
					for g in sim.spawns:
						if g["mob"] == o["alvo"]:
							if pos == null or (g["pos"] as Vector2).distance_to(j.pos) < (pos as Vector2).distance_to(j.pos): pos = g["pos"]
				"interagir", "usar_item":
					for e: Ent in sim.ents.values():
						if e.tipo == "objeto" and e.aux.get("obj", "") == o.get("objeto", ""): pos = e.pos
				"falar", "decidir":
					var n = o.get("npc"); if n is Array: n = n[0]
					for e: Ent in sim.ents.values():
						if e.tipo == "npc" and e.kind == n: pos = e.pos
				"explorar":
					pos = _centro_zona(o.get("subzona", ""))
			if pos == null and o.has("subzona"): pos = _centro_zona(o["subzona"])
			if pos != null: out.append([pos, Missoes.texto_objetivo(o).left(28), tit])
	return out

func _centro_zona(zid: String):
	var m: Dictionary = game.mapa
	var zonas: Array = m.get("zonas", [])
	var idx := -1
	for i in zonas.size():
		if zonas[i]["id"] == zid: idx = i
	if idx < 0: return null
	var soma := Vector2.ZERO; var n := 0
	var zg: Array = m.get("zona_grade", [])
	for y in range(0, zg.size(), 2):
		var ln: String = zg[y]
		for x in range(0, ln.length(), 2):
			if ln.unicode_at(x) - 65 == idx: soma += Vector2(x, y); n += 1
	return soma / n if n > 0 else null

func _estrela(c: CanvasItem, p: Vector2, r: float, cor: Color) -> void:
	var pts := PackedVector2Array()
	for i in 10:
		var rr := r if i % 2 == 0 else r * 0.45
		var a := -PI / 2 + TAU * i / 10.0
		pts.append(p + Vector2(cos(a), sin(a)) * rr)
	c.draw_colored_polygon(pts, Color(0.1, 0.06, 0.02))
	var pts2 := PackedVector2Array()
	for q in pts: pts2.append(p + (q - p) * 0.78)
	c.draw_colored_polygon(pts2, cor)

func _txt_esq(c: CanvasItem, p: Vector2, t: String, tam: int, cor: Color, fonte: Font) -> void:
	c.draw_string_outline(fonte, p, t, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, 3, Color(0, 0, 0, 0.9))
	c.draw_string(fonte, p, t, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

# =================================================================== log, avisos, faixa de zona, canalização
func _montar_log() -> void:
	log_box = VBoxContainer.new()
	log_box.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	log_box.offset_left = 12; log_box.offset_right = 420; log_box.offset_top = -330; log_box.offset_bottom = -160
	log_box.alignment = BoxContainer.ALIGNMENT_END
	log_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	log_box.add_theme_constant_override("separation", 1)
	raiz.add_child(log_box)
	ganhos = VBoxContainer.new()
	ganhos.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	ganhos.offset_left = -420; ganhos.offset_right = -150; ganhos.offset_top = -330; ganhos.offset_bottom = -160
	ganhos.alignment = BoxContainer.ALIGNMENT_END
	ganhos.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(ganhos)

func log_msg(txt: String, cor := Color("#d8cfb8")) -> void:
	if txt == "": return
	var l := Tema.rotulo(txt, 14, cor, Tema.FONTE_TEXTO, 3)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = 400
	log_box.add_child(l)
	while log_box.get_child_count() > 7: log_box.get_child(0).queue_free(); log_box.remove_child(log_box.get_child(0))
	var tw := l.create_tween()
	tw.tween_interval(9.0)
	tw.tween_property(l, "modulate:a", 0.0, 1.5)
	tw.tween_callback(l.queue_free)

func item_ganho(d: Dictionary) -> void:
	var cor := Defs.cor_raridade(d.get("raridade", "comum"))
	var h := HBoxContainer.new()
	h.alignment = BoxContainer.ALIGNMENT_END
	h.add_theme_constant_override("separation", 6)
	var txt: String = d.get("nome", "")
	if int(d.get("qtd", 1)) > 1: txt = "%d × %s" % [int(d["qtd"]), txt]
	var l := Tema.rotulo(txt, 15, cor, Tema.FONTE_TITULO, 4)
	h.add_child(l)
	var ic := Tema.icone_item(d.get("id", ""))
	if ic.size() == 2:
		var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]
		var tr := TextureRect.new(); tr.texture = at; tr.custom_minimum_size = Vector2(26, 26)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		h.add_child(tr)
	ganhos.add_child(h)
	while ganhos.get_child_count() > 6: var c0 := ganhos.get_child(0); ganhos.remove_child(c0); c0.queue_free()
	h.modulate.a = 0.0
	var tw := h.create_tween()
	tw.tween_property(h, "modulate:a", 1.0, 0.15)
	tw.tween_interval(4.0)
	tw.tween_property(h, "modulate:a", 0.0, 1.0)
	tw.tween_callback(h.queue_free)

func _montar_centro() -> void:
	aviso_lbl = Tema.rotulo("", 18, Color("#ffd9a0"), Tema.FONTE_TITULO, 5)
	aviso_lbl.set_anchors_preset(Control.PRESET_CENTER)
	aviso_lbl.offset_left = -400; aviso_lbl.offset_right = 400; aviso_lbl.offset_top = -170; aviso_lbl.offset_bottom = -140
	aviso_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	aviso_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(aviso_lbl)
	banner = _painel(_desenhar_banner)
	banner.set_anchors_preset(Control.PRESET_CENTER_TOP)
	banner.offset_left = -400; banner.offset_right = 400; banner.offset_top = 110; banner.offset_bottom = 200
	raiz.add_child(banner)
	canal_ui = _painel(_desenhar_canal)
	canal_ui.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	canal_ui.offset_left = -130; canal_ui.offset_right = 130; canal_ui.offset_top = -230; canal_ui.offset_bottom = -190
	raiz.add_child(canal_ui)

func aviso(txt: String, cor := Color("#ffd9a0")) -> void:
	if txt == "": return
	aviso_lbl.text = txt
	aviso_lbl.add_theme_color_override("font_color", cor)
	aviso_t = 2.4

func banner_mostrar(titulo: String, sub: String, cor := Color("#f0dca0")) -> void:
	banner_txt = titulo; banner_sub = sub; banner_t = 4.0
	banner.set_meta("cor", cor)

func _desenhar_banner(c: Painel) -> void:
	if banner_t <= 0.0: return
	var a := clampf(banner_t / 0.8, 0.0, 1.0) * clampf((4.0 - banner_t) / 0.4, 0.0, 1.0)
	var cor: Color = banner.get_meta("cor", Color("#f0dca0"))
	var w := 400.0
	for i in 40:
		var k := 1.0 - absf(i - 20) / 20.0
		c.draw_rect(Rect2(w - 300 + i * 15, 24, 15, 48), Color(0, 0, 0, 0.45 * a * k))
	c.draw_line(Vector2(w - 220, 70), Vector2(w + 220, 70), Color(cor.r, cor.g, cor.b, 0.6 * a), 1.0)
	_txt(c, Vector2(w, 58), banner_txt, 36, Color(cor.r, cor.g, cor.b, a), Tema.FONTE_GOTICA, 0, 6)
	if banner_sub != "": _txt(c, Vector2(w, 88), banner_sub, 15, Color(0.75, 0.7, 0.6, a), Tema.FONTE_ITALICO, 0, 3)

func zona(z: Dictionary, primeira: bool) -> void:
	if z.is_empty(): return
	var sub := ""
	if z.get("seguro", false): sub = "Área segura"
	elif z.has("nivel") and z["nivel"] != null:
		var nv = z["nivel"]
		sub = ("Nível %d–%d" % [int(nv[0]), int(nv[1])]) if nv is Array else ("Nível %s" % str(nv))
	if primeira or true: banner_mostrar(z.get("nome", ""), sub)

func canal(d: Dictionary) -> void:
	if int(d.get("id", -1)) != _jog().id and not d.get("chefe", false): return
	canal_d = d.duplicate(); canal_t = 0.0

func canal_fim(d: Dictionary) -> void:
	if int(d.get("id", -1)) == int(canal_d.get("id", -2)): canal_d = {}

func _desenhar_canal(c: Painel) -> void:
	if canal_d.is_empty(): return
	var f := clampf(canal_t / maxf(0.05, float(canal_d.get("dur", 1.0))), 0.0, 1.0)
	var eh_chefe: bool = canal_d.get("chefe", false)
	_txt(c, Vector2(130, 12), canal_d.get("texto", ""), 14, Color("#ffb08a") if eh_chefe else Color("#f0dca0"), Tema.FONTE_TITULO, 0, 3)
	_barra(c, Rect2(10, 18, 240, 10), f, Color(0.85, 0.3, 0.15) if eh_chefe else Color(0.85, 0.7, 0.35))

# =================================================================== morte, ajuda
func morte(d: Dictionary) -> void:
	if morte_ui == null:
		morte_ui = _painel(_desenhar_morte)
		morte_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		raiz.add_child(morte_ui)
	morte_ui.set_meta("d", d)
	morte_ui.set_meta("t", 0.0)
	morte_ui.visible = true
	chefe_d = {}

func reviveu() -> void:
	if morte_ui: morte_ui.visible = false

func _desenhar_morte(c: Painel) -> void:
	var tt: float = morte_ui.get_meta("t", 0.0)
	var d: Dictionary = morte_ui.get_meta("d", {})
	var a := clampf(tt / 1.5, 0.0, 1.0)
	c.draw_rect(Rect2(Vector2.ZERO, c.size), Color(0.12, 0.0, 0.0, 0.55 * a))
	var cen := c.size * 0.5
	_txt(c, cen + Vector2(0, -20), "VOCÊ CAIU", 64, Color(0.75, 0.1, 0.06, a), Tema.FONTE_GOTICA, 0, 8)
	var falta: float = maxf(0.0, float(d.get("t", 5.0)) - tt)
	var sub := "Voltando ao último altar em %d…" % ceili(falta)
	if int(d.get("perda", 0)) > 0: sub = "Perdeu %d de experiência. " % int(d["perda"]) + sub
	_txt(c, cen + Vector2(0, 24), sub, 17, Color(0.85, 0.78, 0.65, a), Tema.FONTE_ITALICO, 0, 3)

func mostrar_ajuda() -> void:
	if ajuda_ui == null:
		ajuda_ui = PanelContainer.new()
		ajuda_ui.set_anchors_preset(Control.PRESET_CENTER)
		ajuda_ui.offset_left = -300; ajuda_ui.offset_right = 300; ajuda_ui.offset_top = -210; ajuda_ui.offset_bottom = 190
		var v := VBoxContainer.new()
		v.add_theme_constant_override("separation", 8)
		ajuda_ui.add_child(v)
		var tl := Tema.rotulo("Como jogar", 30, Color("#ffcf9a"), Tema.FONTE_GOTICA, 4)
		tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(tl)
		var r := RichTextLabel.new()
		r.bbcode_enabled = true; r.fit_content = true; r.scroll_active = false
		r.add_theme_font_size_override("normal_font_size", 15)
		r.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
		r.text = """[b]Clique[/b] no chão para andar (segure para seguir o mouse).
[b]Clique[/b] num inimigo para atacar. [b]Shift + clique[/b] ataca sem sair do lugar.
[b]1 a 6[/b] usam as habilidades (no alvo ou onde o mouse aponta). [b]Botão direito[/b] = habilidade 1.
[b]Q[/b] poção de vida, [b]W[/b] poção de recurso, [b]E[/b] antídoto, [b]R[/b] Vela de Retorno.
[b]Z[/b] liga o modo automático: luta sozinho perto de onde você está e bebe poção (desliga ao clicar).
[b]Clique[/b] em NPCs, baús, portas e itens no chão. [b]Alt[/b] mostra os itens caídos.
[b]I[/b] mochila e equipamento · [b]C[/b] personagem · [b]K[/b] habilidades · [b]J[/b] missões · [b]M[/b] mapa.
Na mochila: [b]botão direito[/b] usa ou equipa; [b]arraste[/b] para mover, equipar ou jogar fora.
Os [b]![/b] em cima das pessoas são missões novas; [b]?[/b] são missões prontas para entregar.
Áreas vermelhas no chão avisam um golpe: saia delas.

[color=#a89f8c][i]H mostra esta ajuda de novo.[/i][/color]"""
		v.add_child(r)
		var b := Button.new(); b.text = "Entendi"; b.custom_minimum_size = Vector2(140, 36)
		b.pressed.connect(func(): ajuda_ui.visible = false)
		var cc := CenterContainer.new(); cc.add_child(b); v.add_child(cc)
		raiz.add_child(ajuda_ui)
	ajuda_ui.visible = true

func alternar_ajuda() -> void:
	if ajuda_ui and ajuda_ui.visible: ajuda_ui.visible = false
	else: mostrar_ajuda()

# =================================================================== tooltip
func _montar_tooltip() -> void:
	tooltip = PanelContainer.new()
	var sb := Tema.caixa(Color(0.05, 0.04, 0.035, 0.96), Color(0.55, 0.44, 0.26), 1, 2)
	sb.set_content_margin_all(10)
	tooltip.add_theme_stylebox_override("panel", sb)
	tooltip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip_lbl = RichTextLabel.new()
	tip_lbl.bbcode_enabled = true
	tip_lbl.fit_content = true
	tip_lbl.scroll_active = false
	tip_lbl.custom_minimum_size.x = 300
	tip_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip_lbl.add_theme_font_override("normal_font", Tema.FONTE_TEXTO)
	tip_lbl.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	tip_lbl.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	tip_lbl.add_theme_font_size_override("normal_font_size", 14)
	tip_lbl.add_theme_font_size_override("italics_font_size", 13)
	tooltip.add_child(tip_lbl)
	tooltip.visible = false
	tooltip.z_index = 100
	var cl := CanvasLayer.new(); cl.layer = 30; add_child(cl)
	var c := Control.new(); c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cl.add_child(c)
	c.add_child(tooltip)

func mostrar_tip(bb: String) -> void:
	if bb == "": esconder_tip(); return
	tip_lbl.text = bb
	tooltip.visible = true
	tooltip.reset_size()

func esconder_tip() -> void:
	tooltip.visible = false

# =================================================================== eventos simples
func xp(d: Dictionary) -> void:
	xp_flash = 1.0

func nivel(d: Dictionary) -> void:
	banner_mostrar("NÍVEL %d" % int(d["nivel"]), ("Nova habilidade: " + d["skill_nova"]) if d.get("skill_nova", "") != "" else "Você tem pontos de atributo para distribuir (C)", Color("#ffe08a"))

func skill_usada(d: Dictionary) -> void:
	if int(d.get("id", -1)) == _jog().id: pressionado[int(d.get("slot", -1))] = t + 0.12

func missao(d: Dictionary) -> void:
	var m := Missoes.def(d.get("id", ""))
	var nm: String = m.get("titulo", "")
	match d.get("estado", ""):
		"aceita": banner_mostrar("Nova missão", nm, Color("#f0dca0"))
		"concluida":
			banner_mostrar("Missão concluída", nm, Color("#c8f08a"))
			if m.get("texto_conclusao", "") != "": log_msg(m["texto_conclusao"], Color("#c8bfa8"))
		"progresso", "atualizada":
			if d.has("texto"): aviso(d["texto"], Color("#e8dfc9"))

func status(d: Dictionary) -> void:
	pass

func atualizar_cinto() -> void:
	barra.queue_redraw()

# =================================================================== laço
func _process(dt: float) -> void:
	t += dt
	xp_flash = maxf(0.0, xp_flash - dt * 2.0)
	if aviso_t > 0.0:
		aviso_t -= dt
		aviso_lbl.modulate.a = clampf(aviso_t / 0.5, 0.0, 1.0)
	if banner_t > 0.0: banner_t -= dt
	if not canal_d.is_empty():
		canal_t += dt
		if canal_t > float(canal_d.get("dur", 1.0)) + 0.6: canal_d = {}
	if morte_ui and morte_ui.visible: morte_ui.set_meta("t", float(morte_ui.get_meta("t")) + dt); morte_ui.queue_redraw()
	if game.jog == null: return
	barra.queue_redraw(); topo_esq.queue_redraw(); alvo_ui.queue_redraw(); minimapa.queue_redraw(); banner.queue_redraw(); canal_ui.queue_redraw()
	if mapa_ui and mapa_ui.visible: mapa_ui.queue_redraw()
	if Engine.get_process_frames() % 15 == 0: _atualizar_rastreador()
	if tooltip.visible:
		var mp := raiz.get_global_mouse_position()
		var s := tooltip.size
		var p := mp + Vector2(18, -s.y - 10)
		if p.y < 4: p.y = mp.y + 24
		p.x = clampf(p.x, 4, raiz.size.x - s.x - 4)
		p.y = clampf(p.y, 4, raiz.size.y - s.y - 4)
		tooltip.position = p

func _atualizar_rastreador() -> void:
	var j := _jog()
	var s := ""
	var n := 0
	for mid in j.missoes:
		if Missoes.estado(j, mid) != "ativa": continue
		var d := Missoes.def(mid)
		if d.is_empty(): continue
		n += 1
		if n > 4: break
		var principal: bool = d.get("tipo", "") == "principal"
		s += "[b][color=%s]%s[/color][/b]\n" % ["#ffcf7a" if principal else "#e8dfc9", d.get("titulo", mid)]
		if Missoes.pronta(j, mid):
			var ent: String = Missoes.nome_entrega(mid) if str(d.get("entrega", "")) != "automatico" else ""
			s += "[color=#c8f08a]  ◆ Volte a %s[/color]\n" % ent if ent != "" else "[color=#c8f08a]  ◆ Pronta[/color]\n"
			continue
		var objs: Array = d["objetivos"]
		var etapa := Missoes._etapa_atual(j, mid)
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) != etapa: continue
			var pr := Missoes.progresso(j, mid, i)
			var feito: bool = pr[0] >= pr[1]
			var tx := Missoes.texto_objetivo(o)
			if pr[1] > 1: tx += " [b]%d/%d[/b]" % [pr[0], pr[1]]
			s += ("[color=#9cd870]  ◆ %s ✓[/color]\n" % tx) if feito else ("[color=#d8cfb8]  ◆ %s[/color]\n" % tx)
	if s != "": s = "[font_size=15][b][color=#e0b84a]★ MISSÕES[/color][/b][/font_size]\n" + s
	if rastreador.text != s: rastreador.text = s

class_name Tema
## Recursos visuais compartilhados do cliente: fontes, peças da barra de HUD, ícones, cores e caixas de painel.

static var FONTE_TITULO: Font      # Cinzel Bold: números e títulos
static var FONTE_TEXTO: Font       # Spectral Medium: texto corrido (a mesma do site; a IM Fell era difícil de ler)
static var FONTE_ITALICO: Font
static var FONTE_PIXEL: Font       # Silkscreen: números pequenos
static var FONTE_GOTICA: Font      # Pirata One: nomes de zona e chefe
static var UI := {}                # nome -> Texture2D (assets/ext/ui/1x)
static var LAYOUT := {}
static var _tex := {}
static var ICONES := {}            # itens_40 / skills_40 / ... -> {id: [x,y,w,h]}
static var _atlas := {}
static var pronto := false

const COR_TEXTO := Color("#e8dfc9")
const COR_TEXTO_FRACO := Color("#a89f8c")
const COR_OURO := Color("#e0b84a")
const COR_SANGUE := Color("#c8302a")
const COR_AMARGO := Color("#9cff3a")
const COR_PAINEL := Color(0.075, 0.062, 0.052, 0.94)
const COR_BORDA := Color("#6b5634")
const COR_BORDA_CLARA := Color("#b08d4f")

static func carregar() -> void:
	if pronto: return
	pronto = true
	FONTE_TITULO = _fonte("cinzel-bold.woff2")
	FONTE_TEXTO = _fonte("spectral-500-normal.woff2")
	FONTE_ITALICO = _fonte("spectral-500-italic.woff2")
	FONTE_PIXEL = _fonte("silkscreen.woff2")
	FONTE_GOTICA = _fonte("PirataOne-Regular.ttf")
	LAYOUT = Defs.ler("res://assets/ext/ui/layout.json")
	ICONES = Defs.ICONES

static func _fonte(f: String) -> Font:
	var p := "res://assets/fontes/" + f   # fontes do próprio jogo; as do kit da HUD vêm em assets/ext/fontes
	if not ResourceLoader.exists(p): p = "res://assets/ext/fontes/" + f
	if ResourceLoader.exists(p):
		var ff: FontFile = load(p)
		ff.antialiasing = TextServer.FONT_ANTIALIASING_GRAY
		ff.hinting = TextServer.HINTING_LIGHT
		return ff
	return ThemeDB.fallback_font

static func ui(nome: String) -> Texture2D:
	if not UI.has(nome):
		var p := "res://assets/ext/ui/1x/%s.png" % nome
		UI[nome] = load(p) if ResourceLoader.exists(p) else null
	return UI[nome]

static func tex(p: String) -> Texture2D:
	if not _tex.has(p):
		_tex[p] = load(p) if ResourceLoader.exists(p) else null
	return _tex[p]

## Ícone de item ou skill: devolve [Texture2D, Rect2] ou [] se não houver arte.
static func icone_item(id: String, grande := false) -> Array:
	var chave := "itens_64" if grande else "itens_40"
	var tab: Dictionary = ICONES.get(chave, {})
	if tab.has(id):
		var r: Array = tab[id]
		return [_atlas_tex(chave), Rect2(r[0], r[1], r[2], r[3])]
	if id in ICONES.get("mochila", []):
		var t := tex("res://assets/ext/icones/mochila/%s.png" % id)
		if t: return [t, Rect2(Vector2.ZERO, t.get_size())]
	return []

## Ícone da mochila no tamanho da grade (30 px por célula).
static func icone_mochila(id: String) -> Texture2D:
	if id in ICONES.get("mochila", []):
		return tex("res://assets/ext/icones/mochila/%s.png" % id)
	return null

static func icone_skill(classe: String, id: String, grande := false) -> Array:
	var chave := "skills_64" if grande else "skills_40"
	var tab: Dictionary = ICONES.get(chave, {})
	var k := classe + "_" + id
	var sk: Dictionary = Defs.skill(classe, id)
	if not tab.has(k) and sk.has("id"): k = sk["id"]
	if tab.has(k):
		var r: Array = tab[k]
		return [_atlas_tex(chave), Rect2(r[0], r[1], r[2], r[3])]
	return []

static func _atlas_tex(chave: String) -> Texture2D:
	if not _atlas.has(chave):
		var partes := chave.split("_")
		_atlas[chave] = tex("res://assets/ext/icones/atlas_%s_%s.png" % [partes[0], partes[1]])
	return _atlas[chave]

## Painel de ferro e couro (StyleBox) usado nas janelas.
static func caixa(cor := COR_PAINEL, borda := COR_BORDA, largura := 2, raio := 3) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = cor
	s.border_color = borda
	s.set_border_width_all(largura)
	s.set_corner_radius_all(raio)
	s.shadow_color = Color(0, 0, 0, 0.55)
	s.shadow_size = 8
	s.set_content_margin_all(10)
	return s

static func rotulo(txt: String, tam := 14, cor := COR_TEXTO, fonte: Font = null, contorno := 0) -> Label:
	var l := Label.new()
	l.text = txt
	l.add_theme_font_override("font", fonte if fonte else FONTE_TEXTO)
	l.add_theme_font_size_override("font_size", tam)
	l.add_theme_color_override("font_color", cor)
	if contorno > 0:
		l.add_theme_constant_override("outline_size", contorno)
		l.add_theme_color_override("font_outline_color", Color(0.04, 0.03, 0.03))
	return l

## Kit "Ferrugem Sagrada" das janelas (assets/ui/hud/1x/menu_*.png): peça como 9-slice.
## m e cm: margens da textura e do conteúdo, [esq, topo, dir, baixo]. Devolve null se a peça não existir.
static var _sb_ui := {}
static func sb_ui(peca: String, m: Array, cm: Array = []) -> StyleBoxTexture:
	var chave := "%s%s%s" % [peca, m, cm]
	if _sb_ui.has(chave): return _sb_ui[chave]
	var t := ui(peca)
	if t == null: return null
	var sb := StyleBoxTexture.new()
	sb.texture = t
	sb.texture_margin_left = m[0]; sb.texture_margin_top = m[1]; sb.texture_margin_right = m[2]; sb.texture_margin_bottom = m[3]
	if cm.size() == 4:
		sb.content_margin_left = cm[0]; sb.content_margin_top = cm[1]; sb.content_margin_right = cm[2]; sb.content_margin_bottom = cm[3]
	_sb_ui[chave] = sb
	return sb

## Caixa interna (atributos, listas, cartões).
static func caixa_menu(conteudo := 6) -> StyleBox:
	var sb := sb_ui("menu_caixa", [10, 10, 10, 10], [conteudo, conteudo, conteudo, conteudo])
	if sb: return sb
	var c := caixa(Color(0.09, 0.075, 0.06), Color(0.3, 0.25, 0.17), 1, 2); c.set_content_margin_all(conteudo); c.shadow_size = 0
	return c

## Moldura da janela de detalhes do item: ferro gótico com espinhos (item_moldura.png, 360x360, margens 44).
## A peça é uma só: a raridade tinge o ferro (vermelho na Relíquia). Devolve null se a peça não existir.
static func moldura_item(rar: String) -> StyleBoxTexture:
	var base := sb_ui("item_moldura", [44, 44, 44, 44], [50, 50, 50, 48])
	if base == null: return null
	var sb := base.duplicate() as StyleBoxTexture
	sb.modulate_color = Color.WHITE.lerp(Defs.cor_raridade(rar), 0.7)
	return sb

## Aba de janela (Diário, Automático...): ativa fica em latão, colada ao painel.
static func estilo_aba(b: Button, ativa: bool) -> void:
	var n := sb_ui("menu_aba_ativa" if ativa else "menu_aba", [14, 12, 14, 4], [16, 8, 16, 6])
	if n == null: return
	for est in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
		b.add_theme_stylebox_override(est, n if est != "focus" else StyleBoxEmpty.new())
	b.add_theme_color_override("font_color", Color("#f0d48a") if ativa else Color("#9a8c74"))
	b.add_theme_color_override("font_hover_color", Color("#fff2d0"))
	b.add_theme_color_override("font_pressed_color", Color("#f0d48a"))
	b.custom_minimum_size.y = 32

## Botão redondo de fechar (medalhão de latão).
static func estilo_fechar(b: Button) -> void:
	var n := sb_ui("menu_fechar", [0, 0, 0, 0]); var h := sb_ui("menu_fechar_hover", [0, 0, 0, 0])
	if n == null: return
	b.text = ""
	b.add_theme_stylebox_override("normal", n); b.add_theme_stylebox_override("hover", h)
	b.add_theme_stylebox_override("pressed", h); b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.custom_minimum_size = Vector2(28, 28)
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER

## Moldura de ferro e latão para caixas soltas (convite, troca, inspeção, ajuda, legenda do mapa).
## A peça tem cantos de 56 px: a caixa precisa de pelo menos 112 de altura (min_y). Sem a peça, caixa lisa.
static func moldura_popup(cm := [26, 24, 26, 24]) -> StyleBox:
	var sb := sb_ui("menu_moldura", [56, 56, 56, 56], cm)
	if sb: return sb
	var c := caixa(Color(0.06, 0.05, 0.04, 0.94), Color(0.6, 0.5, 0.3), 2, 3); c.set_content_margin_all(12)
	return c

## Moldura fina de latão (a do tooltip) para menus pequenos, como o do botão direito num jogador.
static func moldura_dica() -> StyleBox:
	var sb := sb_ui("menu_dica", [18, 18, 18, 18], [14, 11, 14, 12])
	if sb: return sb
	var c := caixa(Color(0.05, 0.04, 0.035, 0.96), Color(0.55, 0.44, 0.26), 1, 2); c.set_content_margin_all(10)
	return c

static func tema_janelas() -> Theme:
	var t := Theme.new()
	t.default_font = FONTE_TEXTO
	t.default_font_size = 15
	t.set_color("font_color", "Label", COR_TEXTO)
	t.set_color("default_color", "RichTextLabel", COR_TEXTO)
	var b := caixa(Color(0.16, 0.12, 0.08), COR_BORDA, 1, 2)
	b.set_content_margin_all(6); b.shadow_size = 0
	var bh := caixa(Color(0.26, 0.19, 0.11), COR_BORDA_CLARA, 1, 2)
	bh.set_content_margin_all(6); bh.shadow_size = 0
	var bp := caixa(Color(0.1, 0.07, 0.05), COR_BORDA_CLARA, 1, 2)
	bp.set_content_margin_all(6); bp.shadow_size = 0
	var bd := caixa(Color(0.1, 0.09, 0.08), Color(0.25, 0.22, 0.2), 1, 2)
	bd.set_content_margin_all(6); bd.shadow_size = 0
	var cm := [16, 6, 16, 9]
	if ui("menu_botao"):   # botões em relevo do kit
		var kp := sb_ui("menu_botao_press", [14, 14, 14, 14], [16, 7, 16, 8])
		t.set_stylebox("normal", "Button", sb_ui("menu_botao", [14, 14, 14, 14], cm))
		t.set_stylebox("hover", "Button", sb_ui("menu_botao_hover", [14, 14, 14, 14], cm))
		t.set_stylebox("pressed", "Button", kp); t.set_stylebox("hover_pressed", "Button", kp)
		t.set_stylebox("disabled", "Button", sb_ui("menu_botao_off", [14, 14, 14, 14], cm))
		t.set_color("font_pressed_color", "Button", Color("#ffd58a"))
		t.set_color("font_color", "Button", Color("#e8d4a4"))
		t.set_constant("outline_size", "Button", 3)
		t.set_color("font_outline_color", "Button", Color(0, 0, 0, 0.85))
	else:
		t.set_stylebox("normal", "Button", b)
		t.set_stylebox("hover", "Button", bh)
		t.set_stylebox("pressed", "Button", bp)
		t.set_stylebox("disabled", "Button", bd)
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	if not ui("menu_botao"): t.set_color("font_color", "Button", COR_TEXTO)
	t.set_color("font_hover_color", "Button", Color("#fff2d0"))
	t.set_color("font_disabled_color", "Button", Color("#6d665c"))
	t.set_font("font", "Button", FONTE_TITULO)
	t.set_font_size("font_size", "Button", 13)
	t.set_stylebox("panel", "PanelContainer", caixa_menu() if ui("menu_caixa") else caixa())
	t.set_stylebox("panel", "Panel", caixa_menu() if ui("menu_caixa") else caixa())
	var sb := StyleBoxFlat.new(); sb.bg_color = Color(0.3, 0.24, 0.16); sb.set_corner_radius_all(2)
	t.set_stylebox("grabber_area", "VScrollBar", sb)
	t.set_stylebox("grabber", "VScrollBar", sb)
	var sbs := StyleBoxFlat.new(); sbs.bg_color = Color(0.08, 0.06, 0.05)
	t.set_stylebox("scroll", "VScrollBar", sbs)
	var tri := sb_ui("menu_rolagem_trilho", [0, 8, 0, 8]); var peg := sb_ui("menu_rolagem_pegador", [0, 12, 0, 12])
	if tri and peg:
		t.set_stylebox("scroll", "VScrollBar", tri)
		for e in ["grabber", "grabber_highlight", "grabber_pressed"]: t.set_stylebox(e, "VScrollBar", peg)
	return t

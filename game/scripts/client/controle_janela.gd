class_name ControleJanela
## Tela "Controle": qual controle está ligado, ajustes (ícones, zona morta, cursor, vibração, canhoto) e a lista
## de botões. Trocar um botão = clicar em "Trocar" e apertar o botão novo no controle (segurando LT vale combinação).
## Entra como aba do menu de configurações (Ajustes.registrar_aba, thread "Menu de configurações") quando ele existe;
## senão abre como janela própria pelo menu do Esc.

const AJ := "res://scripts/client/ajustes.gd"
const ZONAS := [0.12, 0.17, 0.22, 0.28, 0.35]
const VELS := [0.6, 0.8, 1.0, 1.25, 1.5, 2.0]
const VIBS := [0.0, 0.4, 0.8, 1.0]
const ICONES := [["auto", "Automático"], ["xbox", "Xbox"], ["ps", "PlayStation"]]
const COR_SECAO := Color("#c9a860")
const COR_DICA := Color("#a89f8c")

static var _corpo: VBoxContainer
static var _menu = null
static var _esperando := ""

static func registrar_aba() -> void:
	if not ResourceLoader.exists(AJ): return
	var a = load(AJ)
	if a.has_method("registrar_aba"):
		a.registrar_aba("controle", "Controle", func(corpo: VBoxContainer, menu) -> void: construir(corpo, menu))

## Sem o menu de configurações: janela própria (aberta pelo menu do Esc).
static func abrir(game) -> void:
	var c: VBoxContainer = game.janelas._janela("controle", "CONTROLE", Vector2(620, 600), "centro")
	construir(c, null)

static func construir(corpo: VBoxContainer, menu) -> void:
	_corpo = corpo; _menu = menu
	for f in corpo.get_children(): corpo.remove_child(f); f.queue_free()
	var ct: Controle = Controle.inst
	if ct == null:
		corpo.add_child(_dica("O controle não foi iniciado.")); return
	var no_menu: bool = menu != null and menu.has_method("linha_seletor_f")
	# --- estado
	_secao(corpo, "Controle")
	var lig := ct.disp >= 0
	var st := Tema.rotulo(("%s · conectado" % (ct.nome_disp if ct.nome_disp != "" else "Controle")) if lig else "Nenhum controle conectado. Ligue um controle Xbox (ou PlayStation) e aperte qualquer botão.",
		14, Color("#e8d29a") if lig else COR_DICA, Tema.FONTE_TEXTO if lig else Tema.FONTE_ITALICO)
	st.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if no_menu:   # mesmo recuo das linhas do menu
		var mg := MarginContainer.new(); mg.add_theme_constant_override("margin_left", 14)
		mg.add_child(st); corpo.add_child(mg)
	else: corpo.add_child(st)
	# --- ajustes
	_secao(corpo, "Ajustes")
	var aj: Dictionary = ct.ajustes
	var pct := func(lista: Array) -> Array:
		var r := []
		for v in lista: r.append([v, "desligada" if float(v) <= 0.0 else "%d%%" % roundi(float(v) * 100.0)])
		return r
	var opcoes := [
		["icones", "Ícones dos botões", "Automático escolhe pelo nome do controle.", ICONES],
		["canhoto", "Mão", "Canhota troca a função dos dois sticks.", [[false, "Destra"], [true, "Canhota"]]],
		["zona_morta", "Zona morta dos sticks", "Aumente se o personagem anda sozinho com o stick solto.", pct.call(ZONAS)],
		["cursor_vel", "Velocidade do cursor", "Cursor das janelas e menus.", pct.call(VELS)],
		["vibracao", "Vibração", "Golpe recebido, morte e chefe abatido.", pct.call(VIBS)],
	]
	if no_menu:   # no menu de configurações: seletores do próprio menu (◄ valor ►, navegáveis pelo D-pad)
		for o in opcoes:
			var k: String = o[0]
			menu.linha_seletor_f(o[1], o[2], o[3], func(): return ct.ajustes[k], func(v):
				ct.ajustes[k] = v; ct.salvar()
				if k == "vibracao": Controle.vibrar(0.4, 0.7, 0.25)
				if k == "icones": _refazer())
		var br := _botao("Restaurar o padrão do controle", func(): ct.restaurar_padrao(); _refazer())
		corpo.add_child(br)
	else:
		var g := GridContainer.new(); g.columns = 2
		g.add_theme_constant_override("h_separation", 8); g.add_theme_constant_override("v_separation", 6)
		for o in opcoes:
			var k: String = o[0]
			var nome := str(aj[k])
			for par in o[3]:
				if str(par[0]) == str(aj[k]): nome = par[1]
			var lista: Array = o[3]
			g.add_child(_botao("%s: %s" % [o[1], nome], func():
				var idx := 0
				for n in lista.size():
					if str(lista[n][0]) == str(ct.ajustes[k]): idx = n
				_mudar(k, lista[(idx + 1) % lista.size()][0])
				if k == "vibracao": Controle.vibrar(0.4, 0.7, 0.25)))
		g.add_child(_botao("Restaurar o padrão", func(): ct.restaurar_padrao(); _refazer()))
		for b in g.get_children(): b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		corpo.add_child(g)
	# --- botões (dentro do menu ele já rola; na janela própria, uma lista com rolagem)
	_secao(corpo, "Botões")
	var lista_v := VBoxContainer.new(); lista_v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lista_v.add_theme_constant_override("separation", 3)
	if no_menu:
		corpo.add_child(lista_v)
	else:
		var sc := ScrollContainer.new()
		sc.custom_minimum_size = Vector2(0, 220); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
		sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		sc.add_child(lista_v)
		corpo.add_child(sc)
	var grupo := ""
	for a in Controle.ACOES:
		if a[2] != grupo:
			grupo = a[2]
			var gl := Tema.rotulo(grupo, 12, Color("#8f7f60"), Tema.FONTE_TITULO, 2)
			if lista_v.get_child_count() > 0: gl.custom_minimum_size.y = 22
			gl.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
			lista_v.add_child(gl)
		lista_v.add_child(_linha_acao(ct, a))
	# --- como funciona
	var d := _dica("Andando: stick esquerdo anda, stick direito mira (sem mexer, a mira pega o inimigo mais perto à sua frente). Segure LT para a segunda camada de botões.\nCom janela aberta: o stick leva o cursor, A clica, X é o botão direito, B volta, LB segurado deixa o cursor fino, stick direito rola. O D-pad navega nos menus.")
	d.custom_minimum_size.x = 540
	var sep := Control.new(); sep.custom_minimum_size.y = 8
	lista_v.add_child(sep); lista_v.add_child(d)

static func _linha_acao(ct: Controle, a: Array) -> Control:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 8)
	h.custom_minimum_size.y = 30
	var l := Tema.rotulo(a[1], 13, Color("#e6dcc6"), Tema.FONTE_TEXTO)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.clip_text = true
	h.add_child(l)
	var bt: String = ct.mapa.get(a[0], "")
	var gl := HBoxContainer.new(); gl.add_theme_constant_override("separation", 2)
	gl.custom_minimum_size.x = 64; gl.alignment = BoxContainer.ALIGNMENT_END
	for tx in ct.glifos(bt, true):
		var tr := TextureRect.new(); tr.texture = tx
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.custom_minimum_size = Vector2(28, 28)
		gl.add_child(tr)
	gl.tooltip_text = ct.nome_botao(bt)
	h.add_child(gl)
	var b := Button.new(); b.custom_minimum_size = Vector2(132, 28)
	b.add_theme_font_size_override("font_size", 12)
	b.text = "Aperte o botão…" if _esperando == a[0] else "Trocar"
	if _esperando == a[0]: b.add_theme_color_override("font_color", Color("#f0d48a"))
	var id: String = a[0]
	b.pressed.connect(func():
		_som()
		if _esperando == id:   # clicar de novo cancela
			_esperando = ""; ct.capturar(Callable()); _refazer(); return
		if ct.disp < 0:
			b.text = "Sem controle"; return
		_esperando = id
		ct.capturar(func(novo: String):
			_esperando = ""
			if novo != "": ct.definir(id, novo)
			_refazer())
		_refazer())
	h.add_child(b)
	return h

static func _mudar(k: String, v) -> void:
	var ct := Controle.inst
	ct.ajustes[k] = v
	ct.salvar()
	_refazer()

static func _refazer() -> void:
	if is_instance_valid(_corpo): construir.call_deferred(_corpo, _menu)

static func _secao(corpo: Control, txt: String) -> void:
	if _menu != null and _menu.has_method("secao"): _menu.secao(txt, corpo); return
	var l := Tema.rotulo(txt.to_upper(), 13, COR_SECAO, Tema.FONTE_TITULO, 2)
	l.custom_minimum_size.y = 18
	corpo.add_child(l)

static func _dica(txt: String) -> Label:
	var l := Tema.rotulo(txt, 12, COR_DICA, Tema.FONTE_ITALICO)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = 560
	return l

static func _botao(txt: String, acao: Callable) -> Button:
	var b := Button.new(); b.text = txt; b.custom_minimum_size = Vector2(0, 30)
	b.add_theme_font_size_override("font_size", 13)
	b.clip_text = true
	b.pressed.connect(func(): _som(); acao.call())
	return b

static func _som() -> void:
	var ct := Controle.inst
	if ct == null: return
	var g := ct._game()
	if g != null: g.audio.tocar("ui/clique", null, -6.0)

class_name Configuracoes
extends CanvasLayer
## Menu de configurações: Vídeo, Áudio, Jogo, Atalhos (+ abas registradas por outras partes, ex.: Controle).
## Abre pelo menu Esc ("Configurações") ou F10 em qualquer tela. Tudo vale na hora e fica em user://ajustes.cfg (Ajustes).
## Para outra aba usar o mesmo visual: secao(), linha_slider(), linha_chave(), linha_seletor(), linha_teclas().

static var aberto: Configuracoes
static var audio: Node              # som do jogo (o game.gd liga; na tela de abertura fica null)

const LARG := 700.0
const ALT := 612.0
const LARG_CONTROLE := 268.0
const ABAS_BASE := [["video", "Vídeo"], ["audio", "Áudio"], ["jogo", "Jogo"]]

var ao_fechar: Callable
var painel: PanelContainer
var abas_box: HBoxContainer
var corpo: VBoxContainer
var rolagem: ScrollContainer
var restaurar_b: Button
var aba := "video"
var _botoes_aba := {}
var _chaves_aba: Array = []

static func abrir(de: Node, ao_fechar_cb := Callable()) -> void:
	if esta_aberto(): return
	var c := Configuracoes.new()
	c.ao_fechar = ao_fechar_cb
	de.get_tree().root.add_child(c)
	aberto = c

static func alternar(de: Node) -> void:
	if esta_aberto(): aberto.fechar()
	else: abrir(de)

static func esta_aberto() -> bool:
	return aberto != null and is_instance_valid(aberto) and not aberto.is_queued_for_deletion()

func _ready() -> void:
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	Tema.carregar()
	var fundo := ColorRect.new()
	fundo.color = Color(0.02, 0.015, 0.01, 0.55)
	fundo.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fundo.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(fundo)
	var raiz := Control.new()
	raiz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = Tema.tema_janelas()
	add_child(raiz)
	painel = PanelContainer.new()
	var sb: StyleBox = Tema.sb_ui("menu_moldura", [56, 56, 56, 56], [24, 18, 24, 22])
	if sb == null: sb = Tema.caixa(); sb.set_content_margin_all(18)
	painel.add_theme_stylebox_override("panel", sb)
	painel.set_anchors_preset(Control.PRESET_CENTER)
	painel.offset_left = -LARG * 0.5; painel.offset_right = LARG * 0.5
	painel.offset_top = -ALT * 0.5 - 30; painel.offset_bottom = ALT * 0.5 - 30   # acima da barra de skills
	painel.mouse_filter = Control.MOUSE_FILTER_STOP
	raiz.add_child(painel)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	painel.add_child(v)
	# título em placa de latão + medalhão de fechar
	var topo := HBoxContainer.new()
	var tl := Tema.rotulo("CONFIGURAÇÕES", 20, Color("#e0c890"), Tema.FONTE_TITULO, 3)
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var placa := Tema.sb_ui("menu_titulo", [60, 0, 60, 0], [44, 3, 44, 7])
	if placa: tl.add_theme_stylebox_override("normal", placa); tl.custom_minimum_size.y = 40
	topo.add_child(tl)
	var x := Button.new(); x.text = "✕"; x.focus_mode = Control.FOCUS_NONE
	Tema.estilo_fechar(x)
	x.pressed.connect(fechar)
	topo.add_child(x)
	v.add_child(topo)
	var ep := Tema.rotulo("“Acerte a chama do lampião antes de descer. Lá embaixo ninguém ajusta nada.”", 13, Color("#8f8470"), Tema.FONTE_ITALICO)
	ep.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(ep)
	# abas
	abas_box = HBoxContainer.new()
	abas_box.add_theme_constant_override("separation", 4)
	var mg := MarginContainer.new(); mg.add_theme_constant_override("margin_left", 6)
	mg.add_child(abas_box)
	v.add_child(mg)
	# corpo rolável numa caixa funda
	var caixa := PanelContainer.new()
	caixa.add_theme_stylebox_override("panel", Tema.caixa_menu(4))
	caixa.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(caixa)
	rolagem = ScrollContainer.new()
	rolagem.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	rolagem.follow_focus = true
	rolagem.get_v_scroll_bar().custom_minimum_size.x = 12   # as peças de rolagem do kit não têm largura mínima
	caixa.add_child(rolagem)
	corpo = VBoxContainer.new()
	corpo.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	corpo.add_theme_constant_override("separation", 0)
	rolagem.add_child(corpo)
	# rodapé
	var rp := HBoxContainer.new()
	rp.add_theme_constant_override("separation", 8)
	var nota := Tema.rotulo("Vale na hora · fica salvo neste computador", 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	nota.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	nota.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	rp.add_child(nota)
	restaurar_b = Button.new(); restaurar_b.text = "Restaurar padrões"; restaurar_b.custom_minimum_size = Vector2(170, 38)
	restaurar_b.pressed.connect(func():
		Ajustes.restaurar(_chaves_aba); _som("ui/confirmar"); mostrar(aba))
	rp.add_child(restaurar_b)
	var ok := Button.new(); ok.text = "Pronto"; ok.custom_minimum_size = Vector2(120, 38)
	ok.pressed.connect(fechar)
	rp.add_child(ok)
	v.add_child(rp)
	_montar_abas()
	mostrar("video")
	_som("ui/abrir_janela")
	painel.pivot_offset = Vector2(LARG, ALT) * 0.5
	painel.modulate.a = 0.0; painel.scale = Vector2(0.97, 0.97)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(painel, "modulate:a", 1.0, 0.14)
	tw.tween_property(painel, "scale", Vector2.ONE, 0.16).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	(_botoes_aba["video"] as Button).grab_focus.call_deferred()

func fechar() -> void:
	if is_queued_for_deletion(): return
	_som("ui/fechar_janela")
	if aberto == self: aberto = null
	queue_free()
	if ao_fechar.is_valid(): ao_fechar.call()

## Teclas não vazam para o jogo embaixo (I, M, skills...). Esc / B do controle fecha.
func _unhandled_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("ui_cancel"): fechar(); get_viewport().set_input_as_handled(); return
	if ev is InputEventKey or ev is InputEventMouseButton or ev is InputEventJoypadButton:
		get_viewport().set_input_as_handled()

func _som(n: String) -> void:
	if audio != null and is_instance_valid(audio): audio.tocar(n, null, -6.0)

# =================================================================== abas
func _lista_abas() -> Array:
	var l := ABAS_BASE.duplicate()
	for a in Ajustes.abas: l.append([a["id"], a["titulo"]])
	l.append(["atalhos", "Atalhos"])
	return l

func _montar_abas() -> void:
	for a in _lista_abas():
		var b := Button.new()
		b.text = a[1]
		var ic := Tema.ui("menu_aba_icone_" + a[0])
		if ic: b.icon = ic; b.add_theme_constant_override("h_separation", 6)
		b.focus_mode = Control.FOCUS_ALL
		var id: String = a[0]
		b.pressed.connect(func(): if aba != id: _som("ui/pagina"); mostrar(id))
		abas_box.add_child(b)
		_botoes_aba[id] = b

func mostrar(id: String) -> void:
	aba = id
	for k in _botoes_aba: Tema.estilo_aba(_botoes_aba[k], k == id)
	for f in corpo.get_children(): corpo.remove_child(f); f.queue_free()
	_chaves_aba = []
	match id:
		"video": _aba_video()
		"audio": _aba_audio()
		"jogo": _aba_jogo()
		"atalhos": _aba_atalhos()
		_:
			for a in Ajustes.abas:
				if a["id"] == id and (a["construtor"] as Callable).is_valid(): a["construtor"].call(corpo, self)
	restaurar_b.disabled = _chaves_aba.is_empty()
	rolagem.scroll_vertical = 0

func _aba_video() -> void:
	if not Ajustes.web():
		secao("Tela")
		var cheia := Tela.cheia()
		linha_seletor_f("Modo de tela", "Tela cheia cobre o monitor inteiro. F11 alterna em qualquer hora.",
			[[false, "Janela"], [true, "Tela cheia"]], Tela.cheia, func(x):
				Tela.definir(bool(x))
				if not x: Ajustes.aplicar_janela()
				mostrar.call_deferred("video"))
		linha_seletor("Tamanho da janela", "Só vale no modo janela.", "janela",
			[["1280x720", "1280 × 720"], ["1600x900", "1600 × 900"], ["1920x1080", "1920 × 1080"]], not cheia)
		linha_chave("Sincronia vertical", "Evita a imagem rasgando. Desligue se sentir o mouse atrasado.", "vsync")
		linha_seletor("Limite de quadros", "Menos quadros, PC mais frio e silencioso.", "fps_max",
			[[30, "30 por segundo"], [60, "60 por segundo"], [120, "120 por segundo"], [144, "144 por segundo"], [0, "Sem limite"]])
	secao("Imagem")
	linha_slider("Brilho", "Ajuste até o segundo quadrado da régua mal aparecer.", "brilho", 0.6, 1.6, 0.05)
	_linha_regua()
	linha_seletor("Qualidade da luz", "Leve usa um mapa de luz menor. Ajuda em PC fraco.", "luz", [["alta", "Alta"], ["leve", "Leve"]])
	linha_chave("Poeira do Amargo", "O pó verde e a cinza que correm sobre o deserto.", "clima")
	linha_chave("Vinheta", "Escurece as bordas da tela, como lampião no breu.", "vinheta")

func _aba_audio() -> void:
	secao("Volume")
	linha_slider("Geral", "Tudo de uma vez.", "vol_geral", 0.0, 1.0, 0.05)
	linha_slider("Música", "Trilhas das áreas, da cripta e dos chefes.", "vol_musica", 0.0, 1.0, 0.05)
	linha_slider("Ambiente", "Vento, rio, fogueiras, o Geiger.", "vol_ambiente", 0.0, 1.0, 0.05)
	linha_slider("Efeitos", "Golpes, tiros, magias, passos e monstros.", "vol_efeitos", 0.0, 1.0, 0.05, "ui/clique")
	linha_slider("Interface", "Cliques, janelas e avisos.", "vol_interface", 0.0, 1.0, 0.05, "ui/clique")
	secao("Outros")
	linha_chave("Silenciar tudo", "Corta o som sem perder os volumes acima.", "mudo")
	linha_chave("Som em segundo plano", "Desligado, o jogo fica mudo quando você troca de janela.", "som_fundo")

func _aba_jogo() -> void:
	secao("Combate")
	linha_slider("Tremor de tela", "Golpes fortes, explosões e chefes sacodem a câmera.", "tremor", 0.0, 1.0, 0.05)
	linha_chave("Números de dano e cura", "Os números que saltam de quem apanha ou se cura.", "numeros")
	linha_chave("Barras de vida sempre", "Senão, só no alvo, sob o mouse e em quem já está ferido.", "barras_sempre")
	secao("Mundo")
	linha_chave("Nomes sempre visíveis", "Senão, segure Alt para ler NPCs, monstros e itens no chão.", "nomes_sempre")

func _aba_atalhos() -> void:
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 18)
	corpo.add_child(cols)
	var grupos := [
		[["Combate", [["Andar / atacar", "Clique"], ["Habilidades", "1 … 9"], ["Habilidade 1", "Direito"], ["Poção de vida", "Q"],
			["Poção de recurso", "W"], ["Antídoto", "E"], ["Voltar ao acampamento", "R"], ["Modo automático", "Z"], ["Ajustes do automático", "Shift Z"]]],
		 ["Tela", [["Configurações", "F10"], ["Tela cheia", "F11"], ["Menu", "Esc"]]]],
		[["Janelas", [["Mochila", "I"], ["Personagem", "C"], ["Habilidades", "K"], ["Talentos", "T"], ["Missões", "J"], ["Mapa", "M"], ["Teleporte", "V"]]],
		 ["Mundo", [["Mostrar nomes", "Alt"], ["Chat", "Enter"], ["Como jogar", "H"]]]],
	]
	for col in grupos:
		var cv := VBoxContainer.new()
		cv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cv.add_theme_constant_override("separation", 0)
		cols.add_child(cv)
		for g in col:
			secao(g[0], cv)
			for it in g[1]: linha_teclas(it[0], it[1], cv)

# =================================================================== construtores (públicos: outras abas usam)
func secao(titulo: String, onde: Control = null) -> void:
	var alvo := onde if onde else corpo
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", -2)
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 12); m.add_theme_constant_override("margin_top", 8 if alvo.get_child_count() == 0 else 16)
	var l := Tema.rotulo(titulo, 22, Color("#d8b878"), Tema.FONTE_GOTICA, 3)
	m.add_child(l)
	v.add_child(m)
	var div := Tema.ui("menu_divisor")
	if div:
		var tr := TextureRect.new()
		tr.texture = div
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_SCALE
		tr.custom_minimum_size = Vector2(0, 14)
		v.add_child(tr)
	alvo.add_child(v)

## Linha: nome e dica à esquerda, controle à direita; acende em latão com o mouse ou o foco do controle.
func _linha(rotulo: String, dica: String, controle: Control, onde: Control = null) -> PanelContainer:
	var pc := PanelContainer.new()
	var normal := StyleBoxEmpty.new()
	normal.content_margin_left = 14; normal.content_margin_right = 12; normal.content_margin_top = 5; normal.content_margin_bottom = 5
	var luz: StyleBox = Tema.sb_ui("menu_linha_hover", [16, 16, 16, 16], [14, 5, 12, 5])
	pc.add_theme_stylebox_override("panel", normal)
	pc.mouse_filter = Control.MOUSE_FILTER_PASS
	var acender := func(sim: bool): pc.add_theme_stylebox_override("panel", luz if sim and luz else normal)
	pc.mouse_entered.connect(acender.bind(true))
	pc.mouse_exited.connect(func(): if not pc.get_global_rect().has_point(pc.get_global_mouse_position()): acender.call(false))
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 12)
	pc.add_child(h)
	var esq := VBoxContainer.new()
	esq.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	esq.alignment = BoxContainer.ALIGNMENT_CENTER
	esq.add_theme_constant_override("separation", -1)
	esq.add_child(Tema.rotulo(rotulo, 16, Tema.COR_TEXTO))
	if dica != "":
		var d := Tema.rotulo(dica, 12, Color("#8f8470"), Tema.FONTE_ITALICO)
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		esq.add_child(d)
	h.add_child(esq)
	controle.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(controle)
	# foco (teclado/controle) em qualquer peça da linha acende a linha
	for n in [controle] + controle.find_children("*", "Control", true, false):
		if (n as Control).focus_mode != Control.FOCUS_NONE:
			n.focus_entered.connect(acender.bind(true)); n.focus_exited.connect(acender.bind(false))
	(onde if onde else corpo).add_child(pc)
	return pc

func linha_slider(rotulo: String, dica: String, chave: String, mn: float, mx: float, passo: float, som := "") -> HSlider:
	_chaves_aba.append(chave)
	var h := HBoxContainer.new()
	h.custom_minimum_size.x = LARG_CONTROLE
	h.add_theme_constant_override("separation", 10)
	var s := HSlider.new()
	s.min_value = mn; s.max_value = mx; s.step = passo
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	s.focus_mode = Control.FOCUS_ALL
	var tri := Tema.sb_ui("menu_deslizador_trilho", [12, 0, 12, 0], [12, 9, 12, 9])
	var che := Tema.sb_ui("menu_deslizador_cheio", [12, 0, 12, 0], [12, 9, 12, 9])
	if tri and che:
		s.add_theme_stylebox_override("slider", tri)
		s.add_theme_stylebox_override("grabber_area", che)
		s.add_theme_stylebox_override("grabber_area_highlight", che)
		s.add_theme_icon_override("grabber", Tema.ui("menu_deslizador_pegador"))
		s.add_theme_icon_override("grabber_highlight", Tema.ui("menu_deslizador_pegador_hover"))
	s.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	s.value = float(Ajustes.v(chave))
	var val := Tema.rotulo("", 14, Color("#f0d48a"), Tema.FONTE_TITULO, 2)
	val.custom_minimum_size.x = 48
	val.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var txt := func(x: float): val.text = "%d%%" % roundi(x * 100.0)
	txt.call(s.value)
	s.value_changed.connect(func(x: float): Ajustes.definir(chave, x); txt.call(x))
	if som != "": s.drag_ended.connect(func(_m): _som(som))
	h.add_child(s); h.add_child(val)
	_linha(rotulo, dica, h)
	return s

func linha_chave(rotulo: String, dica: String, chave: String) -> TextureButton:
	_chaves_aba.append(chave)
	var h := HBoxContainer.new()
	h.custom_minimum_size.x = LARG_CONTROLE
	h.alignment = BoxContainer.ALIGNMENT_END
	h.add_theme_constant_override("separation", 10)
	var est := Tema.rotulo("", 13, Color("#9a8c74"), Tema.FONTE_TITULO, 2)
	var b := TextureButton.new()
	b.toggle_mode = true
	b.focus_mode = Control.FOCUS_ALL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var pintar := func(lig: bool):
		var n := "menu_chave_lig" if lig else "menu_chave_desl"
		b.texture_normal = Tema.ui(n); b.texture_pressed = Tema.ui(n)
		b.texture_hover = Tema.ui(n + "_hover"); b.texture_focused = Tema.ui(n + "_hover")
		est.text = "LIGADO" if lig else "DESLIGADO"
		est.add_theme_color_override("font_color", Color("#f0c070") if lig else Color("#7d7466"))
	b.set_pressed_no_signal(bool(Ajustes.v(chave)))
	pintar.call(b.button_pressed)
	b.toggled.connect(func(lig: bool): Ajustes.definir(chave, lig); pintar.call(lig); _som("ui/clique"))
	if Tema.ui("menu_chave_lig") == null:   # sem as peças: botão do kit
		b.custom_minimum_size = Vector2(66, 28)
	h.add_child(est); h.add_child(b)
	_linha(rotulo, dica, h)
	return b

func linha_seletor(rotulo: String, dica: String, chave: String, opcoes: Array, ativo := true) -> Control:
	_chaves_aba.append(chave)
	return linha_seletor_f(rotulo, dica, opcoes, func(): return Ajustes.v(chave), func(x): Ajustes.definir(chave, x), ativo)

## Seletor ◀ valor ▶ com leitura e escrita livres (o modo de tela usa a classe Tela).
func linha_seletor_f(rotulo: String, dica: String, opcoes: Array, ler: Callable, escrever: Callable, ativo := true) -> Control:
	var h := HBoxContainer.new()
	h.custom_minimum_size.x = LARG_CONTROLE
	h.add_theme_constant_override("separation", 4)
	h.focus_mode = Control.FOCUS_ALL if ativo else Control.FOCUS_NONE
	var atual = ler.call()
	var idx := 0
	for i in opcoes.size():
		if opcoes[i][0] == atual: idx = i
	var caixa := Tema.rotulo(opcoes[idx][1], 14, Color("#e8d4a4"), Tema.FONTE_TITULO, 2)
	caixa.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	caixa.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caixa.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	caixa.add_theme_stylebox_override("normal", Tema.caixa_menu(5))
	caixa.custom_minimum_size.y = 30
	var estado := {"i": idx}
	var passo := func(d: int):
		if not ativo: return
		estado["i"] = posmod(int(estado["i"]) + d, opcoes.size())
		caixa.text = opcoes[estado["i"]][1]
		_som("ui/clique")
		escrever.call(opcoes[estado["i"]][0])
	var seta := func(lado: String, d: int) -> TextureButton:
		var b := TextureButton.new()
		b.texture_normal = Tema.ui("menu_seletor_" + lado); b.texture_hover = Tema.ui("menu_seletor_%s_hover" % lado)
		b.texture_pressed = b.texture_hover
		b.focus_mode = Control.FOCUS_NONE
		b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		b.pressed.connect(passo.bind(d))
		return b
	h.add_child(seta.call("esq", -1)); h.add_child(caixa); h.add_child(seta.call("dir", 1))
	h.gui_input.connect(func(ev: InputEvent):
		if ev.is_action_pressed("ui_left"): passo.call(-1); h.accept_event()
		elif ev.is_action_pressed("ui_right") or ev.is_action_pressed("ui_accept"): passo.call(1); h.accept_event())
	if not ativo: h.modulate = Color(1, 1, 1, 0.4)
	_linha(rotulo, dica, h)
	return h

## Ação e tecla(s) em teclas de máquina de escrever. "Shift Z" vira duas teclas.
func linha_teclas(acao: String, teclas: String, onde: Control = null) -> void:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 3)
	var sb := Tema.sb_ui("menu_tecla", [12, 12, 12, 12], [9, 3, 9, 9])
	var partes := [teclas] if teclas.contains("…") else Array(teclas.split(" "))
	for i in partes.size():
		var k := Tema.rotulo(partes[i].to_upper(), 12, Color("#24170b"), Tema.FONTE_TITULO)
		k.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		k.custom_minimum_size = Vector2(34, 28)
		if sb: k.add_theme_stylebox_override("normal", sb)
		h.add_child(k)
	var pc := _linha(acao, "", h, onde)
	pc.custom_minimum_size.y = 36

## Régua de cinzas para acertar o brilho (o próprio desenho recebe a mesma curva do jogo).
func _linha_regua() -> void:
	var t := Tema.ui("menu_brilho_ref")
	if t == null: return
	var tr := TextureRect.new()
	tr.texture = t
	tr.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	tr.custom_minimum_size = Vector2(LARG_CONTROLE, 40)
	var sh := Shader.new()
	sh.code = "shader_type canvas_item;\nuniform float gama = 1.0;\nvoid fragment() { vec4 c = texture(TEXTURE, UV); COLOR = vec4(pow(c.rgb, vec3(1.0 / gama)), c.a); }"
	var m := ShaderMaterial.new(); m.shader = sh
	m.set_shader_parameter("gama", float(Ajustes.v("brilho")))
	tr.material = m
	var f := func(chave: String, valor): if chave == "brilho": m.set_shader_parameter("gama", float(valor))
	Ajustes.sinais.mudou.connect(f)
	tr.tree_exiting.connect(func(): if Ajustes.sinais.mudou.is_connected(f): Ajustes.sinais.mudou.disconnect(f))
	_linha("Régua", "Do breu ao osso: oito tons.", tr)

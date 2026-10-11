extends Control
## Launcher do DARK PASSAGE: notícias e crônicas, versão instalada contra a do servidor,
## baixa e atualiza o cliente (cliente.json do site) e abre o jogo.
##
## Argumentos (depois de --): pasta=DIR (onde fica jogo/), manifesto=URL, noticias=URL, fotos=ARQ.png (tira um print e sai).

const VERSAO_LAUNCHER := "1.1"

const C_OSSO := Color("#e8dfc9")
const C_FRACO := Color("#a89f8c")
const C_APAGADO := Color("#6f6556")
const C_OURO := Color("#e0b84a")
const C_OURO_CLARO := Color("#ffe1a0")
const C_AMARGO := Color("#9cff3a")
const C_SANGUE := Color("#d8452f")

var cfg := {}
var args := {}
var noticias := {}
var remoto := {}               # cliente.json do site
var estado := "conectando"     # conectando, offline, instalar, atualizar, baixando, conferindo, extraindo, pronto, erro
var aba := "noticias"
var at: Atualizador

var F_TITULO: Font
var F_TITULO_LARGO: Font
var F_TEXTO: Font
var F_ITALICO: Font
var F_GOTICA: Font

var _texto_noticias: RichTextLabel
var _abas := {}
var _lbl_status: Label
var _ponto_status: Ponto
var _lbl_instalada: Label
var _lbl_servidor: Label
var _lbl_estado: Label
var _lbl_bytes: Label
var _lbl_detalhe: Label
var _barra: Barra
var _jogar: TextureButton
var _lbl_jogar: Label
var _botoes := {}
var _gema: Sprite2D
var _sons := {}
var _arrastando := false
var _arrasto_ini := Vector2i.ZERO
var _vel_amostras: Array = []  # [tempo, bytes] para a velocidade do download
var _erro_msg := ""

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	cfg = _ler_json("res://dados/config.json")
	noticias = _ler_json("res://dados/noticias.json")
	_carregar_fontes()
	for s in ["clique_1", "passar_mouse_1", "confirmar", "erro", "notificacao"]:
		var p := AudioStreamPlayer.new()
		p.stream = load("res://sons/%s.ogg" % s)
		p.volume_db = -10.0 if s == "passar_mouse_1" else -4.0
		add_child(p)
		_sons[s] = p
	at = Atualizador.new()
	at.base = _pasta_base()
	add_child(at)
	at.progresso.connect(_progresso)
	at.terminou.connect(_terminou)
	_montar()
	_mostrar_aba("noticias")
	_atualizar_tela()
	_buscar_manifesto()
	_buscar_noticias()
	if args.has("fotos"):
		get_tree().create_timer(float(args.get("espera", "2.5"))).timeout.connect(_foto)

# ------------------------------------------------------------------ montagem da tela

func _carregar_fontes() -> void:
	F_TITULO = _fonte("cinzel-bold.woff2")
	F_TEXTO = _fonte("fell.woff2")
	F_ITALICO = _fonte("fell-italic.woff2")
	F_GOTICA = _fonte("PirataOne-Regular.ttf")
	var v := FontVariation.new()
	v.base_font = F_TITULO
	v.spacing_glyph = 4
	F_TITULO_LARGO = v

func _fonte(nome: String) -> Font:
	var f: FontFile = load("res://fontes/" + nome)
	f.antialiasing = TextServer.FONT_ANTIALIASING_GRAY
	f.hinting = TextServer.HINTING_LIGHT
	return f

func _tex(nome: String) -> Texture2D:
	return load("res://arte/pecas/%s.png" % nome)

func _montar() -> void:
	var fundo := TextureRect.new()
	fundo.texture = _tex("fundo")
	fundo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fundo)
	_particulas()

	# brilho da gema do Amargo no medalhão do topo
	_gema = Sprite2D.new()
	_gema.texture = _brilho(48, Color(0.61, 1.0, 0.23))
	_gema.position = Vector2(480, 27)
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_gema.material = mat
	add_child(_gema)

	# barra de título: arrastar a janela, minimizar e fechar
	var titulo := Control.new()
	titulo.position = Vector2(12, 12)
	titulo.size = Vector2(870, 30)
	titulo.gui_input.connect(_arrastar)
	add_child(titulo)
	_botao_janela("min", Vector2(890, 16), func(): DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MINIMIZED))
	_botao_janela("fechar", Vector2(916, 16), func(): get_tree().quit())

	# versão do launcher, discreta, sob o logo
	_label(Vector2(40, 146), Vector2(300, 18), "launcher %s" % VERSAO_LAUNCHER, F_ITALICO, 13, C_APAGADO)

	# abas e texto das notícias
	_abas["noticias"] = _aba(Vector2(48, 289), "Notícias", "noticias")
	_abas["cronicas"] = _aba(Vector2(180, 289), "Crônicas", "cronicas")
	_texto_noticias = RichTextLabel.new()
	_texto_noticias.position = Vector2(52, 328)
	_texto_noticias.size = Vector2(518, 140)
	_texto_noticias.bbcode_enabled = true
	_texto_noticias.scroll_active = true
	_texto_noticias.add_theme_font_override("normal_font", F_TEXTO)
	_texto_noticias.add_theme_font_override("italics_font", F_ITALICO)
	_texto_noticias.add_theme_font_override("bold_font", F_TITULO)
	_texto_noticias.add_theme_font_size_override("normal_font_size", 14)
	_texto_noticias.add_theme_font_size_override("italics_font_size", 14)
	_texto_noticias.add_theme_font_size_override("bold_font_size", 14)
	_texto_noticias.add_theme_color_override("default_color", Color("#cfc4ad"))
	_texto_noticias.add_theme_constant_override("line_separation", 1)
	_texto_noticias.meta_clicked.connect(func(m): OS.shell_open(str(m)))
	_estilo_rolagem(_texto_noticias.get_v_scroll_bar())
	add_child(_texto_noticias)

	# painel do servidor
	_ponto_status = Ponto.new()
	_ponto_status.position = Vector2(630, 349)
	add_child(_ponto_status)
	_label(Vector2(642, 337), Vector2(150, 22), String(cfg.get("servidor_nome", "São Lázaro")), F_TITULO, 16, C_OSSO)
	_lbl_status = _label(Vector2(760, 339), Vector2(150, 20), "", F_ITALICO, 15, C_FRACO, HORIZONTAL_ALIGNMENT_RIGHT)
	_label(Vector2(626, 362), Vector2(160, 18), "Versão instalada", F_ITALICO, 14, C_FRACO)
	_lbl_instalada = _label(Vector2(790, 362), Vector2(120, 18), "", F_TITULO, 13, C_OSSO, HORIZONTAL_ALIGNMENT_RIGHT)
	_label(Vector2(626, 380), Vector2(160, 18), "Versão no servidor", F_ITALICO, 14, C_FRACO)
	_lbl_servidor = _label(Vector2(790, 380), Vector2(120, 18), "", F_TITULO, 13, C_OSSO, HORIZONTAL_ALIGNMENT_RIGHT)
	_botoes["site"] = _botao_pequeno(Vector2(624, 410), "Site oficial", func(): OS.shell_open(String(cfg.get("site", ""))))
	_botoes["conta"] = _botao_pequeno(Vector2(770, 410), "Criar conta", func(): OS.shell_open(String(cfg.get("criar_conta", ""))))
	_botoes["pasta"] = _botao_pequeno(Vector2(624, 441), "Pasta do jogo", _abrir_pasta)
	_botoes["reparar"] = _botao_pequeno(Vector2(770, 441), "Reparar", _reparar)

	# progresso
	_lbl_estado = _label(Vector2(36, 492), Vector2(440, 22), "", F_TITULO, 14, C_OSSO)
	_lbl_bytes = _label(Vector2(440, 494), Vector2(258, 20), "", F_TEXTO, 15, C_FRACO, HORIZONTAL_ALIGNMENT_RIGHT)
	_barra = Barra.new()
	_barra.position = Vector2(40, 525)
	_barra.size = Vector2(648, 14)
	_barra.liquido = _tex("barra_liquido")
	_barra.ponta = _tex("barra_ponta")
	_barra.vidro = _tex("barra_vidro")
	add_child(_barra)
	_lbl_detalhe = _label(Vector2(36, 552), Vector2(662, 20), "", F_ITALICO, 15, C_FRACO)

	# botão Jogar
	_jogar = TextureButton.new()
	_jogar.position = Vector2(712, 494)
	_jogar.texture_normal = _tex("jogar_normal")
	_jogar.texture_hover = _tex("jogar_hover")
	_jogar.texture_pressed = _tex("jogar_pressed")
	_jogar.texture_disabled = _tex("jogar_disabled")
	_jogar.pressed.connect(_acao_principal)
	add_child(_jogar)
	_lbl_jogar = _label(Vector2(0, 0), Vector2(212, 76), "JOGAR", F_TITULO_LARGO, 26, C_OURO, HORIZONTAL_ALIGNMENT_CENTER)
	_lbl_jogar.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_lbl_jogar.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	_lbl_jogar.add_theme_constant_override("shadow_offset_y", 2)
	_lbl_jogar.add_theme_constant_override("shadow_outline_size", 4)
	_lbl_jogar.reparent(_jogar, false)
	_hover_cor(_jogar, _lbl_jogar, C_OURO, C_OURO_CLARO)

func _label(pos: Vector2, tam: Vector2, txt: String, fonte: Font, px: int, cor: Color, alin := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = tam
	l.text = txt
	l.horizontal_alignment = alin
	l.clip_text = true
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override("font", fonte)
	l.add_theme_font_size_override("font_size", px)
	l.add_theme_color_override("font_color", cor)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("shadow_offset_y", 1)
	add_child(l)
	return l

func _botao_pequeno(pos: Vector2, txt: String, acao: Callable) -> TextureButton:
	var b := TextureButton.new()
	b.position = pos
	b.texture_normal = _tex("botao_normal")
	b.texture_hover = _tex("botao_hover")
	b.texture_pressed = _tex("botao_pressed")
	b.texture_disabled = _tex("botao_disabled")
	b.pressed.connect(func(): _som("clique_1"); acao.call())
	add_child(b)
	var l := _label(Vector2(0, 0), Vector2(140, 28), txt.to_upper(), F_TITULO, 11, Color("#c9b58c"), HORIZONTAL_ALIGNMENT_CENTER)
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.reparent(b, false)
	_hover_cor(b, l, Color("#c9b58c"), C_OURO_CLARO)
	return b

func _botao_janela(nome: String, pos: Vector2, acao: Callable) -> void:
	var b := TextureButton.new()
	b.position = pos
	b.texture_normal = _tex("janela_%s_normal" % nome)
	b.texture_hover = _tex("janela_%s_hover" % nome)
	b.pressed.connect(acao)
	add_child(b)

func _aba(pos: Vector2, txt: String, id: String) -> TextureButton:
	var b := TextureButton.new()
	b.position = pos
	b.texture_normal = _tex("aba_normal")
	b.texture_hover = _tex("aba_hover")
	b.pressed.connect(func(): _som("clique_1"); _mostrar_aba(id))
	add_child(b)
	var l := _label(Vector2(0, 1), Vector2(128, 28), txt.to_upper(), F_TITULO_LARGO, 12, C_FRACO, HORIZONTAL_ALIGNMENT_CENTER)
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.reparent(b, false)
	b.mouse_entered.connect(func(): _som("passar_mouse_1"))
	return b

func _hover_cor(b: BaseButton, l: Label, normal: Color, sobre: Color) -> void:
	b.mouse_entered.connect(func():
		if not b.disabled:
			l.add_theme_color_override("font_color", sobre)
			_som("passar_mouse_1"))
	b.mouse_exited.connect(func(): l.add_theme_color_override("font_color", C_APAGADO if b.disabled else normal))

func _estilo_rolagem(sb: VScrollBar) -> void:
	var trilho := StyleBoxFlat.new()
	trilho.bg_color = Color(0, 0, 0, 0.5)
	trilho.content_margin_left = 3
	trilho.content_margin_right = 3
	var pega := StyleBoxFlat.new()
	pega.bg_color = Color("#6b5634")
	pega.border_color = Color("#b08d4f")
	pega.border_width_left = 1
	pega.border_width_right = 1
	pega.set_corner_radius_all(2)
	var pega2 := pega.duplicate()
	pega2.bg_color = Color("#8a6d3e")
	sb.add_theme_stylebox_override("scroll", trilho)
	sb.add_theme_stylebox_override("grabber", pega)
	sb.add_theme_stylebox_override("grabber_highlight", pega2)
	sb.add_theme_stylebox_override("grabber_pressed", pega2)
	sb.custom_minimum_size.x = 8

func _particulas() -> void:
	# pó do Amargo subindo devagar sobre o acampamento e cinza caindo
	var amargo := CPUParticles2D.new()
	amargo.position = Vector2(640, 250)
	amargo.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	amargo.emission_rect_extents = Vector2(320, 70)
	amargo.amount = 38
	amargo.lifetime = 7.0
	amargo.preprocess = 7.0
	amargo.texture = _brilho(10, Color(0.61, 1.0, 0.23))
	amargo.direction = Vector2(0.2, -1)
	amargo.spread = 30
	amargo.gravity = Vector2.ZERO
	amargo.initial_velocity_min = 4
	amargo.initial_velocity_max = 12
	amargo.scale_amount_min = 0.25
	amargo.scale_amount_max = 0.7
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 0))
	g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.25, Color(1, 1, 1, 0.75))
	g.add_point(0.7, Color(1, 1, 1, 0.45))
	amargo.color_ramp = g
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	amargo.material = add
	add_child(amargo)
	var cinza := CPUParticles2D.new()
	cinza.position = Vector2(480, 30)
	cinza.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	cinza.emission_rect_extents = Vector2(470, 4)
	cinza.amount = 26
	cinza.lifetime = 12.0
	cinza.preprocess = 12.0
	cinza.texture = _brilho(6, Color(0.75, 0.7, 0.62))
	cinza.direction = Vector2(-0.3, 1)
	cinza.spread = 15
	cinza.gravity = Vector2(0, 2)
	cinza.initial_velocity_min = 10
	cinza.initial_velocity_max = 22
	cinza.scale_amount_min = 0.3
	cinza.scale_amount_max = 0.6
	var g2 := Gradient.new()
	g2.set_color(0, Color(1, 1, 1, 0.0))
	g2.set_color(1, Color(1, 1, 1, 0.0))
	g2.add_point(0.15, Color(1, 1, 1, 0.35))
	g2.add_point(0.4, Color(1, 1, 1, 0.25))
	cinza.color_ramp = g2
	add_child(cinza)

func _brilho(tam: int, cor: Color) -> Texture2D:
	var g := Gradient.new()
	g.set_color(0, cor)
	g.set_color(1, Color(cor, 0.0))
	g.add_point(0.35, Color(cor, 0.5))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.width = tam
	t.height = tam
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	return t

# ------------------------------------------------------------------ notícias

func _mostrar_aba(id: String) -> void:
	aba = id
	for k in _abas:
		var b: TextureButton = _abas[k]
		var ativa: bool = k == id
		b.texture_normal = _tex("aba_ativa" if ativa else "aba_normal")
		b.texture_hover = _tex("aba_ativa" if ativa else "aba_hover")
		(b.get_child(0) as Label).add_theme_color_override("font_color", C_OURO if ativa else C_FRACO)
	var t := ""
	if id == "noticias":
		for n in noticias.get("noticias", []):
			t += "[font_size=11][color=#7fae3e]%s[/color][/font_size]   [b][color=#e8dfc9]%s[/color][/b]\n" % [str(n.get("data", "")).to_upper(), n.get("titulo", "")]
			var txt := str(n.get("texto", ""))
			if n.has("link"): txt += "  [url=%s][color=#e0b84a]Ler mais[/color][/url]" % n["link"]
			t += "%s\n[font_size=6] [/font_size]\n" % txt
	else:
		for c in noticias.get("cronicas", []):
			t += "[b][color=#e0b84a]%s[/color][/b]\n[i]%s[/i]\n[font_size=6] [/font_size]\n" % [c.get("titulo", ""), c.get("texto", "")]
	_texto_noticias.text = t.strip_edges()
	_texto_noticias.scroll_to_line(0)

func _buscar_noticias() -> void:
	var url := String(args.get("noticias", cfg.get("noticias", "")))
	if url == "": return
	_get_json(url, func(d):
		if d is Dictionary and (d.has("noticias") or d.has("cronicas")):
			for k in ["noticias", "cronicas"]:
				if d.has(k): noticias[k] = d[k]
			_mostrar_aba(aba))

# ------------------------------------------------------------------ servidor e versões

func _buscar_manifesto() -> void:
	estado = "conectando"
	_atualizar_tela()
	_get_json(_url_manifesto(), func(d):
		if d is Dictionary and d.has("versao") and d.has("arquivo"):
			remoto = d
			_som("notificacao")
		else:
			remoto = {}
		_decidir())

func _decidir() -> void:
	var local := at.instalada()
	if remoto.is_empty():
		estado = "offline"
	elif local.is_empty():
		estado = "instalar"
	elif _v(local.get("versao", "")) != _v(remoto.get("versao", "")):
		estado = "atualizar"
		_comecar_download()   # atualização começa sozinha, como nos MMOs antigos
		return
	else:
		estado = "pronto"
	_atualizar_tela()

func _acao_principal() -> void:
	_som("confirmar")
	match estado:
		"pronto", "offline":
			if not at.instalada().is_empty(): _abrir_jogo()
		"instalar", "atualizar", "erro":
			if remoto.is_empty(): _buscar_manifesto()
			else: _comecar_download()
		"baixando":
			at.cancelar()

func _comecar_download() -> void:
	_erro_msg = ""
	_vel_amostras.clear()
	var url := String(remoto.get("url", ""))
	if url == "":
		url = _url_manifesto().get_base_dir().path_join(String(remoto["arquivo"]).uri_encode())
	elif not url.begins_with("http"):
		url = _url_manifesto().get_base_dir().path_join(url)
	estado = "baixando"
	at.baixar(remoto, url)
	_atualizar_tela()

func _progresso(fase: String, feito: int, total: int) -> void:
	estado = fase
	var frac := float(feito) / float(total) if total > 0 else 0.0
	_barra.valor = frac
	match fase:
		"baixando":
			var agora := Time.get_ticks_msec() / 1000.0
			_vel_amostras.append([agora, feito])
			while _vel_amostras.size() > 2 and agora - float(_vel_amostras[0][0]) > 3.0: _vel_amostras.pop_front()
			var vel := 0.0
			if _vel_amostras.size() > 1:
				var dt := agora - float(_vel_amostras[0][0])
				if dt > 0.2: vel = (feito - int(_vel_amostras[0][1])) / dt
			_lbl_bytes.text = "%s de %s" % [_mb(feito), _mb(total)]
			var resto := ""
			if vel > 1024 and total > feito:
				resto = " · faltam %s" % _tempo((total - feito) / vel)
			_lbl_detalhe.text = "%s/s%s" % [_mb(vel), resto] if vel > 0 else "Abrindo a conexão com o servidor..."
		"conferindo":
			_lbl_bytes.text = "%d%%" % int(frac * 100)
			_lbl_detalhe.text = "Conferindo o selo (sha256) do arquivo baixado."
		"extraindo":
			_lbl_bytes.text = "%d de %d arquivos" % [feito, total]
			_lbl_detalhe.text = "Desenterrando os arquivos na pasta do jogo."
	_atualizar_estado_texto()

func _terminou(ok: bool, msg: String) -> void:
	if ok:
		_som("confirmar")
		estado = "pronto"
		_barra.valor = 1.0
	else:
		_som("erro")
		_erro_msg = msg
		estado = "erro" if remoto.size() else "offline"
		_barra.valor = 0.0
	_atualizar_tela()

func _reparar() -> void:
	if at.ocupado() or remoto.is_empty(): return
	_comecar_download()

func _abrir_jogo() -> void:
	var exe := at.pasta_jogo().path_join(String(remoto.get("executavel", cfg.get("executavel", "DarkPassage.exe"))))
	if not FileAccess.file_exists(exe):
		_erro_msg = "Não achei o jogo na pasta. Use Reparar para baixar de novo."
		estado = "erro" if remoto.size() else "offline"
		_som("erro")
		_atualizar_tela()
		return
	var pid := OS.create_process(exe, [])
	if pid <= 0:
		_erro_msg = "O Windows não deixou abrir o jogo."
		_som("erro")
		_atualizar_tela()
		return
	_lbl_detalhe.text = "Boa caçada no Deserto de Absinto."
	get_tree().create_timer(1.2).timeout.connect(get_tree().quit)

func _abrir_pasta() -> void:
	var p := at.pasta_jogo() if DirAccess.dir_exists_absolute(at.pasta_jogo()) else at.base
	OS.shell_open(ProjectSettings.globalize_path(p))

# ------------------------------------------------------------------ texto da tela por estado

func _atualizar_tela() -> void:
	var local := at.instalada()
	_lbl_instalada.text = ("v" + _v(local["versao"])) if local.has("versao") else "nenhuma"
	_lbl_servidor.text = ("v" + _v(remoto["versao"])) if remoto.has("versao") else "?"
	var desatualizado: bool = remoto.has("versao") and local.has("versao") and _v(local["versao"]) != _v(remoto["versao"])
	_lbl_instalada.add_theme_color_override("font_color", C_SANGUE if desatualizado else C_OSSO)
	if estado == "conectando":
		_lbl_status.text = "chamando..."
		_ponto_status.color = Color("#c99a3e")
	elif remoto.is_empty():
		_lbl_status.text = "sem resposta"
		_ponto_status.color = Color("#b8321f")
	else:
		_lbl_status.text = "portão aberto"
		_ponto_status.color = C_AMARGO
	_botoes["reparar"].disabled = at.ocupado() or remoto.is_empty() or local.is_empty()
	_botoes["reparar"].get_child(0).add_theme_color_override("font_color", C_APAGADO if _botoes["reparar"].disabled else Color("#c9b58c"))

	var rotulo := "JOGAR"
	var pode := true
	match estado:
		"conectando":
			pode = false
		"instalar":
			rotulo = "INSTALAR"
		"atualizar", "erro":
			rotulo = "TENTAR DE NOVO" if estado == "erro" else "ATUALIZAR"
		"baixando":
			rotulo = "CANCELAR"
		"conferindo", "extraindo":
			pode = false
		"offline":
			pode = not local.is_empty()
	_jogar.disabled = not pode
	_lbl_jogar.text = rotulo
	var curto := rotulo.length() <= 9
	_lbl_jogar.add_theme_font_override("font", F_TITULO_LARGO if curto else F_TITULO)
	_lbl_jogar.add_theme_font_size_override("font_size", 26 if curto else 17)
	_lbl_jogar.add_theme_color_override("font_color", C_OURO if pode else C_APAGADO)
	if not at.ocupado():
		_barra.valor = 1.0 if estado == "pronto" else 0.0
		_lbl_bytes.text = ""
		_lbl_detalhe.text = _detalhe_parado(local)
	_atualizar_estado_texto()

func _atualizar_estado_texto() -> void:
	var r := {
		"conectando": "Chamando o servidor de São Lázaro...",
		"offline": "Sem contato com o servidor",
		"instalar": "O jogo ainda não está neste PC",
		"atualizar": "Há uma prévia nova",
		"baixando": _texto_baixando(),
		"conferindo": "Conferindo o arquivo",
		"extraindo": "Instalando",
		"pronto": "Tudo pronto. A areia espera.",
		"erro": "Algo deu errado",
	}
	_lbl_estado.text = r.get(estado, "")
	_lbl_estado.add_theme_color_override("font_color", C_SANGUE if estado == "erro" else C_OSSO)

func _texto_baixando() -> String:
	var antes := String(at.instalada().get("versao", ""))
	if antes != "" and _v(antes) != _v(remoto.get("versao", "")):
		return "Atualizando da v%s para a v%s" % [_v(antes), _v(remoto.get("versao", ""))]
	return "Baixando a prévia v%s" % _v(remoto.get("versao", ""))

func _detalhe_parado(local: Dictionary) -> String:
	if _erro_msg != "": return _erro_msg
	match estado:
		"offline":
			return "Dá para jogar sozinho ou na rede local. O online volta quando o servidor responder." if local.size() else "Confira a internet e tente de novo."
		"instalar":
			return "Clique em Instalar para baixar a prévia v%s (%s)." % [_v(remoto.get("versao", "")), _mb(int(remoto.get("tamanho", 0)))]
		"pronto":
			return "Prévia v%s instalada em %s" % [_v(local.get("versao", "")), ProjectSettings.globalize_path(at.pasta_jogo())]
	return ""

# ------------------------------------------------------------------ utilidades

func _url_manifesto() -> String:
	return String(args.get("manifesto", cfg.get("manifesto", "")))

func _pasta_base() -> String:
	if args.has("pasta"): return args["pasta"]
	if OS.has_feature("editor"): return "user://"
	# 1) uma instalação que já existe ao lado do launcher continua valendo (menos se ele roda de dentro do zip)
	var aqui := OS.get_executable_path().get_base_dir()
	if not _pasta_temporaria(aqui) and FileAccess.file_exists(aqui.path_join("jogo/versao.json")):
		return aqui
	if FileAccess.file_exists("user://jogo/versao.json"):
		return "user://"
	# 2) senão, um lugar fixo do usuário, que não depende de onde o launcher foi aberto:
	#    aberto de dentro do zip, o Windows roda o launcher numa pasta temporária que some depois,
	#    e o jogo instalado ali era baixado de novo a cada vez
	var local := OS.get_environment("LOCALAPPDATA")
	if local != "":
		var fixo := local.path_join("DarkPassage")
		if DirAccess.make_dir_recursive_absolute(fixo) == OK and _gravavel(fixo):
			return fixo
	if not _pasta_temporaria(aqui) and _gravavel(aqui):
		return aqui
	return "user://"

static func _pasta_temporaria(p: String) -> bool:
	var q := p.replace("\\", "/").to_lower()
	for t in [OS.get_environment("TEMP"), OS.get_environment("TMP")]:
		if t != "" and q.begins_with(t.replace("\\", "/").to_lower()): return true
	return q.contains("/temp/") or q.contains("/tmp/") or q.contains(".zip")

static func _gravavel(p: String) -> bool:
	var teste := p.path_join(".teste_escrita")
	var f := FileAccess.open(teste, FileAccess.WRITE)
	if f == null: return false
	f.close()
	DirAccess.remove_absolute(teste)
	return true

func _get_json(url: String, fim: Callable) -> void:
	var h := HTTPRequest.new()
	h.timeout = 10.0
	add_child(h)
	h.request_completed.connect(func(res: int, cod: int, _hd, corpo: PackedByteArray):
		h.queue_free()
		fim.call(JSON.parse_string(corpo.get_string_from_utf8()) if res == HTTPRequest.RESULT_SUCCESS and cod == 200 else null))
	if h.request(url, ["Cache-Control: no-cache"]) != OK:
		h.queue_free()
		fim.call(null)

func _ler_json(p: String) -> Dictionary:
	var d = JSON.parse_string(FileAccess.get_file_as_string(p))
	return d if d is Dictionary else {}

static func _v(s) -> String:
	return str(s).strip_edges().trim_prefix("v").trim_prefix("V")

static func _host(url: String) -> String:
	return url.trim_prefix("https://").trim_prefix("http://").trim_suffix("/")

static func _mb(b: float) -> String:
	if b >= 1048576.0: return ("%.1f MB" % (b / 1048576.0)).replace(".", ",")
	return "%d KB" % int(b / 1024.0)

static func _tempo(s: float) -> String:
	if s < 60: return "%d s" % int(ceil(s))
	return "%d min %02d s" % [int(s / 60), int(s) % 60]

func _som(id: String) -> void:
	if _sons.has(id): _sons[id].play()

func _arrastar(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
		_arrastando = e.pressed
		_arrasto_ini = DisplayServer.mouse_get_position() - DisplayServer.window_get_position()
	elif e is InputEventMouseMotion and _arrastando:
		DisplayServer.window_set_position(DisplayServer.mouse_get_position() - _arrasto_ini)

func _process(_d: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	_gema.modulate.a = 0.55 + 0.3 * sin(t * 1.7)
	_gema.scale = Vector2.ONE * (1.0 + 0.06 * sin(t * 1.7))

func _foto() -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(args["fotos"])
	get_tree().quit()


## Barra de progresso: líquido verde do Amargo num tubo de vidro.
class Barra extends Control:
	var liquido: Texture2D
	var ponta: Texture2D
	var vidro: Texture2D
	var valor := 0.0:
		set(v):
			valor = clampf(v, 0.0, 1.0)
			queue_redraw()

	func _draw() -> void:
		var w := roundf(size.x * valor)
		if w >= 1.0:
			draw_texture_rect(liquido, Rect2(0, 0, w, size.y), true)
			if valor < 1.0: draw_texture(ponta, Vector2(w - 5, 0))
		draw_texture(vidro, Vector2.ZERO)


## Luz de status do servidor: um ponto com halo.
class Ponto extends Control:
	var color := Color.WHITE:
		set(c):
			color = c
			queue_redraw()

	func _draw() -> void:
		draw_circle(Vector2.ZERO, 7.0, Color(color, 0.12))
		draw_circle(Vector2.ZERO, 4.5, Color(color, 0.3))
		draw_circle(Vector2.ZERO, 3.2, Color(0.05, 0.03, 0.02))
		draw_circle(Vector2.ZERO, 2.4, color)

extends Control
## Tela de abertura: jogar sozinho, hospedar a partida na rede local ou entrar pelo IP de quem hospeda.
## Em rede: conta (cadastro/login) e lista de personagens da conta; o servidor guarda tudo.

signal solo()
signal no_mundo(rede: Node, msg: Dictionary)
signal criar_personagem()

const CFG := "user://rede.cfg"
const NOMES := {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}

var rede: Node
var caixa: VBoxContainer
var aviso: Label
var tela := ""
var u_edit := LineEdit.new()
var s_edit := LineEdit.new()
var ip_edit := LineEdit.new()
var personagens: Array = []
var auto := {}           # teste automático: conectar=ip usuario= senha= classe=

const M := "res://assets/menu/"
const CLASSES_ARTE := {"anjo": "classe_anjo", "demonio": "classe_demonio", "cultista": "classe_cultista", "humano": "classe_humano", "mutante": "classe_mutante", "tecnomancer": "classe_tecnomancer"}
const COR_BOTAO := Color("#dcc89a")
const COR_BOTAO_HOVER := Color("#fff1c8")
const COR_ROTULO := Color("#a8916a")

var placa_txt: Label
var rodape_srv: Label
var fundo_arte: TextureRect

func _ready() -> void:
	Tema.carregar()
	theme = Tema.tema_janelas()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var preto := ColorRect.new(); preto.color = Color(0.02, 0.016, 0.014)
	preto.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); add_child(preto)
	# fundo: o Acampamento da Vela à noite, com um zoom lento
	fundo_arte = TextureRect.new(); fundo_arte.texture = Tema.tex(M + "fundo.png")
	fundo_arte.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fundo_arte.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fundo_arte.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	add_child(fundo_arte)
	fundo_arte.resized.connect(func(): fundo_arte.pivot_offset = fundo_arte.size * Vector2(0.72, 0.5))
	var tw := create_tween().set_loops()
	tw.tween_property(fundo_arte, "scale", Vector2(1.05, 1.05), 28.0).set_trans(Tween.TRANS_SINE)
	tw.tween_property(fundo_arte, "scale", Vector2.ONE, 28.0).set_trans(Tween.TRANS_SINE)
	_particulas()
	# logo e frase
	var logo := TextureRect.new(); logo.texture = Tema.tex(M + "logo.png")
	logo.position = Vector2(44, 20); logo.size = Vector2(496, 120)
	logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	add_child(logo)
	var frase := Tema.rotulo("Deserto de Absinto, onde o Juízo travou.", 18, Color("#cbbd9f"), Tema.FONTE_ITALICO, 3)
	frase.position = Vector2(56, 150); frase.size = Vector2(480, 26)
	frase.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(frase)
	# painel de ferro e couro com a placa do título
	var painel := TextureRect.new(); painel.texture = Tema.tex(M + "painel.png")
	painel.position = Vector2(72, 192); painel.size = Vector2(440, 490)
	add_child(painel)
	var placa := TextureRect.new(); placa.texture = Tema.tex(M + "placa.png")
	placa.position = Vector2(152, 178); placa.size = Vector2(280, 34)
	add_child(placa)
	placa_txt = Tema.rotulo("", 14, Color("#f6e3b4"), Tema.FONTE_TITULO, 3)
	placa_txt.position = Vector2(176, 185); placa_txt.size = Vector2(232, 20)
	placa_txt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	placa_txt.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(placa_txt)
	caixa = VBoxContainer.new()
	caixa.position = Vector2(106, 236); caixa.size = Vector2(372, 420)
	caixa.add_theme_constant_override("separation", 9)
	add_child(caixa)
	# rodapé: versão e servidor
	var faixa := TextureRect.new()
	var g := Gradient.new(); g.colors = PackedColorArray([Color(0, 0, 0, 0), Color(0, 0, 0, 0.85)])
	var gt := GradientTexture2D.new(); gt.gradient = g; gt.fill_from = Vector2(0, 0); gt.fill_to = Vector2(0, 1)
	faixa.texture = gt; faixa.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	faixa.set_anchors_preset(Control.PRESET_BOTTOM_WIDE); faixa.offset_top = -40
	add_child(faixa)
	var ver := Tema.rotulo("Prévia v%s  ·  F11 tela cheia" % rede_versao(), 13, Color("#8a7c64"), Tema.FONTE_ITALICO, 2)
	ver.set_anchors_preset(Control.PRESET_BOTTOM_LEFT); ver.offset_left = 22; ver.offset_top = -28; ver.offset_bottom = -8
	add_child(ver)
	rodape_srv = Tema.rotulo("", 13, Color("#8a7c64"), Tema.FONTE_ITALICO, 2)
	rodape_srv.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT); rodape_srv.offset_left = -520; rodape_srv.offset_right = -22
	rodape_srv.offset_top = -28; rodape_srv.offset_bottom = -8
	rodape_srv.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(rodape_srv)
	for le in [u_edit, s_edit, ip_edit]:
		le.add_theme_font_override("font", Tema.FONTE_TEXTO)
		le.add_theme_font_size_override("font_size", 17)
		le.add_theme_color_override("font_color", Color("#eadfc6"))
		le.add_theme_color_override("font_placeholder_color", Color("#6e6250"))
		le.add_theme_color_override("caret_color", Tema.COR_AMARGO)
		le.add_theme_color_override("selection_color", Color(0.61, 1.0, 0.23, 0.25))
		le.custom_minimum_size = Vector2(372, 40)
	_campo(u_edit, "usuario"); _campo(s_edit, "senha"); _campo(ip_edit, "ip")
	s_edit.secret = true
	u_edit.max_length = 16; s_edit.max_length = 64
	u_edit.placeholder_text = "seu usuário"; s_edit.placeholder_text = "sua senha"
	ip_edit.placeholder_text = "ex.: 192.168.0.10"
	u_edit.text_submitted.connect(func(_x): s_edit.grab_focus())
	s_edit.text_submitted.connect(func(_x): _conta("login"))
	ip_edit.text_submitted.connect(func(_x): _conectar())
	var cfg := ConfigFile.new()
	if cfg.load(CFG) == OK:
		ip_edit.text = cfg.get_value("rede", "ip", "")
		u_edit.text = cfg.get_value("rede", "usuario", "")
	rede = get_node_or_null("/root/Main/Rede")
	if rede:
		rede.mensagem.connect(_msg)
		rede.caiu.connect(func(motivo): _inicio(); _avisar(motivo, true))
	_inicio()
	if auto.has("conectar"):
		ip_edit.text = auto["conectar"]; u_edit.text = auto.get("usuario", "teste"); s_edit.text = auto.get("senha", "1234")
		if auto["conectar"] == "hospedar": _hospedar()
		elif auto["conectar"] == "online": _online()
		else: _conectar()

func rede_versao() -> String:
	return rede.VERSAO if rede != null else "0.7"

## Brasas subindo e poeira do Amargo flutuando por cima da arte.
func _particulas() -> void:
	var g := Gradient.new(); g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
	var pt := GradientTexture2D.new(); pt.gradient = g; pt.width = 16; pt.height = 16
	pt.fill = GradientTexture2D.FILL_RADIAL; pt.fill_from = Vector2(0.5, 0.5); pt.fill_to = Vector2(1.0, 0.5)
	var camada := Node2D.new(); add_child(camada)
	var tela := get_viewport_rect().size
	for cfg in [[Color(1.0, 0.55, 0.2), 70, Vector2(0, -38), 0.35, 9.0], [Color(0.61, 1.0, 0.23), 26, Vector2(6, -14), 0.28, 14.0]]:
		var p := CPUParticles2D.new()
		p.texture = pt
		p.amount = cfg[1]; p.lifetime = cfg[4]; p.preprocess = cfg[4]
		p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		p.emission_rect_extents = Vector2(tela.x * 0.42, 40)
		p.position = Vector2(tela.x * 0.6, tela.y + 20)
		p.direction = Vector2(0, -1); p.spread = 25.0
		p.gravity = cfg[2]; p.initial_velocity_min = 10.0; p.initial_velocity_max = 34.0
		p.scale_amount_min = 0.12; p.scale_amount_max = cfg[3]
		var cor: Color = cfg[0]
		var rampa := Gradient.new()
		rampa.colors = PackedColorArray([Color(cor, 0.0), Color(cor, 0.9), Color(cor, 0.0)])
		rampa.offsets = PackedFloat32Array([0.0, 0.25, 1.0])
		p.color_ramp = rampa
		var mat := CanvasItemMaterial.new(); mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		p.material = mat
		camada.add_child(p)

func _limpar() -> void:
	for c in caixa.get_children(): caixa.remove_child(c); c.queue_free()
	aviso = null

func _placa(txt: String) -> void:
	placa_txt.text = txt.to_upper()

func _estilo(nome: String) -> StyleBoxTexture:
	var sb := StyleBoxTexture.new()
	sb.texture = Tema.tex(M + nome + ".png")
	sb.set_texture_margin_all(12)
	sb.set_content_margin_all(6)
	return sb

func _campo(le: LineEdit, tipo: String) -> void:
	var n := _estilo("campo_%s_normal" % tipo); n.content_margin_left = 48; n.content_margin_right = 12
	var f := _estilo("campo_%s_foco" % tipo); f.content_margin_left = 48; f.content_margin_right = 12
	le.add_theme_stylebox_override("normal", n)
	le.add_theme_stylebox_override("focus", f)
	le.add_theme_stylebox_override("read_only", n)

func _botao(txt: String, f: Callable, destaque := false, pai: Control = null) -> Button:
	var b := Button.new(); b.text = txt.to_upper()
	var base := "principal" if destaque else "botao"
	for e in [["normal", "normal"], ["hover", "hover"], ["pressed", "pressed"], ["disabled", "disabled"], ["focus", "hover"]]:
		b.add_theme_stylebox_override(e[0], _estilo("%s_%s" % [base, e[1]]))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.custom_minimum_size = Vector2(0, 58 if destaque else 40)
	b.add_theme_font_override("font", Tema.FONTE_TITULO)
	b.add_theme_font_size_override("font_size", 19 if destaque else 14)
	b.add_theme_color_override("font_color", COR_BOTAO)
	b.add_theme_color_override("font_hover_color", COR_BOTAO_HOVER)
	b.add_theme_color_override("font_focus_color", COR_BOTAO)
	b.add_theme_color_override("font_pressed_color", Color("#c0a878"))
	b.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	b.add_theme_constant_override("outline_size", 3)
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.pressed.connect(f)
	(pai if pai else caixa).add_child(b)
	return b

## Dois botões lado a lado.
func _par(a: Array, b: Array) -> void:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 10)
	caixa.add_child(h)
	for it in [a, b]:
		var bt := _botao(it[0], it[1], false, h)
		bt.size_flags_horizontal = Control.SIZE_EXPAND_FILL

func _rotulo_campo(txt: String) -> void:
	var l := Tema.rotulo(txt.to_upper(), 11, COR_ROTULO, Tema.FONTE_TITULO, 2)
	l.add_theme_constant_override("line_spacing", 0)
	caixa.add_child(l)

func _divisor() -> void:
	var d := TextureRect.new(); d.texture = Tema.tex(M + "divisor.png")
	d.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	caixa.add_child(d)

func _texto(txt: String, tam := 15, cor := Color("#cbbd9f"), fonte: Font = null) -> Label:
	var l := Tema.rotulo(txt, tam, cor, fonte if fonte else Tema.FONTE_TEXTO, 2)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caixa.add_child(l)
	return l

func _espaco(h: float) -> void:
	var c := Control.new(); c.custom_minimum_size = Vector2(0, h); caixa.add_child(c)

func _avisar(txt: String, erro := false) -> void:
	if aviso == null: aviso = _texto("", 15)
	aviso.text = txt
	aviso.add_theme_color_override("font_color", Color("#ff8a72") if erro else Color("#e8d8a8"))

# =================================================================== telas
func _inicio() -> void:
	tela = "inicio"
	_limpar()
	_placa("O Portão de São Lázaro")
	rodape_srv.text = ""
	if OS.has_feature("web"):
		_espaco(6)
		_botao("Jogar sozinho", func(): solo.emit(), true)
		_divisor()
		_texto("Para jogar online ou com amigos na rede local, use a versão de Windows.", 15, Color("#a89a80"), Tema.FONTE_ITALICO)
		return
	_espaco(6)
	_botao("Jogar online", _online, true)
	_espaco(2)
	_botao("Jogar sozinho", func(): solo.emit())
	_botao("Hospedar na rede local", _hospedar)
	_botao("Entrar por IP na rede local", _tela_ip)
	_espaco(4)
	_divisor()
	_texto("Online, sua conta e seus personagens ficam no servidor %s." % rede.ONLINE, 15, Color("#a89a80"), Tema.FONTE_ITALICO)
	_texto("Na rede local, um PC hospeda e os amigos entram pelo IP dele.", 15, Color("#a89a80"), Tema.FONTE_ITALICO)

func _tela_ip() -> void:
	tela = "ip"
	_limpar()
	_placa("Rede local")
	_espaco(6)
	_texto("Digite o IP que aparece na tela de quem está hospedando.", 15, Color("#cbbd9f"), Tema.FONTE_ITALICO)
	_espaco(4)
	_rotulo_campo("Endereço")
	caixa.add_child(ip_edit)
	_espaco(6)
	_botao("Conectar", _conectar, true)
	_botao("Voltar", _inicio)
	ip_edit.call_deferred("grab_focus")

func _hospedar() -> void:
	var err: String = rede.hospedar()
	if err != "": _avisar(err, true); return
	_tela_login()

func _conectar() -> void:
	var ip := ip_edit.text.strip_edges()
	if ip == "": _avisar("Digite o IP.", true); return
	_guardar("ip", ip)
	var err: String = rede.conectar(ip)
	if err != "": _avisar(err, true); return
	_esperando("Conectando em %s..." % ip)

func _online() -> void:
	_esperando("Abrindo o portão do servidor online...")
	var err: String = rede.conectar_online(auto.get("online", ""), auto.has("tls_inseguro"))
	if err != "": _inicio(); _avisar(err, true)

func _esperando(txt: String) -> void:
	tela = "esperando"
	_limpar()
	_placa("Conectando")
	_espaco(70)
	_texto(txt, 18, Color("#e0d0a8"), Tema.FONTE_ITALICO)
	_espaco(10)
	_divisor()
	_espaco(70)
	_botao("Cancelar", func(): rede.sair(); _inicio())

func _tela_login() -> void:
	tela = "login"
	_limpar()
	_placa("Sua conta")
	if rede.hospedando():
		var ips: Array = rede.meus_ips()
		_texto("Você está hospedando. Os amigos entram pelo IP " + ("  ou  ".join(ips) if not ips.is_empty() else "(sem rede local encontrada)"), 15, Color("#9fd0ff"), Tema.FONTE_ITALICO)
		rodape_srv.text = "Hospedando na rede local"
	elif rede.online:
		_texto("Servidor online · conexão cifrada", 15, Color("#a8d890"), Tema.FONTE_ITALICO)
		rodape_srv.text = "Conectado a " + rede.ip_servidor
	else:
		_texto("Conectado a %s" % rede.ip_servidor, 15, Color("#a8d890"), Tema.FONTE_ITALICO)
		rodape_srv.text = "Rede local · " + rede.ip_servidor
	_espaco(2)
	_rotulo_campo("Usuário")
	caixa.add_child(u_edit)
	_rotulo_campo("Senha")
	caixa.add_child(s_edit)
	_espaco(8)
	_botao("Entrar", func(): _conta("login"), true)
	_par(["Criar conta", func(): _conta("cadastro")], ["Voltar", func(): rede.sair(); _inicio()])
	(s_edit if u_edit.text != "" else u_edit).call_deferred("grab_focus")
	if auto.has("conectar"): call_deferred("_conta", "cadastro")

func _conta(tipo: String) -> void:
	var u := u_edit.text.strip_edges().to_lower()
	var s := s_edit.text
	if u.length() < 3: _avisar("O usuário precisa ter pelo menos 3 letras.", true); return
	if s.length() < 4: _avisar("A senha precisa ter pelo menos 4 caracteres.", true); return
	_guardar("usuario", u)
	# a senha nunca viaja pela rede: vai só o resumo; o servidor ainda põe sal e milhares de rodadas
	rede.enviar_srv({"t": tipo, "u": u, "h": (u + ":dark_passage:" + s).sha256_text(), "v": rede.VERSAO})
	_avisar("Aguarde...")

func _tela_personagens(lista: Array, conta: String) -> void:
	tela = "personagens"
	personagens = lista
	_limpar()
	_placa("Personagens")
	_texto("Conta " + conta, 15, Color("#cbbd9f"), Tema.FONTE_ITALICO)
	if lista.is_empty():
		_espaco(30)
		_texto("Nenhum personagem ainda. Crie o primeiro para entrar no deserto.", 16, Color("#a89a80"), Tema.FONTE_ITALICO)
		_espaco(30)
	var rol := ScrollContainer.new()
	rol.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	rol.custom_minimum_size = Vector2(372, mini(lista.size(), 4) * 64 - 6 if not lista.is_empty() else 0)
	var lv := VBoxContainer.new(); lv.add_theme_constant_override("separation", 6)
	lv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rol.add_child(lv)
	if not lista.is_empty(): caixa.add_child(rol)
	for i in lista.size():
		var p: Dictionary = lista[i]
		var idx := i
		lv.add_child(_cartao(p, func(): _jogar(idx)))
	_espaco(4)
	if lista.size() < 6: _botao("Novo personagem", func(): criar_personagem.emit(), lista.is_empty())
	_botao("Sair da conta", func(): rede.sair(); _inicio())

## Cartão de um personagem: retrato da classe, nome, classe e nível.
func _cartao(p: Dictionary, f: Callable) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(372, 58)
	b.add_theme_stylebox_override("normal", _estilo("cartao_normal"))
	b.add_theme_stylebox_override("hover", _estilo("cartao_hover"))
	b.add_theme_stylebox_override("pressed", _estilo("cartao_hover"))
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.pressed.connect(f)
	var cl := str(p.get("classe", ""))
	# retrato: só busto (topo da arte da classe), recortado num quadrado
	var arte := Tema.tex(M + CLASSES_ARTE.get(cl, "classe_humano") + ".png")
	var ret := TextureRect.new()
	if arte:
		var lado := minf(arte.get_width(), arte.get_height() * 0.5)
		var at := AtlasTexture.new(); at.atlas = arte
		at.region = Rect2((arte.get_width() - lado) * 0.5, 0, lado, lado)
		ret.texture = at
	ret.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; ret.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ret.position = Vector2(7, 7); ret.size = Vector2(44, 44)
	ret.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(ret)
	var nome := Tema.rotulo(str(p.get("nome", "?")), 17, Color("#ecdcb4"), Tema.FONTE_TITULO, 3)
	nome.position = Vector2(64, 7); nome.size = Vector2(290, 24); nome.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(nome)
	var info := Tema.rotulo("%s · nível %d" % [NOMES.get(cl, cl), int(p.get("nivel", 1))], 15, Color("#a89a80"), Tema.FONTE_ITALICO, 2)
	info.position = Vector2(64, 30); info.size = Vector2(290, 22); info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(info)
	return b

func _jogar(i: int) -> void:
	rede.enviar_srv({"t": "jogar", "i": i})
	_esperando("Entrando no Deserto de Absinto...")
	caixa.get_child(caixa.get_child_count() - 1).visible = false

## Volta da tela de classes com a escolha.
func criar(classe: String, nome: String) -> void:
	rede.enviar_srv({"t": "criar", "classe": classe, "nome": nome})
	_esperando("Criando %s..." % nome)
	caixa.get_child(caixa.get_child_count() - 1).visible = false

func _msg(m: Dictionary) -> void:
	if auto.has("conectar"): print("[menu] ", m.get("t", ""), " ", m.get("msg", ""))
	match m.get("t", ""):
		"conectado": _tela_login()
		"erro":
			if tela != "login" and tela != "personagens": _tela_login()
			if auto.has("conectar") and str(m["msg"]).contains("já existe"): _conta("login"); return
			_avisar(str(m.get("msg", "")), true)
			if str(m.get("msg", "")).contains("no site") and tela == "login" and not caixa.has_node("Site"):
				var b := _botao("Abrir o site darkpassage.com.br", func(): OS.shell_open("https://" + rede.ONLINE))
				b.name = "Site"
		"conta":
			_tela_personagens(m.get("personagens", []), str(m.get("u", "")))
			if auto.has("conectar"):
				if personagens.is_empty(): criar(auto.get("classe", "anjo"), auto.get("usuario", "Teste").capitalize())
				else: _jogar(0)
		"mapa":
			rede.mensagem.disconnect(_msg)
			no_mundo.emit(rede, m)

func _guardar(k: String, v: String) -> void:
	var cfg := ConfigFile.new()
	cfg.load(CFG)
	cfg.set_value("rede", k, v)
	cfg.save(CFG)

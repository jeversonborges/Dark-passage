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

func _ready() -> void:
	Tema.carregar()
	theme = Tema.tema_janelas()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var fundo := ColorRect.new(); fundo.color = Color(0.025, 0.02, 0.022)
	fundo.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); add_child(fundo)
	var arte := Tema.tex("res://assets/fundo_menu.png")
	if arte:
		var tr := TextureRect.new(); tr.texture = arte
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.modulate = Color(0.5, 0.47, 0.45)
		add_child(tr)
	var tit := Tema.rotulo("DARK PASSAGE", 84, Color("#b0201a"), Tema.FONTE_GOTICA, 10)
	tit.set_anchors_preset(Control.PRESET_CENTER_TOP)
	tit.offset_left = -420; tit.offset_right = 420; tit.offset_top = 40; tit.offset_bottom = 140
	tit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(tit)
	var sub := Tema.rotulo("Deserto de Absinto · Prévia v0.6", 17, Color("#c8bfa8"), Tema.FONTE_ITALICO, 3)
	sub.set_anchors_preset(Control.PRESET_CENTER_TOP)
	sub.offset_left = -400; sub.offset_right = 400; sub.offset_top = 132; sub.offset_bottom = 160
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(sub)
	var painel := PanelContainer.new()
	var sb := Tema.caixa(Color(0.05, 0.04, 0.035, 0.92), Color(0.42, 0.34, 0.2), 1, 3)
	sb.set_content_margin_all(22)
	painel.add_theme_stylebox_override("panel", sb)
	painel.set_anchors_preset(Control.PRESET_CENTER)
	painel.offset_left = -230; painel.offset_right = 230; painel.offset_top = -110; painel.offset_bottom = -110
	painel.grow_vertical = Control.GROW_DIRECTION_END
	add_child(painel)
	caixa = VBoxContainer.new()
	caixa.add_theme_constant_override("separation", 10)
	painel.add_child(caixa)
	for le in [u_edit, s_edit, ip_edit]:
		var sbe := Tema.caixa(Color(0.03, 0.025, 0.02, 0.95), Color(0.42, 0.34, 0.2), 1, 2); sbe.shadow_size = 0; sbe.set_content_margin_all(7)
		le.add_theme_stylebox_override("normal", sbe); le.add_theme_stylebox_override("focus", sbe)
		le.add_theme_font_size_override("font_size", 16)
		le.custom_minimum_size = Vector2(0, 38)
	s_edit.secret = true
	u_edit.max_length = 16; s_edit.max_length = 64
	u_edit.placeholder_text = "usuário"; s_edit.placeholder_text = "senha"
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
		else: _conectar()

func _limpar() -> void:
	for c in caixa.get_children(): caixa.remove_child(c); c.queue_free()
	aviso = null

func _botao(txt: String, f: Callable, destaque := false) -> Button:
	var b := Button.new(); b.text = txt
	b.custom_minimum_size = Vector2(0, 44 if destaque else 38)
	b.add_theme_font_size_override("font_size", 17 if destaque else 15)
	b.pressed.connect(f)
	caixa.add_child(b)
	return b

func _texto(txt: String, tam := 14, cor := Color("#c8bfa8"), fonte: Font = null) -> Label:
	var l := Tema.rotulo(txt, tam, cor, fonte if fonte else Tema.FONTE_TEXTO, 2)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caixa.add_child(l)
	return l

func _avisar(txt: String, erro := false) -> void:
	if aviso == null: aviso = _texto("", 14)
	aviso.text = txt
	aviso.add_theme_color_override("font_color", Color("#ff8a72") if erro else Color("#e8d8a8"))

# =================================================================== telas
func _inicio() -> void:
	tela = "inicio"
	_limpar()
	_botao("Jogar sozinho", func(): solo.emit(), true)
	if OS.has_feature("web"):
		_texto("Para jogar com amigos na rede local, use a versão de Windows.", 13, Color("#8a8070"), Tema.FONTE_ITALICO)
		return
	_botao("Hospedar partida na rede local", _hospedar)
	_botao("Entrar numa partida (IP)", _tela_ip)
	_texto("Hospedar: este PC vira o servidor e guarda as contas.\nEntrar: use o IP que aparece na tela de quem hospedou.", 12, Color("#8a8070"), Tema.FONTE_ITALICO)

func _tela_ip() -> void:
	tela = "ip"
	_limpar()
	_texto("IP de quem está hospedando", 16, Color("#e0c890"), Tema.FONTE_TITULO)
	caixa.add_child(ip_edit)
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
	_limpar()
	_texto("Conectando em %s..." % ip, 16)
	_botao("Cancelar", func(): rede.sair(); _inicio())

func _tela_login() -> void:
	tela = "login"
	_limpar()
	if rede.hospedando():
		var ips: Array = rede.meus_ips()
		var t := "Você está hospedando. Seus amigos entram pelo IP:\n" + ("  ou  ".join(ips) if not ips.is_empty() else "(sem rede local encontrada)")
		_texto(t, 14, Color("#9fd0ff"), Tema.FONTE_TITULO)
	else:
		_texto("Conectado a %s" % rede.ip_servidor, 14, Color("#a8d890"), Tema.FONTE_ITALICO)
	caixa.add_child(u_edit)
	caixa.add_child(s_edit)
	_botao("Entrar", func(): _conta("login"), true)
	_botao("Criar conta", func(): _conta("cadastro"))
	_botao("Voltar", func(): rede.sair(); _inicio())
	(s_edit if u_edit.text != "" else u_edit).call_deferred("grab_focus")
	if auto.has("conectar"): call_deferred("_conta", "cadastro")

func _conta(tipo: String) -> void:
	var u := u_edit.text.strip_edges().to_lower()
	var s := s_edit.text
	if u.length() < 3: _avisar("O usuário precisa ter pelo menos 3 letras.", true); return
	if s.length() < 4: _avisar("A senha precisa ter pelo menos 4 caracteres.", true); return
	_guardar("usuario", u)
	# a senha nunca viaja pela rede: vai só o resumo; o servidor ainda põe sal e milhares de rodadas
	rede.enviar_srv({"t": tipo, "u": u, "h": (u + ":dark_passage:" + s).sha256_text()})
	_avisar("Aguarde...")

func _tela_personagens(lista: Array, conta: String) -> void:
	tela = "personagens"
	personagens = lista
	_limpar()
	_texto("Conta: " + conta, 15, Color("#e0c890"), Tema.FONTE_TITULO)
	if lista.is_empty(): _texto("Nenhum personagem ainda.", 14, Color("#8a8070"), Tema.FONTE_ITALICO)
	for i in lista.size():
		var p: Dictionary = lista[i]
		var idx := i
		_botao("%s  ·  %s, nível %d" % [p["nome"], NOMES.get(p["classe"], p["classe"]), int(p["nivel"])], func(): _jogar(idx), true)
	if lista.size() < 6: _botao("Novo personagem", func(): criar_personagem.emit())
	_botao("Sair", func(): rede.sair(); _inicio())

func _jogar(i: int) -> void:
	rede.enviar_srv({"t": "jogar", "i": i})
	_limpar(); _texto("Entrando no Deserto de Absinto...", 16)

## Volta da tela de classes com a escolha.
func criar(classe: String, nome: String) -> void:
	rede.enviar_srv({"t": "criar", "classe": classe, "nome": nome})
	_limpar(); _texto("Criando %s..." % nome, 16)

func _msg(m: Dictionary) -> void:
	if auto.has("conectar"): print("[menu] ", m.get("t", ""), " ", m.get("msg", ""))
	match m.get("t", ""):
		"conectado": _tela_login()
		"erro":
			if tela != "login" and tela != "personagens": _tela_login()
			if auto.has("conectar") and str(m["msg"]).contains("já existe"): _conta("login"); return
			_avisar(str(m.get("msg", "")), true)
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

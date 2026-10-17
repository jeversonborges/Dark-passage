extends Node
## Entrada: carrega os dados, mostra a tela de abertura (sozinho / hospedar / entrar pelo IP) e liga o jogo.
## Argumentos de teste (depois de --): classe=humano mapa=area_inicial pos=57,53 fotos=pasta
## Rede: servidor=1 [porta=7777] [max=48] [cert=arquivo.crt chave=arquivo.key | tls_teste=1] sobe só o servidor (sem tela);
## sem cert= ele procura ~/certs/darkpassage.crt e .key (a VPS) e, achando, liga o DTLS.
## conectar=IP|hospedar|online [online=host:porta tls_inseguro=1] usuario=x senha=y classe=anjo entra sozinho
## (teste_rede=pasta tira fotos e sai).

const Jogo := preload("res://scripts/client/game.gd")
const Selecao := preload("res://scripts/client/char_select.gd")
const MenuRede := preload("res://scripts/client/menu_rede.gd")
const Rede := preload("res://scripts/net/rede.gd")

var jogo: Node2D
var args := {}
var rede: Node
var camada: CanvasLayer

func _ready() -> void:
	Defs.carregar()
	Tema.carregar()
	for a in OS.get_cmdline_user_args():
		var p := a.split("=", true, 1)
		args[p[0].trim_prefix("--")] = p[1] if p.size() > 1 else "1"
	rede = Rede.new()
	rede.name = "Rede"
	add_child(rede)
	if args.has("servidor"):
		var tls := _tls_servidor()
		var err: String = rede.hospedar(int(args.get("porta", Rede.PORTA)), int(args.get("max", 48)), tls)
		if err != "": printerr(err); get_tree().quit(1); return
		print("[servidor] DARK PASSAGE v%s ouvindo na porta %s, até %s conexões, %s. IPs: %s" % [Rede.VERSAO, args.get("porta", Rede.PORTA),
			args.get("max", 48), "cifrado (DTLS)" if tls else "sem criptografia (rede local)", ", ".join(rede.meus_ips())])
		return
	add_child(Controle.new())   # controle (Xbox/PlayStation): vale em todas as telas, ver scripts/client/controle.gd
	Ajustes.aplicar_inicio()
	add_child(Ajustes.Vigia.new())   # F10 abre as configurações; som em segundo plano
	if args.has("classe") and not args.has("conectar"):
		_comecar(args["classe"], "Teste", {})
		return
	Tela.aplicar_salvo()
	var at := AtalhoTela.new()
	at.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(at)
	_abertura("")
	if args.has("foto_menu"):   # teste: print da tela de abertura
		get_tree().create_timer(2.0).timeout.connect(func():
			get_viewport().get_texture().get_image().save_png(args["foto_menu"]); get_tree().quit())
	rede.caiu.connect(func(motivo):
		if jogo != null:   # caiu no meio do jogo: volta para a abertura com o motivo
			jogo.queue_free(); jogo = null
			_abertura(motivo))

## Certificado do servidor online: cert=/chave= na linha de comando, ou ~/certs/darkpassage.crt|.key.
func _tls_servidor() -> TLSOptions:
	if args.has("tls_teste"):   # só para teste: certificado feito na hora
		var c := Crypto.new()
		var k := c.generate_rsa(2048)
		return TLSOptions.server(k, c.generate_self_signed_certificate(k, "CN=darkpassage.com.br"))
	var dir := OS.get_environment("HOME") + "/certs/"
	var cert: String = args.get("cert", dir + "darkpassage.crt")
	var chave: String = args.get("chave", dir + "darkpassage.key")
	if not FileAccess.file_exists(cert) or not FileAccess.file_exists(chave):
		if args.has("cert"): printerr("[servidor] certificado não encontrado: ", cert)
		return null
	var x := X509Certificate.new(); var k := CryptoKey.new()
	if x.load(cert) != OK or k.load(chave) != OK:
		printerr("[servidor] não deu para ler o certificado/chave em ", cert); return null
	return TLSOptions.server(k, x)

## F11 / Alt+Enter também com o jogo pausado (menu Esc).
class AtalhoTela extends Node:
	func _input(ev: InputEvent) -> void:
		if Tela.atalho(ev):
			Tela.alternar()
			get_viewport().set_input_as_handled()

func _abertura(motivo: String) -> void:
	if camada: camada.queue_free()
	camada = CanvasLayer.new()
	add_child(camada)
	var menu := MenuRede.new()
	if args.has("conectar"): menu.auto = args
	camada.add_child(menu)
	if motivo != "": menu._avisar(motivo, true)
	menu.solo.connect(func(): _selecao(false, menu))
	menu.criar_personagem.connect(func(): _selecao(true, menu))
	menu.no_mundo.connect(func(r: Node, m: Dictionary):
		camada.queue_free(); camada = null
		jogo = Jogo.new()
		add_child(jogo)
		jogo.iniciar_rede(r, m)
		if args.has("teste_gm"):   # teste do painel do GM (entregas/gm, tools/teste_gm.gd)
			var tg: Node = load("res://tools/teste_gm.gd").new()
			tg.jogo = jogo; tg.args = args
			add_child(tg)
		if args.has("teste_rede"):
			var t: Node = load("res://tools/teste_rede.gd").new()
			t.jogo = jogo; t.args = args
			add_child(t))

func _selecao(em_rede: bool, menu: Control) -> void:
	var cl := CanvasLayer.new()
	cl.layer = 5
	add_child(cl)
	var sel := Selecao.new()
	sel.modo_rede = em_rede
	cl.add_child(sel)
	sel.voltar.connect(func(): cl.queue_free())
	sel.escolhido.connect(func(c: String, n: String, s: Dictionary):
		cl.queue_free()
		if em_rede: menu.criar(c, n)
		else:
			if camada: camada.queue_free(); camada = null
			_comecar(c, n, s))

func _comecar(classe: String, nome: String, salvo: Dictionary) -> void:
	jogo = Jogo.new()
	add_child(jogo)
	jogo.iniciar(classe, nome, salvo)
	if args.has("mapa") or args.has("pos"):
		var pos := Vector2(-1, -1)
		if args.has("pos"):
			var xy: PackedStringArray = args["pos"].split(",")
			pos = Vector2(float(xy[0]), float(xy[1]))
		jogo._entrar(args.get("mapa", jogo.sim.mapa_id), pos)
	if args.has("teste_andar"):
		var ta: Node = load("res://tools/teste_andar.gd").new()
		ta.jogo = jogo; ta.args = args
		add_child(ta)
	if args.has("teste_controle"):
		var tc: Node = load("res://tools/teste_controle.gd").new()
		tc.jogo = jogo; tc.args = args
		add_child(tc)
	if args.has("fotos_config"):
		var tc: Node = load("res://tools/teste_config.gd").new()
		tc.jogo = jogo; tc.dir = args["fotos_config"]
		add_child(tc)
	if args.has("fotos"):
		var t: Node = load("res://tools/teste_visual.gd").new()
		t.jogo = jogo; t.args = args
		add_child(t)

extends Node
## Entrada: carrega os dados, mostra a tela de abertura (sozinho / hospedar / entrar pelo IP) e liga o jogo.
## Argumentos de teste (depois de --): classe=humano mapa=area_inicial pos=57,53 fotos=pasta
## Rede: servidor=1 [porta=7777] sobe só o servidor (sem tela); conectar=IP|hospedar usuario=x senha=y classe=anjo
## entra sozinho (teste_rede=pasta tira fotos e sai).

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
		var err: String = rede.hospedar(int(args.get("porta", Rede.PORTA)))
		if err != "": printerr(err); get_tree().quit(1); return
		print("[servidor] DARK PASSAGE ouvindo na porta %s. IPs: %s" % [args.get("porta", Rede.PORTA), ", ".join(rede.meus_ips())])
		return
	if args.has("classe") and not args.has("conectar"):
		_comecar(args["classe"], "Teste", {})
		return
	_abertura("")
	if args.has("foto_menu"):   # teste: print da tela de abertura
		get_tree().create_timer(2.0).timeout.connect(func():
			get_viewport().get_texture().get_image().save_png(args["foto_menu"]); get_tree().quit())
	rede.caiu.connect(func(motivo):
		if jogo != null:   # caiu no meio do jogo: volta para a abertura com o motivo
			jogo.queue_free(); jogo = null
			_abertura(motivo))

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
	if args.has("fotos"):
		var t: Node = load("res://tools/teste_visual.gd").new()
		t.jogo = jogo; t.args = args
		add_child(t)

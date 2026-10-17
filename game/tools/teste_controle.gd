extends Node
## Teste do controle (scripts/client/controle.gd) sem controle de verdade: injeta eventos de joypad.
## Uso: xvfb-run godot --rendering-driver opengl3 --fixed-fps 30 -- classe=humano teste_controle=/pasta
## Confere: andar pelo stick nas direções da tela, parar ao soltar, alvo e ataque, LT+D-pad abre a mochila e
## liga o cursor, B fecha, o mouse devolve o modo teclado. Tira fotos do HUD com glifos, da mochila e da tela Controle.

var jogo: Node2D
var args := {}
var t := 0.0
var passo := 0
var p0 := Vector2.ZERO
var falhas := 0
var c0 := Vector2.ZERO

func _eixo(ax: int, v: float) -> void:
	var e := InputEventJoypadMotion.new(); e.device = 0; e.axis = ax; e.axis_value = v
	Input.parse_input_event(e)

func _botao(b: int, p: bool) -> void:
	var e := InputEventJoypadButton.new(); e.device = 0; e.button_index = b; e.pressed = p
	Input.parse_input_event(e)

func _ok(cond: bool, txt: String) -> void:
	print("[controle] ", "ok   " if cond else "FALHA", " ", txt)
	if not cond: falhas += 1

func _foto(nome: String) -> void:
	if not args.has("teste_controle") or args["teste_controle"] == "1": return
	var d: String = args["teste_controle"]
	DirAccess.make_dir_recursive_absolute(d)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [d, nome])

func _process(dt: float) -> void:
	if jogo == null or jogo.jog == null: return
	t += dt
	var ct: Controle = Controle.inst
	var tela := func(): return Iso.to_screen(jogo.jog.pos)
	match passo:
		0:
			if t > 2.0:
				p0 = tela.call(); _eixo(JOY_AXIS_LEFT_X, 1.0); passo = 1; t = 0
		1:
			if t > 1.0:
				var d: Vector2 = tela.call() - p0
				_ok(ct.ativo and ct._modo == "mundo", "modo controle ligado no mundo")
				_ok(d.x > 60 and absf(d.y) < d.x * 0.35, "stick para a direita anda para a direita da tela (%s)" % d)
				_eixo(JOY_AXIS_LEFT_X, 0.0); passo = 2; t = 0
		2:
			if t > 0.4: p0 = tela.call()
			if t > 0.8:
				_ok((tela.call() - p0).length() < 4.0, "soltar o stick para")
				p0 = tela.call(); _eixo(JOY_AXIS_LEFT_Y, -1.0); passo = 3; t = 0
		3:
			if t > 0.8:
				var d: Vector2 = tela.call() - p0
				_ok(d.y < -30 and absf(d.x) < -d.y * 0.5, "stick para cima anda para cima da tela (%s)" % d)
				_eixo(JOY_AXIS_LEFT_Y, 0.0); passo = 4; t = 0
		4:
			if t > 0.5:
				_botao(JOY_BUTTON_LEFT_SHOULDER, true); passo = 5; t = 0
		5:
			if t > 0.1:
				_botao(JOY_BUTTON_LEFT_SHOULDER, false)
				var a: int = ct.mira.alvo()
				print("[controle] alvo depois do LB: ", a, " ", jogo.sim.ents[a].nome if a != -1 else "(nenhum inimigo a 9 passos)")
				if a != -1:
					_botao(JOY_BUTTON_A, true)
				passo = 6; t = 0
		6:
			if t > 0.3:
				_botao(JOY_BUTTON_A, false)
				var a: int = ct.mira.alvo()
				if a != -1:
					_ok(jogo.jog.alvo == a, "A ataca o alvo da mira")
					_botao(JOY_BUTTON_B, true); _botao(JOY_BUTTON_B, false)   # B = skill 1 no alvo
				_foto("1_mundo_glifos")
				_eixo(JOY_AXIS_TRIGGER_LEFT, 1.0); passo = 7; t = 0
		7:
			if t > 0.1: _botao(JOY_BUTTON_DPAD_UP, true); passo = 8; t = 0
		8:
			if t > 0.1:
				_botao(JOY_BUTTON_DPAD_UP, false); _eixo(JOY_AXIS_TRIGGER_LEFT, 0.0)
				passo = 9; t = 0
		9:
			if t > 0.2:
				_ok(jogo.janelas.aberta("inventario"), "LT + D-pad cima abre a mochila")
				_ok(ct._modo == "cursor", "janela aberta liga o cursor")
				c0 = ct.cursor; _eixo(JOY_AXIS_LEFT_X, 0.8); _eixo(JOY_AXIS_LEFT_Y, 0.5)
				passo = 10; t = 0
		10:
			if t > 0.4:
				_eixo(JOY_AXIS_LEFT_X, 0.0); _eixo(JOY_AXIS_LEFT_Y, 0.0)
				_ok(ct.cursor.x > c0.x + 40 and ct.cursor.y > c0.y + 10, "stick leva o cursor (%s -> %s)" % [c0, ct.cursor])
				_ok(get_viewport().get_mouse_position().distance_to(ct.cursor) < 3.0, "o mouse do Godot acompanha o cursor (%s, %s)" % [get_viewport().get_mouse_position(), get_viewport().get_final_transform()])
				_foto("2_mochila_cursor")
				_botao(JOY_BUTTON_B, true); passo = 11; t = 0
		11:
			if t > 0.1:
				_botao(JOY_BUTTON_B, false); passo = 12; t = 0
		12:
			if t > 0.2:
				_ok(not jogo.janelas.aberta("inventario"), "B fecha a janela")
				_ok(ct._modo == "mundo", "volta para o modo mundo")
				_botao(JOY_BUTTON_START, true); passo = 13; t = 0
		13:
			if t > 0.1:
				_botao(JOY_BUTTON_START, false); passo = 14; t = 0
		14:
			if t > 0.3:
				_ok(jogo.janelas.aberta("menu"), "Menu abre o menu do jogo")
				_foto("3_menu")
				jogo.janelas.fechar("menu")
				if ResourceLoader.exists("res://scripts/client/configuracoes.gd"):   # com o menu de configurações: aba Controle
					var cfg = load("res://scripts/client/configuracoes.gd")
					cfg.abrir(jogo)
					cfg.aberto.mostrar.call_deferred("controle")
				else: ControleJanela.abrir(jogo)
				passo = 15; t = 0
		15:
			if t > 0.5:
				_foto("4_tela_controle")
				_ok(ct._modo == "cursor", "menu de controle aberto liga o cursor")
				ct.definir("skill_1", "lt+a")
				_ok(ct.mapa["skill_1"] == "lt+a" and ct.mapa["skill_5"] == "b", "trocar botão troca com a ação que o usava")
				ct.restaurar_padrao()
				var m := InputEventMouseMotion.new(); m.relative = Vector2(20, 0); m.position = Vector2(300, 300)
				Input.parse_input_event(m)
				passo = 16; t = 0
		16:
			if t > 0.2:
				_ok(not ct.ativo, "mexer o mouse volta para teclado e mouse")
				print("[controle] fim: %d falha(s)" % falhas)
				get_tree().quit(1 if falhas > 0 else 0)

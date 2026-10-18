extends Node
## Teste da esquiva (entregas/evasao): botão direito de verdade (evento de mouse), Espaço, cargas, recarga de 10 s,
## invulnerabilidade, trava por atordoamento e fotos do meio da esquiva com o HUD.
## Uso: godot -- classe=humano teste_evasao=/pasta   (copiar para game/tools/; o aplicar.py liga o argumento no main.gd)

var jogo: Node2D
var args := {}
var t := 0.0
var passo := 0
var p0 := Vector2.ZERO
var log := []
var fotos := 0

func _ok(cond: bool, txt: String) -> void:
	var l: String = ("[evasao] OK   " if cond else "[evasao] FALHA ") + str(jogo.jog.classe) + " " + txt
	print(l); log.append(l)

func _foto(nome: String) -> void:
	var dir: String = args["teste_evasao"]
	DirAccess.make_dir_recursive_absolute(dir)
	get_viewport().get_texture().get_image().save_png("%s/%s_%s.png" % [dir, jogo.jog.classe, nome])

func _clique_direito() -> void:
	var tela := get_viewport().get_visible_rect().size
	var p := tela * 0.5 + Vector2(220, 40)
	Input.warp_mouse(p)
	for apertou in [true, false]:
		var e := InputEventMouseButton.new()
		e.button_index = MOUSE_BUTTON_RIGHT; e.pressed = apertou; e.position = p; e.global_position = p
		Input.parse_input_event(e)

func _process(dt: float) -> void:
	if jogo == null or jogo.jog == null: return
	t += dt
	var j: Ent = jogo.jog
	var v = jogo.views.get(j.id)
	match passo:
		0:
			if t < 2.5: return
			# tira os inimigos de perto para a esquiva não ser interrompida
			_ok(Evasao.cargas(j) == 2, "começa com 2 cargas (%d)" % Evasao.cargas(j))
			p0 = j.pos
			_clique_direito()
			passo = 1; t = 0.0
		1:
			if t < 0.05: return
			if fotos == 0 and v and v.anim == "evasao": _foto("meio_1"); fotos = 1
			if t < 0.12: return
			_ok(Evasao.cargas(j) == 1, "botão direito gastou 1 carga (%d)" % Evasao.cargas(j))
			_ok(j.invuln_t > 0.0 or not j.deslocando.is_empty(), "invulnerável/deslocando logo depois (invuln %.2f)" % j.invuln_t)
			_ok(v != null and (v.anim == "evasao" or v.anim == "dash" or v.anim_unica != ""), "folha tocando: %s" % (v.anim if v else "?"))
			passo = 2; t = 0.0
		2:
			if t < 0.6: return
			var d: float = j.pos.distance_to(p0)
			var h: Dictionary = Evasao.defn(j)
			_ok(d > 1.0 and d <= float(h["deslocamento"]) + 0.2, "andou %.2f tiles (máx %.1f)" % [d, float(h["deslocamento"])])
			# Espaço gasta a segunda
			var k := InputEventKey.new(); k.keycode = KEY_SPACE; k.physical_keycode = KEY_SPACE; k.pressed = true
			Input.parse_input_event(k)
			var k2 := InputEventKey.new(); k2.keycode = KEY_SPACE; k2.physical_keycode = KEY_SPACE; k2.pressed = false
			Input.parse_input_event(k2)
			passo = 3; t = 0.0
		3:
			if t < 0.08: return
			if fotos == 1: _foto("meio_2"); fotos = 2
			if t < 0.6: return
			_ok(Evasao.cargas(j) == 0, "Espaço gastou a segunda (%d)" % Evasao.cargas(j))
			p0 = j.pos
			jogo.evadir(j.pos + Vector2(-3, 0))
			passo = 4; t = 0.0
		4:
			if t < 0.5: return
			_ok(j.pos.distance_to(p0) < 0.05, "sem carga não esquiva")
			_foto("sem_carga")
			passo = 5; t = 0.0
		5:
			if t < 10.2: return
			_ok(Evasao.cargas(j) == 1, "10 s depois voltou 1 carga (%d)" % Evasao.cargas(j))
			j.status["atordoado"] = {"t": 1.0}
			p0 = j.pos
			jogo.evadir(j.pos + Vector2(3, 0))
			passo = 6; t = 0.0
		6:
			if t < 0.3: return
			_ok(j.pos.distance_to(p0) < 0.05 and Evasao.cargas(j) == 1, "atordoado não esquiva e não gasta")
			passo = 7; t = 0.0
		7:
			if t < 10.2: return
			passo = 8
			_ok(Evasao.cargas(j) == 2, "20 s depois as 2 cargas (%d)" % Evasao.cargas(j))
			_foto("cheio")
			var f := FileAccess.open("%s/%s.txt" % [args["teste_evasao"], j.classe], FileAccess.WRITE)
			f.store_string("\n".join(log) + "\n")
			get_tree().quit()

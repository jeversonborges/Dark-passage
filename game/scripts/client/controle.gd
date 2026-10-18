class_name Controle
extends Node
## Controle (Xbox em primeiro lugar; PlayStation e genéricos pelo mapa SDL do Godot).
## Um nó só, criado pelo main.gd e vivo em todas as telas. Quem usou por último manda: mexeu no controle,
## o jogo passa para o modo controle; mexeu no mouse ou no teclado, volta tudo como era.
##
## Dois modos, trocados sozinhos:
## - MUNDO (jogando, sem janela aberta): stick esquerdo anda, stick direito mira, botões soltam ataque, skills,
##   poções e janelas. A mira (alvo e ponto) vem de MiraControle (scripts/client/mira_controle.gd, thread
##   "Combate no controle"); sem ela, a MiraBasica daqui faz o mínimo. O game.gd lê `ponteiro()` no lugar do mouse.
## - CURSOR (qualquer janela, mapa, menu, telas de abertura e seleção, morto): o stick esquerdo leva um cursor de
##   latão; A clica, X é o botão direito, B volta (Esc), stick direito rola, LB segurado deixa o cursor fino.
##   O D-pad continua navegando pelo foco do Godot (menus de botões) e, depois de navegar pelo D-pad, A aperta o
##   botão em foco.
## O mapa de botões fica em user://controle.cfg e se troca na aba/janela "Controle" (controle_janela.gd).

static var inst: Controle = null

const CFG := "user://controle.cfg"
const BOTAO := {
	"a": JOY_BUTTON_A, "b": JOY_BUTTON_B, "x": JOY_BUTTON_X, "y": JOY_BUTTON_Y,
	"lb": JOY_BUTTON_LEFT_SHOULDER, "rb": JOY_BUTTON_RIGHT_SHOULDER, "l3": JOY_BUTTON_LEFT_STICK, "r3": JOY_BUTTON_RIGHT_STICK,
	"view": JOY_BUTTON_BACK, "menu": JOY_BUTTON_START,
	"cima": JOY_BUTTON_DPAD_UP, "baixo": JOY_BUTTON_DPAD_DOWN, "esquerda": JOY_BUTTON_DPAD_LEFT, "direita": JOY_BUTTON_DPAD_RIGHT}
const GATILHO := {"lt": JOY_AXIS_TRIGGER_LEFT, "rt": JOY_AXIS_TRIGGER_RIGHT}
const CAMADA := "lt"   # segurar LT troca a camada dos botões (skills 5-9 e janelas)
const NOME_BOTAO := {
	"xbox": {"a": "A", "b": "B", "x": "X", "y": "Y", "lb": "LB", "rb": "RB", "lt": "LT", "rt": "RT", "l3": "L3", "r3": "R3",
		"view": "View", "menu": "Menu", "cima": "D-pad ↑", "baixo": "D-pad ↓", "esquerda": "D-pad ←", "direita": "D-pad →"},
	"ps": {"a": "✕", "b": "○", "x": "□", "y": "△", "lb": "L1", "rb": "R1", "lt": "L2", "rt": "R2", "l3": "L3", "r3": "R3",
		"view": "Share", "menu": "Options", "cima": "D-pad ↑", "baixo": "D-pad ↓", "esquerda": "D-pad ←", "direita": "D-pad →"}}

## [id, nome, grupo, botão padrão]. "lt+x" = segurar LT e apertar X.
const ACOES := [
	["atacar", "Ataque básico (sem inimigo: falar, abrir, pegar)", "Combate", "a"],
	["skill_1", "Skill 1", "Combate", "b"],
	["skill_2", "Skill 2", "Combate", "x"],
	["skill_3", "Skill 3", "Combate", "y"],
	["skill_4", "Skill 4", "Combate", "rb"],
	["skill_5", "Skill 5", "Combate", "lt+a"],
	["skill_6", "Skill 6", "Combate", "lt+b"],
	["skill_7", "Skill 7", "Combate", "lt+x"],
	["skill_8", "Skill 8", "Combate", "lt+y"],
	["skill_9", "Skill 9", "Combate", "lt+rb"],
	["evadir", "Esquiva (botão direito)", "Combate", "rt"],
	["interagir", "Pegar item, falar, abrir baú", "Combate", "lt+rt"],
	["alvo", "Próximo alvo", "Combate", "lb"],
	["travar", "Travar / soltar alvo", "Combate", "r3"],
	["auto", "Modo automático (Z)", "Combate", "l3"],
	["pocao_vida", "Poção de vida (Q)", "Cinto", "cima"],
	["pocao_recurso", "Poção de recurso (W)", "Cinto", "baixo"],
	["antidoto", "Antídoto (E)", "Cinto", "esquerda"],
	["vela", "Voltar ao acampamento (R)", "Cinto", "direita"],
	["inventario", "Mochila (I)", "Janelas", "lt+cima"],
	["personagem", "Personagem (C)", "Janelas", "lt+direita"],
	["missoes", "Missões (J)", "Janelas", "lt+baixo"],
	["habilidades", "Habilidades (K)", "Janelas", "lt+esquerda"],
	["talentos", "Talentos (T)", "Janelas", "lt+lb"],
	["auto_cfg", "Ajustes do automático (Shift+Z)", "Janelas", "lt+l3"],
	["mapa", "Mapa (M)", "Sistema", "view"],
	["ajuda", "Como jogar (H)", "Sistema", "lt+view"],
	["menu", "Menu / pausa (Esc)", "Sistema", "menu"],
]
## Ações que valem também com janela aberta (para fechar a mesma janela com o mesmo botão).
const GLOBAIS := ["inventario", "personagem", "missoes", "habilidades", "talentos", "auto_cfg", "mapa", "ajuda"]

# ajustes (salvos em CFG, seção "ajustes")
const PADRAO := {"zona_morta": 0.22, "cursor_vel": 1.0, "vibracao": 0.8, "icones": "auto", "canhoto": false}

var _ult_esq := Vector2.ZERO   # stick esquerdo do quadro (direção da esquiva)
var mapa := {}            # id da ação -> botão ("a", "lt+b"...)
var ajustes := PADRAO.duplicate()
var ativo := false        # o último input foi do controle
var disp := -1            # device do controle em uso
var nome_disp := ""
var cursor := Vector2(640, 360)
var _ant := {}            # token -> apertado no frame anterior
var _acao_do_token := {}  # token -> ação disparada no aperto (o soltar vai para a mesma)
var _seg_t := {}          # ação -> tempo segurando
var _ult_mov := Vector2.ZERO
var _t_mov := 0.0
var _parado := true
var _t_rolar := 0.0
var _gerando_frame := -1
var _foco_dpad := false   # o último movimento na interface foi pelo D-pad (A aperta o foco em vez de clicar)
var _modo := ""
var _capturar: Callable   # tela de configuração esperando um botão
var _cap_t := 0.0
var _camada_cursor: CanvasLayer
var _spr_cursor: Sprite2D
var mira: Node = null     # MiraControle (ou MiraBasica)
var _game_visto: Node = null
var _avisou := false
var _cfg_script = load("res://scripts/client/configuracoes.gd") if ResourceLoader.exists("res://scripts/client/configuracoes.gd") else null

func _ready() -> void:
	inst = self
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_priority = -10   # antes do game.gd: o ponteiro do frame já está pronto quando ele lê
	carregar()
	_camada_cursor = CanvasLayer.new(); _camada_cursor.layer = 128
	add_child(_camada_cursor)
	_spr_cursor = Sprite2D.new(); _spr_cursor.centered = false; _spr_cursor.visible = false
	_spr_cursor.texture = Tema.ui("pad_cursor")
	_camada_cursor.add_child(_spr_cursor)
	Input.joy_connection_changed.connect(_conexao)
	for d in Input.get_connected_joypads(): _conexao(d, true)
	if ClassDB.class_exists("Ajustes") or ResourceLoader.exists("res://scripts/client/ajustes.gd"):
		ControleJanela.registrar_aba.call_deferred()

# =================================================================== configuração
func carregar() -> void:
	mapa.clear()
	for a in ACOES: mapa[a[0]] = a[3]
	var cf := ConfigFile.new()
	if cf.load(CFG) != OK: return
	for a in ACOES:
		var b := str(cf.get_value("botoes", a[0], a[3]))
		if _botao_valido(b): mapa[a[0]] = b
	for k in PADRAO: ajustes[k] = cf.get_value("ajustes", k, PADRAO[k])
	_migrar_evasao(cf)

## Configuração salva antes da esquiva: RT era "interagir" e LT+RT os ajustes do automático. Se o jogador não
## tinha mexido nesses dois, passa para o padrão novo (RT esquiva, LT+RT interagir, LT+L3 ajustes).
func _migrar_evasao(cf: ConfigFile) -> void:
	if cf.has_section_key("botoes", "evadir"): return
	if mapa.get("interagir", "") == "rt" and mapa.get("auto_cfg", "") == "lt+rt":
		mapa["interagir"] = "lt+rt"; mapa["auto_cfg"] = "lt+l3"; mapa["evadir"] = "rt"
	else:
		for k in mapa: if k != "evadir" and mapa[k] == mapa["evadir"]: mapa["evadir"] = ""   # sem conflito: fica sem botão até escolher

func salvar() -> void:
	var cf := ConfigFile.new()
	for k in mapa: cf.set_value("botoes", k, mapa[k])
	for k in ajustes: cf.set_value("ajustes", k, ajustes[k])
	cf.save(CFG)

func restaurar_padrao() -> void:
	for a in ACOES: mapa[a[0]] = a[3]
	ajustes = PADRAO.duplicate()
	salvar()

static func _botao_valido(b: String) -> bool:
	var t := b.trim_prefix(CAMADA + "+")
	return (BOTAO.has(t) or t == "rt") and b != CAMADA

## Liga o botão à ação; se outra ação usava esse botão, as duas trocam (nada fica sem botão).
func definir(acao: String, botao: String) -> void:
	if not _botao_valido(botao): return
	var antigo: String = mapa.get(acao, "")
	for k in mapa:
		if k != acao and mapa[k] == botao: mapa[k] = antigo
	mapa[acao] = botao
	salvar()

## A tela de configuração pede o próximo botão; recebe "" se o jogador cancelar (B segurado ou Esc).
func capturar(cb: Callable) -> void:
	_capturar = cb; _cap_t = 0.0

func acao_de(botao: String) -> String:
	for k in mapa:
		if mapa[k] == botao: return k
	return ""

func estilo_icones() -> String:
	if ajustes["icones"] != "auto": return ajustes["icones"]
	var n := nome_disp.to_lower()
	return "ps" if (n.contains("playstation") or n.contains("dualsense") or n.contains("dualshock") or n.contains("ps4") or n.contains("ps5") or n.contains("sony")) else "xbox"

## Texturas do botão (1 ou 2, a camada LT primeiro). Para a barra de skills e a tela de configuração.
func glifos(botao: String, grande := false) -> Array:
	var e := estilo_icones()
	var r := []
	for t in botao.split("+"):
		var tx: Texture2D = Tema.tex("res://assets/ext/ui/%s/pad_%s_%s.png" % ["2x" if grande else "1x", e, t])
		if tx: r.append(tx)
	return r

func nome_botao(botao: String) -> String:
	var n: Dictionary = NOME_BOTAO[estilo_icones()]
	var partes := []
	for t in botao.split("+"): partes.append(n.get(t, t))
	return " + ".join(partes)

static func pad_ativo() -> bool:
	return inst != null and inst.ativo

## Vibração curta (fraco = motor leve, forte = motor pesado, 0..1). Respeita o ajuste "vibracao".
static func vibrar(fraco: float, forte: float, dur: float) -> void:
	if inst == null or not inst.ativo or inst.disp < 0: return
	var k := float(inst.ajustes["vibracao"])
	if k <= 0.0: return
	Input.start_joy_vibration(inst.disp, clampf(fraco * k, 0, 1), clampf(forte * k, 0, 1), dur)

# =================================================================== dispositivo
func _conexao(d: int, ligado: bool) -> void:
	if ligado:
		if disp == -1 or not disp in Input.get_connected_joypads(): disp = d
		nome_disp = Input.get_joy_name(disp)
		var g := _game()
		if g != null and g.hud: g.hud.aviso("Controle conectado: %s" % nome_disp, Color("#e8d29a"))
	elif d == disp:
		var outros := Input.get_connected_joypads()
		disp = outros[0] if outros.size() > 0 else -1
		nome_disp = Input.get_joy_name(disp) if disp >= 0 else ""
		if disp == -1 and ativo:
			_set_ativo(false)
			var g2 := _game()
			if g2 != null and g2.hud: g2.hud.aviso("Controle desconectado.", Color("#ff9a80"))

func _set_ativo(v: bool) -> void:
	if ativo == v: return
	ativo = v
	if mira != null and "ativo" in mira: mira.ativo = v
	if not v:
		_spr_cursor.visible = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_soltar_movimento()
	else:
		Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
		cursor = get_viewport().get_mouse_position()
		var g := _game()
		if not _avisou and g != null and g.hud:
			_avisou = true
			g.hud.aviso("Modo controle. Menu → Controle mostra e troca os botões.", Color("#e8d29a"))

func _input(ev: InputEvent) -> void:
	if ev is InputEventJoypadMotion:
		if absf(ev.axis_value) > maxf(0.35, float(ajustes["zona_morta"])):
			disp = ev.device; _set_ativo(true)
		get_viewport().set_input_as_handled()   # os sticks são lidos aqui; não deixa o foco do Godot andar sozinho
	elif ev is InputEventJoypadButton:
		disp = ev.device
		if nome_disp == "": nome_disp = Input.get_joy_name(disp)
		_set_ativo(true)
		var dpad: bool = ev.button_index in [JOY_BUTTON_DPAD_UP, JOY_BUTTON_DPAD_DOWN, JOY_BUTTON_DPAD_LEFT, JOY_BUTTON_DPAD_RIGHT]
		if _modo == "cursor" and dpad and _foco_existe():
			if ev.pressed: _foco_dpad = true
			return   # D-pad navega no foco do Godot
		if _modo == "cursor" and ev.button_index == JOY_BUTTON_A and _foco_dpad and _foco_existe():
			return   # A aperta o botão em foco (ui_accept)
		get_viewport().set_input_as_handled()
	elif ev is InputEventMouseMotion:
		# o movimento que nós mesmos geramos chega (às vezes acumulado, um frame depois) na posição do cursor
		if ev.relative.length() > 3.0 and ev.position.distance_to(_para_janela(cursor)) > 2.0: _set_ativo(false)
	elif Engine.get_process_frames() - _gerando_frame <= 2:
		return   # cliques e teclas que nós mesmos geramos
	elif ev is InputEventMouseButton or (ev is InputEventKey and ev.pressed):
		_set_ativo(false)

func _foco_existe() -> bool:
	return get_viewport().gui_get_focus_owner() != null

# =================================================================== laço
func _process(dt: float) -> void:
	if disp < 0 or not ativo:
		_ant.clear()
		if _capturar.is_valid() and disp >= 0: _ler_captura(dt)
		return
	var g := _game()
	_ligar_mira(g)
	var no_mundo := _pode_mundo(g)
	var modo := "mundo" if no_mundo else "cursor"
	if modo != _modo:
		_modo = modo
		if modo == "cursor": _entrar_cursor(g)
		else: _soltar_movimento(); _spr_cursor.visible = false; _foco_dpad = false
	var esq := _stick(JOY_AXIS_LEFT_X, JOY_AXIS_LEFT_Y)
	var dir := _stick(JOY_AXIS_RIGHT_X, JOY_AXIS_RIGHT_Y)
	if ajustes["canhoto"]:   # canhoto: os sticks trocam de função
		var tmp := esq
		esq = dir; dir = tmp
	if _capturar.is_valid(): _ler_captura(dt); return
	if modo == "mundo": _passo_mundo(g, dt, esq, dir)
	else: _passo_cursor(g, dt, esq, dir)

func _game() -> Node:
	if is_instance_valid(_game_visto) and _game_visto.is_inside_tree(): return _game_visto
	_game_visto = null
	for n in get_tree().get_nodes_in_group("jogo_cliente"):
		_game_visto = n; break
	return _game_visto

func _pode_mundo(g: Node) -> bool:
	if g == null or g.jog == null or not g.jog.vivo or g.trocando: return false
	if g.hud.chat_aberto(): return false
	if g.hud.mapa_ui and g.hud.mapa_ui.visible: return false
	if g.hud.ajuda_ui and g.hud.ajuda_ui.visible: return false
	for n in g.janelas.jan:
		if g.janelas.jan[n].visible: return false
	if g.janelas.mao_ativa(): return false
	if get_tree().paused: return false
	for n in get_tree().get_nodes_in_group("menu_aberto"):   # menus de outras frentes
		if n.visible: return false
	if _cfg_script != null and _cfg_script.esta_aberto(): return false   # menu de configurações (F10)
	return true

func _stick(ax: int, ay: int) -> Vector2:
	var v := Vector2(Input.get_joy_axis(disp, ax), Input.get_joy_axis(disp, ay))
	var zm := float(ajustes["zona_morta"])
	var l := v.length()
	if l < zm: return Vector2.ZERO
	return v / l * clampf((l - zm) / (1.0 - zm), 0.0, 1.0)   # zona morta radial, reescalada

func _apertado(t: String) -> bool:
	if GATILHO.has(t): return Input.get_joy_axis(disp, GATILHO[t]) > 0.5
	return Input.is_joy_button_pressed(disp, BOTAO[t])

## Botões que mudaram neste frame: [[token, apertou], ...]
func _bordas() -> Array:
	var r := []
	for t in BOTAO.keys() + ["lt", "rt"]:
		var a := _apertado(t)
		if a != _ant.get(t, false): r.append([t, a])
		_ant[t] = a
	return r

func _resolver(t: String) -> String:
	if t == CAMADA: return ""
	if _apertado(CAMADA):
		var c := acao_de(CAMADA + "+" + t)
		if c != "": return c
	return acao_de(t)

func _ler_captura(dt: float) -> void:
	_cap_t += dt
	for b in _bordas():
		if not b[1] or b[0] == CAMADA or _cap_t < 0.15: continue
		var bt: String = (CAMADA + "+" + b[0]) if _apertado(CAMADA) else b[0]
		var cb := _capturar; _capturar = Callable()
		cb.call(bt)
		return

# =================================================================== mundo
func _ligar_mira(g: Node) -> void:
	if g == null: mira = null; return
	if mira != null and is_instance_valid(mira) and mira.get_parent() == g: return
	var m = g.get_node_or_null("MiraControle")
	if m == null:
		var scr = load("res://scripts/client/mira_controle.gd") if ResourceLoader.exists("res://scripts/client/mira_controle.gd") else MiraBasica
		m = scr.new(); m.name = "MiraControle"
		m.game = g
		g.add_child(m)
	mira = m
	if "ativo" in mira: mira.ativo = ativo

func _passo_mundo(g: Node, dt: float, esq: Vector2, dir: Vector2) -> void:
	if "ativo" in mira: mira.ativo = true   # o MiraControle se desliga com o mouse, inclusive o cursor que geramos nas janelas
	mira.passo(dt, esq, dir)
	_ult_esq = esq
	_mover(g, dt, esq)
	for b in _bordas():
		var t: String = b[0]
		if b[1]:
			var ac := _resolver(t)
			_acao_do_token[t] = ac
			if ac != "": _disparar(g, ac); _seg_t[ac] = 0.0
		else:
			var ac2: String = _acao_do_token.get(t, "")
			_acao_do_token.erase(t); _seg_t.erase(ac2)
	# segurar o ataque: continua batendo (e escolhe o próximo quando o alvo cai)
	if _seg_t.has("atacar"):
		_seg_t["atacar"] += dt
		if fmod(_seg_t["atacar"], 0.2) < dt and _seg_t["atacar"] > 0.2: mira.ataque_basico(true)

func _disparar(g: Node, ac: String) -> void:
	match ac:
		"atacar": mira.ataque_basico(false)
		"interagir": mira.interagir()
		"evadir": _evadir(g)
		"alvo": mira.ciclar_alvo(1)
		"travar": mira.travar_alvo()
		"auto": g.cmd("auto", [not g.jog.aux.get("auto", false)])
		"pocao_vida": g.cmd("pocao", ["vida"])
		"pocao_recurso": g.cmd("pocao", ["recurso"])
		"antidoto": g.cmd("pocao", ["antidoto"])
		"vela": g.usar_vela()
		"inventario", "personagem", "missoes", "habilidades", "talentos": g.janelas.alternar(ac)
		"auto_cfg": g.janelas.alternar("auto")
		"mapa": g.hud.alternar_mapa()
		"ajuda": g.hud.alternar_ajuda()
		"menu": _tecla(KEY_ESCAPE)
		_:
			if ac.begins_with("skill_"): mira.usar_skill(int(ac.substr(6)) - 1)

## Esquiva no controle: para onde o stick esquerdo aponta; parado, para onde o personagem olha.
func _evadir(g: Node) -> void:
	var w: Vector2 = Iso.to_world(_ult_esq).normalized() if _ult_esq.length() > 0.3 else g.jog.facing
	if w == Vector2.ZERO: w = Vector2(0, 1)
	g.evadir(g.jog.pos + w * 4.0)

## Stick esquerdo: anda na direção da TELA (para cima no stick = para cima na tela), passo curto e contínuo.
## Se a frente está bloqueada, desliza pela parede tentando ângulos vizinhos.
func _mover(g: Node, dt: float, v: Vector2) -> void:
	if v == Vector2.ZERO:
		_soltar_movimento(); return
	var jog: Ent = g.jog
	var w := Iso.to_world(v).normalized()
	var passo := 1.2 + 0.4 * v.length()
	var destino := Vector2.INF
	for ang in [0.0, 0.5, -0.5, 1.0, -1.0, 1.4, -1.4]:
		var q: Vector2 = jog.pos + w.rotated(ang) * passo
		if g.sim.andavel(q) and g.sim.visao(jog.pos, q): destino = q; break
	_t_mov -= dt
	var mudou := _ult_mov == Vector2.ZERO or absf(_ult_mov.angle_to(v)) > 0.25
	if destino != Vector2.INF and (mudou or _t_mov <= 0.0 or _parado):
		if _parado: g.cmd("no_lugar", [false])
		g.cmd("mover", [destino])
		_t_mov = 0.1; _ult_mov = v; _parado = false
	elif destino == Vector2.INF and not _parado:
		g.cmd("virar", [w])

func _soltar_movimento() -> void:
	if _parado: return
	_parado = true; _ult_mov = Vector2.ZERO
	var g := _game()
	if g != null and g.jog != null and g.jog.vivo and g.jog.alvo == -1: g.cmd("mover", [g.jog.pos])

## Para onde o game.gd olha no lugar do mouse (coordenadas do mundo desenhado, como get_global_mouse_position).
func ponteiro() -> Vector2:
	var g := _game()
	var id: int = mira.alvo() if mira != null else -1
	if g != null:
		var v = g.views.get(id)
		if v != null and is_instance_valid(v): return v.position + Vector2(0, -v.altura_px * 0.5)
		if g.objs.has(id): return g.objs[id].position + Vector2(0, -25)
	return Iso.to_screen(mira.ponto_mira()) if mira != null else Vector2.ZERO

func no_mundo() -> bool:
	return ativo and _modo == "mundo" and mira != null

# =================================================================== cursor
func _entrar_cursor(g: Node) -> void:
	_soltar_movimento()
	_foco_dpad = false
	cursor = get_viewport().get_visible_rect().size * 0.5
	if g != null:   # começa no meio da janela aberta (diálogo e loja primeiro)
		for n in ["dialogo", "servico", "troca", "inventario", "menu", "auto", "personagem", "habilidades", "missoes", "talentos"]:
			if g.janelas.jan.has(n) and g.janelas.jan[n].visible:
				var r: Rect2 = g.janelas.jan[n].get_global_rect()
				cursor = r.get_center(); break
	_spr_cursor.visible = true
	_mover_cursor(Vector2.ZERO)

func _passo_cursor(g: Node, dt: float, esq: Vector2, dir: Vector2) -> void:
	var fino := _apertado("lb")
	if esq != Vector2.ZERO:
		_foco_dpad = false
		var vel := 1100.0 * float(ajustes["cursor_vel"]) * (0.3 if fino else 1.0)
		_mover_cursor(esq * esq.length() * vel * dt)   # curva quadrática: precisão perto do centro
	_spr_cursor.visible = not _foco_dpad
	# stick direito rola listas
	_t_rolar -= dt
	if absf(dir.y) > 0.4 and _t_rolar <= 0.0:
		_t_rolar = 0.12 / absf(dir.y)
		_clique(MOUSE_BUTTON_WHEEL_DOWN if dir.y > 0 else MOUSE_BUTTON_WHEEL_UP, true); _clique(MOUSE_BUTTON_WHEEL_DOWN if dir.y > 0 else MOUSE_BUTTON_WHEEL_UP, false)
	for b in _bordas():
		var t: String = b[0]
		match t:
			"a":
				if not (_foco_dpad and _foco_existe()): _clique(MOUSE_BUTTON_LEFT, b[1])
			"x": _clique(MOUSE_BUTTON_RIGHT, b[1])
			"b":
				if b[1]: _tecla(KEY_ESCAPE)
			"menu":
				if b[1]: _tecla(KEY_ESCAPE)
			_:
				if b[1] and g != null and g.jog != null:   # LT+D-pad e View fecham a janela que abriram
					var ac := _resolver(t)
					if ac in GLOBAIS: _disparar(g, ac)

func _mover_cursor(d: Vector2) -> void:
	var tam := get_viewport().get_visible_rect().size
	var antes := cursor
	cursor = (cursor + d).clamp(Vector2.ZERO, tam - Vector2(6, 6))   # a ponta fica sempre à vista
	_spr_cursor.position = cursor
	var m := InputEventMouseMotion.new()
	m.position = _para_janela(cursor); m.global_position = m.position
	m.relative = cursor - antes
	m.button_mask = MOUSE_BUTTON_MASK_LEFT if _apertado("a") and not _foco_dpad else 0
	_gerar(m)
	# o mouse do sistema (escondido) vai junto: tooltip, item na mão e get_global_mouse_position() leem dele
	if d != Vector2.ZERO or not _spr_cursor.visible: Input.warp_mouse(m.position)

func _clique(botao: int, apertou: bool) -> void:
	var e := InputEventMouseButton.new()
	e.button_index = botao; e.pressed = apertou
	e.position = _para_janela(cursor); e.global_position = e.position
	if botao == MOUSE_BUTTON_LEFT and apertou: e.button_mask = MOUSE_BUTTON_MASK_LEFT
	_gerar(e)

func _tecla(k: int) -> void:
	for p in [true, false]:
		var e := InputEventKey.new()
		e.keycode = k; e.physical_keycode = k; e.pressed = p
		_gerar(e)

func _gerar(e: InputEvent) -> void:
	_gerando_frame = Engine.get_process_frames()
	Input.parse_input_event(e)

## O cursor vive nas coordenadas da tela base (1280x720 esticada); os eventos vêm em pixels da janela.
func _para_janela(p: Vector2) -> Vector2:
	return get_viewport().get_final_transform() * p

# =================================================================== mira mínima
## Só para o controle funcionar sozinho enquanto o MiraControle (thread "Combate no controle") não chega.
## Alvo macio: o inimigo mais perto na direção do stick direito (ou de onde você anda / olha).
class MiraBasica extends Node:
	var game
	var ativo := false
	var _alvo := -1
	var _travado := false
	var _dir := Vector2(0, 1)   # direção na tela
	var _ponto := Vector2.ZERO

	func passo(_dt: float, dir_mover: Vector2, dir_mira: Vector2) -> void:
		var jog: Ent = game.jog
		if dir_mira != Vector2.ZERO: _dir = dir_mira.normalized()
		elif dir_mover != Vector2.ZERO: _dir = dir_mover.normalized()
		elif jog.facing != Vector2.ZERO: _dir = Iso.to_screen(jog.facing).normalized()
		var e: Ent = game.sim.ents.get(_alvo)
		var valido: bool = e != null and e.vivo and e.alvejavel and not e.invisivel and jog.eh_inimigo_de(e) and e.pos.distance_to(jog.pos) < 11.0
		if not valido: _alvo = -1; _travado = false
		if not _travado and (dir_mira != Vector2.ZERO or _alvo == -1 or jog.alvo == -1):
			var melhor := _escolher(Vector2.INF)
			if melhor != -1 and melhor != _alvo:
				var atual := _nota(game.sim.ents.get(_alvo))
				if _alvo == -1 or _nota(game.sim.ents[melhor]) < atual - 1.0: _alvo = melhor
		var alcance := 3.0 + 4.0 * dir_mira.length()
		_ponto = jog.pos + Iso.to_world(_dir).normalized() * alcance
		if _alvo != -1: _ponto = game.sim.ents[_alvo].pos

	func _nota(e: Ent) -> float:
		if e == null: return 1e9
		var d: Vector2 = Iso.to_screen(e.pos - game.jog.pos)
		var ang := absf(_dir.angle_to(d)) if d.length() > 1.0 else 0.0
		var dist: float = e.pos.distance_to(game.jog.pos)
		if dist > 9.0 or ang > 1.3: return 1e9
		return dist + ang * 4.0

	func _escolher(_x: Vector2) -> int:
		var melhor := -1; var mn := 1e9
		for e: Ent in game.sim.ents.values():
			if not e.vivo or not e.alvejavel or e.invisivel or not game.jog.eh_inimigo_de(e): continue
			var n := _nota(e)
			if n < mn: mn = n; melhor = e.id
		return melhor

	func alvo() -> int: return _alvo
	func ponto_mira() -> Vector2: return _ponto

	func ataque_basico(segurando: bool) -> void:
		if _alvo == -1:
			if segurando: return
			if not _interagir_perto(2.6): game.hud.aviso("Nenhum alvo por perto.")
			return
		if game.jog.alvo != _alvo or not segurando: game.cmd("atacar", [_alvo, false])

	func usar_skill(slot: int) -> void:
		game._sob_mouse()   # o ponteiro já está no alvo: o hover do game.gd acompanha
		game.usar_skill(slot)

	func ciclar_alvo(_d: int) -> void:
		var lista := []
		for e: Ent in game.sim.ents.values():
			if e.vivo and e.alvejavel and not e.invisivel and game.jog.eh_inimigo_de(e) and e.pos.distance_to(game.jog.pos) < 9.0: lista.append(e)
		if lista.is_empty(): return
		lista.sort_custom(func(a, b): return a.pos.distance_to(game.jog.pos) < b.pos.distance_to(game.jog.pos))
		var i := -1
		for k in lista.size():
			if lista[k].id == _alvo: i = k
		_alvo = lista[(i + 1) % lista.size()].id
		_travado = true

	func travar_alvo() -> void:
		_travado = not _travado and _alvo != -1
		game.hud.aviso("Alvo travado." if _travado else "Alvo solto: a mira segue o stick.", Color("#e8d29a"))

	func interagir() -> void:
		if not _interagir_perto(3.5): game.hud.aviso("Nada para pegar ou falar por perto.")

	## O mais perto à frente: item no chão, NPC, baú, porta.
	func _interagir_perto(raio: float) -> bool:
		var jog: Ent = game.jog
		var melhor := -1; var md := raio; var tipo := ""
		for id in game.itens_chao.keys():
			var p: Vector2 = Iso.to_world(game.itens_chao[id].position)
			var d := p.distance_to(jog.pos)
			if d < md: md = d; melhor = id; tipo = "pegar"
		for e: Ent in game.sim.ents.values():
			if not e.vivo or not e.tipo in ["npc", "objeto"] or e.id == jog.id: continue
			if e.tipo == "objeto" and not e.alvejavel and not game.objs.has(e.id): continue
			var d2: float = e.pos.distance_to(jog.pos) - 0.3
			if d2 < md: md = d2; melhor = e.id; tipo = "interagir"
		if melhor == -1: return false
		game.cmd(tipo, [melhor])
		if tipo == "interagir": game.audio.tocar("ui/clique", null, -8.0)
		return true

class_name Ajustes
## Configurações do jogador (vídeo, áudio, jogo), salvas em user://ajustes.cfg e aplicadas na hora.
## O modo de tela (janela / tela cheia) continua com a classe Tela (user://video.cfg).
## Outras telas leem com Ajustes.v("chave") e escutam Ajustes.sinais.mudou(chave, valor).
## Abas extras (ex.: Controle) entram no menu com Ajustes.registrar_aba(id, titulo, construtor).

const CFG := "user://ajustes.cfg"
const BUSES := {"musica": "Musica", "ambiente": "Ambiente", "sfx": "Efeitos", "ui": "Interface"}

static var PADRAO := {
	# vídeo
	"vsync": true, "fps_max": 0, "janela": "1280x720", "brilho": 1.0, "luz": "alta", "clima": true, "vinheta": true,
	# áudio (0..1)
	"vol_geral": 1.0, "vol_musica": 0.8, "vol_ambiente": 0.85, "vol_efeitos": 1.0, "vol_interface": 0.9,
	"mudo": false, "som_fundo": true,
	# jogo
	"tremor": 1.0, "numeros": true, "barras_sempre": false, "nomes_sempre": false,
}
static var valores := {}
static var sinais := Sinais.new()
static var abas: Array = []          # [{id, titulo, construtor}] vindas de outras partes do jogo
static var _carregado := false
static var _sem_foco := false

class Sinais extends RefCounted:
	signal mudou(chave: String, valor)

static func carregar() -> void:
	if _carregado: return
	_carregado = true
	var cfg := ConfigFile.new()
	if cfg.load(CFG) != OK: return
	for k in cfg.get_section_keys("ajustes") if cfg.has_section("ajustes") else []:
		valores[k] = cfg.get_value("ajustes", k)

static func v(chave: String):
	if not _carregado: carregar()
	return valores.get(chave, PADRAO.get(chave))

## Padrão de um ajuste novo (outras abas chamam antes do primeiro uso).
static func padrao(chave: String, valor) -> void:
	if not PADRAO.has(chave): PADRAO[chave] = valor

static func definir(chave: String, valor) -> void:
	if not _carregado: carregar()
	if v(chave) == valor: return
	valores[chave] = valor
	var cfg := ConfigFile.new()
	for k in valores: cfg.set_value("ajustes", k, valores[k])
	cfg.save(CFG)
	_aplicar(chave)
	sinais.mudou.emit(chave, valor)

static func restaurar(chaves: Array) -> void:
	for k in chaves:
		if PADRAO.has(k): definir(k, PADRAO[k])

static func registrar_aba(id: String, titulo: String, construtor: Callable) -> void:
	for a in abas:
		if a["id"] == id: a["titulo"] = titulo; a["construtor"] = construtor; return
	abas.append({"id": id, "titulo": titulo, "construtor": construtor})

# =================================================================== aplicar
## Na abertura do jogo (cliente): vídeo e áudio.
static func aplicar_inicio() -> void:
	carregar()
	_criar_buses()
	for k in ["vsync", "fps_max", "vol_geral", "vol_musica", "vol_ambiente", "vol_efeitos", "vol_interface", "mudo"]: _aplicar(k)

static func web() -> bool:
	return OS.has_feature("web")

static func _aplicar(chave: String) -> void:
	match chave:
		"vsync":
			if not web() and DisplayServer.get_name() != "headless":
				DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if v("vsync") else DisplayServer.VSYNC_DISABLED)
		"fps_max": Engine.max_fps = int(v("fps_max"))
		"janela": aplicar_janela()
		"vol_geral", "mudo": _volume_mestre()
		"vol_musica": _volume("Musica", float(v("vol_musica")))
		"vol_ambiente": _volume("Ambiente", float(v("vol_ambiente")))
		"vol_efeitos": _volume("Efeitos", float(v("vol_efeitos")))
		"vol_interface": _volume("Interface", float(v("vol_interface")))

## Tamanho da janela (só no modo janela): centralizada na tela onde está.
static func aplicar_janela() -> void:
	if web() or DisplayServer.get_name() == "headless" or Tela.cheia(): return
	var p: PackedStringArray = String(v("janela")).split("x")
	var area := DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen())
	var tam := Vector2i(mini(int(p[0]), area.size.x - 40), mini(int(p[1]), area.size.y - 60))
	DisplayServer.window_set_size(tam)
	DisplayServer.window_set_position(area.position + (area.size - tam) / 2)

static func _criar_buses() -> void:
	for nome in BUSES.values():
		if AudioServer.get_bus_index(nome) != -1: continue
		AudioServer.add_bus()
		var i := AudioServer.bus_count - 1
		AudioServer.set_bus_name(i, nome)
		AudioServer.set_bus_send(i, "Master")

## Bus de áudio de cada categoria do audio.json (sfx, ui, musica, ambiente).
static func bus_de(cat: String) -> String:
	var n: String = BUSES.get(cat, "Efeitos")
	return n if AudioServer.get_bus_index(n) != -1 else "Master"

static func _volume(bus: String, lin: float) -> void:
	var i := AudioServer.get_bus_index(bus)
	if i == -1: return
	AudioServer.set_bus_volume_db(i, linear_to_db(maxf(lin, 0.0001)))
	AudioServer.set_bus_mute(i, lin <= 0.001)

static func _volume_mestre() -> void:
	var lin := float(v("vol_geral"))
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(lin, 0.0001)))
	AudioServer.set_bus_mute(0, bool(v("mudo")) or lin <= 0.001 or (_sem_foco and not bool(v("som_fundo"))))

# =================================================================== dentro do jogo
## Liga os ajustes ao jogo (game.gd chama uma vez, depois de criar hud e janelas).
static func ligar_jogo(game: Node) -> void:
	var cl := CanvasLayer.new(); cl.layer = 4; cl.name = "Brilho"   # acima do mundo, luz e clima; abaixo da HUD
	var r := ColorRect.new()
	r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = "shader_type canvas_item;\nuniform sampler2D tela : hint_screen_texture, filter_linear_mipmap;\nuniform float gama = 1.0;\nvoid fragment() { COLOR = vec4(pow(texture(tela, SCREEN_UV).rgb, vec3(1.0 / gama)), 1.0); }"
	var m := ShaderMaterial.new(); m.shader = sh
	r.material = m
	cl.add_child(r)
	game.add_child(cl)
	Configuracoes.audio = game.audio
	var aplicar := func(chave: String, _valor = null) -> void:
		if not is_instance_valid(game): return
		match chave:
			"brilho":
				m.set_shader_parameter("gama", float(v("brilho")))
				cl.visible = absf(float(v("brilho")) - 1.0) > 0.01
			"tremor": game.hud.mult_tremor = float(v("tremor"))
			"nomes_sempre": game.mostrar_nomes = bool(v("nomes_sempre"))
			"luz":
				game.luz.ESCALA = 0.5 if v("luz") == "alta" else 0.25
				game.luz._redimensionar()
			"clima", "vinheta": aplicar_clima(game)
	for k in ["brilho", "tremor", "nomes_sempre", "luz"]: aplicar.call(k)
	sinais.mudou.connect(aplicar)
	game.tree_exiting.connect(func(): if sinais.mudou.is_connected(aplicar): sinais.mudou.disconnect(aplicar))

## Poeira do Amargo e vinheta (game.gd chama no fim de _montar_clima, que roda a cada troca de mapa).
static func aplicar_clima(game: Node) -> void:
	for c in game.clima.get_children():
		if c is TextureRect: c.visible = bool(v("vinheta"))            # a vinheta é o único TextureRect do clima
		elif c.has_meta("f"): c.visible = bool(v("clima"))              # camadas ladrilhadas de pó

## Nó que fica vivo do começo ao fim: F10 abre as configurações em qualquer tela; som em segundo plano.
class Vigia extends Node:
	func _ready() -> void:
		process_mode = Node.PROCESS_MODE_ALWAYS
	func _notification(o: int) -> void:
		if o == NOTIFICATION_APPLICATION_FOCUS_OUT: Ajustes._sem_foco = true; Ajustes._volume_mestre()
		elif o == NOTIFICATION_APPLICATION_FOCUS_IN: Ajustes._sem_foco = false; Ajustes._volume_mestre()
	func _input(ev: InputEvent) -> void:
		if ev is InputEventKey and ev.pressed and not ev.echo and ev.keycode == KEY_F10:
			Configuracoes.alternar(self)
			get_viewport().set_input_as_handled()

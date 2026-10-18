class_name Tela
## Tela cheia: F11 ou Alt+Enter (em qualquer tela) e o item no menu Esc. A escolha fica em user://video.cfg.

const CFG := "user://video.cfg"

static func cheia() -> bool:
	var m := DisplayServer.window_get_mode()
	return m == DisplayServer.WINDOW_MODE_FULLSCREEN or m == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN

static func definir(ligada: bool) -> void:
	if OS.has_feature("web") or DisplayServer.get_name() == "headless": return
	if ligada:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		# volta na resolução escolhida em Vídeo > Tamanho da janela, centralizada na tela onde está
		Ajustes.aplicar_janela(true)
	var cfg := ConfigFile.new()
	cfg.load(CFG)
	cfg.set_value("video", "tela_cheia", ligada)
	cfg.save(CFG)

static func alternar() -> void:
	definir(not cheia())

## Na abertura do jogo: repete a última escolha (padrão: tela cheia).
static func aplicar_salvo() -> void:
	var cfg := ConfigFile.new()
	var ligada := true
	if cfg.load(CFG) == OK: ligada = bool(cfg.get_value("video", "tela_cheia", true))
	if ligada: definir(true)

static func atalho(ev: InputEvent) -> bool:
	if not (ev is InputEventKey) or not ev.pressed or ev.echo: return false
	var k: Key = ev.keycode
	return k == KEY_F11 or (ev.alt_pressed and (k == KEY_ENTER or k == KEY_KP_ENTER))

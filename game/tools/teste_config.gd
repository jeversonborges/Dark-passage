extends Node
## Prévia do menu de configurações: abre o Esc e cada aba, tira fotos e sai.
## xvfb-run godot --rendering-driver opengl3 -- classe=humano fotos_config=DIR
## (o main.gd chama este script quando recebe fotos_config=)

var jogo
var dir := ""

func _ready() -> void:
	await get_tree().create_timer(3.0).timeout
	jogo.janelas.abrir_menu()
	await get_tree().create_timer(0.5).timeout
	_foto("0_menu_esc")
	jogo.janelas.fechar("menu")
	Configuracoes.abrir(jogo)
	var i := 1
	for a in ["video", "audio", "jogo", "atalhos"]:
		await get_tree().create_timer(0.4).timeout
		Configuracoes.aberto.mostrar(a)
		await get_tree().create_timer(0.5).timeout
		_foto("%d_%s" % [i, a]); i += 1
	Ajustes.definir("brilho", 1.35)
	Configuracoes.aberto.mostrar("video")
	await get_tree().create_timer(0.5).timeout
	_foto("5_brilho_135")
	Configuracoes.aberto.fechar()
	await get_tree().create_timer(0.4).timeout
	_foto("6_mundo_brilho_135")
	Ajustes.restaurar(["brilho"])
	await get_tree().create_timer(0.3).timeout
	_foto("7_mundo_brilho_100")
	get_tree().quit()

func _foto(n: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	get_viewport().get_texture().get_image().save_png(dir.path_join(n + ".png"))

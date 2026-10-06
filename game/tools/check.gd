extends SceneTree
func _init() -> void:
	Defs.carregar()
	for f in ["tema", "chao", "luz", "unidade", "efeitos", "audio", "hud", "janelas", "char_select", "menu_rede", "game"]:
		var s = load("res://scripts/client/%s.gd" % f)
		print(f, " ", "ok" if s != null and s.can_instantiate() else "FALHOU")
	print("main ", load("res://scripts/main.gd") != null)
	print("teste ", load("res://tools/teste_visual.gd") != null)
	quit()

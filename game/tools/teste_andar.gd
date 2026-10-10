extends Node
## Teste da animação de andar: anda nas 8 direções e conta trocas walk/idle e quadros mostrados por direção.
## Uso: godot -- classe=anjo teste_andar=/pasta [fps=144]  (fps limita o desenho, a simulação segue em 30 Hz)

var jogo: Node2D
var args := {}
var t := 0.0
var d := -1
var trocas := 0
var quadros := {}
var ult_anim := ""
var parado_em_walk := 0
var amostras := 0
var dir_meio := -1
const DIRS := [Vector2(1, 0), Vector2(1, 1), Vector2(0, 1), Vector2(-1, 1), Vector2(-1, 0), Vector2(-1, -1), Vector2(0, -1), Vector2(1, -1)]

func _ready() -> void:
	Engine.max_fps = int(args.get("fps", 60))

func _process(dt: float) -> void:
	if jogo == null or jogo.jog == null: return
	t += dt
	if t < 2.0: return
	var v = jogo.views.get(jogo.jog.id)
	if v == null: return
	var fase := int((t - 2.0) / 1.6)
	if fase != d:
		if d >= 0: _relatorio(v)
		d = fase
		if d >= DIRS.size():
			print("[andar] fps medido ", Engine.get_frames_per_second())
			get_tree().quit(); return
		trocas = 0; quadros = {}; amostras = 0; ult_anim = v.anim
		jogo.cmd("mover", [jogo.jog.pos + DIRS[d].normalized() * 5.0])
		return
	var tf := t - 2.0 - d * 1.6
	if tf > 0.2 and tf < 1.2:   # meio do trajeto: tem que estar andando
		amostras += 1
		if v.anim != ult_anim: trocas += 1
		ult_anim = v.anim
		if v.anim == "walk": quadros[v.frame] = true
	if is_equal_approx(snappedf(tf, 0.05), 0.7) and args.has("teste_andar") and not quadros.has(-1):
		quadros[-1] = true
		dir_meio = v.dir
		var dir: String = args["teste_andar"]
		DirAccess.make_dir_recursive_absolute(dir)
		get_viewport().get_texture().get_image().save_png("%s/%s_d%d.png" % [dir, jogo.jog.classe, d])

func _relatorio(v) -> void:
	quadros.erase(-1)
	print("[andar] %s dir=%d amostras=%d trocas_walk_idle=%d quadros_walk_distintos=%d dir_sprite_no_meio=%d" % [jogo.jog.classe, d, amostras, trocas, quadros.size(), dir_meio])

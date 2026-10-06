extends Node
## Iluminação: um mapa de luz desenhado num SubViewport (meia resolução) e multiplicado sobre o mundo.
## O mapa guarda luz/2, então o composite dobra: dá para clarear acima do original perto de fogo e lâmpadas.

const COMPOSITE := """
shader_type canvas_item;
uniform sampler2D tela : hint_screen_texture, filter_linear_mipmap;
void fragment() {
	vec3 s = texture(tela, SCREEN_UV).rgb;
	vec3 l = texture(TEXTURE, UV).rgb * 2.0;
	vec3 c = s * l;
	// realce suave nas áreas muito iluminadas (fogo queimando o ar)
	c += max(l - 1.25, 0.0) * s * 0.35;
	COLOR = vec4(c, 1.0);
}
"""

var vp := SubViewport.new()
var cam := Camera2D.new()
var fontes := Node2D.new()
var camada := CanvasLayer.new()
var rect := TextureRect.new()
var ambiente := Color(0.4, 0.4, 0.4)
var tremulas: Array = []     # [sprite, energia_base, fase]
var _grad: Texture2D
var cam_principal: Camera2D
var t := 0.0
const ESCALA := 0.5

func _ready() -> void:
	vp.disable_3d = true
	vp.transparent_bg = false
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR
	add_child(vp)
	vp.add_child(cam)
	vp.add_child(fontes)
	cam.enabled = true
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1)); g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.35, Color(1, 1, 1, 0.62))
	g.add_point(0.7, Color(1, 1, 1, 0.18))
	var gt := GradientTexture2D.new()
	gt.gradient = g; gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5); gt.fill_to = Vector2(1.0, 0.5)
	gt.width = 128; gt.height = 128
	_grad = gt
	camada.layer = 1
	add_child(camada)
	rect.texture = vp.get_texture()
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new(); sh.code = COMPOSITE
	var m := ShaderMaterial.new(); m.shader = sh
	rect.material = m
	camada.add_child(rect)
	get_viewport().size_changed.connect(_redimensionar)
	_redimensionar()

func _redimensionar() -> void:
	var s := get_viewport().get_visible_rect().size
	vp.size = Vector2i(maxi(64, int(s.x * ESCALA)), maxi(64, int(s.y * ESCALA)))

func definir_ambiente(c: Color) -> void:
	ambiente = c
	_atualizar_clear()

func _atualizar_clear() -> void:
	# o SubViewport limpa com a cor padrão do projeto; desenhamos o ambiente como um retângulo gigante no fundo
	if not has_node("Fundo"):
		var f := ColorRect.new(); f.name = "Fundo"
		f.mouse_filter = Control.MOUSE_FILTER_IGNORE
		f.z_index = -100
		f.size = Vector2(200000, 200000); f.position = Vector2(-100000, -100000)
		fontes.add_child(f); fontes.move_child(f, 0)
		f.name = "Fundo"
	(fontes.get_node("Fundo") as ColorRect).color = Color(ambiente.r * 0.5, ambiente.g * 0.5, ambiente.b * 0.5)

func limpar() -> void:
	for c in fontes.get_children():
		if c.name != "Fundo": c.queue_free()
	tremulas.clear()

## Luz no chão: elipse isométrica de raio r tiles. energia 1 = dobra a cor da luz no centro.
func adicionar(pos_tela: Vector2, cor: Color, r: float, energia := 1.0, tremula := false) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = _grad
	s.position = pos_tela
	s.scale = Vector2(45.25 * r * 2.0 / 128.0, 22.63 * r * 2.0 / 128.0)
	s.modulate = Color(cor.r * energia * 0.5, cor.g * energia * 0.5, cor.b * energia * 0.5, 1.0)
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	s.material = mat
	fontes.add_child(s)
	if tremula: tremulas.append([s, s.modulate, randf() * 10.0])
	return s

func _process(dt: float) -> void:
	t += dt
	if cam_principal:
		cam.global_position = cam_principal.get_screen_center_position()
		cam.zoom = cam_principal.zoom * ESCALA
	for tr in tremulas:
		var s = tr[0]
		if not is_instance_valid(s): continue
		var f := 0.86 + 0.1 * sin(t * 9.0 + tr[2]) + 0.06 * sin(t * 23.0 + tr[2] * 3.0)
		var c: Color = tr[1]
		s.modulate = Color(c.r * f, c.g * f, c.b * f, 1.0)

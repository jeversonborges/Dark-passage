extends Node2D
## Chão do mapa num único quad com shader: cada pixel volta para coordenada de tile, lê o piso dos 4 tiles vizinhos
## e mistura com bordas orgânicas (ruído). Os pisos são as texturas do kit desentortadas (tools/pisos.py), em Texture2DArray.

const SHADER := """
shader_type canvas_item;
render_mode unshaded;
uniform sampler2D mapa : filter_nearest;
uniform sampler2DArray pisos : filter_nearest, repeat_enable;
uniform sampler2D ruido : filter_linear, repeat_enable;
uniform vec2 tam;
uniform vec4 cor_vazio : source_color = vec4(0.02, 0.018, 0.02, 1.0);
uniform float agua = -1.0;
uniform float lama = -1.0;
varying vec2 pm;

void vertex() { pm = VERTEX; }

vec2 cel(vec2 c) {
	if (c.x < 0.0 || c.y < 0.0 || c.x >= tam.x || c.y >= tam.y) return vec2(255.0, 0.0);
	vec2 v = texture(mapa, (c + 0.5) / tam).rg;
	return vec2(floor(v.r * 255.0 + 0.5), v.g);
}

vec3 amostra(float l, vec2 t) {
	if (l > 254.0) return cor_vazio.rgb;
	vec3 c = texture(pisos, vec3(t * 0.25, l)).rgb;
	if (abs(l - agua) < 0.5) {
		float o = texture(ruido, t * 0.35 + vec2(TIME * 0.03, TIME * 0.017)).r;
		float o2 = texture(ruido, t * 0.6 - vec2(TIME * 0.025, -TIME * 0.02)).r;
		c = mix(vec3(0.09, 0.13, 0.06), vec3(0.24, 0.42, 0.12), o * 0.6 + o2 * 0.4);
		c += vec3(0.25, 0.55, 0.12) * pow(max(o * o2 * 2.2 - 0.55, 0.0), 2.0);
	}
	return c;
}

void fragment() {
	vec2 t = vec2(pm.x / 64.0 + pm.y / 32.0, pm.x / 64.0 - pm.y / 32.0);
	vec2 n = texture(ruido, t * 0.07).rg - 0.5;
	vec2 n2 = texture(ruido, t * 0.29 + 0.37).gb - 0.5;
	vec2 b = t + n * 1.2 + n2 * 0.45 - 0.5;
	vec2 i = floor(b);
	vec2 f = fract(b);
	vec2 c00 = cel(i), c10 = cel(i + vec2(1.0, 0.0)), c01 = cel(i + vec2(0.0, 1.0)), c11 = cel(i + vec2(1.0, 1.0));
	vec4 w = vec4((1.0 - f.x) * (1.0 - f.y), f.x * (1.0 - f.y), (1.0 - f.x) * f.y, f.x * f.y);
	w = pow(w, vec4(2.6));
	w /= dot(w, vec4(1.0));
	vec3 c = amostra(c00.x, t) * w.x + amostra(c10.x, t) * w.y + amostra(c01.x, t) * w.z + amostra(c11.x, t) * w.w;
	float amargo = c00.y * w.x + c10.y * w.y + c01.y * w.z + c11.y * w.w;
	float macro = texture(ruido, t * 0.021 + 0.5).r;
	c *= mix(0.8, 1.12, macro);
	// Amargo: o chão perto da tempestade fica esverdeado e brilha um pouco
	float pulso = 0.85 + 0.15 * sin(TIME * 1.3 + t.x * 0.4);
	c = mix(c, c * vec3(0.78, 1.1, 0.7) + vec3(0.015, 0.05, 0.0) * pulso, clamp(amargo * 1.4, 0.0, 0.85));
	COLOR = vec4(c, 1.0);
}
"""

var mapa: Dictionary
var w := 0
var h := 0
var _mat: ShaderMaterial

func montar(m: Dictionary) -> void:
	mapa = m
	w = int(m["w"]); h = int(m["h"])
	var legenda: Dictionary = m.get("pisos", {})
	# camadas: só os pisos que este mapa usa
	var usados := {}
	for linha in m["terreno"]:
		for ch in linha: usados[ch] = true
	var nomes: Array = []
	var idx_char := {}
	var imgs: Array[Image] = []
	for ch in usados.keys():
		var nome: String = legenda.get(ch, "")
		if nome == "": continue
		var p := "res://assets/ext/ambiente/pisos_mundo/%s.png" % nome
		if not ResourceLoader.exists(p): continue
		if not nome in nomes:
			var img: Image = (load(p) as Texture2D).get_image()
			if img.is_compressed(): img.decompress()
			img.convert(Image.FORMAT_RGBA8)
			if img.get_width() != 256: img.resize(256, 256, Image.INTERPOLATE_NEAREST)
			imgs.append(img); nomes.append(nome)
		idx_char[ch] = nomes.find(nome)
	if imgs.is_empty():
		var vazio := Image.create(256, 256, false, Image.FORMAT_RGBA8); vazio.fill(Color(0.2, 0.18, 0.15)); imgs.append(vazio); nomes.append("x")
	var arr := Texture2DArray.new()
	arr.create_from_images(imgs)
	# mapa de pisos (R) e de Amargo (G)
	var mi := Image.create(w, h, false, Image.FORMAT_RG8)
	var am: Array = m.get("amargo", [])
	for y in h:
		var ln: String = m["terreno"][y]
		var al: String = am[y] if am.size() > y else ""
		for x in w:
			var ch := ln[x]
			var l := 255 if not idx_char.has(ch) else int(idx_char[ch])
			var a := 0.0
			if al != "":
				var v := int(al[x])
				a = clampf((v - 4) / 5.0, 0.0, 1.0)
			mi.set_pixel(x, y, Color(l / 255.0, a, 0))
	var mt := ImageTexture.create_from_image(mi)
	var ruido := FastNoiseLite.new()
	ruido.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	ruido.frequency = 0.02
	ruido.fractal_octaves = 3
	var ri := ruido.get_seamless_image(256, 256)
	ri.convert(Image.FORMAT_RGBA8)
	# canais G e B com ruídos deslocados (independentes) para a deformação das bordas
	var r2 := ruido.get_seamless_image(256, 256, false, false, 0.1)
	ruido.seed = 77
	var r3 := ruido.get_seamless_image(256, 256)
	for y in 256:
		for x in 256:
			var c := ri.get_pixel(x, y)
			c.g = r2.get_pixel((x + 97) % 256, (y + 41) % 256).r
			c.b = r3.get_pixel(x, y).r
			ri.set_pixel(x, y, c)
	var sh := Shader.new()
	sh.code = SHADER
	_mat = ShaderMaterial.new()
	_mat.shader = sh
	_mat.set_shader_parameter("mapa", mt)
	_mat.set_shader_parameter("pisos", arr)
	_mat.set_shader_parameter("ruido", ImageTexture.create_from_image(ri))
	_mat.set_shader_parameter("tam", Vector2(w, h))
	_mat.set_shader_parameter("agua", float(nomes.find("agua_toxica")))
	var ceu: Dictionary = m.get("ceu", {})
	_mat.set_shader_parameter("cor_vazio", Color(0.012, 0.01, 0.012) if not m.get("exterior", false) else Color(0.05, 0.045, 0.04))
	material = _mat
	queue_redraw()

func _draw() -> void:
	if w == 0: return
	# retângulo que cobre o losango inteiro do mapa na tela
	var x0 := 0.0
	var x1 := 32.0 * (w + h)
	var y0 := -16.0 * h
	var y1 := 16.0 * w
	draw_rect(Rect2(x0 - 64, y0 - 64, x1 - x0 + 128, y1 - y0 + 128), Color.WHITE)

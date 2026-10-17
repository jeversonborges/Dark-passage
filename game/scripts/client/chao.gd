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
uniform float abismo = 0.0;   // cume do Hermon: o vazio vira abismo com nevasca (0.9.x)
varying vec2 pm;

void vertex() { pm = VERTEX; }

// x = piso, y = Amargo, z = água (1 funda, 0,6 rasa), w = ângulo da correnteza (0..1 = 0..2pi)
vec4 cel(vec2 c) {
	if (c.x < 0.0 || c.y < 0.0 || c.x >= tam.x || c.y >= tam.y) return vec4(255.0, 0.0, 0.0, 0.0);
	vec4 v = texture(mapa, (c + 0.5) / tam);
	return vec4(floor(v.r * 255.0 + 0.5), v.g, v.b, v.a);
}

// Água do Rio Amargo: correnteza (flow map em duas fases), ondinhas, reflexo do céu, brilhos e espuma na margem.
vec3 agua_rio(vec3 leito, vec2 t, float prof, vec2 fl) {
	float ph = TIME * 0.09;
	float p0 = fract(ph), p1 = fract(ph + 0.5);
	float mx = abs(p0 - 0.5) * 2.0;
	vec2 u0 = t * 0.16 - fl * p0 * 0.5;
	vec2 u1 = t * 0.16 - fl * p1 * 0.5 + vec2(0.37, 0.61);
	// altura das ondas e a inclinação (diferenças finitas) para iluminar como superfície
	float e = 0.012;
	float h = mix(texture(ruido, u0).r, texture(ruido, u1).r, mx);
	float hx = mix(texture(ruido, u0 + vec2(e, 0.0)).r, texture(ruido, u1 + vec2(e, 0.0)).r, mx);
	float hy = mix(texture(ruido, u0 + vec2(0.0, e)).r, texture(ruido, u1 + vec2(0.0, e)).r, mx);
	float d1 = mix(texture(ruido, u0 * 2.7 + 0.21).g, texture(ruido, u1 * 2.7 + 0.53).g, mx);
	vec2 inc = vec2(hx - h, hy - h) / e * 0.11 + (d1 - 0.5) * 0.25;
	// cor: verde amargo escuro no fundo; no raso aparece um pouco do leito
	vec3 fundo = vec3(0.03, 0.085, 0.085);
	vec3 raso = vec3(0.11, 0.21, 0.19);
	vec3 c = mix(mix(leito * 0.5, raso, 0.6), fundo, smoothstep(0.3, 0.95, prof));
	// luz vinda de cima-esquerda: lado da onda virado para ela clareia, o outro escurece
	float lz = dot(inc, normalize(vec2(-0.6, -0.8)));
	c *= 1.0 + clamp(lz, -0.4, 0.7) * 0.8;
	// reflexo do céu nublado (mais forte onde a água está lisa)
	float liso = 1.0 - clamp(length(inc) * 1.6, 0.0, 1.0);
	c = mix(c, vec3(0.42, 0.52, 0.5), 0.26 + 0.32 * liso);
	// riscos compridos no sentido da corrente (filetes de luz)
	vec2 lado = vec2(-fl.y, fl.x);
	vec2 ur = vec2(dot(t, fl) * 0.05 - TIME * 0.06, dot(t, lado) * 0.34);
	float risco = texture(ruido, ur).b;
	c += vec3(0.4, 0.5, 0.42) * smoothstep(0.64, 0.78, risco) * 0.07;
	// cintilado discreto onde a crista pega luz
	float cint = smoothstep(0.32, 0.5, lz) * smoothstep(0.55, 0.75, d1);
	c += vec3(0.8, 0.92, 0.85) * cint * 0.5;
	// o Amargo luminesce de leve à noite
	c += vec3(0.008, 0.035, 0.016) * (0.6 + 0.4 * sin(TIME * 0.7 + t.x * 0.3 + t.y * 0.2));
	return c;
}

vec3 amostra(float l, vec2 t) {
	if (l > 254.0) {
		if (abismo < 0.5) return cor_vazio.rgb;
		// abismo: nevasca de cinza que corre lá embaixo, em duas camadas, sobre um fundo quase preto
		float n1 = texture(ruido, t * 0.045 + vec2(TIME * 0.012, TIME * 0.004)).r;
		float n2 = texture(ruido, t * 0.11 - vec2(TIME * 0.03, -TIME * 0.01)).g;
		return vec3(0.018, 0.02, 0.026) + vec3(0.07, 0.075, 0.085) * smoothstep(0.35, 0.9, n1) + vec3(0.035, 0.037, 0.042) * smoothstep(0.5, 0.95, n2);
	}
	return texture(pisos, vec3(t * 0.25, l)).rgb;
}

void fragment() {
	vec2 t = vec2(pm.x / 64.0 + pm.y / 32.0, pm.x / 64.0 - pm.y / 32.0);
	vec2 n = texture(ruido, t * 0.07).rg - 0.5;
	vec2 n2 = texture(ruido, t * 0.29 + 0.37).gb - 0.5;
	vec2 b = t + n * 1.2 + n2 * 0.45 - 0.5;
	vec2 i = floor(b);
	vec2 f = fract(b);
	vec4 c00 = cel(i), c10 = cel(i + vec2(1.0, 0.0)), c01 = cel(i + vec2(0.0, 1.0)), c11 = cel(i + vec2(1.0, 1.0));
	vec4 w = vec4((1.0 - f.x) * (1.0 - f.y), f.x * (1.0 - f.y), (1.0 - f.x) * f.y, f.x * f.y);
	w = pow(w, vec4(2.6));
	w /= dot(w, vec4(1.0));
	vec3 c = amostra(c00.x, t) * w.x + amostra(c10.x, t) * w.y + amostra(c01.x, t) * w.z + amostra(c11.x, t) * w.w;
	float amargo = c00.y * w.x + c10.y * w.y + c01.y * w.z + c11.y * w.w;
	// água: mistura com o mesmo contorno orgânico dos pisos, então a margem não fica quadriculada
	float prof = c00.z * w.x + c10.z * w.y + c01.z * w.z + c11.z * w.w;
	if (prof > 0.02) {
		vec2 d00 = vec2(cos(c00.w * 6.2832), sin(c00.w * 6.2832)), d10 = vec2(cos(c10.w * 6.2832), sin(c10.w * 6.2832));
		vec2 d01 = vec2(cos(c01.w * 6.2832), sin(c01.w * 6.2832)), d11 = vec2(cos(c11.w * 6.2832), sin(c11.w * 6.2832));
		vec2 fl = d00 * w.x * c00.z + d10 * w.y * c10.z + d01 * w.z * c01.z + d11 * w.w * c11.z;
		fl = length(fl) > 0.001 ? normalize(fl) : vec2(1.0, 0.0);
		vec3 ag = agua_rio(c, t, prof, fl);
		float borda = smoothstep(0.1, 0.42, prof);
		// espuma fina onde a água encosta na margem
		float esp = (1.0 - smoothstep(0.32, 0.55, prof)) * smoothstep(0.12, 0.3, prof);
		float ne = texture(ruido, t * 1.4 + fl * TIME * 0.12).r;
		ag = mix(ag, vec3(0.46, 0.54, 0.44), esp * smoothstep(0.4, 0.8, ne) * 0.35);
		// a terra molhada escurece logo antes da água
		c *= mix(1.0, 0.62, smoothstep(0.02, 0.15, prof));
		c = mix(c, ag, borda);
	}
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
var _mi: Image
var _mt: ImageTexture

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
	var mi := Image.create(w, h, false, Image.FORMAT_RGBA8)
	var am: Array = m.get("amargo", [])
	var rio: Array = m.get("rio", {}).get("centro", [])
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
			var prof := 1.0 if ch == "w" else (0.6 if ch == "r" else 0.0)
			var ang := 0.0
			if prof > 0.0 and rio.size() > 1: ang = _correnteza(rio, Vector2(x + 0.5, y + 0.5))
			mi.set_pixel(x, y, Color(l / 255.0, a, prof, ang))
	var mt := ImageTexture.create_from_image(mi)
	_mi = mi; _mt = mt
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
	_mat.set_shader_parameter("abismo", 1.0 if m.has("hermon") else 0.0)
	var ceu: Dictionary = m.get("ceu", {})
	_mat.set_shader_parameter("cor_vazio", Color(0.012, 0.01, 0.012) if not m.get("exterior", false) else Color(0.05, 0.045, 0.04))
	material = _mat
	queue_redraw()

## Ângulo (0..1) da correnteza no tile: direção do trecho da linha central do rio mais perto.
func _correnteza(rio: Array, p: Vector2) -> float:
	var melhor := INF
	var dir := Vector2.RIGHT
	for i in rio.size() - 1:
		var a := Vector2(rio[i][0], rio[i][1])
		var b := Vector2(rio[i + 1][0], rio[i + 1][1])
		var ab := b - a
		var k := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 1e-6), 0.0, 1.0)
		var dd := p.distance_squared_to(a + ab * k)
		if dd < melhor: melhor = dd; dir = ab
	return fposmod(dir.angle() / TAU, 1.0)

func _draw() -> void:
	if w == 0: return
	# retângulo que cobre o losango inteiro do mapa na tela
	var x0 := 0.0
	var x1 := 32.0 * (w + h)
	var y0 := -16.0 * h
	var y1 := 16.0 * w
	draw_rect(Rect2(x0 - 64, y0 - 64, x1 - x0 + 128, y1 - y0 + 128), Color.WHITE)

## Cume do Hermon: as células de um anel que caiu viram abismo (piso 255).
func derrubar(celulas: Array) -> void:
	if _mi == null: return
	for c in celulas:
		var px := _mi.get_pixel(int(c[0]), int(c[1]))
		px.r = 1.0
		_mi.set_pixel(int(c[0]), int(c[1]), px)
	_mt.update(_mi)

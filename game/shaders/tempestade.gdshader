shader_type canvas_item;
// Tempestade de Amargo: pó verde-cinza correndo na diagonal, ruído suave em camadas.
uniform vec2 cam = vec2(0.0);
uniform float forca = 0.0;

float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), u.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) {
	float s = 0.0, a = 0.5;
	for (int k = 0; k < 5; k++) { s += a * n(p); p = p * 2.03 + vec2(1.7, 9.2); a *= 0.5; }
	return s;
}
void fragment() {
	vec2 px = FRAGCOORD.xy;
	float t = TIME;
	vec2 v = vec2(1.0, 0.38);
	vec2 p1 = (px + cam * 0.15) / vec2(520.0, 260.0) - v * t * 0.22;
	vec2 p2 = (px + cam * 0.35) / vec2(260.0, 120.0) - v * t * 0.55;
	float nuvem = fbm(p1 + fbm(p1 * 0.7 + t * 0.03));
	float rajada = fbm(p2);
	float d = smoothstep(0.35, 0.85, nuvem) * 0.75 + smoothstep(0.5, 0.95, rajada) * 0.45;
	// riscos de grão finos na diagonal
	vec2 p3 = (px + cam * 0.6) * vec2(0.02, 0.09) - vec2(t * 3.5, t * 1.2);
	float risco = smoothstep(0.82, 0.98, n(vec2(p3.x * 0.6 - p3.y * 1.6, p3.y * 5.0)));
	vec3 cor = mix(vec3(0.17, 0.19, 0.13), vec3(0.42, 0.45, 0.30), nuvem);
	cor = mix(cor, vec3(0.62, 0.72, 0.38), risco * 0.6);
	// bordas da tela mais fechadas
	vec2 uv = SCREEN_UV - 0.5;
	float borda = smoothstep(0.25, 0.75, length(uv * vec2(1.0, 1.4)));
	float a = clamp((0.25 + d * 0.75 + borda * 0.5) * forca + risco * forca * 0.35, 0.0, 0.92);
	COLOR = vec4(cor, a);
}

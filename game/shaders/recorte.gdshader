shader_type canvas_item;
// Recorte em volta do personagem (estilo Diablo 3 / Path of Exile): só a parte do prop que cobre o jogador
// fica translúcida, num óvalo de borda suave e roída, com uma orla queimada para não parecer um furo de recorte.
// O resto do prédio continua sólido. game.gd liga isto só nos props que cobrem o corpo (_atualizar_recortes).

uniform vec2 centro = vec2(0.0);          // tronco do jogador, em coordenadas do mundo (canvas)
uniform vec2 raio = vec2(80.0, 105.0);    // semi-eixos do óvalo (px de mundo)
uniform float forca : hint_range(0.0, 1.0) = 0.0;
uniform float alfa_min = 0.12;            // quanto do prop ainda aparece no miolo do recorte

varying vec2 mundo;

void vertex() {
	mundo = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float ruido(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	float a = fract(sin(dot(i, vec2(127.1, 311.7))) * 43758.5);
	float b = fract(sin(dot(i + vec2(1.0, 0.0), vec2(127.1, 311.7))) * 43758.5);
	float c = fract(sin(dot(i + vec2(0.0, 1.0), vec2(127.1, 311.7))) * 43758.5);
	float d = fract(sin(dot(i + vec2(1.0, 1.0), vec2(127.1, 311.7))) * 43758.5);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

void fragment() {
	vec4 t = texture(TEXTURE, UV) * COLOR;
	if (forca > 0.001) {
		vec2 q = (mundo - centro) / raio;
		// borda roída: o contorno do óvalo treme com ruído fixo no mundo (não "nada" quando o jogador anda)
		float d = length(q) + (ruido(mundo / 9.0) - 0.5) * 0.22;
		float dentro = 1.0 - smoothstep(0.62, 1.0, d);
		float orla = smoothstep(0.55, 0.85, d) * (1.0 - smoothstep(0.85, 1.08, d));
		t.rgb *= 1.0 - orla * 0.45 * forca;   // orla escura, como pedra queimada em volta do buraco
		t.a *= mix(1.0, alfa_min, dentro * forca);
	}
	COLOR = t;
}

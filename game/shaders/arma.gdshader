shader_type canvas_item;
// Camada de arma (assets/armas): R da máscara = metal recebe a cor do item; G = emissivo; B = halo do brilho.
uniform sampler2D mascara : filter_nearest;
uniform vec4 tinta : source_color = vec4(0.6, 0.62, 0.66, 1.0);
uniform vec4 brilho : source_color = vec4(1.0, 0.78, 0.56, 1.0);
uniform float forca_brilho = 0.0;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	vec3 m = texture(mascara, UV).rgb;
	float l = dot(c.rgb, vec3(0.3, 0.59, 0.11));
	c.rgb = mix(c.rgb, clamp(l * tinta.rgb * 2.1, 0.0, 1.0), m.r);
	c.rgb = mix(c.rgb, mix(brilho.rgb, vec3(1.0), 0.35), m.g * max(forca_brilho, 0.6));
	float h = m.b * forca_brilho;
	COLOR = vec4(mix(brilho.rgb, c.rgb, c.a), max(c.a, h * 0.6));
}

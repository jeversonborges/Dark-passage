extends Node2D
## Visual de uma entidade do servidor (jogador, monstro, chefe, NPC, invocação, objeto de arena).
## Lê o Ent direto (o servidor roda no mesmo processo) e suaviza posição; animações das folhas 8 direções.

const SHADER := """
shader_type canvas_item;
uniform vec4 flash_cor : source_color = vec4(0.95, 0.92, 0.85, 1.0);
uniform float flash = 0.0;
uniform vec4 tinta : source_color = vec4(1.0);
uniform float dissolve = 0.0;
uniform float fantasma = 0.0;
uniform vec4 contorno : source_color = vec4(0.0);   // a = força do contorno (hover, jogador)
uniform float realce = 0.0;                          // clareia a figura (hover / legibilidade no escuro)
uniform sampler2D ruido : repeat_enable;
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	c.rgb *= tinta.rgb;
	c.rgb = mix(c.rgb, c.rgb * 1.55 + vec3(0.05), realce);
	c.rgb = mix(c.rgb, flash_cor.rgb, flash);
	if (contorno.a > 0.0 && c.a < 0.5) {
		vec2 px = TEXTURE_PIXEL_SIZE * 2.0;
		float v = max(max(texture(TEXTURE, UV + vec2(px.x, 0.0)).a, texture(TEXTURE, UV - vec2(px.x, 0.0)).a),
			max(texture(TEXTURE, UV + vec2(0.0, px.y)).a, texture(TEXTURE, UV - vec2(0.0, px.y)).a));
		if (v > 0.5) c = vec4(contorno.rgb, contorno.a);
	}
	if (dissolve > 0.0) {
		float n = texture(ruido, UV * 3.0).r;
		if (n < dissolve) c.a = 0.0;
		else if (n < dissolve + 0.06) c.rgb = mix(c.rgb, vec3(0.9, 0.35, 0.1), 0.8);
	}
	if (fantasma > 0.0) { c.a *= 0.55 + 0.15 * sin(TIME * 3.0); c.rgb += vec3(0.05, 0.2, 0.08); }
	COLOR = c * COLOR;
}
"""
static var _shader: Shader
static var _ruido: Texture2D

var game
var ent: Ent
var id := -1
var info: Dictionary          # Defs.sprite(): meta, escala, tint
var meta: Dictionary
var corpo := Sprite2D.new()
var sombra := Node2D.new()
var mat: ShaderMaterial
var anim := "idle"
var anim_unica := ""          # animação de ação tocando (attack, shoot...)
var frame_t := 0.0
var frame := 0
var dir := 0
var pos_vis := Vector2.ZERO   # posição suavizada na tela
var flash_t := 0.0
var flash_dur := 0.08
var congelado_t := 0.0
var morto := false
var morte_t := 0.0
var levita := false
var hover := false
var cor_anel := Color(0, 0, 0, 0)
var escala_base := 1.0
var altura_px := 110.0
var andando := false
var ult_pos := Vector2.ZERO
var tempo := 0.0
var avanco := Vector2.ZERO    # avanço do golpe (px)
var dur_unica := 0.0
var anim_base := ""           # animação em loop no lugar de idle (eat do Andras devorando)

func iniciar(g, e: Ent) -> void:
	game = g; ent = e; id = e.id
	var kind := e.kind
	if e.tipo == "jogador": kind = e.classe
	elif e.tipo == "npc": kind = "npc:" + e.kind
	elif e.tipo == "invocacao": kind = e.kind
	info = Defs.sprite(kind)
	if e.tipo == "npc" and not Defs.SPR.has(kind):
		var s: Dictionary = Defs.SPR_SUBST.get(kind, {})
		var base: String = s.get("usa", e.aux.get("visual", "humano"))
		if Defs.SPR.has(base): info = {"meta": Defs.SPR[base], "escala": float(s.get("escala", 1.0)), "tint": Defs.cor(s.get("tint", "#ffffff")), "fantasma": s.get("fantasma", false)}
	meta = info["meta"]
	escala_base = float(info.get("escala", 1.0)) * float(meta.get("escala", 1.0))
	if e.tipo == "chefe": escala_base *= 1.5   # chefe tem que impor presença
	corpo.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	if _shader == null:
		_shader = Shader.new(); _shader.code = SHADER
		var n := FastNoiseLite.new(); n.frequency = 0.06
		_ruido = ImageTexture.create_from_image(n.get_seamless_image(128, 128))
	mat = ShaderMaterial.new(); mat.shader = _shader
	mat.set_shader_parameter("tinta", info.get("tint", Color.WHITE))
	mat.set_shader_parameter("ruido", _ruido)
	mat.set_shader_parameter("fantasma", 1.0 if info.get("fantasma", false) else 0.0)
	if e.tipo == "jogador": mat.set_shader_parameter("flash_cor", Color("#7a1612"))
	corpo.material = mat
	corpo.region_enabled = true
	corpo.centered = false
	add_child(sombra)
	sombra.draw.connect(_desenhar_sombra)
	add_child(corpo)
	var fr: Array = meta["frame"]
	altura_px = float(fr[1]) * 0.55 * escala_base
	pos_vis = Iso.to_screen(e.pos)
	position = pos_vis
	ult_pos = e.pos
	dir = maxi(0, Iso.dir8(e.facing))
	_definir_anim("idle")
	_aplicar_frame()

## Troca a arte da unidade em jogo (o alfa da matilha nasce como cão comum no sim).
func trocar_visual(kind: String) -> void:
	if not Defs.SPR.has(kind): return
	info = Defs.sprite(kind)
	meta = info["meta"]
	escala_base = float(info.get("escala", 1.0)) * float(meta.get("escala", 1.0))
	altura_px = float(meta["frame"][1]) * 0.55 * escala_base
	anim = ""
	_definir_anim("idle")
	_aplicar_frame()

func _sheet(nome: String) -> Dictionary:
	var anims: Dictionary = meta["anims"]
	if anims.has(nome): return anims[nome]
	return {}

func _definir_anim(nome: String) -> void:
	if anim == nome and corpo.texture != null: return
	var a := _sheet(nome)
	if a.is_empty(): a = _sheet("idle"); nome = "idle"
	anim = nome
	frame = 0; frame_t = 0.0
	corpo.texture = Tema.tex(a["file"])

## Toca uma animação de ação uma vez (attack, shoot, spin, dash, hit, death, eat...). dur: segundos (ajusta o fps).
func tocar(nome: String, dur := 0.0) -> void:
	if morto and nome != "death": return
	var a := _sheet(nome)
	if a.is_empty():
		if nome in ["shoot", "spin", "heavy", "sweep", "lunge", "hook", "leap", "vomit", "feast", "roar", "howl", "shout"]: a = _sheet("attack"); nome = "attack"
		if a.is_empty(): return
	anim_unica = nome
	dur_unica = dur if dur > 0.0 else float(a["frames"]) / float(a["fps"])
	anim = ""
	_definir_anim(nome)

func _aplicar_frame() -> void:
	var a := _sheet(anim)
	if a.is_empty() or corpo.texture == null: return
	var fr: Array = meta["frame"]
	var n := int(a["frames"])
	frame = clampi(frame, 0, n - 1)
	corpo.region_rect = Rect2(frame * fr[0], dir * fr[1], fr[0], fr[1])
	var anc: Array = meta["anchor"]
	var esc := escala_base * float(ent.escala if ent else 1.0)
	corpo.scale = Vector2(esc, esc)
	corpo.position = Vector2(-anc[0], -anc[1]) * esc + avanco + (Vector2(0, -26 + sin(tempo * 2.2) * 5.0) if levita else Vector2.ZERO)

func piscar(ms: float) -> void:
	flash_t = ms / 1000.0; flash_dur = maxf(0.03, flash_t)

func congelar(ms: float) -> void:
	congelado_t = maxf(congelado_t, ms / 1000.0)

func morrer() -> void:
	if morto: return
	morto = true; morte_t = 0.0
	anim_unica = ""
	if not _sheet("death").is_empty(): tocar("death")
	else: anim_unica = "_sem_morte"

func _process(dt: float) -> void:
	tempo += dt
	if congelado_t > 0.0:
		congelado_t -= dt
		_atualizar_flash(dt)
		return
	if not morto and ent != null:
		var alvo := Iso.to_screen(ent.pos)
		var dpos := alvo - pos_vis
		if dpos.length() > 260.0: pos_vis = alvo
		else: pos_vis = pos_vis.lerp(alvo, 1.0 - exp(-dt * 18.0))
		andando = ent.pos.distance_squared_to(ult_pos) > 0.0004 or not ent.caminho.is_empty() and ent.pos.distance_squared_to(ult_pos) > 0.00001
		var mov := ent.pos - ult_pos
		ult_pos = ent.pos
		var fac := ent.facing
		if andando and mov.length_squared() > 1e-5 and anim_unica == "": fac = mov
		var d := Iso.dir8(fac)
		if d >= 0 and (anim_unica == "" or anim_unica == "dash"): dir = d
		elif d >= 0 and anim_unica != "": dir = d
	position = pos_vis
	avanco = avanco.lerp(Vector2.ZERO, 1.0 - exp(-dt * 14.0))
	# animação
	if anim_unica != "":
		if anim_unica == "_sem_morte":
			morte_t += dt
			modulate.a = maxf(0.0, 1.0 - morte_t / 1.2)
			mat.set_shader_parameter("dissolve", clampf(morte_t / 1.2, 0.0, 1.0))
		else:
			var a := _sheet(anim)
			var n := int(a["frames"])
			frame_t += dt
			var f := int(frame_t / maxf(0.01, dur_unica) * n)
			if f >= n:
				if morto:
					frame = n - 1; morte_t += dt
				else:
					anim_unica = ""
					_definir_anim("walk" if andando else "idle")
			else: frame = f
	else:
		var desejada := "walk" if andando else "idle"
		if ent != null and ent.tipo == "objeto": desejada = "idle"
		if anim_base != "" and not _sheet(anim_base).is_empty(): desejada = anim_base
		elif ent != null and ent.quebrado_t > 0.0 and not _sheet("tired").is_empty(): desejada = "tired"
		elif ent != null and ent.quebrado_t > 0.0 and not _sheet("stun").is_empty(): desejada = "stun"
		_definir_anim(desejada)
		var a2 := _sheet(anim)
		if not a2.is_empty():
			var fps := float(a2["fps"])
			if anim == "walk" and ent != null: fps *= clampf(ent.vel / 3.2, 0.6, 1.6)
			frame_t += dt
			frame = int(frame_t * fps) % int(a2["frames"])
	if morto and anim_unica != "_sem_morte":
		morte_t += dt
		if morte_t > 5.0: modulate.a = maxf(0.0, 1.0 - (morte_t - 5.0) / 1.0)
	_aplicar_frame()
	_atualizar_flash(dt)
	_atualizar_realce(dt)
	sombra.queue_redraw()

var realce_t := 0.0
## Hover: contorno colorido + clarear. Jogador: realce leve sempre (não some no escuro).
func _atualizar_realce(dt: float) -> void:
	var alvo := 0.0
	if hover and not morto: alvo = 1.0
	realce_t = lerpf(realce_t, alvo, 1.0 - exp(-dt * 14.0))
	var chefe: bool = ent != null and ent.tipo == "chefe" and not morto
	var base := 0.12 if ent != null and ent.tipo == "jogador" else (0.18 if chefe else 0.0)
	mat.set_shader_parameter("realce", base + realce_t * 0.35)
	var c := cor_anel
	c.a = cor_anel.a * realce_t
	if chefe and c.a < 0.5: c = Color(0.95, 0.3, 0.12, 0.5 + 0.15 * sin(tempo * 3.0))
	mat.set_shader_parameter("contorno", c)

func _atualizar_flash(dt: float) -> void:
	if flash_t > 0.0:
		flash_t -= dt
		mat.set_shader_parameter("flash", clampf(flash_t / flash_dur, 0.0, 1.0))
	else: mat.set_shader_parameter("flash", 0.0)

func _desenhar_sombra() -> void:
	var r := 0.42 * escala_base * float(ent.escala if ent else 1.0)
	if meta["frame"][0] >= 400: r *= 2.2
	elif meta["frame"][0] >= 224: r *= 1.25
	var e := Iso.elipse(r)
	var a := 0.38 * modulate.a
	if levita: a *= 0.6
	_elipse(sombra, Vector2.ZERO, e, Color(0, 0, 0, a), true)
	_elipse(sombra, Vector2.ZERO, e * 0.6, Color(0, 0, 0, a * 0.6), true)
	if ent != null and ent.tipo == "jogador" and not morto and game.jog != null and ent.id == game.jog.id:
		var pul := 0.75 + 0.25 * sin(tempo * 2.6)
		_elipse(sombra, Vector2.ZERO, e * 1.25, Color(0.98, 0.78, 0.35, 0.55 * pul), false, 2.0)
		_elipse(sombra, Vector2.ZERO, e * 1.38, Color(0.98, 0.6, 0.2, 0.18 * pul), false, 3.0)

static func _elipse(c: CanvasItem, centro: Vector2, raio: Vector2, cor: Color, cheio: bool, larg := 1.5) -> void:
	var pts := PackedVector2Array()
	for i in 33:
		var t := TAU * i / 32.0
		pts.append(centro + Vector2(cos(t) * raio.x, sin(t) * raio.y))
	if cheio: c.draw_colored_polygon(pts, cor)
	else: c.draw_polyline(pts, cor, larg, true)

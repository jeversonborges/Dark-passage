extends Node2D
## Visual de uma entidade do servidor (jogador, monstro, chefe, NPC, invocação, objeto de arena).
## Lê o Ent direto (o servidor roda no mesmo processo) e suaviza posição; animações das folhas 8 direções.

const SHADER := """
shader_type canvas_item;
// o COLOR do fragment já vem multiplicado pela textura (alfa 0 fora da figura); o contorno usa a cor do vértice
varying vec4 cor_vertice;
void vertex() { cor_vertice = COLOR; }
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
	vec4 t0 = c;
	c.rgb *= tinta.rgb;
	c.rgb = mix(c.rgb, c.rgb * 1.55 + vec3(0.05), realce);
	c.rgb = mix(c.rgb, flash_cor.rgb, flash);
	if (contorno.a > 0.0 && c.a < 0.5) {
		// contorno suave: anel firme a 2 px e um halo fraco a 4 px, em 8 direções
		vec2 px = TEXTURE_PIXEL_SIZE;
		float v = 0.0;
		for (int i = 0; i < 8; i++) {
			float a = float(i) * 0.785398;
			vec2 d = vec2(cos(a), sin(a));
			v = max(v, texture(TEXTURE, UV + d * px * 2.0).a);
			v = max(v, texture(TEXTURE, UV + d * px * 4.0).a * 0.4);
		}
		c = vec4(mix(contorno.rgb, c.rgb, c.a), max(c.a, v * contorno.a));
	}
	if (dissolve > 0.0) {
		float n = texture(ruido, UV * 3.0).r;
		if (n < dissolve) c.a = 0.0;
		else if (n < dissolve + 0.06) c.rgb = mix(c.rgb, vec3(0.9, 0.35, 0.1), 0.8);
	}
	if (fantasma > 0.0) { c.a *= 0.55 + 0.15 * sin(TIME * 3.0); c.rgb += vec3(0.05, 0.2, 0.08); }
	// a figura mantém o tom de sempre (textura x textura); o contorno, fora dela, sai com a cor pura
	COLOR = c * cor_vertice * (t0.a > 0.0 ? t0 : vec4(1.0));
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
var selecionado := false   # aliado escolhido para cura (verde) ou jogador na mira do PvP (vermelho): contorno fixo
var cor_sel := Color(0.45, 1.0, 0.55, 0.95)
var cor_anel := Color(0, 0, 0, 0)
var escala_base := 1.0
var altura_px := 110.0
var andando := false
var ult_pos := Vector2.ZERO
var ult_mov := Vector2.ZERO   # último deslocamento (vira o boneco para onde anda, mesmo nos quadros sem passo)
var parado_t := 1.0           # segundos desde que a posição mudou pela última vez
const FOLGA_ANDAR := 0.15     # a posição só muda a cada passo da simulação (30 Hz) ou pacote da rede: entre um e
                              # outro o boneco continua "andando", senão a tela a 60+ fps alterna andar/parado e trava no quadro 0
var tempo := 0.0
var avanco := Vector2.ZERO    # avanço do golpe (px)
var dur_unica := 0.0
var ajoelhado := false        # /ajoelhar: fica abaixado até andar ou agir
# Armas visíveis (assets/armas): corpo sem arma + uma camada por silhueta, desenhada por cima do corpo.
const DIRS_ARMA := ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
var _armas := {}       # slot -> Sprite2D (arma, segunda_mao)
var _camadas := {}     # silhueta -> {json, tex, mask}
var _kind_armas := ""  # classe com pasta em assets/armas (vazio: sem camadas)
var anim_base := ""           # animação em loop no lugar de idle (eat do Andras devorando)

func iniciar(g, e: Ent) -> void:
	game = g; ent = e; id = e.id
	var kind := e.kind
	if e.tipo == "jogador":
		kind = e.classe
		var spr_evo: String = Evolucao.defn(e.evolucao).get("sprite", e.evolucao) if e.evolucao != "" else ""
		if e.aux.get("forma", "") == "forma_colossal" and Defs.SPR.has("abominacao_colossal"): kind = "abominacao_colossal"
		elif spr_evo != "" and Defs.SPR.has(spr_evo): kind = spr_evo
	elif e.tipo == "npc": kind = "npc:" + e.kind
	elif e.tipo == "invocacao": kind = e.kind
	elif e.tipo == "objeto" and Defs.SPR.has(str(e.aux.get("visual", ""))): kind = e.aux["visual"]   # estátua viva (Vigilante ajoelhado)
	info = Defs.sprite(kind)
	if e.tipo == "npc" and not Defs.SPR.has(kind):
		var s: Dictionary = Defs.SPR_SUBST.get(kind, {})
		var base: String = s.get("usa", e.aux.get("visual", "humano"))
		if Defs.SPR.has(base): info = {"meta": Defs.SPR[base], "escala": float(s.get("escala", 1.0)), "tint": Defs.cor(s.get("tint", "#ffffff")), "fantasma": s.get("fantasma", false)}
	meta = info["meta"]
	escala_base = float(info.get("escala", 1.0)) * float(meta.get("escala", 1.0))
	if e.tipo == "chefe": escala_base *= 1.5   # chefe tem que impor presença
	_carregar_corpo_armado(kind)
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
	_montar_armas()
	var fr: Array = meta["frame"]
	altura_px = float(fr[1]) * 0.55 * escala_base
	pos_vis = Iso.to_screen(e.pos)
	position = pos_vis
	ult_pos = e.pos
	dir = maxi(0, Iso.dir8(e.facing))
	if e.tipo == "objeto":
		anim_base = str(e.aux.get("anim", ""))
		if e.kind == "estatua_vigilante": mat.set_shader_parameter("tinta", Color(1.5, 1.48, 1.5))   # coberto de cinza até o juramento
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
		if nome in ["shoot", "spin", "heavy", "sweep", "lunge", "hook", "leap", "vomit", "feast", "roar", "howl", "shout", "cast", "summon"]: a = _sheet("attack"); nome = "attack"
		if a.is_empty(): return
	anim_unica = nome; ajoelhado = false
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
	if ajoelhado:   # quadro de idle parado, mais baixo e um pouco mais largo: os pés ficam no chão
		corpo.scale = Vector2(esc * 1.05, esc * 0.78)
		corpo.position = Vector2(-anc[0] * 1.05, -anc[1] * 0.78) * esc + (Vector2(0, -26) if levita else Vector2.ZERO)
	if not _armas.is_empty(): _aplicar_armas()

## /ajoelhar
func ajoelhar() -> void:
	if morto: return
	ajoelhado = true; anim_unica = ""; _definir_anim("idle"); frame = 0

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
		var mexeu := ent.pos.distance_squared_to(ult_pos) > 0.0004 or not ent.caminho.is_empty() and ent.pos.distance_squared_to(ult_pos) > 0.00001
		parado_t = 0.0 if mexeu else parado_t + dt
		andando = parado_t < FOLGA_ANDAR
		var mov := ent.pos - ult_pos
		ult_pos = ent.pos
		if mov.length_squared() > 1e-5: ult_mov = mov
		var fac := ent.facing
		if andando and anim_unica == "" and ult_mov != Vector2.ZERO: fac = ult_mov
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
	elif ajoelhado:
		if andando: ajoelhado = false
		frame = 0
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
	if (hover or selecionado) and not morto: alvo = 1.0
	realce_t = lerpf(realce_t, alvo, 1.0 - exp(-dt * 14.0))
	var chefe: bool = ent != null and ent.tipo == "chefe" and not morto
	var base := 0.12 if ent != null and ent.tipo == "jogador" else (0.18 if chefe else 0.0)
	if ent != null and "vigilante" in ent.kind: base = 0.45 if ent.tipo == "objeto" else 0.22   # Hermon: estátua de cinza / anjo caído legível na nevasca
	mat.set_shader_parameter("realce", base + realce_t * 0.35)
	var c := cor_anel if hover or not selecionado else cor_sel
	c.a = c.a * realce_t
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

## Classe com pasta em assets/armas: o corpo passa a ser a folha sem arma (a arma vem por camada).
func _carregar_corpo_armado(kind: String) -> void:
	var caminho := "res://assets/ext/armas/%s/corpo/sprites.json" % kind
	if not FileAccess.file_exists(caminho): return
	var c: Dictionary = Defs.ler(caminho)
	var m: Dictionary = meta.duplicate(true)
	m["frame"] = c["frame_size"]; m["anchor"] = c["anchor_feet"]; m["dirs"] = c["rows_dirs"]
	m["anims"] = {}
	for n in c["anims"]:
		var a: Dictionary = c["anims"][n].duplicate()
		a["file"] = "res://assets/ext/armas/%s/corpo/%s" % [kind, a["file"]]
		m["anims"][n] = a
	meta = m
	_kind_armas = kind

func _montar_armas() -> void:
	if _kind_armas == "": return
	for slot in ["arma", "segunda_mao"]:
		var sp := Sprite2D.new()
		sp.centered = false
		sp.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		sp.region_enabled = true
		sp.visible = false
		var mat_arma := ShaderMaterial.new()
		mat_arma.shader = load("res://shaders/arma.gdshader")
		sp.material = mat_arma
		add_child(sp)
		_armas[slot] = sp

func _aplicar_armas() -> void:
	var esc := escala_base * float(ent.escala if ent else 1.0)
	var vis: Dictionary = ent.vis if ent else {}
	for slot in _armas:
		var sp: Sprite2D = _armas[slot]
		var q = _quadro_arma(vis.get(slot, {}), anim, dir, frame)
		if q == null:
			sp.visible = false; continue
		sp.visible = true
		sp.texture = q["tex"]
		sp.region_rect = q["rect"]
		sp.position = corpo.position + q["offset"] * esc
		sp.scale = Vector2(esc, esc)
		var mat_arma: ShaderMaterial = sp.material
		mat_arma.set_shader_parameter("mascara", q["mask"])
		mat_arma.set_shader_parameter("tinta", q["tinta"])
		mat_arma.set_shader_parameter("brilho", q["brilho"])
		mat_arma.set_shader_parameter("forca_brilho", q["forca"])

## Quadro da camada da arma para a animação, direção e quadro atuais; null quando a arma está escondida.
func _quadro_arma(v: Dictionary, nome: String, d: int, f: int):
	if v.is_empty() or not Defs.VISUAIS.has(str(v.get("id", ""))): return null
	var it: Dictionary = Defs.VISUAIS[str(v["id"])]
	var sil := str(it.get("silhueta", ""))
	if not _camadas.has(sil):
		var base := "res://assets/ext/armas/%s/%s" % [_kind_armas, sil]
		_camadas[sil] = {} if not FileAccess.file_exists(base + ".json") else {"json": Defs.ler(base + ".json"), "tex": Tema.tex(base + ".png"), "mask": Tema.tex(base + "_mascara.png")}
	var c: Dictionary = _camadas[sil]
	if c.is_empty(): return null
	var quadros: Dictionary = c["json"].get("quadros", {}).get(nome, {}).get(DIRS_ARMA[clampi(d, 0, 7)], {})
	var q = quadros.get(str(f))   # quadro -> {rect, offset}; sem a chave, a arma está escondida atrás do corpo
	if not (q is Dictionary): return null
	var r: Array = q["rect"]
	var o: Array = q["offset"]
	var ref := int(v.get("ref", 0))
	var forca := 0.0
	if it.get("brilho_proprio", false): forca = 0.6
	elif ref >= 7: forca = clampf(0.6 + float(ref - 7) / 8.0 * 0.4, 0.6, 1.0)
	return {"tex": c["tex"], "mask": c["mask"], "rect": Rect2(r[0], r[1], r[2], r[3]), "offset": Vector2(o[0], o[1]),
		"tinta": Defs.cor(str(it.get("tinta", "#9aa0a8"))), "brilho": Defs.cor(str(it.get("brilho", "#ffc890"))), "forca": forca}

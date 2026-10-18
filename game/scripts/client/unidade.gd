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
const ALCANCE_FORJA := 420.0    # a forja (martelo e fole) só se ouve de perto; o resto do jogo usa 1100 px
var _armas := {}       # slot -> Sprite2D (arma, segunda_mao)
var _camadas := {}     # silhueta -> {json, tex, mask}
var _kind_armas := ""  # classe com pasta em assets/armas (vazio: sem camadas)
var _raiz_armas := ""  # pasta das camadas de arma: assets/ext/armas/<classe> ou, voando de asa, assets/ext/asas/corpos/<classe>
# Asas equipáveis (assets/asas): com asa feita, o corpo vira a folha em voo (ou sem as asas próprias, no Anjo/Demônio)
# e a asa é desenhada em duas camadas: atrás do corpo e, quando as costas viram para a câmera, o pedaço da frente.
static var _ancoras_asa := {}   # assets/ext/asas/ancoras.json: classe -> anim -> dir -> [[dx, dy], ...]
static var _asas_cache := {}    # id visual -> {json, tex, frente}
var _kind := ""                 # classe/evolução desenhada (chave das pastas)
var _asa_id := ""               # item de asa equipado agora (de ent.vis)
var _asa := {}                  # camada ativa (vazio: sem asa por camada)
var asa_tras := Sprite2D.new()
var asa_frente := Sprite2D.new()
var anim_base := ""           # animação em loop no lugar de idle (eat do Andras devorando)
var sons := {}                # "sons" do substituto do NPC: loop posicional + som por quadro (forja do ferreiro)
var _quadro_total := 0        # quadros contados desde o início da animação em loop (detecta o quadro cruzado)

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
		# sem entrada: pasta com o id do NPC (modelo próprio) e, na falta dela, a classe de classe_visual
		var base: String = s.get("usa", e.kind if Defs.SPR.has(e.kind) else e.aux.get("visual", "humano"))
		if Defs.SPR.has(base): info = {"meta": Defs.SPR[base], "escala": float(s.get("escala", 1.0)), "tint": Defs.cor(s.get("tint", "#ffffff")), "fantasma": s.get("fantasma", false)}
		sons = s.get("sons", {})
	meta = info["meta"]
	escala_base = float(info.get("escala", 1.0)) * float(meta.get("escala", 1.0))
	if e.tipo == "chefe": escala_base *= 1.5   # chefe tem que impor presença
	_kind = kind
	_asa_id = _id_asa()
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
	if sombra.get_parent() == null:
		add_child(sombra)
		sombra.draw.connect(_desenhar_sombra)
		for sp in [asa_tras, asa_frente]:
			sp.centered = false; sp.region_enabled = true; sp.visible = false
			sp.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(asa_tras)
		add_child(corpo)
	_montar_armas()
	if asa_frente.get_parent() == null: add_child(asa_frente)   # por cima do corpo e das armas
	else: move_child(asa_frente, get_child_count() - 1)
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
	frame = 0; frame_t = 0.0; _quadro_total = 0
	corpo.texture = Tema.tex(a["file"])

## Esquiva: o teleporte some e volta já no destino; a névoa se desfaz e se refaz (shader dissolve).
## Voo, rolamento, salto, tranco e escudo são só a folha "evasao" (a altura do voo/salto está nela).
func evasao(estilo: String, dur: float) -> void:
	if morto: return
	var tw := create_tween()
	match estilo:
		"teleporte":
			tw.tween_property(self, "modulate:a", 0.0, minf(0.06, dur * 0.4))
			tw.tween_interval(maxf(0.04, dur * 0.7))
			tw.tween_callback(func(): if ent != null: pos_vis = Iso.to_screen(ent.pos))
			tw.tween_property(self, "modulate:a", 1.0, 0.12)
		"nevoa":
			tw.tween_method(func(x: float): mat.set_shader_parameter("dissolve", x), 0.0, 0.9, dur * 0.45)
			tw.tween_method(func(x: float): mat.set_shader_parameter("dissolve", x), 0.9, 0.0, dur * 0.55 + 0.12)
		_: tw.kill()

## Toca uma animação de ação uma vez (attack, shoot, spin, dash, hit, death, eat...). dur: segundos (ajusta o fps).
func tocar(nome: String, dur := 0.0) -> void:
	if morto and nome != "death": return
	var a := _sheet(nome)
	if a.is_empty():
		if nome == "evasao": a = _sheet("dash"); nome = "dash"   # personagem sem a folha nova: o dash (Humano) ou nada
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
	_aplicar_asa()

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
	if ent != null and ent.tipo == "jogador" and _id_asa() != _asa_id: _trocar_asa()
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
			var total := int(frame_t * fps)
			frame = total % int(a2["frames"])
			if not sons.is_empty(): _som_do_quadro(total, int(a2["frames"]))
	if morto and anim_unica != "_sem_morte":
		morte_t += dt
		if morte_t > 5.0: modulate.a = maxf(0.0, 1.0 - (morte_t - 5.0) / 1.0)
	if not sons.is_empty(): _som_em_loop()
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

## Som por quadro ("sons": {"quadros": {"idle": {"3": "itens/forja_martelo"}}}): toca uma vez por volta, quando a
## contagem de quadros cruza o quadro configurado (não a cada quadro de tela em que ele aparece).
func _som_do_quadro(total: int, n: int) -> void:
	var q: Dictionary = sons.get("quadros", {}).get(anim, {})
	if total > _quadro_total and not q.is_empty() and is_visible_in_tree():
		for i in range(_quadro_total + 1, mini(total, _quadro_total + n) + 1):   # quadros cruzados desde a última chamada
			var nome := str(q.get(str(i % n), ""))
			if nome != "": game.audio.tocar(nome, position, 0.0, 0.05, ALCANCE_FORJA)
	_quadro_total = total

## Loop posicional ("sons": {"loop": "ambiente/forja"}): pedido todo quadro enquanto a unidade está na tela;
## o Audio atenua pela distância ao jogador e para o loop sozinho quando ninguém mais pede.
func _som_em_loop() -> void:
	var loop := str(sons.get("loop", ""))
	if loop != "" and not morto and is_visible_in_tree(): game.audio.loop_em("npc_%d" % id, loop, position, -6.0, ALCANCE_FORJA)

func _exit_tree() -> void:
	if sons.has("loop") and is_instance_valid(game) and game.audio != null: game.audio.loop_fim("npc_%d" % id)

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
## Com asa feita equipada, a pasta é assets/asas/corpos/<classe> (mesmo formato, corpo em voo) e a asa entra por camada.
func _carregar_corpo_armado(kind: String) -> void:
	_asa = {}
	var raiz := "res://assets/ext/armas/%s" % kind
	var vis_asa := _visual_asa(_asa_id)
	if vis_asa != "" and FileAccess.file_exists("res://assets/ext/asas/corpos/%s/corpo/sprites.json" % kind) and _carregar_asa(vis_asa):
		raiz = "res://assets/ext/asas/corpos/%s" % kind
	var caminho := raiz + "/corpo/sprites.json"
	if not FileAccess.file_exists(caminho): return
	var c: Dictionary = Defs.ler(caminho)
	var m: Dictionary = meta.duplicate(true)
	m["frame"] = c["frame_size"]; m["anchor"] = c["anchor_feet"]; m["dirs"] = c["rows_dirs"]
	m["anims"] = {}
	for n in c["anims"]:
		var a: Dictionary = c["anims"][n].duplicate()
		a["file"] = "%s/corpo/%s" % [raiz, a["file"]]
		m["anims"][n] = a
	meta = m
	_kind_armas = kind if FileAccess.file_exists("res://assets/ext/armas/%s/corpo/sprites.json" % kind) else ""
	_raiz_armas = raiz

## Id do item no slot asa (ent.vis.asa, público: os outros jogadores também veem).
func _id_asa() -> String:
	if ent == null or ent.tipo != "jogador": return ""
	return str((ent.vis as Dictionary).get("asa", {}).get("id", ""))

## Desenho da asa: campo "visual" do item (null nas asas básicas do Anjo e do Demônio: ficam as asas do modelo).
func _visual_asa(id_item: String) -> String:
	if id_item == "": return ""
	var v = Defs.ITENS.get(id_item, {}).get("visual")
	return str(v) if v is String and v != "" else ""

func _carregar_asa(vis: String) -> bool:
	if _ancoras_asa.is_empty() and FileAccess.file_exists("res://assets/ext/asas/ancoras.json"):
		_ancoras_asa = Defs.ler("res://assets/ext/asas/ancoras.json")
	if not _ancoras_asa.has(_kind): return false
	if not _asas_cache.has(vis):
		var base := "res://assets/ext/asas/%s/" % vis
		if not FileAccess.file_exists(base + "asa.json"): return false
		var j: Dictionary = Defs.ler(base + "asa.json")
		var texs := {}
		for n in j["anims"]:
			texs[n] = [Tema.tex(base + j["anims"][n]["file"]), Tema.tex(base + j["anims"][n]["frente"])]
		_asas_cache[vis] = {"json": j, "tex": texs}
	_asa = _asas_cache[vis]
	return true

## Equipou ou tirou a asa: troca a folha do corpo (voo) e as camadas, sem recriar a unidade.
func _trocar_asa() -> void:
	_asa_id = _id_asa()
	meta = info["meta"]
	_camadas = {}
	_kind_armas = ""; _raiz_armas = ""
	_carregar_corpo_armado(_kind)
	if not _kind_armas.is_empty() and _armas.is_empty(): _montar_armas()
	var nome := anim if anim != "" else "idle"
	anim = ""
	_definir_anim(nome)
	_aplicar_frame()

## Camadas da asa: quadro pelo próprio relógio (pairar parado, voar andando), posição pelo encaixe nas costas
## do quadro atual do corpo (ancoras.json) menos o encaixe dentro do quadro da asa.
func _aplicar_asa() -> void:
	if _asa.is_empty() or morto:
		asa_tras.visible = false; asa_frente.visible = false; return
	var j: Dictionary = _asa["json"]
	var nome := "voar" if andando and anim_unica == "" else "pairar"
	var a: Dictionary = j["anims"][nome]
	var n := int(a["frames"])
	var f := int(tempo * float(a["fps"]) * (1.15 if nome == "voar" else 1.0)) % n
	var d: String = DIRS_ARMA[clampi(dir, 0, 7)]
	var r := j["rows_dirs"].find(d) as int
	var fs: Array = j["frame_size"]
	var por_anim: Dictionary = _ancoras_asa[_kind]
	var lista: Array = por_anim.get(anim, por_anim.get("idle", {})).get(d, [])
	var off := Vector2.ZERO
	if not lista.is_empty():
		var o: Array = lista[clampi(frame, 0, lista.size() - 1)]
		off = Vector2(o[0], o[1])
	var anc: Array = j["ancora"][d]
	var esc := corpo.scale
	var pes := corpo.position + Vector2(meta["anchor"][0], meta["anchor"][1]) * esc
	var p := pes + (off - Vector2(anc[0], anc[1])) * esc
	for k in 2:
		var sp: Sprite2D = asa_tras if k == 0 else asa_frente
		sp.visible = true
		sp.texture = _asa["tex"][nome][k]
		sp.region_rect = Rect2(f * fs[0], r * fs[1], fs[0], fs[1])
		sp.position = p
		sp.scale = esc

func _montar_armas() -> void:
	if _kind_armas == "" or not _armas.is_empty(): return
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
		var q = _quadro_arma(vis.get(slot, {}), slot, anim, dir, frame)
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

## Camada da mão para o item (ordem: silhueta do item, silhueta por personagem, padrão da classe; "" = mão vazia).
func _silhueta_arma(v: Dictionary, slot: String) -> String:
	var it: Dictionary = Defs.VISUAIS.get(str(v.get("id", "")), {})
	if not it.is_empty():
		var sil: Variant = it.get("silhueta")
		if sil != null and FileAccess.file_exists("res://assets/ext/armas/%s/%s.json" % [_kind_armas, sil]): return str(sil)
		var pp: Dictionary = it.get("por_personagem", {})
		if pp.has(_kind_armas): return "" if pp[_kind_armas] == null else str(pp[_kind_armas])
	if slot != "arma": return ""   # mão secundária sem item: vazia
	var padrao: Variant = Defs.PADRAO.get(_kind_armas)
	return "" if padrao == null else str(padrao)

## Quadro da camada da arma para a animação, direção e quadro atuais; null quando a arma está escondida.
func _quadro_arma(v: Dictionary, slot: String, nome: String, d: int, f: int):
	var sil := _silhueta_arma(v, slot)
	if sil == "": return null
	var it: Dictionary = Defs.VISUAIS.get(str(v.get("id", "")), {})
	if not _camadas.has(sil):
		var base := "%s/%s" % [_raiz_armas, sil]
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

extends Node2D
## Efeitos visuais do combate: folhas de efeitos (assets/efeitos), números de dano, telegrafias, projéteis,
## áreas no chão, raios e falas. Fica numa camada acima da iluminação para continuar legível no escuro.

const ESC := 2.0   # efeitos foram desenhados na base 640x360

var game
var chao_fx: Node2D           # camada iluminada (poças de sangue, rastros)
var teles := {}               # id -> Telegrafo
var projs := {}               # id -> Node2D
var areas := {}               # id -> Node2D
var numeros_por_alvo := {}    # id -> [tempo, contagem] (leque)
var t := 0.0
var _sens: Dictionary
var _estilos: Dictionary

func _ready() -> void:
	_sens = Defs.SENS
	_estilos = _sens.get("numeros_de_dano", {}).get("estilos", {})

func _process(dt: float) -> void:
	t += dt

# =================================================================== folhas de efeito
class Folha extends Node2D:
	var v: Dictionary
	var tex: Texture2D
	var f := 0.0
	var loop := false
	var dura := -1.0
	var segue: Node2D = null
	var desloc := Vector2.ZERO
	var escala := 2.0
	var vel := 1.0
	var fim_fade := 0.25
	func _process(dt: float) -> void:
		f += dt * float(v["fps"]) * vel
		if dura > 0.0:
			dura -= dt
			if dura <= 0.0: queue_free(); return
			if dura < fim_fade: modulate.a = dura / fim_fade
		var n := int(v["frames"])
		if not loop and dura <= 0.0 and int(f) >= n: queue_free(); return
		if segue != null:
			if is_instance_valid(segue):
				position = segue.position + desloc
				visible = segue.visible and not segue.get("morto")
			else:
				segue = null
				if dura > 100.0: queue_free(); return
		queue_redraw()
	func _draw() -> void:
		if tex == null: return
		var n := int(v["frames"])
		var i := int(f) % n if (loop or dura > 0.0) else mini(int(f), n - 1)
		var c := int(v["cols"])
		var fw := float(v["frame_w"]); var fh := float(v["frame_h"])
		var src := Rect2((i % c) * fw, (i / c) * fh, fw, fh)
		var anc: Array = v["anchor"]
		draw_texture_rect_region(tex, Rect2(-Vector2(anc[0], anc[1]) * escala, Vector2(fw, fh) * escala), src)

func folha(nome: String, pos: Vector2, opc: Dictionary = {}) -> Node2D:
	var v: Dictionary = Defs.VFX.get(nome, {})
	if v.is_empty(): return null
	var n := Folha.new()
	n.v = v
	n.tex = Tema.tex(v["sheet"])
	n.position = pos
	n.loop = bool(v.get("loop", false)) and opc.has("dura")
	n.dura = float(opc.get("dura", -1.0))
	n.escala = ESC * float(opc.get("escala", 1.0))
	n.vel = float(opc.get("vel", 1.0))
	if opc.has("segue"): n.segue = opc["segue"]; n.desloc = opc.get("desloc", Vector2.ZERO)
	if opc.has("rot"): n.rotation = opc["rot"]
	if opc.has("cor"): n.modulate = opc["cor"]
	if opc.get("aditivo", false):
		var m := CanvasItemMaterial.new(); m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD; n.material = m
	if v.get("layer", "frente") == "chao" and chao_fx != null and not opc.get("frente", false):
		chao_fx.add_child(n)
	else:
		add_child(n)
	return n

## Nome do efeito de uma habilidade ("classe/id") nas folhas da thread de Efeitos.
func nome_skill(skill: String) -> Array:
	var p := skill.split("/")
	if p.size() < 2: return []
	var pref: String = {"anjo": "anjo_", "cultista": "cult_", "demonio": "dem_", "humano": "hum_", "mutante": "mut_", "tecnomancer": "tec_"}.get(p[0], "")
	var id: String = p[1]
	# skills em área do nível 5 (v0.6): sem folha própria ainda, usam folhas existentes
	var nivel5 := {"anjo_leque_juizo": ["anjo_leque_juizo_frente", "anjo_leque_juizo_tras"], "demonio_ceifa_infernal": ["hum_corte_largo_frente", "hum_corte_largo_tras"],
		"mutante_terremoto_putrido": ["chefe_onda_choque", "mut_rugido_praga"], "tecnomancer_tempestade_bobina": ["tec_pulso_antidivino"],
		"cultista_espinhos_sangue": ["sangue_jorro", "sangue_poca"], "humano_coquetel_querosene": ["status_queimando", "golpe_impacto"]}
	if nivel5.has(id): return (nivel5[id] as Array).filter(func(n): return Defs.VFX.has(n))
	var achou: Array = []
	if Defs.VFX.has(pref + id): return [pref + id]
	for k in Defs.VFX.keys():
		if k.begins_with(pref + id): achou.append(k)
	if achou.is_empty():
		var tok := id.split("_")[0]
		for k in Defs.VFX.keys():
			if k.begins_with(pref + tok): achou.append(k)
	achou.sort()
	return achou

# =================================================================== números de dano
func numero(pos: Vector2, valor: int, estilo: String, id_alvo: int) -> void:
	var e: Dictionary = _estilos.get(estilo, _estilos.get("normal", {}))
	var txt: String = e.get("texto", "{dano}")
	txt = txt.replace("{dano}", str(valor)).replace("{valor}", str(valor))
	var l := Label.new()
	l.text = txt
	var esc := float(e.get("escala", 1.0))
	l.add_theme_font_override("font", Tema.FONTE_TITULO)
	l.add_theme_font_size_override("font_size", int(17 * esc))
	l.add_theme_color_override("font_color", Defs.cor(e.get("cor", "#e8dfc9")))
	l.add_theme_constant_override("outline_size", 5)
	l.add_theme_color_override("font_outline_color", Defs.cor(e.get("contorno", "#0a0808")))
	l.z_index = 50
	add_child(l)
	l.reset_size()
	# leque: vários números no mesmo alvo abrem para os lados
	var k: Array = numeros_por_alvo.get(id_alvo, [0.0, 0])
	if t - float(k[0]) > 0.6: k = [t, 0]
	k[1] = int(k[1]) + 1; k[0] = t
	numeros_por_alvo[id_alvo] = k
	var leque := float(((int(k[1]) % 5) - 2) * 14)
	l.position = pos + Vector2(-l.size.x * 0.5 + randf_range(-8, 8) + leque, -l.size.y - 6 - (int(k[1]) % 3) * 8)
	l.pivot_offset = l.size * 0.5
	var tw := l.create_tween()
	if e.get("pop", false):
		l.scale = Vector2.ONE * 1.6
		tw.tween_property(l, "scale", Vector2.ONE, 0.08)
	tw.set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 52, 0.75).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(l, "modulate:a", 0.0, 0.3).set_delay(0.45)
	tw.chain().tween_callback(l.queue_free)

func texto_flutuante(pos: Vector2, txt: String, cor: Color, tam := 15, dur := 1.6) -> void:
	var l := Tema.rotulo(txt, tam, cor, Tema.FONTE_TITULO, 5)
	l.z_index = 55
	add_child(l)
	l.reset_size()
	l.position = pos - Vector2(l.size.x * 0.5, l.size.y)
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 30, dur)
	tw.tween_property(l, "modulate:a", 0.0, dur * 0.4).set_delay(dur * 0.6)
	tw.chain().tween_callback(l.queue_free)

## Fala em balão sobre uma unidade (NPC, chefe, mímico).
func fala(view: Node2D, txt: String, cor := Color("#f0e2c0"), dur := 3.5) -> void:
	if view == null: return
	var p := PanelContainer.new()
	var sb := Tema.caixa(Color(0.06, 0.05, 0.04, 0.86), Color(0.45, 0.36, 0.22), 1, 3)
	sb.set_content_margin_all(6); sb.shadow_size = 4
	p.add_theme_stylebox_override("panel", sb)
	var l := Tema.rotulo(txt, 14, cor, Tema.FONTE_ITALICO)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = mini(320, 40 + txt.length() * 7)
	p.add_child(l)
	p.z_index = 60
	add_child(p)
	p.reset_size()
	var alt: float = view.altura_px if "altura_px" in view else 100.0
	var seguir := func():
		if is_instance_valid(view) and is_instance_valid(p):
			p.position = view.position + Vector2(-p.size.x * 0.5, -alt - p.size.y - 26)
	seguir.call()
	var tw := p.create_tween()
	tw.tween_method(func(_x): seguir.call(), 0.0, 1.0, dur)
	tw.tween_property(p, "modulate:a", 0.0, 0.4)
	tw.tween_callback(p.queue_free)

# =================================================================== telegrafias
class Telegrafo extends Node2D:
	var forma := "circulo"
	var p: Dictionary
	var dir := Vector2.RIGHT
	var dur := 1.0
	var t := 0.0
	var segue: Ent = null
	var origem := Vector2.ZERO
	var acabou := false
	var fim_t := 0.0
	var cor_borda := Color("#c0281c")
	var cor_fill := Color("#7a1612")
	var ativo := false
	var t2 := 0.0
	func _process(dt: float) -> void:
		t += dt
		if ativo:
			t2 += dt
		if segue != null and not acabou: origem = segue.pos
		position = Iso.to_screen(origem)
		if acabou:
			fim_t += dt
			modulate.a = maxf(0.0, 1.0 - fim_t / 0.25)
			if fim_t > 0.25: queue_free()
		queue_redraw()
	func _pts_circulo(r: float, a0 := 0.0, a1 := TAU, n := 48) -> PackedVector2Array:
		var pts := PackedVector2Array()
		for i in n + 1:
			var a := a0 + (a1 - a0) * i / n
			pts.append(Iso.to_screen(Vector2(cos(a), sin(a)) * r))
		return pts
	func _draw() -> void:
		var k := clampf(t / maxf(dur, 0.05), 0.0, 1.0)
		var piscar := 1.0
		if dur - t < 0.15 and not acabou: piscar = 0.55 + 0.45 * sin(t * 60.0)
		var af := lerpf(0.16, 0.45, k) * piscar
		if acabou: af = 0.6
		var cb := Color(cor_borda.r, cor_borda.g, cor_borda.b, 0.9 * piscar)
		var cf := Color(cor_fill.r, cor_fill.g, cor_fill.b, af)
		var ang := dir.angle()
		match forma:
			"circulo", "circulo_segue_jogador":
				var r := float(p.get("raio", 1.5))
				draw_colored_polygon(_pts_circulo(r), Color(cf.r, cf.g, cf.b, af * 0.45))
				draw_colored_polygon(_pts_circulo(r * k), cf)
				draw_polyline(_pts_circulo(r), cb, 2.0, true)
			"cone":
				var r2 := float(p.get("raio", 3.0))
				var meia := deg_to_rad(float(p.get("angulo", 90.0))) * 0.5
				var base := PackedVector2Array([Vector2.ZERO]); base.append_array(_pts_circulo(r2, ang - meia, ang + meia, 24))
				var ench := PackedVector2Array([Vector2.ZERO]); ench.append_array(_pts_circulo(r2 * k, ang - meia, ang + meia, 24))
				draw_colored_polygon(base, Color(cf.r, cf.g, cf.b, af * 0.45))
				if k > 0.02: draw_colored_polygon(ench, cf)
				base.append(Vector2.ZERO)
				draw_polyline(base, cb, 2.0, true)
			"linha":
				var comp := float(p.get("comprimento", 6.0))
				var larg := float(p.get("largura", 1.5)) * 0.5
				var n := Vector2(-dir.y, dir.x)
				var q := [n * larg, n * larg + dir * comp, -n * larg + dir * comp, -n * larg]
				var qs := PackedVector2Array(); for v in q: qs.append(Iso.to_screen(v))
				var qk := PackedVector2Array([Iso.to_screen(n * larg), Iso.to_screen(n * larg + dir * comp * k), Iso.to_screen(-n * larg + dir * comp * k), Iso.to_screen(-n * larg)])
				draw_colored_polygon(qs, Color(cf.r, cf.g, cf.b, af * 0.45))
				if k > 0.02: draw_colored_polygon(qk, cf)
				qs.append(qs[0])
				draw_polyline(qs, cb, 2.0, true)
			"anel":
				var rf := float(p.get("raio_final", 6.0))
				var larg := float(p.get("largura", 0.8))
				var gap := deg_to_rad(float(p.get("vao_graus", 45.0)))
				var a0 := ang + gap * 0.5
				var a1 := ang + TAU - gap * 0.5
				if not ativo:
					draw_polyline(_pts_circulo(rf, a0, a1, 48), Color(cb.r, cb.g, cb.b, 0.5 * piscar), 2.0, true)
					var vao := PackedVector2Array([Vector2.ZERO]); vao.append_array(_pts_circulo(rf, ang - gap * 0.5, ang + gap * 0.5, 8))
					draw_colored_polygon(vao, Color(0.6, 0.9, 1.0, 0.12))
					draw_polyline(_pts_circulo(rf * k, a0, a1, 48), Color(cb.r, cb.g, cb.b, 0.35), 1.0, true)
				else:
					var rr := rf * clampf(t2 / 1.1, 0.0, 1.0)
					var fora := _pts_circulo(rr + larg * 0.5, a0, a1, 48)
					var dentro := _pts_circulo(maxf(0.05, rr - larg * 0.5), a0, a1, 48)
					dentro.reverse()
					var poly := fora.duplicate(); poly.append_array(dentro)
					draw_colored_polygon(poly, Color(cb.r, cb.g, cb.b, 0.55))
					draw_polyline(fora, Color(1, 1, 1, 0.7), 1.5, true)

func telegrafo(d: Dictionary) -> void:
	var tg := Telegrafo.new()
	tg.forma = d.get("forma", "circulo")
	tg.p = d.get("p", {})
	tg.dir = d.get("dir", Vector2.RIGHT)
	tg.dur = float(d.get("dur", 1.0))
	tg.origem = d.get("origem", Vector2.ZERO)
	if int(d.get("segue", -1)) >= 0: tg.segue = game.sim.ents.get(int(d["segue"]))
	var dono: Ent = game.sim.ents.get(int(d.get("dono", -1)))
	if dono != null and dono.tipo == "chefe":
		tg.cor_borda = Color("#ff3a1c")
	if dono != null and dono.kind == "zacarias_arauto":
		tg.cor_borda = Color("#ffe08a"); tg.cor_fill = Color("#c89a2a")
	if dono != null and dono.kind == "irma_celeste":
		tg.cor_borda = Color("#cfe4ff"); tg.cor_fill = Color("#5a6a9a")
	tg.z_index = -5
	add_child(tg)
	teles[int(d["id"])] = tg

func telegrafo_anel(id: int) -> void:
	var tg: Telegrafo = teles.get(id)
	if tg != null and is_instance_valid(tg): tg.ativo = true; tg.t2 = 0.0

func telegrafo_fim(id: int) -> void:
	var tg: Telegrafo = teles.get(id)
	if tg != null and is_instance_valid(tg):
		tg.acabou = true; tg.t = tg.dur
		var centro := Iso.to_screen(tg.origem)
		if tg.forma in ["circulo", "circulo_segue_jogador"]:
			folha("chefe_onda_choque", centro, {"escala": maxf(0.6, float(tg.p.get("raio", 1.5)) / 2.0)})
	teles.erase(id)

# =================================================================== projéteis
class Projetil extends Node2D:
	var pos := Vector2.ZERO
	var dir := Vector2.RIGHT
	var vel := 12.0
	var alvo: Ent = null
	var cor := Color(1, 0.8, 0.4)
	var folha: Dictionary = {}
	var tex: Texture2D
	var f := 0.0
	var rastro: Array = []
	var altura := 48.0
	func _process(dt: float) -> void:
		if alvo != null and alvo.vivo:
			var d := alvo.pos - pos
			if d.length() > 0.05: dir = d.normalized()
		pos += dir * vel * dt
		position = Iso.to_screen(pos) + Vector2(0, -altura)
		rastro.push_front(position)
		if rastro.size() > 7: rastro.pop_back()
		f += dt * 16.0
		queue_redraw()
	func _draw() -> void:
		var sd := Iso.to_screen(dir).normalized()
		for i in range(1, rastro.size()):
			var a: Vector2 = rastro[i - 1] - position
			var b: Vector2 = rastro[i] - position
			draw_line(a, b, Color(cor.r, cor.g, cor.b, 0.5 * (1.0 - float(i) / rastro.size())), 4.0 - i * 0.4, true)
		if tex != null and not folha.is_empty():
			var n := int(folha["frames"]); var c := int(folha["cols"])
			var i2 := int(f) % n
			var fw := float(folha["frame_w"]); var fh := float(folha["frame_h"])
			var anc: Array = folha["anchor"]
			draw_set_transform(Vector2.ZERO, sd.angle(), Vector2(2, 2))
			draw_texture_rect_region(tex, Rect2(-Vector2(anc[0], anc[1]), Vector2(fw, fh)), Rect2((i2 % c) * fw, (i2 / c) * fh, fw, fh))
			draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		else:
			draw_circle(Vector2.ZERO, 7.0, Color(cor.r, cor.g, cor.b, 0.35))
			draw_circle(Vector2.ZERO, 4.0, cor)
			draw_circle(Vector2.ZERO, 2.0, Color(1, 1, 0.9))

const COR_ELEM := {"fisico": Color("#e8d8b0"), "fogo": Color("#ff8a2a"), "sagrado": Color("#fff0a0"), "sangue": Color("#d0202a"),
	"veneno": Color("#9cff3a"), "eletrico": Color("#8ad8ff"), "profano": Color("#b060ff"), "gelo": Color("#a0e0ff")}

func projetil(d: Dictionary) -> void:
	var pr := Projetil.new()
	pr.pos = d["pos"]
	pr.dir = d.get("dir", Vector2.RIGHT)
	pr.vel = float(d.get("vel", 12.0))
	if int(d.get("alvo", -1)) >= 0: pr.alvo = game.sim.ents.get(int(d["alvo"]))
	var vfx: String = d.get("vfx", "")
	var el: String = d.get("elem", "fisico")
	pr.cor = COR_ELEM.get(el, Color(1, 0.85, 0.6))
	if d.get("cor", "") != "": pr.cor = Defs.cor(d["cor"])
	var nome := ""
	if vfx in ["bala", "projetil_bala", "basico_humano", "tiro_certeiro"]: nome = "projetil_bala"
	elif vfx in ["sangria", "basico_cultista"]: nome = "cult_sangria_projetil"
	if nome != "" and Defs.VFX.has(nome):
		pr.folha = Defs.VFX[nome]; pr.tex = Tema.tex(pr.folha["sheet"])
	var de: Ent = game.sim.ents.get(int(d.get("de", -1)))
	if de != null and de.tipo == "monstro": pr.altura = 40.0
	add_child(pr)
	projs[int(d["id"])] = pr
	var luz = game.luz.adicionar(Iso.to_screen(pr.pos), pr.cor, 1.6, 1.1)
	pr.set_meta("luz", luz)

func projetil_fim(id: int, pos: Vector2) -> void:
	var pr: Projetil = projs.get(id)
	projs.erase(id)
	if pr == null or not is_instance_valid(pr): return
	if pr.has_meta("luz"):
		var l = pr.get_meta("luz")
		if is_instance_valid(l): l.queue_free()
	if not pr.folha.is_empty() and pr.folha["name"] == "projetil_bala": folha("impacto_bala", Iso.to_screen(pos) + Vector2(0, -40))
	elif not pr.folha.is_empty(): folha("cult_sangria_impacto", Iso.to_screen(pos) + Vector2(0, -40))
	pr.queue_free()

func atualizar_luzes_projeteis() -> void:
	for pr in projs.values():
		if is_instance_valid(pr) and pr.has_meta("luz"):
			var l = pr.get_meta("luz")
			if is_instance_valid(l): l.position = Iso.to_screen(pr.pos)

# =================================================================== áreas no chão
class Area extends Node2D:
	var raio := 1.0
	var tipo := ""
	var cor := Color(1, 0.4, 0.1)
	var t := 0.0
	var dur := 1.0
	func _process(dt: float) -> void:
		t += dt
		queue_redraw()
	func _draw() -> void:
		var a := 1.0
		if dur - t < 0.4: a = maxf(0.0, (dur - t) / 0.4)
		if t < 0.25: a = t / 0.25
		var e := Iso.elipse(raio)
		var pul := 0.85 + 0.15 * sin(t * 6.0)
		for i in 4:
			var k := 1.0 - i * 0.22
			Unidade_elipse(self, e * k, Color(cor.r, cor.g, cor.b, 0.12 * a * pul))
		var pts := PackedVector2Array()
		for i in 41:
			var ang := TAU * i / 40.0
			pts.append(Vector2(cos(ang) * e.x, sin(ang) * e.y) * (0.97 + 0.03 * sin(ang * 7.0 + t * 3.0)))
		draw_polyline(pts, Color(cor.r, cor.g, cor.b, 0.7 * a), 1.5, true)
	static func Unidade_elipse(c: CanvasItem, r: Vector2, cor: Color) -> void:
		var pts := PackedVector2Array()
		for i in 33:
			var t2 := TAU * i / 32.0
			pts.append(Vector2(cos(t2) * r.x, sin(t2) * r.y))
		c.draw_colored_polygon(pts, cor)

const COR_AREA := {"fogo": Color("#ff6a1a"), "veneno": Color("#7cff2a"), "cinzas": Color("#9a8a8a"), "armadilha": Color("#d8e8ff"),
	"halo": Color("#ffe8a0"), "sagrado": Color("#ffe8a0"), "campo": Color("#8ad8ff"), "praga": Color("#9cff3a"), "sangue": Color("#c0202a")}

func area(d: Dictionary) -> void:
	var a := Area.new()
	a.raio = float(d.get("raio", 1.0))
	a.tipo = d.get("tipo", "")
	a.dur = float(d.get("dur", 1.0))
	a.cor = COR_AREA.get(a.tipo, Color(1, 0.5, 0.2))
	a.position = Iso.to_screen(d["pos"])
	a.z_index = -8
	add_child(a)
	areas[int(d["id"])] = a
	if a.tipo == "fogo":
		for i in 3:
			var off := Vector2.from_angle(randf() * TAU) * randf() * a.raio * 0.7
			folha("status_queimando", Iso.to_screen(d["pos"] + off), {"dura": a.dur, "escala": 0.8})
		var l = game.luz.adicionar(a.position, Color(1, 0.5, 0.15), a.raio * 2.2, 1.0, true)
		get_tree().create_timer(a.dur).timeout.connect(func(): if is_instance_valid(l): l.queue_free())
	elif a.tipo == "cinzas" and Defs.VFX.has("cult_chuva_cinzas"):
		folha("cult_chuva_cinzas", a.position, {"dura": a.dur, "escala": a.raio / 1.5})
	elif a.tipo == "veneno":
		folha("status_veneno", a.position, {"dura": a.dur, "escala": a.raio})

func area_fim(id: int) -> void:
	var a: Area = areas.get(id)
	areas.erase(id)
	if a != null and is_instance_valid(a): a.queue_free()

# =================================================================== raio (arco voltaico, lança de luz)
class Raio extends Node2D:
	var a := Vector2.ZERO
	var b := Vector2.ZERO
	var cor := Color("#8ad8ff")
	var t := 0.0
	var dur := 0.25
	var coluna := false
	func _process(dt: float) -> void:
		t += dt
		if t > dur: queue_free()
		queue_redraw()
	func _draw() -> void:
		var al := 1.0 - t / dur
		if coluna:
			draw_rect(Rect2(b.x - 10, b.y - 600, 20, 600), Color(cor.r, cor.g, cor.b, 0.35 * al))
			draw_rect(Rect2(b.x - 4, b.y - 600, 8, 600), Color(1, 1, 0.95, 0.8 * al))
			return
		for k in 2:
			var pts := PackedVector2Array([a])
			var n := 8
			for i in range(1, n):
				var p := a.lerp(b, float(i) / n)
				var nrm := (b - a).normalized().orthogonal()
				pts.append(p + nrm * randf_range(-12, 12))
			pts.append(b)
			draw_polyline(pts, Color(cor.r, cor.g, cor.b, 0.5 * al), 6.0 - k * 3, true)
			draw_polyline(pts, Color(1, 1, 1, 0.9 * al), 1.5, true)

func raio(de: Vector2, para: Vector2, cor: Color, coluna := false) -> void:
	var r := Raio.new()
	r.a = de; r.b = para; r.cor = cor; r.coluna = coluna
	if coluna: r.dur = 0.5
	add_child(r)

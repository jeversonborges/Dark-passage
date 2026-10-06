extends Node2D
## Cliente do jogo: desenha o que o servidor (WorldSim, no mesmo processo) manda e envia os comandos do jogador.
## Camadas: chão (shader) < decalques < mundo (y-sort: cenário + unidades) < luz (multiplica) < efeitos/nomes < HUD.

const Chao := preload("res://scripts/client/chao.gd")
const Luz := preload("res://scripts/client/luz.gd")
const Unidade := preload("res://scripts/client/unidade.gd")
const Efeitos := preload("res://scripts/client/efeitos.gd")
const Audio := preload("res://scripts/client/audio.gd")
const Hud := preload("res://scripts/client/hud.gd")
const Janelas := preload("res://scripts/client/janelas.gd")

const SAVE := "user://dark_passage_v2.save"

var sim: WorldSim
var jog: Ent
var mapa: Dictionary
var chao: Node2D
var decal := Node2D.new()
var mundo := Node2D.new()
var luz: Node
var camada_fx := CanvasLayer.new()
var fx: Node2D
var sobre := Node2D.new()
var clima := CanvasLayer.new()
var audio: Node
var hud: CanvasLayer
var janelas: CanvasLayer
var cam := Camera2D.new()
var views := {}            # id -> Unidade
var objs := {}             # id -> ObjView (baús, portais, interativos)
var itens_chao := {}       # id -> ItemChao
var props_altos: Array = []
var oclusores: Array = []          # [sprite, rect, kind] de todo prop de pé que pode esconder o jogador
var mascaras := {}                 # kind -> BitMap da arte (alfa), para testar oclusão por pixel
var silhueta := Sprite2D.new()     # o jogador desenhado por cima do cenário quando está escondido
var silhueta_a := 0.0
var hover_id := -1
var hover_chao := -1
var segurando := false
var t_seguro := 0.0
var acc := 0.0
var t := 0.0
var tremor := 0.0
var tremor_px := 0.0
var mostrar_nomes := false
var luz_jogador: Sprite2D
var trocando := false
var cortina := ColorRect.new()
var chefe_view: Node2D = null
var t_salvar := 0.0
var cores_piso := {}
var zona_atual := ""
var musica_chefe := false
var rede: Node = null      # conexão de rede (null = jogo solo, o mundo roda aqui mesmo)

# =================================================================== início
func iniciar(classe: String, nome: String, salvo: Dictionary = {}) -> void:
	Tema.carregar()
	sim = WorldSim.new(randi())
	sim.evento.connect(_ev)
	jog = Jogador.criar(sim, classe, nome, salvo)
	_montar_nos()
	var mapa_ini: String = salvo.get("mapa", "area_inicial")
	var pos := Vector2(-1, -1)
	if salvo.get("pos", []).size() == 2: pos = Vector2(salvo["pos"][0], salvo["pos"][1])
	_entrar(mapa_ini, pos)
	if salvo.is_empty() and not OS.get_cmdline_user_args().has("fotos") and not "fotos" in " ".join(OS.get_cmdline_user_args()):
		hud.mostrar_ajuda()

# =================================================================== rede
var chefe_estado := ""     # em rede o chefe mora no servidor; só o estado vem para cá

## Cliente de rede: o mundo roda no servidor; aqui só um espelho (geometria do mapa + entidades que chegam).
func iniciar_rede(r: Node, m: Dictionary) -> void:
	Tema.carregar()
	rede = r
	_montar_nos()
	rede.mensagem.connect(_msg_rede)
	_entrar_rede(m)
	if m.get("novo", false): hud.mostrar_ajuda()

func sair_rede() -> void:
	if rede != null: rede.sair()

func _msg_rede(m: Dictionary) -> void:
	match m.get("t", ""):
		"mapa": _entrar_rede(m)
		"tick": _tick_rede(m)

func _entrar_rede(m: Dictionary) -> void:
	var trocou := not mapa.is_empty()
	_limpar_visual()
	sim = WorldSim.new(1)
	sim.carregar_geometria(m["mapa"])
	mapa = sim.mapa
	Sincro.aplicar(sim, m.get("ents", {}))
	var ch: Dictionary = m.get("chao", {})
	for c in ch: sim.chao[int(c)] = ch[c]
	sim.spawns = m.get("spawns", [])
	chefe_estado = m.get("chefe", "")
	jog = sim.ents.get(int(m["eu"]))
	_montar_mapa()
	for e: Ent in sim.ents.values(): _surgiu(e.id)
	for c in sim.chao.keys(): _item_chao(c, sim.chao[c]["pos"], sim.chao[c]["pos"])
	cam.position = Iso.to_screen(jog.pos)
	cam.reset_smoothing()
	hud.ao_trocar_mapa()
	if trocou and m["mapa"] != "area_inicial": audio.tocar("musica/vinheta/entrar_cripta")
	cortina.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_property(cortina, "modulate:a", 0.0, 0.8)

func _tick_rede(m: Dictionary) -> void:
	if sim == null: return
	if m.has("e"): Sincro.aplicar(sim, m["e"])
	if m.has("chefe"):
		chefe_estado = m["chefe"]
		for o in objs.values(): _atualizar_visibilidade_obj(o)
	for ev in m.get("ev", []):
		var tipo: String = ev[0]
		var d: Dictionary = ev[1]
		if tipo == "chao_novo":
			sim.chao[int(d["id"])] = {"id": int(d["id"]), "item": d.get("item", {}), "pos": d["pos"], "dono": int(d.get("dono", -1)), "t": 0.0}
		_ev(tipo, d)
		if tipo == "chao_sumiu": sim.chao.erase(int(d["id"]))
	for id in m.get("x", []):
		_sumiu(int(id))
		sim.ents.erase(int(id))

func _chefe_vivo() -> bool:
	if rede != null: return chefe_estado != "" and chefe_estado != "morto"
	return sim.chefe != null and sim.chefe.estado != "morto"

func _montar_nos() -> void:
	chao = Chao.new(); chao.z_index = -30; add_child(chao)
	decal.z_index = -20; add_child(decal)
	mundo.y_sort_enabled = true; add_child(mundo)
	add_child(cam)
	cam.enabled = true
	cam.position_smoothing_enabled = false
	cam.zoom = Vector2(1.2, 1.2)
	luz = Luz.new(); add_child(luz)
	luz.cam_principal = cam
	camada_fx.layer = 2
	camada_fx.follow_viewport_enabled = true
	add_child(camada_fx)
	var shs := Shader.new()
	shs.code = "shader_type canvas_item;\nuniform vec4 cor : source_color = vec4(0.98, 0.74, 0.36, 0.5);\nvoid fragment() { vec4 t = texture(TEXTURE, UV); COLOR = vec4(mix(t.rgb * 0.7, cor.rgb, 0.55), step(0.4, t.a) * cor.a * COLOR.a); }"
	var shm := ShaderMaterial.new(); shm.shader = shs
	silhueta.material = shm
	silhueta.centered = false
	silhueta.region_enabled = true
	silhueta.visible = false
	camada_fx.add_child(silhueta)
	fx = Efeitos.new(); fx.game = self; fx.chao_fx = decal
	camada_fx.add_child(fx)
	sobre.z_index = 40
	camada_fx.add_child(sobre)
	sobre.draw.connect(_desenhar_sobre)
	clima.layer = 3; add_child(clima)
	audio = Audio.new(); add_child(audio)
	hud = Hud.new(); hud.game = self; add_child(hud)
	janelas = Janelas.new(); janelas.game = self; add_child(janelas)
	var cl := CanvasLayer.new(); cl.layer = 50; add_child(cl)
	cortina.color = Color.BLACK; cortina.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	cortina.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cl.add_child(cortina)

func _entrar(id_mapa: String, pos: Vector2) -> void:
	var m: Dictionary = Defs.ler("res://data/mapas/%s.json" % id_mapa)
	var nascer := pos.x < 0
	if pos.x < 0:
		var spf: Dictionary = m.get("spawn_por_faccao", {})
		var s: Array = spf.get(jog.faccao, m.get("spawn", [10, 10]))
		pos = Vector2(s[0], s[1])
	_limpar_visual()
	mapa = m
	Jogador.entrar(sim, jog, id_mapa, pos)
	mapa = sim.mapa
	_montar_mapa()
	if nascer: jog.pos = _spawn_aberto(jog.pos)
	for e: Ent in sim.ents.values(): _surgiu(e.id)
	for c in sim.chao.keys(): _item_chao(c, sim.chao[c]["pos"], sim.chao[c]["pos"])
	cam.position = Iso.to_screen(jog.pos)
	cam.reset_smoothing()
	hud.ao_trocar_mapa()
	var tw := create_tween()
	cortina.modulate.a = 1.0
	tw.tween_property(cortina, "modulate:a", 0.0, 0.8)

## Pedido do jogador ao mundo (Comandos). Em rede vai para o servidor; no solo executa direto.
func cmd(nome: String, a: Array = []) -> void:
	if rede != null:
		rede.enviar_cmd(nome, a)
		return
	Comandos.executar(sim, jog, nome, a)

func _limpar_visual() -> void:
	for v in views.values(): v.queue_free()
	for o in objs.values(): o.queue_free()
	for c in itens_chao.values(): c.queue_free()
	views.clear(); objs.clear(); itens_chao.clear(); props_altos.clear(); oclusores.clear()
	for c in mundo.get_children(): c.queue_free()
	for c in decal.get_children(): c.queue_free()
	for c in fx.get_children(): c.queue_free()
	fx.teles.clear(); fx.projs.clear(); fx.areas.clear()
	for c in clima.get_children(): c.queue_free()
	camadas_clima.clear(); tempestade.clear(); tempestade_alvo = 0.0
	luz.limpar()
	chefe_view = null
	musica_chefe = false
	zona_atual = ""

# =================================================================== mapa: chão, cenário, luzes, clima
func _montar_mapa() -> void:
	chao.montar(mapa)
	var amb: Dictionary = Defs.AMB.get("objetos", {})
	for p in mapa.get("props", []):
		if p.has("oculto_por_obj"): continue
		var k: String = p["k"]
		if not amb.has(k): continue
		var s := _sprite_kit(k, Vector2(p["x"], p["y"]))
		if s == null: continue
		if p.get("chao", 0) == 1: decal.add_child(s)
		else:
			mundo.add_child(s)
			var m: Dictionary = amb[k]
			if float(m["h"]) >= 56.0:
				oclusores.append([s, Rect2(s.position + s.offset, s.texture.get_size()), k])
			if float(m["h"]) > 200.0 and not k.begins_with("parede_"):
				var anc: Array = m["anchor"]
				props_altos.append([s, Rect2(s.position - Vector2(anc[0], anc[1]) + Vector2(m["w"] * 0.1, 0), Vector2(m["w"] * 0.8, m["h"] * 0.85))])
	# luz ambiente e pontos de luz
	var ceu: Dictionary = mapa.get("ceu", {})
	var cor: Array = ceu.get("cor", [0.8, 0.8, 0.75])
	var k := maxf(0.86, 1.36 - float(ceu.get("escuro", 0.4)) * 0.8)
	luz.definir_ambiente(Color(cor[0] * k, cor[1] * k, cor[2] * k))
	for l in mapa.get("luzes", []):
		var c := Color(l[2], l[3], l[4])
		var fogo: bool = c.r > c.b * 1.6 and c.r > 0.8
		luz.adicionar(Iso.to_screen(Vector2(l[0], l[1])), c, float(l[5]) * 0.9, 1.25 if fogo else 1.0, fogo)
	luz_jogador = luz.adicionar(Iso.to_screen(jog.pos), Color(1.0, 0.86, 0.66), 6.5 if not mapa.get("exterior", false) else 4.5, 0.85, true)
	_montar_clima(ceu)
	# câmera
	var c4: Array = mapa.get("camera", [0, 0, mapa["w"], mapa["h"]])
	cam.limit_left = int(32.0 * (c4[0] + c4[1]))
	cam.limit_right = int(32.0 * (c4[2] + c4[3]))
	cam.limit_top = int(16.0 * (c4[0] - c4[3]))
	cam.limit_bottom = int(16.0 * (c4[2] - c4[1]))
	_cores_minimapa()

func _sprite_kit(k: String, p: Vector2) -> Sprite2D:
	var amb: Dictionary = Defs.AMB.get("objetos", {})
	if not amb.has(k): return null
	var tex := Tema.tex("res://assets/ext/ambiente/objetos/%s.png" % k)
	if tex == null: return null
	var m: Dictionary = amb[k]
	var s := Sprite2D.new()
	s.texture = tex
	s.centered = false
	var anc: Array = m["anchor"]
	s.offset = -Vector2(anc[0], anc[1])
	s.position = Iso.to_screen(p)
	return s

func _montar_clima(ceu: Dictionary) -> void:
	# vinheta e poeira do Amargo (fora) ou escuro de porão (dentro)
	var vin := TextureRect.new()
	var g := Gradient.new()
	g.set_color(0, Color(0, 0, 0, 0)); g.set_color(1, Color(0, 0, 0, 0.6 if not mapa.get("exterior", false) else 0.32))
	g.add_point(0.55, Color(0, 0, 0, 0))
	var gt := GradientTexture2D.new()
	gt.gradient = g; gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5); gt.fill_to = Vector2(1.05, 0.5); gt.width = 256; gt.height = 256
	vin.texture = gt
	vin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vin.stretch_mode = TextureRect.STRETCH_SCALE
	vin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clima.add_child(vin)
	if mapa.get("exterior", false):
		_camada_ladrilho("amargo_po_noite" if float(ceu.get("escuro", 0.4)) > 0.3 else "amargo_po_dia", 0.42, 3.0, 0.3)
		# tempestade da borda: começa invisível e engrossa com o nível do Amargo
		var tp := ColorRect.new()
		tp.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tp.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/tempestade.gdshader"); sm.set_shader_parameter("forca", 0.0)
		tp.material = sm
		tp.visible = false
		clima.add_child(tp)
		camadas_clima.append(tp)
		tempestade = [tp]

var camadas_clima: Array = []
var tempestade: Array = []
var tempestade_alvo := 0.0
var t_geiger := 0.0

## Efeito ladrilhável cobrindo a tela (pó do Amargo, tempestade), com paralaxe leve pela câmera.
func _camada_ladrilho(nome: String, alfa: float, escala: float, paralaxe: float) -> Control:
	if not Defs.VFX.has(nome): return null
	var c := Control.new()
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	c.modulate = Color(1, 1, 1, alfa)
	c.set_meta("f", 0.0)
	var v: Dictionary = Defs.VFX[nome]
	c.set_meta("fps", float(v.get("fps", 12)))
	var tex := Tema.tex(v["sheet"])
	c.draw.connect(func():
		if c.modulate.a <= 0.01: return
		var f := int(c.get_meta("f")) % int(v["frames"])
		var fw := float(v["frame_w"]); var fh := float(v["frame_h"])
		var src := Rect2((f % int(v["cols"])) * fw + 1.0, (f / int(v["cols"])) * fh + 1.0, fw - 2.0, fh - 2.0)
		var sz := Vector2(fw, fh) * escala
		var off := Vector2(fposmod(cam.position.x * paralaxe, sz.x), fposmod(cam.position.y * paralaxe, sz.y))
		var x := -off.x
		while x < c.size.x:
			var y := -off.y
			while y < c.size.y:
				c.draw_texture_rect_region(tex, Rect2(Vector2(x, y), sz + Vector2(1, 1)), src)
				y += sz.y
			x += sz.x)
	clima.add_child(c)
	camadas_clima.append(c)
	return c

func _cores_minimapa() -> void:
	cores_piso.clear()
	for ch in mapa.get("pisos", {}):
		var p := "res://assets/ext/ambiente/pisos_mundo/%s.png" % mapa["pisos"][ch]
		if ResourceLoader.exists(p):
			var img: Image = (load(p) as Texture2D).get_image()
			if img.is_compressed(): img.decompress()
			img.resize(1, 1, Image.INTERPOLATE_BILINEAR)
			cores_piso[ch] = img.get_pixel(0, 0)

# =================================================================== entidades
class ObjView extends Node2D:
	var ent: Ent
	var spr: Sprite2D
	var marcador := false
	var t := 0.0
	var brilho := 0.0
	func _process(dt: float) -> void:
		t += dt
		if spr: spr.modulate = Color(1 + brilho * 0.35, 1 + brilho * 0.3, 1 + brilho * 0.2)
		queue_redraw()
	func _draw() -> void:
		if marcador and ent and not ent.aux.get("aberto", false):
			# objeto de missão sem arte própria: brilho pulsando no chão
			var a := 0.35 + 0.2 * sin(t * 3.0)
			for i in 3:
				var r := Iso.elipse(0.5 + i * 0.25)
				var pts := PackedVector2Array()
				for k in 25: pts.append(Vector2(cos(TAU * k / 24.0) * r.x, sin(TAU * k / 24.0) * r.y))
				draw_polyline(pts, Color(0.95, 0.8, 0.4, a * (1.0 - i * 0.3)), 1.5, true)
			draw_circle(Vector2(0, -6 - 4 * sin(t * 2.0)), 3.0, Color(1, 0.9, 0.6, a + 0.3))

func _surgiu(id: int) -> void:
	var e: Ent = sim.ents.get(id)
	if e == null: return
	if views.has(id) or objs.has(id): return
	if e.tipo == "objeto" and e.kind in ["bau", "interativo", "portal", "pilha_de_mortos", "cadaver_fresco"]:
		_criar_obj(e)
		return
	var v := Unidade.new()
	v.iniciar(self, e)
	mundo.add_child(v)
	views[id] = v
	if e.tipo == "chefe":
		chefe_view = v
		v.set_meta("luz", luz.adicionar(v.position, Color(1.0, 0.62, 0.38), 5.5, 1.1, true))
	if e.invisivel: v.visible = false
	if e.kind == "nao_julgado" and mapa.get("exterior", false):
		fx.folha("naojulgado_brilho_noite", v.position, {"segue": v, "dura": 99999.0, "aditivo": true})

func _criar_obj(e: Ent) -> void:
	var o := ObjView.new()
	o.ent = e
	o.position = Iso.to_screen(e.pos)
	var k := ""
	match e.kind:
		"bau": k = e.aux.get("visual", "bau_comum")
		"portal": k = "escada_descida"
		"pilha_de_mortos": k = "pilha_cranios"
		"cadaver_fresco": k = "ossos_espalhados"
		"interativo":
			# usa o prop do mapa naquela posição (poço, entrada da cripta...) ou um marcador
			var tem_prop := false
			for p in mapa.get("props", []):
				if p.get("obj", 0) == 1 and absf(p["x"] - e.pos.x) < 0.7 and absf(p["y"] - e.pos.y) < 0.7 and Defs.AMB.get("objetos", {}).has(p["k"]):
					tem_prop = true
			if e.aux.get("obj", "") == "cela_monge": tem_prop = true
			o.marcador = not tem_prop or e.aux.get("obj", "") in ["ninhos_corvo", "covas_abertas", "corpo_lacrado", "tumulo_cardo", "torre_sino"]
	if k != "":
		var s := _sprite_kit(k, Vector2.ZERO)
		if s != null:
			s.position = Vector2.ZERO
			if e.kind == "pilha_de_mortos": s.scale = Vector2(1.3, 1.3)
			o.add_child(s); o.spr = s
		else: o.marcador = true
	mundo.add_child(o)
	objs[e.id] = o
	_atualizar_visibilidade_obj(o)

func _atualizar_visibilidade_obj(o: ObjView) -> void:
	var e := o.ent
	var vis := true
	var cond: Dictionary = e.aux.get("visivel_se", {})
	if e.kind == "interativo": cond = Defs.OBJETOS.get(e.aux.get("obj", ""), {}).get("visivel_se", {})
	if not cond.is_empty(): vis = Missoes.cond(jog, cond, "")
	if e.aux.get("requer_chefe", "") != "" and _chefe_vivo(): vis = false
	o.visible = vis

func _sumiu(id: int) -> void:
	if views.has(id):
		var v = views[id]
		views.erase(id)
		if v.morto:
			var tw: Tween = v.create_tween()
			tw.tween_interval(maxf(0.0, 6.0 - v.morte_t))
			tw.tween_callback(v.queue_free)
		else: v.queue_free()
	if objs.has(id):
		objs[id].queue_free(); objs.erase(id)

# =================================================================== itens no chão
class ItemChao extends Node2D:
	var dados: Dictionary
	var nome := ""
	var cor := Color.WHITE
	var icone: Array = []
	var t := 0.0
	var origem := Vector2.ZERO
	var destino := Vector2.ZERO
	var voo := 0.0
	var hover := false
	var mostrar := false
	var ouro := false
	func _process(dt: float) -> void:
		t += dt
		if voo < 1.0:
			voo = minf(1.0, voo + dt * 2.2)
			var k := voo
			position = origem.lerp(destino, k) + Vector2(0, -sin(k * PI) * 60.0)
		queue_redraw()
	func _draw() -> void:
		draw_set_transform(Vector2(0, 0), 0.0, Vector2(1, 0.5))
		draw_circle(Vector2.ZERO, 12, Color(0, 0, 0, 0.35))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if ouro:
			for i in 5:
				var p := Vector2((i % 3) * 6 - 6, -2 - (i / 3) * 4 + (i % 2) * 2)
				draw_circle(p, 4.0, Color("#6b4a14")); draw_circle(p + Vector2(-0.5, -0.5), 3.2, Color("#e0b84a"))
		elif icone.size() == 2:
			var r: Rect2 = icone[1]
			var sz := Vector2(30, 30)
			draw_texture_rect_region(icone[0], Rect2(-sz * 0.5 + Vector2(0, -12), sz), r, Color(1, 1, 1) * (1.25 if hover else 1.0))
		else:
			draw_rect(Rect2(-8, -18, 16, 16), cor.darkened(0.3)); draw_rect(Rect2(-8, -18, 16, 16), cor, false, 1.5)

func _item_chao(id: int, de: Vector2, pos: Vector2) -> void:
	var c: Dictionary = sim.chao.get(id, {})
	if c.is_empty(): return
	var it: Dictionary = c["item"]
	var n := ItemChao.new()
	n.dados = c
	n.ouro = it["id"] == "_ouro"
	n.nome = ("%d de ouro" % int(it["qtd"])) if n.ouro else Itens.nome(it)
	if not n.ouro and int(it.get("qtd", 1)) > 1: n.nome += " (%d)" % int(it["qtd"])
	n.cor = Defs.cor_raridade(it.get("raridade", "comum")) if not n.ouro else Tema.COR_OURO
	n.icone = Tema.icone_item(it["id"]) if not n.ouro else []
	n.origem = Iso.to_screen(de); n.destino = Iso.to_screen(pos)
	n.position = n.origem
	mundo.add_child(n)
	itens_chao[id] = n
	var rar: String = it.get("raridade", "comum")
	if rar in ["raro", "excelente", "lendario", "conjunto"]:
		var nome := "item_feixe_lendario" if rar in ["lendario", "conjunto"] else "item_feixe_raro"
		var f = fx.folha(nome, n.destino, {"dura": 9999.0, "cor": n.cor.lightened(0.2)})
		if f: n.set_meta("feixe", f)
	audio.tocar("itens/drop_excelente" if rar in ["excelente", "lendario"] else ("itens/drop_metal" if not n.ouro else "itens/moedas"), n.destino, -4.0)

func _item_chao_sumiu(id: int) -> void:
	var n = itens_chao.get(id)
	itens_chao.erase(id)
	if n == null: return
	if n.has_meta("feixe"):
		var f = n.get_meta("feixe")
		if is_instance_valid(f): f.queue_free()
	n.queue_free()

# =================================================================== eventos do servidor
func _ev(tipo: String, d: Dictionary) -> void:
	match tipo:
		"surgiu": _surgiu(int(d["id"]))
		"sumiu": _sumiu(int(d["id"]))
		"ataque": _ataque(d)
		"dano": _dano(d)
		"cura":
			var v = views.get(int(d.get("id", -1)))
			if v and float(d.get("valor", 0)) >= 1.0 and not d.get("silencioso", false):
				fx.numero(v.position + Vector2(0, -v.altura_px), int(d["valor"]), "cura", v.id)
		"morreu": _morreu(d)
		"telegrafo":
			fx.telegrafo(d)
			audio.tocar("combate/telegrafo_inicio", Iso.to_screen(d["origem"]), -6.0)
		"telegrafo_fim":
			fx.telegrafo_fim(int(d["id"]))
			if d.get("impacto", false): audio.tocar("combate/telegrafo_impacto", null, -4.0); _tremer(3, 0.15)
		"telegrafo_anel": fx.telegrafo_anel(int(d["id"]))
		"projetil": fx.projetil(d)
		"projetil_fim": fx.projetil_fim(int(d["id"]), d.get("pos", Vector2.ZERO))
		"area": fx.area(d)
		"area_fim": fx.area_fim(int(d["id"]))
		"desloca":
			var v = views.get(int(d["id"]))
			if v:
				if d.get("anim", "") != "": v.tocar(d["anim"], float(d.get("dur", 0.3)))
				elif d.get("tipo", "") == "investida" and v._sheet("charge").size() > 0: v.tocar("charge", float(d.get("dur", 0.35)))
				if d.get("tipo", "") in ["rolamento", "arrancada", "asas_ascensao", "passo_sombrio", "investida_bestial"]:
					fx.folha("esquiva_poeira", Iso.to_screen(d["de"]))
		"recuo":
			var v = views.get(int(d["id"]))
			if v and not v.morto and v.anim_unica == "": v.tocar("hit")
		"vfx": _vfx(d)
		"raio":
			var de = d.get("de"); var para = d.get("para")
			var a: Vector2 = (views[de].position + Vector2(0, -60)) if de is int and views.has(de) else Iso.to_screen(de if de is Vector2 else Vector2.ZERO)
			var b: Vector2 = (views[para].position + Vector2(0, -50)) if para is int and views.has(para) else Iso.to_screen(para if para is Vector2 else Vector2.ZERO)
			fx.raio(a, b, Defs.cor(d.get("cor", "#8ad8ff")), d.get("coluna", false))
		"chao_novo": _item_chao(int(d["id"]), d.get("de", d["pos"]), d["pos"])
		"chao_sumiu":
			_item_chao_sumiu(int(d["id"]))
			if d.get("pego", false) and int(d.get("por", jog.id)) == jog.id: audio.tocar("ui/pegar_item", null, -4.0)
		"status": _status(d)
		"alerta":
			var v = views.get(int(d["id"]))
			if v:
				v.visible = true
				var e: Ent = sim.ents.get(v.id)
				if e: audio.tocar(_som_mob(e.kind, "alerta"), v.position, -6.0)
				if e and e.aux.get("alfa", false):
					v.tocar("howl", 1.0); audio.tocar("monstros/cao_uivo", v.position, -4.0)
		"some":
			var v = views.get(int(d["id"]))
			if v: v.visible = false
		"anim":
			var v = views.get(int(d["id"]))
			if v: v.tocar(d["anim"], float(d.get("dur", 0.5)))
		"visual":
			var v = views.get(int(d["id"]))
			if v: v.trocar_visual(d["kind"])
		"fala":
			var v = views.get(int(d["id"]))
			if v: fx.fala(v, d.get("texto", ""), Defs.cor(d.get("cor", "#f0e2c0")))
		"chefe_fala":
			var v = views.get(int(d["id"]))
			if v and d.get("texto", "") != "": fx.fala(v, d["texto"], Color("#ffcf9a"), 4.0)
		"chefe": _chefe(d)
		"chefe_derrotado":
			audio.tocar("musica/vinheta/vitoria_chefe")
			for o in objs.values(): _atualizar_visibilidade_obj(o)
		"chefe_buff":
			var v = views.get(int(d["id"]))
			if v: fx.texto_flutuante(v.position + Vector2(0, -v.altura_px - 20), "FOME SACIADA x%d" % int(d.get("fome", 1)), Color("#ff7a3a"), 16)
		"porta": _porta(d)
		"teleporte":
			var v = views.get(int(d["id"]))
			if v:
				v.pos_vis = Iso.to_screen(d["pos"])
				if not d.get("sem_fx", false): fx.folha("chefe_portal", v.pos_vis)
		"levita":
			var v = views.get(int(d["id"]))
			if v: v.levita = d.get("on", false)
		"escudo":
			var v = views.get(int(d["id"]))
			if v: fx.folha("chefe_escudo", v.position, {"segue": v, "dura": 1.2})
		"corista":
			var v = views.get(int(d["id"]))
			if v:
				v.mat.set_shader_parameter("tinta", Color(1.4, 1.3, 0.9) if d.get("canta", false) else Defs.sprite("corista")["tint"])
				if d.get("canta", false): audio.tocar("monstros/carpideira_canto", v.position, -4.0)
		"escuridao":
			var tw := create_tween()
			var c: Color = luz.ambiente
			tw.tween_method(func(k): luz.definir_ambiente(c.lerp(Color(0.05, 0.05, 0.07), k)), 0.0, 1.0, 1.5)
		"luzes_arena": _luzes_arena(d)
		"anel_fogo": hud.aviso("O fogo sagrado fecha a arena!")
		"nota":
			_tremer(8, 0.6)
			fx.folha("chefe_onda_choque", Iso.to_screen(d["pos"]), {"escala": 4.0})
		"canal":
			hud.canal(d)
			var vc = views.get(int(d.get("id", -1)))
			if vc and vc != views.get(jog.id) and str(d.get("texto", "")).begins_with("Devor"): vc.anim_base = "eat"
		"canal_fim":
			hud.canal_fim(d)
			var vf = views.get(int(d.get("id", -1)))
			if vf: vf.anim_base = ""
		"zona": _zona(d)
		"mapa": pass
		"amargo":
			var n := int(d.get("nivel", 0))
			tempestade_alvo = clampf((n - 3) / 6.0, 0.0, 1.0) if n >= 4 else 0.0
			if n == 7: hud.aviso("O Amargo queima a pele. Volte!", Color("#b8ff6a"))
			elif n == 4: hud.aviso("O contador começa a estalar.", Color("#d8f0a0"))
		"trocar_mapa":
			if not trocando:
				trocando = true
				call_deferred("_trocar_mapa", d["mapa"], d.get("pos", Vector2(-1, -1)))
		"jogador_morreu":
			audio.evento("jogador_morre")
			hud.morte(d)
		"reviveu":
			var vr = views.get(int(d["id"]))
			var er: Ent = sim.ents.get(int(d["id"]))
			if vr and er: vr.morto = false; vr.modulate.a = 1.0; vr.anim_unica = ""; vr.mat.set_shader_parameter("dissolve", 0.0); vr.pos_vis = Iso.to_screen(er.pos)
			if int(d["id"]) == jog.id:
				hud.reviveu()
				audio.tocar("ui/ressuscitar")
		"nivel":
			var v = views.get(int(d.get("id", jog.id)))
			if v: fx.folha("level_up", v.position, {"segue": v})
			if int(d.get("id", jog.id)) == jog.id:
				audio.evento("nivel_sobe")
				hud.nivel(d)
				_salvar()
		"xp": hud.xp(d)
		"skill": hud.skill_usada(d)
		"item_ganho": hud.item_ganho(d)
		"ouro": hud.log_msg("+%d de ouro" % int(d["valor"]), Tema.COR_OURO)
		"aviso": hud.aviso(d.get("texto", ""))
		"log": hud.log_msg(d.get("texto", ""))
		"texto": janelas.texto(d.get("titulo", ""), d.get("texto", ""))
		"dialogo": janelas.dialogo(d)
		"dialogo_fim": janelas.fechar("dialogo")
		"missao":
			hud.missao(d)
			for o in objs.values(): _atualizar_visibilidade_obj(o)
			audio.tocar({"aceita": "ui/missao_aceita", "concluida": "ui/missao_concluida"}.get(d.get("estado", ""), "ui/missao_atualizada"))
			_salvar()
		"servico": janelas.servico(d)
		"inventario", "stats", "buff", "refino":
			janelas.atualizar()
			hud.atualizar_cinto()
			if tipo == "refino":
				hud.aviso(("Refino deu certo: " if d.get("ok", false) else "O refino falhou: ") + d.get("nome", ""))
				audio.tocar("itens/refino_sucesso" if d.get("ok", false) else "itens/refino_falha")
		"bau":
			var o = objs.get(int(d["id"]))
			if o and o.spr:
				var k: String = o.ent.aux.get("visual", "bau_comum") + "_aberto"
				var tex := Tema.tex("res://assets/ext/ambiente/objetos/%s.png" % k)
				if tex: o.spr.texture = tex
				fx.folha("bau_abertura", o.position)
			audio.tocar({"caixote_podre": "itens/bau_madeira", "bau_de_ferro": "itens/bau_ferro"}.get(d.get("tipo", ""), "itens/bau_reliquia"), null)
		"som_evento": _som_evento(d)

func _trocar_mapa(id_mapa: String, pos: Vector2) -> void:
	var tw := create_tween()
	tw.tween_property(cortina, "modulate:a", 1.0, 0.45)
	await tw.finished
	if id_mapa != "area_inicial": audio.tocar("musica/vinheta/entrar_cripta")
	_entrar(id_mapa, pos)
	trocando = false
	_salvar()

func _ataque(d: Dictionary) -> void:
	var v = views.get(int(d["id"]))
	if v == null: return
	var e: Ent = sim.ents.get(v.id)
	var nome := "attack"
	if d.get("anim", "") != "": nome = d["anim"]
	elif e != null and e.tipo == "chefe" and e.kind == "general_partido":
		nome = {"arrasto": "lunge", "vomito_de_brasa": "vomit", "banquete": "feast", "golpe_estandarte": "attack", "varredura": "sweep", "ordem_de_levantar": "roar"}.get(d.get("nome", ""), "sweep" if d.get("nome", "").contains("varre") else "attack")
	elif e != null and e.kind == "capataz_gancho" and d.get("nome", "") != "": nome = "hook" if d["nome"].contains("gancho") else ("spin" if d["nome"].contains("gir") else "attack")
	elif e != null and e.kind == "cao_de_vala" and d.get("nome", "") == "bote": nome = "leap"
	elif e != null and e.kind == "porco_pestilento" and d.get("nome", "") == "investida": nome = "scrape"   # cava o chão enquanto o telegrafo enche
	elif e != null and e.kind == "filho_de_cardo" and d.get("nome", "") == "brotar": nome = "burrow"
	elif e != null and e.tipo == "jogador" and d.get("skill", "") != "": nome = "attack"
	if nome == "scrape" and v._sheet("scrape").size() > 0:
		v.tocar("scrape", maxf(0.25, float(d.get("preparo", 0.9))))
	elif nome == "burrow" and d.get("nome", "") == "enterrar":
		v.tocar("burrow", 1.05)
	elif nome == "burrow" and d.get("nome", "") == "brotar":
		v.tocar("burrow", maxf(0.25, float(d.get("preparo", 1.0))) * 0.5)
		get_tree().create_timer(maxf(0.25, float(d.get("preparo", 1.0)))).timeout.connect(func():
			if is_instance_valid(v) and not v.morto: v.tocar("emerge", 0.6))
	else:
		v.tocar(nome, maxf(0.25, float(d.get("dur", 0.5))))
	var alvo: Ent = sim.ents.get(int(d.get("alvo", -1)))
	if alvo != null and e != null:
		var dir := Iso.to_screen(alvo.pos - e.pos).normalized()
		v.avanco = dir * 4.0
	if e != null and e.tipo == "monstro": audio.tocar(_som_mob(e.kind, "ataque"), v.position, -5.0)
	if e != null and e.tipo == "jogador" and nome == "attack" and d.get("skill", "") == "":
		audio.tocar("combate/ar_pesado" if e.classe in ["mutante", "humano"] else "combate/ar_lamina", null, -6.0)
	if e != null and e.tipo == "jogador" and nome == "shoot": audio.tocar("combate/tiro_escopeta", null, -3.0)

func _som_mob(kind: String, acao: String) -> String:
	var base: String = {"carnical": "carnical", "carnical_inchado": "carnical", "nao_julgado": "nao_julgado", "cao_de_vala": "cao",
		"corvo_de_cinza": "corvo", "acougueiro_oco": "acougueiro", "capataz_gancho": "capataz", "soldado_caido": "soldado",
		"porco_pestilento": "porco", "gancheiro": "gancheiro", "larva_de_carne": "larva", "monge_emparedado": "monge",
		"carpideira_de_ossos": "carpideira", "fogo_de_vela": "fogo_vela", "querubim_desfeito": "querubim", "eco_da_trombeta": "eco"}.get(kind, "")
	if base == "": return ""
	var cands := ["monstros/%s_%s" % [base, acao]]
	if acao == "ataque": cands += ["monstros/%s_mordida" % base, "monstros/%s_cutelo" % base, "monstros/%s_gancho" % base, "monstros/%s_chicote" % base, "monstros/%s_cuspe" % base]
	if acao == "alerta": cands += ["monstros/%s_grito" % base, "monstros/%s_rosnado" % base, "monstros/%s_grasnado" % base, "monstros/%s_gemido" % base, "monstros/%s_grunhido" % base]
	for c in cands:
		if audio.sons.has(c): return c
	return ""

func _dano(d: Dictionary) -> void:
	var v = views.get(int(d["id"]))
	var estilo: String = d.get("estilo", "normal")
	if estilo == "nada": return
	var pos: Vector2
	if v != null: pos = v.position + Vector2(0, -v.altura_px)
	elif objs.has(int(d["id"])): pos = objs[int(d["id"])].position + Vector2(0, -50)
	else: return
	var alvo: Ent = sim.ents.get(int(d["id"]))
	var eh_jog := alvo != null and alvo.tipo == "jogador"
	var valor := int(d.get("valor", 0))
	var est := estilo
	if eh_jog and estilo in ["normal", "critico", "excelente", "excelente_critico"]: est = "jogador_recebe"
	if valor > 0 or estilo in ["errou", "esquivou", "imune", "postura_quebrada"]:
		fx.numero(pos, valor, est, int(d["id"]))
	if valor <= 0:
		if estilo == "postura_quebrada":
			fx.folha("faiscas_bloqueio", pos + Vector2(0, 20)); audio.evento("postura_quebrada", pos)
		elif estilo in ["errou", "esquivou"]: audio.evento(estilo, pos)
		return
	var sens: Dictionary = Defs.SENS.get("perfis", {}).get(d.get("sens", "golpe_leve"), Defs.SENS.get("perfis", {}).get("golpe_leve", {}))
	var hs := float(sens.get("hitstop_ms", 40))
	if estilo.contains("critico"): hs += 40.0
	if v != null:
		v.piscar(float(sens.get("flash_ms", 60)))
		v.congelar(minf(hs, 160.0))
	var atk = views.get(int(d.get("de", -1)))
	if atk != null and not eh_jog: atk.congelar(minf(hs, 160.0) * 0.7)
	var tr = sens.get("tremor")
	if tr is Dictionary and (eh_jog or int(d.get("de", -1)) == jog.id): _tremer(float(tr["px"]), float(tr["ms"]) / 1000.0)
	if estilo.contains("critico"): fx.folha("golpe_critico", pos + Vector2(0, 30)); _tremer(3, 0.12)
	elif d.get("sens", "") in ["golpe_pesado", "investida", "area"]: fx.folha("golpe_impacto", pos + Vector2(0, 30))
	elif d.get("sens", "") in ["golpe_leve", "combo"]: fx.folha("golpe_corte", pos + Vector2(0, 30), {"rot": randf_range(-0.6, 0.6)})
	if alvo != null and alvo.tipo != "objeto" and not "espectro" in alvo.tags and not "mecanico" in alvo.tags and randf() < 0.6:
		fx.folha("sangue_jorro", pos + Vector2(0, 26), {"escala": 0.8})
	# som
	if eh_jog: audio.evento("jogador_ferido", pos)
	elif estilo.contains("excelente"): audio.evento("golpe_excelente", pos)
	elif estilo.contains("critico"): audio.evento("golpe_critico", pos)
	elif d.get("sens", "") in ["golpe_pesado", "investida", "tiro_pesado", "area"]: audio.evento("golpe_pesado", pos)
	else: audio.evento("golpe_leve", pos)
	if alvo != null and alvo.kind == "pilha_de_mortos": audio.tocar("chefes/pilha_mortos_dano", pos)

func _morreu(d: Dictionary) -> void:
	var v = views.get(int(d["id"]))
	if v == null:
		if objs.has(int(d["id"])):
			var o = objs[int(d["id"])]
			fx.folha("morte_monstro", o.position)
			audio.tocar("chefes/pilha_mortos_destruida", o.position)
		return
	v.morrer()
	var e: Ent = sim.ents.get(v.id)
	fx.folha("sangue_poca", v.position, {"dura": 7.0})
	if v.anim_unica == "_sem_morte": fx.folha("morte_monstro", v.position)
	if d.get("chefe", false):
		audio.evento("abate_chefe"); _tremer(8, 0.6)
		fx.folha("chefe_morte", v.position, {"escala": 1.5})
	elif e != null and e.tipo == "monstro":
		audio.evento("abate", v.position)
		var s := _som_mob(e.kind, "morte")
		if s != "": audio.tocar(s, v.position, -3.0)
		if int(d.get("de", -1)) == jog.id: _tremer(2, 0.12)

func _status(d: Dictionary) -> void:
	var v = views.get(int(d["id"]))
	if v == null: return
	var s: String = d.get("s", "")
	if d.get("on", true):
		var nome: String = {"atordoado": "status_atordoado", "lento": "status_lentidao", "queimadura": "status_queimando", "sangramento": "status_sangramento", "veneno": "status_veneno"}.get(s, "")
		if nome != "": fx.folha(nome, v.position, {"segue": v, "dura": clampf(float(d.get("t", 2.0)), 0.5, 6.0), "escala": 0.9})
		if audio.sons.has("status/" + s): audio.tocar("status/" + s, v.position, -6.0)
		if int(d["id"]) == jog.id: hud.status(d)
	elif int(d["id"]) == jog.id: hud.status(d)

func _vfx(d: Dictionary) -> void:
	var pos := Vector2.ZERO
	var alvo = views.get(int(d.get("alvo", -1))) if d.get("alvo") is int else null
	var de = views.get(int(d.get("de", -1))) if d.get("de") is int else null
	if d.has("pos"): pos = Iso.to_screen(d["pos"])
	elif alvo != null: pos = alvo.position
	elif de != null: pos = de.position
	if d.has("nome"):
		var opc := {}
		if d.has("fica"): opc["dura"] = float(d["fica"])
		if d["nome"] in ["disparo_cano", "fumaca_tiro"] and de != null:
			pos = de.position + Vector2(0, -56)
			if alvo != null: opc["rot"] = (alvo.position - de.position).angle()
		fx.folha(d["nome"], pos + (Vector2(0, -40) if d["nome"] in ["golpe_corte", "golpe_impacto"] else Vector2.ZERO), opc)
		return
	if d.has("skill"):
		var nomes: Array = fx.nome_skill(d["skill"])
		var classe: String = d["skill"].split("/")[0]
		var sid: String = d["skill"].split("/")[1] if d["skill"].contains("/") else ""
		var som := classe + "_" + sid
		if audio.sons.has("skills/" + som): audio.tocar("skills/" + som, pos)
		if nomes.is_empty(): return
		var opc := {}
		if d.has("fica"): opc["dura"] = float(d["fica"])
		var segue_alvo: bool = d.has("alvo") and alvo != null
		for n in nomes:
			if n.ends_with("_projetil"): continue
			if n.ends_with("_impacto") and not segue_alvo: continue
			var p := pos
			var o2 := opc.duplicate()
			if n.contains("aura") or (de != null and not segue_alvo and not d.has("pos")):
				o2["segue"] = de
			fx.folha(n, p, o2)

func _chefe(d: Dictionary) -> void:
	hud.chefe(d)
	if d.get("inicio", false):
		var e: Ent = sim.ents.get(int(d["id"]))
		var m := {"general_partido": "musica/chefe_andras", "irma_celeste": "musica/chefe_celeste", "zacarias_arauto": "musica/chefe_zacarias"}
		if e: audio.musica(m.get(e.kind, "musica/combate")); musica_chefe = true
		_tremer(4, 0.4)
	if d.has("fase") and not d.get("inicio", false):
		var e2: Ent = sim.ents.get(int(d["id"]))
		var nome_som := {"general_partido": "chefes/andras_fase", "zacarias_arauto": "chefes/zacarias_fase"}
		audio.evento("chefe_fase:{n}")
		if e2 and nome_som.has(e2.kind): audio.tocar(nome_som[e2.kind])
		var v = views.get(int(d["id"]))
		if v: fx.folha("chefe_furia", v.position, {"segue": v}); v.tocar("roar")
		_tremer(6, 0.5)
	if d.get("fim", false):
		musica_chefe = false
		zona_atual = ""
		_zona({"id": jog.zona, "primeira": false})

func _porta(d: Dictionary) -> void:
	var fechada: bool = d.get("fechada", false)
	if not has_meta("portoes"): set_meta("portoes", [])
	for s in get_meta("portoes"):
		if is_instance_valid(s): s.queue_free()
	set_meta("portoes", [])
	if not fechada:
		audio.tocar("itens/porta_ferro")
		return
	audio.tocar("itens/porta_ferro")
	# grade de ferro sobre cada grupo de células da porta
	var cel: Array = d.get("celulas", [])
	var feitos: Array = []
	for c in cel:
		var p := Vector2(c[0] + 0.5, c[1] + 0.5)
		if feitos.any(func(q): return q.distance_to(p) < 2.2): continue
		feitos.append(p)
		var s := _sprite_kit("portao_ferro", p)
		if s:
			mundo.add_child(s)
			get_meta("portoes").append(s)
			s.modulate = Color(1, 0.7, 0.6)
		var l = luz.adicionar(Iso.to_screen(p), Color(1, 0.3, 0.15), 2.0, 1.0, true)
		get_meta("portoes").append(l)

func _luzes_arena(d: Dictionary) -> void:
	if has_meta("luzes_arena"):
		for l in get_meta("luzes_arena"):
			if is_instance_valid(l): l.queue_free()
	var ls: Array = []
	for p in d.get("pos", []):
		ls.append(luz.adicionar(Iso.to_screen(p), Color(1.0, 0.85, 0.55), float(d.get("raio", 2.0)) * 1.3, 1.4, true))
		var f = fx.folha("vela_ar_limpo_chao", Iso.to_screen(p), {"dura": 20.0, "escala": float(d.get("raio", 2.0)) / 1.5})
		if f: ls.append(f)
	set_meta("luzes_arena", ls)

func _zona(d: Dictionary) -> void:
	var zid: String = d.get("id", "")
	if zid == zona_atual or zid == "": return
	zona_atual = zid
	var z: Dictionary = {}
	for zz in mapa.get("zonas", []):
		if zz["id"] == zid: z = zz
	hud.zona(z, d.get("primeira", false))
	if not musica_chefe:
		var mus: String = z.get("musica", "") if z.get("musica") != null else ""
		if mus == "" or not audio.sons.has(mus): mus = "musica/sao_lazaro" if mapa.get("exterior", false) else "musica/cripta"
		audio.musica(mus)
	var amb: String = z.get("ambiente", "") if z.get("ambiente") != null else ""
	if amb == "" or not audio.sons.has(amb): amb = "ambiente/noite_vento" if mapa.get("exterior", false) else "ambiente/cripta_porao"
	audio.ambiente(amb)
	if d.get("primeira", false) and z.get("nome", "") != "": audio.tocar("musica/vinheta/descoberta_area", null, -6.0)

func _som_evento(d: Dictionary) -> void:
	var ev: String = d.get("ev", "")
	if ev == "uivo" and views.has(int(d.get("id", -1))): views[int(d["id"])].tocar("howl", 1.0)
	var m := {"chave": "itens/chave_usar", "comprar": "ui/comprar", "vender": "ui/vender", "equipar_arma": "itens/equipar_arma",
		"erro": "ui/erro", "escudo_quebra": "combate/escudo_quebra", "general_come": "chefes/andras_devorar_cadaver", "moedas": "itens/moedas",
		"pocao": "itens/pocao_beber", "postura_quebrada": "combate/postura_quebrada", "refino_sucesso": "itens/refino_sucesso",
		"sem_recurso": "ui/sem_recurso", "soltar": "ui/soltar_item", "telegrafo_inicio": "combate/telegrafo_inicio", "uivo": "monstros/cao_uivo",
		"zacarias_a_nota": "chefes/zacarias_a_nota", "zacarias_nota_interrompida": "chefes/zacarias_nota_interrompida",
		"celeste_candelabro_apaga": "chefes/celeste_candelabro_apaga", "pegar": "ui/pegar_item", "chefe_fase": "combate/chefe_fase"}
	if m.has(ev): audio.tocar(m[ev])

func _tremer(px: float, dur: float) -> void:
	tremor_px = minf(8.0, maxf(tremor_px, px) * hud.mult_tremor)
	tremor = maxf(tremor, dur)

# =================================================================== entrada
func mouse_mundo() -> Vector2:
	return Iso.to_world(get_global_mouse_position())

func _sob_mouse() -> void:
	var m := get_global_mouse_position()
	var melhor := -1
	var md := 1e9
	for id in views.keys():
		var v = views[id]
		var e: Ent = sim.ents.get(id)
		if e == null or not e.vivo or not v.visible or e.tipo == "jogador": continue
		if e.tipo == "objeto" and not e.alvejavel: continue
		var larg: float = maxf(30.0 * v.escala_base * e.escala, 28.0)
		var alt: float = maxf(v.altura_px * e.escala, 80.0)
		var r := Rect2(v.position.x - larg - 24, v.position.y - alt - 30, (larg + 24) * 2, alt + 50)
		if r.has_point(m):
			var dd := absf(m.x - v.position.x) + absf(m.y - (v.position.y - alt * 0.5)) * 0.5
			if e.tipo == "monstro" or e.tipo == "chefe": dd -= 20
			if dd < md: md = dd; melhor = id
	for id in objs.keys():
		var o = objs[id]
		if not o.visible or o.ent == null: continue
		if o.ent.kind in ["pilha_de_mortos"] and o.ent.vivo:
			if Rect2(o.position.x - 50, o.position.y - 60, 100, 75).has_point(m):
				var dd2 := m.distance_to(o.position + Vector2(0, -25))
				if dd2 < md: md = dd2; melhor = id
			continue
		if o.ent.kind == "cadaver_fresco": continue
		if Rect2(o.position.x - 40, o.position.y - 70, 80, 85).has_point(m):
			var dd3 := m.distance_to(o.position + Vector2(0, -25)) + 10
			if dd3 < md: md = dd3; melhor = id
	if hover_id != melhor:
		if objs.has(hover_id) and is_instance_valid(objs[hover_id]): objs[hover_id].brilho = 0.0
		if views.has(hover_id) and is_instance_valid(views[hover_id]): views[hover_id].hover = false
		hover_id = melhor
		if objs.has(hover_id): objs[hover_id].brilho = 1.0
		if views.has(hover_id):
			var ev2: Ent = sim.ents.get(hover_id)
			views[hover_id].hover = true
			views[hover_id].cor_anel = Color(1.0, 0.22, 0.12, 0.95) if ev2 != null and jog.eh_inimigo_de(ev2) else Color(1.0, 0.86, 0.5, 0.9)
			if ev2 != null and ev2.aux.get("neutro", false) and ev2.estado in ["ocioso", "vagar"]: views[hover_id].cor_anel = Color(1.0, 0.85, 0.2, 0.95)
	hover_chao = -1
	var mc := 26.0
	for id in itens_chao.keys():
		var n = itens_chao[id]
		var dd := m.distance_to(n.position + Vector2(0, -8))
		if dd < mc: mc = dd; hover_chao = id
		n.hover = false
	if hover_chao != -1: itens_chao[hover_chao].hover = true

func _unhandled_input(ev: InputEvent) -> void:
	if trocando or not jog.vivo: return
	if janelas.mao_ativa() and ev is InputEventMouseButton and ev.pressed:
		janelas.soltar_no_mundo(); return
	if ev is InputEventMouseButton:
		if ev.button_index == MOUSE_BUTTON_LEFT:
			if ev.pressed:
				_clique(ev.shift_pressed)
				segurando = true; t_seguro = 0.0
			else: segurando = false
		elif ev.button_index == MOUSE_BUTTON_WHEEL_UP and ev.pressed: cam.zoom = (cam.zoom * 1.08).clamp(Vector2(0.8, 0.8), Vector2(1.6, 1.6))
		elif ev.button_index == MOUSE_BUTTON_WHEEL_DOWN and ev.pressed: cam.zoom = (cam.zoom / 1.08).clamp(Vector2(0.8, 0.8), Vector2(1.6, 1.6))
		elif ev.button_index == MOUSE_BUTTON_RIGHT and ev.pressed: usar_skill(0)
	elif ev is InputEventKey and ev.pressed and not ev.echo:
		match ev.keycode:
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9: usar_skill(ev.keycode - KEY_1)
			KEY_Q: cmd("pocao", ["vida"])
			KEY_W: cmd("pocao", ["recurso"])
			KEY_E: cmd("pocao", ["antidoto"])
			KEY_R: usar_vela()
			KEY_Z: cmd("auto", [not jog.aux.get("auto", false)])
			KEY_I, KEY_B: janelas.alternar("inventario")
			KEY_C: janelas.alternar("personagem")
			KEY_J, KEY_L: janelas.alternar("missoes")
			KEY_K: janelas.alternar("habilidades")
			KEY_M, KEY_TAB: hud.alternar_mapa()
			KEY_H, KEY_F1: hud.alternar_ajuda()
			KEY_ESCAPE:
				if not janelas.fechar_tudo(): janelas.alternar("menu")
			KEY_ALT: mostrar_nomes = true
	elif ev is InputEventKey and not ev.pressed and ev.keycode == KEY_ALT:
		mostrar_nomes = false

func usar_vela() -> void:
	for it in jog.inv:
		if it["id"] == "vela_retorno":
			cmd("usar_item", [int(it["uid"])]); return
	hud.aviso("Sem Vela de Retorno na mochila.")

func usar_skill(slot: int) -> void:
	var alvo := hover_id
	if alvo == -1 or not sim.ents.has(alvo) or not jog.eh_inimigo_de(sim.ents[alvo]): alvo = jog.alvo
	if sim.valido(alvo) == null:   # sem alvo: o inimigo mais perto do cursor, ou o mais perto do jogador
		var p := _inimigo_perto_do_mouse(2.5)
		if p == null:
			var md := 7.0
			for e: Ent in sim.ents.values():
				if e.vivo and e.alvejavel and not e.invisivel and jog.eh_inimigo_de(e) and e.pos.distance_to(jog.pos) < md:
					md = e.pos.distance_to(jog.pos); p = e
		if p != null: alvo = p.id
	cmd("skill", [slot, alvo, mouse_mundo()])

func _clique(shift: bool) -> void:
	_sob_mouse()
	if hover_chao != -1:
		cmd("pegar", [hover_chao]); return
	if hover_id != -1:
		var e: Ent = sim.ents.get(hover_id)
		if e != null:
			if jog.eh_inimigo_de(e) and e.alvejavel:
				cmd("atacar", [hover_id, shift])
				return
			if e.tipo in ["npc", "objeto"]:
				cmd("interagir", [hover_id])
				audio.tocar("ui/clique", null, -8.0)
				return
	var perto := _inimigo_perto_do_mouse(1.1)
	if perto != null:
		cmd("atacar", [perto.id, shift])
		return
	if shift:
		cmd("virar", [mouse_mundo() - jog.pos])
		return
	cmd("no_lugar", [false])
	cmd("mover", [mouse_mundo()])
	_marcador_clique(get_global_mouse_position())

func _inimigo_perto_do_mouse(raio: float) -> Ent:
	var mm := mouse_mundo()
	var melhor: Ent = null
	var md := raio
	for e: Ent in sim.ents.values():
		if not e.vivo or not e.alvejavel or e.invisivel or not jog.eh_inimigo_de(e): continue
		var d := e.pos.distance_to(mm) - e.raio
		if d < md: md = d; melhor = e
	return melhor

func _marcador_clique(p: Vector2) -> void:
	var n := Node2D.new()
	n.position = p
	n.z_index = -6
	var k := [0.0]
	n.draw.connect(func():
		var a: float = 1.0 - k[0]
		var r := Iso.elipse(0.25 + k[0] * 0.35)
		var pts := PackedVector2Array()
		for i in 25: pts.append(Vector2(cos(TAU * i / 24.0) * r.x, sin(TAU * i / 24.0) * r.y))
		n.draw_polyline(pts, Color(0.9, 0.85, 0.6, a * 0.8), 1.5, true))
	fx.add_child(n)
	var tw := n.create_tween()
	tw.tween_method(func(x): k[0] = x; n.queue_redraw(), 0.0, 1.0, 0.35)
	tw.tween_callback(n.queue_free)

# =================================================================== laço
func _process(dt: float) -> void:
	t += dt
	if rede == null and not trocando and not janelas.aberta("menu"):   # Esc pausa o mundo (só no solo)
		acc += minf(dt, 0.1)
		while acc >= WorldSim.TICK:
			acc -= WorldSim.TICK
			sim.passo(WorldSim.TICK)
	_sob_mouse()
	# segurar o botão: segue o mouse (ou continua batendo no alvo)
	if segurando and jog.vivo and not trocando:
		t_seguro += dt
		if t_seguro > 0.18 and jog.alvo == -1 and not jog.aux.has("interagir") and not jog.aux.has("pegar"):
			if Input.is_key_pressed(KEY_SHIFT): pass
			elif fmod(t_seguro, 0.12) < dt: cmd("mover", [mouse_mundo()])
	# câmera
	var vj = views.get(jog.id)
	if vj != null:
		var alvo_cam: Vector2 = vj.pos_vis
		cam.position = cam.position.lerp(alvo_cam, 1.0 - exp(-dt * 10.0))
		if luz_jogador and is_instance_valid(luz_jogador): luz_jogador.position = vj.pos_vis
		audio.ouvinte = vj.pos_vis
	if tremor > 0.0:
		tremor -= dt
		cam.offset = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * tremor_px
		if tremor <= 0.0: cam.offset = Vector2.ZERO; tremor_px = 0.0
	fx.atualizar_luzes_projeteis()
	if chefe_view != null and is_instance_valid(chefe_view) and chefe_view.has_meta("luz"):
		var lc = chefe_view.get_meta("luz")
		if is_instance_valid(lc): lc.position = chefe_view.position
	_fade_props(vj)
	for c in camadas_clima:
		if not is_instance_valid(c) or not c.has_meta("f"): continue
		c.set_meta("f", float(c.get_meta("f")) + dt * float(c.get_meta("fps")))
		c.queue_redraw()
	if not tempestade.is_empty():
		var tp: ColorRect = tempestade[0]
		var sm: ShaderMaterial = tp.material
		var fz := lerpf(float(sm.get_shader_parameter("forca")), tempestade_alvo, 1.0 - exp(-dt * 2.0))
		sm.set_shader_parameter("forca", fz)
		sm.set_shader_parameter("cam", cam.position)
		tp.visible = fz > 0.01
		if tempestade_alvo > 0.05:
			t_geiger -= dt
			if t_geiger <= 0.0:
				t_geiger = randf_range(0.15, 0.6) / (0.4 + tempestade_alvo)
				audio.tocar("ambiente/pontual/geiger_pico", null, -14.0 + tempestade_alvo * 8.0, 0.15)
	sobre.queue_redraw()
	t_salvar += dt
	if t_salvar > 30.0: _salvar()

func _fade_props(vj) -> void:
	if vj == null: return
	var p: Vector2 = vj.pos_vis + Vector2(0, -50)
	for pr in props_altos:
		var s: Sprite2D = pr[0]
		if not is_instance_valid(s): continue
		var r: Rect2 = pr[1]
		var alvo := 1.0
		if r.has_point(p) and s.position.y > vj.pos_vis.y: alvo = 0.4
		s.modulate.a = lerpf(s.modulate.a, alvo, 0.15)
	# silhueta: se algum pixel de cenário na frente cobre o corpo, desenha o jogador por cima (Diablo / Dark Eden)
	var escondido: bool = not vj.morto and _coberto(vj.pos_vis, vj.altura_px)
	silhueta_a = lerpf(silhueta_a, 1.0 if escondido else 0.0, 0.25)
	silhueta.visible = silhueta_a > 0.03
	if silhueta.visible:
		var c: Sprite2D = vj.corpo
		silhueta.texture = c.texture
		silhueta.region_rect = c.region_rect
		silhueta.global_transform = c.global_transform
		silhueta.modulate.a = silhueta_a

## Algum pixel de cenário na frente cobre um corpo de altura alt com os pés em pe (tela)?
func _coberto(pe: Vector2, alt: float) -> bool:
	var pts := [pe + Vector2(0, -alt * 0.2), pe + Vector2(0, -alt * 0.5), pe + Vector2(0, -alt * 0.8),
		pe + Vector2(-alt * 0.15, -alt * 0.5), pe + Vector2(alt * 0.15, -alt * 0.5)]
	var caixa := Rect2(pe - Vector2(alt * 0.2, alt), Vector2(alt * 0.4, alt))
	for oc in oclusores:
		var s2: Sprite2D = oc[0]
		if s2.position.y <= pe.y + 1.0: continue
		var r2: Rect2 = oc[1]
		if not r2.intersects(caixa): continue
		var bm: BitMap = _mascara(oc[2], s2.texture)
		if bm == null: continue
		var cobre := 0
		for q in pts:
			if r2.has_point(q):
				var l: Vector2 = q - r2.position
				if bm.get_bitv(Vector2i(int(l.x), int(l.y))): cobre += 1
		if cobre >= 2: return true
	return false

## Ponto de nascimento em área aberta: procura em volta do spawn do mapa uma célula livre que nada cubra.
func _spawn_aberto(p: Vector2) -> Vector2:
	if not _coberto(Iso.to_screen(p), 110.0): return p
	for r in range(1, 9):
		for i in 16:
			var q := p + Vector2.from_angle(TAU * i / 16.0) * r
			if sim.andavel(q) and sim.zona_segura(q) == sim.zona_segura(p) and not _coberto(Iso.to_screen(q), 110.0):
				return q
	return p

func _mascara(kind: String, tex: Texture2D) -> BitMap:
	if mascaras.has(kind): return mascaras[kind]
	var img := tex.get_image()
	if img == null: mascaras[kind] = null; return null
	if img.is_compressed(): img.decompress()
	var bm := BitMap.new()
	bm.create_from_image_alpha(img, 0.5)
	mascaras[kind] = bm
	return bm

# =================================================================== sobreposição: anéis, barras, nomes, marcadores
func _desenhar_sobre() -> void:
	var f := Tema.FONTE_TITULO
	# anel do alvo e do hover
	for id in [jog.alvo, hover_id]:
		var v = views.get(id)
		if v == null or v.morto: continue
		var e: Ent = sim.ents.get(id)
		if e == null: continue
		var cor := Color(0.85, 0.15, 0.1, 0.85) if jog.eh_inimigo_de(e) else Color(0.95, 0.85, 0.45, 0.8)
		var r := Iso.elipse(0.55 * v.escala_base * e.escala * (2.0 if e.tipo == "chefe" else 1.0))
		Unidade._elipse(sobre, v.position, r, cor, false, 2.0 if id == jog.alvo else 1.2)
	for id in views.keys():
		var v = views[id]
		var e: Ent = sim.ents.get(id)
		if e == null or not v.visible or v.morto: continue
		var topo: Vector2 = v.position + Vector2(0, -v.altura_px * e.escala - (26 if v.levita else 0) - 8)
		match e.tipo:
			"npc":
				var marca := Missoes.marcador_npc(jog, e.kind)
				if marca != "":
					var a: float = 0.85 + 0.15 * sin(t * 4.0)
					var cor2 := Color(1.0, 0.82, 0.25, a) if marca == "!" else Color(0.75, 0.95, 0.4, a)
					sobre.draw_string_outline(Tema.FONTE_GOTICA, topo + Vector2(-7, -16 - 3 * sin(t * 3.0)), marca, HORIZONTAL_ALIGNMENT_LEFT, -1, 34, 6, Color(0, 0, 0, 0.9))
					sobre.draw_string(Tema.FONTE_GOTICA, topo + Vector2(-7, -16 - 3 * sin(t * 3.0)), marca, HORIZONTAL_ALIGNMENT_LEFT, -1, 34, cor2)
				if id == hover_id or mostrar_nomes or e.pos.distance_to(jog.pos) < 5.0:
					_nome(topo, e.nome, Color("#f0dca0"), 13)
					var tit: String = e.aux.get("titulo", "")
					if tit != "": _nome(topo + Vector2(0, 14), tit, Color("#a89f8c"), 11, Tema.FONTE_ITALICO)
			"monstro", "invocacao":
				var ferido := e.hp < e.hp_max - 0.5
				if id == hover_id or id == jog.alvo or ferido or e.arquetipo in ["elite", "raro"]:
					var larg := 44.0
					var cor_b := Color(0.75, 0.12, 0.08) if e.tipo == "monstro" else Color(0.3, 0.7, 0.3)
					if e.tipo == "monstro" and e.aux.get("neutro", false) and e.estado in ["ocioso", "vagar", "voltar"]: cor_b = Color(0.85, 0.7, 0.15)
					sobre.draw_rect(Rect2(topo.x - larg * 0.5 - 1, topo.y - 1, larg + 2, 6), Color(0, 0, 0, 0.8))
					sobre.draw_rect(Rect2(topo.x - larg * 0.5, topo.y, larg * e.frac_hp(), 4), cor_b)
					if e.postura < e.postura_max and e.postura_max > 0:
						sobre.draw_rect(Rect2(topo.x - larg * 0.5, topo.y + 5, larg * (1.0 - e.postura / e.postura_max), 2), Color(0.85, 0.65, 0.2))
				if id == hover_id or id == jog.alvo or mostrar_nomes or e.arquetipo in ["elite", "raro"]:
					var cn := Color("#ff8a72")    # vermelho: ataca quem chegar perto
					if e.aux.get("neutro", false): cn = Color("#f2d65a")   # amarelo: neutro, só reage se apanhar
					if e.arquetipo == "elite": cn = Color("#e0b84a")
					elif e.arquetipo == "raro": cn = Color("#7fb8ff")
					_nome(topo + Vector2(0, -8), "%s  %d" % [e.nome, e.nivel], cn, 12)
			"jogador":
				if id != jog.id:   # outros jogadores da rede: nome, nível e vida
					_nome(topo + Vector2(0, -8), "%s  %d" % [e.nome, e.nivel], Color("#9fd8ff"), 12)
					sobre.draw_rect(Rect2(topo.x - 21, topo.y - 1, 42, 5), Color(0, 0, 0, 0.8))
					sobre.draw_rect(Rect2(topo.x - 20, topo.y, 40 * e.frac_hp(), 3), Color(0.3, 0.8, 0.35))
	# baús e objetos sob o mouse
	if objs.has(hover_id):
		var o = objs[hover_id]
		var e2: Ent = o.ent
		var nm: String = e2.nome
		if e2.kind == "bau" and e2.aux.get("aberto", false): nm += " (vazio)"
		_nome(o.position + Vector2(0, -78), nm, Color("#f0dca0"), 13)
	# itens no chão: nome com a cor da raridade (Alt mostra todos)
	for id in itens_chao.keys():
		var n = itens_chao[id]
		if n.voo < 1.0: continue
		if mostrar_nomes or id == hover_chao or n.cor != Defs.cor_raridade("comum"):
			if not mostrar_nomes and id != hover_chao and n.position.distance_to(views[jog.id].position if views.has(jog.id) else Vector2.ZERO) > 420: continue
			_rotulo_item(n.position + Vector2(0, -34), n.nome, n.cor, id == hover_chao)

func _nome(p: Vector2, txt: String, cor: Color, tam := 13, fonte: Font = null) -> void:
	var fo := fonte if fonte else Tema.FONTE_TITULO
	var w := fo.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	sobre.draw_string_outline(fo, p + Vector2(-w * 0.5, 0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, 4, Color(0, 0, 0, 0.85))
	sobre.draw_string(fo, p + Vector2(-w * 0.5, 0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

func _rotulo_item(p: Vector2, txt: String, cor: Color, hl: bool) -> void:
	var fo := Tema.FONTE_TEXTO
	var w := fo.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 13).x
	var r := Rect2(p.x - w * 0.5 - 6, p.y - 13, w + 12, 18)
	sobre.draw_rect(r, Color(0.04, 0.03, 0.03, 0.85 if hl else 0.7))
	sobre.draw_rect(r, Color(cor.r, cor.g, cor.b, 0.7 if hl else 0.35), false, 1.0)
	sobre.draw_string(fo, Vector2(p.x - w * 0.5, p.y + 1), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, cor)

# =================================================================== salvar
func _salvar() -> void:
	t_salvar = 0.0
	if rede != null: return   # em rede quem salva é o servidor, na conta
	if jog == null or not jog.vivo: return
	var s := Jogador.salvar(jog, sim)
	var f := FileAccess.open(SAVE, FileAccess.WRITE)
	if f: f.store_string(JSON.stringify(s))

static func carregar_save() -> Dictionary:
	if not FileAccess.file_exists(SAVE): return {}
	var f := FileAccess.open(SAVE, FileAccess.READ)
	var d = JSON.parse_string(f.get_as_text())
	return d if d is Dictionary else {}

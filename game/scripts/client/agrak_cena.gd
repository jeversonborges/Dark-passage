extends Node
## O Agrak no cliente: a apresentação ao vivo (design/pvp/agrak/apresentacao.md). A câmera continua do jogador;
## por cima da arena entram as falas de Caim e Abel em letra grande, o cartão de cada gladiador, a faixa da etapa,
## as barras dos leões, a plateia animada, os portões, o Anel do Amargo, a poeira do Pião e a chuva de pétalas.
## O game.gd cria este nó quando o mapa tem o bloco "agrak" e repassa todos os eventos para ev().

const COR_CAIM := Color("#ffb45a")
const COR_ABEL := Color("#d9ccb0")
const COR_AMARGO := Color("#8dff5a")
const COR_SANGUE := Color("#b0231a")
const FPS_PLATEIA := 4.0

var game
var camada := CanvasLayer.new()
var tela: Control
var chao: Node2D            # Anel do Amargo (no chão, abaixo das unidades)
var cima: Node2D            # poeira do Pião, coisas jogadas (acima das unidades)
var t := 0.0

var etapa := {}             # último agrak_etapa
var etapa_t0 := 0.0         # t local em que a etapa começou
var falas: Array = []       # [{quem, texto, t}] (no máximo 2 na tela: Caim em cima, Abel embaixo)
var cartoes: Array = []     # gladiadores sendo apresentados {cartoes, t}
var coroa := {}             # {id, nome, classe, t}
var feras := {}             # id -> nome (barras dos leões)
var plateia: Array = []     # [Sprite2D, v, o, fase]
var reacao_t := -1.0        # > 0: braços para cima (2-3-3-2)
var reacao_tipo := ""
var coro := {}              # texto do coro na tela {texto, t}
var portoes := {}           # id -> [Sprite2D, kind]
var anel := {}              # {centro, r0, r1, dur, t}
var giros := {}             # id -> fim (poeira do Pião)
var petalas: Array = []     # [pos, vel, rot, vrot, cor, tam]
var lixo: Array = []        # coisas jogadas da plateia [de, para, t, dur, cor, tam]
var esporos: Array = []     # pontos do Anel [ang, dr, fase]
var espectador := false

func iniciar(g) -> void:
	game = g
	camada.layer = 9
	add_child(camada)
	tela = Control.new()
	tela.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tela.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tela.draw.connect(_desenhar_tela)
	camada.add_child(tela)
	chao = Node2D.new(); chao.z_index = -4; chao.draw.connect(_desenhar_chao)
	game.decal.add_child(chao)
	cima = Node2D.new(); cima.z_index = 30; cima.draw.connect(_desenhar_cima)
	game.sobre.add_child(cima)
	_achar_props()
	for i in 90: esporos.append([randf() * TAU, randf_range(-0.6, 2.4), randf() * TAU])
	if game.audio.sons.has("ambiente/agrak_multidao"): game.audio.ambiente("ambiente/agrak_multidao")

func limpar() -> void:
	if is_instance_valid(chao): chao.queue_free()
	if is_instance_valid(cima): cima.queue_free()
	queue_free()

## A plateia e os portões são props do mapa (Sprite2D sem nome): acha cada um pela posição e pela textura.
func _achar_props() -> void:
	var por_pos := {}
	for s in game.mundo.get_children() + game.decal.get_children():
		if s is Sprite2D: por_pos[Vector2i(roundi(s.position.x), roundi(s.position.y))] = por_pos.get(Vector2i(roundi(s.position.x), roundi(s.position.y)), []) + [s]
	var i := 0
	for p in game.mapa.get("props", []):
		var k: String = p["k"]
		var tex := Tema.tex("res://assets/ext/ambiente/objetos/%s.png" % k)
		var q := Iso.to_screen(Vector2(p["x"], p["y"]))
		var achado: Sprite2D = null
		for s in por_pos.get(Vector2i(roundi(q.x), roundi(q.y)), []):
			if s.texture == tex: achado = s; break
		if achado == null: continue
		if int(p.get("plateia", 0)) == 1:
			var partes := k.split("_")   # plateia_<v>_<quadro>_<o>
			if partes.size() >= 4:
				plateia.append([achado, partes[1], partes[3], (i * 7 + int(p["x"] * 3.0)) % 4])
				i += 1
		if p.has("portao"):
			portoes[str(p["portao"])] = [achado, k]

# =================================================================== eventos
func ev(tipo: String, d: Dictionary) -> void:
	match tipo:
		"agrak_etapa":
			if d.get("fim", false): etapa = {}; return
			if d.get("etapa", "") != etapa.get("etapa", ""): etapa_t0 = t - float(d.get("t", 0.0))
			etapa = d
			if d.get("etapa", "") in ["luta_leoes", "ultimo_de_pe"] and d.get("t", 0.0) < 0.5:
				game.hud.banner_mostrar(str(d.get("nome", "")).to_upper(), "Último de Pé · todos contra todos" if d.get("pvp", false) else "", Color("#ff8a5a"))
		"agrak_fala":
			falas = falas.filter(func(f): return f["quem"] != d["quem"])
			falas.append({"quem": d["quem"], "texto": str(d.get("texto", "")), "t": t})
			_som("agrak/megafone" if d["quem"] == "caim" else "agrak/abel_resmungo", -8.0 if d["quem"] == "caim" else -10.0)
		"agrak_gladiador":
			cartoes = [{"cartoes": d.get("cartoes", []), "t": t}]
		"agrak_plateia": _plateia(str(d.get("r", "")), str(d.get("texto", "")))
		"agrak_portao": _portao(str(d.get("portao", "")), d.get("aberto", false))
		"agrak_som":
			var p = d.get("pos")
			game.audio.tocar(str(d["som"]), Iso.to_screen(p) if p is Vector2 else null, -2.0)
		"agrak_musica":
			var m := {"luta": "musica/agrak_arena", "final": "musica/agrak_arena", "vitoria": "musica/vinheta/vitoria_chefe"}
			var nome: String = m.get(str(d.get("m", "")), "")
			if nome != "" and game.audio.sons.has(nome):
				if nome.begins_with("musica/vinheta"): game.audio.tocar(nome)
				else: game.audio.musica(nome); game.musica_chefe = true
		"agrak_fera":
			if d.get("fim", false): feras.erase(int(d["id"]))
			else: feras[int(d["id"])] = str(d.get("nome", ""))
		"agrak_anel":
			if d.get("fim", false): anel = {}
			else: anel = {"centro": d["centro"], "r0": float(d["r0"]), "r1": float(d["r1"]), "dur": float(d["dur"]), "t": t}
		"agrak_fx":
			match str(d.get("fx", "")):
				"piao": giros[int(d["id"])] = t + float(d.get("dur", 10.0))
				"coisas_na_areia": _jogar_coisas(d["pos"])
		"agrak_coroacao":
			coroa = d.duplicate(); coroa["t"] = t
			if int(d.get("id", -1)) >= 0: _chuva_petalas()
		"agrak_espectador":
			espectador = d.get("on", false)
			if espectador: game.hud.aviso("O Saulo te levantou. Assista do Camarote dos Derrotados.", Color("#f4e6b8"))
		"agrak_fim":
			etapa = {}; feras.clear(); anel = {}
			game.musica_chefe = false
		"morreu":
			if d.get("tipo", "") == "jogador" or d.get("chefe", false): _plateia("bracos", "")
		"morte_pvp":
			_plateia("urro", "")

func _som(nome: String, db := 0.0) -> void:
	if game.audio.sons.has(nome): game.audio.tocar(nome, null, db)

func _plateia(r: String, texto: String) -> void:
	match r:
		"urro", "bracos", "coro", "golias":
			reacao_t = 1.0 if r in ["urro", "bracos"] else 2.2
			reacao_tipo = r
		"vaia":
			reacao_t = -1.0
	if texto != "": coro = {"texto": texto, "t": t}
	var som := {"urro": "agrak/plateia_urro", "bracos": "agrak/plateia_urro", "coro": "agrak/plateia_agrak", "golias": "agrak/plateia_golias", "vaia": "agrak/plateia_vaia"}
	if som.has(r): _som(som[r], -3.0)

func _portao(id: String, aberto: bool) -> void:
	var pr: Array = portoes.get(id, [])
	if pr.is_empty() or not is_instance_valid(pr[0]): return
	var s: Sprite2D = pr[0]
	var k: String = pr[1]
	var aberto_k := k.replace("portao_grade_agrak_", "portao_grade_agrak_aberto_")
	var tw := create_tween()
	if aberto_k != k and Defs.AMB.get("objetos", {}).has(aberto_k):
		tw.tween_property(s, "position:y", s.position.y - 10.0, 0.5).set_trans(Tween.TRANS_SINE)   # a grade sobe
		tw.tween_callback(func():
			var kk := aberto_k if aberto else k
			var m: Dictionary = Defs.AMB["objetos"][kk]
			s.texture = Tema.tex("res://assets/ext/ambiente/objetos/%s.png" % kk)
			s.offset = -Vector2(m["anchor"][0], m["anchor"][1])
			s.position.y += 10.0)
	else:   # o Portão do Gigante não tem arte aberta: some na poeira
		tw.tween_property(s, "modulate:a", 0.0 if aberto else 1.0, 0.8)
		if aberto: game.fx.folha("esquiva_poeira", s.position)
	game.audio.tocar("itens/porta_ferro", s.position, -2.0)

func _jogar_coisas(centro) -> void:
	var c: Vector2 = Iso.to_screen(centro if centro is Vector2 else Vector2(28, 23))
	var cores := [Color("#5a4a36"), Color("#3c3a2e"), Color("#7a6a52"), Color("#2e2620"), Color("#6b3a24")]
	for i in 26:
		var de := c + Vector2(randf_range(-520, 520), randf_range(-420, -300))
		var para := c + Vector2(randf_range(-300, 300), randf_range(-120, 140))
		lixo.append([de, para, -randf() * 2.5, randf_range(0.7, 1.2), cores[i % cores.size()], randf_range(2.0, 4.5)])

func _chuva_petalas() -> void:
	var tons := [Color("#7a2a1c"), Color("#9a4a2a"), Color("#5c1f18"), Color("#a8724a"), Color("#6e3a22")]
	for i in 160:
		petalas.append([Vector2(randf() * 900.0, -randf() * 500.0), Vector2(randf_range(-14, 22), randf_range(30, 62)), randf() * TAU,
			randf_range(-3.0, 3.0), tons[i % tons.size()], randf_range(3.0, 6.5)])

# =================================================================== tempo
func _process(dt: float) -> void:
	t += dt
	# plateia: 0-1-0-1 a ~4 fps, cada tile num quadro diferente; reação: 2-3-3-2
	var reagindo := reacao_t > 0.0
	if reagindo: reacao_t -= dt
	for pl in plateia:
		var s: Sprite2D = pl[0]
		if not is_instance_valid(s): continue
		var q := int(floor(t * FPS_PLATEIA + pl[3])) % 2
		if reagindo:
			var seq := [2, 3, 3, 2]
			q = seq[int(floor((1.0 - fmod(maxf(reacao_t, 0.0), 1.0)) * 4.0 + pl[3] * 0.25)) % 4]
		var k := "plateia_%s_%d_%s" % [pl[1], q, pl[2]]
		if s.get_meta("q", -1) != q:
			s.set_meta("q", q)
			s.texture = Tema.tex("res://assets/ext/ambiente/objetos/%s.png" % k)
	for p in petalas:
		p[0] += (p[1] + Vector2(sin(t * 1.7 + p[2]) * 18.0, 0)) * dt
		p[2] += p[3] * dt
	petalas = petalas.filter(func(p): return p[0].y < 720.0)
	for l in lixo: l[2] += dt
	var caiu := lixo.filter(func(l): return l[2] >= l[3])
	for l in caiu: game.fx.folha("esquiva_poeira", l[1], {"escala": 0.5})
	lixo = lixo.filter(func(l): return l[2] < l[3])
	for id in giros.keys():
		if t > giros[id]: giros.erase(id)
	tela.queue_redraw()
	if is_instance_valid(chao) and not anel.is_empty(): chao.queue_redraw()
	if is_instance_valid(cima) and (not giros.is_empty() or not lixo.is_empty()): cima.queue_redraw()
	elif is_instance_valid(cima) and cima.get_meta("sujo", false): cima.queue_redraw()
	if is_instance_valid(cima): cima.set_meta("sujo", not giros.is_empty() or not lixo.is_empty())

# =================================================================== desenho (tela)
func _txt(c: CanvasItem, p: Vector2, s: String, tam: int, cor: Color, fonte: Font, contorno := 4, larg_max := -1.0) -> void:
	var w := fonte.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	if larg_max > 0.0 and w > larg_max:
		tam = int(tam * larg_max / w); w = fonte.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var x := p.x - w * 0.5
	if contorno > 0: c.draw_string_outline(fonte, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, contorno, Color(0.03, 0.02, 0.02, cor.a * 0.95))
	c.draw_string(fonte, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

func _faixa_escura(c: CanvasItem, cen: Vector2, w: float, h: float, a: float) -> void:
	for i in 32:
		var k := 1.0 - absf(i - 15.5) / 16.0
		c.draw_rect(Rect2(cen.x - w * 0.5 + i * w / 32.0, cen.y - h * 0.5, w / 32.0 + 1.0, h), Color(0, 0, 0, 0.5 * a * k * k))

func _desenhar_tela() -> void:
	var c := tela
	var sz := c.size
	var cx := sz.x * 0.5
	# ---- faixa da etapa (topo)
	if not etapa.is_empty():
		var nome: String = str(etapa.get("nome", "")).to_upper()
		var dur := float(etapa.get("dur", 0.0))
		var resta := maxf(0.0, dur - (t - etapa_t0))
		_faixa_escura(c, Vector2(cx, 30), 560, 50, 1.0)
		c.draw_line(Vector2(cx - 200, 50), Vector2(cx + 200, 50), Color(0.78, 0.6, 0.32, 0.55), 1.0)
		_txt(c, Vector2(cx, 34), "O AGRAK · " + nome, 22, Color("#f0d79a"), Tema.FONTE_GOTICA, 4)
		var sub := "%d:%02d" % [int(resta) / 60, int(resta) % 60] if dur > 0.0 else ""
		var g := "Gladiadores de pé: %d de %d" % [int(etapa.get("restam", 0)), int(etapa.get("total", 0))]
		_txt(c, Vector2(cx, 64), (sub + "   ·   " if sub != "" else "") + g, 13, Color(0.86, 0.8, 0.68), Tema.FONTE_ITALICO, 3)
		if etapa.get("pvp", false):
			var pul := 0.6 + 0.4 * sin(t * 4.0)
			_txt(c, Vector2(cx, 82), "SEM POÇÕES · TODOS CONTRA TODOS", 11, Color(1.0, 0.45, 0.32, pul), Tema.FONTE_PIXEL, 2)
	# ---- barras dos leões (até 3, abaixo da faixa)
	var i := 0
	for id in feras:
		var e: Ent = game.sim.ents.get(id)
		if e == null or not e.vivo: continue
		var r := Rect2(cx - 300 + i * 205, 96, 190, 9)
		_txt(c, Vector2(r.position.x + r.size.x * 0.5, r.position.y - 3), feras[id], 12, Color("#ffcf9a"), Tema.FONTE_GOTICA, 3, 190.0)
		c.draw_rect(r.grow(1), Color(0, 0, 0, 0.85))
		c.draw_rect(r, Color(0.06, 0.03, 0.03, 0.92))
		c.draw_rect(Rect2(r.position, Vector2(r.size.x * e.frac_hp(), r.size.y)), Color(0.62, 0.06, 0.04))
		c.draw_rect(Rect2(r.position, Vector2(r.size.x * e.frac_hp(), 3)), Color(1, 1, 1, 0.12))
		c.draw_rect(r.grow(1), Color(0.55, 0.16, 0.1, 0.9), false, 1.0)
		i += 1
	# ---- falas de Caim (em cima, berrando) e Abel (embaixo, debochando)
	for f in falas.duplicate():
		var idade: float = t - float(f["t"])
		var vida := 3.6 if f["quem"] == "caim" else 3.4
		if idade > vida: falas.erase(f); continue
		var a := clampf(idade / 0.18, 0.0, 1.0) * clampf((vida - idade) / 0.5, 0.0, 1.0)
		var caim: bool = f["quem"] == "caim"
		var y := sz.y * (0.27 if caim else 0.355)
		var tam := 30 if caim else 19
		var tremor := Vector2(sin(t * 61.0), cos(t * 47.0)) * (2.2 * (1.0 - clampf(idade / 0.5, 0.0, 1.0))) if caim else Vector2.ZERO
		var escala := 1.0 + (0.18 * (1.0 - clampf(idade / 0.2, 0.0, 1.0)) if caim else 0.0)
		_faixa_escura(c, Vector2(cx, y - tam * 0.35), minf(sz.x - 40, 900), tam * 1.7, a * 0.9)
		var quem := "CAIM" if caim else "ABEL"
		_txt(c, Vector2(cx, y - tam - 2), quem, 10, Color(COR_CAIM.r, COR_CAIM.g, COR_CAIM.b, a * 0.8) if caim else Color(COR_ABEL.r, COR_ABEL.g, COR_ABEL.b, a * 0.7), Tema.FONTE_PIXEL, 2)
		var cor := COR_CAIM if caim else COR_ABEL
		_txt(c, Vector2(cx, y) + tremor, str(f["texto"]), int(tam * escala), Color(cor.r, cor.g, cor.b, a), Tema.FONTE_GOTICA if caim else Tema.FONTE_ITALICO, 5 if caim else 3, sz.x - 60)
	# ---- coro da plateia (A-GRAAAK!, GOLIAS! GOLIAS!)
	if not coro.is_empty():
		var idade2: float = t - float(coro["t"])
		if idade2 > 2.4: coro = {}
		else:
			var a2 := clampf(idade2 / 0.15, 0.0, 1.0) * clampf((2.4 - idade2) / 0.6, 0.0, 1.0)
			var pulso := 1.0 + 0.08 * absf(sin(idade2 * 7.0))
			_txt(c, Vector2(cx, sz.y * 0.47), str(coro["texto"]), int(44 * pulso), Color(0.93, 0.83, 0.62, a2 * 0.85), Tema.FONTE_GOTICA, 6, sz.x - 60)
	# ---- cartão do gladiador (nome, classe e facção em letra grande)
	for cc in cartoes.duplicate():
		var idade3: float = t - float(cc["t"])
		if idade3 > 2.9: cartoes.erase(cc); continue
		var a3 := clampf(idade3 / 0.25, 0.0, 1.0) * clampf((2.9 - idade3) / 0.5, 0.0, 1.0)
		var lista: Array = cc["cartoes"]
		var y0 := sz.y * 0.6
		var desliza := (1.0 - clampf(idade3 / 0.3, 0.0, 1.0)) * 60.0
		for k in lista.size():
			var cd: Dictionary = lista[k]
			var yy := y0 + k * (46.0 if lista.size() > 1 else 0.0)
			var tam_n := 34 if lista.size() == 1 else 22
			var fac: String = {"vigilia": "VIGÍLIA", "arautos": "ARAUTOS"}.get(str(cd.get("faccao", "")), "SEM BANDEIRA")
			var cor_f := Color("#d8b46a") if cd.get("faccao", "") == "vigilia" else (Color("#c86a5a") if cd.get("faccao", "") == "arautos" else Color("#b8b0a0"))
			_faixa_escura(c, Vector2(cx, yy - tam_n * 0.3), 620, tam_n * 1.9, a3)
			_txt(c, Vector2(cx - desliza, yy), str(cd.get("nome", "")), tam_n, Color(0.97, 0.92, 0.82, a3), Tema.FONTE_GOTICA, 5)
			_txt(c, Vector2(cx + desliza, yy + tam_n * 0.62), "%s · %s · nível %d" % [str(cd.get("classe", "")), fac, int(cd.get("nivel", 1))], 13 if lista.size() == 1 else 11, Color(cor_f.r, cor_f.g, cor_f.b, a3), Tema.FONTE_TITULO, 3)
	# ---- coroação
	if not coroa.is_empty():
		var idade4: float = t - float(coroa["t"])
		if idade4 > 9.0: coroa = {}
		else:
			var a4 := clampf(idade4 / 0.6, 0.0, 1.0) * clampf((9.0 - idade4) / 1.0, 0.0, 1.0)
			var y4 := sz.y * 0.5
			_faixa_escura(c, Vector2(cx, y4 - 10), minf(sz.x, 900), 120, a4)
			if int(coroa.get("id", -1)) >= 0:
				_txt(c, Vector2(cx, y4 - 26), "ÚLTIMO DE PÉ", 14, Color(0.85, 0.68, 0.4, a4), Tema.FONTE_TITULO, 3)
				_txt(c, Vector2(cx, y4 + 18), str(coroa.get("nome", "")), 52, Color(1.0, 0.86, 0.56, a4), Tema.FONTE_GOTICA, 7)
				_txt(c, Vector2(cx, y4 + 44), "%s · leva uma Ficha de Sangue" % str(coroa.get("classe", "")), 14, Color(0.86, 0.78, 0.64, a4), Tema.FONTE_ITALICO, 3)
			else:
				_txt(c, Vector2(cx, y4 + 12), "O AGRAK COMEU TODO MUNDO", 40, Color(COR_SANGUE.r * 1.4, COR_SANGUE.g * 1.4, COR_SANGUE.b * 1.4, a4), Tema.FONTE_GOTICA, 7)
	# ---- espectador
	if espectador and not etapa.is_empty():
		_txt(c, Vector2(cx, sz.y - 128), "Espectador · Camarote dos Derrotados", 13, Color(0.95, 0.9, 0.72, 0.75), Tema.FONTE_ITALICO, 3)
	# ---- pétalas secas (coroação)
	for p in petalas:
		var pos: Vector2 = p[0] * Vector2(sz.x / 900.0, 1.0)
		var col: Color = p[4]
		var s := float(p[5])
		var dirv := Vector2.from_angle(p[2])
		var lado := dirv.orthogonal() * s * 0.45 * absf(cos(p[2] * 1.3))
		var pts := PackedVector2Array([pos - dirv * s, pos + lado, pos + dirv * s, pos - lado])
		c.draw_colored_polygon(pts, col)
		c.draw_line(pos - dirv * s * 0.8, pos + dirv * s * 0.8, col.darkened(0.45), 1.0)

# =================================================================== desenho (mundo)
## Anel do Amargo: parede de névoa verde que fecha do muro até o centro (fora do anel o Amargo queima).
func _desenhar_chao() -> void:
	if anel.is_empty(): return
	var k := clampf((t - float(anel["t"])) / float(anel["dur"]), 0.0, 1.0)
	var r := lerpf(anel["r0"], anel["r1"], k)
	var cen: Vector2 = anel["centro"]
	var n := 96
	for camada_i in 7:   # névoa: faixas cada vez mais largas e transparentes por fora
		var rr := r + camada_i * 0.55
		var pts := PackedVector2Array()
		for i in n + 1:
			var a := TAU * i / n
			var onda := 0.18 * sin(a * 7.0 + t * 1.3 + camada_i) + 0.12 * sin(a * 13.0 - t * 2.1)
			pts.append(Iso.to_screen(cen + Vector2(cos(a), sin(a)) * (rr + onda)))
		var al := 0.32 * pow(0.72, camada_i)
		chao.draw_polyline(pts, Color(0.35, 0.62, 0.18, al), 9.0 + camada_i * 5.0, true)
	var borda := PackedVector2Array()
	for i in n + 1:
		var a2 := TAU * i / n
		borda.append(Iso.to_screen(cen + Vector2(cos(a2), sin(a2)) * (r + 0.05 * sin(a2 * 9.0 + t * 3.0))))
	chao.draw_polyline(borda, Color(COR_AMARGO.r, COR_AMARGO.g, COR_AMARGO.b, 0.55 + 0.2 * sin(t * 5.0)), 2.0, true)
	for e in esporos:   # esporos verdes flutuando na névoa
		var ang: float = e[0] + t * 0.05
		var rr2: float = r + float(e[1]) + 0.25 * sin(t * 0.9 + e[2])
		var p := Iso.to_screen(cen + Vector2(cos(ang), sin(ang)) * rr2) + Vector2(0, -6.0 - 5.0 * sin(t * 1.5 + e[2]))
		chao.draw_circle(p, 1.6, Color(0.7, 1.0, 0.45, 0.35 + 0.3 * sin(t * 2.0 + e[2])))

func _desenhar_cima() -> void:
	# poeira e faíscas do Pião em volta do Golias
	for id in giros:
		var v = game.views.get(id)
		if v == null: continue
		var p: Vector2 = v.position
		for i in 26:
			var a := t * 9.0 + TAU * i / 26.0
			var rr := 3.3 + 0.35 * sin(t * 6.0 + i)
			var q := p + Vector2(cos(a) * 32.0 * rr, sin(a) * 16.0 * rr) + Vector2(0, -8)
			var cor := Color(0.62, 0.52, 0.38, 0.28) if i % 5 != 0 else Color(1.0, 0.72, 0.32, 0.7)
			cima.draw_circle(q, 7.0 if i % 5 != 0 else 1.8, cor)
		for i in 3:   # rastro da corrente
			var a2 := t * 9.0 - i * 0.22
			cima.draw_line(p + Vector2(0, -60), p + Vector2(cos(a2) * 115.0, sin(a2) * 58.0 - 20.0), Color(0.18, 0.16, 0.14, 0.45 - i * 0.13), 3.0 - i)
	# coisas que a plateia joga na areia (ossos, garrafas, sapatos)
	for l in lixo:
		if float(l[2]) < 0.0: continue
		var k := float(l[2]) / float(l[3])
		var de: Vector2 = l[0]; var para: Vector2 = l[1]
		var q2 := de.lerp(para, k) + Vector2(0, -sin(k * PI) * 160.0)
		var dirv := Vector2.from_angle(k * 9.0 + de.x)
		cima.draw_line(q2 - dirv * l[5], q2 + dirv * l[5], l[4], 2.5)

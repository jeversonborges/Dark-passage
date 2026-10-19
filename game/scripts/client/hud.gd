extends CanvasLayer
## HUD: barra de baixo (orbes, XP, skills, cinto, menu), retrato, alvo, chefe, minimapa, missões, avisos e morte.
## Peças de assets/ext/ui (thread de Interface e HUD), posições do layout.json.

var game
var raiz := Control.new()
var barra: Control
var topo_esq: Control
var alvo_ui: Control
var minimapa: Control
var rastreador: RichTextLabel
var log_box: VBoxContainer
var chat_painel: PanelContainer
var chat_texto: RichTextLabel
var chat_entrada: LineEdit
var chat_fundo: StyleBoxFlat
var chat_canal_bt: Button
var chat_canal := "perto"     # canal da caixa: "perto" ou "global" (o botão troca); /g, /m e /r mudam só aquela mensagem
var chat_ultimo_pm := ""
var chat_barra: HBoxContainer   # aba "Chat" + botões minimizar e fechar, logo abaixo do painel
var chat_aba: Button
var chat_min_bt: Button
var chat_estado := "aberto"   # "aberto", "minimizado" (só a aba, contando as novas) ou "fechado" (some tudo; F2 ou Enter reabrem). Salvo em user://chat.cfg
var chat_nao_lidas := 0
var chat_tw: Tween
const CHAT_CFG := "user://chat.cfg"
var grupo_box: VBoxContainer
var convite_box: PanelContainer
var troca_box: PanelContainer
var inspecao_box: PanelContainer
var menu_box: PanelContainer
var aviso_lbl: Label
var aviso_t := 0.0
var banner: Control
var banner_t := 0.0
var banner_txt := ""
var banner_sub := ""
var canal_ui: Control
var canal_d := {}
var canal_t := 0.0
var morte_ui: Control
var ajuda_ui: Control
var mapa_ui: Control
var tooltip: PanelContainer
var tip_lbl: RichTextLabel
var tip_estilo: StyleBox            # moldura padrão das dicas (volta depois de um item)
var ganhos: VBoxContainer
var chefe_d := {}
var mult_tremor := 1.0
var mini_tex: ImageTexture
var mini_zoom := 3.0
var t := 0.0
var xp_flash := 0.0
var hover_slot := -1
var hover_cinto := -1
var hover_menu := -1
var pressionado := {}         # slot -> tempo do flash
var pet_ui: Control           # barra do pet do Cultista (retrato, vida e 5 comandos), em cima da barra de skills
var hover_pet := -1
var status_jog := {}          # s -> fim

const MENU := ["personagem", "mochila", "habilidades", "missoes", "mapa", "menu"]
const MENU_JANELA := {"personagem": "personagem", "mochila": "inventario", "habilidades": "habilidades", "missoes": "missoes"}
const MENU_NOME := {"personagem": "Personagem (C)", "mochila": "Mochila (I)", "habilidades": "Habilidades (K)", "missoes": "Missões (J)", "mapa": "Mapa (M)", "menu": "Menu (Esc)"}
const CINTO := [["vida", "Q"], ["recurso", "W"], ["antidoto", "E"], ["vela", "R"]]
const CINTO_PAD := ["pocao_vida", "pocao_recurso", "antidoto", "vela"]   # ações do controle de cada slot do cinto
const STATUS_NOME := {"atordoado": "Atordoado", "lento": "Lento", "queimadura": "Queimando", "sangramento": "Sangrando", "veneno": "Envenenado",
	"agarrado": "Agarrado", "silenciado": "Silenciado", "derrubado": "Derrubado", "medo": "Medo", "cego": "Cego", "enraizado": "Preso"}

func _ready() -> void:
	layer = 10
	raiz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = Tema.tema_janelas()
	add_child(raiz)
	_montar_barra()
	_montar_pet()
	_montar_topo()
	_montar_alvo()
	_montar_minimapa()
	_montar_log()
	_montar_chat()
	_montar_grupo()
	_montar_centro()
	_montar_tooltip()

# =================================================================== helpers
func _jog() -> Ent:
	return game.jog

func _txt(c: CanvasItem, p: Vector2, s: String, tam: int, cor: Color, fonte: Font = null, alinhar := 0, contorno := 3) -> void:
	var f := fonte if fonte else Tema.FONTE_TITULO
	var w := f.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var x := p.x - (w * 0.5 if alinhar == 0 else (w if alinhar == 1 else 0.0))
	if contorno > 0: c.draw_string_outline(f, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, contorno, Color(0.03, 0.02, 0.02, 0.95))
	c.draw_string(f, Vector2(x, p.y), s, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

func _barra(c: CanvasItem, r: Rect2, frac: float, cor: Color, fundo := Color(0.05, 0.04, 0.04, 0.9)) -> void:
	c.draw_rect(r.grow(1), Color(0.0, 0.0, 0.0, 0.85))
	c.draw_rect(r, fundo)
	var f := Rect2(r.position, Vector2(r.size.x * clampf(frac, 0.0, 1.0), r.size.y))
	c.draw_rect(f, cor)
	c.draw_rect(Rect2(f.position, Vector2(f.size.x, maxf(1.0, r.size.y * 0.35))), Color(1, 1, 1, 0.12))
	c.draw_rect(r.grow(1), Color(0.42, 0.34, 0.2, 0.9), false, 1.0)

class Painel extends Control:
	var desenhar: Callable
	var dentro: Callable
	var entrada: Callable
	func _draw() -> void:
		if desenhar.is_valid(): desenhar.call(self)
	func _has_point(p: Vector2) -> bool:
		if dentro.is_valid(): return dentro.call(p)
		return Rect2(Vector2.ZERO, size).has_point(p)
	func _gui_input(ev: InputEvent) -> void:
		if entrada.is_valid(): entrada.call(ev)

func _painel(desenhar: Callable) -> Painel:
	var p := Painel.new()
	p.desenhar = desenhar
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p

# =================================================================== barra de baixo
var hover_evasao := false

func _montar_barra() -> void:
	barra = _painel(_desenhar_barra)
	barra.size = Vector2(1280, 150)
	barra.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	barra.offset_left = -640; barra.offset_right = 640; barra.offset_top = -150; barra.offset_bottom = 0
	barra.mouse_filter = Control.MOUSE_FILTER_STOP
	barra.dentro = func(p: Vector2) -> bool:
		if _evasao_rect().has_point(p): return true
		if p.y > 66 and p.x > 0 and p.x < 1280: return true
		if _n_slots() > 10 and p.y > 30 and p.x > 218 and p.x < 222 + 48 * (_n_slots() - 10): return true
		return p.distance_to(Vector2(78, 78)) < 66 or p.distance_to(Vector2(1202, 78)) < 66
	barra.entrada = _entrada_barra
	barra.mouse_exited.connect(func(): hover_slot = -1; hover_cinto = -1; hover_menu = -1; esconder_tip())
	raiz.add_child(barra)

func _slot_rect(i: int) -> Rect2:
	if i >= Evolucao.SLOT_EVO: return Rect2(222 + 48 * (i - Evolucao.SLOT_EVO), 34, 44, 44)   # fileira da evolução (Shift+1..5)
	return Rect2(222 + 54 * i, 90, 52, 52)

## Slot da esquiva (botão direito): acima da barra, à esquerda do orbe do recurso.
func _evasao_rect() -> Rect2:
	return Rect2(1082, 14, 48, 48)

func _n_slots() -> int:
	return maxi(10, game.jog.skills_slots.size()) if game.jog else 10

func _cinto_rect(i: int) -> Rect2:
	return Rect2(792 + 52 * i, 94, 46, 46)

func _menu_rect(i: int) -> Rect2:
	return Rect2(1023 + 36 * (i % 3), 92 + 27 * (i / 3), 34, 24)

func _entrada_barra(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var p: Vector2 = ev.position
		var hs := -1; var hc := -1; var hm := -1
		for i in _n_slots(): if _slot_rect(i).has_point(p): hs = i
		for i in 4: if _cinto_rect(i).has_point(p): hc = i
		for i in 6: if _menu_rect(i).has_point(p): hm = i
		var he := _evasao_rect().has_point(p)
		if he != hover_evasao:
			hover_evasao = he
			if he: mostrar_tip(_tip_evasao())
			elif hs < 0 and hc < 0 and hm < 0: esconder_tip()
		if hs != hover_slot or hc != hover_cinto or hm != hover_menu:
			hover_slot = hs; hover_cinto = hc; hover_menu = hm
			if hs >= 0: mostrar_tip(_tip_skill(hs))
			elif hc >= 0: mostrar_tip(_tip_cinto(hc))
			elif hm >= 0: mostrar_tip("[font_size=14]%s[/font_size]" % MENU_NOME[MENU[hm]])
			else: esconder_tip()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_RIGHT and hover_slot >= 0:
		# clique direito no slot: a skill entra ou sai do modo automático
		game.audio.tocar("ui/clique", null, -6.0)
		game.cmd("auto_skill", [hover_slot])
		barra.accept_event()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if hover_slot >= 0: game.usar_skill(hover_slot)
		elif hover_cinto >= 0:
			var tipo: String = CINTO[hover_cinto][0]
			if tipo == "vela": game.usar_vela()
			else: game.cmd("pocao", [tipo])
		elif hover_menu >= 0:
			var nm: String = MENU[hover_menu]
			game.audio.tocar("ui/clique", null, -6.0)
			if nm == "mapa": alternar_mapa()
			elif nm == "menu": game.janelas.alternar("menu")
			else: game.janelas.alternar(MENU_JANELA[nm])
		barra.accept_event()

func _liquido_recurso() -> String:
	var j := _jog()
	if j.rec_max <= 0.0: return "sangue"
	var m: Dictionary = Tema.LAYOUT.get("orbes", {}).get("recurso", {}).get("liquido_por_classe", {})
	return m.get(j.classe, "neutro")

func _nome_recurso() -> String:
	var j := _jog()
	match j.classe:
		"humano": return "FÔLEGO"
		"cultista": return "SANGUE"
		"anjo": return "GRAÇA"
		"mutante": return "FÚRIA"
		"demonio": return "BRASA"
		"tecnomancer": return "CARGA"
		"warlord": return "ÓDIO"
	return ""

func _orbe(c: CanvasItem, centro: Vector2, frac: float, liquido: String, moldura: String, valor: String, nome: String, pulsar := false) -> void:
	var o := centro - Vector2(70, 70)
	c.draw_texture(Tema.ui("orbe_fundo"), o)
	var top := 17.0; var alt := 106.0
	var y0 := top + alt * (1.0 - clampf(frac, 0.0, 1.0))
	var liq := Tema.ui("orbe_liquido_" + liquido)
	if liq and y0 < top + alt:
		var cor := Color(1, 1, 1)
		if pulsar: cor = Color(1.0 + 0.25 * sin(t * 6.0), 1, 1)
		c.draw_texture_rect_region(liq, Rect2(o + Vector2(0, y0), Vector2(140, top + alt - y0)), Rect2(0, y0, 140, top + alt - y0), cor)
		if frac > 0.02 and frac < 0.99:
			var dy := y0 - 70.0
			var meia := sqrt(maxf(0.0, 53.0 * 53.0 - dy * dy))
			var sup := Tema.ui("orbe_superficie")
			if sup: c.draw_texture_rect(sup, Rect2(centro.x - meia, o.y + y0 - 8 + sin(t * 2.0) * 0.8, meia * 2.0, 16), false)
	c.draw_texture(Tema.ui("orbe_vidro"), o)
	c.draw_texture(Tema.ui("orbe_moldura_" + moldura), o)
	_txt(c, centro + Vector2(0, 4), valor, 15, Color("#f6ead0"), Tema.FONTE_TITULO, 0, 4)
	_txt(c, centro + Vector2(0, 62), nome, 9, Color("#d8c8a0"), Tema.FONTE_TITULO, 0, 3)

func _desenhar_barra(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	# extensão nas laterais (telas mais largas que 1280)
	var ext := Tema.ui("barra_extensao")
	var larg_tela := raiz.size.x
	if ext and larg_tela > 1280:
		var sobra := (larg_tela - 1280) * 0.5 + 2
		var x := -sobra
		while x < 0:
			c.draw_texture(ext, Vector2(x, 66)); x += 512
		x = 1280 - 4
		while x < 1280 + sobra:
			c.draw_texture(ext, Vector2(x, 66)); x += 512
	c.draw_texture(Tema.ui("barra_base"), Vector2.ZERO)
	# XP
	var xp_frac := float(j.xp) / float(maxi(1, Defs.xp_para_proximo(j.nivel)))
	var xr := Rect2(176, 75, 932, 8)
	var fill := Tema.ui("xp_preenchimento")
	if fill and xp_frac > 0.0:
		var wx := xr.size.x * clampf(xp_frac, 0.0, 1.0)
		c.draw_texture_rect(fill, Rect2(xr.position, Vector2(wx, xr.size.y)), true, Color(1, 1, 1) * (1.0 + xp_flash * 0.8))
		var ponta := Tema.ui("xp_ponta")
		if ponta: c.draw_texture(ponta, Vector2(xr.position.x + wx - 6, 71))
	c.draw_texture(Tema.ui("xp_vidro"), Vector2(170, 70))
	_txt(c, Vector2(640, 66), "EXP %.1f%%" % (xp_frac * 100.0), 8, Color("#e8ffb0"), Tema.FONTE_PIXEL, 0, 3)
	# orbes
	var envenenado := j.tem("veneno")
	_orbe(c, Vector2(78, 78), j.frac_hp(), "amargo" if envenenado else "vida", "vida", "%d" % ceili(j.hp), "VIDA", j.frac_hp() < 0.3)
	if j.rec_max > 0.0:
		_orbe(c, Vector2(1202, 78), j.rec / j.rec_max, _liquido_recurso(), "recurso", "%d" % floori(j.rec), _nome_recurso())
	else:
		_orbe(c, Vector2(1202, 78), j.frac_hp(), "sangue", "recurso", "%d%%" % roundi(j.frac_hp() * 100.0), "SANGUE")
	# info
	_txt(c, Vector2(186, 113), "%d" % j.nivel, 18, Color("#f0dca0"), Tema.FONTE_TITULO, 0, 3)
	_txt(c, Vector2(186, 124), "NÍVEL", 7, Color("#a89f8c"), Tema.FONTE_PIXEL, 0, 2)
	if j.classe == "humano":
		_txt(c, Vector2(186, 134), "%d BALAS" % j.municao, 7, Color("#e0b84a") if j.municao > 30 else Color("#ff6a4a"), Tema.FONTE_PIXEL, 0, 2)
	else:
		_txt(c, Vector2(186, 134), "%d OURO" % j.ouro, 7, Color("#e0b84a"), Tema.FONTE_PIXEL, 0, 2)
	# skills
	for i in _n_slots():
		var r := _slot_rect(i)
		var k := r.size.x / 52.0
		var h: Dictionary = Jogador.skill_def(j, i) if i < j.skills_slots.size() else {}
		if not h.is_empty():
			var ic := Tema.icone_skill(j.classe, h["id"])
			var bloq := j.nivel < int(h["nivel"])
			var falta: bool = not bloq and not h.get("passiva", false) and ((j.classe == "cultista" and j.hp <= Jogador.custo(j, h)) or (j.classe != "cultista" and j.rec < Jogador.custo(j, h)))
			var mod := Color(0.3, 0.3, 0.3) if bloq else (Color(0.55, 0.6, 0.85) if falta else Color.WHITE)
			if ic.size() == 2: c.draw_texture_rect_region(ic[0], Rect2(r.position + Vector2(6, 6) * k, Vector2(40, 40) * k), ic[1], mod)
			elif h.has("_evo"): _txt(c, r.position + Vector2(26, 30) * k, String(h["nome"]).left(3).to_upper(), 11, Color("#d8c08a") * mod, Tema.FONTE_PIXEL, 0, 2)   # ícone pintado ainda não chegou (LISTA.md)
			if bloq: _txt(c, r.position + Vector2(26, 32), "%d" % int(h["nivel"]), 13, Color("#a89f8c"))
			var cd := float(j.cds.get(h["id"], 0.0))
			if cd > 0.0:
				var tot := float(Jogador.talentos_em(j, h).get("recarga", 1.0))
				_setor(c, r.position + Vector2(26, 26), 20.0, cd / maxf(0.1, tot), Color(0, 0, 0, 0.72))
				_txt(c, r.position + Vector2(26, 31), ("%.1f" % cd) if cd < 3.0 else ("%d" % ceili(cd)), 13, Color("#f6ead0"))
			if h.has("cargas"):
				var cg := int(j.aux.get("cargas_" + h["id"], int(h["cargas"])))
				_txt(c, r.position + Vector2(44, 46), "%d" % cg, 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 1, 2)
				var rc := float(j.aux.get("recarga_carga_" + h["id"], 0.0))
				if rc > 0.0 and cd <= 0.0: c.draw_rect(Rect2(r.position + Vector2(6, 44), Vector2(40.0 * (1.0 - rc / float(h["recarga"])), 2)), Color(0.9, 0.75, 0.3, 0.9))
		c.draw_texture_rect(Tema.ui("slot_sombra"), r, false)
		var mold := "slot_moldura"
		if pressionado.get(i, 0.0) > t: mold = "slot_pressionado"
		elif i == hover_slot: mold = "slot_hover"
		elif not h.is_empty() and j.buffer_skill.get("slot", -1) == i: mold = "slot_ativo"
		c.draw_texture_rect(Tema.ui(mold), r, false)
		if i < 10: _tecla(c, r.position + Vector2(-4, -5), "tecla_%d" % ((i + 1) % 10), "skill_%d" % (i + 1))
		elif not h.is_empty(): _txt(c, r.position + Vector2(4, 9), "⇧%d" % (i - 9), 8, Color("#d8c08a"), Tema.FONTE_PIXEL, -1, 2)
		if not h.is_empty() and Jogador.skill_no_auto(j, i): _selo_auto(c, r)
	_desenhar_evasao(c, j)
	# modo automático (tecla Z): "AUTO" dourado sobre a barra de skills e moldura pulsando no slot da skill automática
	if j.aux.get("auto", false):
		var pulso := 0.65 + 0.35 * sin(t * 4.0)
		var ca := Vector2(500, 50)
		c.draw_arc(ca, 9.0, t * 3.0, t * 3.0 + TAU * 0.75, 18, Color(0.94, 0.78, 0.32, pulso), 2.0)
		c.draw_circle(ca, 3.0, Color(0.94, 0.78, 0.32, pulso))
		_txt(c, Vector2(540, 56), "AUTO", 16, Color(0.98, 0.82, 0.35, 0.75 + 0.25 * pulso), Tema.FONTE_TITULO, 0, 4)
		for sa in mini(10, j.skills_slots.size()):
			if Jogador.skill_no_auto(j, sa):
				c.draw_rect(_slot_rect(sa).grow(1.0 + 2.0 * pulso), Color(0.98, 0.8, 0.3, 0.5 + 0.4 * pulso), false, 2.0)
	# cinto
	for i in 4:
		var r := _cinto_rect(i)
		var info := _cinto_item(i)
		if info[0] != "":
			var tx := Tema.icone_item(info[0])
			if tx.size() == 2: c.draw_texture_rect_region(tx[0], Rect2(r.position + Vector2(5, 5), Vector2(36, 36)), tx[1], Color.WHITE if info[1] > 0 else Color(0.35, 0.35, 0.35))
			_txt(c, r.position + Vector2(42, 42), "%d" % info[1], 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 1, 2)
		var cdp := float(j.aux.get("cd_pocao", 0.0))
		if cdp > 0.0 and i < 2: _setor(c, r.position + Vector2(23, 23), 18.0, cdp / Jogador.CD_POCAO, Color(0, 0, 0, 0.6))
		c.draw_texture(Tema.ui("cinto_sombra"), r.position)
		c.draw_texture(Tema.ui("cinto_hover" if i == hover_cinto else "cinto_moldura"), r.position)
		_tecla(c, r.position + Vector2(-4, -5), "tecla_" + CINTO[i][1].to_lower(), CINTO_PAD[i])
	# menu
	for i in 6:
		var r := _menu_rect(i)
		var nm: String = MENU[i]
		var aberto: bool = MENU_JANELA.has(nm) and game.janelas.aberta(MENU_JANELA[nm])
		c.draw_texture(Tema.ui("botao_%s_%s" % [nm, "hover" if i == hover_menu or aberto else "normal"]), r.position)
		if nm == "personagem" and j.pontos > 0:
			c.draw_circle(r.position + Vector2(31, 3), 4.0, Color(1.0, 0.75, 0.2, 0.7 + 0.3 * sin(t * 5.0)))

# =================================================================== barra do pet (Cultista, 0.9.3)
## Arte: pet_barra.png (pintada pelo Jefin; retrato, molduras, ícones e nomes já vêm nela). O código desenha por
## cima a vida do familiar, o modo ativo, o hover e o retrato apagado enquanto ele volta do abismo.
const PET_CMD := ["atacar", "proteger", "teleportar", "agressivo", "passivo"]
const PET_NOME := {"atacar": "Atacar: o familiar vai no seu alvo", "proteger": "Proteger: ataca quem bater em você ou nele",
	"teleportar": "Teleportar: o familiar volta para o seu lado", "agressivo": "Modo agressivo: ataca monstros perto de você",
	"passivo": "Modo passivo: só segue, não ataca"}
const PET_BOTAO := [Rect2(80, 8, 54, 49), Rect2(140, 8, 53, 49), Rect2(198, 8, 54, 49), Rect2(258, 8, 57, 49), Rect2(321, 8, 53, 49)]
const PET_RETRATO := Rect2(15, 5, 54, 53)

func _montar_pet() -> void:
	pet_ui = _painel(_desenhar_pet)
	pet_ui.size = Vector2(387, 63)
	pet_ui.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	pet_ui.mouse_filter = Control.MOUSE_FILTER_STOP
	pet_ui.entrada = _entrada_pet
	pet_ui.mouse_exited.connect(func(): hover_pet = -1; esconder_tip())
	pet_ui.visible = false
	raiz.add_child(pet_ui)

## O familiar do jogador (vivo ou voltando do abismo), procurado pelo dono: serve no solo e em rede.
func _meu_pet() -> Ent:
	var j := _jog()
	if j == null or j.classe != "cultista": return null
	for e: Ent in game.sim.ents.values():
		if e.tipo == "invocacao" and e.dono == j.id and String(e.kind).begins_with("familiar_"): return e
	return null

func _posicionar_pet() -> void:
	var j := _jog()
	pet_ui.visible = j != null and j.classe == "cultista" and _meu_pet() != null
	if not pet_ui.visible: return
	var sobe := 48.0 if _n_slots() > 10 else 0.0   # com a fileira da evolução (Shift+1..5), a barra do pet sobe
	pet_ui.offset_left = -640 + 185; pet_ui.offset_right = pet_ui.offset_left + 387
	pet_ui.offset_top = -147 - sobe; pet_ui.offset_bottom = pet_ui.offset_top + 63

func _entrada_pet(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var h := -1
		for i in PET_BOTAO.size(): if PET_BOTAO[i].has_point(ev.position): h = i
		if h != hover_pet:
			hover_pet = h
			if h >= 0: mostrar_tip("[font_size=14]%s[/font_size]" % PET_NOME[PET_CMD[h]])
			elif PET_RETRATO.has_point(ev.position): mostrar_tip(_tip_pet())
			else: esconder_tip()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if hover_pet >= 0:
			game.audio.tocar("ui/clique", null, -6.0)
			game.cmd("pet", [PET_CMD[hover_pet]])
			pressionado["pet_%d" % hover_pet] = t + 0.18
		pet_ui.accept_event()

func _tip_pet() -> String:
	var f := _meu_pet()
	if f == null: return ""
	var est := "voltando do abismo" if not f.vivo else "%d / %d de vida" % [ceili(f.hp), ceili(f.hp_max)]
	return "[font_size=15][b]%s[/b][/font_size]\n[font_size=13]%s · cura 10%% do dano que você causa[/font_size]" % [f.nome, est]

func _desenhar_pet(c: Painel) -> void:
	var f := _meu_pet()
	var j := _jog()
	if f == null or j == null: return
	var tex := Tema.ui("pet_barra")
	if tex: c.draw_texture_rect(tex, Rect2(Vector2.ZERO, c.size), false)
	# retrato apagado enquanto o familiar volta sozinho (30 s)
	if not f.vivo:
		c.draw_rect(PET_RETRATO, Color(0.02, 0.01, 0.01, 0.7))
		_txt(c, PET_RETRATO.get_center() + Vector2(0, 4), "VOLTANDO", 7, Color("#c9a27a"), Tema.FONTE_PIXEL, 0, 2)
	# vida do familiar no pé do retrato
	var hr := Rect2(PET_RETRATO.position.x + 2, PET_RETRATO.end.y - 7, PET_RETRATO.size.x - 4, 5)
	_barra(c, hr, f.frac_hp() if f.vivo else 0.0, Color("#b3261e") if f.frac_hp() > 0.3 else Color("#ff4a2a"))
	# modo ativo: moldura de latão acesa; hover e clique clareiam o botão
	var modo: String = j.aux.get("pet_modo", "proteger")
	for i in PET_BOTAO.size():
		var r: Rect2 = PET_BOTAO[i]
		if PET_CMD[i] == modo:
			var pulso := 0.75 + 0.25 * sin(t * 3.0)
			c.draw_rect(r.grow(1.0), Color(0.98, 0.78, 0.32, 0.85 * pulso), false, 2.0)
		if float(pressionado.get("pet_%d" % i, 0.0)) > t: c.draw_rect(r, Color(1.0, 0.85, 0.5, 0.22))
		elif i == hover_pet: c.draw_rect(r, Color(1.0, 0.95, 0.8, 0.10))
	if not f.vivo:
		for i in [0, 2]: c.draw_rect(PET_BOTAO[i], Color(0, 0, 0, 0.45))   # Atacar e Teleportar esperam o familiar voltar
	# o "AUTO" da barra fica embaixo desta; repete ao lado
	if j.aux.get("auto", false):
		var pulso2 := 0.65 + 0.35 * sin(t * 4.0)
		_txt(c, Vector2(c.size.x + 34, 40), "AUTO", 16, Color(0.98, 0.82, 0.35, 0.75 + 0.25 * pulso2), Tema.FONTE_TITULO, 0, 4)

## Esquiva: ícone pintado (quando chegar: atlas skills_40, chave <classe>_evasao), duas cargas em losango de latão
## embaixo do slot e a carga que está voltando enchendo; sem carga, o setor escuro com os segundos.
func _desenhar_evasao(c: CanvasItem, j: Ent) -> void:
	var h := Evasao.defn(j)
	if h.is_empty(): return
	var r := _evasao_rect()
	var n := Evasao.cargas(j)
	var mx := Evasao.cargas_max()
	var rc := float(j.aux.get("ev_recarga", 0.0))
	c.draw_texture_rect(Tema.ui("slot_sombra"), r, false)
	var ic := Tema.icone_skill(j.classe, "evasao")
	var mod := Color.WHITE if n > 0 else Color(0.5, 0.5, 0.55)
	if ic.size() == 2: c.draw_texture_rect_region(ic[0], Rect2(r.position + Vector2(6, 6) * r.size.x / 52.0, Vector2(40, 40) * r.size.x / 52.0), ic[1], mod)
	else: _txt(c, r.get_center() + Vector2(0, 4), String(h["nome"]).left(3).to_upper(), 11, Color("#d8c08a") * mod, Tema.FONTE_PIXEL, 0, 2)   # ícone pintado ainda não chegou (LISTA.md)
	if n <= 0 and rc > 0.0:
		_setor(c, r.get_center(), 19.0, rc / Evasao.recarga(), Color(0, 0, 0, 0.72))
		_txt(c, r.get_center() + Vector2(0, 5), ("%.1f" % rc) if rc < 3.0 else ("%d" % ceili(rc)), 13, Color("#f6ead0"))
	c.draw_texture_rect(Tema.ui("slot_hover" if hover_evasao else "slot_moldura"), r, false)
	# cargas: losangos de latão embaixo do slot
	for k in mx:
		var p := Vector2(r.get_center().x + (k - (mx - 1) * 0.5) * 16.0, r.end.y + 6.0)
		var fora := PackedVector2Array([p + Vector2(0, -6), p + Vector2(6, 0), p + Vector2(0, 6), p + Vector2(-6, 0)])
		c.draw_colored_polygon(fora, Color(0.07, 0.05, 0.03, 0.92))
		var cheio := 1.0 if k < n else (1.0 - rc / Evasao.recarga() if k == n and rc > 0.0 else 0.0)
		if cheio > 0.0:
			var e := 4.0 * cheio
			c.draw_colored_polygon(PackedVector2Array([p + Vector2(0, -e), p + Vector2(e, 0), p + Vector2(0, e), p + Vector2(-e, 0)]),
				Color(0.86, 0.62, 0.24) if k < n else Color(0.55, 0.38, 0.14))
		c.draw_polyline(PackedVector2Array([fora[0], fora[1], fora[2], fora[3], fora[0]]), Color(0.94, 0.78, 0.36) if k < n else Color(0.5, 0.4, 0.25), 1.0)
	if Controle.pad_ativo(): _tecla(c, r.position + Vector2(-4, -5), "", "evadir")
	elif Tema.ui("tecla_mouse_dir"): c.draw_texture(Tema.ui("tecla_mouse_dir"), r.position + Vector2(-4, -5))

func _tip_evasao() -> String:
	var j := _jog()
	var h := Evasao.defn(j) if j else {}
	if h.is_empty(): return ""
	var linha := "%.1f tiles · %d cargas · %d s cada · sem custo" % [float(h["deslocamento"]), Evasao.cargas_max(), int(Evasao.recarga())]
	return "[font_size=15][b]%s[/b][/font_size]  [color=#a89f8c]esquiva · botão direito ou Espaço[/color]\n[font_size=13]%s[/font_size]\n[color=#c9b88a]%s[/color]" % [h["nome"], h.get("descricao", ""), linha]

## Selo de latão no canto do slot: a skill está no modo automático (clique direito liga/desliga).
func _selo_auto(c: CanvasItem, r: Rect2) -> void:
	var p := r.position + Vector2(44, 44)
	var losango := PackedVector2Array([p + Vector2(0, -7), p + Vector2(7, 0), p + Vector2(0, 7), p + Vector2(-7, 0)])
	c.draw_colored_polygon(losango, Color(0.07, 0.05, 0.03, 0.92))
	var dentro := PackedVector2Array([p + Vector2(0, -5), p + Vector2(5, 0), p + Vector2(0, 5), p + Vector2(-5, 0)])
	c.draw_colored_polygon(dentro, Color(0.55, 0.38, 0.14))
	c.draw_polyline(PackedVector2Array([losango[0], losango[1], losango[2], losango[3], losango[0]]), Color(0.94, 0.78, 0.36), 1.0)
	_txt(c, p + Vector2(0, 3), "A", 7, Color("#fff0c0"), Tema.FONTE_PIXEL, 0, 2)

func _cinto_item(i: int) -> Array:
	var j := _jog()
	var ordem: Array
	match CINTO[i][0]:
		"vida": ordem = ["pocao_vida_m", "pocao_vida_p", "tonico_graxa", "hostia_negra", "caldo_cardo_comum", "pao_duro"]
		"recurso": ordem = ["pocao_recurso_m", "pocao_recurso_p"]
		"antidoto": ordem = ["antidoto_querosene", "agua_benta"]
		"vela": ordem = ["vela_retorno"]
	var total := 0
	var primeiro := ""
	for id in ordem:
		var q := Itens.contar(j.inv, id)
		if q > 0 and primeiro == "": primeiro = id
		total += q
	if primeiro == "": primeiro = ordem[0] if j.classe != "cultista" or CINTO[i][0] != "recurso" else ""
	return [primeiro, total]

## Etiqueta de atalho no canto do slot: a tecla, ou o botão do controle quando ele está em uso.
## Combinação (LT + botão): o LT pequeno atrás e o botão na frente.
func _tecla(c: CanvasItem, p: Vector2, tecla: String, acao_pad: String) -> void:
	if Controle.pad_ativo():
		var gl: Array = Controle.inst.glifos(Controle.inst.mapa.get(acao_pad, ""))
		if gl.size() == 2:
			c.draw_texture_rect(gl[0], Rect2(p + Vector2(-3, -3), Vector2(15, 15)), false)
			c.draw_texture(gl[1], p + Vector2(6, 2))
			return
		if gl.size() == 1: c.draw_texture(gl[0], p + Vector2(-1, -2))
		return   # sem botão no controle (slot 10): sem etiqueta
	c.draw_texture(Tema.ui(tecla), p)

func _setor(c: CanvasItem, centro: Vector2, r: float, frac: float, cor: Color) -> void:
	if frac <= 0.0: return
	var pts := PackedVector2Array([centro])
	var n := 24
	for k in n + 1:
		var a := -PI * 0.5 + TAU * frac * float(k) / n
		pts.append(centro + Vector2(cos(a), sin(a)) * r * 1.42)
	var clip := Rect2(centro - Vector2(r, r), Vector2(r, r) * 2.0)
	for k in pts.size(): pts[k] = pts[k].clamp(clip.position, clip.end)
	c.draw_colored_polygon(pts, cor)

func _tip_skill(i: int) -> String:
	var j := _jog()
	var h := Jogador.skill_def(j, i)
	if h.is_empty(): return ""
	var sk := Defs.skill(j.classe, h["id"])
	var nome: String = sk.get("nome", h["nome"])
	var s := "[font_size=17][color=#f0dca0]%s[/color][/font_size]\n" % nome
	var linha: Array = []
	if h.get("passiva", false): linha.append("Passiva")
	else:
		var cst := Jogador.custo(j, h)
		if cst > 0: linha.append(("%d de vida" % roundi(cst)) if j.classe == "cultista" else ("%d de %s" % [roundi(cst), _nome_recurso().to_lower()]))
		linha.append("recarga %.1fs" % float(h.get("recarga", 0)))
		if h.has("alcance") and float(h["alcance"]) > 2.0: linha.append("alcance %d" % int(h["alcance"]))
		if h.has("cargas"): linha.append("%d cargas" % int(h["cargas"]))
	s += "[color=#a89f8c][i]%s[/i][/color]\n" % " · ".join(linha)
	s += "[color=#e8dfc9]%s[/color]" % sk.get("descricao", h.get("descricao", ""))
	for ef in sk.get("efeitos", []):
		s += "\n[color=#9cc8ff]• %s[/color]" % ef
	if j.nivel < int(h["nivel"]): s += "\n[color=#ff6a4a]Libera no nível %d[/color]" % int(h["nivel"])
	if not h.get("passiva", false):
		s += "\n[color=#e0b84a]%s[/color] [color=#7d7466]· clique direito muda · Shift+Z ajustes[/color]" % ("No automático (Z)" if Jogador.skill_no_auto(j, i) else "Fora do automático")
	return s

func _tip_cinto(i: int) -> String:
	var info := _cinto_item(i)
	var nomes := {"vida": "Poção de vida", "recurso": "Poção de recurso", "antidoto": "Antídoto", "vela": "Vela de Retorno"}
	var s := "[font_size=16][color=#f0dca0]%s[/color][/font_size]  [color=#a89f8c](%s)[/color]\n" % [Defs.ITENS.get(info[0], {}).get("nome", nomes[CINTO[i][0]]), CINTO[i][1]]
	s += "Na mochila: %d" % info[1]
	if CINTO[i][0] == "vela": s += "\n[color=#a89f8c]Volta ao acampamento depois de 3 s parado.[/color]"
	return s

# =================================================================== retrato, buffs
func _montar_topo() -> void:
	topo_esq = _painel(_desenhar_topo)
	topo_esq.position = Vector2(10, 10)
	topo_esq.size = Vector2(280, 118)
	raiz.add_child(topo_esq)

func _desenhar_topo(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	if Tema.ui("retrato_painel"): _desenhar_retrato(c, j)
	else: _desenhar_retrato_simples(c, j)
	_desenhar_buffs(c, j, 92.0 if Tema.ui("retrato_painel") else 82.0)

## Retrato no painel Ferrugem Sagrada (retrato_painel.png, 272x84): poço quadrado de latão com o sprite,
## medalhão do nível e sulcos gravados para vida e recurso. retrato_vidro.png vai por cima do sprite.
func _desenhar_retrato(c: Painel, j: Ent) -> void:
	c.draw_texture(Tema.ui("retrato_painel"), Vector2.ZERO)
	var meta: Dictionary = Defs.SPR.get(j.classe, {})
	if not meta.is_empty():
		var tex := Tema.tex(meta["anims"]["idle"]["file"])
		var anc: Array = meta["anchor"]
		if tex: c.draw_texture_rect_region(tex, Rect2(12, 12, 56, 56), Rect2(anc[0] - 28, anc[1] - 116, 56, 56))
	var vidro := Tema.ui("retrato_vidro")
	if vidro: c.draw_texture(vidro, Vector2.ZERO)
	_txt(c, Vector2(71, 77), "%d" % j.nivel, 12 if j.nivel < 100 else 10, Color("#f0dca0"), Tema.FONTE_TITULO, 0, 3)
	_txt(c, Vector2(92, 27), j.nome, 15, Color("#f0dca0"), Tema.FONTE_TITULO, -1, 3)
	_txt(c, Vector2(92, 41), _linha_classe(j), 12, Color("#a89f8c"), Tema.FONTE_ITALICO, -1, 2)
	_encher(c, Rect2(90, 50, 166, 9), j.frac_hp(), Color(0.72, 0.1, 0.08))
	if j.rec_max > 0.0: _encher(c, Rect2(90, 63, 166, 6), j.rec / j.rec_max, _cor_recurso())

## Líquido dentro de um sulco já desenhado na arte (sem caixa em volta).
func _encher(c: CanvasItem, r: Rect2, frac: float, cor: Color) -> void:
	var f := Rect2(r.position, Vector2(r.size.x * clampf(frac, 0.0, 1.0), r.size.y))
	if f.size.x <= 0.0: return
	c.draw_rect(f, cor.darkened(0.25))
	c.draw_rect(Rect2(f.position + Vector2(0, 1), Vector2(f.size.x, maxf(1.0, r.size.y * 0.35))), cor.lightened(0.15))
	c.draw_rect(Rect2(f.position.x, f.end.y - 1, f.size.x, 1), Color(0, 0, 0, 0.45))
	c.draw_rect(Rect2(f.end.x - 1, f.position.y, 1, f.size.y), cor.lightened(0.45))

func _linha_classe(j: Ent) -> String:
	var cls: Dictionary = {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante", "warlord": "Warlord"}
	return "%s · %s" % [Evolucao.nome_classe(j) if j.evolucao != "" else cls.get(j.classe, j.classe), "Vigília" if j.faccao == "vigilia" else "Arautos do Juízo"]

func _cor_recurso() -> Color:
	var cr := {"folego": Color(0.3, 0.55, 0.9), "graca": Color(0.95, 0.85, 0.45), "furia": Color(0.85, 0.35, 0.1), "brasa": Color(1.0, 0.45, 0.1), "carga": Color(0.35, 0.8, 1.0)}
	return cr.get(_liquido_recurso(), Color(0.5, 0.5, 0.8))

## Visual antigo, quando a peça do retrato não existe.
func _desenhar_retrato_simples(c: Painel, j: Ent) -> void:
	var r := Rect2(0, 0, 262, 76)
	c.draw_style_box(Tema.caixa(Color(0.07, 0.055, 0.045, 0.9), Color(0.42, 0.34, 0.2), 2, 3), r)
	# retrato: primeiro quadro do idle virado para o sul
	var cen := Vector2(38, 38)
	c.draw_circle(cen, 30, Color(0.03, 0.025, 0.02))
	var meta: Dictionary = Defs.SPR.get(j.classe, {})
	if not meta.is_empty():
		var tex := Tema.tex(meta["anims"]["idle"]["file"])
		var fr: Array = meta["frame"]
		var anc: Array = meta["anchor"]
		if tex:
			var src := Rect2(anc[0] - 30, anc[1] - 118, 60, 70)
			c.draw_texture_rect_region(tex, Rect2(cen - Vector2(27, 31), Vector2(54, 63)), src)
	_arco(c, cen, 31, Color(0.69, 0.55, 0.31), 2.0)
	c.draw_circle(Vector2(62, 62), 11, Color(0.08, 0.06, 0.05))
	_arco(c, Vector2(62, 62), 11, Color(0.69, 0.55, 0.31), 1.5)
	_txt(c, Vector2(62, 67), "%d" % j.nivel, 12, Color("#f0dca0"))
	_txt(c, Vector2(82, 24), j.nome, 15, Color("#f0dca0"), Tema.FONTE_TITULO, -1)
	_txt(c, Vector2(82, 40), _linha_classe(j), 12, Color("#a89f8c"), Tema.FONTE_ITALICO, -1, 2)
	_barra(c, Rect2(82, 48, 168, 8), j.frac_hp(), Color(0.72, 0.1, 0.08))
	if j.rec_max > 0.0: _barra(c, Rect2(82, 60, 168, 5), j.rec / j.rec_max, _cor_recurso())

## Buffs e status embaixo do retrato.
func _desenhar_buffs(c: Painel, j: Ent, y: float) -> void:
	var x := 0.0
	var agora := []
	for b in j.buffs: agora.append([b["id"], float(b["t"]), Color(0.4, 0.75, 0.35)])
	for s in j.status: agora.append([s, float(j.status[s].get("t", 0.0)), Color(0.85, 0.25, 0.2)])
	for a in agora:
		var nome: String = STATUS_NOME.get(a[0], Defs.ITENS.get(a[0], {}).get("nome", str(a[0]).replace("_", " ").capitalize()))
		var w := Tema.FONTE_TEXTO.get_string_size(nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 30
		var rr := Rect2(x, y, w, 18)
		c.draw_rect(rr, Color(0.06, 0.05, 0.04, 0.85))
		c.draw_rect(rr, a[2], false, 1.0)
		c.draw_string(Tema.FONTE_TEXTO, Vector2(x + 5, y + 14), nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, a[2].lightened(0.35))
		c.draw_string(Tema.FONTE_PIXEL, Vector2(x + w - 22, y + 13), "%d" % ceili(a[1]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#e8dfc9"))
		x += w + 4

func _arco(c: CanvasItem, cen: Vector2, r: float, cor: Color, w: float) -> void:
	c.draw_arc(cen, r, 0, TAU, 48, cor, w, true)

# =================================================================== alvo e chefe
func _montar_alvo() -> void:
	alvo_ui = _painel(_desenhar_alvo)
	alvo_ui.set_anchors_preset(Control.PRESET_CENTER_TOP)
	alvo_ui.offset_left = -200; alvo_ui.offset_right = 200; alvo_ui.offset_top = 10; alvo_ui.offset_bottom = 90
	raiz.add_child(alvo_ui)

func _desenhar_alvo(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	var sim: WorldSim = game.sim
	if not chefe_d.is_empty():
		var b: Ent = sim.ents.get(int(chefe_d.get("id", -1)))
		if b != null and b.vivo:
			_desenhar_chefe(c, b); return
	var id: int = j.alvo if j.alvo != -1 else game.hover_id
	var e: Ent = sim.ents.get(id)
	if e == null or not e.vivo or e.tipo in ["npc", "jogador"] or (e.tipo == "objeto" and not e.alvejavel): return
	if e.tipo == "objeto" and e.kind != "pilha_de_mortos": return
	var r := Rect2(40, 0, 320, 48)
	# 0.9.8: quatro estilos de barra, pela categoria: comum, elite (moldura de ouro), especial (azul, brilho e losango)
	var borda := Color(0.42, 0.34, 0.2)
	if e.arquetipo == "elite": borda = Color(0.85, 0.66, 0.25)
	elif e.arquetipo == "raro":
		borda = Color(0.5, 0.72, 1.0)
		c.draw_circle(Vector2(r.position.x + 14, 24), 26.0, Color(0.5, 0.72, 1.0, 0.09))
		var d := Vector2(r.position.x + 14, 24)
		c.draw_colored_polygon(PackedVector2Array([d + Vector2(0, -6), d + Vector2(6, 0), d + Vector2(0, 6), d + Vector2(-6, 0)]), Color(0.6, 0.8, 1.0))
	c.draw_style_box(Tema.caixa(Color(0.07, 0.055, 0.045, 0.88), borda, 2, 3), r)
	var cn := Color("#e8dfc9")
	if e.arquetipo == "elite": cn = Color("#e0b84a")
	elif e.arquetipo == "raro": cn = Color("#7fb8ff")
	_txt(c, Vector2(52, 19), e.nome, 15, cn, Tema.FONTE_TITULO, -1)
	var sub := "Nv. %d" % e.nivel
	if e.arquetipo in ["elite", "raro"]: sub = ("Elite · " if e.arquetipo == "elite" else "Raro · ") + sub
	_txt(c, Vector2(348, 19), sub, 12, Color("#a89f8c"), Tema.FONTE_ITALICO, 1, 2)
	_barra(c, Rect2(52, 27, 296, 9), e.frac_hp(), Color(0.7, 0.09, 0.06))
	_txt(c, Vector2(200, 35), "%d%%" % ceili(e.frac_hp() * 100.0), 8, Color("#f6ead0"), Tema.FONTE_PIXEL, 0, 2)
	if e.postura_max > 0:
		var pf := 1.0 - e.postura / e.postura_max
		if e.quebrado_t > 0.0: pf = 1.0
		_barra(c, Rect2(52, 39, 296, 3), pf, Color(0.95, 0.7, 0.2) if e.quebrado_t <= 0.0 else Color(1, 1, 1))

func _desenhar_chefe(c: Painel, b: Ent) -> void:
	var r := Rect2(-80, 0, 560, 70)
	c.draw_style_box(Tema.caixa(Color(0.06, 0.03, 0.03, 0.92), Color(0.55, 0.16, 0.1), 2, 3), r)
	var tit: String = chefe_d.get("nome", b.nome)
	_txt(c, Vector2(200, 28), tit, 17, Color("#ffcf9a"), Tema.FONTE_GOTICA, 0, 3)   # 0.9.8: menor, para não tapar a fala do chefe
	var nf: String = chefe_d.get("nome_fase", "")
	_txt(c, Vector2(462, 22), ("Fase %d" % int(chefe_d.get("fase", 1))) + ((" · " + nf) if nf != "" else ""), 11, Color("#c8a080"), Tema.FONTE_ITALICO, 1, 2)
	c.draw_rect(r.grow(-4), Color(0.55, 0.16, 0.1, 0.7), false, 1.0)   # 0.9.8: moldura interna do chefe de área
	var br := Rect2(-62, 36, 524, 14)
	_barra(c, br, b.frac_hp(), Color(0.62, 0.06, 0.04))
	for m in chefe_d.get("marcas", []):
		var f := float(m)
		if f >= 1.0 or f <= 0.0: continue
		var x := br.position.x + br.size.x * f
		c.draw_line(Vector2(x, br.position.y - 2), Vector2(x, br.end.y + 2), Color(0.95, 0.85, 0.6, 0.9), 2.0)
	_txt(c, Vector2(200, 48), "%d / %d" % [ceili(b.hp), ceili(b.hp_max)], 9, Color("#f6ead0"), Tema.FONTE_PIXEL, 0, 2)
	if b.postura_max > 0:
		var pf := 1.0 - b.postura / b.postura_max
		if b.quebrado_t > 0.0: pf = 1.0
		_barra(c, Rect2(-62, 55, 524, 4), pf, Color(0.95, 0.7, 0.2) if b.quebrado_t <= 0.0 else Color(1, 1, 1))
	if b.escudo > 0.0:
		_barra(c, Rect2(-62, 62, 524, 3), b.escudo / maxf(1.0, b.hp_max * 0.15), Color(0.85, 0.85, 1.0))

func chefe(d: Dictionary) -> void:
	if d.get("fim", false):
		if d.get("morto", false): banner_mostrar("INIMIGO ABATIDO", chefe_d.get("nome", ""), Color("#ffcf9a"))
		chefe_d = {}
		return
	if d.get("inicio", false):
		chefe_d = d.duplicate()
		banner_mostrar(d.get("nome", ""), "", Color("#ff8a6a"))
	else:
		chefe_d["fase"] = d.get("fase", 1)
		chefe_d["nome_fase"] = d.get("nome_fase", "")
		if d.get("nome_fase", "") != "": aviso(d["nome_fase"], Color("#ff9a6a"))

# =================================================================== minimapa
func ao_trocar_mapa() -> void:
	chefe_d = {}
	var m: Dictionary = game.mapa
	var w := int(m["w"]); var h := int(m["h"])
	var img := Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	var grade: Array = m["grade"]
	var ter: Array = m["terreno"]
	for y in h:
		var gl: String = grade[y]
		var tl: String = ter[y]
		for x in w:
			var ch := tl[x]
			var parede := gl[x] == "#"
			if ch == " " or ch == "h":
				continue
			var cor: Color = game.cores_piso.get(ch, Color(0.3, 0.27, 0.22))
			cor = cor.lerp(Color(0.5, 0.45, 0.35), 0.15) * 1.35
			if parede: cor = cor.darkened(0.6)
			cor.a = 1.0
			img.set_pixel(x + 1, y + 1, cor)
	mini_tex = ImageTexture.create_from_image(img)
	mini_zoom = 3.0 if m.get("exterior", false) else 4.0
	if mapa_ui: mapa_ui.queue_redraw()

func _montar_minimapa() -> void:
	minimapa = _painel(_desenhar_minimapa)
	minimapa.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	minimapa.offset_left = -180; minimapa.offset_right = -10; minimapa.offset_top = 10; minimapa.offset_bottom = 200
	minimapa.mouse_filter = Control.MOUSE_FILTER_STOP
	minimapa.dentro = func(p: Vector2) -> bool: return p.distance_to(Vector2(85, 85)) < 80
	minimapa.entrada = func(ev: InputEvent):
		if ev is InputEventMouseButton and ev.pressed:
			if ev.button_index == MOUSE_BUTTON_WHEEL_UP: mini_zoom = minf(8.0, mini_zoom * 1.2)
			elif ev.button_index == MOUSE_BUTTON_WHEEL_DOWN: mini_zoom = maxf(1.5, mini_zoom / 1.2)
			elif ev.button_index == MOUSE_BUTTON_LEFT: alternar_mapa()
			minimapa.accept_event()
	raiz.add_child(minimapa)
	rastreador = RichTextLabel.new()
	rastreador.bbcode_enabled = true
	rastreador.fit_content = true
	rastreador.scroll_active = false
	rastreador.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rastreador.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	rastreador.offset_left = -270; rastreador.offset_right = -14; rastreador.offset_top = 212; rastreador.offset_bottom = 520
	rastreador.add_theme_font_override("normal_font", Tema.FONTE_TEXTO)
	rastreador.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	rastreador.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	rastreador.add_theme_font_size_override("normal_font_size", 14)
	rastreador.add_theme_font_size_override("bold_font_size", 13)
	rastreador.add_theme_constant_override("outline_size", 4)
	rastreador.add_theme_color_override("font_outline_color", Color(0.02, 0.015, 0.015, 0.9))
	raiz.add_child(rastreador)

## Desenha o mapa em losango (iso) dentro de um polígono qualquer: cada vértice ganha a UV do tile embaixo dele.
func _desenhar_mapa_iso(c: CanvasItem, pts: PackedVector2Array, centro_tela: Vector2, centro_mundo: Vector2, px_por_tile: float) -> void:
	if mini_tex == null: return
	var uvs := PackedVector2Array()
	var w := float(mini_tex.get_width()); var h := float(mini_tex.get_height())
	for p in pts:
		var d := (p - centro_tela) / px_por_tile
		# tela iso: sx = (x+y), sy = (x-y)/2  ->  x = (sx + 2sy)/2, y = (sx - 2sy)/2
		var wx := centro_mundo.x + (d.x + 2.0 * d.y) * 0.5 + 1.0
		var wy := centro_mundo.y + (d.x - 2.0 * d.y) * 0.5 + 1.0
		uvs.append(Vector2(wx / w, wy / h))
	var cores := PackedColorArray(); cores.resize(pts.size()); cores.fill(Color.WHITE)
	c.draw_polygon(pts, cores, uvs, mini_tex)

func _mundo_para_mini(p: Vector2, centro_tela: Vector2, centro_mundo: Vector2, k: float) -> Vector2:
	var d := p - centro_mundo
	return centro_tela + Vector2(d.x + d.y, (d.x - d.y) * 0.5) * k

func _desenhar_minimapa(c: Painel) -> void:
	var j := _jog()
	if j == null: return
	var cen := Vector2(85, 85)
	var r := 70.0
	c.draw_circle(cen, r + 8, Color(0.03, 0.025, 0.02, 0.92))
	var pts := PackedVector2Array()
	for i in 48: pts.append(cen + Vector2(cos(TAU * i / 48.0), sin(TAU * i / 48.0)) * r)
	_desenhar_mapa_iso(c, pts, cen, j.pos, mini_zoom)
	_marcadores(c, cen, j.pos, mini_zoom, r)
	_arco(c, cen, r + 1, Color(0.2, 0.15, 0.1), 3.0)
	_arco(c, cen, r + 5, Color(0.69, 0.55, 0.31), 4.0)
	_arco(c, cen, r + 8, Color(0.25, 0.19, 0.12), 2.0)
	for i in 8:
		var a := TAU * i / 8.0
		c.draw_circle(cen + Vector2(cos(a), sin(a)) * (r + 5), 2.2, Color(0.85, 0.72, 0.45))
	# norte iso: +x-y fica para cima-direita; o "N" marca o topo da tela
	_txt(c, cen + Vector2(0, -r - 1), "N", 11, Color("#ff8a6a"), Tema.FONTE_TITULO, 0, 3)
	var zn: String = Defs.nome_local(j.zona) if j.zona != "" else game.mapa.get("nome", "")
	var placa := Rect2(cen.x - 82, cen.y + r + 10, 164, 20)
	c.draw_style_box(Tema.caixa(Color(0.08, 0.06, 0.05, 0.92), Color(0.42, 0.34, 0.2), 1, 2), placa)
	var nz: String = zn.to_upper()
	var tam := 10
	while Tema.FONTE_TITULO.get_string_size(nz, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x > 156 and tam > 7: tam -= 1
	_txt(c, Vector2(cen.x, placa.position.y + 14), nz, tam, Color("#e0c890"), Tema.FONTE_TITULO, 0, 2)

func _marcadores(c: CanvasItem, cen: Vector2, cm: Vector2, k: float, raio: float) -> void:
	var sim: WorldSim = game.sim
	var j := _jog()
	for e: Ent in sim.ents.values():
		if not e.vivo or e.invisivel: continue
		var p := _mundo_para_mini(e.pos, cen, cm, k)
		if p.distance_to(cen) > raio - 3: continue
		match e.tipo:
			"monstro":
				var cm2 := Color(0.85, 0.15, 0.1)
				if e.aux.get("neutro", false) and e.estado in ["ocioso", "vagar"]: cm2 = Color(0.9, 0.78, 0.2)
				c.draw_circle(p, 2.2 if e.arquetipo == "normal" else 3.0, cm2 if e.arquetipo == "normal" else Color(1.0, 0.55, 0.15))
			"chefe":
				c.draw_circle(p, 4.5, Color(0.1, 0, 0)); c.draw_circle(p, 3.5, Color(1.0, 0.25, 0.1))
			"jogador":   # outros jogadores da rede
				if e.id != j.id: c.draw_circle(p, 3.6, Color(0.05, 0.1, 0.15)); c.draw_circle(p, 2.8, Color(0.55, 0.85, 1.0))
			"npc":
				var mk := Missoes.marcador_npc(j, e.kind)
				if mk != "": _txt(c, p + Vector2(0, 5), mk, 14, Color(1, 0.82, 0.25) if mk == "!" else Color(0.75, 0.95, 0.4), Tema.FONTE_GOTICA, 0, 2)
				else: c.draw_circle(p, 2.5, Color(0.95, 0.85, 0.5))
			"objeto":
				if e.kind == "bau" and not e.aux.get("aberto", false) and game.objs.has(e.id) and game.objs[e.id].visible:
					c.draw_rect(Rect2(p - Vector2(2.5, 2), Vector2(5, 4)), Color(0.95, 0.75, 0.3))
				elif e.kind == "portal" or (e.kind == "interativo" and Defs.OBJETOS.get(e.aux.get("obj", ""), {}).has("leva_para")):
					c.draw_circle(p, 3.5, Color(0.4, 0.7, 1.0)); c.draw_circle(p, 1.5, Color(0.9, 0.95, 1.0))
	for cid in sim.chao:
		var p2 := _mundo_para_mini(sim.chao[cid]["pos"], cen, cm, k)
		if p2.distance_to(cen) < raio - 3: c.draw_rect(Rect2(p2 - Vector2(1, 1), Vector2(2, 2)), Color(1, 1, 1, 0.8))
	# jogador: seta na direção em que olha
	var pj := _mundo_para_mini(j.pos, cen, cm, k)
	var f := Iso.to_screen(j.facing).normalized()
	var lado := Vector2(-f.y, f.x)
	c.draw_colored_polygon(PackedVector2Array([pj + f * 6, pj - f * 4 + lado * 4, pj - f * 2, pj - f * 4 - lado * 4]), Color(1, 1, 1))

# =================================================================== mapa grande
func alternar_mapa() -> void:
	if mapa_ui == null:
		mapa_ui = _painel(_desenhar_mapa_grande)
		mapa_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mapa_ui.mouse_filter = Control.MOUSE_FILTER_STOP
		mapa_ui.entrada = func(ev: InputEvent):
			if ev is InputEventMouseButton and ev.pressed: mapa_ui.visible = false; mapa_ui.accept_event()
		var cl := CanvasLayer.new(); cl.layer = 15
		add_child(cl)
		var r2 := Control.new(); r2.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); r2.mouse_filter = Control.MOUSE_FILTER_IGNORE
		r2.theme = raiz.theme
		cl.add_child(r2)
		r2.add_child(mapa_ui)
		mapa_ui.visible = false
	var abrir := not mapa_ui.visible
	if abrir: game.janelas.fechar_tudo()
	mapa_ui.visible = abrir
	game.audio.tocar("ui/abrir_janela" if mapa_ui.visible else "ui/fechar_janela", null, -6.0)

func _desenhar_mapa_grande(c: Painel) -> void:
	var j := _jog()
	var s := c.size
	c.draw_rect(Rect2(Vector2.ZERO, s), Color(0.03, 0.025, 0.02, 0.94))
	var m: Dictionary = game.mapa
	var w := float(m["w"]); var h := float(m["h"])
	var cam: Array = m.get("camera", [0, 0, w, h])
	var cm := Vector2((cam[0] + cam[2]) * 0.5, (cam[1] + cam[3]) * 0.5)
	var lw: float = (cam[2] - cam[0]) + (cam[3] - cam[1])
	var k := minf((s.x - 340) / lw, (s.y - 150) / (lw * 0.5))
	var cen := Vector2((s.x - 260) * 0.5 + 20, s.y * 0.5 + 16)
	var pts := PackedVector2Array([Vector2(20, 70), Vector2(s.x - 280, 70), Vector2(s.x - 280, s.y - 40), Vector2(20, s.y - 40)])
	if mapa_tex == null or mapa_tex_id != m.get("id", ""): _gerar_mapa_claro()
	var guarda := mini_tex
	mini_tex = mapa_tex
	_desenhar_mapa_iso(c, pts, cen, cm, k)
	mini_tex = guarda
	_marcadores(c, cen, cm, k, 99999.0)
	# objetivos das missões ativas: estrela dourada com o nome
	var legenda: Array = []
	for alvo in _alvos_missoes(j):
		var p := _mundo_para_mini(alvo[0], cen, cm, k)
		_estrela(c, p, 9.0, Color(1.0, 0.82, 0.3))
		_txt(c, p + Vector2(0, -14), alvo[1], 12, Color("#ffe6a0"), Tema.FONTE_TITULO, 0, 4)
		if not legenda.has(alvo[2]): legenda.append(alvo[2])
	# nomes das zonas: conhecidas em dourado, as outras em cinza (o nome aparece, a cor diz que você ainda não esteve lá)
	var somas := {}
	var zg: Array = m.get("zona_grade", [])
	for y in range(0, zg.size(), 3):
		var ln: String = zg[y]
		for x in range(0, ln.length(), 3):
			if ln[x] == ".": continue
			var i := ln.unicode_at(x) - 65
			if not somas.has(i): somas[i] = [Vector2.ZERO, 0]
			somas[i][0] += Vector2(x, y); somas[i][1] += 1
	var zonas: Array = m.get("zonas", [])
	for i in somas:
		if i >= zonas.size() or somas[i][1] < 6: continue
		var p := _mundo_para_mini(somas[i][0] / float(somas[i][1]), cen, cm, k)
		var conhecida: bool = j.vistas.has(zonas[i]["id"]) or zonas[i]["id"] == j.zona or Demiurgo.tem(j)   # Olho do Demiurgo: o mapa inteiro
		var niv = zonas[i].get("nivel")
		_txt(c, p, zonas[i]["nome"], 11, Color("#f6e2a8") if conhecida else Color("#a49a86"), Tema.FONTE_TITULO, 0, 5)
		if niv is Array: _txt(c, p + Vector2(0, 15), "nível %d–%d" % [int(niv[0]), int(niv[1])], 11, Color("#c8b890") if conhecida else Color("#8a8070"), Tema.FONTE_ITALICO, 0, 3)
		elif zonas[i].get("seguro", false): _txt(c, p + Vector2(0, 15), "área segura", 11, Color("#a8d890"), Tema.FONTE_ITALICO, 0, 3)
	# passagens: para onde levam (a cripta e os chefes ficam atrás delas)
	for e: Ent in game.sim.ents.values():
		if e.tipo != "objeto": continue
		var dest := ""
		if e.kind == "portal": dest = str(e.aux.get("para", ""))
		elif e.kind == "interativo": dest = str(Defs.OBJETOS.get(e.aux.get("obj", ""), {}).get("leva_para", ""))
		if dest == "" or not DESTINOS.has(dest): continue
		var pp := _mundo_para_mini(e.pos, cen, cm, k)
		_txt(c, pp + Vector2(0, 16), DESTINOS[dest], 12, Color("#9fd0ff"), Tema.FONTE_TITULO, 0, 4)
	_txt(c, Vector2((s.x - 260) * 0.5 + 20, 46), m.get("nome", ""), 30, Color("#ffcf9a"), Tema.FONTE_GOTICA, 0, 5)
	# legenda à direita
	var lx := s.x - 250.0
	var caixa := Rect2(lx, 70, 230, s.y - 110)
	c.draw_style_box(Tema.moldura_popup(), caixa)
	var y0 := 100.0
	_txt_esq(c, Vector2(lx + 16, y0), "LEGENDA", 14, Color("#e0c890"), Tema.FONTE_TITULO); y0 += 26
	var itens := [["voce", "Você"], ["estrela", "Objetivo de missão"], ["!", "Missão nova"], ["?", "Entregar missão"],
		["chefe", "Chefe"], ["mob", "Monstro agressivo"], ["neutro", "Monstro neutro"], ["portal", "Passagem"], ["bau", "Baú"]]
	for it in itens:
		var p2 := Vector2(lx + 26, y0 - 4)
		match it[0]:
			"voce": c.draw_colored_polygon(PackedVector2Array([p2 + Vector2(6, 0), p2 + Vector2(-4, 4), p2 + Vector2(-2, 0), p2 + Vector2(-4, -4)]), Color.WHITE)
			"estrela": _estrela(c, p2, 7.0, Color(1.0, 0.82, 0.3))
			"!": _txt(c, p2 + Vector2(0, 5), "!", 15, Color(1, 0.82, 0.25), Tema.FONTE_GOTICA, 0, 2)
			"?": _txt(c, p2 + Vector2(0, 5), "?", 15, Color(0.75, 0.95, 0.4), Tema.FONTE_GOTICA, 0, 2)
			"chefe": c.draw_circle(p2, 4.5, Color(0.1, 0, 0)); c.draw_circle(p2, 3.5, Color(1.0, 0.25, 0.1))
			"mob": c.draw_circle(p2, 2.6, Color(0.85, 0.15, 0.1))
			"neutro": c.draw_circle(p2, 2.6, Color(0.9, 0.78, 0.2))
			"portal": c.draw_circle(p2, 3.5, Color(0.4, 0.7, 1.0)); c.draw_circle(p2, 1.5, Color(0.9, 0.95, 1.0))
			"bau": c.draw_rect(Rect2(p2 - Vector2(3, 2.5), Vector2(6, 5)), Color(0.95, 0.75, 0.3))
		_txt_esq(c, Vector2(lx + 42, y0), it[1], 13, Color("#d8cfb8"), Tema.FONTE_TEXTO)
		y0 += 24
	if not legenda.is_empty():
		y0 += 12
		_txt_esq(c, Vector2(lx + 16, y0), "MISSÕES", 14, Color("#e0c890"), Tema.FONTE_TITULO); y0 += 24
		for tl in legenda:
			_txt_esq(c, Vector2(lx + 16, y0), "• " + str(tl), 13, Color("#ffe6a0"), Tema.FONTE_TEXTO); y0 += 22
	_txt(c, Vector2((s.x - 260) * 0.5 + 20, s.y - 14), "Clique ou M para fechar", 12, Color("#a89f8c"), Tema.FONTE_ITALICO, 0, 2)

const DESTINOS := {
	"porao_matadouro": "Porão · Cripta (chefe Andras, nv 8)",
	"ossario_carpideiras": "Ossário (chefe Irmã Celeste, nv 10)",
	"camara_trombeta": "Câmara (chefe Zacarias, nv 12)",
	"area_inicial": "Saída para a Paróquia",
	"minas_dos_gigantes": "Fosso · Minas dos Gigantes (chefe Ohya, nv 8)",
	"salao_das_noivas": "Fosso · Salão das Noivas (chefe Naamá, nv 10)",
	"altar_do_juramento": "Fosso · Altar do Juramento (chefe Semyaza, nv 12)",
	"jerusalem_hermon": "Saída para as Fontes do Jordão",
}
var mapa_tex: ImageTexture
var mapa_tex_id := ""
## Versão clara do mapa para a tela grande: chão em sépia legível, caminhos claros, paredes escuras, rio em verde.
func _gerar_mapa_claro() -> void:
	var m: Dictionary = game.mapa
	mapa_tex_id = m.get("id", "")
	var w := int(m["w"]); var h := int(m["h"])
	var img := Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	var grade: Array = m["grade"]
	var ter: Array = m["terreno"]
	for y in h:
		var gl: String = grade[y]
		var tl: String = ter[y]
		for x in w:
			var ch := tl[x]
			if ch == " " or ch == "h": continue
			var base: Color = game.cores_piso.get(ch, Color(0.3, 0.27, 0.22))
			var lum := clampf(base.get_luminance() * 2.2, 0.0, 1.0)
			var cor := Color(0.36, 0.3, 0.22).lerp(Color(0.78, 0.68, 0.5), lum)
			if base.g > base.r * 1.08: cor = cor.lerp(Color(0.42, 0.55, 0.3), 0.6)
			if gl[x] == "#": cor = Color(0.16, 0.13, 0.1)
			img.set_pixel(x + 1, y + 1, cor)
	mapa_tex = ImageTexture.create_from_image(img)

## [pos, rótulo curto, título da missão] para cada objetivo pendente das missões ativas.
func _alvos_missoes(j: Ent) -> Array:
	var out: Array = []
	var sim: WorldSim = game.sim
	for mid in j.missoes:
		if Missoes.estado(j, mid) != "ativa": continue
		var d := Missoes.def(mid)
		if d.is_empty(): continue
		var tit: String = d.get("titulo", mid)
		if Missoes.pronta(j, mid):
			var en = d.get("entrega", "")
			if en is Array: en = en[0] if en.size() > 0 else ""
			for e: Ent in sim.ents.values():
				if e.tipo == "npc" and e.kind == en: out.append([e.pos, "Entregar", tit])
			continue
		var etapa := Missoes._etapa_atual(j, mid)
		var objs: Array = d["objetivos"]
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) != etapa: continue
			var pr := Missoes.progresso(j, mid, i)
			if pr[0] >= pr[1]: continue
			var pos = null
			match o["tipo"]:
				"matar":
					for g in sim.spawns:
						if g["mob"] == o["alvo"]:
							if pos == null or (g["pos"] as Vector2).distance_to(j.pos) < (pos as Vector2).distance_to(j.pos): pos = g["pos"]
				"interagir", "usar_item":
					for e: Ent in sim.ents.values():
						if e.tipo == "objeto" and e.aux.get("obj", "") == o.get("objeto", ""): pos = e.pos
				"falar", "decidir":
					var n = o.get("npc"); if n is Array: n = n[0]
					for e: Ent in sim.ents.values():
						if e.tipo == "npc" and e.kind == n: pos = e.pos
				"explorar":
					pos = _centro_zona(o.get("subzona", ""))
			if pos == null and o.has("subzona"): pos = _centro_zona(o["subzona"])
			if pos != null: out.append([pos, Missoes.texto_objetivo(o).left(28), tit])
	return out

func _centro_zona(zid: String):
	var m: Dictionary = game.mapa
	var zonas: Array = m.get("zonas", [])
	var idx := -1
	for i in zonas.size():
		if zonas[i]["id"] == zid: idx = i
	if idx < 0: return null
	var soma := Vector2.ZERO; var n := 0
	var zg: Array = m.get("zona_grade", [])
	for y in range(0, zg.size(), 2):
		var ln: String = zg[y]
		for x in range(0, ln.length(), 2):
			if ln.unicode_at(x) - 65 == idx: soma += Vector2(x, y); n += 1
	return soma / n if n > 0 else null

func _estrela(c: CanvasItem, p: Vector2, r: float, cor: Color) -> void:
	var pts := PackedVector2Array()
	for i in 10:
		var rr := r if i % 2 == 0 else r * 0.45
		var a := -PI / 2 + TAU * i / 10.0
		pts.append(p + Vector2(cos(a), sin(a)) * rr)
	c.draw_colored_polygon(pts, Color(0.1, 0.06, 0.02))
	var pts2 := PackedVector2Array()
	for q in pts: pts2.append(p + (q - p) * 0.78)
	c.draw_colored_polygon(pts2, cor)

func _txt_esq(c: CanvasItem, p: Vector2, t: String, tam: int, cor: Color, fonte: Font) -> void:
	c.draw_string_outline(fonte, p, t, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, 3, Color(0, 0, 0, 0.9))
	c.draw_string(fonte, p, t, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, cor)

# =================================================================== log, avisos, faixa de zona, canalização
func _montar_log() -> void:
	log_box = VBoxContainer.new()
	log_box.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	log_box.offset_left = 12; log_box.offset_right = 420; log_box.offset_top = -330; log_box.offset_bottom = -160
	log_box.alignment = BoxContainer.ALIGNMENT_END
	log_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	log_box.add_theme_constant_override("separation", 1)
	raiz.add_child(log_box)
	ganhos = VBoxContainer.new()
	ganhos.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	ganhos.offset_left = -420; ganhos.offset_right = -150; ganhos.offset_top = -330; ganhos.offset_bottom = -160
	ganhos.alignment = BoxContainer.ALIGNMENT_END
	ganhos.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(ganhos)

# =================================================================== grupo, convite, inspecionar
func _montar_grupo() -> void:
	grupo_box = VBoxContainer.new()
	grupo_box.set_anchors_preset(Control.PRESET_TOP_LEFT)
	grupo_box.offset_left = 380; grupo_box.offset_top = 14; grupo_box.offset_right = 600
	grupo_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	grupo_box.add_theme_constant_override("separation", 3)
	grupo_box.visible = false
	raiz.add_child(grupo_box)

## Barras de vida do grupo (de todos os mapas): só aparecem com dois ou mais membros.
func grupo_atualizar(membros: Array) -> void:
	grupo_box.visible = membros.size() >= 2
	if not grupo_box.visible:
		for c in grupo_box.get_children(): c.queue_free()
		return
	while grupo_box.get_child_count() > membros.size(): var c := grupo_box.get_child(grupo_box.get_child_count() - 1); grupo_box.remove_child(c); c.queue_free()
	for i in membros.size():
		var m: Dictionary = membros[i]
		var linha: VBoxContainer
		if i < grupo_box.get_child_count():
			linha = grupo_box.get_child(i)
		else:
			linha = VBoxContainer.new(); linha.add_theme_constant_override("separation", 0)
			linha.mouse_filter = Control.MOUSE_FILTER_IGNORE
			grupo_box.add_child(linha)
			var barra := ProgressBar.new(); barra.show_percentage = false; barra.custom_minimum_size = Vector2(200, 9)
			barra.mouse_filter = Control.MOUSE_FILTER_IGNORE
			var cheio := Tema.caixa(Color(0.62, 0.12, 0.08), Color(0, 0, 0, 0), 0, 1); cheio.set_content_margin_all(0)
			var vazio := Tema.caixa(Color(0.08, 0.06, 0.05, 0.85), Color(0, 0, 0, 0), 0, 1); vazio.set_content_margin_all(0)
			barra.add_theme_stylebox_override("fill", cheio)
			barra.add_theme_stylebox_override("background", vazio)
			linha.add_child(barra)
			var nome := Tema.rotulo("", 13, Color("#e8dcc0"), Tema.FONTE_TEXTO, 3)
			nome.mouse_filter = Control.MOUSE_FILTER_IGNORE
			linha.add_child(nome)
		var nome_lbl: Label = linha.get_child(1)
		var cor: String = COR_CLASSE.get(str(m.get("classe", "")), "#e8dcc0")
		var txt := ("★ " if m.get("lider", false) else "") + "%s  Nv %d" % [str(m.get("nome", "?")), int(m.get("nivel", 1))]
		if not m.get("vivo", true): txt += "  (morto)"
		nome_lbl.text = txt
		nome_lbl.add_theme_color_override("font_color", Color(cor))
		var barra: ProgressBar = linha.get_child(0)
		barra.max_value = maxf(float(m.get("hp_max", 1)), 1.0)
		barra.value = clampf(float(m.get("hp", 0)), 0.0, barra.max_value)

func convite_mostrar(d: Dictionary) -> void:
	if convite_box != null: convite_box.queue_free()
	convite_box = PanelContainer.new()
	convite_box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	convite_box.offset_top = 150; convite_box.offset_left = -200; convite_box.offset_right = 200
	convite_box.add_theme_stylebox_override("panel", Tema.moldura_popup())
	convite_box.custom_minimum_size.y = 120
	raiz.add_child(convite_box)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 8)
	convite_box.add_child(v)
	var tl := Tema.rotulo("%s convida você para o grupo." % str(d.get("de", "Alguém")), 16, Color("#f0e2c0"), Tema.FONTE_TEXTO, 2)
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(tl)
	var linha := HBoxContainer.new(); linha.alignment = BoxContainer.ALIGNMENT_CENTER; linha.add_theme_constant_override("separation", 10)
	v.add_child(linha)
	var ok := Button.new(); ok.text = "Aceitar"
	ok.pressed.connect(func(): game.grupo_cmd("aceitar"); convite_box.queue_free())
	linha.add_child(ok)
	var nao := Button.new(); nao.text = "Recusar"
	nao.pressed.connect(func(): game.grupo_cmd("recusar"); convite_box.queue_free())
	linha.add_child(nao)
	get_tree().create_timer(30.0).timeout.connect(func(): if is_instance_valid(convite_box): convite_box.queue_free())

## Alguém pediu para negociar: Aceitar abre a janela de troca nos dois (o servidor manda o estado).
func troca_pedido_mostrar(d: Dictionary) -> void:
	if troca_box != null and is_instance_valid(troca_box): troca_box.queue_free()
	var caixa := PanelContainer.new()
	troca_box = caixa
	caixa.set_anchors_preset(Control.PRESET_CENTER_TOP)
	caixa.offset_top = 150; caixa.offset_left = -200; caixa.offset_right = 200
	caixa.add_theme_stylebox_override("panel", Tema.moldura_popup())
	caixa.custom_minimum_size.y = 120
	raiz.add_child(caixa)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 8)
	caixa.add_child(v)
	var tl := Tema.rotulo("%s quer negociar com você." % str(d.get("de", "Alguém")), 16, Color("#f0e2c0"), Tema.FONTE_TEXTO, 2)
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(tl)
	var linha := HBoxContainer.new(); linha.alignment = BoxContainer.ALIGNMENT_CENTER; linha.add_theme_constant_override("separation", 10)
	v.add_child(linha)
	var ok := Button.new(); ok.text = "Negociar"
	ok.pressed.connect(func(): game.troca_cmd("aceitar"); caixa.queue_free())
	linha.add_child(ok)
	var nao := Button.new(); nao.text = "Recusar"
	nao.pressed.connect(func(): game.troca_cmd("recusar"); caixa.queue_free())
	linha.add_child(nao)
	game.audio.tocar("ui/notificacao", null, -4.0)
	get_tree().create_timer(20.0).timeout.connect(func(): if is_instance_valid(caixa): caixa.queue_free())

func inspecao_mostrar(d: Dictionary) -> void:
	if inspecao_box != null: inspecao_box.queue_free()
	inspecao_box = PanelContainer.new()
	inspecao_box.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	inspecao_box.offset_left = -320; inspecao_box.offset_right = -14; inspecao_box.offset_top = -220; inspecao_box.offset_bottom = 220
	inspecao_box.add_theme_stylebox_override("panel", Tema.moldura_popup([28, 26, 28, 26]))
	raiz.add_child(inspecao_box)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 5)
	inspecao_box.add_child(v)
	var cor: String = COR_CLASSE.get(str(d.get("classe", "")), "#e8dcc0")
	var nm := Tema.rotulo(str(d.get("nome", "?")), 20, Color(cor), Tema.FONTE_TITULO, 3)
	nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var placa := Tema.sb_ui("menu_titulo", [60, 0, 60, 0], [44, 3, 44, 7])
	if placa: nm.add_theme_stylebox_override("normal", placa); nm.custom_minimum_size.y = 40
	v.add_child(nm)
	v.add_child(Tema.rotulo("%s · nível %d" % [str(d.get("classe", "")).capitalize(), int(d.get("nivel", 1))], 14, Color("#b8aa8e"), Tema.FONTE_TEXTO, 2))
	v.add_child(Tema.rotulo("Vida %d / %d" % [int(d.get("hp", 0)), int(d.get("hp_max", 0))], 14, Color("#e8dcc0"), Tema.FONTE_TEXTO, 2))
	var st: Dictionary = d.get("stats", {})
	v.add_child(Tema.rotulo("FOR %d · AGI %d · VIT %d · ESP %d" % [int(st.get("FOR", 0)), int(st.get("AGI", 0)), int(st.get("VIT", 0)), int(st.get("ESP", 0))], 14, Color("#e8dcc0"), Tema.FONTE_TEXTO, 2))
	var div := Tema.ui("menu_divisor")
	if div:
		var tr := TextureRect.new(); tr.texture = div; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.custom_minimum_size = Vector2(0, 14)
		v.add_child(tr)
	v.add_child(Tema.rotulo("Equipamento", 15, Color("#d8b870"), Tema.FONTE_TITULO, 2))
	var eq: Dictionary = d.get("equip", {})
	if eq.is_empty(): v.add_child(Tema.rotulo("(nada equipado)", 14, Color("#8f8270"), Tema.FONTE_ITALICO, 2))
	for slot in eq:
		var it: Dictionary = eq[slot]
		v.add_child(Tema.rotulo("%s: %s" % [str(slot).capitalize(), str(it.get("nome", "?"))], 14, Defs.cor_raridade(str(it.get("raridade", "comum"))), Tema.FONTE_TEXTO, 2))
	var fechar := Button.new(); fechar.text = "Fechar"
	fechar.pressed.connect(func(): inspecao_box.queue_free())
	v.add_child(fechar)

## Menu do botão direito num jogador: inspecionar ou convidar para o grupo.
func menu_jogador(id: int, pos: Vector2) -> void:
	fechar_menu_jogador()
	var caixa := PanelContainer.new()
	menu_box = caixa
	caixa.position = pos + Vector2(14, 10)
	caixa.add_theme_stylebox_override("panel", Tema.moldura_dica())
	raiz.add_child(caixa)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 4)
	caixa.add_child(v)
	var e: Ent = game.sim.ents.get(id)
	if e != null and e.nome != "":
		v.add_child(Tema.rotulo(e.nome, 15, Color("#f0e2c0"), Tema.FONTE_TITULO, 2))
	var b1 := Button.new(); b1.text = "Inspecionar"; b1.focus_mode = Control.FOCUS_NONE
	b1.pressed.connect(func(): game.inspecionar(id); fechar_menu_jogador())
	v.add_child(b1)
	var b2 := Button.new(); b2.text = "Convidar ao grupo"; b2.focus_mode = Control.FOCUS_NONE
	b2.pressed.connect(func(): game.grupo_cmd("convidar", {"id": id}); fechar_menu_jogador())
	v.add_child(b2)
	var b3 := Button.new(); b3.text = "Negociar"; b3.focus_mode = Control.FOCUS_NONE
	b3.pressed.connect(func(): game.troca_cmd("pedir", {"id": id}); fechar_menu_jogador())
	v.add_child(b3)
	# some sozinho depois de 8 s (só este menu, não um aberto depois)
	get_tree().create_timer(8.0).timeout.connect(func(): if is_instance_valid(caixa): caixa.queue_free())

func fechar_menu_jogador() -> void:
	if menu_box != null and is_instance_valid(menu_box): menu_box.queue_free()
	menu_box = null

# =================================================================== chat (Enter abre, Enter manda, Esc cancela)
const COR_CLASSE := {"anjo": "#f3dc8e", "demonio": "#ff7a5c", "cultista": "#d77ad6", "humano": "#e8d4b0", "mutante": "#9fd86a", "tecnomancer": "#7fc8ff", "warlord": "#c8302a"}

func _montar_chat() -> void:
	chat_painel = PanelContainer.new()
	chat_painel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	chat_painel.offset_left = 12; chat_painel.offset_right = 432; chat_painel.offset_top = -530; chat_painel.offset_bottom = -362
	chat_painel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chat_fundo = Tema.caixa(Color(0.04, 0.03, 0.025, 0.0), Color(0.45, 0.36, 0.22, 0.0), 1, 3)
	chat_fundo.set_content_margin_all(8)
	chat_painel.add_theme_stylebox_override("panel", chat_fundo)
	raiz.add_child(chat_painel)
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_theme_constant_override("separation", 4)
	chat_painel.add_child(v)
	chat_texto = RichTextLabel.new()
	chat_texto.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_texto.scroll_following = true
	chat_texto.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chat_texto.add_theme_font_override("normal_font", Tema.FONTE_TEXTO)
	chat_texto.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	chat_texto.add_theme_font_size_override("normal_font_size", 15)
	chat_texto.add_theme_font_size_override("bold_font_size", 13)
	chat_texto.add_theme_constant_override("outline_size", 4)
	chat_texto.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	chat_texto.scroll_active = false
	v.add_child(chat_texto)
	var linha := HBoxContainer.new()
	linha.add_theme_constant_override("separation", 4)
	v.add_child(linha)
	chat_canal_bt = Button.new()
	chat_canal_bt.focus_mode = Control.FOCUS_NONE
	chat_canal_bt.custom_minimum_size = Vector2(76, 0)
	chat_canal_bt.add_theme_font_size_override("font_size", 12)
	chat_canal_bt.tooltip_text = "Troca o canal: Perto (balão, quem está perto) ou Global (todo mundo online)"
	chat_canal_bt.pressed.connect(func():
		chat_canal = "global" if chat_canal == "perto" else "perto"
		_chat_bt(); chat_entrada.grab_focus())
	chat_canal_bt.visible = false
	linha.add_child(chat_canal_bt)
	_chat_bt()
	chat_entrada = LineEdit.new()
	chat_entrada.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	chat_entrada.max_length = 160
	chat_entrada.placeholder_text = "Enter manda · /g global · /m Nome privado · /r responde"
	chat_entrada.add_theme_font_override("font", Tema.FONTE_TEXTO)
	chat_entrada.add_theme_font_size_override("font_size", 15)
	chat_entrada.visible = false
	chat_entrada.text_submitted.connect(_chat_enviar)
	chat_entrada.gui_input.connect(func(ev):
		if ev is InputEventKey and ev.pressed and ev.keycode == KEY_ESCAPE:
			_chat_fechar(); chat_entrada.accept_event())
	linha.add_child(chat_entrada)
	chat_barra = HBoxContainer.new()
	chat_barra.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	chat_barra.offset_left = 12; chat_barra.offset_top = -360; chat_barra.offset_bottom = -336
	chat_barra.add_theme_constant_override("separation", 2)
	chat_barra.modulate.a = 0.6
	chat_barra.mouse_entered.connect(func(): chat_barra.modulate.a = 1.0)
	chat_barra.mouse_exited.connect(func(): chat_barra.modulate.a = 0.6)
	raiz.add_child(chat_barra)
	chat_aba = _chat_botao("", "Minimiza ou mostra o chat (F2). Enter continua abrindo para escrever.", func():
		_chat_mudar("minimizado" if chat_estado == "aberto" else "aberto"))
	chat_min_bt = _chat_botao("–", "Minimizar o chat (F2)", func(): _chat_mudar("minimizado"))
	_chat_botao("×", "Fechar o chat. F2 ou Enter abrem de novo.", func(): _chat_mudar("fechado"))
	var cfg := ConfigFile.new()
	if cfg.load(CHAT_CFG) == OK: chat_estado = str(cfg.get_value("chat", "estado", "aberto"))
	if not chat_estado in ["aberto", "minimizado", "fechado"]: chat_estado = "aberto"
	_chat_aplicar()
	chat_linha_sistema("Enter conversa com quem está perto. /g fala no global, /m Nome manda privado, /r responde o último privado. F2 minimiza o chat.")

func _chat_botao(txt: String, dica: String, acao: Callable) -> Button:
	var b := Button.new()
	b.text = txt
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(24, 0)
	b.add_theme_font_override("font", Tema.FONTE_TITULO)
	b.add_theme_font_size_override("font_size", 12)
	b.tooltip_text = dica
	b.mouse_entered.connect(func(): chat_barra.modulate.a = 1.0)
	b.pressed.connect(acao)
	chat_barra.add_child(b)
	return b

func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventKey and ev.pressed and not ev.echo and ev.keycode == KEY_F2:
		_chat_mudar("minimizado" if chat_estado == "aberto" else "aberto"); get_viewport().set_input_as_handled()

func _chat_mudar(estado: String) -> void:
	chat_estado = estado
	var cfg := ConfigFile.new()
	cfg.set_value("chat", "estado", chat_estado)
	cfg.save(CHAT_CFG)
	_chat_aplicar()

## Minimizado: some o texto e fica só a aba, contando as mensagens novas. Fechado: some até a aba.
## Aberto: as linhas somem sozinhas depois de um tempo parado, para não ficar texto em cima do jogo.
func _chat_aplicar() -> void:
	if chat_estado == "aberto": chat_nao_lidas = 0
	chat_texto.visible = chat_estado == "aberto" or chat_aberto()
	chat_barra.visible = chat_estado != "fechado" or chat_aberto()
	chat_min_bt.visible = chat_estado == "aberto"
	if chat_aberto() or chat_estado != "aberto": _chat_parar_sumico(); chat_texto.modulate.a = 1.0
	else: _chat_acordar()
	var txt := "Chat ▾" if chat_estado == "aberto" else "Chat ▸"
	if chat_estado == "minimizado" and chat_nao_lidas > 0: txt = "Chat ▸  %d nova%s" % [chat_nao_lidas, "" if chat_nao_lidas == 1 else "s"]
	chat_aba.text = txt
	chat_aba.add_theme_color_override("font_color", Color("#f0c060") if chat_nao_lidas > 0 else Color("#cdbf9f"))

func _chat_parar_sumico() -> void:
	if chat_tw and chat_tw.is_valid(): chat_tw.kill()

func _chat_acordar() -> void:
	_chat_parar_sumico()
	chat_texto.modulate.a = 1.0
	if chat_aberto(): return
	chat_tw = chat_texto.create_tween()
	chat_tw.tween_interval(14.0)
	chat_tw.tween_property(chat_texto, "modulate:a", 0.0, 2.0)

func _chat_chegou() -> void:
	if chat_estado == "minimizado" and not chat_aberto():
		chat_nao_lidas += 1; _chat_aplicar()
	elif chat_estado == "aberto" and not chat_aberto(): _chat_acordar()

func chat_aberto() -> bool:
	return chat_entrada != null and chat_entrada.visible

func _chat_bt() -> void:
	chat_canal_bt.text = "Global" if chat_canal == "global" else "Perto"
	chat_canal_bt.add_theme_color_override("font_color", Color("#f0c060") if chat_canal == "global" else Color("#e8dcc0"))

func abrir_chat(texto := "") -> void:
	if chat_estado == "fechado": _chat_mudar("aberto")
	chat_entrada.visible = true; chat_canal_bt.visible = true
	chat_entrada.text = texto
	chat_entrada.grab_focus()
	chat_entrada.caret_column = texto.length()
	chat_fundo.bg_color.a = 0.62; chat_fundo.border_color.a = 0.9
	chat_texto.scroll_active = true
	chat_texto.mouse_filter = Control.MOUSE_FILTER_STOP
	chat_painel.queue_redraw()
	chat_nao_lidas = 0; _chat_aplicar()

func _chat_fechar() -> void:
	chat_entrada.release_focus()
	chat_entrada.visible = false; chat_canal_bt.visible = false
	chat_fundo.bg_color.a = 0.0; chat_fundo.border_color.a = 0.0
	chat_texto.scroll_active = false
	chat_texto.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chat_painel.queue_redraw()
	_chat_aplicar()

func _chat_enviar(t: String) -> void:
	t = t.strip_edges()
	var canal := chat_canal; var para := ""
	var low := t.to_lower()
	if low.begins_with("/g ") or low.begins_with("/global "):
		canal = "global"; t = t.substr(t.find(" ") + 1)
	elif low.begins_with("/p ") or low.begins_with("/perto "):
		canal = "perto"; t = t.substr(t.find(" ") + 1)
	elif low.begins_with("/m ") or low.begins_with("/w ") or low.begins_with("/pm "):
		var resto := t.substr(t.find(" ") + 1).strip_edges()
		var sp := resto.find(" ")
		if sp > 0: canal = "pm"; para = resto.left(sp); t = resto.substr(sp + 1)
		else: chat_linha_sistema("Use: /m Nome mensagem"); _chat_fechar(); return
	elif low.begins_with("/gr "):
		canal = "grupo"; t = t.substr(4)
	elif low.begins_with("/convidar "):
		game.grupo_cmd("convidar_nome", {"nome": t.substr(10).strip_edges()}); _chat_fechar(); return
	elif low == "/sair":
		game.grupo_cmd("sair"); _chat_fechar(); return
	elif low == "/ajoelhar":
		game.cmd("gesto", ["ajoelhar"]); _chat_fechar(); return
	elif low.begins_with("/r "):
		if chat_ultimo_pm == "": chat_linha_sistema("Ninguém te mandou mensagem privada ainda."); _chat_fechar(); return
		canal = "pm"; para = chat_ultimo_pm; t = t.substr(3)
	elif low.begins_with("/"):
		chat_linha_sistema("Comandos: /g global · /gr grupo · /convidar Nome · /sair · /m Nome privado · /r responde · /ajoelhar"); _chat_fechar(); return
	t = t.strip_edges()
	if t != "": game.cmd("falar", [t.left(120), canal, para])
	_chat_fechar()

func chat_linha(d: Dictionary) -> void:
	var canal := str(d.get("canal", "perto"))
	if d.get("anuncio", false):   # anúncio do servidor (um mistério resolvido): linha dourada e aviso na tela
		chat_texto.push_color(Color("#e8c060")); chat_texto.add_text("✦ " + str(d.get("texto", ""))); chat_texto.pop()
		chat_texto.newline(); _chat_aparar()
		if chat_aba: _chat_chegou()
		aviso(str(d.get("texto", "")))
		return
	if canal == "sistema": chat_linha_sistema(str(d.get("texto", ""))); return
	var nome := str(d.get("nome", "?"))
	var cor: String = COR_CLASSE.get(str(d.get("classe", "")), "#e8d4b0")
	var cor_txt := Color("#efe6d2")
	var prefixo := ""
	if canal == "global": prefixo = "[Global] "; cor_txt = Color("#f0d48a")
	elif canal == "grupo": prefixo = "[Grupo] "; cor_txt = Color("#9fd0ff")
	elif canal == "pm":
		cor_txt = Color("#f2a6d8")
		if game.jog != null and nome == game.jog.nome and str(d.get("para", "")).to_lower() != nome.to_lower(): prefixo = "[Para %s] " % str(d.get("para", ""))
		else: prefixo = "[De %s] " % nome; chat_ultimo_pm = nome
	if prefixo != "":
		chat_texto.push_color(cor_txt); chat_texto.add_text(prefixo); chat_texto.pop()
	if not prefixo.begins_with("[De") and not prefixo.begins_with("[Para"):
		chat_texto.push_bold(); chat_texto.push_color(Color(cor)); chat_texto.add_text(nome + ": "); chat_texto.pop(); chat_texto.pop()
	chat_texto.push_color(cor_txt); chat_texto.add_text(str(d.get("texto", ""))); chat_texto.pop()
	chat_texto.newline()
	_chat_aparar()
	_chat_chegou()

func chat_linha_sistema(t: String) -> void:
	chat_texto.push_italics(); chat_texto.push_color(Color("#9c8f78")); chat_texto.add_text(t); chat_texto.pop(); chat_texto.pop()
	chat_texto.newline()
	_chat_aparar()
	if chat_aba: _chat_chegou()

func _chat_aparar() -> void:
	while chat_texto.get_paragraph_count() > 60: chat_texto.remove_paragraph(0)

func log_msg(txt: String, cor := Color("#d8cfb8")) -> void:
	if txt == "": return
	var l := Tema.rotulo(txt, 14, cor, Tema.FONTE_TEXTO, 3)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = 400
	log_box.add_child(l)
	while log_box.get_child_count() > 7: log_box.get_child(0).queue_free(); log_box.remove_child(log_box.get_child(0))
	var tw := l.create_tween()
	tw.tween_interval(9.0)
	tw.tween_property(l, "modulate:a", 0.0, 1.5)
	tw.tween_callback(l.queue_free)

func item_ganho(d: Dictionary) -> void:
	var cor := Defs.cor_raridade(d.get("raridade", "comum"))
	var h := HBoxContainer.new()
	h.alignment = BoxContainer.ALIGNMENT_END
	h.add_theme_constant_override("separation", 6)
	var txt: String = d.get("nome", "")
	if int(d.get("qtd", 1)) > 1: txt = "%d × %s" % [int(d["qtd"]), txt]
	var l := Tema.rotulo(txt, 15, cor, Tema.FONTE_TITULO, 4)
	h.add_child(l)
	var ic := Tema.icone_item(d.get("id", ""))
	if ic.size() == 2:
		var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]
		var tr := TextureRect.new(); tr.texture = at; tr.custom_minimum_size = Vector2(26, 26)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		h.add_child(tr)
	ganhos.add_child(h)
	while ganhos.get_child_count() > 6: var c0 := ganhos.get_child(0); ganhos.remove_child(c0); c0.queue_free()
	h.modulate.a = 0.0
	var tw := h.create_tween()
	tw.tween_property(h, "modulate:a", 1.0, 0.15)
	tw.tween_interval(4.0)
	tw.tween_property(h, "modulate:a", 0.0, 1.0)
	tw.tween_callback(h.queue_free)

func _montar_centro() -> void:
	aviso_lbl = Tema.rotulo("", 18, Color("#ffd9a0"), Tema.FONTE_TITULO, 5)
	aviso_lbl.set_anchors_preset(Control.PRESET_CENTER)
	aviso_lbl.offset_left = -400; aviso_lbl.offset_right = 400; aviso_lbl.offset_top = -170; aviso_lbl.offset_bottom = -140
	aviso_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	aviso_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(aviso_lbl)
	banner = _painel(_desenhar_banner)
	banner.set_anchors_preset(Control.PRESET_CENTER_TOP)
	banner.offset_left = -400; banner.offset_right = 400; banner.offset_top = 110; banner.offset_bottom = 200
	raiz.add_child(banner)
	canal_ui = _painel(_desenhar_canal)
	canal_ui.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	canal_ui.offset_left = -130; canal_ui.offset_right = 130; canal_ui.offset_top = -230; canal_ui.offset_bottom = -190
	raiz.add_child(canal_ui)

func aviso(txt: String, cor := Color("#ffd9a0")) -> void:
	if txt == "": return
	aviso_lbl.text = txt
	aviso_lbl.add_theme_color_override("font_color", cor)
	aviso_t = 2.4

func banner_mostrar(titulo: String, sub: String, cor := Color("#f0dca0")) -> void:
	banner_txt = titulo; banner_sub = sub; banner_t = 4.0
	banner.set_meta("cor", cor)

func _desenhar_banner(c: Painel) -> void:
	if banner_t <= 0.0: return
	var a := clampf(banner_t / 0.8, 0.0, 1.0) * clampf((4.0 - banner_t) / 0.4, 0.0, 1.0)
	var cor: Color = banner.get_meta("cor", Color("#f0dca0"))
	var w := 400.0
	for i in 40:
		var k := 1.0 - absf(i - 20) / 20.0
		c.draw_rect(Rect2(w - 300 + i * 15, 24, 15, 48), Color(0, 0, 0, 0.45 * a * k))
	c.draw_line(Vector2(w - 220, 70), Vector2(w + 220, 70), Color(cor.r, cor.g, cor.b, 0.6 * a), 1.0)
	_txt(c, Vector2(w, 58), banner_txt, 36, Color(cor.r, cor.g, cor.b, a), Tema.FONTE_GOTICA, 0, 6)
	if banner_sub != "": _txt(c, Vector2(w, 88), banner_sub, 15, Color(0.75, 0.7, 0.6, a), Tema.FONTE_ITALICO, 0, 3)

func zona(z: Dictionary, primeira: bool) -> void:
	if z.is_empty(): return
	var sub := ""
	if z.get("seguro", false): sub = "Área segura"
	elif z.has("nivel") and z["nivel"] != null:
		var nv = z["nivel"]
		sub = ("Nível %d–%d" % [int(nv[0]), int(nv[1])]) if nv is Array else ("Nível %s" % str(nv))
	if primeira or true: banner_mostrar(z.get("nome", ""), sub)

func canal(d: Dictionary) -> void:
	if int(d.get("id", -1)) != _jog().id and not d.get("chefe", false): return
	canal_d = d.duplicate(); canal_t = 0.0

func canal_fim(d: Dictionary) -> void:
	if int(d.get("id", -1)) == int(canal_d.get("id", -2)): canal_d = {}

func _desenhar_canal(c: Painel) -> void:
	if canal_d.is_empty(): return
	var f := clampf(canal_t / maxf(0.05, float(canal_d.get("dur", 1.0))), 0.0, 1.0)
	var eh_chefe: bool = canal_d.get("chefe", false)
	_txt(c, Vector2(130, 12), canal_d.get("texto", ""), 14, Color("#ffb08a") if eh_chefe else Color("#f0dca0"), Tema.FONTE_TITULO, 0, 3)
	_barra(c, Rect2(10, 18, 240, 10), f, Color(0.85, 0.3, 0.15) if eh_chefe else Color(0.85, 0.7, 0.35))

# =================================================================== morte, ajuda
func morte(d: Dictionary) -> void:
	if morte_ui == null:
		morte_ui = _painel(_desenhar_morte)
		morte_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		raiz.add_child(morte_ui)
	morte_ui.set_meta("d", d)
	morte_ui.set_meta("t", 0.0)
	morte_ui.visible = true
	chefe_d = {}

func reviveu() -> void:
	if morte_ui: morte_ui.visible = false

func _desenhar_morte(c: Painel) -> void:
	var tt: float = morte_ui.get_meta("t", 0.0)
	var d: Dictionary = morte_ui.get_meta("d", {})
	var a := clampf(tt / 1.5, 0.0, 1.0)
	c.draw_rect(Rect2(Vector2.ZERO, c.size), Color(0.12, 0.0, 0.0, 0.55 * a))
	var cen := c.size * 0.5
	_txt(c, cen + Vector2(0, -20), "VOCÊ CAIU", 64, Color(0.75, 0.1, 0.06, a), Tema.FONTE_GOTICA, 0, 8)
	var falta: float = maxf(0.0, float(d.get("t", 5.0)) - tt)
	var sub := "Voltando ao último altar em %d…" % ceili(falta)
	if int(d.get("perda", 0)) > 0: sub = "Perdeu %d de experiência. " % int(d["perda"]) + sub
	_txt(c, cen + Vector2(0, 24), sub, 17, Color(0.85, 0.78, 0.65, a), Tema.FONTE_ITALICO, 0, 3)

func mostrar_ajuda() -> void:
	if ajuda_ui == null:
		ajuda_ui = PanelContainer.new()
		ajuda_ui.set_anchors_preset(Control.PRESET_CENTER)
		ajuda_ui.offset_left = -316; ajuda_ui.offset_right = 316; ajuda_ui.offset_top = -238; ajuda_ui.offset_bottom = 218
		ajuda_ui.add_theme_stylebox_override("panel", Tema.moldura_popup([30, 24, 30, 26]))
		var v := VBoxContainer.new()
		v.add_theme_constant_override("separation", 8)
		ajuda_ui.add_child(v)
		var tl := Tema.rotulo("Como jogar", 30, Color("#ffcf9a"), Tema.FONTE_GOTICA, 4)
		tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(tl)
		var r := RichTextLabel.new()
		r.bbcode_enabled = true; r.fit_content = true; r.scroll_active = false
		r.add_theme_font_size_override("normal_font_size", 15)
		r.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
		r.text = """[b]Clique[/b] no chão para andar (segure para seguir o mouse).
[b]Clique[/b] num inimigo para atacar. [b]Shift + clique[/b] ataca sem sair do lugar.
[b]1 a 6[/b] usam as habilidades (no alvo ou onde o mouse aponta). [b]Botão direito[/b] (ou [b]Espaço[/b]) = esquiva da classe, para onde o mouse aponta (2 cargas, 10 s cada).
[b]Q[/b] poção de vida, [b]W[/b] poção de recurso, [b]E[/b] antídoto, [b]R[/b] volta para a Paróquia (grátis).
[b]V[/b] abre o teleporte: leva a qualquer área de caça do seu nível por 3.000 de ouro.
[b]Z[/b] liga o modo automático: luta sozinho perto de onde você está, junta os drops e bebe poção (desliga ao clicar).
[b]Clique direito[/b] numa skill da barra põe ou tira ela do automático; [b]Shift+Z[/b] abre os ajustes (raio, poções, drops).
[b]Clique[/b] em NPCs, baús, portas e itens no chão. [b]Alt[/b] mostra os itens caídos.
[b]I[/b] mochila e equipamento · [b]C[/b] personagem · [b]K[/b] habilidades · [b]T[/b] talentos · [b]J[/b] missões · [b]M[/b] mapa.
Na mochila: [b]botão direito[/b] usa ou equipa; [b]arraste[/b] para mover, equipar ou jogar fora.
Os [b]![/b] em cima das pessoas são missões novas; [b]?[/b] são missões prontas para entregar.
Áreas vermelhas no chão avisam um golpe: saia delas.
[b]ENTER[/b] abre o chat: escreva e aperte Enter de novo; [b]Esc[/b] cancela.
[b]F11[/b] ou [b]Alt + Enter[/b] liga e desliga a tela cheia.

[color=#a89f8c][i]H mostra esta ajuda de novo.[/i][/color]"""
		v.add_child(r)
		var b := Button.new(); b.text = "Entendi"; b.custom_minimum_size = Vector2(140, 36)
		b.pressed.connect(func(): ajuda_ui.visible = false)
		var cc := CenterContainer.new(); cc.add_child(b); v.add_child(cc)
		raiz.add_child(ajuda_ui)
	ajuda_ui.visible = true

func alternar_ajuda() -> void:
	if ajuda_ui and ajuda_ui.visible: ajuda_ui.visible = false
	else: mostrar_ajuda()

# =================================================================== tooltip
func _montar_tooltip() -> void:
	tooltip = PanelContainer.new()
	var sb: StyleBox = Tema.sb_ui("menu_dica", [18, 18, 18, 18], [14, 11, 14, 12])
	if sb == null:
		sb = Tema.caixa(Color(0.05, 0.04, 0.035, 0.96), Color(0.55, 0.44, 0.26), 1, 2)
		sb.set_content_margin_all(10)
	tooltip.add_theme_stylebox_override("panel", sb)
	tip_estilo = sb
	tooltip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip_lbl = RichTextLabel.new()
	tip_lbl.bbcode_enabled = true
	tip_lbl.fit_content = true
	tip_lbl.scroll_active = false
	tip_lbl.custom_minimum_size.x = 300
	tip_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip_lbl.add_theme_font_override("normal_font", Tema.FONTE_TEXTO)
	tip_lbl.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	tip_lbl.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	tip_lbl.add_theme_font_size_override("normal_font_size", 14)
	tip_lbl.add_theme_font_size_override("italics_font_size", 13)
	tip_lbl.add_theme_font_size_override("bold_font_size", 14)
	tooltip.add_child(tip_lbl)
	tooltip.visible = false
	tooltip.z_index = 100
	var cl := CanvasLayer.new(); cl.layer = 30; add_child(cl)
	var c := Control.new(); c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cl.add_child(c)
	c.add_child(tooltip)

func mostrar_tip(bb: String) -> void:
	if bb == "": esconder_tip(); return
	tooltip.add_theme_stylebox_override("panel", tip_estilo)
	tip_lbl.custom_minimum_size.x = 300
	tip_lbl.tab_stops = PackedFloat32Array()
	tip_lbl.text = bb
	tooltip.visible = true
	tooltip.reset_size()

## Detalhes de item: moldura gótica tingida pela raridade e texto mais largo (ver janelas.gd tip_item).
func mostrar_tip_item(it: Dictionary, bb: String) -> void:
	# 0.9.8: card simples (como Halls of Torment): fundo preto translúcido e moldura fina na cor da raridade
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0.86)
	sb.border_color = Color(0.75, 0.68, 0.5).lerp(Defs.cor_raridade(str(it.get("raridade", "comum"))), 0.6)
	sb.set_border_width_all(1); sb.set_corner_radius_all(2)
	sb.set_content_margin_all(8)
	tooltip.add_theme_stylebox_override("panel", sb)
	tip_lbl.custom_minimum_size.x = 230   # 0.9.8: ~30% menor (antes 330), com fonte menor
	tip_lbl.tab_stops = PackedFloat32Array([160.0])   # linhas "nome<TAB>valor": o valor cai numa coluna fixa
	tip_lbl.text = bb
	tooltip.visible = true
	tooltip.reset_size()

func esconder_tip() -> void:
	tooltip.visible = false

# =================================================================== eventos simples
func xp(d: Dictionary) -> void:
	xp_flash = 1.0

func nivel(d: Dictionary) -> void:
	banner_mostrar("NÍVEL %d" % int(d["nivel"]), ("Nova habilidade: " + d["skill_nova"]) if d.get("skill_nova", "") != "" else "Você tem pontos de atributo para distribuir (C)", Color("#ffe08a"))

func skill_usada(d: Dictionary) -> void:
	if int(d.get("id", -1)) == _jog().id: pressionado[int(d.get("slot", -1))] = t + 0.12

func missao(d: Dictionary) -> void:
	var m := Missoes.def(d.get("id", ""))
	var nm: String = m.get("titulo", "")
	match d.get("estado", ""):
		"aceita": banner_mostrar("Nova missão", nm, Color("#f0dca0"))
		"concluida":
			banner_mostrar("Missão concluída", nm, Color("#c8f08a"))
			if m.get("texto_conclusao", "") != "": log_msg(m["texto_conclusao"], Color("#c8bfa8"))
		"progresso", "atualizada":
			if d.has("texto"): aviso(d["texto"], Color("#e8dfc9"))

func status(d: Dictionary) -> void:
	pass

func atualizar_cinto() -> void:
	barra.queue_redraw()

# =================================================================== laço
func _process(dt: float) -> void:
	t += dt
	xp_flash = maxf(0.0, xp_flash - dt * 2.0)
	if aviso_t > 0.0:
		aviso_t -= dt
		aviso_lbl.modulate.a = clampf(aviso_t / 0.5, 0.0, 1.0)
	if banner_t > 0.0: banner_t -= dt
	if not canal_d.is_empty():
		canal_t += dt
		if canal_t > float(canal_d.get("dur", 1.0)) + 0.6: canal_d = {}
	if morte_ui and morte_ui.visible: morte_ui.set_meta("t", float(morte_ui.get_meta("t")) + dt); morte_ui.queue_redraw()
	if game.jog == null: return
	_posicionar_pet()
	if pet_ui.visible: pet_ui.queue_redraw()
	barra.queue_redraw(); topo_esq.queue_redraw(); alvo_ui.queue_redraw(); minimapa.queue_redraw(); banner.queue_redraw(); canal_ui.queue_redraw()
	if mapa_ui and mapa_ui.visible: mapa_ui.queue_redraw()
	if Engine.get_process_frames() % 15 == 0: _atualizar_rastreador()
	if tooltip.visible:
		var mp := raiz.get_global_mouse_position()
		var s := tooltip.size
		var p := mp + Vector2(18, -s.y - 10)
		if p.y < 4: p.y = mp.y + 24
		p.x = clampf(p.x, 4, raiz.size.x - s.x - 4)
		p.y = clampf(p.y, 4, raiz.size.y - s.y - 4)
		tooltip.position = p

func _atualizar_rastreador() -> void:
	var j := _jog()
	var s := ""
	var n := 0
	for mid in j.missoes:
		if Missoes.estado(j, mid) != "ativa": continue
		var d := Missoes.def(mid)
		if d.is_empty(): continue
		n += 1
		if n > 4: break
		var principal: bool = d.get("tipo", "") == "principal"
		s += "[b][color=%s]%s[/color][/b]\n" % ["#ffcf7a" if principal else "#e8dfc9", d.get("titulo", mid)]
		if Missoes.pronta(j, mid):
			var ent: String = Missoes.nome_entrega(mid) if str(d.get("entrega", "")) != "automatico" else ""
			s += "[color=#c8f08a]  ◆ Volte a %s[/color]\n" % ent if ent != "" else "[color=#c8f08a]  ◆ Pronta[/color]\n"
			continue
		var objs: Array = d["objetivos"]
		var etapa := Missoes._etapa_atual(j, mid)
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) != etapa: continue
			var pr := Missoes.progresso(j, mid, i)
			var feito: bool = pr[0] >= pr[1]
			var tx := Missoes.texto_objetivo(o)
			if pr[1] > 1: tx += " [b]%d/%d[/b]" % [pr[0], pr[1]]
			s += ("[color=#9cd870]  ◆ %s ✓[/color]\n" % tx) if feito else ("[color=#d8cfb8]  ◆ %s[/color]\n" % tx)
	if s != "": s = "[font_size=15][b][color=#e0b84a]★ MISSÕES[/color][/b][/font_size]\n" + s
	if rastreador.text != s: rastreador.text = s

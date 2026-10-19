class_name GmPainel
## Painel do GM (F8), no kit de janelas do jogo. Só aparece para conta que o SERVIDOR marcou como GM
## (evento "gm_ativo"); o cliente apenas pede ({"t": "gm", ...}) e quem confere e executa é scripts/net/gm.gd.
## F7 teleporta o GM para o ponto do mouse. Abas: Jogadores, Invocar, Itens e nível, Eventos, Viajar.

const ABAS := [["jogadores", "Jogadores"], ["invocar", "Invocar"], ["itens", "Itens e nível"], ["eventos", "Eventos"], ["viajar", "Viajar"]]
const RARIDADES := ["", "comum", "magico", "raro", "excelente"]
const NOME_RAR := {"": "do item", "comum": "comum", "magico": "mágico", "raro": "raro", "excelente": "excelente"}
const NOME_CLASSE := {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomancer", "warlord": "Warlord"}
const COR_TITULO := Color("#e0c890")
const COR_SECAO := Color("#c9a860")
const COR_FRACO := Color("#a89f8c")
const COR_GM := Color("#d9a441")

static var ativo := false
static var conta := ""
static var estado := {}
static var aba := "jogadores"
static var nome_sel := ""        # jogador escolhido na aba Jogadores (também vale para conta offline digitada)
static var alvo := ""            # quem recebe item/ouro/nível ("" = o próprio GM)
static var mob_sel := ""
static var chefe_sel := ""
static var item_sel := ""
static var v := {"nivel": 0, "qtd": 1, "neutro": false, "anunciar": true, "iqtd": 1, "refino": 0, "rar": 0, "lv": 1}
static var _ui := {}             # peças que mudam sem redesenhar a janela (status, lista de jogadores, cabeçalho)
static var _status := ""

# =================================================================== eventos do servidor (game._ev manda os "gm_*")
static func ev(game, tipo: String, d: Dictionary) -> void:
	match tipo:
		"gm_ativo":
			ativo = true; conta = str(d.get("conta", ""))
			game.hud.aviso("Painel do GM liberado: F8 abre, F7 teleporta para o mouse.", COR_GM)
		"gm_estado":
			estado = d
			if aberto(game): _atualizar(game)
		"gm_ok":
			_status = str(d.get("texto", ""))
			game.hud.aviso(_status, COR_GM)
			if aberto(game):
				_atualizar(game)
				pedir(game, "estado")
		"gm_visivel":   # GM ficou (in)visível: os outros escondem, ele mesmo fica translúcido
			var vw = game.views.get(int(d.get("id", -1)))
			if vw == null: return
			var vis: bool = d.get("vis", true)
			if game.jog != null and vw.id == game.jog.id: vw.visible = true; vw.modulate.a = 1.0 if vis else 0.45
			else: vw.visible = vis
		"gm_anuncio":
			game.hud.banner_mostrar("AVISO DO SERVIDOR", str(d.get("texto", "")), COR_GM)

static func pedir(game, a: String, extra := {}) -> void:
	if game.rede == null or not ativo: return
	var m := {"t": "gm", "a": a}
	m.merge(extra, true)
	game.rede.enviar_srv(m)

static func aberto(game) -> bool:
	return game.janelas.aberta("gm")

static func alternar(game) -> void:
	if not ativo: return
	if aberto(game): game.janelas.fechar("gm"); return
	abrir(game)

## F7: teleporte para onde o mouse aponta (mesmo mapa).
static func ponto(game) -> void:
	if ativo: pedir(game, "ir_ponto", {"pos": game.mouse_mundo()})

# =================================================================== janela
static func abrir(game) -> void:
	var J = game.janelas
	var c: VBoxContainer = J._janela("gm", "PAINEL DO GM", Vector2(860, 590), "centro")
	J.jan["gm"].offset_top = -345; J.jan["gm"].offset_bottom = 245
	if not J.jan["gm"].has_node("Pulso"):   # a lista de jogadores se atualiza sozinha enquanto a janela está aberta
		var t := Timer.new(); t.name = "Pulso"; t.wait_time = 3.0; t.autostart = true
		t.timeout.connect(func(): if aberto(game): pedir(game, "estado"))
		J.jan["gm"].add_child(t)
	J._limpar(c)
	_ui.clear()
	c.add_child(_cabecalho(game))
	var abas := HBoxContainer.new(); abas.add_theme_constant_override("separation", 2)
	for a in ABAS:
		var b := Button.new(); b.text = a[1]; b.toggle_mode = true; b.button_pressed = aba == a[0]
		b.focus_mode = Control.FOCUS_NONE
		Tema.estilo_aba(b, aba == a[0])
		b.pressed.connect(func(): aba = a[0]; _clique(game); abrir(game))
		abas.add_child(b)
	c.add_child(abas)
	var corpo := PanelContainer.new(); corpo.size_flags_vertical = Control.SIZE_EXPAND_FILL
	corpo.add_theme_stylebox_override("panel", Tema.caixa_menu(10))
	c.add_child(corpo)
	match aba:
		"jogadores": _aba_jogadores(game, corpo)
		"invocar": _aba_invocar(game, corpo)
		"itens": _aba_itens(game, corpo)
		"eventos": _aba_eventos(game, corpo)
		"viajar": _aba_viajar(game, corpo)
	var rod := HBoxContainer.new()
	var mg := MarginContainer.new(); mg.add_theme_constant_override("margin_left", 12); mg.add_theme_constant_override("margin_right", 14)
	mg.add_child(rod)
	var st := Tema.rotulo(_status, 13, COR_GM, Tema.FONTE_ITALICO); st.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	st.clip_text = true; _ui["status"] = st
	rod.add_child(st)
	rod.add_child(Tema.rotulo("F8 abre e fecha · F7 teleporta ao mouse", 12, Color("#7d7466"), Tema.FONTE_ITALICO))
	c.add_child(mg)
	if estado.is_empty(): pedir(game, "estado")

static func _atualizar(game) -> void:
	if _ui.has("status") and is_instance_valid(_ui["status"]): _ui["status"].text = _status
	if _ui.has("info") and is_instance_valid(_ui["info"]): _ui["info"].text = _info_txt()
	for k in ["invisivel", "imortal"]:
		if _ui.has(k) and is_instance_valid(_ui[k]): _marcar(_ui[k], bool(estado.get(k, false)))
	if aba == "jogadores" and _ui.has("lista") and is_instance_valid(_ui["lista"]): _encher_jogadores(game)
	if aba == "eventos" and _ui.has("agrak") and is_instance_valid(_ui["agrak"]):
		_ui["agrak"].text = _agrak_txt(); _ui["hermon"].text = _hermon_txt()

static func _clique(game) -> void:
	game.audio.tocar("ui/clique", null, -6.0)

# ------------------------------------------------------------------- peças
static func _info_txt() -> String:
	var up := int(estado.get("uptime", 0))
	return "Conta %s  ·  %d online  ·  %d mapas abertos  ·  servidor no ar há %dh%02d" % [conta, estado.get("jogadores", []).size(),
		int(estado.get("mapas_ativos", 0)), up / 3600, (up % 3600) / 60]

static func _cabecalho(game) -> Control:
	var p := PanelContainer.new(); p.add_theme_stylebox_override("panel", Tema.caixa_menu(8))
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 8); p.add_child(h)
	var selo := Tema.rotulo("GM", 22, COR_GM, Tema.FONTE_GOTICA, 3); h.add_child(selo)
	var info := Tema.rotulo(_info_txt(), 13, COR_FRACO); info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.vertical_alignment = VERTICAL_ALIGNMENT_CENTER; _ui["info"] = info
	h.add_child(info)
	var bi := _botao("Invisível", func(): pedir(game, "invisivel", {"v": not bool(estado.get("invisivel", false))}), 120)
	bi.tooltip_text = "Monstros e jogadores deixam de te ver (você fica translúcido na sua tela)."
	_marcar(bi, bool(estado.get("invisivel", false))); _ui["invisivel"] = bi; h.add_child(bi)
	var bm := _botao("Imortal", func(): pedir(game, "imortal", {"v": not bool(estado.get("imortal", false))}), 110)
	bm.tooltip_text = "Nenhum dano te atinge."
	_marcar(bm, bool(estado.get("imortal", false))); _ui["imortal"] = bm; h.add_child(bm)
	h.add_child(_botao("Curar", func(): pedir(game, "curar"), 90))
	return p

static func _botao(txt: String, acao: Callable, larg := 0) -> Button:
	var b := Button.new(); b.text = txt; b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(larg, 32)
	b.add_theme_font_size_override("font_size", 14)
	b.pressed.connect(acao)
	return b

## Botão ligado: afundado no latão, como as skills ligadas do automático.
static func _marcar(b: Button, on: bool) -> void:
	var sb := Tema.sb_ui("menu_botao_press", [14, 14, 14, 14], [16, 7, 16, 8]) if on else null
	for est in ["normal", "hover"]:
		if sb: b.add_theme_stylebox_override(est, sb)
		else: b.remove_theme_stylebox_override(est)
	if on: b.add_theme_color_override("font_color", Color("#ffd58a"))
	else: b.remove_theme_color_override("font_color")

static func _secao(txt: String) -> Label:
	var l := Tema.rotulo(txt.to_upper(), 13, COR_SECAO, Tema.FONTE_TITULO, 2)
	l.custom_minimum_size.y = 18
	return l

static func _campo(dica: String, larg := 0, txt := "") -> LineEdit:
	var e := LineEdit.new(); e.placeholder_text = dica; e.text = txt
	e.custom_minimum_size = Vector2(larg, 30)
	e.add_theme_font_override("font", Tema.FONTE_TEXTO); e.add_theme_font_size_override("font_size", 14)
	return e

## Contador − valor + (sem o SpinBox padrão do Godot).
static func _contador(rotulo: String, chave: String, minimo: int, maximo: int, passo := 1, zero_txt := "") -> HBoxContainer:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 4)
	var l := Tema.rotulo(rotulo, 14, COR_FRACO); l.custom_minimum_size.x = 92; l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	h.add_child(l)
	var val := Tema.rotulo("", 17, COR_TITULO, Tema.FONTE_TITULO, 2)
	val.custom_minimum_size.x = 64; val.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; val.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	var mostrar := func(): val.text = zero_txt if int(v[chave]) == 0 and zero_txt != "" else str(v[chave])
	var menos := _botao("−", func(): v[chave] = clampi(int(v[chave]) - passo, minimo, maximo); mostrar.call(), 34)
	var mais := _botao("+", func(): v[chave] = clampi(int(v[chave]) + passo, minimo, maximo); mostrar.call(), 34)
	h.add_child(menos); h.add_child(val); h.add_child(mais)
	mostrar.call()
	return h

## Lista no estilo do kit (moldura de latão, seleção em latão escuro).
static func _lista() -> ItemList:
	var il := ItemList.new(); il.size_flags_vertical = Control.SIZE_EXPAND_FILL; il.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	il.add_theme_stylebox_override("panel", Tema.caixa(Color(0.045, 0.037, 0.03, 0.96), Color(0.3, 0.25, 0.17), 1, 2))
	il.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var sel := Tema.caixa(Color(0.24, 0.17, 0.08, 0.95), Color("#b08d4f"), 1, 2); sel.set_content_margin_all(2)
	il.add_theme_stylebox_override("selected", sel); il.add_theme_stylebox_override("selected_focus", sel)
	var hv := Tema.caixa(Color(0.15, 0.11, 0.07, 0.9), Color(0.3, 0.25, 0.17), 1, 2)
	il.add_theme_stylebox_override("hovered", hv)
	il.add_theme_font_override("font", Tema.FONTE_TEXTO); il.add_theme_font_size_override("font_size", 14)
	il.add_theme_color_override("font_color", Color("#d8ccb0")); il.add_theme_color_override("font_selected_color", Color("#ffe2a0"))
	il.add_theme_color_override("font_hovered_color", Color("#f0e2c0"))
	il.add_theme_constant_override("v_separation", 3)
	il.fixed_icon_size = Vector2i(28, 28)
	return il

# =================================================================== aba Jogadores
static func _aba_jogadores(game, corpo: Control) -> void:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 12); corpo.add_child(h)
	var esq := VBoxContainer.new(); esq.size_flags_horizontal = Control.SIZE_EXPAND_FILL; h.add_child(esq)
	esq.add_child(_secao("Online agora"))
	var il := _lista(); _ui["lista"] = il
	il.item_selected.connect(func(i: int):
		nome_sel = str(il.get_item_metadata(i)); _clique(game)
		if _ui.has("nome") and is_instance_valid(_ui["nome"]): _ui["nome"].text = nome_sel)
	esq.add_child(il)
	_encher_jogadores(game)
	var dir := VBoxContainer.new(); dir.custom_minimum_size.x = 330; dir.add_theme_constant_override("separation", 6); h.add_child(dir)
	dir.add_child(_secao("Jogador"))
	var nome := _campo("personagem ou conta (vale offline)", 0, nome_sel); _ui["nome"] = nome
	nome.text_changed.connect(func(t): nome_sel = t.strip_edges())
	dir.add_child(nome)
	var g := GridContainer.new(); g.columns = 2; g.add_theme_constant_override("h_separation", 6); g.add_theme_constant_override("v_separation", 6)
	g.add_child(_botao("Ir até ele", func(): pedir(game, "ir_jogador", {"nome": nome_sel}), 160))
	g.add_child(_botao("Trazer até mim", func(): pedir(game, "trazer", {"nome": nome_sel}), 160))
	g.add_child(_botao("Curar e reviver", func(): pedir(game, "curar", {"alvo": nome_sel}), 160))
	g.add_child(_botao("Alvo dos itens", func(): alvo = nome_sel; _status = "Itens, ouro e nível vão para %s." % nome_sel; _atualizar(game), 160))
	dir.add_child(g)
	dir.add_child(_secao("Punição"))
	var motivo := _campo("motivo (aparece para ele e no registro)"); dir.add_child(motivo)
	var g2 := GridContainer.new(); g2.columns = 3; g2.add_theme_constant_override("h_separation", 6); g2.add_theme_constant_override("v_separation", 6)
	g2.add_child(_botao("Silenciar 10 min", func(): pedir(game, "silenciar", {"nome": nome_sel, "min": 10}), 106))
	g2.add_child(_botao("Silenciar 1 h", func(): pedir(game, "silenciar", {"nome": nome_sel, "min": 60}), 106))
	g2.add_child(_botao("Liberar fala", func(): pedir(game, "silenciar", {"nome": nome_sel, "min": 0}), 106))
	g2.add_child(_botao("Expulsar", func(): pedir(game, "expulsar", {"nome": nome_sel, "motivo": motivo.text}), 106))
	g2.add_child(_botao("Banir 1 dia", func(): pedir(game, "banir", {"nome": nome_sel, "dias": 1, "motivo": motivo.text}), 106))
	g2.add_child(_botao("Banir 7 dias", func(): pedir(game, "banir", {"nome": nome_sel, "dias": 7, "motivo": motivo.text}), 106))
	dir.add_child(g2)
	var bp := _botao("Banir para sempre", func(): pedir(game, "banir", {"nome": nome_sel, "dias": 0, "motivo": motivo.text}))
	bp.add_theme_color_override("font_color", Tema.COR_SANGUE.lightened(0.25))
	dir.add_child(bp)
	dir.add_child(_botao("Tirar banimento e silêncio", func(): pedir(game, "desbanir", {"nome": nome_sel})))

static func _encher_jogadores(game) -> void:
	var il: ItemList = _ui["lista"]
	var rol := il.get_v_scroll_bar().value
	il.clear()
	for j in estado.get("jogadores", []):
		var nm: String = NOME_CLASSE.get(str(j["classe"]), str(j["classe"]).capitalize())
		if str(j.get("evolucao", "")) != "": nm = str(Evolucao.defn(str(j["evolucao"])).get("nome", nm))
		var linha := "%s   nv %d  ·  %s  ·  %s%s%s" % [j["nome"], int(j["nivel"]), nm, j["local"], "   (mudo)" if j.get("mudo", false) else "",
			"   (morto)" if not j.get("vivo", true) else ""]
		var i := il.add_item(linha)
		il.set_item_metadata(i, str(j["nome"]))
		il.set_item_tooltip(i, "conta %s · %d de ouro · mapa %s" % [j["conta"], int(j.get("ouro", 0)), j["mapa"]])
		if j.get("gm", false): il.set_item_custom_fg_color(i, COR_GM)
		if str(j["nome"]) == nome_sel: il.select(i)
	if il.item_count == 0: il.add_item("Ninguém online.", null, false)
	il.get_v_scroll_bar().value = rol

# =================================================================== aba Invocar
static func _aba_invocar(game, corpo: Control) -> void:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 14); corpo.add_child(h)
	var esq := VBoxContainer.new(); esq.size_flags_horizontal = Control.SIZE_EXPAND_FILL; esq.add_theme_constant_override("separation", 6); h.add_child(esq)
	esq.add_child(_secao("Monstros"))
	var busca := _campo("procurar monstro"); esq.add_child(busca)
	var il := _lista(); esq.add_child(il)
	var encher := func(f: String):
		il.clear()
		var ids: Array = Defs.MOBS.keys()
		ids.sort_custom(func(a, b): return int(Defs.MOBS[a].get("niveis", [1, 1])[0]) < int(Defs.MOBS[b].get("niveis", [1, 1])[0]))
		for id in ids:
			var nm := str(Defs.MON_TXT.get(id, {}).get("nome", Defs.MOBS[id].get("nome", id)))
			if f != "" and not (nm.to_lower().contains(f.to_lower()) or str(id).contains(f.to_lower())): continue
			var nv: Array = Defs.MOBS[id].get("niveis", [1, 1])
			var i := il.add_item("%s   nv %d-%d" % [nm, int(nv[0]), int(nv[1])])
			il.set_item_metadata(i, id)
			if id == mob_sel: il.select(i)
	encher.call("")
	busca.text_changed.connect(encher)
	il.item_selected.connect(func(i): mob_sel = str(il.get_item_metadata(i)))
	var linha := HBoxContainer.new(); linha.add_theme_constant_override("separation", 14)
	linha.add_child(_contador("Nível", "nivel", 0, 400, 1, "padrão"))
	linha.add_child(_contador("Quantos", "qtd", 1, 20))
	esq.add_child(linha)
	var l2 := HBoxContainer.new(); l2.add_theme_constant_override("separation", 6)
	var bn := _botao("", func(): pass, 170)
	var ntxt := func(): bn.text = "Postura: %s" % ("neutro" if v["neutro"] else "agressivo")
	bn.pressed.connect(func(): v["neutro"] = not v["neutro"]; ntxt.call())
	ntxt.call(); l2.add_child(bn)
	var bi := _botao("Invocar perto de mim", func():
		if mob_sel == "": _status = "Escolha um monstro na lista."; _atualizar(game); return
		pedir(game, "invocar", {"kind": mob_sel, "nivel": v["nivel"], "qtd": v["qtd"], "neutro": v["neutro"]}))
	bi.size_flags_horizontal = Control.SIZE_EXPAND_FILL; bi.add_theme_color_override("font_color", Color("#f0dca0"))
	l2.add_child(bi)
	esq.add_child(l2)
	# chefes
	var dir := VBoxContainer.new(); dir.custom_minimum_size.x = 320; dir.add_theme_constant_override("separation", 6); h.add_child(dir)
	dir.add_child(_secao("Chefes"))
	var ic := _lista(); dir.add_child(ic)
	var cids: Array = Defs.CHEFES.keys()
	cids.sort_custom(func(a, b): return int(Defs.CHEFES[a].get("nivel", 0)) < int(Defs.CHEFES[b].get("nivel", 0)))
	for id in cids:
		var i := ic.add_item("%s   nv %d" % [Defs.CHEFES[id].get("nome", id), int(Defs.CHEFES[id].get("nivel", 0))])
		ic.set_item_metadata(i, id)
		if id == chefe_sel: ic.select(i)
	ic.item_selected.connect(func(i): chefe_sel = str(ic.get_item_metadata(i)))
	var ba := _botao("", func(): pass)
	var atxt := func(): ba.text = "Anunciar no chat: %s" % ("sim" if v["anunciar"] else "não")
	ba.pressed.connect(func(): v["anunciar"] = not v["anunciar"]; atxt.call())
	atxt.call(); dir.add_child(ba)
	var bc := _botao("Invocar chefe aqui", func():
		if chefe_sel == "": _status = "Escolha um chefe na lista."; _atualizar(game); return
		pedir(game, "chefe", {"kind": chefe_sel, "anunciar": v["anunciar"]}))
	bc.add_theme_color_override("font_color", Color("#f0dca0")); dir.add_child(bc)
	dir.add_child(_botao("Reviver o chefe desta dungeon", func(): pedir(game, "reviver_chefe")))
	var g := HBoxContainer.new(); g.add_theme_constant_override("separation", 6)
	var b1 := _botao("Matar em volta", func(): pedir(game, "matar_perto", {"raio": 8.0})); b1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var b2 := _botao("Limpar invocações", func(): pedir(game, "limpar")); b2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	g.add_child(b1); g.add_child(b2); dir.add_child(g)

# =================================================================== aba Itens e nível
static func _aba_itens(game, corpo: Control) -> void:
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 14); corpo.add_child(h)
	var esq := VBoxContainer.new(); esq.size_flags_horizontal = Control.SIZE_EXPAND_FILL; esq.add_theme_constant_override("separation", 6); h.add_child(esq)
	esq.add_child(_secao("Criar item"))
	var busca := _campo("procurar item (nome ou id)"); esq.add_child(busca)
	var il := _lista(); esq.add_child(il)
	var encher := func(f: String):
		il.clear()
		var n := 0
		var ids: Array = Defs.ITENS.keys(); ids.sort()
		for id in ids:
			var nm := str(Defs.ITENS[id].get("nome", id))
			if f != "" and not (nm.to_lower().contains(f.to_lower()) or str(id).contains(f.to_lower())): continue
			var tx: Texture2D = null
			var icn := Tema.icone_item(id)
			if icn.size() == 2:
				var at := AtlasTexture.new(); at.atlas = icn[0]; at.region = icn[1]; tx = at
			var i := il.add_item(nm, tx)
			il.set_item_metadata(i, id)
			il.set_item_custom_fg_color(i, Defs.cor_raridade(str(Defs.ITENS[id].get("raridade", "comum"))).lerp(Color("#d8ccb0"), 0.35))
			il.set_item_tooltip(i, id)
			if id == item_sel: il.select(i)
			n += 1
			if n >= 400: break   # a busca afunila o resto
	encher.call("")
	busca.text_changed.connect(encher)
	il.item_selected.connect(func(i): item_sel = str(il.get_item_metadata(i)))
	# direita: quem recebe, opções do item, ouro e nível
	var dir := VBoxContainer.new(); dir.custom_minimum_size.x = 340; dir.add_theme_constant_override("separation", 6); h.add_child(dir)
	dir.add_child(_secao("Para quem"))
	var pq := HBoxContainer.new(); pq.add_theme_constant_override("separation", 6)
	var ca := _campo("eu mesmo", 0, alvo); ca.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ca.text_changed.connect(func(t): alvo = t.strip_edges())
	pq.add_child(ca)
	pq.add_child(_botao("Eu", func(): alvo = ""; ca.text = "", 60))
	dir.add_child(pq)
	dir.add_child(_secao("Item"))
	dir.add_child(_contador("Quantidade", "iqtd", 1, 999))
	dir.add_child(_contador("Refino", "refino", 0, 15, 1, "+0"))
	var br := _botao("", func(): pass)
	var rtxt := func(): br.text = "Raridade: %s" % NOME_RAR[RARIDADES[int(v["rar"])]]
	br.pressed.connect(func(): v["rar"] = (int(v["rar"]) + 1) % RARIDADES.size(); rtxt.call())
	br.tooltip_text = "Equipamento: escolhe a raridade e rola as opções. \"do item\" = como o item vem."
	rtxt.call(); dir.add_child(br)
	var bc := _botao("Criar", func():
		if item_sel == "": _status = "Escolha um item na lista."; _atualizar(game); return
		pedir(game, "item", {"id": item_sel, "qtd": v["iqtd"], "refino": v["refino"], "raridade": RARIDADES[int(v["rar"])], "alvo": alvo}))
	bc.add_theme_color_override("font_color", Color("#f0dca0")); dir.add_child(bc)
	dir.add_child(_secao("Ouro"))
	var lo := HBoxContainer.new(); lo.add_theme_constant_override("separation", 6)
	var co := _campo("quantia", 0, "100000"); co.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lo.add_child(co)
	lo.add_child(_botao("Dar", func(): pedir(game, "ouro", {"qtd": int(co.text), "alvo": alvo}), 70))
	lo.add_child(_botao("Tirar", func(): pedir(game, "ouro", {"qtd": -int(co.text), "alvo": alvo}), 70))
	dir.add_child(lo)
	dir.add_child(_secao("Nível"))
	var ln := HBoxContainer.new(); ln.add_theme_constant_override("separation", 6)
	var cn := _campo("1 a 400", 90, "50"); ln.add_child(cn)
	var bnv := _botao("Definir nível", func(): pedir(game, "nivel", {"nivel": int(cn.text), "alvo": alvo}))
	bnv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; bnv.tooltip_text = "Os pontos de atributo voltam para distribuir."
	ln.add_child(bnv)
	dir.add_child(ln)

# =================================================================== aba Eventos
static func _tempo(s: int) -> String:
	if s >= 3600: return "%dh%02d" % [s / 3600, (s % 3600) / 60]
	return "%d:%02d" % [s / 60, s % 60]

static func _agrak_txt() -> String:
	return "Próxima luta em %s  ·  %d inscritos  ·  mínimo %d" % [_tempo(int(estado.get("agrak_falta", 0))), int(estado.get("agrak_inscritos", 0)), int(estado.get("agrak_min", 1))]

static func _hermon_txt() -> String:
	if estado.get("hermon_aberto", false): return "Entrada aberta agora (5 min com o Convite dos Vigilantes)"
	return "Abre em %s" % _tempo(int(estado.get("hermon_falta", 0)))

static func _cartao(titulo: String, sub: String) -> Array:
	var sb := Tema.caixa(Color(0.06, 0.05, 0.04, 0.9), Color(0.3, 0.25, 0.17), 1, 2); sb.set_content_margin_all(10)
	var p := PanelContainer.new(); p.add_theme_stylebox_override("panel", sb)
	var vb := VBoxContainer.new(); vb.add_theme_constant_override("separation", 6); p.add_child(vb)
	vb.add_child(Tema.rotulo(titulo, 19, COR_TITULO, Tema.FONTE_GOTICA, 2))
	var s := Tema.rotulo(sub, 13, COR_FRACO, Tema.FONTE_ITALICO); vb.add_child(s)
	return [p, vb, s]

static func _aba_eventos(game, corpo: Control) -> void:
	var vb := VBoxContainer.new(); vb.add_theme_constant_override("separation", 10); corpo.add_child(vb)
	var h := HBoxContainer.new(); h.add_theme_constant_override("separation", 12); vb.add_child(h)
	var ag := _cartao("O Agrak", _agrak_txt()); _ui["agrak"] = ag[2]
	ag[0].size_flags_horizontal = Control.SIZE_EXPAND_FILL; h.add_child(ag[0])
	ag[1].add_child(_botao("Abrir inscrição (luta em 1 min)", func(): pedir(game, "agrak", {"modo": "abrir"})))
	ag[1].add_child(_botao("Começar agora com os inscritos", func(): pedir(game, "agrak", {"modo": "comecar"})))
	var lm := HBoxContainer.new(); lm.add_theme_constant_override("separation", 6)
	v["amin"] = int(estado.get("agrak_min", 1))
	lm.add_child(_contador("Mínimo", "amin", 1, 20))
	var bm := _botao("Usar", func(): pedir(game, "agrak", {"modo": "minimo", "v": v["amin"]}), 70); lm.add_child(bm)
	ag[1].add_child(lm)
	var hm := _cartao("O Cume dos Vigilantes", _hermon_txt()); _ui["hermon"] = hm[2]
	hm[0].size_flags_horizontal = Control.SIZE_EXPAND_FILL; h.add_child(hm[0])
	hm[1].add_child(_botao("Abrir a entrada agora", func(): pedir(game, "hermon", {"modo": "agora"})))
	hm[1].add_child(_botao("Início imediato", func(): pedir(game, "hermon", {"modo": "iniciar"})))
	hm[1].add_child(_botao("Abrir em 5 min (com avisos)", func(): pedir(game, "hermon", {"modo": "5min"})))
	hm[1].add_child(_botao("Voltar à agenda normal", func(): pedir(game, "hermon", {"modo": "fechar"})))
	var cv := _cartao("Os Cavaleiros do Apocalipse", "Agonia, Danação, Perdição e Lamento descem juntos sobre as capitais. Cada um pode deixar a sua montaria.")
	cv[0].size_flags_horizontal = Control.SIZE_EXPAND_FILL; h.add_child(cv[0])
	cv[1].add_child(_botao("Chamar os Cavaleiros agora", func(): pedir(game, "cavaleiros", {"modo": "iniciar"})))
	var dica := Tema.rotulo("A Torre e as dungeons: use \"Reviver o chefe desta dungeon\" na aba Invocar, de dentro do andar.", 13, Color("#7d7466"), Tema.FONTE_ITALICO)
	vb.add_child(dica)
	var av := _cartao("Aviso a todo o servidor", "Aparece no chat de sistema e numa faixa no alto da tela de todos.")
	vb.add_child(av[0])
	var la := HBoxContainer.new(); la.add_theme_constant_override("separation", 6)
	var ca := _campo("ex.: o servidor reinicia em 10 minutos"); ca.size_flags_horizontal = Control.SIZE_EXPAND_FILL; ca.max_length = 200
	var enviar := func(_t: String):
		if ca.text.strip_edges() == "": return
		pedir(game, "aviso_global", {"texto": ca.text}); ca.text = ""
	ca.text_submitted.connect(enviar)
	la.add_child(ca)
	var be := _botao("Enviar a todos", func(): enviar.call(""), 150); be.add_theme_color_override("font_color", Color("#f0dca0"))
	la.add_child(be)
	av[1].add_child(la)

# =================================================================== aba Viajar
static func _aba_viajar(game, corpo: Control) -> void:
	var vb := VBoxContainer.new(); vb.add_theme_constant_override("separation", 6); corpo.add_child(vb)
	var topo := HBoxContainer.new(); topo.add_theme_constant_override("separation", 8)
	topo.add_child(_secao("Ir para um mapa"))
	var busca := _campo("procurar mapa"); busca.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	topo.add_child(busca); vb.add_child(topo)
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var g := GridContainer.new(); g.columns = 3; g.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	g.add_theme_constant_override("h_separation", 6); g.add_theme_constant_override("v_separation", 6)
	sc.add_child(g); vb.add_child(sc)
	var encher := func(f: String):
		for x in g.get_children(): g.remove_child(x); x.queue_free()
		for id in estado.get("mapas", []):
			var nm := Defs.nome_local(id)
			if nm == "" or nm == id: nm = str(id).replace("_", " ").capitalize()
			if f != "" and not (nm.to_lower().contains(f.to_lower()) or str(id).contains(f.to_lower())): continue
			var b := _botao(nm, func(): pedir(game, "ir_mapa", {"mapa": id}))
			b.size_flags_horizontal = Control.SIZE_EXPAND_FILL; b.clip_text = true; b.tooltip_text = id
			if game.sim != null and game.sim.mapa_id == id: b.add_theme_color_override("font_color", COR_GM)
			g.add_child(b)
	encher.call("")
	busca.text_changed.connect(encher)
	vb.add_child(Tema.rotulo("Dica: F7 te leva para o ponto do mouse dentro do mapa. \"Ir até ele\" na aba Jogadores atravessa mapas.", 13, Color("#7d7466"), Tema.FONTE_ITALICO))

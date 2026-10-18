extends CanvasLayer
## Janelas: mochila e equipamento, personagem, habilidades, diário de missões, diálogo, loja, forja, armazém,
## treinador, textos de lore e menu. Itens se movem MU-style: clique pega, clique solta (ou arraste).

var game
var raiz := Control.new()
var jan := {}                 # nome -> PanelContainer
var corpo := {}               # nome -> Control de conteúdo
var servico_d := {}
var dialogo_d := {}
var dialogo_t := 0.0
var mao := {}                 # item na mão: {it, de, slot}
var mao_ui: Control
var alvos_soltar: Array = []  # Controls que aceitam item (grades e slots)
var missao_sel := ""
var troca_d := {}             # estado da troca que o servidor mandou (vazio = sem troca)
var troca_ok_ms := 0          # quando o botão Confirmar acende (o servidor só aceita depois disso)
var _sel_aba := "ativas"
var estante_livros: Array = []   # aba Biblioteca do diário: [{id, titulo}] que o servidor mandou (Biblioteca.estante_pessoal)
var estante_sel := ""
var textos_lidos := {}           # id -> {titulo, texto}: só nesta sessão, nunca em disco

const CEL := 30
const POS_EQUIP := {
	"cabeca": Rect2(4, 4, 52, 52), "peito": Rect2(4, 62, 52, 66), "calcas": Rect2(4, 134, 52, 52),
	"arma": Rect2(60, 4, 52, 124), "anel1": Rect2(60, 134, 52, 52),
	"segunda_mao": Rect2(268, 4, 52, 124), "anel2": Rect2(268, 134, 52, 52),
	"amuleto": Rect2(324, 4, 52, 52), "luvas": Rect2(324, 62, 52, 66), "botas": Rect2(324, 134, 52, 52)}
const AREA_EQUIP := Vector2(380, 236)
var _ganho_cache := {}        # uid -> quanto o Poder sobe ao equipar (cache por atualização do inventário)
var _poder_cache := -1
var _poder_flash := {}        # {v, t}: número que sobe da placa quando o Poder muda
var _poder_visto := -1
var _grade_mochila: Control

func _ready() -> void:
	layer = 20
	raiz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = Tema.tema_janelas()
	add_child(raiz)
	var cl := CanvasLayer.new(); cl.layer = 25; add_child(cl)
	mao_ui = Desenho.new()
	mao_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mao_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mao_ui.desenhar = _desenhar_mao
	cl.add_child(mao_ui)

func _jog() -> Ent: return game.jog
func _sim() -> WorldSim: return game.sim

class Desenho extends Control:
	var desenhar: Callable
	var entrada: Callable
	var dados := {}
	func _draw() -> void:
		if desenhar.is_valid(): desenhar.call(self)
	func _gui_input(ev: InputEvent) -> void:
		if entrada.is_valid(): entrada.call(self, ev)

# =================================================================== base das janelas
func _janela(nome: String, titulo: String, tam: Vector2, onde: String) -> VBoxContainer:
	if game.hud.mapa_ui and game.hud.mapa_ui.visible: game.hud.mapa_ui.visible = false
	if jan.has(nome):
		jan[nome].visible = true
		return corpo[nome]
	var p := PanelContainer.new()
	var sb: StyleBox = _sb("menu_moldura", [56, 56, 56, 56], [18, 16, 18, 18])
	if sb == null:
		sb = Tema.caixa(Color(0.065, 0.052, 0.045, 0.96), Color(0.42, 0.34, 0.2), 2, 3)
		sb.set_content_margin_all(12)
	p.add_theme_stylebox_override("panel", sb)
	p.custom_minimum_size = tam
	p.mouse_filter = Control.MOUSE_FILTER_STOP
	match onde:
		"direita":
			p.set_anchors_preset(Control.PRESET_TOP_RIGHT)
			p.offset_left = -tam.x - 14; p.offset_right = -14; p.offset_top = 56; p.offset_bottom = 56 + tam.y
		"esquerda":
			p.set_anchors_preset(Control.PRESET_TOP_LEFT)
			p.offset_left = 14; p.offset_right = 14 + tam.x; p.offset_top = 56; p.offset_bottom = 56 + tam.y
		"centro":
			p.set_anchors_preset(Control.PRESET_CENTER)
			p.offset_left = -tam.x * 0.5; p.offset_right = tam.x * 0.5; p.offset_top = -tam.y * 0.5 - 40; p.offset_bottom = tam.y * 0.5 - 40
		"baixo":
			p.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
			p.offset_left = -tam.x * 0.5; p.offset_right = tam.x * 0.5; p.offset_top = -tam.y - 168; p.offset_bottom = -168
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	p.add_child(v)
	var topo := HBoxContainer.new()
	var tl := Tema.rotulo(titulo, 20, Color("#e0c890"), Tema.FONTE_TITULO, 3)
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tl.name = "Titulo"
	var placa := _sb("menu_titulo", [60, 0, 60, 0], [44, 3, 44, 7])
	if placa: tl.add_theme_stylebox_override("normal", placa); tl.custom_minimum_size.y = 40
	topo.add_child(tl)
	var x := Button.new(); x.text = "✕"; x.custom_minimum_size = Vector2(26, 24)
	x.add_theme_font_override("font", Tema.FONTE_TEXTO)
	Tema.estilo_fechar(x)
	x.pressed.connect(func(): fechar(nome))
	topo.add_child(x)
	v.add_child(topo)
	if placa == null:
		var linha := ColorRect.new(); linha.color = Color(0.42, 0.34, 0.2, 0.6); linha.custom_minimum_size.y = 1
		v.add_child(linha)
	var c := VBoxContainer.new()
	c.add_theme_constant_override("separation", 8)
	c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(c)
	raiz.add_child(p)
	jan[nome] = p; corpo[nome] = c
	game.audio.tocar("ui/abrir_janela", null, -6.0)
	return c

func _sb(peca: String, m: Array, cm: Array = []) -> StyleBoxTexture:
	return Tema.sb_ui(peca, m, cm)

func _titulo(nome: String, txt: String) -> void:
	if jan.has(nome): jan[nome].get_child(0).get_child(0).get_node("Titulo").text = txt

func aberta(nome: String) -> bool:
	return jan.has(nome) and jan[nome].visible

func alternar(nome: String) -> void:
	if aberta(nome): fechar(nome); return
	match nome:
		"inventario": abrir_inventario()
		"personagem": abrir_personagem()
		"habilidades": abrir_habilidades()
		"missoes": abrir_missoes()
		"menu": abrir_menu()
		"auto": abrir_auto()
		"talentos": abrir_talentos()
		"teleporte": abrir_teleporte()

func fechar(nome: String) -> void:
	if not jan.has(nome): return
	if jan[nome].visible: game.audio.tocar("ui/fechar_janela", null, -6.0)
	jan[nome].visible = false
	game.hud.esconder_tip()
	match nome:
		"dialogo":
			_jog().aux.erase("dialogo"); dialogo_d = {}; game.cmd("fechar", ["dialogo"])
		"servico":
			_jog().aux.erase("servico"); servico_d = {}; game.cmd("fechar", ["servico"])
			if aberta("armazem"): fechar("armazem")
		"armazem":
			if not servico_d.is_empty() and servico_d.get("tipo") == "armazem": fechar("servico")
		"inventario":
			if not mao.is_empty(): _devolver_mao()
		"troca":
			if not troca_d.is_empty(): game.troca_cmd("cancelar")
			troca_d = {}

func fechar_tudo() -> bool:
	var algum := false
	if not mao.is_empty(): _devolver_mao(); return true
	for n in jan.keys():
		if jan[n].visible: fechar(n); algum = true
	if game.hud.mapa_ui and game.hud.mapa_ui.visible: game.hud.mapa_ui.visible = false; algum = true
	if game.hud.ajuda_ui and game.hud.ajuda_ui.visible: game.hud.ajuda_ui.visible = false; algum = true
	return algum

func _limpar(c: Control) -> void:
	for f in c.get_children(): c.remove_child(f); f.queue_free()

func atualizar() -> void:
	_limpar_cache_poder()
	if game.jog:
		var p := poder()
		if _poder_visto >= 0 and p != _poder_visto and aberta("inventario"):
			_poder_flash = {"v": p - _poder_visto, "t": 1.8}
			if p > _poder_visto: game.audio.tocar("ui/confirmar", null, -12.0)
		_poder_visto = p
	if aberta("inventario"): _atualizar_inventario()
	if aberta("personagem"): abrir_personagem()
	if aberta("teleporte"): abrir_teleporte()
	if aberta("servico") and servico_d.get("tipo") == "ferreiro": _corpo_ferreiro()
	_atualizar_arca()
	for n in ["inventario", "servico"]:
		if jan.has(n): _redesenhar(jan[n])

func _redesenhar(n: Node) -> void:
	if n is CanvasItem: n.queue_redraw()
	for c in n.get_children(): _redesenhar(c)

# =================================================================== Poder do equipamento (comparação e incentivo a equipar)
## Personagem de mentira com o equipamento trocado; "troca" é slot -> item ({} tira). Só o cliente usa.
func _simular(troca: Dictionary) -> Ent:
	var j := _jog()
	var f := Ent.new()
	f.tipo = j.tipo; f.kind = j.kind; f.classe = j.classe; f.faccao = j.faccao; f.nivel = j.nivel
	f.stats = j.stats; f.buffs = j.buffs; f.hp = 1.0
	f.equip = j.equip.duplicate()
	for s in troca:
		if (troca[s] as Dictionary).is_empty(): f.equip.erase(s)
		else: f.equip[s] = troca[s]
	Regras.recalc_jogador(f)
	return f

## Um número só para "quanto o personagem rende": dano por segundo e quanto aguenta.
func _poder_de(f: Ent) -> int:
	var crit := f.critico * maxf(f.crit_mult - 1.0, 0.0)
	var dps := f.dano_medio() * (1.0 + crit) * (1.0 + f.excelente * 0.5) / maxf(f.intervalo, 0.15)
	var aguenta := f.hp_max * (1.0 + f.defesa / 100.0)
	return roundi(dps * 3.0 + aguenta * 0.2)

func poder() -> int:
	if _poder_cache < 0: _poder_cache = _poder_de(_simular({}))
	return _poder_cache

## Troca que equipar "it" faria (anel escolhe o pior dos dois, duas mãos tira o escudo).
func _troca_para(it: Dictionary, slot: String) -> Dictionary:
	var j := _jog()
	var t := {slot: it}
	if slot == "arma" and int(Itens.defn(it["id"]).get("maos", 1)) == 2: t["segunda_mao"] = {}
	if slot == "segunda_mao" and j.equip.has("arma") and int(Itens.defn(j.equip["arma"]["id"]).get("maos", 1)) == 2: t["arma"] = {}
	return t

func _slots_de(it: Dictionary) -> Array:
	var sd := Itens.slot_de(it)
	return ["anel1", "anel2"] if sd == "anel" else ([sd] if sd != "" else [])

## [ganho de Poder, slot] do melhor jeito de equipar o item; ganho 0 se não dá para usar.
func _melhor_slot(it: Dictionary) -> Array:
	if not Itens.equipavel(it) or Itens.pode_usar(it, _jog()) != "": return [0, ""]
	var melhor := [-999999, ""]
	for s in _slots_de(it):
		var g := _poder_de(_simular(_troca_para(it, s))) - poder()
		if g > melhor[0]: melhor = [g, s]
	return melhor

func ganho(it: Dictionary) -> int:
	var uid := int(it.get("uid", -1))
	if not _ganho_cache.has(uid): _ganho_cache[uid] = _melhor_slot(it)[0]
	return _ganho_cache[uid]

func _limpar_cache_poder() -> void:
	_ganho_cache.clear(); _poder_cache = -1

## Quantos itens da mochila deixariam o personagem mais forte.
func melhorias_na_mochila() -> int:
	var n := 0
	for it in _jog().inv:
		if ganho(it) > 0: n += 1
	return n

## Algum item da mochila melhora este slot?
func _slot_tem_melhoria(slot: String) -> bool:
	for it in _jog().inv:
		if slot in _slots_de(it) and ganho(it) > 0 and _melhor_slot(it)[1] == slot: return true
	return false

func _comparacao(it: Dictionary) -> String:
	if not Itens.equipavel(it) or Itens.pode_usar(it, _jog()) != "": return ""
	var ms := _melhor_slot(it)
	var slot: String = ms[1]
	if slot == "": return ""
	var a := _simular({})
	var b := _simular(_troca_para(it, slot))
	var s := "[color=#6b5634]────────────[/color]\n"
	var atual: Dictionary = _jog().equip.get(slot, {})
	s += "[color=#a89f8c]Se equipar%s:[/color]\n" % ((" (no lugar de %s)" % Itens.nome(atual)) if not atual.is_empty() else "")
	var dp := _poder_de(b) - _poder_de(a)
	s += "Poder %d → [b]%d[/b] %s\n" % [_poder_de(a), _poder_de(b), _delta(dp)]
	var linhas := [["Dano", "%d–%d" % [roundi(a.dano_min), roundi(a.dano_max)], "%d–%d" % [roundi(b.dano_min), roundi(b.dano_max)], b.dano_medio() - a.dano_medio()],
		["Defesa", "%d" % roundi(a.defesa), "%d" % roundi(b.defesa), b.defesa - a.defesa],
		["Vida", "%d" % roundi(a.hp_max), "%d" % roundi(b.hp_max), b.hp_max - a.hp_max],
		["Crítico", "%d%%" % roundi(a.critico * 100.0), "%d%%" % roundi(b.critico * 100.0), (b.critico - a.critico) * 100.0],
		["Ataques por s", "%.2f" % (1.0 / maxf(a.intervalo, 0.1)), "%.2f" % (1.0 / maxf(b.intervalo, 0.1)), (1.0 / maxf(b.intervalo, 0.1) - 1.0 / maxf(a.intervalo, 0.1)) * 10.0]]
	for l in linhas:
		if absf(float(l[3])) < 0.5: continue
		s += "[color=#a89f8c]%s[/color] %s → %s %s\n" % [l[0], l[1], l[2], _delta(roundi(l[3])) if l[0] != "Ataques por s" else ("[color=#9cff3a]▲[/color]" if l[3] > 0 else "[color=#ff6a4a]▼[/color]")]
	return s

func _delta(v: int) -> String:
	if v > 0: return "[color=#9cff3a]▲ +%d[/color]" % v
	if v < 0: return "[color=#ff6a4a]▼ %d[/color]" % v
	return "[color=#8a8070]=[/color]"

# =================================================================== tooltip de item
## Linha de duas colunas (nome à esquerda, valor alinhado à direita) para a janela de item.
func _lin2(a: String, b: String) -> String:
	return "%s\t%s\n" % [a, b]

## Título de seção em versalete dourado (ATRIBUTOS, PROPRIEDADES ESPECIAIS).
func _titulo_secao(txt: String) -> String:
	return "\n[font_size=12][b][color=#d9b66a]%s[/color][/b][/font_size]\n" % txt.to_upper()

func tip_item(it: Dictionary, contexto := "") -> String:
	var d := Itens.defn(it["id"])
	var j := _jog()
	var rar: String = it.get("raridade", "comum")
	var cor := Defs.cor_raridade(rar).to_html(false)
	var slot := Itens.slot_de(it)
	var cat := Itens.categoria(it)
	# cabeçalho: nome na fonte de título, tipo à esquerda e nível à direita
	var s := "[b][font_size=22][color=#%s]%s[/color][/font_size][/b]\n" % [cor, Itens.nome(it)]
	var tipo := ""
	if slot != "": tipo = Itens.NOME_SLOT.get(slot if slot != "anel" else "anel1", slot)
	else: tipo = {"consumivel": "Consumível", "material": "Material", "joia": "Joia", "missao": "Item de missão", "leitura": "Escrito", "chave": "Chave", "bau": "Baú"}.get(cat, cat.capitalize())
	if slot == "arma" and int(d.get("maos", 1)) == 2: tipo += " (2 mãos)"
	if slot != "" or rar != "comum": tipo += " · " + Defs.nome_raridade(rar)
	var nv := int(d.get("nivel", 1))
	var direita := ""
	if slot != "" and nv > 1: direita = "[color=%s]Nível %d[/color]" % ["#ff6a4a" if j.nivel < nv else "#a89f8c", nv]
	s += _lin2("[i][color=#a89f8c]%s[/color][/i]" % tipo, direita)
	s += "[color=#6b5634]────────────────────────────────────[/color]\n"
	# ataque: número grande, como a arma de referência
	if slot == "arma":
		var dn := Itens.dano_arma(it)
		s += _titulo_secao("Ataque")
		s += "[font_size=24][b][color=#e8584a]%d ~ %d[/color][/b][/font_size]\n" % [roundi(dn[0]), roundi(dn[1])]
		if d.has("intervalo"): s += _lin2("[color=#a89f8c]Velocidade[/color]", "%.2f/s" % (1.0 / float(d["intervalo"])))
	# atributos e defesa em colunas: nome à esquerda, valor à direita
	var linhas := ""
	if d.has("defesa") and slot != "arma":
		linhas += _lin2("Defesa", "[color=#e0b84a]%d[/color]" % roundi(float(d["defesa"]) * (1.0 + 0.08 * int(it.get("refino", 0)))))
	if d.has("bloqueio"): linhas += _lin2("Bloqueio", "[color=#e0b84a]%d%%[/color]" % roundi(float(d["bloqueio"]) * 100.0))
	for src in ["atributos", "atributo_base"]:
		var at = d.get(src)
		if at is Dictionary:
			for k in at: linhas += _lin2(str(Itens.ATTR.get(k, str(k).to_upper())), "[color=#e0b84a]+%d[/color]" % int(at[k]))
	if linhas != "":
		s += _titulo_secao("Atributos")
		s += linhas
	# propriedades especiais: opções roladas, efeito de uso e conjunto
	var props := ""
	for o in it.get("opcoes", []):
		var exc: bool = str(o["tipo"]).begins_with("excelente")
		props += "[color=#c02a2a]◆[/color] [color=%s]%s[/color]\n" % ["#9cff3a" if exc else "#e8dcc0", Itens.texto_opcao(o)]
	var ef = d.get("efeito")
	if ef is String: props += "[color=#c02a2a]◆[/color] [color=#e0b84a]%s[/color]\n" % ef
	elif ef is Dictionary:
		var partes: Array = []
		if ef.has("cura_hp"): partes.append("Recupera %d de vida%s" % [int(ef["cura_hp"]), (" em %ds" % int(ef["duracao_s"])) if ef.has("duracao_s") else ""])
		if ef.has("cura_hp_pct"): partes.append("Recupera %d%% da vida" % int(ef["cura_hp_pct"]))
		if ef.has("recurso_pct"): partes.append("Recupera %d%% do recurso" % roundi(float(ef["recurso_pct"]) * 100.0))
		if ef.has("remove"): partes.append("Cura " + ", ".join(ef["remove"]))
		if ef.has("teleporta"): partes.append("Leva de volta ao acampamento")
		if ef.has("municao"): partes.append("Munição para a escopeta")
		if ef.has("arremesso"): partes.append("Arremessa e explode em área")
		if ef.has("buff"): partes.append("Fortalece por um tempo")
		if ef.has("repele"): partes.append("Afasta %s" % str(ef["repele"]).replace("_", " "))
		for p in partes: props += "[color=#c02a2a]◆[/color] [color=#c8f08a]%s[/color]\n" % p
	if d.has("conjunto"):
		var cj: Dictionary = {}
		for c in Defs.ITENS_DOC.get("conjuntos", []):
			if c is Dictionary and c.get("id") == d["conjunto"]: cj = c
		props += "[color=#c02a2a]◆[/color] [color=#3ad0a0]Conjunto: %s[/color]\n" % cj.get("nome", str(d["conjunto"]).replace("_", " ").capitalize())
	if props != "":
		s += _titulo_secao("Propriedades especiais")
		s += props
	# lore em itálico e, quando o item tem, a citação em vermelho no fim
	var lore: String = d.get("lore", d.get("descricao", ""))
	if lore != "": s += "\n[i][color=#9a9180]%s[/color][/i]\n" % lore
	var citacao: String = d.get("citacao", "")
	if citacao != "": s += "[i][color=#b3261e]\"%s\"[/color][/i]\n" % citacao
	var req := Itens.pode_usar(it, j) if slot != "" else ""
	if slot != "" and nv > 1 and j.nivel < nv: s += "[color=#ff6a4a]Requer nível %d[/color]\n" % nv
	if req != "" and not req.begins_with("Requer"): s += "[color=#ff6a4a]%s[/color]\n" % req
	var cl = d.get("classes")
	if cl is Array and cl.size() > 0 and cl.size() < 6:
		s += "[color=#8a8070]%s[/color]\n" % ", ".join(cl.map(func(x): return {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}.get(x, x)))
	if contexto in ["mochila", "armazem", "loja_compra"]: s += _comparacao(it)
	match contexto:
		"loja_compra": s += "[color=#e0b84a]Preço: %d de ouro[/color]" % Itens.preco(it)
		"mochila":
			if not troca_d.is_empty():
				s += "[color=#8a8070]%s[/color]" % ("Já está na troca" if _na_troca(int(it["uid"])) else "Botão direito põe na troca")
			elif servico_d.get("tipo") == "loja":
				var v := Itens.preco_venda(it)
				s += ("[color=#e0b84a]Vende por %d · botão direito vende[/color]" % v) if v > 0 else "[color=#8a8070]Não se vende[/color]"
			elif servico_d.get("tipo") == "armazem": s += "[color=#8a8070]Botão direito guarda no armazém[/color]"
			elif slot != "": s += "[color=#8a8070]Botão direito equipa[/color]"
			elif cat in ["consumivel", "leitura"] or d.get("tipo_missao") == "leitura": s += "[color=#8a8070]Botão direito usa[/color]"
		"equip": s += "[color=#8a8070]Botão direito tira[/color]"
		"armazem": s += "[color=#8a8070]Botão direito leva para a mochila[/color]"
		"troca": s += "[color=#8a8070]Botão direito tira da troca[/color]"
	return s.strip_edges() + "\n"

func _desenhar_icone(c: CanvasItem, it: Dictionary, r: Rect2, mod := Color.WHITE) -> void:
	var tm := Tema.icone_mochila(it["id"])
	var g := Itens.grade(it)
	if tm != null and absf(float(tm.get_width()) / tm.get_height() - float(g.x) / g.y) < 0.2:
		var esc := minf(r.size.x / tm.get_width(), r.size.y / tm.get_height())
		var sz := Vector2(tm.get_size()) * esc
		c.draw_texture_rect(tm, Rect2(r.get_center() - sz * 0.5, sz), false, mod)
		return
	var ic := Tema.icone_item(it["id"], true)
	if ic.size() == 2:
		var rr: Rect2 = ic[1]
		var esc2 := minf(r.size.x / rr.size.x, r.size.y / rr.size.y)
		var sz2 := rr.size * esc2
		c.draw_texture_rect_region(ic[0], Rect2(r.get_center() - sz2 * 0.5, sz2), rr, mod)
	else:
		c.draw_rect(r.grow(-4), Defs.cor_raridade(it.get("raridade", "comum")).darkened(0.5))

# =================================================================== grade (mochila e armazém)
func _grade(onde: String) -> Desenho:
	var g := Desenho.new()
	var W := Itens.MOCHILA_W if onde == "mochila" else Itens.ARMAZEM_W
	var H := Itens.MOCHILA_H if onde == "mochila" else Itens.ARMAZEM_H
	if onde.begins_with("troca"): W = TROCA_W; H = TROCA_H
	g.custom_minimum_size = Vector2(W * CEL, H * CEL)
	g.mouse_filter = Control.MOUSE_FILTER_STOP
	g.dados = {"onde": onde, "W": W, "H": H, "hover": -1, "cel": Vector2i(-1, -1)}
	g.desenhar = _desenhar_grade
	g.entrada = _entrada_grade
	g.mouse_exited.connect(func(): g.dados["hover"] = -1; g.dados["cel"] = Vector2i(-1, -1); game.hud.esconder_tip(); g.queue_redraw())
	alvos_soltar.append(g)
	return g

func _lista(onde: String) -> Array:
	match onde:
		"troca": return troca_d.get("eu", {}).get("itens", [])
		"troca_outro": return troca_d.get("outro", {}).get("itens", [])
	return _jog().inv if onde == "mochila" else _jog().armazem

func _desenhar_grade(g: Desenho) -> void:
	var W: int = g.dados["W"]; var H: int = g.dados["H"]
	var lista := _lista(g.dados["onde"])
	g.draw_rect(Rect2(Vector2.ZERO, g.size), Color(0.03, 0.025, 0.02, 0.9))
	var cel := Tema.ui("menu_celula")
	for y in H:
		for x in W:
			if cel: g.draw_texture(cel, Vector2(x * CEL, y * CEL)); continue
			var r := Rect2(x * CEL + 1, y * CEL + 1, CEL - 2, CEL - 2)
			g.draw_rect(r, Color(0.075, 0.065, 0.055))
			g.draw_rect(r, Color(0.16, 0.13, 0.1), false, 1.0)
	var seta := Tema.ui("menu_seta")
	var pulso := 0.75 + 0.25 * sin(Time.get_ticks_msec() * 0.006)
	for it in lista:
		if not mao.is_empty() and mao["it"] == it: continue
		var gr := Itens.grade(it)
		var r := Rect2(int(it["x"]) * CEL + 1, int(it["y"]) * CEL + 1, gr.x * CEL - 2, gr.y * CEL - 2)
		var cor := Defs.cor_raridade(it.get("raridade", "comum"))
		var bg := Color(cor.r, cor.g, cor.b, 0.13 if it.get("raridade", "comum") != "comum" else 0.05)
		if Itens.equipavel(it) and Itens.pode_usar(it, _jog()) != "": bg = Color(0.6, 0.08, 0.05, 0.3)
		if int(it["uid"]) == g.dados["hover"]: bg = bg.lightened(0.15); bg.a += 0.12
		g.draw_rect(r, bg)
		if it.get("raridade", "comum") != "comum": g.draw_rect(r, Color(cor.r, cor.g, cor.b, 0.45), false, 1.0)
		var na_troca: bool = g.dados["onde"] == "mochila" and _na_troca(int(it["uid"]))
		_desenhar_icone(g, it, r.grow(-1), Color(1, 1, 1, 0.3) if na_troca else Color.WHITE)
		if na_troca: g.draw_rect(r, Color(0.85, 0.68, 0.3, 0.7), false, 1.0)
		if seta and g.dados["onde"] == "mochila" and not na_troca and ganho(it) > 0:
			g.draw_texture(seta, Vector2(r.end.x - 15, r.position.y + 1), Color(1, 1, 1, pulso))
		if int(it.get("qtd", 1)) > 1:
			var q := str(int(it["qtd"]))
			var p := r.end - Vector2(2, 3)
			var w := Tema.FONTE_PIXEL.get_string_size(q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
			g.draw_string_outline(Tema.FONTE_PIXEL, p - Vector2(w, 0), q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 3, Color(0, 0, 0))
			g.draw_string(Tema.FONTE_PIXEL, p - Vector2(w, 0), q, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#f6ead0"))
	if g.dados["onde"].begins_with("troca") and troca_d.get("eu" if g.dados["onde"] == "troca" else "outro", {}).get("ok", false):
		g.draw_rect(Rect2(Vector2.ZERO, g.size).grow(-1), Color(0.45, 0.9, 0.4, 0.9), false, 2.0)   # esse lado confirmou
	# prévia de onde o item da mão cai
	if not mao.is_empty() and g.dados["cel"].x >= 0 and g.dados["onde"] != "troca_outro":
		var gr2 := Itens.grade(mao["it"])
		var c0 := _canto_mao(g)
		var ok := Itens.cabe_em(lista, W, H, mao["it"], c0.x, c0.y, int(mao["it"]["uid"]))
		g.draw_rect(Rect2(c0.x * CEL, c0.y * CEL, gr2.x * CEL, gr2.y * CEL), Color(0.3, 0.8, 0.3, 0.25) if ok else Color(0.9, 0.2, 0.15, 0.25))

func _canto_mao(g: Desenho) -> Vector2i:
	var gr := Itens.grade(mao["it"])
	var lp := g.get_local_mouse_position()
	return Vector2i(clampi(roundi(lp.x / CEL - gr.x * 0.5), 0, int(g.dados["W"]) - gr.x), clampi(roundi(lp.y / CEL - gr.y * 0.5), 0, int(g.dados["H"]) - gr.y))

func _item_em(lista: Array, c: Vector2i) -> Dictionary:
	for it in lista:
		var gr := Itens.grade(it)
		if c.x >= int(it["x"]) and c.x < int(it["x"]) + gr.x and c.y >= int(it["y"]) and c.y < int(it["y"]) + gr.y: return it
	return {}

func _entrada_grade(g: Desenho, ev: InputEvent) -> void:
	var onde: String = g.dados["onde"]
	var lista := _lista(onde)
	if ev is InputEventMouseMotion:
		var c := Vector2i(floori(ev.position.x / CEL), floori(ev.position.y / CEL))
		g.dados["cel"] = c
		var it := _item_em(lista, c)
		var uid := int(it.get("uid", -1))
		if uid != g.dados["hover"]:
			g.dados["hover"] = uid
			if uid >= 0 and mao.is_empty(): game.hud.mostrar_tip_item(it, tip_item(it, onde))
			else: game.hud.esconder_tip()
		g.queue_redraw()
	elif ev is InputEventMouseButton and ev.pressed and onde == "troca_outro":
		g.accept_event()   # a oferta do outro só se olha
	elif ev is InputEventMouseButton and ev.pressed:
		var c2 := Vector2i(floori(ev.position.x / CEL), floori(ev.position.y / CEL))
		var it2 := _item_em(lista, c2)
		if ev.button_index == MOUSE_BUTTON_LEFT:
			if mao.is_empty():
				if not it2.is_empty() and onde == "mochila" and _na_troca(int(it2["uid"])):
					game.hud.aviso("Esse item já está na troca.")
				elif not it2.is_empty():
					mao = {"it": it2, "de": onde, "pos": ev.global_position}
					game.hud.esconder_tip()
					game.audio.tocar("ui/pegar_item", null, -8.0)
			else:
				_soltar_em_grade(g)
		elif ev.button_index == MOUSE_BUTTON_RIGHT and mao.is_empty() and not it2.is_empty():
			_acao_direita(it2, onde)
		g.accept_event()
		_redesenhar_tudo()
	elif ev is InputEventMouseButton and not ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT and not mao.is_empty():
		# arrastou e soltou: resolve onde caiu
		if ev.global_position.distance_to(mao.get("pos", ev.global_position)) > 10.0:
			soltar_mao_em(ev.global_position)
		g.accept_event()

func _soltar_em_grade(g: Desenho) -> void:
	var onde: String = g.dados["onde"]
	var c0 := _canto_mao(g)
	var it: Dictionary = mao["it"]
	var j := _jog()
	if not troca_d.is_empty() and (onde.begins_with("troca") or mao["de"] == "troca" or onde == "mochila"):
		_soltar_troca(onde, c0)
		return
	if mao["de"] == "equip":
		game.cmd("desequipar", [mao["slot"], c0.x, c0.y, onde])
	else:
		game.cmd("mover_item", [int(it["uid"]), mao["de"], onde, c0.x, c0.y])
	game.audio.tocar("ui/soltar_item", null, -8.0)
	mao = {}

func soltar_mao_em(gp: Vector2) -> void:
	if mao.is_empty(): return
	for a in alvos_soltar:
		if not is_instance_valid(a) or not a.is_visible_in_tree(): continue
		if a.get_global_rect().has_point(gp):
			if a.dados.has("slot"): _soltar_em_slot(a.dados["slot"])
			else: _soltar_em_grade(a)
			_redesenhar_tudo()
			return
	# fora de qualquer janela: joga no chão (só da mochila)
	var dentro_janela := false
	for n in jan:
		if jan[n].visible and jan[n].get_global_rect().has_point(gp): dentro_janela = true
	if mao["de"] == "troca": game.troca_cmd("tirar", {"uid": int(mao["it"]["uid"])})
	elif not dentro_janela and mao["de"] == "mochila" and not troca_d.is_empty(): game.hud.aviso("Termine a troca primeiro.")
	elif not dentro_janela and mao["de"] == "mochila":
		game.cmd("soltar_item", [int(mao["it"]["uid"])])
	mao = {}
	_redesenhar_tudo()

func soltar_no_mundo() -> void:
	soltar_mao_em(Vector2(-99999, -99999))

func mao_ativa() -> bool:
	return not mao.is_empty()

func _devolver_mao() -> void:
	mao = {}
	_redesenhar_tudo()

func _redesenhar_tudo() -> void:
	for n in jan:
		if jan[n].visible: _redesenhar(jan[n])
	mao_ui.queue_redraw()

func _acao_direita(it: Dictionary, onde: String) -> void:
	var j := _jog()
	var uid := int(it["uid"])
	if onde == "troca": game.troca_cmd("tirar", {"uid": uid}); return
	if not troca_d.is_empty():
		if _na_troca(uid): return
		var lugar := Itens.achar_lugar(_lista("troca"), TROCA_W, TROCA_H, it)
		if lugar.x >= 0: game.troca_cmd("por", {"uid": uid, "x": lugar.x, "y": lugar.y})
		else: game.hud.aviso("Não cabe mais nada na troca.")
		return
	if onde == "armazem":
		var p := Itens.achar_lugar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
		if p.x >= 0: game.cmd("mover_item", [uid, "armazem", "mochila", p.x, p.y])
		else: game.hud.aviso("Mochila cheia.")
		return
	match servico_d.get("tipo", ""):
		"loja": game.cmd("vender", [uid]); return
		"armazem":
			var p2 := Itens.achar_lugar(j.armazem, Itens.ARMAZEM_W, Itens.ARMAZEM_H, it)
			if p2.x >= 0: game.cmd("mover_item", [uid, "mochila", "armazem", p2.x, p2.y])
			else: game.hud.aviso("Armazém cheio.")
			return
	game.cmd("usar_item", [uid])

func _desenhar_mao(c: Desenho) -> void:
	if mao.is_empty(): return
	var gr := Itens.grade(mao["it"])
	var mp := c.get_local_mouse_position()
	var r := Rect2(mp - Vector2(gr.x * CEL, gr.y * CEL) * 0.5, Vector2(gr.x * CEL, gr.y * CEL))
	c.draw_rect(r, Color(0, 0, 0, 0.35))
	_desenhar_icone(c, mao["it"], r, Color(1, 1, 1, 0.92))

func _process(dt: float) -> void:
	if not mao.is_empty(): mao_ui.queue_redraw()
	if not troca_d.is_empty() and jan.has("troca"): _botao_ok_troca()
	if _poder_flash.get("t", 0.0) > 0.0: _poder_flash["t"] -= dt
	if aberta("inventario") and is_instance_valid(_grade_mochila) and Engine.get_process_frames() % 3 == 0: _grade_mochila.queue_redraw()
	if dialogo_t < 1.0 and aberta("dialogo"):
		dialogo_t += dt * 2.5
		var rl: RichTextLabel = jan["dialogo"].find_child("Fala", true, false)
		if rl: rl.visible_ratio = clampf(dialogo_t, 0.0, 1.0)
	# serviço fecha se o jogador se afastar do NPC
	if not servico_d.is_empty() and game.jog:
		var npc: Ent = game.sim.ents.get(int(servico_d.get("npc", -1)))
		if npc == null or npc.pos.distance_to(game.jog.pos) > 6.0: fechar("servico")
	if not dialogo_d.is_empty() and game.jog:
		var npc2: Ent = game.sim.ents.get(int(dialogo_d.get("npc", -1)))
		if npc2 == null or npc2.pos.distance_to(game.jog.pos) > 6.0: fechar("dialogo")

func _input(ev: InputEvent) -> void:
	# números escolhem a opção do diálogo
	if aberta("dialogo") and ev is InputEventKey and ev.pressed and not ev.echo:
		var k: int = ev.keycode - KEY_1
		if k >= 0 and k < 9 and k < dialogo_d.get("opcoes", []).size():
			_escolher(k); get_viewport().set_input_as_handled()

# =================================================================== equipamento
func _slot_equip(slot: String) -> Desenho:
	var s := Desenho.new()
	var r: Rect2 = POS_EQUIP[slot]
	s.position = r.position; s.size = r.size
	s.mouse_filter = Control.MOUSE_FILTER_STOP
	s.dados = {"slot": slot, "hover": false}
	s.desenhar = func(c: Desenho):
		var it: Dictionary = _jog().equip.get(slot, {})
		var rr := Rect2(Vector2.ZERO, c.size)
		var borda := Color(0.42, 0.34, 0.2) if not c.dados["hover"] else Color(0.8, 0.65, 0.35)
		var peca := "menu_slot_hover" if c.dados["hover"] else "menu_slot"
		if not mao.is_empty() and mao["de"] != "equip" and Jogador.slot_para(_jog(), mao["it"]) .begins_with(slot.substr(0, 4)):
			var pode := Itens.pode_usar(mao["it"], _jog()) == ""
			borda = Color(0.4, 0.85, 0.35) if pode else Color(0.9, 0.25, 0.2)
			peca = "menu_slot_pronto" if pode else "menu_slot_ruim"
		elif mao.is_empty() and not c.dados["hover"] and _slot_tem_melhoria(slot):
			peca = "menu_slot_pronto"   # tem coisa melhor na mochila para este lugar
		var moldura := _sb(peca, [14, 14, 14, 14])
		if moldura: c.draw_style_box(moldura, rr)
		else: c.draw_rect(rr, Color(0.03, 0.025, 0.02, 0.95))
		var vazio: bool = it.is_empty() or (not mao.is_empty() and mao["it"] == it)
		if vazio:
			var gl := Tema.ui("menu_glifo_" + ("anel" if slot.begins_with("anel") else slot))
			if gl: c.draw_texture(gl, (c.size - gl.get_size()) * 0.5, Color(1, 1, 1, 0.85))
		if not it.is_empty() and not (not mao.is_empty() and mao["it"] == it):
			var cor := Defs.cor_raridade(it.get("raridade", "comum"))
			if it.get("raridade", "comum") != "comum": c.draw_rect(rr, Color(cor.r, cor.g, cor.b, 0.12))
			_desenhar_icone(c, it, rr.grow(-4))
			if int(it.get("refino", 0)) > 0:
				c.draw_string_outline(Tema.FONTE_PIXEL, Vector2(3, 10), "+%d" % int(it["refino"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 3, Color.BLACK)
				c.draw_string(Tema.FONTE_PIXEL, Vector2(3, 10), "+%d" % int(it["refino"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("#e0b84a"))
		elif moldura == null:
			var nome: String = Itens.NOME_SLOT[slot].to_upper()
			var w := Tema.FONTE_PIXEL.get_string_size(nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 7).x
			c.draw_string(Tema.FONTE_PIXEL, Vector2((c.size.x - w) * 0.5, c.size.y * 0.5 + 3), nome, HORIZONTAL_ALIGNMENT_LEFT, -1, 7, Color(0.42, 0.37, 0.3))
		if moldura == null: c.draw_rect(rr, borda, false, 1.5)
	s.entrada = func(c: Desenho, ev: InputEvent):
		var it: Dictionary = _jog().equip.get(slot, {})
		if ev is InputEventMouseMotion:
			if not c.dados["hover"]:
				c.dados["hover"] = true; c.queue_redraw()
				if not it.is_empty() and mao.is_empty(): game.hud.mostrar_tip_item(it, tip_item(it, "equip"))
				elif it.is_empty() and mao.is_empty(): game.hud.mostrar_tip(_tip_slot_vazio(slot))
		elif ev is InputEventMouseButton and ev.pressed:
			if ev.button_index == MOUSE_BUTTON_LEFT:
				if mao.is_empty():
					if not it.is_empty(): mao = {"it": it, "de": "equip", "slot": slot, "pos": ev.global_position}; game.hud.esconder_tip()
				else: _soltar_em_slot(slot)
			elif ev.button_index == MOUSE_BUTTON_RIGHT and not it.is_empty() and mao.is_empty():
				game.cmd("desequipar", [slot])
			c.accept_event()
			_redesenhar_tudo()
		elif ev is InputEventMouseButton and not ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT and not mao.is_empty():
			if ev.global_position.distance_to(mao.get("pos", ev.global_position)) > 10.0: soltar_mao_em(ev.global_position)
			c.accept_event()
	s.mouse_exited.connect(func(): s.dados["hover"] = false; s.queue_redraw(); game.hud.esconder_tip())
	alvos_soltar.append(s)
	return s

func _soltar_em_slot(slot: String) -> void:
	if mao.is_empty(): return
	var j := _jog()
	if mao["de"] == "mochila":
		var sd := Itens.slot_de(mao["it"])
		var alvo := slot
		if sd == "anel" and slot in ["anel1", "anel2"]: alvo = slot
		elif sd != slot: game.hud.aviso("Não vai aí."); mao = {}; return
		game.cmd("equipar", [int(mao["it"]["uid"]), alvo])
	mao = {}

# =================================================================== mochila + equipamento
func abrir_inventario() -> void:
	var c := _janela("inventario", "EQUIPAMENTO", Vector2(416, 560), "direita")
	if c.get_child_count() > 0: _atualizar_inventario(); return
	c.add_theme_constant_override("separation", 4)
	var eq := Desenho.new()
	eq.custom_minimum_size = AREA_EQUIP
	eq.desenhar = _desenhar_boneco
	for slot in POS_EQUIP: eq.add_child(_slot_equip(slot))
	c.add_child(eq)
	# atributos
	var at := GridContainer.new(); at.columns = 4; at.name = "Atributos"
	at.add_theme_constant_override("h_separation", 6)
	c.add_child(at)
	var der := Tema.rotulo("", 13, Color("#c8bfa8")); der.name = "Derivados"
	c.add_child(der)
	var dv := Tema.ui("menu_divisor")
	if dv:
		var tr := TextureRect.new(); tr.texture = dv; tr.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
		tr.custom_minimum_size = Vector2(380, 14)
		c.add_child(tr)
	else:
		var tm := Tema.rotulo("MOCHILA", 15, Color("#e0c890"), Tema.FONTE_TITULO, 2)
		tm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		c.add_child(tm)
	var cg := CenterContainer.new(); _grade_mochila = _grade("mochila"); cg.add_child(_grade_mochila); c.add_child(cg)
	_atualizar_inventario()

## Retrato no pedestal, placa de Poder e o aviso de melhorias na mochila.
func _desenhar_boneco(cc: Desenho) -> void:
	var j := _jog()
	var cx := AREA_EQUIP.x * 0.5
	var ped := Tema.ui("menu_pedestal")
	if ped: cc.draw_texture(ped, Vector2(cx - ped.get_width() * 0.5, 0))
	else: cc.draw_rect(Rect2(cx - 52, 6, 104, 130), Color(0.03, 0.025, 0.02, 0.5))
	var meta: Dictionary = Defs.SPR.get(j.classe, {})
	if not meta.is_empty():
		var tex := Tema.tex(meta["anims"]["idle"]["file"])
		var fr: Array = meta["frame"]; var anc: Array = meta["anchor"]
		var f := int(Time.get_ticks_msec() / 160) % int(meta["anims"]["idle"]["frames"])
		var esc := 1.45
		var pe := Vector2(cx, 178)
		if tex: cc.draw_texture_rect_region(tex, Rect2(pe - Vector2(anc[0], anc[1]) * esc, Vector2(fr[0], fr[1]) * esc), Rect2(f * fr[0], 0, fr[0], fr[1]))
	# placa de Poder
	var pl := Tema.ui("menu_poder")
	var py := 202.0
	if pl: cc.draw_texture(pl, Vector2(cx - pl.get_width() * 0.5, py))
	var txt := "PODER  %d" % poder()
	var w := Tema.FONTE_TITULO.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
	cc.draw_string_outline(Tema.FONTE_TITULO, Vector2(cx - w * 0.5, py + 21), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, 3, Color(0, 0, 0))
	cc.draw_string(Tema.FONTE_TITULO, Vector2(cx - w * 0.5, py + 21), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#f0d48a"))
	# o Poder subiu: número verde subindo da placa
	if _poder_flash.get("t", 0.0) > 0.0:
		var t: float = _poder_flash["t"]
		var v: int = _poder_flash["v"]
		var ft := ("+%d" % v) if v > 0 else str(v)
		var cor := Color("#9cff3a") if v > 0 else Color("#ff6a4a")
		cor.a = clampf(t / 0.6, 0.0, 1.0)
		var fp := Vector2(cx + w * 0.5 + 8, py + 18 - (1.8 - t) * 14.0)
		cc.draw_string_outline(Tema.FONTE_TITULO, fp, ft, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, 3, Color(0, 0, 0, cor.a))
		cc.draw_string(Tema.FONTE_TITULO, fp, ft, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, cor)
	# melhorias esperando na mochila
	var n := melhorias_na_mochila()
	if n > 0:
		var seta := Tema.ui("menu_seta")
		var pulso := 0.7 + 0.3 * sin(Time.get_ticks_msec() * 0.006)
		if seta: cc.draw_texture(seta, Vector2(4, py + 8), Color(1, 1, 1, pulso))
		var mt := "%d melhoria%s" % [n, "s" if n > 1 else ""]
		cc.draw_string_outline(Tema.FONTE_TEXTO, Vector2(22, py + 14), mt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, 3, Color(0, 0, 0))
		cc.draw_string(Tema.FONTE_TEXTO, Vector2(22, py + 14), mt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#b8f070"))
		cc.draw_string(Tema.FONTE_ITALICO, Vector2(22, py + 27), "na mochila", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#7d8a66"))
	var linhas := [["◉ %d" % j.ouro, Tema.COR_OURO, 14]]
	if j.classe == "humano": linhas.append(["%d balas" % j.municao, Color("#a89f8c"), 12])
	for i in linhas.size():
		var l: Array = linhas[i]
		var wn := Tema.FONTE_TITULO.get_string_size(l[0], HORIZONTAL_ALIGNMENT_LEFT, -1, l[2]).x
		var lp := Vector2(AREA_EQUIP.x - 4 - wn, py + (14 if linhas.size() > 1 else 20) + i * 14)
		cc.draw_string_outline(Tema.FONTE_TITULO, lp, l[0], HORIZONTAL_ALIGNMENT_LEFT, -1, l[2], 3, Color(0, 0, 0))
		cc.draw_string(Tema.FONTE_TITULO, lp, l[0], HORIZONTAL_ALIGNMENT_LEFT, -1, l[2], l[1])
	cc.queue_redraw()

func _tip_slot_vazio(slot: String) -> String:
	var s := "[font_size=16][color=#e0c890]%s[/color][/font_size]\n" % Itens.NOME_SLOT[slot]
	var melhor := {}; var g := 0
	for it in _jog().inv:
		if slot in _slots_de(it) and ganho(it) > g and _melhor_slot(it)[1] == slot: melhor = it; g = ganho(it)
	if not melhor.is_empty():
		s += "[color=#9cff3a]%s, na mochila, serve aqui: Poder +%d.[/color]\n[color=#8a8070]Botão direito nele equipa.[/color]" % [Itens.nome(melhor), g]
	else:
		s += "[i][color=#a89f8c]Vazio. Monstros, chefes e baús deixam cair peças para este lugar.[/color][/i]"
	return s

func _atualizar_inventario() -> void:
	if not jan.has("inventario"): return
	var c: Control = corpo["inventario"]
	var j := _jog()
	var at: GridContainer = c.get_node("Atributos")
	_limpar(at)
	for k in ["FOR", "AGI", "VIT", "ESP"]:
		var b := PanelContainer.new()
		var sb := Tema.caixa_menu(4)
		b.add_theme_stylebox_override("panel", sb)
		b.custom_minimum_size = Vector2(88, 40)
		var h := HBoxContainer.new()
		var v := VBoxContainer.new(); v.add_theme_constant_override("separation", -2)
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var l1 := Tema.rotulo(k, 10, Color("#a89f8c"), Tema.FONTE_PIXEL); l1.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		var bonus := float(j.aux.get("bonus", {}).get(k, 0.0))
		var l2 := Tema.rotulo("%d" % roundi(float(j.stats[k]) + bonus), 18, Color("#9cc8ff") if bonus > 0 else Color("#f0dca0"), Tema.FONTE_TITULO); l2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(l1); v.add_child(l2); h.add_child(v)
		if j.pontos > 0:
			var mais := Button.new(); mais.text = "+"; mais.custom_minimum_size = Vector2(22, 22)
			mais.pressed.connect(func(): game.cmd("ponto", [k]); game.audio.tocar("ui/clique", null, -6.0))
			h.add_child(mais)
		b.add_child(h)
		at.add_child(b)
	var der: Label = c.get_node("Derivados")
	var txt := "Dano %d–%d    Defesa %d    Crítico %d%%" % [roundi(j.dano_min), roundi(j.dano_max), roundi(j.defesa), roundi(j.critico * 100.0)]
	if j.pontos > 0: txt += "\n[%d pontos para distribuir]" % j.pontos
	der.text = txt
	der.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_redesenhar(jan["inventario"])

# =================================================================== personagem
func abrir_personagem() -> void:
	var c := _janela("personagem", "PERSONAGEM", Vector2(360, 520), "esquerda")
	_limpar(c)
	var j := _jog()
	var cls: Dictionary = Defs.CLASSES[j.classe]
	var nomes := {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}
	var t1 := Tema.rotulo(j.nome, 24, Color("#f0dca0"), Tema.FONTE_GOTICA, 3); t1.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; c.add_child(t1)
	var t2 := Tema.rotulo("%s de nível %d · %s" % [Evolucao.nome_classe(j) if j.evolucao != "" else nomes[j.classe], j.nivel, "Vigília" if j.faccao == "vigilia" else "Arautos do Juízo"], 14, Color("#a89f8c"), Tema.FONTE_ITALICO)
	t2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; c.add_child(t2)
	var xpb := ProgressBar.new(); xpb.max_value = Defs.xp_para_proximo(j.nivel); xpb.value = j.xp; xpb.show_percentage = false; xpb.custom_minimum_size.y = 8
	var sbf := StyleBoxFlat.new(); sbf.bg_color = Color(0.55, 0.75, 0.25); xpb.add_theme_stylebox_override("fill", sbf)
	var sbb := StyleBoxFlat.new(); sbb.bg_color = Color(0.05, 0.04, 0.03); xpb.add_theme_stylebox_override("background", sbb)
	c.add_child(xpb)
	c.add_child(Tema.rotulo("Experiência %d / %d" % [j.xp, Defs.xp_para_proximo(j.nivel)], 12, Color("#8a8070")))
	var desc := {"FOR": "dano corpo a corpo e postura", "AGI": "precisão, esquiva e velocidade", "VIT": "vida e defesa", "ESP": "poder das habilidades e recurso"}
	for k in ["FOR", "AGI", "VIT", "ESP"]:
		var h := HBoxContainer.new()
		var l := Tema.rotulo(k, 15, Color("#e0c890"), Tema.FONTE_TITULO); l.custom_minimum_size.x = 46
		h.add_child(l)
		var bonus := float(j.aux.get("bonus", {}).get(k, 0.0))
		var v := Tema.rotulo("%d" % roundi(float(j.stats[k]) + bonus) + ((" (+%d)" % roundi(bonus)) if bonus > 0 else ""), 15, Color("#f0dca0"), Tema.FONTE_TITULO); v.custom_minimum_size.x = 70
		h.add_child(v)
		var d := Tema.rotulo(desc[k], 12, Color("#8a8070"), Tema.FONTE_ITALICO); d.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		h.add_child(d)
		if j.pontos > 0:
			var b := Button.new(); b.text = "+"; b.custom_minimum_size = Vector2(26, 24)
			b.pressed.connect(func(): game.cmd("ponto", [k]))
			h.add_child(b)
		c.add_child(h)
	if j.pontos > 0: c.add_child(Tema.rotulo("Pontos livres: %d" % j.pontos, 15, Color("#ffd27a"), Tema.FONTE_TITULO))
	var linha := ColorRect.new(); linha.color = Color(0.42, 0.34, 0.2, 0.5); linha.custom_minimum_size.y = 1; c.add_child(linha)
	var g := GridContainer.new(); g.columns = 2
	g.add_theme_constant_override("h_separation", 24)
	var pares := [["Vida", "%d" % roundi(j.hp_max)], [cls["recurso"]["nome"].split(" ")[0], "%d" % roundi(j.rec_max) if j.rec_max > 0 else "a própria vida"],
		["Dano", "%d–%d" % [roundi(j.dano_min), roundi(j.dano_max)]], ["Defesa", "%d" % roundi(j.defesa)],
		["Precisão", "%d" % roundi(j.ar)], ["Esquiva", "%d" % roundi(j.er)],
		["Crítico", "%d%% (×%.1f)" % [roundi(j.critico * 100.0), j.crit_mult]], ["Golpe excelente", "%d%%" % roundi(j.excelente * 100.0)],
		["Ataques por s", "%.2f" % (j.vel_ataque / maxf(0.1, j.intervalo))], ["Roubo de vida", "%d%%" % roundi(j.roubo_vida * 100.0)],
		["Velocidade", "%.1f" % j.vel], ["Abates", "%d" % j.abates.values().reduce(func(a, b): return a + b, 0)]]
	if j.classe == "humano": pares.append_array([["Munição", "%d" % j.municao], ["", ""]])
	for p in pares:
		g.add_child(Tema.rotulo(p[0], 14, Color("#a89f8c")))
		g.add_child(Tema.rotulo(p[1], 14, Color("#e8dfc9"), Tema.FONTE_TITULO))
	c.add_child(g)
	var res: Array = []
	for el in j.res:
		if absf(float(j.res[el])) > 0.001: res.append("%s %+d%%" % [el.capitalize(), roundi(float(j.res[el]) * 100.0)])
	if not res.is_empty(): c.add_child(Tema.rotulo("Resistências: " + ", ".join(res), 13, Color("#9cc8ff")))

# =================================================================== habilidades
func abrir_habilidades() -> void:
	var c := _janela("habilidades", "HABILIDADES", Vector2(460, 560), "esquerda")
	_limpar(c)
	var j := _jog()
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 10)
	sc.add_child(v); c.add_child(sc)
	var i := 0
	for h in Evolucao.habilidades(j):
		var sk := Defs.skill(j.classe, h["id"]) if not h.has("_evo") else {"nome": h["nome"], "descricao": h.get("descricao", "")}
		var linha := HBoxContainer.new()
		linha.add_theme_constant_override("separation", 10)
		var ic := Tema.icone_skill(j.classe, h["id"], true)
		var tr := TextureRect.new(); tr.custom_minimum_size = Vector2(56, 56)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		if ic.size() == 2:
			var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]; tr.texture = at
		var bloq := j.nivel < int(h["nivel"])
		if bloq: tr.modulate = Color(0.35, 0.35, 0.35)
		tr.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		linha.add_child(tr)
		var col := VBoxContainer.new(); col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.add_theme_constant_override("separation", 2)
		var nm := Tema.rotulo("%s · %s" % [("⇧%d" % (i + 1 - Defs.CLASSES[j.classe]["habilidades"].size())) if h.has("_evo") else str(i + 1), sk.get("nome", h["nome"])], 16, Color("#f0dca0") if not bloq else Color("#7d7466"), Tema.FONTE_TITULO)
		col.add_child(nm)
		var meta: Array = []
		if bloq: meta.append("nível %d" % int(h["nivel"]))
		var cst := Jogador.custo(j, h)
		if cst > 0: meta.append(("%d de vida" % roundi(cst)) if j.classe == "cultista" else ("custa %d" % roundi(cst)))
		if h.has("recarga"): meta.append("recarga %.1fs" % float(h["recarga"]))
		if h.has("cargas"): meta.append("%d cargas" % int(h["cargas"]))
		col.add_child(Tema.rotulo(" · ".join(meta), 12, Color("#a89f8c"), Tema.FONTE_ITALICO))
		var d := Tema.rotulo(sk.get("descricao", ""), 13, Color("#d8cfb8"))
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; d.custom_minimum_size.x = 340
		col.add_child(d)
		for ef in sk.get("efeitos", []):
			var e2 := Tema.rotulo("• " + ef, 12, Color("#9cc8ff")); e2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; e2.custom_minimum_size.x = 340
			col.add_child(e2)
		linha.add_child(col)
		v.add_child(linha)
		i += 1
	# passiva da classe (6ª habilidade do livro, ainda sem número de combate)
	for sk2 in Defs.SKILLS.values():
		if sk2.get("classe") == j.classe and not sk2.has("combate"):
			var l := Tema.rotulo("Definitiva: %s (nível %d) — chega numa próxima versão." % [sk2["nome"], int(sk2.get("nivel", 20))], 12, Color("#7d7466"), Tema.FONTE_ITALICO)
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; l.custom_minimum_size.x = 400
			v.add_child(l)

# =================================================================== missões
func abrir_missoes() -> void:
	var c := _janela("missoes", "DIÁRIO", Vector2(640, 520), "centro")
	_limpar(c)
	var j := _jog()
	var abas := HBoxContainer.new()
	for a in [["ativas", "Em andamento"], ["concluidas", "Concluídas"], ["biblioteca", "Biblioteca"]]:
		var b := Button.new(); b.text = a[1]; b.toggle_mode = true; b.button_pressed = _sel_aba == a[0]
		Tema.estilo_aba(b, _sel_aba == a[0])
		b.pressed.connect(func():
			_sel_aba = a[0]; missao_sel = ""
			if a[0] == "biblioteca": game.cmd("estante", [])
			abrir_missoes())
		abas.add_child(b)
	c.add_child(abas)
	if _sel_aba == "biblioteca":
		_aba_biblioteca(c); return
	var h := HBoxContainer.new(); h.size_flags_vertical = Control.SIZE_EXPAND_FILL
	h.add_theme_constant_override("separation", 12)
	c.add_child(h)
	var sc := ScrollContainer.new(); sc.custom_minimum_size.x = 220; sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var lista := VBoxContainer.new(); sc.add_child(lista); h.add_child(sc)
	var ids: Array = []
	for mid in j.missoes:
		var st := Missoes.estado(j, mid)
		if (_sel_aba == "ativas" and st == "ativa") or (_sel_aba == "concluidas" and st in ["concluida", "falhou"]): ids.append(mid)
	ids.sort_custom(func(a, b): return int(Missoes.def(a).get("tipo") == "principal") > int(Missoes.def(b).get("tipo") == "principal"))
	if missao_sel == "" and not ids.is_empty(): missao_sel = ids[0]
	if ids.is_empty(): lista.add_child(Tema.rotulo("Nada aqui ainda.", 14, Color("#7d7466"), Tema.FONTE_ITALICO))
	for mid in ids:
		var d := Missoes.def(mid)
		var b := Button.new()
		b.text = ("★ " if d.get("tipo") == "principal" else "") + d.get("titulo", mid) + (" ✓" if Missoes.pronta(j, mid) else "")
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.toggle_mode = true; b.button_pressed = mid == missao_sel
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(func(): missao_sel = mid; abrir_missoes())
		lista.add_child(b)
	var sep := ColorRect.new(); sep.color = Color(0.42, 0.34, 0.2, 0.5); sep.custom_minimum_size.x = 1; h.add_child(sep)
	var det := RichTextLabel.new(); det.bbcode_enabled = true; det.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	det.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	det.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	det.add_theme_font_size_override("normal_font_size", 15)
	h.add_child(det)
	if missao_sel != "":
		var d := Missoes.def(missao_sel)
		var s := "[font_size=22][color=#f0dca0]%s[/color][/font_size]\n" % d.get("titulo", "")
		var doador: String = Defs.NPCS.get(d.get("doador", ""), {}).get("nome", "")
		s += "[i][color=#a89f8c]%s%s[/color][/i]\n\n" % [{"principal": "Principal", "secundaria": "Secundária", "repetivel": "Repetível"}.get(d.get("tipo", ""), "Missão"), (" · de " + doador) if doador != "" else ""]
		s += "%s\n\n" % d.get("descricao", d.get("resumo", ""))
		s += "[b][color=#e0c890]Objetivos[/color][/b]\n"
		var objs: Array = d.get("objetivos", [])
		var etapa := Missoes._etapa_atual(j, missao_sel) if Missoes.estado(j, missao_sel) == "ativa" else 999
		for i in objs.size():
			var o: Dictionary = objs[i]
			if int(o.get("etapa", 1)) > etapa: s += "[color=#5d564c]◆ ???[/color]\n"; continue
			var pr := Missoes.progresso(j, missao_sel, i)
			var feito: bool = pr[0] >= pr[1] or Missoes.estado(j, missao_sel) == "concluida"
			var tx := Missoes.texto_objetivo(o) + ((" %d/%d" % pr) if pr[1] > 1 else "")
			s += ("[color=#9cd870]◆ %s ✓[/color]\n" % tx) if feito else ("◆ %s\n" % tx)
		var rec: Dictionary = d.get("recompensas", {})
		var rs: Array = []
		if rec.has("xp"): rs.append("%d de experiência" % int(rec["xp"]))
		if rec.has("ouro"): rs.append("%d de ouro" % int(rec["ouro"]))
		for it in rec.get("itens", []): rs.append(("%d× " % int(it.get("qtd", 1)) if int(it.get("qtd", 1)) > 1 else "") + Defs.ITENS.get(it["id"], {}).get("nome", it["id"]))
		if not rs.is_empty(): s += "\n[b][color=#e0c890]Recompensa[/color][/b]\n[color=#e0b84a]%s[/color]\n" % ", ".join(rs)
		if Missoes.estado(j, missao_sel) == "concluida" and d.get("texto_conclusao", "") != "": s += "\n[i][color=#b8ab90]%s[/color][/i]" % d["texto_conclusao"]
		det.text = s

# =================================================================== Estante (Biblioteca Soterrada)
## Aba "Biblioteca" do diário: a Estante do Caminhante, com tudo o que o personagem já leu, para reler e cruzar.
func _aba_biblioteca(c: Control) -> void:
	var h := HBoxContainer.new(); h.size_flags_vertical = Control.SIZE_EXPAND_FILL
	h.add_theme_constant_override("separation", 12)
	c.add_child(h)
	var sc := ScrollContainer.new(); sc.custom_minimum_size.x = 220; sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var lista := VBoxContainer.new(); sc.add_child(lista); h.add_child(sc)
	if estante_livros.is_empty():
		var l := Tema.rotulo("A estante está vazia. Tudo o que você ler pelo mundo (livros, páginas, pedras gravadas) fica guardado aqui.", 14, Color("#7d7466"), Tema.FONTE_ITALICO)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; l.custom_minimum_size.x = 210
		lista.add_child(l)
	for lv in estante_livros:
		var tid: String = lv["id"]
		var b := Button.new(); b.text = str(lv["titulo"]); b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.toggle_mode = true; b.button_pressed = tid == estante_sel
		b.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS; b.custom_minimum_size.x = 200
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(func():
			estante_sel = tid
			if not textos_lidos.has(tid): game.cmd("ler", [tid])
			abrir_missoes())
		lista.add_child(b)
	var sep := ColorRect.new(); sep.color = Color(0.42, 0.34, 0.2, 0.5); sep.custom_minimum_size.x = 1; h.add_child(sep)
	var det := RichTextLabel.new(); det.bbcode_enabled = true; det.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	det.add_theme_font_override("normal_font", Tema.FONTE_ITALICO)
	det.add_theme_font_override("bold_font", Tema.FONTE_TITULO)
	det.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	det.add_theme_font_size_override("normal_font_size", 16)
	det.add_theme_color_override("default_color", Color("#e8dcc0"))
	h.add_child(det)
	if estante_sel != "" and textos_lidos.has(estante_sel):
		var t: Dictionary = textos_lidos[estante_sel]
		det.text = "[font_size=22][color=#f0dca0]%s[/color][/font_size]\n\n%s" % [t["titulo"], t["texto"]]
	elif estante_sel != "":
		det.text = "[color=#7d7466]Abrindo...[/color]"
	else:
		det.text = "[i][color=#a89f8c]Leve um. Devolva escrito.[/color][/i]\n[color=#7d7466]— Regulamento da Sala de Leitura[/color]"

## O servidor mandou uma lista de livros: da estante que o jogador tocou, ou da Estante pessoal (diário).
func estante(d: Dictionary) -> void:
	var livros: Array = d.get("livros", [])
	if d.get("modo", "") == "diario":
		estante_livros = livros
		if jan.has("missoes") and jan["missoes"].visible and _sel_aba == "biblioteca": abrir_missoes()
		return
	var c := _janela("estante", str(d.get("nome", "Estante")), Vector2(420, 460), "esquerda")
	_limpar(c)
	_titulo("estante", str(d.get("nome", "Estante")))
	var sub := Tema.rotulo("Lombadas de couro, pano e papelão, em ordem que só Eulália entende.", 13, Color("#a89f8c"), Tema.FONTE_ITALICO)
	sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; sub.custom_minimum_size.x = 380
	c.add_child(sub)
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL; sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL; sc.add_child(v); c.add_child(sc)
	for lv in livros:
		var tid: String = lv["id"]
		var b := Button.new(); b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.text = ("✓ " if lv.get("lido", false) else "   ") + str(lv["titulo"])
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 15)
		b.pressed.connect(func(): game.cmd("ler", [tid]))
		v.add_child(b)
	game.audio.tocar("ui/pagina", null, -6.0)

## Texto lido (livro, página, inscrição): guarda nesta sessão e mostra no diário, se a Estante estiver aberta nele.
func texto_lido(d: Dictionary) -> void:
	var tid := str(d.get("id", ""))
	if tid == "": texto(d.get("titulo", ""), d.get("texto", "")); return
	textos_lidos[tid] = {"titulo": str(d.get("titulo", "")), "texto": str(d.get("texto", ""))}
	if not estante_livros.any(func(x): return x["id"] == tid): estante_livros.append({"id": tid, "titulo": str(d.get("titulo", ""))})
	if jan.has("missoes") and jan["missoes"].visible and _sel_aba == "biblioteca" and estante_sel == tid:
		abrir_missoes(); game.audio.tocar("ui/pagina", null, -4.0)
	else:
		texto(d.get("titulo", ""), d.get("texto", ""))

# =================================================================== diálogo
func dialogo(d: Dictionary) -> void:
	dialogo_d = d
	var c := _janela("dialogo", "", Vector2(680, 250), "baixo")
	_limpar(c)
	_titulo("dialogo", d.get("nome", ""))
	if d.get("titulo", "") != "":
		var st := Tema.rotulo(d["titulo"], 14, Color("#a89f8c"), Tema.FONTE_ITALICO); st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		c.add_child(st)
	var fala := RichTextLabel.new(); fala.name = "Fala"
	fala.bbcode_enabled = true; fala.fit_content = true; fala.scroll_active = false
	fala.add_theme_font_size_override("normal_font_size", 17)
	fala.add_theme_color_override("default_color", Color("#efe4c8"))
	fala.text = d.get("texto", "")
	fala.visible_ratio = 0.0
	dialogo_t = 0.0
	c.add_child(fala)
	var ops := VBoxContainer.new(); ops.add_theme_constant_override("separation", 2)
	var i := 0
	for o in d.get("opcoes", []):
		var b := Button.new()
		var cor := Color("#d8cfb8")
		var pre := ""
		match o.get("tipo", ""):
			"aceitar": cor = Color("#ffd27a"); pre = "[!] "
			"concluir": cor = Color("#c8f08a"); pre = "[?] "
			"servico": cor = Color("#9cc8ff")
			"missao": cor = Color("#ffd27a")
		b.text = "%d.  %s%s" % [i + 1, pre, o["texto"]]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.flat = true
		b.add_theme_font_override("font", Tema.FONTE_TEXTO)
		b.add_theme_font_size_override("font_size", 16)
		b.add_theme_color_override("font_color", cor)
		b.add_theme_color_override("font_hover_color", cor.lightened(0.35))
		var idx := i
		b.pressed.connect(func(): _escolher(idx))
		ops.add_child(b)
		i += 1
	c.add_child(ops)
	jan["dialogo"].reset_size()
	var p: PanelContainer = jan["dialogo"]
	p.offset_top = p.offset_bottom - p.get_combined_minimum_size().y

func _escolher(i: int) -> void:
	if dialogo_t < 1.0:
		dialogo_t = 1.0; return
	game.audio.tocar("ui/clique", null, -6.0)
	game.cmd("escolher", [i])

# =================================================================== serviços
func servico(d: Dictionary) -> void:
	servico_d = d.duplicate()
	servico_d["npc"] = d.get("npc", -1)
	if aberta("dialogo"): jan["dialogo"].visible = false
	match d["tipo"]:
		"loja": _abrir_loja(d)
		"ferreiro":
			_janela("servico", d.get("titulo", "Forja"), Vector2(420, 480), "esquerda")
			_titulo("servico", d.get("titulo", "Forja"))
			_corpo_ferreiro()
			abrir_inventario()
		"armazem": _abrir_armazem(d)
		"treinador": _abrir_treinador(d)

func _fala_servico(c: Control, d: Dictionary) -> void:
	if d.get("fala", "") != "":
		var f := Tema.rotulo("“%s”" % d["fala"], 14, Color("#b8ab90"), Tema.FONTE_ITALICO)
		f.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; f.custom_minimum_size.x = 380
		c.add_child(f)

func _abrir_loja(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Loja"), Vector2(420, 560), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Loja"))
	_fala_servico(c, d)
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v); c.add_child(sc)
	for id in d.get("itens", []):
		var it := Itens.novo(id)
		var b := Button.new()
		b.custom_minimum_size = Vector2(0, 40)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var ic := Tema.icone_item(id)
		if ic.size() == 2:
			var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]
			b.icon = at; b.expand_icon = false
			b.add_theme_constant_override("icon_max_width", 32)
		var preco := Itens.preco(it)
		b.text = "  %s   —   %d ouro" % [Itens.nome(it), preco]
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 15)
		var cor := Defs.cor_raridade(it.get("raridade", "comum"))
		b.add_theme_color_override("font_color", cor if it.get("raridade", "comum") != "comum" else Color("#e8dfc9"))
		b.mouse_entered.connect(func(): game.hud.mostrar_tip_item(it, tip_item(it, "loja_compra")))
		b.mouse_exited.connect(func(): game.hud.esconder_tip())
		b.pressed.connect(func():
			var q := 10 if Input.is_key_pressed(KEY_SHIFT) and Itens.pilha(it) > 1 else 1
			game.cmd("comprar", [id, q])
			_atualizar_inventario())
		v.add_child(b)
	c.add_child(Tema.rotulo("Clique compra (Shift compra 10). Botão direito na mochila vende.", 12, Color("#7d7466"), Tema.FONTE_ITALICO))
	abrir_inventario()

func _corpo_ferreiro() -> void:
	if not jan.has("servico"): return
	var c: Control = corpo["servico"]
	_limpar(c)
	_fala_servico(c, servico_d)
	var j := _jog()
	c.add_child(Tema.rotulo("Lágrima Angélica: +0 a +6, sempre dá certo.\nLágrima Sanguínea: +6 a +15; a chance cai a cada nível e, se falhar, o item perde nível (nunca abaixo de +6). Nada quebra.", 13, Color("#c8bfa8")))
	c.add_child(Tema.rotulo("Atenção: passar do +10 tem 15% de chance de quebrar o item.", 13, Color("#e0a050"), Tema.FONTE_ITALICO))
	c.add_child(Tema.rotulo("Angélicas: %d    Sanguíneas: %d    Ouro: %d" % [Itens.contar(j.inv, "lagrima_angelica"), Itens.contar(j.inv, "lagrima_sanguinea"), j.ouro], 14, Tema.COR_OURO, Tema.FONTE_TITULO))
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var v := VBoxContainer.new(); v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(v); c.add_child(sc)
	var itens: Array = []
	for s in Itens.SLOTS:
		if j.equip.has(s): itens.append([j.equip[s], s])
	for it in j.inv:
		if Itens.equipavel(it): itens.append([it, "mochila"])
	if itens.is_empty(): v.add_child(Tema.rotulo("Nada para refinar.", 14, Color("#7d7466"), Tema.FONTE_ITALICO))
	for par in itens:
		var it: Dictionary = par[0]
		var r := int(it.get("refino", 0))
		var b := Button.new()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var ch := "" if r < 6 else "  %d%%" % roundi(100.0 * Jogador.chance_refino(r + 1))
		b.text = "%s%s   →  +%d%s  (%d ouro)" % [Itens.nome(it), "  [equipado]" if par[1] != "mochila" else "", r + 1, ch, 50 * (r + 1)] if r < 15 else "%s   (máximo)" % Itens.nome(it)
		b.disabled = r >= 15
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		b.mouse_entered.connect(func(): game.hud.mostrar_tip_item(it, tip_item(it)))
		b.mouse_exited.connect(func(): game.hud.esconder_tip())
		b.pressed.connect(func(): game.cmd("refinar", [int(it["uid"]), par[1]]))
		v.add_child(b)

func _abrir_armazem(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Armazém"), Vector2(416, 540), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Armazém"))
	_fala_servico(c, d)
	var cg := CenterContainer.new(); cg.add_child(_grade("armazem")); c.add_child(cg)
	var rod := HBoxContainer.new()
	var livre := Tema.rotulo("", 13, Color("#c8bfa8"), Tema.FONTE_TITULO); livre.name = "ArcaLivre"
	livre.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rod.add_child(livre)
	rod.add_child(_botao_menu("Guardar materiais", _guardar_materiais))
	c.add_child(rod)
	_atualizar_arca()
	abrir_inventario()

func _atualizar_arca() -> void:
	if not jan.has("servico") or servico_d.get("tipo") != "armazem": return
	var l: Label = corpo["servico"].find_child("ArcaLivre", true, false)
	if l == null: return
	var usados := 0
	for it in _jog().armazem:
		var g := Itens.grade(it); usados += g.x * g.y
	var tot := Itens.ARMAZEM_W * Itens.ARMAZEM_H
	l.text = "%d de %d espaços livres" % [tot - usados, tot]
	l.add_theme_color_override("font_color", Color("#ff6a4a") if tot - usados < 12 else Color("#c8bfa8"))

## Manda para a arca todo material e joia da mochila (a posição é escolhida aqui; o servidor confere cada uma).
func _guardar_materiais() -> void:
	var j := _jog()
	var lista: Array = j.armazem.duplicate()
	var n := 0
	for it in j.inv.duplicate():
		if not Itens.categoria(it) in ["material", "joia"]: continue
		var p := Itens.achar_lugar(lista, Itens.ARMAZEM_W, Itens.ARMAZEM_H, it)
		if p.x < 0: game.hud.aviso("A arca está cheia."); break
		var cp: Dictionary = it.duplicate(); cp["x"] = p.x; cp["y"] = p.y
		lista.append(cp)
		game.cmd("mover_item", [int(it["uid"]), "mochila", "armazem", p.x, p.y])
		n += 1
	if n == 0: game.hud.aviso("Nenhum material ou joia na mochila.")
	else: game.audio.tocar("ui/soltar_item", null, -6.0)

func _botao_menu(txt: String, acao: Callable) -> Button:
	var b := Button.new(); b.text = txt
	b.pressed.connect(func(): game.audio.tocar("ui/clique", null, -6.0); acao.call())
	return b

func _abrir_treinador(d: Dictionary) -> void:
	var c := _janela("servico", d.get("titulo", "Treino"), Vector2(380, 220), "esquerda")
	_limpar(c)
	_titulo("servico", d.get("titulo", "Treino"))
	_fala_servico(c, d)
	var j := _jog()
	c.add_child(Tema.rotulo("Devolve todos os pontos de atributo para você distribuir de novo.", 14, Color("#c8bfa8")))
	var b := Button.new(); b.text = "Redistribuir (%d ouro)" % (20 * j.nivel)
	b.pressed.connect(func(): game.cmd("redistribuir"); abrir_personagem())
	c.add_child(b)

# =================================================================== troca entre jogadores (estilo MU)
## Em cima a oferta do outro (só olhar), embaixo a sua: arraste da mochila ou use o botão direito. Qualquer mudança
## desfaz as confirmações e o Confirmar fica apagado por alguns segundos. Quem decide tudo é o servidor (net/troca.gd).
const TROCA_W := 8
const TROCA_H := 4

func troca_estado(d: Dictionary) -> void:
	var nova := troca_d.is_empty()
	troca_d = d
	if game.hud.troca_box != null and is_instance_valid(game.hud.troca_box): game.hud.troca_box.queue_free()
	troca_ok_ms = Time.get_ticks_msec() + int(float(d.get("espera", 0.0)) * 1000.0)
	if nova or not aberta("troca"): _abrir_troca()
	_atualizar_troca()

func troca_fim(d: Dictionary) -> void:
	troca_d = {}
	if not mao.is_empty() and mao.get("de") == "troca": mao = {}
	if jan.has("troca"): jan["troca"].visible = false
	game.hud.esconder_tip()
	game.hud.aviso(str(d.get("motivo", "")))
	game.audio.tocar("itens/moedas" if d.get("ok", false) else "ui/erro", null, -4.0)
	_redesenhar_tudo()

func _na_troca(uid: int) -> bool:
	for it in troca_d.get("eu", {}).get("itens", []):
		if int(it["uid"]) == uid: return true
	return false

func _soltar_troca(onde: String, c0: Vector2i) -> void:
	var it: Dictionary = mao["it"]
	var uid := int(it["uid"])
	match [mao["de"], onde]:
		["mochila", "troca"], ["troca", "troca"]: game.troca_cmd("por", {"uid": uid, "x": c0.x, "y": c0.y})
		["troca", "mochila"]: game.troca_cmd("tirar", {"uid": uid})
		["equip", "troca"]: game.hud.aviso("Tire o item do corpo primeiro.")
		["mochila", "mochila"]: game.hud.aviso("Termine a troca primeiro.")
	game.audio.tocar("ui/soltar_item", null, -8.0)
	mao = {}

func _abrir_troca() -> void:
	if aberta("servico"): fechar("servico")
	if aberta("dialogo"): fechar("dialogo")
	var c := _janela("troca", "TROCA", Vector2(300, 520), "esquerda")
	abrir_inventario()
	if c.get_child_count() > 0: return
	var quem := Tema.rotulo("", 16, Color("#f0e2c0"), Tema.FONTE_TITULO, 2); quem.name = "Quem"
	quem.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(quem)
	var g1 := CenterContainer.new(); g1.add_child(_grade("troca_outro")); c.add_child(g1)
	var lo := HBoxContainer.new(); lo.name = "LinhaOutro"
	var oo := Tema.rotulo("", 15, Tema.COR_OURO, Tema.FONTE_TITULO, 2); oo.name = "Ouro"
	oo.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lo.add_child(oo)
	var so := Tema.rotulo("", 13, Color("#8f8270"), Tema.FONTE_ITALICO, 2); so.name = "Estado"
	lo.add_child(so)
	c.add_child(lo)
	var linha := ColorRect.new(); linha.color = Color(0.42, 0.34, 0.2, 0.6); linha.custom_minimum_size.y = 1
	c.add_child(linha)
	var tu := Tema.rotulo("SUA OFERTA", 15, Color("#e0c890"), Tema.FONTE_TITULO, 2)
	tu.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(tu)
	var g2 := CenterContainer.new(); g2.add_child(_grade("troca")); c.add_child(g2)
	var lu := HBoxContainer.new(); lu.name = "LinhaEu"; lu.add_theme_constant_override("separation", 6)
	var ou := Tema.rotulo("", 15, Tema.COR_OURO, Tema.FONTE_TITULO, 2); ou.name = "Ouro"
	ou.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lu.add_child(ou)
	var campo := LineEdit.new(); campo.name = "Campo"; campo.placeholder_text = "ouro"
	campo.custom_minimum_size = Vector2(92, 0); campo.max_length = 10
	campo.add_theme_font_override("font", Tema.FONTE_TEXTO)
	campo.text_changed.connect(func(tx: String):   # só dígitos
		var so_num := ""
		for ch in tx:
			if ch in "0123456789": so_num += ch
		if so_num != tx: campo.text = so_num; campo.caret_column = so_num.length())
	campo.text_submitted.connect(func(_tx): _por_ouro(campo))
	lu.add_child(campo)
	var bo := Button.new(); bo.text = "Pôr ouro"; bo.focus_mode = Control.FOCUS_NONE
	bo.pressed.connect(func(): _por_ouro(campo))
	lu.add_child(bo)
	c.add_child(lu)
	var bt := HBoxContainer.new(); bt.alignment = BoxContainer.ALIGNMENT_CENTER; bt.add_theme_constant_override("separation", 12)
	var ok := Button.new(); ok.name = "Ok"; ok.custom_minimum_size = Vector2(130, 32); ok.focus_mode = Control.FOCUS_NONE
	ok.pressed.connect(func(): game.troca_cmd("ok"); game.audio.tocar("ui/confirmar", null, -6.0))
	bt.add_child(ok)
	var cancelar := Button.new(); cancelar.text = "Cancelar"; cancelar.custom_minimum_size = Vector2(110, 32); cancelar.focus_mode = Control.FOCUS_NONE
	cancelar.pressed.connect(func(): fechar("troca"))
	bt.add_child(cancelar)
	bt.name = "Botoes"
	c.add_child(bt)
	var dica := Tema.rotulo("Arraste da mochila ou use o botão direito. Qualquer mudança desfaz as confirmações.", 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	dica.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; dica.custom_minimum_size.x = 270
	c.add_child(dica)

func _por_ouro(campo: LineEdit) -> void:
	var v := mini(int(campo.text) if campo.text.is_valid_int() else 0, _jog().ouro)
	game.troca_cmd("ouro", {"valor": v})
	campo.text = ""
	campo.release_focus()

func _atualizar_troca() -> void:
	if not jan.has("troca") or troca_d.is_empty(): return
	var c: Control = corpo["troca"]
	var o: Dictionary = troca_d.get("outro", {})
	var eu: Dictionary = troca_d.get("eu", {})
	var quem: Label = c.get_node("Quem")
	quem.text = "%s · %s nível %d" % [str(o.get("nome", "?")), str(o.get("classe", "")).capitalize(), int(o.get("nivel", 0))]
	quem.add_theme_color_override("font_color", Color(game.hud.COR_CLASSE.get(str(o.get("classe", "")), "#f0e2c0")))
	(c.get_node("LinhaOutro/Ouro") as Label).text = "◉ %d ouro" % int(o.get("ouro", 0))
	var est: Label = c.get_node("LinhaOutro/Estado")
	est.text = "✔ confirmou" if o.get("ok", false) else "escolhendo..."
	est.add_theme_color_override("font_color", Color("#8fe07a") if o.get("ok", false) else Color("#8f8270"))
	(c.get_node("LinhaEu/Ouro") as Label).text = "◉ %d" % int(eu.get("ouro", 0))
	_botao_ok_troca()
	_redesenhar(jan["troca"])
	if jan.has("inventario"): _redesenhar(jan["inventario"])

func _botao_ok_troca() -> void:
	var ok: Button = corpo["troca"].get_node("Botoes/Ok")
	var falta := troca_ok_ms - Time.get_ticks_msec()
	var eu_ok: bool = troca_d.get("eu", {}).get("ok", false)
	var txt := "✔ Confirmado" if eu_ok else ("Confirmar (%d)" % ceili(falta / 1000.0) if falta > 0 else "Confirmar")
	if ok.text != txt: ok.text = txt
	ok.disabled = eu_ok or falta > 0

# =================================================================== textos de lore
func texto(titulo: String, txt: String) -> void:
	var c := _janela("texto", titulo, Vector2(520, 380), "centro")
	_limpar(c)
	_titulo("texto", titulo)
	if Tema.ui("menu_moldura") == null:
		var p: PanelContainer = jan["texto"]
		var sb := Tema.caixa(Color(0.16, 0.13, 0.095, 0.97), Color(0.45, 0.36, 0.22), 2, 3)
		sb.set_content_margin_all(18)
		p.add_theme_stylebox_override("panel", sb)
	var r := RichTextLabel.new(); r.bbcode_enabled = true; r.size_flags_vertical = Control.SIZE_EXPAND_FILL
	r.add_theme_font_override("normal_font", Tema.FONTE_ITALICO)
	r.add_theme_font_size_override("normal_font_size", 17)
	r.add_theme_color_override("default_color", Color("#e8dcc0"))
	r.text = txt
	c.add_child(r)
	game.audio.tocar("ui/pagina", null, -4.0)

func fechar_texto() -> void:
	fechar("texto")

# =================================================================== menu
func abrir_menu() -> void:
	var c := _janela("menu", "DARK PASSAGE", Vector2(300, 356), "centro")
	if game.hud.mapa_ui: game.hud.mapa_ui.visible = false
	_limpar(c)
	var itens := [
		["Continuar", func(): fechar("menu")],
		["Como jogar (H)", func(): fechar("menu"); game.hud.mostrar_ajuda()],
		["Modo automático (Shift+Z)", func(): fechar("menu"); abrir_auto()],
		["Teleporte (V)", func(): fechar("menu"); abrir_teleporte()],
		["Configurações (F10)", func(): fechar("menu"); Configuracoes.abrir(self, abrir_menu)],
		["Salvar e voltar ao início" if game.rede == null else "Sair da partida", func(): game._salvar(); game.sair_rede(); get_tree().reload_current_scene()],
	]
	if not ResourceLoader.exists("res://scripts/client/ajustes.gd"):   # sem o menu de configurações, o Controle abre daqui
		itens.insert(itens.size() - 1, ["Controle", func(): fechar("menu"); ControleJanela.abrir(game)])
	for it in itens:
		var b := Button.new(); b.text = it[0]; b.custom_minimum_size = Vector2(0, 40)
		b.add_theme_font_size_override("font_size", 15)
		b.pressed.connect(it[1])
		c.add_child(b)
	var v := Tema.rotulo("Prévia v0.7 · " + ("jogo pausado · salva sozinho" if game.rede == null else "em rede o mundo não pausa · o servidor salva"), 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	v.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(v)

func fechar_dialogo() -> void:
	fechar("dialogo")

# =================================================================== modo automático (Shift+Z)
## Ajustes do automático: quais skills ele usa, raio de caça, o que junta do chão e quando bebe poção.
## Tudo vira comando ("auto_skill" / "auto_cfg"); o servidor confere e guarda no save do personagem.
const AUTO_RAIOS := [[4.0, "Curto"], [6.0, "Médio"], [8.0, "Longo"], [10.0, "Amplo"]]
const AUTO_VIDAS := [0.3, 0.4, 0.5, 0.6, 0.7]
const AUTO_RECURSOS := [0.15, 0.25, 0.35, 0.5]
const AUTO_JUNTAR_NOME := {"tudo": "tudo", "bons": "ouro, poções, mágicos+", "ouro": "só ouro", "nada": "nada"}

func auto_mudou() -> void:
	# em rede o ajuste novo chega no snapshot seguinte: redesenha logo depois
	if not aberta("auto"): return
	if game.rede == null: abrir_auto.call_deferred()
	else: get_tree().create_timer(0.2).timeout.connect(func(): if aberta("auto"): abrir_auto())

func _proximo(lista: Array, atual: float) -> float:
	for v in lista:
		if float(v) > atual + 0.001: return float(v)
	return float(lista[0])

func abrir_auto() -> void:
	var c := _janela("auto", "MODO AUTOMÁTICO", Vector2(470, 480), "centro")
	jan["auto"].offset_top = -320; jan["auto"].offset_bottom = 160   # cresce para baixo sem cobrir a barra (classes com 7 skills)
	_limpar(c)
	var j := _jog()
	var cfg := Jogador.cfg_auto(j)
	var dica := Tema.rotulo("Z liga e desliga. Clique direito numa skill da barra também a põe ou tira daqui. Caça em volta de onde foi ligado e para se aparecer um chefe.", 13, Color("#a89f8c"), Tema.FONTE_ITALICO)
	dica.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; dica.custom_minimum_size.x = 440
	c.add_child(dica)
	c.add_child(_auto_secao("Skills que ele usa"))
	var g := GridContainer.new(); g.columns = 2
	g.add_theme_constant_override("h_separation", 8); g.add_theme_constant_override("v_separation", 6)
	for i in j.skills_slots.size():
		var h := Jogador.skill_def(j, i)
		if h.is_empty() or h.get("passiva", false): continue
		var sk := Defs.skill(j.classe, h["id"])
		var bloq := j.nivel < int(h["nivel"])
		var no := Jogador.skill_no_auto(j, i)
		var b := Button.new()
		b.custom_minimum_size = Vector2(217, 32)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.text = "%d · %s%s" % [i + 1, sk.get("nome", h["nome"]), ("  (nv %d)" % int(h["nivel"])) if bloq else ""]
		b.clip_text = true
		b.add_theme_font_size_override("font_size", 11)
		var ic := Tema.icone_skill(j.classe, h["id"])
		if ic.size() == 2:
			var at := AtlasTexture.new(); at.atlas = ic[0]; at.region = ic[1]
			b.icon = at; b.expand_icon = false
			b.add_theme_constant_override("icon_max_width", 28)
		b.modulate = Color.WHITE if no else Color(0.55, 0.52, 0.48)
		if no:   # ligada: o botão fica "afundado" no latão do kit de janelas
			var sb := Tema.sb_ui("menu_botao_press", [14, 14, 14, 14], [8, 4, 8, 4])
			if sb: for est in ["normal", "hover"]: b.add_theme_stylebox_override(est, sb)
			b.add_theme_color_override("font_color", Color("#f0d48a"))
		b.tooltip_text = "No automático" if no else "Fora do automático"
		var slot := i
		b.pressed.connect(func(): game.audio.tocar("ui/clique", null, -6.0); game.cmd("auto_skill", [slot]))
		g.add_child(b)
	c.add_child(g)
	# Caça e Poções lado a lado (a janela não cobre a barra nem nas classes com 7 skills)
	var cols := HBoxContainer.new(); cols.add_theme_constant_override("separation", 8)
	var ca := VBoxContainer.new(); var po := VBoxContainer.new()
	for col in [ca, po]:
		col.size_flags_horizontal = Control.SIZE_EXPAND_FILL; col.add_theme_constant_override("separation", 6)
		cols.add_child(col)
	c.add_child(cols)
	ca.add_child(_auto_secao("Caça"))
	var raio := float(cfg["raio"])
	var nome_raio := "Médio"
	for r in AUTO_RAIOS:
		if absf(float(r[0]) - raio) < 0.5: nome_raio = r[1]
	ca.add_child(_auto_botao("Raio: %s (%d passos)" % [nome_raio, roundi(raio)], func():
		var prox := AUTO_RAIOS[0]
		for r in AUTO_RAIOS:
			if float(r[0]) > raio + 0.5: prox = r; break
		game.cmd("auto_cfg", ["raio", float(prox[0])])))
	var am := int(cfg["area_min"])
	ca.add_child(_auto_botao("Skill em área: %d+ %s" % [am, "monstro" if am == 1 else "monstros"], func(): game.cmd("auto_cfg", ["area_min", am % 3 + 1])))
	var ordem: Array = Jogador.AUTO_JUNTAR
	var jt: String = cfg["juntar"]
	var bj := _auto_botao("Juntar: %s" % AUTO_JUNTAR_NOME.get(jt, jt), func(): game.cmd("auto_cfg", ["juntar", ordem[(ordem.find(jt) + 1) % ordem.size()]]))
	bj.clip_text = true
	ca.add_child(bj)
	po.add_child(_auto_secao("Poções"))
	var vd := float(cfg["vida"])
	po.add_child(_auto_botao("Vida abaixo de %d%%" % roundi(vd * 100.0), func(): game.cmd("auto_cfg", ["vida", _proximo(AUTO_VIDAS, vd)])))
	if j.rec_max > 0.0:
		var rc := float(cfg["recurso"])
		po.add_child(_auto_botao("%s abaixo de %d%%" % [game.hud._nome_recurso().capitalize(), roundi(rc * 100.0)], func(): game.cmd("auto_cfg", ["recurso", _proximo(AUTO_RECURSOS, rc)])))
	var ps: bool = cfg["pocao_sempre"]
	var bp := _auto_botao("Fora do Z: %s" % ("bebe sozinho" if ps else "só na mão"), func(): game.cmd("auto_cfg", ["pocao_sempre", not ps]))
	bp.tooltip_text = "Bebe poção sozinho em combate mesmo com o automático desligado."
	po.add_child(bp)
	var lig: bool = j.aux.get("auto", false)
	var bz := _auto_botao("Desligar o automático (Z)" if lig else "Ligar o automático aqui (Z)", func(): game.cmd("auto", [not lig]); fechar("auto"))
	bz.add_theme_color_override("font_color", Color("#f0dca0"))
	c.add_child(bz)

func _auto_secao(txt: String) -> Control:
	var l := Tema.rotulo(txt.to_upper(), 13, Color("#c9a860"), Tema.FONTE_TITULO, 2)
	l.custom_minimum_size.y = 16
	return l

func _auto_botao(txt: String, acao: Callable) -> Button:
	var b := Button.new(); b.text = txt; b.custom_minimum_size = Vector2(0, 28)
	b.add_theme_font_size_override("font_size", 13)
	b.pressed.connect(func(): game.audio.tocar("ui/clique", null, -6.0); acao.call())
	return b

# =================================================================== árvore de talentos (T)
## Tronco com um galho por skill ativa, na ordem do nível; clique esquerdo põe 1 ponto. A regra fica em Jogador (talentos_em).
var _tal_hover := -1
const _TAL_X := 222.0   # tronco

func _tal_skills() -> Array:
	var out: Array = []
	for h in Defs.CLASSES[_jog().classe]["habilidades"]:
		if not h.get("passiva", false): out.append(h)
	out.sort_custom(func(a, b): return int(a["nivel"]) < int(b["nivel"]))
	return out

func _tal_no(i: int) -> Vector2:
	return Vector2(_TAL_X - 44.0 if i % 2 == 0 else _TAL_X + 44.0, 30.0 + 50.0 * i)

func abrir_talentos() -> void:
	var c := _janela("talentos", "ÁRVORE DE TALENTOS", Vector2(470, 0), "esquerda")
	_limpar(c)
	var j := _jog()
	var livres := Jogador.talentos_livres(j)
	var prox := (j.nivel / Jogador.TALENTO_NIVEIS + 1) * Jogador.TALENTO_NIVEIS
	var topo := Tema.rotulo("%d %s · próximo no nível %d" % [livres, "ponto livre" if livres == 1 else "pontos livres", prox], 15,
		Color("#f0dca0") if livres > 0 else Color("#a89f8c"), Tema.FONTE_TITULO, 2)
	topo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(topo)
	var dica := Tema.rotulo("Cada ponto: +%d%% de dano e cura, +%d%% de duração, -%d%% de recarga (até %d por skill)." % [
		roundi(Jogador.TALENTO_DANO * 100), roundi(Jogador.TALENTO_DURACAO * 100), roundi(Jogador.TALENTO_RECARGA * 100), Jogador.TALENTO_MAX], 12, Color("#a89f8c"), Tema.FONTE_ITALICO)
	dica.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; dica.custom_minimum_size.x = 440
	c.add_child(dica)
	var n := _tal_skills().size()
	var d := Desenho.new()
	d.custom_minimum_size = Vector2(430, 6.0 + 50.0 * n)
	d.mouse_filter = Control.MOUSE_FILTER_STOP
	d.desenhar = _desenhar_talentos
	d.entrada = _entrada_talentos
	d.mouse_exited.connect(func(): _tal_hover = -1; game.hud.esconder_tip(); d.queue_redraw())
	var caixa := PanelContainer.new()   # a árvore fica numa caixa interna do kit de janelas
	caixa.add_theme_stylebox_override("panel", Tema.caixa_menu(4))
	caixa.add_child(d)
	c.add_child(caixa)
	var gastos := Jogador.talentos_gastos(j)
	if gastos > 0:
		var b := Button.new(); b.custom_minimum_size = Vector2(0, 30)
		b.text = "Esquecer talentos (%d de ouro)" % (gastos * Jogador.TALENTO_OURO_POR_PONTO)
		b.pressed.connect(func(): game.cmd("esquecer_talentos"))
		c.add_child(b)
	jan["talentos"].reset_size.call_deferred()

func talentos_mudou() -> void:
	if aberta("talentos"): abrir_talentos.call_deferred() if game.rede == null else get_tree().create_timer(0.2).timeout.connect(func(): if aberta("talentos"): abrir_talentos())

func _desenhar_talentos(g: Desenho) -> void:
	var j := _jog()
	var hs := _tal_skills()
	var t := Time.get_ticks_msec() / 1000.0
	var livres := Jogador.talentos_livres(j)
	# tronco de latão com rebites
	var y0 := _tal_no(0).y; var y1 := _tal_no(hs.size() - 1).y
	g.draw_rect(Rect2(_TAL_X - 4.0, y0 - 20, 8, y1 - y0 + 40), Color(0.09, 0.06, 0.03))
	g.draw_rect(Rect2(_TAL_X - 3.0, y0 - 20, 6, y1 - y0 + 40), Color(0.55, 0.38, 0.16))
	g.draw_rect(Rect2(_TAL_X - 2.0, y0 - 20, 2, y1 - y0 + 40), Color(0.94, 0.78, 0.45, 0.6))
	for i in hs.size():
		var h: Dictionary = hs[i]
		var p := _tal_no(i)
		var bloq := j.nivel < int(h["nivel"])
		var r := Jogador.talento(j, h["id"])
		# galho até o tronco + rebite
		var cor_galho := Color(0.55, 0.38, 0.16) if not bloq else Color(0.25, 0.2, 0.15)
		g.draw_line(Vector2(_TAL_X, p.y), p + Vector2(-34 if p.x > _TAL_X else 34, 0), Color(0.09, 0.06, 0.03), 7.0)
		g.draw_line(Vector2(_TAL_X, p.y), p + Vector2(-34 if p.x > _TAL_X else 34, 0), cor_galho, 4.0)
		g.draw_circle(Vector2(_TAL_X, p.y), 6.0, Color(0.09, 0.06, 0.03)); g.draw_circle(Vector2(_TAL_X, p.y), 4.5, Color(0.78, 0.58, 0.28))
		g.draw_circle(Vector2(_TAL_X - 1.0, p.y - 1.5), 1.6, Color(1, 0.92, 0.7, 0.8))
		# ícone no slot da barra (mesma moldura aprovada)
		var rr := Rect2(p - Vector2(26, 26), Vector2(52, 52))
		var ic := Tema.icone_skill(j.classe, h["id"])
		var mod := Color(0.3, 0.3, 0.3) if bloq else Color.WHITE
		if ic.size() == 2: g.draw_texture_rect_region(ic[0], Rect2(rr.position + Vector2(6, 6), Vector2(40, 40)), ic[1], mod)
		g.draw_texture(Tema.ui("slot_sombra"), rr.position)
		g.draw_texture(Tema.ui("slot_hover" if i == _tal_hover and not bloq else "slot_moldura"), rr.position)
		if not bloq and livres > 0 and r < Jogador.TALENTO_MAX:
			var pulso := 0.5 + 0.5 * sin(t * 3.0 + i)
			g.draw_rect(rr.grow(2.0 + pulso), Color(0.98, 0.8, 0.3, 0.35 + 0.35 * pulso), false, 1.5)
		if bloq: game.hud._txt(g, rr.position + Vector2(26, 33), "%d" % int(h["nivel"]), 14, Color("#a89f8c"))
		# nome e losangos de rank para fora do tronco
		var nome: String = Defs.skill(j.classe, h["id"]).get("nome", h["nome"])
		var esq := p.x < _TAL_X
		var x_txt := p.x - 34.0 if esq else p.x + 34.0
		game.hud._txt(g, Vector2(x_txt, p.y - 4), nome, 12, Color("#f0dca0") if not bloq else Color("#7d7466"), Tema.FONTE_TITULO, 1 if esq else -1, 2)
		var x0 := x_txt - 10.0 * Jogador.TALENTO_MAX + 5.0 if esq else x_txt + 5.0
		for k in Jogador.TALENTO_MAX:
			var cx := x0 + 10.0 * k
			var cy := p.y + 12.0
			var los := PackedVector2Array([Vector2(cx, cy - 4), Vector2(cx + 4, cy), Vector2(cx, cy + 4), Vector2(cx - 4, cy)])
			g.draw_colored_polygon(los, Color(0.06, 0.04, 0.03))
			if k < r:
				g.draw_colored_polygon(PackedVector2Array([Vector2(cx, cy - 3), Vector2(cx + 3, cy), Vector2(cx, cy + 3), Vector2(cx - 3, cy)]), Color(0.96, 0.76, 0.32))
			else:
				g.draw_polyline(PackedVector2Array([los[0], los[1], los[2], los[3], los[0]]), Color(0.45, 0.34, 0.18), 1.0)

func _tal_em(p: Vector2) -> int:
	for i in _tal_skills().size():
		if Rect2(_tal_no(i) - Vector2(28, 28), Vector2(56, 56)).has_point(p): return i
	return -1

func _entrada_talentos(g: Desenho, ev: InputEvent) -> void:
	var hs := _tal_skills()
	if ev is InputEventMouseMotion:
		var i := _tal_em(ev.position)
		if i != _tal_hover:
			_tal_hover = i; g.queue_redraw()
			if i >= 0: game.hud.mostrar_tip(_tip_talento(hs[i]))
			else: game.hud.esconder_tip()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		var i := _tal_em(ev.position)
		if i >= 0:
			game.audio.tocar("ui/clique", null, -6.0)
			game.cmd("talento", [hs[i]["id"]])

func _tip_talento(h: Dictionary) -> String:
	var j := _jog()
	var r := Jogador.talento(j, h["id"])
	var nome: String = Defs.skill(j.classe, h["id"]).get("nome", h["nome"])
	var s := "[font_size=17][color=#f0dca0]%s[/color][/font_size]  [color=#a89f8c]%d/%d[/color]\n" % [nome, r, Jogador.TALENTO_MAX]
	var agora := Jogador.talentos_em(j, h)
	s += "[color=#e8dfc9]Agora: +%d%% dano e cura · recarga %.1fs[/color]" % [roundi(Jogador.TALENTO_DANO * 100 * r), float(agora.get("recarga", 0))]
	if r < Jogador.TALENTO_MAX:
		s += "\n[color=#9cc8ff]Próximo ponto: +%d%% dano e cura · recarga %.1fs[/color]" % [roundi(Jogador.TALENTO_DANO * 100 * (r + 1)), float(h.get("recarga", 0)) * (1.0 - Jogador.TALENTO_RECARGA * (r + 1))]
	if j.nivel < int(h["nivel"]): s += "\n[color=#ff6a4a]Libera no nível %d[/color]" % int(h["nivel"])
	return s

# =================================================================== menu de teleporte (V)
## Lista estilo MU: cada área de caça com o nome e a faixa de nível; viajar custa 3.000 de ouro, que o servidor
## só gasta quando o canal de 3 s termina (andar ou apanhar cancela). A regra é Teleporte.bloqueio, a mesma do servidor.
const TP_COR_FAIXA := Color("#a8d870")    # nível do jogador dentro da faixa
const TP_COR_ACIMA := Color("#8f8574")    # área fraca para ele
const TP_COR_TRANCADO := Color("#b0473c")

func abrir_teleporte() -> void:
	var c := _janela("teleporte", "TELEPORTE", Vector2(780, 548), "centro")
	jan["teleporte"].offset_top = -330; jan["teleporte"].offset_bottom = 218
	_limpar(c)
	var j := _jog()
	var preco := Teleporte.preco({})
	var falta := j.ouro < preco
	# placa do preço: quanto custa e quanto ouro o jogador tem
	var topo := PanelContainer.new(); topo.add_theme_stylebox_override("panel", Tema.caixa_menu(8))
	var th := HBoxContainer.new(); th.add_theme_constant_override("separation", 12); topo.add_child(th)
	var tv := VBoxContainer.new(); tv.add_theme_constant_override("separation", 0)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL; tv.alignment = BoxContainer.ALIGNMENT_CENTER
	tv.add_child(Tema.rotulo("Cada viagem custa %s de ouro" % _milhar(preco), 16, Tema.COR_OURO, Tema.FONTE_TITULO))
	tv.add_child(Tema.rotulo("Escolha uma área de caça. Voltar ao acampamento (R) continua grátis.", 13, Color("#a89f8c"), Tema.FONTE_ITALICO))
	th.add_child(tv)
	var qt := Tema.rotulo(_milhar(j.ouro), 24, Tema.COR_SANGUE.lightened(0.2) if falta else Tema.COR_OURO, Tema.FONTE_TITULO, 3)
	qt.tooltip_text = "Seu ouro"; qt.mouse_filter = Control.MOUSE_FILTER_PASS
	var qv := VBoxContainer.new(); qv.alignment = BoxContainer.ALIGNMENT_CENTER; qv.add_theme_constant_override("separation", -4)
	qt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; qv.add_child(qt)
	var ql := Tema.rotulo("seu ouro", 11, Color("#7d7466"), Tema.FONTE_ITALICO); ql.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	qv.add_child(ql); qv.custom_minimum_size.x = 96
	th.add_child(qv)
	c.add_child(topo)
	# uma coluna por região (Deserto de Absinto, Novo Éden...); regiões novas descem para a linha de baixo
	var sc := ScrollContainer.new(); sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var grade := GridContainer.new(); grade.columns = 2; grade.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grade.add_theme_constant_override("h_separation", 12); grade.add_theme_constant_override("v_separation", 10)
	sc.add_child(grade); c.add_child(sc)
	var aqui: String = game.sim.zona_em(j.pos) if game.sim else ""
	var mapa_aqui: String = game.sim.mapa_id if game.sim else ""
	var colunas := {}
	var rolar_para: Control = null
	var sb_linha := _sb("menu_botao", [14, 14, 14, 14], [12, 2, 12, 2])
	var sb_hover := _sb("menu_botao_hover", [14, 14, 14, 14], [12, 2, 12, 2])
	var sb_off := _sb("menu_botao_off", [14, 14, 14, 14], [12, 2, 12, 2])
	var sb_aqui := _sb("menu_botao_press", [14, 14, 14, 14], [12, 2, 12, 2])
	for d: Dictionary in Teleporte.destinos():
		var grupo := str(d.get("grupo", ""))
		if not colunas.has(grupo):
			var col := VBoxContainer.new(); col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			col.add_theme_constant_override("separation", 3)
			var gl := _auto_secao(grupo); gl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; gl.custom_minimum_size.y = 22
			col.add_child(gl)
			var dv := TextureRect.new(); dv.texture = Tema.ui("menu_divisor"); dv.stretch_mode = TextureRect.STRETCH_SCALE
			dv.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; dv.custom_minimum_size = Vector2(0, 8)
			if dv.texture: col.add_child(dv)
			grade.add_child(col); colunas[grupo] = col
		var motivo := Teleporte.bloqueio(null, j, d)
		var nv: Array = d.get("nivel", [1, 1])
		var trancado := j.nivel < int(d.get("nivel_min", 1)) or (d.has("requer_flag") and not j.flags.has(str(d["requer_flag"])))
		var esta_aqui := str(d["mapa"]) == mapa_aqui and str(d["id"]) == aqui
		var b := Button.new()
		b.custom_minimum_size = Vector2(0, 30)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_override("font", Tema.FONTE_TEXTO); b.add_theme_font_size_override("font_size", 14)
		if sb_linha:   # todos os estados: o Button mede a altura pelo maior stylebox, e o do tema é alto demais para uma lista
			for est in ["normal", "normal_mirrored"]: b.add_theme_stylebox_override(est, sb_aqui if esta_aqui else sb_linha)
			for est in ["hover", "hover_mirrored"]: b.add_theme_stylebox_override(est, sb_hover if sb_hover else sb_linha)
			for est in ["pressed", "pressed_mirrored", "hover_pressed", "hover_pressed_mirrored"]: b.add_theme_stylebox_override(est, sb_aqui if sb_aqui else sb_linha)
			for est in ["disabled", "disabled_mirrored"]: b.add_theme_stylebox_override(est, sb_off if sb_off else sb_linha)
			b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		b.text = str(d["nome"]) + ("  · base" if d.has("base") else "")
		var h := HBoxContainer.new(); h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		h.mouse_filter = Control.MOUSE_FILTER_IGNORE; h.alignment = BoxContainer.ALIGNMENT_END
		h.add_theme_constant_override("separation", 0)
		if esta_aqui:
			var la := Tema.rotulo("aqui", 12, Color("#c9a860"), Tema.FONTE_ITALICO); la.mouse_filter = Control.MOUSE_FILTER_IGNORE
			la.custom_minimum_size.x = 40; h.add_child(la)
		var faixa := "Nv %d" % int(nv[0]) if int(nv[0]) == int(nv[1]) else "Nv %d–%d" % [int(nv[0]), int(nv[1])]
		var cor_nv := TP_COR_TRANCADO if trancado else (TP_COR_FAIXA if j.nivel <= int(nv[1]) else TP_COR_ACIMA)
		var ln := Tema.rotulo(faixa, 13, cor_nv, Tema.FONTE_TITULO, 2)
		ln.mouse_filter = Control.MOUSE_FILTER_IGNORE; ln.custom_minimum_size.x = 70
		ln.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT; ln.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ln.size_flags_vertical = Control.SIZE_FILL
		h.add_child(ln)
		var m := Control.new(); m.custom_minimum_size.x = 14; m.mouse_filter = Control.MOUSE_FILTER_IGNORE; h.add_child(m)
		b.add_child(h)
		if trancado:
			b.disabled = true
			b.mouse_filter = Control.MOUSE_FILTER_PASS   # o tooltip ainda diz o que falta
			b.add_theme_color_override("font_disabled_color", Color("#6e665a"))
		elif esta_aqui:
			b.add_theme_color_override("font_color", Color("#f0d48a")); rolar_para = b
		var dd := d
		b.mouse_entered.connect(func():
			var txt := "[font_size=15][color=#e0c890]%s[/color][/font_size]\n%s · %s" % [dd["nome"], dd.get("grupo", ""), faixa]
			if motivo != "": txt += "\n[color=#d0675c]%s[/color]" % motivo
			else: txt += "\n[color=#a89f8c]Clique para viajar. Fique parado 3 s.[/color]"
			game.hud.mostrar_tip(txt))
		b.mouse_exited.connect(func(): game.hud.esconder_tip())
		b.pressed.connect(func():
			game.audio.tocar("ui/clique", null, -6.0)
			if motivo != "": game.hud.aviso(motivo); return
			game.cmd("teleportar", [str(dd["id"])])
			fechar("teleporte"))
		colunas[grupo].add_child(b)
	if rolar_para: sc.ensure_control_visible.call_deferred(rolar_para)
	var rod := Tema.rotulo("Verde: áreas do seu nível.  Andar ou apanhar durante a viagem cancela, e o ouro fica com você.", 12, Color("#7d7466"), Tema.FONTE_ITALICO)
	rod.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	c.add_child(rod)

## 3000 -> "3.000"
func _milhar(v: int) -> String:
	var t := str(absi(v)); var out := ""
	while t.length() > 3:
		out = "." + t.right(3) + out; t = t.left(t.length() - 3)
	return ("-" if v < 0 else "") + t + out

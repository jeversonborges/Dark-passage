extends Control
## Tela inicial: escolhe a classe (a facção vem junto) e o nome, ou continua o personagem salvo.

signal escolhido(classe: String, nome: String, salvo: Dictionary)
signal voltar()

const ORDEM := ["humano", "mutante", "tecnomancer", "anjo", "demonio", "cultista"]
const NOMES := {"anjo": "Anjo", "demonio": "Demônio", "cultista": "Cultista", "humano": "Humano", "mutante": "Mutante", "tecnomancer": "Tecnomante"}
const FANTASIA := {
	"humano": "Sem milagre nenhum: escopeta de cano serrado, espada larga e teimosia. Atira de longe enquanto tem bala e resolve no aço quando chegam perto.",
	"mutante": "O Amargo entrou no sangue e não saiu. Quanto mais apanha, mais perigoso fica. Segura a linha para os outros correrem.",
	"tecnomancer": "Ciência proibida com reza de oficina. Torretas, arcos voltaicos e nanomáquinas que costuram carne.",
	"anjo": "Porcelana rachada e asas sujas. Cura os seus enquanto julga os outros, sem pressa e sem pena.",
	"demonio": "Ex-soldado do Inferno com fome de briga. Se alimenta do dano que causa e explode se não controlar a brasa.",
	"cultista": "Paga com o próprio sangue por um poder que ninguém devia ter. Sangra os inimigos devagar e levanta os mortos para lutar."}
const PAPEL := {"humano": "Tiro e espada · versátil", "mutante": "Tanque · berserker", "tecnomancer": "Suporte · controle · torretas",
	"anjo": "Cura · corpo a corpo", "demonio": "Assassino corpo a corpo", "cultista": "Magia de sangue · invocações"}

var classe_sel := "humano"
var nome_edit := LineEdit.new()
var palco: Control
var t := 0.0
var desc: RichTextLabel
var cards := {}
var salvo := {}
var modo_rede := false     # criando personagem numa conta do servidor (sem save local)

func _ready() -> void:
	Tema.carregar()
	theme = Tema.tema_janelas()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var fundo := ColorRect.new(); fundo.color = Color(0.025, 0.02, 0.022)
	fundo.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); add_child(fundo)
	var arte := Tema.tex("res://assets/fundo_menu.png")
	if arte:
		var tr := TextureRect.new(); tr.texture = arte
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.modulate = Color(0.55, 0.52, 0.5)
		add_child(tr)
	palco = Control.new()
	palco.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	palco.mouse_filter = Control.MOUSE_FILTER_IGNORE
	palco.draw.connect(_desenhar_palco)
	add_child(palco)
	# título
	var tit := Tema.rotulo("DARK PASSAGE", 76, Color("#b0201a"), Tema.FONTE_GOTICA, 10)
	tit.set_anchors_preset(Control.PRESET_CENTER_TOP)
	tit.offset_left = -400; tit.offset_right = 400; tit.offset_top = 18; tit.offset_bottom = 110
	tit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(tit)
	var sub := Tema.rotulo("O fim começou, mas não termina. Escolha de que lado você sangra.", 17, Color("#c8bfa8"), Tema.FONTE_ITALICO, 3)
	sub.set_anchors_preset(Control.PRESET_CENTER_TOP)
	sub.offset_left = -400; sub.offset_right = 400; sub.offset_top = 104; sub.offset_bottom = 130
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(sub)
	# colunas das facções
	for lado in ["vigilia", "arautos"]:
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 8)
		if lado == "vigilia":
			col.set_anchors_preset(Control.PRESET_CENTER_LEFT)
			col.offset_left = 40; col.offset_right = 300
		else:
			col.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
			col.offset_left = -300; col.offset_right = -40
		col.offset_top = -170; col.offset_bottom = 170
		var cab := Tema.rotulo("VIGÍLIA" if lado == "vigilia" else "ARAUTOS DO JUÍZO", 18, Color("#9cc8a0") if lado == "vigilia" else Color("#e09a7a"), Tema.FONTE_TITULO, 3)
		cab.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(cab)
		var cs := Tema.rotulo("lutam para cancelar o fim" if lado == "vigilia" else "servem ao fim do mundo", 13, Color("#8a8070"), Tema.FONTE_ITALICO)
		cs.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(cs)
		for k in ORDEM:
			if (Defs.CLASSES[k]["faccao"] == "arautos") != (lado == "arautos"): continue
			var b := Button.new()
			b.custom_minimum_size = Vector2(260, 62)
			b.text = NOMES[k] + "\n" + PAPEL[k]
			b.add_theme_font_size_override("font_size", 15)
			b.toggle_mode = true
			b.pressed.connect(func(): _selecionar(k))
			col.add_child(b)
			cards[k] = b
		add_child(col)
	# descrição + nome + botões embaixo
	var baixo := VBoxContainer.new()
	baixo.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	baixo.offset_left = -330; baixo.offset_right = 330; baixo.offset_top = -190; baixo.offset_bottom = -20
	baixo.add_theme_constant_override("separation", 10)
	add_child(baixo)
	desc = RichTextLabel.new(); desc.bbcode_enabled = true; desc.fit_content = true; desc.scroll_active = false
	desc.add_theme_font_size_override("normal_font_size", 16)
	desc.add_theme_font_override("italics_font", Tema.FONTE_ITALICO)
	desc.add_theme_constant_override("outline_size", 4)
	desc.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	baixo.add_child(desc)
	var hn := HBoxContainer.new(); hn.alignment = BoxContainer.ALIGNMENT_CENTER
	hn.add_theme_constant_override("separation", 10)
	hn.add_child(Tema.rotulo("Nome", 16, Color("#e0c890"), Tema.FONTE_TITULO, 3))
	nome_edit.text = "Sobrevivente"
	nome_edit.max_length = 16
	nome_edit.custom_minimum_size = Vector2(220, 38)
	nome_edit.add_theme_font_override("font", Tema.FONTE_TITULO)
	nome_edit.add_theme_font_size_override("font_size", 16)
	var sbe := Tema.caixa(Color(0.05, 0.04, 0.035, 0.95), Color(0.42, 0.34, 0.2), 1, 2); sbe.shadow_size = 0; sbe.set_content_margin_all(6)
	nome_edit.add_theme_stylebox_override("normal", sbe)
	nome_edit.add_theme_stylebox_override("focus", sbe)
	nome_edit.text_submitted.connect(func(_x): _entrar())
	hn.add_child(nome_edit)
	var b2 := Button.new(); b2.text = "   ENTRAR   "; b2.custom_minimum_size = Vector2(150, 40)
	b2.add_theme_font_size_override("font_size", 17)
	b2.pressed.connect(_entrar)
	hn.add_child(b2)
	baixo.add_child(hn)
	salvo = {} if modo_rede else load("res://scripts/client/game.gd").carregar_save()
	if not salvo.is_empty() and Defs.CLASSES.has(salvo.get("classe", "")):
		var bc := Button.new()
		bc.text = "Continuar com %s (%s, nível %d)" % [salvo.get("nome", "?"), NOMES.get(salvo["classe"], ""), int(salvo.get("nivel", 1))]
		bc.custom_minimum_size = Vector2(0, 38)
		bc.add_theme_font_size_override("font_size", 15)
		bc.pressed.connect(func(): escolhido.emit(salvo["classe"], salvo.get("nome", "Sobrevivente"), salvo))
		baixo.add_child(bc)
	var bv := Button.new(); bv.text = "Voltar"; bv.custom_minimum_size = Vector2(0, 32)
	bv.add_theme_font_size_override("font_size", 13)
	bv.pressed.connect(func(): voltar.emit())
	baixo.add_child(bv)
	var rod := Tema.rotulo("Prévia v0.6 · " + ("novo personagem na conta do servidor" if modo_rede else "Deserto de Absinto e a Cripta da Trombeta Calada · um jogador"), 12, Color("#6d665c"), Tema.FONTE_ITALICO, 2)
	rod.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	baixo.add_child(rod)
	_selecionar("humano")
	nome_edit.call_deferred("grab_focus")

func _selecionar(k: String) -> void:
	classe_sel = k
	for c in cards: cards[c].button_pressed = c == k
	var cl: Dictionary = Defs.CLASSES[k]
	var s := "[center][font_size=24][color=#f0dca0]%s[/color][/font_size]\n[i][color=#c8bfa8]%s[/color][/i]\n" % [NOMES[k], FANTASIA[k]]
	var nomes_sk: Array = []
	for h in cl["habilidades"]:
		nomes_sk.append(Defs.skill(k, h["id"]).get("nome", h["nome"]))
	s += "[color=#8a9fb8]%s[/color][/center]" % " · ".join(nomes_sk)
	desc.text = s
	t = 0.0

func _entrar() -> void:
	var n := nome_edit.text.strip_edges()
	if n == "": n = "Sobrevivente"
	escolhido.emit(classe_sel, n, {})

func _process(dt: float) -> void:
	t += dt
	palco.queue_redraw()

func _desenhar_palco() -> void:
	var s := palco.size
	var cen := Vector2(s.x * 0.5, s.y * 0.5 + 70)
	# luz de chão
	for i in 12:
		var k := 1.0 - i / 12.0
		palco.draw_set_transform(cen, 0.0, Vector2(1.0, 0.42))
		palco.draw_circle(Vector2.ZERO, 40 + i * 16, Color(0.55, 0.4, 0.22, 0.045 * k))
	palco.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var meta: Dictionary = Defs.SPR.get(classe_sel, {})
	if meta.is_empty(): return
	var an: Dictionary = meta["anims"]["idle"]
	var tex := Tema.tex(an["file"])
	if tex == null: return
	var fr: Array = meta["frame"]; var anc: Array = meta["anchor"]
	var f := int(t * float(an["fps"])) % int(an["frames"])
	var d := int(t / 2.5) % 8
	var dirs := [0, 1, 7, 0, 1, 2, 0, 7]
	var row: int = dirs[d]
	var esc := 2.0
	var r := Rect2(cen - Vector2(anc[0], anc[1]) * esc, Vector2(fr[0], fr[1]) * esc)
	palco.draw_set_transform(cen, 0.0, Vector2(1.0, 0.4))
	palco.draw_circle(Vector2.ZERO, 46, Color(0, 0, 0, 0.45))
	palco.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	palco.draw_texture_rect_region(tex, r, Rect2(f * fr[0], row * fr[1], fr[0], fr[1]))

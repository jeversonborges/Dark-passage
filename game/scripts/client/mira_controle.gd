extends Node2D
## Combate no controle (gamepad): alvo automático com trava, mira das skills e interação pelo que está na frente.
## Não lê botão nenhum: quem mapeia o controle (thread do controle Xbox) chama passo(), ataque_basico(), usar_skill()...
## Com mouse e teclado nada muda: game.gd só desvia para cá enquanto `ativo` (último input veio do controle).
## Tudo vira comando comum (Comandos: "atacar", "skill", "interagir", "pegar"), então o servidor confere igual.

const RAIO_BUSCA := 9.0        # tiles: até onde o alvo automático procura
const RAIO_SOLTA := 11.0       # alvo automático que se afasta disso é largado
const RAIO_SOLTA_TRAVA := 14.0 # alvo travado aguenta mais longe
const RAIO_NEUTRO := 3.5       # mob neutro parado só vira alvo se estiver colado ou na mira do stick direito
const CONE_MIRA := deg_to_rad(65.0)   # stick direito: só vale o que está dentro deste cone
const RAIO_INTERAGIR := 2.6
const PASSO_BUSCA := 0.1       # reavalia o alvo 10x por segundo
const COR_SOFT := Color(1.0, 0.62, 0.3, 0.75)
const COR_TRAVA := Color(1.0, 0.25, 0.12, 0.95)
const COR_ALIADO := Color(0.45, 1.0, 0.55, 0.9)
## skills de fuga/mobilidade: vão para onde o stick esquerdo aponta, não para o inimigo
const FUGA := ["rolamento", "asas_ascensao"]

var game: Node2D
var ativo := false:
	set(v):
		if v == ativo: return
		ativo = v
		if not v: limpar()
		ativo_mudou.emit(v)
signal ativo_mudou(v: bool)
signal alvo_mudou(id: int, travado: bool)

var dir_mover := Vector2.ZERO   # mundo, normalizado ou zero
var dir_mira := Vector2.ZERO    # mundo, normalizado ou zero (stick direito)
var _ultima_dir := Vector2(1, 0)
var _alvo := -1
var travado := false
var _t_busca := 0.0
var segurando_ataque := false
var _t_reataque := 0.0
var _t_segura := 0.0   # o controle.gd repete ataque_basico(true) enquanto o botão está apertado; parou de repetir, soltou
var _t := 0.0

func _ready() -> void:
	z_index = -5   # no chão, embaixo dos pés (camada de efeitos)

## Troca automática: o controle liga, o mouse desliga. Teclado não troca (atalhos de janela continuam valendo).
func _input(ev: InputEvent) -> void:
	if ev is InputEventJoypadButton and ev.pressed: ativo = true
	elif ev is InputEventJoypadMotion and absf(ev.axis_value) > 0.5: ativo = true
	elif ev is InputEventMouseButton and ev.pressed: ativo = false
	elif ev is InputEventMouseMotion and ev.relative.length() > 6.0: ativo = false

func limpar() -> void:
	_trocar_alvo(-1, false)
	segurando_ataque = false
	dir_mover = Vector2.ZERO; dir_mira = Vector2.ZERO
	queue_redraw()

# =================================================================== API para quem mapeia o controle
## Todo frame, com os sticks já com zona morta, em coordenadas de TELA (x direita, y baixo).
func passo(dt: float, stick_mover: Vector2, stick_mira: Vector2) -> void:
	dir_mover = _tela_p_mundo(stick_mover)
	dir_mira = _tela_p_mundo(stick_mira)
	if dir_mira != Vector2.ZERO: _ultima_dir = dir_mira
	elif dir_mover != Vector2.ZERO: _ultima_dir = dir_mover
	_t_busca -= dt
	if _t_busca <= 0.0:
		_t_busca = PASSO_BUSCA
		_reavaliar()
	if segurando_ataque:
		_t_segura -= dt
		if _t_segura <= 0.0: segurando_ataque = false
		else: _segurar_ataque(dt)

## Botão de ataque (contrato do controle.gd): ataque_basico(false) no aperto, ataque_basico(true) repetido enquanto segura.
## Apertou: bate no alvo. Segurando: quando ele cai, já vai no próximo (estilo MU). Sem repetição por 0,35 s = soltou.
func ataque_basico(segurando := false) -> void:
	segurando_ataque = true
	_t_segura = 0.35
	if segurando: return   # só renova a janela; o passo() troca de alvo quando o atual cai
	_reavaliar()
	if _alvo == -1: _alvo_na_frente_para_ataque()
	if _alvo != -1: game.cmd("atacar", [_alvo, false])
	_t_reataque = 0.25

## Skill do slot (0..8) mirada pelo controle. Mesma regra de tipo do servidor (Jogador._tipo_skill).
func usar_skill(slot: int) -> void:
	var jog: Ent = game.jog
	var h := Jogador.skill_def(jog, slot)
	if h.is_empty(): return
	var tipo := Jogador._tipo_skill(h)
	match tipo:
		"alvo_aliado":
			var am := alvo_aliado(h)
			game.cmd("skill", [slot, am, jog.pos]); return
		"proprio":
			game.cmd("skill", [slot, _alvo, ponto_skill(h)]); return
	_reavaliar()
	if _alvo == -1: _alvo_na_frente_para_ataque()
	if _alvo == -1 and tipo == "alvo_inimigo": _alvo_mais_perto(maxf(Jogador._alcance_skill(h), 2.0) + 1.0)
	if _alvo == -1 and tipo == "alvo_inimigo":   # como no mouse sem ninguém por perto: não sai, mas avisa
		if "hud" in game and game.hud != null: game.hud.aviso("Nenhum inimigo ao alcance de %s." % str(h["nome"]))
		return
	game.cmd("skill", [slot, _alvo, ponto_skill(h)])

## Último recurso das skills de alvo (igual ao mouse): o inimigo mais perto em qualquer direção, até `raio`.
func _alvo_mais_perto(raio: float) -> void:
	var jog: Ent = game.jog
	var melhor: Ent = null
	var md := raio
	for e: Ent in _candidatos(raio, true):
		var d := e.pos.distance_to(jog.pos) - e.raio
		if d < md: md = d; melhor = e
	if melhor != null: _trocar_alvo(melhor.id, false)

## LB/RB: próximo alvo para a esquerda (-1) ou direita (+1) na tela. Também trava.
func ciclar_alvo(dir: int) -> void:
	var cands := _candidatos(RAIO_BUSCA, true)
	if cands.is_empty(): return
	var jx: float = Iso.to_screen(game.jog.pos).x
	cands.sort_custom(func(a: Ent, b: Ent): return Iso.to_screen(a.pos).x < Iso.to_screen(b.pos).x)
	var i := -1
	for k in cands.size():
		if cands[k].id == _alvo: i = k
	if i == -1:   # sem alvo: começa pelo primeiro daquele lado do personagem
		i = 0 if dir > 0 else cands.size() - 1
		for k in cands.size():
			var x: float = Iso.to_screen(cands[k].pos).x
			if (dir > 0 and x >= jx) or (dir < 0 and x <= jx): i = k; if dir > 0: break
	else: i = posmod(i + dir, cands.size())
	_trocar_alvo(cands[i].id, true)

## Clique do stick direito: trava no alvo atual (ou no melhor), de novo solta.
func travar_alvo() -> void:
	if travado: _trocar_alvo(_alvo, false); _reavaliar(); return
	if _alvo == -1: _reavaliar()
	if _alvo == -1: _alvo_na_frente_para_ataque()
	if _alvo != -1: _trocar_alvo(_alvo, true)

## O que o botão de contexto faria agora: "pegar", "interagir", "atacar" ou "" (para o HUD mostrar a dica).
func contexto() -> String:
	if _item_na_frente() != -1: return "pegar"
	if _interativo_na_frente() != -1: return "interagir"
	if _alvo != -1: return "atacar"
	return ""

## Botão de interação: item no chão, NPC, baú ou portal mais perto à frente.
func interagir() -> bool:
	var it := _item_na_frente()
	if it != -1: game.cmd("pegar", [it]); return true
	var o := _interativo_na_frente()
	if o != -1:
		game.cmd("interagir", [o])
		game.audio.tocar("ui/clique", null, -8.0)
		return true
	return false

## Botão contextual (um botão só para tudo): pega, fala ou bate, nessa ordem.
func acao_contexto(segurando := false) -> void:
	if not segurando and interagir(): return
	ataque_basico(segurando)

func alvo() -> int:
	return _alvo

## Ponto no mundo que faz o papel do mouse para skills de "ponto" e área.
func ponto_mira() -> Vector2:
	var jog: Ent = game.jog
	var e := _valido(_alvo)
	if e != null: return e.pos
	return jog.pos + _dir_frente() * 3.0

# =================================================================== mira das skills
func ponto_skill(h: Dictionary) -> Vector2:
	var jog: Ent = game.jog
	var id: String = h["id"]
	var alc := Jogador._alcance_skill(h)
	if id in FUGA:   # fuga: para onde o personagem anda; parado, para longe do alvo
		var d := dir_mover
		if d == Vector2.ZERO and dir_mira != Vector2.ZERO: d = dir_mira
		var e0 := _valido(_alvo)
		if d == Vector2.ZERO and e0 != null and e0.pos != jog.pos: d = (jog.pos - e0.pos).normalized()
		if d == Vector2.ZERO: d = jog.facing
		return jog.pos + d * 3.0
	var e := _valido(_alvo)
	var p: Vector2 = e.pos if e != null else jog.pos + _dir_frente() * minf(alc if alc > 0.0 else 4.0, 4.0)
	if alc > 0.0 and p.distance_to(jog.pos) > alc: p = jog.pos + (p - jog.pos).normalized() * alc
	if p.distance_to(jog.pos) <= 0.35: p = jog.pos + _dir_frente() * 0.6   # colado: ainda dá direção ao cone
	return p

## Cura/suporte: aliado travado (alvo de cura do mouse), senão o aliado na mira do stick, senão o mais ferido por perto.
## -1 = você mesmo (o servidor já faz isso).
func alvo_aliado(h: Dictionary) -> int:
	var jog: Ent = game.jog
	var alc := Jogador._alcance_skill(h)
	if alc <= 0.0: alc = 6.0
	if game._amigo_valido():
		var ea: Ent = game.sim.ents.get(game.alvo_amigo)
		if ea != null and ea.pos.distance_to(jog.pos) <= alc + 0.5: return game.alvo_amigo
	var melhor := -1
	var nota := 1e9
	for e: Ent in game.sim.ents.values():
		if e.tipo != "jogador" or e == jog or not e.vivo or jog.eh_inimigo_de(e) or not game.views.has(e.id): continue
		var d := e.pos.distance_to(jog.pos)
		if d > alc: continue
		var n: float
		if dir_mira != Vector2.ZERO:
			var ang := absf(dir_mira.angle_to(e.pos - jog.pos))
			if ang > CONE_MIRA: continue
			n = ang + d * 0.05
		else:
			if e.frac_hp() >= 0.9: continue
			n = e.frac_hp() + d * 0.01
		if n < nota: nota = n; melhor = e.id
	if melhor == -1 and jog.frac_hp() >= 0.9:
		# ninguém ferido e você cheio: o aliado mais perto (buff de escudo, nanoreparo preventivo)
		var md := alc
		for e: Ent in game.sim.ents.values():
			if e.tipo == "jogador" and e != jog and e.vivo and not jog.eh_inimigo_de(e) and game.views.has(e.id) and e.pos.distance_to(jog.pos) < md:
				md = e.pos.distance_to(jog.pos); melhor = e.id
	if melhor != -1 and game.views.has(melhor):
		game.views[melhor].cor_anel = COR_ALIADO
	return melhor

# =================================================================== escolha do alvo
func _reavaliar() -> void:
	var jog: Ent = game.jog
	if jog == null: return
	var atual := _valido(_alvo)
	if atual != null:
		var lim := RAIO_SOLTA_TRAVA if travado else RAIO_SOLTA
		if atual.pos.distance_to(jog.pos) > lim: atual = null
	if atual == null:
		_trocar_alvo(-1, false)
	elif travado:
		return
	var cands := _candidatos(RAIO_BUSCA, false)
	var melhor: Ent = null
	var nota := 1e9
	for e: Ent in cands:
		var n := _nota(e)
		if n < nota: nota = n; melhor = e
	if melhor == null: return
	if atual == null: _trocar_alvo(melhor.id, false); return
	if melhor == atual: return
	# troca só com motivo claro: o stick direito apontou para outro, ou o atual é neutro e um agressivo veio em você
	var na := _nota(atual)
	if dir_mira != Vector2.ZERO and nota < na * 0.7: _trocar_alvo(melhor.id, false)
	elif _eh_neutro_parado(atual) and melhor.alvo == jog.id: _trocar_alvo(melhor.id, false)

## Nota menor = alvo melhor. Distância pesada pelo ângulo com a mira; quem está batendo em você vem primeiro.
func _nota(e: Ent) -> float:
	var jog: Ent = game.jog
	var v := e.pos - jog.pos
	var d := maxf(v.length() - e.raio, 0.2)
	var ang := absf(_dir_frente().angle_to(v)) if v.length() > 0.01 else 0.0
	var peso := 1.0 + 1.6 * ang / PI
	if dir_mira != Vector2.ZERO:
		if ang > CONE_MIRA: peso += 4.0
		else: peso *= 0.6
	var n := d * peso
	if e.alvo == jog.id: n *= 0.6
	if e.tipo == "chefe": n *= 0.85
	if _eh_neutro_parado(e): n *= 1.6
	return n

## Inimigos que podem virar alvo. Neutro parado longe só entra se o stick direito apontar para ele
## (mob neutro só briga se apanhar: o controle não pode puxar ele sem querer).
func _candidatos(raio: float, incluir_neutros: bool) -> Array:
	var jog: Ent = game.jog
	var out: Array = []
	for e: Ent in game.sim.ents.values():
		if not e.vivo or not e.alvejavel or e.invisivel or not jog.eh_inimigo_de(e): continue
		if not game.views.has(e.id) or not game.views[e.id].visible: continue
		var v := e.pos - jog.pos
		var d := v.length()
		if d > raio: continue
		if not incluir_neutros and _eh_neutro_parado(e) and d > RAIO_NEUTRO:
			if dir_mira == Vector2.ZERO or absf(dir_mira.angle_to(v)) > CONE_MIRA * 0.6: continue
		out.append(e)
	return out

## Botão de ataque sem alvo na lista: aceita o neutro que está bem na frente (foi de propósito).
func _alvo_na_frente_para_ataque() -> void:
	var jog: Ent = game.jog
	var melhor: Ent = null
	var nota := 1e9
	for e: Ent in _candidatos(RAIO_BUSCA, true):
		var v := e.pos - jog.pos
		if absf(_dir_frente().angle_to(v)) > CONE_MIRA and v.length() > 1.6: continue
		var n := _nota(e)
		if n < nota: nota = n; melhor = e
	if melhor != null: _trocar_alvo(melhor.id, false)

func _eh_neutro_parado(e: Ent) -> bool:
	return e.aux.get("neutro", false) and e.estado in ["ocioso", "vagar"]

func _segurar_ataque(dt: float) -> void:
	_t_reataque -= dt
	if _t_reataque > 0.0: return
	_t_reataque = 0.15
	var jog: Ent = game.jog
	if not jog.vivo or game.trocando: return
	if jog.alvo != -1 and _valido(jog.alvo) != null: return   # ainda batendo
	if dir_mover != Vector2.ZERO: return   # andando com o stick: não puxa de volta para a briga
	_reavaliar()   # larga o que caiu e pega o próximo (neutro parado longe não entra)
	if _alvo != -1: game.cmd("atacar", [_alvo, false])

func _trocar_alvo(id: int, trava: bool) -> void:
	if id == _alvo and trava == travado: return
	_alvo = id
	travado = trava and id != -1
	alvo_mudou.emit(_alvo, travado)
	queue_redraw()

func _valido(id: int) -> Ent:
	if id == -1: return null
	var e: Ent = game.sim.ents.get(id)
	if e == null or not e.vivo or not e.alvejavel or e.invisivel or not game.jog.eh_inimigo_de(e) or not game.views.has(id): return null
	return e

func _dir_frente() -> Vector2:
	if dir_mira != Vector2.ZERO: return dir_mira
	if dir_mover != Vector2.ZERO: return dir_mover
	var f: Vector2 = game.jog.facing
	return f.normalized() if f.length() > 0.01 else _ultima_dir

## Stick em tela -> direção no mundo (a câmera isométrica gira 45° e achata 2:1).
func _tela_p_mundo(s: Vector2) -> Vector2:
	if s.length() < 0.05: return Vector2.ZERO
	var w := Iso.to_world(s)   # linear: a projeção na tela fica paralela ao stick
	return w.normalized() if w.length() > 0.0001 else Vector2.ZERO

# =================================================================== interação pelo que está na frente
func _item_na_frente() -> int:
	var jog: Ent = game.jog
	var melhor := -1
	var md := RAIO_INTERAGIR
	for id in game.itens_chao.keys():
		var n = game.itens_chao[id]
		var p := Iso.to_world(n.position)
		var d := p.distance_to(jog.pos)
		if d < 1.2 or (d < md and absf(_dir_frente().angle_to(p - jog.pos)) < CONE_MIRA):
			if d < md: md = d; melhor = id
	return melhor

func _interativo_na_frente() -> int:
	var jog: Ent = game.jog
	var melhor := -1
	var nota := 1e9
	for e: Ent in game.sim.ents.values():
		if not e.vivo or not e.tipo in ["npc", "objeto"] or not game.views.has(e.id) and not game.objs.has(e.id): continue
		if e.tipo == "objeto" and jog.eh_inimigo_de(e): continue
		var v := e.pos - jog.pos
		var d := v.length() - e.raio
		if d > RAIO_INTERAGIR: continue
		var ang := absf(_dir_frente().angle_to(v)) if v.length() > 0.01 else 0.0
		if ang > CONE_MIRA and d > 1.0: continue
		var n := d + ang
		if n < nota: nota = n; melhor = e.id
	return melhor

# =================================================================== marcador no chão
func _process(dt: float) -> void:
	_t += dt
	if ativo and _alvo != -1 and _valido(_alvo) == null: _trocar_alvo(-1, false)
	if ativo: queue_redraw()

## Retícula fina no chão do alvo (dois arcos que giram, mais quentes quando travado) e uma seta discreta da mira.
func _draw() -> void:
	if not ativo or game == null or game.jog == null: return
	var e := _valido(_alvo)
	if e != null:
		var c := Iso.to_screen(e.pos)
		var r := Iso.elipse(maxf(e.raio, 0.35) * e.escala + 0.35)
		var cor := COR_TRAVA if travado else COR_SOFT
		var gira := _t * (2.2 if travado else 1.1)
		for k in 2:
			var a0 := gira + PI * k
			var pts := PackedVector2Array()
			for i in 15:
				var a := a0 + (PI * 0.62) * i / 14.0
				pts.append(c + Vector2(cos(a) * r.x, sin(a) * r.y))
			draw_polyline(pts, Color(0, 0, 0, cor.a * 0.6), 3.0, true)
			draw_polyline(pts, cor, 1.4, true)
		if travado:   # quatro dentes nos pontos cardeais
			for i in 4:
				var a := PI * 0.5 * i + PI * 0.25
				var p0 := c + Vector2(cos(a) * r.x * 1.18, sin(a) * r.y * 1.18)
				var p1 := c + Vector2(cos(a) * r.x * 1.36, sin(a) * r.y * 1.36)
				draw_line(p0, p1, cor, 1.6, true)
	if dir_mira != Vector2.ZERO:
		var o := Iso.to_screen(game.jog.pos)
		var t := Iso.to_screen(game.jog.pos + dir_mira * 1.6) - o
		var ponta := o + t
		var lado := t.normalized().orthogonal() * 5.0
		var cm := Color(1.0, 0.85, 0.6, 0.45)
		draw_line(o + t * 0.55, ponta, cm, 1.2, true)
		draw_polyline(PackedVector2Array([ponta - t.normalized() * 7.0 + lado, ponta, ponta - t.normalized() * 7.0 - lado]), cm, 1.4, true)

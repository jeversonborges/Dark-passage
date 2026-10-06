class_name WorldSim
extends RefCounted
## Servidor autoritativo do mundo. Um mapa por vez (prévia solo); no multiplayer vira o processo do servidor.
## O cliente só manda comandos (cmd_*, em Jogador) e desenha os eventos que saem do sinal `evento`.

signal evento(tipo: String, d: Dictionary)

const TICK := 1.0 / 30.0
const PX := 2.0 / 45.25     # px da resolução base (640x360) -> tiles

var mapa := {}
var mapa_id := ""
var w := 0
var h := 0
var bloq := PackedByteArray()      # 0 livre, 1 parede, 2 porta fechada
var zona_idx := PackedByteArray()
var zona_ids: Array = []
var astar := AStarGrid2D.new()
var ents := {}
static var _prox := 1             # ids únicos entre todos os mapas (no servidor o jogador passa de um mapa para outro)
var rng := RandomNumberGenerator.new()
var tempo := 0.0
var projeteis: Array = []
var areas: Array = []
var telegrafos: Array = []
var chao := {}
var spawns: Array = []
var jogador_id := -1
var chefe: ChefeCtl = null
var dia := 0                        # para missões diárias (r01, r02)
var agenda: Array = []
var alvos_ia: Array = []            # jogador + invocações (recalculado a cada passo)              # [tempo, Callable]: golpes atrasados, fim de buff etc.

func atrasar(seg: float, f: Callable) -> void:
	agenda.append([tempo + seg, f])

func _init(semente: int = 0) -> void:
	if semente != 0: rng.seed = semente
	else: rng.randomize()

func novo_id() -> int:
	_prox += 1
	return _prox

func emitir(t: String, d: Dictionary = {}) -> void:
	evento.emit(t, d)

## Evento que só interessa a um jogador (mochila, avisos, diálogos...). No solo é igual a emitir;
## no servidor de rede o "_para" diz para qual conexão mandar.
func emitir_a(e: Ent, t: String, d: Dictionary = {}) -> void:
	if e != null: d["_para"] = e.id
	evento.emit(t, d)

func jogador() -> Ent:
	return ents.get(jogador_id)

## Todos os jogadores neste mapa (no solo é um só).
func jogadores() -> Array:
	var out: Array = []
	for e: Ent in ents.values():
		if e.tipo == "jogador": out.append(e)
	return out

## Jogador vivo mais perto de p (ou null).
func jogador_perto(p: Vector2, raio: float = 1e9) -> Ent:
	var melhor: Ent = null
	var md := raio
	for e: Ent in jogadores():
		if not e.vivo: continue
		var d := e.pos.distance_to(p)
		if d < md: md = d; melhor = e
	return melhor

## Servidor: põe um jogador que veio de outro mapa (ou acabou de entrar no jogo) neste mapa já carregado.
func adicionar_jogador(e: Ent, pos: Vector2) -> void:
	ents[e.id] = e
	e.pos = celula_livre_perto(pos)
	e.caminho.clear(); e.acao = {}; e.alvo = -1; e.deslocando = {}; e.interagindo = {}
	e.aux.erase("interagir"); e.aux.erase("pegar"); e.aux.erase("dialogo"); e.aux.erase("servico")
	e.zona = ""
	emitir("surgiu", {"id": e.id})
	Jogador._checar_zona(self, e)

## Servidor: tira o jogador deste mapa (trocou de mapa ou desconectou). Monstros esquecem dele.
func remover_jogador(e: Ent) -> void:
	if not ents.has(e.id): return
	for o: Ent in ents.values():
		o.ameaca.erase(e.id)
		if o.alvo == e.id: o.alvo = -1
	for o: Ent in ents.values().duplicate():
		if o.tipo == "invocacao" and o.dono == e.id: remover(o.id)
	remover(e.id)

## Cliente de rede: só a geometria do mapa (grade, zonas, caminhos). As entidades chegam do servidor.
func carregar_geometria(id: String) -> void:
	ents.clear(); chao.clear(); spawns.clear(); agenda.clear()
	chefe = null
	_ler_grade(id)

# =================================================================== mapa
func carregar_mapa(id: String) -> void:
	# limpa tudo menos o jogador
	var jog := jogador()
	for k in ents.keys():
		if k != jogador_id: emitir("sumiu", {"id": k})
	ents.clear(); agenda.clear(); projeteis.clear(); areas.clear(); telegrafos.clear(); chao.clear(); spawns.clear()
	chefe = null
	_ler_grade(id)
	if jog != null: ents[jogador_id] = jog
	# NPCs, objetos, baús, spawns, chefe
	for n in mapa.get("npcs", []): _criar_npc(n)
	for o in mapa.get("objetos", []): _criar_objeto(o)
	if mapa.get("id", "") == "area_inicial": _ajustar_spawns_novato()
	for s in mapa.get("spawns", []): _criar_spawn(s)
	if mapa.has("chefe"): chefe = ChefeCtl.new(self, mapa["chefe"])
	emitir("mapa", {"id": id})

func _ler_grade(id: String) -> void:
	mapa = Defs.ler("res://data/mapas/%s.json" % id)
	mapa_id = id
	w = int(mapa["w"]); h = int(mapa["h"])
	bloq = PackedByteArray(); bloq.resize(w * h)
	zona_idx = PackedByteArray(); zona_idx.resize(w * h)
	zona_ids = mapa.get("zonas", [])
	var linhas: Array = mapa["grade"]
	var zl: Array = mapa.get("zona_grade", [])
	for y in h:
		var ln: String = linhas[y]
		for x in w:
			bloq[y * w + x] = 1 if ln[x] == "#" else 0
			if zl.size() > y: zona_idx[y * w + x] = zl[y].unicode_at(x) - 65 if zl[y][x] != "." else 255
	astar = AStarGrid2D.new()
	astar.region = Rect2i(0, 0, w, h)
	astar.cell_size = Vector2(1, 1)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	astar.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	astar.update()
	for y in h:
		for x in w:
			if bloq[y * w + x] != 0: astar.set_point_solid(Vector2i(x, y), true)

func dentro(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < w and c.y < h

func andavel(p: Vector2) -> bool:
	var c := Vector2i(floori(p.x), floori(p.y))
	return dentro(c) and bloq[c.y * w + c.x] == 0

func zona_em(p: Vector2) -> String:
	var c := Vector2i(floori(p.x), floori(p.y))
	if not dentro(c): return ""
	var i := zona_idx[c.y * w + c.x]
	return zona_ids[i]["id"] if i < zona_ids.size() else ""

## Radiação do Amargo no tile (0 ar limpo .. 9 tempestade da borda).
func amargo_em(p: Vector2) -> int:
	var am: Array = mapa.get("amargo", [])
	var c := Vector2i(floori(p.x), floori(p.y))
	if not dentro(c) or am.size() <= c.y: return 0
	var ln: String = am[c.y]
	return int(ln[c.x]) if c.x < ln.length() else 0

## Bênção da Vela: nos primeiros níveis os monstros comuns batem menos (curva de aprendizado de uma pessoa, não de um bot).
static func fator_novato(j: Ent) -> float:
	return [0.55, 0.55, 0.65, 0.75, 0.88][clampi(j.nivel, 0, 4)] if j.nivel < 5 else 1.0

## Postura por zona: só vale para spawns antigos sem `temperamento` (o mapa v0.4 traz o temperamento de cada grupo).
const ZONAS_AGRESSIVAS := ["vala_comum", "abatedouro_carnica"]

## Respiro na saída das áreas seguras: grupos fora dos spots a menos de 10 tiles de uma área segura são empurrados para fora,
## e os de nível 1 fora dos spots andam sozinhos. Corvos de nível baixo têm aggro curto.
## Postura: `temperamento` do mapa (neutro | territorial | agressivo); territorial = neutro que ataca quem entra no território.
func _ajustar_spawns_novato() -> void:
	var celulas: Array = []
	var tem_segura := false
	for zz in zona_ids:
		if zz.get("seguro", false): tem_segura = true
	if tem_segura:
		for y in range(0, h, 2):
			for x in range(0, w, 2):
				if zona_segura(Vector2(x + 0.5, y + 0.5)): celulas.append(Vector2(x + 0.5, y + 0.5))
	var lista: Array = []
	for sp0 in mapa.get("spawns", []):
		var sp: Dictionary = sp0.duplicate()
		lista.append(sp)
		var de_spot: bool = str(sp.get("spot", "")) != ""
		if not de_spot and not celulas.is_empty():
			var p := Vector2(sp["pos"][0], sp["pos"][1])
			var perto := Vector2.ZERO; var dmin := 1e9
			for c in celulas:
				var d := p.distance_to(c)
				if d < dmin: dmin = d; perto = c
			if dmin < 10.0:
				var dir := (p - perto).normalized() if p != perto else Vector2(1, 0)
				var novo := celula_livre_perto(p + dir * (10.0 - dmin))
				sp["pos"] = [novo.x, novo.y]
		if not de_spot:
			if int(sp.get("nivel", 1) if sp.get("nivel") != null else 1) <= 1: sp["qtd"] = 1
			if sp["mob"] == "corvo_de_cinza" and int(sp.get("qtd", 1)) > 2: sp["qtd"] = 2
		var temp: String = str(sp.get("temperamento", ""))
		if temp == "":
			# estilo WoW (Jefin): a maioria é neutra, só ataca se apanhar; agressivos só onde a história pede
			temp = "agressivo" if zona_em(Vector2(sp["pos"][0], sp["pos"][1])) in ZONAS_AGRESSIVAS else "neutro"
		sp["postura"] = "agressivo" if temp == "agressivo" else "neutro"
		if temp == "territorial": sp["territorio"] = float(sp.get("raio_territorio", 4.0)) + float(sp.get("raio", 1.5))
		if not de_spot: sp["qtd"] = mini(int(sp.get("qtd", 1)), 3 if temp == "agressivo" else 2)
	mapa["spawns"] = lista

## Spot de farm em que o ponto está (id ou ""). Usa os spots do mapa (centro e raio).
func spot_em(p: Vector2) -> String:
	for sp in mapa.get("spots", []):
		if p.distance_to(Vector2(sp["pos"][0], sp["pos"][1])) <= float(sp.get("raio", 8)) + 1.0: return sp["id"]
	return ""

func zona_segura(p: Vector2) -> bool:
	var z := zona_em(p)
	for zz in zona_ids:
		if zz["id"] == z: return zz.get("seguro", false)
	return false

func definir_bloqueio(celulas: Array, valor: int) -> void:
	for c in celulas:
		var v := Vector2i(int(c[0]), int(c[1]))
		if not dentro(v): continue
		bloq[v.y * w + v.x] = valor
		astar.set_point_solid(v, valor != 0)

func celula_livre_perto(p: Vector2, raio: float = 3.0) -> Vector2:
	if andavel(p): return p
	for r in range(1, int(raio * 2) + 2):
		for i in 16:
			var a := TAU * i / 16.0
			var q := p + Vector2(cos(a), sin(a)) * r * 0.5
			if andavel(q): return q
	return p

func caminho(de: Vector2, para: Vector2) -> Array:
	var a := Vector2i(floori(de.x), floori(de.y))
	var b := Vector2i(floori(para.x), floori(para.y))
	if not dentro(a) or not dentro(b): return []
	if astar.is_point_solid(b):
		var q := celula_livre_perto(para, 2.0)
		b = Vector2i(floori(q.x), floori(q.y))
		if astar.is_point_solid(b): return []
	var solid_a := astar.is_point_solid(a)
	if solid_a: astar.set_point_solid(a, false)
	var pts := astar.get_id_path(a, b)
	if solid_a: astar.set_point_solid(a, true)
	var out: Array = []
	for i in range(1, pts.size()):
		out.append(Vector2(pts[i]) + Vector2(0.5, 0.5))
	if out.size() > 0 and b == Vector2i(floori(para.x), floori(para.y)):
		out[out.size() - 1] = para
	return out

## Linha de visão no grid (para aggro e para se esconder atrás de pilares).
func visao(a: Vector2, b: Vector2) -> bool:
	var d := b - a
	var n := int(d.length() * 2.0) + 1
	for i in range(1, n):
		var p := a + d * (float(i) / n)
		var c := Vector2i(floori(p.x), floori(p.y))
		if dentro(c) and bloq[c.y * w + c.x] == 1: return false
	return true

# =================================================================== criação
func _ent_base(tipo: String, kind: String, pos: Vector2) -> Ent:
	var e := Ent.new()
	e.id = novo_id(); e.tipo = tipo; e.kind = kind; e.pos = pos; e.casa = pos
	ents[e.id] = e
	return e

func _criar_npc(n: Dictionary) -> void:
	var d: Dictionary = Defs.NPCS.get(n["id"], {})
	var e := _ent_base("npc", n["id"], Vector2(n["pos"][0], n["pos"][1]))
	e.nome = d.get("nome", n["id"]); e.aux["titulo"] = d.get("titulo", "")
	e.faccao = d.get("faccao", "")
	e.facing = Vector2(n.get("dir", [1, 0])[0], n.get("dir", [1, 0])[1])
	e.alvejavel = false; e.raio = 0.4
	e.aux["visual"] = d.get("classe_visual", "humano")
	emitir("surgiu", {"id": e.id})

func _criar_objeto(o: Dictionary) -> void:
	var e := _ent_base("objeto", o["kind"], Vector2(o["pos"][0], o["pos"][1]))
	e.alvejavel = false; e.raio = 0.5
	e.aux = o.duplicate(true)
	match o["kind"]:
		"bau":
			var t: String = o.get("bau", "caixote_podre")
			e.nome = {"caixote_podre": "Caixote Podre", "bau_de_ferro": "Baú de Ferro", "relicario_da_trombeta": "Relicário da Trombeta"}.get(t, "Baú")
			if o.has("hist"): e.nome = Defs.BAUS_HIST.get(o["hist"], {}).get("nome", e.nome)
			e.aux["aberto"] = false
		"interativo":
			var d: Dictionary = Defs.OBJETOS.get(o["obj"], {})
			e.nome = d.get("nome", o["obj"])
		"portal":
			e.nome = o.get("nome", "Passagem")
		"pilha_de_mortos", "corista":
			pass
	emitir("surgiu", {"id": e.id})

func _criar_spawn(s: Dictionary) -> void:
	var g := {"mob": s["mob"], "pos": Vector2(s["pos"][0], s["pos"][1]), "raio": float(s.get("raio", 2.0)),
		"qtd": int(s.get("qtd", 1)), "ents": [], "timers": [], "nivel": s.get("nivel"), "faccao_so": s.get("so_para", ""),
		"patrulha": s.get("patrulha", []), "fila": s.get("formacao", "") == "fila", "postura": s.get("postura", "agressivo"),
		"spot": s.get("spot", ""), "respawn_s": float(s.get("respawn_s", 0)), "territorio": float(s.get("territorio", 0))}
	spawns.append(g)
	var idx := spawns.size() - 1
	for i in g["qtd"]:
		spawn_mob(idx)

func spawn_mob(idx: int) -> Ent:
	var g: Dictionary = spawns[idx]
	var p: Vector2 = g["pos"] + Vector2(rng.randf_range(-1, 1), rng.randf_range(-1, 1)) * g["raio"]
	p = celula_livre_perto(p)
	var m: Dictionary = Defs.MOBS.get(g["mob"], {})
	var niv: Array = m.get("niveis", [1, 1])
	var nivel: int = int(g["nivel"]) if g["nivel"] != null else rng.randi_range(int(niv[0]), int(niv[1]))
	var e := criar_mob(g["mob"], p, nivel)
	e.spawn_ref = idx
	if g.get("postura", "agressivo") == "neutro": e.aux["neutro"] = true
	else: e.raio_aggro *= 0.75
	if float(g.get("respawn_s", 0)) > 0: e.renasce_s = float(g["respawn_s"])
	if str(g.get("spot", "")) != "": e.aux["spot"] = g["spot"]
	if float(g.get("territorio", 0)) > 0: e.aux["territorio"] = [g["pos"].x, g["pos"].y, float(g["territorio"])]
	# matilha de 3+ cães tem um alfa: maior, mais vida, uiva para chamar os outros
	if g["mob"] == "cao_de_vala" and int(g["qtd"]) >= 3:
		var tem_alfa := false
		for oid in g["ents"]:
			var o: Ent = ents.get(oid)
			if o != null and o.vivo and o.aux.get("alfa", false): tem_alfa = true
		if not tem_alfa:
			e.aux["alfa"] = true
			e.nome = "Cão de Vala Alfa"
			e.hp_max *= 1.6; e.hp = e.hp_max
			e.raio = 0.5
			emitir("visual", {"id": e.id, "kind": "cao_de_vala_alfa"})
	if g["patrulha"].size() > 0 or g["fila"]:
		var pts: Array = []
		for q in g["patrulha"]: pts.append(Vector2(q[0], q[1]))
		if pts.is_empty():   # fila de Não-Julgados: vai e volta em linha reta
			pts = [g["pos"] + Vector2(-5, 0), g["pos"] + Vector2(5, 0)]
		e.aux["patrulha"] = pts
	g["ents"].append(e.id)
	return e

func criar_mob(kind: String, p: Vector2, nivel: int) -> Ent:
	var m: Dictionary = Defs.MOBS.get(kind, {})
	var e := _ent_base("monstro", kind, p)
	e.nome = Defs.MON_TXT.get(kind, {}).get("nome", m.get("nome", kind))
	Regras.montar_mob(e, m, nivel)
	var ia_p: Dictionary = Defs.MOBS_BASE["ia_padrao"].duplicate()
	ia_p.merge(m.get("ia", {}), true)
	e.ia = ia_p
	e.raio_aggro = float(ia_p.get("raio_aggro", 6))
	e.raio_vagar = float(ia_p.get("raio_vagar", 3))
	e.raio_coleira = float(ia_p.get("raio_coleira", 14))
	e.renasce_s = float(m.get("renascimento_s", ia_p.get("renascimento_s", 25)))
	e.raio = 0.3 if e.arquetipo == "rasteiro" else (0.55 if e.arquetipo in ["bruto", "elite"] else 0.4)
	if e.arquetipo in ["elite", "raro"]: e.escala = 1.25
	if kind == "bau_faminto":
		pass
	e.facing = Vector2(rng.randf_range(-1, 1), rng.randf_range(-1, 1)).normalized()
	if ia_p.get("padrao", "") == "emboscada": e.invisivel = true
	emitir("surgiu", {"id": e.id})
	return e

func remover(id: int) -> void:
	if ents.erase(id): emitir("sumiu", {"id": id})

# =================================================================== passo
func passo(dt: float) -> void:
	tempo += dt
	if agenda.size() > 0:
		for a in agenda.duplicate():
			if tempo >= a[0]:
				agenda.erase(a); (a[1] as Callable).call()
	var lista := ents.values()
	alvos_ia.clear()
	for e: Ent in lista:
		if e.tipo == "jogador" or e.tipo == "invocacao": alvos_ia.append(e)
	var jps: Array = []
	for e: Ent in alvos_ia:
		if e.tipo == "jogador": jps.append(e.pos)
	for e: Ent in lista:
		if not ents.has(e.id): continue
		if e.tipo == "npc": continue
		# monstros longe e em repouso dormem (o mapa tem 160x160; só a vizinhança dos jogadores precisa pensar)
		if e.tipo == "monstro" and e.vivo and (e.estado == "ocioso" or e.estado == "vagar") and e.status.is_empty() and e.deslocando.is_empty():
			var longe := true
			for jp: Vector2 in jps:
				if e.pos.distance_squared_to(jp) <= 900.0: longe = false; break
			if longe: continue
		_passo_ent(e, dt)
	_passo_projeteis(dt)
	_passo_telegrafos(dt)
	_passo_areas(dt)
	_passo_chao(dt)
	_passo_spawns(dt)
	if chefe != null: chefe.passo(dt)

func _passo_ent(e: Ent, dt: float) -> void:
	if not e.vivo:
		e.morto_t += dt
		if e.tipo == "jogador":
			e.renascer_t -= dt
			if e.renascer_t <= 0.0: Jogador.renascer(self, e)
		elif e.tipo in ["monstro", "invocacao"] and e.morto_t > 6.0:
			remover(e.id)
		return
	if e.hitstop > 0.0:
		e.hitstop -= dt
		return
	e.em_combate_t += dt
	if e.imune_t > 0.0: e.imune_t -= dt
	if e.invuln_t > 0.0: e.invuln_t -= dt
	if e.escudo_t > 0.0:
		e.escudo_t -= dt
		if e.escudo_t <= 0.0: e.escudo = 0.0
	_passo_status(e, dt)
	if not e.vivo: return
	_passo_postura(e, dt)
	for k in e.cds.keys():
		e.cds[k] -= dt
		if e.cds[k] <= 0.0: e.cds.erase(k)
	e.cd_basico -= dt
	if e.dura_t > 0.0:
		e.dura_t -= dt
		if e.dura_t <= 0.0:
			matar(e, null); return
	if not e.deslocando.is_empty():
		_passo_deslocamento(e, dt)
	elif e.empurrao_t > 0.0:
		var step := e.empurrao * (dt / 0.12)
		e.empurrao_t -= dt
		var np := e.pos + step
		if andavel(np) or e.tipo == "chefe": e.pos = np
	if not e.acao.is_empty():
		_passo_acao(e, dt)
	match e.tipo:
		"jogador": Jogador.passo(self, e, dt)
		"monstro": IA.passo(self, e, dt)
		"invocacao": IA.passo_invocacao(self, e, dt)
		"chefe": pass   # o ChefeCtl move e decide

# ------------------------------------------------------------------- movimento
func mover_ao_longo(e: Ent, dt: float, vel_mult: float = 1.0) -> bool:
	if e.caminho.is_empty(): return false
	if e.tem("enraizado") or e.tem("atordoado") or e.tem("derrubado"): return true
	var v := e.vel * vel_mult
	if e.tem("lento"): v *= 1.0 + float(Defs.EFEITOS["status"]["lento"]["velocidade_mov"])
	var resta := v * dt
	while resta > 0.0 and not e.caminho.is_empty():
		var alvo: Vector2 = e.caminho[0]
		var d := alvo - e.pos
		var dist := d.length()
		if dist <= resta:
			e.pos = alvo; resta -= dist; e.caminho.pop_front()
		else:
			e.pos += d / dist * resta; resta = 0.0
		if dist > 0.01: e.facing = d.normalized()
	return not e.caminho.is_empty()

func ir_para(e: Ent, p: Vector2, voa: bool = false) -> void:
	if voa:
		e.caminho = [p]
	elif e.pos.distance_to(p) < 1.6 and visao(e.pos, p) and andavel(p):
		e.caminho = [p]
	else:
		e.caminho = caminho(e.pos, p)

func empurrar(e: Ent, de: Vector2, px: float) -> void:
	if px <= 0.0 or e.tipo in ["npc", "objeto"]: return
	var res: float = Defs.SENS["empurrao"]["resistencia_por_arquetipo"].get("chefe" if e.tipo == "chefe" else e.arquetipo, 0.2)
	if e.tipo == "jogador": res = 0.0
	if e.tipo == "chefe" and e.quebrado_t <= 0.0: return
	var dist := px * (1.0 - res) * PX
	if dist <= 0.01: return
	var dir := (e.pos - de).normalized()
	if dir == Vector2.ZERO: dir = -e.facing
	e.empurrao = dir * dist; e.empurrao_t = 0.12

func deslocar(e: Ent, para: Vector2, dur: float, extra: Dictionary = {}) -> void:
	# traça até onde dá para ir sem atravessar parede (a menos que "atravessa")
	var de := e.pos
	var fim := de
	var n := int(de.distance_to(para) * 4.0) + 1
	for i in range(1, n + 1):
		var q := de.lerp(para, float(i) / n)
		if not andavel(q) and not extra.get("atravessa", false): break
		fim = q
	if extra.get("atravessa", false) and not andavel(fim): fim = celula_livre_perto(fim)
	e.deslocando = {"de": de, "para": fim, "t": 0.0, "dur": maxf(dur, 0.05)}
	e.deslocando.merge(extra)
	e.caminho.clear()
	if fim != de: e.facing = (fim - de).normalized()
	emitir("desloca", {"id": e.id, "de": de, "para": fim, "dur": dur, "tipo": extra.get("tipo", ""), "anim": extra.get("anim", "")})

func _passo_deslocamento(e: Ent, dt: float) -> void:
	var d := e.deslocando
	d["t"] += dt
	var k := clampf(d["t"] / d["dur"], 0.0, 1.0)
	e.pos = (d["de"] as Vector2).lerp(d["para"], k)
	if d.has("golpeia"):
		for o in inimigos_de(e, e.pos, 0.9):
			if o.id in d.get("ja", []): continue
			if not d.has("ja"): d["ja"] = []
			d["ja"].append(o.id)
			aplicar_golpe(e, o, d["golpeia"])
	if k >= 1.0:
		var fim := d
		e.deslocando = {}
		if fim.has("ao_fim"): (fim["ao_fim"] as Callable).call()

# =================================================================== consultas
func ents_em(p: Vector2, r: float) -> Array:
	var out: Array = []
	for e in ents.values():
		if e.vivo and e.pos.distance_to(p) <= r + e.raio: out.append(e)
	return out

func inimigos_de(atk: Ent, p: Vector2, r: float) -> Array:
	var out: Array = []
	for e in ents.values():
		if e.vivo and e.alvejavel and not e.invisivel and atk.eh_inimigo_de(e) and e.pos.distance_to(p) <= r + e.raio:
			out.append(e)
	return out

func aliados_de(atk: Ent, p: Vector2, r: float) -> Array:
	var out: Array = []
	for e in ents.values():
		if e.vivo and e.lado() == atk.lado() and e.tipo != "objeto" and e.pos.distance_to(p) <= r + e.raio:
			out.append(e)
	return out

func valido(id: int) -> Ent:
	var e: Ent = ents.get(id)
	return e if e != null and e.vivo else null

# =================================================================== ações (golpes com preparo)
## Começa um ataque/skill. a: {id, preparo, rec, alvo, ponto, dir, def, impacto: Callable, anim, conj}
func iniciar_acao(e: Ent, a: Dictionary) -> void:
	a["t"] = 0.0
	a["fase"] = "preparo"
	if not a.has("rec"): a["rec"] = 0.3
	var d: Dictionary = a.get("def", {})
	if a.has("alvo") and valido(a["alvo"]) != null:
		var al: Ent = ents[a["alvo"]]
		if al.pos != e.pos: e.facing = (al.pos - e.pos).normalized()
	elif a.has("ponto") and a["ponto"] != e.pos:
		e.facing = (a["ponto"] - e.pos).normalized()
	if not a.has("dir"): a["dir"] = e.facing
	e.caminho.clear()
	e.acao = a
	if d.has("telegrafo"):
		a["tele"] = criar_telegrafo(e, d, a)
	var anim_dur: float = a["preparo"] + a["rec"]
	emitir("ataque", {"id": e.id, "alvo": a.get("alvo", -1), "dir": e.facing, "preparo": a["preparo"], "dur": anim_dur,
		"conj": a.get("conj", false), "nome": a.get("nome", ""), "skill": a.get("skill", ""), "anim": a.get("anim", "")})

func cancelar_acao(e: Ent, motivo: String = "") -> void:
	if e.acao.is_empty(): return
	if e.acao.has("tele"): remover_telegrafo(e.acao["tele"])
	e.acao = {}
	emitir("acao_cancelada", {"id": e.id, "motivo": motivo})

func _passo_acao(e: Ent, dt: float) -> void:
	var a := e.acao
	a["t"] += dt * (1.0 + (0.25 if e.aux.has("enrage") else 0.0))
	if a["fase"] == "preparo":
		if a.has("segue") and valido(a["alvo"]) != null:
			e.facing = (ents[a["alvo"]].pos - e.pos).normalized()
		if a["t"] >= a["preparo"]:
			a["fase"] = "rec"
			a["t"] = 0.0
			if a.has("impacto"): (a["impacto"] as Callable).call()
			if a.has("tele"): disparar_telegrafo(a["tele"])
			if e.acao != a: return
	if a["fase"] == "rec" and a["t"] >= a["rec"]:
		if e.acao == a: e.acao = {}

# =================================================================== telegrafos
func criar_telegrafo(e: Ent, d: Dictionary, a: Dictionary) -> int:
	var t: Dictionary = d["telegrafo"].duplicate()
	var tid := novo_id()
	var origem := e.pos
	var dir: Vector2 = a.get("dir", e.facing)
	var alvo_id: int = a.get("alvo", -1)
	if t["forma"] in ["circulo"] and a.has("ponto_tele"):
		origem = a["ponto_tele"]
	var tg := {"id": tid, "dono": e.id, "forma": t["forma"], "origem": origem, "dir": dir, "p": t, "dur": a["preparo"],
		"t": 0.0, "def": d, "op": a.get("op", {}), "segue": -1, "ativo": false}
	if t["forma"] == "circulo_segue_jogador":
		tg["segue"] = alvo_id
		if valido(alvo_id) != null: tg["origem"] = ents[alvo_id].pos
	telegrafos.append(tg)
	emitir("telegrafo", {"id": tid, "forma": t["forma"], "origem": tg["origem"], "dir": dir, "p": t, "dur": tg["dur"],
		"segue": tg["segue"], "dono": e.id})
	return tid

func achar_tele(tid: int) -> Dictionary:
	for t in telegrafos:
		if t["id"] == tid: return t
	return {}

func remover_telegrafo(tid: int) -> void:
	for t in telegrafos:
		if t["id"] == tid:
			telegrafos.erase(t)
			emitir("telegrafo_fim", {"id": tid, "cancelado": true})
			return

func disparar_telegrafo(tid: int) -> void:
	var tg := achar_tele(tid)
	if tg.is_empty(): return
	var dono: Ent = ents.get(tg["dono"])
	if tg["forma"] == "anel":
		tg["ativo"] = true; tg["t"] = 0.0; tg["atingidos"] = []
		emitir("telegrafo_anel", {"id": tid})
		return
	telegrafos.erase(tg)
	emitir("telegrafo_fim", {"id": tid, "impacto": true})
	if dono == null or not dono.vivo: return
	for alvo in alvos_na_forma(dono, tg):
		aplicar_golpe(dono, alvo, tg["op"])
	if tg["op"].has("ao_impacto"): (tg["op"]["ao_impacto"] as Callable).call(tg)

func _passo_telegrafos(dt: float) -> void:
	for tg in telegrafos.duplicate():
		tg["t"] += dt
		if tg["segue"] != -1 and valido(tg["segue"]) != null:
			var trava: float = float(tg["p"].get("trava_ultimos_s", 0.0))
			if tg["t"] < tg["dur"] - trava: tg["origem"] = ents[tg["segue"]].pos
		if tg["ativo"]:
			# anel que cresce a partir do dono
			var p: Dictionary = tg["p"]
			var rf: float = p["raio_final"]
			var r: float = rf * clampf(tg["t"] / 1.1, 0.0, 1.0)
			var dono: Ent = ents.get(tg["dono"])
			if dono == null or not dono.vivo or tg["t"] > 1.2:
				telegrafos.erase(tg); emitir("telegrafo_fim", {"id": tg["id"]}); continue
			for alvo in inimigos_de(dono, tg["origem"], r + 0.5):
				if alvo.id in tg["atingidos"]: continue
				var dd: float = alvo.pos.distance_to(tg["origem"])
				if absf(dd - r) > float(p.get("largura", 0.8)) * 0.5 + alvo.raio: continue
				var ang: float = absf(angle_difference((alvo.pos - tg["origem"]).angle(), (tg["dir"] as Vector2).angle()))
				if ang < deg_to_rad(float(p.get("vao_graus", 45))) * 0.5: continue
				tg["atingidos"].append(alvo.id)
				aplicar_golpe(dono, alvo, tg["op"])

func dentro_forma(tg: Dictionary, p: Vector2, raio_alvo: float) -> bool:
	var o: Vector2 = tg["origem"]
	var t: Dictionary = tg["p"]
	var dir: Vector2 = tg["dir"]
	match tg["forma"]:
		"circulo", "circulo_segue_jogador":
			return p.distance_to(o) <= float(t.get("raio", 1.5)) + raio_alvo
		"cone":
			var d := p - o
			if d.length() > float(t["raio"]) + raio_alvo: return false
			if d.length() < 0.6: return true
			return absf(angle_difference(d.angle(), dir.angle())) <= deg_to_rad(float(t["angulo"])) * 0.5 + 0.1
		"linha":
			var d := p - o
			var al := d.dot(dir)
			if al < -raio_alvo or al > float(t["comprimento"]) + raio_alvo: return false
			return absf(d.dot(dir.orthogonal())) <= float(t.get("largura", 1.0)) * 0.5 + raio_alvo
	return false

func alvos_na_forma(dono: Ent, tg: Dictionary) -> Array:
	var out: Array = []
	for e in ents.values():
		if e.vivo and e.alvejavel and dono.eh_inimigo_de(e) and dentro_forma(tg, e.pos, e.raio):
			out.append(e)
	return out

# =================================================================== projéteis
## op: opções do golpe. p: {vel, alvo (id) ou ponto+dir, alcance, vfx, raio, perfura, ao_atingir}
func lancar(atk: Ent, p: Dictionary, op: Dictionary) -> void:
	var pr := {"id": novo_id(), "de": atk.id, "pos": atk.pos, "vel": float(p.get("vel", 10.0)), "op": op,
		"alvo": p.get("alvo", -1), "dir": p.get("dir", atk.facing), "alcance": float(p.get("alcance", 10.0)),
		"perc": 0.0, "raio": float(p.get("raio", 0.35)), "perfura": p.get("perfura", false), "ja": [],
		"ao_atingir": p.get("ao_atingir")}
	projeteis.append(pr)
	emitir("projetil", {"id": pr["id"], "de": atk.id, "pos": atk.pos, "alvo": pr["alvo"], "dir": pr["dir"],
		"vel": pr["vel"], "alcance": pr["alcance"], "vfx": p.get("vfx", ""), "cor": p.get("cor", ""), "elem": op.get("elemento", atk.elemento)})

func _passo_projeteis(dt: float) -> void:
	for pr in projeteis.duplicate():
		var atk: Ent = ents.get(pr["de"])
		var passo_d: float = pr["vel"] * dt
		var fim := false
		if pr["alvo"] != -1:
			var al := valido(pr["alvo"])
			if al == null or atk == null:
				fim = true
			else:
				var d: Vector2 = al.pos - pr["pos"]
				if d.length() <= passo_d + al.raio:
					aplicar_golpe(atk, al, pr["op"])
					if pr["ao_atingir"] != null: (pr["ao_atingir"] as Callable).call(al)
					fim = true
				else:
					pr["pos"] += d.normalized() * passo_d
		else:
			pr["pos"] += (pr["dir"] as Vector2) * passo_d
			pr["perc"] += passo_d
			if not andavel(pr["pos"]) and not pr["op"].get("voa", false): fim = true
			elif atk != null:
				for o in inimigos_de(atk, pr["pos"], pr["raio"]):
					if o.id in pr["ja"]: continue
					pr["ja"].append(o.id)
					aplicar_golpe(atk, o, pr["op"])
					if pr["ao_atingir"] != null: (pr["ao_atingir"] as Callable).call(o)
					if not pr["perfura"]: fim = true; break
			if pr["perc"] >= pr["alcance"]: fim = true
		if fim:
			projeteis.erase(pr)
			emitir("projetil_fim", {"id": pr["id"], "pos": pr["pos"]})

# =================================================================== áreas no chão (poças, fogo, armadilhas, chuva)
## a: {pos, raio, dur, dono, tick, op (golpe por tick), status, so_inimigos, tipo, vfx, arma_s (armadilha)}
func criar_area(a: Dictionary) -> Dictionary:
	a["id"] = novo_id(); a["t"] = 0.0; a["tick_t"] = 0.0
	areas.append(a)
	emitir("area", {"id": a["id"], "pos": a["pos"], "raio": a["raio"], "dur": a["dur"], "tipo": a.get("tipo", ""), "dono": a.get("dono", -1)})
	return a

func _passo_areas(dt: float) -> void:
	for a in areas.duplicate():
		a["t"] += dt
		if a["t"] >= a["dur"]:
			areas.erase(a); emitir("area_fim", {"id": a["id"]}); continue
		var dono: Ent = ents.get(a.get("dono", -1))
		if a.get("tipo", "") == "armadilha":
			if a["t"] < float(a.get("arma_s", 1.0)) or dono == null: continue
			var pegos := inimigos_de(dono, a["pos"], a["raio"])
			if pegos.size() > 0:
				for o in inimigos_de(dono, a["pos"], a["raio"] + 1.0): aplicar_golpe(dono, o, a["op"])
				areas.erase(a); emitir("area_fim", {"id": a["id"], "disparou": true})
			continue
		a["tick_t"] -= dt
		if a["tick_t"] > 0.0: continue
		a["tick_t"] = float(a.get("tick", 0.5))
		if a.has("cada_tick"): (a["cada_tick"] as Callable).call(a)
		if not a.has("op"): continue
		var alvos: Array
		if dono != null: alvos = inimigos_de(dono, a["pos"], a["raio"])
		else: alvos = ents_em(a["pos"], a["raio"]).filter(func(o): return o.tipo == "jogador")
		for o in alvos:
			if dono == null: aplicar_dano_puro(o, a["op"].get("dano_frac", 0.02) * o.hp_max, a["op"].get("elemento", "fogo"), null)
			else: aplicar_golpe(dono, o, a["op"])

# =================================================================== golpe: dano, postura, efeitos
## Golpe completo de atk em alvo seguindo a ordem de cálculo do design.
func aplicar_golpe(atk: Ent, alvo: Ent, op: Dictionary) -> Dictionary:
	if alvo == null or not alvo.vivo or not alvo.alvejavel: return {}
	if alvo.invuln_t > 0.0 or alvo.aux.get("imune", false):
		emitir("dano", {"id": alvo.id, "de": atk.id, "valor": 0, "estilo": "imune"})
		return {}
	if op.has("cura"):
		curar(alvo, op["cura"], atk); return {}
	var r := Regras.golpe(atk, alvo, op, rng)
	atk.em_combate_t = 0.0; alvo.em_combate_t = 0.0
	if r["errou"]:
		emitir("dano", {"id": alvo.id, "de": atk.id, "valor": 0, "estilo": "errou"})
		return r
	var dano: int = r["dano"]
	if alvo.tipo == "jogador" and atk.tipo == "monstro": dano = maxi(1, roundi(dano * fator_novato(alvo)))
	if alvo.tem("profecia") and alvo.tipo != "chefe":
		var lim := 0.05 if alvo.arquetipo == "elite" else 0.10
		if (alvo.hp - dano) / alvo.hp_max < lim:
			dano = int(alvo.hp) + 1
			emitir("fala", {"id": alvo.id, "texto": "PROFECIA", "cor": "#8a4a9a"})
	var estilo := "normal"
	if r["exc"] and r["crit"]: estilo = "excelente_critico"
	elif r["exc"]: estilo = "excelente"
	elif r["crit"]: estilo = "critico"
	if alvo.tipo == "jogador": estilo = "jogador_recebe"
	var absorvido := 0
	if alvo.escudo > 0.0:
		absorvido = mini(dano, int(alvo.escudo))
		alvo.escudo -= absorvido; dano -= absorvido
		emitir("dano", {"id": alvo.id, "de": atk.id, "valor": absorvido, "estilo": "escudo"})
		if alvo.escudo <= 0.0: emitir("som_evento", {"ev": "escudo_quebra", "pos": alvo.pos})
	alvo.hp -= dano
	var sens: String = op.get("sensacao", "golpe_leve")
	emitir("dano", {"id": alvo.id, "de": atk.id, "valor": dano, "estilo": estilo, "sens": sens, "elem": op.get("elemento", atk.elemento),
		"crit": r["crit"], "exc": r["exc"], "hp": alvo.hp, "hp_max": alvo.hp_max})
	# ameaça
	if alvo.tipo in ["monstro", "chefe"]:
		var mult: float = Defs.FORM["aggro"]["mult_classe"].get(atk.classe, 1.0) * float(atk.aux.get("ameaca_mult", 1.0))
		var dono_id := atk.dono if atk.tipo == "invocacao" and op.get("ameaca_dono", false) else atk.id
		alvo.ameaca[dono_id] = alvo.ameaca.get(dono_id, 0.0) + dano * mult
		if alvo.estado in ["ocioso", "vagar"]: IA.acordar(self, alvo, atk)
	# roubo de vida
	var rv := atk.roubo_vida
	if atk.classe == "demonio" and atk.nivel >= 12 and atk.frac_hp() < 0.3: rv += 0.1   # passiva Banquete
	if atk.classe == "demonio" and atk.frac_hp() < 0.3 and atk.nivel >= 12: rv += 0.1
	if rv > 0.0 and dano > 0: curar(atk, dano * rv, atk, true)
	# postura
	var post: float = float(op.get("postura", atk.postura_arma if atk.tipo == "jogador" else 10.0))
	if alvo.aux.get("agarrando", false): post *= 2.0
	aplicar_postura(alvo, post, atk)
	# recursos do atacante
	if atk.tipo == "jogador": Jogador.ao_acertar(self, atk, alvo, r, op)
	if alvo.tipo == "jogador": Jogador.ao_ser_atingido(self, alvo, atk, dano, r)
	# efeitos
	for s in op.get("efeito", {}):
		var v = op["efeito"][s]
		aplicar_status(alvo, s, v, atk)
	if op.get("empurrao", 0.0) > 0.0: empurrar(alvo, op.get("empurrao_de", atk.pos), op["empurrao"])
	if op.has("puxa_para"):
		var dir: Vector2 = (alvo.pos - atk.pos).normalized()
		if alvo.tipo != "chefe" and alvo.arquetipo != "elite": deslocar(alvo, atk.pos + dir * float(op["puxa_para"]), 0.2, {"tipo": "puxao"})
	if op.has("ao_dano"): (op["ao_dano"] as Callable).call(alvo, dano)
	if alvo.hp <= 0.0:
		matar(alvo, atk)
	return r

func aplicar_dano_puro(alvo: Ent, valor: float, elem: String, atk: Ent, estilo: String = "dano_tempo") -> void:
	if not alvo.vivo or alvo.invuln_t > 0.0: return
	var v := maxi(1, roundi(valor * (1.0 - clampf(float(alvo.res.get(elem, 0.0)), -1.0, 0.75))))
	if alvo.tipo == "jogador" and atk != null and atk.tipo == "monstro": v = maxi(1, roundi(v * fator_novato(alvo)))
	alvo.hp -= v
	alvo.em_combate_t = 0.0
	emitir("dano", {"id": alvo.id, "de": atk.id if atk else -1, "valor": v, "estilo": estilo if alvo.tipo != "jogador" or estilo != "normal" else "jogador_recebe",
		"elem": elem, "hp": alvo.hp, "hp_max": alvo.hp_max})
	if alvo.tipo == "jogador": Jogador.ao_ser_atingido(self, alvo, atk, v, {})
	if alvo.hp <= 0.0: matar(alvo, atk)

func curar(alvo: Ent, valor: float, de: Ent, silencioso: bool = false) -> void:
	if not alvo.vivo: return
	var v := valor
	if alvo.tem("cura_reduzida"): v *= 0.6
	if alvo.tem("veneno"): v *= 0.8
	var antes := alvo.hp
	alvo.hp = minf(alvo.hp_max, alvo.hp + v)
	var ganho := alvo.hp - antes
	if ganho >= 1.0 and not silencioso:
		emitir("cura", {"id": alvo.id, "valor": roundi(ganho)})
	if de != null and de.tipo == "jogador" and de.classe == "anjo" and not silencioso:
		de.rec = minf(de.rec_max, de.rec + ganho / 10.0)

func aplicar_postura(alvo: Ent, v: float, atk: Ent) -> void:
	if alvo.tipo in ["jogador", "npc", "objeto", "invocacao"] or v <= 0.0: return
	alvo.postura_t = 0.0
	if alvo.quebrado_t > 0.0 or alvo.quebra_cd > 0.0: return
	alvo.postura -= v
	# recuo (flinch) de quem não tem super-armadura
	var fl: Dictionary = Defs.EFEITOS["postura"]["flinch"]
	if alvo.arquetipo in fl["recuam"] and alvo.tipo == "monstro":
		emitir("recuo", {"id": alvo.id})
		if v >= float(fl["interrompe_preparo_se_postura_maior_igual"]) and not alvo.acao.is_empty() and alvo.acao["fase"] == "preparo":
			cancelar_acao(alvo, "recuo")
	if alvo.postura <= 0.0:
		var arq := "chefe" if alvo.tipo == "chefe" else alvo.arquetipo
		alvo.quebrado_t = float(Defs.EFEITOS["postura"]["quebrado_duracao"].get(arq, 0.8))
		alvo.postura = 0.0
		alvo.quebra_cd = float(Defs.EFEITOS["postura"]["recarga_apos_quebrar_s"].get(arq, 0.0))
		var interrompeu := not alvo.acao.is_empty()
		cancelar_acao(alvo, "quebrado")
		emitir("dano", {"id": alvo.id, "valor": 0, "estilo": "postura_quebrada"})
		emitir("som_evento", {"ev": "postura_quebrada", "pos": alvo.pos})
		if alvo.tipo == "chefe" and chefe != null: chefe.ao_quebrar(interrompeu)

func _passo_postura(e: Ent, dt: float) -> void:
	if e.quebrado_t > 0.0:
		e.quebrado_t -= dt
		if e.quebrado_t <= 0.0: e.postura = e.postura_max
		return
	if e.quebra_cd > 0.0: e.quebra_cd -= dt
	e.postura_t += dt
	if e.postura < e.postura_max and e.postura_t >= 3.0:
		var mult := 2.0 if e.mod("postura_regen") > 0.0 else 1.0
		e.postura = minf(e.postura_max, e.postura + e.postura_max * 0.25 * dt * mult)

# =================================================================== status
const CC := ["atordoado", "derrubado", "enraizado", "cegueira", "silenciado"]

## v: duração (float) ou {duracao, dano_por_s_mult}
func aplicar_status(alvo: Ent, s: String, v, atk: Ent) -> void:
	if not alvo.vivo or alvo.tipo in ["npc", "objeto"]: return
	var dur: float
	var dados := {}
	if typeof(v) == TYPE_DICTIONARY:
		dur = float(v.get("duracao", 3.0)); dados = v.duplicate()
	else:
		dur = float(v)
	if s == "cura_recebida": s = "cura_reduzida"
	if alvo.tipo == "chefe":
		if s in Defs.CHEFES_REGRAS["imune"]:
			emitir("dano", {"id": alvo.id, "valor": 0, "estilo": "imune"}); return
		if s in ["enraizado", "lento"]: dur *= 0.5
	if alvo.aux.get("imune_cc", false) and s in ["derrubado", "atordoado"]: return
	if s in CC:
		var hst: Array = alvo.cc_hist.get(s, [-99.0, 0])
		if tempo - float(hst[0]) > 15.0: hst = [tempo, 0]
		var esc := [1.0, 0.5, 0.25]
		if int(hst[1]) >= 3:
			if tempo - float(hst[0]) < 8.0 + 15.0:
				emitir("dano", {"id": alvo.id, "valor": 0, "estilo": "imune"}); return
			hst = [tempo, 0]
		dur *= esc[mini(int(hst[1]), 2)]
		hst[1] = int(hst[1]) + 1
		alvo.cc_hist[s] = hst
	# resistência do mutante e antídoto
	dur *= 1.0 - clampf(float(alvo.res.get(s, 0.0)), 0.0, 0.9)
	var def: Dictionary = Defs.EFEITOS["status"].get(s, {})
	var atual: Dictionary = alvo.status.get(s, {})
	var novo := {"t": dur, "dados": dados, "de": atk.id if atk != null else -1, "tick": float(def.get("tick_s", 1.0)), "pilhas": 1}
	if def.get("tipo", "") == "dano_tempo":
		var dm: float = float(dados.get("dano_por_s_mult", 0.2))
		novo["dps"] = (atk.dano_medio() if atk != null else 5.0) * dm
		if not atual.is_empty():
			var mx: int = int(def.get("acumula", 1))
			novo["pilhas"] = mini(int(atual.get("pilhas", 1)) + 1, mx)
			novo["tick"] = atual["tick"]
	elif not atual.is_empty():
		novo["t"] = maxf(dur, float(atual["t"]))
	alvo.status[s] = novo
	if s == "provocado" and atk != null: alvo.alvo = atk.id; alvo.ameaca[atk.id] = alvo.ameaca.values().max() * 2.0 + 50.0 if alvo.ameaca.size() > 0 else 100.0
	if s in ["atordoado", "derrubado"] and not alvo.acao.is_empty(): cancelar_acao(alvo, s)
	if s == "derrubado" and atk != null: empurrar(alvo, atk.pos, 8)
	if atual.is_empty(): emitir("status", {"id": alvo.id, "s": s, "on": true, "t": novo["t"]})

func _passo_status(e: Ent, dt: float) -> void:
	for s in e.status.keys():
		var st: Dictionary = e.status[s]
		st["t"] -= dt
		if st.has("dps"):
			st["tick"] -= dt
			if st["tick"] <= 0.0:
				var def: Dictionary = Defs.EFEITOS["status"].get(s, {})
				st["tick"] += float(def.get("tick_s", 1.0))
				var dano: float = float(st["dps"]) * float(def.get("tick_s", 1.0)) * int(st.get("pilhas", 1))
				aplicar_dano_puro(e, dano, def.get("elemento", "fisico"), ents.get(st["de"]))
				if not e.vivo: return
		if st["t"] <= 0.0:
			e.status.erase(s)
			emitir("status", {"id": e.id, "s": s, "on": false})

# =================================================================== morte e loot
func matar(e: Ent, assassino: Ent) -> void:
	if not e.vivo: return
	e.vivo = false; e.hp = 0.0; e.morto_t = 0.0
	cancelar_acao(e)
	e.caminho.clear(); e.status.clear(); e.deslocando = {}
	emitir("morreu", {"id": e.id, "de": assassino.id if assassino else -1, "tipo": e.tipo, "chefe": e.tipo == "chefe"})
	if e.tipo == "jogador":
		Jogador.morreu(self, e)
		return
	var killer := assassino
	if killer != null and killer.tipo == "invocacao": killer = ents.get(killer.dono)
	if e.tipo in ["monstro", "chefe"]:
		var m: Dictionary = Defs.MOBS.get(e.kind, {})
		# ataque ao morrer (porco explode, larva estoura)
		for at in m.get("ataques", []):
			if at.get("ao_morrer", false): IA.explosao_morte(self, e, at)
		if killer != null and killer.tipo == "jogador":
			# em grupo: quem ajudou (bateu, curou no meio da briga, está na arena do chefe) também ganha XP, missão e o próprio saque
			for j: Ent in participantes(e, killer):
				Jogador.abateu(self, j, e)
				Loot.dropar_mob(self, e, j)
		if e.spawn_ref >= 0 and e.spawn_ref < spawns.size():
			var g: Dictionary = spawns[e.spawn_ref]
			g["ents"].erase(e.id)
			g["timers"].append(e.renasce_s)
		if chefe != null: chefe.ao_morrer_ent(e, killer)
	elif e.tipo == "objeto":
		if chefe != null: chefe.ao_morrer_ent(e, killer)
		remover(e.id)

func participantes(morto: Ent, killer: Ent) -> Array:
	var out: Array = [killer]
	for j: Ent in jogadores():
		if j == killer or not j.vivo: continue
		var perto := j.pos.distance_to(morto.pos) < (30.0 if morto.tipo == "chefe" else 16.0)
		if perto and (morto.ameaca.has(j.id) or morto.tipo == "chefe" or j.pos.distance_to(killer.pos) < 10.0):
			out.append(j)
	return out

func _passo_spawns(dt: float) -> void:
	for i in spawns.size():
		var g: Dictionary = spawns[i]
		var ts: Array = g["timers"]
		for k in range(ts.size() - 1, -1, -1):
			ts[k] -= dt
			if ts[k] <= 0.0:
				if float(g.get("so_quando", 0)) == 0: pass
				ts.remove_at(k)
				var p: Vector2 = g["pos"]
				if jogador_perto(p, 7.0) != null:
					ts.append(4.0)   # não nasce na cara do jogador
				elif g["mob"] != "" and Defs.MOBS.has(g["mob"]) and float(Defs.MOBS[g["mob"]].get("renascimento_s", 25)) > 0:
					spawn_mob(i)

func _passo_chao(dt: float) -> void:
	for id in chao.keys():
		var c: Dictionary = chao[id]
		c["t"] += dt
		if c["t"] > float(Defs.DROPS["regras"]["some_do_chao_s"]):
			chao.erase(id); emitir("chao_sumiu", {"id": id})
		elif c["item"]["id"] == "_ouro" and c["t"] > 0.4:
			var jog := jogador_perto(c["pos"], 0.9)
			if jog != null and (c["dono"] == jog.id or c["dono"] == -1 or c["t"] >= float(Defs.DROPS["regras"]["dono_do_drop_s"])):
				Jogador.pegar_chao(self, jog, id)

func soltar_no_chao(item: Dictionary, p: Vector2, dono: int, de: Vector2) -> void:
	var id := novo_id()
	var ang := rng.randf() * TAU
	var alvo := p + Vector2(cos(ang), sin(ang)) * rng.randf_range(0.3, 1.2)
	alvo = celula_livre_perto(alvo, 1.5)
	chao[id] = {"id": id, "item": item, "pos": alvo, "dono": dono, "t": 0.0}
	emitir("chao_novo", {"id": id, "de": de, "pos": alvo, "item": item, "dono": dono})

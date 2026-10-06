extends Node
## Servidor da rede local: contas, personagens por conta e um mundo (WorldSim) por mapa ocupado.
## Roda dentro do jogo de quem hospeda (ou sozinho com `-- servidor=1`). Os clientes só mandam comandos;
## o servidor manda de volta o que mudou nas entidades e os eventos do mapa onde cada um está.

const ARQ := "user://servidor/contas.json"
const MAX_PERSONAGENS := 6
const ITER_HASH := 4000

var rede: Node
var contas := {}            # usuario -> {sal, hash, personagens: [save]}
var sessoes := {}           # peer -> {u, jog: Ent, mapa, idx, cache, saida, chefe}
var por_jog := {}           # id do Ent do jogador -> peer
var mundos := {}            # id do mapa -> WorldSim
var movimentos: Array = []  # [id do jogador, mapa, pos] (portal, vela de retorno)
var acc := 0.0
var t_salvar := 0.0

func _ready() -> void:
	_carregar_contas()

# =================================================================== contas
func _carregar_contas() -> void:
	DirAccess.make_dir_recursive_absolute("user://servidor")
	if not FileAccess.file_exists(ARQ): return
	var f := FileAccess.open(ARQ, FileAccess.READ)
	var d = JSON.parse_string(f.get_as_text())
	if d is Dictionary: contas = d

func _gravar_contas() -> void:
	var tmp := ARQ + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(contas))
	f.close()
	DirAccess.rename_absolute(tmp, ARQ)

## A senha chega já resumida pelo cliente (sha256 de usuário + senha); aqui ela ganha sal e milhares de rodadas.
static func _resumo(sal: String, h: String) -> String:
	var x := sal + h
	for i in ITER_HASH: x = (x + sal).sha256_text()
	return x

static func _usuario_ok(u: String) -> bool:
	if u.length() < 3 or u.length() > 16: return false
	for c in u:
		if not (c in "abcdefghijklmnopqrstuvwxyz0123456789_"): return false
	return true

func _lista(u: String) -> Array:
	var out: Array = []
	for s in contas[u]["personagens"]:
		out.append({"nome": s.get("nome", "?"), "classe": s.get("classe", ""), "nivel": int(s.get("nivel", 1))})
	return out

# =================================================================== mensagens dos clientes
func receber(peer: int, m: Dictionary) -> void:
	var t = m.get("t", "")
	if not t is String: return
	var s: Dictionary = sessoes.get(peer, {})
	match t:
		"cadastro", "login":
			if not s.is_empty() and s.get("u", "") != "": return
			var u := str(m.get("u", "")).strip_edges().to_lower()
			var h := str(m.get("h", ""))
			if not _usuario_ok(u): _erro(peer, "Usuário precisa ter de 3 a 16 letras ou números (sem espaço)."); return
			if h.length() != 64: _erro(peer, "Senha inválida."); return
			if t == "cadastro":
				if contas.has(u): _erro(peer, "Esse usuário já existe. Use Entrar."); return
				var sal := Crypto.new().generate_random_bytes(16).hex_encode()
				contas[u] = {"sal": sal, "hash": _resumo(sal, h), "personagens": [], "criada": Time.get_datetime_string_from_system()}
				_gravar_contas()
			else:
				if not contas.has(u) or _resumo(contas[u]["sal"], h) != contas[u]["hash"]:
					_erro(peer, "Usuário ou senha errados."); return
			for p in sessoes:
				if sessoes[p].get("u", "") == u: _erro(peer, "Essa conta já está no jogo em outro PC."); return
			sessoes[peer] = {"u": u, "jog": null, "mapa": "", "idx": -1, "cache": {}, "saida": [], "chefe": ""}
			rede.enviar(peer, {"t": "conta", "u": u, "personagens": _lista(u), "novo": t == "cadastro"})
		"criar":
			if s.is_empty() or s["jog"] != null: return
			var classe := str(m.get("classe", ""))
			var nome := str(m.get("nome", "")).strip_edges().left(16)
			if not Defs.CLASSES.has(classe): return
			if nome.length() < 2: _erro(peer, "Escolha um nome com pelo menos 2 letras."); return
			var lista: Array = contas[s["u"]]["personagens"]
			if lista.size() >= MAX_PERSONAGENS: _erro(peer, "Cada conta tem até %d personagens." % MAX_PERSONAGENS); return
			var tmp := WorldSim.new(1)
			var e := Jogador.criar(tmp, classe, nome, {})
			var salvo := Jogador.salvar(e, tmp)
			salvo["novo"] = true
			lista.append(salvo)
			_gravar_contas()
			_entrar_mundo(peer, lista.size() - 1)
		"jogar":
			if s.is_empty() or s["jog"] != null: return
			var i = m.get("i", -1)
			if i is int and i >= 0 and i < contas[s["u"]]["personagens"].size(): _entrar_mundo(peer, i)
		"cmd":
			if s.is_empty() or s["jog"] == null: return
			var n = m.get("n", ""); var a = m.get("a", [])
			if n is String and a is Array and mundos.has(s["mapa"]):
				Comandos.executar(mundos[s["mapa"]], s["jog"], n, a)

func _erro(peer: int, msg: String) -> void:
	rede.enviar(peer, {"t": "erro", "msg": msg})

## Conexão caiu ou o jogador saiu: salva e tira o personagem do mundo.
func desconectou(peer: int) -> void:
	if not sessoes.has(peer): return
	var s: Dictionary = sessoes[peer]
	if s["jog"] != null:
		_salvar_jog(peer)
		var sim: WorldSim = mundos.get(s["mapa"])
		if sim != null:
			sim.remover_jogador(s["jog"])
			_liberar_se_vazio(s["mapa"])
		por_jog.erase(s["jog"].id)
	sessoes.erase(peer)
	print("[servidor] saiu: ", s.get("u", "?"))

func _exit_tree() -> void:
	for p in sessoes.keys():
		if sessoes[p]["jog"] != null: _salvar_jog(p)
	_gravar_contas()

# =================================================================== mundos
func _mundo(id: String) -> WorldSim:
	if mundos.has(id): return mundos[id]
	var sim := WorldSim.new(randi())
	sim.carregar_mapa(id)
	sim.evento.connect(_ev.bind(id))
	mundos[id] = sim
	print("[servidor] mapa carregado: ", id)
	return sim

func _liberar_se_vazio(id: String) -> void:
	var sim: WorldSim = mundos.get(id)
	if sim == null or not sim.jogadores().is_empty(): return
	mundos.erase(id)   # o próximo que entrar encontra o mapa como novo (chefes e baús voltam, como no solo)
	print("[servidor] mapa vazio, descarregado: ", id)

static func _spawn(sim: WorldSim, e: Ent) -> Vector2:
	var spf: Dictionary = sim.mapa.get("spawn_por_faccao", {})
	var s: Array = spf.get(e.faccao, sim.mapa.get("spawn", [10, 10]))
	return Vector2(s[0], s[1])

func _entrar_mundo(peer: int, idx: int) -> void:
	var s: Dictionary = sessoes[peer]
	var salvo: Dictionary = contas[s["u"]]["personagens"][idx]
	var novo: bool = salvo.get("novo", false)
	salvo.erase("novo")
	var mapa_id: String = salvo.get("mapa", "area_inicial")
	if not ResourceLoader.exists("res://data/mapas/%s.json" % mapa_id) and not FileAccess.file_exists("res://data/mapas/%s.json" % mapa_id): mapa_id = "area_inicial"
	var sim := _mundo(mapa_id)
	var e := Jogador.criar(sim, salvo["classe"], salvo.get("nome", "Sobrevivente"), {} if novo else salvo)
	var pos := _spawn(sim, e)
	var ps: Array = salvo.get("pos", [])
	if ps.size() == 2: pos = Vector2(ps[0], ps[1])
	s["jog"] = e; s["mapa"] = mapa_id; s["idx"] = idx; s["saida"] = []
	por_jog[e.id] = peer
	sim.adicionar_jogador(e, pos)
	_enviar_mapa(peer, novo)
	print("[servidor] entrou: %s com %s (%s, nível %d)" % [s["u"], e.nome, e.classe, e.nivel])
	for x in OS.get_cmdline_user_args():   # teste: leva o jogador para outro mapa depois de 8 s
		if x.begins_with("teste_mapa="):
			var dest := x.get_slice("=", 1)
			get_tree().create_timer(8.0).timeout.connect(func(): if e.vivo: movimentos.append([e.id, dest, Vector2(-1, -1)]))

func _enviar_mapa(peer: int, novo := false) -> void:
	var s: Dictionary = sessoes[peer]
	var sim: WorldSim = mundos[s["mapa"]]
	var ents := {}
	s["cache"] = {}
	for e: Ent in sim.ents.values():
		var c := Sincro.campos(e, e == s["jog"])
		ents[e.id] = c
		s["cache"][e.id] = c
	var spawns: Array = []
	for g in sim.spawns: spawns.append({"mob": g["mob"], "pos": g["pos"]})
	s["chefe"] = _chefe_estado(sim)
	rede.enviar(peer, {"t": "mapa", "mapa": s["mapa"], "eu": s["jog"].id, "ents": ents, "chao": Sincro.limpo(sim.chao),
		"spawns": spawns, "chefe": s["chefe"], "novo": novo})

static func _chefe_estado(sim: WorldSim) -> String:
	return sim.chefe.estado if sim.chefe != null else ""

## Eventos do mundo: os de um jogador só vão para ele; o resto vai para todos daquele mapa.
func _ev(tipo: String, d: Dictionary, mapa_id: String) -> void:
	if tipo == "trocar_mapa":
		movimentos.append([int(d.get("_para", -1)), str(d.get("mapa", "area_inicial")), d.get("pos", Vector2(-1, -1))])
		return
	if tipo == "mapa": return
	if d.has("_para"):
		var p = por_jog.get(int(d["_para"]))
		if p != null and sessoes.has(p):
			sessoes[p]["saida"].append([tipo, Sincro.limpo(d)])
			if tipo in ["nivel", "missao"]: sessoes[p]["sujo"] = true
		return
	var dl = null
	for p in sessoes:
		var s: Dictionary = sessoes[p]
		if s["jog"] == null or s["mapa"] != mapa_id: continue
		if dl == null: dl = Sincro.limpo(d)
		s["saida"].append([tipo, dl])
		if tipo == "nivel" and int(d.get("id", -1)) == s["jog"].id: s["sujo"] = true

# =================================================================== laço
func _process(dt: float) -> void:
	acc += minf(dt, 0.25)
	var n := 0
	while acc >= WorldSim.TICK and n < 4:
		acc -= WorldSim.TICK
		n += 1
		for sim: WorldSim in mundos.values(): sim.passo(WorldSim.TICK)
	if n == 0: return
	if not movimentos.is_empty(): _mover_jogadores()
	_enviar_ticks()
	t_salvar += dt
	if t_salvar > 30.0:
		t_salvar = 0.0
		for p in sessoes:
			if sessoes[p]["jog"] != null: _salvar_jog(p, false)
		_gravar_contas()
	else:
		var gravar := false
		for p in sessoes:
			if sessoes[p].get("sujo", false):
				sessoes[p]["sujo"] = false; _salvar_jog(p, false); gravar = true
		if gravar: _gravar_contas()

func _mover_jogadores() -> void:
	var lista := movimentos.duplicate()
	movimentos.clear()
	for mv in lista:
		var p = por_jog.get(mv[0])
		if p == null or not sessoes.has(p): continue
		var s: Dictionary = sessoes[p]
		var e: Ent = s["jog"]
		var velho: String = s["mapa"]
		if mundos.has(velho): mundos[velho].remover_jogador(e)
		var sim := _mundo(mv[1])
		var pos: Vector2 = mv[2] if mv[2] is Vector2 else Vector2(-1, -1)
		if pos.x < 0: pos = _spawn(sim, e)
		s["mapa"] = mv[1]; s["saida"] = []
		sim.adicionar_jogador(e, pos)
		_enviar_mapa(p)
		_liberar_se_vazio(velho)
		_salvar_jog(p)

func _enviar_ticks() -> void:
	var pubs := {}
	for p in sessoes:
		var s: Dictionary = sessoes[p]
		var eu: Ent = s["jog"]
		if eu == null or not mundos.has(s["mapa"]): continue
		var sim: WorldSim = mundos[s["mapa"]]
		if not pubs.has(s["mapa"]):
			var pub := {}
			for e: Ent in sim.ents.values(): pub[e.id] = Sincro.campos(e, false)
			pubs[s["mapa"]] = pub
		var atual: Dictionary = pubs[s["mapa"]]
		var cache: Dictionary = s["cache"]
		var delta := {}
		for id in atual:
			var c: Dictionary = Sincro.campos(eu, true) if id == eu.id else atual[id]
			var v = cache.get(id)
			if v == null:
				delta[id] = c
			else:
				var df := Sincro.diff(v, c)
				if df.is_empty(): continue
				delta[id] = df
			cache[id] = c
		var fora: Array = []
		for id in cache.keys():
			if not atual.has(id): fora.append(id); cache.erase(id)
		var m := {"t": "tick"}
		if not delta.is_empty(): m["e"] = delta
		if not fora.is_empty(): m["x"] = fora
		if not s["saida"].is_empty(): m["ev"] = s["saida"]; s["saida"] = []
		var ce := _chefe_estado(sim)
		if ce != s["chefe"]: s["chefe"] = ce; m["chefe"] = ce
		if m.size() > 1: rede.enviar(p, m)

func _salvar_jog(peer: int, gravar := true) -> void:
	var s: Dictionary = sessoes[peer]
	if s["jog"] == null or not mundos.has(s["mapa"]): return
	var lista: Array = contas[s["u"]]["personagens"]
	if s["idx"] < 0 or s["idx"] >= lista.size(): return
	lista[s["idx"]] = Jogador.salvar(s["jog"], mundos[s["mapa"]])
	if gravar: _gravar_contas()

extends Node
## Servidor da rede local: contas, personagens por conta e um mundo (WorldSim) por mapa ocupado.
## Roda dentro do jogo de quem hospeda (ou sozinho com `-- servidor=1`). Os clientes só mandam comandos;
## o servidor manda de volta o que mudou nas entidades e os eventos do mapa onde cada um está.

const ARQ := "user://servidor/contas.json"
const MAX_PERSONAGENS := 6
const ITER_HASH := 4000
const MAX_ERROS := 5          # erros de senha seguidos (por conexão e por IP) antes de bloquear
const BLOQUEIO_SEG := 60
const MAX_CADASTROS_IP := 5   # contas novas por IP a cada 10 minutos
## Na VPS o site (darkpassage.com.br) é o dono das contas: o jogo confere a senha com ele numa chamada local
## (design/online/site-e-contas.md). Sem a variável CHAVE_INTERNA (rede local) as contas ficam no contas.json.
const SITE_AUTENTICAR := "http://127.0.0.1:8080/api/interno/autenticar"
var contas_pelo_site := OS.has_environment("CHAVE_INTERNA")
var conferindo := {}        # peer -> HTTPRequest em andamento

var rede: Node
var contas := {}            # usuario -> {sal, hash, personagens: [save]}
var sessoes := {}           # peer -> {u, jog: Ent, mapa, idx, cache, saida, chefe}
var por_jog := {}           # id do Ent do jogador -> peer
var grupos := {}            # gid -> {"lider": peer, "membros": [peer, ...]}  (grupo de até GRUPO_MAX, estilo MU)
var convites := {}          # peer convidado -> peer que convidou
var prox_gid := 1
var t_grupo := 0.0
const GRUPO_MAX := 5
const INSPECAO_ALCANCE := 30.0
var mundos := {}            # id do mapa -> WorldSim
var movimentos: Array = []  # [id do jogador, mapa, pos] (portal, vela de retorno)
var acc := 0.0
var t_salvar := 0.0
var erros := {}             # "peer:N" / "ip:X" -> [erros, bloqueado até (ms)]
var cadastros := {}         # ip -> [contas novas, início da janela (ms)]
const Troca := preload("res://scripts/net/troca.gd")
var troca = Troca.new(self) # troca de itens e ouro entre jogadores (scripts/net/troca.gd)
var agrak: Node = preload("res://scripts/net/agrak.gd").new()   # O Agrak: agenda, inscrição, levar e trazer (entregas/agrak)
var hermon: EventoHermon      # evento O Cume dos Vigilantes: agenda, entrada de 5 min e convite
var t_hermon := 0.0
var gm: Node = preload("res://scripts/net/gm.gd").new()   # painel do GM: contas GM, punições, invocar, eventos (entregas/gm)

func _ready() -> void:
	_carregar_contas()
	add_child(agrak)
	add_child(gm)
	hermon = EventoHermon.new(Defs.ler(HermonCtl.DADOS)["evento"])
	print("[servidor] contas: ", "pelo site (%s)" % SITE_AUTENTICAR if contas_pelo_site else "neste servidor (%s)" % ARQ)

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
			if str(m.get("v", "")) != rede.VERSAO:
				_erro(peer, "Atualize o jogo: o servidor está na versão %s e o seu jogo é %s. Baixe a versão nova no site." % [rede.VERSAO, str(m.get("v", "antiga"))]); return
			var ip: String = rede.ip_do_peer(peer)
			var espera := maxi(_bloqueado("peer:%d" % peer), _bloqueado("ip:" + ip))
			if espera > 0: _erro(peer, "Muitas tentativas erradas. Espere %d segundos." % espera); return
			var u := str(m.get("u", "")).strip_edges().to_lower()
			var h := str(m.get("h", ""))
			if not _usuario_ok(u): _erro(peer, "Usuário precisa ter de 3 a 16 letras ou números (sem espaço)."); return
			if h.length() != 64: _erro(peer, "Senha inválida."); return
			if contas_pelo_site:
				if t == "cadastro": _erro(peer, "Crie sua conta no site darkpassage.com.br e depois clique em Entrar."); return
				_conferir_no_site(peer, u, h, ip); return
			if t == "cadastro":
				if contas.has(u): _erro(peer, "Esse usuário já existe. Use Entrar."); return
				var agora := Time.get_ticks_msec()
				var c: Array = cadastros.get(ip, [0, agora])
				if agora - c[1] > 600000: c = [0, agora]
				if ip != "local" and c[0] >= MAX_CADASTROS_IP: _erro(peer, "Contas demais criadas deste lugar. Tente mais tarde."); return
				c[0] += 1; cadastros[ip] = c
				var sal := Crypto.new().generate_random_bytes(16).hex_encode()
				contas[u] = {"sal": sal, "hash": _resumo(sal, h), "personagens": [], "criada": Time.get_datetime_string_from_system()}
				_gravar_contas()
			else:
				if not contas.has(u) or _resumo(contas[u]["sal"], h) != contas[u]["hash"]:
					_errou("peer:%d" % peer); _errou("ip:" + ip)
					_erro(peer, "Usuário ou senha errados."); return
				erros.erase("peer:%d" % peer); erros.erase("ip:" + ip)
			_logar(peer, u, t == "cadastro")
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
		"apagar":   # só da conta logada, fora do mundo, e com o nome digitado igual ao do personagem
			if s.is_empty() or s["jog"] != null: return
			var lista: Array = contas[s["u"]]["personagens"]
			var i = m.get("i", -1)
			if not (i is int and i >= 0 and i < lista.size()): return
			var nome := str(lista[i].get("nome", ""))
			if str(m.get("nome", "")) != nome: _erro(peer, "O nome digitado não confere. Nada foi apagado."); return
			lista.remove_at(i)
			_gravar_contas()
			print("[servidor] %s apagou o personagem %s" % [s["u"], nome])
			rede.enviar(peer, {"t": "conta", "u": s["u"], "personagens": _lista(s["u"]), "apagado": nome})
		"grupo":
			if s.is_empty() or s["jog"] == null: return
			_grupo(peer, m)
		"inspecionar":
			if s.is_empty() or s["jog"] == null: return
			_inspecionar(peer, m)
		"troca":
			if s.is_empty() or s["jog"] == null: return
			troca.receber(peer, m)
		"gm":   # painel do GM: só vale para conta GM deste servidor (scripts/net/gm.gd confere tudo)
			if s.is_empty() or s["jog"] == null: return
			gm.receber(peer, m)
		"cmd":
			if s.is_empty() or s["jog"] == null: return
			var n = m.get("n", ""); var a = m.get("a", [])
			if n is String and troca.em_troca(peer) and n in Troca.TRAVADOS:
				_para(peer, "aviso", {"texto": "Termine a troca primeiro."}); return
			if n is String and n == "falar" and gm.mudo(peer): return   # silenciado por um GM
			if n is String and a is Array and mundos.has(s["mapa"]):
				Comandos.executar(mundos[s["mapa"]], s["jog"], n, a)

func _logar(peer: int, u: String, novo: bool) -> void:
	for p in sessoes:
		if sessoes[p].get("u", "") == u: _erro(peer, "Essa conta já está no jogo em outro PC."); return
	var ban: String = gm.ban_login(u)   # banida por um GM
	if ban != "": _erro(peer, ban); return
	if not contas.has(u):   # conta criada no site: aqui só guardamos os personagens
		contas[u] = {"personagens": [], "criada": Time.get_datetime_string_from_system()}
		_gravar_contas()
	sessoes[peer] = {"u": u, "jog": null, "mapa": "", "idx": -1, "cache": {}, "saida": [], "chefe": ""}
	rede.enviar(peer, {"t": "conta", "u": u, "personagens": _lista(u), "novo": novo})

## Pergunta ao site se a senha confere (só na VPS, chamada local com a chave interna).
func _conferir_no_site(peer: int, u: String, h: String, ip: String) -> void:
	if conferindo.has(peer): return
	var req := HTTPRequest.new()
	req.timeout = 8.0
	add_child(req)
	conferindo[peer] = req
	req.request_completed.connect(func(res: int, cod: int, _cab, corpo: PackedByteArray):
		conferindo.erase(peer); req.queue_free()
		if not multiplayer.get_peers().has(peer) and peer != 1: return   # desistiu no meio
		if res != HTTPRequest.RESULT_SUCCESS or (cod != 200 and cod != 401):
			printerr("[servidor] site de contas não respondeu: resultado %d, código %d" % [res, cod])
			_erro(peer, "O servidor de contas está fora do ar. Tente de novo em alguns minutos."); return
		var d = JSON.parse_string(corpo.get_string_from_utf8())
		if cod == 401 or not (d is Dictionary and d.get("ok", false)):
			_errou("peer:%d" % peer); _errou("ip:" + ip)
			_erro(peer, "Usuário ou senha errados."); return
		erros.erase("peer:%d" % peer); erros.erase("ip:" + ip)
		_logar(peer, u, false))
	var err := req.request(SITE_AUTENTICAR, ["Content-Type: application/json", "X-Chave: " + OS.get_environment("CHAVE_INTERNA")],
		HTTPClient.METHOD_POST, JSON.stringify({"u": u, "h": h}))
	if err != OK:
		conferindo.erase(peer); req.queue_free()
		_erro(peer, "O servidor de contas está fora do ar. Tente de novo em alguns minutos.")

## Segundos que faltam de bloqueio (0 = liberado).
func _bloqueado(k: String) -> int:
	var e: Array = erros.get(k, [0, 0])
	var falta: int = e[1] - Time.get_ticks_msec()
	if falta <= 0 and e[1] > 0: erros.erase(k); return 0
	return ceili(falta / 1000.0) if falta > 0 else 0

func _errou(k: String) -> void:
	var e: Array = erros.get(k, [0, 0])
	e[0] += 1
	if e[0] >= MAX_ERROS: e = [0, Time.get_ticks_msec() + BLOQUEIO_SEG * 1000]
	erros[k] = e

func _erro(peer: int, msg: String) -> void:
	rede.enviar(peer, {"t": "erro", "msg": msg})

## Conexão caiu ou o jogador saiu: salva e tira o personagem do mundo.
func desconectou(peer: int) -> void:
	erros.erase("peer:%d" % peer)
	convites.erase(peer)
	for k in convites.keys():
		if convites[k] == peer: convites.erase(k)
	_sair_grupo(peer)
	troca.desconectou(peer)
	if conferindo.has(peer): conferindo[peer].queue_free(); conferindo.erase(peer)
	if not sessoes.has(peer): return
	var s: Dictionary = sessoes[peer]
	if s["jog"] != null:
		agrak.saiu(peer)   # no meio do Agrak: salva onde ele estava antes
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
	sim.descarregar()
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
	var casa := Defs.mapa_casa_classe(str(salvo["classe"]))   # Arautos nascem em Jerusalém (0.9.3)
	var mapa_id: String = salvo.get("mapa", casa)
	if not ResourceLoader.exists("res://data/mapas/%s.json" % mapa_id) and not FileAccess.file_exists("res://data/mapas/%s.json" % mapa_id): mapa_id = casa
	var sim := _mundo(mapa_id)
	var e := Jogador.criar(sim, salvo["classe"], salvo.get("nome", "Sobrevivente"), {} if novo else salvo)
	var pos := _spawn(sim, e)
	var ps: Array = salvo.get("pos", [])
	if ps.size() == 2: pos = Vector2(ps[0], ps[1])
	s["jog"] = e; s["mapa"] = mapa_id; s["idx"] = idx; s["saida"] = []
	if int(s.get("grupo", -1)) >= 0: e.aux["grupo"] = int(s["grupo"])
	por_jog[e.id] = peer
	sim.adicionar_jogador(e, pos)
	_chave_primarca(s["u"], e, sim)
	_cetro_demiurgo(s["u"], e, sim)
	e.flags["torre_aberta"] = true   # A Torre liberada para todos (0.8.6): a grade do mata_do_granizo pede esta flag
	_enviar_mapa(peer, novo)
	gm.entrou(peer)   # conta GM recebe a chave do painel (F8)
	print("[servidor] entrou: %s com %s (%s, nível %d)" % [s["u"], e.nome, e.classe, e.nivel])
	for x in OS.get_cmdline_user_args():   # teste: leva o jogador para outro mapa depois de 8 s
		if x.begins_with("teste_mapa="):
			var dest := x.get_slice("=", 1)
			get_tree().create_timer(8.0).timeout.connect(func(): if e.vivo: movimentos.append([e.id, dest, Vector2(-1, -1)]))

## Chave-Mestra do Primarca (0.8.3): uma única vez, no Tecnomancer da conta "gustavo".
func _chave_primarca(usuario: String, e: Ent, sim: WorldSim) -> void:
	if usuario != "gustavo" or e.classe != "tecnomancer" or e.flags.has("chave_primarca"): return
	e.flags["chave_primarca"] = true
	Jogador.dar_item(sim, e, Itens.novo("chave_mestra_primarca"))
	_gravar_contas()

## Cetro do Demiurgo (0.9.4): uma única vez por personagem de conta GM (scripts/net/gm.gd), qualquer classe.
## Quem deixou de ser GM perde o cetro ao entrar: ninguém além do administrador fica com ele.
func _cetro_demiurgo(usuario: String, e: Ent, sim: WorldSim) -> void:
	if gm.eh_conta_gm(usuario):
		if e.flags.has("cetro_demiurgo"): return
		if not Jogador.dar_item(sim, e, Itens.novo("cetro_do_demiurgo")): return   # mochila cheia: tenta na próxima entrada
		e.flags["cetro_demiurgo"] = true
		_gravar_contas()
	elif Demiurgo.tirar(sim, e): _gravar_contas()

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
	if tipo == "agrak_pedido":   # Cartaz do Agrak e Caim e Abel: a lista fica no servidor
		agrak.pedido(por_jog.get(int(d.get("_para", -1)), -1), str(d.get("a", "inscrever"))); return
	if tipo == "usar_evento":
		if str(d.get("uso", "")) == "evento:agrak": _usar_bilhete(d)
		else: _usar_convite(d, mapa_id)
		return
	if tipo == "chat":   # perto: mesmo mapa e perto; global: todos; pm: só o destinatário; grupo: membros do grupo
		var dc = Sincro.limpo(d)
		var canal := str(d.get("canal", "perto"))
		var de_peer: int = por_jog.get(int(d.get("id", -1)), -1)
		dc.erase("pos")
		if canal == "pm":
			var alvo := _peer_por_nome(str(d.get("para", "")))
			if alvo < 0:
				_para(de_peer, "chat", {"canal": "sistema", "texto": "%s não está online." % str(d.get("para", ""))})
				return
			_para(alvo, tipo, dc)
			if alvo != de_peer: _para(de_peer, tipo, dc)
			return
		if canal == "grupo":
			var gid: int = int(sessoes.get(de_peer, {}).get("grupo", -1))
			if gid < 0:
				_para(de_peer, "chat", {"canal": "sistema", "texto": "Você não está em um grupo."}); return
			for p in grupos[gid]["membros"]: _para(p, tipo, dc)
			return
		var pos = d.get("pos", Vector2.ZERO)
		for p in sessoes:
			var j = sessoes[p]["jog"]
			if j == null: continue
			if canal == "perto" and (sessoes[p]["mapa"] != mapa_id or j.pos.distance_to(pos) > Jogador.CHAT_PERTO): continue
			_para(p, tipo, dc)
		print("[chat %s] %s: %s" % [canal, str(d.get("nome", "?")), str(d.get("texto", ""))])
		return
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

# =================================================================== grupo e inspecionar
func _para(peer: int, tipo: String, d: Dictionary) -> void:
	if sessoes.has(peer): sessoes[peer]["saida"].append([tipo, d])

func _peer_por_nome(nome: String) -> int:
	for p in sessoes:
		var j = sessoes[p]["jog"]
		if j != null and str(j.nome).to_lower() == nome.strip_edges().to_lower(): return p
	return -1

func _peer_do_ent(id: int) -> int:
	var p: int = por_jog.get(id, -1)
	return p if sessoes.has(p) and sessoes[p]["jog"] != null else -1

func _marcar_grupo(peer: int, gid: int) -> void:
	sessoes[peer]["grupo"] = gid
	var j = sessoes[peer]["jog"]
	if j == null: return
	if gid >= 0: j.aux["grupo"] = gid
	else: j.aux.erase("grupo")

func _grupo(peer: int, m: Dictionary) -> void:
	match str(m.get("a", "")):
		"convidar": _convidar(peer, _peer_do_ent(int(m.get("id", -1))))
		"convidar_nome": _convidar(peer, _peer_por_nome(str(m.get("nome", ""))))
		"aceitar": _aceitar(peer)
		"recusar":
			if convites.has(peer):
				_para(convites[peer], "chat", {"canal": "sistema", "texto": "%s recusou o convite." % sessoes[peer]["jog"].nome})
				convites.erase(peer)
		"sair": _sair_grupo(peer)

func _convidar(peer: int, alvo: int) -> void:
	if alvo < 0 or alvo == peer:
		_para(peer, "aviso", {"texto": "Esse jogador não está online."}); return
	if int(sessoes[alvo].get("grupo", -1)) >= 0:
		_para(peer, "aviso", {"texto": "%s já está em um grupo." % sessoes[alvo]["jog"].nome}); return
	var gid: int = int(sessoes[peer].get("grupo", -1))
	if gid >= 0 and grupos[gid]["membros"].size() >= GRUPO_MAX:
		_para(peer, "aviso", {"texto": "O grupo já tem %d jogadores." % GRUPO_MAX}); return
	convites[alvo] = peer
	_para(alvo, "convite", {"de": sessoes[peer]["jog"].nome})
	_para(peer, "aviso", {"texto": "Convite enviado para %s." % sessoes[alvo]["jog"].nome})

func _aceitar(peer: int) -> void:
	if not convites.has(peer): return
	var de: int = convites[peer]
	convites.erase(peer)
	if not sessoes.has(de) or sessoes[de]["jog"] == null:
		_para(peer, "aviso", {"texto": "O convite expirou."}); return
	var gid: int = int(sessoes[de].get("grupo", -1))
	if gid < 0:
		gid = prox_gid; prox_gid += 1
		grupos[gid] = {"lider": de, "membros": [de]}
		_marcar_grupo(de, gid)
	if grupos[gid]["membros"].size() >= GRUPO_MAX:
		_para(peer, "aviso", {"texto": "O grupo já está cheio."}); return
	if int(sessoes[peer].get("grupo", -1)) >= 0: return
	grupos[gid]["membros"].append(peer)
	_marcar_grupo(peer, gid)
	_grupo_aviso(gid, "%s entrou no grupo." % sessoes[peer]["jog"].nome)

func _sair_grupo(peer: int) -> void:
	if not sessoes.has(peer): return
	var gid: int = int(sessoes[peer].get("grupo", -1))
	if gid < 0 or not grupos.has(gid): return
	var g: Dictionary = grupos[gid]
	var nome: String = sessoes[peer]["jog"].nome if sessoes[peer]["jog"] != null else "Alguém"
	g["membros"].erase(peer)
	_marcar_grupo(peer, -1)
	if g["membros"].size() < 2:
		for p in g["membros"]:
			_marcar_grupo(p, -1)
			_para(p, "chat", {"canal": "sistema", "texto": "O grupo foi desfeito."})
		grupos.erase(gid)
	else:
		if g["lider"] == peer: g["lider"] = g["membros"][0]
		_grupo_aviso(gid, "%s saiu do grupo." % nome)
	_para(peer, "chat", {"canal": "sistema", "texto": "Você saiu do grupo."})

func _grupo_aviso(gid: int, txt: String) -> void:
	for p in grupos[gid]["membros"]: _para(p, "chat", {"canal": "sistema", "texto": txt})

## Manda para cada membro a lista do grupo (vida e mapa de todos) a cada meio segundo.
func _enviar_grupos() -> void:
	for gid in grupos:
		var g: Dictionary = grupos[gid]
		var lista: Array = []
		for p in g["membros"]:
			var j = sessoes.get(p, {}).get("jog")
			if j == null: continue
			lista.append({"id": j.id, "nome": j.nome, "classe": j.classe, "nivel": j.nivel, "hp": j.hp, "hp_max": j.hp_max,
				"vivo": j.vivo, "mapa": sessoes[p]["mapa"], "lider": p == g["lider"]})
		for p in g["membros"]: _para(p, "grupo", {"membros": lista})

func _inspecionar(peer: int, m: Dictionary) -> void:
	var alvo := _peer_do_ent(int(m.get("id", -1)))
	if alvo < 0 or alvo == peer: return
	var eu: Ent = sessoes[peer]["jog"]
	var outro: Ent = sessoes[alvo]["jog"]
	if sessoes[alvo]["mapa"] != sessoes[peer]["mapa"] or eu.pos.distance_to(outro.pos) > INSPECAO_ALCANCE:
		_para(peer, "aviso", {"texto": "Chegue mais perto para inspecionar."}); return
	_para(peer, "inspecao", Jogador.inspecao(outro))

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
	t_hermon += dt
	if t_hermon >= 1.0:
		t_hermon = 0.0
		for txt in hermon.avisos(int(Time.get_unix_time_from_system())): _sistema_todos(txt)
	t_grupo += dt
	if t_grupo >= 0.5:
		t_grupo = 0.0
		_enviar_grupos()
		troca.passo()
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

# =================================================================== evento O Cume dos Vigilantes
func _sistema_todos(txt: String) -> void:
	for p in sessoes:
		if sessoes[p]["jog"] != null: _para(p, "chat", {"canal": "sistema", "texto": txt})

## O jogador usou o Bilhete do Agrak: o servidor põe o nome na lista e só então gasta o bilhete.
func _usar_bilhete(d: Dictionary) -> void:
	var p = por_jog.get(int(d.get("_para", -1)))
	if p == null or not sessoes.has(p): return
	var e: Ent = sessoes[p]["jog"]
	if e == null or not agrak.usar_bilhete(p): return
	Itens.remover(e.inv, str(d.get("item", "bilhete_agrak")), 1)
	_para(p, "inventario", {})

## O jogador clicou no Convite dos Vigilantes (Jogador.usar_item manda "usar_evento" para o servidor decidir).
func _usar_convite(d: Dictionary, mapa_id: String) -> void:
	var p = por_jog.get(int(d.get("_para", -1)))
	if p == null or not sessoes.has(p): return
	var e: Ent = sessoes[p]["jog"]
	var sim: WorldSim = mundos.get(mapa_id)
	if e == null or sim == null or str(d.get("uso", "")) != "evento:cume_vigilantes": return
	var onde := "dungeon" if sim.chefe != null else ("evento" if sim.hermon != null else "mundo")
	var r := hermon.usar_convite(e.nivel, int(Time.get_unix_time_from_system()), onde, sim.hermon != null)
	if not r["ok"]:
		_para(p, "aviso", {"texto": r["texto"]}); return
	Itens.remover(e.inv, str(d.get("item", "convite_dos_vigilantes")), 1)
	_para(p, "inventario", {})
	e.aux["hermon_volta"] = {"mapa": mapa_id, "pos": [e.pos.x, e.pos.y]}
	var cume := _mundo(r["instancia"])
	cume.hermon.definir_nivel(int(r["nivel_mob"]))
	cume.hermon.definir_espera(float(r["resta"]))
	if hermon.inicio_imediato:
		hermon.inicio_imediato = false; cume.hermon.forcar_inicio()
	var ch: Array = cume.hermon.cfg["chegadas"]
	var c: Array = ch[cume.hermon.participantes.size() % ch.size()]
	_para(p, "aviso", {"texto": r["texto"]})
	movimentos.append([e.id, r["instancia"], Vector2(c[0], c[1])])

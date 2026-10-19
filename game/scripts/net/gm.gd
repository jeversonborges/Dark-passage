extends Node
## Painel GM no servidor. O cliente só PEDE ({"t": "gm", "a": ...}); tudo é conferido aqui:
## a conta precisa estar na lista de GMs DO SERVIDOR (nunca vem do cliente), e cada ação vai para o gm_log.
## Lista de GMs: arquivo JSON {"contas": ["login"]} que existe só na máquina do servidor (na VPS,
## /etc/darkpassage/gm.json; fora do repositório e do .pck). Sem ele, user://servidor/gm.json (rede local).
## Sem nenhum dos dois, NINGUÉM é GM. Teste local: argumento do servidor gm_contas=login1,login2.
## Banimento e silêncio ficam na conta (contas.json): ban_ate / mudo_ate.

const ARQS_CFG := ["/etc/darkpassage/gm.json", "user://servidor/gm.json"]
const ARQ_LOG := "user://servidor/gm_log.txt"
const PERMANENTE := 4102444800                 # 01/01/2100: "para sempre"
const MAX_INVOCAR := 20
const MAX_NIVEL := 400

var srv                     # servidor.gd
var contas_gm: Array = []
var mapas: Array = []       # ids de data/mapas (sem as instâncias)
var chefes_gm := {}         # id do Ent -> {mapa, kind}: chefes de campo invocados (saque de chefe ao morrer)
var ligados := {}           # WorldSim -> true (sinal "evento" já conectado)
var inicio_ms := 0

func _ready() -> void:
	srv = get_parent()
	inicio_ms = Time.get_ticks_msec()
	_ler_contas()
	for f in DirAccess.get_files_at("res://data/mapas"):
		var n := f.trim_suffix(".remap")
		if n.ends_with(".json"): mapas.append(n.trim_suffix(".json"))
	mapas.sort()
	print("[gm] contas GM: ", ", ".join(contas_gm) if not contas_gm.is_empty() else "nenhuma (crie /etc/darkpassage/gm.json)")

func _ler_contas() -> void:
	contas_gm.clear()
	for x in OS.get_cmdline_user_args():
		if x.begins_with("gm_contas="):
			for u in x.get_slice("=", 1).split(",", false): contas_gm.append(u.strip_edges().to_lower())
			return
	for arq in ARQS_CFG:
		if not FileAccess.file_exists(arq): continue
		var d = JSON.parse_string(FileAccess.get_file_as_string(arq))
		if d is Dictionary and d.get("contas") is Array:
			for u in d["contas"]: contas_gm.append(str(u).strip_edges().to_lower())
		else: printerr("[gm] %s inválido: use {\"contas\": [\"login\"]}" % arq)
		return

## Para outros sistemas do servidor (ex.: a arma do administrador): esta conta está na lista de GMs?
func eh_conta_gm(u: String) -> bool:
	return u.strip_edges().to_lower() in contas_gm

func eh_gm(peer: int) -> bool:
	var s: Dictionary = srv.sessoes.get(peer, {})
	return not s.is_empty() and str(s.get("u", "")) in contas_gm

func _log(peer: int, txt: String) -> void:
	var u := str(srv.sessoes.get(peer, {}).get("u", "?"))
	var linha := "%s  %s  %s" % [Time.get_datetime_string_from_system(true), u, txt]
	print("[gm] ", linha)
	var f := FileAccess.open(ARQ_LOG, FileAccess.READ_WRITE if FileAccess.file_exists(ARQ_LOG) else FileAccess.WRITE)
	if f == null: return
	f.seek_end()
	f.store_line(linha)

# =================================================================== ganchos do servidor.gd
## Entrou no mundo: o GM recebe a chave do painel (F8). Os outros não recebem nada.
func entrou(peer: int) -> void:
	if not eh_gm(peer): return
	srv._para(peer, "gm_ativo", {"conta": srv.sessoes[peer]["u"]})

## Login: conta banida não entra. Devolve "" ou o texto do erro.
func ban_login(u: String) -> String:
	var c: Dictionary = srv.contas.get(u, {})
	var ate := int(c.get("ban_ate", 0))
	if ate <= int(Time.get_unix_time_from_system()): return ""
	var quando := "para sempre" if ate >= PERMANENTE else "até " + _data(ate)
	return "Esta conta está suspensa %s.%s" % [quando, (" Motivo: " + str(c["ban_motivo"])) if str(c.get("ban_motivo", "")) != "" else ""]

## Chat: devolve true se a conta está silenciada (o servidor.gd não deixa o "falar" passar).
func mudo(peer: int) -> bool:
	var s: Dictionary = srv.sessoes.get(peer, {})
	var ate := int(srv.contas.get(str(s.get("u", "")), {}).get("mudo_ate", 0))
	var falta := ate - int(Time.get_unix_time_from_system())
	if falta <= 0: return false
	srv._para(peer, "aviso", {"texto": "Você está silenciado por mais %d min." % ceili(falta / 60.0)})
	return true

# =================================================================== pedidos do painel
func receber(peer: int, m: Dictionary) -> void:
	if not eh_gm(peer):
		print("[gm] pedido de GM recusado (conta %s)" % str(srv.sessoes.get(peer, {}).get("u", "?")))
		return
	var s: Dictionary = srv.sessoes[peer]
	var eu: Ent = s.get("jog")
	if eu == null: return
	var sim: WorldSim = srv.mundos.get(s["mapa"])
	if sim == null: return
	var a := str(m.get("a", ""))
	match a:
		"estado": _enviar_estado(peer)
		# ---------------------------------------------------------- o próprio GM
		"invisivel":
			eu.invisivel = bool(m.get("v", false))
			eu.aux["gm_invisivel"] = eu.invisivel
			sim.emitir("gm_visivel", {"id": eu.id, "vis": not eu.invisivel})
			_ok(peer, "Invisível." if eu.invisivel else "Visível de novo.")
			_log(peer, "invisivel %s" % eu.invisivel)
		"imortal":
			var on := bool(m.get("v", false))
			if on: eu.aux["imune"] = true; eu.invuln_t = 1.0e7; eu.hp = eu.hp_max
			else: eu.aux.erase("imune"); eu.invuln_t = 0.0
			eu.aux["gm_imortal"] = on
			_ok(peer, "Imortal." if on else "Mortal de novo.")
			_log(peer, "imortal %s" % on)
		"curar":
			var al := _alvo_ent(peer, m)
			if al == null: return
			if not al.vivo: Jogador.renascer(_sim_de(al), al)
			al.hp = al.hp_max; al.rec = al.rec_max; al.status.clear()
			_ok(peer, "%s curado." % al.nome)
		"ir_ponto":   # F7: teleporta para o ponto do mouse no mesmo mapa
			var p = m.get("pos")
			if not (p is Vector2 and (p as Vector2).is_finite()) or not sim.andavel(p): _ok(peer, "Ali não dá para pisar."); return
			eu.caminho.clear(); eu.destino = Vector2.INF; eu.deslocando = {}
			eu.pos = p
			sim.emitir("teleporte", {"id": eu.id, "pos": p})
		"ir_mapa":
			var id := str(m.get("mapa", ""))
			if not id in mapas: _ok(peer, "Mapa desconhecido."); return
			srv.movimentos.append([eu.id, id, Vector2(-1, -1)])
			_log(peer, "foi para o mapa %s" % id)
		# ---------------------------------------------------------- jogadores
		"ir_jogador", "trazer":
			var p2: int = srv._peer_por_nome(str(m.get("nome", "")))
			if p2 < 0: _ok(peer, "Ninguém online com esse nome."); return
			if p2 == peer: return
			var s2: Dictionary = srv.sessoes[p2]
			var outro: Ent = s2["jog"]
			if a == "ir_jogador":
				srv.movimentos.append([eu.id, s2["mapa"], outro.pos + Vector2(0.8, 0.4)])
				_log(peer, "foi até %s (%s)" % [outro.nome, s2["mapa"]])
			else:
				srv.movimentos.append([outro.id, s["mapa"], eu.pos + Vector2(0.8, 0.4)])
				srv._para(p2, "aviso", {"texto": "Um GM te chamou."})
				_log(peer, "trouxe %s de %s" % [outro.nome, s2["mapa"]])
		"expulsar":
			var p3: int = srv._peer_por_nome(str(m.get("nome", "")))
			if p3 < 0 or p3 == peer or p3 == 1: _ok(peer, "Não dá para expulsar esse."); return
			var nome3: String = srv.sessoes[p3]["jog"].nome
			_derrubar(p3, "Você foi desconectado por um GM." + _motivo(m))
			_ok(peer, "%s expulso." % nome3)
			_log(peer, "expulsou %s%s" % [nome3, _motivo(m)])
		"silenciar":
			var u := _conta_de(str(m.get("nome", "")))
			if u == "": _ok(peer, "Conta ou personagem não encontrado."); return
			var minutos := clampi(int(m.get("min", 10)), 0, 60 * 24 * 30)
			srv.contas[u]["mudo_ate"] = int(Time.get_unix_time_from_system()) + minutos * 60 if minutos > 0 else 0
			srv._gravar_contas()
			var pp := _peer_da_conta(u)
			if pp >= 0: srv._para(pp, "aviso", {"texto": "Você foi silenciado por %d min." % minutos if minutos > 0 else "Você pode falar de novo."})
			_ok(peer, ("Conta %s silenciada por %d min." % [u, minutos]) if minutos > 0 else "Conta %s pode falar." % u)
			_log(peer, "silenciou %s por %d min" % [u, minutos])
		"banir":
			var u2 := _conta_de(str(m.get("nome", "")))
			if u2 == "": _ok(peer, "Conta ou personagem não encontrado."); return
			if u2 in contas_gm: _ok(peer, "Não dá para banir um GM."); return
			var dias := int(m.get("dias", 1))
			var ate := PERMANENTE if dias <= 0 else int(Time.get_unix_time_from_system()) + dias * 86400
			srv.contas[u2]["ban_ate"] = ate
			srv.contas[u2]["ban_motivo"] = str(m.get("motivo", "")).strip_edges().left(120)
			srv._gravar_contas()
			var pb := _peer_da_conta(u2)
			if pb >= 0: _derrubar(pb, ban_login(u2))
			_ok(peer, "Conta %s banida %s." % [u2, "para sempre" if dias <= 0 else "por %d dia%s" % [dias, "" if dias == 1 else "s"]])
			_log(peer, "baniu %s (%s)%s" % [u2, "permanente" if dias <= 0 else "%d dias" % dias, _motivo(m)])
		"desbanir":
			var u3 := _conta_de(str(m.get("nome", "")))
			if u3 == "": _ok(peer, "Conta não encontrada."); return
			srv.contas[u3].erase("ban_ate"); srv.contas[u3].erase("ban_motivo"); srv.contas[u3].erase("mudo_ate")
			srv._gravar_contas()
			_ok(peer, "Conta %s liberada." % u3)
			_log(peer, "desbaniu %s" % u3)
		# ---------------------------------------------------------- itens, ouro e nível (em si ou num jogador)
		"item":
			var al2 := _alvo_ent(peer, m)
			var id2 := str(m.get("id", ""))
			if al2 == null or not Defs.ITENS.has(id2): _ok(peer, "Item desconhecido."); return
			var qtd := clampi(int(m.get("qtd", 1)), 1, 999)
			var rar := str(m.get("raridade", ""))
			var refino := clampi(int(m.get("refino", 0)), 0, 15)
			var sim2 := _sim_de(al2)
			var feitos := 0
			if Itens.equipavel(Itens.novo(id2)):
				for i in mini(qtd, 20):
					var it := Itens.gerar_equip(id2, sim2.rng, rar, 3) if rar in ["comum", "magico", "raro", "excelente"] else Itens.novo(id2)
					if refino > 0: it["refino"] = refino
					Jogador.dar_item(sim2, al2, it); feitos += 1
			else:
				var pil := maxi(1, Itens.pilha(Itens.novo(id2)))
				var resta := qtd
				while resta > 0:
					var n := mini(resta, pil)
					Jogador.dar_item(sim2, al2, Itens.novo(id2, n)); resta -= n; feitos += n
			_ok(peer, "%dx %s para %s." % [feitos, Itens.nome(Itens.novo(id2)), al2.nome])
			_log(peer, "criou %dx %s (%s +%d) para %s" % [feitos, id2, rar if rar != "" else "padrão", refino, al2.nome])
		"ouro":
			var al3 := _alvo_ent(peer, m)
			if al3 == null: return
			var q := clampi(int(m.get("qtd", 0)), -100000000, 100000000)
			al3.ouro = maxi(0, al3.ouro + q)
			_sim_de(al3).emitir_a(al3, "ouro", {"valor": q})
			_ok(peer, "%s agora tem %d de ouro." % [al3.nome, al3.ouro])
			_log(peer, "ouro %+d para %s" % [q, al3.nome])
		"nivel":
			var al4 := _alvo_ent(peer, m)
			if al4 == null: return
			var n4 := clampi(int(m.get("nivel", 1)), 1, MAX_NIVEL)
			_definir_nivel(_sim_de(al4), al4, n4)
			_ok(peer, "%s agora é nível %d (pontos devolvidos para distribuir)." % [al4.nome, n4])
			_log(peer, "nivel %d para %s" % [n4, al4.nome])
		# ---------------------------------------------------------- monstros e chefes
		"invocar":
			var kind := str(m.get("kind", ""))
			if not Defs.MOBS.has(kind): _ok(peer, "Monstro desconhecido."); return
			var niv: Array = Defs.MOBS[kind].get("niveis", [1, 1])
			var nivel := clampi(int(m.get("nivel", 0)), 1, MAX_NIVEL) if int(m.get("nivel", 0)) > 0 else int(niv[1])
			var qtd2 := clampi(int(m.get("qtd", 1)), 1, MAX_INVOCAR)
			for i in qtd2:
				var p := sim.celula_livre_perto(eu.pos + Vector2.from_angle(TAU * i / qtd2) * (2.0 + 0.4 * i), 3.0)
				var e := sim.criar_mob(kind, p, nivel)
				e.casa = p; e.aux["gm"] = true
				if bool(m.get("neutro", false)): e.aux["neutro"] = true
			_ok(peer, "%d %s (nível %d) invocado%s." % [qtd2, Defs.MON_TXT.get(kind, {}).get("nome", kind), nivel, "" if qtd2 == 1 else "s"])
			_log(peer, "invocou %dx %s nv %d em %s" % [qtd2, kind, nivel, s["mapa"]])
		"chefe":
			var kc := str(m.get("kind", ""))
			if not Defs.CHEFES.has(kc): _ok(peer, "Chefe desconhecido."); return
			var b := _chefe_de_campo(sim, kc, sim.celula_livre_perto(eu.pos + eu.facing * 4.0, 3.0))
			chefes_gm[b.id] = {"mapa": s["mapa"], "kind": kc}
			_ligar(sim)
			if bool(m.get("anunciar", false)): srv._sistema_todos("%s despertou em %s." % [b.nome, nome_mapa(s["mapa"])])
			_ok(peer, "%s invocado (nível %d)." % [b.nome, b.nivel])
			_log(peer, "invocou o chefe %s em %s" % [kc, s["mapa"]])
		"reviver_chefe":
			_ok(peer, _reviver_chefe(sim))
			_log(peer, "reviveu o chefe de %s" % s["mapa"])
		"limpar":
			var n5 := 0
			for e: Ent in sim.ents.values().duplicate():
				if e.aux.get("gm", false): sim.remover(e.id); chefes_gm.erase(e.id); n5 += 1
			_ok(peer, "%d invocações removidas." % n5)
			_log(peer, "limpou %d invocações em %s" % [n5, s["mapa"]])
		"matar_perto":
			var n6 := 0
			for e: Ent in sim.ents_em(eu.pos, clampf(float(m.get("raio", 8.0)), 1.0, 20.0)):
				if e.vivo and e.tipo == "monstro": sim.matar(e, eu); n6 += 1
			_ok(peer, "%d monstros mortos em volta." % n6)
		# ---------------------------------------------------------- eventos e avisos
		"aviso_global":
			var txt := str(m.get("texto", "")).strip_edges().left(200)
			if txt == "": return
			for p in srv.sessoes:
				if srv.sessoes[p]["jog"] != null:
					srv._para(p, "chat", {"canal": "sistema", "texto": "[GM] " + txt})
					srv._para(p, "gm_anuncio", {"texto": txt})
			_log(peer, "aviso: " + txt)
		"agrak":
			match str(m.get("modo", "")):
				"abrir":   # inscrição aberta, luta em 1 minuto (Cartaz do Agrak ou Caim e Abel)
					srv.agrak._agendar(true)
					srv.agrak._sistema("Um GM abriu o Agrak: inscrição no Cartaz do Agrak ou com Caim e Abel. A luta começa em 1 minuto.")
				"comecar":   # leva já os inscritos (precisa do mínimo)
					srv.agrak._hora()
				"minimo":
					srv.agrak.minimo = clampi(int(m.get("v", 1)), 1, 20)
			_ok(peer, "Agrak: %s (mínimo %d)." % [str(m.get("modo", "")), srv.agrak.minimo])
			_log(peer, "agrak %s" % str(m.get("modo", "")))
		"hermon":
			var agora := int(Time.get_unix_time_from_system())
			match str(m.get("modo", "")):
				"agora": srv.hermon.forcado = agora
				"5min": srv.hermon.forcado = agora + 300
				"fechar": srv.hermon.forcado = -1
				"iniciar": _iniciar_hermon(agora)
			_ok(peer, "Hermon: %s." % {"agora": "entrada aberta por 5 min", "5min": "abre em 5 min (avisos no chat)", "fechar": "volta à agenda"}.get(str(m.get("modo", "")), "?"))
			_log(peer, "hermon %s" % str(m.get("modo", "")))
		"cavaleiros":   # Os Cavaleiros do Apocalipse: os quatro descem sobre as capitais (design/combate/cavaleiros.json)
			if str(m.get("modo", "")) == "iniciar": _iniciar_cavaleiros()
			_ok(peer, "Os Cavaleiros do Apocalipse: chamados.")
			_log(peer, "cavaleiros %s" % str(m.get("modo", "")))

# =================================================================== ajudantes
## GM "Início imediato": começa já o cume aberto (com quem estiver dentro, mesmo 1). Sem ninguém na entrada,
## a próxima pessoa que usar o Convite começa o evento na hora.
func _iniciar_hermon(agora: int) -> void:
	var abertos := 0
	for sim in srv.mundos.values():
		if sim.hermon != null and sim.hermon.estado == "espera":
			sim.hermon.forcar_inicio(); abertos += 1
	if abertos == 0: srv.hermon.inicio_imediato = true
	srv.hermon.forcado = agora

## GM "Chamar os Cavaleiros": cada capital recebe o seu grupo de quatro, ao mesmo tempo.
func _iniciar_cavaleiros() -> void:
	var ev: Dictionary = Defs.ler("res://data/design/combate/cavaleiros.json")
	for cid in ev.get("capitais", {}):
		var sim: WorldSim = srv._mundo(str(ev["capitais"][cid]["mapa"]))
		var c := CavaleirosCtl.new(sim, str(cid), ev)
		sim.cavaleiros.append(c)
		c.iniciar()
	for p in srv.sessoes:
		if srv.sessoes[p]["jog"] != null:
			srv._para(p, "chat", {"canal": "sistema", "texto": "Os Cavaleiros do Apocalipse cruzam os céus. Fome, Guerra, Conquista e Peste descem sobre as capitais."})

func _ok(peer: int, txt: String) -> void:
	srv._para(peer, "gm_ok", {"texto": txt})

func _motivo(m: Dictionary) -> String:
	var t := str(m.get("motivo", "")).strip_edges().left(120)
	return (" Motivo: " + t) if t != "" else ""

static func _data(unix: int) -> String:
	var d := Time.get_datetime_dict_from_unix_time(unix - 3 * 3600)   # Brasília
	return "%02d/%02d/%d %02d:%02d" % [d["day"], d["month"], d["year"], d["hour"], d["minute"]]

## Alvo das ações de item/ouro/nível/cura: o jogador escolhido no painel, ou o próprio GM.
func _alvo_ent(peer: int, m: Dictionary) -> Ent:
	var nome := str(m.get("alvo", "")).strip_edges()
	if nome == "": return srv.sessoes[peer]["jog"]
	var p: int = srv._peer_por_nome(nome)
	if p < 0: _ok(peer, "%s não está online." % nome); return null
	return srv.sessoes[p]["jog"]

func _sim_de(e: Ent) -> WorldSim:
	return srv.mundos[srv.sessoes[srv._peer_do_ent(e.id)]["mapa"]]

## Nome de personagem online ou nome de conta (para punir quem já saiu).
func _conta_de(nome: String) -> String:
	var n := nome.strip_edges().to_lower()
	var p: int = srv._peer_por_nome(n)
	if p >= 0: return str(srv.sessoes[p]["u"])
	if srv.contas.has(n): return n
	for u in srv.contas:   # personagem offline
		for pj in srv.contas[u].get("personagens", []):
			if str(pj.get("nome", "")).to_lower() == n: return u
	return ""

## Nome do mapa para gente ler ("cume_dos_vigilantes#..." vira "Cume Dos Vigilantes" se não tiver nome em locais.json).
static func nome_mapa(id: String) -> String:
	var b := EventoHermon.mapa_base(id)
	var n := Defs.nome_local(b)
	return n if n != "" and n != b else b.replace("_", " ").capitalize()

func _peer_da_conta(u: String) -> int:
	for p in srv.sessoes:
		if srv.sessoes[p].get("u", "") == u: return p
	return -1

## Manda o motivo e derruba meio segundo depois (a mensagem chega antes da queda).
func _derrubar(p: int, txt: String) -> void:
	srv.rede.enviar(p, {"t": "erro", "msg": txt})
	get_tree().create_timer(0.5).timeout.connect(func(): srv.rede._derrubar(p, "GM: " + txt))

func _definir_nivel(sim: WorldSim, e: Ent, n: int) -> void:
	var base: Dictionary = Defs.CLASSES[e.classe]["atributos_iniciais"]
	for k in e.stats: e.stats[k] = float(base[k])
	e.nivel = n; e.xp = 0
	e.pontos = (n - 1) * int(Defs.FORM["pontos_por_nivel"])
	Regras.recalc_jogador(e)
	e.hp = e.hp_max; e.rec = e.rec_max
	sim.emitir("nivel", {"id": e.id, "nivel": e.nivel, "skill_nova": ""})
	sim.emitir_a(e, "stats", {"id": e.id})

## Chefe de campo: o corpo e os números do chefe (combate/chefes.json), andando com a IA de monstro elite.
## Ao morrer solta o saque de chefe (tabela "drop" dele) para cada um que lutou.
func _chefe_de_campo(sim: WorldSim, kind: String, p: Vector2) -> Ent:
	var d: Dictionary = Defs.CHEFES[kind]
	var e := sim.criar_mob(kind, p, int(d.get("nivel", 30)))   # sem linha em mobs.json: curva base, ataque básico
	e.nome = str(d.get("nome", kind))
	e.hp_max = float(d.get("hp", e.hp_max)); e.hp = e.hp_max
	e.defesa = float(d.get("defesa", e.defesa))
	e.dano_min = float(d.get("dano_base", e.dano_min)) * 0.9; e.dano_max = float(d.get("dano_base", e.dano_max)) * 1.1
	e.intervalo = float(d.get("intervalo_ataque", e.intervalo)); e.vel = float(d.get("velocidade_mov", e.vel))
	e.postura_max = float(d.get("postura_max", e.postura_max)); e.postura = e.postura_max
	e.res = d.get("res", {}).duplicate(); e.tags = d.get("tags", []).duplicate()
	e.arquetipo = "elite"; e.raio = 0.9; e.alcance = 1.8; e.escala = 1.0
	e.raio_aggro = 8.0; e.raio_coleira = 30.0
	e.casa = p; e.aux["gm"] = true; e.aux["titulo"] = "Chefe invocado"
	return e

func _ligar(sim: WorldSim) -> void:
	if ligados.has(sim): return
	ligados[sim] = true
	sim.evento.connect(_ev_mundo.bind(sim))

func _ev_mundo(tipo: String, d: Dictionary, sim: WorldSim) -> void:
	if tipo != "morreu" or not chefes_gm.has(int(d.get("id", -1))): return
	var e: Ent = sim.ents.get(int(d["id"]))
	chefes_gm.erase(int(d["id"]))
	var killer: Ent = sim.ents.get(int(d.get("de", -1)))
	if killer != null and killer.tipo == "invocacao": killer = sim.ents.get(killer.dono)
	if e == null or killer == null or killer.tipo != "jogador": return
	e.tipo = "chefe"   # só durante o saque: Loot usa a tabela de chefe
	for j: Ent in sim.participantes(e, killer): Loot.dropar_mob(sim, e, j)
	e.tipo = "monstro"

## Reacende a luta de chefe do mapa (dungeon) do zero, com as mecânicas de verdade.
func _reviver_chefe(sim: WorldSim) -> String:
	if not sim.mapa.has("chefe") or sim.chefe == null or sim.chefe.has_method("comecar"): return "Este mapa não tem chefe de dungeon."
	var velho = sim.chefe
	if velho.estado != "morto" and velho.boss != null and velho.boss.vivo: return "O chefe ainda está de pé."
	for e: Ent in sim.ents.values().duplicate():
		if e.tipo == "chefe" or e.id in velho.pilhas or e.id in velho.coristas or e.id in velho.horda_ids: sim.remover(e.id)
	var c: Dictionary = sim.mapa["chefe"].duplicate(true)
	c.erase("derrotado")
	sim.chefe = ChefeCtl.new(sim, c)
	return "%s está de pé de novo." % sim.chefe.d.get("nome", "O chefe")

# =================================================================== estado para o painel
func _enviar_estado(peer: int) -> void:
	var lista: Array = []
	var agora := int(Time.get_unix_time_from_system())
	for p in srv.sessoes:
		var s: Dictionary = srv.sessoes[p]
		var j = s["jog"]
		if j == null: continue
		var c: Dictionary = srv.contas.get(str(s["u"]), {})
		lista.append({"nome": j.nome, "conta": s["u"], "classe": j.classe, "evolucao": j.evolucao, "nivel": j.nivel,
			"mapa": s["mapa"], "local": nome_mapa(s["mapa"]), "gm": str(s["u"]) in contas_gm,
			"mudo": int(c.get("mudo_ate", 0)) > agora, "vivo": j.vivo, "ouro": j.ouro})
	lista.sort_custom(func(x, y): return str(x["nome"]).naturalnocasecmp_to(str(y["nome"])) < 0)
	var eu: Ent = srv.sessoes[peer]["jog"]
	var hm = srv.hermon
	srv._para(peer, "gm_estado", {"jogadores": lista, "mapas": mapas, "mapas_ativos": srv.mundos.size(),
		"uptime": int((Time.get_ticks_msec() - inicio_ms) / 1000), "invisivel": eu.invisivel, "imortal": eu.aux.get("gm_imortal", false),
		"agrak_falta": maxi(0, srv.agrak.inicio - agora), "agrak_inscritos": srv.agrak.inscritos.size(), "agrak_min": srv.agrak.minimo,
		"hermon_falta": maxi(0, hm.proximo_inicio(agora) - agora), "hermon_aberto": hm.janela_aberta(agora) >= 0})

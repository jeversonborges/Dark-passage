extends RefCounted
## Troca entre jogadores, estilo MU: pedido pelo menu do botão direito no jogador, janela com os itens e o ouro
## dos dois lados, os dois confirmam e o servidor troca tudo de uma vez. O cliente só pede; quem decide é aqui.
##
## Contra dupe:
## - Nada sai da mochila durante a troca: a oferta só aponta para o item (uid) e guarda uma cópia para conferir.
## - Enquanto negocia, a mochila fica travada (usar, equipar, mover, jogar fora, vender, comprar, refinar).
## - Qualquer mudança na oferta desfaz as duas confirmações, e só dá para confirmar ESPERA_OK s depois dela.
## - Na hora de trocar, tudo é conferido de novo (mesmo item, mesma quantidade, ouro, espaço na mochila, distância)
##   antes de mexer em qualquer coisa; os itens que mudam de dono ganham uid novo; os dois personagens são salvos
##   juntos na mesma gravação do contas.json; cada troca vai para o registro user://servidor/trocas.log.

const W := 8                   # grade da oferta (8 x 4, como no MU)
const H := 4
const ALCANCE := 6.0           # tiles para pedir e aceitar
const ALCANCE_MAX := 10.0      # mais longe que isso a troca cai
const PEDIDO_MS := 20000
const ESPERA_OK := 3.0         # segundos depois de qualquer mudança até poder confirmar (golpe de última hora)
const OURO_MAX := 2000000000
const LOG := "user://servidor/trocas.log"
## comandos que mexem na mochila ou no ouro: recusados enquanto o jogador negocia
const TRAVADOS := ["usar_item", "equipar", "desequipar", "mover_item", "soltar_item", "comprar", "vender", "refinar", "redistribuir", "teleportar"]

var srv: Node                  # o servidor (sessoes, mundos, _para, _salvar_jog, _gravar_contas)
var pedidos := {}              # peer convidado -> {"de": peer, "t": ms}
var trocas := {}               # peer -> troca (o mesmo dicionário nos dois peers)
var prox_id := 1

func _init(servidor: Node) -> void:
	srv = servidor

func em_troca(peer: int) -> bool:
	return trocas.has(peer)

# =================================================================== mensagens
func receber(peer: int, m: Dictionary) -> void:
	match str(m.get("a", "")):
		"pedir": _pedir(peer, srv._peer_do_ent(int(m.get("id", -1))))
		"aceitar": _aceitar(peer)
		"recusar":
			var p: Dictionary = pedidos.get(peer, {})
			pedidos.erase(peer)
			if not p.is_empty(): _aviso(p["de"], "%s recusou a troca." % _nome(peer))
		"por":
			var x = m.get("x", -1); var y = m.get("y", -1); var uid = m.get("uid", -1)
			if uid is int and x is int and y is int: _por(peer, uid, x, y)
		"tirar":
			var uid2 = m.get("uid", -1)
			if uid2 is int: _tirar(peer, uid2)
		"ouro":
			var v = m.get("valor", 0)
			if v is int: _ouro(peer, v)
		"ok": _ok(peer)
		"cancelar":
			if trocas.has(peer): _cancelar(trocas[peer], "%s cancelou a troca." % _nome(peer))

func _pedir(peer: int, alvo: int) -> void:
	if alvo < 0 or alvo == peer: _aviso(peer, "Esse jogador não está online."); return
	if trocas.has(peer): _aviso(peer, "Você já está numa troca."); return
	if trocas.has(alvo) or pedidos.has(alvo): _aviso(peer, "%s está ocupado negociando." % _nome(alvo)); return
	var erro := _erro_par(peer, alvo, ALCANCE)
	if erro != "": _aviso(peer, erro); return
	pedidos[alvo] = {"de": peer, "t": Time.get_ticks_msec()}
	srv._para(alvo, "troca_pedido", {"de": _nome(peer)})
	_aviso(peer, "Pedido de troca enviado para %s." % _nome(alvo))

func _aceitar(peer: int) -> void:
	var p: Dictionary = pedidos.get(peer, {})
	pedidos.erase(peer)
	if p.is_empty() or Time.get_ticks_msec() - int(p["t"]) > PEDIDO_MS: _aviso(peer, "O pedido de troca expirou."); return
	var de: int = p["de"]
	if trocas.has(de) or trocas.has(peer): _aviso(peer, "%s já está noutra troca." % _nome(de)); return
	var erro := _erro_par(de, peer, ALCANCE)
	if erro != "": _aviso(peer, erro); return
	var agora := Time.get_ticks_msec()
	var t := {"id": prox_id, "a": de, "b": peer, "lado": {
		de: {"itens": [], "ouro": 0, "ok": false}, peer: {"itens": [], "ouro": 0, "ok": false}}, "mudou": agora}
	prox_id += 1
	trocas[de] = t; trocas[peer] = t
	for q in [de, peer]:
		var e: Ent = _jog(q)
		e.aux.erase("servico"); e.aux.erase("dialogo")   # loja/armazém abertos fecham: a mochila fica só para a troca
		Jogador.desligar_auto(_sim(q), e)
	_enviar(t)

## "" se os dois podem negociar agora; senão o motivo.
func _erro_par(a: int, b: int, alcance: float) -> String:
	var ea: Ent = _jog(a); var eb: Ent = _jog(b)
	if ea == null or eb == null: return "Esse jogador não está online."
	if not ea.vivo or not eb.vivo: return "Não dá para negociar com alguém caído."
	if srv.sessoes[a]["mapa"] != srv.sessoes[b]["mapa"] or ea.pos.distance_to(eb.pos) > alcance:
		return "Chegue mais perto de %s para negociar." % eb.nome
	return ""

# =================================================================== oferta
func _por(peer: int, uid: int, x: int, y: int) -> void:
	var t: Dictionary = trocas.get(peer, {})
	if t.is_empty(): return
	var e: Ent = _jog(peer)
	var it := Itens.por_uid(e.inv, uid)
	if it.is_empty(): return
	var motivo := pode_negociar(it)
	if motivo != "": _aviso(peer, motivo); return
	var lado: Dictionary = t["lado"][peer]
	var grade := _grade(lado)
	var prova := it.duplicate(true); prova["x"] = x; prova["y"] = y
	if not Itens.cabe_em(grade, W, H, prova, x, y, uid): return
	for o in lado["itens"]:
		if o["uid"] == uid: o["x"] = x; o["y"] = y; _mudou(t); return   # só mudou de lugar na janela
	lado["itens"].append({"uid": uid, "x": x, "y": y, "chave": _chave(it)})
	_mudou(t)

func _tirar(peer: int, uid: int) -> void:
	var t: Dictionary = trocas.get(peer, {})
	if t.is_empty(): return
	var lado: Dictionary = t["lado"][peer]
	for o in lado["itens"]:
		if o["uid"] == uid: lado["itens"].erase(o); _mudou(t); return

func _ouro(peer: int, v: int) -> void:
	var t: Dictionary = trocas.get(peer, {})
	if t.is_empty(): return
	var e: Ent = _jog(peer)
	v = clampi(v, 0, mini(e.ouro, OURO_MAX))
	if v == int(t["lado"][peer]["ouro"]): _enviar(t); return
	t["lado"][peer]["ouro"] = v
	_mudou(t)

func _ok(peer: int) -> void:
	var t: Dictionary = trocas.get(peer, {})
	if t.is_empty(): return
	if _espera(t) > 0.0: _enviar(t); return   # cliente apressado: só reenvia o estado
	t["lado"][peer]["ok"] = true
	var outro: int = t["b"] if peer == t["a"] else t["a"]
	if t["lado"][outro]["ok"]: _executar(t)
	else: _enviar(t)

## Desfaz as confirmações e reinicia a espera.
func _mudou(t: Dictionary) -> void:
	for p in t["lado"]: t["lado"][p]["ok"] = false
	t["mudou"] = Time.get_ticks_msec()
	_enviar(t)

func _espera(t: Dictionary) -> float:
	return maxf(0.0, ESPERA_OK - (Time.get_ticks_msec() - int(t["mudou"])) / 1000.0)

## Item de missão e item vinculado ("vinculado": true na definição) não trocam de dono.
static func pode_negociar(it: Dictionary) -> String:
	if it.get("id", "") == "_ouro": return "Ouro vai no campo de ouro."
	if Itens.categoria(it) == "missao": return "Item de missão não se negocia."
	if Itens.defn(it["id"]).get("vinculado", false): return "%s é vinculado a você." % Itens.nome(it)
	return ""

## O que identifica o item por inteiro (tirando a posição na mochila): se mudar, a oferta não vale mais.
static func _chave(it: Dictionary) -> String:
	var c := it.duplicate(true)
	c.erase("x"); c.erase("y")
	return var_to_str(c)

## A grade da oferta como lista de itens (com a posição na janela de troca).
func _grade(lado: Dictionary) -> Array:
	var out: Array = []
	for o in lado["itens"]:
		var it: Dictionary = str_to_var(o["chave"])
		it["uid"] = o["uid"]; it["x"] = o["x"]; it["y"] = o["y"]
		out.append(it)
	return out

# =================================================================== estado para os clientes
func _enviar(t: Dictionary) -> void:
	var esp := snappedf(_espera(t), 0.1)
	for p in [t["a"], t["b"]]:
		var o: int = t["b"] if p == t["a"] else t["a"]
		var eo: Ent = _jog(o)
		srv._para(p, "troca", {"id": t["id"], "espera": esp,
			"eu": {"itens": _grade(t["lado"][p]), "ouro": t["lado"][p]["ouro"], "ok": t["lado"][p]["ok"]},
			"outro": {"itens": _grade(t["lado"][o]), "ouro": t["lado"][o]["ouro"], "ok": t["lado"][o]["ok"],
				"nome": eo.nome if eo else "?", "classe": eo.classe if eo else "", "nivel": eo.nivel if eo else 0}})

func _fim(t: Dictionary, ok: bool, motivo: String) -> void:
	for p in [t["a"], t["b"]]:
		if trocas.get(p) == t: trocas.erase(p)
		srv._para(p, "troca_fim", {"ok": ok, "motivo": motivo})

func _cancelar(t: Dictionary, motivo: String) -> void:
	_fim(t, false, motivo)

# =================================================================== a troca de verdade
func _executar(t: Dictionary) -> void:
	var a: int = t["a"]; var b: int = t["b"]
	if _erro_par(a, b, ALCANCE_MAX) != "": _cancelar(t, "Troca cancelada: vocês se afastaram."); return
	var ea: Ent = _jog(a); var eb: Ent = _jog(b)
	# 1) confere tudo de novo, sem mexer em nada
	for p in [a, b]:
		var e: Ent = _jog(p)
		var lado: Dictionary = t["lado"][p]
		if int(lado["ouro"]) > e.ouro: _cancelar(t, "Troca cancelada: %s não tem esse ouro." % e.nome); return
		for o in lado["itens"]:
			var it := Itens.por_uid(e.inv, o["uid"])
			if it.is_empty() or _chave(it) != o["chave"] or pode_negociar(it) != "":
				_cancelar(t, "Troca cancelada: a oferta de %s mudou." % e.nome); return
	var oa: int = int(t["lado"][a]["ouro"]); var ob: int = int(t["lado"][b]["ouro"])
	if eb.ouro - ob + oa > OURO_MAX or ea.ouro - oa + ob > OURO_MAX: _cancelar(t, "Troca cancelada: ouro demais."); return
	# 2) ensaio: a mochila de cada um, sem o que sai, precisa caber o que entra
	var vai_a := _copias(ea, t["lado"][a]); var vai_b := _copias(eb, t["lado"][b])
	for par in [[ea, a, vai_b], [eb, b, vai_a]]:
		var ensaio: Array = _sem_oferta(par[0], t["lado"][par[1]]).duplicate(true)
		for it in par[2]:
			if Itens.guardar(ensaio, Itens.MOCHILA_W, Itens.MOCHILA_H, it.duplicate(true)) > 0:
				_cancelar(t, "Troca cancelada: a mochila de %s não tem espaço." % par[0].nome); return
	# 3) troca: tira as duas ofertas, passa o ouro, guarda os itens (com uid novo) na mochila do outro
	ea.inv = _sem_oferta(ea, t["lado"][a]); eb.inv = _sem_oferta(eb, t["lado"][b])
	ea.ouro += ob - oa; eb.ouro += oa - ob
	for par in [[ea, vai_b], [eb, vai_a]]:
		var e: Ent = par[0]
		for it in par[1]:
			var sobra := Itens.guardar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
			if sobra > 0:   # não deveria acontecer (o ensaio passou); nunca some item: vai para o chão do dono
				var resto: Dictionary = it.duplicate(true); resto["qtd"] = sobra
				srv.mundos[srv.sessoes[a]["mapa"]].soltar_no_chao(resto, e.pos, e.id, e.pos)
	for p in [a, b]:
		var e: Ent = _jog(p)
		var sim := _sim(p)
		sim.emitir_a(e, "inventario", {})
		sim.emitir_a(e, "som_evento", {"ev": "moedas"})
		Missoes.checar_coleta(sim, e)
	srv._salvar_jog(a, false); srv._salvar_jog(b, false)
	srv._gravar_contas()
	_registrar(t, ea, eb, vai_a, vai_b, oa, ob)
	_fim(t, true, "Troca concluída.")

## Cópias dos itens oferecidos, com uid novo (o item muda de dono; o uid velho morre com a oferta).
func _copias(e: Ent, lado: Dictionary) -> Array:
	var out: Array = []
	for o in lado["itens"]:
		var it: Dictionary = Itens.por_uid(e.inv, o["uid"]).duplicate(true)
		Itens._uid += 1
		it["uid"] = Itens._uid
		it.erase("x"); it.erase("y")
		out.append(it)
	return out

func _sem_oferta(e: Ent, lado: Dictionary) -> Array:
	var sai := {}
	for o in lado["itens"]: sai[o["uid"]] = true
	return e.inv.filter(func(it): return not sai.has(it["uid"]))

func _registrar(t: Dictionary, ea: Ent, eb: Ent, vai_a: Array, vai_b: Array, oa: int, ob: int) -> void:
	var desc := func(lst: Array, ouro: int) -> String:
		var p: Array = lst.map(func(it): return "%s x%d (%s, +%d)" % [it["id"], int(it.get("qtd", 1)), it.get("raridade", "comum"), int(it.get("refino", 0))])
		if ouro > 0: p.append("%d ouro" % ouro)
		return ", ".join(p) if not p.is_empty() else "nada"
	var linha := "%s troca %d: %s [%s] deu %s | %s [%s] deu %s" % [Time.get_datetime_string_from_system(), t["id"],
		ea.nome, srv.sessoes[t["a"]]["u"], desc.call(vai_a, oa), eb.nome, srv.sessoes[t["b"]]["u"], desc.call(vai_b, ob)]
	print("[troca] ", linha)
	var f := FileAccess.open(LOG, FileAccess.READ_WRITE) if FileAccess.file_exists(LOG) else FileAccess.open(LOG, FileAccess.WRITE)
	if f == null: return
	f.seek_end()
	f.store_line(linha)

# =================================================================== a cada meio segundo
## Derruba pedidos velhos e trocas que não valem mais; tira da oferta o que mudou na mochila (poção bebida etc.).
func passo() -> void:
	var agora := Time.get_ticks_msec()
	for alvo in pedidos.keys():
		if agora - int(pedidos[alvo]["t"]) > PEDIDO_MS: pedidos.erase(alvo)
	var vistas := {}
	for p in trocas.keys():
		if not trocas.has(p): continue
		var t: Dictionary = trocas[p]
		if vistas.has(t["id"]): continue
		vistas[t["id"]] = true
		var ea: Ent = _jog(t["a"]); var eb: Ent = _jog(t["b"])
		if ea == null or eb == null or not ea.vivo or not eb.vivo: _cancelar(t, "Troca cancelada."); continue
		if _erro_par(t["a"], t["b"], ALCANCE_MAX) != "": _cancelar(t, "Troca cancelada: vocês se afastaram."); continue
		var mudou := false
		for q in [t["a"], t["b"]]:
			var e: Ent = _jog(q)
			var lado: Dictionary = t["lado"][q]
			for o in lado["itens"].duplicate():
				var it := Itens.por_uid(e.inv, o["uid"])
				if it.is_empty() or _chave(it) != o["chave"]: lado["itens"].erase(o); mudou = true
			if int(lado["ouro"]) > e.ouro: lado["ouro"] = e.ouro; mudou = true
		if mudou: _mudou(t)

## Conexão caiu: a troca cai junto (nada saiu de mochila nenhuma, então não há o que devolver).
func desconectou(peer: int) -> void:
	pedidos.erase(peer)
	for k in pedidos.keys():
		if pedidos[k]["de"] == peer: pedidos.erase(k)
	if trocas.has(peer): _cancelar(trocas[peer], "Troca cancelada: %s saiu do jogo." % _nome(peer))

# =================================================================== atalhos
func _jog(peer: int) -> Ent:
	return srv.sessoes.get(peer, {}).get("jog")

func _sim(peer: int) -> WorldSim:
	return srv.mundos.get(srv.sessoes[peer]["mapa"])

func _nome(peer: int) -> String:
	var e := _jog(peer)
	return e.nome if e != null else "Alguém"

func _aviso(peer: int, txt: String) -> void:
	srv._para(peer, "aviso", {"texto": txt})

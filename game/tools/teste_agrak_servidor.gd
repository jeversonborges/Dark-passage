extends SceneTree
## Arena do Agrak no servidor (scripts/net/agrak.gd): inscrição, nível, ouro, cancelamento, começo com instância,
## volta para o mapa de origem e desconexão. Sem rede: um servidor de mentira com as mesmas funções.
## Uso: godot --headless --path . --script res://tools/teste_agrak_servidor.gd

const AgrakServidor := preload("res://scripts/net/agrak.gd")

class SrvFalso extends RefCounted:
	var sessoes := {}
	var mundos := {}
	var por_jog := {}
	var avisos: Array = []
	var salvos := 0
	func _para(peer: int, tipo: String, d: Dictionary) -> void:
		if tipo == "aviso": avisos.append([peer, d["texto"]])
	func _ev(_tipo: String, _d: Dictionary, _mapa: String) -> void: pass
	func _mundo(id: String) -> WorldSim:
		if not mundos.has(id):
			var s := WorldSim.new(3); s.carregar_mapa(id); mundos[id] = s
		return mundos[id]
	func _enviar_mapa(_peer: int, _novo := false) -> void: pass
	func _liberar_se_vazio(_id: String) -> void: pass
	func _salvar_jog(_peer: int, _gravar := true) -> void: salvos += 1

var falhas := 0

func check(cond: bool, msg: String) -> void:
	if not cond:
		falhas += 1
		print("[teste_agrak_servidor] FALHA ", msg)
	else:
		print("[teste_agrak_servidor] ok    ", msg)

func _gladiador(srv: SrvFalso, base: WorldSim, peer: int, nivel: int, ouro: int) -> Ent:
	var e := Jogador.criar(base, "humano", "P%d" % peer)
	e.nivel = nivel; e.ouro = ouro
	base.adicionar_jogador(e, Vector2(10, 10))
	srv.sessoes[peer] = {"u": "u%d" % peer, "jog": e, "mapa": "area_inicial", "saida": [], "idx": 0}
	srv.por_jog[e.id] = peer
	return e

func _initialize() -> void:
	Defs.carregar()
	var srv := SrvFalso.new()
	var base := WorldSim.new(5)
	base.carregar_mapa("area_inicial")
	srv.mundos["area_inicial"] = base
	var ag := AgrakServidor.new()
	ag.srv = srv

	# inscrição: janela fechada (19h), depois aberta (19h55)
	var caro := _gladiador(srv, base, 1, 25, 500)
	ag.agora_override = 19.0 * 3600
	ag.inscrever(1)
	check(ag.inscritos.is_empty(), "fora da janela não inscreve")
	ag.agora_override = 19.0 * 3600 + 55 * 60
	ag.inscrever(1)
	check(ag.inscritos.size() == 1 and caro.ouro == 400, "dentro da janela cobra 100 de ouro")
	ag.inscrever(1)
	check(ag.inscritos.size() == 1, "não inscreve duas vezes")
	var fraco := _gladiador(srv, base, 2, 10, 500)
	ag.inscrever(2)
	check(ag.inscritos.size() == 1 and fraco.ouro == 500, "nível 10 não entra")
	var pobre := _gladiador(srv, base, 3, 30, 50)
	ag.inscrever(3)
	check(ag.inscritos.size() == 1 and pobre.ouro == 50, "sem ouro não entra")
	var saida := _gladiador(srv, base, 4, 30, 300)
	ag.inscrever(4)
	ag.sair(4)
	check(saida.ouro == 300, "quem sai antes do começo recebe o ouro de volta")
	for p in [5, 6, 7]:
		var g := _gladiador(srv, base, p, 30, 300)
		ag.inscrever(p)

	# começo: 20h. Com 4 inscritos, abre uma instância
	ag.agora_override = 20.0 * 3600 + 1
	ag.passo(0.1)
	check(ag.instancias.size() == 1, "20h abre uma instância")
	check(ag.inscritos.is_empty(), "a lista de inscritos zera ao começar")
	var id: String = ag.instancias.keys()[0]
	check(srv.sessoes[1]["mapa"] == id, "inscrito vai para a instância")
	check(srv.mundos[id].mapa_id == "agrak", "instância usa o mapa agrak")
	var ag_mundo: AgrakMundo = ag.instancias[id]
	check(ag_mundo.jogadores_ids.size() == 4, "quatro gladiadores na instância")
	check(srv.sessoes[1]["jog"].aux.get("agrak_volta", {}).get("mapa", "") == "area_inicial", "volta para area_inicial")

	# desconectou dentro da luta: eliminado
	var sai := int(srv.sessoes[5]["jog"].id)
	ag.saiu(sai)
	check(not ag_mundo.ctl.vivos.has(sai), "desconectou conta como eliminado")

	# fim: todos voltam ao mapa de origem e a instância some
	ag_mundo.encerrar()
	ag.passo(0.1)
	check(ag.instancias.is_empty(), "instância fechada")
	check(srv.sessoes[1]["mapa"] == "area_inicial", "volta para o mapa de origem")
	check(not srv.mundos.has(id), "a instância sai do servidor")

	# cancelado: 3 inscritos abaixo do mínimo, todos recebem o ouro de volta
	var a := _gladiador(srv, base, 10, 30, 300)
	var b := _gladiador(srv, base, 11, 30, 300)
	var c := _gladiador(srv, base, 12, 30, 300)
	ag.agora_override = 21.0 * 3600 + 58 * 60
	ag.inscrever(10); ag.inscrever(11); ag.inscrever(12)
	ag.agora_override = 22.0 * 3600 + 1
	ag.passo(0.1)
	check(ag.instancias.is_empty(), "com 3 inscritos não começa")
	check(a.ouro == 300 and b.ouro == 300 and c.ouro == 300, "cancelado devolve o ouro")

	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

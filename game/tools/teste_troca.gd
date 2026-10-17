extends SceneTree
## Teste da troca entre jogadores (scripts/net/troca.gd), sem rede: dois jogadores num servidor de mentira.
## Uso: godot --headless --path . --script res://tools/teste_troca.gd
## Confere a troca normal e as tentativas de dupe/golpe; no fim, itens e ouro dos dois somados não podem mudar.

const Servidor := preload("res://scripts/net/servidor.gd")

class RedeFalsa extends Node:
	const VERSAO := "teste"
	var caixa := {}   # peer -> [mensagens]
	func enviar(peer: int, m: Dictionary) -> void:
		if not caixa.has(peer): caixa[peer] = []
		caixa[peer].append(m)
	func ip_do_peer(_p: int) -> String: return "local"

var srv
var falhas := 0
var A := 2
var B := 3

func _initialize() -> void:
	Defs.carregar()
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://servidor/contas.json"))
	var rede := RedeFalsa.new()
	root.add_child(rede)
	srv = Servidor.new()
	srv.rede = rede
	srv.contas_pelo_site = false
	root.add_child(srv)
	for par in [[A, "ana", "Ana"], [B, "bia", "Bia"]]:
		srv.receber(par[0], {"t": "cadastro", "v": "teste", "u": par[1], "h": "a".repeat(64)})
		srv.receber(par[0], {"t": "criar", "classe": "humano", "nome": par[2]})
	var ea: Ent = srv.sessoes[A]["jog"]; var eb: Ent = srv.sessoes[B]["jog"]
	var sim: WorldSim = srv.mundos[srv.sessoes[A]["mapa"]]
	ea.inv.clear(); eb.inv.clear()
	ea.ouro = 1000; eb.ouro = 50
	eb.pos = ea.pos + Vector2(2, 0)
	Jogador.dar_item(sim, ea, Itens.novo("espada_vigilia_rachada"))
	Jogador.dar_item(sim, ea, Itens.novo("pocao_vida_p", 7))
	Jogador.dar_item(sim, eb, Itens.novo("escudo_porta_capela"))
	Jogador.dar_item(sim, eb, Itens.novo("pena_querubim"))
	var total0 := _total(ea, eb)
	var espada: int = _uid(ea, "espada_vigilia_rachada"); var pocoes: int = _uid(ea, "pocao_vida_p")
	var escudo: int = _uid(eb, "escudo_porta_capela"); var pena: int = _uid(eb, "pena_querubim")

	# 1) longe demais não pede
	eb.pos = ea.pos + Vector2(30, 0)
	_t(A, "pedir", {"id": eb.id})
	_ok(not srv.troca.pedidos.has(B), "longe: pedido recusado")
	eb.pos = ea.pos + Vector2(2, 0)
	# 2) pedido e aceite
	_t(A, "pedir", {"id": eb.id})
	_ok(_evento(B, "troca_pedido"), "B recebeu o pedido")
	_t(B, "aceitar")
	_ok(srv.troca.em_troca(A) and srv.troca.em_troca(B), "troca aberta nos dois")
	var t: Dictionary = srv.troca.trocas[A]
	# 3) item de missão não entra
	_t(B, "por", {"uid": pena, "x": 0, "y": 0})
	_ok(t["lado"][B]["itens"].is_empty(), "item de missão recusado")
	# 4) ofertas
	_t(A, "por", {"uid": espada, "x": 0, "y": 0})
	_t(A, "por", {"uid": pocoes, "x": 1, "y": 0})
	_t(A, "por", {"uid": pocoes, "x": 0, "y": 0})   # em cima da espada: não cabe
	_ok(t["lado"][A]["itens"].size() == 2 and t["lado"][A]["itens"][1]["x"] == 1, "item que não cabe na grade é recusado")
	_t(B, "por", {"uid": escudo, "x": 0, "y": 0})
	_t(B, "ouro", {"valor": 999999})
	_ok(t["lado"][B]["ouro"] == 50, "ouro acima do que tem vira o máximo (50)")
	# 5) confirmar antes da espera não vale
	_t(A, "ok")
	_ok(not t["lado"][A]["ok"], "confirmar logo depois de mudar é recusado")
	t["mudou"] -= 4000
	_t(A, "ok")
	_ok(t["lado"][A]["ok"], "A confirmou depois da espera")
	# 6) B muda a oferta: a confirmação de A cai
	_t(B, "ouro", {"valor": 40})
	_ok(not t["lado"][A]["ok"], "mudança desfaz a confirmação do outro")
	# 7) mochila travada durante a troca
	srv.receber(A, {"t": "cmd", "n": "soltar_item", "a": [espada]})
	srv.receber(A, {"t": "cmd", "n": "vender", "a": [espada]})
	_ok(not Itens.por_uid(ea.inv, espada).is_empty(), "jogar fora/vender item oferecido é recusado")
	# 8) bebeu poção da pilha oferecida: sai da oferta (não troca o que não tem mais)
	Itens.por_uid(ea.inv, pocoes)["qtd"] = 6
	srv.troca.passo()
	_ok(t["lado"][A]["itens"].size() == 1, "pilha que mudou sai da oferta")
	Itens.por_uid(ea.inv, pocoes)["qtd"] = 7
	_t(A, "por", {"uid": pocoes, "x": 1, "y": 0})
	# 9) troca de verdade
	t["mudou"] -= 4000
	_t(A, "ok"); _t(B, "ok")
	_ok(not srv.troca.em_troca(A) and not srv.troca.em_troca(B), "troca concluída e fechada")
	_ok(_uid(eb, "espada_vigilia_rachada") >= 0 and _uid(ea, "espada_vigilia_rachada") < 0, "espada mudou de dono")
	_ok(Itens.contar(eb.inv, "pocao_vida_p") == 7 and Itens.contar(ea.inv, "pocao_vida_p") == 0, "7 poções mudaram de dono")
	_ok(_uid(ea, "escudo_porta_capela") >= 0 and _uid(eb, "escudo_porta_capela") < 0, "escudo mudou de dono")
	_ok(ea.ouro == 1040 and eb.ouro == 10, "ouro passou (A 1040, B 10): A %d B %d" % [ea.ouro, eb.ouro])
	_ok(_uid(eb, "espada_vigilia_rachada") != espada, "item trocado ganhou uid novo")
	_ok(_total(ea, eb) == total0, "nada foi criado nem sumiu")
	var salvo_b: Dictionary = srv.contas["bia"]["personagens"][0]
	_ok(salvo_b["inv"].any(func(it): return it["id"] == "espada_vigilia_rachada"), "troca já gravada no contas.json")
	# 10) mochila cheia: cancela sem mexer em nada
	_abrir()
	t = srv.troca.trocas[A]
	var cheio: Array = []
	for i in Itens.MOCHILA_W * Itens.MOCHILA_H: cheio.append({"uid": 90000 + i, "id": "pena_querubim", "qtd": 1, "x": i % Itens.MOCHILA_W, "y": i / Itens.MOCHILA_W, "refino": 0, "opcoes": [], "raridade": "comum"})
	var inv_b_antes: Array = eb.inv
	eb.inv = cheio
	_t(A, "por", {"uid": _uid(ea, "escudo_porta_capela"), "x": 0, "y": 0})
	t["mudou"] -= 4000
	_t(A, "ok"); _t(B, "ok")
	_ok(_uid(ea, "escudo_porta_capela") >= 0, "mochila cheia: troca cancelada e escudo ficou com A")
	_ok(_evento(A, "troca_fim"), "A soube do cancelamento")
	eb.inv = inv_b_antes
	# 11) caiu a conexão no meio: cancela, nada some
	_abrir()
	_t(B, "por", {"uid": _uid(eb, "espada_vigilia_rachada"), "x": 0, "y": 0})
	srv.desconectou(B)
	_ok(not srv.troca.em_troca(A), "desconectar cancela a troca")
	_ok(srv.contas["bia"]["personagens"][0]["inv"].any(func(it): return it["id"] == "espada_vigilia_rachada"), "espada continua com B no save")
	print("[teste_troca] ", "TUDO CERTO" if falhas == 0 else "%d FALHAS" % falhas)
	quit(1 if falhas > 0 else 0)

func _abrir() -> void:
	var ea: Ent = srv.sessoes[A]["jog"]; var eb: Ent = srv.sessoes[B]["jog"]
	_t(A, "pedir", {"id": eb.id}); _t(B, "aceitar")

func _t(peer: int, a: String, extra := {}) -> void:
	var m := {"t": "troca", "a": a}
	m.merge(extra)
	srv.receber(peer, m)

func _evento(peer: int, tipo: String) -> bool:
	for ev in srv.sessoes.get(peer, {}).get("saida", []):
		if ev[0] == tipo: return true
	return false

func _uid(e: Ent, id: String) -> int:
	for it in e.inv:
		if it["id"] == id: return int(it["uid"])
	return -1

func _total(ea: Ent, eb: Ent) -> String:
	var n := {}
	for it in ea.inv + eb.inv: n[it["id"]] = n.get(it["id"], 0) + int(it["qtd"])
	var k := n.keys(); k.sort()
	return "%s ouro=%d" % [str(k.map(func(x): return "%s:%d" % [x, n[x]])), ea.ouro + eb.ouro]

func _ok(cond: bool, txt: String) -> void:
	print("[teste_troca] %s %s" % ["ok   " if cond else "FALHA", txt])
	if not cond: falhas += 1

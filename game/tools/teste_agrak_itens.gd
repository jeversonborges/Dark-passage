extends SceneTree
## Teste dos dados e da loja do Agrak (itens, conjunto, Banca do Pedro), sem rede.
## Uso: /opt/godot/godot --headless --path . -s tools/teste_agrak_itens.gd
## Confere: itens carregados, ficha vinculada e moeda, bônus de conjunto (2/3/5 peças),
## compra com fichas (o servidor tira as fichas), e que a ficha não vende nem cai no chão.

const Servidor := preload("res://scripts/net/servidor.gd")

class RedeFalsa extends Node:
	const VERSAO := "teste"
	var caixa := {}
	func enviar(peer: int, m: Dictionary) -> void:
		if not caixa.has(peer): caixa[peer] = []
		caixa[peer].append(m)
	func ip_do_peer(_p: int) -> String: return "local"

const IDS_NOVOS := ["ficha_sangue", "agrak_elmo", "agrak_peito", "agrak_luvas", "agrak_calcas", "agrak_botas",
	"agrak_arma_anjo", "agrak_arma_cultista", "agrak_arma_demonio", "agrak_arma_humano", "agrak_arma_mutante", "agrak_arma_tecnomancer"]
const PECAS := ["agrak_elmo", "agrak_peito", "agrak_luvas", "agrak_calcas", "agrak_botas"]

var falhas := 0

func _ok(cond: bool, txt: String) -> void:
	print("[teste_agrak_itens] %s %s" % ["ok   " if cond else "FALHA", txt])
	if not cond: falhas += 1

func _equip(pecas: Array) -> Dictionary:
	var eq := {}
	var slot := {"agrak_elmo": "cabeca", "agrak_peito": "peito", "agrak_luvas": "luvas", "agrak_calcas": "calcas", "agrak_botas": "botas"}
	for p in pecas: eq[slot[p]] = Itens.novo(p)
	return eq

func _initialize() -> void:
	Defs.carregar()

	# 1. itens existem
	for id in IDS_NOVOS:
		_ok(Defs.ITENS.has(id), "item %s carregado" % id)
	_ok(Defs.ITENS.has("agrak_arma_anjo") and Defs.ITENS.has("agrak_arma_tecnomancer"), "uma arma do Agrak por classe (6)")

	# 2. ficha
	var f: Dictionary = Defs.ITENS.get("ficha_sangue", {})
	_ok(f.get("tipo") == "moeda", "ficha_sangue é tipo moeda")
	_ok(f.get("vinculado", false) == true, "ficha_sangue é vinculada")
	_ok(int(f.get("pilha", 0)) == 99, "ficha_sangue empilha 99")

	# 3. conjunto
	var cj := Itens.conjunto_def("couraca_do_agrak")
	_ok(not cj.is_empty(), "conjunto couraca_do_agrak carregado")
	_ok(cj.get("pecas", []) == PECAS, "conjunto tem as 5 peças certas")

	# 4. bônus de conjunto (dano recebido de jogadores = -0.04 por peça, +hp do elmo e do conjunto)
	var b2 := Itens.bonus(_equip(PECAS.slice(0, 2)))
	_ok(absf(float(b2["hp"]) - (60.0)) < 0.001, "2 peças: só hp do elmo (60), sem bônus de conjunto")
	var b3 := Itens.bonus(_equip(PECAS.slice(0, 3)))
	_ok(absf(float(b3["hp"]) - 210.0) < 0.001, "3 peças: hp +150 do conjunto (210 no total)")
	_ok(absf(float(b3["dano_recebido_jogadores"]) - (-0.12)) < 0.0001, "3 peças: -4% por peça (-0.12), sem o -5%")
	var b5 := Itens.bonus(_equip(PECAS))
	_ok(absf(float(b5["hp"]) - 210.0) < 0.001, "5 peças: hp continua 210 (faixa de 3 segue valendo)")
	_ok(absf(float(b5["dano_recebido_jogadores"]) - (-0.25)) < 0.0001, "5 peças: -0.20 das peças + -0.05 do conjunto = -0.25")
	var ba := Itens.bonus({"arma": Itens.novo("agrak_arma_anjo")})
	_ok(absf(float(ba["dano_em_jogadores"]) - 0.08) < 0.0001, "arma do Agrak: dano em jogadores +0.08")

	# 5. loja e preços
	var lp: Dictionary = Defs.LOJAS.get("loja_pedro", {})
	_ok(lp.get("moeda") == "ficha_sangue", "loja_pedro cobra em ficha_sangue")
	_ok(Itens.preco_na_loja(Itens.novo("agrak_peito"), lp) == 4, "armadura custa 4 fichas")
	_ok(Itens.preco_na_loja(Itens.novo("agrak_arma_humano"), lp) == 10, "arma custa 10 fichas")
	var na_loja: Array = lp.get("itens", [])
	_ok(na_loja.size() == 11 and "agrak_arma_mutante" in na_loja and "agrak_elmo" in na_loja, "loja_pedro vende 5 peças + 6 armas")

	# 6. compra, venda e descarte com servidor de mentira
	var srv
	var rede := RedeFalsa.new()
	root.add_child(rede)
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://servidor/contas.json"))
	srv = Servidor.new()
	srv.rede = rede
	srv.contas_pelo_site = false
	root.add_child(srv)
	srv.receber(2, {"t": "cadastro", "v": "teste", "u": "ana", "h": "a".repeat(64)})
	srv.receber(2, {"t": "criar", "classe": "humano", "nome": "Ana"})
	var ea: Ent = srv.sessoes[2]["jog"]
	var sim: WorldSim = srv.mundos[srv.sessoes[2]["mapa"]]
	ea.inv.clear(); ea.equip.clear()
	ea.nivel = 25
	ea.aux["servico"] = {"tipo": "loja", "id": "loja_pedro"}
	ea.ouro = 500

	Jogador.dar_item(sim, ea, Itens.novo("ficha_sangue", 10))
	Jogador.comprar(sim, ea, "agrak_peito", 1)
	_ok(Itens.contar(ea.inv, "ficha_sangue") == 6, "compra de armadura tira 4 fichas (sobram 6)")
	_ok(Itens.contar(ea.inv, "agrak_peito") == 1, "armadura comprada entra na mochila")
	_ok(ea.ouro == 500, "compra com fichas não mexe no ouro")

	Jogador.comprar(sim, ea, "agrak_arma_humano", 1)
	_ok(Itens.contar(ea.inv, "ficha_sangue") == 6, "sem fichas suficientes (arma 10) a compra falha")
	_ok(Itens.contar(ea.inv, "agrak_arma_humano") == 0, "compra recusada não entrega a arma")

	Jogador.comprar(sim, ea, "agrak_arma_anjo", 1)
	_ok(Itens.contar(ea.inv, "agrak_arma_anjo") == 0, "arma de outra classe não aparece na loja do humano")

	var ficha_uid := -1
	for it in ea.inv:
		if it["id"] == "ficha_sangue": ficha_uid = it["uid"]
	Jogador.vender(sim, ea, ficha_uid)
	_ok(Itens.contar(ea.inv, "ficha_sangue") == 6, "ficha não vende na loja")
	Jogador.soltar_item(sim, ea, ficha_uid)
	_ok(Itens.contar(ea.inv, "ficha_sangue") == 6, "ficha não pode ser jogada fora")

	print("[teste_agrak_itens] ", "TUDO CERTO" if falhas == 0 else "%d FALHAS" % falhas)
	print("FALHAS: %d" % falhas)
	quit(1 if falhas > 0 else 0)

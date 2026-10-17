class_name Teleporte
## Menu de Teleporte (tecla V): leva a qualquer área de caça que o jogo já tem, pelo preço de 1 Lágrima Sanguínea.
## Os destinos vêm de data/teleporte.json (gerado por entregas/teleporte/gerar.py a partir dos mapas).
## Tudo é decidido aqui, no servidor: nível, flag, item e canal (a troca trava o comando em net/troca.gd TRAVADOS). O cliente só mostra a lista e manda o id.
## A volta ao acampamento (R, Vela) continua grátis e não passa por aqui.

const ARQUIVO := "res://data/teleporte.json"
static var _dados := {}

static func dados() -> Dictionary:
	if _dados.is_empty():
		_dados = Defs.ler(ARQUIVO)
		if _dados.is_empty(): _dados = {"destinos": [], "custo": {"item": "lagrima_sanguinea", "qtd": 1}, "canal_s": 3.0}
	return _dados

static func destinos() -> Array:
	return dados().get("destinos", [])

static func destino(id: String) -> Dictionary:
	for d: Dictionary in destinos():
		if str(d.get("id", "")) == id: return d
	return {}

static func custo(d: Dictionary) -> Dictionary:
	return d.get("custo", dados().get("custo", {"item": "lagrima_sanguinea", "qtd": 1}))

## Por que este jogador não pode ir agora ("" = pode). O cliente usa a mesma regra para apagar as linhas.
static func bloqueio(sim: WorldSim, e: Ent, d: Dictionary) -> String:
	if d.is_empty(): return "Destino desconhecido."
	if e.nivel < int(d.get("nivel_min", 1)): return "Precisa do nível %d." % int(d.get("nivel_min", 1))
	if d.has("requer_flag") and not e.flags.has(str(d["requer_flag"])): return str(d.get("texto_trancado", "Ainda fechado para você."))
	var c := custo(d)
	if Itens.contar(e.inv, str(c["item"])) < int(c["qtd"]): return "Precisa de %d %s." % [int(c["qtd"]), _nome_item(str(c["item"]), int(c["qtd"]))]
	if sim != null and sim.chefe != null and sim.chefe.porta_fechada(): return "A grade não abre enquanto o chefe estiver vivo."
	return ""

static func _nome_item(id: String, qtd: int) -> String:
	var n := str(Defs.ITENS.get(id, {}).get("nome", "Lágrima Sanguínea"))
	return n if qtd == 1 else n.replace("Lágrima", "Lágrimas")

## Comando "teleportar" [id]: confere tudo, canaliza parado (apanhar cancela) e só gasta a lágrima quando o canal termina.
static func pedir(sim: WorldSim, e: Ent, id: String) -> void:
	if not e.vivo or e.interagindo.has("t"): return
	var d := destino(id)
	var motivo := bloqueio(sim, e, d)
	if motivo != "":
		sim.emitir_a(e, "aviso", {"texto": motivo}); return
	Jogador.canalizar(sim, e, float(dados().get("canal_s", 3.0)), "Viajando para %s" % str(d["nome"]), func():
		var m2 := bloqueio(sim, e, d)   # pode ter vendido ou soltado a lágrima durante o canal
		if m2 != "":
			sim.emitir_a(e, "aviso", {"texto": m2}); return
		var c := custo(d)
		Itens.remover(e.inv, str(c["item"]), int(c["qtd"]))
		sim.emitir_a(e, "inventario", {})
		sim.emitir_a(e, "log", {"texto": "A Lágrima Sanguínea se desfaz em fumaça vermelha."})
		var p: Array = d["pos"]
		sim.emitir_a(e, "trocar_mapa", {"mapa": str(d["mapa"]), "pos": Vector2(float(p[0]), float(p[1]))}))

class_name Teleporte
## Menu de Teleporte (tecla V): leva a qualquer área de caça que o jogo já tem por 3.000 de ouro (Jefin, 17/10).
## Os destinos vêm de data/teleporte.json (gerado por entregas/teleporte/gerar.py a partir dos mapas).
## Tudo é decidido aqui, no servidor: nível, flag, ouro e canal (a troca trava o comando em net/troca.gd TRAVADOS). O cliente só mostra a lista e manda o id.
## A volta ao acampamento (R, Vela) continua grátis e não passa por aqui.

const ARQUIVO := "res://data/teleporte.json"
const PRECO_PADRAO := 3000
static var _dados := {}

static func dados() -> Dictionary:
	if _dados.is_empty():
		_dados = Defs.ler(ARQUIVO)
		if _dados.is_empty(): _dados = {"destinos": [], "custo": {"ouro": PRECO_PADRAO}, "canal_s": 3.0}
	return _dados

static func destinos() -> Array:
	return dados().get("destinos", [])

static func destino(id: String) -> Dictionary:
	for d: Dictionary in destinos():
		if str(d.get("id", "")) == id: return d
	return {}

## Preço em ouro da viagem (o destino pode ter preço próprio; senão vale o geral do arquivo).
static func preco(d: Dictionary) -> int:
	var c: Dictionary = d.get("custo", dados().get("custo", {}))
	return int(c.get("ouro", PRECO_PADRAO))

## Por que este jogador não pode ir agora ("" = pode). O cliente usa a mesma regra para apagar as linhas.
static func bloqueio(sim: WorldSim, e: Ent, d: Dictionary) -> String:
	if d.is_empty(): return "Destino desconhecido."
	if e.nivel < int(d.get("nivel_min", 1)): return "Precisa do nível %d." % int(d.get("nivel_min", 1))
	if d.has("requer_flag") and not e.flags.has(str(d["requer_flag"])): return str(d.get("texto_trancado", "Ainda fechado para você."))
	if e.ouro < preco(d): return "A viagem custa %d de ouro." % preco(d)
	if sim != null and sim.chefe != null and sim.chefe.porta_fechada(): return "A grade não abre enquanto o chefe estiver vivo."
	return ""

## Comando "teleportar" [id]: confere tudo, canaliza parado (apanhar cancela) e só cobra o ouro quando o canal termina.
static func pedir(sim: WorldSim, e: Ent, id: String) -> void:
	if not e.vivo or e.interagindo.has("t"): return
	var d := destino(id)
	var motivo := bloqueio(sim, e, d)
	if motivo != "":
		sim.emitir_a(e, "aviso", {"texto": motivo}); return
	Jogador.canalizar(sim, e, float(dados().get("canal_s", 3.0)), "Viajando para %s" % str(d["nome"]), func():
		var m2 := bloqueio(sim, e, d)   # pode ter gastado o ouro durante o canal
		if m2 != "":
			sim.emitir_a(e, "aviso", {"texto": m2}); return
		var p_ouro := preco(d)
		e.ouro -= p_ouro
		sim.emitir_a(e, "ouro", {"valor": -p_ouro})
		sim.emitir_a(e, "inventario", {})
		var p: Array = d["pos"]
		sim.emitir_a(e, "trocar_mapa", {"mapa": str(d["mapa"]), "pos": Vector2(float(p[0]), float(p[1]))}))

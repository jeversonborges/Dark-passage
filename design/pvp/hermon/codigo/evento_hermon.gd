class_name EventoHermon
extends RefCounted
## Servidor: agenda do evento "O Cume dos Vigilantes", janela de entrada (5 min) e uso do Convite dos Vigilantes.
## Só decide; quem move jogador e cria instância é o servidor.gd (ver LEIAME.md, "Integração").
## Horário de Brasília = UTC-3 (sem horário de verão desde 2019).

const FUSO_S := -3 * 3600
const MAPA := "cume_dos_vigilantes"

var ev: Dictionary
var instancias := {}           # "f<faixa>" -> [{id, jogadores:[ids]}] da subida atual
var subida_atual := -1         # unix do início da janela em curso (-1 = fechada)
var _ultimo_aviso := {}        # minuto -> unix da subida avisada

func _init(p_ev: Dictionary) -> void:
	ev = p_ev

static func _hm(s: String) -> int:
	var p := s.split(":")
	return int(p[0]) * 3600 + int(p[1]) * 60

## Próximo início (unix, UTC) a partir de agora (inclusive).
func proximo_inicio(agora: int) -> int:
	var local := agora + FUSO_S
	var dia0 := local - posmod(local, 86400)
	var melhor := -1
	for d in 2:
		for h in ev["agenda"]["diario"]:
			var u := dia0 + d * 86400 + _hm(h) - FUSO_S
			if u >= agora and (melhor < 0 or u < melhor): melhor = u
	return melhor

## Início da janela em curso (se a entrada está aberta agora) ou -1.
func janela_aberta(agora: int) -> int:
	var ini := proximo_inicio(agora - int(ev["entrada"]["janela_s"]) + 1)
	if ini >= 0 and ini <= agora and agora < ini + int(ev["entrada"]["janela_s"]): return ini
	return -1

func resta_entrada(agora: int) -> int:
	var ini := janela_aberta(agora)
	return ini + int(ev["entrada"]["janela_s"]) - agora if ini >= 0 else 0

## Chamado a cada segundo pelo servidor: devolve os avisos de sistema a mandar para todos agora.
func avisos(agora: int) -> Array:
	var out: Array = []
	var ini := proximo_inicio(agora)
	for m in ev["avisos_min_antes"]:
		var falta := ini - agora
		if falta <= int(m) * 60 and falta > int(m) * 60 - 60 and _ultimo_aviso.get(m, -1) != ini:
			_ultimo_aviso[m] = ini
			out.append("O Hermon chama em %d min. Tenha um Convite dos Vigilantes na mochila." % int(m))
	var ab := janela_aberta(agora)
	if ab >= 0 and subida_atual != ab:
		subida_atual = ab; instancias.clear()
		out.append(ev["falas"]["abriu"])
	elif ab < 0 and subida_atual >= 0:
		subida_atual = -1
	return out

func faixa_de(nivel: int) -> int:
	var fs: Array = ev["faixas"]
	for i in fs.size():
		if nivel >= int(fs[i]["niveis"][0]) and nivel <= int(fs[i]["niveis"][1]): return i
	return -1

func nivel_mob(faixa: int) -> int:
	return int(ev["faixas"][faixa]["nivel_mob"])

## O jogador clicou no convite. Devolve {ok, texto, gasta, instancia, faixa, nivel_mob, resta}.
## onde: "mundo" | "dungeon" | "evento" | "chefe" (o servidor diz onde ele está).
func usar_convite(nivel: int, agora: int, onde: String = "mundo", ja_dentro: bool = false) -> Dictionary:
	if ja_dentro: return {"ok": false, "gasta": false, "texto": "Você já está no cume."}
	var ab := janela_aberta(agora)
	if ab < 0:
		var falta := proximo_inicio(agora) - agora
		return {"ok": false, "gasta": false, "texto": "O lacre não rompe. O Hermon chama de novo em %s." % _tempo(falta)}
	if nivel < int(ev["entrada"]["nivel_min"]):
		return {"ok": false, "gasta": false, "texto": "Só a partir do nível %d." % int(ev["entrada"]["nivel_min"])}
	if onde != "mundo":
		return {"ok": false, "gasta": false, "texto": "Saia da dungeon ou do evento antes de romper o lacre."}
	var f := faixa_de(nivel)
	var k := "f%d" % f
	var lista: Array = instancias.get(k, [])
	if lista.is_empty() or (lista[-1]["n"] as int) >= int(ev["entrada"]["max_por_cume"]):
		lista.append({"id": "%s#%d-%d-%d" % [MAPA, ab, f, lista.size() + 1], "n": 0})
		instancias[k] = lista
	lista[-1]["n"] = int(lista[-1]["n"]) + 1
	return {"ok": true, "gasta": true, "instancia": lista[-1]["id"], "faixa": f, "nivel_mob": nivel_mob(f),
		"resta": ab + int(ev["entrada"]["janela_s"]) - agora, "texto": "O lacre se rompe. O vento te leva ao cume."}

static func _tempo(s: int) -> String:
	if s >= 3600: return "%dh%02d" % [s / 3600, (s % 3600) / 60]
	return "%d min" % maxi(1, (s + 59) / 60)

## Id do arquivo de mapa de uma instância ("cume_dos_vigilantes#<subida>-<faixa>-<n>" -> "cume_dos_vigilantes").
static func mapa_base(id: String) -> String:
	return id.get_slice("#", 0)

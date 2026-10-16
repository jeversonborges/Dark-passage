class_name AgrakCtl
extends RefCounted
## Controlador da Arena do Agrak (data/design/pvp/agrak.json): etapas, chamada, lutas, Anel do Amargo e premio.
## Não conhece o mundo. Fala com o dono (host) por métodos, então roda sem rede e sem nós (tools/teste_agrak.gd).
## O host implementa: etapa(id, dur), prender(ids), fala(quem, texto), portao(id, aberto), spawn_chefe(id, hp),
## recuar_chefes(), recuperar(ids, frac), trancar_pocoes(bool), definir_lados(mapa), anel(raio),
## fora_do_anel(id, raio) -> bool, dano_anel(id, frac_hp), espectador(id), premiar(id, qtd),
## hp_frac(id) -> float, cancelar(ids), encerrar().

const FALAS := {
	"chamada_caim": "SENHORAS, SENHORES E COISAS QUE UM DIA FORAM GENTE! BEM-VINDOS AO AGRAK!",
	"chamada_abel": "Ele ensaiou isso a semana toda.",
	"leoes_caim": "SOLTEM OS LEÕES!",
	"leoes_abel": "Eles não comem desde a última trombeta. Nem eu.",
	"golias_caim": "ELE GIRA, VOCÊS SANGRAM. GOOOLIAS!",
	"golias_abel": "Já foi gente. Igual a nós. Mais ou menos.",
	"gigante_morto_caim": "DERRUBARAM O GIGANTE!",
	"gigante_morto_abel": "Agora a parte que a plateia pagou pra ver: um contra o outro.",
	"anel_caim": "O AMARGO TÁ ENTRANDO!",
	"anel_abel": "Andem logo, que a plateia tem hora.",
	"sem_vencedor_caim": "O AGRAK COMEU TODO MUNDO!",
	"sem_vencedor_abel": "Voltem amanhã com mais carne.",
	"vencedor_abel": "Uma Ficha de Sangue. Leve ao Pedro antes que alguém leve você.",
}

var d: Dictionary
var host
var etapas: Array = []
var idx := -1                   # etapa atual (-1 = parado)
var t := 0.0                    # tempo dentro da etapa
var inscritos: Array = []       # ids que entraram (não mudam)
var vivos: Array = []           # gladiadores ainda na luta
var chefes_vivos: Array = []    # ids dos chefes desta luta
var vencedor := -1
var fim := false
var sem_premio := false         # terminou sem vencedor (ou empate no tempo)

func _init(p_dados: Dictionary, p_host) -> void:
	d = p_dados; host = p_host
	etapas = d["evento"]["etapas"]

func min_jogadores() -> int:
	return int(d["evento"]["inscricao"]["min_jogadores"])

func etapa_atual() -> String:
	return "" if idx < 0 or idx >= etapas.size() else String(etapas[idx]["id"])

func luta_final() -> bool:
	return etapa_atual() == "ultimo_de_pe"

## Começa o evento com os inscritos. Abaixo do mínimo, cancela e devolve o ouro (host.cancelar).
func iniciar(ids: Array) -> bool:
	if ids.size() < min_jogadores():
		fim = true
		host.cancelar(ids.duplicate())
		return false
	inscritos = ids.duplicate()
	vivos = ids.duplicate()
	_avancar()
	return true

func passo(dt: float) -> void:
	if fim or idx < 0: return
	t += dt
	var e: Dictionary = etapas[idx]
	var id := String(e["id"])
	if id == "chamada" or id == "respiro" or id == "coroacao":
		if t >= float(e["dur"]): _avancar()
	elif id == "luta_leoes" or id == "luta_gigante":
		if chefes_vivos.is_empty():
			_avancar()
		elif t >= float(e["dur_max"]):
			_tempo_esgotado()
	elif id == "ultimo_de_pe":
		_passo_anel(dt)
		if vivos.size() <= 1:
			_vencer_ou_ninguem()
		elif t >= float(e["dur_max"]):
			_tempo_esgotado()

## Um chefe da luta atual morreu (o host chama).
func chefe_morreu(id: String) -> void:
	chefes_vivos.erase(id)
	var et := etapa_atual()
	if et == "luta_leoes" and not chefes_vivos.is_empty():
		host.fala("caim", "UM GATINHO A MENOS!")
		host.fala("abel", "Era o meu favorito. Anota o nome desse aí.")
	elif chefes_vivos.is_empty() and et in ["luta_leoes", "luta_gigante"]:
		if et == "luta_gigante":
			host.fala("caim", FALAS["gigante_morto_caim"])
			host.fala("abel", FALAS["gigante_morto_abel"])
		_avancar()

## Gladiador morreu ou desconectou. Morte vira espectador (sem penalidade); desconectar = eliminado (o host decide o resto).
func jogador_saiu(id: int) -> void:
	if not vivos.has(id) or fim: return
	vivos.erase(id)
	host.espectador(id)
	var et := etapa_atual()
	if et == "luta_leoes" or et == "luta_gigante":
		if vivos.is_empty():
			_ir_para("coroacao"); sem_premio = true
			host.fala("caim", FALAS["sem_vencedor_caim"]); host.fala("abel", FALAS["sem_vencedor_abel"])
	elif et == "ultimo_de_pe":
		if vivos.size() <= 1: _vencer_ou_ninguem()

## Entrada na etapa idx, com as ações do host.
func _avancar() -> void:
	idx += 1; t = 0.0
	if idx >= etapas.size():
		_terminar(); return
	var e: Dictionary = etapas[idx]
	var id := String(e["id"])
	# ninguém de pé: não há luta nem vencedor. Um só de pé nas lutas 1 e 2 segue, mas a luta 3 não acontece
	if vivos.is_empty() and id != "coroacao":
		sem_premio = true
		_ir_para("coroacao"); return
	if id == "ultimo_de_pe" and vivos.size() <= 1:
		_vencer_ou_ninguem(); return
	host.etapa(id, float(e.get("dur", e.get("dur_max", 0.0))))
	match id:
		"chamada":
			host.prender(vivos.duplicate())
			host.fala("caim", FALAS["chamada_caim"]); host.fala("abel", FALAS["chamada_abel"])
		"luta_leoes":
			host.portao("portao_leoes", true)
			host.fala("caim", FALAS["leoes_caim"]); host.fala("abel", FALAS["leoes_abel"])
			_spawn_chefes(e["chefes"], "leoes")
		"luta_gigante":
			host.portao("portao_gigante", true)
			host.fala("caim", FALAS["golias_caim"]); host.fala("abel", FALAS["golias_abel"])
			_spawn_chefes(e["chefes"], "golias")
		"respiro":
			host.recuperar(vivos.duplicate(), float(e.get("recupera_frac", 0.5)))
		"ultimo_de_pe":
			host.trancar_pocoes(not bool(e.get("pocoes", true)))
			host.definir_lados(_lados_proprios())
			host.fala("caim", FALAS["anel_caim"]); host.fala("abel", FALAS["anel_abel"])
		"coroacao":
			_coroar()

func _spawn_chefes(lista: Array, chave: String) -> void:
	chefes_vivos = lista.duplicate()
	var n := vivos.size()
	var esc: Dictionary = d["escala_por_jogadores"][chave]
	for c in lista:
		var hp := float(d["chefes"][c]["hp"]) + float(esc["hp_por_jogador"]) * n
		host.spawn_chefe(String(c), hp)

## Luta 3: cada gladiador vira o próprio lado (todos inimigos). O host aplica o id como lado_forcado.
func _lados_proprios() -> Dictionary:
	var m := {}
	for i in vivos: m[i] = "g_%d" % i
	return m

func _passo_anel(dt: float) -> void:
	var a: Dictionary = etapas[idx]["anel_do_amargo"]
	var comeca := float(a["comeca_s"])
	if t < comeca: return
	var frac := clampf((t - comeca) / float(a["fecha_em_s"]), 0.0, 1.0)
	var raio := lerpf(float(a["raio_inicial"]), float(a["raio_final"]), frac)
	host.anel(raio)
	for i in vivos.duplicate():
		if host.fora_do_anel(i, raio):
			host.dano_anel(i, float(a["dano_frac_hp_por_s"]) * dt)

func _tempo_esgotado() -> void:
	var et := etapa_atual()
	if et == "ultimo_de_pe":
		_vencer_por_hp()
		return
	host.recuar_chefes()
	chefes_vivos.clear()
	_avancar()    # monstros recuam e todos os vivos passam

## Luta 3 acabou com 1 vivo, ou os sobreviventes saíram da arena: decide e vai para a coroação.
func _vencer_ou_ninguem() -> void:
	if vivos.size() == 1:
		vencedor = vivos[0]
	else:
		sem_premio = true
	_ir_para("coroacao")

func _vencer_por_hp() -> void:
	var melhor := -1.0
	var empatados := []
	for i in vivos:
		var f: float = host.hp_frac(i)
		if f > melhor + 0.000001:
			melhor = f; empatados = [i]
		elif absf(f - melhor) <= 0.000001:
			empatados.append(i)
	if empatados.size() == 1:
		vencedor = empatados[0]
	else:
		sem_premio = true    # empate no tempo: sem ficha (a regra não fala do empate; decisão de implementação)
	_ir_para("coroacao")

func _ir_para(id: String) -> void:
	for i in range(etapas.size()):
		if String(etapas[i]["id"]) == id:
			idx = i - 1; t = 0.0
			_avancar()
			return

func _coroar() -> void:
	if vencedor >= 0 and not sem_premio:
		host.premiar(vencedor, int(d["evento"]["premio"]["vencedor"]["ficha_sangue"]))
		host.fala("caim", "%s! DO PÓ VIEMOS E VOCÊ FICOU DE PÉ!" % str(vencedor))
		host.fala("abel", FALAS["vencedor_abel"])
	else:
		host.fala("caim", FALAS["sem_vencedor_caim"]); host.fala("abel", FALAS["sem_vencedor_abel"])

func _terminar() -> void:
	fim = true
	host.encerrar()

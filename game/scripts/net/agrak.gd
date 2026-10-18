extends Node
## O Agrak no servidor: agenda (horário de Brasília), inscrição, avisos no chat do sistema e levar/trazer os
## gladiadores. Filho do servidor.gd. A arena em si (etapas, apresentação, feras) é o AgrakCtl do mapa `agrak`.
## Teste: `agrak=agora` abre a inscrição já e começa em 60 s; `agrak_min=1` aceita menos de 4 inscritos.

const ARQ := "res://data/design/pvp/agrak.json"
const MAPA := "agrak"
const FUSO_H := -3          # Brasília (sem horário de verão)

var srv                     # servidor.gd
var cfg := {}               # dados.json > evento
var inicio := 0             # unix (UTC) da próxima luta
var inscritos: Array = []   # peers, na ordem de inscrição
var avisados := {}          # minutos já avisados nesta rodada
var t := 0.0
var levando := -1.0         # > 0: esperando os gladiadores chegarem ao mapa para começar
var ids_levados: Array = []
var minimo := 1          # regra do Jefin (18/10): com 1 gladiador a arena começa e vai até o fim
var aberta_manual := false  # a agenda só abre a lista; quem começa a luta é o GM (Painel F8)

func _ready() -> void:
	srv = get_parent()
	cfg = Defs.ler(ARQ).get("evento", {})
	minimo = int(cfg.get("inscricao", {}).get("min_jogadores", 1))
	for x in OS.get_cmdline_user_args():
		if x.begins_with("agrak_min="): minimo = maxi(1, int(x.get_slice("=", 1)))
	_agendar("agrak=agora" in OS.get_cmdline_user_args())

func _agora() -> int:
	return int(Time.get_unix_time_from_system())

## Próximo horário da agenda (dados.json > agenda), em UTC.
func _agendar(ja := false) -> void:
	avisados.clear()
	if ja: inicio = _agora() + 60; return
	var ag: Dictionary = cfg.get("agenda", {})
	var agora := _agora()
	var local := agora + FUSO_H * 3600
	var dia0 := local - local % 86400
	inicio = 0
	for dd in 8:
		var dia := dia0 + dd * 86400
		var wd := int(Time.get_datetime_dict_from_unix_time(dia)["weekday"])   # 0 = domingo
		var horas: Array = ag.get("diario", ["20:00", "22:00"]).duplicate()
		if wd == 0 or wd == 6: horas += ag.get("sabado_domingo_extra", [])
		for hm in horas:
			var p: PackedStringArray = str(hm).split(":")
			var ts := dia + int(p[0]) * 3600 + int(p[1] if p.size() > 1 else "0") * 60 - FUSO_H * 3600
			if ts > agora and (inicio == 0 or ts < inicio): inicio = ts
		if inicio != 0: break

func aberta() -> bool:
	if aberta_manual: return true
	var falta := inicio - _agora()
	return falta > 0 and falta <= int(cfg.get("inscricao", {}).get("abre_min_antes", 10)) * 60

func _process(dt: float) -> void:
	if levando > 0.0:
		levando -= dt
		if levando <= 0.0: _comecar_arena()
		return
	t += dt
	if t < 1.0: return
	t = 0.0
	var falta := inicio - _agora()
	for m in cfg.get("inscricao", {}).get("avisos_min", [10, 5, 1]):
		if falta <= int(m) * 60 and falta > int(m) * 60 - 5 and not avisados.has(m):
			avisados[m] = true
			_sistema("O Agrak abre em %d minuto%s. Inscrição no Cartaz do Agrak ou com Caim e Abel (nível %d, %d de ouro). Inscritos: %d." %
				[int(m), "" if int(m) == 1 else "s", _nivel_min(), _custo(), inscritos.size()])
	if falta <= 0: _aguardar_gm()

## Na hora da agenda: a lista fica aberta e a luta espera o GM (pedido do Jefin, 18/10: "quando o ADM mandar").
func _aguardar_gm() -> void:
	aberta_manual = true
	_agendar()
	_sistema("O Agrak está com a lista aberta: inscrição no Cartaz do Agrak ou com Caim e Abel. A luta começa quando um GM der o sinal.")

func _quando() -> String:
	return "quando um GM der o sinal" if aberta_manual else "em %s" % _falta_txt()

func _nivel_min() -> int: return int(cfg.get("inscricao", {}).get("nivel_min", 25))
func _custo() -> int: return int(cfg.get("inscricao", {}).get("custo_ouro", 100))

func _sistema(txt: String) -> void:
	for p in srv.sessoes:
		if srv.sessoes[p]["jog"] != null: srv._para(p, "chat", {"canal": "sistema", "texto": txt})

func _aviso(peer: int, txt: String, cor := "#ffd9a0") -> void:
	srv._para(peer, "aviso", {"texto": txt, "cor": cor})

## Pedido do Cartaz do Agrak ou do diálogo de Caim e Abel (evento "agrak_pedido" do sim).
func pedido(peer: int, a: String) -> void:
	if peer < 0 or not srv.sessoes.has(peer): return
	var e: Ent = srv.sessoes[peer]["jog"]
	if e == null: return
	if a == "sair":
		if peer in inscritos:
			inscritos.erase(peer)
			e.ouro += _custo()
			_aviso(peer, "Você saiu da lista do Agrak. O ouro voltou.")
		return
	if peer in inscritos:
		_aviso(peer, "Você já está na lista. A luta começa %s." % _quando()); return
	if not aberta():
		_aviso(peer, "A lista do Agrak abre %d minutos antes da luta. Próxima: %s (horário de Brasília)." % [int(cfg.get("inscricao", {}).get("abre_min_antes", 10)), _hora_txt()]); return
	if e.nivel < _nivel_min():
		_aviso(peer, "O Agrak só aceita gladiadores do nível %d para cima." % _nivel_min()); return
	if e.ouro < _custo():
		_aviso(peer, "A entrada custa %d de ouro." % _custo()); return
	e.ouro -= _custo()
	inscritos.append(peer)
	_aviso(peer, "Seu nome está na lista do Agrak. A luta começa %s." % _quando(), "#ffb070")

func _falta_txt() -> String:
	var s := maxi(0, inicio - _agora())
	return "%d:%02d" % [s / 60, s % 60]

func _hora_txt() -> String:
	var d := Time.get_datetime_dict_from_unix_time(inicio + FUSO_H * 3600)
	return "%02d:%02d" % [d["hour"], d["minute"]]

## Na hora: cancela com menos do mínimo (devolve o ouro); senão leva até 20 para o mapa agrak.
func _hora() -> void:
	aberta_manual = false
	var lista: Array = inscritos.filter(func(p): return srv.sessoes.has(p) and srv.sessoes[p]["jog"] != null)
	inscritos.clear()
	_agendar()
	if lista.size() < minimo:
		for p in lista:
			srv.sessoes[p]["jog"].ouro += _custo()
			_aviso(p, "O Agrak foi cancelado: gladiadores de menos. O ouro voltou.")
		if not lista.is_empty(): _sistema("O Agrak de hoje foi cancelado: a plateia veio, os gladiadores não.")
		return
	var maxn := int(cfg.get("inscricao", {}).get("max_por_arena", 20))
	if srv.mundos.has(MAPA) and srv.mundos[MAPA].chefe != null and srv.mundos[MAPA].chefe.etapa_i >= 0:
		maxn = 0   # ainda tem um Agrak rodando
	for i in range(maxn, lista.size()):   # acima do máximo (uma arena por vez nesta versão): devolve
		srv.sessoes[lista[i]]["jog"].ouro += _custo()
		_aviso(lista[i], "O Agrak lotou antes do seu nome. O ouro voltou; tente na próxima.")
	lista = lista.slice(0, maxn)
	if lista.is_empty(): return
	var ent: Array = Defs.ler("res://data/mapas/%s.json" % MAPA).get("agrak", {}).get("entrada_fosso", [23, 13.5])
	ids_levados.clear()
	for p in lista:
		var s: Dictionary = srv.sessoes[p]
		var e: Ent = s["jog"]
		if s["mapa"] == MAPA: continue
		e.aux["agrak_volta"] = [s["mapa"], e.pos.x, e.pos.y]
		if not e.vivo: Jogador.renascer(srv.mundos[s["mapa"]], e)
		ids_levados.append(e.id)
		srv.movimentos.append([e.id, MAPA, Vector2(ent[0], ent[1])])
	_sistema("O AGRAK COMEÇOU! %d gladiadores na areia." % ids_levados.size())
	levando = 1.0

func _comecar_arena() -> void:
	levando = -1.0
	var sim: WorldSim = srv.mundos.get(MAPA)
	if sim == null: return
	var ctl = sim.chefe
	if ctl == null or not ctl.has_method("comecar"): return
	ctl.comecar(ids_levados.filter(func(id): return sim.ents.has(id)))

## Desconectou durante o evento: salva o personagem no lugar de onde ele veio (não no coliseu).
func saiu(peer: int) -> void:
	inscritos.erase(peer)
	var s: Dictionary = srv.sessoes.get(peer, {})
	var e = s.get("jog")
	if e == null or s.get("mapa", "") != MAPA or not e.aux.has("agrak_volta"): return
	var v: Array = e.aux["agrak_volta"]
	e.aux.erase("agrak_volta")
	if srv.mundos.has(MAPA): srv.mundos[MAPA].remover_jogador(e)
	var sim2: WorldSim = srv._mundo(str(v[0]))
	s["mapa"] = str(v[0])
	e.lado_forcado = ""; e.alvejavel = true
	if not e.vivo: e.vivo = true
	e.hp = e.hp_max
	sim2.adicionar_jogador(e, Vector2(float(v[1]), float(v[2])))
	srv._liberar_se_vazio(MAPA)

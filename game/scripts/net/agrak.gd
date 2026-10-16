class_name AgrakServidor
extends RefCounted
## Arena do Agrak no servidor: agenda (horário de Brasília), inscrição, instâncias de até 20 gladiadores e a volta
## para onde cada um estava. A luta em si é scripts/sim/agrak_mundo.gd, numa instância do mapa "agrak".
## O servidor (srv) entrega: sessoes, mundos, por_jog, _mundo(), _ev(), _enviar_mapa(), _liberar_se_vazio(), _para().

const MIN_GLADIADORES := 4
const GRUPO_MAX := 20
const NIVEL_MIN := 25
const CUSTO_OURO := 100
const AVISOS_MIN := [10, 5, 1]
const FUSO_S := -3 * 3600           # America/Sao_Paulo (sem horário de verão desde 2019)

var srv
var inscritos: Array = []           # [{peer, id, volta: {mapa, pos}}] para o próximo começo
var instancias: Dictionary = {}     # "agrak#n" -> AgrakMundo
var contador := 0
var avisos_dados: Dictionary = {}   # "S:m" -> true
var comecou_em: Dictionary = {}     # início (segundos do dia) -> true
var agora_override := -1.0          # testes: segundos do dia em Brasília (-1 = relógio real)

## Segundos desde 00:00 de Brasília e dia da semana (0 = domingo).
func agora() -> Dictionary:
	var t := Time.get_unix_time_from_system() + FUSO_S
	var dt := Time.get_datetime_dict_from_unix_time(int(t))
	var s := float(dt["hour"] * 3600 + dt["minute"] * 60 + dt["second"])
	if agora_override >= 0.0: s = agora_override
	return {"s": s, "dia": int(dt["weekday"])}

## Horários de hoje em segundos do dia: 20h e 22h todo dia, e 15h no sábado e domingo.
func inicios_hoje(dia: int) -> Array:
	var lista := [20 * 3600, 22 * 3600]
	if dia == 0 or dia == 6: lista.append(15 * 3600)
	lista.sort()
	return lista

func passo(_dt: float) -> void:
	var a := agora()
	for ini in inicios_hoje(a["dia"]):
		var falta := float(ini) - float(a["s"])
		for m in AVISOS_MIN:
			var chave := "%d:%d" % [ini, m]
			if falta > 0.0 and falta <= m * 60.0 and not avisos_dados.has(chave):
				avisos_dados[chave] = true
				_avisar_todos("O Agrak começa em %d min. Inscrição pelo Cartaz do Agrak ou com o ogro Caim e Abel (nível %d, %d de ouro)." % [m, NIVEL_MIN, CUSTO_OURO])
		if falta <= 0.0 and falta > -2.0 and not comecou_em.has(ini):
			comecou_em[ini] = true
			_comecar()
	for id in instancias.keys():
		var ag: AgrakMundo = instancias[id]
		if ag.encerrado: _encerrar(id)

func janela_aberta() -> bool:
	if not instancias.is_empty(): return false
	var a := agora()
	for ini in inicios_hoje(a["dia"]):
		var falta := float(ini) - float(a["s"])
		if falta > 0.0 and falta <= 600.0: return true
	return false

## Pedido de inscrição (do cartaz ou do ogro). Confere nível, janela, ouro e se já está inscrito.
func inscrever(peer: int) -> void:
	var s: Dictionary = srv.sessoes.get(peer, {})
	var e: Ent = s.get("jog")
	if e == null: return
	if not janela_aberta(): srv._para(peer, "aviso", {"texto": "A inscrição do Agrak não está aberta."}); return
	if e.nivel < NIVEL_MIN: srv._para(peer, "aviso", {"texto": "O Agrak é para nível %d ou mais." % NIVEL_MIN}); return
	if not e.vivo: return
	for i in inscritos:
		if i["peer"] == peer: srv._para(peer, "aviso", {"texto": "Você já está inscrito no Agrak."}); return
	if e.ouro < CUSTO_OURO: srv._para(peer, "aviso", {"texto": "Faltam %d de ouro para o Agrak." % (CUSTO_OURO - e.ouro)}); return
	e.ouro -= CUSTO_OURO
	inscritos.append({"peer": peer, "id": e.id, "volta": {"mapa": s["mapa"], "pos": e.pos}})
	srv._para(peer, "aviso", {"texto": "Inscrito no Agrak. Você entra no horário marcado."})
	srv._salvar_jog(peer)

## Saiu antes de começar: devolve o ouro.
func sair(peer: int) -> void:
	for k in range(inscritos.size()):
		if inscritos[k]["peer"] == peer:
			_devolver(inscritos[k]); inscritos.remove_at(k)
			srv._para(peer, "aviso", {"texto": "Você saiu da lista do Agrak. Ouro devolvido."})
			return

func _devolver(i: Dictionary) -> void:
	var s: Dictionary = srv.sessoes.get(i["peer"], {})
	var e: Ent = s.get("jog")
	if e == null: return
	e.ouro += CUSTO_OURO
	srv._para(i["peer"], "ouro", {"valor": CUSTO_OURO})
	srv._salvar_jog(i["peer"])

## Desconectou durante a luta: eliminado (o controlador decide o resto).
func saiu(ent_id: int) -> void:
	for id in instancias.keys():
		var ag: AgrakMundo = instancias[id]
		if not ag.encerrado and ag.jogadores_ids.has(ent_id): ag.ctl.jogador_saiu(ent_id)

func _avisar_todos(txt: String) -> void:
	for p in srv.sessoes.keys():
		if srv.sessoes[p].get("jog") != null: srv._para(p, "aviso", {"texto": txt})

func _comecar() -> void:
	var validos: Array = []
	for i in inscritos:
		var s: Dictionary = srv.sessoes.get(i["peer"], {})
		if s.get("jog") != null and s["jog"].id == i["id"]: validos.append(i)
		else: _devolver(i)
	inscritos.clear()
	if validos.size() < MIN_GLADIADORES:
		for i in validos: _devolver(i); srv._para(i["peer"], "aviso", {"texto": "Agrak cancelado: menos de %d inscritos. Ouro devolvido." % MIN_GLADIADORES})
		return
	var grupos: Array = []
	for k in range(0, validos.size(), GRUPO_MAX): grupos.append(validos.slice(k, mini(k + GRUPO_MAX, validos.size())))
	if grupos.size() > 1 and grupos[-1].size() < MIN_GLADIADORES:
		grupos[-2].append_array(grupos[-1]); grupos.pop_back()
	for g in grupos: _instanciar(g)
	_avisar_todos("O Agrak começou! Quem está na arena luta; os outros podem ver pela plateia.")

func _instanciar(grupo: Array) -> void:
	contador += 1
	var id := "agrak#%d" % contador
	var sim := WorldSim.new(randi())
	sim.carregar_mapa("agrak")
	sim.evento.connect(srv._ev.bind(id))
	srv.mundos[id] = sim
	var ids: Array = []
	for i in grupo:
		var s: Dictionary = srv.sessoes[i["peer"]]
		var e: Ent = s["jog"]
		var velho: String = s["mapa"]
		if srv.mundos.has(velho): srv.mundos[velho].remover_jogador(e)
		s["mapa"] = id; s["saida"] = []
		e.aux["agrak_volta"] = i["volta"]
		var sp: Array = sim.mapa.get("spawn", [23, 13])
		sim.adicionar_jogador(e, Vector2(sp[0], sp[1]))
		srv._enviar_mapa(i["peer"])
		srv._liberar_se_vazio(velho)
		ids.append(e.id)
	var ag := AgrakMundo.new(sim, Defs.AGRAK, ids)
	sim.agrak = ag
	instancias[id] = ag
	ag.iniciar()

func _encerrar(id: String) -> void:
	var sim: WorldSim = srv.mundos.get(id)
	var ag: AgrakMundo = instancias[id]
	instancias.erase(id)
	if sim == null: return
	for e in sim.jogadores().duplicate():
		var peer: int = srv.por_jog.get(e.id, -1)
		var volta: Dictionary = e.aux.get("agrak_volta", {"mapa": "area_inicial", "pos": Vector2(-1, -1)})
		e.aux.erase("agrak_volta"); e.aux.erase("agrak_espectador"); e.aux.erase("sem_pocoes")
		e.lado_forcado = ""; e.alvejavel = true
		e.hp = e.hp_max
		if e.rec_max > 0.0: e.rec = e.rec_max
		sim.remover_jogador(e)
		if peer < 0 or not srv.sessoes.has(peer): continue
		var s: Dictionary = srv.sessoes[peer]
		s["mapa"] = volta["mapa"]; s["saida"] = []
		var destino: WorldSim = srv._mundo(volta["mapa"])
		var sp: Array = destino.mapa.get("spawn", [10, 10])
		var pos: Vector2 = volta["pos"] if volta["pos"] is Vector2 and volta["pos"].x >= 0 else Vector2(sp[0], sp[1])
		destino.adicionar_jogador(e, pos)
		srv._enviar_mapa(peer)
		srv._salvar_jog(peer)
	srv.mundos.erase(id)
	print("[servidor] Agrak encerrado: ", id)

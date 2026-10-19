class_name CavaleirosCtl
extends RefCounted
## Evento "Os Cavaleiros do Apocalipse": Agonia, Danação, Perdição e Lamento (Fome, Guerra, Conquista e Peste). Um controlador por capital
## (design/combate/cavaleiros.json > capitais), dentro do WorldSim do mapa dela. Os quatro nascem juntos:
## em Jerusalém voam por cima da cidade e descem no pouso; nas outras capitais descem do céu direto.
## Enquanto voam não podem ser atacados. Depois de pousados, ficam juntos perto do pouso (a coleira é o
## próprio pouso) até um deles morrer ou o tempo do evento acabar. Cada cavaleiro morto dá ao assassino
## uma chance de deixar a montaria dele no chão.

const DADOS := "res://data/design/combate/cavaleiros.json"

var sim: WorldSim
var ev: Dictionary          # cavaleiros.json inteiro
var capital := ""           # id da capital (jerusalem, acampamento_vela...)
var estado := "ocioso"      # ocioso | voo | pousados | fim
var rota: Array = []        # pontos do voo; o último é o pouso
var etapa := 1              # próximo ponto da rota a alcançar
var ids: Array = []         # cavaleiros deste grupo que ainda estão no mapa
var posto := {}             # id do cavaleiro -> índice na formação (não muda quando um morre)
var t := 0.0                # tempo desde que pousaram
var pouso := Vector2.ZERO

func _init(p_sim: WorldSim, p_capital: String, p_ev: Dictionary = {}) -> void:
	sim = p_sim
	capital = p_capital
	ev = p_ev if not p_ev.is_empty() else Defs.ler(DADOS)

func _ponto(v: Array) -> Vector2:
	return Vector2(float(v[0]), float(v[1]))

func _off(i: int) -> Vector2:
	return _ponto(ev["formacao"][i])

## Nasce o grupo e começa o voo (ou a descida, nas capitais sem voo).
func iniciar() -> void:
	var cap: Dictionary = ev["capitais"][capital]
	pouso = _ponto(cap["pouso"])
	rota = []
	for p in cap.get("voo", []): rota.append(_ponto(p))
	rota.append(pouso)
	var inicio: Vector2 = rota[0]
	if rota.size() == 1:   # sem voo: desce do céu até o pouso
		inicio = pouso + Vector2(-8, -8)
		rota.push_front(inicio)
	var nivel := int(ev.get("nivel", 30))
	for i in ev["cavaleiros"].size():
		var e := sim.criar_mob(str(ev["cavaleiros"][i]), inicio + _off(i), nivel)
		e.alvejavel = false
		e.casa = pouso + _off(i)
		e.aux["bando"] = "cavaleiros_%d" % get_instance_id()   # os quatro reagem juntos (ia.gd, _mesmo_bando)
		ids.append(e.id)
		posto[e.id] = i
	etapa = 1
	estado = "voo"

func _vivos() -> Array:
	var r: Array = []
	for id in ids:
		var e := sim.valido(id)
		if e != null and e.vivo: r.append(e)
	ids = r.map(func(e: Ent): return e.id)
	return r

func _em_movimento(vivos: Array) -> bool:
	for e in vivos:
		if not e.deslocando.is_empty(): return true
	return false

func passo(dt: float) -> void:
	if estado == "ocioso" or estado == "fim": return
	var vivos := _vivos()
	if vivos.is_empty():
		estado = "fim"; return
	if _em_movimento(vivos): return
	if etapa < rota.size():   # manda o grupo para o próximo ponto do voo, sempre juntos
		var de: Vector2 = rota[etapa - 1]
		var alvo: Vector2 = rota[etapa]
		var dur := maxf(de.distance_to(alvo) / float(ev.get("velocidade_voo", 9.0)), 0.8)
		for e: Ent in vivos:
			sim.deslocar(e, alvo + _off(posto[e.id]), dur, {"atravessa": true, "tipo": "voo"})
		etapa += 1
		return
	if estado == "voo":   # chegou ao pouso: pousa, todos podem ser atacados
		estado = "pousados"
		for e in vivos: e.alvejavel = true
	t += dt
	if t >= float(ev.get("duracao_s", 900.0)):
		for e in vivos: sim.remover(e.id)
		ids.clear()
		estado = "fim"

## Chamado pelo WorldSim quando um mob morre. Só conta os cavaleiros deste grupo.
func ao_morrer(e: Ent, killer: Ent) -> void:
	if not ids.has(e.id): return
	ids.erase(e.id)
	for v in _vivos():   # quando um cai, o grupo inteiro vem para cima de quem matou
		if killer != null: v.ameaca[killer.id] = v.ameaca.get(killer.id, 0.0) + 1.0
		IA.acordar(sim, v, killer)
	if killer == null or killer.tipo != "jogador": return
	var montaria := str(ev.get("montarias", {}).get(e.kind, ""))
	if not Defs.ITENS.has(montaria):
		push_warning("Cavaleiros: a montaria %s ainda não existe em itens.json" % montaria)
		return
	if sim.rng.randf() < float(ev.get("chance_montaria", 0.10)):
		sim.soltar_no_chao(Itens.novo(montaria), e.pos, killer.id, e.pos)

func acabou() -> bool:
	return estado == "fim"

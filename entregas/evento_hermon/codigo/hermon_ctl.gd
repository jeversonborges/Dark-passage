class_name HermonCtl
extends RefCounted
## Evento "O Cume dos Vigilantes" (estilo Chaos Castle): roda dentro do WorldSim de uma instância do mapa
## cume_dos_vigilantes. Números em data/design/pvp/hermon/dados.json; geometria em mapa["hermon"].
## Fases: espera (entrada aberta, sem PvP, Vigilantes ajoelhados como estátuas) -> juramento (15 min de
## sobrevivência, todos contra todos, os anéis do cume caem) -> fim (prêmios e todo mundo volta).

const DADOS := "res://data/design/pvp/hermon/dados.json"

var sim: WorldSim
var cfg: Dictionary            # mapa["hermon"]
var ev: Dictionary             # dados.json -> evento
var nivel_mob := 30
var estado := "espera"         # espera | juramento | fim | cancelado
var espera_t := 300.0          # o servidor acerta com o tempo que falta da janela de entrada
var t := 0.0                   # tempo de juramento
var fim_t := 0.0
var centro := Vector2.ZERO
var abismo := {}               # Vector2i -> true (células que já caíram)
var disco := {}                # Vector2i -> anel ("" = laje)
var aneis: Array = []          # [{id, cai_em, celulas, avisado, caiu}]
var estatuas: Array = []       # ids das estátuas (objetos) na espera
var participantes := {}        # id do jogador -> {nome, pontos, ordem, vivo, saiu}
var ordem := 0
var vencedor := -1
var _prox_check := 0.0

func _init(p_sim: WorldSim, c: Dictionary, p_ev: Dictionary = {}) -> void:
	sim = p_sim; cfg = c
	var d: Dictionary = p_ev if not p_ev.is_empty() else Defs.ler(DADOS)
	ev = d["evento"]
	for k in d.get("mobs", {}):          # os Vigilantes e o convite entram no Defs na primeira instância
		if not Defs.MOBS.has(k): Defs.MOBS[k] = d["mobs"][k]
	for it in d.get("itens", []):
		if not Defs.ITENS.has(it["id"]): Defs.ITENS[it["id"]] = it
	centro = Vector2(cfg["centro"][0], cfg["centro"][1])
	espera_t = float(ev["entrada"]["janela_s"])
	for a in cfg["aneis"]:
		var cels: Array = []
		for c2 in a["celulas"]:
			var v := Vector2i(int(c2[0]), int(c2[1]))
			cels.append(v); disco[v] = a["id"]
		aneis.append({"id": a["id"], "cai_em": float(a["cai_em"]), "celulas": cels, "avisado": false, "caiu": false})
	_criar_estatuas()

func definir_nivel(n: int) -> void:
	nivel_mob = n

## Servidor: segundos que faltam para a entrada fechar (a janela é global; a instância só conta).
func definir_espera(seg: float) -> void:
	espera_t = maxf(0.0, seg)

## GM "Início imediato": fecha a entrada agora (animações e luta já) com quem estiver dentro, mesmo que seja 1.
func forcar_inicio() -> void:
	if estado == "espera": _fechar_entrada()

# =================================================================== jogadores
func entrou(j: Ent) -> void:
	if estado != "espera":
		return
	ordem += 1
	participantes[j.id] = {"nome": j.nome, "pontos": 0, "ordem": ordem, "vivo": true, "saiu": false, "fichas": 0}
	j.lado_forcado = "hermon"          # na espera todos do mesmo lado: sem PvP
	j.aux["hermon"] = true
	sim.emitir_a(j, "hermon", {"fase": "espera", "resta": espera_t, "texto": ev["falas"]["abriu"]})

## Desconectou ou saiu do mapa (vela de retorno, teleporte): conta como eliminado.
func saiu(j: Ent) -> void:
	if participantes.has(j.id) and participantes[j.id]["vivo"]:
		participantes[j.id]["vivo"] = false; participantes[j.id]["saiu"] = true
	j.lado_forcado = ""; j.aux.erase("hermon")

func vivos() -> Array:
	var out: Array = []
	for id in participantes:
		if not participantes[id]["vivo"]: continue
		var j: Ent = sim.ents.get(id)
		if j != null and j.vivo: out.append(j)
	return out

func vigilantes_vivos() -> int:
	var n := 0
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.vivo and e.aux.get("vigilante", false): n += 1
	return n

# =================================================================== passo
func passo(dt: float) -> void:
	match estado:
		"espera":
			espera_t -= dt
			if espera_t <= 0.0: _fechar_entrada()
		"juramento":
			t += dt
			_passo_aneis()
			_passo_quedas()
			_passo_lados()
			_checar_fim()
		"fim", "cancelado":
			fim_t += dt

func _fechar_entrada() -> void:
	var js := vivos()
	if js.size() < int(ev["entrada"]["min_para_comecar"]):    # 1 jogador já basta (regra do Jefin, 18/10)
		estado = "cancelado"
		for j: Ent in js:
			Jogador.dar_item(sim, j, Itens.novo(ev["entrada"]["item"], 1))
			sim.emitir_a(j, "aviso", {"texto": "Ninguém mais subiu. O convite voltou para a sua mochila."})
			_mandar_de_volta(j)
		sim.emitir("hermon", {"fase": "cancelado"})
		return
	estado = "juramento"; t = 0.0
	for j: Ent in js:
		j.lado_forcado = "h_%d" % j.id     # cada um é o próprio lado
	_acordar_vigilantes(js.size())
	sim.emitir("hermon", {"fase": "juramento", "dur": float(ev["sobrevivencia"]["dur_s"]), "texto": ev["falas"]["comecou"],
		"aneis": _aneis_info()})
	sim.emitir("aviso", {"texto": ev["falas"]["fechou"]})

func _aneis_info() -> Array:
	var out: Array = []
	for a in aneis: out.append({"id": a["id"], "cai_em": a["cai_em"]})
	return out

# =================================================================== Vigilantes
func _criar_estatuas() -> void:
	for v in cfg["vigilantes"]:
		var p := Vector2(v["pos"][0], v["pos"][1])
		var e := sim._ent_base("objeto", "estatua_vigilante", p)
		e.alvejavel = false; e.raio = 0.45; e.nome = "Vigilante"
		e.facing = Vector2(v["olha"][0], v["olha"][1])
		e.aux = {"visual": "vigilante_jurado", "anim": "kneel", "anel": v.get("anel", "")}
		estatuas.append(e.id)
		sim.emitir("surgiu", {"id": e.id})

func _sortear_tipo() -> String:
	var r := sim.rng.randf()
	var acc := 0.0
	var mix: Dictionary = ev["vigilantes"]["mistura"]
	for k in mix:
		acc += float(mix[k])
		if r <= acc: return k
	return "vigilante_jurado"

func _acordar_vigilantes(n_jog: int) -> void:
	var vg: Dictionary = ev["vigilantes"]
	var n := mini(int(vg["inicio_max"]), int(vg["inicio_base"]) + int(vg["inicio_por_jogador"]) * n_jog)
	var i := 0
	for sid in estatuas:
		var s: Ent = sim.ents.get(sid)
		if s == null: continue
		var p := s.pos
		var f := s.facing
		sim.remover(sid)
		if i < n:
			var m := _criar_vigilante(_sortear_tipo(), p, "rise")
			m.facing = f
		i += 1
	estatuas.clear()

func _criar_vigilante(kind: String, p: Vector2, anim: String) -> Ent:
	var m := sim.criar_mob(kind, p, nivel_mob)
	m.aux["vigilante"] = true
	m.aux["anim_entrada"] = anim                 # o cliente toca "rise" ou "land" ao surgir
	m.casa = p; m.raio_coleira = 99.0; m.raio_vagar = 0.0
	m.renasce_s = 1e9
	m.ia_t = 1.2 if anim == "rise" else 1.0   # espera a animação de entrada antes de procurar alvo
	return m

func _reforco() -> void:
	var r: Dictionary = ev["vigilantes"]["reforco_ao_cair_anel"]
	var n := int(r["base"]) + vivos().size() / int(r["por_jogadores_vivos"])
	n = mini(n, int(r["max_vivos"]) - vigilantes_vivos())
	var livres: Array = []
	for c in disco:
		if not abismo.has(c) and sim.andavel(Vector2(c) + Vector2(0.5, 0.5)): livres.append(c)
	if livres.is_empty(): return
	for k in maxi(n, 0):
		var c: Vector2i = livres[sim.rng.randi() % livres.size()]
		_criar_vigilante(_sortear_tipo(), Vector2(c) + Vector2(0.5, 0.5), "land")
	if n > 0: sim.emitir("aviso", {"texto": ev["falas"]["reforco"]})

# =================================================================== anéis e quedas
func _passo_aneis() -> void:
	var aviso := float(ev["desmoronamento"]["aviso_s"])
	for a in aneis:
		if a["caiu"]: continue
		if not a["avisado"] and t >= a["cai_em"] - aviso:
			a["avisado"] = true
			sim.emitir("hermon_aviso", {"anel": a["id"], "em": aviso})
			sim.emitir("aviso", {"texto": ev["falas"]["aviso_anel"]})
		if t >= a["cai_em"]:
			_derrubar(a)

func _derrubar(a: Dictionary) -> void:
	a["caiu"] = true
	var cels: Array = []
	for c: Vector2i in a["celulas"]:
		abismo[c] = true; cels.append([c.x, c.y])
	sim.definir_bloqueio(cels, 1)
	sim.emitir("hermon_anel_caiu", {"anel": a["id"]})
	sim.emitir("aviso", {"texto": ev["falas"]["caiu_anel"]})
	_passo_quedas()
	_reforco()

func no_abismo(p: Vector2) -> bool:
	var c := Vector2i(floori(p.x), floori(p.y))
	if abismo.has(c): return true
	return not disco.has(c) and Vector2(c).distance_to(centro) > float(cfg["laje_raio"]) + 1.0

## Todo vivo sobre o abismo cai; e na beira, um empurrão para fora também derruba.
func _passo_quedas() -> void:
	var beira := 0.7
	for e: Ent in sim.ents.values().duplicate():
		if not e.vivo or not (e.tipo in ["jogador", "monstro", "invocacao"]): continue
		if e.tipo == "jogador" and not participantes.get(e.id, {}).get("vivo", false): continue   # já eliminado, de saída
		var cai := no_abismo(e.pos)
		if not cai and e.empurrao_t > 0.0 and e.empurrao.length() > 0.001:
			cai = no_abismo(e.pos + e.empurrao.normalized() * beira)
		if not cai and not e.deslocando.is_empty():
			cai = no_abismo(e.deslocando["para"])
		if cai: _cair(e)

func _cair(e: Ent) -> void:
	sim.emitir("hermon_queda", {"id": e.id, "pos": e.pos})
	if e.tipo == "jogador":
		sim.emitir("aviso", {"texto": ev["falas"]["queda"] % e.nome})
	e.deslocando = {}; e.empurrao_t = 0.0
	sim.matar(e, null)

## Invocações (torretas, familiar) ficam do lado do dono.
func _passo_lados() -> void:
	for e: Ent in sim.ents.values():
		if e.tipo == "invocacao":
			var d: Ent = sim.ents.get(e.dono)
			if d != null: e.lado_forcado = d.lado_forcado

# =================================================================== mortes (chamado por WorldSim.matar)
## Devolve true quando o evento cuidou da morte do jogador (sem penalidade, eliminado e mandado de volta).
func ao_morrer(e: Ent, killer: Ent) -> bool:
	var k := killer
	if k != null and k.tipo == "invocacao": k = sim.ents.get(k.dono)
	if e.tipo == "monstro" and e.aux.get("vigilante", false):
		if k != null and k.tipo == "jogador" and participantes.has(k.id):
			participantes[k.id]["pontos"] += int(ev["pontos"].get(e.kind, 1))
		return false
	if e.tipo != "jogador" or not participantes.has(e.id):
		return false
	participantes[e.id]["vivo"] = false
	e.renascer_t = 1e9                   # não renasce no cume: volta para casa
	if k != null and k.tipo == "jogador" and k != e and participantes.has(k.id):
		participantes[k.id]["pontos"] += int(ev["pontos"]["jogador"])
		var fp: Dictionary = ev["premios"].get("abate_pvp", {})
		if int(fp.get("ficha_sangue", 0)) > 0 and int(participantes[k.id].get("fichas", 0)) < int(fp.get("max_por_evento", 3)):
			participantes[k.id]["fichas"] = int(participantes[k.id].get("fichas", 0)) + int(fp["ficha_sangue"])
			Jogador.dar_item(sim, k, Itens.novo("ficha_sangue", int(fp["ficha_sangue"])))
			sim.emitir_a(k, "inventario", {})
		sim.emitir("morte_pvp", {"de": k.id, "vitima": e.id})
		sim.emitir("aviso", {"texto": ev["falas"]["abate_pvp"] % [k.nome, e.nome]})
	sim.emitir_a(e, "hermon", {"fase": "eliminado", "texto": "O Hermon não te guardou. Sem perda de experiência."})
	sim.atrasar(1.5, func(): _mandar_de_volta(e))
	return true

func _mandar_de_volta(j: Ent) -> void:
	if not sim.ents.has(j.id): return
	j.vivo = true; j.hp = j.hp_max; j.status.clear(); j.renascer_t = 0.0
	j.lado_forcado = ""; j.aux.erase("hermon")
	var volta: Dictionary = j.aux.get("hermon_volta", {})
	var mapa: String = volta.get("mapa", "area_inicial")
	var pos = volta.get("pos", Vector2(-1, -1))
	if pos is Array: pos = Vector2(pos[0], pos[1])
	sim.emitir_a(j, "trocar_mapa", {"mapa": mapa, "pos": pos})

# =================================================================== fim e prêmios
func _checar_fim() -> void:
	var js := vivos()
	var dur := float(ev["sobrevivencia"]["dur_s"])
	if t >= dur or js.is_empty() or (js.size() == 1 and vigilantes_vivos() == 0):
		_terminar(js)

func classificar(js: Array) -> Array:
	var l := js.duplicate()
	l.sort_custom(func(a: Ent, b: Ent) -> bool:
		var pa: Dictionary = participantes[a.id]; var pb: Dictionary = participantes[b.id]
		if pa["pontos"] != pb["pontos"]: return pa["pontos"] > pb["pontos"]
		if absf(a.frac_hp() - b.frac_hp()) > 0.0001: return a.frac_hp() > b.frac_hp()
		return pa["ordem"] < pb["ordem"])
	return l

func _terminar(js: Array) -> void:
	estado = "fim"
	var pr: Dictionary = ev["premios"]
	var ranking := classificar(js)
	if ranking.is_empty():
		sim.emitir("hermon", {"fase": "fim", "vencedor": -1, "texto": ev["fim"]["sem_ninguem"]})
		return
	var w: Ent = ranking[0]
	vencedor = w.id
	for j: Ent in ranking:
		_premiar(j, pr["sobrevivente"])
	w.aux["titulo_ganho"] = pr["testemunha"]["titulo"]
	if int(pr["testemunha"].get("ficha_sangue", 0)) > 0:
		Jogador.dar_item(sim, w, Itens.novo("ficha_sangue", int(pr["testemunha"]["ficha_sangue"])))
	var arma := _arma_lendaria(w, pr["testemunha"])
	var txt: String = ev["falas"]["vencedor"] % w.nome
	if not arma.is_empty():
		txt = ev["falas"]["vencedor_arma"] % [w.nome, Itens.nome(arma)]
	else:
		sim.emitir_a(w, "aviso", {"texto": pr["testemunha"]["sem_arma_fala"]})
	sim.emitir("hermon", {"fase": "fim", "vencedor": w.id, "texto": txt, "arma": arma.get("id", ""), "placar": placar()})
	for j: Ent in ranking:
		sim.atrasar(8.0, func(): _mandar_de_volta(j))

## Prêmio do vencedor (Jefin): 30% de chance de uma arma lendária da classe dele (pool lendario:hermon).
func _arma_lendaria(w: Ent, p: Dictionary) -> Dictionary:
	if sim.rng.randf() >= float(p["chance_arma_lendaria"]): return {}
	var ids: Array = []
	for id in Defs.ITENS:
		var d: Dictionary = Defs.ITENS[id]
		if p["pool"] in d.get("tags", []) and (not p.get("arma_da_classe", true) or w.classe in d.get("classes", [])): ids.append(id)
	if ids.is_empty(): return {}
	ids.sort()
	var it := Itens.novo(ids[sim.rng.randi() % ids.size()])
	it["raridade"] = "lendario"
	Jogador.dar_item(sim, w, it)
	return it

func _premiar(j: Ent, p: Dictionary) -> void:
	for id in ["lagrima_sanguinea", "lagrima_angelica", "ficha_sangue"]:
		if int(p.get(id, 0)) > 0: Jogador.dar_item(sim, j, Itens.novo(id, int(p[id])))
	var ouro := int(p.get("ouro_por_nivel_mob", 0)) * nivel_mob
	if ouro > 0: Jogador.dar_item(sim, j, {"id": "_ouro", "qtd": ouro})
	sim.emitir_a(j, "inventario", {})

func placar() -> Array:
	var out: Array = []
	for id in participantes:
		var p: Dictionary = participantes[id]
		out.append({"id": id, "nome": p["nome"], "pontos": p["pontos"], "vivo": p["vivo"]})
	out.sort_custom(func(a, b): return a["pontos"] > b["pontos"])
	return out

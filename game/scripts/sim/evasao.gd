class_name Evasao
## Esquiva de todas as classes (design/combate/evasao.json): botão direito do mouse, Espaço ou RT no controle.
## Não ocupa slot nem gasta recurso. Duas cargas; cada uma volta sozinha em 10 s, uma de cada vez.
## Cancela o ataque/conjuração e a canalização em andamento; não sai preso, atordoado, derrubado ou quebrado.
## Estado no e.aux (vai para o dono pela rede): ev_cargas, ev_recarga (s até a próxima carga), ev_ult (trava curta).

static var _doc := {}

static func doc() -> Dictionary:
	if _doc.is_empty():
		var d = Defs.ler(Defs.DESIGN + "combate/evasao.json")
		_doc = d if d is Dictionary else {"classes": {}}
	return _doc

## Definição da evasão do personagem: números da classe base, nome e cor da evolução por cima.
static func defn(e: Ent) -> Dictionary:
	return defn_de(e.classe, e.evolucao) if e != null else {}

static func defn_de(classe: String, evolucao: String) -> Dictionary:
	var c: Dictionary = doc().get("classes", {}).get(classe, {})
	if c.is_empty(): return {}
	var ev: Dictionary = doc().get("evolucoes", {}).get(evolucao, {}) if evolucao != "" else {}
	if ev.is_empty(): return c
	var r := c.duplicate()
	r.merge(ev, true)
	return r

static func cargas_max() -> int:
	return int(doc().get("cargas", 2))

static func recarga() -> float:
	return float(doc().get("recarga_por_carga_s", 10.0))

static func cargas(e: Ent) -> int:
	return int(e.aux.get("ev_cargas", cargas_max()))

## Chamado todo quadro pelo Jogador.passo: devolve as cargas uma de cada vez.
static func passo(e: Ent, dt: float) -> void:
	if e.aux.get("ev_ult", 0.0) > 0.0: e.aux["ev_ult"] = float(e.aux["ev_ult"]) - dt
	var n := cargas(e)
	if n >= cargas_max():
		if e.aux.has("ev_recarga"): e.aux.erase("ev_recarga")
		return
	var t := float(e.aux.get("ev_recarga", recarga())) - dt
	if t <= 0.0:
		n += 1
		e.aux["ev_cargas"] = n
		t = recarga() if n < cargas_max() else 0.0
	if n >= cargas_max(): e.aux.erase("ev_recarga")
	else: e.aux["ev_recarga"] = t

## Motivo para não esquivar agora ("" = pode).
static func recusa(e: Ent) -> String:
	if not e.vivo: return "-"
	if defn(e).is_empty(): return "-"
	if cargas(e) <= 0: return "Esquiva recarregando."
	if e.aux.get("ev_ult", 0.0) > 0.0 or not e.deslocando.is_empty(): return "-"
	for s in doc().get("bloqueada_por_status", []):
		if e.tem(s): return "Preso: não dá para esquivar."
	if e.quebrado_t > 0.0: return "Sem fôlego para esquivar."
	if e.aux.get("imovel_t", 0.0) > 0.0: return "-"
	return ""

## Comando "evadir" [ponto]: esquiva na direção do ponto (o mouse); ponto em cima do personagem = para onde ele olha.
static func evadir(sim: WorldSim, e: Ent, ponto: Vector2) -> void:
	var motivo := recusa(e)
	if motivo != "":
		if motivo != "-": sim.emitir_a(e, "aviso", {"texto": motivo})
		return
	var h := defn(e)
	var dir := (ponto - e.pos).normalized() if ponto.distance_to(e.pos) > 0.3 else e.facing
	if dir == Vector2.ZERO: dir = Vector2(0, 1)
	if h.get("direcao", "") == "tras" and e.facing != Vector2.ZERO: dir = -e.facing   # Humano: pula para trás, de onde olha (0.9.8.2)
	# paga a carga; a recarga só começa a contar se ainda não estava contando
	var n := cargas(e) - 1
	e.aux["ev_cargas"] = n
	if not e.aux.has("ev_recarga"): e.aux["ev_recarga"] = recarga()
	e.aux["ev_ult"] = float(doc().get("intervalo_minimo_s", 0.15)) + float(h["duracao_s"])
	# larga o que estava fazendo: ataque, conjuração, canalização e skill guardada
	if not e.interagindo.is_empty(): Jogador.cancelar_canal(sim, e)
	sim.cancelar_acao(e, "evasao")
	e.buffer_skill = {}; e.caminho.clear()
	e.aux.erase("interagir"); e.aux.erase("pegar")
	e.invuln_t = maxf(e.invuln_t, float(h["invulneravel_s"]))
	var estilo: String = h.get("estilo", "rolamento")
	var extra := {"tipo": "evasao", "anim": h.get("anim", "evasao"), "estilo": estilo, "classe": e.classe, "evolucao": e.evolucao}
	if h.has("empurra_no_caminho"): extra["ao_passar"] = func(o: Ent): _empurrar(sim, e, o, h, dir)
	var de := e.pos
	sim.deslocar(e, e.pos + dir * float(h["deslocamento"]), float(h["duracao_s"]), extra)
	e.facing = dir
	# o alvo continua só se dá para bater de onde ele chega (o Humano rola e segue atirando); senão voltaria correndo
	var al := sim.valido(e.alvo)
	if al != null and (e.deslocando.get("para", e.pos) as Vector2).distance_to(al.pos) - al.raio > Jogador.alcance_basico(e): e.alvo = -1
	if h.has("escudo_depois"):
		var ed: Dictionary = h["escudo_depois"]
		var dur := float(h["duracao_s"]) + float(ed["duracao_s"])
		Jogador.add_buff(sim, e, "passo_de_escudo", dur, {"dano_recebido": float(ed["dano_recebido"])})
	sim.emitir("evasao", {"id": e.id, "classe": e.classe, "evolucao": e.evolucao, "estilo": estilo, "de": de,
		"para": e.deslocando.get("para", e.pos), "dur": float(h["duracao_s"])})

## Tranco do Mutante: mob comum no caminho é jogado para o lado (sem dano; chefe, elite e jogador não).
static func _empurrar(sim: WorldSim, e: Ent, o: Ent, h: Dictionary, dir: Vector2) -> void:
	if o.tipo in h.get("empurra_nao_afeta", []) or o.arquetipo in h.get("empurra_nao_afeta", []): return
	if o.tipo == "jogador" or o.tipo == "objeto" or not o.deslocando.is_empty(): return
	var lado := Vector2(-dir.y, dir.x)
	if (o.pos - e.pos).dot(lado) < 0.0: lado = -lado
	sim.deslocar(o, o.pos + lado * float(h["empurra_no_caminho"]), 0.2, {"tipo": "empurrao"})

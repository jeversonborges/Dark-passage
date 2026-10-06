class_name Sincro
## Rede: transforma entidades do servidor em dicionários enviáveis (e de volta, no espelho do cliente).
## Os outros veem só o público; o dono do personagem recebe também mochila, missões, recargas etc.

const PUB := ["tipo", "kind", "nome", "nivel", "pos", "facing", "raio", "vivo", "invisivel", "alvejavel", "escala",
	"hp", "hp_max", "rec", "rec_max", "escudo", "postura", "postura_max", "estado", "arquetipo", "tags", "classe",
	"faccao", "alvo", "dono", "vel", "res"]
const PRIV := ["xp", "pontos", "ouro", "municao", "folego", "inv", "equip", "armazem", "missoes", "flags", "vistas",
	"stats", "dano_min", "dano_max", "defesa", "ar", "er", "critico", "crit_mult", "excelente", "vel_ataque", "intervalo",
	"alcance", "roubo_vida", "no_lugar", "zona", "abates", "skills_slots", "pity_raro"]
## chaves de aux que o cliente usa para desenhar entidades dos outros
const AUX_PUB := ["neutro", "alfa", "titulo", "visual", "obj", "aberto", "requer_chefe", "visivel_se", "bau", "hist", "para",
	"mapa", "chegada", "nome", "texto", "enrage", "imune", "auto"]
## chaves de aux do próprio jogador que mudam todo quadro e o cliente não precisa
const AUX_RUIDO := ["repath", "parado_t", "amargo_t", "ia_t"]

## Valor seguro para a rede: sem Callable/Object (Ent vira id), floats arredondados quando pedido.
static func limpo(v, passo := 0.0):
	match typeof(v):
		TYPE_CALLABLE, TYPE_SIGNAL, TYPE_RID: return null
		TYPE_OBJECT:
			return v.id if v is Ent else null
		TYPE_FLOAT:
			return snappedf(v, passo) if passo > 0.0 else v
		TYPE_DICTIONARY:
			var d := {}
			for k in v:
				var x = limpo(v[k], passo)
				if x != null or v[k] == null: d[k] = x
			return d
		TYPE_ARRAY:
			var a := []
			for x in v:
				var y = limpo(x, passo)
				if y != null or x == null: a.append(y)
			return a
	return v

## Todos os campos que vão para a rede. priv = é o personagem de quem recebe.
static func campos(e: Ent, priv: bool) -> Dictionary:
	var d := {}
	for k in PUB: d[k] = limpo(e.get(k))
	d["quebrado_t"] = snappedf(e.quebrado_t, 0.25)
	d["caminho"] = [] if e.caminho.is_empty() else [e.caminho[e.caminho.size() - 1]]
	var aux := {}
	if priv:
		for k in PRIV: d[k] = limpo(e.get(k))
		var st := {}
		for s in e.status: st[s] = limpo(e.status[s], 0.1)
		d["status"] = st
		d["buffs"] = limpo(e.buffs, 0.1)
		d["cds"] = limpo(e.cds, 0.05)
		d["cd_basico"] = snappedf(e.cd_basico, 0.05)
		d["buffer_skill"] = {} if e.buffer_skill.is_empty() else {"slot": e.buffer_skill.get("slot", 0)}
		d["interagindo"] = {} if e.interagindo.is_empty() else {"t": snappedf(float(e.interagindo.get("t", 0.0)), 0.1), "dur": e.interagindo.get("dur", 1.0)}
		for k in e.aux:
			if k in AUX_RUIDO: continue
			var x = limpo(e.aux[k], 0.05)
			if x != null: aux[k] = x
	else:
		var st2 := {}
		for s in e.status: st2[s] = {"pilhas": e.status[s].get("pilhas", 1)} if e.status[s] is Dictionary else {}
		d["status"] = st2
		for k in AUX_PUB:
			if e.aux.has(k):
				var x2 = limpo(e.aux[k])
				if x2 != null: aux[k] = x2
	d["aux"] = aux
	return d

## Diferença entre o que o cliente já tem e o atual ({} = nada mudou). aux vai chave a chave.
static func diff(velho: Dictionary, novo: Dictionary) -> Dictionary:
	var d := {}
	for k in novo:
		if k == "aux":
			var va: Dictionary = velho.get("aux", {})
			var na: Dictionary = novo["aux"]
			var mud := {}
			for ka in na:
				if not va.has(ka) or typeof(va[ka]) != typeof(na[ka]) or va[ka] != na[ka]: mud[ka] = na[ka]
			var sai: Array = []
			for ka in va:
				if not na.has(ka): sai.append(ka)
			if not mud.is_empty(): d["aux"] = mud
			if not sai.is_empty(): d["aux_x"] = sai
		elif not velho.has(k) or typeof(velho[k]) != typeof(novo[k]) or velho[k] != novo[k]:
			d[k] = novo[k]
	return d

## Cliente: aplica campos (completos ou diferença) no espelho, criando a entidade se ela é nova.
static func aplicar(sim: WorldSim, ents: Dictionary) -> void:
	for id in ents:
		var e: Ent = sim.ents.get(id)
		if e == null:
			e = Ent.new(); e.id = int(id)
			sim.ents[e.id] = e
		var d: Dictionary = ents[id]
		for k in d:
			match k:
				"aux":
					for ka in d["aux"]: e.aux[ka] = d["aux"][ka]
				"aux_x":
					for ka in d["aux_x"]: e.aux.erase(ka)
				_:
					e.set(k, d[k])

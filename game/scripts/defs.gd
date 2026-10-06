class_name Defs
## Carrega todos os dados do jogo (design das outras frentes + manifestos de assets).
## Nada aqui é desenho: é a "base de dados" que o servidor e o cliente consultam.

const DESIGN := "res://data/design/"

static var FORM := {}        # combate/formulas.json
static var CLASSES := {}     # combate/classes_base.json -> classes
static var MOBS := {}        # combate/mobs.json -> mobs (+ textos de missoes/monstros.json)
static var MOBS_BASE := {}   # combate/mobs.json inteiro (curva, arquetipos, ia)
static var CHEFES := {}      # combate/chefes.json -> chefes
static var CHEFES_REGRAS := {}
static var DROPS := {}       # combate/drops.json
static var SENS := {}        # combate/sensacao.json
static var EFEITOS := {}     # combate/efeitos.json (status e postura)
static var PROG := {}        # combate/progressao.json
static var ITENS := {}       # skills-itens/itens.json por id
static var ITENS_DOC := {}
static var POR_TAG := {}     # tag de drop -> [ids]
static var SKILLS := {}      # "classe/id_combate" -> skill completa (texto + combate + ícone)
static var NPCS := {}
static var DIALOGOS := {}
static var MISSOES := {}
static var MISSOES_LISTA: Array = []
static var OBJETOS := {}
static var BAUS_HIST := {}
static var LOJAS := {}
static var FERREIROS := {}
static var LOCAIS := {}      # subzonas e andares por id
static var MON_TXT := {}     # missoes/monstros.json por id
static var SPR := {}         # data/ext/sprites.json
static var SPR_SUBST := {}   # data/sprites_substitutos.json
static var VFX := {}
static var AUDIO := {}
static var ICONES := {}
static var AMB := {}         # kit de cenário (meta de cada asset)
static var SPOTS := {}       # design/mapas/spots.json por id (spots de farm da área inicial)
static var _expr_cache := {}
static var carregado := false

static func ler(path: String) -> Variant:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_warning("faltando: " + path)
		return {}
	var v = JSON.parse_string(f.get_as_text())
	return v if v != null else {}

static func carregar() -> void:
	if carregado: return
	carregado = true
	FORM = ler(DESIGN + "combate/formulas.json")
	CLASSES = ler(DESIGN + "combate/classes_base.json")["classes"]
	MOBS_BASE = ler(DESIGN + "combate/mobs.json")
	MOBS = MOBS_BASE["mobs"]
	var ch: Dictionary = ler(DESIGN + "combate/chefes.json")
	CHEFES = ch["chefes"]; CHEFES_REGRAS = ch["regras_gerais"]
	DROPS = ler(DESIGN + "combate/drops.json")
	SENS = ler(DESIGN + "combate/sensacao.json")
	EFEITOS = ler(DESIGN + "combate/efeitos.json")
	PROG = ler(DESIGN + "combate/progressao.json")
	ITENS_DOC = ler(DESIGN + "skills-itens/itens.json")
	for it in ITENS_DOC["itens"]:
		ITENS[it["id"]] = it
		for t in it.get("tags", []):
			if not POR_TAG.has(t): POR_TAG[t] = []
			POR_TAG[t].append(it["id"])
	# textos dos itens de missão (descrição) vêm da thread de missões
	for it in ler(DESIGN + "missoes/itens.json")["itens"]:
		if ITENS.has(it["id"]):
			for k in it:
				if not ITENS[it["id"]].has(k): ITENS[it["id"]][k] = it[k]
		else:
			ITENS[it["id"]] = it
	for s in ler(DESIGN + "skills-itens/skills.json")["skills"]:
		var cid: String = s["combate"]["id"] if s.has("combate") else s["id"]
		SKILLS[s["classe"] + "/" + cid] = s
	for n in ler(DESIGN + "missoes/npcs.json")["npcs"]: NPCS[n["id"]] = n
	for d in ler(DESIGN + "missoes/dialogos.json")["dialogos"]: DIALOGOS[d["id"]] = d
	MISSOES_LISTA = ler(DESIGN + "missoes/missoes.json")["missoes"]
	for m in MISSOES_LISTA: MISSOES[m["id"]] = m
	var ob: Dictionary = ler(DESIGN + "missoes/objetos.json")
	for o in ob["objetos"]: OBJETOS[o["id"]] = o
	for b in ob["baus"]: BAUS_HIST[b["id"]] = b
	var lj: Dictionary = ler(DESIGN + "missoes/lojas.json")
	for l in lj["lojas"]: LOJAS[l["id"]] = l
	for l in lj.get("ferreiros", []): FERREIROS[l["npc"]] = l
	var lc: Dictionary = ler(DESIGN + "missoes/locais.json")
	for a in lc["areas"]:
		for s in a["subzonas"]: LOCAIS[s["id"]] = s
	for dg in lc["dungeons"]:
		for s in dg["andares"]: LOCAIS[s["id"]] = s
	for m in ler(DESIGN + "missoes/monstros.json")["monstros"]: MON_TXT[m["id"]] = m
	_extras_v06()
	var sp: Dictionary = ler(DESIGN + "mapas/spots.json")
	for s in sp.get("spots", []): SPOTS[s["id"]] = s
	SPR = ler("res://data/ext/sprites.json")
	SPR_SUBST = ler("res://data/sprites_substitutos.json")
	VFX = ler("res://data/ext/efeitos.json")
	AUDIO = ler("res://data/ext/audio.json")
	ICONES = ler("res://data/ext/icones.json")
	AMB = ler("res://data/ext/ambiente.json")

## Avalia expressões dos JSON de design ("FOR/6 + AGI/10", "32 + 7*L").
static func expr(txt: String, nomes: PackedStringArray, valores: Array) -> float:
	var chave := txt + "|" + ",".join(nomes)
	var e: Expression = _expr_cache.get(chave)
	if e == null:
		e = Expression.new()
		if e.parse(txt.replace("^", "**"), nomes) != OK:
			push_warning("expressão inválida: " + txt)
			return 0.0
		_expr_cache[chave] = e
	var r = e.execute(valores, null, false)
	return float(r) if r != null else 0.0

## Dados que ainda faltam nas entregas (data/v06_extra.json): só entram se o design não tiver o mesmo id.
static func _extras_v06() -> void:
	var ex: Dictionary = ler("res://data/v06_extra.json")
	for k in ex.get("mobs", {}):
		if MOBS.has(k): continue
		var m: Dictionary = ex["mobs"][k].duplicate(true)
		if m.has("base") and MOBS.has(m["base"]):
			var b: Dictionary = MOBS[m["base"]].duplicate(true)
			b.merge(m, true)
			m = b
		MOBS[k] = m
		if not MON_TXT.has(k): MON_TXT[k] = {"id": k, "nome": m["nome"]}
	for n in ex.get("npcs", []):
		if not NPCS.has(n["id"]): NPCS[n["id"]] = n
	for d in ex.get("dialogos", []):
		if not DIALOGOS.has(d["id"]): DIALOGOS[d["id"]] = d
	for l in ex.get("lojas", []):
		if not LOJAS.has(l["id"]): LOJAS[l["id"]] = l

## Curva de XP (progressao.json v0.2: 75L² + 375L, 3x a v0.1 por causa dos spots e do modo automático).
static func xp_para_proximo(n: int) -> int:
	var x := 75.0 * n * n + 375.0 * n
	if n > 100: x *= 1.0 + (n - 100) / 50.0
	return int(round(x))

static func cor(hex: String) -> Color:
	return Color.from_string(hex, Color.WHITE)

static func cor_raridade(r: String) -> Color:
	var rr: Dictionary = DROPS["raridades"].get(r, {})
	return cor(rr.get("cor", "#b8afa0"))

static func nome_raridade(r: String) -> String:
	return {"comum": "Comum", "magico": "Mágico", "raro": "Raro", "excelente": "Excelente", "lendario": "Relíquia"}.get(r, r.capitalize())

## Sprite de um tipo de unidade (classe, monstro, npc). Usa substituto quando a arte ainda não chegou.
static func sprite(kind: String) -> Dictionary:
	if SPR.has(kind):
		return {"meta": SPR[kind], "escala": 1.0, "tint": Color.WHITE}
	var s: Dictionary = SPR_SUBST.get(kind, SPR_SUBST.get("_padrao", {}))
	var base: String = s.get("usa", "carnical")
	if not SPR.has(base): base = SPR.keys()[0]
	return {"meta": SPR[base], "escala": float(s.get("escala", 1.0)), "tint": cor(s.get("tint", "#ffffff")), "substituto": true}

static func skill(classe: String, id: String) -> Dictionary:
	return SKILLS.get(classe + "/" + id, {})

static func nome_local(id: String) -> String:
	return LOCAIS.get(id, {}).get("nome", id)

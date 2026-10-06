class_name Itens
## Itens: instâncias (raridade rolada, opções, refino), mochila em grade estilo MU, preços e bônus.

const MOCHILA_W := 12
const MOCHILA_H := 6
const ARMAZEM_W := 12
const ARMAZEM_H := 8
const SLOTS := ["arma", "segunda_mao", "cabeca", "peito", "luvas", "calcas", "botas", "amuleto", "anel1", "anel2"]
const NOME_SLOT := {"arma": "Arma", "segunda_mao": "2ª mão", "cabeca": "Cabeça", "peito": "Peito", "luvas": "Luvas",
	"calcas": "Calças", "botas": "Botas", "amuleto": "Amuleto", "anel1": "Anel", "anel2": "Anel"}
const ATTR := {"for": "FOR", "agi": "AGI", "vit": "VIT", "esp": "ESP"}

static var _uid := 1

static func defn(id: String) -> Dictionary:
	return Defs.ITENS.get(id, {})

static func novo(id: String, qtd: int = 1) -> Dictionary:
	var d := defn(id)
	_uid += 1
	var it := {"uid": _uid, "id": id, "qtd": qtd, "refino": 0, "opcoes": [], "raridade": d.get("raridade", "comum")}
	if it["raridade"] == "rolada" or it["raridade"] == null: it["raridade"] = "comum"
	if it["raridade"] == "unico": it["raridade"] = "lendario"
	return it

static func grade(it: Dictionary) -> Vector2i:
	var g = defn(it["id"]).get("grade", [1, 1])
	return Vector2i(int(g[0]), int(g[1]))

static func nome(it: Dictionary) -> String:
	var n: String = defn(it["id"]).get("nome", it["id"])
	if int(it.get("refino", 0)) > 0: n += " +%d" % it["refino"]
	return n

static func pilha(it: Dictionary) -> int:
	return int(defn(it["id"]).get("pilha", 1))

static func categoria(it: Dictionary) -> String:
	var d := defn(it["id"])
	var c: String = d.get("categoria", d.get("tipo", ""))
	return c

static func slot_de(it: Dictionary) -> String:
	return str(defn(it["id"]).get("slot", "")) if defn(it["id"]).get("slot") != null else ""

static func equipavel(it: Dictionary) -> bool:
	return slot_de(it) != ""

## Faixa de item: 1 para mobs até o nível 7, 2 a partir do 7 (meio a meio no 7).
static func faixa(nivel_mob: int, rng: RandomNumberGenerator) -> int:
	if nivel_mob < 7: return 1
	if nivel_mob > 7: return 2
	return 1 + rng.randi_range(0, 1)

static func rolar_raridade(rng: RandomNumberGenerator, minima: String) -> String:
	var ordem := ["comum", "magico", "raro", "excelente"]
	var pesos := []
	var tot := 0.0
	for r in ordem:
		var p := float(Defs.DROPS["raridades"][r]["peso_base"]) if ordem.find(r) >= ordem.find(minima) else 0.0
		pesos.append(p); tot += p
	var x := rng.randf() * tot
	for i in ordem.size():
		x -= pesos[i]
		if x <= 0.0: return ordem[i]
	return minima

static func rolar_refino(rng: RandomNumberGenerator) -> int:
	var ch: Dictionary = Defs.DROPS["nivel_de_refino_no_drop"]["chances"]
	var x := rng.randf()
	for k in ["+3", "+2", "+1"]:
		x -= float(ch[k])
		if x < 0.0: return int(k.substr(1))
	return 0

const OPCOES_NORMAIS := ["dano_plano", "defesa_plana", "hp_plano", "atributo", "critico", "velocidade_ataque", "roubo_de_vida", "res_elemento"]
const OPCOES_EXC := ["excelente_golpe", "excelente_dano", "excelente_reduz_dano", "excelente_ouro"]

static func _opcao(tipo: String, f: int, rng: RandomNumberGenerator) -> Dictionary:
	var faixa_v: Array = Defs.DROPS["opcoes_de_item"][tipo]["faixa%d" % f]
	var v: float
	if typeof(faixa_v[0]) == TYPE_FLOAT and float(faixa_v[0]) < 1.0 and float(faixa_v[1]) < 1.0:
		v = snappedf(rng.randf_range(faixa_v[0], faixa_v[1]), 0.005)
	else:
		v = float(rng.randi_range(int(faixa_v[0]), int(faixa_v[1])))
	var o := {"tipo": tipo, "valor": v}
	if tipo == "atributo": o["attr"] = ["FOR", "AGI", "VIT", "ESP"][rng.randi_range(0, 3)]
	if tipo == "res_elemento": o["elem"] = ["fogo", "sagrado", "veneno", "sangue", "eletrico"][rng.randi_range(0, 4)]
	return o

## Gera um equipamento base com raridade, opções e refino.
static func gerar_equip(id: String, rng: RandomNumberGenerator, minima: String, f: int) -> Dictionary:
	var it := novo(id)
	var d := defn(id)
	if d.get("raridade", "rolada") != "rolada":
		return it
	var r := rolar_raridade(rng, minima)
	it["raridade"] = r
	it["refino"] = rolar_refino(rng)
	var rr: Dictionary = Defs.DROPS["raridades"][r]
	var n := 0
	var oe = rr.get("opcoes_extras", 0)
	if typeof(oe) == TYPE_ARRAY: n = rng.randi_range(int(oe[0]), int(oe[1]))
	else: n = int(oe)
	var usados := []
	if rr.get("opcao_excelente_garantida", false):
		var ex: String = OPCOES_EXC[rng.randi_range(0, OPCOES_EXC.size() - 1)]
		it["opcoes"].append(_opcao(ex, f, rng)); usados.append(ex)
	var pool: Array = OPCOES_NORMAIS.duplicate()
	if d.has("dano"): pool.erase("defesa_plana")
	else: pool.erase("dano_plano")
	for i in n:
		var t: String = pool[rng.randi_range(0, pool.size() - 1)]
		if t in usados: continue
		usados.append(t)
		it["opcoes"].append(_opcao(t, f, rng))
	return it

static func preco(it: Dictionary) -> int:
	var d := defn(it["id"])
	if d.has("preco"): return int(d["preco"])
	var nv := int(d.get("nivel", 1))
	var base := 12 + nv * 9
	var mult: float = {"comum": 1.0, "magico": 2.2, "raro": 5.0, "excelente": 10.0, "lendario": 25.0}.get(it.get("raridade", "comum"), 1.0)
	match categoria(it):
		"missao", "leitura": return 0
		"material": return 4
		"joia": return 250
		"chave": return 40
	return int(base * mult * (1.0 + 0.25 * int(it.get("refino", 0))))

static func preco_venda(it: Dictionary) -> int:
	return maxi(1, int(preco(it) * 0.25)) * int(it.get("qtd", 1)) if preco(it) > 0 else 0

# ------------------------------------------------------------------ bônus do equipamento
## Soma o que o equipamento dá: dano da arma, defesa, atributos, opções.
static func bonus(equip: Dictionary) -> Dictionary:
	var b := {"FOR": 0.0, "AGI": 0.0, "VIT": 0.0, "ESP": 0.0, "defesa": 0.0, "hp": 0.0, "dano_plano": 0.0, "critico": 0.0,
		"velocidade_ataque": 0.0, "roubo_de_vida": 0.0, "excelente": 0.0, "excelente_dano": 0.0, "reduz_dano": 0.0,
		"ouro": 0.0, "res": {}, "dano_magico_extra": 0.0, "bloqueio": 0.0, "efeitos": []}
	var conj := {}
	for s in equip:
		var it: Dictionary = equip[s]
		if it.is_empty(): continue
		var d := defn(it["id"])
		var ref := 1.0 + 0.08 * int(it.get("refino", 0))
		if s != "arma" and d.has("defesa"): b["defesa"] += float(d["defesa"]) * ref
		if s == "segunda_mao" and d.has("defesa"): pass
		b["bloqueio"] += float(d.get("bloqueio", 0.0))
		b["dano_magico_extra"] += float(d.get("dano_magico_extra", 0.0)) * ref
		for src in ["atributos", "atributo_base"]:
			var at = d.get(src)
			if typeof(at) != TYPE_DICTIONARY: continue
			for k in at:
				if ATTR.has(k): b[ATTR[k]] += float(at[k])
				elif k == "hp": b["hp"] += float(at[k])
		for o in it.get("opcoes", []):
			match o["tipo"]:
				"dano_plano": b["dano_plano"] += o["valor"]
				"defesa_plana": b["defesa"] += o["valor"]
				"hp_plano": b["hp"] += o["valor"]
				"atributo": b[o["attr"]] += o["valor"]
				"critico": b["critico"] += o["valor"]
				"velocidade_ataque": b["velocidade_ataque"] += o["valor"]
				"roubo_de_vida": b["roubo_de_vida"] += o["valor"]
				"res_elemento": b["res"][o["elem"]] = b["res"].get(o["elem"], 0.0) + o["valor"]
				"excelente_golpe": b["excelente"] += o["valor"]
				"excelente_dano": b["excelente_dano"] += o["valor"]
				"excelente_reduz_dano": b["reduz_dano"] += o["valor"]
				"excelente_ouro": b["ouro"] += o["valor"]
		if d.get("efeito") is String: b["efeitos"].append(it["id"])
		if d.has("conjunto"): conj[d["conjunto"]] = conj.get(d["conjunto"], 0) + 1
	b["conjuntos"] = conj
	return b

static func dano_arma(it: Dictionary) -> Array:
	var d := defn(it["id"])
	var dn = d.get("dano", [3, 6])
	var ref := 1.0 + 0.08 * int(it.get("refino", 0))
	return [float(dn[0]) * ref, float(dn[1]) * ref]

static func pode_usar(it: Dictionary, e: Ent) -> String:
	var d := defn(it["id"])
	var cl = d.get("classes", d.get("classe"))
	if cl != null and typeof(cl) == TYPE_ARRAY and cl.size() > 0 and not e.classe in cl:
		return "Sua classe não usa isto."
	if d.get("faccao") != null and d.get("faccao") != e.faccao:
		return "Só para a %s." % ("Vigília" if d["faccao"] == "vigilia" else "Arautos do Juízo")
	if int(d.get("nivel", 1)) > e.nivel:
		return "Requer nível %d." % int(d["nivel"])
	return ""

# ------------------------------------------------------------------ grade da mochila
static func _ocupado(lista: Array, w: int, h: int, ignora: int = -1) -> Array:
	var occ := []
	occ.resize(w * h); occ.fill(false)
	for it in lista:
		if it["uid"] == ignora: continue
		var g := grade(it)
		for yy in g.y:
			for xx in g.x:
				var cx: int = int(it["x"]) + xx
				var cy: int = int(it["y"]) + yy
				if cx < w and cy < h: occ[cy * w + cx] = true
	return occ

static func cabe_em(lista: Array, w: int, h: int, it: Dictionary, x: int, y: int, ignora: int = -1) -> bool:
	var g := grade(it)
	if x < 0 or y < 0 or x + g.x > w or y + g.y > h: return false
	var occ := _ocupado(lista, w, h, ignora)
	for yy in g.y:
		for xx in g.x:
			if occ[(y + yy) * w + x + xx]: return false
	return true

static func achar_lugar(lista: Array, w: int, h: int, it: Dictionary) -> Vector2i:
	var g := grade(it)
	var occ := _ocupado(lista, w, h)
	for y in h - g.y + 1:
		for x in w - g.x + 1:
			var ok := true
			for yy in g.y:
				for xx in g.x:
					if occ[(y + yy) * w + x + xx]: ok = false; break
				if not ok: break
			if ok: return Vector2i(x, y)
	return Vector2i(-1, -1)

## Coloca na lista (empilhando quando dá). Devolve a quantidade que NÃO coube.
static func guardar(lista: Array, w: int, h: int, it: Dictionary) -> int:
	var mx := pilha(it)
	var qtd := int(it.get("qtd", 1))
	if mx > 1:
		for o in lista:
			if o["id"] == it["id"] and int(o["qtd"]) < mx:
				var add := mini(mx - int(o["qtd"]), qtd)
				o["qtd"] = int(o["qtd"]) + add; qtd -= add
				if qtd <= 0: return 0
	it["qtd"] = qtd
	while qtd > 0:
		var p := achar_lugar(lista, w, h, it)
		if p.x < 0: return qtd
		var novo_it := it.duplicate(true)
		_uid += 1
		if lista.any(func(o): return o["uid"] == it["uid"]): novo_it["uid"] = _uid
		novo_it["qtd"] = mini(qtd, mx); novo_it["x"] = p.x; novo_it["y"] = p.y
		lista.append(novo_it)
		qtd -= int(novo_it["qtd"])
	return 0

static func contar(lista: Array, id: String) -> int:
	var n := 0
	for o in lista:
		if o["id"] == id: n += int(o["qtd"])
	return n

static func remover(lista: Array, id: String, qtd: int) -> int:
	var tirou := 0
	for o in lista.duplicate():
		if tirou >= qtd: break
		if o["id"] != id: continue
		var t := mini(int(o["qtd"]), qtd - tirou)
		o["qtd"] = int(o["qtd"]) - t; tirou += t
		if int(o["qtd"]) <= 0: lista.erase(o)
	return tirou

static func por_uid(lista: Array, uid: int) -> Dictionary:
	for o in lista:
		if o["uid"] == uid: return o
	return {}

## Texto das opções para o tooltip.
static func texto_opcao(o: Dictionary) -> String:
	var v: float = o["valor"]
	match o["tipo"]:
		"dano_plano": return "+%d de dano" % v
		"defesa_plana": return "+%d de defesa" % v
		"hp_plano": return "+%d de vida" % v
		"atributo": return "+%d %s" % [v, o["attr"]]
		"critico": return "+%.1f%% de chance de crítico" % (v * 100)
		"velocidade_ataque": return "+%d%% de velocidade de ataque" % roundi(v * 100)
		"roubo_de_vida": return "+%.1f%% de roubo de vida" % (v * 100)
		"res_elemento": return "+%d%% de resistência a %s" % [roundi(v * 100), o["elem"]]
		"excelente_golpe": return "Golpe excelente +%d%%" % roundi(v * 100)
		"excelente_dano": return "Dano +%d%%" % roundi(v * 100)
		"excelente_reduz_dano": return "Reduz o dano recebido em %d%%" % roundi(v * 100)
		"excelente_ouro": return "Ouro dos monstros +%d%%" % roundi(v * 100)
	return o["tipo"]

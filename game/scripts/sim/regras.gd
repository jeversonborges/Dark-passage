class_name Regras
## Fórmulas de combate (design/combate/formulas.json). Tudo estático e determinístico dado o RNG.

const PERFIS := {
	"corpo_a_corpo": ["FOR/6", "FOR/4"],
	"corpo_a_corpo_agil": ["FOR/6 + AGI/10", "FOR/4 + AGI/10"],
	"distancia": ["AGI/7 + FOR/14", "AGI/4 + FOR/8"],
	"magico": ["ESP/9", "ESP/4"],
	"sagrado": ["ESP/10 + FOR/12", "ESP/5 + FOR/8"],
	"hibrido": ["FOR/6", "FOR/4"],   # espada larga; o tiro usa "distancia" + arma secundária (aux.tiro)
}
const NOMES_ATTR := ["FOR", "AGI", "VIT", "ESP"]

static func _attr_vals(e: Ent) -> Array:
	return [float(e.stats["FOR"]), float(e.stats["AGI"]), float(e.stats["VIT"]), float(e.stats["ESP"])]

## Recalcula tudo que deriva de atributos + equipamento + buffs de um jogador.
static func recalc_jogador(e: Ent) -> void:
	var c: Dictionary = Defs.CLASSES[e.classe]
	var b := Itens.bonus(e.equip)
	e.aux["bonus"] = b
	var base_stats: Dictionary = e.stats
	var st := {}
	for k in NOMES_ATTR:
		st[k] = float(base_stats[k]) + float(b[k]) + e.mod(k)
	e.aux["ef"] = st
	var F: float = st["FOR"]; var A: float = st["AGI"]; var V: float = st["VIT"]; var E: float = st["ESP"]
	var vals := [F, A, V, E]
	var hp_old := e.frac_hp()
	e.hp_max = float(c["hp"]["base"]) + float(c["hp"]["por_nivel"]) * e.nivel + float(c["hp"]["por_vit"]) * V + float(b["hp"])
	e.hp_max *= 1.0 + e.mod("hp_pct")
	if e.hp > 0.0: e.hp = minf(e.hp, e.hp_max)
	var perfil: Array = PERFIS[c["perfil_dano"]]
	var arma := Ent_arma(e)
	var mn := Defs.expr(perfil[0], NOMES_ATTR, vals) + float(arma["min"]) + float(b["dano_plano"]) + float(b["dano_magico_extra"])
	var mx := Defs.expr(perfil[1], NOMES_ATTR, vals) + float(arma["max"]) + float(b["dano_plano"]) + float(b["dano_magico_extra"])
	e.dano_min = mn; e.dano_max = maxf(mx, mn)
	if c["perfil_dano"] == "hibrido":
		var sec: Dictionary = c["arma_secundaria"]
		var pt: Array = PERFIS["distancia"]
		var tmn := Defs.expr(pt[0], NOMES_ATTR, vals) + float(sec["min"]) + float(b["dano_plano"])
		var tmx := Defs.expr(pt[1], NOMES_ATTR, vals) + float(sec["max"]) + float(b["dano_plano"])
		e.aux["tiro"] = [tmn, maxf(tmx, tmn)]
	e.defesa = V / 5.0 + A / 10.0 + float(b["defesa"])
	var magico: bool = c["perfil_dano"] == "magico"
	e.ar = e.nivel * 3.0 + ((E / 2.0 + A / 2.0) if magico else (A + F / 4.0))
	e.er = e.nivel * 2.0 + A / 2.0
	e.critico = minf(float(Defs.FORM["critico"]["chance_max"]), 0.05 + A * 0.0008 + float(b["critico"]) + e.mod("critico"))
	e.crit_mult = float(Defs.FORM["critico"]["mult_por_classe"].get(e.classe, Defs.FORM["critico"]["mult"]))
	e.excelente = minf(0.25, float(b["excelente"]))
	e.vel_ataque = minf(2.0, 1.0 + A * 0.004 + float(b["velocidade_ataque"]) + e.mod("velocidade_ataque"))
	e.intervalo = float(arma["intervalo"]) / e.vel_ataque
	e.alcance = float(c["alcance_basico"]["espada"]) if c["alcance_basico"] is Dictionary else float(c["alcance_basico"])
	e.elemento = c["elemento_ataque"]
	e.postura_arma = float(arma.get("postura", 10))
	e.roubo_vida = float(c.get("roubo_de_vida", 0.0)) + float(b["roubo_de_vida"])
	e.res = b["res"].duplicate()
	if e.classe == "mutante":
		for r in Defs.FORM["vantagem_cruzada"]["mutante"]["resiste"]: e.res[r] = e.res.get(r, 0.0) + 0.3
	e.vel = float(Defs.MOBS_BASE["velocidade_mov_jogador"]) * (1.0 + e.mod("vel"))
	# recurso
	var rc: Dictionary = c["recurso"]
	match e.classe:
		"anjo", "tecnomancer": e.rec_max = 100.0 + E / 2.0
		"mutante", "demonio": e.rec_max = 100.0
		"humano": e.rec_max = float(rc["folego"]["max"])
		"cultista": e.rec_max = 0.0
	e.rec = minf(e.rec, e.rec_max)
	if hp_old > 0.0 and e.hp <= 0.0: e.hp = e.hp_max * hp_old

static func Ent_arma(e: Ent) -> Dictionary:
	var c: Dictionary = Defs.CLASSES[e.classe]
	var it: Dictionary = e.equip.get("arma", {})
	if it.is_empty():
		var a: Dictionary = c["arma_inicial"]
		return {"min": a["min"] * 0.5, "max": a["max"] * 0.5, "intervalo": a["intervalo"], "postura": a.get("postura", 8), "projetil_vel": a.get("projetil_vel", 0)}
	var d := Itens.defn(it["id"])
	var dn := Itens.dano_arma(it)
	return {"min": dn[0], "max": dn[1], "intervalo": d.get("intervalo", c["arma_inicial"]["intervalo"]),
		"postura": c["arma_inicial"].get("postura", 10), "projetil_vel": c["arma_inicial"].get("projetil_vel", 0), "tipo": d.get("tipo", "")}

## Monta um mob a partir da curva base, arquétipo e ajuste (design/combate/mobs.json).
static func montar_mob(e: Ent, m: Dictionary, nivel: int) -> void:
	var cb: Dictionary = Defs.MOBS_BASE["curva_base"]
	var arq: Dictionary = Defs.MOBS_BASE["arquetipos"][m.get("arquetipo", "normal")]
	var aj: Dictionary = m.get("ajuste", {})
	var L := float(nivel)
	e.nivel = nivel
	e.arquetipo = m.get("arquetipo", "normal")
	e.hp_max = roundf(Defs.expr(cb["hp"], ["L"], [L]) * float(arq["hp"]) * float(aj.get("hp", 1.0)))
	e.hp = e.hp_max
	var dm := float(arq["dano"]) * float(aj.get("dano", 1.0))
	e.dano_min = Defs.expr(cb["dano_min"], ["L"], [L]) * dm
	e.dano_max = Defs.expr(cb["dano_max"], ["L"], [L]) * dm
	e.defesa = Defs.expr(cb["defesa"], ["L"], [L]) * float(arq["defesa"]) * float(aj.get("defesa", 1.0))
	e.intervalo = float(arq["intervalo"])
	e.vel = float(cb["velocidade_mov"]) * float(arq["mov"]) * float(aj.get("mov", 1.0))
	e.ar = L * 4.0 + 10.0
	e.er = L * 3.0 + 5.0
	e.critico = 0.05
	e.crit_mult = 1.5
	e.alcance = float(m.get("alcance", 1.2))
	e.res = m.get("res", {}).duplicate()
	e.tags = m.get("tags", []).duplicate()
	e.postura_max = float(Defs.EFEITOS["postura"]["max_por_arquetipo"].get(arq.get("postura", "normal"), 30))
	e.postura = e.postura_max
	e.elemento = "fisico"

static func xp_mob(e: Ent) -> float:
	var arq: Dictionary = Defs.MOBS_BASE["arquetipos"].get(e.arquetipo, {"xp": 1.0})
	return (10.0 + 5.0 * e.nivel) * float(arq.get("xp", 1.0))

static func mod_xp_nivel(nivel_mob: int, nivel_jog: int) -> float:
	var d := nivel_mob - nivel_jog
	if d >= 5: return 1.2
	if d >= -3: return 1.0 + 0.04 * d
	return maxf(0.10, 1.0 - 0.15 * (-d - 3) - 0.12)

static func mitigacao(defesa: float, nivel_atk: int) -> float:
	if defesa <= 0.0: return 0.0
	return minf(float(Defs.FORM["defesa"]["mitigacao_max"]), defesa / (defesa + 40.0 + 8.0 * nivel_atk))

static func chance_acerto(ar: float, er: float, dl: int) -> float:
	var c := 0.90 + 0.25 * (ar - er) / maxf(ar + er, 1.0) - 0.03 * maxi(0, dl)
	return clampf(c, 0.55, 0.98)

static func mult_nivel(nivel_alvo: int, nivel_atk: int) -> float:
	var d := nivel_alvo - nivel_atk
	if d > 0: return maxf(0.40, 1.0 - 0.04 * d)
	return minf(1.20, 1.0 + 0.02 * (-d))

static func tem_tag(alvo: Ent, chave: String) -> bool:
	if chave.begins_with("tag:"): return chave.substr(4) in alvo.tags
	return alvo.classe == chave or alvo.kind == chave

static func mult_vantagem(atk: Ent, alvo: Ent) -> float:
	var v: Dictionary = Defs.FORM["vantagem_cruzada"].get(atk.classe if atk.tipo == "jogador" else "", {})
	if v.has("alvos"):
		for a in v["alvos"]:
			if tem_tag(alvo, a): return float(v["mult"])
	return 1.0

## Resolve um golpe. op: mult, add, elemento, area (nunca erra), crit_extra, magico, bonus_vs, postura, forca_crit.
## Devolve {dano, crit, exc, errou, imune}.
static func golpe(atk: Ent, alvo: Ent, op: Dictionary, rng: RandomNumberGenerator) -> Dictionary:
	var r := {"dano": 0, "crit": false, "exc": false, "errou": false}
	if not op.get("area", false) and not op.get("nunca_erra", false):
		var ar := atk.ar
		var ch := chance_acerto(ar, alvo.er, alvo.nivel - atk.nivel)
		if atk.tem("cegueira"): ch -= 0.5
		if rng.randf() > ch:
			r["errou"] = true
			return r
	var faixa: Array = op.get("faixa", [atk.dano_min, atk.dano_max])
	var bruto := rng.randf_range(float(faixa[0]), float(faixa[1])) * float(op.get("mult", 1.0)) + float(op.get("add", 0.0))
	if atk.aux.get("bonus_prox_t", 0.0) > 0.0 and op.get("skill", "") != "arrancada":
		bruto *= 1.0 + float(atk.aux.get("bonus_prox", 0.0)); atk.aux["bonus_prox_t"] = 0.0
	if op.has("base_fixa"): bruto = float(op["base_fixa"]) * rng.randf_range(0.9, 1.1)
	var crit_ch := atk.critico + float(op.get("crit_extra", 0.0))
	if op.get("forca_crit", false) or rng.randf() < crit_ch:
		r["crit"] = true; bruto *= atk.crit_mult
	var def_ef := alvo.defesa * (1.0 + alvo.mod("defesa_pct"))
	if atk.excelente > 0.0 and rng.randf() < atk.excelente:
		r["exc"] = true; bruto *= 1.2; def_ef *= 0.5
		bruto *= 1.0 + float(atk.aux.get("bonus", {}).get("excelente_dano", 0.0))
	var mit := mitigacao(def_ef, atk.nivel)
	var dano := maxf(bruto * (1.0 - mit), bruto * 0.05)
	var el: String = op.get("elemento", atk.elemento)
	dano *= 1.0 - clampf(float(alvo.res.get(el, 0.0)), -1.0, 0.75)
	dano *= mult_nivel(alvo.nivel, atk.nivel) * mult_vantagem(atk, alvo)
	for k in op.get("bonus_vs", {}):
		if tem_tag(alvo, k): dano *= float(op["bonus_vs"][k])
	# buffs do atacante e debuffs do alvo
	dano *= 1.0 + atk.mod("dano") + (atk.mod("dano_magico") if op.get("magico", false) else 0.0)
	dano *= 1.0 + alvo.mod("dano_recebido")
	if alvo.tem("marcado"): dano *= 1.15
	if alvo.quebrado_t > 0.0: dano *= 1.0 + float(Defs.EFEITOS["postura"]["quebrado_dano_recebido_extra"])
	if alvo.tipo == "jogador": dano *= 1.0 - float(alvo.aux.get("bonus", {}).get("reduz_dano", 0.0))
	# recursos que dão dano
	if atk.classe == "mutante": dano *= 1.0 + floorf(atk.rec / 10.0) * 0.02
	if atk.classe == "demonio" and atk.rec >= 80.0: dano *= 1.15
	if atk.aux.has("enrage"): dano *= 1.5
	r["dano"] = maxi(1, roundi(dano))
	return r

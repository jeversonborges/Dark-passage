class_name Revista
## A Gazeta do Impasse: o que cada chefe de masmorra e de raid solta, lido dos dados de combate
## (drops.json, chefes.json, v06_extra.json). Nada aqui é escrito à mão: quem muda um drop muda o dado.
## Itens marcados "secreto" no design e recompensas de missão ficam de fora.

const NOMES_EXTRA := {"a_torre": "A Torre", "catacumba_das_raizes": "Catacumba das Raízes", "atlantida": "Atlântida"}

static func _oculto(id: String) -> bool:
	return bool(Defs.ITENS.get(id, {}).get("secreto", false))

static func _nome_masmorra(id: String) -> String:
	return str(Defs.DUNGEONS.get(id, {}).get("nome", NOMES_EXTRA.get(id, id)))

static func _rotulo(tag: String) -> String:
	if tag.begins_with("equip:faixa"): return "Equipamento · faixa %s" % tag.substr(11)
	if tag.begins_with("lendario:"): return "Relíquia"
	if tag.begins_with("joia:"): return "Joia de refino"
	if tag.begins_with("material:"): return "Material"
	if tag.begins_with("consumivel:"): return "Consumível"
	if tag.begins_with("chave:"): return "Chave"
	return tag

## Ids de itens que uma rolagem pode trazer (sem os secretos e sem as recompensas de missão).
static func _ids(tag: String) -> Array:
	if tag.begins_with("missao:"): return []
	var pool: Array = Defs.ITENS_DOC["pools_lendarios"].get(tag, []) if tag.begins_with("lendario:") else Defs.POR_TAG.get(tag, [])
	return pool.filter(func(i): return not _oculto(i))

static func _chefe(ch: Dictionary) -> Dictionary:
	var t: Dictionary = Defs.DROPS["tabelas"][ch["drop"]]
	var bd: Dictionary = Defs.DROPS["balanco"]["bau_dourado"]
	var nivel := int(ch.get("nivel", 1))
	var bau := float(bd["chefe_top"] if nivel >= int(bd["nivel_chefe_top"]) else bd["elite_ou_chefe"])
	var tot := 0.0
	for r in t.get("rolagens", []): tot += float(r["peso"])
	var rolagens := []
	for r in t.get("rolagens", []):
		var tag := str(r["tag"])
		var ids := _ids(tag)
		if ids.is_empty(): continue
		rolagens.append({
			"pct": float(r["peso"]) / tot * 100.0,
			"rotulo": _rotulo(tag),
			"raridade": "lendario" if tag.begins_with("lendario:") else str(t.get("raridade_minima", "comum")),
			"itens": ids,
		})
	return {
		"id": ch.get("id", ""),
		"nome": ch.get("nome", ""),
		"nivel": nivel,
		"rolagens_garantidas": int(t.get("rolagens_garantidas", 0)),
		"raridade_minima": str(t.get("raridade_minima", "comum")),
		"bau_pct": bau * 100.0,
		"rolagens": rolagens,
	}

## Uma página por masmorra ou raid, com os chefes em ordem de nível.
static func paginas() -> Array:
	var grupos := {}
	var masmorra_de := {}   # chefes.json não diz a masmorra: vem do registro de chefes (locais.json)
	for r in Defs.REG_CHEFES: masmorra_de[r["id"]] = r["dungeon"]
	for k in Defs.CHEFES:
		var ch: Dictionary = Defs.CHEFES[k]
		var dg := str(ch.get("raid", ch.get("dungeon", masmorra_de.get(k, ""))))
		if dg == "" or not Defs.DROPS["tabelas"].has(ch.get("drop")): continue
		ch = ch.duplicate(); ch["id"] = k
		if not grupos.has(dg): grupos[dg] = {"id": dg, "nome": _nome_masmorra(dg), "raid": ch.has("raid"), "chefes": []}
		grupos[dg]["chefes"].append(_chefe(ch))
	var lista := grupos.values()
	for g in lista:
		g["chefes"].sort_custom(func(a, b): return a["nivel"] < b["nivel"])
		g["nivel_min"] = g["chefes"][0]["nivel"]
		g["nivel_max"] = g["chefes"][-1]["nivel"]
		g["grupo"] = Defs.DUNGEONS.get(g["id"], {}).get("grupo", [])
	lista.sort_custom(func(a, b): return a["nivel_min"] < b["nivel_min"])
	return lista

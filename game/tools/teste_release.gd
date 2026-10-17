extends SceneTree
const Unidade := preload("res://scripts/client/unidade.gd")
## Portão de release: falha (saída 1) se algum portal aponta para mapa inexistente ou vazio,
## ou se alguma skill fica sem ícone que não esteja pendente em data/icones_pendentes.json (a arte é pintada pelo Jefin), ou se algum item de mão principal fica sem camada (a Abominação só tem corpo; itens de segunda mão podem ficar sem).

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var portais := 0
	var mapas := {}
	for f in DirAccess.get_files_at("res://data/mapas"):
		if f.ends_with(".json"): mapas[f.get_basename()] = "res://data/mapas/" + f
	for id in mapas:
		var m: Dictionary = Defs.ler(mapas[id])
		for o in m.get("objetos", []):
			if not (o is Dictionary) or not o.has("para"): continue
			var destino := str(o["para"])
			portais += 1
			if not mapas.has(destino):
				print("FALHA: portal em %s leva a '%s', que não existe" % [id, destino]); falhas += 1; continue
			var d: Dictionary = Defs.ler(mapas[destino])
			if d.get("grade", []).is_empty():
				print("FALHA: portal em %s leva a '%s', que abre vazio" % [id, destino]); falhas += 1
	var u := Unidade.new()
	for kind in Defs.PADRAO:
		if kind == "abominacao": continue
		u._kind_armas = kind
		for item_id in Defs.VISUAIS:
			if Defs.VISUAIS[item_id].get("mao", "R") == "L": continue   # segunda mão: sem camada, mão esquerda vazia
			var sil: String = u._silhueta_arma({"id": item_id}, "arma")
			if sil == "" or not FileAccess.file_exists("res://assets/ext/armas/%s/%s.json" % [kind, sil]):
				print("FALHA: %s com %s sem camada na mão" % [kind, item_id]); falhas += 1
	var sem_icone := 0
	var pendentes: Array = Defs.ler("res://data/icones_pendentes.json")
	for chave in Defs.SKILLS:
		var classe := str(chave).get_slice("/", 0)
		var sid := str(chave).get_slice("/", 1)
		var k := sid if sid.begins_with(classe + "_") else classe + "_" + sid
		if Defs.ICONES.get("skills_40", {}).has(k): continue
		if k in pendentes: print("AVISO: skill sem ícone (pendente na LISTA.md): %s" % k)
		else: sem_icone += 1; print("FALHA: skill sem ícone: %s" % k)
	falhas += sem_icone
	print("teste_release: %s (%d mapas, %d portais verificados)" % ["OK" if falhas == 0 else "%d falha(s)" % falhas, mapas.size(), portais])
	quit(falhas)

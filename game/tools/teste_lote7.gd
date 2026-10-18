extends SceneTree
## Lote 7 de itens novos 0.9.7 (18/10): 104 sobras de ícone viram itens, com ícone no atlas e tags de drop ligadas.
## Rodar: godot --headless -s tools/teste_lote7.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var ids := []
	for id in Defs.ITENS:
		if str(Defs.ITENS[id].get("fonte", "")).contains("lote7") or str(Defs.ITENS[id].get("icone_mochila", "")).contains("elmo_do_manto_sangrento"):
			ids.append(id)
	if ids.size() != 104:
		print("FALHA: %d itens do lote 7 (esperado 104)" % ids.size()); falhas += 1
	for id in ids:
		var d: Dictionary = Defs.ITENS[id]
		if not Defs.ICONES.get("itens_64", {}).has(id): print("FALHA: sem ícone 64 em %s" % id); falhas += 1
		if not Defs.ICONES.get("mochila", []).has(id): print("FALHA: sem ícone de mochila em %s" % id); falhas += 1
		if str(d.get("categoria", "")) == "arma" and not d.has("dano"): print("FALHA: arma sem dano em %s" % id); falhas += 1
		if d.has("efeito") and d["efeito"] is String and str(d["efeito"]) == "": print("FALHA: efeito vazio em %s" % id); falhas += 1
	if absf(float(Itens.bonus({"amuleto": Itens.novo("ankh_de_asas")})["perda_xp_menos"]) - 0.10) > 0.0001:
		print("FALHA: perda de XP do Ankh de Asas"); falhas += 1
	if absf(float(Itens.bonus({"amuleto": Itens.novo("bussola_de_ouro_e_safira")})["evasao"]) - 0.02) > 0.0001:
		print("FALHA: esquiva da Bússola"); falhas += 1
	print("teste_lote7: %s (itens: %d)" % ["OK" if falhas == 0 else "%d falha(s)" % falhas, ids.size()])
	quit(1 if falhas > 0 else 0)

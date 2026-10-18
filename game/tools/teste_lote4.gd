extends SceneTree
## Lote 4 de itens novos 0.9.6 (18/10): dois equipamentos com efeito de Relíquia e dois papiros de leitura entram em itens.json.
## Rodar: godot --headless -s tools/teste_lote4.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	for id in ["balanca_do_coracao", "escudo_de_anubis", "livro_das_cordas_de_ankh", "papiro_das_carpideiras"]:
		if not Defs.ITENS.has(id): print("FALHA: item %s ausente" % id); falhas += 1
	if Defs.ITENS.has("balanca_do_coracao") and absf(float(Itens.bonus({"amuleto": Itens.novo("balanca_do_coracao")})["evasao"]) - 0.04) > 0.0001:
		print("FALHA: evasão da Balança"); falhas += 1
	if Defs.ITENS.has("escudo_de_anubis") and int(Itens.bonus({"segunda_mao": Itens.novo("escudo_de_anubis")})["defesa"]) != 15:
		print("FALHA: defesa do Escudo de Anúbis (esperado 14 + 10% = 15)"); falhas += 1
	print("teste_lote4: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(1 if falhas > 0 else 0)

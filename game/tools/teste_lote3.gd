extends SceneTree
## Lote 3 de itens novos 0.9.6 (18/10): dez itens entram em itens.json e nas tabelas de drop; missão ficam de fora.
## Rodar: godot --headless -s tools/teste_lote3.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var ids := ["emblema_da_cerca", "escudo_do_coro_dourado", "ampulheta_do_juizo_travado", "lanterna_do_cranio_verde", "cinto_de_caveira",
		"livro_do_olho_roxo", "coracao_de_vidro", "ampulheta_da_trombeta", "medalhao_do_sol_de_latao", "astrolabio_do_deserto"]
	for id in ids:
		if not Defs.ITENS.has(id): print("FALHA: item %s ausente" % id); falhas += 1
	if Defs.ITENS.has("cinto_de_caveira") and Defs.ITENS["cinto_de_caveira"].get("slot") != "calcas": print("FALHA: slot do cinto"); falhas += 1
	var livro: Dictionary = Defs.ITENS.get("livro_do_olho_roxo", {})
	if float(livro.get("efeito", {}).get("xp_pct", 0)) != 10.0: print("FALHA: XP do livro"); falhas += 1
	var coracao: Dictionary = Defs.ITENS.get("coracao_de_vidro", {})
	if float(coracao.get("efeito", {}).get("cura_hp_pct", 0)) != 20.0 or float(coracao.get("efeito", {}).get("recurso_pct", 0)) != -0.05:
		print("FALHA: efeito do Coração de Vidro"); falhas += 1
	for tag in ["raro:sao_lazaro", "consumivel:xp", "consumivel:cura", "raro:egito", "excelente:atlantida"]:
		if Defs.POR_TAG.get(tag, []).is_empty(): print("FALHA: tag %s sem itens" % tag); falhas += 1
	if not ("ampulheta_do_juizo_travado" in Defs.ITENS_DOC["pools_lendarios"].get("lendario:atlantida", [])):
		print("FALHA: ampulheta fora do pool de Atlântida"); falhas += 1
	print("teste_lote3: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(1 if falhas > 0 else 0)

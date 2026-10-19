extends SceneTree
## Azul (Mágico) e verde (Excelente) +40% em drop de mob comum (0.9.8). Rodar: godot --headless -s tools/teste_verdeazul.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var rng := RandomNumberGenerator.new()
	rng.seed = 8080
	var n := 400000
	var base := {"comum": 0, "magico": 0, "raro": 0, "excelente": 0}
	var bonus := {"comum": 0, "magico": 0, "raro": 0, "excelente": 0}
	for i in n:
		base[Itens.rolar_raridade(rng, "comum", 1.0)] += 1
		bonus[Itens.rolar_raridade(rng, "comum", 1.4)] += 1
	var fm := float(bonus["magico"]) / float(base["magico"])
	var fe := float(bonus["excelente"]) / float(base["excelente"])
	print("antes  comum %.4f magico %.4f raro %.4f excelente %.5f" % [base["comum"]/float(n), base["magico"]/float(n), base["raro"]/float(n), base["excelente"]/float(n)])
	print("depois comum %.4f magico %.4f raro %.4f excelente %.5f" % [bonus["comum"]/float(n), bonus["magico"]/float(n), bonus["raro"]/float(n), bonus["excelente"]/float(n)])
	print("fator azul %.3f, fator verde %.3f" % [fm, fe])
	if absf(fm - 1.4) > 0.03: print("FALHA: azul fora de 1.4"); falhas += 1
	if absf(fe - 1.4) > 0.25: print("FALHA: verde fora de 1.4"); falhas += 1
	var rng2 := RandomNumberGenerator.new(); rng2.seed = 1
	var sem := 0
	for i in 1000:
		if Itens.rolar_raridade(rng2, "excelente", 1.4) != "excelente": sem += 1
	if sem > 0: print("FALHA: minima excelente deve dar só excelente"); falhas += 1
	print("teste_verdeazul: %s" % ["OK" if falhas == 0 else "%d falha(s)" % falhas])
	quit(1 if falhas > 0 else 0)

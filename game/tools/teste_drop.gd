
extends SceneTree
## Drop de mob comum (0.9.8): chance absoluta por abate por raridade, e sem branco acima do nível 30. Rodar: godot --headless -s tools/teste_drop.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var rng := RandomNumberGenerator.new()
	rng.seed = 9090
	var n := 2000000
	var baixo := {"comum": 0, "verde": 0, "magico": 0, "excelente": 0, "raro": 0, "laranja": 0}
	var alto := {"comum": 0, "verde": 0, "magico": 0, "excelente": 0, "raro": 0, "laranja": 0}
	for i in n:
		var a := Itens.rolar_raridade_mob(rng, 20)
		if a != "": baixo[a] += 1
		var b := Itens.rolar_raridade_mob(rng, 35)
		if b != "": alto[b] += 1
	var esperado := {"comum": 0.10, "verde": 0.05, "magico": 0.005, "excelente": 0.005, "raro": 0.0001, "laranja": 0.00001}
	for r in esperado:
		var p := baixo[r] / float(n)
		print("nivel 20 %-9s %.5f (esperado %.5f)" % [r, p, esperado[r]])
		# tolerância: 6 desvios padrão binomiais, com piso para as raridades muito raras
		var dp := sqrt(esperado[r] * (1.0 - esperado[r]) / n)
		if absf(p - esperado[r]) > maxf(6.0 * dp, 0.000002): print("FALHA: %s fora do esperado" % r); falhas += 1
	if alto["comum"] != 0: print("FALHA: nivel 35 deu branco"); falhas += 1
	var fator := (0.10 + 0.05 + 0.005 + 0.005 + 0.0001 + 0.00001) / (0.05 + 0.005 + 0.005 + 0.0001 + 0.00001)
	var pv := alto["verde"] / float(n)
	print("nivel 35 verde %.4f (esperado %.4f)" % [pv, 0.05 * fator])
	if absf(pv - 0.05 * fator) > 0.002: print("FALHA: verde acima de 30 fora da redistribuicao"); falhas += 1
	var nomes := ["Branco", "Verde", "Azul", "Roxo", "Amarelo", "Laranja", "Relíquia"]
	for r in ["comum", "verde", "magico", "excelente", "raro", "laranja", "lendario"]:
		if Defs.nome_raridade(r) != nomes[["comum", "verde", "magico", "excelente", "raro", "laranja", "lendario"].find(r)]:
			print("FALHA: nome de %s" % r); falhas += 1
	print("teste_drop: %s" % ["OK" if falhas == 0 else "%d falha(s)" % falhas])
	quit(1 if falhas > 0 else 0)

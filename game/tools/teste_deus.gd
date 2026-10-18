extends SceneTree
## Variantes Deus (18/10): cada arma-base que cai tem balanco.variante_deus de virar a versão Deus (atributos x1,35).
## Rodar: godot --headless -s tools/teste_deus.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var pool: Array = []
	for id in Defs.ITENS:
		if str(Defs.ITENS[id].get("variante_de", "")) != "": pool.append(id)
	if pool.size() != 10: print("FALHA: %d variantes Deus (esperado 10)" % pool.size()); falhas += 1
	for vid in pool:
		var v: Dictionary = Defs.ITENS[vid]
		var b: Dictionary = Defs.ITENS.get(v["variante_de"], {})
		if b.is_empty(): print("FALHA: base de %s não existe" % vid); falhas += 1; continue
		if Itens.deus_de(v["variante_de"]) != vid: print("FALHA: deus_de(%s)" % v["variante_de"]); falhas += 1
		var dv: Array = v.get("dano", [])
		var db: Array = b.get("dano", [])
		if dv.size() != 2 or db.size() != 2 or int(dv[0]) != roundi(int(db[0]) * 1.35) or int(dv[1]) != roundi(int(db[1]) * 1.35):
			print("FALHA: dano de %s não é x1,35 da base" % vid); falhas += 1
		for k in b.get("atributos", {}):
			if int(v["atributos"].get(k, -1)) != roundi(int(b["atributos"][k]) * 1.35): print("FALHA: atributo %s de %s" % [k, vid]); falhas += 1
	if absf(float(Defs.DROPS["balanco"]["variante_deus"]) - 0.001) > 0.000001: print("FALHA: chance da variante Deus"); falhas += 1
	# a base cai: 0,1% de virar Deus (amostra grande, com semente fixa)
	var sim := WorldSim.new(1)
	var rng := RandomNumberGenerator.new(); rng.seed = 11
	sim.rng = rng
	var base_id := "cimitarra_de_janes"
	var virou := 0
	for i in 100000:
		var it := Loot._trocar_por_deus(sim, Itens.novo(base_id))
		if str(it["id"]).begins_with("deus_"): virou += 1
	if virou < 40 or virou > 160: print("FALHA: %d de 100000 bases viraram Deus (esperado ~100)" % virou); falhas += 1
	# item que não é base nunca vira Deus
	for i in 1000:
		if str(Loot._trocar_por_deus(sim, Itens.novo("veu_carpideira"))["id"]).begins_with("deus_"): print("FALHA: item não-base virou Deus"); falhas += 1; break
	print("teste_deus: %s (bases que viraram Deus: %d/100000)" % ["OK" if falhas == 0 else "%d falha(s)" % falhas, virou])
	quit(1 if falhas > 0 else 0)

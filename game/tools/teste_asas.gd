extends SceneTree
## Teste headless do sistema de asas (entregas/asas). Copie para game/tools/ e rode:
##   godot --headless --path . --script res://tools/teste_asas.gd
## Confere: asa básica no Anjo/Demônio, slot asa, bônus, vis público, missão do Pedro (materiais, lágrimas, ouro,
## prova de chefe, asa anterior), drops por tag e asa de chefe.

var falhas := 0

func ok(cond: bool, txt: String) -> void:
	print(("  ok   " if cond else "  FALHA ") + txt)
	if not cond: falhas += 1

func dar(sim: WorldSim, j: Ent, id: String, q: int) -> void:
	while q > 0:
		var n := mini(q, int(Defs.ITENS[id].get("pilha", 1)))
		Itens.guardar(j.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, Itens.novo(id, n)); q -= n

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	print("== asa básica")
	for c in ["anjo", "demonio", "humano"]:
		var j := Jogador.criar(sim, c, "T")
		var tem: bool = j.equip.has("asa")
		ok(tem == (c != "humano"), "%s nasce %s asa (%s)" % [c, "com" if tem else "sem", str(j.equip.get("asa", {}).get("id", "-"))])
		if tem: ok(j.vis.has("asa"), "%s publica vis.asa" % c)
	print("== bônus")
	var h := Jogador.criar(sim, "humano", "H")
	h.nivel = 80
	Regras.recalc_jogador(h)
	var d0 := h.dano_max; var hp0 := h.hp_max
	var it := Itens.novo("asa_demonio_3"); Itens.guardar(h.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)
	Jogador.equipar(sim, h, int(it["uid"]), "")
	ok(h.equip.get("asa", {}).get("id", "") == "asa_demonio_3", "equipa no slot asa")
	ok(absf(h.dano_max / d0 - 1.33) < 0.01, "dano +33%% (%.1f -> %.1f)" % [d0, h.dano_max])
	ok(h.hp_max - hp0 >= 399.0, "hp +400")
	ok(absf(float(h.aux["bonus"]["reduz_dano"]) - 0.18) < 0.001, "reduz dano 18%")
	ok(str(h.vis.get("asa", {}).get("id", "")) == "asa_demonio_3", "vis.asa = asa_demonio_3")
	ok(Sincro.campos(h, false).has("vis"), "vis vai para os outros jogadores (PUB)")
	Jogador.desequipar(sim, h, "asa")
	ok(not h.vis.has("asa") and absf(h.dano_max - d0) < 0.01, "tirar a asa volta tudo")
	print("== missão do Pedro (mecânica 1 e 2)")
	var m := Jogador.criar(sim, "tecnomancer", "M")
	m.nivel = 30
	ok(Missoes.disponivel(m, "asa_mecanica_1_receita"), "nível 1 disponível")
	ok(not Missoes.disponivel(m, "asa_mecanica_2_receita"), "nível 2 trancado antes do 1")
	Missoes.aceitar(sim, m, "asa_mecanica_1_receita")
	dar(sim, m, "engrenagem_gasta", 40); dar(sim, m, "lagrima_angelica", 19); m.ouro = 10000
	ok(not Missoes.pronta(m, "asa_mecanica_1_receita"), "falta 1 lágrima: não fica pronta")
	dar(sim, m, "lagrima_angelica", 1)
	ok(Missoes.pronta(m, "asa_mecanica_1_receita"), "com tudo: pronta")
	Missoes.concluir(sim, m, "asa_mecanica_1_receita")
	ok(Itens.contar(m.inv, "asa_mecanica_1") == 1, "recebe Mochila de Foguetes")
	ok(m.ouro == 0 and Itens.contar(m.inv, "engrenagem_gasta") == 0 and Itens.contar(m.inv, "lagrima_angelica") == 0, "consome ouro, engrenagens e lágrimas")
	ok(Missoes.disponivel(m, "asa_mecanica_2_receita"), "nível 2 abre depois do 1")
	Missoes.aceitar(sim, m, "asa_mecanica_2_receita")
	dar(sim, m, "engrenagem_gasta", 120); dar(sim, m, "lagrima_sanguinea", 20); m.ouro = 90000
	ok(not Missoes.pronta(m, "asa_mecanica_2_receita"), "sem o Telegrafista: não fica pronta")
	Missoes.evento(sim, m, "matar", "o_telegrafista")
	for i in 100: Missoes.evento(sim, m, "matar", "guarda_fios")
	ok(Missoes.pronta(m, "asa_mecanica_2_receita"), "chefe + 100 guarda-fios: pronta")
	Missoes.concluir(sim, m, "asa_mecanica_2_receita")
	ok(Itens.contar(m.inv, "asa_mecanica_2") == 1 and Itens.contar(m.inv, "asa_mecanica_1") == 0, "troca a asa 1 pela 2")
	ok(m.ouro == 10000, "cobra 80.000 de ouro")
	print("== drops (100 mil abates simulados)")
	var cont := {}
	sim.chao.clear()
	var jg := Jogador.criar(sim, "humano", "D"); jg.nivel = 12
	for kind in ["corvo_de_brasa", "legionario_desgarrado", "lobo_de_cinza"]:
		var e := Ent.new(); e.tipo = "monstro"; e.kind = kind; e.nivel = 14; e.arquetipo = "normal"
		e.tags = Defs.MOBS.get(kind, {}).get("tags", [])
		for i in 100000: Loot._rolar_materiais_asa(sim, e, jg)
		for c in sim.chao.values():
			var id: String = c["item"]["id"] if c.has("item") else str(c.get("id", ""))
			cont[kind + ":" + id] = cont.get(kind + ":" + id, 0) + 1
		sim.chao.clear()
	print("   ", cont)
	ok(cont.get("corvo_de_brasa:pena_cinzenta", 0) > 1500 and cont.get("corvo_de_brasa:pena_cinzenta", 0) < 2500, "ave solta pena (~2%)")
	ok(cont.get("legionario_desgarrado:pele_ressecada", 0) > 1100, "demônio solta pele (~1,5%)")
	ok(not cont.keys().any(func(k): return k.begins_with("lobo_de_cinza")), "lobo não solta material de asa")
	var b := Ent.new(); b.tipo = "chefe"; b.kind = "general_partido"; b.nivel = 8; b.arquetipo = "chefe"
	var asas := 0
	for i in 20000:
		Loot._rolar_materiais_asa(sim, b, jg)
	for c in sim.chao.values():
		var id2: String = c["item"]["id"] if c.has("item") else str(c.get("id", ""))
		if id2 == "asa_andras": asas += 1
	ok(asas > 40 and asas < 130, "Andras solta a Asa Partida (~0,4%%: %d em 20 mil)" % asas)
	print("\n%s" % ("TUDO CERTO" if falhas == 0 else "%d FALHAS" % falhas))
	quit(1 if falhas > 0 else 0)

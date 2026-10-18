extends SceneTree
## Efeitos de Relíquia (18/10): defesa do próprio item, evasão, fogo, gelo e invocação.
## Rodar: godot --headless -s tools/teste_reliquias.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(1)
	var e: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	var veu := Itens.novo("veu_carpideira")
	var base_def := float(Itens.defn("veu_carpideira").get("defesa", 0.0))
	var b := Itens.bonus({"cabeca": veu})
	if absf(float(b["defesa"]) - base_def * 1.3) > 0.01:
		print("FALHA: defesa do Véu esperada %.2f, veio %.2f" % [base_def * 1.3, b["defesa"]]); falhas += 1
	var b_critico := Itens.bonus({"amuleto": Itens.novo("etiqueta_branca")})
	if absf(float(b_critico["critico"]) - 0.03) > 0.0001: print("FALHA: crítico da Etiqueta Branca"); falhas += 1
	var b_evasao := Itens.bonus({"amuleto": Itens.novo("estilhaco_lacre")})
	if absf(float(b_evasao["evasao"]) - 0.03) > 0.0001: print("FALHA: evasão do Estilhaço do Lacre"); falhas += 1
	# evasão total: o alvo esquiva todo golpe corpo a corpo
	var atk := Ent.new(); atk.tipo = "monstro"; atk.nivel = e.nivel; atk.ar = 999.0; atk.dano_min = 5.0; atk.dano_max = 6.0; atk.id = sim.novo_id()
	e.aux["bonus"] = {"evasao": 1.0}
	var rng := RandomNumberGenerator.new(); rng.seed = 7
	var r := Regras.golpe(atk, e, {}, rng)
	if not r.get("evadiu", false): print("FALHA: evasão total não esquivou"); falhas += 1
	e.aux["bonus"] = {}
	# fogo: +50% no golpe de fogo, nada no de outro elemento
	atk.aux["bonus"] = {"dano_fogo": 0.5}
	atk.critico = 0.0; atk.excelente = 0.0
	var rng2 := RandomNumberGenerator.new(); rng2.seed = 11
	var d_fogo := int(Regras.golpe(atk, e, {"elemento": "fogo", "nunca_erra": true}, rng2)["dano"])
	var rng3 := RandomNumberGenerator.new(); rng3.seed = 11
	var d_fisico := int(Regras.golpe(atk, e, {"elemento": "fisico", "nunca_erra": true}, rng3)["dano"])
	if d_fogo <= d_fisico: print("FALHA: fogo (%d) não passou do físico (%d)" % [d_fogo, d_fisico]); falhas += 1
	# invocação: a Relíquia chama dois Não-Julgados e só recarrega depois do tempo
	var dono: Ent = e
	dono.aux["bonus"] = Itens.bonus({"arma": Itens.novo("bacula_femur")})
	sim.tempo = 10.0
	var antes := sim.ents.values().filter(func(o): return o.tipo == "invocacao" and o.dono == dono.id).size()
	sim._efeitos_de_item(dono, e)
	var depois := sim.ents.values().filter(func(o): return o.tipo == "invocacao" and o.dono == dono.id).size()
	if depois - antes != 2: print("FALHA: invocação deveria trazer 2, trouxe %d" % (depois - antes)); falhas += 1
	sim._efeitos_de_item(dono, e)
	var de_novo := sim.ents.values().filter(func(o): return o.tipo == "invocacao" and o.dono == dono.id).size()
	if de_novo != depois: print("FALHA: invocou antes da recarga"); falhas += 1
	print("teste_reliquias: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

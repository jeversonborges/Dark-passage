extends SceneTree
## Teste headless do PvP livre (0.9.8.2): CTRL liga a briga em qualquer lugar menos na Cidade; quem bate fica marcado
## por 10 s (o outro revida sem CTRL); morte para jogador derruba 15% dos itens no chão.
## godot --headless --path . --script res://tools/teste_pvp.gd

var erros: Array = []

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

func _par(sim: WorldSim, mapa: String, pos_a: Vector2, pos_b: Vector2) -> Array:
	var a := Jogador.criar(sim, "humano", "Caçador")
	a.faccao = "vigilia"
	Jogador.entrar(sim, a, mapa, pos_a)
	var b := Jogador.criar(sim, "anjo", "Anjo")
	b.faccao = "arautos"
	sim.adicionar_jogador(b, pos_b)
	b.pos = sim.celula_livre_perto(pos_b)
	for e: Ent in [a, b]: e.hp = e.hp_max
	return [a, b]

func _init() -> void:
	Defs.carregar()

	print("== fora da cidade: CTRL liga, sem CTRL não")
	var sim := WorldSim.new(11)
	var par := _par(sim, "porao_matadouro", Vector2(30, 30), Vector2(31, 30))
	var a: Ent = par[0]; var b: Ent = par[1]
	a.pos = sim.celula_livre_perto(Vector2(30, 30))
	b.pos = sim.celula_livre_perto(a.pos + Vector2(1, 0))
	Jogador.cmd_atacar(sim, a, b.id, false)
	checar(not a.eh_inimigo_de(b) and a.alvo == -1, "sem CTRL, jogador não ataca jogador de outra facção")
	Jogador.cmd_atacar(sim, a, b.id, true)
	checar(a.pvp_t > 0.0 and a.eh_inimigo_de(b), "CTRL + ataque liga o PvP (marcado %.1f s)" % a.pvp_t)
	checar(a.alvo == b.id, "o ataque com CTRL segue no alvo")
	checar(b.eh_inimigo_de(a), "quem tomou o CTRL revida sem CTRL")
	rodar(sim, 1.5)
	checar(b.hp < b.hp_max, "o golpe pegou (HP %d de %d)" % [b.hp, b.hp_max])
	checar(a.pvp_t >= 8.5, "o golpe renova a marca (%.1f s)" % a.pvp_t)
	a.alvo = -1; b.alvo = -1
	rodar(sim, 11.0)
	checar(a.pvp_t <= 0.0 and not b.eh_inimigo_de(a), "11 s sem golpe: a marca acaba e o revide para")

	print("== skill com CTRL, mesma facção ignorada")
	var c := Jogador.criar(sim, "anjo", "Mesmo")
	c.faccao = "vigilia"
	sim.adicionar_jogador(c, a.pos + Vector2(0.5, 0.5))
	Jogador.cmd_atacar(sim, a, c.id, true)
	checar(a.pvp_t <= 0.0, "mesma facção não liga o PvP")

	print("== Cidade de São Lázaro: CTRL é ignorado")
	var sim2 := WorldSim.new(12)
	var par2 := _par(sim2, "area_inicial", Vector2(44.5, 44), Vector2(45.5, 44))
	var a2: Ent = par2[0]; var b2: Ent = par2[1]
	Jogador.cmd_atacar(sim2, a2, b2.id, true)
	checar(a2.pvp_t <= 0.0 and not a2.eh_inimigo_de(b2), "na Cidade, CTRL não liga o PvP")
	Jogador.cmd_skill(sim2, a2, 0, b2.id, b2.pos, true)
	checar(a2.pvp_t <= 0.0, "na Cidade, skill com CTRL também é ignorada")

	print("== morte para jogador: 15% dos itens caem no chão")
	var sim3 := WorldSim.new(13)
	var par3 := _par(sim3, "porao_matadouro", Vector2(30, 30), Vector2(31, 30))
	var k: Ent = par3[0]; var v: Ent = par3[1]
	var ids: Array = Defs.ITENS.keys().filter(func(i): return Itens.categoria(Itens.novo(i)) != "missao" and not Itens.vinculado(Itens.novo(i)))
	for i in 10: v.inv.append(Itens.novo(ids[i]))
	var antes_chao := sim3.chao.size()
	var antes_inv := v.inv.size()
	Jogador.cmd_atacar(sim3, k, v.id, true)
	sim3.matar(v, k)
	var caiu := sim3.chao.size() - antes_chao
	checar(caiu == 2 and v.inv.size() == antes_inv - 2, "10 itens: 2 caem no chão (caíram %d)" % caiu)
	var de_k := 0
	for cid in sim3.chao: if sim3.chao[cid]["dono"] == k.id: de_k += 1
	checar(de_k == 2, "os itens caídos ficam com o assassino primeiro")

	print("== morte para mob não derruba nada")
	var v2 := Jogador.criar(sim3, "humano", "Outro")
	v2.faccao = "vigilia"
	sim3.adicionar_jogador(v2, Vector2(33, 30))
	for i in 5: v2.inv.append(Itens.novo(ids[i]))
	var n_chao := sim3.chao.size()
	var n_inv := v2.inv.size()
	sim3.matar(v2, null)
	checar(sim3.chao.size() == n_chao and v2.inv.size() == n_inv, "morte sem jogador não derruba itens (chão %d, mochila %d)" % [n_chao, n_inv])

	print("")
	if erros.is_empty(): print("TODOS OK")
	else: print("FALHAS: %d" % erros.size())
	quit(0 if erros.is_empty() else 1)

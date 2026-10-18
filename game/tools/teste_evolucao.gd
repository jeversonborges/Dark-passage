extends SceneTree
## Teste headless das evoluções do nível 30: carta do Simão, escolha com o Pedro (só os 2 caminhos da classe),
## troca de classe, bônus (atributos, hp_mult, defesa_mult), as 5 skills novas de cada caminho e o save.
## godot --headless --path . -s tools/teste_evolucao.gd

var cont := {}
var avisos: Array = []
var falhas := 0

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "aviso" and avisos.size() < 40: avisos.append(str(d.get("texto", "")))

func falha(msg: String) -> void:
	print("FALHA: ", msg); falhas += 1

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

func subir(sim: WorldSim, j: Ent, nivel: int) -> void:
	while j.nivel < nivel: Jogador.ganhar_xp(sim, j, Defs.xp_para_proximo(j.nivel) - j.xp)

func npc(sim: WorldSim, kind: String) -> Ent:
	for e: Ent in sim.ents.values():
		if e.tipo == "npc" and e.kind == kind: return e
	return null

## Escolhe no diálogo aberto a opção visível com esse texto. Devolve false se ela não estiver na tela.
func opcao(sim: WorldSim, j: Ent, texto: String) -> bool:
	var st: Dictionary = j.aux.get("dialogo", {})
	if st.is_empty(): return false
	var ops: Array = Defs.DIALOGOS[st["dlg"]]["nos"][st["no"]]["opcoes"]
	for i in st["vis"].size():
		if ops[st["vis"][i]]["texto"] == texto:
			Missoes.escolher(sim, j, i); return true
	return false

func visiveis(j: Ent) -> Array:
	var st: Dictionary = j.aux.get("dialogo", {})
	var ops: Array = Defs.DIALOGOS[st["dlg"]]["nos"][st["no"]]["opcoes"]
	return st["vis"].map(func(i): return ops[i]["texto"])

func _init() -> void:
	Defs.carregar()
	if Defs.EVOLUCOES.is_empty():
		print("FALHA: design/combate/evolucoes.json não carregou (rode tools/sync.sh)"); quit(1); return
	var sim := WorldSim.new(7)
	sim.evento.connect(_ev)
	var j0 := Jogador.criar(sim, "anjo", "Mapa")
	Jogador.entrar(sim, j0, "area_inicial", Vector2(44.5, 44))
	var pedro := npc(sim, "pedro_exilado")
	if pedro == null:
		print("AVISO: pedro_exilado não está no mapa area_inicial do jogo (precisa do mapa novo de São Lázaro); o teste cria um")
	else:
		print("pedro_exilado no mapa em ", pedro.pos, " andável=", sim.andavel(pedro.pos), " zona=", sim.zona_em(pedro.pos))
		if sim.zona_em(pedro.pos) != "ilha_do_exilado": falha("Pedro fora da zona ilha_do_exilado")
	sim.remover_jogador(j0)

	for classe in ["anjo", "demonio", "cultista", "humano", "mutante", "tecnomancer"]:
		for caminho_idx in 2:
			_testar(classe, caminho_idx)
	_testar_passivas()
	print("eventos: ", cont)
	print("avisos: ", avisos)
	print("RESULTADO: ", "OK" if falhas == 0 else "%d falha(s)" % falhas)
	quit(1 if falhas > 0 else 0)

func _testar(classe: String, caminho_idx: int) -> void:
	var sim := WorldSim.new(11 + caminho_idx)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, classe, "Teste_" + classe)
	Jogador.entrar(sim, j, "area_inicial", Vector2(44.5, 44))
	var simao := npc(sim, "simao_coveiro")
	var pedro := npc(sim, "pedro_exilado")
	if pedro == null:
		sim._criar_npc({"id": "pedro_exilado", "pos": [j.pos.x + 1.5, j.pos.y]})
		pedro = npc(sim, "pedro_exilado")
	if simao == null: falha("Simão não está no mapa"); return
	var opcoes: Array = Evolucao.opcoes(classe)
	var tag := "%s/%s" % [classe, opcoes[caminho_idx]]
	# ------------------------------------------------ nível mínimo
	subir(sim, j, 28)
	if Missoes.disponivel(j, "ev01"): falha(tag + ": ev01 disponível no nível 28")
	subir(sim, j, 30)
	if Missoes.disponivel(j, "ev01"): falha(tag + ": ev01 disponível sem a g02 do Livro dos Vencidos")
	j.missoes["g02"] = {"estado": "concluida"}   # requisito: Livro dos Vencidos do Simão
	for b in Defs.REG_CHEFES: j.flags["venceu_" + str(b["id"])] = true   # Livro dos Vencidos cheio até o nível da evolução
	if not Missoes.disponivel(j, "ev01"): falha(tag + ": ev01 indisponível no nível 30")
	# ------------------------------------------------ carta do Simão
	Missoes.abrir(sim, j, simao)
	if not opcao(sim, j, "Tem alguma carta para o Exilado?"): falha(tag + ": Simão não oferece a carta: " + str(visiveis(j))); return
	if Missoes.estado(j, "ev01") != "ativa": falha(tag + ": ev01 não ficou ativa")
	if Itens.contar(j.inv, "carta_de_simao") < 1: falha(tag + ": sem a carta de Simão na mochila")
	j.aux.erase("dialogo")
	# ------------------------------------------------ Pedro lê a carta; Os Dois Caminhos começa sozinha
	Missoes.abrir(sim, j, pedro)
	if not opcao(sim, j, "O coveiro me mandou. Esta é a carta."): falha(tag + ": Pedro não aceita a carta: " + str(visiveis(j))); return
	if Missoes.estado(j, "ev01") != "concluida": falha(tag + ": ev01 não concluiu")
	if Missoes.estado(j, "ev02") != "ativa": falha(tag + ": ev02 não começou")
	j.aux.erase("dialogo")
	# ------------------------------------------------ escolha: só os 2 caminhos da classe
	var stats_antes: Dictionary = j.stats.duplicate()
	var hp_antes := j.hp_max; var def_antes := j.defesa; var pontos_antes := j.pontos
	Missoes.abrir(sim, j, pedro)
	if not opcao(sim, j, "Estou pronto para escolher o meu caminho."): falha(tag + ": Pedro não abre a escolha"); return
	var vis := visiveis(j)
	var nomes: Array = opcoes.map(func(o): return Evolucao.defn(o)["nome"])
	if vis.size() != 3 or not (nomes[0] in vis and nomes[1] in vis): falha(tag + ": opções erradas na escolha: " + str(vis))
	# caminho de outra classe é recusado
	var alheio := "serafim" if classe != "anjo" else "ceifador"
	Missoes.concluir(sim, j, "ev02", alheio)
	if j.evolucao != "" or Missoes.estado(j, "ev02") != "ativa": falha(tag + ": aceitou caminho de outra classe")
	var escolhido: String = opcoes[caminho_idx]
	if not opcao(sim, j, Evolucao.defn(escolhido)["nome"]): falha(tag + ": não achou a opção " + escolhido); return
	if j.evolucao != escolhido: falha(tag + ": evolução não aplicada (%s)" % j.evolucao); return
	if Missoes.estado(j, "ev02") != "concluida": falha(tag + ": ev02 não concluiu")
	if not j.flags.has("evolucao_50"): falha(tag + ": sem a flag evolucao_50")
	if Evolucao.recusa(j, opcoes[1 - caminho_idx]) == "": falha(tag + ": dá para evoluir duas vezes")
	# ------------------------------------------------ bônus: atributos, pontos, hp_mult e defesa_mult
	var d := Evolucao.defn(escolhido)
	var b: Dictionary = d["bonus"]
	if j.pontos < pontos_antes + 10: falha(tag + ": não ganhou os 10 pontos extras")
	for k in ["FOR", "AGI", "VIT", "ESP"]:
		var esperado: float = float(j.stats[k]) + float(b.get(k, 0)) + float(j.aux["bonus"][k])
		if absf(float(j.aux["ef"][k]) - esperado) > 0.01: falha(tag + ": atributo %s efetivo %.1f, esperado %.1f" % [k, j.aux["ef"][k], esperado])
	# recalcula sem e com a evolução, com os mesmos atributos e nível, para isolar os multiplicadores
	var evo := j.evolucao
	j.evolucao = ""; Regras.recalc_jogador(j)
	var hp_sem := j.hp_max; var def_sem := j.defesa
	j.evolucao = evo; Regras.recalc_jogador(j)
	var hp_mult := 1.15 * float(b.get("hp_mult", 1.0))
	var def_mult := float(b.get("defesa_mult", 1.0))
	var V: float = j.aux["ef"]["VIT"]; var A: float = j.aux["ef"]["AGI"]
	var c: Dictionary = Defs.CLASSES[classe]
	var hp_base: float = (float(c["hp"]["base"]) + float(c["hp"]["por_nivel"]) * j.nivel + float(c["hp"]["por_vit"]) * V + float(j.aux["bonus"]["hp"])) * (1.0 + j.mod("hp_pct"))
	if absf(j.hp_max - hp_base * hp_mult) > 0.5: falha(tag + ": hp_max %.1f, esperado %.1f (x%.3f)" % [j.hp_max, hp_base * hp_mult, hp_mult])
	var def_base := V / 5.0 + A / 10.0 + float(j.aux["bonus"]["defesa"])
	if absf(j.defesa - def_base * def_mult) > 0.01: falha(tag + ": defesa %.2f, esperada %.2f (x%.2f)" % [j.defesa, def_base * def_mult, def_mult])
	print("%-32s hp %.0f -> %.0f (x%.3f)  defesa %.1f -> %.1f (x%.2f)  slots %d" % [tag, hp_antes, j.hp_max, hp_mult, def_antes, j.defesa, def_mult, j.skills_slots.size()])
	if hp_sem >= j.hp_max and hp_mult > 1.0: falha(tag + ": hp não subiu com a evolução")
	if def_mult > 1.0 and def_sem >= j.defesa: falha(tag + ": defesa não subiu com a evolução")
	# ------------------------------------------------ barra: base + 5 da evolução nos slots 10..14
	if j.skills_slots.size() != Evolucao.SLOT_EVO + 5: falha(tag + ": slots %d" % j.skills_slots.size())
	for i in 5:
		if j.skills_slots[Evolucao.SLOT_EVO + i] != d["habilidades"][i]["id"]: falha(tag + ": slot %d errado" % (Evolucao.SLOT_EVO + i))
	# ------------------------------------------------ as 5 skills disparam e fazem efeito
	subir(sim, j, 50)
	var campo := _campo_aberto(sim, j.pos)   # fora da zona segura, senão os monstros ficam imunes
	j.pos = campo
	for i in 5:
		var slot := Evolucao.SLOT_EVO + i
		var h := Jogador.skill_def(j, slot)
		if h.is_empty(): falha(tag + ": skill_def vazia no slot %d" % slot); continue
		for o: Ent in sim.ents.values():
			if o.tipo in ["monstro", "invocacao"] and o.pos.distance_to(j.pos) < 30.0: sim.remover(o.id)
		var alvo_m := sim.criar_mob(Defs.MOBS.keys()[0], sim.celula_livre_perto(campo + Vector2(2.0, 0.0)), 70)
		alvo_m.hp_max = 1e7; alvo_m.hp = 1e7; alvo_m.dano_min = 0.0; alvo_m.dano_max = 0.0
		var outro := sim.criar_mob(Defs.MOBS.keys()[0], sim.celula_livre_perto(campo + Vector2(2.5, 1.0)), 70)
		outro.hp_max = 1e7; outro.hp = 1e7; outro.dano_min = 0.0; outro.dano_max = 0.0
		if not j.vivo: Jogador.renascer(sim, j)
		j.pos = campo; j.caminho.clear(); j.deslocando = {}
		j.cds.clear(); j.acao = {}; j.buffs.clear(); Regras.recalc_jogador(j); j.hp = j.hp_max * 0.6; j.rec = j.rec_max
		if classe in ["demonio", "mutante"]: j.rec = j.rec_max
		var antes := cont.duplicate()
		var hp_m := alvo_m.hp + outro.hp
		var vel0 := j.vel_ataque; var crit0 := j.critico; var esc0 := j.escala; var hp0 := j.hp_max
		Jogador.cmd_skill(sim, j, slot, alvo_m.id, alvo_m.pos)
		var forma_vel := -1.0; var forma_crit := -1.0; var forma_esc := -1.0; var forma_hp := -1.0
		if h.get("transformacao", false):
			rodar(sim, 0.2)
			forma_vel = j.vel_ataque; forma_crit = j.critico; forma_esc = j.escala; forma_hp = j.hp_max
		rodar(sim, 4.0)
		if cont.get("skill", 0) <= antes.get("skill", 0): falha(tag + ": %s não saiu (vivo=%s acao=%s status=%s avisos=%s)" % [h["id"], j.vivo, j.acao.get("skill", ""), j.status.keys(), avisos.slice(-2)])
		var fez := []
		for k in ["dano", "cura", "buff", "escudo", "surgiu", "status"]:
			if cont.get(k, 0) > antes.get(k, 0): fez.append(k)
		var feriu := alvo_m.hp + outro.hp < hp_m
		print("    %-28s %-12s %s%s" % [h["id"], Evolucao.tipo(h), ",".join(fez), " (feriu)" if feriu else ""])
		if fez.is_empty(): falha(tag + ": %s não fez nada" % h["id"])
		if h.has("mult") and not h.has("buff") and not feriu: falha(tag + ": %s tem mult e não feriu" % h["id"])
		if h["id"] == "forma_vingativa":
			if absf(forma_vel - 2.3) > 0.01: falha(tag + ": Forma Vingativa deu velocidade de ataque %.2f" % forma_vel)
			if absf(forma_crit - minf(float(Defs.FORM["critico"]["chance_max"]), crit0 + 0.3)) > 0.01: falha(tag + ": Forma Vingativa deu crítico %.2f (antes %.2f)" % [forma_crit, crit0])
		if h["id"] == "forma_colossal":
			if absf(forma_hp / hp0 - 3.0) > 0.05: falha(tag + ": Forma Colossal deu hp x%.2f" % (forma_hp / hp0))
			if absf(forma_vel - 0.45) > 0.01: falha(tag + ": Forma Colossal bate a %.2f" % forma_vel)
			if absf(forma_esc - 1.8 * esc0) > 0.01: falha(tag + ": Forma Colossal escala %.2f" % forma_esc)
		if h.get("transformacao", false):
			rodar(sim, float(h["duracao"]))
			if absf(j.escala - esc0) > 0.01 or j.aux.has("forma"): falha(tag + ": %s não terminou" % h["id"])
	# ------------------------------------------------ save: ida e volta pelo JSON (como o servidor grava)
	j.buffs.clear(); Regras.recalc_jogador(j)
	var txt := JSON.stringify(Jogador.salvar(j, sim))
	var sim2 := WorldSim.new(3)
	var j2 := Jogador.criar(sim2, classe, j.nome, JSON.parse_string(txt))
	if j2.evolucao != escolhido: falha(tag + ": save perdeu a evolução")
	if j2.skills_slots != j.skills_slots: falha(tag + ": save mudou a barra")
	if absf(j2.hp_max - j.hp_max) > 0.5: falha(tag + ": hp_max depois do save %.1f != %.1f" % [j2.hp_max, j.hp_max])
	if absf(j2.defesa - j.defesa) > 0.01: falha(tag + ": defesa depois do save %.2f != %.2f" % [j2.defesa, j.defesa])
	if Missoes.estado(j2, "ev02") != "concluida": falha(tag + ": save perdeu ev02")
	# save com caminho de outra classe é ignorado
	var s3: Dictionary = JSON.parse_string(txt)
	s3["evolucao"] = alheio
	var j3 := Jogador.criar(sim2, classe, "x", s3)
	if j3.evolucao != "": falha(tag + ": save adulterado aceitou " + alheio)

func _campo_aberto(sim: WorldSim, perto: Vector2) -> Vector2:
	for r in range(4, 80, 2):
		for k in 16:
			var p := perto + Vector2.from_angle(TAU * k / 16.0) * r
			if not sim.andavel(p) or sim.zona_segura(p) or sim.amargo_em(p) >= 4: continue
			var ok := true
			for q in [Vector2(3, 0), Vector2(-3, 0), Vector2(0, 3), Vector2(0, -3), Vector2(2.5, 1)]:
				if not sim.andavel(p + q) or sim.zona_segura(p + q): ok = false
			if ok: return p
	return perto

## Cria um jogador já evoluído no nível 70, num campo aberto do mapa.
func _evoluido(sim: WorldSim, classe: String, evo: String, pos: Vector2) -> Ent:
	var j := Jogador.criar(sim, classe, "P_" + evo)
	sim.adicionar_jogador(j, pos)
	subir(sim, j, 50)
	if not Evolucao.aplicar(sim, j, evo): falha("passivas: não evoluiu " + evo)
	j.pos = pos
	return j

func _testar_passivas() -> void:
	var sim := WorldSim.new(21)
	sim.evento.connect(_ev)
	var j0 := Jogador.criar(sim, "anjo", "Mapa")
	Jogador.entrar(sim, j0, "area_inicial", Vector2(44.5, 44))
	var campo := _campo_aberto(sim, j0.pos)
	sim.remover_jogador(j0)
	for o: Ent in sim.ents.values():
		if o.tipo == "monstro" and o.pos.distance_to(campo) < 30.0: sim.remover(o.id)
	# ------------------------------------------------ Serafim: Seis Asas, Coro dos Seis Ais e Levanta-te
	var sera := _evoluido(sim, "anjo", "serafim", campo)
	var aliado := _evoluido(sim, "anjo", "arcanjo", campo + Vector2(1.5, 0))
	sera.hp = sera.hp_max; sera.escudo = 0.0
	sim.curar(sera, 200.0, sera)
	if sera.escudo <= 0.0: falha("Seis Asas: a sobra da cura não virou escudo")
	if sera.escudo > sera.hp_max * 0.2 + 0.1: falha("Seis Asas: escudo passou de 20%")
	sim.matar(aliado, null)
	if aliado.vivo: falha("aliado não morreu"); return
	sera.rec = sera.rec_max; sera.cds.clear()
	Jogador.cmd_skill(sim, sera, Evolucao.SLOT_EVO + 3, -1, sera.pos)   # Coro dos Seis Ais
	rodar(sim, 1.0)
	if not aliado.vivo: falha("Coro dos Seis Ais não levantou o aliado")
	elif aliado.frac_hp() < 0.59: falha("Coro dos Seis Ais: voltou com %.0f%%" % (aliado.frac_hp() * 100))
	print("Coro dos Seis Ais: aliado vivo=%s hp=%.0f%%" % [aliado.vivo, aliado.frac_hp() * 100])
	rodar(sim, 4.5)
	sim.matar(aliado, null)
	sera.rec = sera.rec_max; sera.cds.clear()
	Jogador.cmd_skill(sim, sera, Evolucao.SLOT_EVO + 4, -1, aliado.pos)   # Levanta-te (2 s de conjuração)
	rodar(sim, 3.0)
	if not aliado.vivo: falha("Levanta-te não levantou o aliado")
	print("Levanta-te: aliado vivo=%s hp=%.0f%%" % [aliado.vivo, aliado.frac_hp() * 100])
	if aliado.vivo and absf(aliado.frac_hp() - 0.4) > 0.05 and aliado.frac_hp() < 0.35: falha("Levanta-te: hp %.0f%%" % (aliado.frac_hp() * 100))
	# ------------------------------------------------ Arcanjo: Hoste em Marcha dá defesa aos aliados em combate
	aliado.em_combate_t = 0.0; sera.em_combate_t = 0.0
	var def0 := sera.defesa * (1.0 + sera.mod("defesa_pct"))
	rodar(sim, 1.2)
	if not sera.buffs.any(func(b): return b["id"] == "hoste_em_marcha"): falha("Hoste em Marcha não chegou no aliado")
	sim.remover_jogador(sera); sim.remover_jogador(aliado)
	# ------------------------------------------------ Lorde das Trevas: redução por inimigo perto
	var lorde := _evoluido(sim, "demonio", "lorde_das_trevas", campo)
	for k in 3:
		var m := sim.criar_mob(Defs.MOBS.keys()[0], campo + Vector2(1.0 + k * 0.5, 1.0), 70)
		m.dano_min = 0.0; m.dano_max = 0.0; m.hp_max = 1e7; m.hp = 1e7
	rodar(sim, 1.2)
	var red := 0.0
	for b in lorde.buffs:
		if b["id"] == "trono_vazio": red = -float(b["mods"]["dano_recebido"])
	if absf(red - 0.09) > 0.031: falha("Trono Vazio: redução %.2f com 3 inimigos" % red)
	print("Trono Vazio: redução %.0f%%" % (red * 100))
	sim.remover_jogador(lorde)
	# ------------------------------------------------ Abominação: abaixo de 50% ganha dano e roubo de vida
	var abo := _evoluido(sim, "mutante", "abominacao", campo)
	var rv0 := abo.roubo_vida
	abo.hp = abo.hp_max * 0.2; abo.em_combate_t = 0.0
	rodar(sim, 1.2)
	if not abo.buffs.any(func(b): return b["id"] == "o_amargo_venceu"): falha("O Amargo Venceu não ligou abaixo de 50%")
	if abo.roubo_vida < rv0 + 0.049: falha("O Amargo Venceu: roubo de vida %.2f -> %.2f" % [rv0, abo.roubo_vida])
	sim.remover_jogador(abo)
	# ------------------------------------------------ Arquimago: a 4ª magia sai de graça
	var arq := _evoluido(sim, "cultista", "arquimago", campo)
	var custos: Array = []
	for i in 4:
		custos.append(Evolucao.custo(arq, 10.0))
	if custos != [10.0, 10.0, 10.0, 0.0]: falha("Três Auréolas: custos " + str(custos))
	if float(arq.aux.get("bonus_prox", 0.0)) < 0.39: falha("Três Auréolas: sem +40% na magia grátis")
	sim.remover_jogador(arq)
	# ------------------------------------------------ Ceifador: matar renova o Passo Sombrio
	var cei := _evoluido(sim, "demonio", "ceifador", campo)
	cei.cds["passo_sombrio"] = 8.0
	var vit := sim.criar_mob(Defs.MOBS.keys()[0], campo + Vector2(1.0, 0), 10)
	Evolucao.abateu(sim, cei, vit)
	if cei.cds.has("passo_sombrio"): falha("Colheita não renovou o Passo Sombrio")
	var fraco := sim.criar_mob(Defs.MOBS.keys()[0], campo + Vector2(1.0, 0), 10)
	fraco.hp = fraco.hp_max * 0.2
	if absf(Evolucao.mult_golpe(cei, fraco, {}) - 1.25) > 0.001: falha("Colheita: sem +25% abaixo de 30%")
	sim.remover_jogador(cei)
	# ------------------------------------------------ Pistoleiro: alados e defesa ignorada
	var pis := _evoluido(sim, "humano", "pistoleiro", campo)
	var anjo_alvo := Jogador.criar(sim, "anjo", "Alvo")
	if absf(Evolucao.mult_golpe(pis, anjo_alvo, {}) - 1.3) > 0.001: falha("Balas Bentas: sem +30% em alado")
	if absf(Evolucao.pen_defesa(pis, {}) - 0.15) > 0.001: falha("Balas Bentas: não ignora 15% da defesa")
	print("passivas testadas: Seis Asas, Coro, Levanta-te, Hoste, Trono Vazio, Amargo Venceu, Três Auréolas, Colheita, Balas Bentas")

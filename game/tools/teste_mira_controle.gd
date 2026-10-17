extends SceneTree
## Teste headless do combate no controle (scripts/client/mira_controle.gd): alvo automático, trava, ciclo,
## ataque básico segurando, skills por tipo, interação e a troca mouse <-> controle.
## godot --headless --path . -s tools/teste_mira_controle.gd

var falhas := 0
var jogo: Node2D
var fase := 0
var t := 0.0
var classes := ["humano", "anjo", "mutante", "tecnomancer", "cultista", "demonio"]
var ci := 0
var skills_usadas := {}
var avisos: Array = []
var ativas := 0   # skills ativas liberadas no nível do teste (o mínimo exigido depende disso)

func ok(cond: bool, msg: String) -> void:
	if not cond: falhas += 1; print("FALHA: ", msg)
	else: print("  ok: ", msg)

func _init() -> void:
	Defs.carregar()

func _novo(classe: String) -> void:
	if jogo != null: jogo.queue_free()
	jogo = load("res://tools/jogo_falso.gd").new()
	root.add_child(jogo)
	jogo.iniciar(classe, "Teste")
	jogo.sim.evento.connect(func(tp, d):
		if tp == "skill" and int(d.get("id", -1)) == jogo.jog.id: skills_usadas[d["skill"]] = true
		if tp == "aviso" and avisos.size() < 20: avisos.append(str(d.get("texto", ""))))

func _mob_perto(pos: Vector2, raio: float) -> Ent:
	var m: Ent = null
	var md := raio
	for e: Ent in jogo.sim.ents.values():
		if e.vivo and e.tipo == "monstro" and e.alvejavel and not e.invisivel and e.pos.distance_to(pos) < md:
			md = e.pos.distance_to(pos); m = e
	return m

func _passos(n: int, mover := Vector2.ZERO, mira := Vector2.ZERO) -> void:
	for i in n:
		jogo.mira_ctl.passo(1.0 / 30.0, mover, mira)
		jogo.sim.passo(WorldSim.TICK); jogo._ver_todos()

func _process(dt: float) -> bool:
	t += dt
	match fase:
		0:
			print("== ", classes[ci])
			_novo(classes[ci]); fase = 1; t = 0.0
		1:
			if t < 0.3: return false
			var mc = jogo.mira_ctl
			var jog: Ent = jogo.jog
			ok(not mc.ativo, "começa no mouse (controle desligado)")
			# direção do stick vira direção no mundo que, projetada, fica paralela ao stick na tela
			for s in [Vector2(1, 0), Vector2(0, -1), Vector2(0.7, 0.7), Vector2(-1, 0.2)]:
				var w: Vector2 = mc._tela_p_mundo(s)
				var back := Iso.to_screen(w).normalized()
				ok(back.distance_to(s.normalized()) < 0.01, "stick %s -> mundo %s (tela %s)" % [s, w, back])
			# entra no controle por um botão do joypad
			var bt := InputEventJoypadButton.new(); bt.button_index = JOY_BUTTON_A; bt.pressed = true
			mc._input(bt)
			ok(mc.ativo, "botão do controle liga o modo controle")
			while jog.nivel < 12: Jogador.ganhar_xp(jogo.sim, jog, Defs.xp_para_proximo(jog.nivel) - jog.xp)
			jog.hp = jog.hp_max; jog.rec = jog.rec_max
			# acha um mob e põe o jogador a 2.5 tiles dele, olhando para ele
			var m: Ent = null
			for e: Ent in jogo.sim.ents.values():
				if e.vivo and e.tipo == "monstro" and e.alvejavel and not e.invisivel: m = e; break
			ok(m != null, "há mob no mapa")
			if m == null: fase = 9; return false
			jog.pos = jogo.sim.celula_livre_perto(m.pos + Vector2(2.0, 1.5))
			jog.facing = (m.pos - jog.pos).normalized()
			for e: Ent in jogo.sim.ents.values(): if not jogo.views.has(e.id): jogo._surgiu(e.id)
			_passos(4)
			var a: int = mc.alvo()
			ok(a != -1, "alvo automático escolheu alguém perto (%s)" % (jogo.sim.ents[a].nome if a != -1 else "-"))
			# neutro parado longe não vira alvo sozinho
			for e: Ent in mc._candidatos(RAIO_LONGE(), false):
				if mc._eh_neutro_parado(e): ok(e.pos.distance_to(jog.pos) <= mc.RAIO_NEUTRO + 0.01, "neutro parado só entra colado (%s a %.1f)" % [e.nome, e.pos.distance_to(jog.pos)])
			mc.ataque_basico(false)   # aperto (contrato do controle.gd)
			ok(jog.alvo == mc.alvo() and jog.alvo != -1, "ataque básico bate no alvo da mira")
			_passos(15)
			ok(not mc.segurando_ataque, "sem repetição do botão, o segurar expira (soltou)")
			mc.travar_alvo()
			ok(mc.travado, "trava no alvo")
			var travado_em: int = mc.alvo()
			_passos(10, Vector2.ZERO, Vector2(-1, 0))
			ok(mc.alvo() == travado_em or mc.alvo() == -1, "stick direito não tira o alvo travado")
			mc.travar_alvo()
			ok(not mc.travado, "clicar de novo solta a trava")
			mc.ciclar_alvo(1)
			ok(mc.alvo() != -1 and mc.travado, "ciclar pega um alvo e trava")
			# skills: cada tipo vira um comando sem erro; ponto da skill respeita o alcance
			for i in jog.skills_slots.size():
				var h := Jogador.skill_def(jog, i)
				if h.is_empty() or h.get("passiva", false) or jog.nivel < int(h["nivel"]): continue
				ativas += 1
				var p: Vector2 = mc.ponto_skill(h)
				var alc := Jogador._alcance_skill(h)
				if alc > 0.0 and not h["id"] in mc.FUGA: ok(p.distance_to(jog.pos) <= alc + 0.01, "%s: ponto dentro do alcance (%.1f <= %.1f)" % [h["id"], p.distance_to(jog.pos), alc])
				if h["id"] in mc.FUGA:
					_passos(1, Vector2(0, 1))
					var pf: Vector2 = mc.ponto_skill(h)
					ok((pf - jog.pos).normalized().dot(mc._tela_p_mundo(Vector2(0, 1))) > 0.99, "%s: fuga vai para onde o stick esquerdo aponta" % h["id"])
				jog.cds.clear(); jog.rec = jog.rec_max; jog.hp = jog.hp_max
				_garantir_alvo()   # o golpe anterior pode ter matado o mob: o teste é da mira, não da sorte do spawn
				var antes := skills_usadas.size()
				jogo.usar_skill(i)   # entra pelo game.gd, como a tecla/botão faria
				_passos(45)   # skill de alvo um pouco longe anda até lá (buffer) antes de sair
				if skills_usadas.size() == antes:
					var ex: Ent = jogo.sim.ents.get(mc.alvo())
					print("    %s não saiu: alvo=%s dist=%s buffer=%s acao=%s estado=%s" % [h["id"], mc.alvo(), str(snappedf(ex.pos.distance_to(jog.pos), 0.1)) if ex != null else "-", jog.buffer_skill, not jog.acao.is_empty() if "acao" in jog else "?", jog.estado])
				var ea: Ent = jogo.sim.ents.get(mc.alvo())
				if ea != null: ea.hp = ea.hp_max
			print("  skills soltas: ", skills_usadas.keys())
			ok(skills_usadas.size() >= mini(2, ativas), "soltou skills pelo controle (%d de %d ativas)" % [skills_usadas.size(), ativas])
			if skills_usadas.size() < mini(2, ativas):   # diagnóstico: o que cada slot é e o que o servidor respondeu
				for i in jog.skills_slots.size():
					var h2 := Jogador.skill_def(jog, i)
					if not h2.is_empty(): print("    slot %d %s nivel=%s passiva=%s tipo=%s" % [i, h2["id"], h2.get("nivel"), h2.get("passiva", false), Jogador._tipo_skill(h2)])
				print("    avisos: ", avisos)
			# segurar ataque: quando o alvo cai, já vai no próximo
			var alvo1: int = mc.alvo()
			if mc.travado: mc.travar_alvo()
			mc.ataque_basico(false)
			var e1: Ent = jogo.sim.ents.get(alvo1)
			if e1 != null: jogo.sim.matar(e1, jog)
			for k in 3:   # o controle.gd repete ataque_basico(true) a cada 0,2 s enquanto segura
				_passos(6); mc.ataque_basico(true)
			var outro: bool = mc._candidatos(9.0, false).size() > 0
			if outro: ok(jog.alvo != -1 and jog.alvo != alvo1, "segurando ataque: foi no próximo depois que o alvo caiu")
			# mouse volta: tudo como antes
			var mb := InputEventMouseButton.new(); mb.button_index = MOUSE_BUTTON_LEFT; mb.pressed = true
			mc._input(mb)
			ok(not mc.ativo and mc.alvo() == -1, "clique do mouse desliga o controle e limpa a mira")
			fase = 9
		9:
			ci += 1
			skills_usadas = {}; avisos = []; ativas = 0
			if ci >= classes.size():
				print("RESULTADO: ", "OK" if falhas == 0 else "%d falha(s)" % falhas)
				quit(1 if falhas else 0)
				return true
			fase = 0
	return false

## Põe o jogador a ~2 tiles de um mob vivo (com HP cheio) se a mira ficou sem alvo.
func _garantir_alvo() -> void:
	var mc = jogo.mira_ctl
	var jog: Ent = jogo.jog
	var at: Ent = jogo.sim.ents.get(mc.alvo())
	if at != null:   # já tem alvo: só encosta nele (as skills de alvo do Demônio são corpo a corpo)
		at.hp = at.hp_max
		if at.pos.distance_to(jog.pos) > 1.2:
			jog.pos = jogo.sim.celula_livre_perto(at.pos + (jog.pos - at.pos).normalized() * 0.9)
			jog.facing = (at.pos - jog.pos).normalized()
			_passos(2)
		return
	for e: Ent in jogo.sim.ents.values():
		if e.vivo and e.tipo == "monstro" and e.alvejavel and not e.invisivel:
			jog.pos = jogo.sim.celula_livre_perto(e.pos + Vector2(0.7, 0.5))
			jog.facing = (e.pos - jog.pos).normalized()
			e.hp = e.hp_max
			_passos(4)
			if mc.alvo() != -1: return
	print("  aviso do teste: nenhum mob ao alcance para a skill")

func RAIO_LONGE() -> float:
	return 9.0

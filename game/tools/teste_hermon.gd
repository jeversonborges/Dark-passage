extends SceneTree
## Teste headless do evento "O Cume dos Vigilantes" (agenda, convite, espera, juramento, anéis, quedas, PvP, prêmios).
## godot --headless --path . --script res://tools/teste_hermon.gd

var falhas := 0
var oks := 0
var evs: Array = []

func ok(cond: bool, txt: String) -> void:
	if cond: oks += 1; print("  ok   ", txt)
	else: falhas += 1; print("  FALHA ", txt)

func _ev(t: String, d: Dictionary) -> void:
	evs.append([t, d])

func conta(t: String, f: Callable = Callable()) -> int:
	var n := 0
	for x in evs:
		if x[0] == t and (not f.is_valid() or f.call(x[1])): n += 1
	return n

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 6 == 0: f.call()
		sim.passo(WorldSim.TICK)

func unix(s: String) -> int:   # "AAAA-MM-DDTHH:MM:SS" em UTC
	return Time.get_unix_time_from_datetime_string(s)

func _init() -> void:
	Defs.carregar()
	var dados: Dictionary = Defs.ler(HermonCtl.DADOS)
	var ev: Dictionary = dados["evento"]
	teste_agenda(ev)
	teste_espera_e_juramento()
	teste_cancelado()
	teste_clicar_convite()
	teste_fim_por_tempo()
	print("\nteste_hermon: %d ok, %d falhas" % [oks, falhas])
	quit(1 if falhas > 0 else 0)

# ------------------------------------------------------------------ agenda e convite (servidor)
func teste_agenda(ev: Dictionary) -> void:
	print("[agenda e convite]")
	var a := EventoHermon.new(ev)
	var t0 := unix("2026-10-16T15:00:00")          # 12:00 em Brasília
	ok(a.proximo_inicio(t0) == unix("2026-10-16T22:00:00"), "próxima subida 19:00 de Brasília (22:00 UTC)")
	ok(a.proximo_inicio(unix("2026-10-16T22:06:00")) == unix("2026-10-17T22:00:00"), "depois das 19h vai para as 19h do dia seguinte")
	ok(a.janela_aberta(t0) < 0, "fora da janela às 12h")
	var r := a.usar_convite(30, t0)
	ok(not r["ok"] and not r["gasta"], "convite fora da janela não gasta: " + r["texto"])
	var av := a.avisos(unix("2026-10-16T21:50:00"))
	ok(av.size() == 1 and "10 min" in av[0], "aviso de 10 min")
	ok(a.avisos(unix("2026-10-16T21:50:30")).is_empty(), "aviso não repete")
	var ab := unix("2026-10-16T22:01:00")
	ok(a.avisos(ab).has(ev["falas"]["abriu"]), "aviso de entrada aberta")
	ok(a.janela_aberta(ab) == unix("2026-10-16T22:00:00") and a.resta_entrada(ab) == 60, "janela aberta, faltam 1 min")
	ok(a.janela_aberta(unix("2026-10-16T22:02:00")) < 0, "janela fecha aos 2 min")
	r = a.usar_convite(10, ab)
	ok(not r["ok"] and not r["gasta"], "nível 10 não sobe")
	r = a.usar_convite(30, ab, "dungeon")
	ok(not r["ok"], "não sobe de dentro da dungeon")
	var ids := {}
	for i in 21:
		r = a.usar_convite(30, ab)
		ids[r["instancia"]] = ids.get(r["instancia"], 0) + 1
	ok(r["ok"] and r["gasta"] and r["faixa"] == 0 and r["nivel_mob"] == 30, "nível 30 sobe na faixa 15-49 (mob 30)")
	ok(ids.size() == 2 and ids.values().has(20) and ids.values().has(1), "21 jogadores = 2 cumes (20 + 1)")
	r = a.usar_convite(120, ab)
	ok(r["faixa"] == 2 and not ids.has(r["instancia"]), "nível 120 vai para outro cume (faixa 100-149)")
	ok(EventoHermon.mapa_base(r["instancia"]) == "cume_dos_vigilantes", "instância usa o mesmo arquivo de mapa")

# ------------------------------------------------------------------ instância completa
func novo_cume(jogs: Array) -> Array:
	evs.clear()
	var sim := WorldSim.new(11)
	sim.evento.connect(_ev)
	sim.carregar_mapa("cume_dos_vigilantes#teste-0-1")
	var ctl: HermonCtl = sim.hermon
	ctl.definir_nivel(30)
	ctl.definir_espera(120.0)   # o servidor faz isto ao abrir a instância (convite): aí os Vigilantes ajoelham
	var out: Array = []
	var ch: Array = ctl.cfg["chegadas"]
	for i in jogs.size():
		var j := Jogador.criar(sim, jogs[i], "J%d" % i)
		j.aux["hermon_volta"] = {"mapa": "area_inicial", "pos": [50, 50]}
		j.nivel = 30; Regras.recalc_jogador(j); j.hp = j.hp_max   # faixa 15-49 contra Vigilantes nível 30
		sim.adicionar_jogador(j, Vector2(ch[i * 3][0], ch[i * 3][1]))
		out.append(j)
	return [sim, ctl, out]

func lutar(sim: WorldSim, j: Ent) -> void:
	if not j.vivo or not j.acao.is_empty(): return
	var m: Ent = null
	for e: Ent in sim.ents.values():
		if e.vivo and e.alvejavel and j.eh_inimigo_de(e) and (m == null or e.pos.distance_to(j.pos) < m.pos.distance_to(j.pos)): m = e
	if m == null: return
	if randf() < 0.3: Jogador.cmd_skill(sim, j, randi_range(0, 4), m.id, m.pos)
	else: Jogador.cmd_atacar(sim, j, m.id)
	if j.frac_hp() < 0.4: Jogador.cmd_pocao(sim, j, "vida")

func teste_espera_e_juramento() -> void:
	print("[espera e juramento, 4 jogadores]")
	var r := novo_cume(["humano", "anjo", "demonio", "mutante"])
	var sim: WorldSim = r[0]; var ctl: HermonCtl = r[1]; var js: Array = r[2]
	ok(ctl != null and ctl.estado == "espera", "mapa com 'hermon' cria o controle em espera")
	var est := 0
	for e: Ent in sim.ents.values():
		if e.kind == "estatua_vigilante": est += 1
	ok(est == ctl.cfg["vigilantes"].size() and est >= 50, "%d Vigilantes ajoelhados (estátuas) na espera" % est)
	ok(not js[0].eh_inimigo_de(js[1]), "sem PvP na espera")
	ctl.definir_espera(2.0)
	rodar(sim, 2.5)
	ok(ctl.estado == "juramento", "entrada fechou: juramento começou")
	ok(js[0].eh_inimigo_de(js[1]) and js[2].eh_inimigo_de(js[3]), "PvP ligado: cada um é o próprio lado")
	ok(ctl.vigilantes_vivos() == 28, "20 + 2x4 = 28 Vigilantes levantaram (%d)" % ctl.vigilantes_vivos())
	var est2 := 0
	for e: Ent in sim.ents.values():
		if e.kind == "estatua_vigilante": est2 += 1
	ok(est2 == 0, "estátuas sumiram")
	var tipos := {}
	for e: Ent in sim.ents.values():
		if e.aux.get("vigilante", false): tipos[e.kind] = tipos.get(e.kind, 0) + 1
	ok(tipos.has("vigilante_jurado") and tipos.has("vigilante_ferreiro"), "mistura de Vigilantes: %s" % str(tipos))
	# o Mutante fica parado no anel 1 (vai cair); os outros lutam
	var parado: Ent = js[3]
	var a1: Array = ctl.aneis[0]["celulas"]
	var c1: Vector2i = a1[0]
	for c: Vector2i in a1:
		if Vector2(c).distance_to(ctl.centro) > 19.5 and sim.andavel(Vector2(c) + Vector2(.5, .5)): c1 = c; break
	var xp_antes: int = parado.xp
	rodar(sim, 178.0, func():
		for k in 3:
			lutar(sim, js[k]); js[k].invuln_t = 0.5   # os 3 lutam sem morrer (o teste é da mecânica dos anéis)
		parado.pos = Vector2(c1) + Vector2(.5, .5); parado.invuln_t = 0.5; parado.caminho.clear())
	ok(conta("hermon_aviso", func(d): return d["anel"] == "anel_1") == 1, "aviso do anel 1 aos 160 s")
	ok(not ctl.aneis[0]["caiu"], "anel 1 ainda de pé aos 178 s")
	rodar(sim, 4.0, func():
		for k in 3: js[k].invuln_t = 0.5)
	ok(ctl.estado == "juramento", "juramento segue depois da queda do anel 1 (%d vivos)" % ctl.vivos().size())
	ok(conta("hermon_queda", func(d): return d["pos"].distance_to(ctl.centro) <= 17.0) == 0, "só caiu quem estava no anel 1 (raio > 17)")
	ok(ctl.aneis[0]["caiu"] and sim.bloq[c1.y * sim.w + c1.x] == 1, "anel 1 caiu aos 180 s e virou abismo")
	ok(conta("hermon_queda", func(d): return d["id"] == parado.id) == 1 and not ctl.participantes[parado.id]["vivo"], "quem estava no anel 1 caiu e foi eliminado")
	ok(parado.xp >= xp_antes, "sem perda de XP no evento")
	ok(conta("trocar_mapa", func(d): return d.get("_para") == parado.id and d["mapa"] == "area_inicial") == 1, "eliminado volta para onde estava")
	var vg_borda := 0
	for e: Ent in sim.ents.values():
		if e.aux.get("vigilante", false) and e.vivo and ctl.no_abismo(e.pos): vg_borda += 1
	ok(vg_borda == 0, "nenhum Vigilante vivo flutuando no abismo")
	ok(conta("aviso", func(d): return d["texto"] == ctl.ev["falas"]["reforco"]) == 1, "reforço desceu do céu quando o anel caiu")
	# empurrão na beira derruba
	var vit: Ent = null
	for e: Ent in sim.ents.values():
		if e.kind == "vigilante_jurado" and e.vivo: vit = e; break
	var beira := Vector2.ZERO
	for c: Vector2i in ctl.aneis[1]["celulas"]:
		var p := Vector2(c) + Vector2(.5, .5)
		var fora := p + (p - ctl.centro).normalized() * 0.8
		if sim.andavel(p) and ctl.no_abismo(fora): beira = p; break
	vit.pos = beira; vit.deslocando = {}; vit.acao = {}
	sim.empurrar(vit, ctl.centro, 30.0)
	rodar(sim, 0.2)
	ok(not vit.vivo, "empurrão na beira derrubou o Vigilante")
	# abate PvP dá 3 pontos
	var a: Ent = js[0]; var b: Ent = js[1]
	var pa: int = ctl.participantes[a.id]["pontos"]
	sim.matar(b, a)
	ok(ctl.participantes[a.id]["pontos"] == pa + 3 and conta("morte_pvp") >= 1, "abate PvP: +3 pontos")
	ok(Itens.contar(a.inv, "ficha_sangue") == 1, "abate PvP: +1 Ficha de Sangue na hora")
	ctl.participantes[a.id]["fichas"] = 3
	ctl.ao_morrer(b, a)
	ok(Itens.contar(a.inv, "ficha_sangue") == 1, "no máximo 3 fichas por abate em um evento")
	ok(b.renascer_t > 1000, "eliminado não renasce no cume")

func teste_cancelado() -> void:
	print("[1 jogador começa e vai até o fim]")
	var r := novo_cume(["cultista"])
	var sim: WorldSim = r[0]; var ctl: HermonCtl = r[1]; var j: Ent = r[2][0]
	ctl.definir_espera(1.0)
	rodar(sim, 1.5)
	ok(ctl.estado == "juramento", "1 jogador: o evento começa (regra do Jefin, 18/10)")
	var r2 := novo_cume(["cultista"])
	r2[1].forcar_inicio()
	ok(r2[1].estado == "juramento", "início imediato (GM) com 1 jogador")

func teste_fim_por_tempo() -> void:
	print("[fim aos 15 min com 2 sobreviventes]")
	var r := novo_cume(["tecnomancer", "humano"])
	var sim: WorldSim = r[0]; var ctl: HermonCtl = r[1]; var js: Array = r[2]
	ctl.definir_espera(0.5)
	rodar(sim, 1.0)
	for e: Ent in sim.ents.values():
		if e.aux.get("vigilante", false): e.alvejavel = false; e.raio_aggro = 0.0
	ctl.participantes[js[1].id]["pontos"] = 5
	for c in ctl.aneis: c["avisado"] = true; c["caiu"] = true   # sem quedas neste teste
	var ouro0: int = js[1].ouro
	ctl.t = 899.0
	rodar(sim, 1.5, func():
		for j: Ent in js: j.hp = j.hp_max)
	ok(ctl.estado == "fim" and ctl.vencedor == js[1].id, "vence quem tem mais pontos")
	ok(Itens.contar(js[1].inv, "lagrima_angelica") == 1 and js[1].ouro - ouro0 == 15 * 30, "vencedor também leva o prêmio de sobrevivente (1 Angélica + 450 de ouro)")
	ok(Itens.contar(js[0].inv, "lagrima_angelica") == 1, "sobrevivente: 1 Angélica")
	ok(Itens.contar(js[0].inv, "ficha_sangue") == 1 and Itens.contar(js[1].inv, "ficha_sangue") == 3, "fichas de PvP: sobrevivente 1, vencedor 3")
	rodar(sim, 9.0)
	ok(conta("trocar_mapa") == 2, "todos voltam depois da coroação")
	# chance da arma lendária: 1000 vencedores do Humano, ~30% ganham a Escopeta do Juramento Quebrado
	var ganhou := 0
	var outra := false
	for i in 1000:
		var w := Jogador.criar(sim, "humano", "W")
		var a := ctl._arma_lendaria(w, ctl.ev["premios"]["testemunha"])
		if not a.is_empty():
			ganhou += 1
			if a["id"] != "escopeta_juramento_quebrado" or a["raridade"] != "lendario": outra = true
	ok(ganhou >= 255 and ganhou <= 345, "arma lendária sai em ~30%% dos vencedores (%d de 1000)" % ganhou)
	ok(not outra, "a arma é sempre a lendária da classe do vencedor")

func teste_clicar_convite() -> void:
	print("[clicar no convite]")
	var r := novo_cume(["anjo"])
	var sim: WorldSim = r[0]; var j: Ent = r[2][0]
	Jogador.dar_item(sim, j, Itens.novo("convite_dos_vigilantes", 1))
	var it: Dictionary = {}
	for x in j.inv:
		if x["id"] == "convite_dos_vigilantes": it = x
	evs.clear()
	Jogador.usar_item(sim, j, int(it["uid"]))
	ok(conta("usar_evento", func(d): return d["uso"] == "evento:cume_vigilantes" and d["_para"] == j.id) == 1, "clicar no convite chama o servidor")
	ok(Itens.contar(j.inv, "convite_dos_vigilantes") == 1, "o convite só é gasto quando o servidor aceita")

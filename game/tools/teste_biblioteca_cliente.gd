extends SceneTree
## Biblioteca Soterrada, parte 2: mapa interior, estante, leitura, /ajoelhar, título/aura/anúncio, água, portais.
## godot --headless --script res://tools/teste_biblioteca_cliente.gd
var ev: Array = []
func _ev(t: String, d: Dictionary) -> void:
	ev.append([t, d.duplicate()])
func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)
func achar(tipo: String) -> Array:
	return ev.filter(func(x): return x[0] == tipo)
var falhas := 0
func ok(c: bool, msg: String) -> void:
	if not c: falhas += 1; print("FALHA: ", msg)
	else: print("ok: ", msg)

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(3)
	sim.evento.connect(_ev)
	var j := Jogador.criar(sim, "humano", "Tester")
	Jogador.entrar(sim, j, "biblioteca_soterrada", Vector2(15.5, 13.5))
	rodar(sim, 0.3)
	ok(sim.mapa_id == "biblioteca_soterrada", "mapa interior carrega")
	ok(sim.zona_em(j.pos) == "biblioteca_soterrada", "zona da biblioteca: " + sim.zona_em(j.pos))
	var est: Ent = null; var esc: Ent = null; var fic: Ent = null
	var n_est := 0
	for o: Ent in sim.ents.values():
		if o.tipo == "objeto" and o.aux.get("obj", "") == "estante_biblioteca":
			n_est += 1
			if est == null: est = o
		if o.tipo == "objeto" and o.aux.get("obj", "") == "escada_corda_biblioteca": esc = o
		if o.tipo == "objeto" and o.aux.get("obj", "") == "ficharia": fic = o
	ok(n_est == 8, "8 estantes (%d)" % n_est)
	var npc_ok := sim.ents.values().any(func(x): return x.tipo == "npc" and x.kind == "eulalia_prado")
	ok(npc_ok, "Eulália no balcão")
	# estante: abrir lista
	ev.clear()
	Jogador.cmd_interagir(sim, j, est.id); rodar(sim, 6.0)
	var le := achar("estante")
	ok(le.size() == 1 and le[0][1]["modo"] == "estante" and le[0][1]["livros"].size() == 9, "estante abre lista com os 9 (%d livros)" % (le[0][1]["livros"].size() if le.size() else 0))
	ok(achar("aviso").filter(func(x): return str(x[1]).contains("Já fez")).is_empty(), "estante não diz 'Já fez isto aqui'")
	# ler perto da estante
	ev.clear()
	Comandos.executar(sim, j, "ler", ["regulamento"]); rodar(sim, 0.1)
	var tx := achar("texto")
	ok(tx.size() == 1 and tx[0][1].get("id", "") == "regulamento", "lê livro aberto com id")
	ok(j.flags.has("estante_regulamento") and j.flags.has("leu_regulamento"), "flags estante_/leu_")
	# um texto do servidor que a estante oferece (o título vem do servidor, nunca do cliente)
	var tid_srv := ""
	for lv in le[0][1]["livros"]:
		if not Defs.ler("res://data/design/missoes/biblioteca.json")["livros"].has(lv["id"]): tid_srv = lv["id"]
	ev.clear()
	if tid_srv != "": Comandos.executar(sim, j, "ler", [tid_srv]); rodar(sim, 0.1)
	ok(tid_srv != "" and achar("texto").size() == 1 and achar("texto")[0][1]["titulo"] != "", "lê texto do servidor pela estante")
	# longe: só relê o que já está na Estante
	j.pos = Vector2(15.5, 13.5); rodar(sim, 0.1); ev.clear()
	Comandos.executar(sim, j, "ler", ["sete_principios"]); rodar(sim, 0.1)
	ok(achar("texto").size() == 0, "longe da estante não lê livro que não leu")
	Comandos.executar(sim, j, "ler", ["regulamento"]); rodar(sim, 0.1)
	ok(achar("texto").size() == 1, "relê da Estante pessoal em qualquer lugar")
	Comandos.executar(sim, j, "ler", ["nao_existe_123"]); rodar(sim, 0.1)
	ok(achar("texto").size() == 1, "id inexistente não lê nada")
	# diário
	ev.clear()
	Comandos.executar(sim, j, "estante", []); rodar(sim, 0.1)
	var di := achar("estante")
	ok(di.size() == 1 and di[0][1]["modo"] == "diario" and di[0][1]["livros"].size() >= 1, "Estante do diário (%d)" % (di[0][1]["livros"].size() if di.size() else 0))
	# ficharia (texto do servidor pela definição do objeto)
	ev.clear()
	Jogador.cmd_interagir(sim, j, fic.id); rodar(sim, 6.0)
	ok(achar("texto").size() >= 1 and j.flags.has("leu_ficharia"), "fichário mostra texto do servidor")
	# gesto
	ev.clear()
	Comandos.executar(sim, j, "gesto", ["ajoelhar"]); rodar(sim, 0.1)
	ok(achar("gesto").size() == 1, "gesto ajoelhar emitido")
	Comandos.executar(sim, j, "gesto", ["dancar"]); rodar(sim, 0.1)
	ok(achar("gesto").size() == 1, "gesto desconhecido ignorado")
	# ações de payload: título, aura, anúncio, estado, uma_vez (payload de teste, não vem do selo)
	ev.clear()
	Biblioteca._acoes(sim, j, [{"titulo": "Teste de Título"}, {"aura": "teste"}, {"anuncio": "{nome} testou o anúncio."}])
	ok(j.aux.get("titulo", "") == "Teste de Título" and j.flags.get("bib_titulo", "") == "Teste de Título", "título guardado")
	ok(j.aux.get("aura", "") == "teste", "aura guardada")
	var an := achar("chat")
	ok(an.size() == 1 and an[0][1].get("anuncio", false) and str(an[0][1]["texto"]) == "Tester testou o anúncio.", "anúncio com {nome}")
	j.aux.erase("titulo"); j.aux.erase("aura"); Biblioteca.restaurar(j)
	ok(j.aux.get("titulo", "") == "Teste de Título" and j.aux.get("aura", "") == "teste", "título e aura voltam ao carregar")
	j.flags["estado:teste"] = 3
	ok(Biblioteca._requer(sim, j, {"estado": {"teste": 3}}) and not Biblioteca._requer(sim, j, {"estado": {"teste": 2}}), "estado exato")
	ok(Biblioteca._requer(sim, j, {"missao_concluida": "missao_que_nao_existe"}) == false, "missao_concluida aceita texto")
	j.flags.erase("bib_titulo"); j.flags.erase("bib_aura"); j.aux.erase("titulo"); j.aux.erase("aura")
	# água: no mapa da cidade, perto do rio
	var sim2 := WorldSim.new(4)
	var j2 := Jogador.criar(sim2, "humano", "Agua")
	Jogador.entrar(sim2, j2, "area_inicial", Vector2(70, 94))
	var ter: Array = sim2.mapa.get("terreno", []); var pisos: Dictionary = sim2.mapa.get("pisos", {})
	var p_agua := Vector2(-1, -1)
	for y in ter.size():
		for x in (ter[y] as String).length():
			if str(pisos.get((ter[y] as String)[x], "")).contains("agua"): p_agua = Vector2(x + 0.5, y + 0.5); break
		if p_agua.x >= 0: break
	ok(p_agua.x < 0 or Biblioteca.perto_de_agua(sim2, p_agua + Vector2(1.0, 0)), "perto de água: %s" % str(p_agua))
	ok(not Biblioteca.perto_de_agua(sim2, Vector2(70, 94)), "longe da água")
	# portal da escada de corda -> rua
	ev.clear()
	Jogador.cmd_interagir(sim, j, esc.id); rodar(sim, 6.0)
	var tm := achar("trocar_mapa")
	ok(tm.size() == 1 and tm[0][1]["mapa"] == "area_inicial", "escada de corda leva à rua " + (str(tm[0][1]) if tm.size() else ""))
	print("teste_biblioteca_cliente: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

extends SceneTree
## Teste headless do Cume dos Vigilantes (0.9.8): contagem de 3 min na tela, spot de farm de 10 min com
## Vigilantes, anjos com 3x XP, baú dourado a 0,5% por abate e o final todo mundo contra todo mundo.
## godot --headless --path . --script res://tools/teste_vigilantes.gd

var cont := {}
var fases: Array = []
var avisos_bau := 0
var erros: Array = []

func _ev(t: String, d: Dictionary) -> void:
	cont[t] = cont.get(t, 0) + 1
	if t == "hermon" and (fases.is_empty() or fases[fases.size() - 1] != d.get("fase", "")):
		fases.append(d.get("fase", ""))
	if t == "aviso" and str(d.get("texto", "")).begins_with("Um baú dourado"): avisos_bau += 1

func rodar(sim: WorldSim, seg: float, f: Callable = Callable()) -> void:
	for i in int(seg * 30):
		if f.is_valid() and i % 30 == 0: f.call()
		sim.passo(WorldSim.TICK)

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

func vigilantes(sim: WorldSim) -> int:
	var n := 0
	for e: Ent in sim.ents.values():
		if e.tipo == "monstro" and e.vivo and e.aux.get("vigilante", false): n += 1
	return n

func check_xp(xa: int, xb: int) -> void:
	checar(xb > 0, "mob comum dá XP (%d)" % xb)
	checar(absi(xa - xb * 3) <= 1, "Vigilante dá 3x o XP do mob comum (%d contra %d)" % [xa, xb])

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	sim.evento.connect(_ev)
	var js: Array = []
	for i in 3:
		var j := Jogador.criar(sim, ["anjo", "humano", "demonio"][i], "Vig%d" % i)
		if i == 0: Jogador.entrar(sim, j, "cume_dos_vigilantes", Vector2(30, 30))
		else: sim.adicionar_jogador(j, Vector2(30 + i * 0.5, 30))
		js.append(j)
	var h: HermonCtl = sim.hermon
	checar(h != null, "o mapa cume_dos_vigilantes cria o HermonCtl")
	if h == null: quit(1); return
	for j: Ent in js: h.entrou(j)
	checar(h.participantes.size() == 3, "3 jogadores entram na janela (%d)" % h.participantes.size())
	h.forcar_inicio()
	checar(h.estado == "contagem", "a entrada fecha e começa a contagem (%s)" % h.estado)
	checar(fases.has("contagem"), "a fase contagem chega na tela de todos")
	checar(vigilantes(sim) == 0, "Vigilantes ainda ajoelhados durante a contagem")
	rodar(sim, 179.0)
	checar(h.estado == "contagem", "ainda na contagem aos 179 s (%s)" % h.estado)
	rodar(sim, 2.0)
	checar(h.estado == "farm", "depois de 3 min entra o farm (%s)" % h.estado)
	checar(vigilantes(sim) >= 1, "Vigilantes surgem no spot (%d)" % vigilantes(sim))
	checar(fases.has("farm"), "a fase farm chega na tela de todos")
	# sem PvP no farm: todos do mesmo lado
	var mesmo_lado := true
	for j: Ent in js:
		if j.lado_forcado != "hermon": mesmo_lado = false
	checar(mesmo_lado, "no farm todos estão do mesmo lado (sem PvP)")
	# XP triplo: dois jogadores iguais (nível 1) abatem um Vigilante e um mob comum do mesmo nível
	var a: Ent = Jogador.criar(sim, "anjo", "XpVig")
	var b: Ent = Jogador.criar(sim, "anjo", "XpComum")
	var vig := sim.criar_mob("vigilante_jurado", a.pos, 1)
	vig.aux["vigilante"] = true; vig.aux["xp_mult"] = float(h.ev["farm"]["xp_mult"])
	Jogador.abateu(sim, a, vig)
	var comum := sim.criar_mob("vigilante_jurado", b.pos, 1)
	Jogador.abateu(sim, b, comum)
	check_xp(a.xp, b.xp)
	# baú: 0,5% por abate do Vigilante; amostra grande
	var n_abates := 20000
	var antes := avisos_bau
	for i in n_abates: h.rolar_bau(a)
	var taxa := float(avisos_bau - antes) / n_abates
	checar(absf(taxa - 0.005) < 0.002, "baú dourado cai com ~0,5%% (%.4f em %d rolagens)" % [taxa, n_abates])
	# farm acaba em 10 min: vira todos contra todos
	rodar(sim, float(h.ev["farm"]["dur_s"]) + 1.0)
	checar(h.estado == "juramento", "depois de 10 min começa o todos contra todos (%s)" % h.estado)
	checar(fases.has("juramento"), "a fase juramento chega na tela de todos")
	var lados := true
	for j: Ent in h.vivos():
		if not j.lado_forcado.begins_with("h_"): lados = false
	checar(lados, "no final cada um é o próprio lado (PvP liberado)")
	# final: quando sobra um jogador e nenhum Vigilante, termina
	for e: Ent in sim.ents.values().duplicate():
		if e.tipo == "monstro" and e.aux.get("vigilante", false): sim.matar(e, null)
	for j in js.slice(1): h.participantes[j.id]["vivo"] = false
	rodar(sim, 1.0)
	checar(h.estado == "fim", "com um jogador vivo e nenhum Vigilante, o evento termina (%s)" % h.estado)
	print("\nFases vistas: %s" % str(fases))
	print("RESULTADO: %s" % ("PASSOU" if erros.is_empty() else "%d falha(s)" % erros.size()))
	quit(0 if erros.is_empty() else 1)

class_name Comandos
## Tudo que o jogador pode pedir ao mundo. No solo o cliente chama direto; em rede chega pelo servidor.
## Os argumentos vêm de fora (rede), então cada um é conferido antes de virar ação.

const NOMES := ["mover", "atacar", "interagir", "pegar", "pocao", "skill", "ponto", "usar_item", "equipar", "desequipar",
	"mover_item", "soltar_item", "comprar", "vender", "refinar", "redistribuir", "escolher", "virar", "no_lugar", "fechar", "auto"]

static func executar(sim: WorldSim, e: Ent, nome: String, a: Array) -> void:
	if e == null or not nome in NOMES: return
	match nome:
		"mover":
			if _v2(a, 0): Jogador.cmd_mover(sim, e, a[0])
		"atacar":
			if _int(a, 0):
				Jogador.cmd_atacar(sim, e, a[0])
				if a.size() > 1 and a[1] is bool: e.no_lugar = a[1]
		"interagir":
			if _int(a, 0): Jogador.cmd_interagir(sim, e, a[0])
		"pegar":
			if _int(a, 0): Jogador.cmd_pegar(sim, e, a[0])
		"pocao":
			if _str(a, 0) and a[0] in ["vida", "recurso", "antidoto"]: Jogador.cmd_pocao(sim, e, a[0])
		"skill":
			if _int(a, 0) and _int(a, 1) and _v2(a, 2) and a[0] >= 0 and a[0] < 9: Jogador.cmd_skill(sim, e, a[0], a[1], a[2])
		"ponto":
			if _str(a, 0): Jogador.cmd_ponto(sim, e, a[0])
		"usar_item":
			if _int(a, 0): Jogador.usar_item(sim, e, a[0])
		"equipar":
			if _int(a, 0) and _str(a, 1): Jogador.equipar(sim, e, a[0], a[1])
		"desequipar":
			if not _str(a, 0): return
			var x: int = a[1] if _int(a, 1) else -1
			var y: int = a[2] if _int(a, 2) else -1
			var uid := int(e.equip.get(a[0], {}).get("uid", -1))
			Jogador.desequipar(sim, e, a[0], x, y)
			# arrastou do corpo direto para o armazém: passa pela mochila
			if a.size() > 3 and a[3] == "armazem" and uid >= 0 and not Itens.por_uid(e.inv, uid).is_empty():
				Jogador.mover_item(sim, e, uid, "mochila", "armazem", x, y)
		"mover_item":
			if _int(a, 0) and _str(a, 1) and _str(a, 2) and _int(a, 3) and _int(a, 4) and a[1] in ["mochila", "armazem"] and a[2] in ["mochila", "armazem"]:
				Jogador.mover_item(sim, e, a[0], a[1], a[2], a[3], a[4])
		"soltar_item":
			if _int(a, 0): Jogador.soltar_item(sim, e, a[0])
		"comprar":
			if _str(a, 0) and _int(a, 1) and a[1] >= 1 and a[1] <= 99: Jogador.comprar(sim, e, a[0], a[1])
		"vender":
			if _int(a, 0): Jogador.vender(sim, e, a[0])
		"refinar":
			if _int(a, 0) and _str(a, 1): Jogador.refinar(sim, e, a[0], a[1])
		"redistribuir":
			Jogador.redistribuir(sim, e)
		"escolher":
			if _int(a, 0): Missoes.escolher(sim, e, a[0])
		"virar":
			if _v2(a, 0) and (a[0] as Vector2).length() > 0.01: e.facing = (a[0] as Vector2).normalized()
		"no_lugar":
			if a.size() > 0 and a[0] is bool: e.no_lugar = a[0]
		"auto":   # modo automático (tecla Z): a lógica fica em Jogador.passo, lendo e.aux["auto"]
			if a.size() > 0 and a[0] is bool:
				e.aux["auto"] = a[0]
				sim.emitir_a(e, "aviso", {"texto": "Modo automático ligado." if a[0] else "Modo automático desligado."})
		"fechar":
			if _str(a, 0) and a[0] in ["dialogo", "servico"]: e.aux.erase(a[0])

static func _int(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is int

static func _str(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is String and (a[i] as String).length() < 64

static func _v2(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is Vector2 and (a[i] as Vector2).is_finite()

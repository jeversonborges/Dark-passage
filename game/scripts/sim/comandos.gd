class_name Comandos
## Tudo que o jogador pode pedir ao mundo. No solo o cliente chama direto; em rede chega pelo servidor.
## Os argumentos vêm de fora (rede), então cada um é conferido antes de virar ação.

const NOMES := ["mover", "atacar", "interagir", "pegar", "pocao", "skill", "ponto", "usar_item", "equipar", "desequipar",
	"mover_item", "soltar_item", "comprar", "vender", "refinar", "redistribuir", "escolher", "virar", "no_lugar", "fechar", "auto",
	"pet_modo", "pet_atacar", "pet_mover"]

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
		"pet_modo":
			if _str(a, 0) and a[0] in ["agressivo", "passivo", "seguir", "parado"]: _pet_modo(sim, e, a[0])
		"pet_atacar":
			if _int(a, 0): _pet_atacar(sim, e, a[0])
		"pet_mover":
			if _v2(a, 0): _pet_mover(sim, e, a[0])
		"fechar":
			if _str(a, 0) and a[0] in ["dialogo", "servico"]: e.aux.erase(a[0])

static func _pets(sim: WorldSim, e: Ent) -> Array:
	var out: Array = []
	if e.classe != "cultista": return out
	for pet: Ent in sim.ents.values():
		if pet.tipo == "invocacao" and pet.dono == e.id and pet.kind == "servo_de_carne" and pet.vivo: out.append(pet)
	return out

static func _pet_modo(sim: WorldSim, e: Ent, modo: String) -> void:
	if e.classe != "cultista": return
	e.aux["pet_modo"] = modo
	e.aux.erase("pet_destino"); e.aux.erase("pet_pos_parado"); e.aux.erase("pet_alvo_pendente")
	for pet: Ent in _pets(sim, e):
		pet.aux["pet_modo"] = modo
		pet.aux.erase("pet_destino"); pet.aux.erase("pet_pos_parado"); pet.aux.erase("pet_ordem_alvo")
		pet.alvo = -1; pet.caminho.clear()
	var texto := {"agressivo": "Servo em modo agressivo.", "passivo": "Servo em modo passivo.", "seguir": "Servo vai acompanhar você.", "parado": "Servo vai ficar neste local."}
	sim.emitir_a(e, "aviso", {"texto": texto[modo]})

static func _pet_atacar(sim: WorldSim, e: Ent, alvo_id: int) -> void:
	if e.classe != "cultista": return
	var alvo: Ent = sim.valido(alvo_id)
	if alvo == null or not e.eh_inimigo_de(alvo) or alvo.pos.distance_to(e.pos) > 16.0:
		sim.emitir_a(e, "aviso", {"texto": "Escolha um inimigo próximo para o Servo atacar."}); return
	var pets := _pets(sim, e)
	if pets.is_empty():
		e.aux["pet_alvo_pendente"] = alvo_id
		sim.emitir_a(e, "aviso", {"texto": "Ordem guardada: o Servo atacará esse alvo quando voltar."}); return
	for pet: Ent in pets:
		pet.alvo = alvo_id; pet.aux["pet_ordem_alvo"] = true
		pet.aux.erase("pet_destino"); pet.caminho.clear()
	sim.emitir_a(e, "aviso", {"texto": "Servo, ataque!"})

static func _pet_mover(sim: WorldSim, e: Ent, destino: Vector2) -> void:
	if e.classe != "cultista": return
	var alvo := destino
	if alvo.distance_to(e.pos) > 10.0: alvo = e.pos + (alvo - e.pos).normalized() * 10.0
	alvo = sim.celula_livre_perto(alvo)
	e.aux["pet_modo"] = "mover"; e.aux["pet_destino"] = alvo; e.aux.erase("pet_alvo_pendente")
	e.aux.erase("pet_pos_parado")
	for pet: Ent in _pets(sim, e):
		pet.aux["pet_modo"] = "mover"; pet.aux["pet_destino"] = alvo
		pet.aux.erase("pet_pos_parado")
		pet.aux.erase("pet_ordem_alvo"); pet.alvo = -1; pet.caminho.clear()
	sim.emitir_a(e, "aviso", {"texto": "Servo, fique neste local."})

static func _int(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is int

static func _str(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is String and (a[i] as String).length() < 64

static func _v2(a: Array, i: int) -> bool:
	return a.size() > i and a[i] is Vector2 and (a[i] as Vector2).is_finite()

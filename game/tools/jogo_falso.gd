extends Node2D
## Cliente mínimo para testar mira_controle.gd sem importar arte: só o que a mira lê do game.gd.
var sim: WorldSim
var jog: Ent
var views := {}
var objs := {}
var itens_chao := {}
var alvo_amigo := -1
var trocando := false
var audio := Audio.new()
var mira_ctl: Node2D

class Vista:
	var visible := true
	var cor_anel := Color.WHITE

class Audio:
	func tocar(_a, _b = null, _c = 0.0) -> void: pass

func iniciar(classe: String, _nome: String) -> void:
	sim = WorldSim.new(7)
	jog = Jogador.criar(sim, classe, "Teste")
	Jogador.entrar(sim, jog, "area_inicial", Vector2(44.5, 44))
	mira_ctl = load("res://scripts/client/mira_controle.gd").new()
	mira_ctl.game = self
	add_child(mira_ctl)
	_ver_todos()

func _ver_todos() -> void:
	for e: Ent in sim.ents.values():
		if not views.has(e.id): views[e.id] = Vista.new()

func _surgiu(id: int) -> void:
	if not views.has(id): views[id] = Vista.new()

func cmd(nome: String, a: Array = []) -> void:
	Comandos.executar(sim, jog, nome, a)

func usar_skill(slot: int) -> void:
	if mira_ctl.ativo: mira_ctl.usar_skill(slot)

func _amigo_valido() -> bool:
	return false

extends SceneTree
## Teste headless da passiva do Andras (Marcado pelo General): cada acerto soma uma pilha de +3% no dano
## que o jogador toma; dez segundos sem acertar zera. godot --headless --path . --script res://tools/teste_marca_general.gd

var erros: Array = []

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

func pilhas(j: Ent) -> int:
	for b in j.buffs:
		if b["id"] == ChefeCtl.MARCA_GENERAL: return int(b.get("pilhas", 0))
	return 0

func mod_dano(j: Ent) -> float:
	return j.mod("dano_recebido")

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(11)
	var j := Jogador.criar(sim, "anjo", "Teste")
	sim.ents[j.id] = j
	var boss := Ent.new()
	boss.id = sim.novo_id(); boss.tipo = "chefe"; boss.kind = "general_partido"
	sim.ents[boss.id] = boss
	print("Marcado pelo General")
	checar(pilhas(j) == 0, "começa sem pilha")
	for i in 3: ChefeCtl.marcar_golpe(sim, boss, j)
	checar(pilhas(j) == 3, "três acertos somam três pilhas")
	checar(absf(mod_dano(j) - 0.09) < 0.0001, "três pilhas = +9% de dano recebido")
	rodar(sim, 5.0)
	ChefeCtl.marcar_golpe(sim, boss, j)
	checar(pilhas(j) == 4, "acerto antes de 10 s continua o acúmulo (4 pilhas)")
	rodar(sim, 10.5)
	checar(pilhas(j) == 0, "dez segundos sem acertar zera a pilha")
	checar(absf(mod_dano(j))  < 0.0001, "sem pilha, sem dano extra")
	ChefeCtl.marcar_golpe(sim, boss, j)
	checar(pilhas(j) == 1, "novo acerto depois do reset volta a uma pilha")
	for i in 20: ChefeCtl.marcar_golpe(sim, boss, j)
	checar(pilhas(j) == 10, "teto de dez pilhas (chefes.json max_pilhas)")
	print("\nteste_marca_general: %d erro(s)" % erros.size())
	quit(1 if erros.size() > 0 else 0)

extends SceneTree
## Teste headless da zona azul do Andras: quem está no azul no impacto não toma dano; quem está na vermelha
## e fora do azul leva dano_fora_azul_mult. godot --headless --path . --script res://tools/teste_zona_azul.gd

var erros: Array = []

func checar(ok: bool, txt: String) -> void:
	print(("  ok  " if ok else "  FALHOU  ") + txt)
	if not ok: erros.append(txt)

## Monta um golpe telegrafado do Andras e devolve o HP que o jogador perdeu no impacto.
func impacto(seed_: int, pos_jogador: Vector2, sem_mult: bool) -> float:
	var sim := WorldSim.new(seed_)
	var j := Jogador.criar(sim, "anjo", "Teste")
	sim.ents[j.id] = j
	j.pos = pos_jogador; j.er = 0.0; j.defesa = 0.0
	var boss := Ent.new()
	boss.id = sim.novo_id(); boss.tipo = "chefe"; boss.kind = "general_partido"
	boss.pos = Vector2(10, 10); boss.nivel = 8; boss.dano_min = 27.0; boss.dano_max = 36.0; boss.ar = 999.0
	boss.critico = 0.0; boss.vivo = true
	sim.ents[boss.id] = boss
	var d: Dictionary = Defs.CHEFES["general_partido"]["fases"][0]["ataques"][1].duplicate(true)
	if sem_mult: d.erase("dano_fora_azul_mult")
	var a := {"preparo": 0.8, "dir": Vector2.RIGHT, "op": {"mult": 1.6, "sensacao": "golpe_pesado", "postura": 0.0, "area": true, "elemento": "fisico"}, "def": d}
	var tid := sim.criar_telegrafo(boss, d, a)
	var hp0 := j.hp
	j.pos = pos_jogador
	sim.disparar_telegrafo(tid)
	return hp0 - j.hp

func _init() -> void:
	Defs.carregar()
	var centro := Vector2(10 + 1.2, 10) + Vector2.RIGHT.orthogonal() * 0.9
	print("Zona azul do golpe de estandarte")
	var no_azul := impacto(5, centro, false)
	checar(no_azul == 0.0, "quem está no azul não toma dano (perdeu %s)" % no_azul)
	var na_vermelha := impacto(5, Vector2(10 + 1.8, 10), false)
	checar(na_vermelha > 0.0, "quem está na vermelha fora do azul toma dano (perdeu %s)" % na_vermelha)
	var normal := impacto(5, Vector2(10 + 1.8, 10), true)
	var razao := na_vermelha / maxf(normal, 0.0001)
	checar(absf(razao - 3.0) < 0.2, "com dano_fora_azul_mult 3 o golpe sai 3x (razão %.2f)" % razao)
	print("\nteste_zona_azul: %d erro(s)" % erros.size())
	quit(1 if erros.size() > 0 else 0)

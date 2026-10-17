extends SceneTree
const Unidade := preload("res://scripts/client/unidade.gd")
## Camadas de arma: o Anjo com espada tem quadro na direção S, sem arma não tem camada, e a folha do corpo muda.

func _init() -> void:
	Defs.carregar()
	var falhas := 0
	var sim := WorldSim.new(1)
	var e: Ent = Jogador.criar(sim, "anjo", "Teste", {})
	var u := Unidade.new()
	u.iniciar(null, e)
	if u._kind_armas != "anjo": print("FALHA: corpo sem arma não carregou para o anjo"); falhas += 1
	if not u._armas.has("arma"): print("FALHA: camada da arma não montada"); falhas += 1
	var sem = u._quadro_arma({}, "segunda_mao", "idle", 0, 0)
	if sem != null: print("FALHA: sem segunda mão apareceu camada"); falhas += 1
	if u._quadro_arma({}, "arma", "idle", 0, 0) == null: print("FALHA: mão principal vazia (padrão da classe deveria aparecer)"); falhas += 1
	var id_espada := "espada_vigilia_rachada"
	if not Defs.VISUAIS.has(id_espada):
		for k in Defs.VISUAIS:
			if Defs.VISUAIS[k]["silhueta"] == "espada": id_espada = k; break
	var q = u._quadro_arma({"id": id_espada, "ref": 0}, "arma", "idle", 0, 0)
	if q == null and u._quadro_arma({"id": id_espada, "ref": 0}, "arma", "idle", 0, 1) == null:
		print("FALHA: espada sem quadro no idle S"); falhas += 1
	print("teste_armas: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

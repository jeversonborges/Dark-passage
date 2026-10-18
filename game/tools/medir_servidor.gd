extends SceneTree
## Mede a memória do servidor por mapa: carrega cada mapa num WorldSim, roda uns segundos de simulação,
## solta o mapa e conta os objetos que ficaram vivos. Depois repete o ciclo carregar/soltar num mapa grande
## e mostra quanto a memória cresceu por ciclo (o que um servidor que troca de mapa vai acumulando).
## godot --headless --path . --script res://tools/medir_servidor.gd [-- sem_descarregar]
##   sem_descarregar: pula WorldSim.descarregar(), para comparar com o comportamento antigo.

const SEGUNDOS := 20.0
const CICLOS := 30
const MAPA_CICLO := "area_inicial"

func _initialize() -> void:
	var descarregar := not "sem_descarregar" in OS.get_cmdline_user_args()
	var m_antes := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
	Defs.carregar()
	print("memória antes dos dados: %.1f MB, depois: %.1f MB" % [m_antes, Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0])
	print("modo: ", "com descarregar" if descarregar else "SEM descarregar (antigo)")
	var ids: Array = []
	for f in DirAccess.get_files_at("res://data/mapas"):
		if f.ends_with(".json"): ids.append(f.get_basename())
	ids.sort()
	print("mapa\tobjetos_antes\tobjetos_com_mapa\tobjetos_depois_soltar")
	for id in ids:
		var antes := Performance.get_monitor(Performance.OBJECT_COUNT)
		var sim := _simular(id, SEGUNDOS)
		var com := Performance.get_monitor(Performance.OBJECT_COUNT)
		if descarregar: sim.descarregar()
		sim = null
		print("%s\t%d\t%d\t%d" % [id, antes, com, Performance.get_monitor(Performance.OBJECT_COUNT)])
	var mem0 := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
	for i in CICLOS:
		var sim := _simular(MAPA_CICLO, 2.0)
		if descarregar: sim.descarregar()
		sim = null
	var mem1 := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
	print("ciclos de %s: %d, memória %.1f MB -> %.1f MB (+%.2f MB por ciclo)" % [MAPA_CICLO, CICLOS, mem0, mem1, (mem1 - mem0) / CICLOS])
	quit()

func _simular(id: String, seg: float) -> WorldSim:
	var sim := WorldSim.new(1)
	sim.carregar_mapa(id)
	for i in int(seg * 30):
		sim.passo(WorldSim.TICK)
	return sim

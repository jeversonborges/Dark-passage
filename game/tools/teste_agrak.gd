extends SceneTree
## Teste da Arena do Agrak (scripts/sim/agrak_ctl.gd) com um host falso, sem mundo nem rede.
## Uso: godot --headless --path . --script res://tools/teste_agrak.gd
## Confere a sequência das etapas, os chefes e o HP por gladiador, os casos de borda do README e o Anel do Amargo.

const AgrakCtl := preload("res://scripts/sim/agrak_ctl.gd")

class HostFalso extends RefCounted:
	var etapas := []          # ids na ordem
	var spawns := []          # [id, hp]
	var portoes := []
	var lados := {}
	var espectadores := []
	var premios := []         # [id, qtd]
	var falas := []
	var cancelados := []
	var recuos := 0
	var encerrado := false
	var anel_raio := -1.0
	var dano_por_id := {}     # id -> total
	var fora := {}            # id -> bool (fora do anel agora)
	var hp := {}              # id -> fração
	var recuperados := []
	var pocoes_trancadas := false
	func etapa(id: String, _dur: float) -> void: etapas.append(id)
	func prender(_ids: Array) -> void: pass
	func fala(quem: String, texto: String) -> void: falas.append([quem, texto])
	func portao(id: String, aberto: bool) -> void: portoes.append([id, aberto])
	func spawn_chefe(id: String, hp_total: float) -> void: spawns.append([id, hp_total])
	func recuar_chefes() -> void: recuos += 1
	func recuperar(ids: Array, frac: float) -> void: recuperados.append([ids, frac])
	func trancar_pocoes(v: bool) -> void: pocoes_trancadas = v
	func definir_lados(m: Dictionary) -> void: lados = m
	func anel(raio: float) -> void: anel_raio = raio
	func fora_do_anel(id: int, _raio: float) -> bool: return bool(fora.get(id, false))
	func dano_anel(id: int, frac: float) -> void: dano_por_id[id] = float(dano_por_id.get(id, 0.0)) + frac
	func espectador(id: int) -> void: espectadores.append(id)
	func premiar(id: int, qtd: int) -> void: premios.append([id, qtd])
	func hp_frac(id: int) -> float: return float(hp.get(id, 1.0))
	func cancelar(ids: Array) -> void: cancelados.append(ids)
	func encerrar() -> void: encerrado = true

var falhas := 0

func check(cond: bool, msg: String) -> void:
	if not cond:
		falhas += 1
		print("[teste_agrak] FALHA ", msg)
	else:
		print("[teste_agrak] ok    ", msg)

func _novo(ids: Array) -> Array:
	var h := HostFalso.new()
	var c := AgrakCtl.new(Defs.AGRAK, h)
	c.iniciar(ids)
	return [c, h]

func _initialize() -> void:
	Defs.carregar()
	var ids := [1, 2, 3, 4]

	# A: caminho feliz: chamada, leões, respiro, golias, respiro, luta 3, vencedor
	var r := _novo(ids); var c: AgrakCtl = r[0]; var h: HostFalso = r[1]
	check(c.etapa_atual() == "chamada", "começa na chamada")
	c.passo(45.1)
	check(c.etapa_atual() == "luta_leoes", "chamada acaba aos 45 s e abre a luta dos leões")
	check(h.portoes.has(["portao_leoes", true]), "portão dos leões abre")
	check(h.spawns.size() == 3 and h.spawns[0][0] == "leao_sansao", "três leões, Sansão primeiro")
	check(absf(float(h.spawns[0][1]) - (2600.0 + 450.0 * 4)) < 0.01, "HP do Sansão = base + 450 x 4 gladiadores")
	for i in ["leao_sansao", "leao_dalila", "leao_nabucodonosor"]: c.chefe_morreu(i)
	check(c.etapa_atual() == "respiro", "leões mortos vão ao respiro")
	c.passo(20.1)
	check(c.etapa_atual() == "luta_gigante", "respiro de 20 s leva ao Golias")
	check(absf(float(h.spawns[3][1]) - (6000.0 + 1500.0 * 4)) < 0.01, "HP do Golias = 6000 + 1500 x 4")
	c.chefe_morreu("golias")
	c.passo(15.1)
	check(c.etapa_atual() == "ultimo_de_pe", "respiro de 15 s leva à luta final")
	check(h.pocoes_trancadas, "poções trancadas na luta final")
	check(h.lados.size() == 4 and h.lados[1] == "g_1", "cada gladiador vira o próprio lado")
	c.jogador_saiu(2); c.jogador_saiu(3); c.jogador_saiu(4)
	check(h.espectadores == [2, 3, 4], "quem cai vira espectador")
	check(c.etapa_atual() == "coroacao" and h.premios == [[1, 1]], "último de pé ganha 1 ficha")
	c.passo(15.1)
	check(c.fim and h.encerrado, "coroação termina e encerra")

	# B: menos de 4 inscritos cancela e devolve
	r = _novo([1, 2, 3]); c = r[0]; h = r[1]
	check(c.fim and h.cancelados.size() == 1, "3 inscritos cancela e devolve o ouro")

	# C: todos morrem na luta 1: sem vencedor, sem ficha
	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	for i in ids: c.jogador_saiu(i)
	check(c.etapa_atual() == "coroacao" and h.premios.is_empty(), "todos mortos nos leões: sem ficha")
	c.passo(15.1)
	check(c.fim and h.encerrado, "sem vencedor encerra depois da coroação")

	# D: tempo da luta dos leões acaba: monstros recuam e os vivos passam
	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	c.passo(240.1)
	check(h.recuos == 1 and c.etapa_atual() == "respiro", "tempo de 240 s: leões recuam e vivos passam")

	# E: um só sobrevive aos leões: enfrenta o Golias sozinho e, se vencer, ganha a ficha sem a luta 3
	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	c.jogador_saiu(2); c.jogador_saiu(3); c.jogador_saiu(4)
	for i in ["leao_sansao", "leao_dalila", "leao_nabucodonosor"]: c.chefe_morreu(i)
	c.passo(20.1)
	check(c.etapa_atual() == "luta_gigante", "um sobrevivente ainda enfrenta o Golias")
	c.chefe_morreu("golias")
	c.passo(15.1)
	check(not h.etapas.has("ultimo_de_pe"), "com um só de pé, a luta 3 não acontece")
	check(h.premios == [[1, 1]], "vencedor sozinho ganha a ficha")

	# F: tempo da luta final acaba: vence quem tem mais % de HP; empate não dá ficha
	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	for i in ["leao_sansao", "leao_dalila", "leao_nabucodonosor"]: c.chefe_morreu(i)
	c.passo(20.1); c.chefe_morreu("golias"); c.passo(15.1)
	c.jogador_saiu(4); c.jogador_saiu(3)
	h.hp = {1: 0.5, 2: 0.9}
	c.passo(180.1)
	check(h.premios == [[2, 1]], "tempo estourado: vence quem tem mais % de HP")

	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	for i in ["leao_sansao", "leao_dalila", "leao_nabucodonosor"]: c.chefe_morreu(i)
	c.passo(20.1); c.chefe_morreu("golias"); c.passo(15.1)
	c.jogador_saiu(4); c.jogador_saiu(3)
	h.hp = {1: 0.5, 2: 0.5}
	c.passo(180.1)
	check(h.premios.is_empty(), "empate no tempo: sem ficha")

	# G: Anel do Amargo: começa aos 60 s, encolhe de 13 a 4 em 90 s, dá dano fora dele
	r = _novo(ids); c = r[0]; h = r[1]
	c.passo(45.1)
	for i in ["leao_sansao", "leao_dalila", "leao_nabucodonosor"]: c.chefe_morreu(i)
	c.passo(20.1); c.chefe_morreu("golias"); c.passo(15.1)
	check(c.etapa_atual() == "ultimo_de_pe", "chega à luta final para testar o anel")
	h.fora = {1: true}
	c.passo(59.0)
	check(h.anel_raio < 0.0, "antes dos 60 s o anel ainda não aparece")
	check(h.dano_por_id.is_empty(), "sem dano antes do anel fechar")
	c.passo(1.5)
	check(h.anel_raio > 12.0 and h.anel_raio <= 13.0, "anel começa perto de 13 tiles aos 60 s")
	check(float(h.dano_por_id.get(1, 0.0)) > 0.0, "fora do anel tira HP desde o primeiro segundo")
	c.passo(75.0)
	check(h.anel_raio > 4.0 and h.anel_raio < 6.0, "anel encolhe até perto de 4 tiles ao fim dos 90 s")
	check(not h.dano_por_id.has(2), "quem está dentro do anel não leva dano")

	print("FALHAS: ", falhas)
	quit(1 if falhas > 0 else 0)

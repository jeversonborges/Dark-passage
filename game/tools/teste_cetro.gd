extends SceneTree
## Teste headless do Cetro do Demiurgo (entregas/cetro_demiurgo): sem rede, um jogador recebe e equipa o cetro e
## cada efeito é conferido na simulação. godot --headless --path . --script res://tools/teste_cetro.gd

var falhas := 0

func _ok(cond: bool, txt: String) -> void:
	print("[teste_cetro] %s %s" % ["OK    " if cond else "FALHOU", txt])
	if not cond: falhas += 1

func rodar(sim: WorldSim, seg: float) -> void:
	for i in int(seg * 30): sim.passo(WorldSim.TICK)

## Um carniçal de nível 3 perto do jogador (neutro por padrão: só reage se apanhar).
func mob(sim: WorldSim, j: Ent, desloc: Vector2, neutro := true) -> Ent:
	var m := sim.criar_mob("carnical", sim.celula_livre_perto(j.pos + desloc), 3)
	if neutro: m.aux["neutro"] = true
	return m

func uid_cetro(j: Ent) -> int:
	for o in j.inv:
		if o["id"] == Demiurgo.ITEM: return int(o["uid"])
	return -1

func _init() -> void:
	Defs.carregar()
	var sim := WorldSim.new(42)
	var j := Jogador.criar(sim, "demonio", "Jefin")
	Jogador.entrar(sim, j, "area_inicial", Vector2(44.5, 44))
	rodar(sim, 0.5)
	for m: Ent in sim.ents.values():   # campo limpo: só os monstros do teste
		if m.tipo == "monstro": m.vivo = false
	j.pos = sim.celula_livre_perto(Vector2(57, 53))
	# ---------------------------------------------------------------- item: dado e equipado
	Jogador.dar_item(sim, j, Itens.novo(Demiurgo.ITEM))
	var uid := uid_cetro(j)
	_ok(uid >= 0, "cetro na mochila")
	Jogador.equipar(sim, j, uid, "")
	_ok(str(j.equip.get("arma", {}).get("id", "")) == Demiurgo.ITEM and Demiurgo.tem(j), "cetro equipado e reconhecido (bonus.efeitos)")
	var dn := Itens.dano_arma(j.equip["arma"])
	_ok(absf(dn[0] - 777.0) < 0.5 and absf(dn[1] - 999.0) < 0.5, "dano da arma 777-999 (%d-%d)" % [roundi(dn[0]), roundi(dn[1])])
	_ok(str(j.equip["arma"]["raridade"]) == "demiurgico" and Defs.nome_raridade("demiurgico") == "Demiúrgico", "raridade demiurgico = Demiúrgico")
	_ok(Defs.cor_raridade("demiurgico").to_html(false) == "f4ffe9", "cor da raridade #f4ffe9")
	_ok(str(j.aux.get("aura", "")) == "demiurgo", "aux.aura = demiurgo enquanto equipado")
	# ---------------------------------------------------------------- vinculado: vender e largar recusados (segunda cópia na mochila)
	Jogador.dar_item(sim, j, Itens.novo(Demiurgo.ITEM))
	var uid2 := uid_cetro(j)
	Jogador.soltar_item(sim, j, uid2)
	_ok(not Itens.por_uid(j.inv, uid2).is_empty(), "largar recusado")
	j.aux["servico"] = {"tipo": "loja", "id": "loja_tobias"}
	var ouro := j.ouro
	Jogador.vender(sim, j, uid2)
	_ok(not Itens.por_uid(j.inv, uid2).is_empty() and j.ouro == ouro, "vender recusado")
	j.aux.erase("servico")
	j.inv.erase(Itens.por_uid(j.inv, uid2))
	# ---------------------------------------------------------------- Como em Cima, Assim Embaixo: imune a status
	sim.aplicar_status(j, "veneno", 5.0, null)
	sim.aplicar_status(j, "atordoado", 2.0, null)
	_ok(not j.tem("veneno") and not j.tem("atordoado"), "imune a status (veneno, atordoado)")
	# ---------------------------------------------------------------- Sopro do Primeiro Dia
	j.hp = 1.0; j.em_combate_t = 0.0
	rodar(sim, 10.0)
	_ok(j.hp >= j.hp_max * 0.9, "Sopro: HP %d/%d depois de 10 s" % [roundi(j.hp), roundi(j.hp_max)])
	# ---------------------------------------------------------------- A Mão que Mede: custo zero e recarga -90%
	var slot := -1; var h := {}
	for s in 6:
		var hd := Jogador.skill_def(j, s)
		if hd.is_empty() or hd.get("passiva", false) or hd.has("cargas") or int(hd.get("nivel", 1)) > j.nivel: continue
		slot = s; h = hd; break
	_ok(slot >= 0, "skill de teste no slot %d (%s)" % [slot, h.get("id", "?")])
	if slot >= 0:
		_ok(Jogador.custo(j, h) == 0.0, "custo zero")
		var alvo := mob(sim, j, Vector2(1.0, 0))
		Jogador.cmd_skill(sim, j, slot, alvo.id, alvo.pos)
		var cd: float = j.cds.get(h["id"], -1.0)
		var rec := float(h.get("recarga", 1.0))
		_ok(cd >= 0.0 and cd <= rec * 0.1 + 0.001, "recarga reduzida: %.2f s de %.2f s" % [cd, rec])
	# ---------------------------------------------------------------- Verbo: o ataque básico num monstro mata os outros a 8 m
	rodar(sim, 2.0)
	var alvos: Array = [mob(sim, j, Vector2(1.0, 0.5)), mob(sim, j, Vector2(-3.0, 2.0)), mob(sim, j, Vector2(4.0, -4.0))]
	Jogador.cmd_atacar(sim, j, alvos[0].id)
	rodar(sim, 4.0)
	var mortos := 0
	for m: Ent in alvos:
		if not m.vivo: mortos += 1
	_ok(mortos == 3, "Verbo: %d de 3 monstros a 8 m mortos pelo ataque básico" % mortos)
	# ---------------------------------------------------------------- Como em Cima, Assim Embaixo: quem bate leva o dano de volta
	rodar(sim, 1.0)
	var m2 := mob(sim, j, Vector2(1.0, 0))
	var hp0 := m2.hp
	sim.aplicar_golpe(m2, j, {"area": true})
	_ok(m2.hp < hp0 or not m2.vivo, "reflexo: o monstro que bateu perdeu vida (%d -> %d)" % [roundi(hp0), roundi(m2.hp)])
	if m2.vivo: m2.hp = 0.0; sim.matar(m2, j)
	# ---------------------------------------------------------------- Aura Demiúrgica: aliado a 5 m +50% de dano e XP; monstro a 5 m -50%
	var amigo := Jogador.criar(sim, "anjo", "Amigo")
	sim.adicionar_jogador(amigo, j.pos + Vector2(5.0, 0))
	var m3 := mob(sim, j, Vector2(-5.0, 0))
	rodar(sim, 2.0)
	_ok(absf(amigo.mod("dano") - 0.5) < 0.001 and absf(amigo.mod("xp") - 0.5) < 0.001, "aura: aliado a 5 m com dano +50%% e XP +50%% (%.2f / %.2f)" % [amigo.mod("dano"), amigo.mod("xp")])
	_ok(absf(j.mod("dano") - 0.5) < 0.001, "aura: o próprio portador com dano +50%")
	_ok(absf(m3.mod("dano") + 0.5) < 0.001, "aura: monstro a 5 m com dano -50%% (%.2f)" % m3.mod("dano"))
	# ---------------------------------------------------------------- Olho do Demiurgo: monstro agressivo a 3 m fica ocioso até apanhar
	var m4 := mob(sim, j, Vector2(0, 3.0), false)   # longe do Amigo: sem o cetro, ele é alvo normal
	m4.raio_aggro = 4.0; m4.raio_vagar = 0.0
	rodar(sim, 2.0)
	var d4 := j.pos.distance_to(m4.pos)
	_ok(m4.vivo and m4.estado in ["ocioso", "vagar"] and d4 <= m4.raio_aggro, "Olho: monstro agressivo a %.1f m (aggro %.0f m) continua ocioso (%s)" % [d4, m4.raio_aggro, m4.estado])
	sim.aplicar_golpe(j, m4, {"area": true, "mult": 0.001})
	_ok(not m4.vivo or not m4.estado in ["ocioso", "vagar"], "Olho: depois de apanhar ele revida (%s)" % m4.estado)
	# ---------------------------------------------------------------- tirar o cetro: aura some e os buffs expiram
	Jogador.desequipar(sim, j, "arma")
	rodar(sim, 2.5)
	_ok(not Demiurgo.tem(j) and not j.aux.has("aura"), "sem o cetro: bonus.efeitos e aux.aura limpos")
	_ok(absf(m3.mod("dano")) < 0.001 and absf(amigo.mod("dano")) < 0.001 and absf(j.mod("dano")) < 0.001, "sem o cetro: buffs da aura expiraram")
	# ---------------------------------------------------------------- servidor: lista de contas GM
	var gm = preload("res://scripts/net/gm.gd").new()
	gm.contas_gm = ["jefin"]
	_ok(gm.eh_conta_gm("jefin") and gm.eh_conta_gm(" Jefin ") and not gm.eh_conta_gm("outro"), "gm.eh_conta_gm: jefin é GM, outro não")
	gm.free()
	print("teste_cetro: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(falhas)

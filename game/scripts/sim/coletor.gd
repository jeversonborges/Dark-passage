class_name Coletor
## Pet coletor (0.9.6, Jefin 2026-10-18): um animal que anda com o dono e junta do chão os drops que o filtro deixa
## passar. Comprado com o vendedor de pets (Vigília e Arautos). Não ataca, não é alvo, não ganha XP e não solta nada.
## 0.9.7 (Jefin 2026-10-19, estilo MU): cada espécie é um item de pet (slot "pet"). Equipado, invoca o pet; o filtro de
## coleta fica no próprio item. Vai para o baú, e dá para ter vários. Não ataca, não é alvo, não ganha XP.
## Espécies são os animais de assets/monstros que viram pet.

const ESPECIES := {
	"cao_de_vala": {"nome": "Cão de Vala", "preco": 4000, "item": "pet_cao_de_vala", "filtro": "tudo"},
	"corvo_de_cinza": {"nome": "Corvo de Cinza", "preco": 3000, "item": "pet_corvo_de_cinza", "filtro": "raridade_minima:raro"},
	"cervo_de_lume": {"nome": "Cervo de Lume", "preco": 8000, "item": "pet_cervo_de_lume", "filtro": "ouro"},
	"serpente_do_eden": {"nome": "Serpente do Éden", "preco": 6000, "item": "pet_serpente_do_eden", "filtro": "pocoes"},
}
const RARIDADES := ["comum", "magico", "raro", "excelente", "lendario"]   ## lendario é a Relíquia (vermelho)
const POCOES := ["pocao_vida_m", "pocao_vida_p", "tonico_graxa", "hostia_negra", "caldo_cardo_comum", "pao_duro",
		"pocao_recurso_m", "pocao_recurso_p"]
const SEGUE_DIST := 2.5       ## acima disso o pet anda até o dono
const SEGUE_MAX := 12.0       ## acima disso teleporta para perto do dono
const RAIO_JUNTAR := 7.0      ## drops até essa distância do dono entram na conta
const ALCANCE_PEGAR := 0.9

## Filtro padrão: junta tudo. O jogador desmarca o que não quer.
static func filtro_padrao() -> Dictionary:
	var raridade := {}
	for r in RARIDADES: raridade[r] = true
	return {"raridade": raridade, "pocoes": true, "joias": {}, "asas": true, "baus": true}

## Filtro de fábrica do item de pet (filtro_coleta da Drops). O jogador muda depois, no próprio item.
static func filtro_inicial(esp: String) -> Dictionary:
	var f := filtro_padrao()
	var modo: String = ESPECIES[esp]["filtro"]
	if modo == "tudo": return f
	var minima := RARIDADES.find(modo.split(":")[1]) if modo.begins_with("raridade_minima") else RARIDADES.size()
	for r in RARIDADES: f["raridade"][r] = RARIDADES.find(r) >= minima   # "ouro" e "pocoes" não juntam equipamento
	f["pocoes"] = modo != "ouro"
	f["joias"] = {}; f["asas"] = false; f["baus"] = false
	return f

## Espécie de um item de pet ("" se não for item de pet).
static func especie_do_item(id: String) -> String:
	for esp in ESPECIES:
		if ESPECIES[esp]["item"] == id: return esp
	return ""

## O item de pet equipado no slot "pet" ({} se não há).
static func pet_equipado(dono: Ent) -> Dictionary:
	return dono.equip.get("pet", {})

## Configuração do pet equipado: {"especie": id ou "", "filtro": {...}}. O filtro é o do próprio item (por referência).
static func cfg(dono: Ent) -> Dictionary:
	var it := pet_equipado(dono)
	if it.is_empty(): return {"especie": "", "filtro": filtro_padrao()}
	if not (it.get("filtro") is Dictionary): it["filtro"] = filtro_padrao()
	return {"especie": especie_do_item(str(it["id"])), "filtro": it["filtro"]}

static func filtro(dono: Ent) -> Dictionary:
	return cfg(dono)["filtro"]

## O item passa no filtro? Ouro passa sempre. Poção, joia, material de asa e baú dourado têm a sua chave;
## o resto segue a raridade (comum, mágico, raro, excelente, relíquia).
static func deve_pegar(it: Dictionary, f: Dictionary) -> bool:
	var id: String = it["id"]
	if id == "_ouro": return true
	if id == "bau_dourado": return bool(f["baus"])
	if id in POCOES: return bool(f["pocoes"])
	if id in Defs.POR_TAG.get("joia:refino", []): return bool(f["joias"].get(id, true))
	if _eh_material_asa(id): return bool(f["asas"])
	return bool(f["raridade"].get(str(it.get("raridade", "comum")), true))

## Materiais de criar asas (entregas/asas/dados/asas_itens.json): rolados nos abates, fora da tabela do mob.
const MATERIAIS_ASA := ["pena_cinzenta", "pele_ressecada", "engrenagem_gasta"]

static func _eh_material_asa(id: String) -> bool:
	return id in MATERIAIS_ASA

## Muda uma chave do filtro (vinda do comando "coletor"). Valores inválidos são ignorados.
static func cmd_cfg(sim: WorldSim, e: Ent, chave: String, valor) -> void:
	var f := filtro(e)
	match chave:
		"raridade":   # [raridade, marcado]
			if not (valor is Array and valor.size() == 2 and str(valor[0]) in RARIDADES and valor[1] is bool): return
			f["raridade"][str(valor[0])] = valor[1]
		"joia":   # [id da joia ou lágrima, marcado]
			if not (valor is Array and valor.size() == 2 and str(valor[0]) in Defs.POR_TAG.get("joia:refino", [])
					and valor[1] is bool): return
			f["joias"][str(valor[0])] = valor[1]
		"pocoes", "asas", "baus":
			if not valor is bool: return
			f[chave] = valor
		_: return
	sim.emitir_a(e, "coletor", {})

## Compra o pet de uma espécie no vendedor (servico tipo "coletor"). Troca o pet que já existia.
static func comprar(sim: WorldSim, e: Ent, esp: String) -> void:
	var serv: Dictionary = e.aux.get("servico", {})
	if serv.get("tipo") != "coletor" or not ESPECIES.has(esp): return
	var preco := int(ESPECIES[esp]["preco"])
	if e.ouro < preco:
		sim.emitir_a(e, "aviso", {"texto": "Ouro insuficiente."}); sim.emitir_a(e, "som_evento", {"ev": "erro"}); return
	var it := Itens.novo(ESPECIES[esp]["item"])
	it["filtro"] = filtro_inicial(esp)
	if Itens.guardar(e.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it) > 0:
		sim.emitir_a(e, "aviso", {"texto": "Mochila cheia."}); return
	e.ouro -= preco
	sim.emitir_a(e, "ouro", {"valor": -preco})
	sim.emitir_a(e, "som_evento", {"ev": "comprar"})
	sim.emitir_a(e, "inventario", {})
	sim.emitir_a(e, "coletor", {})

## Manda o pet embora: tira o item do slot "pet" e o põe na mochila (o filtro vai junto).
static func dispensar(sim: WorldSim, e: Ent) -> void:
	if pet_equipado(e).is_empty(): return
	Jogador.desequipar(sim, e, "pet")
	sim.emitir_a(e, "coletor", {})

## Troca de pet equipado (ou tirou/pôs): o pet da cena sai e nasce o da espécie que está equipada agora.
static func trocar(sim: WorldSim, dono: Ent) -> void:
	_tirar(sim, dono)
	garantir(sim, dono)

## Saves antigos guardavam o pet em dono.aux["coletor"]. Vira um item de pet na mochila, uma vez.
static func migrar(dono: Ent) -> void:
	var antigo = dono.aux.get("coletor")
	if not (antigo is Dictionary): return
	var esp := str(antigo.get("especie", ""))
	if not ESPECIES.has(esp): dono.aux.erase("coletor"); return
	var it := Itens.novo(ESPECIES[esp]["item"])
	it["filtro"] = antigo.get("filtro", filtro_padrao())
	if Itens.guardar(dono.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it) > 0: return   # mochila cheia: tenta de novo na próxima entrada
	dono.aux.erase("coletor")

static func _meu(sim: WorldSim, dono: Ent) -> Ent:
	var pet: Ent = sim.ents.get(int(dono.aux.get("coletor_id", -1)))
	if pet != null and pet.tipo == "invocacao" and pet.dono == dono.id and pet.aux.get("coletor", false): return pet
	return null

static func _tirar(sim: WorldSim, dono: Ent) -> void:
	var pet := _meu(sim, dono)
	if pet != null: sim.ents.erase(pet.id)
	dono.aux.erase("coletor_id")

## Põe o pet da espécie escolhida ao lado do dono, se ele ainda não está neste mapa. Chamado ao entrar no mapa.
static func garantir(sim: WorldSim, dono: Ent) -> void:
	migrar(dono)
	var esp := str(cfg(dono)["especie"])
	if not ESPECIES.has(esp) or _meu(sim, dono) != null: return
	var pet := Ent.new()
	pet.id = sim.novo_id(); pet.tipo = "invocacao"; pet.dono = dono.id
	pet.kind = esp; pet.nome = ESPECIES[esp]["nome"]
	pet.aux["coletor"] = true
	pet.alvejavel = false   # ninguém ataca o coletor
	pet.hp_max = 1.0; pet.hp = 1.0
	pet.nivel = dono.nivel; pet.raio = 0.4
	pet.vel = dono.vel
	pet.pos = sim.celula_livre_perto(dono.pos + Vector2(-1.2, 0.6))
	pet.casa = pet.pos
	sim.ents[pet.id] = pet
	dono.aux["coletor_id"] = pet.id

## Um passo do pet: anda com o dono, vai até o drop mais perto que passa no filtro e o leva para a mochila do dono.
static func passo(sim: WorldSim, pet: Ent, dt: float) -> void:
	var dono: Ent = sim.ents.get(pet.dono)
	if dono == null or not dono.vivo or dono.tipo != "jogador": return
	if not pet.pronto(): return
	var d := pet.pos.distance_to(dono.pos)
	if d > SEGUE_MAX:
		pet.pos = sim.celula_livre_perto(dono.pos + Vector2(-1.2, 0.6)); pet.caminho.clear(); return
	var alvo := _proximo(sim, dono, pet)
	if not alvo.is_empty():
		if pet.pos.distance_to(alvo["pos"]) <= ALCANCE_PEGAR:
			_pegar(sim, dono, int(alvo["id"])); pet.caminho.clear()
		elif pet.caminho.is_empty():
			sim.ir_para(pet, alvo["pos"])
	elif d > SEGUE_DIST and pet.caminho.is_empty():
		sim.ir_para(pet, dono.pos + Vector2(-1.2, 0.6))
	if not pet.caminho.is_empty(): sim.mover_ao_longo(pet, dt)

## O drop mais perto do dono que o filtro deixa passar e que cabe na mochila (vazio se não há nenhum).
static func _proximo(sim: WorldSim, dono: Ent, pet: Ent) -> Dictionary:
	var f := filtro(dono)
	var dono_s := float(Defs.DROPS["regras"]["dono_do_drop_s"])
	var melhor := {}
	var dmin := 1e9
	for c: Dictionary in sim.chao.values():
		if c["pos"].distance_to(dono.pos) > RAIO_JUNTAR: continue
		if c["dono"] != dono.id and float(c["t"]) < dono_s: continue
		var it: Dictionary = c["item"]
		if not deve_pegar(it, f): continue
		if not _cabe(dono, it): continue
		var d: float = c["pos"].distance_to(pet.pos)
		if d < dmin: dmin = d; melhor = c
	return melhor

static func _cabe(dono: Ent, it: Dictionary) -> bool:
	if it["id"] == "_ouro": return true
	if Itens.pilha(it) > 1 and dono.inv.any(func(o): return o["id"] == it["id"]): return true
	return Itens.achar_lugar(dono.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it).x >= 0

static func _pegar(sim: WorldSim, dono: Ent, id: int) -> void:
	var c: Dictionary = sim.chao.get(id, {})
	if c.is_empty(): return
	var it: Dictionary = c["item"]
	sim.chao.erase(id)
	sim.emitir("chao_sumiu", {"id": id, "pego": true, "por": dono.id})
	sim.emitir_a(dono, "som_evento", {"ev": "moedas" if it["id"] == "_ouro" else "pegar"})
	Jogador.dar_item(sim, dono, it)

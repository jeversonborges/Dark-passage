class_name Coletor
## Pet coletor (0.9.6, Jefin 2026-10-18): um animal que anda com o dono e junta do chão os drops que o filtro deixa
## passar. Comprado com o vendedor de pets (Vigília e Arautos). Não ataca, não é alvo, não ganha XP e não solta nada.
## Espécies são os animais de assets/monstros que viram pet. A escolha e o filtro ficam em dono.aux["coletor"] (vão no save).

const ESPECIES := {
	"cao_de_vala": {"nome": "Cão de Vala", "preco": 4000},
	"corvo_de_cinza": {"nome": "Corvo de Cinza", "preco": 3000},
	"cervo_de_lume": {"nome": "Cervo de Lume", "preco": 8000},
	"serpente_do_eden": {"nome": "Serpente do Éden", "preco": 6000},
}
const RARIDADES := ["comum", "verde", "magico", "excelente", "raro", "laranja", "lendario"]   ## lendario é a Relíquia (vermelho)
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

## Configuração do dono: {"especie": id ou "", "filtro": {...}}. Cria o padrão na primeira vez.
static func cfg(dono: Ent) -> Dictionary:
	if not (dono.aux.get("coletor") is Dictionary): dono.aux["coletor"] = {"especie": "", "filtro": filtro_padrao()}
	return dono.aux["coletor"]

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
	e.ouro -= preco
	sim.emitir_a(e, "ouro", {"valor": -preco})
	sim.emitir_a(e, "som_evento", {"ev": "comprar"})
	cfg(e)["especie"] = esp
	_tirar(sim, e)
	garantir(sim, e)
	sim.emitir_a(e, "coletor", {})

## Manda o pet embora (o filtro fica salvo).
static func dispensar(sim: WorldSim, e: Ent) -> void:
	cfg(e)["especie"] = ""
	_tirar(sim, e)
	sim.emitir_a(e, "coletor", {})

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
	return Itens.cabe_inteiro(dono.inv, Itens.MOCHILA_W, Itens.MOCHILA_H, it)

static func _pegar(sim: WorldSim, dono: Ent, id: int) -> void:
	var c: Dictionary = sim.chao.get(id, {})
	if c.is_empty(): return
	var it: Dictionary = c["item"]
	sim.chao.erase(id)
	sim.emitir("chao_sumiu", {"id": id, "pego": true, "por": dono.id})
	sim.emitir_a(dono, "som_evento", {"ev": "moedas" if it["id"] == "_ouro" else "pegar"})
	Jogador.dar_item(sim, dono, it)

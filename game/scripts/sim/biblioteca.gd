class_name Biblioteca
## Os mistérios e a Biblioteca Soterrada, lado do servidor. Cada acontecimento vira um evento de texto para
## Selo.abrir. Quase sempre nada abre, e é para ser assim. O que abre aplica o payload no personagem.
## Nada aqui guarda resposta nenhuma: o conteúdo só existe selado em server_data/ e no cliente não há nada.

const CAMINHO := "res://server_data/misterios.srv.json"
const CHAVES := "user://biblioteca_chaves.json"
const DIST_FALA := 6.0
const DIST_GESTO := 2.0
const DIST_AGUA := 1.5
const DIST_ESTANTE := 3.0
const DADOS := "res://data/design/missoes/biblioteca.json"

static var _dados := {}

static func _bib() -> Dictionary:
	if _dados.is_empty():
		var d = Defs.ler(DADOS)
		_dados = d if d is Dictionary and not d.is_empty() else {"livros": {}, "estantes": {}, "drops": {}}
	return _dados

static var _selo: Selo = null
static var _tentou := false

static func _sel() -> Selo:
	if not _tentou:
		_tentou = true
		var s := Selo.new()
		if s.carregar(CAMINHO):
			_selo = s
			_carregar_chaves()
	return _selo

static func _carregar_chaves() -> void:
	if not FileAccess.file_exists(CHAVES): return
	var d = JSON.parse_string(FileAccess.get_file_as_string(CHAVES))
	if d is Dictionary: _selo.chaves = d

static func _gravar_chaves() -> void:
	var f := FileAccess.open(CHAVES, FileAccess.WRITE)
	if f: f.store_string(JSON.stringify(_selo.chaves))

# ------------------------------------------------------------------ entradas

## Fala no chat local: cada NPC e objeto interativo a até DIST_FALA tiles gera seus eventos de fala.
static func falar(sim: WorldSim, e: Ent, texto: String) -> void:
	if _sel() == null: return
	for alvo in sim.ents.values():
		if alvo.tipo != "npc" and not (alvo.tipo == "objeto" and alvo.kind == "interativo"): continue
		if alvo.pos.distance_to(e.pos) > DIST_FALA: continue
		var id := _id_de(alvo)
		for ev in Selo.eventos_de_fala(id, texto, e.nome):
			evento(sim, e, ev)

## Interagir com um objeto: o evento tocar, e o texto de inscrição ou livro vem do servidor.
static func tocar(sim: WorldSim, e: Ent, o: Ent) -> void:
	if _sel() == null: return
	evento(sim, e, "tocar|" + _id_de(o))
	var ts := texto_servidor_de(o)
	if ts != "": ler(sim, e, ts)

## Id do texto do servidor de um objeto (no mapa ou na definição), "" se não tiver.
static func texto_servidor_de(o: Ent) -> String:
	if o.aux.has("texto_servidor"): return str(o.aux["texto_servidor"])
	if o.tipo == "objeto" and o.kind == "interativo":
		return str(Defs.OBJETOS.get(str(o.aux.get("obj", "")), {}).get("texto_servidor", ""))
	return ""

## Usar um item: o evento usar, com subzona e se o jogador está perto de água.
static func usar(sim: WorldSim, e: Ent, item_id: String, agua := false) -> void:
	if _sel() == null: return
	agua = agua or perto_de_agua(sim, e.pos)
	var sub := sim.zona_em(e.pos)
	evento(sim, e, "usar|%s|%s%s" % [item_id, sub, "|agua" if agua else ""])

## Há um tile de água (piso de água, rio ou brejo) a até DIST_AGUA tiles do ponto?
static func perto_de_agua(sim: WorldSim, p: Vector2) -> bool:
	var ter: Array = sim.mapa.get("terreno", [])
	var pisos: Dictionary = sim.mapa.get("pisos", {})
	if ter.is_empty(): return false
	var r := int(ceil(DIST_AGUA))
	for dy in range(-r, r + 1):
		for dx in range(-r, r + 1):
			var c := Vector2i(floori(p.x) + dx, floori(p.y) + dy)
			if c.y < 0 or c.y >= ter.size() or c.x < 0 or c.x >= (ter[c.y] as String).length(): continue
			if p.distance_to(Vector2(c.x + 0.5, c.y + 0.5)) > DIST_AGUA + 0.5: continue
			var nome := str(pisos.get((ter[c.y] as String)[c.x], ""))
			if nome.contains("agua") or nome.contains("rio") or nome.contains("brejo"): return true
	return false

## Gesto (/ajoelhar): emite o evento com o objeto mais perto a até DIST_GESTO tiles (interativo tem preferência),
## ou "-" sem objeto. O personagem ajoelha para quem estiver vendo.
static func gesto(sim: WorldSim, e: Ent, nome: String) -> void:
	if not e.vivo: return
	sim.emitir("gesto", {"id": e.id, "gesto": nome})
	if _sel() == null: return
	var alvo := "-"; var melhor := INF
	for o in sim.ents.values():
		if o.tipo != "objeto" and o.tipo != "npc": continue
		var d: float = o.pos.distance_to(e.pos)
		if d > DIST_GESTO: continue
		if o.tipo == "objeto" and o.kind == "interativo": d -= 10.0      # interativo ganha de baú e portal
		if d < melhor: melhor = d; alvo = _id_de(o)
	evento(sim, e, "gesto|%s|%s" % [nome, alvo])

## Lê um texto guardado no servidor. Confere que o personagem tem o texto por perto ou na mão, aqui
## a conferência é feita pelo chamador (tocar ou usar). Marca leu_<id> e deixa a leitura na Estante.
static func ler(sim: WorldSim, e: Ent, tid: String) -> void:
	var t = _texto(tid)
	if not (t is Dictionary): return
	e.flags["leu_" + tid] = true
	e.flags["estante_" + tid] = true
	sim.emitir_a(e, "texto", {"titulo": str(t.get("titulo", "")), "texto": _corpo(t), "id": tid})
	evento(sim, e, "ler|" + tid)

## Texto de um livro aberto (biblioteca.json) ou do servidor (selado). null se não existir.
static func _texto(tid: String):
	var l = _bib().get("livros", {}).get(tid, null)
	if l is Dictionary: return l
	var s := _sel()
	var t = s.texto(tid) if s != null else null
	if t is Dictionary or t == null: return t
	# texto do servidor é um texto corrido: a 1ª linha é o título; numa linha só (pedra, trono), o título é o nome do objeto
	var linhas := str(t).split("\n")
	if linhas.size() > 1: return {"titulo": linhas[0].strip_edges(), "texto": "\n".join(linhas.slice(1)).strip_edges()}
	var nome := "Inscrição"
	for oid in Defs.OBJETOS:
		var d: Dictionary = Defs.OBJETOS[oid]
		if oid == tid or str(d.get("texto_servidor", "")) == tid: nome = str(d.get("nome", nome)); break
	return {"titulo": nome, "texto": str(t)}

static func _corpo(t: Dictionary) -> String:
	var c := str(t.get("texto", ""))
	var assina := ", ".join(PackedStringArray([str(t.get("autor", "")), str(t.get("data", ""))].filter(func(x): return x != "")))
	return c + ("\n\n[i]%s[/i]" % assina if assina != "" and not c.contains(str(t.get("autor", "@@"))) else "")

static func _titulo(tid: String) -> String:
	var t = _texto(tid)
	return str(t.get("titulo", tid)) if t is Dictionary else ""

# ------------------------------------------------------------------ Estante

## Objeto "abre": "estante": mostra o que aquela estante oferece (marca o que o personagem já leu).
static func abrir_estante(sim: WorldSim, e: Ent, o: Ent) -> void:
	var lista: Array = _bib().get("estantes", {}).get(_id_de(o), [])
	var livros := []
	for tid in lista:
		var tit := _titulo(str(tid))
		if tit != "": livros.append({"id": str(tid), "titulo": tit, "lido": e.flags.has("leu_" + str(tid))})
	sim.emitir_a(e, "estante", {"modo": "estante", "nome": o.nome, "livros": livros})

## Aba "Biblioteca" do diário: tudo o que o personagem já leu (flags estante_<id>), para reler.
static func estante_pessoal(sim: WorldSim, e: Ent) -> void:
	var livros := []
	for f in e.flags:
		var k := str(f)
		if not k.begins_with("estante_"): continue
		var tid := k.substr(8)
		var tit := _titulo(tid)
		if tit != "": livros.append({"id": tid, "titulo": tit, "lido": true})
	livros.sort_custom(func(a, b): return a["titulo"] < b["titulo"])
	sim.emitir_a(e, "estante", {"modo": "diario", "livros": livros})

## Pedido de leitura do cliente: só lê o que já está na Estante do personagem, ou o que uma estante perto oferece.
static func pedido_ler(sim: WorldSim, e: Ent, tid: String) -> void:
	if tid.length() > 64: return
	var pode: bool = e.flags.has("estante_" + tid)
	if not pode:
		var est: Dictionary = _bib().get("estantes", {})
		for o in sim.ents.values():
			if o.tipo == "objeto" and o.kind == "interativo" and o.pos.distance_to(e.pos) <= DIST_ESTANTE \
					and tid in est.get(_id_de(o), []):
				pode = true; break
	if pode: ler(sim, e, tid)

# ------------------------------------------------------------------ título, aura e falas guardadas

## Ao carregar o personagem: título e aura voltam do que ficou guardado nas flags.
static func restaurar(e: Ent) -> void:
	if e.flags.has("bib_titulo"): e.aux["titulo"] = str(e.flags["bib_titulo"])
	if e.flags.has("bib_aura"): e.aux["aura"] = str(e.flags["bib_aura"])

## Primeira fala de um NPC para quem já ganhou uma fala guardada (fala_npc_extra). "" se não tiver.
static func fala_guardada(e: Ent, npc_id: String) -> String:
	return str(e.flags.get("fala_npc:" + npc_id, ""))

## Guarda a hora da última vez que o jogador viu um nó de diálogo (janela do requer).
static func visitar(sim: WorldSim, e: Ent, dlg: String, no: String) -> void:
	if not e.aux.has("dlg_visto"): e.aux["dlg_visto"] = {}
	e.aux["dlg_visto"][dlg + ":" + no] = sim.tempo

# ------------------------------------------------------------------ eventos

static func evento(sim: WorldSim, e: Ent, ev: String) -> void:
	var s := _sel()
	if s == null: return
	var feitos := {}
	for p in s.abrir(ev):
		var m := str(p.get("misterio", ""))
		if feitos.has(m): continue
		if not _requer(sim, e, p.get("requer", {})):
			if p.has("senao"):
				_aplicar(sim, e, p["senao"]); feitos[m] = true
			continue
		if p.get("uma_vez", false):
			# a chave junta o mistério e as ações: variações da mesma resposta rendem uma vez só, e etapas
			# diferentes do mesmo mistério (ações diferentes) continuam valendo
			var chave := "bib_feito:%s:%d" % [m, hash(JSON.stringify(p.get("acoes", [])))]
			if e.flags.has(chave): continue
			e.flags[chave] = true
		feitos[m] = true
		_aplicar(sim, e, p)

static func _aplicar(sim: WorldSim, e: Ent, p: Dictionary) -> void:
	_acoes(sim, e, p.get("acoes", []))
	var dep = p.get("depois", null)
	if dep is Dictionary and _flags_batem(e, dep.get("se", {})):
		_acoes(sim, e, dep.get("acoes", []))

static func _flags_batem(e: Ent, se: Dictionary) -> bool:
	for f in se.get("flags", []):
		if not e.flags.has(str(f)): return false
	return true

static func _requer(sim: WorldSim, e: Ent, r: Dictionary) -> bool:
	if not _flags_batem(e, r): return false
	for f in r.get("sem_flags", []):
		if e.flags.has(str(f)): return false
	var itens = r.get("itens", [])
	if itens is Dictionary:
		for id in itens:
			if Itens.contar(e.inv, str(id)) < int(itens[id]): return false
	else:
		for id in itens:
			if Itens.contar(e.inv, str(id)) < 1: return false
	var est: Dictionary = r.get("estado", {})
	for id in est:
		if int(e.flags.get("estado:" + str(id), 0)) != int(est[id]): return false
	var mc = r.get("missao_concluida", [])
	if not (mc is Array): mc = [mc]
	for mid in mc:
		if Missoes.estado(e, str(mid)) != "concluida": return false
	if r.has("janela"):
		var j: Dictionary = r["janela"]
		var visto: Dictionary = e.aux.get("dlg_visto", {})
		var quando = visto.get(str(j.get("dialogo", "")), null)
		if quando == null or sim.tempo - float(quando) > float(j.get("s", 0)): return false
	return true

## Páginas soltas dos diários: cada uma cai no máximo uma vez por personagem, e quem já leu não ganha de novo.
static func cair_pagina(sim: WorldSim, e: Ent, morto: Ent) -> void:
	if _sel() == null: return
	var lista: Array = Defs.ler("res://data/design/missoes/biblioteca.json").get("drops", {}).get("paginas_soltas", [])
	var area := "sao_lazaro" if sim.mapa_id.begins_with("area") else ("a_torre" if sim.mapa_id.begins_with("torre") else "")
	for p in lista:
		if p["area"] != area or (p["monstro"] != "*" and p["monstro"] != morto.kind): continue
		var tid := str(p["texto"])
		if e.flags.has("pagina:" + tid) or e.flags.has("leu_" + tid): continue
		if sim.rng.randf() >= float(p["chance"]): continue
		e.flags["pagina:" + tid] = true
		_dar(sim, e, {"id": "pagina_solta", "texto_id": tid})
		return   # no máximo uma página por abate

static func _acoes(sim: WorldSim, e: Ent, lista) -> void:
	if not (lista is Array): return
	for a in lista:
		if not (a is Dictionary): continue
		for k in a:
			var v = a[k]
			match k:
				"dar_item": _dar(sim, e, v)
				"tirar_item":
					var id := str(v.get("id", "")) if v is Dictionary else str(v)
					var qtd := int(v.get("qtd", 1)) if v is Dictionary else 1
					Itens.remover(e.inv, id, qtd)
				"flag": e.flags[str(v)] = true
				"estado":
					if v is Array and v.size() == 2: e.flags["estado:" + str(v[0])] = int(v[1])
				"texto":
					var titulo := ""; var corpo := str(v)
					if v is Dictionary: titulo = str(v.get("titulo", "")); corpo = str(v.get("texto", ""))
					sim.emitir_a(e, "texto", {"titulo": titulo, "texto": corpo})
				"texto_extra":
					if v is Dictionary:
						var t = _sel().texto(str(v.get("texto_id", "")))
						if t is Dictionary:
							sim.emitir_a(e, "texto", {"titulo": str(t.get("titulo", "")), "texto": str(t.get("texto", "")) + "\n\n" + str(v.get("texto", ""))})
				"fala":
					if v is Dictionary: _fala_de(sim, str(v.get("npc", "")), str(v.get("texto", "")))
				"fala_npc_extra":
					if v is Dictionary:
						e.flags["fala_npc:" + str(v.get("npc", ""))] = str(v.get("texto", ""))
						sim.emitir_a(e, "fala", {"id": _id_npc(sim, str(v.get("npc", ""))), "texto": str(v.get("texto", "")), "chat": false})
				"chave":
					if v is Dictionary:
						for nome in v: _sel().chaves[str(nome)] = str(v[nome])
						_gravar_chaves()
				"teleporte":
					if v is Dictionary: _teleporte(sim, e, str(v.get("mapa", "")), str(v.get("ponto", "")))
				"titulo":
					e.flags["bib_titulo"] = str(v); e.aux["titulo"] = str(v)
					sim.emitir_a(e, "aviso", {"texto": "Título: " + str(v)})
				"aura":
					e.flags["bib_aura"] = str(v); e.aux["aura"] = str(v)
				"anuncio":
					var txt := str(v.get("texto", "")) if v is Dictionary else str(v)
					txt = txt.replace("{nome}", e.nome)
					if txt != "": sim.emitir("chat", {"id": e.id, "nome": "", "classe": "", "texto": txt, "canal": "sistema", "para": "", "anuncio": true, "pos": e.pos})
				"efeito":
					sim.emitir("efeito_bib", {"id": e.id, "fx": str(v)})
				"som":
					sim.emitir_a(e, "som_evento", {"ev": str(v)})

static func _dar(sim: WorldSim, e: Ent, v) -> void:
	var id := ""
	if v is Dictionary:
		id = str(v.get("id", ""))
		if not Defs.ITENS.has(id): Defs.ITENS[id] = v.duplicate()
	else:
		id = str(v)
	if id == "" or not Defs.ITENS.has(id): return
	var it := Itens.novo(id, int(v.get("qtd", 1)) if v is Dictionary else 1)
	if v is Dictionary and v.has("texto_id"): it["texto_id"] = str(v["texto_id"])
	Jogador.dar_item(sim, e, it)

static func _fala_de(sim: WorldSim, npc: String, txt: String) -> void:
	for x in sim.ents.values():
		if _id_de(x) == npc and (x.tipo == "npc" or x.tipo == "objeto"):
			sim.emitir("fala", {"id": x.id, "texto": txt, "chat": true}); return

static func _id_npc(sim: WorldSim, npc: String) -> int:
	for x in sim.ents.values():
		if _id_de(x) == npc and x.tipo == "npc": return x.id
	return -1

static func _teleporte(sim: WorldSim, e: Ent, mapa: String, ponto: String) -> void:
	var lugares: Dictionary = Defs.ler("res://data/mapas/%s.json" % mapa).get("lugares", {}) if ResourceLoader.exists("res://data/mapas/%s.json" % mapa) else {}
	var p = lugares.get(ponto, [])
	Jogador._portal_para(sim, e, mapa, p if p is Array else [])

static func _id_de(x: Ent) -> String:
	return str(x.aux.get("obj", x.aux.get("id", x.kind)))

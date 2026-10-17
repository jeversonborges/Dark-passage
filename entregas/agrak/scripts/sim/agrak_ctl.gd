class_name AgrakCtl
extends ChefeCtl
## O Agrak, o Grande Coliseu (evento PvP): etapas, apresentação ao vivo e as feras.
## Roteiro: design/pvp/agrak/apresentacao.md. Números: design/pvp/agrak/dados.json (data/design/pvp/agrak.json).
## O world_sim cria este controlador no lugar do ChefeCtl quando o mapa tem o bloco "agrak"; os ganchos do
## world_sim (passo, ao_morrer_ent, ao_quebrar, jogador_morreu, porta_fechada) chegam aqui sem mudar nada lá.
## Nenhum jogador perde o controle da tela: na Chamada eles só ficam presos no Círculo de Ferro.

const ARQ := "res://data/design/pvp/agrak.json"
const NOMES_ETAPA := {"chamada": "A Chamada", "luta_leoes": "Os Leões", "respiro": "Respiro", "luta_gigante": "O Gigante",
	"ultimo_de_pe": "Último de Pé", "coroacao": "Coroação"}
const NOME_CLASSE := {"anjo": "ANJO", "cultista": "CULTISTA", "demonio": "DEMÔNIO", "humano": "HUMANO", "mutante": "MUTANTE",
	"tecnomancer": "TECNOMANCER", "warlord": "WARLORD"}
const DA_FACCAO := {"vigilia": "DA VIGÍLIA", "arautos": "DOS ARAUTOS"}
## Abel debocha de cada gladiador pela classe (uma linha sorteada; a semente do mundo decide).
const DEBOCHE := {
	"anjo": ["Asa bonita. Vai ficar ótima no tapete da sala.", "Veio rezar ou veio apanhar? Aqui as duas coisas doem."],
	"cultista": ["Esse sangra de propósito. Economiza o serviço dos leões.", "Paga a entrada com o próprio sangue. Gostei."],
	"demonio": ["Mais um da Legião. O general sumiu e sobrou isso.", "Chifre grande, juízo pequeno."],
	"humano": ["Chapéu de vaqueiro no fim do mundo. Coragem ou falta de espelho?", "Escopeta serrada. A plateia adora barulho."],
	"mutante": ["Esse aí já nasceu meio leão. Vai ser briga de família.", "Grande, feio e com cheiro. Vai longe."],
	"tecnomancer": ["Trouxe as torrezinhas. Que fofo.", "Se der errado ele culpa a fiação."],
	"warlord": ["Mercenário. Luta por quem pagar mais. Hoje paga a plateia.", "Nem Vigília nem Arauto. Só fome."],
}

static var _dados := {}

var A := {}                  # bloco "agrak" do mapa (centro, portões, camarote...)
var E := {}                  # dados.json: evento
var etapas: Array = []
var etapa_i := -1
var etapa := ""
var etapa_t := 0.0           # tempo dentro da etapa
var etapa_dur := 0.0
var gladiadores: Array = []  # ids, na ordem da inscrição
var eliminados: Array = []   # ids que caíram (viram espectadores)
var espectadores: Array = [] # ids já levantados no camarote
var xp_entrada := {}         # id -> xp ao entrar (morrer aqui não custa nada)
var feras: Array = []        # Fera (um ChefeCtl por leão ou pelo Golias)
var roteiro: Array = []      # [tempo da etapa, Callable] da apresentação
var vencedor := -1
var anel := {}               # Anel do Amargo: {t, raio, tick}
var caim := -1               # id do NPC Caim e Abel
var saulo := -1
var portoes := {}            # id -> aberto
var t_aviso := 0.0
var feras_vivas := 0
var fim_t := -1.0

static func dados() -> Dictionary:
	if _dados.is_empty(): _dados = Defs.ler(ARQ)
	return _dados

## Põe os leões e o Golias em Defs.CHEFES no formato do chefes.json (fases, fúria, efeitos que o jogo conhece).
static func preparar_chefes() -> void:
	var ch: Dictionary = dados().get("chefes", {})
	for k in ch:
		if Defs.CHEFES.has(k): continue
		var c: Dictionary = ch[k].duplicate(true)
		if not c.has("fases"):
			c["fases"] = [{"n": 1, "hp": [1.0, 0.0], "ataques": c.get("ataques", [])}]
		var base: Array = c["fases"][0]["ataques"]
		for f in c["fases"]:
			if not f.has("ataques"):   # fase 2 do Golias: os mesmos golpes com as "mudancas"
				var lista: Array = []
				var mud: Dictionary = f.get("mudancas", {})
				for a in base:
					var m: Dictionary = a.duplicate(true)
					if mud.has(a["id"]):
						for kk in mud[a["id"]]:
							if m.get(kk) is Dictionary and mud[a["id"]][kk] is Dictionary: m[kk].merge(mud[a["id"]][kk], true)
							else: m[kk] = mud[a["id"]][kk]
					lista.append(m)
				f["ataques"] = lista
			for a in f["ataques"]:
				var ef: Dictionary = a.get("efeito", {})
				if ef.has("medo"): ef["atordoado"] = ef["medo"]; ef.erase("medo")   # o medo do Rugido é um atordoar curto
				if a.has("derruba"): ef["derrubado"] = float(a["derruba"])
				if not ef.is_empty(): a["efeito"] = ef
		c["furia_tempo_s"] = float(c.get("furia_tempo_s", 9999))
		Defs.CHEFES[k] = c

static func _cfg_base(p_sim: WorldSim) -> Dictionary:
	preparar_chefes()
	var a: Dictionary = p_sim.mapa.get("agrak", {})
	var c: Array = a.get("centro", [28, 23])
	return {"id": "golias", "pos": c, "arena": {"centro": c, "raio": float(a.get("anel_raio_max", 13)) + 2.0}, "derrotado": true}

func _init(p_sim: WorldSim) -> void:
	super(p_sim, _cfg_base(p_sim))
	estado = "dormindo"
	A = sim.mapa.get("agrak", {})
	E = dados().get("evento", {})
	etapas = E.get("etapas", [])
	for id in A.get("portoes", {}):
		portoes[id] = false
		sim.definir_bloqueio(A["portoes"][id]["celulas"], 1)
	for e: Ent in sim.ents.values():
		if e.tipo == "npc" and e.kind == "caim_abel": caim = e.id
		if e.tipo == "npc" and e.kind == "saulo": saulo = e.id
	# solo / teste: `agrak=agora` começa assim que o primeiro jogador entra
	for x in OS.get_cmdline_user_args():
		if x == "agrak=agora": esp["auto"] = true

# =================================================================== começo (o servidor chama com os inscritos já no mapa)
func comecar(ids: Array) -> void:
	if etapa_i >= 0: return
	gladiadores.clear()
	var cen := _centro()
	var n := ids.size()
	for i in n:
		var e: Ent = sim.ents.get(int(ids[i]))
		if e == null or e.tipo != "jogador": continue
		gladiadores.append(e.id)
		xp_entrada[e.id] = e.xp
		e.lado_forcado = ""
		e.vivo = true; e.hp = e.hp_max
		var ang := TAU * i / maxf(1.0, n) - PI * 0.5
		e.pos = sim.celula_livre_perto(cen + Vector2(cos(ang), sin(ang)) * minf(2.4, float(A.get("raio_circulo", 3.5)) - 0.6))
		e.caminho.clear(); e.acao = {}; e.alvo = -1
		e.facing = (cen - e.pos).normalized() if cen != e.pos else Vector2.DOWN
		sim.emitir("teleporte", {"id": e.id, "pos": e.pos})
	if gladiadores.is_empty(): return
	estado = "luta"
	_etapa(0)

func porta_fechada() -> bool:
	return etapa_i >= 0 and fim_t < 0.0

# =================================================================== passo
func passo(dt: float) -> void:
	if etapa_i < 0:
		if esp.get("auto", false) and not sim.jogadores().is_empty():
			var ids: Array = []
			for j: Ent in sim.jogadores(): ids.append(j.id)
			comecar(ids)
		return
	if fim_t >= 0.0:
		fim_t -= dt
		if fim_t <= 0.0: _devolver_todos()
		return
	etapa_t += dt
	while not roteiro.is_empty() and etapa_t >= float(roteiro[0][0]):
		var r: Array = roteiro.pop_front()
		(r[1] as Callable).call()
	_vigiar_gladiadores(dt)
	for f in feras: f.passo(dt)
	match etapa:
		"chamada": _prender()
		"luta_leoes", "luta_gigante":
			if _vivos().is_empty(): _sem_vencedor(); return
			if feras_vivas <= 0 and esp.get("feras_soltas", false): _proxima(); return
			if esp.get("luta_t", -1.0) >= 0.0:
				esp["luta_t"] += dt
				if esp["luta_t"] >= etapa_dur: _feras_recuam(); return
		"ultimo_de_pe":
			_passo_final(dt)
			return
	if etapa_dur > 0.0 and etapa_t >= etapa_dur and etapa in ["chamada", "respiro", "coroacao"]:
		_proxima()

func _centro() -> Vector2:
	var c: Array = A.get("centro", [28, 23])
	return Vector2(c[0], c[1])

func _vivos() -> Array:
	var out: Array = []
	for id in gladiadores:
		var e: Ent = sim.ents.get(id)
		if e != null and e.vivo and not id in eliminados: out.append(e)
	return out

## Dentro do fosso (o Camarote dos Derrotados e o corredor ficam fora).
func _no_fosso(p: Vector2) -> bool:
	var f: Array = A.get("fosso", [13, 12, 42, 33])
	return p.x >= f[0] and p.y >= f[1] and p.x <= f[2] + 1 and p.y <= f[3] + 1

# =================================================================== etapas
func _etapa(i: int) -> void:
	etapa_i = i
	var d: Dictionary = etapas[i]
	etapa = d["id"]
	etapa_t = 0.0
	etapa_dur = float(d.get("dur", d.get("dur_max", 0)))
	roteiro.clear()
	esp.erase("luta_t"); esp.erase("feras_soltas")
	_emitir_etapa()
	match etapa:
		"chamada": _chamada()
		"luta_leoes": _luta_leoes()
		"respiro": _respiro(d)
		"luta_gigante": _luta_gigante()
		"ultimo_de_pe": _ultimo_de_pe(d)
		"coroacao": _coroacao()

func _proxima() -> void:
	var vivos := _vivos()
	if etapa in ["luta_leoes", "luta_gigante"] and vivos.is_empty(): _sem_vencedor(); return
	# um só de pé depois do Golias: ganha sem a luta final
	if etapa == "luta_gigante" and vivos.size() == 1:
		vencedor = vivos[0].id
		_etapa(etapas.size() - 1); return
	if etapa_i + 1 >= etapas.size(): _encerrar(); return
	var prox: Dictionary = etapas[etapa_i + 1]
	if prox["id"] == "ultimo_de_pe" and vivos.size() <= 1:
		vencedor = vivos[0].id if vivos.size() == 1 else -1
		_etapa(etapas.size() - 1); return
	_etapa(etapa_i + 1)

func _emitir_etapa() -> void:
	sim.emitir("agrak_etapa", {"etapa": etapa, "nome": NOMES_ETAPA.get(etapa, etapa), "dur": etapa_dur, "t": etapa_t,
		"restam": _vivos().size(), "total": gladiadores.size(), "pvp": etapa == "ultimo_de_pe"})

func _em(t: float, f: Callable) -> void:
	roteiro.append([t, f])
	roteiro.sort_custom(func(a, b): return float(a[0]) < float(b[0]))

# ------------------------------------------------------------------- falas, plateia e portões
## quem: "caim" (berra) ou "abel" (debocha). anim: anunciar | discutir | rir (folhas do caim_abel).
func _fala(quem: String, texto: String, anim := "") -> void:
	sim.emitir("agrak_fala", {"quem": quem, "texto": texto, "id": caim})
	if caim >= 0:
		sim.emitir("fala", {"id": caim, "texto": texto, "cor": "#ffcf7a" if quem == "caim" else "#d8cbb0"})
		if anim != "": sim.emitir("anim", {"id": caim, "anim": anim, "dur": 2.4})

## r: vibrar | urro | coro | vaia | golias | bracos
func _plateia(r: String, texto := "") -> void:
	sim.emitir("agrak_plateia", {"r": r, "texto": texto})

func _portao(id: String, aberto: bool) -> void:
	if not A.get("portoes", {}).has(id) or portoes.get(id, false) == aberto: return
	portoes[id] = aberto
	sim.definir_bloqueio(A["portoes"][id]["celulas"], 0 if aberto else 1)
	sim.emitir("agrak_portao", {"portao": id, "aberto": aberto})

func _nome(e: Ent) -> String:
	return str(e.nome).to_upper()

func _classe(e: Ent) -> String:
	if e.evolucao != "":
		var n: String = str(Evolucao.defn(e.evolucao).get("nome", ""))
		if n != "": return n.to_upper()
	return NOME_CLASSE.get(e.classe, str(e.classe).to_upper())

# ------------------------------------------------------------------- A Chamada (45 s)
func _chamada() -> void:
	_plateia("vibrar")
	sim.emitir("agrak_musica", {"m": "chamada"})
	_em(2.0, func(): _fala("caim", "SENHORAS, SENHORES E COISAS QUE UM DIA FORAM GENTE! BEM-VINDOS AO AGRAK!", "anunciar"))
	_em(6.0, func(): _fala("abel", "Ele ensaiou isso a semana toda.", "discutir"))
	_em(9.0, func(): _plateia("coro", "A-GRAAAK!"))
	# um gladiador por vez (no máximo 8 chamadas; acima disso, em grupos)
	var lista: Array = gladiadores.duplicate()
	var por := ceili(lista.size() / 8.0)
	var grupos: Array = []
	for i in range(0, lista.size(), por): grupos.append(lista.slice(i, i + por))
	var passo_t := minf(3.0, 24.0 / maxf(1.0, grupos.size()))
	for gi in grupos.size():
		var g: Array = grupos[gi]
		var t0 := 11.0 + gi * passo_t
		_em(t0, func(): _apresentar(g))
		if gi % 2 == 0 or grupos.size() <= 4:
			_em(t0 + passo_t * 0.55, func(): _debochar(g))
	_em(36.0, func(): _fala("abel", "Aposto dois dentes que não passa dos leões.", "rir"))
	_em(38.0, func():
		_fala("caim", "SOLTEM OS LEÕES!", "anunciar")
		_portao("portao_leoes", true)
		sim.emitir("agrak_som", {"som": "agrak/grade_sobe", "pos": _pos_portao("portao_leoes")})
		_criar_leoes())
	var ordem := ["leao_dalila", "leao_nabucodonosor", "leao_sansao"]   # Sansão sai por último
	for k in 3:
		var kind: String = ordem[k]
		_em(39.0 + k * 1.4, func(): _soltar_fera(kind))
	_em(43.0, func(): _fala("abel", "Eles não comem desde a última trombeta. Nem eu.", "discutir"))

func _apresentar(g: Array) -> void:
	var nomes: Array = []
	var cartoes: Array = []
	var faccoes := {}
	for id in g:
		var e: Ent = sim.ents.get(id)
		if e == null: continue
		nomes.append(_nome(e))
		faccoes[e.faccao] = true
		cartoes.append({"id": e.id, "nome": e.nome, "classe": _classe(e), "faccao": e.faccao, "nivel": e.nivel})
	if cartoes.is_empty(): return
	var txt := ""
	if cartoes.size() == 1:
		var e1: Ent = sim.ents.get(g[0])
		txt = "%s, UM %s: %s!" % [DA_FACCAO.get(e1.faccao, "DE LUGAR NENHUM"), _classe(e1), _nome(e1)]
	else:
		var f := " E ".join(faccoes.keys().map(func(x): return DA_FACCAO.get(x, "DE LUGAR NENHUM")))
		txt = "%s: %s E %s!" % [f, ", ".join(nomes.slice(0, nomes.size() - 1)), nomes[nomes.size() - 1]]
	_fala("caim", txt, "anunciar")
	sim.emitir("agrak_gladiador", {"cartoes": cartoes})
	_plateia("urro")

func _debochar(g: Array) -> void:
	var e: Ent = sim.ents.get(g[0]) if not g.is_empty() else null
	if e == null: return
	var linhas: Array = DEBOCHE.get(e.classe, DEBOCHE["warlord"])
	_fala("abel", linhas[(e.id + gladiadores.size()) % linhas.size()], "discutir")

func _pos_portao(id: String) -> Vector2:
	var cs: Array = A.get("portoes", {}).get(id, {}).get("celulas", [[0, 0]])
	var s := Vector2.ZERO
	for c in cs: s += Vector2(c[0] + 0.5, c[1] + 0.5)
	return s / maxf(1.0, cs.size())

## Prende os gladiadores vivos no Círculo de Ferro (grade invisível): quem sai volta para a borda.
func _prender() -> void:
	var cen := _centro()
	var r := float(A.get("raio_circulo", 3.5))
	for e: Ent in _vivos():
		var d := e.pos.distance_to(cen)
		if d > r:
			e.pos = cen + (e.pos - cen) / d * (r - 0.15)
			e.caminho.clear()
			if not e.deslocando.is_empty(): e.deslocando = {}
			if not e.aux.get("agrak_avisou", false):
				e.aux["agrak_avisou"] = true
				sim.emitir_a(e, "aviso", {"texto": "A grade invisível do Círculo de Ferro não deixa sair antes da luta."})

# ------------------------------------------------------------------- feras
func _criar_leoes() -> void:
	var pts: Array = A.get("chefes_nascem", {}).get("portao_leoes", [[7, 21], [7, 23], [7, 25]])
	var ordem := ["leao_dalila", "leao_nabucodonosor", "leao_sansao"]
	for k in 3: _criar_fera(ordem[k], Vector2(pts[k % pts.size()][0], pts[k % pts.size()][1]))
	feras_vivas = feras.size()

func _criar_fera(kind: String, p: Vector2) -> Fera:
	var f := Fera.new(sim, {"id": kind, "pos": [p.x, p.y], "arena": {"centro": [_centro().x, _centro().y], "raio": 40.0}})
	f.arena = self
	var esc: Dictionary = dados().get("escala_por_jogadores", {})
	var por := float(esc.get("golias" if kind == "golias" else "leoes", {}).get("hp_por_jogador", 0))
	f.boss.hp_max = float(f.d["hp"]) + por * maxi(1, _vivos().size())
	f.boss.hp = f.boss.hp_max
	f.boss.aux["imune"] = true          # até a luta começar ninguém acerta (nem de longe)
	f.boss.raio = float(f.d.get("raio", 0.75 if kind != "leao_sansao" else 0.85))
	if kind == "golias": f.boss.raio = 1.1
	feras.append(f)
	return f

## Leão sai da jaula correndo até perto do círculo e ruge.
func _soltar_fera(kind: String) -> void:
	for f in feras:
		if f.boss.kind != kind: continue
		var cen := _centro()
		var gate := _pos_portao("portao_leoes")
		var lado := (cen - gate).normalized()
		var i := ["leao_dalila", "leao_nabucodonosor", "leao_sansao"].find(kind)
		var alvo := cen - lado * 6.0 + lado.orthogonal() * (i - 1) * 2.6
		f.correr(sim.celula_livre_perto(alvo), 2.4, "run")
		_plateia("urro")
		sim.emitir("agrak_som", {"som": "agrak/rugido_" + kind.trim_prefix("leao_"), "pos": f.boss.pos})

func _luta_leoes() -> void:
	sim.emitir("agrak_musica", {"m": "luta"})
	_plateia("urro")
	esp["feras_soltas"] = true
	esp["luta_t"] = 0.0
	for f in feras: f.acordar()

func fera_caiu(f: Fera, killer: Ent) -> void:
	feras_vivas -= 1
	_plateia("urro")
	if f.boss.kind.begins_with("leao"):
		for o in feras:   # o bando se vinga
			if o != f and o.boss.vivo:
				o.boss.dano_min *= 1.15; o.boss.dano_max *= 1.15; o.boss.vel *= 1.1
				sim.emitir("chefe_buff", {"id": o.boss.id, "fome": 1})
				sim.emitir("anim", {"id": o.boss.id, "anim": "roar", "dur": 1.2})
		if feras_vivas > 0:
			_fala("caim", "UM GATINHO A MENOS!", "anunciar")
			_em(etapa_t + 2.2, func(): _fala("abel", "Era o meu favorito. Anota o nome desse aí.", "discutir"))
	else:
		_fala("caim", "DERRUBARAM O GIGANTE!", "anunciar")
		_em(etapa_t + 2.4, func(): _fala("abel", "Agora a parte que a plateia pagou pra ver: um contra o outro.", "rir"))
	if killer != null: killer.flags["venceu_" + f.boss.kind] = true

## Tempo esgotado: as feras voltam para a jaula, todos os vivos passam, a plateia vaia.
func _feras_recuam() -> void:
	_plateia("vaia")
	_fala("abel", "Tempo! As feras ganharam folga e vocês ganharam vaia.", "rir")
	for f in feras:
		if f.boss.vivo:
			f.estado = "morto"
			sim.cancelar_acao(f.boss)
			sim.emitir("vfx", {"nome": "chefe_portal", "pos": f.boss.pos})
			sim.remover(f.boss.id)
			if f.boss.kind == "golias": sim.emitir("chefe", {"id": f.boss.id, "fim": true})
	feras_vivas = 0
	_limpar_feras()
	_proxima()

func _limpar_feras() -> void:
	for t in sim.telegrafos.duplicate():
		for f in feras:
			if t["dono"] == f.boss.id: sim.remover_telegrafo(t["id"])
	for f in feras: f.parar_giro()
	feras.clear()
	_portao("portao_leoes", false); _portao("portao_gigante", false)

# ------------------------------------------------------------------- respiro
func _respiro(d: Dictionary) -> void:
	_limpar_feras()
	var k := float(d.get("recupera_frac", 0.5))
	for e: Ent in _vivos():
		sim.curar(e, e.hp_max * k, null)
		e.rec = minf(e.rec_max, e.rec + e.rec_max * k)
	_plateia("bracos")
	sim.emitir("agrak_musica", {"m": "respiro"})
	sim.emitir("agrak_fx", {"fx": "coisas_na_areia", "pos": _centro()})
	if etapa_i + 1 < etapas.size() and etapas[etapa_i + 1]["id"] == "ultimo_de_pe":
		_em(1.5, func(): _fala("caim", "AGORA, UM CONTRA O OUTRO!", "anunciar"))
		_em(5.0, func(): _fala("abel", "A Trégua da Areia vale até agora. Depois, cada um por si.", "discutir"))
	else:
		_em(1.5, func(): _fala("caim", "RESPIREM, CARNES! O PIOR AINDA VEM!", "anunciar"))
		_em(5.5, func(): _fala("abel", "O Saulo cobra barato pra costurar. Aproveitem.", "discutir"))

# ------------------------------------------------------------------- O Gigante
func _luta_gigante() -> void:
	var pts: Array = A.get("chefes_nascem", {}).get("portao_gigante", [[27.5, 39.0]])
	var g := _criar_fera("golias", Vector2(pts[0][0], pts[0][1]))
	feras_vivas = 1
	_fala("caim", "ELE GIRA, VOCÊS SANGRAM. GOOOLIAS!", "anunciar")
	_portao("portao_gigante", true)
	sim.emitir("agrak_som", {"som": "agrak/guincho_corrente", "pos": _pos_portao("portao_gigante")})
	_em(1.2, func():
		var cen := _centro()
		g.correr(sim.celula_livre_perto(cen + Vector2(0, 3.0)), 1.0, "walk", func():
			sim.emitir("anim", {"id": g.boss.id, "anim": "roar", "dur": 1.6})
			sim.emitir("agrak_som", {"som": "agrak/golias_urro", "pos": g.boss.pos})
			_plateia("golias", "GOLIAS! GOLIAS!")
			_em(etapa_t + 2.0, func(): _fala("abel", "Já foi gente. Igual a nós. Mais ou menos.", "discutir"))
			_em(etapa_t + 3.6, func():
				esp["feras_soltas"] = true
				esp["luta_t"] = 0.0
				sim.emitir("agrak_musica", {"m": "luta"})
				g.acordar())))

# ------------------------------------------------------------------- Último de Pé
func _ultimo_de_pe(d: Dictionary) -> void:
	_portao("portao_gladiadores", false)
	for e: Ent in _vivos():
		e.lado_forcado = "g_%d" % e.id
		_buff(e, "agrak_trega", {"dano_recebido": -(1.0 - float(dados().get("regras_pvp", {}).get("dano_jogador_em_jogador", 0.6)))})
		sim.emitir_a(e, "aviso", {"texto": "Último de Pé: todos contra todos. Sem poções.", "cor": "#ff8a6a"})
	sim.emitir("agrak_musica", {"m": "final"})
	_plateia("urro")
	var an: Dictionary = d.get("anel_do_amargo", {})
	anel = {"comeca": float(an.get("comeca_s", 60)), "r0": float(an.get("raio_inicial", A.get("anel_raio_max", 13))),
		"r1": float(an.get("raio_final", 4)), "dur": float(an.get("fecha_em_s", 90)), "frac": float(an.get("dano_frac_hp_por_s", 0.08)),
		"raio": float(an.get("raio_inicial", 13)), "tick": 0.0, "ativo": false}
	_em(anel["comeca"], func():
		anel["ativo"] = true
		sim.emitir("agrak_anel", {"centro": _centro(), "r0": anel["r0"], "r1": anel["r1"], "dur": anel["dur"]})
		_fala("caim", "O AMARGO TÁ ENTRANDO!", "anunciar")
		_em(etapa_t + 2.6, func(): _fala("abel", "Andem logo, que a plateia tem hora.", "discutir")))

func _buff(e: Ent, id: String, mods: Dictionary) -> void:
	for b in e.buffs:
		if b["id"] == id: return
	e.buffs.append({"id": id, "t": 9999.0, "mods": mods})
	Regras.recalc_jogador(e)

func _tirar_buff(e: Ent, id: String) -> void:
	for b in e.buffs.duplicate():
		if b["id"] == id: e.buffs.erase(b)
	Regras.recalc_jogador(e)

func _passo_final(dt: float) -> void:
	var vivos := _vivos()
	for e in vivos:
		e.aux["cd_pocao"] = maxf(float(e.aux.get("cd_pocao", 0.0)), 1.0)   # poção proibida na luta final
	for o: Ent in sim.ents.values():   # torretas e familiar contam como do dono
		if o.tipo == "invocacao" and o.dono in gladiadores: o.lado_forcado = "g_%d" % o.dono
	if anel.get("ativo", false):
		var k := clampf((etapa_t - float(anel["comeca"])) / float(anel["dur"]), 0.0, 1.0)
		anel["raio"] = lerpf(anel["r0"], anel["r1"], k)
		anel["tick"] -= dt
		if anel["tick"] <= 0.0:
			anel["tick"] = 0.5
			var cen := _centro()
			for e in vivos:
				if e.pos.distance_to(cen) > float(anel["raio"]):
					sim.aplicar_dano_puro(e, e.hp_max * float(anel["frac"]) * 0.5, "veneno", null, "normal")
	vivos = _vivos()
	if vivos.size() <= 1:
		vencedor = vivos[0].id if vivos.size() == 1 else -1
		_etapa(etapas.size() - 1); return
	if etapa_t >= etapa_dur:   # tempo esgotado: vence quem tiver mais % de HP
		var melhor: Ent = null
		for e in vivos:
			if melhor == null or e.frac_hp() > melhor.frac_hp(): melhor = e
		vencedor = melhor.id
		_fala("abel", "Tempo! Ganha quem sangrou menos.", "discutir")
		_etapa(etapas.size() - 1)

# ------------------------------------------------------------------- Coroação e fim
func _coroacao() -> void:
	_limpar_feras()
	anel = {}
	sim.emitir("agrak_anel", {"fim": true})
	for id in gladiadores:
		var e: Ent = sim.ents.get(id)
		if e == null: continue
		e.lado_forcado = "neutro" if id in espectadores else ""
		_tirar_buff(e, "agrak_trega")
	for o: Ent in sim.ents.values():
		if o.tipo == "invocacao": o.lado_forcado = ""
	var w: Ent = sim.ents.get(vencedor)
	if w == null or not w.vivo:
		_sem_vencedor(); return
	var premio: Dictionary = E.get("premio", {}).get("vencedor", {"ficha_sangue": 1})
	for it in premio:
		if Defs.ITENS.has(it): Jogador.dar_item(sim, w, Itens.novo(it, int(premio[it])))
	w.flags["agrak_vitorias"] = int(w.flags.get("agrak_vitorias", 0)) + 1
	sim.emitir("agrak_coroacao", {"id": w.id, "nome": w.nome, "classe": _classe(w)})
	_fala("caim", "%s! DO PÓ VIEMOS E VOCÊ FICOU DE PÉ!" % _nome(w), "anunciar")
	_plateia("bracos")
	sim.emitir("agrak_musica", {"m": "vitoria"})
	_em(3.4, func(): _fala("abel", "Uma Ficha de Sangue. Leve ao Saulo antes que alguém leve você.", "rir"))
	_em(7.0, func(): _plateia("coro", "A-GRAAAK!"))

func _sem_vencedor() -> void:
	vencedor = -1
	if etapa != "coroacao":
		etapa = "coroacao"; etapa_i = etapas.size() - 1; etapa_t = 0.0
		etapa_dur = float(etapas[etapa_i].get("dur", 15))
		roteiro.clear()
		_emitir_etapa()
	_limpar_feras()
	anel = {}
	sim.emitir("agrak_anel", {"fim": true})
	sim.emitir("agrak_coroacao", {"id": -1})
	_fala("caim", "O AGRAK COMEU TODO MUNDO!", "rir")
	_plateia("vaia")
	_em(3.0, func(): _fala("abel", str(E.get("premio", {}).get("sem_vencedor_fala", "Voltem amanhã com mais carne.")), "discutir"))

func _encerrar() -> void:
	sim.emitir("agrak_fim", {"vencedor": vencedor, "ids": gladiadores})
	_emitir_etapa()
	fim_t = 2.0
	estado = "morto"

## Todos voltam para onde estavam antes da inscrição (o servidor guardou em aux.agrak_volta), com HP cheio.
func _devolver_todos() -> void:
	fim_t = -1.0
	for id in gladiadores:
		var e: Ent = sim.ents.get(id)
		if e == null: continue
		_restaurar(e)
		var v: Array = e.aux.get("agrak_volta", ["area_inicial", -1, -1])
		e.aux.erase("agrak_volta")
		sim.emitir_a(e, "trocar_mapa", {"mapa": v[0], "pos": Vector2(float(v[1]), float(v[2]))})
	sim.emitir("agrak_etapa", {"etapa": "", "fim": true})
	etapa_i = -1; etapa = ""; gladiadores.clear(); eliminados.clear(); espectadores.clear(); vencedor = -1
	esp.erase("auto")

func _restaurar(e: Ent) -> void:
	e.lado_forcado = ""
	e.alvejavel = true
	_tirar_buff(e, "agrak_trega")
	e.aux.erase("cd_pocao"); e.aux.erase("agrak_espectador"); e.aux.erase("agrak_avisou")
	if not e.vivo:
		e.vivo = true; sim.emitir("reviveu", {"id": e.id})
	e.hp = e.hp_max
	if xp_entrada.has(e.id): e.xp = maxi(e.xp, int(xp_entrada[e.id]))

# =================================================================== mortes e espectadores
func jogador_morreu() -> void:
	for id in gladiadores:
		var e: Ent = sim.ents.get(id)
		if e == null or e.vivo or id in eliminados: continue
		_eliminar(e)

func _eliminar(e: Ent) -> void:
	eliminados.append(e.id)
	e.renascer_t = 9999.0                         # quem levanta é o Saulo, não o altar
	if xp_entrada.has(e.id): e.xp = maxi(e.xp, int(xp_entrada[e.id]))   # sem penalidade no Agrak
	var killer: Ent = sim.ents.get(int(e.aux.get("ultimo_agressor", -1)))
	if killer != null and killer.tipo == "jogador" and etapa == "ultimo_de_pe":
		sim.emitir("morte_pvp", {"killer": killer.id, "vitima": e.id})
		_fala("caim", "%s DERRUBOU %s!" % [_nome(killer), _nome(e)], "anunciar")
	elif fim_t < 0.0:
		_fala("abel", "Menos um. %s vai assistir do camarote." % e.nome, "rir")
	_plateia("urro")
	_emitir_etapa()
	for o: Ent in sim.ents.values().duplicate():   # torretas somem com o dono; o familiar só assiste
		if o.tipo == "invocacao" and o.dono == e.id:
			if o.aux.get("familiar", false): o.lado_forcado = "neutro"
			else: sim.remover(o.id)
	sim.atrasar(3.0, func(): _levantar(e))

## O Saulo levanta o derrotado com a luz dele, no Camarote dos Derrotados.
func _levantar(e: Ent) -> void:
	if not sim.ents.has(e.id) or not e.id in gladiadores: return
	var cam: Dictionary = A.get("camarote_derrotados", {"pos": [6.5, 16.0]})
	e.vivo = true; e.hp = e.hp_max
	e.lado_forcado = "neutro"                     # espectador: ninguém acerta e ele não acerta ninguém
	e.alvejavel = false
	e.aux["agrak_espectador"] = true
	e.status.clear(); e.acao = {}; e.alvo = -1; e.caminho.clear()
	e.pos = sim.celula_livre_perto(Vector2(cam["pos"][0], cam["pos"][1]) + Vector2(sim.rng.randf_range(-1, 1), sim.rng.randf_range(-1, 1)))
	espectadores.append(e.id)
	sim.emitir("reviveu", {"id": e.id})
	sim.emitir("teleporte", {"id": e.id, "pos": e.pos})
	sim.emitir("vfx", {"nome": "chefe_portal", "pos": e.pos})
	if saulo >= 0:
		sim.emitir("anim", {"id": saulo, "anim": "rezar", "dur": 2.4})
		sim.emitir("fala", {"id": saulo, "texto": "Levanta, filho. Aqui ninguém morre. Só perde.", "cor": "#f4e6b8"})
	sim.emitir("agrak_som", {"som": "combate/sino_curto", "pos": e.pos})
	sim.emitir_a(e, "agrak_espectador", {"on": true})

## Desconectou (sumiu do mapa) = eliminado. Espectador fica no camarote.
func _vigiar_gladiadores(_dt: float) -> void:
	for id in gladiadores:
		var e: Ent = sim.ents.get(id)
		if e == null:
			if not id in eliminados: eliminados.append(id); _emitir_etapa()
			continue
		if id in espectadores:
			var r: Array = A.get("camarote_derrotados", {}).get("ret", [4, 13, 8, 18])
			if e.pos.x < r[0] or e.pos.y < r[1] or e.pos.x > r[2] + 1 or e.pos.y > r[3] + 1:
				e.pos = Vector2(clampf(e.pos.x, r[0] + 0.5, r[2] + 0.5), clampf(e.pos.y, r[1] + 0.5, r[3] + 0.5))
				e.caminho.clear()
			e.acao = {}; e.alvo = -1
		elif e.vivo and etapa != "chamada" and not _no_fosso(e.pos) and fim_t < 0.0:
			# o corredor fica fechado depois da Chamada; quem escapou pelo vão volta para a areia
			e.pos = sim.celula_livre_perto(Vector2(A.get("entrada_fosso", [23, 13.5])[0], A.get("entrada_fosso", [23, 13.5])[1]))
			e.caminho.clear()
			sim.emitir("teleporte", {"id": e.id, "pos": e.pos})

# =================================================================== ganchos do world_sim
func ao_quebrar(interrompeu: bool) -> void:
	for f in feras:
		if f.boss.quebrado_t > 0.0: f.ao_quebrar(interrompeu)

func ao_morrer_ent(e: Ent, killer: Ent) -> void:
	for f in feras.duplicate():
		f.ao_morrer_ent(e, killer)


# =================================================================== uma fera (leão ou Golias)
class Fera extends ChefeCtl:
	var arena                       # AgrakCtl
	var correr_para := Vector2.INF
	var correr_vel := 2.0
	var correr_fim := Callable()
	var giro := {}                  # Pião em andamento
	var tonto_t := 0.0

	func _init(p_sim: WorldSim, c: Dictionary) -> void:
		super(p_sim, c)
		estado = "dormindo"

	## Entrada: anda ou corre até o ponto sem lutar (imune), depois para.
	func correr(p: Vector2, vel_mult: float, anim: String, ao_fim := Callable()) -> void:
		correr_para = p; correr_vel = vel_mult; correr_fim = ao_fim
		sim.ir_para(boss, p)
		var dur := boss.pos.distance_to(p) / maxf(0.5, boss.vel * vel_mult)
		if anim == "run": sim.emitir("anim", {"id": boss.id, "anim": "run", "dur": dur})

	func acordar() -> void:
		boss.aux.erase("imune")
		correr_para = Vector2.INF
		estado = "luta"; luta_t = 0.0; fase = 1
		boss.cd_basico = 0.8
		var j := _jog()
		if j != null: boss.ameaca[j.id] = 1.0
		if boss.kind == "golias":
			boss.cds["piao"] = float(_atk("piao").get("primeiro_aos_s", 15))
			sim.emitir("chefe", {"id": boss.id, "nome": d["nome"], "fase": 1, "marcas": d["fases"].map(func(x): return x["hp"][0]), "inicio": true})
		else:
			sim.emitir("agrak_fera", {"id": boss.id, "nome": d["nome"]})

	func _atk(id: String) -> Dictionary:
		for a in _ataques_fase(fase):
			if a["id"] == id: return a
		return {}

	## Alvo: leões espalham (quem já é caçado por outro leão vale metade); o Golias vai na maior ameaça.
	func _jog() -> Ent:
		if arena == null: return null
		var melhor: Ent = null
		var ma := -1e9
		for e: Ent in arena._vivos():
			if not arena._no_fosso(e.pos): continue
			var a := float(boss.ameaca.get(e.id, 0.0)) - boss.pos.distance_to(e.pos) * 0.5
			if boss.kind.begins_with("leao"):
				for o in arena.feras:
					if o != self and o.boss.vivo and o.boss.alvo == e.id: a *= 0.5 if a > 0.0 else 2.0
			if a > ma: ma = a; melhor = e
		return melhor

	func _resetar() -> void:
		pass   # no Agrak a fera não volta para casa: espera alguém aparecer

	func passo(dt: float) -> void:
		if not boss.vivo: return
		if correr_para != Vector2.INF:
			if boss.caminho.is_empty() or boss.pos.distance_to(correr_para) < 0.4:
				correr_para = Vector2.INF
				boss.caminho.clear()
				if boss.kind.begins_with("leao"):
					sim.emitir("anim", {"id": boss.id, "anim": "roar", "dur": 1.3})
					var c: Vector2 = arena._centro()
					boss.facing = (c - boss.pos).normalized()
				if correr_fim.is_valid(): correr_fim.call()
			else:
				sim.mover_ao_longo(boss, dt, correr_vel)
			return
		if estado == "dormindo" or estado == "morto": return
		if tonto_t > 0.0:
			tonto_t -= dt
			if tonto_t <= 0.0:
				for b in boss.buffs.duplicate():
					if b["id"] == "tonto": boss.buffs.erase(b)
		if not giro.is_empty():
			_passo_giro(dt); return
		if _jog() == null: return
		super.passo(dt)

	func _usar(a: Dictionary, j: Ent) -> void:
		match a["id"]:
			"bote": _bote(a)
			"piao": _piao(a)
			_: super._usar(a, j)

	## Bote: salta numa linha em quem estiver mais longe (dentro do alcance), derruba.
	func _bote(a: Dictionary) -> void:
		var alc := float(a["telegrafo"]["comprimento"]) * 1.4
		var alvo: Ent = null
		for e: Ent in arena._vivos():
			var dd := boss.pos.distance_to(e.pos)
			if dd <= alc and (alvo == null or dd > boss.pos.distance_to(alvo.pos)): alvo = e
		if alvo == null: alvo = _jog()
		if alvo == null: return
		boss.cds["bote"] = float(a.get("recarga", 10))
		boss.cd_basico = boss.intervalo
		var dir := (alvo.pos - boss.pos).normalized()
		var op := _op(a)
		var desl := float(a.get("deslocamento", 6))
		sim.iniciar_acao(boss, {"preparo": float(a.get("preparo", 0.7)), "rec": 0.5, "alvo": alvo.id, "def": a, "op": op, "dir": dir,
			"nome": "Bote", "anim": "leap", "impacto": func():
				sim.deslocar(boss, boss.pos + dir * desl, 0.32, {"tipo": "investida", "anim": "leap"})})

	## Pião do Golias: 10 s girando atrás da maior ameaça, 5% do HP máximo a cada 0,25 s em quem estiver no raio
	## (ignora defesa), depois fica tonto (+50% de dano recebido) por 4 s.
	func _piao(a: Dictionary) -> void:
		boss.cds["piao"] = float(a.get("recarga", 30))
		boss.cd_basico = boss.intervalo
		var prep := float(a.get("preparo", 0.7))
		var raio := float(a["telegrafo"].get("raio", 3.5))
		var tid := sim.novo_id()
		sim.emitir("telegrafo", {"id": tid, "forma": "circulo_segue_jogador", "origem": boss.pos, "dir": Vector2.RIGHT,
			"p": {"raio": raio}, "dur": prep + float(a.get("duracao", 10)), "segue": boss.id, "dono": boss.id})
		sim.emitir("chefe_fala", {"id": boss.id, "texto": ""})
		arena._fala("caim", "OLHA O PIÃO!", "anunciar")
		sim.iniciar_acao(boss, {"preparo": prep, "rec": 0.05, "nome": "Pião", "anim": "spin_start", "conj": true, "impacto": func():
			giro = {"t": float(a.get("duracao", 10)), "tick": 0.0, "raio": raio, "frac": float(a.get("dano_frac_hp_max_por_s", 0.2)),
				"passo": float(a.get("tick", 0.25)), "vel": float(a.get("velocidade_mov_girando", 1.2)), "tele": tid,
				"anim_t": 0.0, "depois": a.get("depois", {})}
			boss.aux["imune_cc"] = true
			sim.emitir("agrak_som", {"som": "agrak/corrente_girando", "pos": boss.pos, "segue": boss.id, "dur": giro["t"]})
			sim.emitir("agrak_fx", {"fx": "piao", "id": boss.id, "dur": giro["t"]})})
		sim.atrasar(prep + 2.6, func():
			if not giro.is_empty(): arena._fala("abel", "Quem ficar no meio vira farinha. Farinha boa, pelo menos.", "discutir"))

	func _passo_giro(dt: float) -> void:
		giro["t"] -= dt
		giro["anim_t"] -= dt
		if giro["anim_t"] <= 0.0:
			giro["anim_t"] = 0.5
			sim.emitir("anim", {"id": boss.id, "anim": "spin", "dur": 0.55})
		var j := _jog()
		if j != null:
			boss.aux["repath"] = boss.aux.get("repath", 0.0) - dt
			if boss.caminho.is_empty() or boss.aux["repath"] <= 0.0:
				boss.aux["repath"] = 0.3
				sim.ir_para(boss, j.pos)
			sim.mover_ao_longo(boss, dt, float(giro["vel"]) / maxf(0.1, boss.vel))
		giro["tick"] -= dt
		if giro["tick"] <= 0.0:
			giro["tick"] += float(giro["passo"])
			for o: Ent in sim.inimigos_de(boss, boss.pos, float(giro["raio"])):
				if o.tipo != "jogador" and o.tipo != "invocacao": continue
				var v := o.hp_max * float(giro["frac"]) * float(giro["passo"])
				if o.escudo > 0.0:   # escudo absorve
					var abs_v := minf(v, o.escudo); o.escudo -= abs_v; v -= abs_v
				if v > 0.0: sim.aplicar_dano_puro(o, v, "fisico", boss, "normal")
		if giro["t"] <= 0.0: _fim_giro()

	func _fim_giro() -> void:
		var dep: Dictionary = giro.get("depois", {})
		sim.emitir("telegrafo_fim", {"id": giro.get("tele", -1)})
		giro = {}
		boss.aux.erase("imune_cc")
		boss.caminho.clear()
		sim.emitir("anim", {"id": boss.id, "anim": "spin_end", "dur": 1.0})
		tonto_t = float(dep.get("duracao", 4))
		boss.buffs.append({"id": "tonto", "t": tonto_t, "mods": {"dano_recebido": float(dep.get("dano_recebido", 0.5))}})
		sim.aplicar_status(boss, "exausto", tonto_t, null)
		sim.emitir("chefe_buff", {"id": boss.id, "fome": 0})
		sim.emitir("fala", {"id": boss.id, "texto": "TONTO", "cor": "#ffd27a"})

	func parar_giro() -> void:
		if not giro.is_empty():
			sim.emitir("telegrafo_fim", {"id": giro.get("tele", -1)})
			giro = {}

	func ao_morrer_ent(e: Ent, killer: Ent) -> void:
		if e != boss or estado == "morto": return
		estado = "morto"
		parar_giro()
		for t in sim.telegrafos.duplicate():
			if t["dono"] == boss.id: sim.remover_telegrafo(t["id"])
		if boss.kind == "golias":
			sim.emitir("chefe", {"id": boss.id, "fim": true, "morto": true})
		else:
			sim.emitir("agrak_fera", {"id": boss.id, "fim": true})
		sim.emitir("agrak_som", {"som": "agrak/rugido_morte", "pos": boss.pos})
		arena.fera_caiu(self, killer)

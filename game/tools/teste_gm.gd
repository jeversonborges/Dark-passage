extends Node
## Teste do Painel do GM: hospeda em rede local como "jefin", abre cada aba (fotos) e confere no servidor o efeito
## de cada ação. Uso (main.gd carrega este script com teste_gm=DIR, igual ao teste_rede):
##   xvfb-run godot --rendering-driver opengl3 -- conectar=hospedar usuario=jefin senha=1234 classe=humano gm_contas=jefin teste_gm=/tmp/gm

var jogo: Node2D
var args := {}
var t := 0.0
var feitos := {}
var falhas := 0

func _ok(cond: bool, txt: String) -> void:
	print("[teste_gm] %s %s" % ["OK  " if cond else "FALHOU", txt])
	if not cond: falhas += 1

func _foto(nome: String) -> void:
	var dir: String = args["teste_gm"]
	DirAccess.make_dir_recursive_absolute(dir)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [dir, nome])

func _em(seg: float, k: String) -> bool:
	if feitos.has(k) or t < seg: return false
	feitos[k] = true
	return true

func _process(dt: float) -> void:
	t += dt
	if jogo == null or jogo.jog == null: return
	var srv = jogo.rede.servidor
	var eu: Ent = srv.sessoes[1]["jog"] if srv != null and srv.sessoes.has(1) else null
	var sim: WorldSim = srv.mundos.get(srv.sessoes[1]["mapa"]) if eu != null else null
	if _em(3.0, "ativo"):
		if jogo.hud.ajuda_ui: jogo.hud.ajuda_ui.visible = false
		_ok(GmPainel.ativo, "servidor marcou a conta como GM (gm_ativo)")
		var antes: Array = srv.gm.contas_gm.duplicate()   # conta comum: pedido ignorado
		srv.gm.contas_gm = ["outra"]
		var o0 := eu.ouro
		srv.gm.receber(1, {"t": "gm", "a": "ouro", "qtd": 999})
		_ok(eu.ouro == o0, "conta que não é GM é ignorada")
		srv.gm.contas_gm = antes
		GmPainel.pedir(jogo, "imortal", {"v": true})
		GmPainel.pedir(jogo, "invocar", {"kind": "carnical", "nivel": 8, "qtd": 3, "neutro": true})
		GmPainel.pedir(jogo, "chefe", {"kind": "general_partido", "anunciar": true})
		GmPainel.pedir(jogo, "item", {"id": "pocao_vida_p", "qtd": 30})
		GmPainel.pedir(jogo, "ouro", {"qtd": 50000})
		GmPainel.pedir(jogo, "nivel", {"nivel": 60})
		GmPainel.pedir(jogo, "hermon", {"modo": "agora"})
		GmPainel.pedir(jogo, "agrak", {"modo": "abrir"})
		GmPainel.pedir(jogo, "aviso_global", {"texto": "Teste do painel do GM."})
		srv.contas["teste_ban"] = {"personagens": [{"nome": "Bandido", "classe": "humano", "nivel": 3}]}
		GmPainel.pedir(jogo, "banir", {"nome": "Bandido", "dias": 7, "motivo": "teste"})
	if _em(4.5, "confere"):
		var gms := 0; var chefe := 0
		for e: Ent in sim.ents.values():
			if e.aux.get("gm", false): gms += 1
			if e.kind == "general_partido": chefe += 1
		_ok(gms >= 4, "invocações no mapa: %d (3 carniçais + chefe)" % gms)
		_ok(chefe == 1, "chefe de campo Andras invocado")
		_ok(Itens.contar(eu.inv, "pocao_vida_p") >= 30, "30 poções criadas")
		_ok(eu.ouro >= 50000, "ouro dado: %d" % eu.ouro)
		_ok(eu.nivel == 60 and eu.pontos == 59 * int(Defs.FORM["pontos_por_nivel"]), "nível 60 com pontos devolvidos")
		_ok(eu.aux.get("imune", false) and eu.invuln_t > 1000.0, "imortal")
		var agora := int(Time.get_unix_time_from_system())
		_ok(srv.hermon.janela_aberta(agora) >= 0, "Hermon aberto à mão")
		_ok(srv.agrak.inicio - agora <= 61 and srv.agrak.aberta(), "Agrak com inscrição aberta")
		_ok(srv.gm.ban_login("teste_ban") != "", "conta offline banida: " + srv.gm.ban_login("teste_ban"))
		GmPainel.pedir(jogo, "desbanir", {"nome": "teste_ban"})
		GmPainel.pedir(jogo, "invisivel", {"v": true})
	if _em(5.5, "confere2"):
		_ok(srv.gm.ban_login("teste_ban") == "", "banimento tirado")
		_ok(eu.invisivel, "invisível no servidor")
		var vw = jogo.views.get(jogo.jog.id)
		_ok(vw != null and vw.visible and vw.modulate.a < 0.6, "o próprio GM se vê translúcido")
		GmPainel.pedir(jogo, "invisivel", {"v": false})
		srv.contas.erase("teste_ban")
		GmPainel.aba = "invocar"; GmPainel.mob_sel = "carnical"; GmPainel.chefe_sel = "general_partido"
		GmPainel.abrir(jogo)
	if _em(7.0, "f_invocar"): _foto("painel_invocar")
	if _em(7.2, "a_jog"): GmPainel.aba = "jogadores"; GmPainel.nome_sel = jogo.jog.nome; GmPainel.abrir(jogo)
	if _em(8.5, "f_jog"): _foto("painel_jogadores")
	if _em(8.7, "a_itens"): GmPainel.aba = "itens"; GmPainel.item_sel = "pocao_vida_p"; GmPainel.abrir(jogo)
	if _em(10.0, "f_itens"): _foto("painel_itens")
	if _em(10.2, "a_ev"): GmPainel.aba = "eventos"; GmPainel.abrir(jogo)
	if _em(11.5, "f_ev"): _foto("painel_eventos")
	if _em(11.7, "a_via"): GmPainel.aba = "viajar"; GmPainel.abrir(jogo)
	if _em(13.0, "f_via"): _foto("painel_viajar")
	if _em(13.2, "fecha"):
		jogo.janelas.fechar("gm")
		GmPainel.pedir(jogo, "limpar")
	if _em(14.5, "fim"):
		var gms := 0
		for e: Ent in sim.ents.values(): if e.aux.get("gm", false): gms += 1
		_ok(gms == 0, "limpar removeu as invocações")
		print("[teste_gm] fim: %d falha(s)" % falhas)
		get_tree().quit(1 if falhas > 0 else 0)

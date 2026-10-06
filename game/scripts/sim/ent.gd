class_name Ent
extends RefCounted
## Uma entidade do mundo (jogador, monstro, chefe, NPC, objeto, invocação). Só dados.

var id := 0
var tipo := ""            # jogador | monstro | chefe | npc | objeto | invocacao
var kind := ""            # classe, id do mob, id do npc...
var nome := ""
var nivel := 1
var pos := Vector2.ZERO
var facing := Vector2(1, 0)
var raio := 0.35          # corpo, em tiles
var vivo := true
var morto_t := 0.0
var invisivel := false    # emboscada (monge na parede), enterrado (Filho de Cardo)
var alvejavel := true
var escala := 1.0

# combate
var hp := 100.0
var hp_max := 100.0
var rec := 0.0
var rec_max := 0.0
var escudo := 0.0
var escudo_t := 0.0
var stats := {"FOR": 0, "AGI": 0, "VIT": 0, "ESP": 0}
var dano_min := 1.0
var dano_max := 2.0
var defesa := 0.0
var ar := 10.0            # taxa de ataque
var er := 10.0            # taxa de esquiva
var critico := 0.05
var crit_mult := 1.5
var excelente := 0.0
var vel_ataque := 1.0     # bônus (divide o intervalo)
var intervalo := 1.5
var alcance := 1.2
var vel := 3.2            # tiles/s
var elemento := "fisico"
var res := {}             # elemento -> resistência
var tags: Array = []
var arquetipo := "normal"
var postura := 30.0
var postura_max := 30.0
var postura_t := 0.0      # s desde o último dano de postura
var quebrado_t := 0.0
var quebra_cd := 0.0
var postura_arma := 10.0
var roubo_vida := 0.0
var status := {}          # id -> {t, dados...}
var cc_hist := {}         # retornos decrescentes: id -> [tempo, contagem]
var buffs: Array = []     # {id, t, mods:{...}}
var ameaca := {}          # id -> ameaça (mobs)
var em_combate_t := 99.0  # s desde o último golpe dado/recebido
var hitstop := 0.0

# ação em andamento (golpe com preparo, conjuração, canalização)
var acao := {}
var cds := {}             # id do ataque/skill -> recarga restante
var cd_basico := 0.0
var golpes := 0           # contador para "a_cada"

# movimento
var caminho: Array = []
var destino := Vector2.INF
var empurrao := Vector2.ZERO
var empurrao_t := 0.0
var deslocando := {}      # investida/arrasto/rolamento: {de, para, t, dur}

# IA
var estado := "ocioso"
var casa := Vector2.ZERO
var raio_vagar := 3.0
var raio_coleira := 14.0
var raio_aggro := 6.0
var renasce_s := 25.0
var spawn_ref := -1
var ia := {}              # parâmetros do mob (padrao, distancias...)
var ia_t := 0.0
var aux := {}             # memória livre da IA / chefe
var dono := -1            # invocações
var dura_t := -1.0
var alvo := -1

# jogador
var classe := ""
var faccao := ""
var xp := 0
var pontos := 0
var ouro := 0
var municao := 0
var folego := 0.0
var inv: Array = []       # itens na mochila: {uid, id, x, y, qtd, ...}
var equip := {}           # slot -> item
var armazem: Array = []
var missoes := {}         # id -> {estado: ativa|concluida|falhou, prog:[...], escolha}
var flags := {}
var buffer_skill := {}    # skill pedida fora de alcance (fica até 2s)
var seguir_alvo := false
var no_lugar := false
var renascer_t := 0.0
var imune_t := 0.0
var invuln_t := 0.0
var zona := ""
var vistas := {}          # subzonas visitadas
var pity_raro := 0
var abates := {}          # mob -> total (estatística)
var interagindo := {}     # canalização de baú {obj, t}
var skills_slots: Array = []

func pronto() -> bool:
	return vivo and acao.is_empty() and not tem("atordoado") and not tem("derrubado") and quebrado_t <= 0.0 and deslocando.is_empty()

func tem(s: String) -> bool:
	return status.has(s)

func frac_hp() -> float:
	return hp / maxf(hp_max, 1.0)

func dano_medio() -> float:
	return (dano_min + dano_max) * 0.5

func mod(chave: String) -> float:
	var t := 0.0
	for b in buffs:
		t += float(b["mods"].get(chave, 0.0))
	return t

func eh_inimigo_de(o: Ent) -> bool:
	if o == null or o == self: return false
	var a := lado()
	var b := o.lado()
	return a != b and a != "neutro" and b != "neutro"

func lado() -> String:
	match tipo:
		"jogador", "invocacao": return "jogadores"
		"monstro", "chefe": return "monstros"
		"objeto": return "monstros" if alvejavel else "neutro"
	return "neutro"

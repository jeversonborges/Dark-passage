class_name NpcTipo
extends RefCounted
## Função de cada NPC, para o jogador ler de longe (0.9.8.2): ícone acima da cabeça e no mapa, e o
## subtítulo com a função (Armazenamento, Ferreiro...) no lugar do título de lore. O ícone sai dos
## serviços do npcs.json; os casos fora dessa regra ficam em OVERRIDES.

const DIR_ICONES := "res://assets/ext/ui/npc/"
## NPC -> tipo, quando os serviços não dizem a função (o alquimista não tem serviço próprio no JSON)
const OVERRIDES := {
	"saulo": "pvp", "sariel_porta": "convite", "zaqueu_vendedor": "convite",
	"tobias_pavio": "pocao", "bartimeu_carrinho": "pocao",
}
## tipo -> [arquivo do ícone, subtítulo]
const FUNCOES := {
	"pvp": ["pvp", "PvP / Arena"],
	"convite": ["convite", "Convites"],
	"pocao": ["pocao", "Alquimista"],
	"coletor": ["pata", "Pet Shop"],
	"ferreiro": ["ferreiro", "Ferreiro"],
	"treinador": ["estrela", "Treinador"],
	"ascensao_de_classe": ["estrela", "Ascensão de Classe"],
	"biblioteca": ["livro", "Biblioteca"],
	"armazem": ["bau", "Armazenamento"],
	"loja": ["bau", "Vendedor"],
	"missao": ["missao", "Missões"],
}
## primeiro serviço que casar vale (o mais claro para o jogador)
const ORDEM := ["coletor", "ferreiro", "treinador", "ascensao_de_classe", "biblioteca", "armazem", "loja", "missao"]

static var _cache := {}


## {"icone": nome do arquivo ou "", "funcao": subtítulo ou ""}
static func de(npc: String) -> Dictionary:
	if _cache.has(npc): return _cache[npc]
	var tipo := ""
	if OVERRIDES.has(npc):
		tipo = OVERRIDES[npc]
	else:
		var servicos: Array = Defs.NPCS.get(npc, {}).get("servicos", [])
		for t in ORDEM:
			if t == "missao":
				if _doa_missao(npc): tipo = t
			elif t in servicos: tipo = t
			if tipo != "": break
	var r := {"icone": "", "funcao": ""}
	if tipo != "": r = {"icone": FUNCOES[tipo][0], "funcao": FUNCOES[tipo][1]}
	_cache[npc] = r
	return r


static func textura(icone: String) -> Texture2D:
	return Tema.tex(DIR_ICONES + icone + ".png") if icone != "" else null


static func _doa_missao(npc: String) -> bool:
	for m in Defs.MISSOES_LISTA:
		if not m.get("oculta", false) and m.get("doador") == npc: return true
	return false

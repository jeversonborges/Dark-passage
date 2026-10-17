# A trava dos mistérios, lado do servidor (porta de entregas/biblioteca/trava/servidor_ref.py).
# Só o servidor carrega isto. O arquivo misterios.srv.json NÃO pode ir no export do cliente.
# Não há nenhum segredo neste código: as respostas só existem como hash, e o conteúdo só abre com o evento certo.
class_name Selo
extends RefCounted

const NEGACAO := ["nao", "nunca", "jamais", "nem"]
const ACENTOS := {"á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a", "é": "e", "è": "e", "ê": "e", "ë": "e",
	"í": "i", "ì": "i", "î": "i", "ï": "i", "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
	"ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c", "ñ": "n", "ý": "y"}

var sal := ""
var textos := {}
var idx := {}          # hash -> Array[entrada]
var chaves := {}       # chaves encadeadas já abertas (nome -> hex). Persistir no banco do servidor.

func carregar(caminho: String) -> bool:
	var f := FileAccess.open(caminho, FileAccess.READ)
	if f == null: return false
	var d: Dictionary = JSON.parse_string(f.get_as_text())
	sal = d["sal"]; textos = d["textos"]
	for e in d["entradas"]:
		if not idx.has(e["h"]): idx[e["h"]] = []
		idx[e["h"]].append(e)
	return true

static func _sem_acento(s: String) -> String:
	var out := ""
	for c in s.to_lower():
		out += ACENTOS.get(c, c)
	return out

static func _limpa(s: String, permitidos: String) -> String:
	var re := RegEx.new(); re.compile("[^a-z0-9" + permitidos + " ]+")
	var r := re.sub(_sem_acento(s), " ", true)
	var sp := RegEx.new(); sp.compile(" +")
	return sp.sub(r, " ", true).strip_edges()

static func normalizar(ev: String) -> String:
	return _limpa(ev, "{}|_")

static func limpar_fala(t: String) -> String:
	return _limpa(t, "")

static func _sha(partes: Array) -> PackedByteArray:
	var h := HashingContext.new(); h.start(HashingContext.HASH_SHA256)
	h.update("|".join(PackedStringArray(partes)).to_utf8_buffer())
	return h.finish()

func hash_evento(ev: String) -> String:
	return _sha([sal, "h", normalizar(ev)]).hex_encode()

func _chave_evento(ev: String, extra: String) -> PackedByteArray:
	return _sha([sal, "k", normalizar(ev), extra]) if extra != "" else _sha([sal, "k", normalizar(ev)])

static func _decifrar(chave: PackedByteArray, iv_b64: String, c_b64: String) -> String:
	var aes := AESContext.new()
	if aes.start(AESContext.MODE_CBC_DECRYPT, chave, Marshalls.base64_to_raw(iv_b64)) != OK: return ""
	var out := aes.update(Marshalls.base64_to_raw(c_b64)); aes.finish()
	if out.is_empty(): return ""
	var pad := out[out.size() - 1]
	if pad < 1 or pad > 16: return ""
	return out.slice(0, out.size() - pad).get_string_from_utf8()

## Payloads (Dictionary) que este evento abre. Quase sempre vazio.
func abrir(ev: String) -> Array:
	var res := []
	for e in idx.get(hash_evento(ev), []):
		var extra := ""
		if e.has("kr"):
			if not chaves.has(e["kr"]): continue
			extra = chaves[e["kr"]]
		var txt := _decifrar(_chave_evento(ev, extra), e["iv"], e["c"])
		var p = JSON.parse_string(txt) if txt != "" else null
		if p is Dictionary: res.append(p)
	return res

## Texto de pista guardado no servidor (null se não existir).
func texto(tid: String):
	if not textos.has(tid): return null
	var t: Dictionary = textos[tid]
	var s := _decifrar(_sha([sal, "t", tid]), t["iv"], t["c"])
	return JSON.parse_string(s) if s != "" else null

## Uma fala no chat local vira vários eventos fala|<alvo>|<pedaço>. O nome do próprio personagem vira {eu}.
static func eventos_de_fala(alvo: String, texto_: String, nome_jogador: String, max_tokens := 14, max_n := 6) -> PackedStringArray:
	var re := RegEx.new(); re.compile("[.,;:!?…\\n]+")
	var toks: Array = []; var oracao: Array = []
	var k := 0
	for o in re.sub(texto_, "\u0001", true).split("\u0001"):
		for t in limpar_fala(o).split(" ", false):
			toks.append(t); oracao.append(k)
		k += 1
	toks = toks.slice(0, max_tokens); oracao = oracao.slice(0, max_tokens)
	var nome := limpar_fala(nome_jogador).split(" ", false)
	if nome.size() > 0:
		var nt: Array = []; var no: Array = []; var i := 0
		while i < toks.size():
			if toks.slice(i, i + nome.size()) == Array(nome):
				nt.append("{eu}"); no.append(oracao[i]); i += nome.size()
			else:
				nt.append(toks[i]); no.append(oracao[i]); i += 1
		toks = nt; oracao = no
	var evs := PackedStringArray()
	for i in toks.size():
		var negado := false
		for j in range(max(0, i - 3), i):
			if toks[j] in NEGACAO and oracao[j] == oracao[i]: negado = true
		if negado: continue
		for n in range(1, max_n + 1):
			if i + n <= toks.size():
				evs.append("fala|%s|%s" % [alvo, " ".join(PackedStringArray(toks.slice(i, i + n)))])
	return evs

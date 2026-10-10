class_name Atualizador
extends Node
## Baixa o zip do cliente, confere o sha256 e extrai em <base>/jogo.
## O trabalho pesado (sha256 e extração) roda numa thread para a janela não travar.

signal progresso(fase: String, feito: int, total: int)
signal terminou(ok: bool, mensagem: String)

var base := ""                 # pasta onde ficam jogo/ e .baixando/
var _http: HTTPRequest
var _thread: Thread
var _manifesto := {}
var _parte := ""
var _tamanho := 0
var _fase := ""
var _feito := 0                # escrito pela thread, lido no _process
var _total := 0
var _cancelar := false

func ocupado() -> bool:
	return _fase != ""

func pasta_jogo() -> String:
	return base.path_join("jogo")

## Versão instalada ({} se não houver jogo).
func instalada() -> Dictionary:
	var p := pasta_jogo().path_join("versao.json")
	if not FileAccess.file_exists(p): return {}
	var d = JSON.parse_string(FileAccess.get_file_as_string(p))
	return d if d is Dictionary else {}

func baixar(manifesto: Dictionary, url_zip: String) -> void:
	if ocupado(): return
	_manifesto = manifesto
	_tamanho = int(manifesto.get("tamanho", 0))
	_cancelar = false
	var tmp := base.path_join(".baixando")
	DirAccess.make_dir_recursive_absolute(tmp)
	_parte = tmp.path_join(String(manifesto.get("arquivo", "cliente.zip")).get_file() + ".part")
	if FileAccess.file_exists(_parte): DirAccess.remove_absolute(_parte)
	_http = HTTPRequest.new()
	_http.use_threads = true
	_http.download_chunk_size = 262144
	_http.download_file = _parte
	_http.timeout = 0
	add_child(_http)
	_http.request_completed.connect(_baixou)
	var err := _http.request(url_zip)
	if err != OK:
		_falhar("Não deu para começar o download (erro %d)." % err)
		return
	_fase = "baixando"

func cancelar() -> void:
	_cancelar = true
	if _http:
		_http.cancel_request()
		_http.queue_free()
		_http = null
	if _fase == "baixando":
		_fase = ""
		DirAccess.remove_absolute(_parte)
		terminou.emit(false, "Download cancelado.")

func _process(_d: float) -> void:
	match _fase:
		"baixando":
			if _http: progresso.emit("baixando", _http.get_downloaded_bytes(), max(_tamanho, _http.get_body_size()))
		"conferindo", "extraindo":
			progresso.emit(_fase, _feito, _total)

func _baixou(resultado: int, codigo: int, _h: PackedStringArray, _b: PackedByteArray) -> void:
	_http.queue_free()
	_http = null
	if _cancelar: return
	if resultado != HTTPRequest.RESULT_SUCCESS or codigo != 200:
		_falhar("O download falhou (%s). Tente de novo." % (("HTTP %d" % codigo) if codigo else "sem conexão"))
		return
	_fase = "conferindo"
	_feito = 0
	_total = _tamanho_arquivo(_parte)
	_thread = Thread.new()
	_thread.start(_trabalho)

func _tamanho_arquivo(p: String) -> int:
	var f := FileAccess.open(p, FileAccess.READ)
	return f.get_length() if f else 0

## Roda na thread: confere o sha256 e extrai. Devolve "" ou a mensagem de erro.
func _trabalho() -> void:
	var erro := _conferir()
	if erro == "": erro = _extrair()
	call_deferred("_fim_trabalho", erro)

func _conferir() -> String:
	var esperado := String(_manifesto.get("sha256", "")).to_lower()
	var f := FileAccess.open(_parte, FileAccess.READ)
	if f == null: return "O arquivo baixado sumiu."
	var tam := f.get_length()
	if _tamanho > 0 and tam != _tamanho:
		return "O arquivo veio incompleto (%d de %d bytes)." % [tam, _tamanho]
	if esperado == "": return ""
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	while f.get_position() < tam:
		if _cancelar: return "Cancelado."
		h.update(f.get_buffer(1 << 20))
		_feito = f.get_position()
	if h.finish().hex_encode() != esperado:
		return "O arquivo baixado não confere com o servidor (sha256). Tente de novo."
	return ""

func _extrair() -> String:
	_fase = "extraindo"
	var zip := ZIPReader.new()
	if zip.open(_parte) != OK: return "O arquivo baixado não é um zip válido."
	var arquivos := zip.get_files()
	var novo := base.path_join("jogo.novo")
	_apagar(novo)
	DirAccess.make_dir_recursive_absolute(novo)
	_total = arquivos.size()
	_feito = 0
	for nome in arquivos:
		if _cancelar: return "Cancelado."
		# nada de caminho absoluto nem de sair da pasta do jogo
		if nome.begins_with("/") or nome.contains("..") or nome.contains(":") or nome.contains("\\"):
			return "O zip tem um caminho inválido: %s" % nome
		var destino := novo.path_join(nome)
		if nome.ends_with("/"):
			DirAccess.make_dir_recursive_absolute(destino)
		else:
			DirAccess.make_dir_recursive_absolute(destino.get_base_dir())
			var w := FileAccess.open(destino, FileAccess.WRITE)
			if w == null: return "Não deu para gravar %s (disco cheio ou sem permissão)." % nome
			w.store_buffer(zip.read_file(nome))
			w.close()
		_feito += 1
	zip.close()
	var info := {"versao": _manifesto.get("versao", "?"), "arquivo": _manifesto.get("arquivo", ""),
		"sha256": _manifesto.get("sha256", ""), "instalado_em": Time.get_datetime_string_from_system()}
	var v := FileAccess.open(novo.path_join("versao.json"), FileAccess.WRITE)
	v.store_string(JSON.stringify(info, "\t"))
	v.close()
	# troca a pasta antiga pela nova só no fim, para nunca deixar o jogo pela metade
	_apagar(pasta_jogo())
	if DirAccess.rename_absolute(novo, pasta_jogo()) != OK:
		return "Não deu para trocar a pasta do jogo. Feche o jogo se ele estiver aberto."
	DirAccess.remove_absolute(_parte)
	return ""

func _fim_trabalho(erro: String) -> void:
	_thread.wait_to_finish()
	_thread = null
	if erro != "":
		DirAccess.remove_absolute(_parte)
		_falhar(erro)
		return
	_fase = ""
	terminou.emit(true, "")

func _falhar(msg: String) -> void:
	_fase = ""
	terminou.emit(false, msg)

static func _apagar(p: String) -> void:
	if not DirAccess.dir_exists_absolute(p): return
	var d := DirAccess.open(p)
	if d == null: return
	d.include_hidden = true
	for sub in d.get_directories(): _apagar(p.path_join(sub))
	for f in d.get_files(): DirAccess.remove_absolute(p.path_join(f))
	DirAccess.remove_absolute(p)

func _exit_tree() -> void:
	_cancelar = true
	if _thread and _thread.is_started(): _thread.wait_to_finish()

extends Node
## Som do jogo: música e ambiente por zona (com crossfade), efeitos com variação de pitch e posição na tela.
## Tudo vem de data/ext/audio.json (thread de Som e música).

var sons: Dictionary
var musica_a := AudioStreamPlayer.new()
var musica_b := AudioStreamPlayer.new()
var amb_a := AudioStreamPlayer.new()
var amb_b := AudioStreamPlayer.new()
var musica_atual := ""
var amb_atual := ""
var pool: Array = []
var _cache := {}
var _ultimo := {}       # nome -> tempo (evita metralhar o mesmo som)
var t := 0.0
var vol := {"musica": -8.0, "ambiente": -6.0, "sfx": -2.0, "ui": -4.0}
var mudo := false
var ouvinte := Vector2.ZERO   # posição de tela do jogador (para volume por distância)

func _ready() -> void:
	sons = Defs.AUDIO.get("sons", {})
	for p in [musica_a, musica_b, amb_a, amb_b]:
		add_child(p)
	for i in 16:
		var s := AudioStreamPlayer.new()
		add_child(s); pool.append(s)

func _stream(nome: String, idx := -1) -> AudioStream:
	var s: Dictionary = sons.get(nome, {})
	var arqs: Array = s.get("arquivos", [])
	if arqs.is_empty(): return null
	var f: String = arqs[idx if idx >= 0 else randi() % arqs.size()]
	if not _cache.has(f):
		var st: AudioStream = load(f) if ResourceLoader.exists(f) else null
		if st is AudioStreamOggVorbis and s.get("loop", false): st.loop = true
		_cache[f] = st
	return _cache[f]

func _process(dt: float) -> void:
	t += dt

## Efeito sonoro. pos_tela opcional: atenua com a distância ao jogador.
func tocar(nome: String, pos_tela = null, vol_db := 0.0, pitch_var := 0.05) -> void:
	if mudo or nome == "": return
	if _ultimo.get(nome, -1.0) > t - 0.045: return
	_ultimo[nome] = t
	var st := _stream(nome)
	if st == null: return
	var s: Dictionary = sons[nome]
	var bus: String = s.get("bus", "sfx")
	var db := float(vol.get(bus, 0.0)) + vol_db
	if pos_tela != null:
		var d := (pos_tela as Vector2).distance_to(ouvinte)
		if d > 1100.0: return
		db -= d / 1100.0 * 18.0
	var p: AudioStreamPlayer = null
	for q in pool:
		if not q.playing: p = q; break
	if p == null: p = pool[randi() % pool.size()]
	p.stream = st
	p.volume_db = db
	p.pitch_scale = randf_range(1.0 - pitch_var, 1.0 + pitch_var)
	p.play()

func evento(ev: String, pos_tela = null) -> void:
	var lista = Defs.AUDIO.get("eventos_combate", {}).get(ev, null)
	if lista == null:
		if sons.has(ev): tocar(ev, pos_tela)
		return
	for n in lista: tocar(n, pos_tela)

func musica(nome: String) -> void:
	if nome == musica_atual: return
	musica_atual = nome
	_crossfade(musica_a, musica_b, nome, float(vol["musica"]))
	var tmp := musica_a; musica_a = musica_b; musica_b = tmp

func ambiente(nome: String) -> void:
	if nome == amb_atual: return
	amb_atual = nome
	_crossfade(amb_a, amb_b, nome, float(vol["ambiente"]))
	var tmp := amb_a; amb_a = amb_b; amb_b = tmp

func _crossfade(velho: AudioStreamPlayer, novo: AudioStreamPlayer, nome: String, db: float) -> void:
	if velho.playing:
		var tw := create_tween()
		tw.tween_property(velho, "volume_db", -60.0, 1.8)
		tw.tween_callback(velho.stop)
	var st := _stream(nome, 0) if nome != "" else null
	if st == null or mudo: return
	novo.stream = st
	novo.volume_db = -50.0
	novo.play()
	var tw2 := create_tween()
	tw2.tween_property(novo, "volume_db", db, 2.2)

func alternar_mudo() -> void:
	mudo = not mudo
	for p in [musica_a, musica_b, amb_a, amb_b]: p.stream_paused = mudo

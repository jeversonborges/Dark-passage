extends Node
## Conexão da rede local (ENet). O mesmo nó existe em todos os PCs, em /root/Main/Rede.
## Quem hospeda roda o servidor aqui dentro e também joga como o cliente de número 1.

signal mensagem(m: Dictionary)   # servidor -> este cliente
signal caiu(motivo: String)

const PORTA := 7777
const Servidor := preload("res://scripts/net/servidor.gd")

var servidor: Node = null
var ip_servidor := ""

## Sobe o servidor neste PC. Devolve "" ou o motivo do erro.
func hospedar(porta := PORTA) -> String:
	var p = ClassDB.instantiate("ENetMultiplayerPeer")
	if p == null: return "Rede local não disponível nesta versão."
	var err: int = p.create_server(porta, 16)
	if err != OK: return "Não deu para abrir a porta %d (já tem outro servidor aberto?)." % porta
	multiplayer.multiplayer_peer = p
	servidor = Servidor.new()
	servidor.name = "Servidor"
	servidor.rede = self
	add_child(servidor)
	multiplayer.peer_connected.connect(func(id): print("[servidor] conexão nova: ", id))
	multiplayer.peer_disconnected.connect(func(id): if servidor: servidor.desconectou(id))
	ip_servidor = "127.0.0.1"
	return ""

## Entra no servidor de outro PC.
func conectar(ip: String, porta := PORTA) -> String:
	if ip.count(":") == 1:   # "192.168.0.10:7777"
		porta = int(ip.get_slice(":", 1)); ip = ip.get_slice(":", 0)
	var p = ClassDB.instantiate("ENetMultiplayerPeer")
	if p == null: return "Rede local não disponível nesta versão."
	var err: int = p.create_client(ip, porta)
	if err != OK: return "Endereço inválido: " + ip
	multiplayer.multiplayer_peer = p
	ip_servidor = ip
	multiplayer.connected_to_server.connect(func(): mensagem.emit({"t": "conectado"}), CONNECT_ONE_SHOT)
	multiplayer.connection_failed.connect(func(): _fechar(); caiu.emit("Não achei nenhum servidor em %s. Confira o IP e se o outro PC clicou em Hospedar." % ip), CONNECT_ONE_SHOT)
	multiplayer.server_disconnected.connect(func(): _fechar(); caiu.emit("O servidor fechou a partida."), CONNECT_ONE_SHOT)
	return ""

func hospedando() -> bool:
	return servidor != null

func sair() -> void:
	if servidor != null:
		servidor.queue_free(); servidor = null
	_fechar()

func _fechar() -> void:
	if multiplayer.multiplayer_peer != null and not multiplayer.multiplayer_peer is OfflineMultiplayerPeer:
		multiplayer.multiplayer_peer.close()
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()

func _exit_tree() -> void:
	_fechar()

## IPs deste PC na rede local (para quem hospeda passar aos amigos).
static func meus_ips() -> Array:
	var out: Array = []
	for a in IP.get_local_addresses():
		if a.contains(":") or a.begins_with("127.") or a.begins_with("169.254."): continue
		out.append(a)
	out.sort_custom(func(x, y): return x.begins_with("192.168.") and not y.begins_with("192.168."))
	return out

# =================================================================== envio
## Cliente -> servidor.
func enviar_srv(m: Dictionary) -> void:
	if servidor != null:
		servidor.receber(1, _dec(_cod(m)))
	elif multiplayer.multiplayer_peer != null and multiplayer.multiplayer_peer.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED:
		_srv.rpc_id(1, _cod(m))

func enviar_cmd(nome: String, a: Array) -> void:
	enviar_srv({"t": "cmd", "n": nome, "a": a})

## Servidor -> cliente (o 1 é quem hospeda, no mesmo processo).
func enviar(peer: int, m: Dictionary) -> void:
	var b := _cod(m)
	if peer == 1: call_deferred("_entregar", b)
	else: _cli.rpc_id(peer, b)

@rpc("any_peer", "call_remote", "reliable")
func _srv(b: PackedByteArray) -> void:
	if servidor == null: return
	var m := _dec(b)
	if not m.is_empty(): servidor.receber(multiplayer.get_remote_sender_id(), m)

@rpc("authority", "call_remote", "reliable")
func _cli(b: PackedByteArray) -> void:
	_entregar(b)

func _entregar(b: PackedByteArray) -> void:
	var m := _dec(b)
	if not m.is_empty(): mensagem.emit(m)

static func _cod(m: Dictionary) -> PackedByteArray:
	var b := var_to_bytes(m)
	if b.size() < 1400:
		var o := PackedByteArray([0]); o.append_array(b); return o
	var z := b.compress(FileAccess.COMPRESSION_DEFLATE)
	var o2 := PackedByteArray([1, 0, 0, 0, 0])
	o2.encode_u32(1, b.size())
	o2.append_array(z)
	return o2

static func _dec(o: PackedByteArray) -> Dictionary:
	if o.size() < 2: return {}
	var b: PackedByteArray
	if o[0] == 0: b = o.slice(1)
	else:
		var n := o.decode_u32(1)
		if n > 16 * 1024 * 1024: return {}
		b = o.slice(5).decompress(n, FileAccess.COMPRESSION_DEFLATE)
	var v = bytes_to_var(b)
	return v if v is Dictionary else {}

extends Node
## Conexão da rede local (ENet). O mesmo nó existe em todos os PCs, em /root/Main/Rede.
## Quem hospeda roda o servidor aqui dentro e também joga como o cliente de número 1.

signal mensagem(m: Dictionary)   # servidor -> este cliente
signal caiu(motivo: String)

const PORTA := 7777
const VERSAO := "0.9.4"                    # cliente e servidor precisam bater (o servidor recusa outra)
const ONLINE := "darkpassage.com.br"       # servidor oficial (a VPS)
const ONLINE_IP := "213.109.169.186"       # se o DNS do domínio falhar, vai direto no IP
const MAX_MSG_SEG := 60                    # mais que isso por segundo (média de 2 s) derruba a conexão
const MAX_PACOTE := 64 * 1024              # do cliente para o servidor, já descomprimido
const Servidor := preload("res://scripts/net/servidor.gd")

var servidor: Node = null
var ip_servidor := ""
var online := false                        # conectado ao servidor oficial (com DTLS)
var _contagem := {}                        # peer -> [início da janela, mensagens]

## Sobe o servidor neste PC. Devolve "" ou o motivo do erro.
## Com `tls` (certificado + chave) a conexão é cifrada (DTLS), como no servidor online.
func hospedar(porta := PORTA, maximo := 48, tls: TLSOptions = null) -> String:
	var p = ClassDB.instantiate("ENetMultiplayerPeer")
	if p == null: return "Rede local não disponível nesta versão."
	var err: int = p.create_server(porta, maximo)
	if err != OK: return "Não deu para abrir a porta %d (já tem outro servidor aberto?)." % porta
	if tls != null:
		err = p.host.dtls_server_setup(tls)
		if err != OK: p.close(); return "Não deu para ligar a criptografia (DTLS): erro %d." % err
	multiplayer.multiplayer_peer = p
	servidor = Servidor.new()
	servidor.name = "Servidor"
	servidor.rede = self
	add_child(servidor)
	multiplayer.peer_connected.connect(func(id): print("[servidor] conexão nova: ", id))
	multiplayer.peer_disconnected.connect(func(id):
		_contagem.erase(id)
		if servidor: servidor.desconectou(id))
	ip_servidor = "127.0.0.1"
	return ""

## Entra no servidor de outro PC. `tls_nome` liga o DTLS e confere o certificado desse domínio.
func conectar(ip: String, porta := PORTA, tls_nome := "", tls_inseguro := false) -> String:
	if ip.count(":") == 1:   # "192.168.0.10:7777"
		porta = int(ip.get_slice(":", 1)); ip = ip.get_slice(":", 0)
	var p = ClassDB.instantiate("ENetMultiplayerPeer")
	if p == null: return "Rede local não disponível nesta versão."
	var err: int = p.create_client(ip, porta)
	if err != OK: return "Endereço inválido: " + ip
	if tls_nome != "":
		err = p.host.dtls_client_setup(tls_nome, TLSOptions.client_unsafe() if tls_inseguro else TLSOptions.client())
		if err != OK: p.close(); return "Não deu para ligar a criptografia (DTLS): erro %d." % err
	multiplayer.multiplayer_peer = p
	ip_servidor = ip
	online = tls_nome != ""
	multiplayer.connected_to_server.connect(func(): mensagem.emit({"t": "conectado"}), CONNECT_ONE_SHOT)
	var on := tls_nome != ""
	multiplayer.connection_failed.connect(func(): _fechar(); caiu.emit(
		"O servidor online não respondeu. Ele pode estar em manutenção; tente de novo em alguns minutos." if on
		else "Não achei nenhum servidor em %s. Confira o IP e se o outro PC clicou em Hospedar." % ip), CONNECT_ONE_SHOT)
	multiplayer.server_disconnected.connect(func(): _fechar(); caiu.emit(
		"A conexão com o servidor caiu." if on else "O servidor fechou a partida."), CONNECT_ONE_SHOT)
	return ""

func hospedando() -> bool:
	return servidor != null

func sair() -> void:
	if servidor != null:
		servidor.queue_free(); servidor = null
	_fechar()

## Entra no servidor oficial (darkpassage.com.br), sempre cifrado.
func conectar_online(endereco := "", tls_inseguro := false) -> String:
	var host := endereco if endereco != "" else ONLINE
	var porta := PORTA
	if host.count(":") == 1: porta = int(host.get_slice(":", 1)); host = host.get_slice(":", 0)
	var ip := host
	if not host.is_valid_ip_address():
		ip = IP.resolve_hostname(host, IP.TYPE_IPV4)
		if ip == "": ip = ONLINE_IP if host == ONLINE else ""
	if ip == "": return "Não achei o endereço %s. Confira a internet." % host
	var err := conectar(ip, porta, host if not host.is_valid_ip_address() else ONLINE, tls_inseguro)
	if err == "": ip_servidor = host
	return err

## O servidor derruba quem manda mensagem demais (robô, cliente alterado).
func _derrubar(peer: int, motivo: String) -> void:
	print("[servidor] derrubado %d: %s" % [peer, motivo])
	_contagem.erase(peer)
	var p = multiplayer.multiplayer_peer
	if p is ENetMultiplayerPeer: (p as ENetMultiplayerPeer).disconnect_peer(peer)

func ip_do_peer(peer: int) -> String:
	var p = multiplayer.multiplayer_peer
	if peer == 1 or not p is ENetMultiplayerPeer: return "local"
	var pp = (p as ENetMultiplayerPeer).get_peer(peer)
	return pp.get_remote_address() if pp != null else "?"

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
	var peer := multiplayer.get_remote_sender_id()
	var agora := Time.get_ticks_msec()
	var c: Array = _contagem.get(peer, [agora, 0])
	if agora - c[0] > 2000: c = [agora, 0]
	c[1] += 1
	_contagem[peer] = c
	if c[1] > MAX_MSG_SEG * 2: _derrubar(peer, "mensagens demais"); return
	var m := _dec(b, MAX_PACOTE)
	if m.is_empty(): _derrubar(peer, "pacote inválido ou grande demais"); return
	servidor.receber(peer, m)

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

static func _dec(o: PackedByteArray, limite := 16 * 1024 * 1024) -> Dictionary:
	if o.size() < 2 or o.size() > limite + 5: return {}
	var b: PackedByteArray
	if o[0] == 0: b = o.slice(1)
	else:
		if o.size() < 6: return {}
		var n := o.decode_u32(1)
		if n > limite: return {}
		b = o.slice(5).decompress(n, FileAccess.COMPRESSION_DEFLATE)
	var v = bytes_to_var(b)
	return v if v is Dictionary else {}

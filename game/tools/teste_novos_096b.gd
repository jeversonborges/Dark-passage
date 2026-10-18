extends SceneTree
## Cinco itens novos 0.9.6 (18/10): escudos, Frasco de Bílis, Azeite de Lavanda e Serra da Vala entram nas tabelas de drop.
## Rodar: godot --headless -s tools/teste_novos_096b.gd
func _init() -> void:
	Defs.carregar()
	var falhas := 0
	for id in ["escudo_da_cruz_remida", "escudo_de_raizes_vivas", "frasco_de_bilis_dourado", "azeite_de_lavanda_bento", "serra_da_vala"]:
		if not Defs.ITENS.has(id): print("FALHA: item %s ausente" % id); falhas += 1
	if Defs.ITENS.has("escudo_da_cruz_remida") and int(Itens.bonus({"segunda_mao": Itens.novo("escudo_da_cruz_remida")})["defesa"]) != 16:
		print("FALHA: defesa do Escudo da Cruz Remida"); falhas += 1
	if Defs.ITENS.has("escudo_de_raizes_vivas") and int(Itens.bonus({"segunda_mao": Itens.novo("escudo_de_raizes_vivas")})["defesa"]) != 25:
		print("FALHA: defesa do Escudo de Raízes Vivas"); falhas += 1
	var pf: Dictionary = Defs.ITENS.get("frasco_de_bilis_dourado", {})
	if pf.get("efeito", {}).get("duracao_s", 0) != 8 or float(pf.get("efeito", {}).get("cura_hp_pct", 0)) != 15.0:
		print("FALHA: efeito do Frasco de Bílis"); falhas += 1
	for tag in ["consumivel:bilis_dourado", "consumivel:azeite_bento", "excelente:vala_dos_caes", "excelente:jerusalem", "excelente:egito"]:
		if Defs.POR_TAG.get(tag, []).is_empty(): print("FALHA: tag %s sem itens" % tag); falhas += 1
	print("teste_novos_096b: %s" % ("OK" if falhas == 0 else "%d falha(s)" % falhas))
	quit(1 if falhas > 0 else 0)

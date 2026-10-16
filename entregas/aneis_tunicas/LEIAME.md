# Entrega: anéis e túnicas padrão (PR #17, 2026-10-15)

Já está na pasta compartilhada (mesmos caminhos do repositório):
- `design/skills-itens/itens.json`: 24 itens novos (`colecao` = aneis_simples, aneis_gemas, tunicas; `motivo` = arte_pronta).
- Ícones: `assets/icones/itens/{64,40,32,mochila,mochila_2x}/<id>.png` e atlas `assets/icones/atlas_itens_*.png/json`.
- Folhas originais: `assets/icones/fontes/`. Gerador: `tools/icones/arte_pronta.py`.
- Prévia: `design/skills-itens/previas/aneis_tunicas.png`.

Rode `game/tools/sync.sh` para copiar para o jogo.

## Duas mudanças no jogo

1. `game/scripts/sim/itens.gd`, em `Itens.bonus()`, dentro do loop por slot, depois de somar `atributos`:

```gdscript
		var bf = d.get("bonus_fixo")
		if typeof(bf) == TYPE_DICTIONARY:
			for k in bf:
				if k == "res":
					for el in bf["res"]: b["res"][el] = b["res"].get(el, 0.0) + float(bf["res"][el])
				elif k == "defesa": b["defesa"] += float(bf[k]) * ref
				elif b.has(k): b[k] += float(bf[k])
```
Chaves usadas: hp, defesa, dano_plano, critico, velocidade_ataque, roubo_de_vida, reduz_dano, dano_magico_extra, ouro, res.

2. `game/scripts/sim/loot.gd`, em `item_da_tag` (ramo `equip:`): trocar o sorteio uniforme do `pool` por sorteio pelo campo `peso_drop` (padrão 1.0):

```gdscript
		var tot := 0.0
		for i in pool: tot += float(Defs.ITENS[i].get("peso_drop", 1.0))
		var x := sim.rng.randf() * tot
		var id: String = pool[pool.size() - 1]
		for i in pool:
			x -= float(Defs.ITENS[i].get("peso_drop", 1.0))
			if x <= 0.0: id = i; break
```
Sem isso, os 24 itens sem classe dominam os drops (entram sempre no pool "meus").

Túnicas: slot `peito`, `classes: null` (todas as classes), não mudam o visual do personagem.

## Lote 2 (2026-10-16): conjuntos de pano, colares, espadas, Decreto Vampírico
Mesmo fluxo, 51 itens novos em `design/skills-itens/itens.json` (ver README de skills-itens). Ícones já gerados.
3. Bônus de conjunto: `itens.json > conjuntos[]` tem `pecas` e `bonus_conjunto_fixo` ({"2": {...}, "4": {...}}, mesmas chaves de
   `bonus_fixo`). `Itens.bonus()` já conta `b["conjuntos"]`; falta somar o maior degrau atingido de cada conjunto.
4. Itens antigos com `peso_drop: 0` não devem cair (a mudança 2 já cuida disso se o peso 0 for respeitado).
5. Decreto Vampírico (`decreto_vampirico`, lendário, 2ª mão do Cultista): o `efeito` (skills que custam HP devolvem 25% ao acertar) precisa de código.

# Cetro do Demiurgo · a arma do administrador

Pedido do Jefin (17/10/2026): "a arma do adm que sou eu; bastante efeito, linda, poderosa e absurda; nenhuma arma é
igual; absolutamente superior, e causar inveja em todos". Mesmo caminho da Chave-Mestra do Primarca (0.8.3), só que
sem balanceamento de propósito: existe uma, é dele, e ninguém mais chega perto.

## O que já está na pasta do projeto
- Item `cetro_do_demiurgo` em `design/missoes/dados/itens.json` (e em `design/skills-itens/itens.json`, regerado):
  nível 1, todas as 7 classes, dano 777-999, +99 em FOR/AGI/VIT/ESP, +9999 HP, +999 defesa, 7 efeitos únicos.
  O item traz `"numeros_fixos": true`: o `gerar_json.py` passou a respeitar esse campo e copia dano, defesa e a
  raridade como estão (sem a fórmula por nível), então `Defs.ITENS` já recebe 777-999 e `demiurgico` sem retoque.
  (Obs.: a Chave-Mestra do Primarca não tem a flag e sai do gerador com dano 5-10; se quiserem o 15-28 dela, é só
  marcar `numeros_fixos` no item e regerar.)
- Raridade nova `demiurgico` em `design/combate/drops.json` (exibida "Demiúrgico", cor `#f4ffe9`, feixe `#9dffc8`,
  peso 0): acima do Lendário/primordial. `Defs.nome_raridade` tem a tabela fixa: acrescentar `"demiurgico": "Demiúrgico"`.
- Modelo 3D `assets/armas/modelos/cetro_do_demiurgo.glb` (formato combinado em `armas.py`: metros, origem na pegada,
  +Z para a coroa; emissivo = brilho). O item já traz `"visual": "item:cetro_do_demiurgo:haste"` para a camada de arma
  visível (`entregas/armas_camada`). Fonte: `tools/sprite-pipeline/personagens/cetro_demiurgo.py`.
- Efeitos visuais em `assets/efeitos/` (`tools/vfx/efeitos_demiurgo.py`): `demiurgo_aura` (loop, no pé, todos veem),
  `demiurgo_golpe` (no alvo de cada ataque), `demiurgo_verbo` (chão, 8 m, a cada ataque), `demiurgo_juizo` (no inimigo apagado).
- Sons em `assets/audio/sfx/itens/` (`assets/audio/fontes/sfx_demiurgo.py`): `cetro_golpe` (3 variações),
  `cetro_juizo`, `cetro_aura` (loop posicional, bus ambiente).
- Prévias aqui: `cetro_render.png`, `cetro_cabeca.png`, `cetro_previa.png`.
- Ícone: ainda não existe. Pela regra dos ícones, entrou na lista do Jefin (`entregas/arte_itens/LISTA.md`) com a
  referência `cetro_cabeca.png`. Até chegar, o ícone gerado do `gerar_json.py` serve de tapa-buraco só na conta dele.

## Para a thread "Prévia jogável" (dona de game/)

### 1. Entrega única, na conta do administrador (`servidor.gd`, ao lado de `_chave_primarca`)
A conta ainda precisa ser confirmada pelo Jefin (abaixo está `"jefin"`). Qualquer classe, qualquer personagem novo
dessa conta: ele recebe o cetro na primeira entrada.

```gdscript
## Cetro do Demiurgo: uma única vez por personagem da conta do administrador, qualquer classe.
const CONTA_DEMIURGO := "jefin"
func _cetro_demiurgo(usuario: String, e: Ent, sim: WorldSim) -> void:
	if usuario != CONTA_DEMIURGO or e.flags.has("cetro_demiurgo"): return
	e.flags["cetro_demiurgo"] = true
	Jogador.dar_item(sim, e, Itens.novo("cetro_do_demiurgo"))
	_gravar_contas()
```
Chamar onde `_chave_primarca(s["u"], e, sim)` é chamado. O wipe da 0.9.3 não atrapalha: a flag é por personagem.

### 2. Vínculo e raridade
`vinculado.conta`: mesma regra da Chave-Mestra (não vende, não troca, não larga; some do chão se cair por bug).
A raridade lê `drops.json`, então cor e nome do feixe já saem certos; `cor_feixe` é um campo novo (o feixe de drop
e o brilho do nome usam `cor_feixe` quando existe, senão `cor`).

### 3. Efeitos únicos (`efeitos_unicos`, mesmo esquema da Chave-Mestra)
| id | o que faz | onde |
|---|---|---|
| `verbo` | todo ataque básico atinge todos os inimigos num raio de 8 m com 100% do dano; toca `demiurgo_verbo` no chão e `cetro_golpe` | ataque básico |
| `juizo_do_demiurgo` | 10% por golpe: inimigo comum morre na hora (`demiurgo_juizo` + `cetro_juizo`); chefe perde 10% da vida máxima | após o dano |
| `como_em_cima_assim_embaixo` | devolve 100% de todo dano recebido ao agressor; imune a todos os status | ao receber dano / status |
| `sopro_do_primeiro_dia` | +10% da vida máxima e do recurso por segundo | tick |
| `mao_que_mede` | recarga de todas as skills -90% e custo zero | uso de skill |
| `olho_do_demiurgo` | mapa inteiro revelado, vê invisíveis, mobs agressivos não puxam (só revidam) | cliente (mapa/minimapa) e IA dos mobs |
| `aura_demiurgica` | `demiurgo_aura` no pé, visível para todos (sincronizar como `vis_aura`); aliados a 10 m +50% dano e +50% XP; inimigos a 10 m -50% dano | tick, raio 10 m |

### 4. Arma visível e som
- Camada de arma: `"visual": "item:cetro_do_demiurgo:haste"` segue o formato de `armas.py` (`montar("item:...")`).
  Enquanto a camada não existe no jogo, nada a fazer.
- `cetro_aura` é um loop posicional (bus ambiente) tocando no jogador enquanto o cetro está equipado.

## Regerar
- Modelo e prévias: `cd tools/sprite-pipeline/personagens && /opt/bpy42/bin/python cetro_demiurgo.py -- <saida>`
  (venv `/opt/bpy42` com `bpy==4.2.0`, ver `tools/sprite-pipeline/npcs/kit.py`).
- Efeitos: `cd tools/vfx && python3 build.py demiurgo`. Sons: `cd assets/audio/fontes && python3 build.py itens/cetro`.

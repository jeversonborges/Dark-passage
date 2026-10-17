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

## Como foi integrado (0.9.4)
- **Dados do jogo** (`game/data/design/`): `missoes/itens.json` e `skills-itens/itens.json` ganharam o item com
  `"vinculado": true` (o bloco conta/vende/troca/larga ficou em `_vinculo_doc`; o texto de `efeito` continua sendo
  o que o tooltip mostra, e é por ele ser texto que `Itens.bonus` registra o id em `bonus.efeitos`);
  `combate/drops.json` ganhou a raridade `demiurgico` e `Defs.nome_raridade` mostra "Demiúrgico". Efeitos
  (`demiurgo_*`) e sons (`itens/cetro_*`) copiados para `game/assets/ext/` e registrados em `efeitos.json` e
  `audio.json` (`game/tools/manifest.py` regenera `data/ext/`). Arma visível em `assets/ext/armas/visuais.json`:
  silhueta `cajado_osso` por enquanto, tinta ouro `#e6c25a`, brilho esmeralda `#9dffc8`, `brilho_proprio`; a
  silhueta própria vinda do `.glb` fica para a camada de armas.
- **Entrega** (`game/scripts/net/servidor.gd`, `_cetro_demiurgo`, ao lado de `_chave_primarca`): uma vez por
  personagem de qualquer conta da lista de GMs (`gm.eh_conta_gm`: `/etc/darkpassage/gm.json` ou
  `user://servidor/gm.json`; teste local `gm_contas=login`), qualquer classe, flag `cetro_demiurgo` no personagem.
  Conta que deixou de ser GM perde o cetro ao entrar (`Demiurgo.tirar`: mochila, equipamento e armazém).
- **Efeitos** (`game/scripts/sim/demiurgo.gd`; uma linha de gancho em cada ponto): Golpe, Verbo e Juízo em
  `Jogador.ao_acertar` (o ataque básico marca `op.basico`); reflexo em `Jogador.ao_ser_atingido`; imunidade a status
  em `WorldSim.aplicar_status`; Sopro em `Jogador._regen`; custo zero em `Jogador.custo` e recarga ×0,1 em
  `_tentar_skill`; Olho na busca de alvo de `IA._ocioso` (o mob só revida); Aura em `Jogador.passo` (buffs
  `aura_demiurgica` e `aura_demiurgica_fraqueza` renovados a cada 1 s, `mod("xp")` em `Jogador.ganhar_xp`, a
  fraqueza dos monstros expira em `WorldSim._passo_ent`) e `aux.aura = "demiurgo"` enquanto está equipado
  (`Regras.recalc_jogador`, sem apagar a aura da Biblioteca). Vinculado: `Jogador.vender` e `soltar_item` recusam
  (`Itens.vinculado`); a troca já recusava.
- **Cliente** (`game/scripts/client/game.gd`, `hud.gd`): `aux.aura == "demiurgo"` vira a folha `demiurgo_aura` em
  loop seguindo a unidade (todos veem) mais o loop posicional `itens/cetro_aura`; `som_evento` aceita o nome do som
  com posição (`itens/cetro_golpe`, `itens/cetro_juizo`); com o cetro, as unidades invisíveis aparecem a 60% e o
  mapa (M) mostra todas as zonas como conhecidas (não há névoa de guerra); a raridade `demiurgico` entra no feixe
  e no som de drop.
- **Teste**: `cd game && /opt/godot/godot --headless --path . --script res://tools/teste_cetro.gd` (sem rede: dá e
  equipa o cetro e confere dano, raridade, vínculo, imunidade, Sopro, custo/recarga, Verbo, reflexo, aura, Olho e
  `gm.eh_conta_gm`).
- Ainda sem ícone próprio: a mochila mostra o quadro na cor da raridade até a arte da lista do Jefin chegar.

## Regerar
- Modelo e prévias: `cd tools/sprite-pipeline/personagens && /opt/bpy42/bin/python cetro_demiurgo.py -- <saida>`
  (venv `/opt/bpy42` com `bpy==4.2.0`, ver `tools/sprite-pipeline/npcs/kit.py`).
- Efeitos: `cd tools/vfx && python3 build.py demiurgo`. Sons: `cd assets/audio/fontes && python3 build.py itens/cetro`.

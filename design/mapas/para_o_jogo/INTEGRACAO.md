# Mapa do deserto: como encaixar no jogo

O Jefin aprovou o mapa em 2026-10-04. Este guia é para a thread "Prévia jogável e área inicial".

## Passo 1: rodar já (só copiar)

`para_o_jogo/area_inicial.json` carrega no `world_sim.gd` e no `game.gd` atuais sem mudar código. Para usar, copie esse arquivo sobre `game/data/mapas/area_inicial.json`.

- Ele tem os mesmos campos que o jogo lê (`name`, `size`, `spawn`, `safe_zone`, `props`, `blocked`, `spawns`). Também traz as camadas novas, que o jogo ainda ignora.
- Os mobs são 31 grupos, 68 no total. Quando o mob do design ainda não existe em `game/data/monstros.json`, o `kind` usa um substituto e o id final fica em `kind_design`:
  - `cao_de_vala`, `corvo_de_cinza` e `porco_pestilento` viram `cao_praga`;
  - `nao_julgado` vira `flagelado`;
  - `acougueiro_oco` e `capataz_gancho` viram `acougueiro`.
- Ficaram de fora 5 grupos: as 4 patrulhas de facção (`so_para`, que é PvP e vem depois) e o Filho de Cardo da missão s02 (`so_por_missao`).
- Conferi que o spawn do jogador e o centro de cada grupo caem em tile livre. Não testei dentro do Godot, porque ele não está instalado aqui.

Ao rodar, você vai ver o seguinte:
- O chão aparece xadrez, porque não existe `assets/ground/area_inicial.png` para 160×160.
- Quase nenhum prop aparece. O jogo só desenha os kinds que estão em `game/assets/props/props.json`, e o kit de ambiente ainda não exportou PNG de objetos (o `objetos` do manifest está vazio).
- As luzes aparecem, porque saem do campo `light` do prop.

## Passo 2: o que muda no código, em ordem de impacto

1. **Mobs novos.** Crie em `game/data/monstros.json` os ids de `design/combate/mobs.json`: `corvo_de_cinza`, `cao_de_vala`, `nao_julgado`, `porco_pestilento`, `acougueiro_oco`, `capataz_gancho` e `filho_de_cardo`. Depois troque para o JSON de origem (`design/mapas/area_inicial.json`), que já usa os ids finais.
2. **Chão.** A camada `terreno` traz uma string por x e um caractere por tile, e a legenda está em `terreno_legenda`. Monte o chão em blocos (TileMap ou pedaços de 16×16 tiles) com os pisos do kit, porque uma imagem única de 160 tiles fica grande demais.
3. **Props.** Os `kind` seguem os nomes de `assets/ambiente/fontes/assets.py`.
   - `camada: "chao"` é decalque e vai abaixo do y-sort.
   - `pendente: true` ainda não tem arte (a lista está em `props_pendentes`).
   - `decor_moldura: true` é só cenário da borda.
   - Atenção à escala: o kit usa 64 px/m a 30°, e o `iso.gd` usa 44,8 px/m a 35°.
4. **Câmera.** Use `camera_limite` (14 a 146) em vez de `size`, para a borda nunca aparecer crua.
5. **Borda disfarçada.** `amargo` é a grade de radiação, um caractere por tile, e as regras estão em `amargo_regras`.
   - O contador começa a estalar no nível 4, e o dano começa no 7.
   - A faixa de tempestade é andável, e o resto da moldura está em `blocked`.
   - A névoa e a areia da tempestade vêm da thread de efeitos.
6. **Spawns com comportamento.**
   - `patrulha` é uma lista de pontos para o grupo seguir.
   - `formacao: "fila"` faz o grupo andar em fila.
   - `ancora` é o prop que o grupo guarda.
   - `elite: true` marca o Capataz.
   - `so_por_missao` só nasce com a missão ativa.
   - `so_para` é patrulha de facção.
7. **Mundo vivo.**
   - `npcs` traz os ids de `design/missoes/dados/npcs.json`.
   - `baus` e `objetos` são as posições dos objetos de missão.
   - `luzes` e `sons_pontuais` usam ids de `assets/audio/audio.json`.
   - Há duas zonas seguras em `safe_zones`, com `spawn_por_faccao`. Isso se cruza com a escolha da facção na tela de personagem.


## v0.4 do mapa (06/10): spots de farm, temperamento e oásis

Isto é para a v0.6 do jogo. `design/mapas/area_inicial.json` agora traz:

- **`spots`**: 8 spots de farm. Cada um tem id, nome, nível, centro, raio e lista de mobs, e `spots.json` repete os mesmos dados para a thread de Missões. Dentro de cada spot já tirei os objetos altos, para o leque do nível 5 caber.
- **Spawns de spot**: são grupos de 2 ou 3, todos com `spot`, `temperamento` (`neutro`, `territorial` ou `agressivo`) e `respawn_s` (14 nos spots do nível 3 em diante, 18 nos de nível 1 a 3). Os territoriais trazem também `ancora` e `raio_territorio`.
  - Para isso funcionar, o `tools/mapa.py` precisa copiar `temperamento`, `respawn_s`, `spot` e `raio_territorio`.
  - O `world_sim.gd` hoje decide a postura pela zona e corta `qtd` para 2 ou 3. Os spawns com `temperamento` devem usar esse valor como postura (`territorial` = neutro que também ataca quem entra no `raio_territorio` da âncora).
  - Os spots já chegam em grupos de 2 ou 3, então o corte não muda nada neles. Também vale não aplicar a regra de "nível 1 = 1 mob" aos spots.
- **Spawns fora dos spots**: também têm `temperamento`. Nenhum grupo fica a menos de 15 m da borda de uma zona segura.
- **`descanso`**: 4 fogueiras de descanso, cada uma com um `carrinho_tobias` (props com `"ponto": "descanso"`). A ideia é um vendedor de poção em cada fogueira.
- **Beira da Tempestade (nível 9 a 12)**: usa `nao_julgado` e `carnical` em nível alto, com o campo `variante` (`nao_julgado_da_tempestade`, `carnical_inchado`), até a thread de Monstros entregar essas variantes.
- **Oásis do Rio Amargo** (escolha do Jefin): 75 touceiras de `flor_absinto` nas margens, marcadas `pendente`, com `luz_fraca` verde-água. Enquanto não houver arte, dá para usar `planta_mutante` no lugar.

`para_o_jogo/area_inicial.json` foi gerado de novo com o mesmo conteúdo.

## Se o mapa mudar

Não edite o JSON à mão. Altere `design/mapas/fontes/layout.py` e depois rode:

```
python3 layout.py && python3 spots.py && python3 render.py && python3 exportar_jogo.py
```

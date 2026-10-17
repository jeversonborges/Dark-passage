# Evoluções do nível 50 no jogo (patch para a Prévia)

O patch `evolucao_jogo.patch` foi feito contra `/mnt/project-files/game/scripts` de 17/10 05:15 (UTC) e confere em dry-run.
Para aplicar: `cd /mnt/project-files/game && patch -p1 < ../entregas/evolucoes/patch_jogo/evolucao_jogo.patch`, depois
`bash tools/sync.sh` e `godot --headless --path . -s tools/teste_evolucao.gd` (resultado esperado: `RESULTADO: OK`).

## O que entra

- **`scripts/sim/evolucao.gd` (novo).** Escolha e validação do caminho, bônus do caminho, barra de skills e as 60 skills
  novas, montadas a partir dos campos de `design/combate/evolucoes.json`. A classe base continua em `e.classe`, então
  recurso, ataque básico e skills base não mudam. O caminho fica em `e.evolucao` (campo novo do `Ent`, sincronizado e salvo).
- **Bônus.** `regras.gd` aplica os atributos do caminho e estes multiplicadores:
  - `hp_mult`, que é 1,15 da evolução vezes o do caminho;
  - `defesa_mult`, `dano_mult`, `dano_magico_mult`, `velocidade_ataque_mult`, `alcance_mult`, `dano_critico_mult` e `recurso_max_mult`;
  - `critico`, `roubo_vida`, `bloqueio` (vira esquiva) e `cura_mult`;
  - `resistencia_amargo` reduz o dano do Amargo. A evolução também dá +10 pontos de atributo.
- **Missões.** `missoes.gd` passa a ter:
  - a condição `classe` nos diálogos. Antes ela caía no `_: ok = true`, e o Pedro mostrava os 12 caminhos para todo mundo;
  - `nivel_minimo` em `disponivel()`;
  - o objetivo `chefes_dungeon`, que por enquanto vale pelo nível, porque a linha G ainda não está no jogo;
  - `aplica_evolucao` na conclusão, que recusa caminho de outra classe ou uma segunda evolução;
  - `flags` aplicadas ao concluir.
- **Barra.** As 5 skills da evolução ficam nos slots 10 a 14: uma fileira menor acima da barra, usada com Shift+1 a Shift+5.
  O tooltip e a janela de skills mostram as skills novas. Enquanto os ícones pintados do Jefin não chegam (lista em
  `entregas/arte_itens/LISTA.md`), o slot mostra as 3 primeiras letras do nome.
- **Boneco.** `unidade.gd` usa o sprite da evolução (`sprite` em `evolucoes.json`) quando ele está em `Defs.SPR`. Na
  Forma Colossal, usa `abominacao_colossal`. Os eventos `evolucao` e `forma` recarregam o boneco. As folhas estão em
  `entregas/evolucoes/sprites/`.
- **Save.** O campo novo é `evolucao`. Um save com caminho de outra classe é ignorado.
- **`tools/teste_evolucao.gd` (novo).** Roda as 12 evoluções:
  - nível 48 contra 50;
  - carta do Simão e conclusão da ev01 com o Pedro;
  - a ev02 começando sozinha;
  - só as 2 opções da classe na tela, recusa de caminho alheio e de segunda evolução;
  - os atributos, `hp_mult` e `defesa_mult` conferidos pela fórmula;
  - os slots 10 a 14 e as 5 skills de cada caminho saindo e fazendo efeito (as de dano ferindo);
  - Forma Vingativa com velocidade de ataque 2,3 e +30% de crítico;
  - Forma Colossal com HP x3, ataque a 0,45 e escala 1,8, voltando ao normal no fim;
  - o save de ida e volta pelo JSON.

## A ilha do Pedro

- O mapa novo de São Lázaro já tem a Ilha do Exilado: zona `ilha_do_exilado`, ponto `oficina_do_exilado` e o Pedro em
  (128,2, 107,8). As pontes de corda ligam a ilha às duas margens, e o BFS confirma o caminho.
- O `area_inicial.json` e o `spots.json` atualizados foram copiados para `entregas/cidade_sao_lazaro/`, que é de onde o
  `sync.sh` lê.
- As peças novas do kit estão em `assets/ambiente/objetos/`: `ponte_corda`, `oficina_exilado`, `manequim_evolucao_a/_b`,
  `sino_ponte` e `trapiche_exilado`. A fonte é `assets/ambiente/fontes/exilado.py`.
- Prévia: `entregas/evolucoes/previa/ilha_exilado.png`.

## Segundo patch: passivas e ressurreição (`evolucao_passivas.patch`)

Aplica por cima do primeiro, que já está em `game/`: `cd /mnt/project-files/game && patch -p1 < ../entregas/evolucoes/patch_jogo/evolucao_passivas.patch`.

- **As 12 passivas no servidor:**
  - Hoste em Marcha;
  - Seis Asas (cura que passa do HP máximo vira escudo de até 20%);
  - Trono Vazio (redução de dano por inimigo perto e devolução em brasa ao bloquear);
  - Colheita (+25% abaixo de 30% de HP e Passo Sombrio renovado ao matar);
  - Três Auréolas (a 4ª magia sai de graça e com +40%);
  - Bebeu do Rio (acúmulos de Amargo cortam a cura do alvo e curam o Profeta);
  - Balas Bentas;
  - Troféu;
  - A Plateia (bloqueio dá Fúria; com Fúria cheia, o golpe atordoa);
  - O Amargo Venceu;
  - Liturgia da Máquina (reparo de 2%/s);
  - Sino Derretido.
- **Ressurreição.** O Coro dos Seis Ais levanta no lugar os aliados mortos a até 10 m. O Levanta-te levanta o morto mais
  perto do cursor depois de 2 s de conjuração e, sem morto por perto, cura o alvo. O evento `reviveu` que o cliente já trata
  é o mesmo.
- O `teste_evolucao.gd` ganhou a parte das passivas e da ressurreição, e o resultado continua `RESULTADO: OK`.

## Ainda de fora (texto do JSON sem regra no servidor)

- O "+1 torreta ativa" da Liturgia da Máquina.
- O enxame que pula para outro alvo quando o primeiro morre.
- O "ninguém sai" da arena do Gladiador.
- Os números não passaram pelo `simular.py`.

## Testes antigos

O `teste_v06.gd` falha igual com e sem o patch (carrinhos, spots e skill em área do auto). As falhas vêm do mapa novo e
do modo automático novo, não deste patch.

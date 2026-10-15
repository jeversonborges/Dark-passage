# Skills, itens e ícones (v0.2)

- `skills.json`: as 43 skills (6 por classe: 5 da 1ª entrega + a suprema do estágio 3; o Humano tem uma a mais, o Corte Giratório; mais as 6 skills de área do nível 5), com descrição, efeito visual e som sugeridos, tipo, elemento e ícone. O bloco `combate` de cada skill é copiado de `design/combate/classes_base.json`, que é a fonte dos números. As supremas ainda têm números provisórios.
- `itens.json`: 147 itens. As armas iniciais e secundárias usam os números de `classes_base.json`.
  - Bases genéricas (armas e conjuntos por classe e peso, acessórios): raridade **rolada** no drop (comum, mágico, raro, excelente), tags `equip:faixa1` e `equip:faixa2`. Dano e defesa saem das fórmulas de `classes_base.json`.
  - Consumíveis, munição, materiais, jóias de refino, chave e baús com as tags de `design/combate/drops.json`. `cobertura_tags_drops` mostra que todas as tags das tabelas têm item.
  - Os 57 itens com nome da thread Missões (`design/missoes/dados/itens.json`), com o mesmo id e nome, completados com raridade no padrão do combate, tag de drop, dano e defesa pela fórmula (o valor que Missões sugeriu fica em `*_sugerido_missoes`), grade da mochila e ícone.
  - `pools_lendarios`: qual item com nome sai em cada tag `lendario:*`.
- `fontes/`: dados em Python e `gerar_json.py` (rode depois de mudar algo em combate ou missões).

## Ícones (`assets/icones/`)
- `skills/{64,40,32}/<id>.png`: moldura dourada para Arautos e de aço e latão para Vigília. O HUD usa 40 px.
- `itens/{64,40,32}/<id>.png`: ícone quadrado para loja, tooltip e barra rápida. Mágico, raro, excelente e Relíquia têm brilho na cor da raridade.
- `itens/mochila/<id>.png` (30 px por célula) e `itens/mochila_2x/` (60 px): arte da mochila em grade no estilo do MU, no tamanho `grade` de cada item.
- `atlas_*.png` + `.json`: atlas com as coordenadas. `previa_*.png`: folhas de conferência.

Para gerar de novo, use `tools/icones/` (precisa de `pip install pillow numpy` e do Chromium do container):

    cd tools/icones
    PYTHONPATH=. python3 gerar_skills.py && PYTHONPATH=. python3 gerar_itens.py
    PYTHONPATH=. python3 folha.py skills && PYTHONPATH=. python3 folha.py itens && PYTHONPATH=. python3 mochila_previa.py

## Skills de área do nível 5 (v0.3)

**Ids no combate (2026-10-06):** o `classes_base.json` do Design do combate usa os mesmos ids destas 6 skills (`anjo_leque_juizo`, `cultista_espinhos_sangue`, `mutante_terremoto_putrido`, `demonio_ceifa_infernal`, `humano_coquetel_querosene`, `tecnomancer_tempestade_bobina`), então nenhum id é trocado. Custo, recarga, multiplicador e raio vêm de lá; nome, descrição, FX e ícone vêm daqui. Só o 1º alvo atingido gera recurso. Desbloqueios nos níveis 1, 3, 5, 6, 9 e 12 (o Humano tem a Armadilha de Prata no 15). Poções: vida P 6, vida M 18, recurso P 8 (40%), recurso M 22 (80%), pilha de 100.
Uma por classe, feitas para farmar em spots e para o modo automático: Leque do Juízo (Anjo), Espinhos de Sangue (Cultista), Terremoto Pútrido (Mutante), Ceifa Infernal (Demônio), Coquetel de Querosene (Humano) e Tempestade de Bobina (Tecnomancer).
Cada uma tem `formato_area` (cone ou círculo, raio, ângulo), dano por alvo, custo, recarga e `economia_auto`: quanto gasta e ganha por segundo e quantos segundos de uso contínuo aguenta do recurso cheio (~20 s; Cultista ~40 s até 25% de HP).
A proposta do modo automático e das poções está em `skills.json > modo_automatico`. Tudo PROVISÓRIO até a thread Design do combate fechar a economia de mana e poções.

## Pacto do Familiar (2026-10-11)
O Cultista ganhou a **racial Pacto do Familiar** (`cultista_familiar_pacto`, `tipo: racial`, não ocupa slot nem tecla; o Servo de Carne continua), a pedido do Jefin:
um demônio permanente que anda com o Cultista, ataca quem bater no mestre e evolui com o nível dele (Diabrete de Fuligem no 1,
Algoz de Enxofre no 6, Tirano da Fornalha no 16). Números em `classes_base.json > cultista > racial > familiar`;
plano de sprites e prévia em `design/personagens/familiar_cultista.md`. Falta o ícone da racial (motivo novo em `tools/icones/`).

## Anéis e túnicas padrão (2026-10-15, arte pronta do Jefin)
O Jefin mandou a arte pintada de 16 anéis (8 simples, 8 com gema) e 8 túnicas: são os **itens padrão** do jogo, e a regra dele é
**quanto mais bonito o item, mais atributos**. Folhas originais em `assets/icones/fontes/` (`aneis_simples.png`, `aneis_gemas.png`,
`tunicas.png`, grade 4x2). Dados em `fontes/itens_data.py` (`ANEIS_SIMPLES`, `ANEIS_GEMAS`, `TUNICAS`).

- Raridade **rolada** como as outras bases (comum a excelente, com as opções de `drops.json`), tags `equip:faixa1`/`faixa2` pelo nível.
- Anéis simples: nível 1 a 11, 2 a 9 pontos de atributo. Anéis com gema: nível 7 a 15, 6 a 18 pontos, mais HP e um bônus fixo.
  Túnicas: peito de pano para **todas as classes**, nível 1 a 15, defesa 1 a 9, atributos e HP crescentes. Item não muda o visual (só a arma).
- Campos novos que o jogo precisa ler (`game/scripts/sim/`):
  - `bonus_fixo`: somar em `Itens.bonus()` com as mesmas chaves do dicionário (`hp`, `defesa`, `dano_plano`, `critico`,
    `velocidade_ataque`, `roubo_de_vida`, `reduz_dano`, `dano_magico_extra`, `ouro`, e `res: {elemento: valor}`).
  - `peso_drop` (1,0 a 0,15): peso na escolha do item em `Loot.item_da_tag`; sem ele os 24 itens sem classe dominariam os drops.
    Os mais bonitos caem menos. Itens sem o campo valem 1,0.
  - `colecao` (`aneis_simples`, `aneis_gemas`, `tunicas`) e `arte` (folha e índice): só para ferramentas.
- Ícones: `cd tools/icones && PYTHONPATH=. python3 arte_pronta.py` (só pillow e numpy). O `gerar_itens.py` pula esses itens.

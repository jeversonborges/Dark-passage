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

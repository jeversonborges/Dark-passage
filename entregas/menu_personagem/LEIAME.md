# Menu do personagem, arca e kit de janelas (15/10/2026)

Pedidos do Jefin: menu do personagem onde se equipa e guarda, com incentivo a isso; arca maior; e depois "menus
mais charmosos, com moldura e botões com sombreamento, cara de MMORPG". A barra de skills e vida não foi tocada.

Prévias: `previa_equipamento_e_arca.png`, `previa_comparacao.png`, `previa_abas.png`.

## O que muda no jogo

- **Todas as janelas** ganham o kit "Ferrugem Sagrada": moldura de ferro e latão com cantoneiras e medalhões,
  fundo de couro curtido, placa de título, botão de fechar em medalhão, botões em relevo (normal, hover, pressionado,
  desativado), abas, caixas internas, barra de rolagem e tooltip com moldura de latão. Vem pelo tema
  (`Tema.tema_janelas()`), então janelas novas pegam o estilo sozinhas.
- **Equipamento (I/B):** retrato animado do personagem num arco de vitral, 10 slots em volta (glifo gravado quando
  vazio), placa de **Poder** (um número de dano por segundo + quanto aguenta).
- **Incentivo a equipar:**
  - seta verde pulsando nos itens da mochila que deixariam o personagem mais forte, e "N melhorias na mochila" ao
    lado do Poder;
  - o slot vazio ou pior fica com moldura verde quando há algo melhor na mochila; o tooltip dele diz qual item;
  - tooltip de item mostra "Se equipar: Poder 68 → 129 ▲ +61", dano, defesa, vida, crítico e velocidade
    (simula a troca no cliente com `Regras.recalc_jogador`, anel escolhe o pior dos dois, duas mãos tira o escudo);
  - ao equipar, o ganho sobe da placa em verde com um som curto.
- **Arca (12x12, o tamanho que a Prévia já subiu):** contador "N de 144 espaços livres" e botão
  **Guardar materiais** (manda todo material e joia da mochila para a arca; a posição é escolhida no cliente e cada
  movimento passa pelo `mover_item` de sempre, que o servidor confere).
- Ouro e munição foram para o lado da placa de Poder; as janelas ficaram mais baixas e não cobrem mais a barra.

## Aplicar

    cd /mnt/project-files && patch -p1 < entregas/menu_personagem/menu_personagem.patch
    bash game/tools/sync.sh      # traz as peças novas (assets/ui/hud/1x/menu_*.png) para assets/ext/ui

Arquivos: `game/scripts/client/janelas.gd`, `tema.gd`, `hud.gd` (só o painel do tooltip) e
`game/tools/teste_visual.gd` (roteiro `menu`).
Feito em cima da versão da pasta compartilhada de 15/10 ~22:50 UTC (já com automático e troca).

Teste: `godot --headless --check-only` limpo em janelas, tema, hud e game; teste visual
`xvfb-run godot --rendering-driver opengl3 -- classe=humano fotos=DIR roteiro=menu` gera as prévias.
Sem as peças `menu_*` o código volta ao visual antigo (nada quebra).

## Rede e versão

Só cliente. Nenhum comando novo, nada no save. Pode sair com qualquer versão do servidor que já tenha a arca 12x12.

## Kit para outras telas

- `Tema.sb_ui(peca, margens, conteudo)`: qualquer peça como 9-slice.
- `Tema.caixa_menu(conteudo)`, `Tema.estilo_aba(botao, ativa)`, `Tema.estilo_fechar(botao)`.
- Peças (1x e 2x em `assets/ui/hud/`): `menu_moldura` (margem 56), `menu_titulo` (60 nas laterais), `menu_botao`,
  `_hover`, `_press`, `_off` (14), `menu_aba`, `menu_aba_ativa`, `menu_fechar`, `menu_caixa`, `menu_dica`,
  `menu_slot` (+ `_hover`, `_pronto`, `_ruim`), `menu_glifo_*`, `menu_pedestal`, `menu_poder`, `menu_celula`,
  `menu_seta`, `menu_divisor`, `menu_rolagem_*`.
- Fonte: `assets/ui/src/menu/pecas_menu.html` (mesmo método da barra: sirva a pasta com as texturas `tex_*.svg` e
  `fonts/` de `assets/ui/src/barra` e rode `node shot.js pecas_menu.html --pecas saida 1` e depois com escala 2).

Nada foi publicado.

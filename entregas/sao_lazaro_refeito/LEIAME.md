# São Lázaro refeita (Vigília, 1890) · entrega para a Prévia (0.9.5)

Pedido do Jefin (18/10/2026): a região inicial da Vigília reimaginada como **uma cidade do século XIX, soturna mas
linda**, legível em isométrico (sem prédios gigantes), com paredes que bloqueiam de verdade. Liberdade total de layout.

## O que tem aqui

| Arquivo | O quê |
|---|---|
| `area_inicial.json` | O mapa novo, no **mesmo formato** do anterior (`design/mapas/area_inicial.json`). 200x200 com moldura de 20; área jogável 160x160. |
| `spots.json` | Os 13 spots e as 7 fogueiras (ids das missões mantidos). |
| `imagens/` | Prévias com a arte real do kit: `visao_geral.jpg`, `cidade.jpg`, `praca_matriz.jpg`, `rua_direita_estacao.jpg`, `mercado_casario.jpg`, `largo_bondes.jpg` e as áreas de fora. `planta_colisao.png` é a planta de bloqueio (laranja = base dos prédios; claro = andável a partir do spawn). |
| `kit_1890.png` | As peças novas do kit lado a lado. |

Fontes (gere de novo com `cd design/mapas/sao_lazaro_refeito/fontes && python3 montar.py && python3 layout.py && python3 teste_colisao.py && python3 overview.py ../../../../entregas/sao_lazaro_refeito/imagens`):
- `design/mapas/sao_lazaro_refeito/fontes/cidade_1890.py`: a cidade (a única parte escrita do zero);
- `montar.py`: monta o `layout.py` a partir do gerador anterior (`design/mapas/sao_lazaro/fontes/layout.py`) trocando a cidade, as ruas, a colisão e alguns pontos; o resto do deserto (spots, mobs, NPCs, cemitério, abatedouro, rio, ilha) continua igual;
- `teste_colisao.py`: o teste de colisão (abaixo);
- `cena2d.py` / `overview.py` / `dbg.py`: prévias e planta.

## O kit novo: `sao_lazaro_1890` (`assets/ambiente/fontes/sao_lazaro_1890.py`)

16 peças, no padrão de materiais e luz do kit (bpy 4.2, 64 px/m, câmera do jogo). Já publicadas em `assets/ambiente/objetos/`
(o `sync.sh` leva para o jogo). Sobrados com `_a` (fachada para baixo-esquerda) e `_b` (fachada para baixo-direita).

| Peça | O quê |
|---|---|
| `sobrado_ocre`, `sobrado_rosa`, `sobrado_azul`, `sobrado_verde`, `sobrado_loja`, `sobrado_ruina` | sobrados de dois andares (o andar de baixo era o 4º antes da areia: a janela virou porta, com degraus de tábua), janelas de arco com veneziana, sacadas de ferro batido, cimalha, telhado de barro ou platibanda com urnas, remendos de zinco da Vigília, uma janela acesa |
| `sobrado_esquina` | esquina com a porta chanfrada no canto e o relógio de rua |
| `casario` | três casas geminadas (ocre, rosa, branca) |
| `radio_sao_lazaro` | a Rádio: sobrado de platibanda da antiga Companhia Telefônica, mastro de treliça com a luz vermelha, cornetas, fios para a rua |
| `coreto`, `chafariz`, `quiosque`, `poste_relogio`, `banco_praca` | a praça |
| `mercado_ferro` | o Mercado Municipal de ferro e vidro (onde ficam Gaspar, Mãe Cardo, Tobias e Celina) |
| `portao_cidade` | portão da Cerca: pilares com braseiros, folhas abertas; **bloqueia só nos pilares** (`passagem`) |

Cada peça devolve **`base`** (xmin, ymin, xmax, ymax em metros): o chão que as paredes ocupam. É isso que o layout usa
para bloquear; a `footprint_tiles` continua só para o espalhamento.

## A cidade

Um eixo só, lido de cima para baixo na tela: **Igreja Matriz** (no alto, com os jardins e as alamedas de ciprestes dos
dois lados) → adro → **Praça da Matriz** (coreto no meio, chafariz no eixo, a Vela ao lado, a Arca do Gustavo, o
quiosque de velas e o relógio de rua) → **Rua Direita** → **Cúpula da Estação** → **Rua dos Bondes** (trilhos da Linha 7,
o bonde-veleiro atracado, o posto da Odete) → **Largo dos Bondes** → Cerca sul.

Ruas em grade: Rua de Cima (y=105), Rua Direita (y=70), Rua dos Bondes (y=58); Beco da Rádio (x=22), Rua da Matriz
(x=38), Rua do Mercado (x=57), Travessa da Forja (x=75). Quadras: **NW** Rádio (Isaura) + Enfermaria no sobrado verde
(Anselmo e Lindalva); **NE** Casario + Mercado de Ferro (Gaspar, Mãe Cardo, Tobias, Celina); **SW** dois sobrados;
**S** a Estação; **SE** o Armazém (Gustavo mora em cima) e o Sobrado de Esquina; **Largo** a Pensão da Linha 7 e a
casa em ruína, o guindaste e a caixa d'água. A **Cerca** é um muro de tijolo retangular (20..78 x 46..108) com 7
portões e torres de vigia nos cantos; o Damião fica no portão leste.

Nada é sorteado dentro da Cerca: tudo está posto à mão. Os prédios enterrados gigantes (`predio_enterrado`,
`predio_concreto`) saíram da cidade, do Bairro Afogado, da Vila Militar e do deserto aberto (viraram `sobrado_ruina`,
`sobrado_azul` e `casa_ruina`).

Ids que continuam valendo: zona `acampamento_vela` (agora o retângulo da Cerca; zona segura com raio 32 em 49,77), todos
os `ponto`s dos NPCs e das missões (`a_vela`, `arca_primarca`, `posto_odete`, `plataforma_bondes`, `portao_cupula`,
`forja_bigorna`, `caldeirao_cardo`, `carrinho_tobias`, `forno_vidro`, `barraca_anselmo`, `enfermaria_lindalva`,
`radio_sao_lazaro`, `costelas_cupula`, `porta_matriz`, `matriz_sao_lazaro`, `poco_praca`, `poco_jardim`, `cartaz_agrak_vela`,
`loja_corvina`...), os 13 spots e as 7 fogueiras.

O que mudou de lugar fora da cidade (pequeno): a Linha 7 passa em y=58 (antes 70) e o ramal do Pátio sai pelo portão
sul; o Marco do Corte foi para (92, 52); Covas Rasas para (94, 94); Cemitério de Bondes para (24, 31); a Mata dos Cardos
para (64, 118); a Fogueira do Pátio e a do Espantalho se afastaram da Cerca. A estrada para Jerusalém
(`ligacoes.py`, Estrada dos Peregrinos) agora começa fora do portão oeste da Rua de Cima (37.5, 125.5 no jogo).

## Colisão (o pedido de "não atravessar construção")

Antes, o bloqueio vinha de `footprint_tiles` x 0,7 centrado na âncora, que para vários prédios era menor que a parede.
Agora:
- toda peça do kit novo traz `base`; as peças antigas grandes (capela, cúpula, frigorífico, casa em ruína, torres,
  bondes...) têm a base à mão em `BASE_FIX` no `layout.py`;
- `add()` bloqueia **toda célula que a base toca** (+30 cm de folga) e grava `base` no prop do JSON;
- `teste_colisao.py` confere no JSON final: (1) nenhuma célula de parede livre; (2) do spawn se chega a todo NPC, spot,
  baú, objeto, portão, fogueira e ponto; (3) ruas inteiras e sem bolsão fechado dentro da Cerca; (4) nenhuma célula
  andável dentro de base. Sai com código 1 se falhar. Resultado desta entrega: **OK** (ver `teste_colisao.txt`).

## Para a integração (0.9.5)

1. `sync.sh`: trocar `entregas/cidade_sao_lazaro/` por `entregas/sao_lazaro_refeito/` nas duas cópias do mapa
   (o ramo `claude/sao-lazaro-095` já faz isso e traz o `game/` regerado).
2. `game/tools/mapa.py` lê o formato sem mudar nada; os kinds novos chegam pelo `sync.sh` (assets/ambiente/objetos).
3. `ligacoes.py` (design/mapas/mundo/fontes) já aponta a Estrada dos Peregrinos para o portão oeste.
4. Missões: nenhum JSON de `design/missoes/` mudou; os pontos têm os mesmos ids.

## Arte que falta (já na `entregas/arte_itens/LISTA.md`)

Continuam pendentes do mapa anterior: `antena_radio` (repetidora do Bairro Afogado), `flor_absinto`, `varal_lanternas`,
`escotilha_silo`. Nenhum ícone novo.

# Familiar do Cultista: plano de sprites (v0.1, 2026-10-11)

Pedido do Jefin: o Cultista troca uma skill por um pet demônio que anda com ele o tempo todo, evolui nos
níveis 1, 6 e 16, protege o mestre e ataca quando o mestre é atacado.

- **Skill que saiu:** Servo de Carne (`cultista_servo_carne`, invocação temporária de 20 s). O Cultista já
  era o "invocador" da facção, então o familiar ocupa o mesmo papel, só que permanente.
- **Skill nova:** Pacto do Familiar (`cultista_familiar_pacto`, nível 1). Dados em
  `design/skills-itens/skills.json` (gerado por `fontes/skills_data.py`) e números em
  `design/combate/classes_base.json > cultista > invocacoes > familiar_do_pacto`.
- **Prévia:** `familiar/previa.png` (idle SE em 2x ao lado do Cultista) e `familiar/*_idle_SE.gif`.

## As três formas

| Forma | Nível do mestre | Altura | Quadro | Silhueta |
|---|---|---|---|---|
| Diabrete de Fuligem (`familiar_diabrete`) | 1 a 5 | 0,75 m | 160 px | cabeção, orelhas de morcego, asinhas rasgadas, rabo em S erguido |
| Algoz de Enxofre (`familiar_algoz`) | 6 a 15 | 1,9 m | 256 px | curvado, capuz de carrasco com chifres serrados, cutelo enorme |
| Tirano da Fornalha (`familiar_tirano`) | 16+ | 2,7 m | 352 px | chifres de carneiro, duas chaminés, canhão no braço direito, perna de pistão |

Regras da Ferrugem Sagrada aplicadas: demônios vestidos (avental, capuz, saiote, tabardo), sujeira,
latão e ferro enferrujado, **um só emissivo** (brasa laranja: olhos, boca, fornalha, cano do canhão),
contraluz laranja-brasa, 8 direções, 64 px/m, paleta indexada de 44 cores com 4 reservadas ao brilho.
O fio que liga as três formas é o **lacre de cera vermelha do pacto** (coleira do Diabrete, peito do
Algoz, corrente no peito do Tirano) e o rabo de ponta de seta.

## Pipeline

Módulo `tools/sprite-pipeline/monstros/familiar.py`, uma variante por forma (estilo MU):

    cd tools/sprite-pipeline/monstros
    blender -b -P render.py -- familiar:diabrete /tmp/brutos/diabrete
    python3 process.py /tmp/brutos/diabrete /mnt/project-files/assets/monstros/familiar_diabrete 44 .5
    # idem familiar:algoz e familiar:tirano

Saída final em `assets/monstros/familiar_<forma>/` (mesmo formato dos monstros: folha por animação,
8 linhas de direção, `meta.json`).

## Animações a fazer (só o idle existe, para a prévia)

| Animação | Diabrete | Algoz | Tirano | Notas |
|---|---|---|---|---|
| `idle` (loop) | ✓ 6q | ✓ 6q | ✓ 6q | feito |
| `walk` (loop) | 8q, saltitante, asas batendo | 8q, passo pesado de bode | 8q, pistão bombeando, vapor | precisa acompanhar o mestre (vel. 1,1x) |
| `attack` | 8q, cospe brasa | 10q, golpe de cutelo de cima | 10q, soco com a manopla | o jogo cria o projétil do Diabrete |
| `special` | – | 10q, Puxão de Corrente (corrente esticada, osso escondido fora dela, como o `pull` do Gancheiro) | 12q, Canhão de Brasa (recuo, vapor) + 10q Rugido | |
| `hit` | 3q | 3q | 3q | |
| `death` | 8q, vira fuligem no chão | 8q, ajoelha e tomba | 9q, desaba, fornalha apaga | segurar o último quadro; volta em 30 s |
| `evolve` | 12q | 12q | – | casulo de brasa e carne de 2 s; o jogo troca para a próxima forma no último quadro |
| `spawn` | 8q, sai da fumaça do lacre | 8q | 8q | quando a tecla reinvoca |

Efeitos para a thread Efeitos visuais: cuspe de brasa, corrente com gancho em brasa, tiro do Canhão de
Brasa com anel de fogo no chão, fumaça das chaminés (partícula leve em loop), casulo da evolução.
Sons para Som e música: risadinha do Diabrete, corrente arrastando, rugido grave com escape de vapor.

## Para a Prévia jogável (integração em `game/`)

O familiar usa a lógica genérica de invocação (`invoca` na skill) com três diferenças: é permanente
(`permanente: true`), escolhe a forma pelo nível do dono (`formas[].nivel_dono`) e só ataca quem bateu
no dono, quem bateu nele ou o alvo da tecla (`alvo.prioridade`, nunca puxa neutro parado). Os ids
antigos `servo_carne` e `servo_de_carne` saíram de `classes_base.json`.

# Mechanicus: Juízo de Ferro (robô gigante)

Status: **fase 1, rascunho para aprovação do Jefin.** Só design, dado e ícone placeholder. Modelo 3D e animações (fase 2) só depois do OK.

Números **PROVISÓRIOS**: o balanceamento final é da thread de combate. Dado em `design/combate/mechanicus_robo.json`.

## Conceito

Ultimate do **Mechanicus** (evolução do Tecnomancer no nível 30). É a assinatura visual da classe: o Mechanicus convoca um colosso de ferro que anda ao lado dele, atira e pisa o chão. Referência de silhueta: **Liberty Prime** do Fallout 4 (`design/arte/mechanicus_robo/liberty_prime_ref_1.jpg` e `_2.jpg`).

Em "Ferrugem Sagrada": aço enferrujado, bronze oxidado, placas soltas com remendos, correntes e fiação, luzes vermelhas nos olhos, exaustores soltando fumaça. Capacete tipo escafandro com visor. Nada de brilho limpo: o robô é um altar de guerra feito de sucata. Só **um** emissivo forte: o visor vermelho (dentro da regra de 1 cor emissiva por personagem).

## Ficha da skill

| Campo | Valor provisório |
|---|---|
| Nome | **Juízo de Ferro** (alternativa: Avatar Mecânico) |
| Classe | Mechanicus (evolução do Tecnomancer) |
| Nível | 30 |
| Tipo | suprema (invocação) |
| Custo | 60 Carga |
| Recarga | 120 s |
| Duração | 30 s |
| Tamanho | ~4 tiles de altura (bem maior que qualquer personagem) |
| HP próprio | 1800 + 40 × nível do Mechanicus (sem regeneração) |
| Elemento | físico (pisão) e elétrico (descarga do visor) |

## Comportamento

- **Segue** o Mechanicus a 2 tiles. Anda devagar (mais lento que o jogador), para quando ele para.
- **Incontrolável** (regra do Jefin): o jogador não escolhe alvo e não dá comando. Ataca o inimigo mais próximo num raio de 10 tiles e troca de alvo livremente sempre que outro ficar mais perto. Alterna dois golpes:
  - **Metralhadoras do Juízo (giratórias, estilo minigun):** os braços são as armas, com canos múltiplos girando. Em vez de mirar num alvo, o robô varre uma **zona de tiro** visível: um leque de 60° e 8 tiles de alcance, desenhado no chão por decal e marcadores de impacto. O dano cai em quem estiver dentro da zona a cada tick de 0.5 s, mult 0.35 (ESP) por tick. Quem sair da zona antes do próximo tick se livra, então o golpe é esquivável. A zona gira em direção ao alvo mais próximo, a 120° por segundo, e troca de alvo junto com o robô.
  - **Descarga do visor:** raio curto e largo na frente, mult 1.1, a cada 5 s.
- **Pisão ao andar:** a cada 4 passos (ou 4 s andando), bate no chão numa área de raio 2 tiles. Mult 0.9, 20% de chance de atordoar 0.5 s. A tela treme (leve).
- **Quem ele ataca:** qualquer inimigo no raio, inclusive mobs que já estão em combate com outros. Mobs neutros parados não são atacados. O robô **não chama vizinhos** para a briga: puxada em cadeia quebra a regra "menos Diablo, mais WoW". Esse é o risco da ulti: ele pode arrastar uma luta que o jogador não queria.
- **Fim:** some ao acabar a duração ou quando o HP próprio zera. Ao sumir, solta fumaça e uma faísca no chão. Se morrer, a recarga começa do mesmo jeito.
- Não funciona em área segura (cidade). Só uma invocação do tipo por Mechanicus.

## Feedback visual e sonoro

- **VFX:** fumaça e vapor dos exaustores nas costas, luz vermelha dos olhos, faíscas nas juntas, canos girando com faíscas, decal no chão mostrando onde os tiros caem, cartuchos, pisadas com poeira e estilhaço de ferrugem.
- **Tremor de tela** só nos pisões e nas rajadas mais longas (intensidade pequena).
- **Som:** pisada metálica grave e oca, zumbido de motor das metralhadoras que sobe ao varrer, chiado de válvula, voz robótica distorcida e curta no início e no fim (não repetir a cada golpe).

## Padrão de animação (fase 2)

- Qualidade alta, sem sprite básico. Inclui a animação dos tiros: tracers, impacto, cartuchos ejetados e faíscas.
- Seguir a skill de animação e de VFX da biblioteca vendorizada em `tools/sprite-pipeline/vendor/blender-skills-arjun988/`.
- QA pass antes de entregar. Referência de qualidade: o kit do Egito.
- Nada começa antes da aprovação do design.

## Pontos em aberto para o Jefin

1. Nome: **Juízo de Ferro** (sugestão) ou Avatar Mecânico?
2. Mesma ulti em estágio 3 (nível 400) ou só a do 30?
3. Cooldown de 120 s está bom ou prefere 90 s?

## Próximas etapas

- **Fase 1 (esta entrega):** design, dado em `design/combate/mechanicus_robo.json`, ícone placeholder em `design/arte/mechanicus_robo/`.
- **Fase 2 (depois do OK):** modelo 3D do robô por código no Blender (`tools/sprite-pipeline/`), animações de andar, atirar e pisar, e VFX/sons.

## Notas de dado

- `design/combate/classes_base.json` só vai até o nível ~13, então a skill fica no JSON próprio do Mechanicus e não no `classes_base.json`. A Prévia decide se a integra ao gerador de skills.
- `design/classes.md` e `CLAUDE.md` ainda dizem que os estágios de classe são no 150 e no 400. A evolução no nível 30 vem da decisão do Jefin registrada na memória do projeto. Precisa de uma revisão dos documentos antes do release.

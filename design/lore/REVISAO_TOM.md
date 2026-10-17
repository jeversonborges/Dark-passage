# Revisão de tom dos textos atuais (17/10/2026)

Varri `missoes.json`, `dialogos.json`, `itens.json`, `npcs.json`, `monstros.json`, `objetos.json`, `locais.json`,
`citacoes.json` e `biblioteca.json` com as listas da §8.2 do GUIA (termos de jogo dentro do mundo, gíria de hoje,
anacronismo, clichê de fantasia, melodrama). Li por amostragem 14 diálogos, 6 missões e 6 citações.

## Veredito

Os textos estão no tom. A regra das vozes está sendo cumprida nas missões (cabeçalho, ordem, assinatura) e nas
citações; os diálogos têm gente no meio de algo quando o jogador chega ("Meio tom abaixo!", "Não encoste na bobina",
"Não no caixote, que é meu"). Nenhuma gíria de hoje, nenhum anacronismo, nenhum "escolhido" ou "mal ancestral".

## O que a varredura achou (nada para corrigir em texto do jogador)

| Achado | Onde | Veredito |
|---|---|---|
| "XP", "drop", "skill" | campos `nota`, `origem`, `efeito` | metadados e texto de ficha técnica, não fala do mundo; permitido pela §5.10 |
| "trevas" | missões e falas do Egito | é a nona praga (Êxodo 10); correto |
| "reino" | missão da Esfinge | a promessa de Tutmés IV na Estela do Sonho; correto |
| "de boa" | Dalva | "de boa vontade"; falso positivo |
| "quer você queira ou não!" | fala de Zacarias ao ver | uma exclamação, de quem grita de verdade; dentro da regra |
| "drone" | `musica_sugerida` de Amenti | nota para a thread de Som, não texto de jogo; sugiro "bordão grave" para não confundir |

## Duas observações de estilo para as próximas rodadas (não são erros)

1. **Tríades automáticas** em algumas `historia` de NPC ("Fumaça calma, abelha calma, Rute calma"). O GUIA agora tem a
   regra (§3.11). Não vale reescrever o que existe; vale não repetir.
2. **"X, o Y" em todo chefe.** Os três da Cripta e os do Egito já têm; os da Torre ganharam no site epítetos
   diferentes dos dados (ver `REVISAO_SITE.md`). Decidir um por chefe e usar o mesmo em todo lugar.

Nada vai para a Prévia como correção de texto; só os renomes de `renomes.md`.

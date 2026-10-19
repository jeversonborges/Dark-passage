# Guerreiro Iniciante (Arautos do Juízo)

> Rascunho v0.1 (19/10/2026). Os números valem o `guerreiro.json` (este `.md` resume). Ainda não está em `classes_base.json`: entra lá quando o Jefin aprovar, para não virar selecionável no servidor antes da hora.

**Arquivos:** `guerreiro.json` (classe, evolução Paladino e Duelista) · `design/arte/guerreiro/` (as 3 artes de referência e os ícones placeholder).

## Visão geral

**Papel:** tanque e dano físico corpo a corpo, sem magia. Primeira classe do Arauto que luta de perto com aço, sem fé nem sangue.
**Facção:** Arautos do Juízo (fica com 4 classes: Anjo, Cultista, Demônio e Guerreiro).
**Atributos iniciais:** FOR 26 · AGI 18 · VIT 24 · ESP 12. Build sugerida: FOR e VIT.
**Arma inicial:** Espada Curta do Recruta (1 mão, 5 a 8 de dano, intervalo 1,0 s).
**Recurso: Ímpeto (0 a 100).** Proposta minha, o kit não definiu um: sobe ao acertar (+6) e ao apanhar (+4), cai 4 por segundo fora de combate. Jefin confirma ou troca.

**Fantasia:** o recruta que foi mandado para a linha de frente do Juízo e nunca voltou atrás. Sobretudo vermelho, espada, sem poder nenhum além de se manter de pé.

## Ataque básico

**Golpe de Espada:** ataque físico corpo a corpo em alvo único. Usa a espada de 1 mão. Sem recarga.

## Habilidades (nível 1 a 30)

| Nível | Habilidade | Tipo | Custo (Ímpeto) | Recarga | Efeito |
|---|---|---|---|---|---|
| 1 | Corte do Recruta | Ativa | 10 | 3 s | Ataque físico em alvo único, mais forte que o básico (1,6x) |
| 1 | Determinação do Recruta | Passiva | — | — | +8% HP máximo e +5% ataque físico, permanente |
| 3 | Varredura de Aço | Área | 12 | 2 s | Giro de 360º em volta do guerreiro (estilo hack and slash), 0,9x em todos num raio de 5 tiles |
| 6 | Guarda Firme | Buff | 15 | 20 s | +30% defesa física por 8 s (em si) |
| 9 | Quebra-Guarda | Debuff | 15 | 15 s | Alvo perde 25% de defesa física por 6 s (0,8x de dano) |

**Visual da Varredura:** giro completo do corpo com a espada passando por todos os ângulos e um rastro luminoso fechando o círculo. Referência do Jefin em `design/arte/skills/rodar_espada_ref/` (GIF e JPG). Mesmo tratamento para o Redemoinho de Aço do Warlord e para futuras skills de rodopio.

**Obs.:** os níveis de desbloqueio (1, 1, 3, 6, 9) são escolha minha, seguindo a escala do Anjo e do Demônio. Os tempos de recarga e duração são os do kit do Jefin.

## Evolução no nível 30

Escolha única entre dois caminhos. Os dois mantêm o Ímpeto.

### Paladino (o da espada grande, tanque pesado)

**Papel:** tanque pesado e controle de área. **Arma:** Espadão do Juramento (2 mãos, 10 a 15 de dano, intervalo 1,7 s). +25% HP máximo, +4 de HP por VIT.

| Nível | Habilidade | Tipo | Efeito |
|---|---|---|---|
| 30 | Golpe Devastador | Ativa | 2,8x de dano em alvo único, 30% de chance de atordoar por 1 s |
| 30 | Juramento de Ferro | Ativa | Cura 10% do HP máximo e provoca inimigos por 6 s (puxa a atenção) |
| 30 | Couraça do Paladino | Passiva | +10% defesa física |
| 33 | Reflexo de Aço | Buff | Reflete 50% do dano recebido por 3 s |
| 36 | Investida da Couraça | Mobilidade | Avança 4 tiles, 1,5x de dano e atordoa por 1,5 s |

### Duelista (assassino de dupla lâmina)

**Papel:** maior velocidade de ataque do jogo, burst e golpe pelas costas. **Arma:** duas espadas de 1 mão, uma em cada mão (3 a 5 de dano por golpe, intervalo base 0,5 s). +35% velocidade de ataque. HP máximo -15%, pouca defesa.

| Nível | Habilidade | Tipo | Efeito |
|---|---|---|---|
| 30 | Passo Sombrio | Mobilidade | Teleporta para trás do alvo (alcance 6), fica furtivo por 1,5 s |
| 30 | Golpe Mortal | Ativa | 1,8x de dano; pelas costas, crítico de 2x |
| 30 | Dupla Lâmina | Passiva | Golpes alternados entre as mãos somam +10% de ataque |
| 33 | Relâmpago de Lâmina | Combo | 3 golpes rápidos de 0,6x (combo de curta distância) |
| 36 | Rajada Gêmea | Área | 6 golpes em 1,5 s, 0,5x cada, em área de 1,6 tile (burst) |

**Inspiração:** o Duelista do Lineage 2 (Shadow Step, golpes de burst, golpe crítico atrás do alvo), com o estilo de rogue do jogo.

## Pendências e decisões

- **Ímpeto:** recurso proposto por mim (o kit não trouxe). Confirmar.
- **Níveis de desbloqueio** da base e das evoluções: escolha minha, ajustar se o Jefin quiser outra curva.
- **Evolução no nível 30:** segue o pedido atual do Jefin. O `classes.md` v0.1 ainda diz estágios em 150 e 400 para as outras classes. Vale alinhar.
- **Sensações novas:** `buff` e `passiva` não existem ainda na lista de sensações do cliente; precisam de VFX/som quando a classe entrar.
- **Ícones:** 16 placeholders (base 6, Paladino 5, Duelista 5) nos tamanhos 64, 40 e 32, com o nome escrito. Em 32 px entram só as iniciais. O Jefin pinta os finais.
- **Entrada no jogo:** nada de código mudou. Para liberar a classe, mover `guerreiro` para `classes_base.json` e rodar `design/skills-itens/fontes/gerar_json.py`.

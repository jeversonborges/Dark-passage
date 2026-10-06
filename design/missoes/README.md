# Missões, NPCs e história (v0.1)

Primeiro pacote de conteúdo da **Paróquia de São Lázaro** (área inicial, nível 1 a 8) e da dungeon **Cripta da Trombeta Calada** (nível 6 a 12, 3 chefes nos níveis 8, 10 e 12).

- `historia.md`: a lore (o que aconteceu, as bases, o coveiro, os chefes, o arco do jogador, o tom de escrita).
- `dados/`: tudo em JSON para o jogo ler direto.
- `validar.py`: confere se todas as referências entre os arquivos batem. Rode depois de qualquer edição: `python3 validar.py`.

## Arquivos de dados

| Arquivo | O que tem |
|---|---|
| `locais.json` | Área, subzonas (2 bases + 4 zonas de caça) e os 3 andares da dungeon |
| `npcs.json` | 11 NPCs com aparência, personalidade, história, serviços |
| `dialogos.json` | Árvore de diálogo de cada NPC, com condições e ações |
| `missoes.json` | 27 missões: objetivos, requisitos, recompensas e textos do diário |
| `monstros.json` | 20 monstros com lore e aparência; elite, raro e 3 chefes com fases e falas de combate |
| `itens.json` | 56 itens: de missão, consumíveis, textos de leitura e equipamentos com nome |
| `objetos.json` | Objetos interativos e baús de história (inclui 3 baús de chefe e 1 baú amaldiçoado) |
| `lojas.json` | Estoque de história das lojas, ferreiros e treinador |

Números de combate (HP, dano, IA) e tabelas de drop genéricas não estão aqui: são da thread de combate e do sistema de loot. Os atributos dos equipamentos são sugestões.

## Fluxo das missões

```
VIGÍLIA                                ARAUTOS
v01 Pavio Curto (Odete)                a01 Primeira Oração de Sangue (Ivone)
v02 Cobre para a Vela (Anselmo)        a02 Penas dos Irmãos Caídos (Abdiel)
v03 Os Cães da Vala (Odete) [arma]     a03 Dentes para o Penhor (Malfas) [arma]
v04 Lacres Inteiros -> Simão           a04 A Espera dos Mortos -> Simão
                  \                   /
                   c01 Velas para os Mortos (Simão)
                   c02 O Livro de Óbitos (elite Capataz Gancho)
                   c03 A Porta Debaixo da Carne (entra na dungeon)
                   c04 O General Partido        (chefe 1: Andras)
                   c05 Silêncio no Ossário      (chefe 2: Irmã Celeste)
                   c06 A Trombeta Calada        (chefe 3: Zacarias) -> Simão
                  /                   \
v05 O Destino do Bocal                 a05 O Destino do Bocal
   destruir (Odete) ou estudar            Abdiel (anjos) ou Malfas (demônios)
   (Anselmo)
```

Secundárias: Mãe Cardo e o filho mutante (s01, s02), Gaspar e o último sino (s03), os baús do Tobias (s04, tutorial de baú), o relicário e a carta do Lúcio com escolha de trair ou não (s05, s06, s07), as covas do Simão (s08), as confissões dos emparedados na dungeon (s09). Diárias: r01 (Vigília), r02 (Arautos).

Deserto (níveis 5 a 12, as duas facções, rodam em paralelo; cada passo manda para um spot de farm):

```
Linha D: A Estrela Que Nós Soltamos         Linha E: A Legião Sem General
d01v (Anselmo) / d01a (Ivone) -> Isaura     e01v (Tobias) / e01a (Malfas) -> Corvina
d02 Antena no Telhado     fosso_dos_caes     e02 Desertores        acampamento_desertores*
d03 A Ordem das 03h11     margem_das_viuvas   e03 Veneno no Cálice  margem_das_viuvas [escolha]
d04 O Que a Água Lembra   acampamento_desertores* e04 O Marco do Corte  marco_do_corte*
d05 O Muro das Sombras    beira_da_tempestade  e05a (Malfas) / e05v (Odete), requer c02,
d06 Absinto-2 (elite Brandão) [escolha]         chiqueiro_do_carnica [escolha]
```

Os ids de spot são os da Level design (`design/mapas/spots.json`). Os marcados com * ainda foram pedidos à Level design e estão em `locais.json` → `spots.pedidos`. d01 usa `telhados_dos_corvos` e e01 usa `covas_rasas`.

## Regras do formato (para quem programa)

**Objetivos** (`missoes.json`): `matar {alvo, qtd}`, `coletar {item, qtd}`, `interagir {objeto, subzona, qtd, concede?}`, `usar_item {item, objeto, subzona}`, `explorar {subzona}`, `falar {npc}`, `decidir {npc}`, `farmar_spot {spot, qtd}` (qualquer monstro morto dentro da área do spot; ids de `design/mapas/spots.json`, mais os pedidos em `locais.json` → `spots.pedidos`). Um objetivo com `etapa` maior só começa a contar quando todos os de etapa menor terminam (sem `etapa` = 1).

**Campos da missão:** `requer` (todas), `requer_qualquer` (uma basta), `ao_aceitar_recebe`, `ao_concluir_inicia`, `falha_ao_aceitar`, `oculta` (não aparece em lista, só via diálogo), `escolhas` (cada escolha tem recompensas e flags próprias), `escolha_por_classe` nas recompensas, `entrega: "automatico"` (conclui sozinha quando os objetivos terminam).

**Diálogos:** cada nó tem `fala` (texto, ou lista de variantes `{se, texto}` em que vale a primeira que bate) e `opcoes`. Opção sem `ir` fecha a conversa; opção com `se` só aparece quando todas as condições batem.

- Condições: `missao_disponivel`, `missao_ativa`, `missao_pronta`, `missao_concluida`, `missao_nao_iniciada`, `faccao`, `flag`, `sem_flag`, `tem_item` (id, ou `{id, qtd}`). Quando o valor é uma lista de missões, basta uma.
- `missao_pronta` = todos os objetivos cumpridos, sem contar os de `falar`/`decidir` com o NPC da conversa atual.
- Ações: `aceitar_missao`, `concluir_missao` (+ `escolha`), `falhar_missao`, `cumprir_falar`, `abrir_loja`, `abrir_ferreiro`, `abrir_armazem`, `abrir_treinador`, `dar_item`, `remover_item`, `definir_flag`.
- Ao concluir uma missão, os itens dos objetivos `coletar` saem do inventário.

**Facção:** NPCs da Vigília só conversam com jogadores da Vigília e os dos Arautos só com Arautos. Simão e Frei Anacleto falam com os dois. Os monstros `patrulha_arauto` e `patrulha_vigilia` só aparecem para a facção inimiga.

**Flags que ficam para o futuro:** `bocal_destruido`, `bocal_estudo_vigilia`, `bocal_anjos`, `bocal_demonios`, `lucio_denunciado`.

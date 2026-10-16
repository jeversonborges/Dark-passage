# Jerusalém e Monte Hermon · área inicial dos Arautos

Para a thread **Prévia jogável e área inicial** integrar. Nada aqui publica cliente.

## A ideia

Os Arautos (Anjo, Demônio, Cultista) nascem em **Jerusalém**, a cidade santa onde o Juízo começou: Sariel abriu a
Porta Dourada no primeiro toque e o fim entrou, mas não terminou. Da cidade murada (pedra branca suja de cinza, a
Cúpula, a Brasa do Altar, a forja do Tubal) o caminho desce o **Monte das Oliveiras** (Getsêmani, a necrópole dos
mortos que levantaram primeiro), passa pelo **Vale de Josafá**, pela **Geena** (as fornalhas de Tofete) e sobe a
encosta dos cedros até as **Fontes do Jordão** e o **cume do Hermon**, onde os duzentos Vigilantes juraram antes do
dilúvio. A dungeon é o **Fosso dos Vigilantes**, atrás dos Portões do Hades (gruta de Pã).

Linhas de história próprias, no lugar das da Vigília:
- **O Juramento do Hermon** (espelho da D): o Coro afrouxou as correntes dos duzentos para ganhar a guerra; eles
  juraram de novo, "que o fim fique onde está". Por isso o fim travou. Kokabiel conta as noites.
- **O Trono da Geena** (espelho da E): a Legião sem general, o trono vazio, e o rastro de brasa que leva ao Andras.
- **O Escriba Que Não Morreu** (espelho da F): o Escriba do bosque é Henoc, que andou com Deus e voltou quando o fim travou.

## Por que é justo com a Vigília

Tudo é espelho numérico do deserto (detalhes em `espelho.txt`, gerado):
- **Spots:** os mesmos 10, com os mesmos níveis, quantidades, temperamentos (neutro/territorial/agressivo), respawn
  e motivo. Distância de cada spot à base dentro de ±30% da do deserto.
- **Mobs:** 149 no mundo (138 em spots), igual. Cada mob daqui usa os números do mob espelho (`base` em `dados.json`,
  sem `ajuste`). Mesmas tabelas de drop.
- **Missões:** 36, cópia estrutural das que a Vigília faz do 1 ao 12. **XP total de missão até o 12: 119.570 nos dois
  lados.** Mesmo ouro, objetivos, pré-requisitos e escolhas; itens de recompensa com os mesmos atributos.
- **Baús 23, fogueiras com Bartimeu 6**, iguais. **Dungeon:** 3 andares com as mesmas salas, grupos, níveis e
  números de chefe da Cripta da Trombeta Calada.

## Arquivos

| Arquivo | O que é |
|---|---|
| `gerar.py` | gera os 4 mapas, `dados.json`, plantas e `espelho.txt` (`python3 gerar.py`; usa `design/mapas/cripta/gerar.py`) |
| `jerusalem_hermon.json` | mapa da área (160x160), formato de `game/data/mapas/` |
| `minas_dos_gigantes.json`, `salao_das_noivas.json`, `altar_do_juramento.json` | andares 1, 2, 3 do Fosso |
| `dados.json` | mobs (formato `v06_extra`), sprites substitutos, chefes, aliases de drop, nomes do HUD, portais |
| `conteudo.py` | gera os `*_acrescimo.json` e confere com o `validar.py` de Missões (sai `OK`) |
| `*_acrescimo.json` | missões, NPCs, diálogos, itens, monstros, objetos/baús, lojas e locais para juntar em `design/missoes/dados/` |
| `planta_*.png` | plantas de conferência |

## Passos de integração

1. **Dados de missão:** juntar cada `*_acrescimo.json` à lista correspondente em `design/missoes/dados/`
   (`locais_acrescimo` → `areas`, `dungeons` e `spots.pedidos`); rodar `validar.py`; `sync.sh`.
2. **Mapas:** copiar os 4 JSON para `game/data/mapas/`. `jerusalem_hermon.json` tem `spawn_por_faccao.arautos`:
   personagem novo dos Arautos nasce em Jerusalém (Vigília continua no deserto).
3. **Mobs e chefes:** mesclar `dados.json` → `mobs` em `v06_extra.mobs`, `sprites` em `sprites_substitutos.json`,
   `chefes` em `CHEFES`, `drops_alias` em `DROPS`, `nomes_mapa_hud`.
4. **Chefes com mecânica espelho:** `chefe_ctl` escolhe o roteiro pelo id; os chefes daqui trazem `mecanica_de`
   (`general_partido`, `irma_celeste`, `zacarias_arauto`). Despachar por `CHEFES[id].get("mecanica_de", id)`, e usar
   os campos genéricos `invoca` e `nome` dos ataques (o mesmo pedido da integração da Mata).
5. **Casos especiais no código que precisam do par:**
   - `porta_do_altar` = mesmo tratamento de `porta_camara` (filtro dos dois selos: `selo_do_sonho`, `selo_das_aguas`).
   - `chave_de_pa` sempre cai do Capataz de Tofete, como `chave_gancho` em `loot.gd`.
   - `porta_de_pa` (interativo nas Fontes do Jordão) leva a `minas_dos_gigantes`, como `porta_ganchos`.
   - `laje_do_juramento` invoca `kokabiel_contador` (elite), como `escotilha_silo` invoca `ultimo_operador`.
   - `jogador.gd estoque()`: pôr `loja_hulda`, `loja_zilpa`, `loja_bartimeu`, `loja_carrinho_bartimeu`, `loja_zaqueu`
     na lista que recebe o estoque geral, e `loja_bartimeu`/`loja_carrinho_bartimeu` na de munição e armas da faixa 1
     (como `loja_tobias`).
   - Missão `g02` deve aceitar `g01` **ou** `jg01` como pré-requisito.
6. **Portais:** `dados.json → ligacao`: saída de Jerusalém para o deserto (nível 12) e volta perto da Capela de São
   Lázaro (acrescentar em `area_inicial.json` pelo `layout.py` do deserto).
7. **Missões antigas dos Arautos no deserto** (a01–a05, s05–s07, r02, d01a, e01a, e05a, f01a): personagem novo não
   precisa delas. Sugestão: esconder para quem nasceu em Jerusalém; quem já tem progresso continua.
8. **Balanceamento:** pedir à thread de Combate um `farm.py` com os spots daqui (devem dar o mesmo que os do deserto).

## Pendências para outras threads

- **Cenário:** `props_pendentes` do mapa: `cupula_da_rocha` (hoje usa `cupula_estacao`), `oliveira_morta`,
  `antena_radio`. O resto usa objetos que já existem.
- **Monstros:** os 21 mobs e 3 chefes usam folha recolorida (`usa` + `tint` + `escala`). Regra do Jefin: arte nova
  1 mob + 1 chefe primeiro (sugestão: Peregrino Ressecado e Ohya).
- **Som:** o mapa pede `porcos` e `martelo_forja`; se não existirem em `audio.json`, trocar ou pedir à thread de Som.
- **Personagens:** NPCs usam a arte das classes (`classe_visual`) até ganharem sprite próprio.

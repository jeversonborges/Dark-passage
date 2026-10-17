# Jerusalém, Monte Hermon e o Evento Hermon · integração na 0.9.3

Para a thread **Prévia jogável e área inicial**. Atualizado 17/10/2026. Tudo foi testado numa cópia do `game/` de
hoje (17/10 ~10:30 UTC): os dois patches aplicam limpos, `check.gd` compila tudo, `teste_hermon.gd` 50/50,
`teste_jerusalem.gd` 50/50. Nada aqui publica cliente.

O que entra:
- **Jerusalém e Monte Hermon**: área inicial dos Arautos (Anjo, Demônio, Cultista), nível 1 a 12, e a dungeon
  **Fosso dos Vigilantes** (Minas dos Gigantes, Salão das Noivas, Altar do Juramento; chefes Ohya, Naamá e Semyaza).
  Espelho do deserto: mesmos spots, níveis, temperamentos, baús, fogueiras e números de chefe.
- **O Cume dos Vigilantes**: evento diário às 19h (Brasília), o Chaos Castle do Hermon. Regras em
  `entregas/evento_hermon/LEIAME.md`.

## Passos (da raiz do repositório, nesta ordem)

```bash
# 0. numa sessão nova
[ -e /mnt/project-files ] || ln -s "$(git rev-parse --show-toplevel)" /mnt/project-files

# 1. código do evento (sim, servidor e cliente do Cume dos Vigilantes)
patch -p1 < entregas/evento_hermon/codigo/jogo.patch

# 2. código de Jerusalém (casa por facção, chefes espelho, portais, lojas, chave de Pã, sync.sh e mapa.py)
patch -p1 < entregas/jerusalem_hermon/integrar/jerusalem.patch

# 3. dados (missões, NPCs, itens, mapas, mobs, chefes, drops, sprites); pode rodar de novo sem estragar
python3 entregas/jerusalem_hermon/integrar/aplicar_dados.py      # termina com "validar.py ... OK"
python3 design/skills-itens/fontes/gerar_json.py

# 4. para dentro do jogo
cd game && bash tools/sync.sh
python3 ../entregas/teleporte/gerar.py data/mapas data/teleporte.json   # Jerusalém no menu V (10 destinos)
godot --headless --path . --import

# 5. testes
godot --headless --path . -s res://tools/check.gd               # todos "ok"
godot --headless --path . -s res://tools/teste_hermon.gd        # 50 ok, 0 falhas
godot --headless --path . -s res://tools/teste_jerusalem.gd     # 50 ok, 0 falhas
godot --headless --path . -s res://tools/sim_test.gd            # 6 classes e os 3 chefes da Cripta, sem SCRIPT ERROR
```

No PC do Jefin é o mesmo: os dois patches e o script estão no projeto compartilhado; quem copia o `game/` inteiro do
compartilhado depois do passo 4 não precisa repetir 1 e 2.

## O que o `jerusalem.patch` muda

| Arquivo | Mudança |
|---|---|
| `scripts/defs.gd` | `mapa_casa(faccao)`: Arautos nascem em `jerusalem_hermon`, Vigília em `area_inicial`. `mecanica_chefe(id)` lê `mecanica_de`. **Conserto:** as tabelas de drop do `v06_extra.json` entravam fora de `DROPS["tabelas"]`, onde o Loot procura (os chefes da Torre também não dropavam pela tabela deles). |
| `scripts/net/servidor.gd`, `client/game.gd` | personagem novo entra no mapa de casa da facção; a vinheta da cripta não toca ao entrar em Jerusalém. |
| `scripts/sim/jogador.gd` | volta à base (tecla e Vela de Retorno) leva cada facção para a sua casa; o save guarda posição em Jerusalém; `porta_do_altar` igual à `porta_camara`; as 5 lojas de Jerusalém vendem o básico (Bartimeu vende munição e armas da faixa 1, como o Tobias); portal com `nivel_minimo`. |
| `scripts/sim/chefe_ctl.gd` | o roteiro da luta vem de `mecanica_de` (Ohya = Andras, Naamá = Irmã Celeste, Semyaza = Zacarias) e `invoca_troca` faz o espelho chamar os próprios mobs. |
| `client/efeitos.gd`, `client/game.gd` | cores dos telégrafos e a animação do Andras seguem a mecânica, não o id. |
| `scripts/sim/loot.gd` | a Chave de Pã cai sempre do Capataz de Tofete, como a Chave de Gancho. |
| `client/hud.gd` | nomes das saídas do Fosso no mapa. |
| `tools/mapa.py` | portal **Estrada dos Peregrinos** no São Lázaro novo (56.5, 126.5), no caminho da banca da Corvina. |
| `tools/sync.sh` | copia os 4 mapas de `design/mapas/jerusalem_hermon/` e o `design/pvp/hermon/cume_dos_vigilantes.json`. |
| `tools/teste_jerusalem.gd` | teste novo. |
| `tools/sim_test.gd` | não trava mais: o São Lázaro novo só tem spawn da Vigília e o teste pedia o dos Arautos (erro e o teste nunca terminava). |

## O que o `aplicar_dados.py` faz

- Junta os `*_acrescimo.json` em `design/missoes/dados/`. Dois ids colidiam com coisas que entraram depois:
  o acessório de Jerusalém vira `martelo_de_tubal` (o `malho_de_tubal` é a arma lendária do Hermon) e a loja do
  Zaqueu de Jerusalém vira `loja_zaqueu_cobrador` (a `loja_zaqueu` é a do convite).
- **Regra dos 25% (17/10):** cada missão de Jerusalém recebe o XP de hoje da missão da Vigília que ela espelha
  (as 36 somam 19.120, igual às espelhadas).
- A `g02` passa a abrir com `g01` **ou** `jg01` (`requer_qualquer`), para os Arautos chegarem na linha G.
- Grava os 4 mapas em `design/mapas/jerusalem_hermon/` com a **Estrada do Sul** (portal para o deserto, nível 12,
  chega ao lado da Estrada dos Peregrinos).
- `game/data/v06_extra.json`: 21 mobs, 3 chefes (com `invoca_troca`), 3 tabelas de drop e nomes do HUD. Mobs que
  herdam um ataque de invocar chamam o espelho daqui (o Capataz de Tofete chama Peregrinos, não Carniçais).
  `game/data/sprites_substitutos.json`: os recolores.
- Copia o mapa do evento para `design/pvp/hermon/` (o `dados.json` de lá já é o atual).
- Põe Jerusalém na lista do `entregas/teleporte/gerar.py`.

## Mudanças no mapa (17/10)

- As quatro portas da muralha de Jerusalém não davam em caminho nenhum (os caminhos saíam do centro e batiam na
  muralha perto dos cantos): só 432 das 6.098 células andáveis eram alcançáveis a pé a partir do nascimento. Agora
  cada caminho sai de uma porta (Damasco para o Hissopo, Dourada para o Getsêmani, da Fonte para a Cidade de Davi,
  do Esterco para o Hinom) e 6.089 de 6.098 são alcançáveis; o teste confere que se anda da cidade até todos os grupos.
- O `gerar.py` lia os spots do deserto antigo. Com o São Lázaro novo ele parou de rodar; os grupos de cada spot
  agora vêm de `grupos_espelho.json` (os mesmos de 16/10, sem mudar números) e o `espelho.txt` de 16/10 continua valendo.

## Pendências para outras threads (não travam a 0.9.3)

- **Arte:** os 21 mobs e 3 chefes usam folha recolorida; `cupula_da_rocha`, `oliveira_morta` e `antena_radio` usam
  props substitutos. Ícones do convite e das 6 Armas de Azazel estão na lista de arte do Jefin.
- **Som:** o mapa pede `ambiente/pontual/porcos` e `martelo_forja`; música própria do evento.
- **Combate:** efeitos especiais das Armas de Azazel ainda são só texto.
- **Missões:** há dois Zaqueus (o do convite em São Lázaro e o cobrador de Jerusalém). Funciona, mas a lore pode
  querer juntar os dois.
- **Cidade de São Lázaro:** se o `layout.py` da cidade mudar o sul, conferir a Estrada dos Peregrinos (56.5, 126.5).

## A área em poucas linhas

Os Arautos nascem em **Jerusalém**, onde o Juízo começou: Sariel abriu a Porta Dourada no primeiro toque. Da cidade
murada o caminho desce o Monte das Oliveiras (Getsêmani, a necrópole), passa pelo Vale de Josafá e pela Geena (Tofete)
e sobe pelos cedros até as Fontes do Jordão e o cume do Hermon, onde os duzentos Vigilantes juraram. O Fosso dos
Vigilantes fica atrás dos Portões do Hades. Linhas próprias: **O Juramento do Hermon** (espelho da D), **O Trono da
Geena** (da E) e **O Escriba Que Não Morreu** (da F). Plantas em `planta_*.png`.

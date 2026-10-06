# DARK PASSAGE · cliente Godot 4 (prévia v0.6)

Prévia jogável: Paróquia de São Lázaro (Deserto de Absinto, mapa 160x160 da thread de level design) e a
Cripta da Trombeta Calada (3 andares: Porão do Matadouro, Ossário das Carpideiras, Câmara da Trombeta),
com os chefes Andras, Irmã Celeste e Zacarias. 6 classes, missões e diálogos da thread de missões,
baús, drops com raridade, loja, forja (refino), armazém, treinador, morte e renascimento, save automático.

v0.3: os 170 objetos do lote 2 de ambiente (1939 de 1940 props do deserto com arte; falta `ponte_pedra_ruina`),
22 sprites de monstros entregues no lugar dos substitutos, radiação do Amargo (contador Geiger a partir do
nível 4, dano a partir do 7, lentidão na faixa da borda) com tempestade em shader (`shaders/tempestade.gdshader`)
que engrossa conforme o nível, Andras comendo (anim `eat`) e cansado (`tired`), brilho do Não-Julgado à noite.
Lote 2 de monstros: alfa em toda matilha de 3+ cães (uiva ao avistar), salto do cão, porco cava (scrape), investe (charge)
e fica tonto (stun) ao bater na parede, Filho de Cardo se enterra para trocar de posição (burrow/emerge).
Teste headless dos especiais: `godot --headless -s tools/teste_bichos.gd`.

Jogar: https://claude.ai/artifact/CzSX1qdoE9wb1qHour4e4o · Windows: `builds/DarkPassage-v0.6-windows.zip`.

v0.6: contas e rede local (abaixo); linhas de missão D (Isaura, A Estrela Que Nós Soltamos) e E (Corvina, A Legião Sem
General) com objetivo `farmar_spot`; mapa novo com 8 spots de farm (temperamento por spawn: neutro, agressivo, territorial),
fogueiras com o carrinho de poções do Tobias; skills de área do nível 5 das 6 classes; modo automático (Z); curva de XP
75L²+375L e poções baratas. Monstros novos sem arte própria usam variantes (`data/v06_extra.json`, `data/sprites_substitutos.json`).

## Rede local (Windows)
- Abertura: Jogar sozinho · Hospedar partida (este PC vira servidor e também joga) · Entrar numa partida (IP).
- `scripts/net/rede.gd` (ENet, porta 7777, nó /root/Main/Rede), `servidor.gd` (contas, um WorldSim por mapa ocupado,
  descarrega o mapa quando esvazia), `sincro.gd` (entidades -> dicionários; o dono recebe os campos privados, os outros só os públicos).
- Contas em `user://servidor/contas.json` do PC que hospeda: sal + sha256 iterado sobre o resumo que o cliente manda
  (a senha nunca viaja). Até 6 personagens por conta (saves no mesmo formato do solo).
- Comandos do jogador passam por `scripts/sim/comandos.gd` (solo chama direto; em rede vai para o servidor, que valida).
  Eventos de um jogador só usam `sim.emitir_a(e, ...)`; nada novo deve chamar `sim.jogador()`.
- Em grupo: quem ajudou ganha XP, crédito de missão e o próprio saque; o chefe só reseta quando ninguém está de pé na arena.
- Testes: `godot --headless -- servidor=1 [porta=7781]` e clientes `xvfb-run -a godot --path . --rendering-driver opengl3 --
  conectar=127.0.0.1:7781 usuario=ana senha=1234 classe=anjo teste_rede=/tmp/r tempo=30` (`conectar=hospedar` testa o modo
  hospedar; `teste_mapa=porao_matadouro` no servidor leva quem entra para outro mapa após 8 s).

## Estrutura
- `scripts/sim/` servidor autoritativo (WorldSim a 30 Hz, IA, combate, chefes em `chefe_ctl.gd`, itens, loot,
  missões). O cliente só chama `Jogador.cmd_*` e escuta o sinal `evento`.
- `scripts/client/` desenho: `game.gd` (camadas, entrada, eventos, clima), `chao.gd` (chão em shader com transições),
  `luz.gd` (mapa de luz), `unidade.gd` (sprites 8 direções), `efeitos.gd` (VFX, números, telegrafos, projéteis),
  `audio.gd`, `hud.gd` (barra do kit de UI), `janelas.gd` (mochila, diálogos, lojas...), `char_select.gd`.
- `data/design/` cópia dos JSON de design das outras threads; `data/mapas/` mapas gerados por `tools/mapa.py`;
  `data/ext/` manifestos dos assets; `data/sprites_substitutos.json` arte provisória de quem ainda não tem sprite.
- `assets/ext/` cópia dos assets das outras threads (gerada por `tools/sync.sh`); aqui só fica `ambiente/`,
  que também guarda o kit de cenário renderizado nesta thread.

v0.4 (avaliação da v0.3): silhueta do jogador atrás do cenário e nascimento em área aberta; dano dos monstros reduzido
até o nível 4 (Bênção da Vela), primeiros grupos sozinhos e afastados das áreas seguras; cena mais clara, zoom 1,2,
contorno no monstro sob o mouse e clique/skill que acham o inimigo mais perto; chefes 1,5× maiores com luz e contorno;
filtro suave nas texturas; mapa (M) legível com legenda e objetivos; Esc pausa.
Mobs estilo WoW (Jefin): no deserto a maioria é neutra (nome amarelo, só reage se apanhar); agressivos (nome vermelho)
só na Vala e no Abatedouro (`ZONAS_AGRESSIVAS` em world_sim.gd), grupos de 2 (3 nos agressivos), puxada só do mesmo grupo.

## Do zero, num container novo (tudo sai desta pasta + /mnt/project-files)
    bash tools/instalar_godot.sh                 # Godot 4.4.1 + modelos de export
    bash tools/sync.sh                           # assets e design das outras threads -> assets/ext, data/
    GODOT=/opt/godot/godot bash tools/build_web.sh   # build Web em dist/artifact (áudio re-encodado numa cópia)
O kit de cenário renderizado por esta thread (pisos e objetos que não vieram da thread de ambiente) fica em
`fontes/ambiente_kit/` (PNGs prontos + scripts Blender em `src/`).

## Atualizar com entregas das outras threads
    bash tools/sync.sh          # copia assets/design do /mnt/project-files, refaz pisos, manifestos e mapas

## Testar e gerar builds (no container)
    godot --headless --import
    godot --headless -s tools/check.gd                         # compila todos os scripts do cliente
    godot --headless -s tools/sim_test.gd                      # servidor: 6 classes, baús, missões, 3 chefes
    xvfb-run -a godot --path . --rendering-driver opengl3 -- classe=humano fotos=/tmp/f       # prints
    xvfb-run -a godot --path . --rendering-driver opengl3 -- classe=anjo mapa=porao_matadouro roteiro=chefe fotos=/tmp/c
    xvfb-run -a godot --path . --rendering-driver opengl3 -- classe=humano roteiro=tour "pontos=99,80;23,80" fotos=/tmp/t
    godot --headless --export-release "Web" build/web/index.html     # numa cópia com áudio re-encodado (abaixo)
    godot --headless --export-release "Windows" build/windows/DarkPassage.exe
    python3 tools/make_artifact.py build/web dist/artifact      # partes < 15 MB para o claude.ai (publicar em 2 vezes)

Web: o áudio é re-encodado só na cópia do build Web (ffmpeg libvorbis q0/q1, mono nos efeitos) para caber.

## Controles
Clique anda/ataca/interage (segure para seguir o mouse) · Shift+clique ataca parado · 1–6 habilidades ·
botão direito = habilidade 1 · Q/W/E poções · R Vela de Retorno · I mochila · C personagem · K habilidades ·
J missões · M mapa · Alt itens no chão · H ajuda · Esc menu.

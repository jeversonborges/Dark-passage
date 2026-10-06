# Monstros e chefes do DARK PASSAGE

Pipeline de sprites dos monstros: modelo procedural no Blender, rig próprio,
animações por quadro e render isométrico em 8 direções, igual aos personagens
(mesma câmera 30°/45°, 64 px por metro, luz da lua + contraluz + preenchimento).

Dependências (container novo): ver `../README.md` (Blender, Pillow, NumPy).

## Arquivos

- `base_rig.py`: cópia congelada de `../personagens/rig.py` (materiais sujos, Skin modifier, saias).
- `mrig.py`: rig genérico. Esqueleto por dicionário (`humanoid(escala, largura)` ou ossos próprios),
  pesos automáticos, peças rígidas, poses por quadro com trava no chão, interpolação de poses
  (`keys_to_frames`) e material com manchas (`stained`).
- Um módulo por monstro com `build()` e `anims(R)`: `carnical.py`, `general.py`.
- `render.py`: quadros brutos em 2x. `process.py`: folhas finais. `contato.py`: folha de conferência.

## Uso

    blender -b -P render.py -- carnical /tmp/brutos/carnical                # tudo
    blender -b -P render.py -- carnical /tmp/brutos/c teste 1               # conferência rápida
    blender -b -P render.py -- general /tmp/brutos/g attack,roar 1,3        # só algumas animações/direções
    python3 process.py /tmp/brutos/carnical /mnt/project-files/assets/monstros/carnical 40 .6

## Saída (assets/monstros/<id>/)

- `<id>_<anim>.png`: folha com 8 linhas (direções S, SE, E, NE, N, NW, W, SW) e uma coluna por quadro.
- `meta.json`: tamanho do quadro, âncora (ponto no chão sob o monstro, em px dentro do quadro),
  fps e loop de cada animação. A sombra já vem desenhada no sprite.
- `previa/<anim>_SE.gif`: prévias animadas.

Animações: `idle`, `walk`, `attack`, `hit`, `death` (todas as criaturas); chefes ganham extras
(o General tem `roar`, para a troca de fase). `death` termina no corpo caído: segure o último quadro.

## Monstros (módulos e variantes)

- `carnical.py`: Carniçal; variantes `nao_julgado` (mortalha, mãos amarradas) e `carnical_inchado` (elite, pústulas).
- `general.py`: Andras, o General Partido (chefe do andar 1). Saída em `assets/monstros/andras/`.
- `acougueiro.py`: `acougueiro_oco` (barriga oca, capuz de saco, cutelo; extra `heavy`) e `capataz_gancho`
  (elite: braço de ferro com gancho, porrete, máscara de porco; extras `hook`, `spin`, `shout`).
  O gancho some durante o voo de `hook` (chave de pose `scale`).
- `soldado.py`: `soldado_caido` (luta do General) e `soldado_escudeiro` (escudo e elmo fechado); extra `rise`
  (levanta do chão a mando do General; começa no mesmo quadro final de `death`).
- `quad.py`: esqueleto quadrúpede compartilhado (`quad_bones`, patas `upper_arm/forearm/hand` e `thigh/shin/foot`,
  trava no chão por `PAWS`), corpo em anéis (`ring_path`/`loft`, com costelas e vértebras), tufos de pelo, ciclo de
  pata (`leg_cycle`) e `QRig` (chave de pose `bloat`: escala não uniforme por osso, ex. barriga inchando).
- `cao_de_vala.py`: Cão de Vala (matilha; extras `leap` bote no lugar, o jogo desloca, e `howl`); variante elite
  `cao_de_vala_alfa` (maior, quase preto, placas de sucata parafusadas, cicatrizes). Quadro 192 px.
- `porco_pestilento.py`: Porco Pestilento (placa-aríete na testa, arreio, pústulas verde-ácido; extras `scrape`,
  `charge`, `stun` em loop; `death` termina inchado no chão, a explosão fica com os efeitos). Quadro 256 px.
- `corvo_de_cinza.py`: Corvo de Cinza (esqueleto de ave: corpo, cauda, pescoço, cabeça, bico, asas em 3 ossos com
  penas planas por osso, pernas). Voa sempre a ~1,3 m (`"ground": None`); só `death` trava no chão (cai de asas
  abertas). Variante `corvo_de_cinza_carnica` (1,25x, quase preto, pescoço pelado, bico em gancho, carne pendurada;
  quadro 224 px). `safe_ground(R)` contorna a trava no chão de um quadro travado logo após quadros sem trava.
- `filho_de_cardo.py`: Filho de Cardo (raro de missão): massa de carne com espinhos e cardos roxos, boca vertical,
  6 raízes de 2 ossos, cipós, lápide e cruz de ferro. Extras `burrow`/`emerge`: o root desce abaixo do chão e um
  disco Holdout preso ao osso `occ` esconde o que fica embaixo (fora dessas animações o disco fica 12 m abaixo,
  fora do quadro). Quadro 256 px.
- `monge_emparedado.py`: Monge Emparedado (cripta, andar 2): monge de 2,3 m de argamassa com hábito podre, pedaço de
  parede fundido nas costas, punhos de pedra com grilhões, correntes e rosário de ferro (olhos âmbar). Extras `ambush`
  (atrás de uma parede de tijolos; ~20 pedaços em ossos sem pai `wp*` voam em arco e ficam no chão; fora dela somem
  por escala), `pray` (ajoelha e a crosta de pedra dos ossos `crust.*` cresce; segure o último quadro) e `broken` (loop).
  Quadro 256 px.
- `carpideira_de_ossos.py`: Carpideira de Ossos (cripta, andar 2): ossada flutuante de luto, véu rasgado, máscara de
  ossos em leque, lágrimas negras, relicário-turíbulo na mão esquerda (brilho frio). Sem pernas: vestido em 6 painéis
  de 2 ossos (`sk*`) que arrastam e se abrem no chão na morte; `settle()` assenta a morte no chão sem a trava do mrig.
  Extras `lament`, `heal` (loop). Variante elite `carpideira_de_ossos_viuva` (véu vermelho-escuro, 1,12x, relicário e
  coroa maiores). Quadro 224 px.
- `larva_de_carne.py`: Larva de Carne (cripta, andar 1): verme segmentado de carne de defunto (loft com dobras), pregos de
  caixão, faixas de mortalha furadas, mão e costelas de quem ela comeu, boca de lampreia com 4 lábios (`lip_*`). Traz o
  `XRig` (reaproveitado pelos módulos da cripta): spec `inf`/`sx`/`sy`/`sz` (escala por osso), `vis` (esconde; ossos em
  `R.hidden` começam escondidos), `lx`/`ly`/`lz` (move ossos sem pai), pseudo-ossos `glow` (veias emissivas do material,
  keyframe por animação) e `lamp` (energia de luzes presas a ossos). `attack` = incha 0,8 s pulsando com as veias acesas;
  `death` = estoura (ossos-folha `s_*` murcham, 8 pedaços `k*` voam e caem, poça `pool`, rasgo `rip`). Variante elite
  `larva_de_carne_mae` (1,55x, mais roxa, 4 larvinhas `kid*` nas costas que se mexem; quadro 256 px). Quadro 192 px.
- `gancheiro.py`: Gancheiro (cripta, andar 1): ajudante do abatedouro magro e alto, capuz de carrasco de couro, óculos
  de soldador de latão (lentes acesas), avental curto (`apron_sheet` de `acougueiro.py`), bandoleira de corrente, ganchos no
  cinto e nas costas. `attack` arremessa (osso `hook` some em voo pela chave `scale`); extra `pull` (corrente esticada com o
  gancho na ponta no osso `line`, escondido fora dela; puxa duas vezes com o corpo todo). Quadro 224 px.
- `fogo_de_vela.py`: Fogo-de-Vela (cripta, andar 2): velas de igreja derretidas fundidas num corpinho flutuante (cera com
  subsurface, escorridos, rosto derretido, aro de lustre com corrente); chamas em ossos `fl*` tremulando por escala, luz
  pontual presa à cabeça (`lamp`). Extras `blink_out` (encolhe numa bola de cera, vira poça e some) e `blink_in`; `death`
  derrete numa poça (`pool`, com tocos e o rosto) e as chamas apagam uma a uma. Quadro 192 px.
- `corista.py`: Corista de Osso (adicional da Irmã Celeste, andar 2): esqueleto de menino do coro (batina vermelha,
  sobrepeliz rasgada, gola de renda, cera escorrida, hinário aberto). Osso `voice` leva olhos, boca e auréola acesos e fica
  escondido (escala .001) fora de `sing`. `idle` = estátua apagada (2 quadros); `sing` canta e brilha; `death` desmorona
  (reaproveita painéis e `settle()` da Carpideira). Quadro 224 px.
- `celeste.py`: Irmã Celeste (chefe, andar 2): freira regente de hábito preto com cauda, sobretúnica rasgada, escapulário,
  rosto de porcelana com lágrimas de cera acesas, véu, coroa de 7 velas (chamas no osso `flames`), batuta de osso com sino
  e rosário de dentes. Reaproveita `tube`/`skirt_wave`/`settle` da Carpideira e `apron_sheet`. Extras `lament`, `weep`,
  `conduct` (rege os Coristas), `choir`, `exhausted` (loop caída no chão), `snuff`, `summon`; `death` apaga a coroa.
  Escala 1,45x, quadro 416 px.
- `zacarias.py`: Zacarias, o Arauto (chefe final, andar 3): anjo de porcelana com rachaduras de ouro, boca costurada em
  volta da trombeta lacrada com chumbo, auréola quebrada, tabardo azul com trombeta de ouro, grilhões partidos, espada
  com gravação acesa, asas grandes de penas (3 ossos por asa, `FOLD` fechada). Extras `lance`, `wings` (giro de 360°),
  `mark`, `channel` (flutua), `exhausted` (ajoelhado). Variante `zacarias_chamas` (fase 3, asas em chamas). Escala 1,55x,
  quadro 512 px.

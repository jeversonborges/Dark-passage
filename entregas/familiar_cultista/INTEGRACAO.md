# Pet do Cultista 0.9.3: DPS em área, 3x mais resistente, cura pelo dono, barra do pet e Líder dos Demônios (nível 60)

Pedidos do Jefin (2026-10-17): pet DPS, "todos os demônios pet batem em área", "a última evolução será o Demônio
Líder lvl 60", "o pet precisa de uma barra / faça uma igual" (print em `referencia/barra_pet_jefin.png`),
"põe ele invulnerável não, põe ele com muita vida e defesa, 3x mais resistente que antes" e "coloca ele curando
10% do que o dono bate". **A versão invulnerável da manhã foi substituída por esta.**

## O que muda no jogo

- **Resistência:** vida 1,05 / 2,10 / 3,30 / 4,50 da vida máxima do dono e defesa 1,5 / 2,4 / 3,6 / 4,5 da defesa
  do dono (3x os valores de antes). Ele apanha e pode morrer de novo.
- **Cura:** 10% de todo dano que o Cultista causa (golpes e dano por tempo) cura o familiar (`cura_por_dano_do_dono`).
- **Volta visível:** ao renascer (30 s) o familiar emite `reviveu`. O cliente já trata esse evento (`game.gd`, o
  mesmo do jogador) e tira a view do estado de morto. Antes ele voltava invisível até trocar de área.
- **Área:** todas as formas acertam todos os inimigos em `ataque.area_raio` do alvo (1,5 / 2 / 2,5 / 3 tiles).
- **Barra do pet** (só para o Cultista com familiar), em cima da barra de skills, igual ao print:
  - Atacar: o familiar vai no alvo atual do dono (vale em qualquer modo).
  - Proteger (padrão): ataca quem bater no dono ou nele.
  - Teleportar: volta para o lado do dono (recarga de 5 s).
  - Modo agressivo: também ataca monstros a até 6 tiles do dono.
  - Modo passivo: só segue, não ataca.
  - O retrato mostra a vida do familiar e fica apagado com "VOLTANDO" enquanto ele está morto. O modo ativo
    ganha moldura de latão pulsando. Com a fileira da evolução (Shift+1..5), a barra sobe 48 px.
  - Arte: `pet_barra.png` recortada do print do Jefin (retrato, molduras, ícones e nomes pintados por ele).

## O que aplicar (Prévia)

Cada arquivo tem o `.gd` pronto e um `.patch` contra a pasta compartilhada de 2026-10-17 ~12h UTC. Se o arquivo
mudou desde então, aplique o `.patch` (são trechos pequenos e isolados).

1. `game/scripts/sim/familiar.gd` ← `familiar.gd` (`familiar.patch`).
2. `game/scripts/sim/world_sim.gd` ← `novo/world_sim.gd` (`novo/world_sim.patch`): 3 linhas (quem bateu no
   familiar e a cura de 10% em `aplicar_golpe` e `aplicar_dano_puro`).
3. `game/scripts/sim/comandos.gd` ← `novo/comandos.gd` (`novo/comandos.patch`): comando `pet`.
4. `game/scripts/client/hud.gd` ← `novo/hud.gd` (`novo/hud.patch`). Se o hud.gd mudar de novo:
   `python3 aplicar_hud.py game/scripts/client/hud.gd game/scripts/client/hud.gd novo/hud.gd`.
5. Arte: `assets/ui/hud/1x/pet_barra.png` e `2x/pet_barra.png` (o sync.sh copia; já estão também em `game/assets/ext/ui/`).
6. Números: `design/combate/classes_base.json > classes > cultista > racial > familiar` (já atualizado; rode o sync.sh).
7. Sprites do nível 60: `assets/monstros/familiar_lider/` (rode o `tools/manifest.py`).
8. Teste: `godot --headless -s tools/teste_familiar.gd` (cópia desta pasta). Esperado nas 4 formas:
   `atingidos=3 apanhou=true curou=true passivo_ok=true morreu=1 reviveu=1 vivo=true`. Passou aqui no Godot 4.4.1
   com o game/ compartilhado de agora.

Observação: o "AUTO" do modo automático fica embaixo da barra do pet; a barra do pet repete o "AUTO" ao lado dela.

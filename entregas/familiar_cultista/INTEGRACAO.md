# Pet do Cultista 0.9.3: invulnerável, DPS, ataque em área e 4ª forma (Líder dos Demônios, nível 60)

Pedido do Jefin (2026-10-17): "ele morre fácil e não volta quando morre, só se trocar de área; deixa o pet do
cultista invulnerável", "ele vai ser mais um DPS", "todos os demônios pet batem em área", "a última evolução será
o Demônio Líder lvl 60". Tudo entra na 0.9.3.

## Por que ele não voltava

A simulação já revivia o familiar depois de 30 s (`world_sim.gd` chama `Familiar.renascer`), mas o cliente não:
`unidade.gd` marca a view como `morto` e só a view de jogador é ressuscitada (`game.gd:734`). O familiar voltava
invisível e só reaparecia quando a view era recriada na troca de mapa. Com o pet invulnerável ele nunca mais morre,
então o problema some na raiz.

## O que aplicar (Prévia)

1. **Código:** substitua `game/scripts/sim/familiar.gd` por `entregas/familiar_cultista/familiar.gd`
   (diferença em `familiar.patch`, feita sobre o `familiar.gd` da pasta compartilhada de 2026-10-17). Só esse
   arquivo muda. O que ele faz:
   - `_blindar()`: `alvejavel = false` (monstros não o miram, áreas e projéteis passam por ele), `invuln_t`
     infinito (dano por tempo não pega) e vida sempre cheia. Reaplicado a cada passo, caso algo mexa.
   - Ataque básico em área: `_respingo()` acerta todos os inimigos em `ataque.area_raio` do alvo (o Diabrete pelo
     `ao_atingir` do projétil). Puxão de Corrente também respinga.
   - Guarda-Costas removido do JSON (pet é DPS); `desviar()` não tira mais vida do pet.
   - 4ª forma `familiar_lider` com o especial Decreto do Lorde (usa o mesmo ramo do Canhão de Brasa).
2. **Números:** já estão em `design/combate/classes_base.json > classes > cultista > racial > familiar`
   (dano 0,45 / 0,60 / 0,75 / 1,00 do dano mágico do dono; área 1,5 / 2,0 / 2,5 / 3,0 tiles; nova forma
   `familiar_lider` no nível 60). Texto da racial regenerado em `design/skills-itens/skills.json`.
3. **Sprites:** `assets/monstros/familiar_lider/` (idle, walk, attack, hit, death, 8 direções, quadro 448 px,
   `meta.json`). Rode `bash tools/sync.sh` e `python3 tools/manifest.py` antes do build para o `familiar_lider`
   entrar no `data/ext/sprites.json`.
4. **Teste:** `godot --headless -s tools/teste_familiar.gd` (arquivo nesta pasta; copie para `game/tools/`).
   Resultado esperado, nas 4 formas: `vivo=true`, `alvejavel=false`, `atingidos=3`, `dano_no_familiar=0`,
   `mortes=0`. Rodado aqui com o Godot 4.4.1 e passou.

## Opcional

Se um dia o familiar voltar a poder morrer, o cliente precisa reviver a view dele como faz com o jogador
(`game.gd:734`), senão ele volta invisível de novo.

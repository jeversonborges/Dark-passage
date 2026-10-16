# Mapa `agrak` (O Agrak, o Grande Coliseu)

Feito pela thread Level design em 16/10, com o kit do Cenário. Gerado por `design/mapas/fontes/agrak.py`.
Não editar o JSON à mão: rode `python3 agrak.py`.

- `agrak.json`: mesmo formato de `game/data/mapas/*.json`, igual aos andares da cripta. Pode ir direto para `game/data/mapas/agrak.json`.
- `planta_agrak.png`: planta do mapa.
- `previa_agrak.png`: foto tirada de uma cópia do jogo.

## O que o evento usa (bloco `agrak` do JSON)

- `centro`, `raio_circulo` (3.5) e `fosso` [x0, y0, x1, y1]. O fosso tem 30 x 22 tiles.
- `anel_raio_max`: 13. É o raio inicial do Anel do Amargo.
- `portoes`:
  - Os três portões são `portao_leoes`, `portao_gigante` e `portao_gladiadores`.
  - Cada um tem as `celulas` que bloqueiam enquanto ele está fechado. O `agrak_ctl` deve começar com elas bloqueadas e abrir com `definir_bloqueio`.
  - O prop do portão tem `portao: <id>`, para trocar o sprite pelo `portao_grade_agrak_aberto_*` quando abrir.
  - O Portão do Gigante é o `portao_gigante_a` e não tem sprite de aberto: ele some ou fica.
- `chefes_nascem`: os 3 leões nascem nas jaulas, atrás do Portão dos Leões, e o Golias no curral, atrás do Portão do Gigante.
- `entrada_fosso`: o ponto logo depois do Portão dos Gladiadores.
- `camarote_derrotados`: o retângulo e o `pos` para onde os mortos vão como espectadores.
- `seguro`: o Corredor dos Gladiadores (onde o `spawn` fica, junto da Ermida do Saulo) e o Camarote dos Derrotados.
- NPCs:
  - `saulo`, na ermida.
  - `caim_abel`, no camarote do placar.
- Plateia: são os props com `plateia: 1`, todos no quadro 0.
  - No dia a dia, alternar 0-1-0-1 a cerca de 4 fps.
  - Na morte (`morte_pvp` ou morte de chefe), tocar 2-3-3-2.
  - Começar cada tile num quadro diferente, para a plateia não balançar junta.
  - O nome é `plateia_<v>_<quadro>_<o>`.
- `sem_penalidade: true`.
- Saída: um `portal` com `volta: true` no corredor. Ele devolve o jogador para onde ele estava antes da inscrição.

## Layout

- No alto da tela ficam o muro de 3 m, as faixas dos campeões e os braseiros-holofote, com duas fileiras de arquibancada e a plateia atrás.
- Embaixo fica só a mureta baixa: a arquibancada da frente desabou, e a câmera vê a luta inteira.
- Os quatro pilares de entulho ficam perto dos cantos e deixam o centro livre para o Pião do Golias.

# Humano sem espada larga (16/10/2026)

Pedido do Jefin (14:01): o Humano base perde a espada larga. Básico com a besta pesada; tiro secundário com a escopeta.

**Arquivo:** `classes_humano.json`. Traz o bloco `classes.humano` inteiro para substituir o de `design/combate/classes_base.json`. Não toquei no arquivo compartilhado, porque a escrita foi bloqueada.

Mudanças:
- `arma_inicial`: Besta Pesada, mesmos números da espada (6-10, intervalo 1.25, postura 18), tipo `arma_de_fogo`.
- `perfil_hibrido.distancia_troca` = 0: o básico sempre dispara. Sem munição, sobra o golpe de coronha curto.
- `corte_largo` renomeado para **Rajada de Escopeta** (mesmo custo, recarga, mult e raio). Sai o giro de 360.
- `arrancada` renomeado para **Salto de Recuo** (mesmo custo, recarga, cargas e deslocamento).

Ainda falta (Combate):
- A animação de giro e a de dash com espada: o código em `scripts/sim/habilidades.gd` (`corte_largo` usa `anim: "spin"`) precisa de uma animação de tiro.
- Os ids das skills ficam iguais (`corte_largo`, `arrancada`) porque o código usa esses ids.
- O sprite do Humano sem espada: a folha está na fila da Evoluções. Hoje só há a prévia em `entregas/evolucoes/previa/humano_sem_espada.png`.

Para aplicar, substituir o bloco `classes.humano` em `design/combate/classes_base.json` pelo de `classes_humano.json` e rodar `game/tools/sync.sh`.

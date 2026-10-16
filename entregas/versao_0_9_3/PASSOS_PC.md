# 0.9.3: passos para rodar no Claude do PC (E:\darkpassage\Dark-passage)

Não rodar nada disto na nuvem: são escritas em arquivos compartilhados. Rodar na ordem. Se algum passo falhar, parar e avisar.

1. Mapa de São Lázaro (igreja nova, cartaz do Agrak, Gustavo):
   - Copiar entregas/cidade_sao_lazaro/area_inicial.json para design/mapas/area_inicial.json.
   - Copiar entregas/cidade_sao_lazaro/spots.json para design/mapas/spots.json.
   - Rodar: python entregas/cidade_sao_lazaro/missoes/missoes_cidade.py design/missoes
   - Rodar: python design/missoes/validar.py (esperado: OK, 61 missões).
   - No design/mapas/area_inicial.json, trocar o objeto {"id":"cartaz_agrak","x":63.6,"y":92.8} por {"kind":"interativo","obj":"cartaz_agrak","pos":[63.6,92.8],"i":0}.

2. Novo Éden (Revisão Gênesis, PR #19): seguir design/mapas/mata_do_granizo/INTEGRACAO.md, seção "Revisão Gênesis". Inclui patches/chao_agua.diff (a Prévia já aplicou no código).

3. Humano sem espada larga: substituir o bloco classes.humano de design/combate/classes_base.json pelo de entregas/humano_sem_espada/classes_humano.json (ver LEIAME.md da pasta).

4. Itens do PR #17 (lote 2): ver o fim de entregas/aneis_tunicas/LEIAME.md.

5. Rodar game/tools/sync.sh e game/tools/manifest.py. Conferir que nada de game/ sumiu (edições locais em data/design/{combate,missoes,skills-itens} são sobrescritas).

6. Só depois: a Prévia faz a build de teste e o zip da 0.9.3. Não publicar sozinho.

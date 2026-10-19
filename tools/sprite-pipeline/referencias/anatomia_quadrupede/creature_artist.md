<!-- Fonte: texto colado pelo Jefin em 2026-10-19 (skill "creature-artist", autor arjun988, MIT). Não está em nenhum dos repos em vendor/. -->
# Creature Artist (fluxo de criatura)

Fluxo: Reference → Skeleton Blockout → Muscle Masses → Surface Forms → Detail → Retopology → Rig → Animation Test.

Tipos de criatura (base do esqueleto):
- Quadrúpede: base cão ou cavalo. Forma-chave: shoulder hump, haunches.
- Bípede: humano ou primata. Coluna ereta, apoio do calcanhar.
- Voador: morcego ou ave. Membrana da asa, quilha do peito.
- Aquático: peixe ou tubarão. Linha lateral, barbatanas.
- Serpentino: cobra. Segmentação das costelas.
- Inseto: artrópode. Corpo segmentado, pernas articuladas.

Músculo: origem → inserção aparece na superfície. Área flexionada comprime; estendida estica. Gordura: transição suave. Cicatriz ou armadura quebra o fluxo de propósito.

Esqueleto antes da superfície: posicionar juntas, checar amplitude em cada junta, garantir que o membro suporta o ciclo de passada, e que a cabeça e o pescoço suportam poses de ataque e olhar.

Níveis de detalhe: primário (massa), secundário (grupos musculares), terciário (dobras, veias), micro (escamas, cicatrizes, normal map).

Regras: referência real mesmo no fantástico; silhueta testada na câmera do jogo; joints planejados no blockout; retopologia antes do rig; polycount por nível (fundo vs chefe).

Observação para nosso pipeline: a skill foi escrita para Blender via MCP ao vivo. Nosso bpy roda em lote, então o blockout vira código (`quad.py`), não escultura.

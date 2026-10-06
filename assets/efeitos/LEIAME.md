# Efeitos visuais do DARK PASSAGE

95 efeitos em sprite sheet PNG (alfa reto), no estilo "Ferrugem Sagrada": pixel art nativa para 640x360 (ampliar 2x sem filtro), paleta fixa sem dither, brilho só nos pontos de luz.

Galeria animada: https://claude.ai/artifact/97zJSkx9MHYFcsBUKkdMg1

## Pastas

| Pasta | Conteúdo |
|---|---|
| `combate/` | impacto, corte, crítico, sangue, faíscas, disparo, fumaça, bala, poeira, morte de monstro |
| `status/` | veneno, sangramento, em chamas, atordoado, lentidão (loops sobre o alvo) |
| `itens/` | brilho de item no chão (4 raridades), feixe de drop, baú abrindo |
| `progresso/` | subida de nível, cura |
| `anjo/ cultista/ demonio/ humano/ mutante/ tecnomancer/` | as 6 habilidades de cada classe (design/classes.md), supremas incluídas |
| `chefes/` | avisos de área/cone/linha, pisão, meteoro, fenda de invocação, fúria, raio, casca invulnerável, morte de chefe |
| `auras/` | aura de equipamento lendário / estágio 3, uma por classe |
| `ambiente/` | clima e luz do Deserto de Absinto: pó Amargo (dia e noite), tempestade de Amargo, areia soprando, veios acesos, brilho dos Não-Julgados, ar limpo e lâmpada da Vela |
| `_previa/` | GIF e tira de quadros de cada efeito (só para revisão, não vai no jogo) |

`efeitos.json` é o índice de tudo. Cada sheet tem um `.json` ao lado:

```json
{"name": "level_up", "frame_w": 128, "frame_h": 192, "frames": 24, "cols": 8, "rows": 3,
 "fps": 16, "loop": false, "anchor": [64, 168], "layer": "frente", "title": "Subida de nível"}
```

- **anchor**: pixel do quadro que vai no ponto de aplicação (pé do personagem para efeitos de corpo e de chão; ponto de impacto para golpes; boca da arma para disparos).
- **layer**: `chao` desenha abaixo dos personagens (poças, avisos, armadilhas); `frente` desenha por cima, ordenado por Y.
- **loop**: `true` para status, auras e áreas contínuas; o motor repete enquanto o efeito durar.
- Efeitos direcionais (disparo, rajada, corrente, investida, avisos em cone e linha, projéteis) apontam para a **direita**: girar ou espelhar no motor conforme a direção.

## Uso no Godot 4

Importar os PNG com filtro **Nearest** (Projeto > Configurações > Renderização > Texturas > Filtro padrão = Nearest) e sem mipmaps. Exemplo de carregamento a partir do JSON:

```gdscript
static func carregar_efeito(nome: String, cat: String) -> SpriteFrames:
	var base := "res://assets/efeitos/%s/%s" % [cat, nome]
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(base + ".json"))
	var tex: Texture2D = load(base + ".png")
	var sf := SpriteFrames.new()
	sf.set_animation_loop("default", meta.loop)
	sf.set_animation_speed("default", meta.fps)
	for i in int(meta.frames):
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2((i % int(meta.cols)) * meta.frame_w, (i / int(meta.cols)) * meta.frame_h, meta.frame_w, meta.frame_h)
		sf.add_frame("default", at)
	return sf
```

No `AnimatedSprite2D`, use `centered = false` e `offset = -Vector2(meta.anchor[0], meta.anchor[1])`, então a posição do nó é o ponto de âncora. Para efeitos de luz ficarem ainda mais vivos sobre cenário claro, dá para usar `CanvasItemMaterial` com `blend_mode = BLEND_MODE_ADD` nos efeitos de brilho; no chão escuro do jogo o modo normal já funciona.

## Efeitos em duas camadas

- **Corte Giratório (`corte_largo`)**: `humano/hum_corte_largo_tras` (atrás do personagem) e `humano/hum_corte_largo_frente` (na frente), mesmo ponto, mesmo quadro, tocados juntos. Raio de 2 tiles, o giro ocupa os primeiros 0,45 s (9 quadros a 20 fps) e o resto é o rastro sumindo.
- **Arrancada (`arrancada`)**: `humano/hum_arrancada` com âncora no ponto de saída; o dash anda 136 px (4 tiles) para a direita nos primeiros 0,18 s, cortando numa faixa de 1,2 tile (marcada no chão) com impactos que jogam faíscas e areia para os dois lados. Espelhar ou girar conforme a direção e tocar `combate/esquiva_poeira` na saída.

## Clima do Deserto de Absinto (`ambiente/`)

Cenas de exemplo montadas com estes efeitos: `_previa/cena_deserto_noite.gif` e `_previa/cena_tempestade_amargo.gif` (script `tools/vfx/cena_deserto.py`).

- **Ladrilháveis** (`amargo_po_dia`, `amargo_po_noite`, `tempestade_amargo_nevoa`, `tempestade_amargo_graos`): repetem lado a lado e em cima/baixo, e o último quadro emenda no primeiro. Cobrir a tela com um `TextureRect` em modo tile (ou um `ParallaxLayer` com `motion_mirroring` do tamanho do quadro) numa `CanvasLayer` acima do mundo e abaixo da interface.
- **Dia e noite:** de dia use `amargo_po_dia`; à noite troque por `amargo_po_noite` e espalhe `areia_veios_noite` pelo chão.
- **Tempestade de Amargo (evento):** ligar `tempestade_amargo_nevoa` (fundo, ~90% de opacidade) + `amargo_po_dia` + `tempestade_amargo_graos` (frente). Tocar `tempestade_amargo_rajada`, ampliada 2x, de vez em quando atravessando a tela. Escurecer o mundo com um `CanvasModulate` puxado para cinza-esverdeado (ex.: `#8a9480`).
- **Não-Julgados:** `naojulgado_brilho_noite` vai por cima do sprite do morto, com âncora no pé; só à noite.
- **Limite do mundo (`limite_tempestade`):** em vez de parede, uma muralha de tempestade de Amargo nas bordas do mapa. Ladrilha na horizontal; o topo do quadro é o lado de fora. Girar para cada borda, pôr acima do mundo e, perto do limite, escurecer a tela e frear o jogador aos poucos (o vento empurra de volta).
- **A Vela:** `vela_ar_limpo_chao` (camada do chão) e `vela_ar_limpo_borda` (frente) centrados na base da Vela, raio de ~140x70 px; `vela_lampada_arco` no topo do poste. Dentro do raio, esconder a camada de pó Amargo (máscara elíptica ou `light_mask`). Para a luz da Vela iluminar personagens, somar um `PointLight2D` branco-azulado no mesmo ponto.

## Como gerar de novo ou criar efeitos novos

O gerador está em `tools/vfx` (Python + numpy + Pillow, roda na nuvem). Ver `tools/vfx/README.md`.

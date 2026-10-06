# Barra de HUD (v1, Deserto de Absinto)

Latão gasto pela areia, couro costurado e orbes de vidro verde do Amargo, com uma gaiola de latão.
Prévia: `previa/barra_hud.png` (1280x720) e `previa/barra_hud_detalhe_2x.png`.

- `1x/`: peças no tamanho da tela base 1280x720. `2x/`: as mesmas peças em dobro, para telas grandes.
- `layout.json`: posição de cada peça, ordem de desenho, cor do líquido por classe e margens de 9-slice.
- `fontes/`: Cinzel Bold (números e títulos), IM Fell (texto) e Silkscreen (números pequenos). Todas são OFL, do Google Fonts, e o Godot 4 importa woff2.

## Orbe no Godot
Desenhe em ordem: fundo, líquido recortado pela base, superfície, vidro e moldura.

```gdscript
func _orbe(c: CanvasItem, pos: Vector2, frac: float, liq: Texture2D) -> void:
	c.draw_texture(T.orbe_fundo, pos)
	var topo := 17.0 + 106.0 * (1.0 - frac)          # liquido_y_topo + liquido_altura
	var src := Rect2(0, topo, 140, 140 - topo)
	c.draw_texture_rect_region(liq, Rect2(pos + Vector2(0, topo), src.size), src)
	if frac > 0.02 and frac < 0.98:
		var meia := sqrt(1.0 - pow((topo - 70.0) / 53.0, 2.0))   # largura da linha na altura do nível
		c.draw_texture_rect(T.orbe_superficie, Rect2(pos + Vector2(70 - 56 * meia, topo - 8), Vector2(112 * meia, 16)), false)
	c.draw_texture(T.orbe_vidro, pos)
	c.draw_texture(T.orbe_moldura_vida, pos)   # ou orbe_moldura_recurso
```

A recarga das skills é desenhada no código: um setor escuro (`draw_polygon` em leque) sobre o ícone, abaixo de `slot_sombra` e da moldura, com os segundos em Cinzel 16.

## Regerar
Fontes em `assets/ui/src/barra/` (`pecas.html` desenha tudo em HTML e SVG). Sirva a pasta com `python3 -m http.server 8766`, crie um link `icones` para `assets/icones` e rode:

    node shot.js pecas.html --pecas out2x 2     # cada .peca vira um PNG transparente em 2x
    # reduza para 1x com Pillow (LANCZOS) e rode previa.html para a prévia

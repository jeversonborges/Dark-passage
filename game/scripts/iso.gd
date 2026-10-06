class_name Iso
## Projeção isométrica 2:1 do projeto (elevação 30°, azimute 45°, 64 px/m).
## Mundo em TILES (1 tile = losango de 64x32 px = 0,7071 m). Tile (i,j) -> tela (32(i+j), 16(i-j)).

const TW := 64.0
const TH := 32.0
const PX_M := 64.0
const TILE_M := 0.70710678
const ALTURA_PX := 55.43   # px de tela por metro de altura (64 * cos 30°)

static func to_screen(p: Vector2) -> Vector2:
	return Vector2(32.0 * (p.x + p.y), 16.0 * (p.x - p.y))

static func to_world(s: Vector2) -> Vector2:
	var a := s.x / 32.0
	var b := s.y / 16.0
	return Vector2((a + b) * 0.5, (a - b) * 0.5)

## Direção de sprite (linhas S, SE, E, NE, N, NW, W, SW) a partir de uma direção no mundo.
static func dir8(v: Vector2) -> int:
	if v.length_squared() < 1e-6: return -1
	var s := Vector2(32.0 * (v.x + v.y), 16.0 * (v.x - v.y))
	return posmod(int(round(atan2(s.x, s.y) / (PI / 4.0))), 8)

## Distância em tiles para px de tela ao longo do chão (para desenhar círculos no chão).
static func elipse(raio_tiles: float) -> Vector2:
	return Vector2(raio_tiles * 45.25, raio_tiles * 22.63)

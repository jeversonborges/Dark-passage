# Míssil do Cultista: integração (para a thread "Prévia jogável")

Assets já gerados em `assets/efeitos/cultista/` (e no índice `assets/efeitos/efeitos.json`):

| Folha | Uso |
|---|---|
| `cult_basico_projetil` | projétil do ataque básico (72x32, âncora 58,16, loop) |
| `cult_missil_impacto` | impacto do básico (96x96, âncora 48,46; o chão fica 20 px abaixo da âncora = pé do alvo com o `-40` atual) |
| `cult_conjura_mao` | estalo na mão ao lançar (48x48, âncora 24,24) |
| `cult_sangria_projetil` | Sangria redesenhada como lâmina (64x32, âncora 48,16) |
| `cult_sangria_impacto` | Sangria: corte em X (80x80, âncora 40,38) |

Gerador: `tools/vfx/efeitos_classes.py` (`python3 build.py cult_`). Prévia: `previa_cena.gif`.

## Passos
1. `bash game/tools/sync.sh`
2. Em `game/scripts/client/efeitos.gd`:

```gdscript
# perto de COR_ELEM
const IMPACTO_PROJ := {"cult_basico_projetil": "cult_missil_impacto", "cult_sangria_projetil": "cult_sangria_impacto",
	"projetil_bala": "impacto_bala"}
```

Em `projetil()`, trocar a linha da Sangria:

```gdscript
	elif vfx == "sangria": nome = "cult_sangria_projetil"
	elif vfx == "basico_cultista": nome = "cult_basico_projetil"
```

e, logo depois de `add_child(pr)`:

```gdscript
	if nome == "cult_basico_projetil" or nome == "cult_sangria_projetil":
		folha("cult_conjura_mao", Iso.to_screen(pr.pos) + Vector2(0, -pr.altura))
```

Em `projetil_fim()`, trocar as duas linhas de impacto por:

```gdscript
	if not pr.folha.is_empty():
		folha(IMPACTO_PROJ.get(pr.folha["name"], "cult_sangria_impacto"), Iso.to_screen(pos) + Vector2(0, -40))
```

Nada muda no servidor nem nos dados (`vfx` continua `basico_cultista` / `sangria`).

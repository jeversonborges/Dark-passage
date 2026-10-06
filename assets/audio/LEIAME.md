# Áudio do DARK PASSAGE (lote 1)

Tudo aqui foi gerado por síntese no container, sem samples nem serviços externos. Formato: OGG Vorbis, 44,1 kHz, estéreo.

## Pastas

| Pasta | O que tem |
|---|---|
| `musica/` | 9 trilhas em loop sem emenda (tema, São Lázaro, acampamento, capela, combate, cripta e os 3 chefes: Andras, Celeste, Zacarias) |
| `musica/vinheta/` | vitória sobre chefe, descoberta de área, entrada na cripta |
| `ambiente/` | 17 loops de 60 s por área (a área inicial é um deserto radioativo: vento com areia, Geiger, metal rangendo, rádio, prédios cedendo); `ambiente/pontual/` tem 14 sons para espalhar no mapa |
| `sfx/combate/`, `sfx/status/` | golpes no ar, impactos por material, crítico, excelente, abate, armas de fogo, status |
| `sfx/skills/` | as 36 skills (nomes iguais aos ids de `design/skills-itens/skills.json`) |
| `sfx/monstros/`, `sfx/chefes/` | vozes, ataques, mortes e mecânicas de cada monstro e chefe |
| `sfx/itens/`, `sfx/ui/`, `sfx/passos/` | baús, drops por raridade, forja e refino, interface, passos por piso |

## Como ligar no jogo

`audio.json` é o índice:
- `sons`: id, descrição, arquivos (variações), duração e `loop`.
- `eventos_combate`: evento do combate (`design/combate/sensacao.json`) para id de som.
- `musica_por_area`, `ambiente_por_area`, `passos_por_piso`, `armas_no_ar`.
- `mixagem`: buses sugeridos e regras.

Regras rápidas:
- Sons com várias variações (`golpe_leve_1..5`, `passos/pedra_1..6`): sorteie uma por disparo e varie `pitch_scale` entre 0.95 e 1.05.
- Arquivos com `loop: true` emendam sem clique. No Godot, marque Loop no import do OGG.
- O loudness já vem normalizado por arquivo. Ajuste só o volume dos buses (sugestão: música -6 dB, ambiente -4 dB, sfx 0 dB, ui -2 dB).
- Críticos e excelentes: toque `golpe_critico` / `golpe_excelente` no lugar do golpe normal, ou some `estalo_metal` / `sino_curto` por cima.

## Regerar

```
python3 -m pip install numpy scipy numba soundfile pyloudnorm
cd assets/audio/fontes
python3 build.py                 # tudo
python3 build.py chefes/ skills/anjo   # só o que começa com esses prefixos
```

Cada som é uma função registrada com `@som(...)` em `sfx_*.py`, `ambiente*.py` ou `musica*.py`. Os módulos carregados depois substituem ids repetidos (`ambiente_deserto.py` e `musica_deserto.py` refazem a área inicial). A semente é fixa por id, então regerar dá o mesmo resultado.

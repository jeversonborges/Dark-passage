# Motor de efeitos procedurais (tools/vfx)

Gera os sprite sheets de `assets/efeitos/` a partir de código, sem serviço pago.

    python3 -m pip install --break-system-packages pillow numpy
    cd tools/vfx
    python3 build.py              # todos
    python3 build.py anjo chefe   # só os que contêm esses trechos no nome

## Arquivos

- `vfx.py`: o motor. Desenha campos de intensidade com supersample 4x (blob, anel, disco, linha, polilinha, chama), aplica textura de ruído nas rampas de chama/fumaça, reduz para a resolução nativa e mapeia cada campo numa **rampa de cor fixa** da paleta. Rampas `glow` são luz (fogo, brasa, sagrado, ácido, elétrico, rubro, abismo, alma, faísca, runa, aviso); rampas `solid` são matéria com contorno escuro de 1px (sangue, cinza, pedra, osso, latão, carne, praga, aço) ou semitransparente (fumaça, poeira, sombra).
- `efeitos_combate.py`: combate, status, itens, progresso.
- `efeitos_classes.py`: as habilidades das 6 classes, com ajudantes (`crescent`, `rune_circle`, `star`, `burst`, `motes`, `feather`).
- `efeitos_chefes.py`: chefes e auras.
- `acentos.py`: títulos curtos e acentuação das descrições que vão para o JSON.
- `build.py`: gera sheets, JSON, `efeitos.json` e as prévias em `assets/efeitos/_previa/`.

## Criar um efeito

```python
@effect('meu_efeito', 'combate', (64, 64), 10, fps=16, anchor=(32, 50), desc='Nome: o que faz.')
def _(rng):
    def f(c, t, i):          # t vai de 0 a 1 (em loop, 0 a quase 1); i é o quadro
        c.blob('fogo', 32, 40, 8 * (1 - t), 1.2)
        c.flame('fogo', 32, 50, 5, 30 * t, ph=t)
    return f
```

Regras que mantêm o estilo: blobs grandes com amplitude baixa (até ~0,6), núcleo pequeno e forte; brilho só em pontos; no máximo uma rampa emissiva dominante por efeito (a da classe); matéria (sangue, pedra) com `hard=True`.

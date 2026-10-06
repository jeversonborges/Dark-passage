# Monta as folhas de sprites do jogo a partir dos renders de dp_chars.py.
# Cada folha: 8 linhas (direções) x 10 colunas (idle, walk x4, attack x3, death x2).
# Processo da época: reduz o supersample com AA, paleta indexada de 64 cores sem dither,
# alpha binário e contorno escuro de 1 px. A sombra "blob" é desenhada pelo jogo.
# Uso: python3 make_sheets.py <raw_dir> <saida_dir>
import sys, os
from PIL import Image, ImageFilter
raw, out = sys.argv[1], sys.argv[2]
TAGS = ["idle_0","walk_0","walk_1","walk_2","walk_3","attack_0","attack_1","attack_2","death_0","death_1"]
os.makedirs(out, exist_ok=True)
for kind in sorted(os.listdir(raw)):
    first = Image.open(f"{raw}/{kind}/idle_0_d0.png")
    w, h = first.width // 2, first.height // 2
    sheet = Image.new("RGBA", (w*len(TAGS), h*8))
    for d in range(8):
        for c, t in enumerate(TAGS):
            im = Image.open(f"{raw}/{kind}/{t}_d{d}.png").convert("RGBA").resize((w, h), Image.LANCZOS)
            sheet.paste(im, (c*w, d*h))
    a = sheet.getchannel("A")
    body = a.point(lambda v: 255 if v > 150 else 0)
    outline = body.filter(ImageFilter.MaxFilter(3))
    rgb = sheet.convert("RGB").quantize(64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    res = Image.new("RGBA", sheet.size, (0,0,0,0))
    res.paste((8,6,10,255), mask=outline)
    res.paste(rgb, mask=body)
    res.save(f"{out}/{kind}.png"); print(kind, res.size, (w, h))

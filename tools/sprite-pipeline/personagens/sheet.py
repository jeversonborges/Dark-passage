# Monta as sprite sheets no padrão do jogo a partir dos renders 2x.
# Uso: python3 sheet.py <dir_renders> <dir_saida> [cores]
# Saída: <anim>.png (linhas = 8 direções, colunas = quadros), <anim>.gif de prévia
# (direção SE) e sprites.json com tamanho do quadro, âncora dos pés e fps.
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFilter
src, dst = sys.argv[1], sys.argv[2]; ncol = int(sys.argv[3]) if len(sys.argv) > 3 else 40
meta = json.load(open(f"{src}/meta.json")); W, H = meta["frame_size"]; ax, ay = meta["anchor"]
os.makedirs(dst, exist_ok=True)
frames = {}; glows = {}
def glow_of(im2x):
    """Brilho dos pontos emissivos (halo, lâmina, frascos), como os itens brilhantes do MU."""
    import numpy as np
    a = np.asarray(im2x).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    hot = ((al > 200) & (rgb.min(-1) > 215)).astype(np.float32)   # quase branco = emissivo estourado
    col = np.where(hot[..., None] > 0, np.maximum(rgb, [255, 214, 150]) * [1, .95, .8], 0)  # tom quente
    def blur(x): return np.asarray(Image.fromarray(x.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    m = blur(hot*255)
    c = np.stack([blur(col[..., k]*hot) for k in range(3)], -1)
    c = np.clip(c / np.maximum(m[..., None]/255, 1e-3), 0, 255)
    out = np.dstack([c, np.clip(m*1.6, 0, 170)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA").resize((im2x.width//2, im2x.height//2), Image.LANCZOS)
for anim, info in meta["anims"].items():
    for d in meta["dirs"]:
        for f in range(info["frames"]):
            im = Image.open(f"{src}/{anim}/{d}_{f:02d}.png").convert("RGBA").resize((W, H), Image.LANCZOS)
            frames[anim, d, f] = im
            glows[anim, d, f] = glow_of(Image.open(f"{src}/{anim}/{d}_{f:02d}.png").convert("RGBA"))
# paleta única por personagem (até 40 cores, sem dither), só com pixels opacos
import numpy as np
X = []
for im in frames.values():
    a = np.asarray(im).reshape(-1, 4); X.append(a[a[:, 3] > 140, :3])
X = np.concatenate(X).astype(np.float32)
rng = np.random.default_rng(1)
# amostra dando peso extra a pixels saturados (detalhes de cor pequenos: faixas, lenço, brilhos)
sat = X.max(1) - X.min(1); w = 1 + (sat/40)**2; w /= w.sum()
S_ = X[rng.choice(len(X), min(len(X), 120000), p=w)]
C = S_[rng.choice(len(S_), ncol, replace=False)]
for it in range(20):
    l = ((S_[:, None, :] - C[None])**2).sum(-1).argmin(1)
    for k in range(ncol):
        if (l == k).any(): C[k] = S_[l == k].mean(0)
def quant(im):
    a = np.asarray(im.convert("RGB")).reshape(-1, 3).astype(np.float32)
    q = C[((a[:, None, :] - C[None])**2).sum(-1).argmin(1)]
    return Image.fromarray(q.reshape(im.height, im.width, 3).astype(np.uint8))
def cell(im, gl):
    body = im.getchannel("A").point(lambda v: 255 if v > 140 else 0)
    rgb = quant(im)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([ax-24, ay-11, ax+24, ay+11], fill=255)
    out.paste((0, 0, 0, 100), mask=sh)
    out.paste((10, 8, 8, 255), mask=body.filter(ImageFilter.MaxFilter(3)))
    out.paste(rgb, mask=body)
    lum = im.convert("RGB").point(lambda v: 255 if v > 238 else 0).convert("L").point(lambda v: 255 if v > 200 else 0)
    hot = Image.composite(lum, Image.new("L", (W, H), 0), body)
    out.paste(im.convert("RGB"), mask=hot)
    return Image.alpha_composite(out, gl)
sheets = {}
for anim, info in meta["anims"].items():
    n = info["frames"]; sheet = Image.new("RGBA", (W*n, H*8))
    gif = []
    for r, d in enumerate(meta["dirs"]):
        for f in range(n):
            c = cell(frames[anim, d, f], glows[anim, d, f]); sheet.paste(c, (f*W, r*H))
            if d == "SE":
                g = Image.new("RGB", (W, H), (22, 20, 22)); g.paste(c, (0, 0), c); gif.append(g.resize((W*2, H*2), Image.NEAREST))
    sheet.save(f"{dst}/{anim}.png")
    gif[0].save(f"{dst}/{anim}_SE.gif", save_all=True, append_images=gif[1:], duration=int(1000/info["fps"]), loop=0)
    sheets[anim] = {"file": f"{anim}.png", "frames": n, "fps": info["fps"], "loop": info["loop"]}
json.dump({"classe": meta["classe"], "frame_size": [W, H], "anchor_feet": [ax, ay],
           "rows_dirs": meta["dirs"], "dirs_note": "direção para onde o personagem olha na tela (S = para baixo)",
           "pixels_per_meter": meta["pixels_per_meter"], "camera": meta["camera"], "palette_colors": ncol,
           "anims": sheets}, open(f"{dst}/sprites.json", "w"), indent=1, ensure_ascii=False)
print("ok", dst, list(sheets))

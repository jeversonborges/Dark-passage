"""Previa das skills de area em 2 camadas e 8 direcoes: tras + personagem + frente, grade 4x2.
uso: python3 prev_area.py anjo_leque_juizo anjo"""
import sys, os, json
import numpy as np
from PIL import Image
from build import floor, comp, sprite, OUT, PREV


def main(base, cat, char, dirs=8, fundo=None):
    meta = json.load(open(os.path.join(OUT, cat, base + '_tras.json')))
    W, H, F = meta['frame_w'], meta['frame_h'], meta['frames']
    ax, ay = meta['anchor']
    T = np.asarray(Image.open(os.path.join(OUT, cat, base + '_tras.png')))
    Fr = np.asarray(Image.open(os.path.join(OUT, cat, base + '_frente.png')))
    s = sprite(char)
    PW, PH = W + 8, H + 8
    bg = floor(PW, PH)
    ordem = [3, 2, 1, 4, 0, 5, 6, 7] if dirs == 8 else list(range(dirs))
    gifs = []
    for k in range(F):
        tiles = []
        for d in ordem[:dirs]:
            sl = (slice(d * H, d * H + H), slice(k * W, k * W + W))
            im = comp(bg, T[sl], 4, 4)
            im = comp(im, s, 4 + ax - s.shape[1] // 2, 4 + ay - s.shape[0] + 6)
            im = comp(im, Fr[sl], 4, 4)
            tiles.append(im)
        cols = 4 if dirs == 8 else dirs
        rows = (len(tiles) + cols - 1) // cols
        g = np.zeros((rows * PH, cols * PW, 3), np.float32)
        for j, t in enumerate(tiles):
            g[(j // cols) * PH:(j // cols + 1) * PH, (j % cols) * PW:(j % cols + 1) * PW] = t
        im = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8))
        gifs.append(im)
    big = [g.resize((g.width * 2, g.height * 2), Image.NEAREST) for g in gifs]
    big[0].save(os.path.join(PREV, base + '_8dir.gif'), save_all=True, append_images=big[1:],
                duration=int(1000 / meta['fps']), loop=0, disposal=1)
    # direcao leste grande, para conferir detalhe
    one = []
    for k in range(F):
        sl = (slice(0, H), slice(k * W, k * W + W))
        im = comp(bg, T[sl], 4, 4); im = comp(im, s, 4 + ax - s.shape[1] // 2, 4 + ay - s.shape[0] + 6)
        im = comp(im, Fr[sl], 4, 4)
        one.append(Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).resize((PW * 3, PH * 3), Image.NEAREST))
    one[0].save(os.path.join(PREV, base + '.gif'), save_all=True, append_images=one[1:],
                duration=int(1000 / meta['fps']), loop=0, disposal=1)
    strip = Image.new('RGB', (PW * 2 * 4, PH * 2 * ((F + 3) // 4)))
    for k, g in enumerate(one):
        strip.paste(g.resize((PW * 2, PH * 2), Image.NEAREST), ((k % 4) * PW * 2, (k // 4) * PH * 2))
    strip.save(os.path.join(PREV, base + '_quadros.png'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2])

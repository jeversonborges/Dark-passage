# brilho de raridade da arte da mochila (usado por gerar_itens.py e arte_pronta.py)
import numpy as np
from PIL import Image, ImageFilter
from posproc import _hex

def brilho(out, cor, tam):
    a = np.asarray(out)
    m = Image.fromarray(((a[..., 3] > 0) * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(max(1.2, tam / 24)))
    halo = Image.new("RGBA", out.size, _hex(cor) + (0,)); halo.putalpha(m.point(lambda v: int(v * 0.8)))
    return Image.alpha_composite(halo, out)

# Pós-processamento comum: sujeira leve, paleta indexada sem dither, contorno 1px e brilho de raridade (estilo MU).
import numpy as np
from PIL import Image, ImageFilter
K = (10, 8, 8)
rng = np.random.default_rng(13)

def _hex(c): c = c.lstrip("#"); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def sujar(im, forca=0.22):
    a = np.asarray(im).astype(float) / 255
    rgb, al = a[..., :3], a[..., 3:]
    h, w = al.shape[:2]
    n = np.asarray(Image.fromarray((rng.random((h//8+1, w//8+1))*255).astype("uint8")).resize((w, h), Image.BICUBIC)) / 255
    grad = np.linspace(1.04, 0.80, h)[:, None, None]
    out = rgb * (1 - forca/2 + forca*n[..., None]) * grad
    g = out.mean(-1, keepdims=True); out = g + (out - g) * 0.88
    lum = rgb.max(-1, keepdims=True); keep = np.clip((lum - 0.80) / 0.12, 0, 1)   # emissivos não sujam
    out = out * (1 - keep) + rgb * keep
    return Image.fromarray((np.clip(np.concatenate([out, al], -1), 0, 1) * 255).astype("uint8"))

def indexar(im, cores):
    a = np.asarray(im).copy(); alpha = a[..., 3]
    rgb = Image.fromarray(a[..., :3]).quantize(cores, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")
    return np.dstack([np.asarray(rgb), alpha])

def contorno(a, limiar=120):
    m = a[..., 3] > limiar; edge = np.zeros_like(m)
    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)): edge |= np.roll(np.roll(m, dy, 0), dx, 1)
    edge &= ~m; a = a.copy(); a[..., 3] = np.where(m, 255, 0); a[edge] = (*K, 255); return a

def finalizar_item(im256, tam, cor_brilho=None):
    s = sujar(im256).resize((tam, tam), Image.LANCZOS)
    a = contorno(indexar(s, 40 if tam == 64 else 28))
    out = Image.fromarray(a)
    if cor_brilho:
        m = Image.fromarray(((a[..., 3] > 0) * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(tam/22))
        halo = Image.new("RGBA", (tam, tam), _hex(cor_brilho) + (0,)); halo.putalpha(m.point(lambda v: int(v * 0.85)))
        out = Image.alpha_composite(halo, out)
    return out

def finalizar_skill(im256, tam):
    s = sujar(im256, 0.16).resize((tam, tam), Image.LANCZOS)
    a = indexar(s, 48 if tam == 64 else 36); a[..., 3] = np.where(a[..., 3] > 100, 255, 0)
    return Image.fromarray(a)

def volume(im, raio=7, forca=0.55):
    """Dá volume (luz de cima-esquerda) a partir da silhueta e dos traços internos, como relevo pintado à mão."""
    a = np.asarray(im).astype(float) / 255
    rgb, al = a[..., :3], a[..., 3]
    lum = rgb.mean(-1)
    alt = np.asarray(Image.fromarray((al * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(raio))).astype(float) / 255
    det = np.asarray(Image.fromarray((np.clip(lum, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2))).astype(float) / 255
    h = alt * 1.0 + det * 0.35
    gy, gx = np.gradient(h)
    n = np.dstack([-gx * 18, -gy * 18, np.ones_like(h)]); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array([-0.55, -0.65, 0.52]); L /= np.linalg.norm(L)
    s = (n @ L) - L[2]                                    # 0 em superfície plana
    lumf = 1 + forca * np.clip(s, -0.6, 0.8)
    spec = np.clip(s - 0.35, 0, 1) ** 1.5 * 0.9           # brilho especular nas bordas viradas para a luz
    out = rgb * lumf[..., None] + spec[..., None] * np.array([1.0, 0.95, 0.85])
    ao = 1 - 0.28 * np.clip(1 - alt * 1.6, 0, 1)          # oclusão leve perto das bordas
    out = out * ao[..., None]
    em = (rgb.max(-1) > 0.86)[..., None]                   # emissivos ficam como estão
    out = np.where(em, rgb, out)
    return Image.fromarray((np.clip(np.dstack([out, al]), 0, 1) * 255).astype("uint8"))

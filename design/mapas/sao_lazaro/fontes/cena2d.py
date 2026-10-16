# Monta uma imagem do mapa com a arte real do kit (pisos, objetos, luzes) e os sprites de mobs e NPCs,
# na mesma câmera do jogo (iso 2:1, 30°, azimute 45°, 64 px por metro na escala 1).
# É a "prévia honesta": o que aparece aqui é o que o jogo vai desenhar, com a mesma arte.
# Uso como biblioteca: cena2d.render(mapa_json, (x0, y0, x1, y1), escala, saida, ...)
import json, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

PF = "/mnt/project-files"
AMB = f"{PF}/assets/ambiente"
AQUI = os.path.dirname(os.path.abspath(__file__))
HW, HH = 45.255, 22.627          # meio-losango de 1 m na escala 1 (64 px/m, 2:1)

# terreno do layout -> piso do kit (tiles/<piso>.png); a ordem diz quem fica por cima na emenda
PISO = {"a": "areia", "u": "areia", "d": "areia", "h": None, "y": "areia_vitrificada", "q": "calcamento",
        "s": "leito_rachado", "t": "terra", "z": "cinza", "c": "calcamento", "g": "cemiterio", "l": "laje_capela",
        "m": "chapa_matadouro", "w": "agua_toxica", "r": "agua_toxica", "b": "lama", "e": "mata_morta",
        "p": "lama", "f": "mata_morta", "v": "terra", "k": "cascalho", "n": "entulho", "x": "asfalto_rachado"}
ORDEM = ["areia", "mata_morta", "terra", "leito_rachado", "lama", "cinza", "areia_vitrificada", "entulho", "cemiterio",
         "cascalho", "asfalto_rachado", "calcamento", "laje_capela", "chapa_matadouro", "agua_toxica"]
TINT = {"u": 1.06, "d": 1.12}     # dunas um pouco mais claras no topo

_objs = {}
def obj(kind):
    """(imagem RGBA, âncora, meta) do objeto do kit; None se não tem arte."""
    if kind in _objs: return _objs[kind]
    p = f"{AMB}/objetos/{kind}.png"
    r = None
    if os.path.exists(p):
        m = json.load(open(f"{AMB}/objetos/{kind}.json"))
        r = (Image.open(p).convert("RGBA"), m["anchor"], m)
    _objs[kind] = r
    return r

# arte que ainda não existe no kit: na prévia entra um parecido do kit (o jogo usa o mesmo até o Cenário fazer a peça)
SUBST = {"flor_absinto_lata": "flor_lume", "flor_absinto": "flor_lume_2", "varal_lanternas": "varal_roupas",
         "antena_radio": "poste_telegrafo", "escotilha_silo": "ralo_ferro"}
def kind_arte(p):
    k = SUBST.get(p["kind"], p["kind"])
    if obj(k): return k
    o = p.get("orient")
    for suf in (("_a", "_b") if o != "y" else ("_b", "_a")):
        if obj(k + suf): return k + suf
    return None

_patch = {}
def patch(piso):
    """Bloco periódico 256x128 do piso montado com as 16 células (sem emenda)."""
    if piso in _patch: return _patch[piso]
    at = Image.open(f"{AMB}/tiles/{piso}.png").convert("RGBA")
    out = Image.new("RGBA", (256, 128))
    for i in range(4):
        for j in range(4):
            c = at.crop((i * 64, j * 32, i * 64 + 64, j * 32 + 32))
            for (bx, by) in ((0, 0), (128, 64)):          # o retângulo 256x128 tem duas cópias do bloco 4x4
                cx, cy = ((i + j) * 32 + bx) % 256, ((i - j) * 16 + by) % 128
                for ox in (-256, 0, 256):
                    for oy in (-128, 0, 128):
                        out.alpha_composite(c, (cx - 32 + ox, cy - 16 + oy)) if -64 < cx - 32 + ox < 256 and -32 < cy - 16 + oy < 128 else None
    a = np.asarray(out).astype(np.float32)
    _patch[piso] = a[..., :3]
    return _patch[piso]

def textura(piso, W, H, s, ox, oy):
    """Piso repetido cobrindo a tela (W x H), na escala s, alinhado com a grade do mundo."""
    pt = patch(piso)
    ph, pw = max(2, int(round(128 * s))), max(2, int(round(256 * s)))
    small = np.asarray(Image.fromarray(pt.astype(np.uint8)).resize((pw, ph), Image.LANCZOS)).astype(np.float32)
    ry, rx = H // ph + 3, W // pw + 3
    big = np.tile(small, (ry, rx, 1))
    sx, sy = int(ox % pw), int(oy % ph)
    return big[ph - sy: ph - sy + H, pw - sx: pw - sx + W]

def render(M, caixa, s, saida, mobs=True, npcs=True, rotulos=None, luz_amb=(.46, .47, .56), escurecer=1.0,
           neblina=True, seed=3, titulo=None, subtitulo=None, max_lado=None, poeira=True):
    x0, y0, x1, y1 = caixa
    T = M["terreno"]; N = M["size"]
    # tela: cantos do retângulo do mundo
    def scr0(x, y): return ((x + y) * HW * s, (x - y) * HH * s)
    cs = [scr0(x, y) for x, y in ((x0, y0), (x0, y1), (x1, y0), (x1, y1))]
    minx, maxx = min(c[0] for c in cs), max(c[0] for c in cs)
    miny, maxy = min(c[1] for c in cs), max(c[1] for c in cs)
    W, H = int(maxx - minx), int(maxy - miny)
    PADT = int(260 * s)        # espaço para o que é alto na borda de cima
    H += PADT
    def scr(x, y): return ((x + y) * HW * s - minx, (x - y) * HH * s - miny + PADT)
    rnd = random.Random(seed)

    # ---------------- chão: um piso por camada, emendas suaves com ruído
    # mapa de tela -> tile (afim inversa)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xx + minx) / (HW * s); v = (yy - PADT + miny) / (HH * s)
    TX = (u + v) / 2; TY = (u - v) / 2
    rng = np.random.default_rng(seed)
    nz = ndimage.zoom(rng.random((H // 24 + 3, W // 24 + 3)), 24, order=3)[:H, :W]
    nz2 = ndimage.zoom(rng.random((H // 6 + 3, W // 6 + 3)), 6, order=1)[:H, :W]
    jit = (nz - .5) * 1.4 + (nz2 - .5) * .5
    TXi = np.clip((TX + jit * .5).astype(int), 0, N - 1); TYi = np.clip((TY - jit * .5).astype(int), 0, N - 1)
    TA = np.array([list(r) for r in T])
    cod = TA[TXi, TYi]
    ox, oy = -minx, PADT - miny
    img = np.zeros((H, W, 3), np.float32)
    presentes = {PISO.get(c) for c in np.unique(cod)} - {None}
    for piso in [p for p in ORDEM if p in presentes]:
        mask = np.isin(cod, [c for c, p in PISO.items() if p == piso])
        if not mask.any(): continue
        m = ndimage.gaussian_filter(mask.astype(np.float32), 1.2 * max(.6, s * 2))
        img = img * (1 - m[..., None]) + textura(piso, W, H, s, ox, oy) * m[..., None]
    for c, f in TINT.items():
        m = ndimage.gaussian_filter((cod == c).astype(np.float32), 6 * s + 1)
        img *= 1 + (f - 1) * m[..., None]
    # abismo: preto com um fio de luz fria na beira
    ab = ndimage.gaussian_filter((cod == "h").astype(np.float32), 3 * s + 1)
    img = img * (1 - ab[..., None]) + np.array([4, 4, 6], np.float32) * ab[..., None]
    # sombra de nuvem / variação larga para o chão não ficar chapado
    var = ndimage.zoom(rng.random((H // 120 + 3, W // 120 + 3)), 120, order=3)[:H, :W]
    img *= (.86 + .26 * var)[..., None]
    # água: brilho verde do Amargo
    ag = ndimage.gaussian_filter(np.isin(cod, ["w", "r"]).astype(np.float32), 2 * s + .5)
    img += np.array([10, 38, 18], np.float32) * ag[..., None]
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")

    # ---------------- objetos, ordenados por profundidade (y de tela da âncora)
    lista = []
    def dentro(x, y, folga=6): return x0 - folga <= x <= x1 + folga and y0 - folga <= y <= y1 + folga
    for p in M["props"]:
        if p.get("invisivel") or not dentro(p["x"], p["y"]): continue
        k = kind_arte(p)
        if not k: continue
        chao = p.get("camada") == "chao"
        sx, sy = scr(p["x"], p["y"])
        lista.append((0 if chao else 1, sy, sx, ("obj", k, p)))
    fr_cache = {}
    def frame_mob(kind, i):
        d = f"{PF}/assets/monstros/{kind}"
        if not os.path.exists(f"{d}/meta.json"): return None
        if kind not in fr_cache:
            me = json.load(open(f"{d}/meta.json")); fw, fh = me["frame_size"]
            sh = Image.open(f"{d}/{kind}_idle.png").convert("RGBA")
            fr_cache[kind] = (sh, fw, fh, me["anchor"], me["dirs"])
        sh, fw, fh, an, dirs = fr_cache[kind]
        row = dirs.index(["SE", "S", "SW", "E", "W"][i % 5])
        col = i % 4
        return sh.crop((col * fw, row * fh, col * fw + fw, row * fh + fh)), an
    def frame_npc(nome, i):
        d = f"{PF}/assets/personagens/{nome}"
        if not os.path.exists(f"{d}/sprites.json"): return None
        key = "npc:" + nome
        if key not in fr_cache:
            me = json.load(open(f"{d}/sprites.json")); fw, fh = me["frame_size"]
            sh = Image.open(f"{d}/idle.png").convert("RGBA")
            fr_cache[key] = (sh, fw, fh, me["anchor_feet"], me["rows_dirs"])
        sh, fw, fh, an, dirs = fr_cache[key]
        row = dirs.index(["S", "SE", "SW"][i % 3])
        return sh.crop(((i % 4) * fw, row * fh, (i % 4) * fw + fw, row * fh + fh)), an
    if mobs:
        for g in M.get("spawns", []):
            if g.get("so_para") or g.get("so_por_missao") or not dentro(g["x"], g["y"]): continue
            kind = g.get("kind_design", g["kind"]) if os.path.exists(f"{PF}/assets/monstros/{g.get('kind_design', g['kind'])}") else (g.get("variante") or g["kind"])
            if not os.path.exists(f"{PF}/assets/monstros/{kind}"): kind = g.get("substituto", kind)
            for c in range(g["count"]):
                a = c / max(1, g["count"]) * 6.28 + rnd.random()
                x, y = g["x"] + math.cos(a) * (1.1 if g["count"] > 1 else 0), g["y"] + math.sin(a) * (1.1 if g["count"] > 1 else 0)
                sx, sy = scr(x, y)
                lista.append((1, sy, sx, ("mob", kind, rnd.randrange(20))))
    NPCV = json.load(open(f"{AQUI}/npc_visual.json")) if os.path.exists(f"{AQUI}/npc_visual.json") else {}
    if npcs:
        for n in M.get("npcs", []):
            if not dentro(n["x"], n["y"]): continue
            vis = NPCV.get(n["id"], "humano")
            sx, sy = scr(n["x"], n["y"])
            lista.append((1, sy, sx, ("npc", vis, rnd.randrange(12))))
    lista.sort(key=lambda o: (o[0], o[1], o[2]))
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sombra)
    for camada, sy, sx, it in lista:
        if it[0] in ("mob", "npc"):
            sd.ellipse([sx - 20 * s, sy - 8 * s, sx + 20 * s, sy + 8 * s], fill=(0, 0, 0, 110))
    base = Image.alpha_composite(base, sombra.filter(ImageFilter.GaussianBlur(max(1, 3 * s))))
    cache_s = {}
    for camada, sy, sx, it in lista:
        if it[0] == "obj":
            _, k, p = it
            im, an, _m = obj(k)
            if k not in cache_s:
                cache_s[k] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS) if s != 1 else im
            sp = cache_s[k]
            base.alpha_composite(sp, (int(sx - an[0] * s), int(sy - an[1] * s))) if True else None
        else:
            r = frame_mob(it[1], it[2]) if it[0] == "mob" else frame_npc(it[1], it[2])
            if not r: continue
            fr, an = r
            fr = fr.resize((max(1, int(fr.width * s)), max(1, int(fr.height * s))), Image.LANCZOS)
            base.alpha_composite(fr, (int(sx - an[0] * s), int(sy - an[1] * s)))

    # ---------------- luz: ambiente frio de lua + poças das fontes locais (multiplica) + emissivos preservados
    A = np.asarray(base).astype(np.float32)[..., :3] / 255
    f = 4
    Lh, Lw = H // f + 1, W // f + 1
    L = np.zeros((Lh, Lw, 3), np.float32) + np.array(luz_amb, np.float32) * escurecer
    gy, gx = np.mgrid[0:Lh, 0:Lw].astype(np.float32)
    for l in M.get("luzes", []):
        x, y = l[0], l[1]
        if not dentro(x, y, 14): continue
        cor = np.array(l[2:5], np.float32); r = l[5]
        sx, sy = scr(x, y); sx /= f; sy /= f
        R = r * HW * s / f * 1.25
        x_a, x_b = int(max(0, sx - R * 1.6)), int(min(Lw, sx + R * 1.6))
        y_a, y_b = int(max(0, sy - R)), int(min(Lh, sy + R * .9))
        if x_a >= x_b or y_a >= y_b: continue
        dx = (gx[y_a:y_b, x_a:x_b] - sx) / R; dy = (gy[y_a:y_b, x_a:x_b] - sy) / (R * .55)
        d2 = dx * dx + dy * dy
        fall = np.clip(1 - d2, 0, 1) ** 2 * 1.15 + np.exp(-d2 * 9) * .9
        L[y_a:y_b, x_a:x_b] += cor * fall[..., None] * .95
    L = np.asarray(Image.fromarray(np.clip(L / 3 * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255 * 3
    lum = A.max(-1)
    emis = np.clip((lum - .62) / .3, 0, 1) ** 1.5
    out = A * L * 1.12
    out = out * (1 - emis[..., None]) + np.maximum(out, A * 1.05) * emis[..., None]
    # brilho suave em volta dos emissivos e das luzes
    glow = ndimage.gaussian_filter(out * (emis[..., None] * .8), (6 * s + 2, 6 * s + 2, 0))
    out = out + glow * .55
    if poeira:   # Amargo caindo: pontinhos verdes
        for _ in range(int(W * H / 9000)):
            px, py = rnd.randrange(W), rnd.randrange(H)
            out[py:py + 2, px:px + 2] += np.array([.12, .26, .12]) * rnd.random()
    if neblina:   # névoa baixa e vinheta
        fog = np.array([.10, .12, .11], np.float32)
        d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
        vig = np.clip(1.12 - d ** 1.7, .2, 1)[..., None]
        nb = (ndimage.zoom(rng.random((H // 90 + 3, W // 90 + 3)), 90, order=3)[:H, :W] * .16)[..., None]
        out = out * vig + fog * (1 - vig) * .5 + fog * nb
    if "jogavel" in M:   # a moldura some na poeira da tempestade (como a câmera do jogo)
        J = M["jogavel"]
        fx = np.maximum(np.maximum(J["x0"] - TX, TX - J["x1"]), np.maximum(J["y0"] - TY, TY - J["y1"]))
        fz = np.clip((fx + 1) / 9, 0, 1)[..., None] ** .8
        poeira_c = np.array([.07, .075, .07], np.float32) + .03 * var[..., None]
        out = out * (1 - fz) + poeira_c * fz
    # paleta puxada para sépia frio
    g = out.mean(-1, keepdims=True)
    out = out * .82 + g * np.array([1.02, 1.0, .96]) * .18
    im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    FT = f"{AQUI}/PirataOne-Regular.ttf"; FS = f"{AQUI}/IMFeENsc28P.ttf"; FIt = f"{AQUI}/IMFeENit28P.ttf"
    if rotulos:
        fz = max(16, int(46 * s * 2.2)); fz2 = max(12, int(fz * .55))
        fT = ImageFont.truetype(FT, fz); fS_ = ImageFont.truetype(FIt, fz2)
        for (x, y, nome, sub) in rotulos:
            if not dentro(x, y, 0): continue
            sx, sy = scr(x, y)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2)):
                d.text((sx + dx, sy + dy), nome, font=fT, fill=(0, 0, 0), anchor="mm")
            d.text((sx, sy), nome, font=fT, fill=(236, 222, 190), anchor="mm")
            if sub:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    d.text((sx + dx, sy + fz * .72 + dy), sub, font=fS_, fill=(0, 0, 0), anchor="mm")
                d.text((sx, sy + fz * .72), sub, font=fS_, fill=(196, 206, 170), anchor="mm")
    if titulo:
        fz = max(40, int(W / 22))
        d.text((int(W * .025) + 3, int(H * .03) + 3), titulo, font=ImageFont.truetype(FT, fz), fill=(0, 0, 0))
        d.text((int(W * .025), int(H * .03)), titulo, font=ImageFont.truetype(FT, fz), fill=(236, 222, 190))
        if subtitulo:
            d.text((int(W * .027), int(H * .03) + fz * 1.15), subtitulo, font=ImageFont.truetype(FS, int(fz * .36)), fill=(150, 200, 140))
    if max_lado and max(im.size) > max_lado:
        k = max_lado / max(im.size); im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    im.save(saida, quality=90) if saida.endswith(".jpg") else im.save(saida)
    return im

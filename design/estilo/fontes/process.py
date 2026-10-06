import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
rng = np.random.default_rng(7)
NS = ['anjo','demonio','cultista','humano','mutante','tecnomancer']

def noise(h, w, scales=(2,6,18)):
    n = np.zeros((h, w))
    for s in scales:
        small = rng.random((h//s+2, w//s+2))
        n += np.array(Image.fromarray((small*255).astype('uint8')).resize((w+ s*2, h+ s*2), Image.BICUBIC))[:h,:w]/255
    return n/len(scales)

def grit(im):
    a = np.asarray(im).astype(float)/255
    rgb, al = a[...,:3], a[...,3:]
    h, w = al.shape[:2]
    n = noise(h, w)[...,None]
    rgb = rgb*(0.78+0.32*n)                               # sujeira
    grad = np.linspace(1.05, 0.62, h)[:,None,None]         # luz de cima, pés no escuro
    side = np.linspace(1.0, 0.85, w)[None,:,None]
    rgb = rgb*grad*side
    g = rgb.mean(-1, keepdims=True); rgb = g + (rgb-g)*0.82 # dessatura
    rgb = rgb*np.array([1.0,0.96,0.92])                    # tom sépia frio
    src = a[...,:3]; lum = src.max(-1, keepdims=True)
    keep = np.clip((lum-0.78)/0.15, 0, 1)                   # brilhos (halo, brasas, runas) não sujam
    rgb = rgb*(1-keep) + src*keep
    return Image.fromarray((np.clip(np.concatenate([rgb,al],-1),0,1)*255).astype('uint8'))

def spritify(im, height=104, colors=40):
    w = round(im.width*height/im.height)
    s = im.resize((w, height), Image.LANCZOS)
    a = np.asarray(s).copy()
    alpha = a[...,3] > 110
    rgb = Image.fromarray(a[...,:3]).quantize(colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    out = np.dstack([np.asarray(rgb), np.where(alpha,255,0).astype('uint8')])
    # contorno escuro de 1px por fora
    m = alpha; edge = np.zeros_like(m)
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)): edge |= np.roll(np.roll(m,dy,0),dx,1)
    edge &= ~m
    out[edge] = (10,8,8,255)
    return Image.fromarray(out)

sprites = {}
for n in NS:
    c = grit(Image.open(f'concept_{n}.png').convert('RGBA'))
    c.save(f'grit_{n}.png')
    sprites[n] = spritify(c); sprites[n].save(f'sprite_{n}.png')

# ---------- cena: rua em ruínas à noite (640x360, ampliada 2x) ----------
W, H = 640, 360
img = Image.new('RGBA', (W, H), (12,10,11,255)); d = ImageDraw.Draw(img)
# chão isométrico de pedras
TW, TH = 48, 24
for j in range(-2, 34):
    for i in range(-2, 16):
        cx = i*TW + (j%2)*TW//2; cy = 120 + j*TH//2
        if random.random() < 0.08: continue                 # buraco/terra
        v = random.randint(27, 36); tint = (v+5, v+2, v)
        d.polygon([(cx,cy-TH//2+1),(cx+TW//2-1,cy),(cx,cy+TH//2-1),(cx-TW//2+1,cy)], fill=tint, outline=(19,17,17))
        d.line([(cx-TW//2+3,cy),(cx,cy-TH//2+2)], fill=(v+11,v+8,v+6))
        if random.random() < 0.25:
            d.line([(cx-8,cy-2),(cx-2,cy+1),(cx+6,cy-3)], fill=(16,14,14))
# muro gótico em ruínas ao fundo
for x in range(0, W, 16):
    top = 40 + int(18*np.sin(x*0.05)) + random.randint(-6,10) if not 200<x<440 else 30+random.randint(0,6)
    for y in range(top, 130, 8):
        off = 8 if (y//8)%2 else 0
        v = random.randint(28,40)
        d.rectangle([x+off-8, y, x+off+7, y+7], fill=(v+4,v,v-2), outline=(14,12,12))
# janela em arco com brilho vermelho (catedral)
d.rectangle([292,52,348,128], fill=(8,6,6))
d.pieslice([292,30,348,86], 180, 360, fill=(8,6,6))
glow = Image.new('RGBA',(W,H),(0,0,0,0)); gd = ImageDraw.Draw(glow)
gd.rectangle([298,60,342,126], fill=(150,20,14,255)); gd.pieslice([298,38,342,82],180,360, fill=(150,20,14,255))
for x in (306,320,334): d.line([(x,40),(x,128)], fill=(10,8,8), width=2)
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
img.alpha_composite(Image.composite(glow, Image.new('RGBA',(W,H),(0,0,0,0)), glow).filter(ImageFilter.GaussianBlur(1)))
for x in (306,320,334): d.line([(x,40),(x,128)], fill=(10,8,8), width=2)
d.line([(292,90),(348,90)], fill=(10,8,8), width=2)
# poste a gás quebrado com poça de luz
light = Image.new('RGBA',(W,H),(0,0,0,0)); ld = ImageDraw.Draw(light)
ld.ellipse([480,210,620,290], fill=(255,140,50,70)); ld.ellipse([538,80,566,108], fill=(255,170,80,200))
img.alpha_composite(light.filter(ImageFilter.GaussianBlur(14)))
d.rectangle([550,96,554,252], fill=(20,18,18)); d.polygon([(542,96),(562,96),(558,84),(546,84)], fill=(40,32,26), outline=(10,8,8))
d.rectangle([546,90,558,96], fill=(255,190,100))
# sangue e entulho
for _ in range(14):
    x,y = random.randint(20,620), random.randint(150,350); r = random.randint(2,6); c = (46+random.randint(0,24),6,6)
    for _ in range(5):
        ox, oy = random.randint(-r*2,r*2), random.randint(-r,r); rr = random.randint(1,r)
        d.ellipse([x+ox-rr*2,y+oy-rr,x+ox+rr*2,y+oy+rr], fill=c)
for _ in range(30):
    x,y = random.randint(0,640), random.randint(130,360)
    d.polygon([(x,y),(x+random.randint(3,8),y+2),(x+2,y+random.randint(2,5))], fill=(50,46,44), outline=(14,12,12))
# fogo de barril
d.rectangle([90,226,108,250], fill=(40,30,24), outline=(10,8,8)); d.line([(90,234),(108,234)], fill=(70,40,20))
fire = Image.new('RGBA',(W,H),(0,0,0,0)); fd = ImageDraw.Draw(fire)
fd.ellipse([40,180,160,280], fill=(255,110,30,60)); fd.polygon([(92,226),(99,206),(102,214),(106,204),(108,226)], fill=(255,150,40,255))
img.alpha_composite(fire.filter(ImageFilter.GaussianBlur(6))); d.polygon([(94,226),(99,212),(102,218),(105,210),(106,226)], fill=(255,200,90))

def place(spr, x, y, flip=False):
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    sh = Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse([x-20,y-6,x+20,y+5], fill=(0,0,0,150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5)))
    img.alpha_composite(spr, (x-spr.width//2, y-spr.height+4))
# Arautos à esquerda, Vigília à direita, frente a frente
place(sprites['cultista'], 150, 240); place(sprites['anjo'], 215, 285); place(sprites['demonio'], 280, 330)
place(sprites['tecnomancer'], 490, 240); place(sprites['humano'], 425, 285); place(sprites['mutante'], 360, 332)
# nomes estilo MMO acima das cabeças
from PIL import ImageFont
f = ImageFont.load_default()
for name, x, y, col in (('Cultista',150,240,(230,90,70)),('Anjo',215,285,(230,90,70)),('Demonio',280,330,(230,90,70)),
                        ('Tecnomancer',490,240,(120,190,230)),('Humano',425,285,(120,190,230)),('Mutante',360,332,(120,190,230))):
    tw = d.textlength(name, font=f); tx, ty = x-tw/2, y-118
    for ox,oy in ((1,0),(-1,0),(0,1),(0,-1)): d.text((tx+ox,ty+oy), name, font=f, fill=(0,0,0))
    d.text((tx,ty), name, font=f, fill=col)
# névoa e vinheta
a = np.asarray(img).astype(float)
fog = noise(H, W, (24,60))[...,None]
a[...,:3] = a[...,:3]*(1-0.18*fog) + np.array([70,64,72])*0.18*fog
yy, xx = np.mgrid[0:H,0:W]; v = 1 - 0.75*(((xx-W/2)/(W*0.62))**2 + ((yy-H*0.55)/(H*0.7))**2)
a[...,:3] *= np.clip(v,0.15,1)[...,None]
scene = Image.fromarray(np.clip(a,0,255).astype('uint8')).convert('RGB')
scene.resize((W*2,H*2), Image.NEAREST).save('cena.png')

# folha de sprites: 1x e 3x
sw = sum(s.width for s in sprites.values()) + 7*12
sheet = Image.new('RGB', (sw*3, 120*3), (18,15,16)); x = 12*3
for n in NS:
    s = sprites[n].resize((sprites[n].width*3, sprites[n].height*3), Image.NEAREST)
    sheet.paste(s, (x, 8*3), s); x += s.width + 12*3
sheet.save('sprites_3x.png')
print('ok', [s.size for s in sprites.values()])

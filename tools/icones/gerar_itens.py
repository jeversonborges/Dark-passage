# Gera os ícones de itens a partir de design/skills-itens/itens.json:
#   assets/icones/itens/{64,40,32}/<id>.png  (ícone quadrado: loja, tooltip, barra rápida do HUD)
#   assets/icones/itens/mochila/<id>.png      (arte da mochila em grade estilo MU, 30 px por célula)
#   assets/icones/itens/mochila_2x/<id>.png   (mesma arte em 60 px por célula)
# Uso: python3 gerar_itens.py   (precisa de pillow+numpy e do Chromium/Playwright do container)
import json, os, subprocess, shutil, sys
import numpy as np
from PIL import Image
import motivos_itens as MI, motivos_extra as MX
from posproc import finalizar_item, volume, sujar, indexar, contorno, _hex
from PIL import ImageFilter
AQUI = os.path.dirname(os.path.abspath(__file__)); PF = os.path.abspath(os.path.join(AQUI, "../.."))
TMP = os.environ.get("TMPDIR_ICONES", "/tmp/icones") + "_itens"
MOT = {**MI.MOTIVOS, **MX.MOTIVOS}
GIRA_GRADE = {"besta": -90, "pistola_raio": 0}      # arte da mochila: besta deitada (3x2), como no mock da UI
DEFS = '<defs><filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
COR_RAR = {"magico":"#6f9fc9","raro":"#c99a3e","excelente":"#9cff3a","lendario":"#c8302a"}
dados = json.load(open(f"{PF}/design/skills-itens/itens.json"))
so = set(sys.argv[1:])
itens = [i for i in dados["itens"] if not so or i["id"] in so]
shutil.rmtree(TMP, ignore_errors=True)
for modo in ("icone", "grade"):
    os.makedirs(f"{TMP}/{modo}/svg")
    MI.ROT = (modo == "icone")
    for it in itens:
        corpo = MOT[it["motivo"]](MI.TINTS[it.get("tint") or "ferro"], it.get("emissivo"))
        if modo == "grade" and GIRA_GRADE.get(it["motivo"]): corpo = f'<g transform="rotate({GIRA_GRADE[it["motivo"]]} 32 32)">{corpo}</g>'
        vb = "0 0 64 64" if modo == "icone" else "-16 -16 96 96"
        tam = 64 if modo == "icone" else 96
        open(f"{TMP}/{modo}/svg/{it['id']}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{tam}" height="{tam}" viewBox="{vb}">{DEFS}{corpo}</svg>')
    subprocess.run(["node", f"{AQUI}/render.js", f"{TMP}/{modo}/svg", f"{TMP}/{modo}/png", "96" if modo == "grade" else "64"], check=True)

def brilho(out, cor, tam):
    a = np.asarray(out)
    m = Image.fromarray(((a[..., 3] > 0) * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(max(1.2, tam / 24)))
    halo = Image.new("RGBA", out.size, _hex(cor) + (0,)); halo.putalpha(m.point(lambda v: int(v * 0.8)))
    return Image.alpha_composite(halo, out)

for d in ("64", "40", "32", "mochila", "mochila_2x"): os.makedirs(f"{PF}/assets/icones/itens/{d}", exist_ok=True)
for it in itens:
    cor = COR_RAR.get(it.get("raridade"))
    im = volume(Image.open(f"{TMP}/icone/png/{it['id']}.png").convert("RGBA"))
    for tam in (64, 40, 32):
        finalizar_item(im, tam, cor).save(f"{PF}/assets/icones/itens/{tam}/{it['id']}.png")
    # arte da mochila: recorta a silhueta e encaixa na grade (w x h células)
    g = volume(Image.open(f"{TMP}/grade/png/{it['id']}.png").convert("RGBA"))
    bb = g.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox(); g = g.crop(bb)
    w, h = it.get("grade", [1, 1])
    for cel, pasta in ((30, "mochila"), (60, "mochila_2x")):
        W, H = w * cel, h * cel; pad = max(2, cel // 10)
        esc = min((W - 2 * pad) / g.width, (H - 2 * pad) / g.height)
        r = sujar(g).resize((max(1, round(g.width * esc)), max(1, round(g.height * esc))), Image.LANCZOS)
        r = Image.fromarray(contorno(indexar(r, 40)))
        tela = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tela.paste(r, ((W - r.width) // 2, (H - r.height) // 2), r)
        if cor: tela = brilho(tela, cor, cel * min(w, h))
        tela.save(f"{PF}/assets/icones/itens/{pasta}/{it['id']}.png")
print("ok", len(itens))

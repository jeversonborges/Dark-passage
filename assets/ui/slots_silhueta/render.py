# Reduz os PNG de 104 px para 52 px (filtro Lanczos) e copia para o jogo: game/assets/ext/ui/1x/silhueta_<slot>.png
import glob, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
dst = os.path.join(here, "..", "..", "..", "game", "assets", "ext", "ui", "1x")
for src in glob.glob(os.path.join(here, "*_104.png")):
    slot = os.path.basename(src).replace("_104.png", "")
    im = Image.open(src).convert("RGBA").resize((52, 52), Image.LANCZOS)
    im.save(os.path.join(here, "silhueta_" + slot + ".png"))
    im.save(os.path.join(dst, "silhueta_" + slot + ".png"))
    os.remove(src)
print("ok")

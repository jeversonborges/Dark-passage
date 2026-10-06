# Monta folha de prévia (ícones 64px ampliados 2x sobre slot de inventário escuro) + atlas.
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
PF = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
def fonte(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()
def folha(ids, pasta, cores_nome, saida, cols=10, titulo=""):
    cw, ch = 150, 178; rows = (len(ids)+cols-1)//cols
    W, H = cols*cw+20, rows*ch+60
    im = Image.new("RGB", (W, H), (14,12,13)); d = ImageDraw.Draw(im); f = fonte(12)
    d.text((14, 16), titulo, fill=(211,202,183), font=fonte(20))
    for i, (iid, nome) in enumerate(ids):
        x, y = 10 + (i%cols)*cw, 50 + (i//cols)*ch
        d.rectangle([x+10, y, x+10+132, y+132], fill=(30,27,28), outline=(70,64,74))
        ic = Image.open(f"{pasta}/{iid}.png").resize((128,128), Image.NEAREST)
        im.paste(ic, (x+12, y+2), ic)
        words, line, lines = nome.split(), "", []
        for w in words:
            if d.textlength(line+" "+w, font=f) > cw-8 and line: lines.append(line); line = w
            else: line = (line+" "+w).strip()
        lines.append(line)
        for j, l in enumerate(lines[:3]): d.text((x+cw//2-d.textlength(l,font=f)//2, y+136+j*13), l, fill=cores_nome.get(iid,(200,192,176)), font=f)
    im.save(saida)
def atlas(ids, pasta, saida, tam, cols=16):
    rows = (len(ids)+cols-1)//cols; a = Image.new("RGBA", (cols*tam, rows*tam), (0,0,0,0)); idx = {}
    for i, iid in enumerate(ids):
        a.paste(Image.open(f"{pasta}/{iid}.png"), ((i%cols)*tam, (i//cols)*tam)); idx[iid] = [(i%cols)*tam, (i//cols)*tam, tam, tam]
    a.save(saida); json.dump(idx, open(saida.replace(".png", ".json"), "w"), indent=0)
if __name__ == "__main__":
    qual = sys.argv[1]
    hexc = lambda c: tuple(int(c.lstrip("#")[i:i+2],16) for i in (0,2,4))
    if qual == "itens":
        dd = json.load(open(f"{PF}/design/skills-itens/itens.json")); rar = {"magico":hexc("#6f9fc9"),"raro":hexc("#c99a3e"),"excelente":hexc("#9cff3a"),"lendario":hexc("#e04a3a")}
        ids = [(i["id"], i["nome"]) for i in dd["itens"]]; cores = {i["id"]: rar.get(i.get("raridade","comum"), (200,192,176)) for i in dd["itens"]}
        folha(ids, f"{PF}/assets/icones/itens/64", cores, f"{PF}/assets/icones/previa_itens.png", 13, "DARK PASSAGE · Itens v0.2 (nome em vermelho = Relíquia, azul = mágico, dourado = raro)")
        for t in (64, 40, 32): atlas([i for i,_ in ids], f"{PF}/assets/icones/itens/{t}", f"{PF}/assets/icones/atlas_itens_{t}.png", t)
    else:
        dd = json.load(open(f"{PF}/design/skills-itens/skills.json")); ids = [(s["id"], s["nome"]) for s in dd["skills"]]
        folha(ids, f"{PF}/assets/icones/skills/64", {}, f"{PF}/assets/icones/previa_skills.png", 6, "DARK PASSAGE · Skills v0.2 (Anjo, Cultista, Mutante, Demônio, Humano, Tecnomancer)")
        for t in (64, 40, 32): atlas([i for i,_ in ids], f"{PF}/assets/icones/skills/{t}", f"{PF}/assets/icones/atlas_skills_{t}.png", t, 6)

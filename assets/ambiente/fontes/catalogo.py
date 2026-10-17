"""Catálogo de todos os objetos de cenário (assets/ambiente/objetos/) por TIPO, para reaproveitar em mapas novos.
Pedido do Jefin (17/10/2026): "guardar uma lista dos props por tipo, se um dia a gente precisar a gente reutiliza".

Gera (rode de novo sempre que publicar objetos novos):
  assets/ambiente/CATALOGO.md          índice por tipo: id, bioma, tamanho em tiles, descrição
  assets/ambiente/catalogo.json        o mesmo em dados {tipo: [{id, bioma, tiles, categoria, descricao}]}
  assets/ambiente/catalogo/<tipo>.png  prancha de miniaturas com o nome de cada peça

Uso: python3 catalogo.py
O tipo sai de regras por palavra (TIPOS abaixo, a primeira que bater vence); o bioma sai do json do objeto ou, se não
tiver, do módulo de fontes/ que define a peça. Peça nova que cair em "Outros" pede uma palavra nova em TIPOS.
"""
import glob, json, os, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
AMB = os.path.dirname(AQUI)
OUT = os.path.join(AMB, "catalogo")

# (slug, título, categorias do kit que caem direto aqui, palavras no id/descrição)
TIPOS = [
    ("coliseu", "Coliseu do Agrak (arquibancadas, plateia, faixas)", set(), ["plateia", "arquibancada", "faixa_campeao", "corda_guarda", "agrak"]),
    ("chefes_efeitos", "Peças de chefe e efeitos de ambiente", {"chefes", "efeitos"}, ["poeira", "vento", "lasca", "astral", "fenda", "nevoa", "arena_"]),
    ("paredes", "Paredes, muros e limites do mapa", {"paredes", "limites"}, ["parede", "muro", "rodape", "pilar_", "canto"]),
    ("predios", "Prédios e estruturas grandes", {"predios"}, ["predio", "igreja", "capela_", "torre_", "templo", "piramide", "casa_", "galpao", "barraco", "ruina", "tenda"]),
    ("arquitetura", "Colunas, arcos, degraus e peças de arquitetura", set(), ["coluna", "degrau", "plataforma", "arco_", "laje", "domo", "eclusa", "viga", "trelica", "palco", "pilastra", "capitel"]),
    ("portas", "Portas, escadas, elevadores e passagens", set(), ["porta", "portao", "escada", "elevador", "alcapao", "portal", "ponte", "passarela", "grade_"]),
    ("decalques", "Decalques de chão (manchas, rastros, símbolos)", {"decalques"}, ["_chao", "mancha", "poca", "rastro", "simbolo", "tapete", "circulo"]),
    ("vegetacao", "Vegetação (árvores, arbustos, raízes, fungos)", {"vegetacao"}, ["arvore", "arbusto", "palmeira", "cacto", "raiz", "fungo", "cogumelo", "junco", "papiro_", "musgo", "tronco_", "galho", "acacia", "flor", "cevada", "videira"]),
    ("rio", "Água, rio e barcos", {"rio"}, ["rio", "agua", "barca", "barco", "cais", "poco", "fonte", "cisterna", "margem", "lotus"]),
    ("rochas", "Rochas, dunas e terreno", set(), ["rocha", "pedra", "duna", "seixo", "penhasco", "rochedo", "monte_", "areia", "entulho", "cascalho", "escombro", "destroco", "pedregulho", "barranco"]),
    ("luz", "Luz e fogo (velas, lampiões, braseiros)", set(), ["vela", "lampi", "lamparina", "braseiro", "tocha", "fogueira", "candelabro", "lanterna", "lustre", "luminaria", "lampada", "incensario", "brasa", "fogo", "farol"]),
    ("religioso", "Religioso e funerário (altares, túmulos, estátuas)", set(), ["altar", "cruz", "tumulo", "sarcofago", "lapide", "estatua", "idolo", "relicario", "sino", "oratorio", "ossuario", "mumia", "ushabti", "caixao", "santo", "anjo", "obelisco", "esfinge", "estela", "votiv", "ex_voto", "genuflexorio", "coroa", "trombeta", "nicho", "cripta", "capela", "jazigo", "farao", "deus", "escaravelho", "oferenda", "cova", "espelho", "globo", "tabua", "diapasao", "tripode", "chifres", "atlante"]),
    ("ossos", "Ossos, corpos e restos", set(), ["osso", "caveira", "cadaver", "carcaca", "cranio", "corpo", "esqueleto", "carne", "pernil", "visceras", "tripa", "gancho", "boi", "morto", "ossada", "emparedado"]),
    ("maquinas", "Máquinas, rádio, sucata e trilhos", set(), ["radio", "valvula", "gerador", "antena", "motor", "engrenagem", "cabo", "transformador", "sucata", "trilho", "bonde", "maquina", "caldeira", "cano", "tubo", "fio", "parabolica", "microfone", "fone", "gravador", "solda", "torre", "moedor", "serra", "balanca", "relogio", "painel", "alto_falante", "bomba", "tanque", "vagao", "roda", "manivela", "fita", "carroca", "guindaste", "quadro_frequencias", "campanula", "estai"]),
    ("moveis", "Móveis (mesas, cadeiras, estantes, camas)", set(), ["mesa", "cadeira", "banco", "cama", "estante", "armario", "atril", "bancada", "prateleira", "trono", "balcao", "cabide", "escrivaninha", "biombo", "harpa", "piano", "orgao", "livro", "papiro", "pergaminho", "cepo", "faqueiro", "varal", "tripe"]),
    ("recipientes", "Recipientes e cargas (caixotes, barris, vasos)", set(), ["caixote", "barril", "balde", "cesto", "vaso", "jarra", "saco", "bau", "anfora", "caixa", "pote", "tonel", "garrafa", "bandeja", "carga", "fardo", "pilha", "urna", "jarro", "tina", "barris", "tambor", "tone", "cocho", "colmeia", "sebo"]),
    ("sinais", "Cercas, estandartes, placas e sinais", set(), ["estaca", "cerca", "espantalho", "estandarte", "placa", "bandeira", "cartaz", "faixa", "letreiro", "marco", "totem", "poste", "mastro"]),
    ("ferramentas", "Ferramentas e armas", set(), ["faca", "cutelo", "ferramenta", "espada", "lanca", "arma", "machado", "pa_", "picareta", "amolar", "bigorna", "forja", "escudo"]),
    ("props", "Outros props", set(), []),
]
BIOMA_MOD = {"amenti": "amenti", "atlantida": "atlantida", "biblioteca": "biblioteca", "eden": "novo_eden", "egito": "egito",
             "matadouro": "matadouro", "torre_radio": "torre", "torre_kit_base": "torre", "torre_kit_alto": "torre",
             "plateia_agrak": "coliseu_agrak", "exilado": "rio_amargo", "assets": "base", "rodape": "cripta", "luzes": "base"}


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def modulo_de(fontes):
    """kind -> módulo de fontes/ onde o nome aparece entre aspas (o primeiro que define a peça)."""
    achou = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "*.py"))):
        mod = os.path.basename(f)[:-3]
        if mod not in BIOMA_MOD: continue
        for k in re.findall(r'["\']([a-z0-9_]+)["\']', open(f, encoding="utf-8").read()):
            achou.setdefault(k, mod)
    return achou


PISTA = [("agrak", "coliseu_agrak"), ("plateia", "coliseu_agrak"), ("arquibancada", "coliseu_agrak"), ("faixa_campeao", "coliseu_agrak"),
         ("torre", "torre"), ("portadora", "torre"), ("hawara", "egito"), ("duat", "egito"), ("egito", "egito"), ("amenti", "amenti"),
         ("atlant", "atlantida"), ("eden", "novo_eden"), ("granizo", "novo_eden"), ("matadouro", "matadouro"), ("carpideira", "cripta"),
         ("trombeta", "cripta"), ("ossario", "cripta"), ("cripta", "cripta"), ("vala", "cripta"), ("biblioteca", "biblioteca"),
         ("capela", "sao_lazaro"), ("lazaro", "sao_lazaro")]


def bioma_por_nome(k, mods):
    for p, b in PISTA:
        if p in k: return b
    base = re.sub(r"(_frente)?(_v\d)?(_[ab]|_canto)$", "", k)
    for cand in (k, base, base + "_a", re.sub(r"_\d+$", "", base)):
        if cand in mods: return BIOMA_MOD[mods[cand]]
    return "base"


def tipo_de(k, j):
    cat = j.get("categoria", "")
    txt = sem_acento(k + " ")
    for slug, _, cats, palavras in TIPOS[:1]:
        if any(p in txt for p in palavras): return slug
    for slug, _, cats, palavras in TIPOS:
        if cat in cats: return slug
    for slug, _, cats, palavras in TIPOS:
        if any(p in txt for p in palavras): return slug
    d = sem_acento(j.get("descricao", "")[:90])   # só o começo da descrição (o que a peça É)
    for slug, _, cats, palavras in TIPOS:
        if any(re.search(r"\b" + re.escape(p.strip("_")), d) for p in palavras if len(p.strip("_")) > 3): return slug
    return "props"


def fonte(t):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, t)
    return ImageFont.load_default()


def prancha(titulo, itens, out, cel=(184, 150), cols=10):
    fn, ft, fb = fonte(12), fonte(26), fonte(11)
    rows = (len(itens) + cols - 1) // cols
    W = cel[0]*cols + 24; H = cel[1]*rows + 70
    S = Image.new("RGB", (W, H), (20, 17, 15)); d = ImageDraw.Draw(S)
    d.text((14, 16), f"{titulo} · {len(itens)} peças", font=ft, fill=(222, 204, 166))
    for i, it in enumerate(itens):
        x0 = 12 + (i % cols)*cel[0]; y0 = 58 + (i // cols)*cel[1]
        d.rectangle([x0 + 2, y0 + 2, x0 + cel[0] - 3, y0 + cel[1] - 3], fill=(30, 26, 23))
        try:
            im = Image.open(os.path.join(AMB, "objetos", it["id"] + ".png")).convert("RGBA")
            bb = im.getbbox() or (0, 0, im.width, im.height); im = im.crop(bb)
            esc = min((cel[0] - 14)/im.width, (cel[1] - 40)/im.height, 1.5)
            im = im.resize((max(1, int(im.width*esc)), max(1, int(im.height*esc))), Image.LANCZOS)
            # clareia um pouco para a prancha (os objetos são escuros de propósito)
            r, g, b, a = im.split(); rgb = Image.merge("RGB", (r, g, b)).point(lambda v: min(255, int(v*1.35 + 6)))
            im = Image.merge("RGBA", (*rgb.split(), a))
            S.paste(im, (x0 + (cel[0] - im.width)//2, y0 + 6 + (cel[1] - 40 - im.height)//2 + 4), im)
        except Exception:
            pass
        nome = it["id"] if len(it["id"]) <= 26 else it["id"][:25] + "…"
        tw = d.textlength(nome, font=fn); d.text((x0 + (cel[0] - tw)/2, y0 + cel[1] - 32), nome, font=fn, fill=(214, 196, 160))
        sub = f'{it["bioma"]} · {it["tiles"]}'
        tw = d.textlength(sub, font=fb); d.text((x0 + (cel[0] - tw)/2, y0 + cel[1] - 17), sub, font=fb, fill=(140, 124, 104))
    S.save(out, optimize=True)


def main():
    man = json.load(open(os.path.join(AMB, "manifest.json")))["objetos"]
    mods = modulo_de(AQUI)
    grupos = {s: [] for s, *_ in TIPOS}
    for k in sorted(man):
        p = os.path.join(AMB, "objetos", k + ".json")
        j = json.load(open(p)) if os.path.exists(p) else {}
        j.setdefault("categoria", man[k].get("categoria", ""))
        bioma = j.get("bioma") or bioma_por_nome(k, mods)
        fp = j.get("footprint_tiles") or man[k].get("footprint_tiles") or [1, 1]
        desc = " ".join(j.get("descricao", "").split())
        grupos[tipo_de(k, j)].append({"id": k, "bioma": bioma, "tiles": f"{fp[0]}x{fp[1]}", "categoria": j["categoria"],
                                      "enfeite": bool(j.get("enfeite")), "descricao": desc})
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*.png")): os.remove(f)
    md = ["# Catálogo de props por tipo", "",
          "Todos os objetos de cenário do jogo (`assets/ambiente/objetos/`), separados por tipo para reaproveitar em mapas novos.",
          "Gerado por `assets/ambiente/fontes/catalogo.py` (rode de novo depois de publicar peças novas). Cada tipo tem uma prancha",
          "com as miniaturas em `assets/ambiente/catalogo/`. Os dados ficam em `assets/ambiente/catalogo.json`.", "",
          "Reaproveitar: o id é o `k` do prop no mapa (`{\"k\": id, \"x\": .., \"y\": ..}`); `tiles` é a pegada no chão. Peças com",
          "`descricao` dizem o que são; as de bioma fechado (egito, amenti, torre...) seguem a paleta daquela área, então numa",
          "área de outro tema prefira as de bioma `base` (kit original: deserto, São Lázaro, cripta, que combina com quase tudo).", "", "## Índice", ""]
    total = 0
    for slug, tit, *_ in TIPOS:
        n = len(grupos[slug]); total += n
        if n: md.append(f"- [{tit}](#{slug}) · {n} peças · prancha `catalogo/{slug}.png`")
    md.insert(4, f"Total: **{total} peças** em {sum(1 for s in grupos if grupos[s])} tipos.")
    for slug, tit, *_ in TIPOS:
        itens = sorted(grupos[slug], key=lambda it: (it["bioma"], it["id"]))
        if not itens: continue
        prancha(tit, itens, os.path.join(OUT, f"{slug}.png"))
        md += ["", f'<a id="{slug}"></a>', f"## {tit}", "", f"![{tit}](catalogo/{slug}.png)", "",
               "| id | bioma | tiles | o que é |", "|---|---|---|---|"]
        for it in itens:
            d = it["descricao"]
            d = (d[:150].rsplit(" ", 1)[0] + "…") if len(d) > 150 else d
            md.append(f'| `{it["id"]}` | {it["bioma"]} | {it["tiles"]} | {d.replace("|", "/")} |')
    open(os.path.join(AMB, "CATALOGO.md"), "w").write("\n".join(md) + "\n")
    json.dump({s: sorted(grupos[s], key=lambda it: (it["bioma"], it["id"])) for s, *_ in TIPOS if grupos[s]},
              open(os.path.join(AMB, "catalogo.json"), "w"), ensure_ascii=False, indent=1)
    for slug, tit, *_ in TIPOS: print(f"{slug:16s} {len(grupos[slug])}")
    print("total", total)


if __name__ == "__main__":
    main()

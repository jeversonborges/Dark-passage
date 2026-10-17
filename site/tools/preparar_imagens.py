#!/usr/bin/env python3
"""Gera as imagens do site a partir das artes do jogo (nada é desenhado à mão aqui).

    python3 site/tools/preparar_imagens.py            # lê de /mnt/project-files, grava em site/publico/img/

- Cenas: recortes das prévias de cada área, sem HUD, em JPG.
- Personagens: a animação "parado" de cada classe na direção SE, numa tira horizontal (um quadro ao lado do outro),
  recortada justa e na mesma escala para todas as classes. O site anima a tira com CSS.
  As medidas de cada tira vão para img/sprites.json.
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(os.environ.get("RAIZ", "/mnt/project-files"))
SAIDA = Path(__file__).resolve().parent.parent / "publico" / "img"

# id: (arquivo, recorte (x0, y0, x1, y1) ou None, largura final)
CENAS = {
    "heroi":       ("assets/ui/carregamento/tela_carregamento_sem_logo_1920x1080.png", None, 1920),
    "sao_lazaro":  ("entregas/cidade_sao_lazaro/imagens/igreja.jpg", (160, 60, 2120, 1314), 1400),
    "jerusalem":   ("entregas/jerusalem_hermon/previa/1_jerusalem.png", (400, 195, 1170, 575), 1280),
    "hermon":      ("entregas/jerusalem_hermon/previa/5_cume_hermon.png", (400, 210, 1170, 575), 1280),
    "novo_eden":   ("design/mapas/mata_do_granizo/previa_eden/portao_do_oriente.png", (400, 200, 1170, 575), 1280),
    "torre":       ("design/mapas/a_torre/previas/torre_radio.png", None, 620),
    "atlantida":   ("entregas/atlantida/print_2_ilha_do_templo.jpg", (60, 60, 1562, 1003), 1300),
    "egito":       ("entregas/egito/previa/cenario_1.png", (300, 60, 2200, 1180), 1500),
    "agrak":       ("design/mapas/agrak/previa_agrak.png", (40, 40, 1240, 700), 1200),
}

BASES = "assets/personagens"
EVOS = "entregas/evolucoes/sprites"
# id no site: pasta com idle.png + sprites.json
PERSONAGENS = {
    "anjo": f"{BASES}/anjo", "demonio": f"{BASES}/demonio", "cultista": f"{BASES}/cultista",
    "humano": f"{EVOS}/humano_sem_espada", "mutante": f"{BASES}/mutante", "tecnomancer": f"{BASES}/tecnomancer",
    "warlord": f"{BASES}/warlord",
    **{e: f"{EVOS}/{e}" for e in (
        "arcanjo", "serafim", "lorde_das_trevas", "ceifador", "arquimago", "profeta_do_amargo",
        "pistoleiro", "cacador_de_anjos", "gladiador", "abominacao", "mechanicus", "engenheiro_herege")},
}
ESCALA = 1.5   # mesma escala para todos: o tamanho relativo é o do jogo


def cena(nome, arq, recorte, largura):
    im = Image.open(RAIZ / arq).convert("RGB")
    if recorte:
        im = im.crop(recorte)
    if im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im.save(SAIDA / f"{nome}.jpg", quality=84, optimize=True, progressive=True)


def tira(nome, pasta):
    meta = json.loads((RAIZ / pasta / "sprites.json").read_text(encoding="utf-8"))
    fw, fh = meta["frame_size"]
    anim = meta["anims"]["idle"]
    folha = Image.open(RAIZ / pasta / anim["file"]).convert("RGBA")
    linha = meta["rows_dirs"].index("SE")
    quadros = [folha.crop((i * fw, linha * fh, (i + 1) * fw, (linha + 1) * fh)) for i in range(anim["frames"])]

    caixa = None
    for q in quadros:
        b = q.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if b:
            caixa = b if caixa is None else (min(caixa[0], b[0]), min(caixa[1], b[1]), max(caixa[2], b[2]), max(caixa[3], b[3]))
    x0, y0, x1, y1 = caixa
    x0, y0, x1, y1 = max(0, x0 - 2), max(0, y0 - 2), min(fw, x1 + 2), min(fh, y1 + 2)
    w, h = x1 - x0, y1 - y0
    W, H = round(w * ESCALA), round(h * ESCALA)

    saida = Image.new("RGBA", (W * len(quadros), H), (0, 0, 0, 0))
    for i, q in enumerate(quadros):
        q = q.crop((x0, y0, x1, y1))
        q = q.resize((W, H), Image.LANCZOS)
        saida.paste(q, (i * W, 0))
    # 255 cores com transparência: o jogo usa 64 por personagem, então quase nada se perde e o arquivo cai pela metade
    saida.quantize(colors=255, method=Image.FASTOCTREE, dither=Image.NONE).save(SAIDA / f"p_{nome}.png", optimize=True)
    return {"w": W, "h": H, "n": len(quadros), "fps": anim["fps"]}


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, (arq, rec, larg) in CENAS.items():
        cena(nome, arq, rec, larg)
    logo = Image.open(RAIZ / "assets/ui/carregamento/logo_dark_passage.png").convert("RGBA")
    logo.thumbnail((960, 960), Image.LANCZOS)
    logo.save(SAIDA / "logo.png", optimize=True)

    medidas = {nome: tira(nome, pasta) for nome, pasta in PERSONAGENS.items()}
    (SAIDA / "sprites.json").write_text(json.dumps(medidas, indent=1), encoding="utf-8")
    for nome, m in medidas.items():
        print(f"{nome:20s} {m['w']}x{m['h']} x{m['n']} @{m['fps']}")


if __name__ == "__main__":
    sys.exit(main())

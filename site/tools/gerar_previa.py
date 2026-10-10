#!/usr/bin/env python3
"""Gera a versão do site para publicar como Artifact (prévia que o Jefin abre no navegador).

O Artifact já embrulha o arquivo em <!doctype html><head>...<body>, então aqui só tiramos
essa casca do index.html e ligamos o modo prévia (nenhuma conta é gravada de verdade).

    python3 tools/gerar_previa.py <pasta_de_saida>
"""
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "publico" / "index.html"


def gerar(saida: Path) -> Path:
    html = FONTE.read_text(encoding="utf-8")

    cabeca = html.split("<head>", 1)[1].split("</head>", 1)[0]
    corpo = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]

    guardar = []
    for tag in re.findall(r'<link rel="stylesheet"[^>]*>|<title>.*?</title>|<style>.*?</style>',
                          cabeca, re.S):
        guardar.append(tag)

    saida.mkdir(parents=True, exist_ok=True)
    arquivo = saida / "previa.html"
    arquivo.write_text(
        "\n".join(guardar) + "\n<script>window.__PREVIA = true;</script>\n" + corpo,
        encoding="utf-8",
    )

    destino_img = saida / "img"
    if destino_img.exists():
        shutil.rmtree(destino_img)
    shutil.copytree(RAIZ / "publico" / "img", destino_img)
    return arquivo


if __name__ == "__main__":
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "previa")
    print(gerar(destino))

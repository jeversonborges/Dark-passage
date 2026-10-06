# Gera os ícones de skills a partir de design/skills-itens/skills.json. Uso: python3 gerar_skills.py
import json, os, subprocess, shutil
from PIL import Image
import motivos_skills as M
from posproc import finalizar_skill
AQUI = os.path.dirname(os.path.abspath(__file__)); PF = os.path.abspath(os.path.join(AQUI, "../.."))
TMP = os.environ.get("TMPDIR_ICONES", "/tmp/icones") + "_skills"
dados = json.load(open(f"{PF}/design/skills-itens/skills.json"))
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(f"{TMP}/svg")
for s in dados["skills"]:
    E, Ed = M.ELEM[s["elemento"]]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">{M.defs(E, Ed)}{M.moldura(s["classe"], getattr(M, s["id"])(E), E, Ed)}</svg>'
    open(f"{TMP}/svg/{s['id']}.svg", "w").write(svg)
subprocess.run(["node", f"{AQUI}/render.js", f"{TMP}/svg", f"{TMP}/png"], check=True)
for tam in (64, 40, 32):
    os.makedirs(f"{PF}/assets/icones/skills/{tam}", exist_ok=True)
    for s in dados["skills"]:
        finalizar_skill(Image.open(f"{TMP}/png/{s['id']}.png").convert("RGBA"), tam).save(f"{PF}/assets/icones/skills/{tam}/{s['id']}.png")
print("ok", len(dados["skills"]))

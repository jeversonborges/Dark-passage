# Empacota o build Web do Godot como página única (Artifact do claude.ai):
# index.js vai inline, o .wasm é dividido em partes < 15 MB e remontado por um fetch interceptado.
# Uso: python3 tools/make_artifact.py build/web dist/artifact
import sys, os, json, re
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
wasm = open(f"{src}/index.wasm", "rb").read()
PART = 14 * 1024 * 1024
parts = []
for i in range(0, len(wasm), PART):
    name = f"engine.part{len(parts)}.wasm"; open(f"{out}/{name}", "wb").write(wasm[i:i+PART]); parts.append(name)
pck = open(f"{src}/index.pck", "rb").read()
pck_parts = []
for i in range(0, len(pck), PART):
    name = f"dados.part{len(pck_parts)}.wasm"; open(f"{out}/{name}", "wb").write(pck[i:i+PART]); pck_parts.append(name)
import shutil
for w in ["index.audio.worklet.js", "index.audio.position.worklet.js"]: shutil.copy(f"{src}/{w}", f"{out}/{w}")
js = open(f"{src}/index.js").read().replace("</script", "<\\/script")
html = open(os.path.join(os.path.dirname(__file__), "artifact_shell.html")).read()
html = html.replace("/*PCK_PARTS*/", json.dumps(pck_parts)).replace("/*PARTS*/", json.dumps(parts)).replace("/*WASM_SIZE*/", str(len(wasm))).replace("/*PCK_SIZE*/", str(len(pck)))
html = html.replace("/*GODOT_JS*/", js)
open(f"{out}/dark-passage.html", "w").write(html)
print("ok", parts, pck_parts, len(html)//1024, "KB")

# Publica os renders em assets/ambiente/objetos/<kind>.png + <kind>.json e atualiza o manifesto.
# Uso: python3 publicar.py <raw_dir>
import sys, os, json, subprocess
raw = sys.argv[1]
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dst = os.path.join(base, "objetos"); os.makedirs(dst, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(os.listdir(raw)):
    if not f.endswith(".json"): continue
    kind = f[:-5]; png = f"{raw}/{kind}_raw.png"
    if not os.path.exists(png): continue
    out_png = f"{dst}/{kind}.png"
    if not os.path.exists(out_png) or os.path.getmtime(out_png) < os.path.getmtime(png):
        subprocess.run(["python3", f"{here}/post.py", "asset", png, out_png], check=True)
        meta = json.load(open(f"{raw}/{f}")); meta["kind"] = kind
        json.dump(meta, open(f"{dst}/{kind}.json", "w"), ensure_ascii=False, indent=1)
man_p = os.path.join(base, "manifest.json"); man = json.load(open(man_p))
man["pisos"] = {k[:-4]: {"atlas": f"tiles/{k}", "grade": [4, 4], "celula_px": [64, 32],
    "uso": "bloco periodico 4x4 sem emenda: tile (x,y) usa a celula (x mod 4, y mod 4)"} for k in sorted(os.listdir(os.path.join(base, "tiles"))) if k.endswith(".png")}
man["objetos"] = {}
for f in sorted(os.listdir(dst)):
    if f.endswith(".json"):
        m = json.load(open(f"{dst}/{f}"))
        man["objetos"][f[:-5]] = {"png": f"objetos/{f[:-5]}.png", **{k: m[k] for k in ("w", "h", "anchor", "footprint_tiles", "categoria") if k in m}}
json.dump(man, open(man_p, "w"), ensure_ascii=False, indent=1)
print(len(man["objetos"]), "objetos,", len(man["pisos"]), "pisos")

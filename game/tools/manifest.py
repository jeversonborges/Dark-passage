"""Gera data/ext/*.json a partir do que existe em assets/ext (sprites, efeitos, áudio, ícones).
Roda no fim do tools/sync.sh. O jogo nunca lista pastas: só lê estes manifestos."""
import json, os, glob
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = f"{G}/assets/ext"; OUT = f"{G}/data/ext"; os.makedirs(OUT, exist_ok=True)
spr = {}
for d in sorted(glob.glob(f"{E}/personagens/*/sprites.json")):
    m = json.load(open(d)); k = os.path.basename(os.path.dirname(d)); base = f"res://assets/ext/personagens/{k}/"
    spr[k] = {"frame": m["frame_size"], "anchor": m["anchor_feet"], "dirs": m["rows_dirs"],
              "anims": {a: {"file": base + v["file"], "frames": v["frames"], "fps": v["fps"], "loop": v["loop"]} for a, v in m["anims"].items()}}
for d in sorted(glob.glob(f"{E}/monstros/*/meta.json")):
    m = json.load(open(d)); k = os.path.basename(os.path.dirname(d)); base = f"res://assets/ext/monstros/{k}/"
    anims = {}
    for a, v in m["anims"].items():
        f = m.get("sheets", {}).get(a, {}).get("file", f"{k}_{a}.png")
        if os.path.exists(f"{E}/monstros/{k}/{f}"):
            anims[a] = {"file": base + f, "frames": v["frames"], "fps": v["fps"], "loop": v["loop"]}
    spr[k] = {"frame": m["frame_size"], "anchor": m.get("anchor", m.get("anchor_feet")), "dirs": m.get("dirs", m.get("rows_dirs")), "anims": anims,
              "escala": m.get("escala", 1.0)}
json.dump(spr, open(f"{OUT}/sprites.json", "w"), ensure_ascii=False, indent=1)
vfx = json.load(open(f"{E}/efeitos/efeitos.json"))
for v in vfx: v["sheet"] = "res://assets/ext/efeitos/" + v["sheet"]
json.dump({v["name"]: v for v in vfx}, open(f"{OUT}/efeitos.json", "w"), ensure_ascii=False)
au = json.load(open(f"{E}/audio/audio.json"))
for k, v in au["sons"].items():
    v["arquivos"] = ["res://assets/ext/audio/" + a for a in v["arquivos"] if os.path.exists(f"{E}/audio/{a}")]
json.dump(au, open(f"{OUT}/audio.json", "w"), ensure_ascii=False)
ic = {}
for n in ("itens", "skills"):
    for s in ("40", "64"):
        ic[f"{n}_{s}"] = json.load(open(f"{E}/icones/atlas_{n}_{s}.json"))
ic["mochila"] = sorted(os.path.basename(p)[:-4] for p in glob.glob(f"{E}/icones/mochila/*.png"))
json.dump(ic, open(f"{OUT}/icones.json", "w"))
amb = {"objetos": {}, "pisos": sorted(os.path.basename(p)[:-4] for p in glob.glob(f"{E}/ambiente/tiles/*.png")),
       "luzes": sorted(os.path.basename(p)[:-4] for p in glob.glob(f"{E}/ambiente/luzes/*.png"))}
for p in glob.glob(f"{E}/ambiente/objetos/*.json"):
    if os.path.exists(p[:-5] + ".png"): amb["objetos"][os.path.basename(p)[:-5]] = json.load(open(p))
json.dump(amb, open(f"{OUT}/ambiente.json", "w"), ensure_ascii=False)
print("manifesto:", len(spr), "sprites,", len(vfx), "efeitos,", len(au["sons"]), "sons,", len(amb["objetos"]), "objetos de cenário,", len(amb["pisos"]), "pisos")

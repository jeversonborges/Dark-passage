# Folhas finais de um NPC no formato dos personagens (assets/personagens/<id>/: idle.png, walk.png, sprites.json,
# idle_SE.gif, walk_SE.gif). Usa o pós-processo dos monstros (process.py: redução do 2x, paleta indexada sem
# dither com reserva para brilhos, contorno escuro de 1 px, sombra "blob").
# Uso: python3 folha.py <dir_brutos> <dir_saida> [cores] [largura_sombra_m]
#      CORES_EXTRA="40f0d8" python3 folha.py ...   (emissivo pequeno que a paleta perderia)
import sys, os, json, shutil, subprocess, tempfile
H = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
cores = sys.argv[3] if len(sys.argv) > 3 else "64"; sombra = sys.argv[4] if len(sys.argv) > 4 else ".62"
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(H, "..", "monstros", "process.py"), src, tmp, cores, sombra], check=True)
m = json.load(open(f"{tmp}/meta.json")); os.makedirs(dst, exist_ok=True)
nome = os.path.basename(os.path.normpath(dst))
out = {"classe": f"npc_{nome}", "frame_size": m["frame_size"], "anchor_feet": m["anchor"], "rows_dirs": m["dirs"],
       "dirs_note": "direção para onde o personagem olha na tela (S = para baixo)", "pixels_per_meter": m["pixels_per_meter"],
       "camera": m["camera"], "palette_colors": int(cores), "anims": {}}
for a, sh in m["sheets"].items():
    shutil.copy(f"{tmp}/{sh['file']}", f"{dst}/{a}.png")
    shutil.copy(f"{tmp}/previa/{a}_SE.gif", f"{dst}/{a}_SE.gif")
    ma = m["anims"][a]; out["anims"][a] = {"file": f"{a}.png", "frames": ma["frames"], "fps": ma["fps"], "loop": ma["loop"]}
json.dump(out, open(f"{dst}/sprites.json", "w"), indent=1, ensure_ascii=False)
shutil.rmtree(tmp); print("ok", dst)

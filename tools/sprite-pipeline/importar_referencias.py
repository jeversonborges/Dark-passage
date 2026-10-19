# Organiza o que está em referencias/inbox/ dentro da pasta do tema e atualiza o index.json do tema.
# Nome do arquivo no inbox: tema__nome.ext (ex.: armaduras__barda_cavalo.png). Sem o prefixo, vai para
# inbox/sem_tema/ e o script avisa, para ninguém esquecer de rotular.
# Uso: python3 tools/sprite-pipeline/importar_referencias.py [--fonte "texto da fonte"]
import argparse, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skills_lib import REF, TEMAS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", default="upload do Jefin", help="de onde vieram os arquivos (repo, site, upload)")
    args = ap.parse_args()
    inbox = os.path.join(REF, "inbox")
    movidos, semtema = [], []
    for nome in sorted(os.listdir(inbox)):
        src = os.path.join(inbox, nome)
        if nome.startswith("README") or not os.path.isfile(src):
            continue
        tema, sep, resto = nome.partition("__")
        if not sep or tema not in TEMAS:
            semtema.append(nome)
            continue
        dst_dir = os.path.join(REF, tema)
        shutil.move(src, os.path.join(dst_dir, resto))
        idx_path = os.path.join(dst_dir, "index.json")
        idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else []
        idx = [i for i in idx if i.get("arquivo") != resto]
        idx.append({"arquivo": resto, "repo": args.fonte, "commit": ""})
        json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        movidos.append(f"{tema}/{resto}")
    print("organizados:", movidos or "nenhum")
    if semtema:
        print("sem tema (renomeie com tema__nome.ext):", semtema)

if __name__ == "__main__":
    main()

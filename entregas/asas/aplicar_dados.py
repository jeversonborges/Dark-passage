# Junta os dados das asas (entregas/asas/dados/) nos arquivos de design. Pode rodar mais de uma vez (não duplica).
# Uso:
#   python3 entregas/asas/aplicar_dados.py                      # fontes em design/ (depois: validar.py e tools/sync.sh)
#   python3 entregas/asas/aplicar_dados.py --jogo <game/data/design>   # direto na cópia do jogo (teste)
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "dados")
R = os.path.dirname(os.path.dirname(AQUI))
if "--jogo" in sys.argv:
    base = sys.argv[sys.argv.index("--jogo") + 1]
    P = {"itens": f"{base}/missoes/itens.json", "missoes": f"{base}/missoes/missoes.json",
         "dialogos": f"{base}/missoes/dialogos.json", "drops": f"{base}/combate/drops.json"}
else:
    P = {"itens": f"{R}/design/missoes/dados/itens.json", "missoes": f"{R}/design/missoes/dados/missoes.json",
         "dialogos": f"{R}/design/missoes/dados/dialogos.json", "drops": f"{R}/design/combate/drops.json"}
def ler(p): return json.load(open(p, encoding="utf-8"))
def gravar(p, d, ind=None): open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=ind))

def juntar_lista(arq, chave, novos):
    d = ler(arq); lst = d[chave]; ids = {x["id"]: i for i, x in enumerate(lst)}
    for n in novos:
        if n["id"] in ids: lst[ids[n["id"]]] = n
        else: lst.append(n)
    gravar(arq, d); return len(novos)

print("itens", juntar_lista(P["itens"], "itens", ler(f"{D}/asas_itens.json")["itens"]))
print("missões", juntar_lista(P["missoes"], "missoes", ler(f"{D}/asas_missoes.json")["missoes"]))

# diálogo do Pedro: nós novos + uma opção na raiz, antes de "Quem é você?"
dd = ler(P["dialogos"]); A = ler(f"{D}/asas_dialogo.json")
lista = dd["dialogos"] if isinstance(dd, dict) and "dialogos" in dd else dd
dlg = lista[A["dialogo"]] if isinstance(lista, dict) else next(x for x in lista if x.get("id") == A["dialogo"])
dlg["nos"].update(A["nos"])
raiz = dlg["nos"]["raiz"]["opcoes"]; op = {k: v for k, v in A["opcao_na_raiz"].items() if not k.startswith("_")}
if not any(o.get("ir") == "asas" for o in raiz):
    i = next((k for k, o in enumerate(raiz) if o.get("ir") == "quem"), len(raiz) - 1)
    raiz.insert(i, op)
gravar(P["dialogos"], dd); print("diálogo", A["dialogo"], len(A["nos"]), "nós")

dr = ler(P["drops"]); X = ler(f"{D}/asas_drops.json")
for k in ("materiais_asa", "asas_de_chefe"): dr[k] = X[k]
gravar(P["drops"], dr, 2); print("drops ok")

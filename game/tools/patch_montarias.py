# Patch 0.9.8: vendedores de montarias (um por cidade inicial, mesmo modelo, nomes diferentes) e as 6 montarias à venda.
# Aplica em design/missoes/dados (fonte) e game/data/design/missoes (cópia do jogo). Idempotente: pula o que já existe.
# Os nomes e pontos são provisórios: Missões aprova os nomes; Mapas cria os pontos (estabulo_vela, pulpito_montarias, curral_jerusalem).
import json, os, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ALVOS = ["design/missoes/dados", "game/data/design/missoes"]
MONTARIAS = ["montaria_cavalo_esqueleto", "montaria_corcel_cavaleiro_negro", "montaria_leao_branco_thoth",
             "montaria_lobo_guerra", "montaria_touro_guerra", "montaria_javali_blindado"]
CIDADES = [
    {"sufixo": "vela", "nome": "Caetano Ninho", "faccao": "vigilia", "subzona": "acampamento_vela", "ponto": "estabulo_vela",
     "loja": "Estábulo da Vela", "aparencia": "Homem baixo de botas de couro molhadas, sempre com um cabresto no ombro.",
     "fala": "Bicho bom não se compra com pressa. Escolhe o seu."},
    {"sufixo": "capela", "nome": "Joel Arreio", "faccao": "arautos", "subzona": "capela_sao_lazaro", "ponto": "pulpito_montarias",
     "loja": "Cavalariça da Capela", "aparencia": "Homem magro de batina cortada na altura do joelho, com arreio pendurado no ombro.",
     "fala": "Os cavalos da Capela foram benzidos. Os seus, não sei. Ninguém sabe."},
    {"sufixo": "jerusalem", "nome": "Samuel Cabresto", "faccao": "neutro", "subzona": "jerusalem", "ponto": "curral_jerusalem",
     "loja": "Curral de Jerusalém", "aparencia": "Velho de chapéu de feltro e mãos calejadas de rédea.",
     "fala": "Monta quem aguenta. Eu só vendo o lombo."},
]

def npc(c):
    return {"id": f"vendedor_montarias_{c['sufixo']}", "nome": c["nome"], "titulo": "Tratador de Montarias",
            "faccao": c["faccao"], "classe_visual": "humano", "local": {"subzona": c["subzona"], "ponto": c["ponto"]},
            "servicos": [], "dialogo": f"dlg_montarias_{c['sufixo']}", "aparencia": c["aparencia"],
            "personalidade": "Direto, de poucas palavras, e sempre com um cavalo para olhar.",
            "historia": "Cuida dos bichos de quem chega à cidade. Não pergunta de onde veio o cavalo."}

def loja(c):
    return {"id": f"loja_montarias_{c['sufixo']}", "npc": f"vendedor_montarias_{c['sufixo']}", "nome": c["loja"],
            "itens": MONTARIAS, "fala_ao_abrir": c["fala"]}

def dialogo(c):
    return {"id": f"dlg_montarias_{c['sufixo']}", "npc": f"vendedor_montarias_{c['sufixo']}", "inicio": "raiz",
            "nos": {
                "raiz": {"fala": "Bicho para andar mais rápido. Escolhe o que aguenta o seu peso.",
                         "opcoes": [{"texto": "Quero ver o estoque.", "acoes": [{"abrir_loja": f"loja_montarias_{c['sufixo']}"}]},
                                    {"texto": "Como eu monto?", "ir": "como"},
                                    {"texto": "Até mais."}]},
                "como": {"fala": "Clique duas vezes na montaria da mochila para montar. Atacar ou apanhar derruba você. Para desmontar, tire a montaria do slot dela.",
                         "opcoes": [{"texto": "Voltar.", "ir": "raiz"}]}}}

def aplicar(caminho, chave, novos, lista_chave_dict=None):
    p = os.path.join(RAIZ, caminho)
    if not os.path.exists(p): print("pulado (não existe):", caminho); return
    d = json.load(open(p, encoding="utf-8"))
    alvo = d[chave]
    ids = {x["id"] for x in alvo}
    n = 0
    for x in novos:
        if x["id"] not in ids: alvo.append(x); n += 1
    original = open(p, encoding="utf-8").read()
    # mesma formatação do arquivo: indentado (npcs) ou uma linha só (lojas e diálogos)
    indent = 2 if "\n  \"" in original[:200] else None
    fim = "\n" if original.endswith("\n") else ""
    open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=indent) + fim)
    print(caminho, chave, "+", n)

for alvo in ALVOS:
    aplicar(f"{alvo}/npcs.json", "npcs", [npc(c) for c in CIDADES])
    aplicar(f"{alvo}/lojas.json", "lojas", [loja(c) for c in CIDADES])
    aplicar(f"{alvo}/dialogos.json", "dialogos", [dialogo(c) for c in CIDADES])

# Biblioteca de apoio das threads de Blender: referências por tema, orçamento low-poly e utilitários
# extraídos dos repositórios em vendor/ (ver vendor/SOURCES.md). Só stdlib, para rodar fora do Blender.
# Uso: from skills_lib import referencias, orcamento, citar
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "referencias")
TEMAS = ("anatomia_quadrupede", "locomocao", "materiais_foscos", "rigging", "lowpoly", "armaduras", "armas")

# Orçamento de triângulos por tipo de asset (padrão, em triângulos). Montarias e chefes no topo.
ORCAMENTO = {
    "montaria": (6000, 8000),
    "chefe": (7000, 8000),
    "monstro": (3000, 5000),
    "npc": (4000, 6000),
    "arma": (1200, 2000),
    "escudo": (1500, 2000),
    "prop": (800, 2000),
}

def referencias(tema=None):
    """Lista as referências indexadas (index.json de cada tema). Sem tema, devolve todas."""
    temas = [tema] if tema else TEMAS
    out = []
    for t in temas:
        idx = os.path.join(REF, t, "index.json")
        if os.path.exists(idx):
            for item in json.load(open(idx, encoding="utf-8")):
                out.append({"tema": t, **item})
    return out

def citar(item):
    """Linha de citação para commit ou comentário: 'tema: arquivo (repo@commit)'."""
    fonte = item.get("repo", "próprio")
    commit = item.get("commit", "")
    return f"{item['tema']}: {item['arquivo']} ({fonte}{'@' + commit if commit else ''})"

def orcamento(tipo):
    """(mínimo, máximo) de triângulos para o tipo. Erro se o tipo não existe, para não passar batido."""
    if tipo not in ORCAMENTO:
        raise KeyError(f"tipo de asset desconhecido: {tipo} (use um de {sorted(ORCAMENTO)})")
    return ORCAMENTO[tipo]

# Regras de método tiradas dos repositórios (texto, não código):
REGRAS_SKINNING = [
    # EL4CTEO, blender-character-rigging: props rígidos pesam 100% em um único osso (barda, placas, capacete)
    "Peças de armadura (placas, gualdrapa rígida) pesam 100% em um osso, para não esticar.",
    # EL4CTEO: transição suave nas juntas, 1 a 2 anéis de vértices
    "Transição de peso nas juntas com 1 a 2 anéis, nunca corte seco 1/0.",
    # EL4CTEO: no máximo 4 influências por vértice, normalizado, pesos abaixo de 0.01 removidos
    "Máximo de 4 influências por vértice; normalizar; remover pesos abaixo de 0.01.",
]
REGRAS_ANATOMIA = [
    # Majid, blender-image-to-3d/references/categories.md: régua de cavalo e articulações
    "Cavalo: cernelha ~1,5 m; articulações do membro posterior são garupa, fêmur, jarrete (hock) e boleto.",
    "O jarrete do cavalo é a articulação que parece joelho traseiro; o joelho real fica mais acima.",
]
REGRAS_MATERIAL = [
    # Estilo do projeto (CLAUDE.md e design/estilo-visual.md): fosco, sujo, sem brilho de vitrine
    "Rugosidade alta (0,6 a 0,9) para couro e pelo; metal enferrujado 0,5 a 0,7; sem clearcoat.",
    "Brilho de vitrine (clearcoat, vidro, transmissão) não entra; é o contrário do estilo Ferrugem Sagrada.",
]

if __name__ == "__main__":
    print(json.dumps({"temas": TEMAS, "orcamento": ORCAMENTO, "referencias": len(referencias())}, ensure_ascii=False, indent=2))

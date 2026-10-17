"""Atlântida (nv 30-45) e Salões de Amenti no jogo (0.9.4). Roda no fim do tools/sync.sh e pode rodar sozinho.

- data/mapas/atlantida.json e saloes_de_amenti.json: vêm de design/mapas/{atlantida,amenti}/ (gerados lá, nunca à mão);
  os NPCs desses geradores trazem x/y e o WorldSim lê "pos".
- A Fenda no Novo Éden (FENDA_ATLANTIDA em eden_mapa.py) e a entrada de Amenti no Egito (a Esfinge entre as patas e a laje
  que desce, combinado com a thread do Egito) entram aqui também, para o sync não apagar quando copiar os mapas das outras threads.
- Monstros, chefe (Gadiro), drops e nomes do HUD em data/v06_extra.json; sprites tingidos e dos NPCs em sprites_substitutos.json.
Tudo idempotente: só acrescenta o que falta."""
import json, os
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.environ.get("PROJETO", "/mnt/project-files")
MAPAS = f"{G}/data/mapas"

FENDA = [83.5, 34.5]            # Novo Éden, Coração do Éden (eden_mapa.py: FENDA_ATLANTIDA)
CHEGADA_ATLANTIDA = [128.0, 122.5]
ESFINGE = [78.5, 126.5]         # mapa egito: corredor entre as patas (combinado com a thread do Egito)
LAJE = [79.5, 132.5]
CHEGADA_AMENTI = [60.0, 8.5]


def ler(p): return json.load(open(p, encoding="utf-8"))
def gravar(p, d, compacto=True):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, **({"separators": (",", ":")} if compacto else {"indent": 1}))


def copiar_mapa(origem, destino):
    if not os.path.exists(origem): return
    m = ler(origem)
    for n in m.get("npcs", []):
        if "pos" not in n: n["pos"] = [n["x"], n["y"]]
    for k in ("pendencias_jogo",): m.pop(k, None)
    gravar(f"{MAPAS}/{destino}.json", m)


def portal_em(m, para):
    return any(o.get("kind") == "portal" and o.get("para") == para for o in m["objetos"])


def fenda_no_eden():
    p = f"{MAPAS}/mata_do_granizo.json"
    m = ler(p)
    if portal_em(m, "atlantida"): return
    m["props"].append({"k": "fenda", "x": FENDA[0], "y": round(FENDA[1] - .4, 2)})
    m["luzes"].append([FENDA[0], round(FENDA[1] - .4, 2), .55, .9, 1.0, 7])
    m["objetos"].append({"kind": "portal", "pos": FENDA, "para": "atlantida", "chegada": CHEGADA_ATLANTIDA,
                         "nome": "A Fenda · Atlântida (nv 30)", "visual": "fenda", "nivel_minimo": 30,
                         "texto_trancado": "A Fenda canta numa nota que ainda te derruba. Volte no nível 30."})
    gravar(p, m)


def esfinge_no_egito():
    p = f"{MAPAS}/egito.json"
    if not os.path.exists(p): return
    m = ler(p)
    if portal_em(m, "saloes_de_amenti"): return
    m["npcs"].append({"id": "esfinge_amenti", "pos": ESFINGE, "dir": [1, 1]})
    m["objetos"].append({"kind": "portal", "pos": LAJE, "para": "saloes_de_amenti", "chegada": CHEGADA_AMENTI,
                         "nome": "A laje sob a pata", "visual": "escada_descida", "requer_flag": "amenti_aberto",
                         "texto_trancado": "A pedra tem a forma de uma porta e nenhuma fechadura. Alguém precisa perguntar primeiro."})
    gravar(p, m)


AMENTI_MOBS = {
    "guardiao_da_aurora": {"nome": "O Guardião da Aurora", "base": "anubis_guardiao", "niveis": [150, 150], "arquetipo": "elite",
        "tags": ["guardiao", "sagrado", "astral"], "res": {"sagrado": 0.6, "fisico": 0.3}, "renascimento_s": 3600, "grupo": [1, 1],
        "ia": {"padrao": "guarda", "raio_aggro": 3.0, "raio_coleira": 8},
        "motivo": "guarda o Portão do lado da luz; não se mexe para quem não o toca"},
    "guardiao_do_crepusculo": {"nome": "O Guardião do Crepúsculo", "base": "anubis_guardiao", "niveis": [150, 150], "arquetipo": "elite",
        "tags": ["guardiao", "chacal", "sombra"], "res": {"sombra": 0.6, "fisico": 0.3}, "renascimento_s": 3600, "grupo": [1, 1],
        "ia": {"padrao": "guarda", "raio_aggro": 3.0, "raio_coleira": 8},
        "motivo": "pesa o coração de quem chega ao Portão; não se mexe para quem não o toca"},
    "arconte_de_luz": {"nome": "Arconte de Luz", "base": "anubis_sentinela", "niveis": [150, 150], "arquetipo": "elite",
        "tags": ["astral"], "res": {"sagrado": 0.8, "fisico": 0.5}, "renascimento_s": 3600, "grupo": [1, 1],
        "ia": {"padrao": "guarda", "raio_aggro": 2.0, "raio_coleira": 10},
        "motivo": "passa pelo Salão do Universo como passa pelo céu, sem ver ninguém"},
    "o_que_nao_tem_rosto": {"nome": "O Que Não Tem Rosto", "base": "anubis_sentinela", "niveis": [150, 150], "arquetipo": "elite",
        "tags": ["astral", "sombra"], "res": {"sombra": 0.8, "fisico": 0.5}, "renascimento_s": 3600, "grupo": [1, 1], "velocidade_mov": 0.01,
        "ia": {"padrao": "guarda", "raio_aggro": 1.5, "raio_coleira": 1},
        "motivo": "está no meio do Vazio desde antes do Vazio"},
    "cao_da_barreira": {"nome": "Cão da Barreira", "base": "anubis_sentinela", "niveis": [145, 145], "arquetipo": "normal",
        "tags": ["chacal", "sombra"], "res": {"sombra": 0.4}, "renascimento_s": 1800, "grupo": [2, 3],
        "ia": {"padrao": "matilha", "raio_aggro": 5.0},
        "motivo": "guardam a Barreira; só andam em ângulos"},
}
NPC_SPR = {"iolanda_prumo": "iolanda_prumo", "cabo_nestor": "nestor_calco", "evemon_parado": "evemon_parado", "thotme": "thotme",
           "irma_sinesia": "irma_sinesia", "belzarim": "belzarim", "lider_dos_anjos": "lider_dos_anjos", "lider_dos_demonios": "lider_dos_demonios"}


def dados():
    ex_p = f"{G}/data/v06_extra.json"; ex = ler(ex_p)
    sp_p = f"{G}/data/sprites_substitutos.json"; sp = ler(sp_p)
    d = ler(f"{P}/design/mapas/atlantida/dados.json") if os.path.exists(f"{P}/design/mapas/atlantida/dados.json") else {}
    for k, v in {**d.get("mobs", {}), **AMENTI_MOBS}.items(): ex["mobs"].setdefault(k, v)
    for k, v in d.get("chefes", {}).items(): ex["chefes"].setdefault(k, v)
    for k, v in d.get("drops", {}).items(): ex["drops"].setdefault(k, v)
    ex["nomes_mapa_hud"].setdefault("atlantida", "Atlântida (nv 30-45)")
    ex["nomes_mapa_hud"].setdefault("saloes_de_amenti", "Os Salões de Amenti")
    for k, v in d.get("sprites", {}).items():
        if "tint" in v or v.get("usa") != k: sp.setdefault(k, v)   # os de folha própria o jogo acha sozinho
    for npc, folha in NPC_SPR.items(): sp.setdefault("npc:" + npc, {"usa": folha})
    sp.setdefault("npc:esfinge_amenti", {"usa": "esfinge_de_hawara", "escala": 0.7, "fantasma": True})
    gravar(ex_p, ex, compacto=False); gravar(sp_p, sp, compacto=False)


if __name__ == "__main__":
    copiar_mapa(f"{P}/design/mapas/atlantida/atlantida.json", "atlantida")
    copiar_mapa(f"{P}/design/mapas/amenti/saloes_de_amenti.json", "saloes_de_amenti")
    fenda_no_eden(); esfinge_no_egito(); dados()
    print("atlântida ok")

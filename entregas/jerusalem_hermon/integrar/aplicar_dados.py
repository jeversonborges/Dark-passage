#!/usr/bin/env python3
"""Junta Jerusalém e Monte Hermon (e o mapa do Cume dos Vigilantes) aos dados do projeto, para a 0.9.3.

Uso (da raiz do repositório):  python3 entregas/jerusalem_hermon/integrar/aplicar_dados.py [RAIZ]

Pode rodar de novo sem estragar: tudo é por id (o que já existe é atualizado, nada é duplicado).
O que faz:
  1. design/missoes/dados/*: missões, NPCs, diálogos, itens, monstros, objetos/baús, lojas e locais de Jerusalém.
     Dois ids batiam com coisas que entraram depois da entrega (16/10): o acessório `malho_de_tubal` vira
     `martelo_de_tubal` (o `malho_de_tubal` agora é a arma lendária do Hermon) e a loja do Zaqueu de Jerusalém vira
     `loja_zaqueu_cobrador` (a `loja_zaqueu` é a do convite, em São Lázaro). A g02 passa a abrir com g01 OU jg01.
     XP: cada missão de Jerusalém recebe o XP atual da missão da Vigília que ela espelha (regra dos 25%, 17/10).
  2. design/mapas/jerusalem_hermon/: os 4 mapas (área + 3 andares do Fosso), com a Estrada do Sul (portal para o
     deserto, nível 12) dentro de Jerusalém.
  3. (a volta, Estrada dos Peregrinos, entra pelo game/tools/mapa.py, no jerusalem.patch)
  4. game/data/v06_extra.json: mobs, chefes (com `invoca_troca`), tabelas de drop e nomes do HUD.
     game/data/sprites_substitutos.json: os recolores dos 21 mobs e 3 chefes.
  5. design/pvp/hermon/cume_dos_vigilantes.json: o mapa do evento (o sync.sh do patch copia para game/data/mapas).
  6. entregas/teleporte/gerar.py: Jerusalém e Monte Hermon no menu de teleporte (V). Gere o teleporte.json DEPOIS
     do sync.sh (ele lê game/data/mapas): python3 entregas/teleporte/gerar.py game/data/mapas game/data/teleporte.json
"""
import json, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
JH = AQUI.parent
RAIZ = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else JH.parent.parent
DADOS = RAIZ / "design/missoes/dados"
MAPAS = ["jerusalem_hermon", "minas_dos_gigantes", "salao_das_noivas", "altar_do_juramento"]

TROCA_ID = {"malho_de_tubal": "martelo_de_tubal", "loja_zaqueu": "loja_zaqueu_cobrador"}
TROCA_NOME = {"martelo_de_tubal": "Martelo de Tubal"}
LOJAS_JERUSALEM = ["loja_hulda", "loja_zilpa", "loja_bartimeu", "loja_carrinho_bartimeu", "loja_zaqueu_cobrador"]

# Estrada para o deserto (a volta está no game/tools/mapa.py). O São Lázaro novo (200x200) não tem a Capela de
# antes: a chegada fica no caminho da banca da Corvina (Arautos), no sul da cidade.
ESTRADA_SUL = {"kind": "portal", "pos": [101.5, 32.0], "para": "area_inicial", "chegada": [56.5, 128.5],
               "nome": "Estrada do Sul · para o Deserto de Absinto", "visual": "escada_subida", "nivel_minimo": 12,
               "texto_trancado": "Bartimeu segura o seu braço: \"Lá embaixo é a Vigília. Volte no nível 12.\""}


def ler(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gravar(p, d, compacto=False):
    """Grava no mesmo estilo do arquivo que já existe (uma linha só ou indentado), para o diff ficar limpo."""
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    if compacto:
        txt = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    else:
        linhas = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
        if len(linhas) == 1: txt = json.dumps(d, ensure_ascii=False)
        else:
            ind = len(linhas[1]) - len(linhas[1].lstrip(" ")) if len(linhas) > 1 else 1
            txt = json.dumps(d, ensure_ascii=False, indent=ind or 1)
    p.write_text(txt, encoding="utf-8")


def trocar(o):
    """Aplica TROCA_ID em todo valor string igual a um id trocado (referências em missões, lojas, drops)."""
    if isinstance(o, dict): return {k: trocar(v) for k, v in o.items()}
    if isinstance(o, list): return [trocar(v) for v in o]
    if isinstance(o, str): return TROCA_ID.get(o, o)
    return o


def juntar(lista, novos, rotulo):
    idx = {x.get("id"): i for i, x in enumerate(lista)}
    n_novo = n_atual = 0
    for x in novos:
        if x["id"] in idx: lista[idx[x["id"]]] = x; n_atual += 1
        else: lista.append(x); n_novo += 1
    print(f"  {rotulo:<22} +{n_novo} novos, {n_atual} atualizados")


def portal_em(mapa, portal):
    objs = mapa.setdefault("objetos", [])
    objs[:] = [o for o in objs if not (o.get("kind") == "portal" and o.get("para") == portal["para"] and o.get("nome") == portal["nome"])]
    objs.append(portal)


def dados_de_missao():
    print("1. design/missoes/dados")
    for arq, chaves in [("dialogos", ["dialogos"]), ("itens", ["itens"]), ("lojas", ["lojas"]), ("missoes", ["missoes"]),
                        ("monstros", ["monstros"]), ("npcs", ["npcs"]), ("objetos", ["objetos", "baus"])]:
        a = trocar(ler(JH / f"{arq}_acrescimo.json")); d = ler(DADOS / f"{arq}.json")
        if arq == "missoes":   # regra dos 25% (Revisão das missões, 17/10): cada missão daqui dá o XP de hoje da missão espelhada
            hoje = {m["id"]: m for m in d["missoes"]}
            for m in a["missoes"]:
                e = hoje.get(m.get("espelho_de"), {})
                if "xp" in m.get("recompensas", {}) and "xp" in e.get("recompensas", {}): m["recompensas"]["xp"] = e["recompensas"]["xp"]
        for k in chaves:
            if arq == "itens":
                for it in a[k]:
                    if it["id"] in TROCA_NOME: it["nome"] = TROCA_NOME[it["id"]]
            juntar(d[k], a[k], f"{arq}.{k}")
        if arq == "missoes":   # a linha G (fim de jogo do nível 12) abre pelo g01 da Vigília OU pelo jg01 de Jerusalém
            g02 = next((m for m in d["missoes"] if m["id"] == "g02"), None)
            if g02 is not None:
                g02["requer"] = [r for r in g02.get("requer", []) if r != "g01"]
                if not g02["requer"]: g02.pop("requer")
                g02["requer_qualquer"] = ["g01", "jg01"]
        gravar(DADOS / f"{arq}.json", d)
    a = ler(JH / "locais_acrescimo.json"); d = ler(DADOS / "locais.json")
    juntar(d["areas"], a["areas"], "locais.areas")
    juntar(d["dungeons"], a["dungeons"], "locais.dungeons")
    juntar(d["spots"]["pedidos"], a["spots_pedidos"], "locais.spots")
    gravar(DADOS / "locais.json", d)


def mapas():
    print("2. design/mapas/jerusalem_hermon")
    dst = RAIZ / "design/mapas/jerusalem_hermon"
    for m in MAPAS:
        d = ler(JH / f"{m}.json")
        if m == "jerusalem_hermon": portal_em(d, ESTRADA_SUL)
        gravar(dst / f"{m}.json", d, compacto=True)
    for p in JH.glob("planta_*.png"): shutil.copy2(p, dst / p.name)
    print(f"  {len(MAPAS)} mapas + plantas")


def dados_do_jogo():
    print("4. game/data")
    ex_p = RAIZ / "game/data/v06_extra.json"; ex = ler(ex_p)
    jd = ler(JH / "dados.json")
    # mobs que herdam um ataque de invocar (Capataz -> carniçais, Eco -> eco) chamam o espelho daqui, não o do deserto
    base_mobs = ler(RAIZ / "design/combate/mobs.json")["mobs"]
    espelho = {}
    for k, m in jd["mobs"].items(): espelho.setdefault(m.get("espelho_de", m.get("base")), k)
    for k, m in jd["mobs"].items():
        ats = base_mobs.get(m.get("base"), {}).get("ataques", [])
        if any("invoca" in a for a in ats):
            m["ataques"] = [dict(a, invoca={(k if i == m["base"] else espelho.get(i, i)): q for i, q in a["invoca"].items()}) if "invoca" in a else a
                            for a in ats]
    ex.setdefault("mobs", {}).update(jd["mobs"])
    tabelas = ler(RAIZ / "design/combate/drops.json")["tabelas"]
    for novo, orig in jd["drops_alias"].items():
        ex.setdefault("drops", {})[novo] = tabelas[orig]
    # os chefes daqui usam o roteiro de um chefe da Cripta (mecanica_de) e chamam os próprios mobs (invoca_troca)
    troca = {"soldado_caido": "soldado_de_pedra", "carpideira_de_ossos": "noiva_afogada",
             "eco_da_trombeta": "eco_do_juramento", "querubim_desfeito": "vigilante_desfeito"}
    for k, c in jd["chefes"].items():
        c = dict(c); c["invoca_troca"] = troca
        ex.setdefault("chefes", {})[k] = c
    ex.setdefault("nomes_mapa_hud", {}).update(jd["nomes_mapa_hud"])
    gravar(ex_p, ex)
    print(f"  v06_extra: {len(jd['mobs'])} mobs, {len(jd['chefes'])} chefes, {len(jd['drops_alias'])} tabelas de drop")
    sp_p = RAIZ / "game/data/sprites_substitutos.json"; sp = ler(sp_p)
    sp.update(jd["sprites"]); gravar(sp_p, sp)
    print(f"  sprites_substitutos: {len(jd['sprites'])}")
    print("5. design/pvp/hermon/cume_dos_vigilantes.json")
    shutil.copy2(RAIZ / "entregas/evento_hermon/mapa/cume_dos_vigilantes.json", RAIZ / "design/pvp/hermon/cume_dos_vigilantes.json")


def teleporte():
    print("6. teleporte")
    g = RAIZ / "entregas/teleporte/gerar.py"
    t = g.read_text(encoding="utf-8")
    linha = '    {"mapa": "jerusalem_hermon", "grupo": "Jerusalém e Monte Hermon"},\n'
    if linha not in t:
        t = t.replace('    {"mapa": "area_inicial", "grupo": "Deserto de Absinto"},\n',
                      '    {"mapa": "area_inicial", "grupo": "Deserto de Absinto"},\n' + linha)
        g.write_text(t, encoding="utf-8")
    print("  Jerusalém e Monte Hermon no gerar.py (rode-o depois do sync.sh)")


def validar():
    print("7. validar.py")
    r = subprocess.run([sys.executable, "validar.py"], cwd=RAIZ / "design/missoes", capture_output=True, text=True)
    print("  " + "\n  ".join((r.stdout + r.stderr).strip().splitlines()[-6:]))
    if r.returncode != 0: sys.exit("validar.py falhou")


if __name__ == "__main__":
    print("raiz:", RAIZ)
    dados_de_missao(); mapas(); dados_do_jogo(); teleporte(); validar()
    print("\nAgora: patch -p1 < entregas/jerusalem_hermon/integrar/jerusalem.patch (se ainda não aplicado), "
          "python3 design/skills-itens/fontes/gerar_json.py, cd game && bash tools/sync.sh, "
          "python3 ../entregas/teleporte/gerar.py data/mapas data/teleporte.json")

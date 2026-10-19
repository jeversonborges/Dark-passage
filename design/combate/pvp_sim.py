"""Simulador de PvP 1x1 do DARK PASSAGE (teste de balanceamento, v0.1).

Faz luta 1x1 entre todas as classes basicas (lvl 29) e entre todas as evolucoes (lvl 40).
Mesmo nivel, mesma armadura e mesma arma para todos. Cada lutador usa as habilidades
que ja tem, com uma heuristica gulosa: cura se estiver baixo, buff se estiver livre,
a habilidade de maior dano pronta e paga, e o basico quando nada mais esta pronto.

Le classes_base.json e formulas.json (design/combate) e evolucoes.json (copia
sincronizada em game/data/design/combate). Nao altera nenhum numero do jogo.

Simplificacoes (ver relatorio): sem alcance e sem movimento (todos batem de perto),
sem invocacoes, sem atordoamento/derrubar/silencio, sem passivas exceto as de dano,
roubo de vida e recurso, sem itens excelentes nem resistencias elementais.

Uso: python3 pvp_sim.py [--rodadas 40] [--saida DIR]
Gera resultados.json e relatorio.md em DIR (padrao: /mnt/project-files/entregas/pvp_balanceamento).
"""
import argparse, json, os, random
from collections import Counter

D = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(D, "..", ".."))
BASE = json.load(open(f"{D}/classes_base.json"))["classes"]
FORMULAS = json.load(open(f"{D}/formulas.json"))
EVOS = json.load(open(f"{RAIZ}/game/data/design/combate/evolucoes.json"))["evolucoes"]

NOME_BASE = {"anjo": "Anjo", "cultista": "Cultista", "mutante": "Mutante", "demonio": "Demônio",
             "humano": "Humano", "tecnomancer": "Tecnomancer", "warlord": "Warlord"}
NIVEL_BASICAS = 29
NIVEL_EVOLUCOES = 40
DT = 0.05            # passo da simulacao (s)
TEMPO_MAX = 150.0    # passou disso sem morte: empate
ARMADURA_POR_NIVEL = 1.5   # defesa_armadura_completa = 1.5 * nivel (armas_por_faixa)
MAGICOS = {"magico", "sagrado"}
TAG_DA_CLASSE = {"anjo": "celestial", "demonio": "infernal", "mutante": "praga", "humano": "humano"}

# Recurso por classe (classes_base.json). custo_pct: Sangue do Cultista, custo em % do HP max.
RECURSO = {
    "anjo": dict(maximo=lambda esp: 100 + esp / 2, inicio=50, regen=1.5, golpe=4),
    "mutante": dict(maximo=lambda esp: 100, inicio=0, regen=0, golpe=3, por_pct_hp_perdido=1.0),
    "demonio": dict(maximo=lambda esp: 100, inicio=0, regen=0, golpe=6, bonus_acima_80=0.15),
    "humano": dict(maximo=lambda esp: 100, inicio=100, regen=6, golpe=0),       # Folego
    "tecnomancer": dict(maximo=lambda esp: 100 + esp / 2, inicio=100, regen=3, golpe=0),
    "warlord": dict(maximo=lambda esp: 100, inicio=0, regen=0, golpe=4, por_golpe_recebido=3),
}


def vantagem(atacante, defensor):
    """Vantagem cruzada (formulas.json): mult quando o alvo e da lista do atacante."""
    regra = FORMULAS["vantagem_cruzada"].get(atacante, {})
    for alvo in regra.get("alvos", []):
        if alvo == defensor or (alvo.startswith("tag:") and alvo[4:] == TAG_DA_CLASSE.get(defensor)):
            return regra["mult"]
    return 1.0


def perfil_base(perfil, a):
    """Dano base min/max antes da arma (formulas.json dano_base; hibrido como em simular.py)."""
    F, A, E = a["FOR"], a["AGI"], a["ESP"]
    return {
        "corpo_a_corpo": (F / 6, F / 4),
        "corpo_a_corpo_pesado": (F / 6, F / 4),   # sem entrada no formulas.json: usa o corpo a corpo
        "corpo_a_corpo_agil": (F / 6 + A / 10, F / 4 + A / 10),
        "distancia": (A / 7 + F / 14, A / 4 + F / 8),
        "magico": (E / 9, E / 4),
        "sagrado": (E / 10 + F / 12, E / 5 + F / 8),
        "hibrido": ((F / 6 + A / 7 + F / 14) / 2, (F / 4 + A / 4 + F / 8) / 2),
    }[perfil]


def golpes_da_habilidade(h):
    """Lista de multiplicadores, um por golpe que a habilidade entrega."""
    if "golpes" in h:             # evolucoes: golpes x mult (sem mult_por_golpe)
        return [h.get("mult_por_golpe", h.get("mult", 1.0))] * h["golpes"]
    if "ticks" in h and "mult_por_tick" in h:
        return [h["mult_por_tick"]] * h["ticks"]
    if "projeteis" in h:
        return [h["mult_por_projetil"]] * h["projeteis"]
    if "saltos" in h:             # 1x1: so o primeiro salto acerta (os outros cairiam em outros inimigos)
        return [h["mult"]]
    if "mult" in h:
        return [h["mult"]]
    return []


def normaliza(h, cultista):
    efeito = dict(h.get("efeito", {}))
    dots = []
    for tipo in ("sangramento", "veneno", "queimadura"):
        for origem in (h, efeito):
            if tipo in origem and origem[tipo].get("dano_por_s_mult"):
                dots.append((tipo, origem[tipo]["duracao"], origem[tipo]["dano_por_s_mult"]))
    buff = h.get("buff", {})
    buff = buff if any(k in buff for k in ("dano", "dano_magico", "dano_recebido")) else None
    custo = h.get("custo", 0)
    cura = h.get("cura_mult", h.get("cura_mult_por_tick", 0) * h.get("ticks", 0))
    return dict(
        id=h["id"], nome=h["nome"], recarga=float(h.get("recarga", 0)), custo=custo,
        custo_pct=cultista, hits=golpes_da_habilidade(h),
        area=bool(h.get("area_raio") or h.get("nunca_erra") or "arco_graus" in h or "cone_graus" in h),
        crit=h.get("critico_extra", 0), dots=dots, buff=buff, cura=cura if not h.get("mult") and cura else 0,
        gera=h.get("gera", 0), cast=max(0.3, h.get("conjuracao", h.get("preparo", 0))),
        cd_ate=0.0,
    )


class Lutador:
    def __init__(self, nome, base_id, nivel, evo=None):
        self.nome, self.base, self.L = nome, base_id, nivel
        base = BASE[base_id]
        bonus = evo["bonus"] if evo else {}
        a = dict(base["atributos_iniciais"])
        for k, v in base["build_sugerida_por_nivel"].items():
            a[k] += v * (nivel - 1)
        for k in ("FOR", "AGI", "VIT", "ESP"):
            a[k] += bonus.get(k, 0)
        self.FOR, self.AGI, self.VIT, self.ESP = a["FOR"], a["AGI"], a["VIT"], a["ESP"]
        self.perfil = base["perfil_dano"]
        self.magico = self.perfil in MAGICOS
        mn, mx = perfil_base(self.perfil, a)
        arma = 5 + 1.2 * nivel     # mesma arma para todos (armas_por_faixa)
        self.dmg_min, self.dmg_max = mn + arma * 0.8, mx + arma * 1.2
        self.hp_max = (base["hp"]["base"] + base["hp"]["por_nivel"] * nivel
                       + base["hp"]["por_vit"] * self.VIT) * bonus.get("hp_mult", 1)
        self.defesa_base = (self.VIT / 5 + self.AGI / 10 + ARMADURA_POR_NIVEL * nivel) * bonus.get("defesa_mult", 1)
        intervalo = base["arma_inicial"]["intervalo"]
        if self.perfil == "hibrido":
            intervalo = (intervalo + base["arma_secundaria"]["intervalo"]) / 2
        aspd = min(2.0, 1 + self.AGI * 0.004) * bonus.get("velocidade_ataque_mult", 1)
        self.intervalo = intervalo / aspd
        self.dano_mult = bonus.get("dano_mult", 1) * (bonus.get("dano_magico_mult", 1) if self.magico else 1)
        self.crit_passiva = bonus.get("critico", 0)
        self.crit_mult = (1.75 if base_id == "humano" else 1.5) * bonus.get("dano_critico_mult", 1)
        self.roubo_base = (0.04 if base_id == "demonio" else 0) + bonus.get("roubo_vida", 0)
        self.regen_mult = bonus.get("recurso_regen_mult", 1)
        self.cura_mult = bonus.get("cura_mult", 1)
        self.dot_mult = bonus.get("dano_continuo_mult", 1)
        self.conj_mult = bonus.get("conjuracao_mult", 1)
        self.cultista = base_id == "cultista"
        self.recurso = None if self.cultista else RECURSO[base_id]
        self.skills = [normaliza(h, self.cultista) for h in base["habilidades"]
                       if not h.get("passiva") and h["nivel"] <= nivel]
        if evo:
            self.skills += [normaliza(h, self.cultista) for h in evo["habilidades"]
                            if not h.get("passiva") and h["nivel"] <= nivel]
        for s in self.skills:
            s["cast"] *= self.conj_mult

    # ---- estado da luta -------------------------------------------------
    def reset(self):
        self.hp = self.hp_max
        self.pool = self.recurso["inicio"] if self.recurso else 0
        self.pool_max = self.recurso["maximo"](self.ESP) if self.recurso else 0
        # entrada aleatoria: a aproximacao nao da iniciativa a quem age primeiro no tick 0
        self.pronto_em = random.uniform(0, 1.0)
        self.dots = []             # [dps, fim, dono]
        self.buffs = {}            # nome -> (valor, fim)
        self.dealt = 0.0
        self.usos = Counter()
        for s in self.skills:
            s["cd_ate"] = 0.0

    def ativo(self, nome, t):
        valor, fim = self.buffs.get(nome, (0, 0))
        return valor if t < fim else 0

    def dano_mult_atual(self, t):
        mult = self.dano_mult * (1 + self.ativo("dano", t))
        if self.recurso and self.base == "demonio" and self.pool >= 80:
            mult *= 1 + self.recurso["bonus_acima_80"]
        if self.base == "warlord":
            mult *= 1 + 0.03 * (self.pool // 20)
        return mult

    def defesa_atual(self):
        mult = 1.0
        if self.base == "warlord":
            mult = 1.03 + 0.02 * (self.pool // 20)   # Coroa de Ferro (1 inimigo) + Odio
        return self.defesa_base * mult

    def recebido_mult(self, t):
        return 1 + self.ativo("recebido", t)

    def roubo_atual(self):
        extra = 0.10 if self.base == "demonio" and self.hp < 0.30 * self.hp_max else 0
        return self.roubo_base + extra

    def pode_pagar(self, s):
        if s["custo_pct"]:          # Sangue: nunca mata, o custo para em 1 HP
            return self.hp > 1
        return self.pool >= s["custo"]

    def paga(self, s):
        if s["custo_pct"]:
            custo = s["custo"] if s["custo"] < 1 else s["custo"] / 100
            self.hp = max(1, self.hp - custo * self.hp_max)
        else:
            self.pool -= s["custo"]

    def ganha(self, quanto):
        if self.recurso:
            self.pool = min(self.pool_max, self.pool + quanto)

    def regen(self):
        if self.recurso and self.recurso["regen"]:
            self.pool = min(self.pool_max, self.pool + self.recurso["regen"] * self.regen_mult * DT)

    def escolhe(self, t):
        """Heuristica gulosa: cura baixa, buff livre, maior dano pronto, senao basico."""
        pronto = [s for s in self.skills if s["cd_ate"] <= t and self.pode_pagar(s)]
        if self.hp < 0.45 * self.hp_max:
            for s in pronto:
                if s["cura"]:
                    return "cura", s
        for s in pronto:
            if s["buff"] and not self.ativo("dano", t) and not self.ativo("recebido", t):
                return "skill", s
        com_dano = [s for s in pronto if s["hits"] and not s["buff"]]
        if com_dano:
            return "skill", max(com_dano, key=lambda s: sum(s["hits"]))
        return "basico", None

    def tick_dots(self, t):
        for dot in list(self.dots):
            dps, fim, dono = dot
            if t >= fim:
                self.dots.remove(dot)
                continue
            self.recebe(dps * DT, t, dono)

    def recebe(self, dano, t, atacante):
        self.hp -= dano
        if self.base == "mutante":
            self.ganha(dano / self.hp_max * 100 * self.recurso["por_pct_hp_perdido"])
        if self.base == "warlord":
            self.ganha(self.recurso["por_golpe_recebido"])
        atacante.dealt += dano

    def golpe(self, df, mult, t, area=False, crit_extra=0.0):
        """Um golpe. Devolve (dano, acertou) seguindo formulas.json."""
        bruto = random.uniform(self.dmg_min, self.dmg_max) * mult * self.dano_mult_atual(t)
        if not area:
            ar = self.L * 3 + (self.ESP / 2 + self.AGI / 2 if self.magico else self.AGI + self.FOR / 4)
            er = df.L * 2 + df.AGI / 2
            chance = min(0.98, max(0.55, 0.90 + 0.25 * (ar - er) / (ar + er)))
            if random.random() > chance:
                return 0, False
        chance_crit = min(0.4, 0.05 + self.AGI * 0.0008) + crit_extra + self.crit_passiva
        if random.random() < chance_crit:
            bruto *= self.crit_mult
        bruto *= vantagem(self.base, df.base)
        defesa = df.defesa_atual()
        mitig = min(0.7, defesa / (defesa + 40 + 8 * self.L))
        dano = max(bruto * (1 - mitig), bruto * 0.05) * df.recebido_mult(t)
        return max(1, round(dano)), True

    def age(self, t, df):
        """Escolhe e executa uma acao. Devolve quanto tempo ela ocupa."""
        acao, s = self.escolhe(t)
        if acao == "basico":
            dano, ok = self.golpe(df, 1.0, t)
            if ok:
                self.ganha(self.recurso["golpe"] if self.recurso else 0)
                self.causa(dano, t, df)
            self.usos["Básico"] += 1
            return self.intervalo
        self.paga(s)
        s["cd_ate"] = t + s["recarga"]
        self.usos[s["nome"]] += 1
        self.ganha(s["gera"])
        if s["cura"]:
            self.hp = min(self.hp_max, self.hp + (self.ESP / 3 + self.L * 2) * s["cura"] * self.cura_mult)
        if s["buff"]:
            b = s["buff"]
            for chave in ("dano", "dano_recebido"):
                if chave in b:
                    nome = "recebido" if chave == "dano_recebido" else "dano"
                    self.buffs[nome] = (b[chave], t + b["duracao"])
            if "dano_magico" in b:
                self.buffs["dano"] = (b["dano_magico"], t + b["duracao"])
        for h in s["hits"]:
            dano, ok = self.golpe(df, h, t, area=s["area"], crit_extra=s["crit"])
            if ok:
                self.ganha(self.recurso["golpe"] if self.recurso else 0)
                self.causa(dano, t, df)
        # uma acao dura no minimo um intervalo de basico: sem isso, todas as skills prontas
        # no inicio sairiam em 0.3 s e a luta acabaria em rajada
        ocupa = max(self.intervalo, s["cast"])
        for tipo, duracao, mult_dot in s["dots"]:
            base = (self.dmg_min + self.dmg_max) / 2 * self.dano_mult_atual(t) * mult_dot * self.dot_mult
            if df.base == "mutante" and tipo in ("veneno", "sangramento"):
                base *= 0.7      # Mutante resiste a veneno e sangramento (formulas.json)
            df.dots.append([base * (1 - min(0.7, df.defesa_atual() / (df.defesa_atual() + 40 + 8 * self.L))), t + duracao, self])
        return ocupa

    def causa(self, dano, t, df):
        if self.roubo_atual():
            self.hp = min(self.hp_max, self.hp + dano * self.roubo_atual())
        df.recebe(dano, t, self)


def luta(a, b):
    a.reset()
    b.reset()
    t = 0.0
    while t < TEMPO_MAX:
        t += DT
        for x in (a, b):
            x.regen()
        a.tick_dots(t)
        b.tick_dots(t)
        if a.hp <= 0 or b.hp <= 0:
            break
        for x, y in ((a, b), (b, a)):
            if x.hp > 0 and y.hp > 0 and t >= x.pronto_em:
                x.pronto_em = t + x.age(t, y)
            if x.hp <= 0 or y.hp <= 0:
                break
    if a.hp > 0 and b.hp > 0:
        return dict(vencedor=None, tempo=t, hp_pct=0.0)
    vencedor = a if a.hp > 0 else b
    return dict(vencedor=vencedor, tempo=t, hp_pct=vencedor.hp / vencedor.hp_max * 100)


def roda_par(x, y, rodadas):
    """Luta x contra y nos dois sentidos (quem comeca), rodadas vezes cada."""
    lutas = []
    for _ in range(rodadas):
        for a, b in ((x, y), (y, x)):
            r = luta(a, b)
            lutas.append(dict(a=a.nome, b=b.nome, vencedor=r["vencedor"].nome if r["vencedor"] else None,
                              tempo=r["tempo"], hp_pct=r["hp_pct"],
                              dano_a=a.dealt, dano_b=b.dealt, usos_a=dict(a.usos), usos_b=dict(b.usos)))
    return lutas


def resume(x, y, lutas):
    n = len(lutas)
    vitorias_x = sum(1 for l in lutas if l["vencedor"] == x.nome)
    vitorias_y = sum(1 for l in lutas if l["vencedor"] == y.nome)
    empates = n - vitorias_x - vitorias_y
    tempo = sum(l["tempo"] for l in lutas) / n

    def lado(nome):
        dps = []
        usos = Counter()
        for l in lutas:
            if l["a"] == nome:
                dps.append(l["dano_a"] / l["tempo"])
                usos.update(l["usos_a"])
            else:
                dps.append(l["dano_b"] / l["tempo"])
                usos.update(l["usos_b"])
        top = [f"{k} ({v / n:.1f}/luta)" for k, v in usos.most_common(3)]
        return sum(dps) / n, top

    dps_x, top_x = lado(x.nome)
    dps_y, top_y = lado(y.nome)
    hp_vencedores = [l["hp_pct"] for l in lutas if l["vencedor"]]
    return dict(
        x=x.nome, y=y.nome, vitorias_x=vitorias_x / n, vitorias_y=vitorias_y / n, empates=empates / n,
        tempo_medio_s=tempo, hp_vencedor_pct=sum(hp_vencedores) / len(hp_vencedores) if hp_vencedores else 0,
        dps_x=dps_x, dps_y=dps_y, top_x=top_x, top_y=top_y,
    )


def rodada_completa(grupo, rodadas, rotulo):
    resultados = {}
    matriz = {}
    for i, x in enumerate(grupo):
        matriz.setdefault(x.nome, {})
        for y in grupo[i + 1:]:
            r = resume(x, y, roda_par(x, y, rodadas))
            resultados[f"{x.nome} x {y.nome}"] = r
            matriz[x.nome][y.nome] = r["vitorias_x"]
            matriz.setdefault(y.nome, {})[x.nome] = r["vitorias_y"]
    print(f"{rotulo}: {len(resultados)} pares", flush=True)
    return resultados, matriz


def monta_grupos():
    basicas = [Lutador(NOME_BASE[b], b, NIVEL_BASICAS) for b in NOME_BASE]
    evos = [Lutador(e["nome"], e["classe_base"], NIVEL_EVOLUCOES, e) for e in EVOS.values()]
    return basicas, evos


def tabela_matriz(nomes, matriz):
    linhas = ["| | " + " | ".join(nomes) + " |", "|---|" + "---|" * len(nomes)]
    for x in nomes:
        celulas = []
        for y in nomes:
            if x == y:
                celulas.append("—")
            else:
                v = matriz[x].get(y)
                celulas.append("—" if v is None else f"{v * 100:.0f}%")
        linhas.append(f"| **{x}** | " + " | ".join(celulas) + " |")
    return "\n".join(linhas)


def tabela_pares(resultados):
    linhas = ["| Par | Vence (1º / 2º) | Empate | Tempo médio | HP restante do vencedor | DPS (1º / 2º) | Skills mais usadas (1º) | Skills mais usadas (2º) |",
              "|---|---|---|---|---|---|---|---|"]
    for par, r in resultados.items():
        def top(lista):
            return "; ".join(t for t in lista) or "—"
        linhas.append(
            f"| {par} | {r['vitorias_x'] * 100:.0f}% / {r['vitorias_y'] * 100:.0f}% | {r['empates'] * 100:.0f}% | "
            f"{r['tempo_medio_s']:.1f} s | {r['hp_vencedor_pct']:.0f}% | {r['dps_x']:.0f} / {r['dps_y']:.0f} | "
            f"{top(r['top_x'])} | {top(r['top_y'])} |")
    return "\n".join(linhas)


def resumo_classes(nomes, matriz):
    linhas = ["| Classe | Vitória média contra o grupo | Sinal |", "|---|---|---|"]
    for x in nomes:
        vs = [matriz[x][y] for y in nomes if y != x and matriz[x].get(y) is not None]
        media = sum(vs) / len(vs)
        sinal = "forte demais" if media > 0.6 else "fraca" if media < 0.4 else "ok"
        linhas.append(f"| {x} | {media * 100:.0f}% | {sinal} |")
    return "\n".join(linhas)


def relatorio(saida, dados):
    nomes_b = list(NOME_BASE.values())
    nomes_e = [e["nome"] for e in EVOS.values()]
    texto = f"""# Teste de PvP 1x1 (balanceamento)

Gerado por `design/combate/pvp_sim.py` ({dados['rodadas_por_sentido']} lutas por sentido em cada par, semente fixa).
**Só mostra os números. Nenhum valor do jogo foi alterado.**

## Como foi feito
- **Básicas:** 7 classes no nível {dados['nivel_basicas']}, sem evolução.
- **Evoluções:** {len(nomes_e)} evoluções no nível {dados['nivel_evolucoes']}, com as skills básicas da classe e as da evolução até esse nível.
- Mesma armadura para todos (defesa de armadura = 1,5 × nível) e mesma arma para todos (média 5 + 1,2 × nível).
- Atributos: cada classe com a própria distribuição (atributos iniciais + build sugerida por nível), como no `classes_base.json`. Evoluções somam o bônus de atributos da evolução.
- Fórmulas de `formulas.json`: acerto, crítico, mitigação, vantagem cruzada. Área sempre acerta.
- Cada lutador usa a skill de maior dano pronta e paga; cura abaixo de 45% do HP; buff quando livre; o básico quando nada mais está pronto. Uma ação dura pelo menos um intervalo de básico.
- Entrada aleatória (0 a 1 s) para ninguém ganhar a iniciativa no tick zero.

## Limites deste modelo
- **Sem alcance nem movimento:** todos batem de perto. Classes à distância (Humano, Cultista, Tecnomancer e os Pistoleiro, Mechanicus, Engenheiro Herege) não kitam aqui. Isso pesa contra elas.
- **Não modelado:** invocações (Servo, Torreta, familiar do Cultista, Estandarte), atordoar, derrubar, silenciar, enraizar, escudos, reflexo, ressurreição, passivas que não são de dano, roubo de vida além do básico, itens excelentes, resistências elementais.
- **Buffs:** só os que mexem em dano ou dano recebido (Juramento de Ódio, Carapaça, Muralha de Escudo, Pacto Rubro).
- **Sangue do Cultista:** custo em % do HP máximo, nunca mata. Nas evoluções, custo ≥ 1 foi lido como ÷100 (ex.: 28 → 28% do HP). **Premissa a confirmar.**
- **Evoluções:** lidas de `game/data/design/combate/evolucoes.json` (cópia sincronizada). **Paladino e Duelista (Guerreiro) não aparecem:** não há dados de evolução deles no repositório.

## Matriz — Básicas (nível {dados['nivel_basicas']})
Cada célula é a % de vitórias da **linha** contra a **coluna** (somando as duas ordens de início).

{tabela_matriz(nomes_b, dados['matriz_basicas'])}

## Matriz — Evoluções (nível {dados['nivel_evolucoes']})

{tabela_matriz(nomes_e, dados['matriz_evolucoes'])}

## Resumo por classe — Básicas
{resumo_classes(nomes_b, dados['matriz_basicas'])}

## Resumo por classe — Evoluções
{resumo_classes(nomes_e, dados['matriz_evolucoes'])}

## Pares — Básicas
{tabela_pares(dados['basicas'])}

## Pares — Evoluções
{tabela_pares(dados['evolucoes'])}
"""
    with open(os.path.join(saida, "relatorio.md"), "w") as f:
        f.write(texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodadas", type=int, default=40)
    ap.add_argument("--saida", default="/mnt/project-files/entregas/pvp_balanceamento")
    ap.add_argument("--semente", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.semente)
    basicas, evos = monta_grupos()
    res_b, mat_b = rodada_completa(basicas, args.rodadas, "Basicas lvl 29")
    res_e, mat_e = rodada_completa(evos, args.rodadas, "Evolucoes lvl 40")
    os.makedirs(args.saida, exist_ok=True)
    saida = dict(rodadas_por_sentido=args.rodadas, nivel_basicas=NIVEL_BASICAS,
                 nivel_evolucoes=NIVEL_EVOLUCOES, basicas=res_b, evolucoes=res_e,
                 matriz_basicas=mat_b, matriz_evolucoes=mat_e)
    with open(os.path.join(args.saida, "resultados.json"), "w") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    relatorio(args.saida, saida)
    print(f"gravado em {args.saida}/resultados.json e relatorio.md")


if __name__ == "__main__":
    main()

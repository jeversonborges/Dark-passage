"""Conta de farm por minuto num spot (DARK PASSAGE v0.2).
Le classes_base.json, mobs.json e farm_auto.json. Para cada classe e nivel de spot,
compara o modo automatico com e sem pocao: abates/min, XP/min, ouro/min, pocoes/min,
custo das pocoes e minutos por nivel. Uso: python3 farm.py
"""
import json, os, importlib.util
D = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sim", f"{D}/simular.py")
sim = importlib.util.module_from_spec(spec)
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(sim)
C = sim.C
F = json.load(open(f"{D}/farm_auto.json"))
P = json.load(open(f"{D}/progressao.json"))["tabela"]
SP = F["spots"]["padrao"]
POT = F["pocoes"]["itens"]
LEQ = {s["classe"]: s for s in F["skill_leque_nivel5"]["skills"]}

def pool(cls, L):
    a = sim.stats(cls, L); p = sim.player(cls, L)
    r = F["recursos"][cls]
    if r["tipo"] == "hp": return p["hp"]
    return r["max_base"] + a["ESP"] * r.get("max_por_esp", 0)

def farm(cls, Lp, Ls, pots):
    p = sim.player(cls, Lp)
    mix = SP["mistura"]  # arquetipo -> fracao
    mobs = [(sim.mob(Ls, k), f) for k, f in mix.items()]
    mhp = sum(m["hp"] * f for m, f in mobs); mdef = sum(m["deff"] * f for m, f in mobs)
    mdmg = sum(m["dmg"] * f for m, f in mobs); mint = sum(m["interval"] * f for m, f in mobs)
    dl = Ls - Lp
    lvl = max(0.4, 1 - 0.04 * dl) if dl > 0 else min(1.2, 1 + 0.02 * -dl)
    hit = sim.hitch(p["ar"], Ls*3 + 5, dl)
    one = sim.per_hit(p, Lp, mdef, Ls) * lvl
    basic_dps = one * hit / p["interval"]
    s = LEQ[cls]
    alvos = SP["alvos_por_leque"]
    fan_dps = one * s["mult"] * alvos / s["recarga"]
    # recurso
    r = F["recursos"][cls]; pl = pool(cls, Lp)
    custo_s = (s["custo"] * (pl if r["tipo"] == "hp" else 1)) / s["recarga"]
    ganho_s = r.get("regen_combate_s", 0) * (pl if r.get("regen_pct") else 1) + r.get("ganho_por_leque", 0) / s["recarga"]
    net = custo_s - ganho_s
    ganho_basico_s = r.get("regen_combate_s", 0) * (pl if r.get("regen_pct") else 1) + r.get("ganho_por_golpe_basico", 0) / p["interval"]
    if pots or net <= 0:
        frac_leque = 1.0
    else:
        # ciclo: gasta de 100% ate o custo com leque; recarrega ate o limiar so com basico
        lim = F["modo_automatico"]["sem_pocao_volta_ao_leque_em"]
        t_on = pl * lim / net; t_off = pl * lim / max(0.01, ganho_basico_s)
        frac_leque = t_on / (t_on + t_off)
    dps = frac_leque * (fan_dps + basic_dps * SP["basico_entre_leques"]) + (1 - frac_leque) * basic_dps
    kpm_dano = dps * 60 / mhp * SP["eficiencia_movimento"]
    oferta = SP["mobs"] * 60 / SP["renascimento_s"]
    kpm = min(kpm_dano, oferta)
    # dano recebido (sem regen em combate)
    atacando = SP["mobs_batendo_com_leque"] if frac_leque > 0.5 else SP["mobs_batendo_sem_leque"]
    mhit = sim.hitch(Ls*4 + 10, p["er"])
    taken = atacando * mdmg * (1 - sim.mitig(p["deff"], Ls)) * mhit / mint * (max(0.4, 1 - 0.04 * -dl) if dl < 0 else min(1.2, 1 + 0.02 * dl))
    if cls == "mutante": taken *= 0.85
    if cls == "demonio": taken -= one * hit / p["interval"] * 0.04
    # cultista paga o leque em HP: vira consumo de pocao de vida
    hp_s = taken + (custo_s if cls == "cultista" else 0)
    kill_heal = r.get("cura_por_abate_pct", 0) * p["hp"] * kpm / 60
    hp_s = max(0.0, hp_s - kill_heal)
    vp = POT["pocao_vida_p"]; rp = POT["pocao_recurso_p"]
    vida_min = hp_s * 60 / (vp["cura_pct"] * p["hp"] + vp.get("cura_fixa", 0))
    rec_min = (max(0, net) * 60 / (rp["recurso_pct"] * pl)) if (pots and r["tipo"] != "hp") else 0
    custo_pot = vida_min * vp["preco"] + rec_min * rp["preco"]
    xp = (10 + 5 * Ls) * kpm
    d = dl
    xmod = 1.2 if d >= 5 else (1 + 0.04 * d if d >= -3 else max(0.1, 1 - 0.15 * (-d - 3) - 0.12))
    xp *= xmod
    ouro = 3.5 * Ls * 0.55 * kpm
    return dict(kpm=kpm, xp=xp, ouro=ouro, vida=vida_min, rec=rec_min, custo=custo_pot, frac=frac_leque, cap=kpm_dano >= oferta)

if __name__ == "__main__":
    print("Spot padrao: %d mobs, renascimento %ds, %.1f alvos por leque. Jogador no nivel do spot." % (SP["mobs"], SP["renascimento_s"], SP["alvos_por_leque"]))
    print("Colunas: abates/min | XP/min | ouro/min | pocoes vida+recurso por min | custo pocoes/min (% do ouro) | min por nivel\n")
    for L in [5, 6, 7, 8, 9, 10]:
        need = P[L-1]["xp_para_proximo"]
        print(f"--- Spot nivel {L} (XP para o proximo nivel: {need}) ---")
        for cls in C:
            out = []
            for pots in (True, False):
                f = farm(cls, L, L, pots)
                out.append(f"{'com' if pots else 'sem'} pocao: {f['kpm']:4.1f}{'*' if f['cap'] else ' '} {f['xp']:5.0f} {f['ouro']:4.0f} {f['vida']:4.1f}+{f['rec']:4.1f} {f['custo']:4.0f} ({f['custo']/max(1,f['ouro'])*100:3.0f}%) {need/f['xp']:4.1f}m")
            print(f"  {cls:12} " + " | ".join(out))
    print("\n* = limitado pelo renascimento do spot (o jogador mata mais rapido do que os monstros voltam)")

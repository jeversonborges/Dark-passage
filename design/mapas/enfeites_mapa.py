# Espalha os enfeites (assets/ambiente/fontes/enfeites.py) nas salas de um mapa gerado, com as regras do Jefin:
# nada empilhado, cada sala com um motivo, espaço para andar, longe de portais, baús, spawns e da arena do chefe.
# Uso nos geradores: enfeitar(andar, PLANO, arena=(cx, cy, r)). PLANO = [(nome_da_sala, [ids...]), ...]
# (o andar precisa ter .salas, .livre(x, y), .prop(...), .objetos, .spawns, .props e .w/.h, como a classe Andar da cripta).
import math, random, zlib

# id -> (raio de bloqueio, decalque de chão, luz [r, g, b, raio] ou None)
VELA = [1, .55, .2, 3]
VALV = [1, .5, .16, 3]
INFO = {
    # matadouro
    "cepo_cutelo": (.5, 0, None), "balde_miudos": (.4, 0, None), "varal_linguica": (.8, 0, None), "cabide_avental": (.4, 0, None),
    "bandeja_visceras": (.4, 0, None), "caveira_boi": (0, 1, None), "pedra_amolar": (.5, 0, None), "balanca_gancho": (.5, 0, None),
    "caixote_ossos": (.4, 0, None), "faqueiro_parede": (.5, 0, None), "pernis_tripe": (.5, 0, None), "restos_carne_chao": (0, 1, None),
    # egito
    "mesa_oferendas": (.6, 0, VELA), "ushabtis": (.4, 0, None), "cesto_papiros": (.4, 0, None), "incensario_braco": (.4, 0, VELA),
    "vasos_alabastro": (.4, 0, None), "cabeca_farao": (.8, 0, None), "harpa_arco": (.4, 0, None), "cadeira_ebano": (.4, 0, None),
    "mumias_gato": (.4, 0, None), "lamparinas_chao": (0, 1, VELA), "escaravelho_coracao": (.5, 0, None), "modelo_barca": (.6, 0, None),
    # cripta
    "trombetas_caladas": (.4, 0, None), "relicario": (.4, 0, VELA), "candelabro_ferro": (.4, 0, VELA), "ex_votos": (.5, 0, VELA),
    "coroa_flores_secas": (.4, 0, None), "sino_rachado": (.6, 0, None), "atril_partituras": (.5, 0, None), "genuflexorio": (.4, 0, VELA),
    "ossuario_caixa": (.5, 0, None), "lacres_cera_chao": (0, 1, None), "raizes_ossos": (.7, 0, None), "cruz_ferro_tombada": (.4, 0, None),
    # torre de rádio
    "radio_votivo": (.5, 0, VALV), "pilha_fones": (.4, 0, VELA), "caixa_valvulas": (.4, 0, VALV), "fitas_rolo": (.5, 0, VALV),
    "microfone_caido": (.5, 0, VELA), "bancada_solda": (.8, 0, VALV), "totem_antena": (.4, 0, VALV), "cadeira_escuta": (.5, 0, VALV),
    "pilha_radios": (.5, 0, VALV), "circulo_giz_chao": (0, 1, VELA), "baldes_incendio": (.5, 0, None), "estante_pecas": (.5, 0, None),
}

def _salas(a):
    out = {}
    for s in a.salas:
        if isinstance(s, dict): out[s["nome"]] = s["ret"]
        else: out[s[0]] = list(s[1:5])
    return out

def enfeitar(a, plano, arena=None, seed=0, margem=1.2):
    rng = random.Random(zlib.crc32(f"enfeites{a.id}{seed}".encode()))
    salas = _salas(a)
    fixos = [tuple(o["pos"]) for o in a.objetos + a.spawns + a.npcs]
    postos = 0
    for nome, ids in plano:
        if nome not in salas: print("  enfeites: sala não achada", nome); continue
        x0, y0, x1, y1 = salas[nome]
        for k in ids:
            r, chao, luz = INFO.get(k, (.4, 0, None))
            melhor = None
            for _ in range(400):
                x = rng.uniform(x0 + margem, x1 + 1 - margem); y = rng.uniform(y0 + margem, y1 + 1 - margem)
                if not all(a.livre(int(x) + dx, int(y) + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)): continue
                if a.ter[int(y)][int(x)] in "rw": continue   # nada dentro de água ou lama
                if hasattr(a, "extra_blk") and (int(x), int(y)) in a.extra_blk: continue
                if any(math.dist((x, y), f) < 2.2 for f in fixos): continue
                if arena and math.dist((x, y), arena[:2]) < arena[2] + .5: continue
                d_props = min([math.dist((x, y), (p["x"], p["y"])) for p in a.props if not p.get("chao") and not p["k"].startswith(("parede", "grade_", "sujeira"))] or [99])
                if d_props < (1.6 if not chao else 1.0): continue
                # preferir o pé das paredes (sala respira no meio): distância até a parede mais próxima
                dw = min([abs(x - x0), abs(x1 + 1 - x), abs(y - y0), abs(y1 + 1 - y)])
                nota = abs(dw - 1.7) + rng.uniform(0, .6)
                if melhor is None or nota < melhor[0]: melhor = (nota, x, y)
            if not melhor: print("  enfeites: sem lugar para", k, "em", nome); continue
            _, x, y = melhor
            a.prop(k, x, y, bloqueia=r, chao=bool(chao), luz=luz); postos += 1
    print("  enfeites postos:", postos)
    return postos

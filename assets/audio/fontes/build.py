"""Gera todos os sons registrados e o manifesto assets/audio/audio.json.

Uso: python3 build.py [filtro ...] [--jobs N]
     filtro = prefixo de id (ex.: combate/ skills/anjo)
"""
import json
import os
import sys
import time
import importlib
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)  # assets/audio
MODULOS = ['sfx_combate', 'sfx_mundo', 'sfx_skills', 'sfx_monstros', 'sfx_chefes', 'sfx_andras', 'ambiente', 'ambiente_deserto', 'musica', 'musica_andras', 'musica_deserto']


def load():
    from registro import REG
    for m in MODULOS:
        if os.path.exists(os.path.join(HERE, m + '.py')):
            importlib.import_module(m)
    return REG


def pasta(id):
    if id.startswith('musica/') or id.startswith('ambiente/'):
        return id
    return 'sfx/' + id


def render(args):
    id, v = args
    import dsp
    from kit import finish
    from registro import REG, seed_of
    load()
    e = REG[id]
    dsp.seed(seed_of(id, v))
    t0 = time.time()
    try:
        x = e['fn'](v)
    except Exception as ex:
        import traceback
        return id, v, 'ERRO ' + traceback.format_exc().strip().splitlines()[-1] + ' @ ' + \
            [l for l in traceback.format_exc().splitlines() if 'line' in l][-1].strip(), 0, 0
    if e['loop']:
        x = dsp.to_stereo(x)
        if e['espaco']:
            # reverb circular: a cauda do fim volta para o comeco, o loop fica sem emenda
            n = len(x)
            r = dsp.reverb(x, e['espaco'], e['mix'], tail=True)
            out = r[:n].copy()
            k = len(r) - n
            while k > 0:
                seg = r[len(r) - k:len(r) - k + n]
                out[:len(seg)] += seg
                k -= len(seg)
            x = out
        # filtros/limitador tambem circulares: processa com 3 s do fim na frente e descarta
        pre = min(len(x) // 2, dsp.ns(3.0))
        x = dsp.master(dsp.bhp(np.concatenate([x[-pre:], x]), 25, 2), e['lufs'], e['peak'])[pre:]
    else:
        x = finish(x, e['lufs'], e['espaco'], e['mix'], e['peak'], e['tail'])
    nome = pasta(id) + (f'_{v + 1}' if e['var'] > 1 else '') + '.ogg'
    dsp.write(os.path.join(OUT, nome), x, 'ogg', 6 if e['bus'] == 'sfx' else 7)
    return id, v, nome, len(x) / dsp.SR, time.time() - t0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = 4
    for a in sys.argv[1:]:
        if a.startswith('--jobs='):
            jobs = int(a.split('=')[1])
    REG = load()
    tasks = [(id, v) for id, e in REG.items() for v in range(e['var'])
             if not args or any(id.startswith(f) for f in args)]
    print(f'{len(tasks)} arquivos')
    results = []
    with Pool(jobs) as p:
        for r in p.imap_unordered(render, tasks):
            print(f'  {r[2]:55s} {r[3]:6.2f}s  ({r[4]:.1f}s)', flush=True)
            if not r[2].startswith('ERRO'):
                results.append(r)
    # manifesto (mescla com o existente)
    mpath = os.path.join(OUT, 'audio.json')
    man = json.load(open(mpath)) if os.path.exists(mpath) else {}
    sons = man.get('sons', {})
    for id, v, nome, dur, _ in results:
        e = REG[id]
        s = sons.setdefault(id, {})
        s.update(desc=e['desc'], bus=e['bus'], loop=e['loop'], variacoes=e['var'])
        arqs = s.get('arquivos', [None] * e['var'])
        if len(arqs) != e['var']:
            arqs = [None] * e['var']
        arqs[v] = nome
        s['arquivos'] = arqs
        s['duracao_s'] = round(max(dur, s.get('duracao_s', 0) if s.get('variacoes') == e['var'] else 0), 2)
    man['sons'] = dict(sorted(sons.items()))
    json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

"""Registro de sons: cada gerador vira um ou mais arquivos em assets/audio/."""
import zlib

REG = {}


def som(id, var=1, lufs=-16, espaco=None, mix=0.2, loop=False, desc='', peak=-1.0, tail=True, bus='sfx'):
    """Registra um gerador. fn(v) devolve o sinal cru (mono ou estereo) da variacao v."""
    def deco(fn):
        REG[id] = dict(fn=fn, var=var, lufs=lufs, espaco=espaco, mix=mix, loop=loop, desc=desc,
                       peak=peak, tail=tail, bus=bus)
        return fn
    return deco


def seed_of(id, v):
    return zlib.crc32(f'{id}#{v}'.encode()) & 0x7fffffff

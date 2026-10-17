"""Avisa se o ícone do .exe não é o do jogo (compara as imagens do .ico com o conteúdo do exe)."""
import struct, sys
exe = open(sys.argv[1], "rb").read()
ico = open(sys.argv[2], "rb").read()
n = struct.unpack("<H", ico[4:6])[0]
achou = 0
for i in range(n):
    tam, off = struct.unpack("<II", ico[6 + 16 * i + 8:6 + 16 * i + 16])
    if ico[off:off + tam][:4096] in exe:
        achou += 1
print(f"ícone: {achou}/{n} imagens do icone.ico dentro do exe" + ("" if achou else " (AVISO: exe ficou com o ícone padrão)"))

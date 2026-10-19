# Referências e skills para as threads de Blender

Guia curto para quem modela, rigga ou anima no `tools/sprite-pipeline/`.

## 1. Antes de modelar: consulte

```python
import sys; sys.path.insert(0, "tools/sprite-pipeline")
from skills_lib import referencias, orcamento, citar
for r in referencias("anatomia_quadrupede"):
    print(citar(r))
print(orcamento("montaria"))   # (6000, 8000)
```

Ou `python3 tools/sprite-pipeline/skills_lib.py` para ver os temas e o total de referências.

Temas em `referencias/`: `anatomia_quadrupede`, `locomocao`, `materiais_foscos`, `rigging`, `lowpoly`, `armaduras`.

## 2. Ao usar uma referência, cite

No commit e no comentário do código, use a linha que `citar()` devolve, por exemplo:

    montarias: cavalo_guerra usa a régua de cernelha 1,5 m (majid/blender-game-skills@f0ef293, categories.md)

Se a fonte for upload do Jefin, cite como `upload do Jefin 2026-10-18`. Essas imagens não são versionadas.

## 3. Onde depositar referência nova

1. Jogue o arquivo em `referencias/inbox/` no formato `tema__nome.ext`.
2. Rode `python3 tools/sprite-pipeline/importar_referencias.py --fonte "de onde veio"`.
3. O script move o arquivo para a pasta do tema e atualiza o `index.json`. Arquivo sem tema fica na inbox e o script avisa.

Nunca coloque imagem com marca d'água ou de banco de imagens no repositório. Se for só para consulta, deixe fora e cite a fonte.

## 4. Orçamento de triângulos (low-poly)

| Tipo | Triângulos |
|---|---|
| montaria | 6 000 a 8 000 |
| chefe | 7 000 a 8 000 |
| monstro comum | 3 000 a 5 000 |
| NPC | 4 000 a 6 000 |
| arma | 1 200 a 2 000 |
| escudo | 1 500 a 2 000 |
| prop | 800 a 2 000 |

Conferir antes de exportar:

    /opt/bpy42/bin/python tools/sprite-pipeline/check_lowpoly.py -- arquivo.blend montaria

Sai com código 1 se passar do máximo ou se algum objeto estiver sem material.

## 5. Estilo: fosco, sujo, sem vitrine

- Rugosidade 0,6 a 0,9 para couro e pelo; metal enferrujado 0,5 a 0,7.
- Sem clearcoat, vidro ou transmissão. Essas técnicas dos repos de vitrine (Kevin, product-polish) não entram.
- Peça de armadura pesa 100% em um osso, para não esticar (EL4CTEO).
- Até 4 influências por vértice, normalizadas, pesos abaixo de 0,01 removidos.

## 6. Onde ficam os repositórios de referência

`tools/sprite-pipeline/vendor/`, com commit e licença em `vendor/SOURCES.md`. São cópias para consulta, não dependência de execução.

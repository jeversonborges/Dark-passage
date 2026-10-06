# Monta uma prévia da mochila em grade (estilo MU) com a arte de mochila_2x, para conferir encaixes.
import json, os
from PIL import Image, ImageDraw
PF = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
it = {i["id"]: i for i in json.load(open(f"{PF}/design/skills-itens/itens.json"))["itens"]}
C, COLS, ROWS = 60, 8, 8
def painel(lista, titulo):
    im = Image.new("RGB", (COLS*C + 40, ROWS*C + 70), (20, 17, 18)); d = ImageDraw.Draw(im)
    d.text((20, 18), titulo, fill=(211, 202, 183))
    ox, oy = 20, 50; occ = [[False]*COLS for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS): d.rectangle([ox+x*C, oy+y*C, ox+x*C+C-1, oy+y*C+C-1], fill=(30, 27, 28), outline=(58, 52, 56))
    for iid in lista:
        w, h = it[iid]["grade"]; ok = False
        for y in range(ROWS - h + 1):
            for x in range(COLS - w + 1):
                if all(not occ[y+j][x+i] for j in range(h) for i in range(w)):
                    for j in range(h):
                        for i in range(w): occ[y+j][x+i] = True
                    cor = {"lendario":(90,24,20),"raro":(80,62,24),"magico":(30,44,66)}.get(it[iid].get("raridade"), (40,36,38))
                    d.rectangle([ox+x*C+1, oy+y*C+1, ox+(x+w)*C-2, oy+(y+h)*C-2], fill=cor)
                    a = Image.open(f"{PF}/assets/icones/itens/mochila_2x/{iid}.png"); im.paste(a, (ox+x*C, oy+y*C), a); ok = True; break
            if ok: break
    return im
a = painel(["foice_serrilhada","escopeta_cano_duplo","lanca_procissao","cajado_vertebras","machado_placa_transito","placas_sino_peito","besta_sucata","escudo_porta_capela",
            "espada_vigilia_rachada","pocao_vida_p","pocao_vida_m","pocao_recurso_p","adaga_ritual_cega","couro_sobrevivente_cabeca","lagrima_anjo","fragmento_alma","chave_bau_ferro","anel_prego_caixao","osso","sucata"], "Mochila: bases")
b = painel(["estandarte_legiao","bacula_femur","dragonas_general","machado_bonde","gancho_capataz","halo_incandescente","veu_carpideira","espada_escudeiro","adaga_chaga",
            "pena_zacarias","estilhaco_lacre","diapasao_reverso","selo_madre","lenco_cardo","livro_obitos","bocal_trombeta","hostia_negra","tonico_graxa","lacre_carne","lacre_lagrimas"], "Mochila: itens com nome")
out = Image.new("RGB", (a.width*2 + 20, a.height), (14, 12, 13)); out.paste(a, (0, 0)); out.paste(b, (a.width + 20, 0))
out.save(f"{PF}/assets/icones/previa_mochila.png")

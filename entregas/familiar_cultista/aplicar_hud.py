# Aplica a barra do pet no hud.gd atual: python3 aplicar_hud.py <hud.gd de origem> <saida> <hud.gd com a barra (novo/hud.gd)>
import sys
src, out, ref = sys.argv[1:4]
s = open(src).read(); r = open(ref).read()
a = r.index("# =================================================================== barra do pet (Cultista, 0.9.3)")
b = r.index("## Selo de latão no canto do slot")
bloco = r[a:b]
def R(x, y):
    global s
    assert s.count(x) == 1, x
    s = s.replace(x, y)
if "barra do pet (Cultista" not in s:
    R("var pressionado := {}         # slot -> tempo do flash\n",
      "var pressionado := {}         # slot -> tempo do flash\nvar pet_ui: Control           # barra do pet do Cultista (retrato, vida e 5 comandos), em cima da barra de skills\nvar hover_pet := -1\n")
    R("\t_montar_barra()\n\t_montar_topo()", "\t_montar_barra()\n\t_montar_pet()\n\t_montar_topo()")
    R("## Selo de latão no canto do slot", bloco + "## Selo de latão no canto do slot")
    R("\tbarra.queue_redraw(); topo_esq.queue_redraw()", "\t_posicionar_pet()\n\tif pet_ui.visible: pet_ui.queue_redraw()\n\tbarra.queue_redraw(); topo_esq.queue_redraw()")
open(out, "w").write(s)

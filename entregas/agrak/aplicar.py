#!/usr/bin/env python3
"""O Agrak: copia os scripts novos e liga os ganchos no game/ (pode rodar de novo: não duplica nada).

Uso (da raiz do repositório):  python3 entregas/agrak/aplicar.py [pasta_do_game]
Padrão: game/ ao lado deste repositório (no PC do Jefin, E:\\darkpassage\\Dark-passage\\game).
"""
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, '..', '..', 'game'))

NOVOS = {
    'scripts/sim/agrak_ctl.gd': 'scripts/sim/agrak_ctl.gd',
    'scripts/net/agrak.gd': 'scripts/net/agrak.gd',
    'scripts/client/agrak_cena.gd': 'scripts/client/agrak_cena.gd',
    'tools/teste_agrak.gd': 'tools/teste_agrak.gd',
}

# (arquivo, âncora que já existe, texto novo que entra logo depois da âncora, marca para não duplicar)
GANCHOS = [
    ('scripts/sim/world_sim.gd',
     '\tif mapa.has("chefe"): chefe = ChefeCtl.new(self, mapa["chefe"])\n',
     '\telif mapa.has("agrak"): chefe = AgrakCtl.new(self)   # O Agrak (evento PvP): entregas/agrak\n',
     'AgrakCtl.new(self)'),
    ('scripts/net/sincro.gd',
     '"faccao", "alvo", "dono", "vel", "res"',
     ', "lado_forcado"',
     '"lado_forcado"'),
    ('scripts/client/game.gd',
     'const MiraControle := preload("res://scripts/client/mira_controle.gd")\n',
     'const AgrakCena := preload("res://scripts/client/agrak_cena.gd")   # O Agrak: apresentação ao vivo (entregas/agrak)\n',
     'const AgrakCena'),
    ('scripts/client/game.gd',
     'var mira_ctl: Node2D',
     None,   # linha inteira: entra depois do fim da linha da âncora
     'var agrak_cena'),
    ('scripts/client/game.gd',
     '\tchefe_view = null\n\tmusica_chefe = false\n\tzona_atual = ""\n',
     '\tif agrak_cena != null: agrak_cena.limpar(); agrak_cena = null\n',
     'agrak_cena.limpar()'),
    ('scripts/client/game.gd',
     '\t_cores_minimapa()\n',
     '\tif mapa.has("agrak"):\n\t\tagrak_cena = AgrakCena.new(); add_child(agrak_cena); agrak_cena.iniciar(self)\n',
     'agrak_cena.iniciar(self)'),
    ('scripts/client/game.gd',
     'func _ev(tipo: String, d: Dictionary) -> void:\n',
     '\tif agrak_cena != null: agrak_cena.ev(tipo, d)\n',
     'agrak_cena.ev(tipo, d)'),
    ('scripts/sim/missoes.gd',
     '\t\tif a.has("definir_flag"): jog.flags[a["definir_flag"]] = true\n',
     '\t\tif a.has("agrak"): sim.emitir_a(jog, "agrak_pedido", {"a": a["agrak"]})   # Caim e Abel: entrar ou sair da lista do Agrak\n',
     '"agrak_pedido", {"a": a["agrak"]}'),
    ('scripts/net/servidor.gd',
     'var troca = Troca.new(self)',
     None,
     'var agrak: Node'),
    ('scripts/net/servidor.gd',
     'func _ready() -> void:\n\t_carregar_contas()\n',
     '\tadd_child(agrak)\n',
     'add_child(agrak)'),
    ('scripts/net/servidor.gd',
     '\tif tipo == "mapa": return\n',
     '\tif tipo == "agrak_pedido":   # Cartaz do Agrak e Caim e Abel: a lista fica no servidor\n'
     '\t\tagrak.pedido(por_jog.get(int(d.get("_para", -1)), -1), str(d.get("a", "inscrever"))); return\n',
     'agrak.pedido('),
    ('scripts/net/servidor.gd',
     '\tif s["jog"] != null:\n\t\t_salvar_jog(peer)\n',
     None,
     'agrak.saiu(peer)'),
    ('scripts/defs.gd',
     '\t\tif not CHEFES.has(k): CHEFES[k] = ex["chefes"][k]\n',
     '\t# O Agrak (entregas/agrak): Caim e Abel, o Saulo e a Banca de Sangue (sync.sh copia para pvp/agrak_npcs.json)\n'
     '\tvar pv: Dictionary = ler(DESIGN + "pvp/agrak_npcs.json")\n'
     '\tfor n in pv.get("npcs", []):\n\t\tif not NPCS.has(n["id"]): NPCS[n["id"]] = n\n'
     '\tfor d in pv.get("dialogos", []):\n\t\tif not DIALOGOS.has(d["id"]): DIALOGOS[d["id"]] = d\n'
     '\tfor l in pv.get("lojas", []):\n\t\tif not LOJAS.has(l["id"]): LOJAS[l["id"]] = l\n'
     '\tfor o in pv.get("objetos", []):\n\t\tif not OBJETOS.has(o["id"]): OBJETOS[o["id"]] = o\n',
     'pvp/agrak_npcs.json'),
]

# linhas inteiras (texto None acima): entram depois da linha que tem a âncora
LINHAS = {
    'var agrak_cena': 'var agrak_cena: Node = null  # O Agrak (mapa com bloco "agrak"): falas, faixa, plateia, portões, Anel do Amargo\n',
    'var agrak: Node': 'var agrak: Node = preload("res://scripts/net/agrak.gd").new()   # O Agrak: agenda, inscrição, levar e trazer (entregas/agrak)\n',
}


def main():
    if not os.path.isdir(os.path.join(GAME, 'scripts')):
        sys.exit('não achei o game/ em ' + GAME)
    for de, para in NOVOS.items():
        shutil.copy2(os.path.join(AQUI, de), os.path.join(GAME, para))
        print('copiado', para)
    falhas = 0
    for arq, ancora, novo, marca in GANCHOS:
        p = os.path.join(GAME, arq)
        s = open(p, encoding='utf-8').read()
        if marca in s:
            print('já tinha', arq, '·', marca)
            continue
        if ancora not in s:
            print('FALTA A ÂNCORA em', arq, ':', ancora.strip()[:70]); falhas += 1
            continue
        i = s.index(ancora) + len(ancora)
        if marca == 'agrak.saiu(peer)':   # antes de salvar quem desconectou
            i = s.index(ancora) + len('\tif s["jog"] != null:\n')
            novo = '\t\tagrak.saiu(peer)   # no meio do Agrak: salva onde ele estava antes\n'
        elif novo is None:   # linha inteira
            i = s.index('\n', s.index(ancora)) + 1
            novo = LINHAS[marca]
        s = s[:i] + novo + s[i:]
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
        print('ligado', arq, '·', marca)
    print('OK' if falhas == 0 else 'FALHOU: %d âncora(s) não encontrada(s)' % falhas)
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()

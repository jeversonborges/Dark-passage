"""O Agrak, o Grande Coliseu: o estádio de São Lázaro que a areia engoliu (mapa de instância do evento PvP).

Gera ../agrak/agrak.json no MESMO formato de game/data/mapas/*.json (usa a classe Andar de ../cripta/gerar.py)
e a planta ../agrak/planta_agrak.png. Design do evento: design/pvp/agrak/ (coliseu_e_narrador.md, dados.json).
Kit de arte: assets/ambiente/previa/coliseu/LEIAME_kit_agrak.md (Cenário, 16/10).

Tela: +X desce para a direita, +Y sobe para a direita. As bordas "de trás" do fosso (x = X0-1 e y = Y1+1) ficam
no alto da tela: muro de 3 m, faixas, portões e duas fileiras de arquibancada com a plateia. As bordas "da frente"
(y = Y0-1 e x = X1+1) ficam embaixo: mureta baixa e a arquibancada desabada em rampa de areia, para a câmera ver a luta.
Pontos cardeais do design: norte = alto da tela (Portão dos Leões), leste = direita (Portão do Gigante),
sul = embaixo (Portão dos Gladiadores), oeste = esquerda (placar e Camarote dos Derrotados).
Uso: python3 agrak.py
"""
import json, math, os, sys, zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "..", "agrak")
sys.path.insert(0, os.path.join(AQUI, "..", "cripta"))
import gerar as G

FOGO = [1, .55, .22]; OURO = [1, .78, .35]

W, H = 52, 48
X0, X1, Y0, Y1 = 13, 42, 12, 33            # o fosso: 30 x 22 tiles
CX, CY = (X0 + X1 + 1) / 2, (Y0 + Y1 + 1) / 2


def main():
    a = G.Andar("agrak", "O Agrak, o Grande Coliseu", W, H, "a", "muro_fosso",
                {"id": "agrak", "nome": "O Agrak", "seguro": False, "nivel": [25, 400], "pvp_evento": True,
                 "musica": "musica/cripta", "ambiente": "ambiente/noite_vento"})
    a.sala(X0, Y0, X1, Y1, nome="O Fosso")

    # ---- portões (células de muro que abrem): leões no muro de trás à esquerda, gigante no de trás à direita,
    # gladiadores na mureta da frente à esquerda. Cada um dá num túnel/curral fora do fosso.
    gy = int(CY) - 1                                    # Portão dos Leões: x = X0-1, y = gy, gy+1  (2x1 ao longo de Y)
    gx = int(CX) - 1                                    # Portão do Gigante: y = Y1+1, x = gx-1..gx+1 (3x1 ao longo de X)
    sx = int(CX) - 6                                    # Portão dos Gladiadores: y = Y0-1, x = sx, sx+1
    portoes = {
        "portao_leoes": [[X0 - 1, gy], [X0 - 1, gy + 1]],
        "portao_gigante": [[gx - 1, Y1 + 1], [gx, Y1 + 1], [gx + 1, Y1 + 1]],
        "portao_gladiadores": [[sx, Y0 - 1], [sx + 1, Y0 - 1]],
    }
    # currais atrás dos portões (onde os chefes esperam) e o corredor dos gladiadores com a ermida do Saulo
    a.sala(X0 - 8, gy - 3, X0 - 4, gy + 4, piso="n", nome="Jaulas dos Leões")
    a.corredor(X0 - 3, gy, X0 - 2, gy + 1, piso="n")
    a.sala(gx - 3, Y1 + 4, gx + 3, Y1 + 8, piso="n", nome="Curral do Gigante")
    a.corredor(gx - 1, Y1 + 2, gx + 1, Y1 + 3, piso="n")
    a.sala(sx - 5, Y0 - 9, sx + 2, Y0 - 4, piso="c", nome="Corredor dos Gladiadores")
    a.corredor(sx, Y0 - 3, sx + 1, Y0 - 2, piso="c")
    # Camarote dos Derrotados: plataforma atrás da arquibancada oeste, ao lado do placar (zona segura, vista da luta)
    cam = (X0 - 9, Y0 + 1, X0 - 5, Y0 + 6)
    a.sala(*cam, piso="c", nome="Camarote dos Derrotados")
    for cel in sum(portoes.values(), []):
        a.ter[cel[1]][cel[0]] = "n"; a.blk[cel[1]][cel[0]] = False

    # ---- chão do fosso: areia batida escura, linhas de cal do campo antigo, Círculo de Ferro no centro
    a.pisar(X0, Y0, X1, Y1, "t")
    a.prop("circulo_ferro", CX, CY, chao=True)
    for y in range(Y0 + 1, Y1):                         # linha do meio-campo, apagada aos pedaços
        if abs(y + .5 - CY) > 3.8 and zlib.crc32(f"cal{y}".encode()) % 4: a.prop("linha_cal_b", CX, y + .5, chao=True)
    for (x, y) in [(X0 + 4, CY - 3), (X0 + 4, CY + 3), (X1 - 4, CY - 3), (X1 - 4, CY + 3)]:   # restos da grande área
        a.prop("linha_cal_meio", x, y, chao=True)
    a.espalhar(["poca_sangue", "poca_sangue_rastro", "ossos_espalhados"], 9, (X0 + 1, Y0 + 1, X1 - 1, Y1 - 1), dist=4)
    for (x, y) in [(X0 + 5.5, Y0 + 4.5), (X0 + 5.5, Y1 - 3.5), (X1 - 4.5, Y0 + 4.5), (X1 - 4.5, Y1 - 3.5)]:
        a.prop("pilar_entulho", x, y, bloqueia=1.0)       # cobertura contra o Bote dos leões, longe do centro (Pião)
        a.extra_blk |= {(int(x) + dx, int(y) + dy) for dx in (-1, 0) for dy in (-1, 0)}

    # ---- muros (um tile por célula de borda); portões no lugar do muro
    porta = {tuple(c) for c in sum(portoes.values(), [])}
    fosso = lambda x, y: X0 <= x <= X1 and Y0 <= y <= Y1
    for x in range(X0 - 1, X1 + 2):
        for y in range(Y0 - 1, Y1 + 2):
            if fosso(x, y) or (x, y) in porta: continue
            tras_b = x == X0 - 1 and Y0 <= y <= Y1
            tras_a = y == Y1 + 1 and X0 <= x <= X1
            fre_b = x == X1 + 1 and Y0 <= y <= Y1
            fre_a = y == Y0 - 1 and X0 <= x <= X1
            if tras_b: a.prop("muro_fosso_b", x + .5, y + .5)
            elif tras_a: a.prop("muro_fosso_a", x + .5, y + .5)
            elif fre_b: a.prop("muro_fosso_frente_b", x + .5, y + .5)
            elif fre_a: a.prop("muro_fosso_frente_a", x + .5, y + .5)
            elif (x, y) == (X0 - 1, Y1 + 1) or (x, y) == (X1 + 1, Y1 + 1) or (x, y) == (X0 - 1, Y0 - 1):
                a.prop("muro_fosso_canto", x + .5, y + .5)
            elif (x, y) == (X1 + 1, Y0 - 1): a.prop("muro_fosso_frente_canto", x + .5, y + .5)
    a.prop("portao_grade_agrak_b", X0 - .5, gy + 1.0, portao="portao_leoes")
    a.prop("portao_gigante_a", gx + .5, Y1 + 1.5, portao="portao_gigante")
    a.prop("portao_grade_agrak_a", sx + 1.0, Y0 - .5, portao="portao_gladiadores")
    # faixas dos campeões na face do muro de trás, entre os portões
    for i, y in enumerate([Y0 + 3, Y0 + 8, Y1 - 6, Y1 - 1]):
        if abs(y - gy) > 2: a.prop(["faixa_campeao_b", "faixa_campeao_2_b", "faixa_campeao_3_b"][i % 3], X0 - .5, y + .5)
    for i, x in enumerate([X0 + 2, X0 + 7, X1 - 8, X1 - 3]):
        if abs(x - gx) > 3: a.prop(["faixa_campeao_2_a", "faixa_campeao_3_a", "faixa_campeao_a"][i % 3], x + .5, Y1 + 1.5)

    # ---- arquibancada (duas fileiras atrás do muro de trás) com a plateia por cima; desabada na frente
    ocupado = {(x, y) for y in range(H) for x in range(W) if not a.blk[y][x]}
    perto_de_sala = lambda x, y: any((x + dx, y + dy) in ocupado for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    def degrau(k, x, y, o):
        if perto_de_sala(x, y): return
        v = "_v2" if zlib.crc32(f"arq{x},{y}".encode()) % 4 == 0 else ""
        a.prop(f"arquibancada_agrak{v}_{o}", x + .5, y + .5)
        pl = "abc"[zlib.crc32(f"pl{x},{y}".encode()) % 3]
        a.prop(f"plateia_{pl}_0_{o}", x + .5, y + .5, plateia=1)    # a Prévia anima 0-1-0-1 (e 2-3-3-2 na morte)
    for fila in (2, 3):
        for y in range(Y0 - 1, Y1 + 2): degrau("b", X0 - fila, y, "b")
        for x in range(X0 - 1, X1 + 2): degrau("a", x, Y1 + fila, "a")
    # a arquibancada da frente desabou e foi levada pela areia: só a mureta baixa, a câmera vê a luta inteira

    # ---- currais e portões de dentro
    for i, (dx, dy) in enumerate([(-6.5, -1.5), (-6.5, 1.0), (-6.5, 3.5)]):
        a.prop("jaula_leao", X0 + dx, gy + dy, bloqueia=1.0, jaula=["leao_sansao", "leao_dalila", "leao_nabucodonosor"][i])
    a.prop("guincho_corrente", gx - 2.0, Y1 + 7.0, bloqueia=1.0)
    a.prop("tonel_fogo", gx + 2.5, Y1 + 5.5, bloqueia=.4, luz=FOGO + [5])
    a.prop("tonel_fogo", X0 - 5, gy - 2.5, bloqueia=.4, luz=FOGO + [5])

    # ---- placar com o camarote do ogro (Caim e Abel) e a Ermida do Saulo
    a.prop("placar_camarote", X0 - 7.0, Y0 + 9.5, bloqueia=1.0, luz=FOGO + [6])
    a.prop("ermida_saulo", sx - 3.0, Y0 - 7.5, bloqueia=1.0)
    a.luzes.append([sx - 3.0, Y0 - 8.3] + OURO + [4])
    a.prop("braseiro_holofote", cam[0] + .5, cam[1] + .5, luz=FOGO + [5])
    a.npcs.append({"id": "saulo", "pos": [sx - 1.5, Y0 - 6.5]})
    a.npcs.append({"id": "caim_abel", "pos": [X0 - 7.0, Y0 + 7.5]})

    # ---- braseiros-holofote no alto do muro de trás, a cada ~6 tiles, e nos dois cantos da frente
    for y in range(Y0 + 2, Y1, 6):
        if abs(y - gy) > 2: a.prop("braseiro_holofote", X0 - 1.5, y + .5, luz=FOGO + [7])
    for x in range(X0 + 3, X1, 6):
        if abs(x - gx) > 3: a.prop("braseiro_holofote", x + .5, Y1 + 1.8, luz=FOGO + [7])
    for (x, y) in [(X0 + .5, Y0 - 2.5), (X1 + 2.5, Y1 + .5)]:
        a.prop("braseiro_holofote", x, y, luz=FOGO + [7])

    a.objetos.append({"kind": "portal", "pos": [sx - 3.5, Y0 - 5.0], "para": "area_inicial", "chegada": None,
                      "nome": "Sair do Agrak (volta para onde você estava)", "visual": "portal_dungeon", "volta": True})
    m = a.exportar(ceu={"escuro": 0.3, "cor": [0.92, 0.84, 0.72], "neblina": [0.14, 0.1, 0.07]},
                   spawn=[sx + 1.0, Y0 - 3.0])
    m["agrak"] = {
        "centro": [CX, CY], "raio_circulo": 3.5, "fosso": [X0, Y0, X1, Y1], "anel_raio_max": 13,
        "portoes": {k: {"celulas": v, "fechado": True} for k, v in portoes.items()},
        "chefes_nascem": {"portao_leoes": [[X0 - 6.0, gy - 1.0], [X0 - 6.0, gy + 1.0], [X0 - 6.0, gy + 3.0]],
                          "portao_gigante": [[gx + .5, Y1 + 6.0]]},
        "entrada_fosso": [sx + 1.0, Y0 + 1.5],
        "camarote_derrotados": {"ret": list(cam), "pos": [cam[0] + 2.5, cam[1] + 3.0]},
        "seguro": ["Corredor dos Gladiadores", "Camarote dos Derrotados"],
        "plateia": "props com plateia=1: animar 0-1-0-1 a ~4 fps; morte_pvp ou morte de chefe: 2-3-3-2",
    }
    m["sem_penalidade"] = True
    m["exterior"] = True
    os.makedirs(SAIDA, exist_ok=True)
    json.dump(m, open(os.path.join(SAIDA, "agrak.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    try: os.remove(os.path.join(os.path.dirname(G.__file__), "agrak.json"))   # Andar.exportar grava ao lado do gerar.py
    except OSError: pass
    G.planta(m, os.path.join(SAIDA, "planta_agrak.png"), "O Agrak · o Grande Coliseu · evento PvP nv 25+")
    return m


if __name__ == "__main__":
    main()

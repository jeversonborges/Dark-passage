# Fonte dos dados de skills do DARK PASSAGE. Gera ../skills.json (rode: python3 gerar_json.py)
# TODOS os números de dano, custo e recarga são PROVISÓRIOS: o balanceamento final é da thread "Design do combate".

RECURSOS = {
  "anjo":        {"nome": "Graça",          "max": 100, "regen": "+4 por cura feita, +2 por golpe acertado; não regenera parado"},
  "cultista":    {"nome": "Sangue",         "max": "HP", "regen": "Custa o próprio HP. Ao matar: recupera 6% do HP máximo"},
  "mutante":     {"nome": "Fúria",          "max": 100, "regen": "+1 por 1% de HP perdido; cai 5/s fora de combate"},
  "demonio":     {"nome": "Brasa Infernal", "max": 100, "regen": "+3 por golpe; acima de 100 queima 2% do HP por segundo até gastar"},
  "humano":      {"nome": "Fôlego",         "max": 100, "regen": "+8/s; munição é item separado (balas, virotes, cartuchos)"},
  "tecnomancer": {"nome": "Carga",          "max": 120, "regen": "+3/s sempre; módulos aumentam o máximo"},
}

# tipo: ativa | area | buff | debuff | invocacao | passiva | suprema
# elemento: fisico | sagrado | sangue | fogo | veneno | eletrico | sombra
# dano: pct_arma = % do dano da arma; base = dano fixo somado; escala = atributo que soma dano
S = []
def sk(**k): S.append(k)

# ---------------- ANJO ----------------
sk(id="anjo_lamina_veredito", classe="anjo", nome="Lâmina do Veredito", tipo="ativa", nivel=1,
   custo=0, recarga=0.0, conjuracao=0.0, alcance=1.5, area=0, duracao=0, elemento="sagrado", escala=["ESP","FOR"],
   dano={"pct_arma":120,"base":8}, efeitos=["+15% de dano em Mutantes", "gera 2 de Graça ao acertar"],
   descricao="Corte de cima para baixo com a lâmina benta. O metal chia ao tocar carne contaminada.",
   fx="rastro de luz dourada em arco + faíscas brancas no impacto", som="lâmina pesada + coro curto abafado")
sk(id="anjo_toque_graca", classe="anjo", nome="Toque de Graça", tipo="ativa", nivel=3,
   custo=20, recarga=4.0, conjuracao=0.6, alcance=6, area=0, duracao=0, elemento="sagrado", escala=["ESP"],
   cura={"base":40,"pct_esp":180}, efeitos=["cura um aliado (ou a si mesmo)", "remove 1 sangramento"],
   descricao="A mão enfaixada pousa na ferida e a costura com fio de luz.",
   fx="partículas douradas subindo do alvo + halo pulsando no Anjo", som="sino pequeno")
sk(id="anjo_asas_ascensao", classe="anjo", nome="Asas da Ascensão", tipo="ativa", nivel=8,
   custo=25, recarga=12.0, conjuracao=0.0, alcance=5, area=0, duracao=0.4, elemento="sagrado", escala=[],
   efeitos=["salto/voo curto até 5 tiles", "atravessa inimigos e obstáculos baixos", "invulnerável durante o voo"],
   descricao="Duas batidas das asas sujas e o Anjo some numa nuvem de penas.",
   fx="explosão de penas cinza na saída e na chegada", som="bater de asas pesado")
sk(id="anjo_halo_ardente", classe="anjo", nome="Halo Ardente", tipo="area", nivel=15,
   custo=40, recarga=18.0, conjuracao=0.8, alcance=0, area=3.5, duracao=2.0, elemento="sagrado", escala=["ESP"],
   dano={"pct_arma":60,"base":20}, cura={"base":30,"pct_esp":90},
   efeitos=["cega inimigos no raio por 2s (erram 50% dos ataques)", "cura aliados no raio"],
   descricao="O halo de ferro se abre num anel de luz que queima os olhos de quem não foi escolhido.",
   fx="anel de luz expandindo no chão + flash branco", som="acorde de órgão")
sk(id="anjo_sentenca", classe="anjo", nome="Sentença", tipo="debuff", nivel=22,
   custo=30, recarga=20.0, conjuracao=0.3, alcance=7, area=0, duracao=8.0, elemento="sagrado", escala=["ESP"],
   efeitos=["marca um alvo por 8s", "todo dano contra o alvo +15%", "o alvo fica visível mesmo invisível"],
   descricao="Um selo de lacre vermelho aparece sobre a cabeça do condenado.",
   fx="selo de cera vermelha flutuando sobre o alvo", som="carimbo / martelo de juiz")
sk(id="anjo_trombeta_juizo", classe="anjo", nome="Trombeta do Juízo", tipo="suprema", nivel=400,
   custo=100, recarga=180.0, conjuracao=1.2, alcance=0, area=8, duracao=5.0, elemento="sagrado", escala=["ESP"],
   efeitos=["aliados no raio não podem morrer por 5s (HP mínimo 1)", "requer Estágio 3 (Arcanjo do Juízo)"],
   descricao="O Anjo toca a trombeta partida. Por cinco segundos, a morte não tem permissão de entrar.",
   fx="pilar de luz + trombeta fantasma no céu + ondas douradas", som="trombeta longa distorcida")

# ---------------- CULTISTA ----------------
sk(id="cultista_sangria", classe="cultista", nome="Sangria", tipo="ativa", nivel=1,
   custo="3% HP", recarga=0.8, conjuracao=0.4, alcance=7, area=0, duracao=6.0, elemento="sangue", escala=["ESP"],
   dano={"pct_arma":70,"base":10}, efeitos=["sangramento: 12% do dano inicial por segundo por 6s", "acumula até 3x"],
   descricao="Uma gota do próprio sangue vira uma lâmina vermelha que corta e não estanca.",
   fx="projétil líquido vermelho escuro + respingo", som="chiado úmido")
sk(id="cultista_pacto_rubro", classe="cultista", nome="Pacto Rubro", tipo="buff", nivel=5,
   custo="15% HP", recarga=30.0, conjuracao=0.5, alcance=0, area=0, duracao=12.0, elemento="sangue", escala=["ESP"],
   efeitos=["+30% de dano mágico por 12s", "custos de Sangue -20% durante o pacto"],
   descricao="Corta a palma e assina no ar. O livro acorrentado bebe primeiro.",
   fx="runas vermelhas girando em volta do corpo + lentes da máscara acendem", som="sussurros em coro")
sk(id="cultista_servo_carne", classe="cultista", nome="Servo de Carne", tipo="invocacao", nivel=10,
   custo="10% HP", recarga=25.0, conjuracao=1.5, alcance=3, area=0, duracao=30.0, elemento="sombra", escala=["ESP","VIT"],
   invocacao={"hp_pct_do_dono":60,"dano_pct_arma":40,"maximo":1},
   efeitos=["invoca um zumbi costurado por 30s", "o servo provoca inimigos que ele golpeia"],
   descricao="A terra cospe pedaços que se costuram sozinhos num corpo obediente.",
   fx="poça de sangue que borbulha e ergue o zumbi", som="carne e ossos estalando")
sk(id="cultista_chuva_cinzas", classe="cultista", nome="Chuva de Cinzas", tipo="area", nivel=16,
   custo="8% HP", recarga=14.0, conjuracao=1.0, alcance=8, area=3, duracao=6.0, elemento="sombra", escala=["ESP"],
   dano={"pct_arma":25,"base":6,"por_segundo":True}, efeitos=["inimigos na área recebem -40% de cura", "lentidão de 15%"],
   descricao="Cinzas de cidades queimadas caem do nada e grudam na pele como piche.",
   fx="cinzas cinza-escuro caindo em coluna + brasas pequenas", som="vento seco")
sk(id="cultista_profecia_sombria", classe="cultista", nome="Profecia Sombria", tipo="debuff", nivel=24,
   custo="12% HP", recarga=40.0, conjuracao=0.6, alcance=7, area=0, duracao=10.0, elemento="sombra", escala=["ESP"],
   efeitos=["marca por 10s", "se o alvo ficar abaixo de 10% do HP, morre na hora", "em chefes: dano extra igual a 8% do HP perdido"],
   descricao="O Cultista lê em voz alta a data da morte do alvo. Às vezes ela é hoje.",
   fx="olho preto com íris vermelha sobre o alvo; quando executa, o corpo vira cinza", som="voz sussurrando o nome")
sk(id="cultista_setimo_selo", classe="cultista", nome="Sétimo Selo", tipo="suprema", nivel=400,
   custo="35% HP", recarga=180.0, conjuracao=3.0, alcance=8, area=6, duracao=0, elemento="sangue", escala=["ESP"],
   dano={"pct_arma":900,"base":200}, efeitos=["canaliza 3s (interrompível)", "dano massivo em área ao terminar", "requer Estágio 3 (Profeta do Fim)"],
   descricao="Sete selos de cera se rompem no chão. O sétimo abre um olho.",
   fx="círculo ritual com 7 selos acendendo um por um + coluna de sangue", som="coro grave crescendo até o estouro")

# ---------------- MUTANTE ----------------
sk(id="mutante_golpe_purulento", classe="mutante", nome="Golpe Purulento", tipo="ativa", nivel=1,
   custo=0, recarga=3.0, conjuracao=0.3, alcance=1.5, area=0, duracao=6.0, elemento="veneno", escala=["FOR","VIT"],
   dano={"pct_arma":150,"base":10}, efeitos=["veneno: 6% do dano por segundo por 6s", "gera 10 de Fúria"],
   descricao="O braço deformado desce como um martelo. As pústulas estouram junto.",
   fx="respingo verde ácido + nuvem tóxica pequena", som="impacto úmido pesado")
sk(id="mutante_carapaca", classe="mutante", nome="Carapaça", tipo="buff", nivel=5,
   custo=30, recarga=20.0, conjuracao=0.0, alcance=0, area=0, duracao=8.0, elemento="fisico", escala=["VIT"],
   efeitos=["-35% de dano recebido por 8s", "imune a empurrão durante o efeito"],
   descricao="A pele endurece em placas de crosta, como casca de ferida velha.",
   fx="placas cinza-esverdeadas cobrindo o corpo + rachaduras", som="estalo de couro secando")
sk(id="mutante_rugido_praga", classe="mutante", nome="Rugido da Praga", tipo="area", nivel=10,
   custo=15, recarga=12.0, conjuracao=0.4, alcance=0, area=4, duracao=4.0, elemento="veneno", escala=["VIT"],
   efeitos=["provoca (taunt) inimigos no raio por 4s", "-10% de dano dos provocados"],
   descricao="Um urro pelo respirador que espalha esporos e ódio.",
   fx="onda de esporos verde ácido em anel", som="rugido animal com chiado de filtro")
sk(id="mutante_regeneracao_profana", classe="mutante", nome="Regeneração Profana", tipo="passiva", nivel=12,
   custo=0, recarga=0, conjuracao=0, alcance=0, area=0, duracao=0, elemento="veneno", escala=["VIT"],
   efeitos=["fora de combate: 3% do HP por segundo", "ao matar: recupera 5% do HP"],
   descricao="A carne fecha sozinha. Nem sempre no formato certo.",
   fx="bolhas verdes discretas nas feridas", som="nenhum")
sk(id="mutante_investida_bestial", classe="mutante", nome="Investida Bestial", tipo="ativa", nivel=18,
   custo=20, recarga=10.0, conjuracao=0.0, alcance=6, area=0, duracao=1.5, elemento="fisico", escala=["FOR"],
   dano={"pct_arma":110,"base":15}, efeitos=["avança até 6 tiles", "derruba o alvo por 1.5s", "atropela inimigos no caminho (50% do dano)"],
   descricao="Abaixa a cabeça e corre como um touro doente.",
   fx="rastro de poeira + tremor de tela no impacto", som="passos pesados + impacto")
sk(id="mutante_forma_besta", classe="mutante", nome="Forma da Besta", tipo="suprema", nivel=400,
   custo=100, recarga=180.0, conjuracao=1.0, alcance=0, area=0, duracao=20.0, elemento="veneno", escala=["VIT","FOR"],
   efeitos=["vira criatura gigante por 20s", "+60% HP máximo, +40% dano, ataques em área", "requer Estágio 3 (Besta do Apocalipse)"],
   descricao="O corpo rasga as próprias roupas e cresce até o que a praga sempre quis que fosse.",
   fx="explosão de carne verde + sprite gigante", som="ossos quebrando e rugido grave")

# ---------------- DEMÔNIO ----------------
sk(id="demonio_garra_abismo", classe="demonio", nome="Garra do Abismo", tipo="ativa", nivel=1,
   custo=0, recarga=0.0, conjuracao=0.0, alcance=1.5, area=0, duracao=0, elemento="fogo", escala=["FOR","AGI"],
   dano={"pct_arma":45,"base":4,"golpes":3}, efeitos=["combo de 3 golpes rápidos", "cada golpe gera 4 de Brasa"],
   descricao="Três rasgos rápidos que deixam a carne fumegando.",
   fx="três arcos laranja brasa + fumaça", som="três cortes rápidos com chiado")
sk(id="demonio_corrente_danacao", classe="demonio", nome="Corrente de Danação", tipo="ativa", nivel=5,
   custo=20, recarga=10.0, conjuracao=0.2, alcance=7, area=0, duracao=1.0, elemento="fisico", escala=["FOR"],
   dano={"pct_arma":60,"base":10}, efeitos=["puxa o alvo até o Demônio", "atordoa por 1s"],
   descricao="A corrente presa ao braço voa e volta trazendo alguém junto.",
   fx="corrente incandescente estendendo e recolhendo", som="corrente arrastando")
sk(id="demonio_pele_enxofre", classe="demonio", nome="Pele de Enxofre", tipo="buff", nivel=10,
   custo=30, recarga=22.0, conjuracao=0.0, alcance=0, area=0, duracao=10.0, elemento="fogo", escala=["VIT"],
   efeitos=["reflete 25% do dano corpo a corpo recebido como fogo", "+10% de defesa"],
   descricao="As rachaduras do peito se abrem e a pele passa a ferver.",
   fx="rachaduras de brasa intensificadas + fumaça amarela", som="chiado de chapa quente")
sk(id="demonio_passo_sombrio", classe="demonio", nome="Passo Sombrio", tipo="ativa", nivel=15,
   custo=25, recarga=12.0, conjuracao=0.0, alcance=6, area=0, duracao=2.0, elemento="sombra", escala=["AGI"],
   efeitos=["teleporta para as costas do alvo", "próximo golpe em 2s é crítico garantido"],
   descricao="Some numa fumaça preta e reaparece onde a vítima não está olhando.",
   fx="silhueta de fumaça preta com olhos de brasa", som="sopro grave")
sk(id="demonio_banquete", classe="demonio", nome="Banquete", tipo="passiva", nivel=20,
   custo=0, recarga=0, conjuracao=0, alcance=0, area=0, duracao=0, elemento="sangue", escala=["FOR"],
   efeitos=["roubo de vida 3% (base)", "roubo de vida 12% contra alvos abaixo de 30% do HP"],
   descricao="Quanto mais fraca a presa, mais ele come.",
   fx="fios vermelhos do alvo até o Demônio ao acertar", som="nenhum")
sk(id="demonio_portao_inferno", classe="demonio", nome="Portão do Inferno", tipo="suprema", nivel=400,
   custo=100, recarga=180.0, conjuracao=1.0, alcance=5, area=5, duracao=8.0, elemento="fogo", escala=["FOR"],
   dano={"pct_arma":120,"base":40,"por_segundo":True}, efeitos=["abre uma fenda por 8s que queima tudo em volta", "+20% de dano em Humanos", "requer Estágio 3 (Arquidemônio)"],
   descricao="O chão racha e o Inferno mostra a cara, só por um instante.",
   fx="fenda no chão com fogo subindo + braços de brasa", som="rugido de fornalha")

# ---------------- HUMANO ----------------
sk(id="humano_tiro_certeiro", classe="humano", nome="Tiro Certeiro", tipo="ativa", nivel=1,
   custo=10, recarga=2.0, conjuracao=0.5, alcance=9, area=0, duracao=0, elemento="fisico", escala=["AGI"],
   dano={"pct_arma":160,"base":12}, efeitos=["+25% de chance de crítico", "gasta 1 munição"],
   descricao="Respira, segura, aperta. Uma bala, um problema a menos.",
   fx="clarão de cano + rastro de bala + fumaça de pólvora", som="estampido seco")
sk(id="humano_rajada", classe="humano", nome="Rajada", tipo="area", nivel=6,
   custo=25, recarga=8.0, conjuracao=0.3, alcance=5, area="cone 60°", duracao=0, elemento="fisico", escala=["AGI"],
   dano={"pct_arma":70,"base":6,"projeteis":5}, efeitos=["leque de 5 projéteis em cone", "gasta 3 munições", "empurra levemente"],
   descricao="A escopeta de cano duplo fala alto e para todos os lados.",
   fx="leque de chumbo + clarão largo", som="tiro de escopeta duplo")
sk(id="humano_armadilha_prata", classe="humano", nome="Armadilha de Prata", tipo="ativa", nivel=12,
   custo=20, recarga=16.0, conjuracao=0.8, alcance=3, area=1, duracao=3.0, elemento="sagrado", escala=["AGI"],
   dano={"pct_arma":80,"base":20}, efeitos=["prende por 3s quem pisar", "+50% de dano em Anjos e Demônios", "dura 60s no chão"],
   descricao="Uma armadilha de urso banhada em prata e rezada pelo padre do bairro.",
   fx="mandíbula de metal fechando + faíscas prateadas", som="clangor metálico")
sk(id="humano_agua_benta_polvora", classe="humano", nome="Água Benta e Pólvora", tipo="buff", nivel=16,
   custo=30, recarga=25.0, conjuracao=1.0, alcance=0, area=0, duracao=15.0, elemento="sagrado", escala=["AGI"],
   efeitos=["próximos 15s: tiros causam +20% como sagrado OU fogo (alterna a cada uso)", "sagrado: +10% extra em Arautos"],
   descricao="Molha os cartuchos num frasco benzido. Ou em querosene, depende do dia.",
   fx="cano brilhando azul-claro (sagrado) ou laranja (fogo)", som="clique de recarga")
sk(id="humano_arrancada", classe="humano", nome="Arrancada", tipo="ativa", nivel=6,
   custo=20, recarga=5.0, conjuracao=0.0, alcance=4, area=0, duracao=0.18, elemento="fisico", escala=["FOR","AGI"],
   efeitos=["avança 4 tiles até o mouse com a espada larga estendida", "corta cada inimigo no caminho uma vez", "invulnerável no começo; o próximo golpe ou tiro em 2s causa +30%", "2 cargas"],
   descricao="Não tem poder nenhum, só pernas e uma lâmina larga. Atravessa a fila de inimigos antes que eles entendam o que passou.",
   fx="rastro de silhueta escura + sobretudo esvoaçando + corte em cada alvo + poeira no início e no fim", som="passos rápidos + lâmina cortando em sequência")
sk(id="humano_corte_largo", classe="humano", nome="Corte Giratório", tipo="area", nivel=3,
   custo=25, recarga=7.0, conjuracao=0.0, alcance=0, area=2, duracao=0.6, elemento="fisico", escala=["FOR","AGI"],
   dano={"pct_arma":110,"base":8}, efeitos=["gira a espada larga e corta 360° em volta (raio 2 tiles)", "empurra um pouco os inimigos atingidos", "precisa de espada larga equipada"],
   descricao="Quando cercam o caçador, ele planta os pés e gira o corpo inteiro. A espada larga corta em 360° e joga todo mundo para fora do círculo.",
   fx="anel de corte prateado girando em volta do personagem + faíscas e respingo de sangue nos atingidos", som="lâmina cortando o ar em giro + impacto pesado")
sk(id="humano_ultimo_suspiro", classe="humano", nome="Último Suspiro", tipo="suprema", nivel=400,
   custo=0, recarga=300.0, conjuracao=0, alcance=0, area=0, duracao=6.0, elemento="fisico", escala=["AGI"],
   efeitos=["passiva-suprema: 1x por combate sobrevive a golpe fatal com 1 HP", "ganha dano dobrado por 6s", "requer Estágio 3 (Último Guardião)"],
   descricao="Já devia estar morto. Ainda não.",
   fx="tela em preto e branco por 0.5s + batida de coração + aura vermelha", som="batida de coração")

# ---------------- TECNOMANCER ----------------
sk(id="tecnomancer_arco_voltaico", classe="tecnomancer", nome="Arco Voltaico", tipo="ativa", nivel=1,
   custo=12, recarga=1.2, conjuracao=0.4, alcance=7, area=0, duracao=0, elemento="eletrico", escala=["ESP","AGI"],
   dano={"pct_arma":90,"base":10}, efeitos=["salta para até 3 inimigos próximos (-25% por salto)", "+15% de dano em invocações"],
   descricao="A bobina das costas descarrega pelo cajado e escolhe as vítimas sozinha.",
   fx="raio azul-claro em zigue-zague entre alvos", som="estalo elétrico")
sk(id="tecnomancer_nanoreparo", classe="tecnomancer", nome="Nanoreparo", tipo="ativa", nivel=4,
   custo=25, recarga=8.0, conjuracao=0.5, alcance=6, area=0, duracao=8.0, elemento="eletrico", escala=["ESP"],
   cura={"base":10,"pct_esp":30,"por_segundo":True}, efeitos=["cura contínua por 8s em um aliado"],
   descricao="Um enxame de aranhas de latão costura a ferida por dentro.",
   fx="pontos de luz laranja rodando o alvo", som="zumbido de enxame mecânico")
sk(id="tecnomancer_torreta_sentinela", classe="tecnomancer", nome="Torreta Sentinela", tipo="invocacao", nivel=10,
   custo=40, recarga=20.0, conjuracao=1.2, alcance=3, area=0, duracao=25.0, elemento="eletrico", escala=["ESP"],
   invocacao={"hp_pct_do_dono":35,"dano_pct_arma":35,"alcance":6,"maximo":2},
   efeitos=["torreta fixa por 25s que atira no inimigo mais próximo", "até 2 ativas"],
   descricao="Monta em segundos um tripé de sucata com um olho rúnico que nunca dorme.",
   fx="torreta montando peça por peça + runa laranja acesa", som="catraca e engrenagens")
sk(id="tecnomancer_campo_forca", classe="tecnomancer", nome="Campo de Força", tipo="area", nivel=15,
   custo=50, recarga=24.0, conjuracao=0.8, alcance=5, area=3, duracao=6.0, elemento="eletrico", escala=["ESP"],
   escudo={"base":60,"pct_esp":150}, efeitos=["aliados na área ganham escudo que absorve dano por 6s"],
   descricao="Uma cúpula de estática que faz o cabelo de todo mundo arrepiar.",
   fx="cúpula azul translúcida com hexágonos e faíscas", som="zumbido grave de transformador")
sk(id="tecnomancer_pulso_antidivino", classe="tecnomancer", nome="Pulso Anti-Divino", tipo="debuff", nivel=22,
   custo=45, recarga=28.0, conjuracao=0.6, alcance=6, area=3, duracao=3.0, elemento="eletrico", escala=["ESP"],
   efeitos=["silencia magias na área por 3s", "remove 1 buff de cada inimigo", "+50% de duração contra Anjos"],
   descricao="Um pulso de frequência herege que faz as preces falharem no meio da frase.",
   fx="onda circular azul com sigilo laranja invertido no centro", som="pulso eletrônico grave")
sk(id="tecnomancer_maquina_juizo_reverso", classe="tecnomancer", nome="Máquina do Juízo Reverso", tipo="suprema", nivel=400,
   custo=120, recarga=180.0, conjuracao=2.5, alcance=3, area=7, duracao=12.0, elemento="eletrico", escala=["ESP"],
   efeitos=["constrói um artefato por 12s", "supremas inimigas não funcionam na área", "requer Estágio 3 (Arquiteto do Amanhã)"],
   descricao="Uma torre de cobre, válvulas e ossos de santo que toca a trombeta ao contrário.",
   fx="torre montando com raios em volta + campo distorcendo a imagem", som="sirene reversa")

# ---------------- SKILLS DE ÁREA DO NÍVEL 5 (pedido do Jefin, 2026-10-05) ----------------
# Feitas para FARMAR em spots e para o MODO AUTOMÁTICO: área grande, recarga curta, custo que esvazia o recurso
# em ~20 s de uso contínuo a partir do cheio (ver 'economia_auto'). Números PROVISÓRIOS até a thread Design do combate fechar mana e poções.
NIVEL5 = dict(nivel=5, area_nivel5=True, provisorio=True)
sk(id="anjo_leque_juizo", classe="anjo", nome="Leque do Juízo", tipo="area", **NIVEL5,
   custo=16, recarga=1.6, conjuracao=0.35, alcance=0, area="leque 100° à frente, 3.5 tiles", duracao=2.0, elemento="sagrado", escala=["ESP","FOR"],
   formato_area={"forma":"cone","angulo_graus":100,"raio_tiles":3.5,"origem":"personagem","direcao":"mouse"},
   dano={"golpe_espada_mult":1.3,"fogo_mult_por_alvo":0.9,"queimadura_sagrada":{"duracao_s":2.0,"dano_por_s_mult":0.1}},
   efeitos=["golpe de espada no alvo da frente", "fogo divino queima tudo no leque", "+15% de dano em tag:praga (mutantes e pragas)", "só o 1º alvo gera Graça"],
   descricao="O Anjo desce a espada e o golpe não para na lâmina: o ar à frente pega fogo branco e se abre como um leque de penas em brasa.",
   fx="arco da espada + chamas brancas e douradas abrindo em leque do chão para frente + penas queimando no ar", som="lâmina pesada + whoosh de fogo + coro curto",
   economia_auto={"recurso_max_nivel5":"~120 Graça", "gasto_por_s":10.0, "ganho_por_s":"~4 (1,5 regen + golpe no 1º alvo)", "dura_do_cheio_s":20})
sk(id="cultista_espinhos_sangue", classe="cultista", nome="Espinhos de Sangue", tipo="area", **NIVEL5,
   custo="5% HP", recarga=1.8, conjuracao=0.5, alcance=7, area="círculo de 2.2 tiles no ponto do mouse", duracao=0.6, elemento="sangue", escala=["ESP"],
   formato_area={"forma":"circulo","raio_tiles":2.2,"origem":"ponto_alvo","alcance_max_tiles":7},
   dano={"mult_por_alvo":1.0,"sangramento":{"duracao_s":4.0,"dano_por_s_mult":0.12}},
   efeitos=["lanças de sangue brotam do chão no círculo", "lentidão de 20% por 1.5 s", "abates com esta skill devolvem só 3% de HP (metade do normal)", "modo automático para sozinho abaixo de 25% de HP"],
   descricao="O Cultista crava a adaga na própria palma e aponta. O sangue que pinga lá longe vira um campo de espinhos vermelhos.",
   fx="círculo de runas vermelhas no chão + estacas de sangue subindo e quebrando + respingos", som="chiado úmido + estalo de cristal",
   economia_auto={"recurso_max_nivel5":"HP", "gasto_por_s":"2,8% do HP", "ganho_por_s":"~1% do HP (abates)", "dura_do_cheio_s":"~40 até 25% de HP; usa poção de vida, não de mana"})
sk(id="mutante_terremoto_putrido", classe="mutante", nome="Terremoto Pútrido", tipo="area", **NIVEL5,
   custo=20, recarga=2.0, conjuracao=0.45, alcance=0, area="círculo de 2.5 tiles em volta", duracao=3.0, elemento="veneno", escala=["FOR","VIT"],
   formato_area={"forma":"circulo","raio_tiles":2.5,"origem":"personagem"},
   dano={"mult_por_alvo":1.1,"poca_veneno":{"duracao_s":3.0,"dano_por_s_mult":0.12}},
   efeitos=["soco no chão com o braço gigante: onda de choque em volta", "deixa uma poça de veneno por 3 s", "atordoa 0.4 s", "só o 1º alvo gera Fúria"],
   descricao="O braço deformado desce como um bate-estaca. O chão racha e as rachaduras vomitam pus verde.",
   fx="anel de terra levantando + rachaduras com brilho verde ácido + poça borbulhando", som="impacto grave + chão rachando + borbulho",
   economia_auto={"recurso_max_nivel5":"100 Fúria (começa em 0)", "gasto_por_s":10.0, "ganho_por_s":"~4,5 nos golpes + o que apanhar", "dura_do_cheio_s":"~18; o Mutante precisa puxar os monstros e apanhar para manter"})
sk(id="demonio_ceifa_infernal", classe="demonio", nome="Ceifa Infernal", tipo="area", **NIVEL5,
   custo=25, recarga=1.8, conjuracao=0.3, alcance=0, area="meia-lua de 180° à frente, 2.8 tiles", duracao=2.5, elemento="fogo", escala=["FOR","AGI"],
   formato_area={"forma":"cone","angulo_graus":180,"raio_tiles":2.8,"origem":"personagem","direcao":"mouse"},
   dano={"mult_por_alvo":1.2,"chao_em_chamas":{"duracao_s":2.5,"dano_por_s_mult":0.1}},
   efeitos=["foiçada em meia-lua que deixa um rastro de fogo no chão", "só o 1º alvo gera Brasa", "acima de 80 de Brasa, o rastro dura o dobro"],
   descricao="A foice passa rente ao chão e o chão lembra que já foi Inferno.",
   fx="meia-lua laranja brasa + rastro de chamas baixas + fagulhas", som="lâmina cortando + rugido de fornalha curto",
   economia_auto={"recurso_max_nivel5":"100 Brasa", "gasto_por_s":13.9, "ganho_por_s":"~10 (golpes)", "dura_do_cheio_s":25})
sk(id="humano_coquetel_querosene", classe="humano", nome="Coquetel de Querosene", tipo="area", **NIVEL5,
   custo=28, recarga=2.2, conjuracao=0.35, alcance=6, area="círculo de 2 tiles no ponto do mouse", duracao=3.0, elemento="fogo", escala=["AGI"],
   formato_area={"forma":"circulo","raio_tiles":2.0,"origem":"ponto_alvo","alcance_max_tiles":6},
   dano={"explosao_mult_por_alvo":1.0,"fogo_no_chao":{"duracao_s":3.0,"dano_por_s_mult":0.12}},
   efeitos=["arremessa uma garrafa de querosene com pavio aceso", "explode e deixa fogo no chão por 3 s", "+10% de dano em tag:planta e tag:praga"],
   descricao="Garrafa de vidro, querosene do lampião e um trapo de batina. A Vigília chama de 'vela grande'.",
   fx="garrafa girando em arco + estilhaços de vidro + bola de fogo laranja + chamas no chão", som="vidro quebrando + whoosh de fogo",
   economia_auto={"recurso_max_nivel5":"100 Fôlego", "gasto_por_s":12.7, "ganho_por_s":"8 (regen)", "dura_do_cheio_s":21})
sk(id="tecnomancer_tempestade_bobina", classe="tecnomancer", nome="Tempestade de Bobina", tipo="area", **NIVEL5,
   custo=16, recarga=1.7, conjuracao=0.4, alcance=0, area="círculo de 2.6 tiles em volta", duracao=0.5, elemento="eletrico", escala=["ESP"],
   formato_area={"forma":"circulo","raio_tiles":2.6,"origem":"personagem"},
   dano={"mult_por_alvo":0.95},
   efeitos=["a caldeira das costas descarrega raios em todos em volta", "15% de chance de paralisar 0.6 s", "+15% de dano em invocações"],
   descricao="As bobinas de tesla das costas zumbem, o cabelo de todo mundo em volta arrepia, e então o ar explode em raios azuis.",
   fx="cúpula de raios azuis saindo das bobinas das costas até cada inimigo + faíscas no chão", som="zumbido crescente + estalo elétrico forte",
   economia_auto={"recurso_max_nivel5":"~125 Carga", "gasto_por_s":9.4, "ganho_por_s":"3 (regen; parado não conta no modo auto)", "dura_do_cheio_s":20})

MODO_AUTO = {
  "_doc": "Proposta para a thread Design do combate. Números PROVISÓRIOS.",
  "regra": "No modo automático, a skill de área do nível 5 é usada sozinha quando ela sai da recarga e há 2+ inimigos na área (ou 1, se o jogador marcar). Ela para quando o recurso não paga o custo.",
  "meta": "Do recurso cheio até zerar, uso contínuo dura ~20 s (Cultista ~40 s até 25% de HP). Depois disso o jogador precisa de poção ou de pausa.",
  "fonte": "Regras finais em design/combate/combate.md seção 9 e farm_auto.json (tecla Z, poção automática, spots).",
}

# ids que a thread Design do combate usa em classes_base.json para a skill de área do nível 5.
# O desenho, o nome e o ícone são os daqui; os NÚMEROS vêm de lá.
ID_COMBATE_N5 = {   # Design do combate adotou os mesmos ids (classes_base.json, 2026-10-06)
  k: k for k in ["anjo_leque_juizo","cultista_espinhos_sangue","mutante_terremoto_putrido",
                 "demonio_ceifa_infernal","humano_coquetel_querosene","tecnomancer_tempestade_bobina"]
}

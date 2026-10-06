# Catálogo de itens do DARK PASSAGE v0.2. Gera ../itens.json (rode: python3 gerar_json.py)
# Alinhado com design/combate (drops.json, classes_base.json) e design/missoes/dados/itens.json.
# - Itens BASE (armas e armaduras genéricas): a raridade é ROLADA no drop (comum/magico/raro/excelente), como no MU.
#   Dano e defesa saem das fórmulas de classes_base.json ("armas_por_faixa"). Tudo PROVISÓRIO até o Design do combate revisar.
# - Itens COM NOME (lore, únicos, missão, leitura) vêm da thread Missões: mesmo id e nome; aqui só completamos o que faltava.

# grade = [largura, altura] em células de 30 px da mochila (estilo MU)
ARMAS = [
 # id, nome, classes, tipo, maos, nivel, intervalo, grade, motivo, tint, emissivo, lore
 ("espada_vigilia_rachada","Espada de Vigília Rachada",["anjo"],"espada",1,1,1.05,[1,3],"espada","aco",None,"Lâmina de um sentinela de igreja que morreu no posto. Ainda tem cera de vela no punho."),
 ("escudo_porta_capela","Escudo de Porta de Capela",["anjo"],"escudo",1,3,None,[2,2],"escudo","madeira",None,"Meia porta de capela com uma cruz pregada. Pesa como um pecado."),
 ("lanca_procissao","Lança de Procissão",["anjo"],"lanca",2,5,1.15,[1,4],"lanca","osso",None,"Carregava um estandarte de santo. O santo caiu primeiro."),
 ("espada_sineiro","Espada do Sineiro",["anjo"],"espada",1,9,1.05,[1,3],"espada","bronze",None,"Fundida com o bronze de um sino rachado. Quando bate em armadura, ainda soa."),
 ("adaga_ritual_cega","Adaga Ritual Cega",["cultista"],"adaga",1,1,1.0,[1,2],"adaga","osso",None,"Não corta bem. Corta o suficiente."),
 ("cajado_vertebras","Cajado de Vértebras",["cultista"],"cajado",2,5,1.1,[1,4],"cajado_osso","osso",None,"Doze vértebras de doze voluntários. Diz a seita que eram voluntários."),
 ("grimorio_acorrentado","Grimório Acorrentado",["cultista"],"grimorio",1,8,None,[2,2],"grimorio","vinho",None,"A corrente não é para roubarem o livro. É para o livro não sair andando."),
 ("adaga_ossuario","Adaga do Ossuário",["cultista"],"adaga",1,11,1.0,[1,2],"adaga","ferro_negro",None,"Afiada num degrau de crânios. Corta melhor no escuro."),
 ("machado_placa_transito","Machado de Placa de Trânsito",["mutante"],"machado",2,1,1.2,[2,3],"machado_placa","placa",None,"PARE. Ninguém parou."),
 ("punhos_sucata","Punhos de Sucata",["mutante"],"punhos",2,5,1.0,[2,2],"punhos","ferrugem",None,"Canos, porcas e arame farpado enrolados em fita isolante."),
 ("cutelo_matadouro","Cutelo do Matadouro",["mutante","demonio"],"machado",1,8,1.1,[1,3],"cutelo","aco",None,"Do matadouro municipal. Depois da praga, ninguém mais sabia o que era gado."),
 ("garras_ossario","Garras do Ossário",["mutante"],"punhos",2,11,0.95,[2,2],"garras","praga",None,"Ossos de dedo afiados e cravados nos nós da mão. Doem mais em quem usa. No começo."),
 ("foice_serrilhada","Foice Serrilhada",["demonio"],"foice",2,1,0.95,[2,4],"foice","aco",None,"Era de colher trigo. Os dentes vieram depois, quando o trigo acabou."),
 ("espada_serrilhada","Espada Serrilhada",["demonio"],"espada",1,5,1.0,[1,3],"espada_serra","ferro_negro",None,"Os dentes foram limados à mão, um por noite, durante um ano inteiro de cerco."),
 ("corrente_gancho","Corrente com Gancho",["demonio"],"corrente",1,8,1.05,[2,2],"corrente","ferro_negro",None,"Gancho de açougue numa corrente de portão. Puxa gente como quem puxa um balde."),
 ("foice_sepultura","Foice de Sepultura",["demonio"],"foice",2,11,0.95,[2,4],"foice","ferro_negro",None,"O coveiro usava para cortar raiz de cova. Hoje corta o que sai dela."),
 ("besta_sucata","Besta de Sucata",["humano"],"besta",2,1,1.15,[3,2],"besta","madeira",None,"Mola de cama, arco de barril e muita paciência. Silenciosa, e no fim do mundo silêncio vale mais que bala."),
 ("espada_larga_sucata","Espada Larga de Sucata",["humano"],"espada_larga",1,1,1.25,[1,3],"espada_larga","aco",None,"Chapa de trilho batida até virar lâmina. Abre caminho quando a munição acaba. Ela sempre acaba."),
 ("escopeta_cano_serrado","Escopeta de Cano Serrado",["humano"],"escopeta",1,1,1.1,[1,3],"escopeta","madeira",None,"Calibre 12, cano serrado no torno da oficina. Cabe no coldre da coxa e faz o barulho de um sino caindo."),
 ("espada_larga_carrasco","Espada Larga do Carrasco",["humano"],"espada_larga",1,6,1.15,[1,3],"espada_larga","ferro",None,"Ponta quadrada, sem fio na ponta: foi feita para cortar cabeça, não para furar. Hoje corta Não-Julgados."),
 ("montante_vigilia","Montante da Vigília",["humano"],"espada_larga",2,10,1.3,[1,4],"espada_larga","prata",None,"Forjado pela Vigília com prata de castiçal. A lâmina é larga como uma porta de cripta."),
 ("escopeta_cano_duplo","Escopeta de Cano Duplo",["humano"],"escopeta",2,5,1.3,[1,4],"escopeta","madeira",None,"Cano serrado, coronha remendada com couro de bota."),
 ("mosquete_pederneira","Mosquete de Pederneira",["humano"],"mosquete",2,9,1.6,[1,4],"mosquete","latao",None,"Velho como a república. Ainda acerta um anjo a cem passos."),
 ("besta_repeticao","Besta de Repetição",["humano"],"besta",2,11,0.9,[3,2],"besta","latao",None,"Engenhoca da Vigília: um carregador de seis virotes e uma manivela que range."),
 ("cajado_antena_torto","Cajado-Antena Torto",["tecnomancer"],"cajado",2,1,1.1,[1,4],"cajado_antena","latao",None,"Uma antena de rádio de guerra com uma válvula no topo. Pega estações que não deviam existir."),
 ("luva_voltaica","Luva Voltaica",["tecnomancer"],"luva",1,5,1.0,[2,2],"luva_voltaica","cobre",None,"Dá choque em quem você toca. E um pouco em você."),
 ("pistola_raios","Pistola de Raios",["tecnomancer"],"pistola",1,8,1.05,[2,2],"pistola_raio","latao",None,"Bobina de carro, lâmpada de farol e um sigilo de Salomão gravado na empunhadura."),
 ("cajado_valvulas","Cajado de Válvulas",["tecnomancer"],"cajado",2,11,1.1,[1,4],"cajado_antena","cobre",None,"Três válvulas de rádio em fila. Quando todas acendem, o cabelo de todo mundo em volta levanta."),
]

PESOS = {"leve":["cultista","tecnomancer","anjo"], "medio":["humano","mutante","tecnomancer","demonio"], "pesado":["anjo","demonio","mutante"]}
GRADE_SLOT = {"cabeca":[2,2],"peito":[2,3],"luvas":[2,2],"calcas":[2,2],"botas":[2,2]}
FRACAO_DEF = {"cabeca":0.16,"peito":0.34,"luvas":0.12,"calcas":0.22,"botas":0.16}
MULT_PESO = {"leve":0.8,"medio":1.0,"pesado":1.25}
CONJUNTOS = [
  {"id":"batina_remendada","nome":"Batina Remendada","peso":"leve","nivel":2,"tint":"vinho",
   "pecas":{"cabeca":"Capuz Remendado","peito":"Batina Remendada","luvas":"Ataduras de Penitente","calcas":"Saia de Penitente","botas":"Sandálias de Corda"},
   "lore":"Roupa de seminarista de uma ordem que não existe mais."},
  {"id":"couro_sobrevivente","nome":"Couro de Sobrevivente","peso":"medio","nivel":2,"tint":"couro",
   "pecas":{"cabeca":"Chapéu de Aba Larga","peito":"Sobretudo Gasto","luvas":"Luvas de Couro","calcas":"Calças Remendadas","botas":"Coturnos"},
   "lore":"Tudo o que sobrou de um armazém saqueado três vezes."},
  {"id":"placas_sino","nome":"Placas de Sino Fundido","peso":"pesado","nivel":3,"tint":"bronze",
   "pecas":{"cabeca":"Elmo de Sino","peito":"Peitoral de Sino","luvas":"Manoplas de Bronze","calcas":"Grevas de Bronze","botas":"Sapatos de Ferro"},
   "lore":"Os ferreiros derreteram os sinos da cidade. Era isso ou continuar ouvindo eles tocarem sozinhos."},
  {"id":"coro_mudo","nome":"Vestes do Coro Mudo","peso":"leve","nivel":10,"tint":"osso","emissivo":"#ff3a2a",
   "pecas":{"cabeca":"Máscara do Coro Mudo","peito":"Sobrepeliz do Coro Mudo","luvas":"Mãos Costuradas","calcas":"Saias do Coro Mudo","botas":"Passos Calados"},
   "bonus_conjunto":{"2":"+3 ESP","3":"+6% de dano mágico","5":"habilidades custam 10% menos recurso"},
   "lore":"Os cantores do ossário costuraram a própria boca para não cantar o fim. Ele veio assim mesmo."},
  {"id":"couraca_acougueiro_oco","nome":"Couraça do Açougueiro Oco","peso":"medio","nivel":10,"tint":"sangue","emissivo":"#9cff3a",
   "pecas":{"cabeca":"Respirador do Açougueiro","peito":"Couraça do Açougueiro","luvas":"Luvas de Esfolar","calcas":"Calças de Matadouro","botas":"Botas de Matadouro"},
   "bonus_conjunto":{"2":"+3 VIT","3":"+5% de dano físico","5":"golpes críticos causam sangramento"},
   "lore":"Tirada dos Açougueiros Ocos do porão. Por dentro não tinha ninguém, só o cheiro."},
  {"id":"juramento_quebrado","nome":"Armadura do Juramento Quebrado","peso":"pesado","nivel":11,"tint":"ferro_negro","emissivo":"#ff7a1a",
   "pecas":{"cabeca":"Elmo do Juramento Quebrado","peito":"Couraça do Juramento Quebrado","luvas":"Manoplas do Juramento Quebrado","calcas":"Grevas do Juramento Quebrado","botas":"Botas do Juramento Quebrado"},
   "bonus_conjunto":{"2":"+3 FOR","3":"+8% de defesa","5":"abaixo de 25% de HP, explode em fogo em volta (1x a cada 60 s)"},
   "lore":"Feita para um paladino que jurou proteger a cidade e depois mudou de lado. A armadura não mudou junto."},
]

ACESSORIOS = [  # bases genéricas: raridade rolada
  dict(id="anel_prego_caixao", nome="Anel de Prego de Caixão", slot="anel", nivel=4, faixa=1, grade=[1,1], motivo="anel", tint="ferro", atributo_base={"vit":2}, lore="Um prego dobrado em volta do dedo. Saiu de um caixão que estava vazio."),
  dict(id="colar_dentes", nome="Colar de Dentes", slot="amuleto", nivel=4, faixa=1, grade=[1,1], motivo="colar_dentes", tint="osso", atributo_base={"for":2}, lore="Nenhum dos dentes é humano. Quase nenhum."),
  dict(id="anel_ferro_cripta", nome="Anel de Ferro da Cripta", slot="anel", nivel=9, faixa=2, grade=[1,1], motivo="anel", tint="ferro_negro", atributo_base={"vit":3}, lore="Arrancado do dedo de um monge emparedado. O dedo não queria soltar."),
  dict(id="rosario_ossos", nome="Rosário de Ossos", slot="amuleto", nivel=9, faixa=2, grade=[1,1], motivo="rosario", tint="osso", atributo_base={"esp":3}, lore="Cinquenta e nove contas de osso de dedo. A sexagésima é sua, quando chegar a hora."),
]

CONSUMIVEIS = [
  dict(id="pocao_vida_p", tag="consumivel:pocao_vida_p", nome="Frasco de Sangue Pequeno", efeito={"cura_hp":120}, preco=6, pilha=100, motivo="pocao", tint="vermelho", lore="Ninguém pergunta de quem é."),
  dict(id="pocao_vida_m", tag="consumivel:pocao_vida_m", nome="Frasco de Sangue Médio", efeito={"cura_hp":300}, preco=18, pilha=100, nivel=8, motivo="pocao_grande", tint="vermelho", lore="Coagulado no fundo. Agite antes de beber."),
  dict(id="pocao_recurso_p", tag="consumivel:pocao_recurso_p", nome="Elixir de Éter Pequeno", efeito={"recurso_pct":0.4}, preco=8, pilha=100, motivo="pocao", tint="azul", lore="Gosto de moeda velha e trovoada. Devolve Graça, Fúria, Brasa, Fôlego ou Carga."),
  dict(id="pocao_recurso_m", tag="consumivel:pocao_recurso_m", nome="Elixir de Éter Médio", efeito={"recurso_pct":0.8}, preco=22, pilha=100, nivel=8, motivo="pocao_grande", tint="azul", lore="O frasco zumbe baixinho quando ninguém está olhando."),
  dict(id="agua_benta", tag="consumivel:extra", nome="Frasco de Água Benta", efeito={"remove":["maldicao","sangramento"]}, preco=35, pilha=20, motivo="agua_benta", tint="agua", lore="Benzida às pressas. Ainda vale."),
  dict(id="antidoto_querosene", tag="consumivel:extra", nome="Antídoto de Querosene", efeito={"remove":["veneno"],"res_veneno":0.2,"duracao_s":60}, preco=30, pilha=20, motivo="antidoto", tint="verde", lore="Arde na garganta. A praga arde mais."),
  dict(id="vela_retorno", tag="consumivel:extra", nome="Vela de Retorno", efeito={"teleporta":"acampamento","canalizar_s":3}, preco=50, pilha=10, motivo="vela", tint="cera", lore="Acenda e pense em casa. Se ainda tiver uma."),
  dict(id="gazua", tag="consumivel:gazua", nome="Gazua", efeito={"abre":"bau_de_ferro","chance":0.6}, preco=40, pilha=20, motivo="gazua", tint="aco", lore="Dois grampos de cabelo e um dedo de prática."),
  dict(id="balas_chumbo", tag="consumivel:municao", nome="Balas de Chumbo", efeito={"municao":"mosquete","qtd":100}, preco=10, pilha=999, classes=["humano"], motivo="balas", tint="chumbo", lore="Derretidas de canos de igreja."),
  dict(id="virotes_prata", tag="consumivel:municao", nome="Virotes de Prata", efeito={"municao":"besta","qtd":100,"bonus_vs":{"tag:celestial":1.05,"tag:infernal":1.05}}, preco=14, pilha=999, classes=["humano"], motivo="virotes", tint="prata", lore="Pontas feitas de talheres de família."),
  dict(id="cartuchos_sal", tag="consumivel:municao", nome="Cartuchos Calibre 12", efeito={"municao":"escopeta calibre 12","qtd":100}, preco=12, pilha=999, classes=["humano"], motivo="cartuchos", tint="vermelho", lore="Sal, pólvora e uma reza curta."),
]

MATERIAIS = [
  dict(id="osso", tag="material:osso", nome="Osso Rachado", motivo="osso", tint="osso", lore="Serve para cajado, para amuleto e para assustar criança."),
  dict(id="couro_podre", tag="material:couro_podre", nome="Couro Podre", motivo="couro", tint="couro", lore="Ainda dá para costurar. Não dá para cheirar."),
  dict(id="sucata", tag="material:sucata", nome="Sucata", motivo="sucata", tint="ferrugem", lore="Porcas, molas e pedaços de cano. Para um Tecnomancer, é um tesouro."),
  dict(id="cinza_de_alma", tag="material:cinza_de_alma", nome="Cinza de Alma", motivo="cinza", tint="cinza", lore="O que sobra de um espectro. Morna e leve demais."),
  dict(id="carne_estragada", tag="material:carne_estragada", nome="Carne Estragada", motivo="carne", tint="sangue", lore="Do porão do matadouro. Os Carniçais pagam bem."),
  dict(id="pedra_benta", tag="material:pedra_benta", nome="Pedra Benta", motivo="pedra_benta", tint="cinza", lore="Lasca de altar com uma cruz riscada. Refina armas sagradas."),
  dict(id="cera_de_vela", tag="material:cera_de_vela", nome="Cera de Vela", motivo="cera", tint="cera", lore="Escorrida dos castiçais do ossário. Algumas gotas parecem lágrimas."),
  dict(id="pena_suja", tag="material:pena_suja", nome="Pena Suja", motivo="pena", tint="osso", lore="Cinza de fuligem. Cai das asas de quem desceu sem ser chamado."),
]

JOIAS = [
  dict(id="lagrima_anjo", tag="joia:refino", nome="Lágrima de Anjo", efeito="refina +0 a +6 (100%)", motivo="joia_lagrima", tint="ouro", emissivo="#ffe08a", lore="Cristalizou no rosto de porcelana de um anjo que hesitou por um segundo."),
  dict(id="fragmento_alma", tag="joia:refino", nome="Fragmento de Alma", efeito="refina +6 a +9 (55%; falha volta 1 nível, nunca destrói)", motivo="joia_alma", tint="alma", emissivo="#bfe6ff", lore="Um pedaço de alguém. Quente ao toque."),
  dict(id="coagulo_caos", tag="joia:extra", nome="Coágulo do Caos", efeito="combinações no Altar do Caos (versão futura)", motivo="joia_caos", tint="sangue", emissivo="#ff3a2a", lore="Sangue que nunca terminou de secar porque não lembra de quem era."),
  dict(id="engrenagem_viva", tag="joia:extra", nome="Engrenagem Viva", efeito="adiciona +4 a uma opção do item (versão futura)", motivo="joia_engrenagem", tint="latao", emissivo="#9cff3a", lore="Gira sozinha. Os Tecnomancers juram que não construíram."),
]

CHAVES_BAUS = [
  dict(id="chave_bau_ferro", tag="chave:bau_de_ferro", nome="Chave Enferrujada", tipo="chave", grade=[1,2], motivo="chave", tint="ferrugem", lore="Abre um baú de ferro por aqui. Quase tudo por aqui está trancado."),
  dict(id="caixote_podre", tipo="bau", nome="Caixote Podre", motivo="bau_madeira", tint="madeira", lore="Madeira mole, prego solto. Às vezes solta um gás verde."),
  dict(id="bau_de_ferro", tipo="bau", nome="Baú de Ferro", motivo="bau_ferro", tint="ferro", lore="Trancado. Alguém achou que valia a pena trancar."),
  dict(id="bau_faminto", tipo="bau", nome="Baú Faminto", motivo="bau_faminto", tint="madeira", lore="Um em cada doze caixotes da cripta morde."),
  dict(id="relicario_da_trombeta", tipo="bau", nome="Relicário da Trombeta", motivo="relicario", tint="ouro", emissivo="#ffe08a", lore="Acende vela por vela antes de abrir."),
]

# ---------- Itens da thread Missões: só completamos o que faltava ----------
RARIDADE_MISSAO = {"comum":"comum","magico":"magico","raro":"raro","unico":"lendario"}
# motivo, tint, emissivo, grade, tag de drop (quando existe), slot normalizado
MISSOES = {
 "bobina_cobre":("bobina","cobre",None,[1,1]), "pena_querubim":("pena","prata",None,[1,2]), "dente_vala":("dente","osso",None,[1,1]),
 "raiz_cova":("raiz","pano",None,[1,1]), "caldo_cardo":("tigela","madeira",None,[1,1]), "medalhinha_cardo":("medalha","latao",None,[1,1]),
 "sebo_rancoso":("sebo","cera",None,[1,1]), "ferro_velho":("sucata","ferro",None,[1,1]), "badalo_rachado":("badalo","bronze",None,[1,2]),
 "livro_obitos":("livro","couro",None,[2,2]), "chave_gancho":("chave_gancho","ferro",None,[1,2]), "lacre_carne":("lacre","sangue","#ff3a2a",[1,1]),
 "lacre_lagrimas":("lacre","cera","#bfe6ff",[1,1]), "bocal_trombeta":("bocal","ouro","#ffe08a",[1,2]), "carta_lucio":("carta","pano",None,[1,1]),
 "mapa_rasgado":("mapa","pano",None,[2,2]), "relicario_vazio":("relicario_peq","prata",None,[1,1]), "pa_simao":("pa","ferro",None,[1,4]),
 "caixinha_musica":("caixinha","latao",None,[1,1]),
 "pao_duro":("pao","madeira",None,[1,1]), "tonico_graxa":("tonico","azul",None,[1,1]), "hostia_negra":("hostia","ferro_negro","#ff3a2a",[1,1]),
 "vela_simao":("vela","cera",None,[1,1]), "agua_benta_polvora":("bomba_benta","agua",None,[1,1]), "caldo_cardo_comum":("tigela","madeira",None,[1,1]),
 "figo_anacleto":("figo","vinho",None,[1,1]), "agua_doce":("cantil","agua",None,[1,2]),
 "leitura_obitos":("livro","couro",None,[2,2]), "leitura_carta_lucio":("carta","pano",None,[1,1]), "leitura_mapa_tobias":("mapa","pano",None,[2,2]),
 "leitura_anselmo":("livro","azul",None,[2,2]), "leitura_tabela_carnica":("papel","pano",None,[1,1]), "leitura_hino_carpideiras":("pergaminho","pano",None,[1,2]),
 "leitura_confissao_anacleto":("tabua","cinza",None,[2,2]), "leitura_ordem_zacarias":("pergaminho","ouro","#ffe08a",[1,2]),
 "faixa_vigilia":("bracadeira","azul","#ff9a3a",[1,1]), "fita_juizo":("fita","vermelho","#ffe08a",[1,1]),
 "escopeta_badalada":("escopeta","bronze",None,[1,4]), "machado_bonde":("machado_bonde","azul",None,[2,3]), "cajado_lampiao":("cajado_lampiao","ferro","#ffe0a0",[1,4]),
 "espada_escudeiro":("espada","prata",None,[1,3]), "foice_penhor":("foice_penhor","aco",None,[2,4]), "adaga_chaga":("adaga_curva","sangue",None,[1,2]),
 "badalo_de_guerra":("amuleto_sino","bronze",None,[1,1]), "lenco_cardo":("lenco","vermelho",None,[1,1]), "terco_lucio":("terco_partido","osso",None,[1,1]),
 "selo_madre":("anel_selo","ferro","#ffe08a",[1,1]), "dragonas_general":("casaca","sangue","#ff7a1a",[2,3]), "veu_carpideira":("veu","ferro_negro","#bfe6ff",[2,2]),
 "estilhaco_lacre":("estilhaco","chumbo","#ff9a3a",[1,1]), "diapasao_reverso":("diapasao","latao","#9fd8ff",[1,1]), "pena_zacarias":("pena","ouro","#ffe08a",[1,2]),
 "etiqueta_branca":("etiqueta","pano","#ff7a1a",[1,1]), "gancho_capataz":("gancho","ferrugem",None,[1,3]), "estandarte_legiao":("estandarte","sangue","#ff7a1a",[2,4]),
 "bacula_femur":("cajado_femur","osso","#bfe6ff",[1,4]), "halo_incandescente":("halo","ferro","#ff7a1a",[2,2]),
 "estilhaco_absinto":("estilhaco","praga","#9dff4a",[1,1]), "chave_segunda_estrela":("chave_gancho","latao","#ffe08a",[1,2]), "divisa_legiao":("medalha","bronze","#ff3a2a",[1,1]),
 "valvula_radio":("bobina","lata","#ffc070",[1,1]), "pagina_ordem":("pergaminho","pano",None,[1,1]), "amostra_amarga":("tonico","praga","#9dff4a",[1,1]),
 "fragmento_clarao":("estilhaco","cinza","#fff2c0",[1,1]), "chave_lancamento":("chave_gancho","latao","#ffe08a",[1,2]), "insignia_arrancada":("medalha","sangue",None,[1,1]),
 "carta_apostata":("carta","pano",None,[1,1]), "meia_dragona":("bracadeira","ouro",None,[1,1]), "leitura_ordem_lancamento":("pergaminho","pano",None,[1,1]),
 "leitura_carta_apostata":("carta","pano",None,[1,1]), "contador_isaura":("diapasao","latao","#9dff4a",[1,2]),
}
# lendario:<chefe/elite> de drops.json -> itens com nome da thread Missões
POOLS_LENDARIOS = {
  "lendario:capataz":  ["gancho_capataz"],
  "lendario:cardo":    ["lenco_cardo"],
  "lendario:general":  ["estandarte_legiao"],
  "lendario:celeste":  ["bacula_femur", "veu_carpideira"],
  "lendario:zacarias": ["halo_incandescente"],
}

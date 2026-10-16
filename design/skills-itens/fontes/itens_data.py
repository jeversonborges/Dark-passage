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
 "placa_coveiro":("etiqueta","ferro",None,[1,1]), "folha_tombo":("pergaminho","ouro",None,[1,1]), "ultimo_tijolo":("tabua","cinza",None,[1,1]),
 "leitura_livro_tombo":("livro","couro",None,[2,2]), "faixas_betania":("fita","pano",None,[1,1]),
 "eco_do_nome":("estilhaco","bronze","#fff2c0",[1,1]), "elmo_rafael":("elmo_pesado","prata","#fff2c0",[2,2]),
}
# lendario:<chefe/elite> de drops.json -> itens com nome da thread Missões
POOLS_LENDARIOS = {
  "lendario:capataz":  ["gancho_capataz"],
  "lendario:cardo":    ["lenco_cardo"],
  "lendario:general":  ["estandarte_legiao"],
  "lendario:celeste":  ["bacula_femur", "veu_carpideira"],
  "lendario:zacarias": ["halo_incandescente"],
}

# ---------- Arte pronta do Jefin (2026-10-15): anéis e túnicas, os itens PADRÃO do jogo ----------
# A arte vem pintada (assets/icones/fontes/*.png, grade 4x2 lida da esquerda para a direita, de cima para baixo);
# tools/icones/arte_pronta.py recorta cada peça e gera os ícones. Regra do Jefin: quanto mais bonito o item, mais atributos.
# Raridade rolada como as outras bases (comum..excelente, opções extras de drops.json); a base já vem forte.
# bonus_fixo usa as mesmas chaves de Itens.bonus() no jogo (dano_plano, defesa, hp, critico, velocidade_ataque,
# roubo_de_vida, reduz_dano, dano_magico_extra, ouro, res:{elemento}). peso_drop: os mais bonitos caem menos.
# Túnicas: armadura de peito de pano, todas as classes; o visual do personagem não muda (só a arma muda).
ANEIS_SIMPLES = [  # (id, nome, nível, índice na folha, atributos, bonus_fixo, lore)
 ("aro_ferro_velho", "Aro de Ferro Velho", 1, 0, {"vit":2}, {}, "Batido de um rebite de trilho. Todo mundo em São Lázaro começou com um destes."),
 ("alianca_cobre_silo", "Aliança de Cobre do Silo", 2, 3, {"vit":2,"esp":1}, {}, "Fio de cobre tirado da fiação do Silo. Esquenta um pouco quando o contador estala."),
 ("anel_couro_arreio", "Anel de Couro de Arreio", 3, 5, {"agi":3,"for":1}, {}, "Tira de arreio de bonde-veleiro amarrada num aro de lata. Segura firme como corda de vela."),
 ("anel_osso_cintado", "Anel de Osso Cintado", 4, 7, {"vit":3,"esp":2}, {"hp":10}, "Falange de santo cintada com ferro, para não fugir de volta para o relicário."),
 ("anel_coroa_espinhos", "Anel da Coroa de Espinhos", 6, 2, {"for":4,"vit":2}, {"dano_plano":1}, "Latão cortado em dentes, como a coroa do Cristo da capela. Machuca quem dá o soco também."),
 ("anel_luto_negro", "Anel do Luto Negro", 7, 4, {"esp":4,"vit":3}, {"hp":15}, "Azeviche de viúva em aro de ferro. As carpideiras usavam um para cada morto que não levantou."),
 ("anel_vento_absinto", "Anel do Vento de Absinto", 9, 1, {"agi":5,"esp":3}, {"critico":0.01}, "Prata gravada com o redemoinho que a tempestade faz quando passa pelo Rio Amargo."),
 ("alianca_ouro_enterrado", "Aliança de Ouro Enterrado", 11, 6, {"for":3,"agi":2,"vit":2,"esp":2}, {"hp":20,"ouro":0.05}, "Achada no quarto andar de uma casa que hoje é porão. A rua de hoje é o telhado de ontem, e o ouro ficou lá embaixo."),
]
ANEIS_GEMAS = [
 ("anel_runas_bobina", "Anel das Runas de Bobina", 7, 1, {"esp":4,"agi":2}, {"hp":15,"dano_magico_extra":2}, "As runas acendem em azul quando passa corrente. Os Tecnomancers dizem que é eletricidade; os padres dizem que não."),
 ("anel_nao_julgado", "Anel do Não-Julgado", 8, 3, {"vit":5,"for":2}, {"hp":25,"reduz_dano":0.02}, "Obsidiana lacrada com uma caveira que ainda espera o Juízo. Quem usa também aprende a esperar."),
 ("serpente_rio_amargo", "Serpente do Rio Amargo", 9, 4, {"agi":5,"vit":3}, {"hp":20,"res":{"veneno":0.1}}, "Escamas de bronze verdes do Amargo. Bebeu do rio e não morreu, e agora não solta o dedo."),
 ("sinete_bispo_violeta", "Sinete do Bispo Violeta", 10, 7, {"esp":6,"vit":3}, {"hp":30,"res":{"sagrado":0.08}}, "Ametista de bispo em bronze velho. Lacrou as últimas indulgências vendidas antes da terceira trombeta."),
 ("anel_segunda_estrela", "Anel da Segunda Estrela", 11, 5, {"esp":5,"agi":4,"vit":2}, {"hp":35,"critico":0.02}, "Uma safira presa numa estrela de quatro pontas. Dizem que aponta para o Silo, onde a outra estrela ainda dorme."),
 ("anel_cardeal_carmim", "Anel do Cardeal Carmim", 12, 2, {"for":6,"vit":4}, {"hp":45,"roubo_de_vida":0.02}, "Ouro e rubi de cardeal. O cardeal benzeu a guerra; o anel lembra o gosto."),
 ("coracao_enxofre", "Coração de Enxofre", 13, 0, {"for":7,"vit":5}, {"hp":55,"dano_plano":3,"res":{"fogo":0.1}}, "Um rubi que bate. Ferro de forja infernal cravado em volta para ele não sair correndo."),
 ("garra_legiao_blasfema", "Garra da Legião Blasfema", 15, 6, {"for":8,"agi":5,"vit":5}, {"hp":70,"critico":0.03,"velocidade_ataque":0.03}, "Anel de oficial da Legião Blasfema. As garras seguram a gema como seguravam a tropa: até o general sumir."),
]
TUNICAS = [  # (id, nome, nível, índice, defesa, atributos, bonus_fixo, lore)
 ("tunica_saco_peregrino", "Túnica de Saco do Peregrino", 1, 0, 1, {"vit":1}, {}, "Saco de farinha com buraco para a cabeça. Os peregrinos chegavam a São Lázaro vestindo isto e esperança."),
 ("gibao_batedor_vela", "Gibão do Batedor da Vela", 3, 4, 2, {"agi":2,"vit":1}, {}, "Lona de vela de bonde, costurada em dupla. A bolsa na cintura sempre tem um cartucho e um pedaço de pão."),
 ("gibao_fivelas_bondeiro", "Gibão de Fivelas do Bondeiro", 5, 1, 3, {"for":2,"vit":2}, {"hp":10}, "Os bondeiros se prendem ao mastro pelas fivelas quando a tempestade vira o bonde de lado."),
 ("tunica_margem_amarga", "Túnica da Margem Amarga", 7, 6, 4, {"vit":3,"agi":2}, {"hp":20,"res":{"veneno":0.08}}, "Tingida com as folhas retorcidas da beira do rio. O verde não sai, nem fervendo."),
 ("tunica_vigia_anil", "Túnica do Vigia Anil", 9, 3, 5, {"esp":3,"vit":3}, {"hp":30,"defesa":1}, "Anil e prata de quem ficava acordado na torre esperando o clarão. Viu o clarão. Continua acordado."),
 ("habito_penitente_carmim", "Hábito do Penitente Carmim", 11, 2, 6, {"for":3,"vit":4}, {"hp":40,"roubo_de_vida":0.01}, "Vermelho de flagelante, com a cruz bordada a ouro. Cada ponto da costura foi uma reza; cada reza, uma chicotada."),
 ("sobreveste_setimo_selo", "Sobreveste do Sétimo Selo", 13, 5, 7, {"esp":5,"vit":4}, {"hp":50,"dano_magico_extra":3}, "Preta e violeta, com a ametista do sétimo selo no peito. Quem a costurou não quis dizer o que ela abre."),
 ("alva_juizo_dourado", "Alva do Juízo Dourado", 15, 7, 9, {"for":3,"agi":3,"vit":4,"esp":4}, {"hp":70,"reduz_dano":0.03}, "Veste branca de altar com o sol do Juízo bordado a ouro. Limpa demais para este mundo, e mesmo assim ninguém consegue sujá-la."),
]

# ---------- Arte pronta, lote 2 (Jefin, 2026-10-16): conjuntos de pano, colares, espadas e o Decreto Vampírico ----------
# Capuzes, calças e botas vêm em 10 cores que casam com as túnicas: viram CONJUNTOS (túnica + capuz + calças + botas).
# Índice na folha (5x2): 0 saco, 1 cinza, 2 creme, 3 vermelho, 4 azul, 5 verde, 6 branco, 7 roxo, 8 pele, 9 azul coroado.
# (id do conjunto, nome do conjunto, nível, índice nas folhas 5x2, id da túnica ou None, base: defesa, atributos e hp de referência,
#  nomes [capuz, calças, botas], bônus de 2 e 4 peças (ou 3 sem túnica), lore)
CONJUNTOS_PANO = [
 ("peregrino", "Trapos do Peregrino", 1, 0, "tunica_saco_peregrino", (1, {"vit":1}, 0), ["Capuz de Saco do Peregrino", "Calças Remendadas do Peregrino", "Botas de Trapo do Peregrino"],
  {"2":{"hp":10}, "4":{"hp":25, "defesa":1}}, "Tudo o que um peregrino tinha quando chegou a São Lázaro, e quase tudo o que tinha quando foi embora."),
 ("batedor_vela", "Lonas do Batedor da Vela", 3, 2, "gibao_batedor_vela", (2, {"agi":2,"vit":1}, 0), ["Capuz do Batedor da Vela", "Calças do Batedor da Vela", "Botas do Batedor da Vela"],
  {"2":{"agi":2}, "4":{"agi":3, "critico":0.01}}, "Lona de vela de bonde. Os batedores andam na frente da caravana, onde a areia ainda não decidiu se vai engolir o trilho."),
 ("bondeiro", "Fivelas do Bondeiro", 5, 1, "gibao_fivelas_bondeiro", (3, {"for":2,"vit":2}, 10), ["Capuz de Fivelas do Bondeiro", "Calças de Fivelas do Bondeiro", "Botas de Fivelas do Bondeiro"],
  {"2":{"for":2}, "4":{"for":3, "dano_plano":2}}, "Cada fivela segura alguma coisa: o mastro, a carga, o colega que caiu."),
 ("margem_amarga", "Folhas da Margem Amarga", 7, 5, "tunica_margem_amarga", (4, {"vit":3,"agi":2}, 20), ["Capuz da Margem Amarga", "Calças da Margem Amarga", "Botas da Margem Amarga"],
  {"2":{"res":{"veneno":0.05}}, "4":{"res":{"veneno":0.1}, "hp":40}}, "Tingido nas margens do Rio Amargo, onde as folhas crescem tortas e não morrem."),
 ("inverno_cinza", "Peles do Inverno de Cinza", 8, 8, None, (5, {"vit":4,"for":2}, 30), ["Capuz de Pele do Inverno de Cinza", "Calças de Pele do Inverno de Cinza", "Botas de Pele do Inverno de Cinza"],
  {"2":{"vit":3}, "3":{"vit":4, "reduz_dano":0.02}}, "Depois do clarão veio o inverno de cinza. Quem sobreviveu aprendeu a costurar pele de qualquer coisa que tivesse pelo."),
 ("vigia_anil", "Anil do Vigia", 9, 4, "tunica_vigia_anil", (5, {"esp":3,"vit":3}, 30), ["Capuz do Vigia Anil", "Calças do Vigia Anil", "Botas do Vigia Anil"],
  {"2":{"esp":2}, "4":{"esp":4, "defesa":2}}, "Anil e prata das torres de vigia. Os vigias bordavam a lua para lembrar que a noite ainda tem fim."),
 ("penitente_carmim", "Carmim do Penitente", 11, 3, "habito_penitente_carmim", (6, {"for":3,"vit":4}, 40), ["Capuz do Penitente Carmim", "Calças do Penitente Carmim", "Botas do Penitente Carmim"],
  {"2":{"roubo_de_vida":0.01}, "4":{"roubo_de_vida":0.02, "for":4}}, "Vermelho de flagelante. A roda bordada é a roda do suplício, e quem veste lembra dela a cada passo."),
 ("setimo_selo", "Violeta do Sétimo Selo", 13, 7, "sobreveste_setimo_selo", (7, {"esp":5,"vit":4}, 50), ["Capuz do Sétimo Selo", "Calças do Sétimo Selo", "Botas do Sétimo Selo"],
  {"2":{"dano_magico_extra":2}, "4":{"dano_magico_extra":4, "esp":5}}, "A lua crescente e a ametista são o sétimo selo. Quando ele abrir, haverá silêncio no céu por meia hora."),
 ("juizo_dourado", "Alva do Juízo Dourado", 15, 6, "alva_juizo_dourado", (9, {"for":3,"agi":3,"vit":4,"esp":4}, 70), ["Capuz do Juízo Dourado", "Calças do Juízo Dourado", "Botas do Juízo Dourado"],
  {"2":{"hp":40}, "4":{"hp":80, "reduz_dano":0.03}}, "Branco de altar e ouro de custódia. Feito para o dia do Juízo, que começou e não terminou."),
 ("regente_anil", "Coroa do Regente Anil", 17, 9, None, (10, {"esp":5,"vit":5,"agi":3}, 80), ["Capuz Coroado do Regente Anil", "Calças do Regente Anil", "Botas do Regente Anil"],
  {"2":{"esp":4}, "3":{"esp":6, "critico":0.02, "hp":60}}, "Um vigia que sobreviveu tanto tempo na torre que a cidade enterrada passou a chamá-lo de rei. Ele nunca aceitou a coroa; costurou-a no capuz."),
]
FRACAO_PANO = {"cabeca": (0.5, 0.5, 0.4), "calcas": (0.65, 0.6, 0.5), "botas": (0.45, 0.45, 0.35)}   # defesa, atributos, hp em relação à túnica

COLARES = [  # (id, nome, nível, índice na folha 5x2, atributos, bonus_fixo, lore)
 ("medalha_peregrino", "Medalha do Peregrino", 1, 0, {"vit":2}, {}, "Couro trançado e uma medalha de cruz gasta de tanto ser apertada na mão."),
 ("colar_presas_vala", "Colar de Presas da Vala", 3, 1, {"for":3}, {"dano_plano":1}, "Presas dos cães da Vala. Cada uma foi tirada de um que não vai voltar."),
 ("gota_carmim_martirio", "Gota Carmim do Martírio", 5, 2, {"for":3,"vit":2}, {"hp":15}, "Um rubi em forma de gota, preso em espinhos. Diz a Madre que é sangue de mártir que endureceu."),
 ("colar_raiz_amarga", "Colar da Raiz Amarga", 7, 7, {"vit":4,"agi":2}, {"hp":20,"res":{"veneno":0.08}}, "Raiz das margens do Rio Amargo, trançada em volta de uma esmeralda. Ainda brota folha nova toda semana."),
 ("pingente_lua_anil", "Pingente da Lua Anil", 9, 6, {"esp":5,"agi":3}, {"hp":25,"critico":0.01}, "Safiras e uma lua crescente de prata. Os vigias diziam que a lua era o único farol que a bomba não apagou."),
 ("sol_ambar", "Sol de Âmbar", 10, 3, {"esp":4,"vit":4}, {"hp":35,"res":{"sagrado":0.08}}, "Um sol de bronze com âmbar no centro. Esquenta a pele como o sol de antes, o que não queimava."),
 ("estrela_espinhos_violeta", "Estrela de Espinhos Violeta", 11, 4, {"esp":6,"vit":3}, {"hp":35,"dano_magico_extra":3}, "Ametista cravada numa estrela de espinhos. Os cultistas dizem que ela escuta as orações e responde com dor."),
 ("cranio_duque_chifrudo", "Crânio do Duque Chifrudo", 13, 5, {"for":7,"vit":4}, {"hp":45,"roubo_de_vida":0.02}, "O crânio de um duque da Legião Blasfema, ainda de olhos acesos. Ele não gosta de quem o carrega, e se vinga em quem bate em você."),
 ("asas_querubim_caido", "Asas do Querubim Caído", 15, 8, {"esp":6,"agi":4,"vit":4}, {"hp":60,"reduz_dano":0.02}, "As asas de um querubim que caiu no deserto, presas a uma custódia de ouro. As penas ainda tentam bater."),
 ("relicario_santo_acorrentado", "Relicário do Santo Acorrentado", 17, 9, {"for":5,"agi":5,"vit":5,"esp":5}, {"hp":80,"reduz_dano":0.03,"critico":0.02}, "Um santo que se levantou para o Juízo e foi acorrentado de volta ao relicário. A auréola ainda queima."),
]

ESPADAS = [  # (id, nome, nível, índice na folha 10x1, mult de dano, bonus_fixo, lore)
 ("espada_ferro_sangrento", "Espada de Ferro Sangrento", 2, 0, 1.0, {}, "Ferro de trilho que nunca parou de sangrar ferrugem vermelha."),
 ("espada_geada_atomica", "Espada da Geada Atômica", 4, 1, 1.03, {"res":{"fogo":0.05}}, "Forjada no inverno que veio depois do clarão. A lâmina ainda guarda o frio daquela noite."),
 ("espada_vazio_violeta", "Espada do Vazio Violeta", 6, 2, 1.06, {"dano_magico_extra":2}, "O olho violeta no punho não reflete nada. Os cultistas pagam caro para olhar dentro dele."),
 ("espada_custodia_solar", "Espada da Custódia Solar", 8, 3, 1.09, {"res":{"sagrado":0.08}}, "O punho é uma custódia de altar, com a hóstia trocada por um sol que não se apaga."),
 ("espada_fornalha", "Espada da Fornalha", 10, 4, 1.12, {"dano_plano":2}, "Tirada da fornalha da Legião Blasfema ainda em brasa. Nunca esfriou."),
 ("espada_amargo", "Espada do Amargo", 11, 5, 1.14, {"res":{"veneno":0.1}}, "Temperada nas águas do Rio Amargo. O verde corre por dentro da lâmina como veia."),
 ("espada_bobina_viva", "Espada da Bobina Viva", 12, 6, 1.16, {"velocidade_ataque":0.04}, "Um Tecnomancer enrolou uma bobina na lâmina por aposta. A bobina ganhou."),
 ("espada_firmamento_partido", "Espada do Firmamento Partido", 14, 7, 1.19, {"critico":0.02}, "Feita do pedaço de céu que rachou quando a terceira trombeta tocou. Dentro dela ainda tem estrelas."),
 ("espada_eclipse_rubro", "Espada do Eclipse Rubro", 16, 8, 1.22, {"roubo_de_vida":0.02}, "O sol negro no punho é o eclipse que anunciou a guerra. A lâmina bebe até a luz."),
 ("espada_juizo_acorrentado", "Espada do Juízo Acorrentado", 18, 9, 1.26, {"critico":0.03,"dano_plano":3}, "A espada que deveria encerrar o Juízo. Acorrentaram-na porque ninguém teve coragem de usá-la. Até agora."),
]
CLASSES_ESPADA = ["anjo", "demonio", "humano"]

DECRETO_VAMPIRICO = dict(id="decreto_vampirico", nome="Decreto Vampírico", slot="segunda_mao", tipo="grimorio", classes=["cultista"], nivel=12,
  raridade="lendario", grade=[2,2], atributos={"esp":8,"vit":4}, bonus_fixo={"hp":60,"roubo_de_vida":0.05,"dano_magico_extra":6},
  efeito="Skills que custam HP devolvem 25% do custo quando acertam.",
  lore="Um decreto lacrado com sangue e pregado com um punhal. Quem assinou nunca morreu, e cobra a assinatura de quem lê.",
  arte={"folha":"assets/icones/fontes/decreto_vampirico.png","indice":0,"grade":[1,1]})
CORTES_ESPADAS = [223, 407, 595, 817, 1005, 1211, 1396, 1634, 1884]   # as espadas têm larguras diferentes: fronteiras em px na folha

# ---------- Arte pronta, lote 3 (Jefin, 2026-10-16): ícones pintados para os itens que já existiam ----------
# Só troca o ícone; nome e status ficam como estão. Folhas armas_N.png na ordem do catálogo (entregas/arte_itens/catalogo).
# "auto": a folha não segue grade fixa; arte_pronta.py acha as peças pela silhueta e lê da esquerda para a direita, por linha.
ARTE_EXISTENTES = {
 "armas_1": ["espada_vigilia_rachada", "adaga_ritual_cega", "espada_escudeiro", "adaga_chaga", "lanca_procissao", "cajado_vertebras", "espada_sineiro", "escudo_porta_capela"],
 "armas_2": ["machado_placa_transito", "machado_bonde", "punhos_sucata", "cutelo_matadouro", "bacula_femur", "adaga_ossuario", "garras_ossario", "grimorio_acorrentado"],
 "armas_3": ["foice_serrilhada", "besta_sucata", "foice_penhor", "espada_serrilhada", "gancho_capataz", "corrente_gancho", "estandarte_legiao", "foice_sepultura"],
 "armas_4": ["espada_larga_sucata", "escopeta_cano_serrado", "escopeta_badalada", "escopeta_cano_duplo", "espada_larga_carrasco", "mosquete_pederneira", "montante_vigilia", "besta_repeticao"],
 "armas_5": ["cajado_antena_torto", "cajado_lampiao", "luva_voltaica", "pistola_raios", "cajado_valvulas"],
}
ARTE_EXISTENTES["acessorios_1"] = ["badalo_de_guerra", "lenco_cardo", "terco_lucio", "contador_isaura", "divisa_legiao", "faixa_vigilia", "fita_juizo", "selo_madre",
 "faixas_betania", "estilhaco_lacre", "diapasao_reverso", "pena_zacarias", "etiqueta_branca", "estilhaco_absinto", "chave_segunda_estrela", "faixa_de_linho_rafael",
 "pena_que_ficou"]
GRADE_FOLHA = {"acessorios_1": [8, 3]}   # folhas com peças coladas: grade fixa em vez de silhueta

# ---------- Relíquias Sangrentas (Jefin, 2026-10-16): 10 armas lendárias dos chefes, arte em reliquias_sangrentas.png (5x2) ----------
# (id, nome, classes, tipo, mãos, nível, índice, tag lendaria, grade, atributos, bonus_fixo, lore)
RELIQUIAS_SANGRENTAS = [
 ("lamina_primeiro_martir", "Lâmina do Primeiro Mártir", ["anjo","demonio","humano"], "espada", 1, 9, 0, "lendario:celeste", [1,3], {"for":6,"vit":4}, {"roubo_de_vida":0.03,"hp":40}, "A espada de quem morreu primeiro na Grande Batalha. O sangue dele nunca secou na lâmina, e ela não deixa o seu secar também."),
 ("unha_carpideira", "Unha da Carpideira", ["cultista"], "adaga", 1, 10, 1, "lendario:celeste", [1,2], {"esp":7,"agi":3}, {"dano_magico_extra":4,"critico":0.03}, "Irmã Celeste arranhava os caixões até a unha virar lâmina. Ainda chora quando corta."),
 ("raio_anunciacao", "Raio da Anunciação", ["anjo"], "espada", 1, 12, 2, "lendario:zacarias", [1,3], {"for":5,"esp":6,"vit":3}, {"res":{"sagrado":0.15},"dano_plano":4}, "O anjo que anunciou o fim trazia esta espada. O anúncio terminou; a luz na lâmina, não."),
 ("meia_lua_andras", "Meia-Lua de Andras", ["demonio"], "foice", 2, 8, 3, "lendario:general", [2,4], {"for":7,"agi":3}, {"critico":0.04,"roubo_de_vida":0.02}, "A foice com que Andras ceifava as próprias tropas quando recuavam. Ele perdeu as pernas; ela não perdeu o fio."),
 ("lanca_centuriao_calado", "Lança do Centurião Calado", ["anjo"], "lanca", 2, 11, 4, "lendario:zacarias", [1,4], {"for":6,"vit":5}, {"hp":60,"velocidade_ataque":0.04}, "O centurião que guardava a Trombeta Calada nunca disse uma palavra. A lança falava por ele."),
 ("espinha_coro_mudo", "Espinha do Coro Mudo", ["cultista"], "cajado", 2, 10, 5, "lendario:celeste", [1,4], {"esp":8,"vit":3}, {"dano_magico_extra":6,"hp":30}, "A coluna do regente do coro, com o crânio ainda aberto no último grito que ninguém ouviu."),
 ("porta_ossario", "Porta do Ossário", ["anjo"], "escudo", 1, 9, 6, "lendario:general", [2,2], {"vit":7,"for":2}, {"reduz_dano":0.05,"hp":50}, "A porta que fechava o ossário da cripta. Do lado de dentro, alguém ainda bate."),
 ("badalo_de_carne", "Badalo de Carne", ["mutante"], "machado", 2, 8, 7, "lendario:general", [2,3], {"for":8,"vit":4}, {"dano_plano":4,"hp":40}, "O badalo do sino do abatedouro, cravado de ganchos. Cada golpe toca uma missa que ninguém pediu."),
 ("alabarda_juramento", "Alabarda do Juramento Quebrado", ["mutante","demonio"], "lanca", 2, 11, 8, "lendario:zacarias", [1,4], {"for":7,"vit":5}, {"critico":0.03,"reduz_dano":0.02}, "Jurada para defender São Lázaro, entregue aos Arautos no mesmo dia. O rubi no centro ainda lembra das duas promessas."),
 ("machado_ultimo_bonde", "Machado do Último Bonde", ["mutante"], "machado", 2, 7, 9, "lendario:capataz", [2,3], {"for":7,"vit":3}, {"dano_plano":3,"velocidade_ataque":0.03}, "A placa do último bonde que saiu de São Lázaro antes do clarão. Ninguém sabe onde ele chegou; a placa voltou sozinha."),
]
ARTE_EXISTENTES["armaduras_1"] = ["veu_carpideira", "halo_incandescente", "elmo_rafael", "batina_remendada_luvas", "couro_sobrevivente_luvas",
 "placas_sino_luvas", "coro_mudo_luvas", "dragonas_general", "couraca_acougueiro_oco_luvas", "juramento_quebrado_luvas"]
GRADE_FOLHA["armaduras_1"] = [5, 2]
ARTE_EXISTENTES["consumiveis_1"] = ["pao_duro", "agua_doce", "tonico_graxa", "hostia_negra", "vela_simao", "agua_benta_polvora", "caldo_cardo_comum",
 "figo_anacleto", "pocao_vida_p", "pocao_recurso_p", "antidoto_querosene", "balas_chumbo", "virotes_prata", "cartuchos_sal",
 "pocao_vida_m", "pocao_recurso_m", "agua_benta", "vela_retorno", "gazua"]
AUTO_FOLHA = {"consumiveis_1": {"dilata": 0}}   # ajuste da silhueta quando as peças quase se encostam
ARTE_EXISTENTES["materiais_1"] = ["osso", "couro_podre", "sucata", "cinza_de_alma", "carne_estragada", "pedra_benta", "cera_de_vela", "pena_suja",
 "coagulo_caos", "engrenagem_viva", "chave_bau_ferro", "bau_de_ferro", "bau_faminto", "relicario_da_trombeta"]   # o Caixote Podre não veio na folha

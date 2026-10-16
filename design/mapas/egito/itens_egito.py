"""Saque dos chefes do Egito: relíquias exclusivas de cada chefe, dois conjuntos e os materiais da área.
Pedido do Jefin (16/10/2026): menos chance de drop e mais variedade. Cada chefe tem a sua lista (lendario:<chefe>),
com peso baixo nas tabelas; o resto cai da faixa 3 comum. Importado por conteudo_egito.py e dados_egito.py.
"""

ATTR = {"for": "for", "agi": "agi", "vit": "vit", "esp": "esp"}
CL_FIS = ["humano", "demonio", "mutante"]
CL_MAG = ["cultista", "anjo", "tecnomancer"]


def _stats(slot, nivel, foco, peso=1.0):
    """Números na escala da faixa 3 (nível 50-66); o mesmo molde dos itens com nome da área inicial."""
    a, b = foco
    base = nivel * 0.42 * peso
    at = {a: round(base), b: round(base * 0.6)}
    if slot == "arma":
        lo = round(nivel * 1.75 * peso); at = {"dano": [lo, round(lo * 1.65)], **at}
    elif slot in ("cabeca", "peito", "calcas", "botas", "luvas", "segunda_mao"):
        at["defesa"] = round(nivel * {"peito": 1.0, "calcas": .8, "cabeca": .7, "botas": .55, "luvas": .55, "segunda_mao": .9}[slot] * peso)
    else:
        at["hp"] = round(nivel * 5 * peso)
    return at


def item(i, nome, slot, nivel, foco, efeito, desc, chefe, classe=None, conjunto=None, peso=1.0):
    x = {"id": i, "nome": nome, "tipo": "equipamento", "slot": slot, "raridade": "unico", "classe": classe, "nivel": nivel,
         "origem": "drop:" + chefe, "atributos": _stats(slot, nivel, foco, peso), "efeito": efeito, "descricao": desc}
    if conjunto: x["conjunto"] = conjunto
    return x


# --------------------------------------------------------------------------- relíquias por chefe (4 na dungeon, 5 na raid)
POR_CHEFE = {
    "petsuchos": [
        item("argola_do_deus_crocodilo", "Argola do Deus Crocodilo", "anel", 51, ("vit", "for"), "Golpes recebidos acima de 10% da vida devolvem 20% do dano como sangramento.", "A outra argola de Petsuchos. Grande demais para um dedo, você usa no polegar.", "petsuchos"),
        item("escama_dourada_de_sobek", "Escama Dourada de Sobek", "peito", 51, ("vit", "for"), "Dentro da água: -15% de dano recebido e +10% de velocidade.", "Couraça feita das escamas que os sacerdotes douravam. Ainda brilha embaixo da lama.", "petsuchos"),
        item("arpao_do_juncal", "Arpão do Juncal", "arma", 51, ("agi", "for"), "O primeiro golpe em um alvo o puxa 1,5 m e deixa lento por 2 s.", "Arpão de bronze dos caçadores de hipopótamo, com corda de papiro trançado.", "petsuchos", classe=CL_FIS),
        item("cajado_da_cheia", "Cajado da Cheia", "arma", 51, ("esp", "vit"), "Skills de área deixam uma poça por 3 s que causa 20% do dano por segundo.", "Vara de nilômetro com as marcas das cheias, encharcada até o topo.", "petsuchos", classe=CL_MAG),
    ],
    "esfinge_de_hawara": [
        item("diadema_do_enigma", "Diadema do Enigma", "cabeca", 53, ("esp", "agi"), "A cada 20 s, a próxima skill não gasta recurso.", "Uma tiara de pedra com três glifos que mudam de lugar quando você pisca.", "esfinge_de_hawara"),
        item("garras_da_esfinge", "Garras da Esfinge", "luvas", 53, ("for", "agi"), "Críticos derrubam o alvo por 0,5 s (recarga 8 s por alvo).", "Luvas de couro de leão com garras de calcário costuradas nos dedos.", "esfinge_de_hawara"),
        item("selo_dos_doze_patios", "Selo dos Doze Pátios", "amuleto", 53, ("esp", "vit"), "+12% de dano contra construtos e guardiões de pedra.", "Doze pátios gravados num disco de faiança. No meio, um buraco do tamanho de uma resposta.", "esfinge_de_hawara"),
        item("lamina_da_pergunta", "Lâmina da Pergunta", "arma", 53, ("agi", "for"), "Golpes em alvos com mais de 80% de vida causam +25% de dano.", "Espada curta de pedra polida; a lâmina tem o perfil de um ponto de interrogação.", "esfinge_de_hawara", classe=CL_FIS),
    ],
    "serket": [
        item("ferrao_de_bronze", "Ferrão de Bronze", "arma", 54, ("agi", "for"), "Golpes aplicam 1 pilha de veneno (até 5); com 5, o alvo recebe +10% de dano.", "Adaga curva feita do ferrão de uma filha de Serket, encaixado num cabo de ébano.", "serket", classe=CL_FIS),
        item("cetro_que_abre_a_garganta", "Cetro que Abre a Garganta", "arma", 54, ("esp", "vit"), "Curas também removem um veneno ou sangramento do alvo.", "O cetro dos médicos de Serket: um escorpião de ouro com a cauda virada para cima.", "serket", classe=CL_MAG),
        item("couraca_de_quitina", "Couraça de Quitina", "peito", 54, ("vit", "agi"), "+30% de resistência a veneno; quem te ataca corpo a corpo leva 2% do dano em veneno.", "Placas de casca de escorpião gigante amarradas com tendão sobre linho grosso.", "serket"),
        item("ankh_de_serket", "Ankh de Serket", "amuleto", 54, ("esp", "vit"), "Abaixo de 25% de vida, cura 15% da vida máxima (recarga 90 s).", "Um ankh pequeno de turquesa, que acende quando você para de respirar.", "serket"),
    ],
    "sekhmet": [
        item("juba_da_leoa", "Juba da Leoa", "cabeca", 60, ("for", "vit"), "Cada golpe recebido dá 1% de dano (até 15%) por 6 s.", "Capacete de bronze com a juba de uma leoa de Sekhmet, ainda cheirando a sangue e cerveja.", "sekhmet"),
        item("presas_do_massacre", "Presas do Massacre", "arma", 60, ("for", "agi"), "Abaixo de 50% de vida: +12% de velocidade de ataque.", "Duas presas de leoa fundidas num punho de bronze. Pesam como raiva.", "sekhmet", classe=CL_FIS),
        item("taca_de_cerveja_ocre", "Taça de Cerveja Ocre", "segunda_mao", 60, ("esp", "vit"), "Poções curam 20% a mais e dão 4 s de imunidade a lentidão.", "Uma das sete mil jarras, reduzida a uma taça. O fundo nunca seca.", "sekhmet"),
        item("disco_do_sol_terco", "Disco do Sol Terço", "amuleto", 60, ("esp", "for"), "Dano de fogo e sagrado +10%.", "O disco que Sekhmet levava na cabeça, rachado em três como o sol de agora.", "sekhmet"),
        item("sandalias_de_mut", "Sandálias de Mut", "botas", 60, ("agi", "vit"), "+10% de velocidade por 3 s depois de matar um inimigo.", "Sandálias de couro tingido de ocre do templo de Mut, onde as estátuas de Sekhmet eram setecentas e trinta.", "sekhmet"),
    ],
    "janes": [
        item("bastao_que_virou_serpente", "Bastão que Virou Serpente", "arma", 61, ("esp", "agi"), "15% de chance de a skill invocar uma serpente por 6 s que copia 30% do seu dano.", "O bastão de Janes. Às vezes ele se mexe sozinho na sua mão. Às vezes morde.", "janes", classe=CL_MAG),
        item("anel_de_jambres", "Anel de Jambres", "anel", 61, ("esp", "vit"), "Quando um aliado do grupo morre perto, você recebe +20% de dano por 8 s.", "Um anel de cobre com dois nomes gravados. Um deles foi riscado e regravado.", "janes"),
        item("manto_dos_magos_de_farao", "Manto dos Magos de Faraó", "peito", 61, ("esp", "agi"), "Ao receber um feitiço, 10% de chance de refletir metade do dano.", "Linho bordado com fios de ouro e serpentes; cheira a incenso e a derrota.", "janes"),
        item("luvas_da_imitacao", "Luvas da Imitação", "luvas", 61, ("agi", "esp"), "A skill usada logo depois de uma esquiva custa metade.", "Luvas finas de mago, feitas para copiar gestos alheios.", "janes"),
        item("cimitarra_de_janes", "Cimitarra de Janes", "arma", 61, ("for", "agi"), "Golpes contra conjuradores interrompem e silenciam 1 s (recarga 10 s).", "A espada que o mago carregava escondida debaixo do manto, para quando os encantamentos falhassem.", "janes", classe=CL_FIS),
    ],
    "imseti": [
        item("tampa_de_hapi", "Tampa de Hapi", "cabeca", 62, ("vit", "esp"), "+15% de vida máxima.", "A tampa do vaso dos pulmões, com cabeça de babuíno. Respira-se melhor com ela.", "imseti"),
        item("arco_de_qebehsenuef", "Arco de Qebehsenuef", "arma", 62, ("agi", "for"), "Ataques a mais de 6 m causam +15% de dano.", "Arco de chifre com a cabeça de falcão do guardião dos intestinos esculpida no punho.", "imseti", classe=CL_FIS),
        item("escudo_de_duamutef", "Escudo de Duamutef", "segunda_mao", 62, ("vit", "for"), "Cura 1% da vida máxima por segundo enquanto você não se mexe.", "Escudo de couro de chacal esticado num aro de bronze, com o rosto do guardião do estômago.", "imseti"),
        item("vaso_de_imseti", "Vaso de Imseti", "amuleto", 62, ("esp", "vit"), "-12% de dano recebido enquanto houver um aliado a menos de 5 m.", "O vaso do fígado em miniatura, com rosto de homem. Imseti, o único dos quatro com cara de gente.", "imseti"),
        item("cetro_dos_quatro", "Cetro dos Quatro Filhos", "arma", 62, ("esp", "vit"), "Cada aliado do grupo a menos de 8 m dá +3% de dano mágico (até 12%).", "Cetro com quatro cabeças nos quatro lados: homem, babuíno, chacal e falcão.", "imseti", classe=CL_MAG),
    ],
    "apofis": [
        item("escama_do_caos", "Escama do Caos", "peito", 63, ("vit", "esp"), "-20% de dano sombrio; no escuro, +8% de esquiva.", "Uma escama de Apófis do tamanho de um escudo, que engole a luz da tocha.", "apofis"),
        item("olho_que_apaga", "Olho que Apaga", "amuleto", 63, ("esp", "agi"), "Críticos cegam o alvo por 1,5 s (recarga 12 s).", "Um olho de serpente petrificado. Quem olha nele esquece por um instante para onde ia.", "apofis"),
        item("remo_da_barca_de_ra", "Remo da Barca de Rá", "arma", 63, ("for", "vit"), "Golpes em área empurram os inimigos 1 m e dão 5% de defesa por inimigo atingido.", "Um remo de cedro dourado da barca do sol. Serve de arma e de juramento.", "apofis", classe=CL_FIS),
        item("brasa_da_proa", "Brasa da Proa", "arma", 63, ("esp", "for"), "Skills de fogo deixam o alvo em brasa: +10% de dano de fogo recebido por 4 s.", "Uma brasa da lanterna de Rá presa num cajado de ferro. Nunca apaga.", "apofis", classe=CL_MAG),
        item("botas_da_setima_hora", "Botas da Sétima Hora", "botas", 63, ("agi", "esp"), "Ao virar de costas para um inimigo, ganha 1 s de imunidade a atordoamento (recarga 15 s).", "Botas de couro escuro de quem atravessou a sétima hora da noite e voltou.", "apofis"),
    ],
    "anubis_pesador": [
        item("mascara_do_chacal", "Máscara do Chacal", "cabeca", 64, ("esp", "for"), "Inimigos abaixo de 20% de vida aparecem marcados e recebem +8% de dano.", "A máscara negra que os embalsamadores usavam, com orelhas de chacal e olhos de ouro.", "anubis_pesador"),
        item("pena_de_maat_viva", "Pena de Maat Viva", "amuleto", 64, ("esp", "vit"), "Curas em quem tem menos vida que você curam 15% a mais.", "Uma pena que pesa exatamente o certo. Ela se inclina para quem precisa.", "anubis_pesador"),
        item("prato_do_coracao", "Prato do Coração", "segunda_mao", 64, ("vit", "for"), "Bloqueia 10% de todo dano; se você estiver com mais vida que o atacante, 20%.", "Um dos pratos da balança do Salão das Duas Verdades, transformado em escudo.", "anubis_pesador"),
        item("faixas_do_embalsamador", "Faixas do Embalsamador", "calcas", 64, ("vit", "agi"), "Ao cair abaixo de 15% de vida, fica imune a dano por 1,5 s (recarga 120 s).", "Linho de múmia embebido em resina, enrolado com as orações certas.", "anubis_pesador"),
        item("garra_de_ammit", "Garra de Ammit", "arma", 64, ("for", "agi"), "Matar um inimigo cura 4% da vida máxima.", "Uma garra de leão com escamas de crocodilo, arrancada da Devoradora quando ela pulou cedo demais.", "anubis_pesador", classe=CL_FIS),
    ],
    "farao_sem_nome": [
        item("cajado_das_dez_pragas", "Cajado das Dez Pragas", "arma", 65, ("esp", "vit"), "A cada 10 skills usadas, a próxima solta uma praga aleatória no alvo (sangue, piolhos, peste ou trevas).", "O cajado do Faraó, com dez anéis de bronze. Cada um tem o nome de uma praga.", "farao_sem_nome", classe=CL_MAG),
        item("khopesh_do_coracao_duro", "Khopesh do Coração Duro", "arma", 65, ("for", "vit"), "Imune a medo e provocação; +1% de dano por 1% de vida que falta ao alvo acima de 50%.", "A espada-foice do Faraó. Não tem nome gravado. Tem dez entalhes.", "farao_sem_nome", classe=CL_FIS),
        item("cartucho_sem_nome", "Cartucho Sem Nome", "amuleto", 65, ("esp", "for"), "+10% de dano; o seu nome some da lista de alvos dos chefes por 3 s ao usar uma poção (recarga 60 s).", "Um cartucho real de ouro, raspado até ficar liso. Quem usa também fica um pouco esquecido.", "farao_sem_nome"),
        item("nemes_do_farao", "Nemes do Faraó", "cabeca", 65, ("vit", "esp"), "+20% de resistência a todos os efeitos de controle.", "O lenço listrado de azul e ouro dos reis, esfarrapado na ponta, com a serpente da coroa arrancada.", "farao_sem_nome"),
        item("anel_do_primogenito", "Anel do Primogênito", "anel", 65, ("for", "agi"), "Ao sobreviver a um golpe que seria mortal, fica com 1 de vida e invisível por 2 s (recarga 300 s).", "O anel de um príncipe que morreu na décima praga. Ainda está quente.", "farao_sem_nome"),
    ],
}

# --------------------------------------------------------------------------- conjuntos (caem de qualquer chefe da sua masmorra)
CONJUNTOS = [
    {"id": "regalia_de_sobek", "nome": "Regalia de Sobek", "nivel": 52, "chefes": ["petsuchos", "esfinge_de_hawara", "serket"],
     "bonus": {"2": "+8% de vida máxima", "3": "+10% de dano contra animais e sagrados", "5": "Golpes têm 10% de chance de prender o alvo como um crocodilo (1 s)"},
     "pecas": [("coroa_de_sobek", "Coroa de Sobek", "cabeca", ("vit", "for")), ("peitoral_de_sobek", "Peitoral de Sobek", "peito", ("vit", "for")),
               ("saiote_de_sobek", "Saiote de Sobek", "calcas", ("vit", "agi")), ("sandalias_de_sobek", "Sandálias de Sobek", "botas", ("agi", "vit")),
               ("braceletes_de_sobek", "Braceletes de Sobek", "luvas", ("for", "agi"))],
     "lore": "O que os sacerdotes de Crocodilópolis vestiam para alimentar o deus: ouro, couro de crocodilo e linho encharcado."},
    {"id": "regalia_do_farao", "nome": "Regalia do Faraó Sem Nome", "nivel": 62, "chefes": ["sekhmet", "janes", "imseti", "apofis", "anubis_pesador", "farao_sem_nome"],
     "bonus": {"2": "+10% de defesa", "4": "+8% de dano", "6": "Dez Nãos: a cada 10 s, o próximo golpe recebido é reduzido em 50%", "8": "Coração Endurecido: imune a controle por 3 s a cada 30 s"},
     "pecas": [("pschent_do_farao", "Pschent do Faraó", "cabeca", ("vit", "esp")), ("peitoral_de_ouro", "Peitoral de Ouro e Lápis", "peito", ("vit", "for")),
               ("shendyt_real", "Shendyt Real", "calcas", ("vit", "agi")), ("sandalias_de_papiro_real", "Sandálias de Papiro Real", "botas", ("agi", "vit")),
               ("braceletes_do_ureu", "Braceletes do Ureu", "luvas", ("for", "esp")), ("colar_usekh", "Colar Usekh", "amuleto", ("esp", "vit")),
               ("anel_de_sinete_real", "Anel de Sinete Real", "anel", ("for", "esp")), ("cetro_heka", "Cetro Heka", "segunda_mao", ("esp", "for"))],
     "lore": "As insígnias de um rei cujo nome foi raspado de toda parte. As peças não lembram de quem eram; lembram que eram de um rei."},
]


def itens_conjuntos():
    out = []
    for c in CONJUNTOS:
        for i, nome, slot, foco in c["pecas"]:
            x = item(i, nome, slot, c["nivel"], foco, "Peça do conjunto " + c["nome"] + ".", c["lore"], c["chefes"][0], conjunto=c["id"], peso=0.9)
            x["origem"] = "drop:" + ",".join(c["chefes"]); x["raridade"] = "raro"
            out.append(x)
    return out


# --------------------------------------------------------------------------- materiais (formato itens_data.MATERIAIS da thread de Skills/itens)
MATERIAIS = [
    dict(id="couro_do_nilo", tag="material:couro_do_nilo", nome="Couro do Nilo", motivo="couro", tint="couro", lore="Couro de crocodilo curtido na lama preta. Não rasga e não esquece o cheiro do rio."),
    dict(id="casca_de_escaravelho", tag="material:casca_de_escaravelho", nome="Casca de Escaravelho", motivo="sucata", tint="latao", lore="Furta-cor como óleo na água. Os ourives de Mênfis pagam por peso."),
    dict(id="linho_de_mumia", tag="material:linho_de_mumia", nome="Linho de Múmia", motivo="pano", tint="pano", lore="Faixas de três mil anos, ainda com resina. Os curandeiros juram que fecham ferida."),
    dict(id="bronze_antigo", tag="material:bronze_antigo", nome="Bronze Antigo", motivo="sucata", tint="latao", lore="Pedaços de estátua sem rosto. Besankh derrete; os com rosto, não."),
    dict(id="po_de_calcario", tag="material:po_de_calcario", nome="Pó de Calcário de Tura", motivo="cinza", tint="osso", lore="O revestimento branco das pirâmides, moído. Brilhava ao sol quando havia sol."),
    dict(id="ouro_de_sobek", tag="material:ouro_de_sobek", nome="Ouro de Sobek", motivo="joia", tint="ouro", lore="Lascas dos brincos e pulseiras dos crocodilos sagrados. Ouro de deus, molhado."),
    dict(id="fragmento_do_duat", tag="material:fragmento_do_duat", nome="Fragmento do Duat", motivo="cinza", tint="alma", lore="Um pedaço de noite do mundo dos mortos. Pesa nada e esfria a mão."),
]


def todas_reliquias():
    return [x for v in POR_CHEFE.values() for x in v]


def pools():
    p = {f"lendario:{c}": [x["id"] for x in v] for c, v in POR_CHEFE.items()}
    for c in CONJUNTOS: p[f"lendario:{c['id']}"] = [i for i, *_ in c["pecas"]]
    return p

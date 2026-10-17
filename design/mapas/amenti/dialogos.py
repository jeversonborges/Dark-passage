"""Falas dos Salões de Amenti: a Esfinge das 3 perguntas (na entrada, mapa egito) e os dois Lordes intocáveis da Antecâmara.
Sem missão e sem farm (pedido do Jefin): ninguém explica o que há atrás do Portão. Gera entregas/amenti/conteudo_amenti.json
no formato de design/missoes/dados e confere com o validar.py da thread de Missões numa cópia (não edita design/missoes).
Uso: python3 dialogos.py"""
import json, os, shutil, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SAIDA = os.path.join(RAIZ, "entregas", "amenti", "conteudo_amenti.json")

def op(t, ir=None, se=None, acoes=None):
    o = {"texto": t}
    if ir: o["ir"] = ir
    if se: o["se"] = se
    if acoes: o["acoes"] = acoes
    return o
ERRO = [{"definir_flag": "esfinge_calada"}]   # o jogo deve limpar esta flag depois de 24 h (ver INTEGRACAO)

NPCS = [
    {"id": "esfinge_amenti", "nome": "A Esfinge", "titulo": "A que guarda a casa de baixo", "faccao": "neutro", "classe_visual": "humano",
     "visual_prop": "esfinge", "local": {"subzona": "gize", "ponto": "patas_da_esfinge"}, "servicos": [], "dialogo": "dlg_esfinge_amenti",
     "aparencia": "Não aparece. É a voz que sai da pedra entre as patas da Esfinge, grave, sem boca que se mexa. A areia em volta treme quando ela fala.",
     "personalidade": "Paciente, exata, sem piedade. Faz três perguntas e não repete nenhuma.",
     "historia": "Thoth a pôs ali quando desceu aos Salões de Amenti pela última vez. Ela não guarda tesouro: guarda a pergunta de quem quer descer."},
]

AREA = {"id": "saloes_de_amenti", "nome": "Salões de Amenti", "tipo": "dungeon", "nivel": None,
        "descricao": "Debaixo da casa que Thoth ergueu em Khem. Quem desce não sobe pelo mesmo caminho. Não há missão, não há farm: "
                     "há seis salas e um Portão que nunca abriu.",
        "musica_sugerida": "drone grave quase inaudível, coro distante sem palavras, um sino de vidro a cada minuto",
        "subzonas": [{"id": i, "nome": n, "tipo": "dungeon"} for (i, n) in [
            ("vestibulo_do_livro", "Vestíbulo do Livro"), ("salao_do_universo", "O Salão do Universo"), ("o_vazio", "O Vazio"),
            ("camaras_sombrias", "As Câmaras Sombrias"), ("salao_da_flor_da_vida", "O Salão da Flor da Vida"),
            ("antecamara_dos_portoes", "A Antecâmara dos Portões")]]}

DIALOGOS = [
    {"id": "dlg_esfinge_amenti", "npc": "esfinge_amenti", "inicio": "raiz", "nos": {
        "raiz": {"fala": [{"se": {"flag": "amenti_aberto"}, "texto": "A casa de baixo já te ouviu. Desce, ou não desce. Eu não pergunto duas vezes."},
                          {"se": {"flag": "esfinge_calada"}, "texto": "(A pedra está fria. A Esfinge não responde hoje.)"},
                          {"se": {"tem_item": "livro_de_thoth"}, "texto": "Tu trazes o Livro de quem me pôs aqui. Então respondes. Três perguntas. Uma resposta errada, e eu me calo por um dia."},
                          {"texto": "Areia. Silêncio. Entre as patas, a pedra tem a forma de uma porta e nenhuma fechadura."}],
                 "opcoes": [op("Pergunta.", "p1", {"tem_item": "livro_de_thoth"}), op("(Ir embora.)")]},
        "p1": {"fala": "Primeira. O que está embaixo...",
               "opcoes": [op("...é como o que está em cima.", "p2"), op("...é o que foi enterrado.", "erro", acoes=ERRO),
                          op("...é o inferno.", "erro", acoes=ERRO)]},
        "p2": {"fala": "Segunda. Os de Khem o chamaram Thoth. Os de além do mar o chamaram de outro nome. Quantas vezes grande?",
               "opcoes": [op("Uma, e basta.", "erro", acoes=ERRO), op("Três vezes grande.", "p3"), op("Sete, uma por coluna.", "erro", acoes=ERRO)]},
        "p3": {"fala": "Terceira. O Livro que trazes tem as páginas em branco. Quando a letra acende?",
               "opcoes": [op("Quando a lua cheia bate nele.", "erro", acoes=ERRO), op("Quando alguém lê em voz alta.", "certo"),
                          op("Quando quem o escreveu voltar.", "erro", acoes=ERRO)]},
        "certo": {"fala": "Então lê. A pedra desce. Quem desce não sobe pelo mesmo caminho, e a porta de baixo fecha atrás de quem passa. O que há no fundo, eu nunca vi. Só vi quem subiu de lá: um escriba de cabeça de íbis, coberto de areia do tempo, que passou por mim sem perguntar nada.",
                  "opcoes": [op("Descer.", acoes=[{"definir_flag": "amenti_aberto"}])]},
        "erro": {"fala": "(A Esfinge se cala. A areia para de tremer.)", "opcoes": [op("(Ir embora.)")]},
    }},
    {"id": "dlg_lider_dos_anjos", "npc": "lider_dos_anjos", "inicio": "raiz", "nos": {
        "raiz": {"fala": [{"se": {"faccao": "arautos"}, "texto": "Servo. Chegaste longe. Não te ajoelhes: aqui embaixo não há para quem."},
                          {"texto": "Uma vela. Desceu até aqui acesa. Que curioso."}],
                 "opcoes": [op("O que tem atrás do Portão?", "portao"), op("Por que vocês não lutam?", "lutar"),
                            op("Quem decide o Juízo?", "juizo"), op("(Afastar-se.)")]},
        "portao": {"fala": "O que sempre esteve. Eu já vi. Ele também diz que já viu. Um de nós mente, e eu não minto.", "opcoes": [op("Voltar.", "raiz")]},
        "lutar": {"fala": "Porque o primeiro que levantar a mão perde. Isso está escrito no Portão, do lado de dentro.", "opcoes": [op("Voltar.", "raiz")]},
        "juizo": {"fala": "Ninguém. Por isso esperamos. Quando alguém decidir, saberemos quem foi, porque estará do lado de lá.", "opcoes": [op("Voltar.", "raiz")]},
    }},
    {"id": "dlg_lider_dos_demonios", "npc": "lider_dos_demonios", "inicio": "raiz", "nos": {
        "raiz": {"fala": [{"se": {"faccao": "arautos"}, "texto": "Um dos nossos! Ou um dos dele. Daqui de cima vocês são todos do mesmo tamanho, inseto."},
                          {"texto": "Inseto. Desceu até aqui só para olhar para mim? Eu entendo. Olhe à vontade."}],
                 "opcoes": [op("O que tem atrás do Portão?", "portao"), op("Onde está o general da Legião?", "general"),
                            op("Ele disse que nunca mente.", "mente"), op("(Afastar-se.)")]},
        "portao": {"fala": "Tudo. Ou nada. Abre e me conta. Ah, não abre? Que pena. Nem para mim abre, e eu sou eu.", "opcoes": [op("Voltar.", "raiz")]},
        "general": {"fala": "Do lado de lá. Ou do lado de cá, olhando pra você agora. Pergunte ao Perfeito: ele adora responder o que não sabe.", "opcoes": [op("Voltar.", "raiz")]},
        "mente": {"fala": "E você acreditou? Ele disse isso a Thoth também. Thoth dobrou um continente para não precisar ouvir de novo.", "opcoes": [op("Voltar.", "raiz")]},
    }},
]


def gerar():
    out = {"_doc": "Conteúdo dos Salões de Amenti no formato de design/missoes/dados. Cada bloco é acrescentado no arquivo de mesmo nome. "
                   "Sem missões e sem farm, por pedido do Jefin. Gerado e validado por design/mapas/amenti/dialogos.py.",
           "locais.areas": [AREA], "npcs.npcs": NPCS, "dialogos.dialogos": DIALOGOS}
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(out, open(SAIDA, "w"), ensure_ascii=False, indent=1)
    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(RAIZ, "design", "missoes"), os.path.join(tmp, "missoes"))
    os.makedirs(os.path.join(tmp, "mapas"))
    shutil.copy(os.path.join(RAIZ, "design", "mapas", "spots.json"), os.path.join(tmp, "mapas", "spots.json"))
    shutil.copytree(os.path.join(RAIZ, "design", "mapas", "mata_do_granizo"), os.path.join(tmp, "mapas", "mata_do_granizo"))
    D = os.path.join(tmp, "missoes", "dados")
    # o livro_de_thoth vem do pacote da Atlântida: soma junto para a validação
    atl = json.load(open(os.path.join(RAIZ, "entregas", "atlantida", "conteudo_missoes.json"), encoding="utf-8"))
    blocos = {k: v for k, v in atl.items() if not k.startswith("_")}
    # a subzona "gize" (Esfinge) vem do pacote do Egito
    egl = os.path.join(RAIZ, "entregas", "egito", "conteudo", "locais_acrescimo.json")
    if os.path.exists(egl): blocos["locais.areas"] = blocos["locais.areas"] + json.load(open(egl, encoding="utf-8"))["areas"]
    for k, v in out.items():
        if not k.startswith("_"): blocos[k] = blocos.get(k, []) + v
    # defs de NPC dos Lordes (thread do Egito), com a subzona da Antecâmara
    lp = os.path.join(RAIZ, "entregas", "warlord", "lordes", "objetos_lordes.json")
    if os.path.exists(lp):
        lor = json.load(open(lp, encoding="utf-8"))["npcs_acrescimo"]
        for n in lor: n["local"]["subzona"] = "antecamara_dos_portoes"
        blocos["npcs.npcs"] = blocos.get("npcs.npcs", []) + lor
    for chave, bloco in blocos.items():
        arq, campo = chave.split(".")
        p = os.path.join(D, f"{arq}.json"); d = json.load(open(p, encoding="utf-8"))
        d[campo] = d[campo] + bloco
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, os.path.join(tmp, "missoes", "validar.py")], capture_output=True, text=True)
    print(r.stdout[-2500:], r.stderr[-1500:])
    shutil.rmtree(tmp)


if __name__ == "__main__":
    gerar()

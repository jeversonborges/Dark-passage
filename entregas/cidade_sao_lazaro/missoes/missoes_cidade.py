#!/usr/bin/env python3
"""Missões novas da Cidade de São Lázaro (Vigília) + o que os dados de missões precisam saber do mapa novo.

Acrescenta, sem mexer no que existe:
  - 5 missões da Vigília (vc01 a vc05) com os diálogos de oferta, entrega e 'falar';
  - subzonas patio_bondes, vila_militar e chiqueiros (área sao_lazaro) e o objeto matriz_sao_lazaro;
  - os 3 spots novos em locais.json > spots > pedidos (cemiterio_bondes, alameda_ciprestes, casas_da_vila).

Uso:  python3 missoes_cidade.py <pasta design/missoes>        (aplica nos dados/ dessa pasta)
      python3 missoes_cidade.py --teste                        (aplica numa cópia temporária e roda o validar.py)
Quem aplica de verdade é a thread de Missões ou a Prévia, junto com o mapa novo."""
import json, os, sys, shutil, tempfile, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
PF = "/mnt/project-files"

MISSOES = [
 {"id": "vc01", "titulo": "Noite Nova na Cidade", "tipo": "principal", "faccao": "vigilia", "nivel": 1,
  "doador": "zulmira_faroleira", "entrega": "zulmira_faroleira", "requer": [],
  "resumo": "Apresente-se à Capitã Odete, ao Gaspar e à Isaura.",
  "descricao": "BILHETE DA VELA · DITADO AO PIRRALHO · NOITE 11.214 DO IMPASSE\nRecruta. A cidade é grande para quem chega e pequena para quem fica. Antes de sair pela Cerca, deixe que ela saiba o seu passo.\nA Capitã na estação, o ferreiro na Rua do Mercado, a moça do rádio no prédio da beira. Cada um vai olhar para você de um jeito. Volte e me conte como.\nEnquanto houver vela, não é noite.\n— Nhá Zulmira, Faroleira da Vela (escreveu o Pirralho, que errou duas letras)",
  "objetivos": [{"tipo": "falar", "npc": "capita_odete"}, {"tipo": "falar", "npc": "gaspar_bigorna"}, {"tipo": "falar", "npc": "isaura_radialista"}],
  "recompensas": {"xp": 250, "ouro": 10, "itens": [{"id": "pao_duro", "qtd": 3}, {"id": "agua_doce", "qtd": 1}]},
  "texto_conclusao": "A Zulmira escutou o seu relato de olhos fechados, que é o único jeito que ela tem. \"A Odete mediu suas botas, o Gaspar mediu suas mãos e a Isaura não olhou para você\", disse. \"Então ela gostou.\""},
 {"id": "vc02", "titulo": "Cobre dos Bondes", "tipo": "secundaria", "faccao": "vigilia", "nivel": 3,
  "doador": "capita_odete", "entrega": "capita_odete", "requer": ["v01"],
  "resumo": "Limpe o Cemitério de Bondes para a Cerca recuperar o cobre dos vagões.",
  "descricao": "DESPACHO DA VELA · Nº 7 · ANO 31 DO IMPASSE\nNo ramal morto do Pátio dos Bondes há trinta vagões com fiação de cobre. A Vela come cobre. Os corvos fizeram ninho nos mastros e os Carniçais dormem dentro dos bancos.\nDesocupe o pátio. A turma do Bento entra atrás de você com alicate.\nNão quebre os vagões. Um dia eles voltam a andar.\n— C. O. Ferrolho, Capitã da Cerca",
  "objetivos": [{"tipo": "farmar_spot", "spot": "cemiterio_bondes", "qtd": 12}, {"tipo": "matar", "alvo": "corvo_de_cinza", "qtd": 6}],
  "recompensas": {"xp": 900, "ouro": 35, "itens": [{"id": "tonico_graxa", "qtd": 5}]},
  "texto_conclusao": "A turma do Bento tirou quarenta metros de fio antes de amanhecer. A Odete enrolou o primeiro metro no pulso, como quem guarda um terço. \"Esse aqui é seu\", disse, e não deu."},
 {"id": "vc03", "titulo": "O Sino da Matriz", "tipo": "secundaria", "faccao": "vigilia", "nivel": 5,
  "doador": "gaspar_bigorna", "entrega": "gaspar_bigorna", "requer": [],
  "resumo": "Toque o último sino da Matriz e derrube os Não-Julgados que vierem atrás do som.",
  "descricao": "CADERNO DA FORJA · FOLHA SOLTA · ANO 31 DO IMPASSE\nA Matriz tinha sete sinos. Seis viraram bala. O sétimo os Sineiros não deixam fundir: dizem que é ele que avisa o Juízo de que ainda tem gente aqui.\nEu preciso saber se ele está rachado antes de discutir com eles. Suba pela rosácea e bata uma vez. Uma só.\nOs mortos ouvem sino. Leve munição.\n— G. Bigorna, ferreiro da Cerca",
  "objetivos": [{"tipo": "interagir", "objeto": "matriz_sao_lazaro", "subzona": "acampamento_vela", "qtd": 1}, {"tipo": "matar", "alvo": "nao_julgado", "qtd": 8, "etapa": 2}],
  "recompensas": {"xp": 1500, "ouro": 45, "itens": [{"id": "tonico_graxa", "qtd": 5}, {"id": "pao_duro", "qtd": 5}]},
  "texto_conclusao": "O sino não estava rachado. O Gaspar ficou um tempo calado, com o martelo parado no ar. \"Então fica\", disse. \"Bala eu arrumo em outro lugar. Sino que ainda canta, não.\""},
 {"id": "vc04", "titulo": "Os Nomes do Alto", "tipo": "secundaria", "faccao": "vigilia", "nivel": 6,
  "doador": "simao_coveiro", "entrega": "simao_coveiro", "requer": ["v04"],
  "resumo": "Acalme os mortos da Alameda dos Ciprestes para o Simão reescrever os nomes.",
  "descricao": "CADERNO DO COVEIRO · PÁGINA DOBRADA · SEM DATA\nNo alto do morro ficam as famílias antigas da paróquia. A areia apagou os nomes das lápides, e quem não tem nome não sabe para onde voltar.\nEles andam pela alameda procurando a própria cova. Deite-os, com respeito. Eu subo depois com o cinzel.\nOs corvos do mausoléu são mais velhos que eu acho que sou. Não brigue com eles à toa.\n— Simão, coveiro",
  "objetivos": [{"tipo": "farmar_spot", "spot": "alameda_ciprestes", "qtd": 15}],
  "recompensas": {"xp": 3000, "ouro": 70, "itens": [{"id": "vela_simao", "qtd": 2}]},
  "texto_conclusao": "O Simão gravou os nomes sem consultar livro nenhum. Você reparou que ele sabia a data de cada um, e o apelido, e de que lado do rosto cada um ria."},
 {"id": "vc05", "titulo": "O Último Turno", "tipo": "secundaria", "faccao": "vigilia", "nivel": 9,
  "doador": "isaura_radialista", "entrega": "isaura_radialista", "requer": ["d03"],
  "resumo": "Limpe as Casas da Vila, onde moravam os oficiais do silo.",
  "descricao": "RÁDIO SÃO LÁZARO · FORA DO AR · NOITE 11.231 DO IMPASSE\n(sem estática; ela escreveu à mão) O turno da noite do silo morava na vila. Eu dividia o rádio com eles. Eles saíram para o turno e não voltaram, e as casas ficaram esperando.\nAgora tem apóstata sangrando gente nas cozinhas deles. Eu não quero as casas de volta. Quero que ninguém mais use aquelas mesas.\n— Isaura Valente",
  "objetivos": [{"tipo": "farmar_spot", "spot": "casas_da_vila", "qtd": 15}],
  "recompensas": {"xp": 6000, "ouro": 120, "itens": [{"id": "agua_doce", "qtd": 4}]},
  "texto_conclusao": "A Isaura não perguntou como estavam as casas. Perguntou se o relógio da cozinha do Capitão Moura ainda funcionava. Funcionava. Ela desligou o rádio pela primeira vez desde que você chegou."},
]

DLG = {   # npc -> (oferta, aceito, entrega) por missão
 "vc01": ("(ela estende a mão no escuro até achar o seu ombro) Recém-chegado. Ainda cheira a estrada. A cidade precisa ouvir o seu passo antes de confiar nele. Vá falar com a Odete, com o Gaspar e com a Isaura. Depois volte.",
          "Vá com os pés leves. O vidro ouve.", "Então eles já sabem quem você é. Agora a Vela também sabe. Pode sair pela Cerca."),
 "vc02": ("Trinta vagões no ramal morto, cheios de cobre e de bicho. A Vela come cobre. Desocupe o Cemitério de Bondes e a turma do Bento entra atrás.",
          "Não quebre os vagões.", "Quarenta metros de fio. A Vela agradece, e eu também, o que é mais raro."),
 "vc03": ("Seis sinos da Matriz viraram bala. O sétimo os Sineiros não deixam tocar. Preciso saber se ele está rachado. Sobe pela rosácea e bate uma vez.",
          "Uma vez só. E leve munição.", "Inteiro? (ele larga o martelo) Então fica. Sino que ainda canta não vai para a forja."),
 "vc04": ("Os mortos do alto não lembram mais o próprio nome. Andam pela Alameda dos Ciprestes procurando a cova. Deite-os com respeito; eu subo com o cinzel.",
          "Com respeito.", "Obrigado. Agora eles sabem para onde voltar. Eu também, às vezes."),
 "vc05": ("As Casas da Vila. O turno da noite do silo morava lá. Tem apóstata sangrando gente nas cozinhas deles. Faça isso parar.",
          "Não traga nada de lá.", "(ela desliga o rádio) Obrigada. Hoje eu não vou contar a noite."),
}
FALAR = {"capita_odete": "A Nhá Zulmira me mandou me apresentar.", "gaspar_bigorna": "A Nhá Zulmira me mandou me apresentar.",
         "isaura_radialista": "A Nhá Zulmira me mandou me apresentar."}
RESP = {"capita_odete": "(ela mede suas botas de cima a baixo) Botas de estrada. Vão gastar rápido aqui. Seu nome vai para o Livro da Cerca quando você merecer um.",
        "gaspar_bigorna": "(ele pega a sua mão, vira a palma, solta) Mão de quem nunca segurou martelo. Tudo bem. Por aqui a gente aprende segurando arma.",
        "isaura_radialista": "(ela não tira o fone do ouvido) Noite onze mil duzentos e catorze. Mais um. Anotado."}

def aplicar(dados):
    J = lambda n: json.load(open(os.path.join(dados, n), encoding="utf-8"))
    mis, dl, loc, obj, mon = J("missoes.json"), J("dialogos.json"), J("locais.json"), J("objetos.json"), J("monstros.json")
    ids = {q["id"] for q in mis["missoes"]}
    mis["missoes"] += [q for q in MISSOES if q["id"] not in ids]
    D = {d["npc"]: d for d in dl["dialogos"]}
    for q in MISSOES:
        d = D[q["doador"]]; raiz = d["nos"][d["inicio"]]; qid = q["id"]
        of, ac, fim = DLG[qid]
        if f"{qid}_oferta" in d["nos"]: continue
        d["nos"][f"{qid}_oferta"] = {"fala": of, "opcoes": [{"texto": "Deixa comigo.", "acoes": [{"aceitar_missao": qid}], "ir": f"{qid}_aceita"}, {"texto": "Agora não."}]}
        d["nos"][f"{qid}_aceita"] = {"fala": ac, "opcoes": [{"texto": "Até logo."}]}
        d["nos"][f"{qid}_fim"] = {"fala": fim, "opcoes": [{"texto": "Feito.", "acoes": [{"concluir_missao": qid}]}]}
        raiz["opcoes"][-1:-1] = [{"texto": q["titulo"] + "?", "ir": f"{qid}_oferta", "se": {"missao_disponivel": qid}},
                                 {"texto": "Está feito.", "ir": f"{qid}_fim", "se": {"missao_pronta": qid}}]
    for npc, txt in FALAR.items():
        d = D[npc]; raiz = d["nos"][d["inicio"]]
        if "vc01_falar" in d["nos"]: continue
        d["nos"]["vc01_falar"] = {"fala": RESP[npc], "opcoes": [{"texto": "Voltar.", "ir": d["inicio"]}]}
        raiz["opcoes"].insert(0, {"texto": txt, "ir": "vc01_falar", "se": {"missao_ativa": "vc01"}, "acoes": [{"cumprir_falar": "vc01"}]})
    area = next(a for a in loc["areas"] if a["id"] == "sao_lazaro")
    subs = {s["id"] for s in area["subzonas"]}
    for s in [{"id": "patio_bondes", "nome": "Pátio dos Bondes", "tipo": "caca", "nivel": [2, 4],
               "descricao": "O ramal morto onde a companhia largava os bondes quebrados. A maré de areia cobriu metade dos vagões; os corvos fazem ninho nos mastros.",
               "monstros": ["corvo_de_cinza", "carnical"]},
              {"id": "vila_militar", "nome": "Vila Militar do Silo", "tipo": "caca", "nivel": [8, 10],
               "descricao": "As casas dos oficiais do Silo São Lázaro, com as sombras do clarão gravadas nas paredes. Os apóstatas fizeram das cozinhas um altar.",
               "monstros": ["nao_julgado", "sangrador_apostata"]},
              {"id": "chiqueiros", "nome": "Chiqueiros", "tipo": "caca", "nivel": [4, 6],
               "descricao": "Cercas de chapa e lama na frente do Abatedouro Carniça.", "monstros": ["porco_pestilento"]}]:
        s["monstros"] = [m for m in s["monstros"] if m in {x["id"] for x in mon["monstros"]}]
        if s["id"] not in subs: area["subzonas"].append(s)
    for s in area["subzonas"]:
        if s["id"] == "acampamento_vela":
            s["nome"] = "Cidade de São Lázaro"
            s["descricao"] = ("A cidade da Vigília, em cima da cidade afogada: a rua de hoje é o telhado de ontem. No meio, a Igreja Matriz enterrada até o coro, "
                              "com a Praça da Vela na porta. A Linha 7 corta a cidade e para na Estação de cúpula de vidro; a Rádio da Isaura fica no prédio da beira do precipício.")
            for p in ("matriz_sao_lazaro", "porta_matriz", "radio_sao_lazaro"):
                if p not in s.setdefault("pontos", []): s["pontos"].append(p)
    ped = loc.setdefault("spots", {}).setdefault("pedidos", [])
    MONS = {x["id"] for x in mon["monstros"]}
    for sp in [{"id": "cemiterio_bondes", "nome": "Cemitério de Bondes", "subzona": "patio_bondes", "nivel": [2, 4], "monstros": ["corvo_de_cinza", "carnical"], "missoes": ["vc02"]},
               {"id": "alameda_ciprestes", "nome": "Alameda dos Ciprestes", "subzona": "cemiterio_sao_lazaro", "nivel": [5, 7], "monstros": ["nao_julgado", "corvo_de_cinza"], "missoes": ["vc04"]},
               {"id": "casas_da_vila", "nome": "Casas da Vila", "subzona": "vila_militar", "nivel": [8, 10], "monstros": ["sangrador_apostata", "nao_julgado"], "missoes": ["vc05"]}]:
        sp["monstros"] = [m for m in sp["monstros"] if m in MONS]
        if sp["id"] not in {p["id"] for p in ped}: ped.append(sp)
    if "matriz_sao_lazaro" not in {o["id"] for o in obj["objetos"]}:
        obj["objetos"].append({"id": "matriz_sao_lazaro", "nome": "Rosácea da Matriz", "subzona": "acampamento_vela",
                               "texto_ao_usar": "Você desce pela rosácea quebrada por uma escada de corda. Lá embaixo, na nave cheia de areia, o sétimo sino espera pendurado numa viga. Uma batida. O som desce pela areia e alguma coisa lá fora responde.",
                               "visivel_se": {"missao_ativa": "vc03"}})
    for n, o in (("missoes.json", mis), ("dialogos.json", dl), ("locais.json", loc), ("objetos.json", obj)):
        json.dump(o, open(os.path.join(dados, n), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("aplicado em", dados)

if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        t = tempfile.mkdtemp()
        shutil.copytree(f"{PF}/design/missoes", f"{t}/design/missoes", ignore=shutil.ignore_patterns("__pycache__"))
        os.makedirs(f"{t}/design/mapas", exist_ok=True)
        shutil.copy(f"{PF}/design/mapas/sao_lazaro/spots.json", f"{t}/design/mapas/spots.json")
        shutil.copytree(f"{PF}/design/mapas/mata_do_granizo", f"{t}/design/mapas/mata_do_granizo")
        aplicar(f"{t}/design/missoes/dados")
        r = subprocess.run([sys.executable, f"{t}/design/missoes/validar.py"], capture_output=True, text=True)
        print(r.stdout[-3000:], r.stderr[-2000:]); sys.exit(r.returncode)
    aplicar(os.path.join(sys.argv[1], "dados"))

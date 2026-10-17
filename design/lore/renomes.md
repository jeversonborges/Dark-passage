# Renomes de exibição (lore, 17/10/2026)

Só o campo `nome` e as menções em texto mudam. **Nenhum id muda**: o jogo e o servidor leem os ids. Já aplicado em
`design/missoes/dados/*.json` (validar.py OK). A Prévia sincroniza depois que a 0.9.3 sair (`game/tools/sync.sh`);
se algum nome estiver escrito à mão em `game/` ou em mapas gerados, usar esta lista de/para.

Motivos: crítica `criticas/nomes.md` (Ent é de Tolkien; nomes colidindo com facção/instituição; muletas "de Cinza",
"Brasa", "Filho/Filha/Cria"; dois Bento e dois coveiros; dois Ferrolho; Abatedouro x Matadouro).

| id | de | para |
|---|---|---|
| ent_de_cinza | Ent-de-Cinza | Tronco Penitente |
| (subzona Novo Éden) | Clareira do Ent | Clareira do Tronco |
| sineiro_do_coro | Sineiro do Coro | Badaleiro do Coro |
| porao_matadouro (andar da cripta) | Porão do Matadouro | Porão do Abatedouro |
| bento_fel | Bento Fel, o Coveiro do Amargo | Crispim Fel, o Enterrador do Amargo |
| lobo_de_cinza | Lobo de Cinza | Lobo da Queimada |
| javali_brasa | Javali-Brasa | Javali Tição |
| cao_de_brasa | Cão de Brasa da Legião | Mastim da Legião |
| filha_de_serket | Filha de Serket | Escorpião de Serket |
| cria_do_duat | Cria do Rio do Duat | Anel de Apófis |
| filho_do_hissopo | Filho do Hissopo | Hissopo Levantado |
| pirralho_ferrolho | Ferrolho | Ferrolhinho (a Capitã Odete lhe deu o sobrenome; está na `historia`) |
| spot pocilga_de_gadara | Pocilga de Gadara | Chiqueiro de Gadara |
| madre_brasilia | Madre Brasília da Comunhão | Madre Urze da Comunhão (Jefin: "nome ridículo"; urze é a planta que só cresce depois da queimada) |

## Pendente de decisão do Jefin

- **Vigilantes** (os duzentos anjos de Enoque no Hermon) x **Vigília** (facção). Card na thread de lore com as
  opções Irin / Insones / manter. Afeta: Cume dos Vigilantes, Fosso dos Vigilantes, Vigilante Acorrentado,
  Vigilante Desfeito, Naamá, a Noiva dos Vigilantes, Convite dos Vigilantes, Testemunha do Juramento (não muda),
  textos do evento Hermon (entregas/evento_hermon/dados.json).

## Mantidos de propósito (o crítico pediu, eu discordo)

- **Sombra Gravada**: é cânone (historia.md §1.2, o clarão da Absinto-1 gravou as sombras no muro) e é imagem
  concreta, não abstração.
- **O Perfeito / O Soberbo**: são os Lordes do Jefin (entregas/warlord). Ganham origem e ofício nos dossiês, não
  nome novo.
- **O Vazio** (Salões de Amenti): conceito hermético da Atlântida; fica.
- **Corvo de Cinza, Corvo de Brasa, Campos de Cinza, Neve de Cinza**: cortei as outras muletas; estes carregam
  história própria.
- **Margens do Lago Sagrado, Eira das Duas Colheitas, Lagoa dos Elefantes**: não são duplicatas, são spots dentro
  da subzona com o mesmo nome; a hierarquia é legítima.
- **"Coro" como mob**: não existe em monstros.json; o crítico leu errado.
- Nomes-ferramenta da Vigília (Graxa, Bigorna, Prumo, Calço, Catraca...): são personagens já falados e
  reconhecidos pelo Jefin; regra nova no guia impede que o padrão cresça, sem trocar os que existem.

## Decidido pelo Jefin (17/10, card): Vigilantes → Irin

Aplicado em `design/missoes/dados/*.json` e `entregas/evento_hermon/dados.json` (só texto; ids `vigilante_*`,
`fosso_dos_vigilantes`, `cume_dos_vigilantes` ficam). "Irin" é invariável: os Irin, um Irin.

| de | para |
|---|---|
| O Cume dos Vigilantes | O Cume dos Irin |
| Fosso dos Vigilantes | Fosso dos Irin |
| Vigilante Acorrentado / Desfeito | Irin Acorrentado / Desfeito |
| Naamá, a Noiva dos Vigilantes | Naamá, a Noiva dos Irin |
| Convite dos Vigilantes | Convite dos Irin |
| Elo de Vigilante / Ferro de Vigilante | Elo de Irin / Ferro de Irin |

Para a Prévia: textos do evento em `game/` (avisos das 19h, nome do evento no cliente) e o LEIAME de
`entregas/evento_hermon` ainda dizem Vigilantes; sincronizar depois da 0.9.3.

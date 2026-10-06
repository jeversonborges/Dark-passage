"""Acentua as descricoes (o codigo fica em ASCII; o .json sai em portugues correto)."""
import re
A = dict(Agua='Água', Ascensao='Ascensão', Bau='Baú', Carapaca='Carapaça', Clarao='Clarão', Danacao='Danação',
 Demonio='Demônio', graus='graus',  Po='Pó', Nao='Não', lampada='lâmpada', Ladrilhavel='Ladrilhável', ladrilhavel='ladrilhável', veu='véu', ancora='âncora', graos='grãos', transparencia='transparência', demonio='demônio', Tocar='Tocar', Forca='Força', Fumaca='Fumaça', Furia='Fúria', Graca='Graça', Juizo='Juízo', Lamina='Lâmina', Giratorio='Giratório', disfarcado='disfarçado', ATRAS='ATRÁS',
 Maquina='Máquina', Pisao='Pisão', Poca='Poça', Polvora='Pólvora', Portao='Portão', Regeneracao='Regeneração',
 Sentenca='Sentença', Setimo='Sétimo', Ultimo='Último', Tracante='Traçante',
 acida='ácida', acidas='ácidas', acido='ácido', amaldicoada='amaldiçoada', aneis='anéis', apos='após', area='área',
 ate='até', atras='atrás', baixas='baixas', cabeca='cabeça', ceu='céu', chao='chão', circulo='círculo', clarao='clarão',
 continua='contínua', contrario='contrário', critico='crítico', cupula='cúpula', duracao='duração', eletrica='elétrica',
 eletrico='elétrico', eletricos='elétricos', estagio='estágio', estilhacos='estilhaços', explosao='explosão',
 faiscas='faíscas', fumaca='fumaça', invocacao='invocação', invulneravel='invulnerável', juizo='juízo', lamina='lâmina',
 lancas='lanças', lendario='lendário', linguas='línguas', maquina='máquina', municao='munição', mutacao='mutação',
 nanomaquinas='nanomáquinas', nevoa='névoa', nivel='nível', pedacos='pedaços', pes='pés', po='pó', poca='poça',
 pocao='poção', polvora='pólvora', pustulas='pústulas', rapido='rápido', sao='são', saida='saída', tracante='traçante',
 tres='três', triangulo='triângulo', ultimo='último', valioso='valioso', voo='voo', estalos='estalos', quitina='quitina')
def acentuar(s):
    s = re.sub(r'[A-Za-z]+', lambda m: A.get(m.group(0), m.group(0)), s)
    return s.replace(' a noite', ' à noite')

# nomes curtos para efeitos que nao sao skills (skills usam o nome antes dos dois-pontos)
TITULOS = dict(
 golpe_impacto='Impacto de golpe', golpe_corte='Corte em arco', golpe_critico='Acerto crítico',
 sangue_jorro='Jorro de sangue', sangue_poca='Poça de sangue', faiscas_bloqueio='Faíscas de bloqueio',
 disparo_cano='Clarão de disparo', fumaca_tiro='Fumaça de pólvora', projetil_bala='Bala traçante',
 impacto_bala='Impacto de bala', esquiva_poeira='Poeira de esquiva', morte_monstro='Morte de monstro',
 status_veneno='Envenenado', status_sangramento='Sangrando', status_queimando='Em chamas',
 status_atordoado='Atordoado', status_lentidao='Lento e preso',
 item_brilho_excelente='Brilho de item excelente', item_brilho_raro='Brilho de item raro',
 item_brilho_lendario='Brilho de item lendário', item_brilho_tecnico='Brilho de item de set',
 item_feixe_raro='Feixe de drop raro', item_feixe_lendario='Feixe de drop lendário', bau_abertura='Baú abrindo',
 level_up='Subida de nível', cura_generica='Cura recebida',
 chefe_aviso_area='Aviso de área', chefe_aviso_cone='Aviso em cone', chefe_aviso_linha='Aviso em linha',
 chefe_onda_choque='Pisão do chefe', chefe_meteoro='Meteoro', chefe_portal='Fenda de invocação',
 chefe_furia='Fúria do chefe', chefe_raio_ceu='Raio do céu', chefe_escudo='Casca invulnerável',
 chefe_morte='Morte de chefe', cult_sangria_projetil='Sangria (projétil)', cult_sangria_impacto='Sangria (impacto)',
 hum_corte_largo_tras='Corte Giratório (atrás)', hum_corte_largo_frente='Corte Giratório (frente)', hum_arrancada='Arrancada',
 tec_torreta_invocacao='Torreta Sentinela', tec_torreta_disparo='Torreta Sentinela (disparo)',
 aura_anjo='Aura do Anjo', aura_demonio='Aura do Demônio', aura_cultista='Aura do Cultista',
 aura_humano='Aura do Humano', aura_mutante='Aura do Mutante', aura_tecnomancer='Aura do Tecnomancer')

def titulo(name, desc):
    return TITULOS.get(name) or desc.split(':')[0].strip().rstrip('.')

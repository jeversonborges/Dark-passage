# Revisão da lore do site (`site/publico/index.html`, 17/10/2026)

Veredito: o site está no tom certo. Usa a abertura canônica (Crônica do Emparedado), as vozes (Despacho nº 0,
Versículo da Retirada, Rádio das 03h11, Caderno do Coveiro), cita só o que existe no jogo e não promete nada fora
dele. As sete classes e as duas facções estão como no cânone. Nada a cortar.

## Feito

- "duzentos Vigilantes" e "Os Vigilantes se levantam" → **Irin** (decisão do Jefin, ver `renomes.md`). Só texto.

## Para a thread do site (não alterei)

1. **A Torre.** O bloco "A Torre, Repetidora do Granizo" diz que "foi por esta torre que passou a ordem que lançou a
   ogiva", fala numa "Congregação da Portadora" e dá aos chefes epítetos diferentes dos de `monstros.json`
   (site: "Ferrabrás, o Guarda-Linhas", "Madre Urze, a Voz da Portadora", "Baraquiel, o Que Respondeu";
   dados: Centurião Ferrabrás, Madre Urze da Comunhão, Baraquiel, o Arauto do Granizo; faltam no site o
   Telegrafista e Malaquias). No cânone a ordem da ogiva foi lida por Isaura no Silo São Lázaro, e a Torre do Éden
   é a torre de vigia de incêndio e rádio do Tadeu. Sugestão: alinhar o site aos dados (nomes dos cinco chefes
   como no JSON) e manter a frase "A sétima trombeta não é de metal. É uma frequência." como **boato**, assinado
   ("Dizem na Congregação da Portadora"), porque é um gancho bom e o cânone já admite que a sétima "nem é de metal".
2. **Nova seção "A Crônica inteira".** O Livro do Impasse (`design/lore/LIVRO_DO_IMPASSE.md`, versão diagramada em
   https://claude.ai/artifact/LLpriiS7s5Mk91hHtLzspZ) pode virar a página de lore do site: um link "Ler a Crônica
   do Emparedado" abaixo da abertura. O HTML já existe no artifact; é copiar o `<style>` e o corpo para
   `publico/cronica.html`, sem dependências (fontes do Google são as únicas externas; o site hoje não usa fontes
   externas, então conferir se a VPS permite ou embutir).
3. **Texto do Warlord**: "Os Arautos pregam ordem, a Vigília abraça o caos" é a frase das referências do Jefin; no
   cânone é o contrário (a Vigília é a cerca, a ordem improvisada; os Arautos são três exércitos que se odeiam).
   Para o Warlord, que despreza os dois, a frase funciona como opinião dele. Sugiro assinar: "— dito de um Warlord".

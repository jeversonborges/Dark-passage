# Branch `servidor`

Só o pacote do servidor dedicado do DARK PASSAGE. A VPS (darkpassage.com.br) faz `git pull` deste branch a cada 2 minutos e reinicia o jogo quando muda.

- `servidor/DarkPassage-servidor.pck`: export "Servidor Linux" (sem texturas nem áudio), roda com Godot 4.4.1:
  `godot --headless --main-pack servidor/DarkPassage-servidor.pck -- servidor=1 max=48`
- `servidor/VERSAO`: versão que o servidor aceita; clientes de outra versão recebem "Atualize o jogo".

Não edite à mão: é gerado pela thread do jogo a cada versão.

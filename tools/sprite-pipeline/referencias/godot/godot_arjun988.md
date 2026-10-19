<!-- Fonte: texto colado pelo Jefin em 2026-10-19 (skill "godot", snapshot 2026-06-19). Não está em nenhum repo em vendor/ (a única correspondência, godot-export, é outra skill). O texto colado veio cortado na seção "Quick Patterns": o resto precisa de nova colagem. -->
---
name: godot
description: Godot game engine development skill, a dated snapshot tracking the current stable Godot (4.x, currently 4.7).
tags: [game, godot, gdscript]
date: 2026-06-19
---

# Godot Development

Skill com snapshot datado. Os paradigmas (GDScript tipado, TileMapLayer no lugar de TileMap, sintaxe de anotação, call-down-signal-up) mudam devagar. Os números de versão e as mudanças por release mudam rápido, então precisam ser reconferidos.

## Snapshot e atualidade
- Snapshot em 2026-06-19, alvo Godot 4.x com 4.7 como estável atual.
- Antes de qualquer coisa, conferir a versão do projeto em `project.godot` (`config/features`). Não assumir de memória.
- Regra de atualidade: se a data de `Verified` de um arquivo de referência estiver velha, ou saiu uma minor nova, tratar as afirmações de versão como suspeitas e conferir nas release notes oficiais.

## Regras centrais
1. Sempre tipar (static typing): mais rápido e pega erro no parse.
2. Usar TileMapLayer, não TileMap (TileMap está depreciado desde 4.3).
3. Sintaxe de anotação: `@export`, `@onready`, `@tool`.
4. Sintaxe de sinal atual: `signal.connect(callable)`, `signal.emit()`.
5. Call down, signal up: pai chama filho, filho emite sinal.
6. Nunca combinar `@onready` com `@export` (o `@onready` sobrescreve o valor exportado).

## Estrutura de projeto sugerida
    res://
      scenes/      .tscn com .gd junto
      scripts/     autoload/, data/ (class_name Resource), systems/
      resources/   .tres organizados por tipo
      assets/      sprites/, tilesets/, audio/

## Arquivos de referência (no skill original)
- Linguagem e projeto: gdscript, architecture, scene-tree, file-formats, editor-tooling, pitfalls
- Sistemas de jogo: physics, input, math, navigation, tilemaplayer, multiplayer, 3d
- Apresentação: ui, animation, audio, shaders, particles
- Dados e entrega: persistence, performance, testing, workflow

## Padrão de função tipada
    func calculate(base: float, mult: float) -> float:   # (trecho cortado no texto colado)

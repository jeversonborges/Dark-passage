#!/bin/bash
f="$1"
case "$f" in
  ./musica/*) opts="-ac 2 -q:a 0";;
  ./ambiente/*) opts="-ac 1 -q:a 0";;
  *) opts="-ac 1 -q:a 1";;
esac
ffmpeg -loglevel error -y -i "$f" -c:a libvorbis $opts "${f%.ogg}.tmp.ogg" && mv "${f%.ogg}.tmp.ogg" "$f"

# Frames de vídeo (não versionados)

Os frames não entram no repositório, para não pesar. Só vale extrair quando houver um vídeo real de cavalo em locomoção.
Comando, a partir da pasta `referencias/locomocao/` com o vídeo ao lado:

    mkdir -p video_frames && ffmpeg -i <video>.mp4 -vf fps=10 video_frames/frame_%04d.png

O vídeo enviado em 2026-10-19 é uma escultura de capacete em ZBrush, não um cavalo. Foi removido do repositório e serve só para acabamento de placa de barda.

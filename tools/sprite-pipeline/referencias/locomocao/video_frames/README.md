# Frames do horse_video.mp4

Os 588 PNGs (10 fps, 360x640, cerca de 90 MB) não foram versionados, para não pesar o repositório.
Para gerar de novo, a partir da pasta `referencias/locomocao/`:

    mkdir -p video_frames && ffmpeg -i horse_video.mp4 -vf fps=10 video_frames/frame_%04d.png

Nos frames de galope, o intervalo de 100 ms (10 fps) é o usado para comparar quadro a quadro.

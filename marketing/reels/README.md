# Рилс «8 бесплатных уроков об уюте»

`python3 marketing/reels/make_reel.py` → `soul-of-home-reels-8-urokov.mp4` (1080×1920, 30 fps, ~39 с).
Тексты уроков — список `LESSONS` в начале скрипта, картинки берутся из `docs/img/`.
Нужны: Python 3 с Pillow и fontTools (+ brotli), ffmpeg, шрифт Lora (путь — переменная `LORA_TTF`).
`python3 marketing/reels/make_reel.py preview` — несколько кадров для проверки вёрстки без сборки видео.

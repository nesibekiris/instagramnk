# Stratri Reels — kaynak dosyalar
- `index.html`: animasyonun kendisi. Tarayıcıda açınca oynatıcı ve zaman çubuğuyla önizlenir. Metinler `TEXT`, zamanlamalar `T` nesnesinde.
- `node render.js stills 2 9.5 ...`: belirtilen saniyelerden PNG kare alır ve `preview/` klasörüne yazar.
- `node render.js video 30`: 1080×1920, 30 fps MP4 üretir ve `output/` klasörüne yazar (Playwright + ffmpeg, ücretsiz).
- `KREATIF_BRIEF.md`: araştırma, fikirler, storyboard.

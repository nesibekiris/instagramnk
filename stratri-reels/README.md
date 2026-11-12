# Stratri Reels — kaynak dosyalar
- `v1_sakin.html`: animasyonun kendisi. Tarayıcıda açınca oynatıcı ve zaman çubuğuyla önizlenir. Metinler `TEXT`, zamanlamalar `T` nesnesinde.
- `node render.js stills 2 9.5 ...`: belirtilen saniyelerden PNG kare alır ve `preview/` klasörüne yazar.
- `node render.js video 30`: 1080×1920, 30 fps MP4 üretir ve `output/` klasörüne yazar (Playwright + ffmpeg, ücretsiz).
- `KREATIF_BRIEF.md`: araştırma, fikirler, storyboard.

## v2 (güncel): "Kim onayladı?"
- `index.html`: 27 sn, 120 BPM, sert kesmeler ve ritme oturan kinetik tipografi. Metinler `TEXT`, çekim zamanları `SHOTS` nesnesinde.
- `python3 make_audio.py`: telifsiz, sentezlenmiş ses izi üretir (`output/audio.wav`).
- Birleştirme: `node render.js video 30` ve ardından `ffmpeg -i output/stratri_reels.mp4 -i output/audio.wav -c:v copy -c:a aac -shortest output/final.mp4`
- `v1_sakin.html`: ilk, sakin versiyon.

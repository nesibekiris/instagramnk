# Yapay Zekâ Yönetişimi — Kısa Video Üretici

Ücretsiz araçlarla (Python + Pillow + ffmpeg) 1080x1920 dikey Reels/TikTok videosu üretir.

## Yeni video yapmak
1. `scripts/` içindeki bir `.json` dosyasını kopyalayın, metinleri değiştirin.
2. `python3 make_video.py scripts/yeni_dosya.json`
3. Video `output/` klasörüne düşer. Müziği Instagram/TikTok uygulamasında ekleyin (trend sesler oradan eklenince erişim artar).

## Sahne tipleri
- `hook`: iki satırlık açılış sorusu (`line1`, `line2`)
- `statement`: tek vurucu cümle (`text`, isteğe bağlı `label`)
- `list`: numaralı maddeler (`title`, `items`)
- `levels`: renkli seviye/merdiven (`title`, `levels`: [ad, açıklama])
- `cta`: kapanış ve buton (`text`, `button`)

Her sahnede `duration` (saniye) zorunludur.

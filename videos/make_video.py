"""Ücretsiz araçlarla (Pillow + ffmpeg) dikey kısa video üretir.
Kullanım: python3 make_video.py scripts/ornek.json
Senaryo dosyası sahnelerden oluşur; her sahne bir "tip" ve metinler içerir.
"""
import json, subprocess, sys, math, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
def font(weight, size):
    return ImageFont.truetype(FONT_DIR + f"Inter-{weight}.otf", size)

THEME = {
    "bg": (14, 17, 28), "bg2": (24, 30, 48), "text": (245, 246, 250),
    "muted": (150, 160, 185), "accent": (120, 220, 190), "warn": (255, 120, 110),
}
LEVEL_COLORS = [(255, 95, 95), (255, 170, 80), (250, 215, 90), (120, 220, 190)]

def ease(t):  # 0..1 -> 0..1, yumuşak çıkış
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= maxw: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def background(t, handle):
    img = Image.new("RGB", (W, H), THEME["bg"])
    d = ImageDraw.Draw(img)
    # yavaş hareket eden yumuşak daire
    cx = W * 0.7 + math.sin(t * 0.4) * 120
    cy = H * 0.25 + math.cos(t * 0.3) * 160
    for r in range(520, 0, -40):
        a = int(18 * (1 - r / 520))
        c = tuple(min(255, THEME["bg"][i] + a * (1 if i != 0 else 0.4).__int__()) for i in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(THEME["bg"][0] + a // 3, THEME["bg"][1] + a, THEME["bg"][2] + a))
    d.text((80, H - 150), handle, font=font("Medium", 34), fill=THEME["muted"])
    return img, d

def draw_text_block(d, lines_spec, t, top):
    """lines_spec: [(text, fontobj, color, delay)] -> kelime kelime belirerek yazar."""
    y = top
    for text, fnt, color, delay in lines_spec:
        for line in wrap(d, text, fnt, W - 160):
            x = 80
            for i, word in enumerate(line.split()):
                p = ease((t - delay - i * 0.06) / 0.35)
                if p > 0:
                    col = tuple(int(THEME["bg"][k] + (color[k] - THEME["bg"][k]) * p) for k in range(3))
                    d.text((x, y + (1 - p) * 40), word, font=fnt, fill=col)
                x += d.textlength(word + " ", font=fnt)
            y += int(fnt.size * 1.22)
            delay += 0.06 * len(line.split())
        y += 30
    return y

def scene_frame(sc, t, handle, progress, idx, total):
    img, d = background(t + idx * 3, handle)
    kind = sc["type"]
    big, mid, small = font("Bold", 92), font("SemiBold", 62), font("Medium", 46)
    if kind == "hook":
        draw_text_block(d, [(sc["line1"], big, THEME["text"], 0.0),
                            (sc["line2"], big, THEME["accent"], 0.9)], t, 620)
    elif kind == "statement":
        y = 520
        if sc.get("label"):
            d.text((80, y), sc["label"].upper(), font=font("Bold", 40), fill=THEME["accent"]); y += 90
        draw_text_block(d, [(sc["text"], mid if len(sc["text"]) > 60 else big, THEME["text"], 0.1)], t, y)
    elif kind == "list":
        ty = 360
        for ln in wrap(d, sc["title"], font("Bold", 72), W - 160):
            d.text((80, ty), ln, font=font("Bold", 72), fill=THEME["text"]); ty += 88
        y = 560
        for i, item in enumerate(sc["items"]):
            p = ease((t - 0.5 - i * sc.get("step", 1.1)) / 0.4)
            if p <= 0: continue
            off = (1 - p) * 120
            d.rounded_rectangle([80 + off, y, W - 80 + off, y + 170], 28, fill=THEME["bg2"])
            d.text((120 + off, y + 48), str(i + 1), font=font("Bold", 64), fill=THEME["accent"])
            lines = wrap(d, item, small, W - 360)
            ty = y + 85 - len(lines) * 28
            for ln in lines:
                d.text((220 + off, ty), ln, font=small, fill=THEME["text"]); ty += 56
            y += 200
    elif kind == "levels":
        ty = 260
        for ln in wrap(d, sc["title"], font("Bold", 64), W - 160):
            d.text((80, ty), ln, font=font("Bold", 64), fill=THEME["text"]); ty += 80
        y = max(520, ty + 80)
        for i, (name, desc) in enumerate(sc["levels"]):
            p = ease((t - 0.5 - i * 1.0) / 0.4)
            if p <= 0: continue
            wbar = int((W - 160) * (1 - i * 0.12) * p)
            col = LEVEL_COLORS[i % 4]
            d.rounded_rectangle([80, y, 80 + max(wbar, 60), y + 110], 24, fill=col)
            d.text((115, y + 25), name, font=font("Bold", 52), fill=THEME["bg"])
            d.text((90, y + 130), desc, font=font("Medium", 40), fill=THEME["muted"])
            y += 250
    elif kind == "cta":
        draw_text_block(d, [(sc["text"], mid, THEME["text"], 0.1)], t, 640)
        p = ease((t - 1.5) / 0.5)
        if p > 0:
            bw = d.textlength(sc["button"], font=font("Bold", 56)) + 120
            x0 = (W - bw) / 2; y0 = 1250 + (1 - p) * 60
            d.rounded_rectangle([x0, y0, x0 + bw, y0 + 130], 65, fill=THEME["accent"])
            d.text((x0 + 60, y0 + 32), sc["button"], font=font("Bold", 56), fill=THEME["bg"])
    # üst ilerleme çubuğu + sahne sayacı
    d.rectangle([0, 0, W, 12], fill=THEME["bg2"])
    d.rectangle([0, 0, int(W * progress), 12], fill=THEME["accent"])
    d.text((W - 200, H - 150), f"{idx + 1}/{total}", font=font("Medium", 34), fill=THEME["muted"])
    return img

def render(script_path):
    cfg = json.load(open(script_path, encoding="utf-8"))
    scenes, handle = cfg["scenes"], cfg.get("handle", "")
    total_dur = sum(s["duration"] for s in scenes)
    out = os.path.join(os.path.dirname(__file__), "output",
                       os.path.splitext(os.path.basename(script_path))[0] + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
           "-c:a", "aac", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    elapsed = 0.0
    for idx, sc in enumerate(scenes):
        n = int(sc["duration"] * FPS)
        for f in range(n):
            t = f / FPS
            img = scene_frame(sc, t, handle, (elapsed + t) / total_dur, idx, len(scenes))
            fade = min(1.0, t / 0.2, (sc["duration"] - t) / 0.2)
            if fade < 1: img = Image.blend(Image.new("RGB", (W, H), THEME["bg"]), img, max(0, fade))
            proc.stdin.write(img.tobytes())
        elapsed += sc["duration"]
    proc.stdin.close(); proc.wait()
    print("Hazır:", out, f"({total_dur:.0f} sn)")

if __name__ == "__main__":
    for p in sys.argv[1:]: render(p)

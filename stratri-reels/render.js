// Kullanım:
//   node render.js stills 2.2 9.5 12 ...   -> preview/frame_<t>.png
//   node render.js video [fps]             -> output/stratri_reels.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'); const fs = require('fs');
(async () => {
  const [mode, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 2000 }, deviceScaleFactor: 1 });
  await page.addInitScript(() => { window.__render = true; });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.addStyleTag({ content: 'body{padding:0!important;background:#000}#ui{display:none!important}' });
  await page.evaluate(() => document.fonts.ready);
  const stage = await page.$('#stage');
  if (mode === 'stills') {
    fs.mkdirSync(path.join(__dirname, 'preview'), { recursive: true });
    for (const s of rest) { const t = +s; await page.evaluate(t => seek(t), t);
      await stage.screenshot({ path: path.join(__dirname, 'preview', `frame_${t.toFixed(1)}.png`) }); }
  } else {
    const fps = +(rest[0] || 30); const dur = await page.evaluate(() => DURATION);
    fs.mkdirSync(path.join(__dirname, 'output'), { recursive: true });
    const out = path.join(__dirname, 'output', 'stratri_reels.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-r', String(fps), '-movflags', '+faststart', out]);
    const n = Math.round(dur * fps);
    for (let i = 0; i < n; i++) { await page.evaluate(t => seek(t), i / fps);
      ff.stdin.write(await stage.screenshot({ type: 'png' })); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('Hazır:', out);
  }
  await browser.close();
})();

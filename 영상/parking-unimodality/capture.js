// Frame-exact capture of film.html with Playwright, encoded by FFmpeg.
//   node capture.js stills <layout> <outdir> <sec|t=epoch> ...   -> PNG per moment (2x scale)
//   node capture.js video  <layout> <out.mp4> [fps]               -> H.264 mp4, frames piped to ffmpeg
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FFMPEG = process.env.FFMPEG || path.join(process.env.LOCALAPPDATA, 'Microsoft', 'WinGet', 'Packages',
  'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 'ffmpeg-9.0.2-full_build', 'bin', 'ffmpeg.exe');
const PAGE = 'file:///' + encodeURI(path.resolve(__dirname, 'film.html').replace(/\\/g, '/'));

async function open(layout, scale) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.goto(`${PAGE}?layout=${layout}`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([document.fonts.load('400 34px "Noto Serif KR"'), document.fonts.load('400 21px "Noto Sans KR"')]));
  return { browser, page };
}

async function stills(layout, outdir, moments) {
  fs.mkdirSync(outdir, { recursive: true });
  const { browser, page } = await open(layout, 2);
  for (const m of moments) {
    // moment syntax: <sec> | t=<epoch>[+<screen seconds>] | end
    let sec;
    if (m === 'end') sec = await page.evaluate(() => window.FILM.total - 1);
    else if (m.startsWith('t=')) {
      const [epoch, plus] = m.slice(2).split('+');
      sec = await page.evaluate(t => window.FILM.tToSec(t), +epoch) + (+(plus || 0));
    } else sec = +m;
    await page.evaluate(s => window.renderFrame(s), sec);
    const name = `${layout}-${m.replace(/[^0-9a-z.+=]/gi, '')}.png`;
    await page.screenshot({ path: path.join(outdir, name), type: 'png' });
    console.log('wrote', name);
  }
  await browser.close();
}

async function video(layout, out, fps) {
  const { browser, page } = await open(layout, 1);
  const total = await page.evaluate(() => window.FILM.total);
  const frames = Math.round(total * fps);
  const ff = spawn(FFMPEG, ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const started = Date.now();
  for (let i = 0; i < frames; i++) {
    await page.evaluate(s => window.renderFrame(s), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${frames}  ${((Date.now() - started) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  await browser.close();
  console.log('wrote', out, 'frames', frames);
}

(async () => {
  const [mode, layout, out, ...rest] = process.argv.slice(2);
  if (mode === 'stills') await stills(layout, out, rest);
  else if (mode === 'video') await video(layout, out, +(rest[0] || 30));
  else throw new Error('usage: node capture.js stills|video <layout> <out> ...');
})().catch(e => { console.error(e); process.exit(1); });

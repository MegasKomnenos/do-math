// Layout diagnostics: minimum node distance and near-overlaps for a layout under several span weightings.
const { chromium } = require('playwright');
const path = require('path');
const PAGE = 'file:///' + encodeURI(path.resolve(__dirname, 'film.html').replace(/\\/g, '/'));
(async () => {
  const layout = process.argv[2] || 'radial';
  const weights = (process.argv[3] || '0.4,0.5,0.6,0.7,1.0').split(',');
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const wt of weights) {
    await pg.goto(`${PAGE}?layout=${layout}&wt=${wt}`);
    const r = await pg.evaluate(() => {
      const P = window.POS, N = window.NODES; let min = 1e9, close = 0;
      for (let i = 0; i < N.length; i++) for (let j = i + 1; j < N.length; j++) {
        const a = P[N[i].id], c = P[N[j].id]; const d = Math.hypot(a.x - c.x, a.y - c.y);
        if (d < min) min = d; if (d < 10) close++;
      }
      return { min: min.toFixed(1), close };
    });
    console.log(`wt ${wt}: min node distance ${r.min}px, pairs closer than 10px: ${r.close}`);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });

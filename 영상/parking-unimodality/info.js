// Prints the film's total screen length and the cascade holds for a layout.
const { chromium } = require('playwright');
const path = require('path');
const PAGE = 'file:///' + encodeURI(path.resolve(__dirname, 'film.html').replace(/\\/g, '/'));
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto(`${PAGE}?layout=${process.argv[2] || 'radial'}`);
  const f = await pg.evaluate(() => ({
    total: window.FILM.total,
    holds: window.FILM.holds.map(h => ({ len: +h.len.toFixed(2), sec: +h.sec.toFixed(1), levels: h.levels })),
  }));
  console.log('total screen seconds', f.total.toFixed(2), 'frames@30', Math.round(f.total * 30));
  console.log('holds', JSON.stringify(f.holds));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });

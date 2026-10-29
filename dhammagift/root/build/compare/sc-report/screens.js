// Opens each error on suttacentral.net (the live site), outlines the segment and saves a screenshot.
const { chromium } = require('playwright');
const ITEMS = [
  ['sn35.19', 'sn35.19:2.9', 'aparimutto'], ['sn35.20', 'sn35.20:2.2', 'aparimutto'], ['sn35.20', 'sn35.20:2.8', 'aparimutto'],
  ['dn33', 'dn33:1.11.85', 'bhikkhave'], ['dn33', 'dn33:1.11.91', 'bhikkhave'],
  ['sn22.7', 'sn22.7:8.2', 'saṅkhāravantaṁ'], ['pli-tv-bu-vb-ss13', 'pli-tv-bu-vb-ss13:2.8', 'veḷuyā vejjikāya'],
  ['pli-tv-pvr5', 'pli-tv-pvr5:122.4', 'ammukhāvinayena'],
  ['sn48.137-146', 'sn48.137-146:1.1', 'On Display'], ['sn48.147-158', 'sn48.147-158:1.1', 'On Display'], ['sn50.67-76', 'sn50.67-76:1.1', 'On Display'],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  for (const [uid, key, word] of ITEMS) {
    const url = `https://suttacentral.net/${uid}/pli/ms?layout=plain&reference=none&notes=none&highlight=false&script=latin#${key}`;
    await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
    await p.waitForTimeout(3000);
    // SC renders inside shadow roots: search every root for the segment id and the word
    const found = await p.evaluate(([key, word]) => {
      const roots = [document];
      for (let i = 0; i < roots.length; i++) roots[i].querySelectorAll('*').forEach(e => e.shadowRoot && roots.push(e.shadowRoot));
      for (const r of roots) {
        const el = r.getElementById ? r.getElementById(key) : r.querySelector(`[id="${key}"]`);
        if (el) {
          el.scrollIntoView({ block: 'center' });
          el.style.outline = '3px solid red'; el.style.background = '#ffe9e6';
          return el.textContent.trim().slice(0, 200);
        }
      }
      return null;
    }, [key, word]);
    await p.waitForTimeout(800);
    const file = require('path').join(process.argv[2] || '.', `sc-${key.replace(/[:.]/g, '_')}.png`);
    await p.screenshot({ path: file });
    console.log(key, '|', found, '|', file, '|', url);
  }
  await b.close();
})();

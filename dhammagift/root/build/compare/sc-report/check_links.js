// Opens every edition link of 1-errors-in-sc-ms.md, looks for the correct reading on the page, outlines it and saves
// a screenshot: node check_links.js OUT_DIR [what-ed filter, e.g. pvr5-pts]
const { chromium } = require('playwright');
const path = require('path');
const PARI = 'nabhinandati\\W+parimutto';
const LINKS = [
  ['sn35.19', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/13S4/1/1.1/1.1.2/1.1.2.7.html', PARI],
  ['sn35.19', 'bjt', 'https://tipitaka.lk/sn-4-1-1/12-4/pali', 'නාභිනන්දති,\\s+පරිමුත්තො', 'si'],
  ['sn35.19', 'vri', 'https://www.tipitaka.org/romn/cscd/s0304m.mul0.xml', PARI],
  ['sn35.19', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=18&item=19', PARI],
  ['sn35.19', 'pts', 'https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu4pu.htm', PARI],
  ['sn35.20', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/13S4/1/1.1/1.1.2/1.1.2.8.html', PARI],
  ['sn35.20', 'bjt', 'https://tipitaka.lk/sn-4-1-1/12-9/pali', 'නාභිනන්දති,\\s+පරිමුත්තො', 'si'],
  ['sn35.20', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=18&item=20', PARI],
  ['dn33', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/8D/10/10.4.html', 'idh\\W*avuso\\W+bhikkhu\\W+uppannam\\W+kama\\W*vitakkam'],
  ['dn33', 'bjt', 'https://tipitaka.lk/dn-3-10/15-0/pali', 'ඉධාවුසො\\s+භික්ඛු\\s+උප්පන්නං', 'si'],
  ['dn33', 'vri', 'https://www.tipitaka.org/romn/cscd/s0103m.mul9.xml', 'idh\\W*avuso\\W+bhikkhu\\W+uppannam\\W+kama\\W*vitakkam'],
  ['dn33', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=11&item=238', 'idh\\W*avuso\\W+bhikkhu\\W+uppannam\\W+kama\\W*vitakkam'],
  ['dn33', 'pts', 'https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/1_digh/dighn3pu.htm', 'idh\\W*avuso\\W+bhikkhu\\W+uppannam\\W+kama\\W*vitakkam'],
  ['sn22.7', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/13S3/1/1.1/1.1.1/1.1.1.7.html', 'na\\W+sankharavantam\\W+(va\\W+)?attanam\\W+na\\W+attani\\W+va\\W+sankhare'],
  ['sn22.7', 'bjt', 'https://tipitaka.lk/sn-3-1-1-1/14-6/pali', 'න\\s+සඞ්ඛාරවන්තං\\s+අත්තානං,\\s+න\\s+අත්තනි', 'si'],
  ['sn22.7', 'vri', 'https://www.tipitaka.org/romn/cscd/s0303m.mul0.xml', 'na\\W+sankharavantam\\W+(va\\W+)?attanam\\W+na\\W+attani\\W+va\\W+sankhare'],
  ['sn22.7', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=17&item=33', 'na\\W+sankharavantam\\W+(va\\W+)?attanam\\W+na\\W+attani\\W+va\\W+sankhare'],
  ['sn22.7', 'pts', 'https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu3pu.htm', 'na\\W+sankhara\\W*vantam\\W+(va\\W+)?attanam\\W+na\\W+attani\\W+va\\W+sankhare'],
  ['ss13', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/1V/1/1.2/1.2.13.html', 'vel\\w+\\W+va\\W'],
  ['ss13', 'bjt', 'https://tipitaka.lk/vp-prj-3-12/74-3/pali', 'වෙළුනා\\s+වා', 'si'],
  ['ss13', 'vri', 'https://www.tipitaka.org/romn/cscd/vin01m.mul2.xml', 'vel\\w+\\W+va\\W'],
  ['ss13', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=1&item=624', 'vel\\w+\\W+va\\W'],
  ['ss13', 'pts', 'https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin3s1pu.htm', 'vel\\w+\\W+va\\W'],
  ['pvr5', 'ms2005', 'https://tipitaka2500.github.io/tipitaka/5V/5/5.13.html', 'sattahi\\W+samathehi\\W+sammanti\\W+sammukhavinayena\\W+ca\\W+yebhuyyasikaya'],
  ['pvr5', 'bjt', 'https://tipitaka.lk/vp-pv-4-6/91-5/pali', 'සත්තහි\\s+සමථෙහි\\s+සම්මන්ති\\s*:\\s*සම්මුඛාවිනයෙන', 'si'],
  ['pvr5', 'vri', 'https://www.tipitaka.org/romn/cscd/vin02m4.mul2.xml', 'sattahi\\W+samathehi\\W+sammanti\\W+sammukhavinayena\\W+ca\\W+yebhuyyasikaya'],
  ['pvr5', 'sya', 'https://84000.org/tipitaka/read/roman_item_s.php?book=8&item=904', 'sattahi\\W+samathehi\\W+sammanti\\W+sammukhavinayena\\W+ca\\W+yebhuyyasikaya'],
  ['pvr5', 'pts', 'https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin5papu.htm', 'apattadhikaranan\\W+ca\\W+katihi\\W+\\.\\W+\\.\\W+\\.\\W+sattahi\\W+s\\W+s\\W+samm\\W+ca\\W+yebh'],
];
(async () => {
  const out = process.argv[2] || '.';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  for (const [what, ed, url, re, mode] of LINKS.filter(l => !process.argv[3] || (l[0] + '-' + l[1]).includes(process.argv[3]))) {
    let status = '', found = null;
    try {
      const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
      status = r ? r.status() : '?';
      await p.waitForTimeout(6000);
      found = await p.evaluate(([re, mode]) => {
        // all text nodes (shadow roots too), folded char by char so a match maps back to the page
        const fold = c => mode === 'si' ? c.replace(/[‌‍]/g, '') : c.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '');
        const nodes = [], walk = root => {
          const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
          for (let n = w.currentNode; n; n = w.nextNode()) {
            if (n.nodeType === 3) nodes.push(n);
            else if (n.shadowRoot) walk(n.shadowRoot);
          }
        };
        walk(document.body || document.documentElement);
        let all = '', map = [];
        for (const n of nodes) for (let i = 0; i < n.data.length; i++) { const f = fold(n.data[i]); for (const c of f) { all += c; map.push([n, i]); } }
        const m = new RegExp(re, 'u').exec(all);
        if (!m) return null;
        const [n1, i1] = map[m.index], [n2, i2] = map[m.index + m[0].length - 1];
        const range = document.createRange(); range.setStart(n1, i1); range.setEnd(n2, i2 + 1);
        (n1.parentElement || document.body).scrollIntoView({ block: 'center' });
        const r0 = range.getBoundingClientRect();  // a long text node: bring the match itself to the middle
        window.scrollBy(0, r0.top - window.innerHeight / 2);
        const rects = [...range.getClientRects()];
        for (const r of rects) {
          const d = document.createElement('div');
          Object.assign(d.style, { position: 'fixed', left: r.left - 3 + 'px', top: r.top - 2 + 'px', width: r.width + 6 + 'px', height: r.height + 4 + 'px',
            border: '3px solid #1d8a3a', background: 'rgba(29,138,58,.15)', zIndex: 99999, pointerEvents: 'none' });
          document.body.appendChild(d);
        }
        return all.slice(Math.max(0, m.index - 50), m.index + m[0].length + 20).replace(/\s+/g, ' ');
      }, [re, mode || 'ro']);
    } catch (e) { status = 'error: ' + e.message.split('\n')[0]; }
    await p.waitForTimeout(500);
    const file = path.join(out, `ed-${what}-${ed}.png`);
    await p.screenshot({ path: file });
    console.log([what, ed, status, found ? 'FOUND: ' + found : 'NOT FOUND', file].join(' | '));
  }
  await b.close();
})();

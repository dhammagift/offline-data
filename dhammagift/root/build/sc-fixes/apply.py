"""Write our fixes of SC's Pali (fixes.json) into the SC checkout, root/pli/ms. Idempotent: a segment that already
holds `new` is skipped, one that holds neither `old` nor `new` (SC changed it) is reported and left alone.
`inserts` add segments SC lacks (printed headings): the root text and its template in html/pli/ms, before `before`.
The weekly mirror refresh (dg-node scripts/update-external-repos.sh) resets the checkout, so this runs after it.
usage: apply.py [SC_ROOT_PLI_MS]   (default /var/www/suttacentral.net/sc-data/sc_bilara_data/root/pli/ms)
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/var/www/suttacentral.net/sc-data/sc_bilara_data/root/pli/ms'
HTML = ROOT.replace('/root/pli/ms', '/html/pli/ms')
spec = json.load(open(os.path.join(HERE, 'fixes.json'), encoding='utf-8'))
fixes, inserts = spec['fixes'], spec.get('inserts', [])

by_file, changed, done, skipped = {}, 0, 0, []
for fx in fixes:
    sutta = fx['seg'].split(':')[0]
    hits = glob.glob(os.path.join(ROOT, '**', sutta + '_root-pli-ms.json'), recursive=True)
    if len(hits) != 1:
        skipped.append(f"{fx['seg']}: file not found ({len(hits)})")
        continue
    by_file.setdefault(hits[0], []).append(fx)

def find(base, sutta, suffix):
    hits = glob.glob(os.path.join(base, '**', sutta + suffix), recursive=True)
    return hits[0] if len(hits) == 1 else None

def save(path, data):
    # SC's own layout: 2-space indent, unescaped UTF-8, no trailing newline
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

for fx in inserts:
    sutta = fx['seg'].split(':')[0]
    root, html = find(ROOT, sutta, '_root-pli-ms.json'), find(HTML, sutta, '_html.json')
    if not root or not html:
        skipped.append(f"{fx['seg']}: root or html file not found")
        continue
    pair = []
    for path in (root, html):
        with open(path, encoding='utf-8') as f:
            pair.append(json.load(f))
    r, h = pair
    want = (fx['new'], fx['html'])
    if (r.get(fx['seg']), h.get(fx['seg'])) == want:
        done += 1
        continue
    if fx['seg'] in r or fx['seg'] in h or fx['before'] not in r or fx['before'] not in h:
        skipped.append(f"{fx['seg']}: SC text changed, not inserted")
        continue
    for path, data, value in ((root, r, fx['new']), (html, h, fx['html'])):
        out = {}
        for k, v in data.items():
            if k == fx['before']:
                out[fx['seg']] = value
            out[k] = v
        save(path, out)
    changed += 1

for path, fxs in by_file.items():
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    dirty = False
    for fx in fxs:
        cur = data.get(fx['seg'])
        if cur == fx['new']:
            done += 1
        elif cur == fx['old']:
            data[fx['seg']] = fx['new']
            dirty = True
            changed += 1
        else:
            skipped.append(f"{fx['seg']}: SC text changed, not touched: {cur!r}")
    if dirty:
        save(path, data)

print(f'sc-fixes: {changed} applied, {done} already in place, {len(skipped)} skipped')
for s in skipped:
    print('  ' + s)
sys.exit(1 if skipped else 0)

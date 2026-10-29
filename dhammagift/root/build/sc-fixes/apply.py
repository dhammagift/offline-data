"""Write our fixes of SC's Pali (fixes.json) into the SC checkout, root/pli/ms. Idempotent: a segment that already
holds `new` is skipped, one that holds neither `old` nor `new` (SC changed it) is reported and left alone.
The weekly mirror refresh (dg-node scripts/update-external-repos.sh) resets the checkout, so this runs after it.
usage: apply.py [SC_ROOT_PLI_MS]   (default /var/www/suttacentral.net/sc-data/sc_bilara_data/root/pli/ms)
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/var/www/suttacentral.net/sc-data/sc_bilara_data/root/pli/ms'
fixes = json.load(open(os.path.join(HERE, 'fixes.json'), encoding='utf-8'))['fixes']

by_file, changed, done, skipped = {}, 0, 0, []
for fx in fixes:
    sutta = fx['seg'].split(':')[0]
    hits = glob.glob(os.path.join(ROOT, '**', sutta + '_root-pli-ms.json'), recursive=True)
    if len(hits) != 1:
        skipped.append(f"{fx['seg']}: file not found ({len(hits)})")
        continue
    by_file.setdefault(hits[0], []).append(fx)

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
        # SC's own layout: 2-space indent, unescaped UTF-8, no trailing newline
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

print(f'sc-fixes: {changed} applied, {done} already in place, {len(skipped)} skipped')
for s in skipped:
    print('  ' + s)
sys.exit(1 if skipped else 0)

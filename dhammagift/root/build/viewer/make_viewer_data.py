"""Data for viewer/index.html: one JSON per book with ms + bjt + my + th rows, variants and references.

usage: make_viewer_data.py DHAMMAGIFT_DIR BILARA_MS_SUTTA_DIR OUT_DIR   (writes OUT_DIR/data/*.json)
"""
import json, glob, os, re, sys
DG, MS, OUT = sys.argv[1:4]
os.makedirs(f'{OUT}/data', exist_ok=True)
EDS = ['bjt', 'my', 'th']
books = sorted({p.split('/')[-2] for p in glob.glob(f'{DG}/root/pli/bjt/sutta/*/*/*.json')},
               key=lambda b: (b[:2] != 'sn', int(b[2:])))
def nkey(f):
    b = os.path.basename(f).split('_')[0]
    return [int(x) for x in re.findall(r'\d+', b)]
index = []
for book in books:
    coll = book[:2]
    files = sorted(glob.glob(f'{MS}/{coll}/{book}/*_root-pli-ms.json'), key=nkey)
    suttas = []
    stats = {e: [0, 0] for e in EDS}
    for f in files:
        base = os.path.basename(f).split('_')[0]
        ms = json.load(open(f))
        eds, var, ref = {}, {}, {}
        for e in EDS:
            p = f'{DG}/root/pli/{e}/sutta/{coll}/{book}/{base}_root-pli-{e}.json'
            eds[e] = json.load(open(p)) if os.path.exists(p) else {}
            for kind, store in (('variant', var), ('reference', ref)):
                q = f'{DG}/{kind}/pli/{e}/sutta/{coll}/{book}/{base}_{kind}-pli-{e}.json'
                if os.path.exists(q):
                    store[e] = json.load(open(q))
        rows = []
        for k, v in ms.items():
            rows.append([k, v.strip()] + [eds[e].get(k, '').strip() for e in EDS])
            for e in EDS:
                stats[e][1] += 1
                stats[e][0] += bool(eds[e].get(k, '').strip())
        title = (ms.get(next((k for k in ms if k.endswith(':0.3')), ''), '') or '').strip()
        suttas.append({'id': base, 'title': title, 'rows': rows, 'var': var, 'ref': ref})
    json.dump({'book': book, 'suttas': suttas}, open(f'{OUT}/data/{book}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    index.append({'book': book, 'n': len(suttas), 'fill': {e: round(100 * a / b) for e, (a, b) in stats.items()},
                  'suttas': [[s['id'], s['title']] for s in suttas]})
json.dump(index, open(f'{OUT}/data/index.json', 'w'), ensure_ascii=False, separators=(',', ':'))

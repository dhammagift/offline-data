"""Data for viewer/index.html: one JSON per page with ms + bjt + my + th rows, variants and references.
A page is a DN / MN sutta, an SN saṃyutta, an AN nipāta, a KN or Vinaya book (large books in parts).

usage: make_viewer_data.py DHAMMAGIFT_DIR BILARA_MS_SUTTA_DIR OUT_DIR   (writes OUT_DIR/data/*.json)
"""
import json, glob, os, re, sys
DG, MS, OUT = sys.argv[1:4]
os.makedirs(f'{OUT}/data', exist_ok=True)
EDS = ['bjt', 'my', 'th']
KN = ['kp', 'dhp', 'ud', 'iti', 'snp', 'vv', 'pv', 'thag', 'thig', 'tha-ap', 'thi-ap', 'bv', 'cp', 'ja', 'mnd', 'cnd',
      'ps', 'mil', 'ne', 'pe']
PART = 2500  # segments: a KN or Vinaya book longer than this is shown in parts
ROOT = os.path.dirname(MS.rstrip('/'))  # bilara root/pli/ms: sutta/, vinaya/
VINAYA = [f'pli-tv-{s}-vb-{k}' for s, ks in (('bu', ['pj', 'ss', 'ay', 'np', 'pc', 'pd', 'sk', 'as']),
                                            ('bi', ['pj', 'ss', 'np', 'pc', 'pd', 'sk', 'as'])) for k in ks] \
    + ['pli-tv-bu-pm', 'pli-tv-bi-pm', 'pli-tv-kd', 'pli-tv-pvr']


def nkey(f):
    return [int(x) for x in re.findall(r'\d+', os.path.basename(f).split('_')[0])]


def built(f):
    """does any edition have this ms file built?"""
    rel = os.path.relpath(f, ROOT).replace('_root-pli-ms.json', '')
    return any(os.path.exists(f'{DG}/root/pli/{e}/{rel}_root-pli-{e}.json') for e in EDS)


pages = []  # (page id, collection, label, [ms files])
for coll in ('dn', 'mn'):
    for f in sorted(glob.glob(f'{MS}/{coll}/*_root-pli-ms.json'), key=nkey):
        if built(f):
            b = os.path.basename(f).split('_')[0]
            pages.append((b, coll, b.upper(), [f]))
for coll in ('sn', 'an'):
    for d in sorted(glob.glob(f'{MS}/{coll}/{coll}*'), key=nkey):
        fs = [f for f in sorted(glob.glob(f'{d}/*_root-pli-ms.json'), key=nkey) if built(f)]
        if fs:
            b = os.path.basename(d)
            pages.append((b, coll, b.upper(), fs))
books = [('kn', b, glob.glob(f'{MS}/kn/{b}/**/*_root-pli-ms.json', recursive=True)) for b in KN] + \
    [('vinaya', b, [f for f in glob.glob(f'{ROOT}/vinaya/**/{b}*_root-pli-ms.json', recursive=True)
                    if re.fullmatch(re.escape(b) + r'[\d.-]*', os.path.basename(f).split('_')[0])]) for b in VINAYA]
for coll, book, found in books:
    fs = [f for f in sorted(found, key=lambda f: nkey(f)[-2:] if coll == 'vinaya' else nkey(f)) if built(f)]
    if not fs:
        continue
    parts, cur, n = [], [], 0
    for f in fs:
        size = len(json.load(open(f)))
        if cur and n + size > PART:
            parts.append(cur)
            cur, n = [], 0
        cur.append(f)
        n += size
    parts.append(cur)
    name = book.replace('pli-tv-', '')  # bu-vb-pj, bi-pm
    for i, part in enumerate(parts, 1):
        first, last = (os.path.basename(x).split('_')[0] for x in (part[0], part[-1]))
        pid = name if len(parts) == 1 else f'{name}-p{i}'
        span = first[len(book):] if first == last else f'{first[len(book):]}–{last[len(book):]}'
        label = name.upper() if len(parts) == 1 else f'{name.upper()} {span}'
        pages.append((pid, coll, label, part))

index = []
for pid, coll, label, files in pages:
    suttas = []
    stats = {e: [0, 0] for e in EDS}
    for f in files:
        base = os.path.basename(f).split('_')[0]
        sub = os.path.relpath(os.path.dirname(f), ROOT)  # sutta/sn/sn1, vinaya/pli-tv-bu-vb/...
        ms = json.load(open(f))
        eds, var, ref = {}, {}, {}
        for e in EDS:
            p = f'{DG}/root/pli/{e}/{sub}/{base}_root-pli-{e}.json'
            eds[e] = json.load(open(p)) if os.path.exists(p) else {}
            q = f'{DG}/reference/pli/{e}/{sub}/{base}_reference-pli-{e}.json'
            if os.path.exists(q):
                ref[e] = json.load(open(q))
        q = f'{DG}/variant/pli/ms/{sub}/{base}_variant-pli-ms.json'  # all readings, footnotes included (collate.py)
        if os.path.exists(q):
            var['ms'] = json.load(open(q))
        rows = []
        for k, v in ms.items():
            rows.append([k, v.strip()] + [eds[e].get(k, '').strip() for e in EDS])
            for e in EDS:
                if eds[e]:  # an edition without this book (BJT Milinda, Thai Netti) is not counted
                    stats[e][1] += 1
                    stats[e][0] += bool(eds[e].get(k, '').strip())
        heads = [v.strip() for k, v in ms.items() if re.search(r':0\.\d+$', k) and len(v.split()) < 5]
        title = (heads[-1] if heads else '') if coll == 'vinaya' else \
            next((v.strip() for k, v in ms.items() if re.search(r':0\.[2-9]$', k) and 'sutta' in v.lower()), '') \
            or (ms.get(next((k for k in ms if k.endswith(':0.3')), ''), '') or '').strip()
        suttas.append({'id': base, 'title': title, 'rows': rows, 'var': var, 'ref': ref})
    json.dump({'book': pid, 'suttas': suttas}, open(f'{OUT}/data/{pid}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    index.append({'book': pid, 'coll': coll, 'label': label, 'n': len(suttas),
                  'fill': {e: round(100 * a / b) if b else None for e, (a, b) in stats.items()},
                  'suttas': [[s['id'], s['title']] for s in suttas]})
json.dump(index, open(f'{OUT}/data/index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(pages), 'pages')

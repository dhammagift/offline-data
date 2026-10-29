"""SC ms against the Mahāsaṅgīti as printed (World Tipiṭaka 2005, tipitaka2500.github.io), segment by segment.
The printed text is built with build_editions.py --eds mso into a folder outside dhammagift (not part of the data).

usage: compare_ms.py BILARA_ROOT_PLI_MS MSO_ROOT_PLI_MSO OUT.tsv [DHAMMAGIFT_DIR]
  -> summary on stdout, differences in OUT.tsv; with DHAMMAGIFT_DIR also the readings of the print where its words
     differ from SC ms as variants, DHAMMAGIFT_DIR/variant/pli/mso/..._variant-pli-mso.json, with the editions
     (bjt, my, th) that read as the print
"""
import collections, glob, json, os, re, sys, unicodedata

MS, MSO, OUT = sys.argv[1:4]


def plain(s):
    """lower case, no punctuation, ṁ = ṃ"""
    s = re.sub(r'<[^>]+>', '', s)  # SC <b> in the Niddesa
    s = unicodedata.normalize('NFC', s.lower()).replace('ṁ', 'ṃ').replace('…pe…', ' ').replace('…', ' ')
    return [w for w in (re.sub(r'[^\w]', '', x) for x in re.sub(r"[’'](?=\w)", '', s).split()) if w and w != 'pe' and not w.isdigit()]


def ortho(ws):
    """SC writes ṅ for the printed ṃ before k, g (saṃgha → saṅgha, evaṃgotto → evaṅgotto)"""
    return [re.sub(r'ṃ(?=[kg])', 'ṅ', w) for w in ws]


import difflib
TITLE = re.compile(r'(vagg|kaṇḍ|sutt|sikkhāpad|vibhaṅg|pāḷi|nipāt|saṃyutt|peyyāl|vatth|kath|jātak|apadān|vaṃs|'
                   r'cariy|niddes|pucch|gāth|vimān|bhāṇavār|pabb|uddes|vār|khandhak|paññatti|pañh|ādi|ekadhamm|saraṇattay|samuṭṭhān)')
kinds, rows, edits = collections.Counter(), [], collections.Counter()
for p in sorted(glob.glob(os.path.join(MS, '**', '*_root-pli-ms.json'), recursive=True)):
    rel = os.path.relpath(p, MS).replace('_root-pli-ms.json', '_root-pli-mso.json')
    q = os.path.join(MSO, rel)
    if not os.path.exists(q):
        continue
    ms, mso = json.load(open(p)), json.load(open(q))
    keys = [k for k in ms if not (k.split(':')[1].startswith('0.') or re.search(r'(^|\.)0(\.|$)', k.split(':')[1]))]
    a = [(k, w) for k in keys for w in ortho(plain(ms[k]))]
    b = [(k, w) for k in keys for w in ortho(plain(mso.get(k, '')))]
    kinds['words'] += len(a)
    sm = difflib.SequenceMatcher(None, [w for _, w in a], [w for _, w in b], autojunk=False)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(w for _, w in a[a1:a2]), ' '.join(w for _, w in b[b1:b2])
        if x.replace(' ', '') == y.replace(' ', ''):
            kinds['spacing'] += 1
            continue
        k = a[a1][0] if a1 < len(a) else a[-1][0]
        if op == 'insert' and all(TITLE.search(w) for w in y.split()):
            kinds['printed title'] += 1  # a heading of the printed edition, which SC gives in its own 0.x
            continue
        kinds[op] += 1
        edits[(x, y)] += 1
        rows.append((k, op, x, y))
def words_only(x):
    return ' '.join(w for w in x.split() if not TITLE.search(w))


def squash(x):
    return re.sub('ṅ', 'ṃ', x.replace(' ', ''))


variants = collections.defaultdict(dict)  # ms file -> {key: entry}
if len(sys.argv) > 4:
    DG = sys.argv[4]
    skip = set()
    for n, (k, op, x, y) in enumerate(rows):  # the same words put in another order or segment (sn22.7:8.2)
        if n + 1 < len(rows) and rows[n + 1][0].split(':')[0] == k.split(':')[0] and \
                sorted(squash(x + rows[n + 1][2])) == sorted(squash(y + rows[n + 1][3])):
            skip.update((n, n + 1))
    keys = []
    for n, (k, op, x, y) in enumerate(rows):
        x2, y2 = words_only(x), words_only(y)
        if n in skip or squash(x2) == squash(y2) or (not x2 and op != 'insert') or (op == 'insert' and not y2):
            continue  # headings and numbers of the print, spacing
        if op == 'insert' and len(y2.split()) > 2:
            continue
        if k not in keys:
            keys.append(k)
    files = {}
    for p in glob.glob(os.path.join(MS, '**', '*_root-pli-ms.json'), recursive=True):
        for k in json.load(open(p)):
            files[k] = p
    for k in keys:
        rel = os.path.relpath(files[k], MS)
        old = json.load(open(files[k]))[k]
        new = json.load(open(os.path.join(MSO, rel.replace('_root-pli-ms.json', '_root-pli-mso.json'))))[k]
        ow, nw = old.split(), new.split()
        A, B = [squash(' '.join(ortho(plain(w)))) for w in ow], [squash(' '.join(ortho(plain(w)))) for w in nw]
        eds = {}
        for ed in ('bjt', 'my', 'th'):
            q = os.path.join(DG, 'root', 'pli', ed, rel.replace('_root-pli-ms.json', f'_root-pli-{ed}.json'))
            if os.path.exists(q):
                eds[ed] = [squash(' '.join(ortho(plain(w)))) for w in json.load(open(q)).get(k, '').split()]
        entries = []
        for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
            if op == 'equal' or ''.join(A[a1:a2]) == ''.join(B[b1:b2]) or not any(B[b1:b2]):
                continue  # nothing of the print here: its heading or end line stands in another segment
            if any(TITLE.search(w) for w in B[b1:b2]) and not A[a1:a2]:
                continue
            insert = a1 == a2
            if insert:  # the print has more: show it with the word before
                a1, b1 = max(a1 - 1, 0), max(b1 - 1, 0)
            sc, pr = ' '.join(ow[a1:a2]), ' '.join(nw[b1:b2])
            want, avoid = B[b1:b2], [] if insert else A[a1:a2]
            agree = [ed for ed, w in eds.items()
                     if any(w[i:i + len(want)] == want for i in range(len(w))) and
                     not (avoid and any(w[i:i + len(avoid)] == avoid for i in range(len(w))))]
            clean = lambda t: t.strip('‘’“”—,.;:?!() ').replace('’', '').replace('‘', '')
            entries.append(f'{clean(sc)} → {clean(pr)} (Mahāsaṅgīti 2005' + (f'; {", ".join(agree)}' if agree else '') + ')')
        if entries:
            variants[rel][k] = ' | '.join(entries)
    for rel, v in variants.items():
        out = os.path.join(DG, 'variant', 'pli', 'mso', rel.replace('_root-pli-ms.json', '_variant-pli-mso.json'))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(v, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        for k, e in v.items():
            print('variant', k, e)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('key\top\tSC ms\tprinted Mahāsaṅgīti\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('SC ms words', kinds.pop('words'))
for k, n in kinds.most_common():
    print(f'{k:10} {n:7}')
print('most frequent differences (SC ms -> printed):')
for (x, y), n in edits.most_common(40):
    print(f'{n:6}  {x[:50]!r} -> {y[:50]!r}')

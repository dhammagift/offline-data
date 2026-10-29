"""SC ms against the Mahāsaṅgīti as printed (World Tipiṭaka 2005, tipitaka2500.github.io), segment by segment.
The printed text is built with build_editions.py --eds mso into a folder outside dhammagift (not part of the data).

usage: compare_ms.py BILARA_ROOT_PLI_MS MSO_ROOT_PLI_MSO OUT.tsv   -> summary on stdout, word differences in OUT.tsv
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
                   r'cariy|niddes|pucch|gāth|vimān|bhāṇavār|pabb|uddes|vār|khandhak|paññatti|pañh|ādi|ekadhamm)')
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

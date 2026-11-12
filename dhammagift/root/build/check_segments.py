"""The rule every edition file must keep: a word of the edition that is the same word as in ms, at the same place in
the sutta, stands in the same segment as that ms word.

Each sutta (one ms file) is aligned word by word with each edition (difflib, runs of 2 words or more, so a stray `ca`
is no anchor). A matched word whose edition segment is not the segment of its ms word breaks the rule: the text of
one ms segment sits in another (dn22 PTS before gap_fragments: `Katamañ ca bhikkhave` in 18.27, its ms words in 18.33).
Breaks are grouped by sutta, edition, the segment the words are in and the segment they belong to. Words the edition
prints a second time, while its own segment for them already reads as ms, are `extra`, not a break (BJT mn82 10.1).

usage: check_segments.py BILARA_ROOT_PLI_MS DHAMMAGIFT_DIR OUT.tsv [editions, default bjt,my,th,mso,pts] [top N]
"""
import collections, difflib, glob, json, os, re, sys, unicodedata

MS, DG, OUT = sys.argv[1:4]
EDS = (sys.argv[4] if len(sys.argv) > 4 else 'bjt,my,th,mso,pts').split(',')
TOP = int(sys.argv[5]) if len(sys.argv) > 5 else 20
ONLY = re.compile(sys.argv[6]) if len(sys.argv) > 6 else None  # e.g. '^dn\d': only these suttas


PEYYALA = re.compile(r'…|\.\.\.|\. \. \.|\bpe\b|\bla\b|peyyāl|vitthāretabb|saṅkhitt|saṃkhitt|saṁkhitt', re.I)


def words(text):
    """normalised words: lower case, no diacritics, a compound split where the edition marks it (- ' ’)"""
    t = unicodedata.normalize('NFD', re.sub(r'<[^>]+>', ' ', text).lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return [w for w in re.split(r'[^a-z]+', t) if w]


def seq(d):
    out = []
    for k, v in d.items():
        out += [(w, k) for w in words(v or '')]
    return out


rows = []
for p in sorted(glob.glob(os.path.join(MS, '**', '*_root-pli-ms.json'), recursive=True)):
    rel = os.path.relpath(p, MS)
    if ONLY and not ONLY.search(os.path.basename(p)):
        continue
    ms = json.load(open(p, encoding='utf-8'))
    A = seq(ms)
    if not A:
        continue
    order = {k: i for i, k in enumerate(ms)}
    for ed in EDS:
        q = os.path.join(DG, 'root', 'pli', ed, rel.replace('_root-pli-ms.json', f'_root-pli-{ed}.json'))
        if not os.path.exists(q):
            continue
        e = json.load(open(q, encoding='utf-8'))
        B = seq(e)
        if not B:
            continue
        sm = difflib.SequenceMatcher(None, [w for w, _ in A], [w for w, _ in B], autojunk=False)
        bad = collections.defaultdict(list)  # (edition segment, ms segment) -> words
        matched = 0
        for m in sm.get_matching_blocks():
            if m.size < 2:
                continue
            for d in range(m.size):
                matched += 1
                (w, km), (_, ke) = A[m.a + d], B[m.b + d]
                if km != ke:
                    bad[(ke, km)].append(w)
        for (ke, km), ws in bad.items():
            here = ' '.join(words(ms.get(ke) or ''))
            same = difflib.SequenceMatcher(None, words(ms.get(ke) or ''), words(ms.get(km) or ''), autojunk=False)
            if (' '.join(ws[:6]) in here and ke in ms) or same.ratio() >= 0.5:
                kind = 'repeat'  # ms has the same words (or a segment much like it) here too: which repetition is meant is unclear
            elif PEYYALA.search(ms.get(km) or '') or PEYYALA.search(e.get(ke) or '') or PEYYALA.search(ms.get(ke) or ''):
                kind = 'peyyala'  # one side abbreviates
            elif e.get(km) and difflib.SequenceMatcher(None, words(e.get(km)), words(ms.get(km) or ''),
                                                       autojunk=False).ratio() >= 0.8:
                kind = 'extra'  # the edition prints these words twice: its own segment km has them too (BJT mn82 10.1)
            else:
                kind = 'break'
            rows.append((len(ws), kind, ed, os.path.basename(p).split('_')[0], ke, km, order.get(km, 0) - order.get(ke, 0),
                         ' '.join(ws[:12]), (e.get(ke) or '').strip()[:90], (ms.get(ke) or '').strip()[:70],
                         (ms.get(km) or '').strip()[:70]))

rows.sort(key=lambda r: (r[1] != 'break', -r[0]))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('words\tkind\tedition\tsutta\tin_segment\tbelongs_to\tsteps\tmoved_words\tedition_text\tms_in_segment\tms_belongs_to\n')
    for r in rows:
        f.write('\t'.join(map(str, r)) + '\n')
by = collections.Counter()
for r in rows:
    by[(r[1], r[2])] += r[0]
print('displaced words by kind and edition:', dict(sorted(by.items())))
for r in [r for r in rows if r[1] == 'break'][:TOP]:
    print(f'{r[0]:5} {r[2]:4} {r[4]} -> {r[5]} ({r[6]:+d})  [{r[7][:60]}]\n       ed: {r[8][:80]}\n       ms here: {r[9][:70]}\n       ms there: {r[10][:70]}')

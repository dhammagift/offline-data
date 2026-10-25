"""Find segment shifts in the aligned Pali editions (viewer data: rows [key, ms, bjt, my, th]).
An edition's segment that carries words ms has in the NEIGHBOURING segment (its start pulled back, its end pushed on)
is a shift; across a sutta boundary it is a sutta-level shift (sn45.114 Thai type). Usage: find_shifts.py viewer/data viewer/data/shifts.json (or out.tsv for a table)"""
import json, sys, os, re, unicodedata, glob
from difflib import SequenceMatcher
# ponytail: peyyāla segments are skipped whole (expanded text repeats its neighbours); a shift right at a …pe… is not seen
EDS = ['bjt', 'my', 'th']
PE = re.compile(r'…\s*(pe|la|pa)\s*…|-pe-|\.\.\.pe|\bpe\b', re.I)
SKIP = {'pe', 'la', 'pa', 'peyyalo'}

def words(t):
    t = unicodedata.normalize('NFD', t.lower())
    t = re.sub(r'[̀-ͯ]', '', t)
    return [w for w in re.findall(r'[a-z]+', t) if w not in SKIP]

def sim(a, b):
    return SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0

def edge_match(extra, other, at_start):
    """share of `extra` words found at the matching edge of `other` (start of next / end of previous)"""
    if len(extra) < 2 or not other: return 0.0
    probe = other[:len(extra) + 2] if at_start else other[-(len(extra) + 2):]
    m = SequenceMatcher(None, extra, probe, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks()) / len(extra)

def scan(rows):
    out = []
    ms = [words(r[1]) for r in rows]
    for e, ed in enumerate(EDS, start=2):
        ew = [words(r[e]) for r in rows]
        for i, w in enumerate(ew):
            if len(w) < 2: continue
            # peyyāla: one side abbreviates (…pe…) what the other prints in full; the full text repeats the
            # neighbours' words by nature, which is not a shift
            if any(PE.search(rows[j][k]) for j in (i - 1, i, i + 1) if 0 <= j < len(rows) for k in (1, e)): continue
            # ms abbreviating with a bare … (sn35.53:2.3 "Cakkhuviññāṇaṁ …") is peyyāla too
            if any('…' in rows[j][1] for j in (i - 1, i, i + 1) if 0 <= j < len(rows)): continue
            m = SequenceMatcher(None, ms[i], w, autojunk=False)
            blocks = [b for b in m.get_matching_blocks() if b.size]
            first = blocks[0].b if blocks else len(w)
            last = blocks[-1].b + blocks[-1].size if blocks else 0
            sid = rows[i][0].split(':')[0]
            # tail: edition words after the last ms match that are the start of the next ms segment
            if i + 1 < len(rows) and last < len(w):
                extra = w[last:]
                if len(extra) >= 2 and edge_match(extra, ms[i + 1], True) >= 0.7 and not ms[i][-len(extra):] == extra:
                    out.append((rows[i][0], ed, 'next-in', rows[i + 1][0].split(':')[0] != sid, len(extra), ' '.join(extra[:12])))
            # head: edition words before the first ms match that are the end of the previous ms segment
            if i > 0 and first > 0:
                extra = w[:first]
                if len(extra) >= 2 and edge_match(extra, ms[i - 1], False) >= 0.7 and not ms[i][:len(extra)] == extra:
                    out.append((rows[i][0], ed, 'prev-in', rows[i - 1][0].split(':')[0] != sid, len(extra), ' '.join(extra[:12])))
            # whole segment belongs to a neighbour
            own = sim(ms[i], w)
            for j in (i - 1, i + 1):
                if 0 <= j < len(rows) and own < 0.4 and sim(ms[j], w) > own + 0.35 and len(w) >= 3:
                    out.append((rows[i][0], ed, 'is-' + ('prev' if j < i else 'next'), rows[j][0].split(':')[0] != sid, len(w), ' '.join(w[:12])))
    return out

def main(data, dst):
    res = []
    for f in sorted(glob.glob(os.path.join(data, '*.json'))):
        if os.path.basename(f) in ('index.json', 'shifts.json'): continue
        d = json.load(open(f, encoding='utf8'))
        rows = [r for s in d['suttas'] for r in s['rows']]
        res += [(d['book'],) + x for x in scan(rows)]
    if dst.endswith('.json'):   # the viewer's marks: {book: {key: {edition: "kind: words"}}}
        out = {}
        say = {'next-in': 'в конце начало следующего сегмента ms', 'prev-in': 'в начале конец предыдущего сегмента ms',
               'is-next': 'это текст следующего сегмента ms', 'is-prev': 'это текст предыдущего сегмента ms'}
        for book, key, ed, kind, cross, n, text in res:
            cell = out.setdefault(book, {}).setdefault(key, {})
            cell[ed] = (cell[ed] + '; ' if ed in cell else '') + say[kind] + (' (через границу сутты)' if cross else '') + ': ' + text
        json.dump(out, open(dst, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    else:
        with open(dst, 'w', encoding='utf8') as o:
            o.write('book\tkey\tedition\tkind\tcross_sutta\twords\ttext\n')
            for r in res: o.write('\t'.join(map(str, r)) + '\n')
    return res

if __name__ == '__main__':
    r = main(sys.argv[1], sys.argv[2])
    from collections import Counter
    print(len(r), 'flags;', Counter((x[2], x[3]) for x in r).most_common())
    print('cross-sutta:', Counter(x[2] for x in r if x[4]).most_common())

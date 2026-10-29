"""The footnotes of the PTS editions (the manuscripts' readings: `S1-3 rūpaṃ . . . aniccaṃ`), from the annotated
GRETIL files (`*ou.htm`, the text with its line breaks and page notes), put on the words of root/pli/pts.

A note number stands after its word (`aniccā<sup>2</sup>`), the notes at the foot of the page (`2 S1-3 …`). The
annotated text is the plain text (`*pu.htm`, which root/pli/pts is made from) with its lines broken: its words are
matched in order with the words of root/pli/pts, a stretch at a time, and a note goes to the segment of its word.
Out: NOTES_DIR/pts/<sc path>_variant-pli-pts.json, {key: "word → note | …"}, read by collate.py like the BJT notes.

usage: pts_notes.py GRETIL_1_TIPIT BILARA_MS_SUTTA DG_ROOT_PLI_PTS NOTES_DIR
"""
import html, json, os, re, sys, unicodedata
from difflib import SequenceMatcher
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_editions import PTS, pts_groups, ms_files  # noqa: E402

GRETIL, MS, PTS_ROOT, OUT = sys.argv[1:5]
MARK = re.compile(r'<span class="red">(?:<sup>)?(\d+)(?:</sup>)?</span>')


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    return re.sub(r'[^a-z]', '', re.sub(r'[̀-ͯ]', '', w))


def annotated(path):
    """[(word, [note, …])] in reading order"""
    t = open(path, encoding='utf-8', errors='replace').read()
    t = t[t.find('[page '):]
    words, pending = [], {}  # pending: note number -> index of its word, on the current page
    in_notes, last = False, None
    for line in re.split(r'<br>', t, flags=re.I):
        if '<span class="red">----' in line:
            in_notes, last = True, None
            continue
        if in_notes:
            if '</span>' in line:
                in_notes = False
            body = html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
            m = re.match(r'(\d+)\s*(\D.*)', body)  # `2More complete …` too
            if m and int(m.group(1)) in pending:
                last = pending.pop(int(m.group(1)))
                words[last][1].append(m.group(2).strip())
            elif body and last is not None:  # a note runs on to the next line
                words[last][1][-1] += ' ' + body
            continue
        if re.search(r'\[page \d+', line):
            pending = {}
            continue
        line = re.sub(r'<i>.*?</i>', ' ', line)
        line = MARK.sub(lambda m: f' \x00{m.group(1)} ', line)
        line = html.unescape(re.sub(r'<[^>]+>', ' ', line))
        toks = line.split()
        for k, tok in enumerate(toks):
            if tok.startswith('\x00'):
                if words:
                    pending[int(tok[1:])] = len(words) - 1
                continue
            if words and words[-1][0].endswith('-') and k == 0 and tok[:1].isalpha():
                words[-1] = (words[-1][0][:-1] + tok, words[-1][1])  # a word broken at the line's end
            else:
                words.append((tok, []))
    return [(w, ns) for w, ns in words if norm(w) or ns]


def root_words(coll, books):
    """[(key, word)] of root/pli/pts in SC order"""
    out = []
    for b in books:
        for f in ms_files(MS, coll, b):
            rel = os.path.relpath(f, os.path.dirname(MS.rstrip('/')))
            p = os.path.join(PTS_ROOT, rel.replace('_root-pli-ms.json', '_root-pli-pts.json'))
            if os.path.exists(p):
                for k, v in json.load(open(p, encoding='utf-8')).items():
                    out += [(k, w) for w in v.split() if norm(w)]
    return out


def place(ann, root):
    """ann word index -> root word index, matched a stretch at a time"""
    a = [norm(w) for w, _ in ann]
    b = [norm(w) for _, w in root]
    at, j0, CH = {}, 0, 300
    for i0 in range(0, len(a), CH):
        for win in (2500, 25000):  # lost (a passage one side has and the other not): look further on
            sm = SequenceMatcher(None, a[i0:i0 + CH], b[j0:j0 + win], autojunk=False)
            blocks = [m for m in sm.get_matching_blocks() if m.size >= 3]  # runs of words, not stray ones
            if sum(m.size for m in blocks) >= 0.3 * len(a[i0:i0 + CH]):
                break
        last = None
        for m in blocks:
            for d in range(m.size):
                at[i0 + m.a + d] = j0 + m.b + d
                last = j0 + m.b + d
        if last is not None:
            j0 = max(j0, last + 1 - CH // 3)
    return at


n_notes = n_placed = 0
for coll, books, files in pts_groups():
    root = root_words(coll, books)
    for f in files:
        ou = os.path.join(GRETIL, re.sub(r'pu\.htm$', 'ou.htm', f))
        if not root or not os.path.exists(ou):
            continue
        ann = annotated(ou)
        at = place(ann, root)
        out = {}
        for i, (w, ns) in enumerate(ann):
            for n in ns:
                n_notes += 1
                if i not in at:
                    continue
                key, word = root[at[i]]
                if SequenceMatcher(None, norm(w), norm(word)).ratio() < 0.7:
                    continue  # matched by its neighbours only: not the same word
                n_placed += 1
                word = word.strip('.,;:!?‘’“”"\'()[]|—–')
                out.setdefault(key, []).append(f'{word} → {n}')
        by_file = {}
        for key, es in out.items():
            by_file.setdefault(key.split(':')[0], {})[key] = ' | '.join(es)
        for b in books:
            for g in ms_files(MS, coll, b):
                uid = os.path.basename(g).split('_')[0]
                if uid not in by_file:
                    continue
                rel = os.path.relpath(g, os.path.dirname(MS.rstrip('/')))
                q = os.path.join(OUT, 'pts', rel.replace('_root-pli-ms.json', '_variant-pli-pts.json'))
                os.makedirs(os.path.dirname(q), exist_ok=True)
                old = json.load(open(q, encoding='utf-8')) if os.path.exists(q) else {}
                old.update(by_file[uid])
                json.dump(old, open(q, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f, len(ann), "words", sum(len(ns) for _, ns in ann), "notes", n_placed, "placed so far of", n_notes, file=sys.stderr)
print(f'{n_placed} of {n_notes} notes placed', file=sys.stderr)

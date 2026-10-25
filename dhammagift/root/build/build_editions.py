#!/usr/bin/env python3
"""Build BJT and Myanmar (VRI CST) Pali root texts on SuttaCentral ms segment ids.

Sources (re-run after every pull, the BJT license requires keeping in sync):
  BJT  : github.com/pathnirvana/tipitaka.lk  public/static/text/*.json  (CC BY-ND, attribution tipitaka.lk)
  my   : github.com/VipassanaTech/tipitaka-xml  romn/*.mul.xml        (VRI Chaṭṭha Saṅgāyana)
  ms   : github.com/suttacentral/bilara-data   root/pli/ms/sutta     (ids and segmentation only)

The edition text is never edited: it is transliterated (BJT, Sinhala to Roman), split into
words and every word is assigned to one ms segment. Joining all segments gives back the whole
edition text in order. Edition headings go to the 0.x segments of the sutta they open,
footnotes / <note> readings to variant/, page and paragraph numbers to reference/.

usage: build_editions.py --bjt DIR --vri DIR --ms DIR --out DIR [--only sn1-10,sn45-49,an1,an2]
"""
import argparse, bisect, collections, difflib, glob, json, os, re, sys, unicodedata
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- Sinhala -> Roman

SI_VOWELS = {'අ': 'a', 'ආ': 'ā', 'ඇ': 'æ', 'ඈ': 'ǣ', 'ඉ': 'i', 'ඊ': 'ī', 'උ': 'u', 'ඌ': 'ū',
             'ඍ': 'ṛ', 'එ': 'e', 'ඒ': 'ē', 'ඓ': 'ai', 'ඔ': 'o', 'ඕ': 'ō', 'ඖ': 'au'}
SI_CONS = {'ක': 'k', 'ඛ': 'kh', 'ග': 'g', 'ඝ': 'gh', 'ඞ': 'ṅ', 'ඟ': 'ṅg', 'ච': 'c', 'ඡ': 'ch',
           'ජ': 'j', 'ඣ': 'jh', 'ඤ': 'ñ', 'ඥ': 'jñ', 'ඦ': 'ñj', 'ට': 'ṭ', 'ඨ': 'ṭh', 'ඩ': 'ḍ',
           'ඪ': 'ḍh', 'ණ': 'ṇ', 'ඬ': 'ṇḍ', 'ත': 't', 'ථ': 'th', 'ද': 'd', 'ධ': 'dh', 'න': 'n',
           'ඳ': 'nd', 'ප': 'p', 'ඵ': 'ph', 'බ': 'b', 'භ': 'bh', 'ම': 'm', 'ඹ': 'mb', 'ය': 'y',
           'ර': 'r', 'ල': 'l', 'ව': 'v', 'ශ': 'ś', 'ෂ': 'ṣ', 'ස': 's', 'හ': 'h', 'ළ': 'ḷ', 'ෆ': 'f'}
SI_SIGNS = {'ා': 'ā', 'ැ': 'æ', 'ෑ': 'ǣ', 'ි': 'i', 'ී': 'ī', 'ු': 'u', 'ූ': 'ū', 'ෘ': 'ṛ',
            'ෲ': 'ṝ', 'ෙ': 'e', 'ේ': 'ē', 'ෛ': 'ai', 'ො': 'o', 'ෝ': 'ō', 'ෞ': 'au'}
SI_VIRAMA, SI_ANUSVARA, ZWJ, ZWNJ = '්', 'ං', '‍', '‌'


def si2ro(s):
    out, i, n = [], 0, len(s)
    while i < n:
        ch = s[i]
        if ch in SI_CONS:
            out.append(SI_CONS[ch])
            j = i + 1
            while j < n and s[j] in (ZWJ, ZWNJ):
                j += 1
            nx = s[j] if j < n else ''
            if nx == SI_VIRAMA:
                i = j + 1
                continue
            if nx in SI_SIGNS:
                out.append(SI_SIGNS[nx])
                i = j + 1
                continue
            out.append('a')
            i = j
            continue
        if ch in SI_VOWELS:
            out.append(SI_VOWELS[ch])
        elif ch == SI_ANUSVARA:
            out.append('ṃ')
        elif ch in (ZWJ, ZWNJ, SI_VIRAMA):
            pass
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


# ---------------------------------------------------------------- tokens

class Tok:
    __slots__ = ('text', 'norm', 'entry', 'refs', 'vars', 'heads', 'para')

    def __init__(self, text, entry):
        self.text, self.entry = text, entry
        self.norm = norm(text)
        self.refs, self.vars, self.heads, self.para = [], [], [], None


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    w = ''.join(c for c in w if not unicodedata.combining(c))
    w = w.replace('æ', 'a')
    return re.sub(r'[^a-z0-9]', '', w)


def tokenize(text, markers, entry):
    """text: entry string; markers: [(offset, kind, value)]. pb/para attach to the next word,
    note to the previous word. Returns list of Tok."""
    toks, spans = [], []
    for m in re.finditer(r'\S+', text):
        toks.append(Tok(m.group(), entry))
        spans.append((m.start(), m.end()))
    if not toks:
        return toks
    starts = [a for a, _ in spans]
    for off, kind, val in markers:
        if kind == 'note':
            k = max(0, bisect.bisect_left(starts, off) - 1)
            toks[k].vars.append((strip_punct(toks[k].text), val))
        else:
            k = bisect.bisect_left([b for _, b in spans], off + 1)
            k = min(k, len(toks) - 1)
            if kind == 'para':
                toks[k].para = toks[k].para or val
                toks[k].refs.append('para' + val)
            else:
                toks[k].refs.append(val)
    return toks


def strip_punct(w):
    return re.sub(r'^[^\w]+|[^\w]+$', '', w)


# ---------------------------------------------------------------- heading classes

NUM_RE = re.compile(r'^[\s\d.\-–\[\]()]+$')


def head_class(text, big=False):
    t = norm(text)
    if 'namotassa' in t:
        return 'above'
    if NUM_RE.match(text):
        return 'num'
    if big or re.search(r'samyutt|nipat|pannasak|nikay|pitak|bhago', t):
        return 'above'
    if re.search(r'vagg|peyyal', t) and 'sutt' not in t:
        return 'vagga'
    return 'sutta'


class Stream:
    """Edition text as words; headings are kept aside and hang on the next body word."""

    def __init__(self):
        self.toks, self.pending, self.entry = [], [], 0

    def heading(self, text, cls, refs=()):
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            self.pending.append((cls, text))
        self.pending_refs = getattr(self, 'pending_refs', []) + list(refs)

    def body(self, text, markers):
        self.entry += 1
        toks = tokenize(text, markers, self.entry)
        if not toks:
            return
        if self.pending:
            toks[0].heads, self.pending = self.pending, []
        if getattr(self, 'pending_refs', None):
            toks[0].refs[:0], self.pending_refs = self.pending_refs, []
        self.toks.extend(toks)


# ---------------------------------------------------------------- BJT reader

BJT_MARK = re.compile(r'\{([^}]*)\}')


def bjt_footnotes(page):
    fn = {}
    for f in page['pali'].get('footnotes', []):
        t = si2ro(f['text'])
        m = re.match(r'\s*([^\s.]+)\.\s*(.*)', t, re.S)
        if m:
            fn[m.group(1)] = bjt_variant(m.group(2))
    return fn


def bjt_variant(t):
    parts = []
    for p in t.split(';'):
        p = p.strip()
        m = re.match(r'(.*?)\s+[–-]\s+(.+)$', p)
        parts.append(f'{m.group(1)} ({m.group(2)})' if m else p)
    return '; '.join(x for x in parts if x)


def bjt_entries(files):
    """yield (kind, text_roman, markers, level) in book order."""
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        name = os.path.basename(f)[:-5]
        for page in d['pages']:
            fn = bjt_footnotes(page)
            first = True
            for e in page['pali']['entries']:
                raw = si2ro(e['text']).replace('**', '').replace('__', '')
                markers, buf, pos = [], [], 0
                for m in BJT_MARK.finditer(raw):
                    buf.append(raw[pos:m.start()])
                    off = sum(map(len, buf))
                    if m.group(1) in fn:
                        markers.append((off, 'note', fn[m.group(1)]))
                    pos = m.end()
                buf.append(raw[pos:])
                text = ''.join(buf)
                if first:
                    markers.insert(0, (0, 'pb', f'{name}.{page["pageNum"]}'))
                    first = False
                yield e['type'], text, markers, e.get('level') or 1


def bjt_stream(files, split_re=None):
    """Returns {chunk_number: Stream}; chunks split on saṃyutta headings when split_re given."""
    chunks, cur, n = {}, Stream(), 0
    pre = []
    for kind, text, markers, level in bjt_entries(files):
        if kind in ('heading', 'centered'):
            m = split_re.match(text.strip()) if split_re and kind == 'heading' else None
            if m:
                n = int(m.group(1))
                cur = chunks.setdefault(n, Stream())
                for h in pre:
                    cur.heading(*h)
                pre = []
            cls = head_class(text, big=level >= 4 and kind == 'heading')
            if kind == 'centered' and level == 1 and cls in ('sutta', 'vagga'):
                kind = 'body'  # end lines like "vaggo paṭhamo.", "saṃyuttaṃ samattaṃ."
            elif kind == 'centered' and cls in ('sutta', 'vagga'):
                cls = 'above'
            if kind != 'body':
                refs = [v for _, k, v in markers if k == 'pb']
                if split_re and not chunks:
                    pre.append((text, cls, refs))
                else:
                    cur.heading(text, cls, refs)
                continue
        mk = list(markers)
        m = re.match(r'\s*(\d+(?:\s*-\s*\d+)?)\.\s+', text)
        if m and kind in ('paragraph', 'unindented', 'gatha', 'body'):
            mk.append((0, 'para', m.group(1).replace(' ', '')))
            mk = [(max(0, o - m.end()), k, v) for o, k, v in mk]
            text = text[m.end():]
        if not chunks and split_re:
            chunks.setdefault(0, cur)
        cur.body(text, mk)
    if not split_re:
        chunks[0] = cur
    return chunks


# ---------------------------------------------------------------- VRI reader

def vri_root(path):
    raw = open(path, 'rb').read().decode('utf-16')
    raw = re.sub(r'<\?xml[^>]*\?>', '', raw)
    return ET.fromstring(raw)


def vri_flatten(el):
    """-> text, markers"""
    buf, markers = [], []

    def add(s):
        if s:
            buf.append(s)

    def walk(e, top=False):
        if not top:
            tag, rend = e.tag, e.get('rend')
            off = sum(map(len, buf))
            if tag == 'pb':
                markers.append((off, 'pb', e.get('ed') + e.get('n')))
            elif tag == 'note':
                markers.append((off, 'note', ''.join(e.itertext()).strip()))
            elif tag == 'hi' and rend == 'paranum':
                markers.append((off, 'para', ''.join(e.itertext()).strip()))
            elif tag == 'hi' and rend == 'dot':
                pass
            else:
                add(e.text)
                for c in e:
                    walk(c)
            add(e.tail)
            return
        add(e.text)
        for c in e:
            walk(c)

    walk(el, top=True)
    return ''.join(buf), markers


def vri_stream(path, chunk_div=None):
    """chunk_div: 'samyutta' -> {n: Stream} by div id sn<k>_<n>; None -> {0: Stream}."""
    root = vri_root(path)
    chunks = {}
    pre = Stream()

    def walk(e, cur, types):
        for c in e:
            if c.tag == 'div':
                t = c.get('type')
                nxt = cur
                if chunk_div and t == chunk_div:
                    n = int(c.get('id').split('_')[-1])
                    nxt = chunks.setdefault(n, Stream())
                    if pre.pending and n == 1:
                        nxt.pending, pre.pending = pre.pending, []
                walk(c, nxt, types + [t])
                continue
            if c.tag not in ('p', 'head', 'trailer'):
                walk(c, cur, types)
                continue
            rend = c.get('rend') or ''
            text, markers = vri_flatten(c)
            if c.tag == 'head' or rend in ('title', 'subhead', 'nikaya', 'book', 'chapter'):
                big = rend in ('nikaya', 'book') or (c.tag == 'head' and types and types[-1] in ('book', 'samyutta'))
                cur.heading(text, head_class(text, big=big), [v for _, k, v in markers if k == 'pb'])
                continue
            if rend == 'hangnum':
                para = [v for _, k, v in markers if k == 'para']
                cur.heading((para[0] + '.') if para else text, 'num',
                            [v for _, k, v in markers if k == 'pb'] + ['para' + p for p in para])
                continue
            if rend == 'centre' and 'namotassa' in norm(text):
                cur.heading(text, 'above')
                continue
            cur.body(text, markers)

    body = root.find('.//body')
    if chunk_div:
        walk(body, pre, [])
    else:
        chunks[0] = pre
        walk(body, pre, [])
    return chunks


# ---------------------------------------------------------------- ms

def ms_files(ms_dir, coll, book):
    fs = glob.glob(os.path.join(ms_dir, coll, book, '*_root-pli-ms.json'))

    def key(f):
        b = os.path.basename(f).split('_')[0][len(book) + 1:]
        return [int(x) for x in re.findall(r'\d+', b)]
    return sorted(fs, key=key)


def sutta_of(k):
    return k.split(':')[0]


def header_slots(keys):
    """per sutta: its 0.x keys and a leading N.0 key (sutta number) before the first body key."""
    slots, started = collections.OrderedDict(), set()
    for k in keys:
        s, seg = k.split(':')
        sl = slots.setdefault(s, [])
        if s in started:
            continue
        if seg.startswith('0.') or re.fullmatch(r'\d+\.0', seg):
            sl.append(k)
        else:
            started.add(s)
    return slots


# ---------------------------------------------------------------- alignment

def lis(pairs):
    """longest increasing subsequence on j of pairs sorted by i."""
    tails, prev, pos = [], [None] * len(pairs), []
    for k, (_, j) in enumerate(pairs):
        x = bisect.bisect_left([pairs[t][1] for t in tails], j)
        if x == len(tails):
            tails.append(k)
        else:
            tails[x] = k
        prev[k] = tails[x - 1] if x else None
    out, k = [], tails[-1] if tails else None
    while k is not None:
        out.append(pairs[k])
        k = prev[k]
    return out[::-1]


def patience(a, b):
    """order-preserving word matches [(i, j)]: anchors on words unique in both ranges
    (robust to repeated formulas), difflib only inside small gaps without anchors."""
    out, stack = [], [(0, len(a), 0, len(b))]
    while stack:
        alo, ahi, blo, bhi = stack.pop()
        if alo >= ahi or blo >= bhi:
            continue
        # extend equal head / tail
        while alo < ahi and blo < bhi and a[alo] == b[blo]:
            out.append((alo, blo)); alo += 1; blo += 1
        while alo < ahi and blo < bhi and a[ahi - 1] == b[bhi - 1]:
            out.append((ahi - 1, bhi - 1)); ahi -= 1; bhi -= 1
        if alo >= ahi or blo >= bhi:
            continue
        ca = collections.Counter(a[alo:ahi])
        cb = collections.Counter(b[blo:bhi])
        posb = {b[j]: j for j in range(blo, bhi) if cb[b[j]] == 1}
        pairs = [(i, posb[a[i]]) for i in range(alo, ahi) if ca[a[i]] == 1 and a[i] in posb]
        anchors = lis(pairs)
        if not anchors:
            if (ahi - alo) * (bhi - blo) <= 4_000_000:
                sm = difflib.SequenceMatcher(None, a[alo:ahi], b[blo:bhi], autojunk=False)
                for i, j, n in sm.get_matching_blocks():
                    out.extend((alo + i + k, blo + j + k) for k in range(n))
            continue
        pi, pj = alo, blo
        for i, j in anchors:
            stack.append((pi, i, pj, j))
            out.append((i, j))
            pi, pj = i + 1, j + 1
        stack.append((pi, ahi, pj, bhi))
    return sorted(out)


def head_key(text):
    """one anchor word for a title line: digits dropped, words joined, endings cut
    ("10. Nandiyasuttaṃ" ~ "Nandiyasutta", "1. naḷavaggo" ~ "1. Naḷavagga")."""
    w = norm(re.sub(r'[\d.\-–]+', ' ', text))
    w = re.sub(r'm$', '', w)
    w = re.sub(r'[aiueo]$', '', w)
    return '#' + w if len(w) > 3 else None


def vagga_num(text):
    m = re.match(r'\s*\[?(\d+)\.', text)
    return m.group(1) if m and re.search(r'vagg|peyyal', norm(text)) else None


def title_keys(text, vn):
    hk = head_key(text)
    return [hk, f'{hk}/{vn}'] if hk and vn else [hk] if hk else []


def align(toks, segs, slots_before=None):
    """toks: edition Tok list; segs: [(key, text)] body segments;
    slots_before: {body seg index: [ms header texts]} used as title anchors.
    -> seg index per tok, match ratio."""
    b, bseg = [], []
    for si, (_, t) in enumerate(segs):
        hs = (slots_before or {}).get(si, [])
        if hs:
            vn = next((vagga_num(h) for h in hs if vagga_num(h)), None)
            for hk in title_keys(hs[-1], vn):
                b.append(hk)
                bseg.append(si)
        for w in t.split():
            nw = norm(w)
            if nw:
                b.append(nw)
                bseg.append(si)
    idx, a, vn = [], [], None
    for i, t in enumerate(toks):
        for c, h in t.heads:
            if c == 'vagga' and vagga_num(h):
                vn = vagga_num(h)
            if c == 'sutta':
                for hk in title_keys(h, vn):
                    idx.append(-1)
                    a.append(hk)
        if t.norm:
            idx.append(i)
            a.append(t.norm)
    out = [None] * len(toks)
    if not b:
        return [0] * len(toks), 0.0
    matches = patience(a, b)
    ops = []
    pi = pj = 0
    for i, j in matches + [(len(a), len(b))]:
        if i > pi or j > pj:
            ops.append(('replace' if i > pi and j > pj else 'delete' if i > pi else 'insert', pi, i, pj, j))
        if i < len(a):
            ops.append(('equal', i, i + 1, j, j + 1))
        pi, pj = i + 1, j + 1
    equal = 0
    for op, i1, i2, j1, j2 in ops:
        if op == 'equal':
            equal += i2 - i1
            for k in range(i2 - i1):
                if idx[i1 + k] >= 0:
                    out[idx[i1 + k]] = bseg[j1 + k]
                else:
                    equal -= 1  # title anchors are not edition words
        elif op == 'replace':
            for k in range(i1, i2):
                j = j1 + (k - i1) * (j2 - j1) // (i2 - i1)
                if idx[k] >= 0:
                    out[idx[k]] = bseg[j]
        elif op == 'insert':  # ms words the edition does not have
            continue
        else:  # 'delete': edition words ms does not have
            ent = lambda k: toks[idx[k]].entry if idx[k] >= 0 else -k - 1
            whole = (i1 == 0 or ent(i1 - 1) != ent(i1)) and (i2 == len(a) or ent(i2) != ent(i2 - 1))
            if (whole or j1 == 0) and j1 < len(b):
                s = bseg[j1]
            else:
                s = bseg[j1 - 1]
            for k in range(i1, i2):
                if idx[k] >= 0:
                    out[idx[k]] = s
    last = None
    for i in range(len(toks)):
        if out[i] is None:
            out[i] = last
        last = out[i]
    first = next((x for x in out if x is not None), 0)
    out = [first if x is None else x for x in out]
    for i in range(1, len(out)):  # keep order monotonic
        if out[i] < out[i - 1]:
            out[i] = out[i - 1]
    return out, equal / max(1, sum(1 for x in idx if x >= 0))


def place(chunk, ms_paths, ed, out_dir, coll, book, report):
    segs_all, keys_all = [], []
    files = []
    for p in ms_paths:
        d = json.load(open(p, encoding='utf-8'))
        files.append((p, list(d.keys())))
        for k, v in d.items():
            keys_all.append(k)
            segs_all.append((k, v))
    slots = header_slots(keys_all)
    slot_keys = {k for v in slots.values() for k in v}
    body, before, hold = [], {}, []
    for k, v in segs_all:
        if k in slot_keys:
            if k.split(':')[1].startswith('0.'):
                hold.append(v)
            continue
        if hold:
            before[len(body)], hold = hold, []
        body.append((k, v))
    assign, score = align(chunk.toks, body, before)

    text = collections.defaultdict(list)
    refs = collections.defaultdict(list)
    vars_ = collections.defaultdict(list)
    leftover_heads = list(chunk.pending)
    body_words = collections.defaultdict(list)
    seen = set()
    for t, si in zip(chunk.toks, assign):
        key = body[si][0]
        s = sutta_of(key)
        start = s not in seen  # first edition word of this sutta
        seen.add(s)
        if t.heads:
            if start and slots.get(s):
                put_heads(t.heads, slots[s], text, t.para)
            else:
                text[key].append(' '.join(h for _, h in t.heads))
        elif t.para and start:
            sl = [k for k in slots.get(s, []) if not k.split(':')[1].startswith('0.')]
            if sl and not text[sl[0]]:
                text[sl[0]].append(t.para + '.')
        text[key].append(t.text)
        body_words[key].append(t.text)
        refs[key].extend(r for r in t.refs if r not in refs[key])
        vars_[key].extend(f'{l} → {r}' for l, r in t.vars)
    if leftover_heads and body:
        text[body[-1][0]].append(' '.join(h for _, h in leftover_heads))

    n_full = n_seg = 0
    for p, keys in files:
        base = os.path.basename(p).replace('_root-pli-ms.json', '')
        rel = os.path.join('sutta', coll, book)
        root = {k: (' '.join(text[k]) + ' ') if text[k] else '' for k in keys}
        n_seg += len(keys)
        n_full += sum(1 for v in root.values() if v)
        write(os.path.join(out_dir, 'root', 'pli', ed, rel, f'{base}_root-pli-{ed}.json'), root)
        v = {k: ' | '.join(vars_[k]) for k in keys if vars_[k]}
        if v:
            write(os.path.join(out_dir, 'variant', 'pli', ed, rel, f'{base}_variant-pli-{ed}.json'), v)
        r = {k: ', '.join(refs[k]) for k in keys if refs[k]}
        if r:
            write(os.path.join(out_dir, 'reference', 'pli', ed, rel, f'{base}_reference-pli-{ed}.json'), r)
    # every edition word must be somewhere, once, in order
    got = [w for k, _ in body for w in body_words[k]]
    if got != [t.text for t in chunk.toks]:
        raise SystemExit(f'{ed} {book}: edition words lost or reordered')
    n_heads = sum(len(t.heads) for t in chunk.toks) + len(leftover_heads)
    n_words = len(chunk.toks)
    report.append((ed, book, len(files), n_seg, n_full, n_words, n_heads, round(score, 3)))


def put_heads(heads, slots, text, para):
    zero = [k for k in slots if k.split(':')[1].startswith('0.')]
    nums = [k for k in slots if not k.split(':')[1].startswith('0.')]
    by = collections.defaultdict(list)
    for c, h in heads:
        by[c].append(h)
    if nums:
        text[nums[0]].extend(by.pop('num', []))
    sutta = by.get('num', []) + by.get('sutta', [])
    if not zero:
        target = nums[0]
        text[target].extend(by.get('above', []) + by.get('vagga', []) + sutta)
        return
    if len(zero) >= 3:
        text[zero[0]].extend(by.get('above', []))
        text[zero[-2]].extend(by.get('vagga', []))
        text[zero[-1]].extend(sutta)
    elif len(zero) == 2:  # ms: 0.1 nikāya, 0.2 vagga
        text[zero[0]].extend(by.get('above', []))
        text[zero[1]].extend(by.get('vagga', []) + sutta)
    else:
        text[zero[0]].extend(by.get('above', []) + by.get('vagga', []) + sutta)
    if nums and para and not text[nums[0]]:
        text[nums[0]].append(para + '.')


def write(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ---------------------------------------------------------------- catalogue

# SN: saṃyutta -> (BJT book prefix, VRI file, local number); AN: nipāta -> (BJT file, VRI file)
SN_VAGGA = [(1, 11, 'sn-1', 's0301m.mul.xml'), (12, 21, 'sn-2', 's0302m.mul.xml'),
            (22, 34, 'sn-3', 's0303m.mul.xml'), (35, 44, 'sn-4', 's0304m.mul.xml'),
            (45, 56, 'sn-5', 's0305m.mul.xml')]
AN_VRI = {1: 's0401m.mul.xml', 2: 's0402m1.mul.xml', 3: 's0402m2.mul.xml', 4: 's0402m3.mul.xml'}
SN_SPLIT = re.compile(r'^(\d+)\.\s*\S*\s*saṃyuttaṃ')


def bjt_book_files(bjt_dir, prefix):
    fs = [f for f in glob.glob(os.path.join(bjt_dir, prefix + '*.json'))
          if re.fullmatch(re.escape(prefix) + r'(-\d+)*\.json', os.path.basename(f))]
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r'\d+', os.path.basename(f))[1:]])


def parse_only(s):
    books = []
    for part in s.split(','):
        m = re.fullmatch(r'(sn|an)(\d+)(?:-(\d+))?', part.strip())
        a, b = int(m.group(2)), int(m.group(3) or m.group(2))
        books += [(m.group(1), n) for n in range(a, b + 1)]
    return books


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bjt', required=True)
    ap.add_argument('--vri', required=True)
    ap.add_argument('--ms', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='sn1-10,sn45-49,an1-2')
    ap.add_argument('--report')
    a = ap.parse_args()
    report, cache = [], {}
    for coll, n in parse_only(a.only):
        book = f'{coll}{n}'
        ms = ms_files(a.ms, coll, book)
        if coll == 'sn':
            lo, hi, bpre, vfile = next(v for v in SN_VAGGA if v[0] <= n <= v[1])
            local = n - lo + 1
            if bpre not in cache:
                cache[bpre] = bjt_stream(bjt_book_files(a.bjt, bpre), SN_SPLIT)
                cache[vfile] = vri_stream(os.path.join(a.vri, vfile), 'samyutta')
            chunks = {'bjt': cache[bpre].get(local), 'my': cache[vfile].get(local)}
        else:
            chunks = {'bjt': bjt_stream(bjt_book_files(a.bjt, f'an-{n}'))[0],
                      'my': vri_stream(os.path.join(a.vri, AN_VRI[n]))[0]}
        for ed, ch in chunks.items():
            if ch is None:
                print(f'!! {ed} {book}: chunk not found', file=sys.stderr)
                continue
            place(ch, ms, ed, a.out, coll, book, report)
            print('\t'.join(map(str, report[-1])), file=sys.stderr)
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('edition\tbook\tfiles\tsegments\tfilled\twords\theadings\tmatch\n')
            for r in report:
                f.write('\t'.join(map(str, r)) + '\n')


if __name__ == '__main__':
    main()

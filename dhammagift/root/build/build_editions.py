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
    __slots__ = ('text', 'norm', 'entry', 'refs', 'vars', 'heads', 'para', 'glue')

    def __init__(self, text, entry, glue=False):
        self.text, self.entry, self.glue = text, entry, glue
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
        start = m.start()
        for k, part in enumerate(GLUED.split(m.group())):
            toks.append(Tok(part, entry, glue=k > 0))
            spans.append((start, start + len(part)))
            start += len(part)
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


# words printed with no space between them: after , : ; ("tīhi:accayaṃ", "viditavedassa,purindadassa"), before an
# opening quote ("samāno‘na"), after an opening quote that follows -ṃ ("gotamaṃ’jinaṃ"). An elision mark stays inside
# the word ("cattāro’me" is ms "cattārome"), as does the enclitic ’ti / ’nti.
GLUED = re.compile(r"(?:(?<=[,:;])(?=[‘“’'\"]?[^\W\d_]))"
                   r"|(?:(?<=[^\W\d_])(?=[‘“][^\W\d_]))"
                   r"|(?:(?<=ṃ[’'])(?=[^\W\d_])(?!n?ti\b|ti[,.;:’'”]))")


def strip_punct(w):
    return re.sub(r'^[^\w]+|[^\w]+$', '', w)


# ---------------------------------------------------------------- heading classes

NUM_RE = re.compile(r'^[\s\d.\-–\[\]()]+$')


COLOPHON = re.compile(r'(samatt|nitthit)(o|a|am|ani|e)?$')


def colophon(text):
    """end lines of a section ("paṭhamo paṇṇāsako samatto", "akusalapeyyālaṃ niṭṭhitaṃ"): text, not a title"""
    w = [norm(x) for x in text.split() if norm(x)]
    if len(w) > 1 and ordinal(w[-1]):  # "... suttaṃ niṭṭhitaṃ navamaṃ"
        w = w[:-1]
    return bool(w) and bool(COLOPHON.match(w[-1]))


def head_class(text, big=False):
    t = norm(text)
    if 'namotassa' in t:
        return 'above'
    if NUM_RE.match(text):
        return 'num'
    if big or re.search(r'samyutt|nipat|pannasak|nikay|pitak|bhago', t):
        return 'above'
    if re.search(r'vagg|peyyal', t) and 'sutt' not in t:
        return 'vagga' if vagga_num(text) else 'above'
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
                raw = re.sub(r'-(pe|la)-', r'…\1…', raw).replace('...', '…')  # peyyāla marks as in ms
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
            if colophon(text):
                kind = 'body'
            elif kind == 'centered' and level == 1 and cls in ('sutta', 'vagga'):
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
            if (c.tag == 'head' or rend in ('title', 'subhead', 'nikaya', 'book', 'chapter')) and not colophon(text):
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


# ---------------------------------------------------------------- Thai (Siam Rath 1927, E-Tipitaka palinew.sqlite)

TH_CONS = {'ก': 'k', 'ข': 'kh', 'ค': 'g', 'ฆ': 'gh', 'ง': 'ṅ', 'จ': 'c', 'ฉ': 'ch', 'ช': 'j',
           'ฌ': 'jh', 'ญ': 'ñ', 'ฎ': 'ṭ', 'ฏ': 'ṭ', 'ฐ': 'ṭh', 'ฑ': 'ḍ', 'ฒ': 'ḍh', 'ณ': 'ṇ',
           'ต': 't', 'ถ': 'th', 'ท': 'd', 'ธ': 'dh', 'น': 'n', 'ป': 'p', 'ผ': 'ph', 'พ': 'b',
           'ภ': 'bh', 'ม': 'm', 'ย': 'y', 'ร': 'r', 'ล': 'l', 'ว': 'v', 'ส': 's', 'ห': 'h',
           'ฬ': 'ḷ', 'อ': '', 'ด': 'd', 'ซ': 's', 'ฝ': 'f', 'ฟ': 'f', 'ฅ': 'kh'}
TH_SIGNS = {'า': 'ā', 'ิ': 'i', 'ี': 'ī', 'ึ': 'iṃ', 'ุ': 'u', 'ู': 'ū'}
TH_PRE = {'เ': 'e', 'โ': 'o'}
TH_VIRAMA, TH_NIGGAHITA = 'ฺ', 'ํ'


def th2ro(s):
    # peyyāla marks written as in ms: …pe…, …la…
    s = re.sub(r'\s*ฯ\s*(เป|ล|ป)\s*ฯ', lambda m: ' …%s… ' % {'เป': 'pe', 'ล': 'la', 'ป': 'pa'}[m.group(1)], s)
    s = s.replace('...', '…')
    s = re.sub(r'\s*ฯ', '.', s)
    out, pre, i, n = [], None, 0, len(s)
    while i < n:
        ch = s[i]
        if ch in TH_PRE:
            pre = TH_PRE[ch]
        elif ch in TH_CONS:
            out.append(TH_CONS[ch])
            nx = s[i + 1] if i + 1 < n else ''
            if nx == TH_VIRAMA:
                i += 1
            elif nx in TH_SIGNS:
                out.append(TH_SIGNS[nx])
                i += 1
                pre = None
            else:
                out.append(pre or 'a')
                pre = None
        elif ch == TH_NIGGAHITA:
            out.append('ṃ')
        elif '๐' <= ch <= '๙':
            out.append(str(ord(ch) - ord('๐')))
        elif ch in ('่', '้', '๊', '๋', 'ๆ', TH_VIRAMA):
            pass
        elif ch == 'ฤ':
            out.append('ṛ')
        else:
            if pre:
                out.append(pre)
                pre = None
            out.append(ch)
        i += 1
    return ''.join(out)


TH_BODY_HEAD = re.compile(r'(tassuddan|tatruddan|uddanambhavati)')


def th_footnotes(footer):
    t = th2ro(re.sub(r'\s+', ' ', footer or '')).strip()
    fn = {}
    parts = re.split(r'(?:^|\s)(\d+)\s(?=\D)', t)
    for k in range(1, len(parts) - 1, 2):
        fn[parts[k]] = parts[k + 1].strip()
    return fn


def th_stream(db, volume):
    import sqlite3
    st = Stream()
    buf, mk = [], []

    def flush():
        if buf:
            st.body(' '.join(buf), list(mk))
        buf.clear()
        mk.clear()

    con = sqlite3.connect(db)
    for page, html, footer in con.execute(
            'select page, html, footer from main where volume=? order by page', (volume,)):
        fn = th_footnotes(footer)
        html = re.sub(r'<span class="reference">([^<]*)</span>', r'<\1>', html)
        html = re.split(r'<br/>', html)[0]
        page_ref = f'sya{volume}.{page}'
        for raw in html.split('\r\n'):
            m = re.fullmatch(r'\s*<div class="center">(.*)</div>\s*', raw)
            line = th2ro(m.group(1) if m else raw)
            if not line.strip() or re.fullmatch(r'\s*_+\s*', line):
                continue
            cls = head_class(line) if m else None
            if m and (not line.rstrip().endswith('.') or 'namotassa' in norm(line)) \
                    and not TH_BODY_HEAD.search(norm(line)) \
                    and not (cls == 'sutta' and 'sutt' not in norm(line)) \
                    and not colophon(line):  # centred verse lines and section end lines are text
                flush()
                st.heading(line, cls, [page_ref] if page_ref else [])
                page_ref = None
                continue
            if m or re.match(r'\s{4,}', raw):  # centred end line, paragraph [n], verse
                flush()
            line = ' '.join(line.split())
            joined = ' '.join(buf)
            glue = bool(buf) and joined.endswith('-') and line[:1].isalpha()  # word broken at line end
            base = len(joined) - 1 if glue else len(joined) + (1 if buf else 0)
            out, lmk, pos = [], [], 0
            for mm in re.finditer(r'\[(\d+(?:\s*-\s*\d+)?)\]\s*|\s*<([^>]*)>', line):
                out.append(line[pos:mm.start()])
                off = len(''.join(out))
                if mm.group(1):
                    lmk.append((off, 'para', mm.group(1).replace(' ', '')))
                elif mm.group(2) in fn:
                    lmk.append((off, 'note', fn[mm.group(2)]))
                pos = mm.end()
            out.append(line[pos:])
            clean = ''.join(out)
            lead = len(clean) - len(clean.lstrip())
            clean = clean.strip()
            if page_ref:
                mk.append((base, 'pb', page_ref))
                page_ref = None
            mk.extend((base + max(0, o - lead), k, v) for o, k, v in lmk)
            if clean:
                if glue:
                    buf[-1] = buf[-1][:-1] + clean
                else:
                    buf.append(clean)
    flush()
    return st


# SC reference has no sya marks for these; volumes checked against the nipāta titles in palinew.sqlite
SYA_VOLUME = {'an5': 22, 'an6': 22, 'an7': 23, 'an9': 23}


def sya_volume(ref_dir, coll, book):
    """Siam Rath volume of a SC book, from SC reference 'syaV.P' marks."""
    if book in SYA_VOLUME:
        return SYA_VOLUME[book]
    for f in ms_files(ref_dir, coll, book, suffix='_reference.json'):
        for v in json.load(open(f, encoding='utf-8')).values():
            m = re.search(r'\bsya(\d+)\.', v)
            if m:
                return int(m.group(1))
    return None


# ---------------------------------------------------------------- ms

FLAT = ('dn', 'mn')  # SC keeps these as one file per sutta, no book folder


def ms_files(ms_dir, coll, book, suffix='_root-pli-ms.json'):
    if coll in FLAT:
        f = os.path.join(ms_dir, coll, book + suffix)
        return [f] if os.path.exists(f) else []
    fs = glob.glob(os.path.join(ms_dir, coll, book, '*' + suffix))

    def key(f):
        b = os.path.basename(f).split('_')[0][len(book) + 1:]
        return [int(x) for x in re.findall(r'\d+', b)]
    return sorted(fs, key=key)


def is_subhead(k):
    """an ms subheading / number segment inside the text: the last level is 0 (an1.2:1.0, dn16:1.4.0)"""
    seg = k.split(':')[1]
    return seg.endswith('.0') and not seg.startswith('0.')


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
    tails, tails_j, prev = [], [], [None] * len(pairs)
    for k, (_, j) in enumerate(pairs):
        x = bisect.bisect_left(tails_j, j)
        if x == len(tails):
            tails.append(k)
            tails_j.append(j)
        else:
            tails[x], tails_j[x] = k, j
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
        anchors, n = gram_anchors(a, b, alo, ahi, blo, bhi)
        if not anchors:
            if (ahi - alo) * (bhi - blo) <= 4_000_000:
                sm = difflib.SequenceMatcher(None, a[alo:ahi], b[blo:bhi], autojunk=False)
                for i, j, m in sm.get_matching_blocks():
                    out.extend((alo + i + k, blo + j + k) for k in range(m))
            continue
        pi, pj = alo, blo
        for i, j in anchors:
            if i < pi or j < pj:  # overlapping n-grams
                continue
            stack.append((pi, i, pj, j))
            out.extend((i + k, j + k) for k in range(n))
            pi, pj = i + n, j + n
        stack.append((pi, ahi, pj, bhi))
    return sorted(out)


def gram_anchors(a, b, alo, ahi, blo, bhi):
    """anchors for one gap: words, then 2-, 3-, 5-word runs that occur once on both sides; in texts made
    of one repeated formula (SN 34) none may, then words occurring the same few times on both sides are
    paired in order. -> (LIS of (i, j) pairs, run length)"""
    for n in (1, 2, 3, 5):
        ga = [tuple(a[i:i + n]) for i in range(alo, ahi - n + 1)]
        gb = [tuple(b[j:j + n]) for j in range(blo, bhi - n + 1)]
        ca, cb = collections.Counter(ga), collections.Counter(gb)
        posb = {g: blo + k for k, g in enumerate(gb) if cb[g] == 1}
        pairs = [(alo + k, posb[g]) for k, g in enumerate(ga) if ca[g] == 1 and g in posb]
        anchors = lis(pairs)
        if anchors:
            return anchors, n
    if (ahi - alo) * (bhi - blo) <= 4_000_000:
        return [], 1
    ca, cb = collections.Counter(a[alo:ahi]), collections.Counter(b[blo:bhi])
    seen, posb = collections.Counter(), collections.defaultdict(list)
    for j in range(blo, bhi):
        posb[b[j]].append(j)
    pairs = []
    for i in range(alo, ahi):
        w = a[i]
        if ca[w] == cb[w] <= 8:
            pairs.append((i, posb[w][seen[w]]))
            seen[w] += 1
    return lis(pairs), 1


def head_key(text):
    """one anchor word for a title line: digits dropped, words joined, endings cut
    ("10. Nandiyasuttaṃ" ~ "Nandiyasutta", "1. naḷavaggo" ~ "1. Naḷavagga")."""
    w = norm(re.sub(r'[\d.\-–]+', ' ', text))
    w = re.sub(r'm$', '', w)
    w = re.sub(r'[aiueo]$', '', w)
    return '#' + w if len(w) > 3 else None


ORDINALS = ['patham', 'dutiy', 'tatiy', 'catutth', 'pancam', 'chatth', 'sattam', 'attham',
            'navam', 'dasam', 'ekadasam', 'dvadasam', 'terasam', 'cuddasam', 'pannarasam',
            'solasam', 'sattarasam', 'attharasam']
ORD_RE = re.compile(r'^(%s)(o|am|a|e)?$' % '|'.join(ORDINALS))


def ordinal(word):
    m = ORD_RE.match(norm(word))
    return str(ORDINALS.index(m.group(1)) + 1) if m else None


def vagga_num(text):
    if not re.search(r'vagg|peyyal', norm(text)):
        return None
    m = re.match(r'\s*\[?(\d+)\.', text)
    if m:
        return m.group(1)
    return next((ordinal(w) for w in text.split()[1:] if ordinal(w)), None)  # "naḷavaggo paṭhamo"


def title_keys(text, vn):
    words = text.split()
    texts = [text]
    if len(words) > 1 and ordinal(words[0]):  # "paṭhamaṃ oghataraṇasuttaṃ"
        texts.append(' '.join(words[1:]))
    keys = []
    for t in texts:
        hk = head_key(t)
        if hk:
            keys += [hk, f'{hk}/{vn}'] if vn else [hk]
    return keys


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
    matched = set()

    def starts(k):
        return idx[k] < 0 or bool(toks[idx[k]].heads) or toks[idx[k]].para is not None

    equal = 0
    for op, i1, i2, j1, j2 in ops:
        if op == 'equal':
            equal += i2 - i1
            for k in range(i2 - i1):
                if idx[i1 + k] >= 0:
                    out[idx[i1 + k]] = bseg[j1 + k]
                    matched.add(idx[i1 + k])
                else:
                    equal -= 1  # title anchors are not edition words
        elif op == 'replace':
            # where a sutta boundary of ms falls in or right after the block, the edition words from its
            # heading or, failing that, its new paragraph on, open the next sutta; both sides are split there
            prev_s = sutta_of(segs[bseg[j1 - 1]][0]) if j1 > 0 else None
            jc = next((j for j in range(j1, min(j2 + 1, len(b))) if sutta_of(segs[bseg[j]][0]) != prev_s), None)
            cut = i2
            if jc is not None and j1 > 0:
                cut = next((k for k in range(i1, i2) if starts(k)), i2)
            else:
                jc = j2
            for k in range(i1, i2):
                if idx[k] < 0:
                    continue
                if k < cut:
                    j = j1 + (k - i1) * (jc - j1) // (cut - i1) if jc > j1 else max(j1 - 1, 0)
                else:
                    j = jc + (k - cut) * (j2 - jc) // (i2 - cut) if j2 > jc else min(jc, len(b) - 1)
                out[idx[k]] = bseg[j]
        elif op == 'insert':  # ms words the edition does not have
            continue
        else:  # 'delete': edition words ms does not have
            ent = lambda k: toks[idx[k]].entry if idx[k] >= 0 else -k - 1
            whole = (i1 == 0 or ent(i1 - 1) != ent(i1)) and (i2 == len(a) or ent(i2) != ent(i2 - 1))
            nxt = bseg[j1] if j1 < len(b) else bseg[j1 - 1]
            prv = bseg[j1 - 1] if j1 > 0 else nxt
            boundary = sutta_of(segs[prv][0]) != sutta_of(segs[nxt][0])
            if not boundary and nxt != prv and is_subhead(segs[nxt][0]):
                nxt = prv  # an ms subheading segment (dn8:5.0) takes no edition text it lacks
            cut = next((k for k in range(i1, i2) if starts(k) if boundary or idx[k] < 0 or toks[idx[k]].heads), i2)
            # the edition opens the next sutta right after these words: they close the previous one
            closes = boundary and cut == i2 and i2 < len(a) and starts(i2) and j1 > 0
            for k in range(i1, i2):
                if idx[k] >= 0:
                    if boundary and j1 > 0:  # sutta boundary: split at the edition's own start of the next sutta
                        out[idx[k]] = prv if closes or k < cut else nxt
                    else:
                        out[idx[k]] = nxt if (whole or j1 == 0 or k >= cut) else prv
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
    # an ms subheading inside a sutta (dn8:5.0, "N.0 Tassuddānaṁ") keeps only edition words that match it;
    # the rest is the end of the previous segment (vagga end lines, readings ms lacks)
    sub = {si for si, (k, _) in enumerate(segs) if is_subhead(k)
           and si > 0 and sutta_of(segs[si - 1][0]) == sutta_of(k)}
    i = 0
    while i < len(toks):  # move the words before the first one that matches (all, if none does)
        if out[i] in sub:
            j = i
            while j < len(toks) and out[j] == out[i] and j not in matched and not toks[j].heads:
                j += 1
            seg = out[i]
            for k in range(i, j):
                out[k] = seg - 1
            while j < len(toks) and out[j] == seg:
                j += 1
            i = j
        else:
            i += 1
    return out, equal / max(1, sum(1 for x in idx if x >= 0))


def place(chunk, ms_paths, ed, out_dir, label, report, write_books=None):
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
            prev = body[si - 1][0] if si > 0 else None
            if start and slots.get(s):
                put_heads(t.heads, slots[s], text, t.para)
            elif prev and sutta_of(prev) == s and is_subhead(prev) and not text[prev]:
                text[prev].append(' '.join(h for _, h in t.heads))  # a subheading ms keeps in its own N.0 segment
            else:
                text[key].append(' '.join(h for _, h in t.heads))
        elif t.para and start:
            sl = [k for k in slots.get(s, []) if not k.split(':')[1].startswith('0.')]
            if sl and not text[sl[0]]:
                text[sl[0]].append(t.para + '.')
        if t.glue and body_words[key] and text[key] and text[key][-1].endswith(body_words[key][-1]):
            text[key][-1] += t.text
        else:
            text[key].append(t.text)
        body_words[key].append(t.text)
        refs[key].extend(r for r in t.refs if r not in refs[key])
        vars_[key].extend(f'{l} → {r}' for l, r in t.vars)
    if leftover_heads and body:
        text[body[-1][0]].append(' '.join(h for _, h in leftover_heads))

    n_full = n_seg = n_written = 0
    for p, keys in files:
        base = os.path.basename(p).replace('_root-pli-ms.json', '')
        book = base.split('.')[0]
        if write_books and book not in write_books:
            continue
        coll = re.match(r'[a-z]+', book).group()
        rel = os.path.join('sutta', coll) if coll in FLAT else os.path.join('sutta', coll, book)
        root = {k: (' '.join(text[k]) + ' ') if text[k] else '' for k in keys}
        n_seg += len(keys)
        n_written += 1
        n_full += sum(1 for v in root.values() if v)
        write(os.path.join(out_dir, 'root', 'pli', ed, rel, f'{base}_root-pli-{ed}.json'), root)
        v = {k: ' | '.join(vars_[k]) for k in keys if vars_[k]}
        write_or_drop(os.path.join(out_dir, 'variant', 'pli', ed, rel, f'{base}_variant-pli-{ed}.json'), v)
        r = {k: ', '.join(refs[k]) for k in keys if refs[k]}
        write_or_drop(os.path.join(out_dir, 'reference', 'pli', ed, rel, f'{base}_reference-pli-{ed}.json'), r)
    # every edition word must be somewhere, once, in order
    got = [w for k, _ in body for w in body_words[k]]
    if got != [t.text for t in chunk.toks]:
        raise SystemExit(f'{ed} {label}: edition words lost or reordered')
    n_heads = sum(len(t.heads) for t in chunk.toks) + len(leftover_heads)
    n_words = len(chunk.toks)
    report.append((ed, label, n_written, n_seg, n_full, n_words, n_heads, round(score, 3)))


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


def write_or_drop(path, d):
    """an empty file is not written, and one left from an earlier build is removed"""
    if d:
        write(path, d)
    elif os.path.exists(path):
        os.remove(path)


def write(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ---------------------------------------------------------------- catalogue

# Each edition volume is aligned whole against all SC books inside it (as for Thai), so no text
# can spill from one book into the next and no splitting on headings is needed.
# collection: [(first SC book number, last, BJT file prefix, VRI file)]
VOLUMES = {
    'dn': [(1, 13, 'dn-1', 's0101m.mul.xml'), (14, 23, 'dn-2', 's0102m.mul.xml'), (24, 34, 'dn-3', 's0103m.mul.xml')],
    'mn': [(1, 50, 'mn-1', 's0201m.mul.xml'), (51, 100, 'mn-2', 's0202m.mul.xml'), (101, 152, 'mn-3', 's0203m.mul.xml')],
    'sn': [(1, 11, 'sn-1', 's0301m.mul.xml'), (12, 21, 'sn-2', 's0302m.mul.xml'), (22, 34, 'sn-3', 's0303m.mul.xml'),
           (35, 44, 'sn-4', 's0304m.mul.xml'), (45, 56, 'sn-5', 's0305m.mul.xml')],
    'an': [(n, n, f'an-{n}', f) for n, f in enumerate(
        ['s0401m.mul.xml', 's0402m1.mul.xml', 's0402m2.mul.xml', 's0402m3.mul.xml', 's0403m1.mul.xml',
         's0403m2.mul.xml', 's0403m3.mul.xml', 's0404m1.mul.xml', 's0404m2.mul.xml', 's0404m3.mul.xml',
         's0404m4.mul.xml'], 1)],
}
LAST = {c: v[-1][1] for c, v in VOLUMES.items()}


def bjt_book_files(bjt_dir, prefix):
    fs = [f for f in glob.glob(os.path.join(bjt_dir, prefix + '*.json'))
          if re.fullmatch(re.escape(prefix) + r'(-\d+)*\.json', os.path.basename(f))]
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r'\d+', os.path.basename(f))[1:]])


def parse_only(s):
    books = []
    for part in s.split(','):
        part = part.strip()
        m = re.fullmatch(r'(dn|mn|sn|an)(?:(\d+)(?:-(\d+))?)?', part)
        if not m:
            raise SystemExit(f'--only: cannot read {part!r} (e.g. dn, mn1-50, sn1-56, an4)')
        a = int(m.group(2) or 1)
        b = int(m.group(3) or m.group(2) or LAST[m.group(1)])
        books += [(m.group(1), n) for n in range(a, b + 1)]
    return books


def log(report):
    print('\t'.join(map(str, report[-1])), file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bjt', required=True)
    ap.add_argument('--vri', required=True)
    ap.add_argument('--ms', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='dn,mn,sn,an', help='e.g. dn,mn,sn1-10,an4')
    ap.add_argument('--thai', help='E-Tipitaka palinew.sqlite (Siam Rath 1927)')
    ap.add_argument('--ref', help='bilara-data reference/pli/ms/sutta, for Siam Rath volumes')
    ap.add_argument('--report')
    a = ap.parse_args()
    report = []
    asked = {f'{c}{n}' for c, n in parse_only(a.only)}
    for coll, vols in VOLUMES.items():
        for lo, hi, bjt_prefix, vri_file in vols:
            inside = [f'{coll}{n}' for n in range(lo, hi + 1)]
            books = asked.intersection(inside)
            if not books:
                continue
            ms = [p for b in inside for p in ms_files(a.ms, coll, b)]
            label = f'{coll}{lo}-{hi}' if lo != hi else f'{coll}{lo}'
            place(bjt_stream(bjt_book_files(a.bjt, bjt_prefix))[0], ms, 'bjt', a.out, label, report, books)
            log(report)
            place(vri_stream(os.path.join(a.vri, vri_file))[0], ms, 'my', a.out, label, report, books)
            log(report)
    if a.thai:
        want = collections.defaultdict(set)  # Siam Rath volume -> books to write
        for b in asked:
            want[sya_volume(a.ref, re.match(r'[a-z]+', b).group(), b)].add(b)
        for vol, books in sorted(want.items()):
            coll = re.match(r'[a-z]+', next(iter(books))).group()
            inside = [f'{coll}{n}' for n in range(1, LAST[coll] + 1) if sya_volume(a.ref, coll, f'{coll}{n}') == vol]
            ms = [p for b in inside for p in ms_files(a.ms, coll, b)]
            label = f'sya{vol}:{inside[0]}-{inside[-1]}'
            place(th_stream(a.thai, vol), ms, 'th', a.out, label, report, books)
            log(report)
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('edition\tvolume\tfiles\tsegments\tfilled\twords\theadings\tmatch\n')
            for r in report:
                f.write('\t'.join(map(str, r)) + '\n')


if __name__ == '__main__':
    main()

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
import argparse
import html, bisect, collections, difflib, glob, json, os, re, sys, unicodedata
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
SI_PRE = {'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ'}  # signs written left of the consonant


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
        if ch in SI_SIGNS and i + 1 < n and s[i + 1] in SI_CONS and ch in SI_PRE:
            out.append(SI_CONS[s[i + 1]] + SI_SIGNS[ch])  # sign typed before its consonant (source typo)
            i += 2
            continue
        if ch in SI_SIGNS:
            out.append(SI_SIGNS[ch])  # a sign with no consonant: its vowel
        elif ch in SI_VOWELS:
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
    __slots__ = ('text', 'norm', 'entry', 'refs', 'vars', 'heads', 'para', 'glue', 'end')

    def __init__(self, text, entry, glue=False):
        self.text, self.entry, self.glue = text, entry, glue
        self.norm = norm(text)
        self.refs, self.vars, self.heads, self.para = [], [], [], None
        self.end = False  # a word of a section end line ("upālipucchākathā niṭṭhitā"): no anchor


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    w = ''.join(c for c in w if not unicodedata.combining(c))
    w = w.replace('æ', 'a')
    w = re.sub(r'[^a-z0-9]', '', w)
    return '' if w.isdigit() else w  # a bare number (list mark, paragraph) is no word to align on


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
                   r"|(?:(?<=[^\W\d_]-)(?=[^\W\d_]))"  # BJT verse halves "rammā-agamā"
                   r"|(?:(?<=[^\W\d_][.?!])(?=[\[(]|[A-ZĀĪŪṬḌṆÑṄḶ]))"  # VRI "patthiyo.[iti", "ekanidānāni.Vihāravaggo"
                   r"|(?:(?<=[^\s(\[])(?=[\[(][^\W\d_]))"  # "attanā-(sabhiyāti", VRI "patthiyo’’.[iti"
                   r"|(?:(?<=[.?!])(?=[‘“]+[^\W\d_]))"  # VRI "nāgaseno’’ti?‘‘Na", "jānāhī’’ti.‘‘Suṭṭhu"
                   r"|(?:(?<=[–—])(?=[‘“’'\"]?[^\W\d_]))"  # BJT "gotama,–na"
                   r"|(?:(?<=[^\W\d_])(?=-\d+$))"  # VRI Pātimokkha "Pubbakaraṇaṃ-4" (number of items)
                   r"|(?:(?<=[^\s…])(?=…(?:pe|la|pa)…))|(?:(?<=…(?:pe|la|pa)…)(?=[^\s…]))"  # VRI "nissajjitabbaṃ…pe…"
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
        if len(toks) <= 6 and colophon(text):
            for t in toks:
                t.end = True
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


def bjt_end_line(text, level, kind):
    """BJT prints the end line of a vagga / paṇṇāsaka like a title. A vagga that starts carries its number
    ("15. navapurāṇavaggo", "[5. parisavaggo]"), the end line has none ("navapurāṇavaggo pañcadasamo.",
    "catuttha gaṅgāpeyyāli"); a paṇṇāsaka end line ends with a full stop ("paṭhamo paṇṇāsako.")."""
    t = norm(text)
    if level >= 4 and kind == 'heading':  # book titles (sagāthavaggo)
        return False
    if re.search(r'vagg|peyyal', t) and not re.match(r'\s*\[?\d', text):
        return True
    return 'pannasak' in t and text.rstrip().endswith('.')


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


def tail_titles(entries):
    """Sutta titles printed after their text (BJT Jātaka: verse, then "4. macchajātakaṃ."; the vagga's text
    starts before its first title and its last title is followed by no text): end lines, text like ms
    "Macchajātakaṁ pañcamaṁ."."""
    def cls(i):
        kind, text, _, level = entries[i]
        if kind not in ('heading', 'centered') or colophon(text) or bjt_end_line(text, level, kind):
            return None
        if kind != 'heading':
            return 'centered'
        return head_class(text) if level == 1 else 'above'  # level 2+ is a vagga or higher (AN1 "14. etadaggapāḷi.")
    segs, i = [], 0
    while i < len(entries):
        j = i + 1
        while j < len(entries) and cls(j) not in ('vagga', 'above'):
            j += 1
        titles = [k for k in range(i + 1, j) if cls(k) == 'sutta']
        if titles:
            text_first = any(entries[k][0] in ('paragraph', 'gatha') for k in range(i + 1, titles[0]))
            nxt = entries[titles[-1] + 1] if titles[-1] + 1 < j else None
            text_after = nxt and nxt[0] in ('paragraph', 'gatha', 'unindented') and 'uddān' not in nxt[1]
            segs.append((titles, text_first, len(titles) > 1 and not text_after))
        i = j
    # a book where most vaggas print their titles after the text does so also in a vagga of one title (Thag 30-70)
    tail = sum(1 for _, first, clear in segs if first and clear)
    if not tail or tail * 2 < sum(1 for t, _, _ in segs if len(t) > 1):
        return set()
    return {k for titles, first, _ in segs if first for k in titles}


def bjt_stream(files, split_re=None):
    """Returns {chunk_number: Stream}; chunks split on saṃyutta headings when split_re given."""
    chunks, cur, n = {}, Stream(), 0
    pre = []
    entries = list(bjt_entries(files))
    tails = tail_titles(entries)
    for n_e, (kind, text, markers, level) in enumerate(entries):
        if kind in ('heading', 'centered'):
            m = split_re.match(text.strip()) if split_re and kind == 'heading' else None
            if m:
                n = int(m.group(1))
                cur = chunks.setdefault(n, Stream())
                for h in pre:
                    cur.heading(*h)
                pre = []
            cls = head_class(text, big=level >= 4 and kind == 'heading')
            if colophon(text) or bjt_end_line(text, level, kind) or n_e in tails:
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
    """path: a file or a list of files read as one text. chunk_div: 'samyutta' -> {n: Stream} by div id
    sn<k>_<n>; None -> {0: Stream}."""
    paths = path if isinstance(path, list) else [path]
    chunks = {}
    pre = Stream()
    stop = [None]

    class Stop(Exception):
        pass

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
            if stop[0] and rend == 'chapter' and text.strip().startswith(stop[0]):
                raise Stop
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

    for path in paths:
        path, _, stop[0] = path.partition('|')  # 'vin04t.nrf.xml|Kaṅkhāvitaraṇī': the text before that chapter
        body = vri_root(path).find('.//body')
        if not chunk_div:
            chunks[0] = pre
        try:
            walk(body, pre, [])
        except Stop:
            pass
    return chunks


# ---------------------------------------------------------------- Mahāsaṅgīti as printed (World Tipiṭaka 2005)

def t2500_pages(vol_dir):
    """the pages of a volume of tipitaka2500.github.io in reading order: a page, then the pages under it"""
    def num(name):
        return [int(x) for x in re.findall(r'\d+', name)]

    def walk(d):
        for f in sorted((f for f in os.listdir(d) if f.endswith('.html')), key=num):
            yield os.path.join(d, f)
            sub = os.path.join(d, f[:-5])
            if os.path.isdir(sub):
                yield from walk(sub)
    yield vol_dir + '.html'
    yield from walk(vol_dir)


def t2500_stream(vol_dirs):
    """Mahāsaṅgīti Tipiṭaka Buddhavasse 2500 (Dhamma Society 2005), as reconstructed by tipitaka2500.github.io
    (CC0): the text SC ms comes from, before SC's edits. For comparison only."""
    st = Stream()
    for vol in vol_dirs:
        for path in t2500_pages(vol):
            t = open(path, encoding='utf-8').read()
            t = t[t.find('<div class="container overflow-scroll">'):t.find('<div class="fixed_bottom')]
            t = re.sub(r'<nav.*?</nav>|<div class="m-4 p-4.*?</div>|<ul class="list-group.*?</ul>', '', t, flags=re.S)
            for m in re.finditer(r'<(h3|p)([^>]*)>(.*?)</\1>', t, flags=re.S):
                tag, attr, inner = m.groups()
                para = re.search(r'text-bg-secondary[^>]*>\s*(\d+(?:-\d+)?)\.?\s*<', inner)
                inner = re.sub(r'<span class="badge[^>]*>.*?</span>', '', inner, flags=re.S)
                text = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', inner)).split())
                if not text:
                    continue
                if tag == 'h3' or re.search(r'text-center h[13]', attr):
                    st.heading(text, head_class(text))
                else:
                    st.body(text, [(0, 'para', para.group(1))] if para else [])
    return st


# ---------------------------------------------------------------- Thai (Siam Rath 1927, E-Tipitaka palinew.sqlite)

TH_CONS = {'ก': 'k', 'ข': 'kh', 'ค': 'g', 'ฆ': 'gh', 'ง': 'ṅ', 'จ': 'c', 'ฉ': 'ch', 'ช': 'j',
           'ฌ': 'jh', 'ญ': 'ñ', 'ฎ': 'ṭ', 'ฏ': 'ṭ', 'ฐ': 'ṭh', 'ฑ': 'ḍ', 'ฒ': 'ḍh', 'ณ': 'ṇ',
           'ต': 't', 'ถ': 'th', 'ท': 'd', 'ธ': 'dh', 'น': 'n', 'ป': 'p', 'ผ': 'ph', 'พ': 'b',
           'ภ': 'bh', 'ม': 'm', 'ย': 'y', 'ร': 'r', 'ล': 'l', 'ว': 'v', 'ส': 's', 'ห': 'h',
           'ฬ': 'ḷ', 'อ': '', 'ด': 'd', 'ซ': 's', 'ฝ': 'f', 'ฟ': 'f', 'ฅ': 'kh', 'ฃ': 'kh', 'บ': 'b'}
TH_SIGNS = {'า': 'ā', 'ิ': 'i', 'ี': 'ī', 'ึ': 'iṃ', 'ุ': 'u', 'ู': 'ū', 'ั': 'a'}
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
            if nx in (TH_VIRAMA, '๎'):  # ๎ (yamakkan) marks a cluster like the pinthu
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
        elif ch in ('่', '้', '๊', '๋', 'ๆ', '์', '็', TH_VIRAMA, '๎'):  # tone and Thai-only marks
            pass
        elif ch in TH_SIGNS:
            out.append(TH_SIGNS[ch])  # a sign with no consonant: its vowel
        elif ch == 'ฤ':
            out.append('ṛ')
        else:
            if pre:
                out.append(pre)
                pre = None
            out.append(ch)
        i += 1
    return ''.join(out)


# on the last word; strict endings, so verse words like vādapathātivattaṃ, vusitabrahmacariyo are no titles
TH_TITLE = re.compile(r'(sutt[a-z]*|jatak[a-z]*|vatthu|apadan[a-z]*|niddes[a-z]*|kath(a|am|o)?|panh[a-z]*'
                      r'|gath(a|ayo)|cariy(a|am)|vams(o|am)|uddes[a-z]*|path(o|am)|kand(a|am|o)|sikkhapad(a|am))$')
TH_BODY_HEAD = re.compile(r'(tassuddan|tatruddan|uddanambhavati)')


def th_footnotes(footer):
    t = th2ro(re.sub(r'\s+', ' ', footer or '')).strip()
    fn = {}
    parts = re.split(r'(?:^|\s)(\d+)\s(?=\D)', t)
    for k in range(1, len(parts) - 1, 2):
        fn[parts[k]] = parts[k + 1].strip()
    return fn


def th_stream(db, volume):
    """volume: a Siam Rath volume or a list of them read as one text"""
    import sqlite3
    st = Stream()
    buf, mk = [], []

    def flush():
        if buf:
            st.body(' '.join(buf), list(mk))
        buf.clear()
        mk.clear()

    con = sqlite3.connect(db)
    vols = volume if isinstance(volume, list) else [volume]
    for volume, page, html, footer in con.execute(
            'select volume, page, html, footer from main where volume in (%s) order by volume, page'
            % ','.join('?' * len(vols)), vols):
        fn = th_footnotes(footer)
        html = re.sub(r'<span class="reference">([^<]*)</span>', r'<\1>', html)
        html = re.split(r'<br/>', html)[0]
        page_ref = f'sya{volume}.{page}'
        for raw in html.split('\r\n'):
            m = re.fullmatch(r'\s*<div class="center">(.*)</div>\s*', raw)
            line = th2ro(m.group(1) if m else raw)
            if m:
                line = re.sub(r'\s*<[^>]*>', '', line)  # footnote marks in a title line
            if not line.strip() or re.fullmatch(r'\s*_+\s*', line):
                continue
            cls = head_class(line) if m else None
            if m and (not line.rstrip().endswith('.') or 'namotassa' in norm(line)) \
                    and not TH_BODY_HEAD.search(norm(line)) \
                    and not (cls == 'sutta' and not TH_TITLE.search(norm(line.split()[-1]))) \
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


def sya_volumes(ref_dir, coll, book):
    """all Siam Rath volumes a SC book is printed in"""
    if book in SYA_VOLUME:
        return {SYA_VOLUME[book]}
    vols = set()
    for f in ms_files(ref_dir, coll, book, suffix='_reference.json'):
        for v in json.load(open(f, encoding='utf-8')).values():
            vols.update(int(m) for m in re.findall(r'\bsya(\d+)\.', v))
    return vols


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
    """ms_dir: the sutta folder of root/ or reference/; Vinaya files are in the vinaya folder beside it"""
    if coll == 'vinaya':
        fs = [f for f in glob.glob(os.path.join(os.path.dirname(ms_dir.rstrip('/')), 'vinaya', '**', book + '*' + suffix),
                                   recursive=True)
              if re.fullmatch(re.escape(book) + r'[\d.-]*', os.path.basename(f)[:-len(suffix)])]
        return sorted(fs, key=lambda f: [int(x) for x in re.findall(r'\d+', os.path.basename(f)[len(book):])])
    if coll in FLAT:
        f = os.path.join(ms_dir, coll, book + suffix)
        return [f] if os.path.exists(f) else []
    fs = glob.glob(os.path.join(ms_dir, coll, book, '**', '*' + suffix), recursive=True)

    def key(f):
        b = os.path.basename(f).split('_')[0][len(book):]
        return [int(x) for x in re.findall(r'\d+', b)]
    return sorted(fs, key=key)


def is_subhead(k):
    """an ms subheading / number segment inside the text: the last level is 0 (an1.2:1.0, dn16:1.4.0)"""
    parts = k.split(':')[1].split('.')
    return parts[0] != '0' and '0' in parts[1:]  # an1.2:1.0, dn16:1.4.0, dn1:1.28.0.2


def sutta_of(k):
    return k.split(':')[0]


def header_slots(keys, texts=None):
    """per sutta: its 0.x keys and a leading N.0 key (sutta number) before the first body key.
    A 0.x that is a sentence (Vinaya sk1:0.6 "Ime kho panāyasmanto sekhiyā dhammā uddesaṁ āgacchanti.") is text."""
    slots, started = collections.OrderedDict(), set()
    for k in keys:
        s, seg = k.split(':')
        sl = slots.setdefault(s, [])
        if s in started:
            continue
        t = (texts or {}).get(k, '').strip()
        if len(t.split()) >= 5 and t[-1:] in '.?—':
            started.add(s)
        elif seg.startswith('0.') or re.fullmatch(r'\d+\.0', seg):
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


def patience(a, b, weak=frozenset(), weak_b=frozenset()):
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
        anchors, n = gram_anchors(a, b, alo, ahi, blo, bhi, weak, weak_b)
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


def gram_anchors(a, b, alo, ahi, blo, bhi, weak=frozenset(), weak_b=frozenset()):
    """anchors for one gap: words, then 2-, 3-, 5-word runs that occur once on both sides; in texts made
    of one repeated formula (SN 34) none may, then words occurring the same few times on both sides are
    paired in order; in a gap too long for difflib, runs of 8, 13, 21 words first. -> (LIS of (i, j) pairs, run length)"""
    for n in (1, 2, 3, 5, 8, 13, 21):  # long runs: formulas repeated with one word changed (kd9 Campeyya)
        if n > 5 and (ahi - alo) * (bhi - blo) <= 4_000_000:
            break
        ga = [tuple(a[i:i + n]) for i in range(alo, ahi - n + 1)]
        gb = [tuple(b[j:j + n]) for j in range(blo, bhi - n + 1)]
        ca, cb = collections.Counter(ga), collections.Counter(gb)
        posb = {g: blo + k for k, g in enumerate(gb) if cb[g] == 1}
        pairs = [(alo + k, posb[g]) for k, g in enumerate(ga) if ca[g] == 1 and g in posb
                 and not any(alo + k + x in weak or posb[g] + x in weak_b for x in range(n))]
        # an edition end line and an ms subheading repeat a title (kd11:1.0.1 "1. Tajjanīyakamma"): no anchor
        if (ahi - alo) * (bhi - blo) > 4_000_000:  # a long gap: a pair far from its place on the other side is
            near = [(i, j) for i, j in pairs  # a look-alike line (kd13 "(yathā heṭṭhā tathā vitthāretabbaṁ)")
                    if abs((i - alo) / (ahi - alo) - (j - blo) / (bhi - blo)) <= 0.35]
            pairs = near or pairs
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


def spacing(A, B):
    """Word pairs of a gap where the two texts space compounds differently (`yoniso manasikāro`,
    ms `yonisomanasikāro`): edit distance where 2 or 3 words joined equal one word at no cost.
    -> (words matched, B index per A word) or None when nothing joins or matches."""
    n, m = len(A), len(B)
    if not n or not m or n * m > 4000:
        return None
    INF = 1 << 30
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            c = cost[i][j]
            if c == INF:
                continue
            steps = []
            if i < n and j < m:
                steps.append((1, 1, 0 if A[i] == B[j] else 1))
            for w in (2, 3):
                if i + w <= n and j < m and ''.join(A[i:i + w]) == B[j]:
                    steps.append((w, 1, 0))
                if j + w <= m and i < n and A[i] == ''.join(B[j:j + w]):
                    steps.append((1, w, 0))
            if i < n:
                steps.append((1, 0, 1))
            if j < m:
                steps.append((0, 1, 1))
            for di, dj, dc in steps:
                if c + dc < cost[i + di][j + dj]:
                    cost[i + di][j + dj] = c + dc
                    back[i + di][j + dj] = (di, dj, dc)
    pairs, got, i, j = [None] * n, 0, n, m
    while i or j:
        di, dj, dc = back[i][j]
        i, j = i - di, j - dj
        for k in range(di):
            pairs[i + k] = j if dj else None
        if di and dj and not dc:
            got += di
    if not got:
        return None
    last = next((p for p in pairs if p is not None), 0)
    for k in range(n):  # words only the edition has go with the word before
        if pairs[k] is None:
            pairs[k] = last
        last = pairs[k]
    return got, pairs


def align(toks, segs, slots_before=None, with_matched=False):
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
    matches = patience(a, b, {k for k, i in enumerate(idx) if i >= 0 and toks[i].end},
                       {j for j, si in enumerate(bseg) if not b[j].startswith('#') and (
                           is_subhead(segs[si][0]) or len(segs[si][1].split()) <= 6 and colophon(segs[si][1]))})
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
                fit = spacing(a[i1:i2], b[j1:j2])
                if fit:
                    got, pairs = fit
                    equal += got
                    for k, j in enumerate(pairs):
                        if idx[i1 + k] >= 0:
                            out[idx[i1 + k]] = bseg[j1 + j]
                    continue
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
    # edition words that are, word for word, an ms segment left empty right before (or after) their segment go
    # there: VRI prints "Ime kho panāyasmanto … āgacchanti." after the title, BJT before it (pc1:1.0.2)
    seg_words = [[w for w in map(norm, t.split()) if w] for _, t in segs]
    runs = collections.defaultdict(list)
    for i, si in enumerate(out):
        if toks[i].norm:
            runs[si].append(i)
    for si in sorted(runs):
        got = runs[si]
        for j in range(si - 1, max(-1, si - 4), -1):  # leading words -> an empty segment before
            if runs.get(j) or sutta_of(segs[j][0]) != sutta_of(segs[si][0]):
                break
            w = seg_words[j]
            if w and len(w) < len(got) and [toks[i].norm for i in got[:len(w)]] == w:
                for i in range(got[0], got[len(w) - 1] + 1):
                    out[i] = j
                runs[j], got = got[:len(w)], got[len(w):]
                runs[si] = got
                break
        for j in range(si + 1, min(len(segs), si + 4)):  # trailing words -> an empty segment after
            if runs.get(j) or sutta_of(segs[j][0]) != sutta_of(segs[si][0]):
                break
            w = seg_words[j]
            if w and len(w) < len(got) and [toks[i].norm for i in got[-len(w):]] == w:
                last = got[-len(w)]
                for i in range(last, len(toks)):
                    if out[i] != si:
                        break
                    out[i] = j
                runs[j], runs[si] = got[-len(w):], got[:-len(w)]
                break
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
    ratio = equal / max(1, sum(1 for x in idx if x >= 0))
    return (out, ratio, matched) if with_matched else (out, ratio)


def reordered(toks, body):
    """suttas the edition prints in another order (BJT Jātaka: Khaṇḍahāla = ms ja544 right after Nimi ja541):
    the edition's text is cut at its own sutta titles, each block goes to the ms sutta whose rare words it has;
    a block whose sutta gets no block in the common order is that sutta. -> [(lo, hi, ms body indices)]"""
    by = collections.OrderedDict()
    for si, (k, _) in enumerate(body):
        by.setdefault(sutta_of(k), []).append(si)
    starts = [i for i, t in enumerate(toks) if any(c == 'sutta' for c, _ in t.heads)]
    if len(by) < 3 or len(starts) < 3:
        return []
    order = {s: n for n, s in enumerate(by)}
    words = {s: {w for si in ix for w in map(norm, body[si][1].split()) if len(w) >= 4} for s, ix in by.items()}
    df = collections.Counter(w for ws in words.values() for w in ws)
    where = collections.defaultdict(list)
    for s_, ws in words.items():
        for w in ws:
            if df[w] <= 20:
                where[w].append(s_)
    bounds = sorted({0, len(toks), *starts})
    blocks = []
    for lo, hi in zip(bounds, bounds[1:]):
        sc = collections.Counter()
        for w in {t.norm for t in toks[lo:hi] if len(t.norm) >= 4}:
            for s_ in where.get(w, ()):
                sc[s_] += 1 / df[w]
        top = sc.most_common(2) + [(None, 0)] * 2
        size = sum(1 for t in toks[lo:hi] if t.norm)
        sure = top[0][1] >= 3 and top[0][1] >= 5 * top[1][1] and size >= 200  # ja544: 331 against 22
        blocks.append((lo, hi, top[0][0] if sure else None))
    sure = [(n, order[s_]) for n, (_, _, s_) in enumerate(blocks) if s_]
    keep = set(n for n, _ in lis_nondecreasing(sure))
    covered = {blocks[n][2] for n in keep}
    moves = []
    for n, (lo, hi, s_) in enumerate(blocks):
        if s_ and n not in keep and s_ not in covered:
            if moves and moves[-1][2] == s_ and moves[-1][1] == lo:
                moves[-1] = (moves[-1][0], hi, s_)
            else:
                moves.append((lo, hi, s_))
    return [(lo, hi, by[s_]) for lo, hi, s_ in moves]


def lis_nondecreasing(pairs):
    """longest run of (n, v) pairs with v not decreasing"""
    import bisect
    tails, prev, at = [], [None] * len(pairs), []
    for k, (_, v) in enumerate(pairs):
        p = bisect.bisect_right(tails, v)
        if p == len(tails):
            tails.append(v)
            at.append(k)
        else:
            tails[p] = v
            at[p] = k
        prev[k] = at[p - 1] if p else None
    out, k = [], at[-1] if at else None
    while k is not None:
        out.append(pairs[k])
        k = prev[k]
    return out[::-1]


def align_book(toks, body, before):
    """align(); suttas the edition prints elsewhere (reordered()) are aligned on their own. Words keep their
    order inside every sutta. -> (seg index per tok, match ratio, matched toks)"""
    moves = reordered(toks, body)
    if not moves:
        return align(toks, body, before, with_matched=True)
    gone_t = {i for lo, hi, _ in moves for i in range(lo, hi)}
    gone_s = {si for _, _, ix in moves for si in ix}
    keep_t = [i for i in range(len(toks)) if i not in gone_t]
    keep_s = [si for si in range(len(body)) if si not in gone_s]
    pos = {si: k for k, si in enumerate(keep_s)}
    a, score, m = align([toks[i] for i in keep_t], [body[si] for si in keep_s],
                        {pos[si]: h for si, h in (before or {}).items() if si in pos}, with_matched=True)
    assign = [None] * len(toks)
    for k, i in enumerate(keep_t):
        assign[i] = keep_s[a[k]]
    matched = {keep_t[k] for k in m}
    for lo, hi, ix in moves:
        sub, _, sm = align(toks[lo:hi], [body[si] for si in ix],
                           {0: before[ix[0]]} if before and ix[0] in before else {}, with_matched=True)
        for k, x in enumerate(sub):
            assign[lo + k] = ix[x]
        matched |= {lo + k for k in sm}
    return assign, score, matched

NOTES = None


def place(chunk, ms_paths, ed, out_dir, label, report, write_books=None):
    segs_all, keys_all = [], []
    files = []
    for p in ms_paths:
        d = json.load(open(p, encoding='utf-8'))
        files.append((p, list(d.keys())))
        for k, v in d.items():
            keys_all.append(k)
            segs_all.append((k, re.sub(r'</?b>', '', v)))  # ms marks the lemma of niddesa books in <b>
    ms_text = dict(segs_all)
    slots = header_slots(keys_all, ms_text)
    slot_keys = {k for v in slots.values() for k in v}
    body, before, hold = [], {}, []
    for k, v in segs_all:
        if k in slot_keys:
            if k.split(':')[1].startswith('0.'):
                hold.append((sutta_of(k), v))
            continue
        # the title anchors before the first text segment, after ms subheadings that open the sutta
        # (Vinaya pc1:1.0.2 "Ime kho panāyasmanto dvenavuti pācittiyā dhammā…", printed before the title)
        if hold and not (is_subhead(k) and sutta_of(k) == hold[0][0]):
            before[len(body)], hold = [h for _, h in hold], []
        body.append((k, v))
    assign, score = align(chunk.toks, body, before)
    toks = heads_as_text(chunk.toks, assign, body, [v for k, v in segs_all if k in slot_keys])
    if len(toks) != len(chunk.toks):
        chunk.toks = toks
    assign, score, matched = align_book(chunk.toks, body, before)

    text = collections.defaultdict(list)
    refs = collections.defaultdict(list)
    vars_ = collections.defaultdict(list)
    leftover_heads = list(chunk.pending)
    body_words = collections.defaultdict(list)
    body_idx = collections.defaultdict(list)
    def home(h, si):
        """an empty ms segment just before si that this title line is the end line of (same first word)"""
        hw = [norm(x) for x in h.split() if norm(x)]
        if not hw or len(hw) > 6:
            return None
        for j in range(si - 1, max(-1, si - 5), -1):
            k, v = body[j]
            vw = [norm(x) for x in v.split() if norm(x)]
            if vw and vw[0] == hw[0] and not text[k] and not body_words[k]:
                return k
            if body_words[k]:  # stop at edition text already placed
                break
        return None

    seen = set()
    for n_tok, (t, si) in enumerate(zip(chunk.toks, assign)):
        if t.heads:
            keep = []
            for c, h in t.heads:
                k = home(h, si) if not keep else None  # only the leading end lines
                if k:
                    text[k].append(h)
                else:
                    keep.append((c, h))
            t.heads = keep
        key = body[si][0]
        s = sutta_of(key)
        start = s not in seen  # first edition word of this sutta
        seen.add(s)
        if t.heads:
            prev = body[si - 1][0] if si > 0 else None
            if start and slots.get(s):
                put_heads(t.heads, slots[s], text, t.para, ms_text)
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
        body_idx[key].append(n_tok)
        refs[key].extend(r for r in t.refs if r not in refs[key])
        vars_[key].extend(f'{l} → {r}' for l, r in t.vars)
    # a leading N.0 that ms gives a title (VRI Pātimokkha "Pubbakaraṇaṃ-4" printed as a text line) takes the
    # edition's first words of the sutta when they are that title
    first = {}
    for k, _ in body:
        first.setdefault(sutta_of(k), k)
    for s_, ks in slots.items():
        k0 = next((k for k in ks if not k.split(':')[1].startswith('0.')), None)
        want = [w for w in map(norm, ms_text.get(k0, '').split()) if w] if k0 else []
        f = first.get(s_)
        if want and not text[k0] and f and [re.sub(r'\d+$', '', norm(w)) for w in text[f][:len(want)]] == want:
            n = len(want)
            while n < len(text[f]) and not norm(text[f][n]):  # "-4"
                n += 1
            text[k0], text[f] = text[f][:n], text[f][n:]
    if leftover_heads and body:
        text[body[-1][0]].append(' '.join(h for _, h in leftover_heads))

    n_full = n_seg = n_written = 0
    for p, keys in files:
        base = os.path.basename(p).replace('_root-pli-ms.json', '')
        rel = os.path.relpath(os.path.dirname(p), os.path.dirname(MS_DIR))  # sutta/sn/sn1 | vinaya/pli-tv-bu-vb/...
        parts = rel.split(os.sep)
        if parts[0] == 'vinaya':
            book = re.sub(r'\d.*$', '', base)  # pli-tv-bu-vb-pj1 -> pli-tv-bu-vb-pj, pli-tv-bu-pm
        else:
            book = parts[2] if len(parts) > 2 else base
        if write_books and book not in write_books:
            continue
        root = {k: (' '.join(text[k]) + ' ') if text[k] else '' for k in keys}
        n_seg += len(keys)
        n_written += 1
        n_full += sum(1 for v in root.values() if v)
        write(os.path.join(out_dir, 'root', 'pli', ed, rel, f'{base}_root-pli-{ed}.json'), root)
        v = {k: ' | '.join(vars_[k]) for k in keys if vars_[k]}
        write_or_drop(os.path.join(NOTES or os.path.join(out_dir, 'variant', 'pli'), ed, rel,
                                   f'{base}_variant-pli-{ed}.json'), v)  # the edition's footnotes: collate.py
        r = {k: ', '.join(refs[k]) for k in keys if refs[k]}
        write_or_drop(os.path.join(out_dir, 'reference', 'pli', ed, rel, f'{base}_reference-pli-{ed}.json'), r)
    # every edition word must be somewhere, once, in order inside its sutta (a sutta printed elsewhere moves whole)
    got = [i for k, _ in body for i in body_idx[k]]
    per = collections.defaultdict(list)
    for k, _ in body:
        per[sutta_of(k)] += body_idx[k]
    if sorted(got) != list(range(len(chunk.toks))) or any(x != sorted(x) for x in per.values()):
        raise SystemExit(f'{ed} {label}: edition words lost or reordered')
    n_heads = sum(len(t.heads) for t in chunk.toks) + len(leftover_heads)
    n_words = len(chunk.toks)
    report.append((ed, label, n_written, n_seg, n_full, n_words, n_heads, round(score, 3)))


def heads_as_text(toks, assign, body, headers):
    """An edition title line that is, word for word, one or more whole ms text segments (no subheading)
    ending just before where the line was placed (VRI ja152 verse marked subhead, Thai
    `atha vagguddānaṃ`) is text: its words are aligned like any other."""
    def seq(t):
        return ' '.join(w for w in map(norm, t.split()) if w)
    starts, ends, sub, flow = {}, {}, set(), ''
    for i, (k, v) in enumerate(body):
        q = seq(v)
        if not q:
            continue
        starts[len(flow) + 1], ends[len(flow) + 1 + len(q)] = i, i
        if is_subhead(k):
            sub.add(i)
        flow += ' ' + q
    flow += ' '
    tops = [' ' + seq(h) + ' ' for h in headers]

    def text_run(q, si):
        at = flow.find(' ' + q + ' ')
        while at >= 0:
            i, j = starts.get(at + 1), ends.get(at + 1 + len(q))
            if i is not None and j is not None and si - 3 <= j <= si:
                return len(q.split()) >= 5 or not sub & set(range(i, j + 1))  # a sentence may be an ms subheading
            at = flow.find(' ' + q + ' ', at + 1)
        return False

    out = []
    for t, si in zip(toks, assign):
        new = []
        while t.heads:
            c, h = t.heads[-1]
            q = seq(h)
            if c == 'num' or len(q.split()) < 2 or not text_run(q, si) or any(' ' + q + ' ' in x for x in tops):
                break
            t.heads.pop()
            new[:0] = [Tok(part, t.entry, glue=k > 0) for w in h.split() for k, part in enumerate(GLUED.split(w))]
        if new:
            new[0].heads, t.heads = t.heads, []
            new[0].para, t.para = t.para, None
            out.extend(new)
        out.append(t)
    return out


def title_fit(h, t):
    """how well the edition title h names the ms header t: the common start of the two titles without numbers,
    if it leaves no more than an ending of the shorter one (`sekhiyakaṇḍo` / `Sekhiyakaṇḍa`, `samaṇasaññā suttaṃ` /
    `Samaṇasaññāsutta`; not `dhātusaṃyuttaṃ` / `Dhātunānattasutta`)"""
    a, b = (''.join(w for w in map(norm, x.split()) if w) for x in (h, t))
    n = len(os.path.commonprefix([a, b]))
    return n if n >= 5 and n >= min(len(a), len(b)) - 2 else 0


def put_heads(heads, slots, text, para, ms_text=None):
    zero = [k for k in slots if k.split(':')[1].startswith('0.')]
    nums = [k for k in slots if not k.split(':')[1].startswith('0.')]

    def by_class(c):
        if (c == 'num' and nums) or not zero:
            return nums[0]
        if len(zero) >= 3:
            return {'above': zero[0], 'vagga': zero[-2]}.get(c, zero[-1])
        if len(zero) == 2:  # ms: 0.1 nikāya, 0.2 vagga
            return zero[0] if c == 'above' else zero[1]
        return zero[0]
    for c, h in heads:  # a title that names an ms header goes there, the rest by its class; in printed order
        fit = {k: title_fit(h, ms_text.get(k, '')) for k in zero} if ms_text and c != 'num' else {}
        best = max(fit.values(), default=0)
        k = by_class(c)
        if best and fit.get(k) != best:
            k = next(k for k in zero if fit[k] == best)
        text[k].append(h)
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
# KN: (SC books, BJT file prefixes, VRI files); BJT has no Milindapañha. Apadāna is one text in all editions.
KN = [
    (['kp'], ['kn-khp'], ['s0501m.mul.xml']), (['dhp'], ['kn-dhp'], ['s0502m.mul.xml']),
    (['ud'], ['kn-ud'], ['s0503m.mul.xml']), (['iti'], ['kn-iti'], ['s0504m.mul.xml']),
    (['snp'], ['kn-snp'], ['s0505m.mul.xml']), (['vv'], ['kn-vv'], ['s0506m.mul.xml']),
    (['pv'], ['kn-pv'], ['s0507m.mul.xml']), (['thag'], ['kn-thag'], ['s0508m.mul.xml']),
    (['thig'], ['kn-thig'], ['s0509m.mul.xml']),
    (['tha-ap', 'thi-ap'], ['kn-ap'], ['s0510m1.mul.xml', 's0510m2.mul.xml']),
    (['bv'], ['kn-bv'], ['s0511m.mul.xml']), (['cp'], ['kn-cp'], ['s0512m.mul.xml']),
    (['ja'], ['kn-jat'], ['s0513m.mul.xml', 's0514m.mul.xml']), (['mnd'], ['kn-mn'], ['s0515m.mul.xml']),
    (['cnd'], ['kn-nc'], ['s0516m.mul.xml']), (['ps'], ['kn-ps'], ['s0517m.mul.xml']),
    (['mil'], [], ['s0518m.nrf.xml']), (['ne'], ['kn-nett'], ['s0519m.mul.xml']),
    (['pe'], ['kn-petk'], ['s0520m.nrf.xml']),
]
KN_BOOKS = [b for books, _, _ in KN for b in books]


def vb(side, parts):
    return [f'pli-tv-{side}-vb-{k}' for k in parts]


# Vinaya: Vibhaṅga, Khandhaka, Parivāra in the volumes of BJT and VRI; Pātimokkha (Dvemātikā) only in VRI,
# before its commentary
VINAYA = [
    (vb('bu', ['pj', 'ss', 'ay', 'np']), ['vp-prj'], ['vin01m.mul.xml']),
    (vb('bu', ['pc', 'pd', 'sk', 'as']) + vb('bi', ['pj', 'ss', 'np', 'pc', 'pd', 'sk', 'as']), ['vp-pct'],
     ['vin02m1.mul.xml']),
    (['pli-tv-bu-pm', 'pli-tv-bi-pm'], [], ['vin04t.nrf.xml|Kaṅkhāvitaraṇī']),
    (['pli-tv-kd'], ['vp-mv', 'vp-cv'], ['vin02m2.mul.xml', 'vin02m3.mul.xml']),  # Mahāvagga kd1-10, Cūḷavagga kd11-22
    (['pli-tv-pvr'], ['vp-pv'], ['vin02m4.mul.xml']),
]
VINAYA_BOOKS = [b for books, _, _ in VINAYA for b in books]


def groups():
    """(collection, SC books, BJT prefixes, VRI files) for every edition volume"""
    for coll, vols in VOLUMES.items():
        for lo, hi, bjt_prefix, vri_file in vols:
            yield coll, [f'{coll}{n}' for n in range(lo, hi + 1)], [bjt_prefix], [vri_file]
    for books, bjt, vri in KN:
        yield 'kn', books, bjt, vri
    for books, bjt, vri in VINAYA:
        yield 'vinaya', books, bjt, vri


T2500_KN = {'kp': ['18Kh'], 'dhp': ['18Dh'], 'ud': ['18Ud'], 'iti': ['18It'], 'snp': ['18Sn'], 'vv': ['19Vv'],
            'pv': ['19Pv'], 'thag': ['19Th1'], 'thig': ['19Th2'], 'tha-ap': ['20Ap1', '20Ap2'], 'bv': ['21Bu'],
            'cp': ['21Cp'], 'ja': ['22J', '23J'], 'mnd': ['24Mn'], 'cnd': ['25Cn'], 'ps': ['26Ps'], 'mil': ['28Mi'],
            'ne': ['27Ne'], 'pe': ['27Pe'], 'pli-tv-bu-vb-pj': ['1V'], 'pli-tv-bu-vb-pc': ['2V'], 'pli-tv-kd': ['3V', '4V'],
            'pli-tv-pvr': ['5V']}


def t2500_volumes(coll, inside):
    """World Tipiṭaka volumes of a group (the Pātimokkha is none of its 40 volumes)"""
    if coll in VOLUMES:
        n = [lo for lo, _, _, _ in VOLUMES[coll]].index(int(re.findall(r'\d+', inside[0])[0]))
        return {'dn': ['6D', '7D', '8D'], 'mn': ['9M', '10M', '11M'],
                'sn': ['12S1', '12S2', '13S3', '13S4', '14S5'],
                'an': ['15A1', '15A2', '15A3', '15A4', '16A5', '16A6', '16A7', '17A8', '17A9', '17A10', '17A11']}[coll][n]
    return T2500_KN.get(inside[0], [])


def coll_of(book):
    if book in VINAYA_BOOKS:
        return 'vinaya'
    return 'kn' if book in KN_BOOKS else re.match(r'[a-z]+', book).group()


def books_of(coll):
    if coll == 'vinaya':
        return VINAYA_BOOKS
    return KN_BOOKS if coll == 'kn' else [f'{coll}{n}' for n in range(1, LAST[coll] + 1)]


def bjt_book_files(bjt_dir, prefix):
    fs = [f for f in glob.glob(os.path.join(bjt_dir, prefix + '*.json'))
          if re.fullmatch(re.escape(prefix) + r'(-\d+)*\.json', os.path.basename(f))]
    # parts in order: dn-1, dn-1-3, dn-1-6 ... (numbers after the prefix; KN prefixes have none of their own)
    return sorted(fs, key=lambda f: [int(x) for x in re.findall(r'\d+', os.path.basename(f)[len(prefix):])])


def parse_only(s):
    books = []
    for part in s.split(','):
        part = part.strip()
        if part == 'kn' or part in KN_BOOKS:
            books += [('kn', b) for b in (KN_BOOKS if part == 'kn' else [part])]
            continue
        vin = [b for b in VINAYA_BOOKS if part == 'vinaya' or part in (b, b.replace('pli-tv-', ''))
               or (part in ('vb', 'pm') and b.split('-')[3] == part)]
        if vin:
            books += [('vinaya', b) for b in vin]
            continue
        m = re.fullmatch(r'(dn|mn|sn|an)(?:(\d+)(?:-(\d+))?)?', part)
        if not m:
            raise SystemExit(f'--only: cannot read {part!r} (e.g. dn, mn1-50, sn1-56, an4, kn, dhp, vinaya, vb, pm, bu-vb-pj)')
        a = int(m.group(2) or 1)
        b = int(m.group(3) or m.group(2) or LAST[m.group(1)])
        books += [(m.group(1), n) for n in range(a, b + 1)]
    return books


def log(report):
    print('\t'.join(map(str, report[-1])), file=sys.stderr, flush=True)


def main():
    global MS_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument('--bjt', required=True)
    ap.add_argument('--vri', required=True)
    ap.add_argument('--ms', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='dn,mn,sn,an,kn,vinaya', help='e.g. dn,mn,sn1-10,an4,kn,dhp,vinaya,vb,pm')
    ap.add_argument('--thai', help='E-Tipitaka palinew.sqlite (Siam Rath 1927)')
    ap.add_argument('--ref', help='bilara-data reference/pli/ms/sutta, for Siam Rath volumes')
    ap.add_argument('--report')
    ap.add_argument('--eds', default='bjt,my,th', help='editions to build; mso = Mahāsaṅgīti as printed, for comparison')
    ap.add_argument('--mso', help='tipitaka2500.github.io/tipitaka (World Tipiṭaka 2005), for --eds mso')
    ap.add_argument('--notes', help="folder for the editions' footnotes, which collate.py puts into variant/pli/ms")
    a = ap.parse_args()
    eds = set(a.eds.split(','))
    global NOTES
    NOTES = a.notes
    MS_DIR = a.ms
    report = []
    asked = {b if c in ('kn', 'vinaya') else f'{c}{b}' for c, b in parse_only(a.only)}
    for coll, inside, bjt_prefixes, vri_files in groups():
        books = asked.intersection(inside)
        if not books:
            continue
        ms = [p for b in inside for p in ms_files(a.ms, coll, b)]
        label = inside[0] if len(inside) == 1 else f'{inside[0]}-{inside[-1]}'
        if bjt_prefixes and 'bjt' in eds:
            files = [f for pre in bjt_prefixes for f in bjt_book_files(a.bjt, pre)]
            place(bjt_stream(files)[0], ms, 'bjt', a.out, label, report, books)
            log(report)
        if 'my' in eds:
            place(vri_stream([os.path.join(a.vri, f) for f in vri_files])[0], ms, 'my', a.out, label, report, books)
            log(report)
        vols = t2500_volumes(coll, inside) if 'mso' in eds else []
        if vols:
            vols = [vols] if isinstance(vols, str) else vols
            place(t2500_stream([os.path.join(a.mso, v) for v in vols]), ms, 'mso', a.out, label, report, books)
            log(report)
    if a.thai and 'th' in eds:
        # SC books joined by the Siam Rath volumes they share (ja spans two, Apadāna and Bv/Cp share one)
        for coll in sorted({coll_of(b) for b in asked}):
            vols = {b: sya_volumes(a.ref, coll, b) for b in books_of(coll)}
            todo = [b for b in books_of(coll) if vols[b]]
            while todo:
                group = [todo.pop(0)]
                gv = set(vols[group[0]])
                grew = True
                while grew:
                    grew = False
                    for b in list(todo):
                        if vols[b] & gv:
                            group.append(b)
                            gv |= vols[b]
                            todo.remove(b)
                            grew = True
                books = asked.intersection(group)
                if not books:
                    continue
                group = [b for b in books_of(coll) if b in group]
                ms = [p for b in group for p in ms_files(a.ms, coll, b)]
                label = 'sya' + ','.join(map(str, sorted(gv))) + f':{group[0]}-{group[-1]}'
                place(th_stream(a.thai, sorted(gv)), ms, 'th', a.out, label, report, books)
                log(report)
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('edition\tvolume\tfiles\tsegments\tfilled\twords\theadings\tmatch\n')
            for r in report:
                f.write('\t'.join(map(str, r)) + '\n')


if __name__ == '__main__':
    main()

"""The project's variant readings of ms, one file per ms file, as SC's own: dhammagift/variant/pli/ms/..._variant-pli-ms.json
(the dg.db build mixes it with SC's variant-pli-ms). Collated from the texts of the editions on SC ids:

  bj      Buddha Jayanti (dhammagift/root/pli/bjt)
  cck     Chaṭṭha Saṅgāyana, VRI (dhammagift/root/pli/my)
  sya-all Siam Rath 1927 (dhammagift/root/pli/th)
  ms2005  the Mahāsaṅgīti as printed, World Tipiṭaka 2005 (built with build_editions.py --eds mso, not in the data)
  pts     Pali Text Society (GRETIL, Dhammakaya input; build_editions.py --eds pts, not in the data)

Each edition is compared with ms word by word over a whole sutta, so a word the alignment put in a neighbour segment
is no variant. Left out: ṁ/ṃ, ṅ for ṃ before k, g, case, punctuation, spacing (`yoniso manasikāro` /
`yonisomanasikāro`), peyyāla (a side with …pe…, …la…), differences of more than 4 words (an abbreviation or a
passage printed in full), and readings SC already gives for that edition. The project's own readings
(variant_own.json, from the old site) come first.

The editions' own footnotes (build_editions.py --notes) go in too, after the collation, marked with the edition and
its sources: `varaṇajātakaṁ → varuṇajātakaṁ (bj: machasaṃ, syā)` (BJT's note: so the Chaṭṭha Saṅgāyana and Siam
Rath read), `(cck: ka.)`, `(sya-all: yu.)`; a note that names no source is `(bj note)`.

usage: collate.py BILARA_ROOT_PLI_MS BILARA_VARIANT_PLI_MS DHAMMAGIFT_DIR MSO_ROOT_PLI_MSO|- NOTES_DIR|- [PTS_ROOT_PLI_PTS]
"""
import collections, difflib, glob, json, os, re, sys, unicodedata

MS, SCVAR, DG = sys.argv[1:4]
MSO = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
NOTES = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
PTS = sys.argv[6] if len(sys.argv) > 6 else None
NOTE_ED = [('bjt', 'bj'), ('my', 'cck'), ('th', 'sya-all')]
TH_SRC = re.compile(r'^((?:(?:ma|yu|sī|syā|ka|machasaṃ|pī|kaṃ)\.?\s*)+)\s')
SIGLA = [('bj', os.path.join(DG, 'root', 'pli', 'bjt'), 'bjt'), ('cck', os.path.join(DG, 'root', 'pli', 'my'), 'my'),
         ('sya-all', os.path.join(DG, 'root', 'pli', 'th'), 'th')] + ([('ms2005', MSO, 'mso')] if MSO else []) \
    + ([('pts', PTS, 'pts')] if PTS else [])
PEYYALA = {'pe', 'la', 'pa', 'peyyālo'}
# headings and end lines an edition prints inside the text: no readings of it
TITLE = re.compile(r'.{3,}(vagg[aoā]?|vaggā|kaṇḍ(a|aṃ|o)|sutt(a|aṃ|ā)|sikkhāpad(a|aṃ)|kkhandhak(a|o|aṃ)|pabb(a|aṃ)|'
                   r'kathā|vatthu|bhāṇavār(a|o|aṃ)|niddes(a|o)|pucchā|apadān(a|aṃ)|jātak(a|aṃ)|vimān(a|aṃ)|'
                   r'peyyāl(a|o|aṃ)|vār(a|o)|kaṇḍaka|pāḷi|nipāt(a|o)|saṃyutt(a|aṃ)|bhūmi|samuṭṭhān(a|aṃ)|saraṇattay(a|aṃ)|'
                   r'saṅkhep(a|o))$|^(niṭṭhit|samatt|pariniṭṭhit|saraṇattay|samuṭṭhān)')
# what an edition adds at the end of a line and is no text: an uddāna label, a number word, a subheading
END = re.compile(r'(uddān|uddes|ānisaṃs)|^(paṭham|dutiy|tatiy|catutth|pañcam|chaṭṭh|sattam|aṭṭham|navam|dasam|'
                 r'ekādasam|dvādasam|terasam|cuddasam|pannarasam|paṇṇarasam|soḷasam|vīsatim)(o|aṃ|ā|ī)$')
PARTICLES = {'vā', 'ca', 'pi', 'na', 'hi', 'va', 'ti', 'te', 'me', 'no', 'so', 'sā', 've', 'yo', 'ce', 'su', 'ha', 'ku'}
MAX = 4
VOWELS = set('aāiīuūeo')


def norm(w):
    w = unicodedata.normalize('NFC', re.sub(r'<[^>]+>', '', w).lower()).replace('ṁ', 'ṃ')
    w = re.sub(r'[^\w]', '', w)
    return re.sub(r'ṅ(?=[kg])', 'ṃ', w)


def loose(ws):
    """words joined, spelling the editions differ in without a reading: niggahita as m (PTS `evam eva`, `yan ti`),
    any nasal before a stop or nasal (`angaṃ`, `saṃcāra`, `yaṃ nūna`), single for double consonants (PTS `upekhā`,
    `na pajānāti`), evamevaṃ / evam eva, -nīya / -niya, by / vy, vīriya / viriya, catūhi / catuhi, seyyathīdaṃ"""
    ws = [w[:-1] + 'm' if len(w) > 1 and w.endswith('n') and (i + 1 == len(ws) or ws[i + 1][0] not in VOWELS) else w
          for i, w in enumerate(ws)]  # yan ti; not n' etaṃ, ten' upasaṅkami
    s = ''.join(re.sub(r'(?<=.)evaṃ$', 'eva', w) for w in ws).replace('ṃ', 'm')  # evam eva
    s = re.sub(r'[ṅñnṇ](?=[kgcjṭḍtdpbnm])', 'm', s)
    s = s.replace('nīy', 'niy').replace('thīdam', 'thidam').replace('vy', 'by').replace('ūhi', 'uhi').replace('vīriy', 'viriy')
    s = re.sub(r'([kgcjṭḍtdpbsylvm])(?=\1)', '', s)
    return re.sub(r'([kgcjṭḍtdpb])(?=\1h)', '', s)



def abbreviated(xa, xb):
    """PTS abbreviations: `āp` for āpatti, `a a maggaṃ` for ariyaṃ aṭṭhaṅgikaṃ maggaṃ, `pañcah`, the Parivāra's
    `kattha paññattaṃ` left out"""
    if any(len(w) == 1 for w in xb) or 'kattha' in xa and 'kattha' not in xb:
        return True
    if any(w[-1] not in VOWELS | {'ṃ', 'm', 'n'} and (i + 1 == len(xb) or xb[i + 1][0] not in VOWELS)
           for i, w in enumerate(xb)):
        return True
    pairs = list(zip(xa, xb))
    return len(xa) == len(xb) and any(a != b and a.startswith(b) for a, b in pairs) and \
        all(loose([a]) == loose([b]) or a.startswith(b) for a, b in pairs)


def words(text):
    """[(word as written, normalized)], numbers dropped, …pe… as one word 'pe'"""
    text = re.sub(r'…\s*(pe|la|pa)\s*…', r' \1 ', text.replace('...', '…'))
    out = []
    for w in text.split():
        n = norm(w)
        if n and not n.isdigit():
            out.append((w, n))
    return out


def shown(ws):
    """a reading as SC writes it: lower case, ṁ, no punctuation"""
    return ' '.join(re.sub(r'[^\w]', '', unicodedata.normalize('NFC', re.sub(r'<[^>]+>', '', w).lower()).replace('ṃ', 'ṁ'))
                    for w in ws).strip()


def body(d):
    """text segments: no 0.x, no subheading (an1.2:1.0, dn16:1.4.0): SC titles them its own way"""
    def head(seg):
        parts = seg.split('.')
        return parts[0] == '0' or '0' in parts[1:]
    return [k for k in d if not head(k.split(':')[1])]


OWN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'variant_own.json'), encoding='utf-8'))
new_entries = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
n_files = 0
for p in sorted(glob.glob(os.path.join(MS, '**', '*_root-pli-ms.json'), recursive=True)):
    rel = os.path.relpath(p, MS)
    ms = json.load(open(p, encoding='utf-8'))
    keys = body(ms)
    A = [(k, w, n) for k in keys for w, n in words(ms[k])]
    if not A:
        continue
    scv = os.path.join(SCVAR, rel.replace('_root-pli-ms.json', '_variant-pli-ms.json'))
    sc = json.load(open(scv, encoding='utf-8')) if os.path.exists(scv) else {}
    for siglum, root, ed in SIGLA:
        q = os.path.join(root, rel.replace('_root-pli-ms.json', f'_root-pli-{ed}.json'))
        if not os.path.exists(q):
            continue
        e = json.load(open(q, encoding='utf-8'))
        B = [(w, n) for k in keys for w, n in words(e.get(k, ''))]
        if not B:
            continue
        sm = difflib.SequenceMatcher(None, [n for _, _, n in A], [n for _, n in B], autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
        moved = set()
        for i in range(len(ops) - 1):  # the same words taken out and put in again next to it (sn22.7:8.2)
            o, q2 = ops[i], ops[i + 1]
            wa = sorted(''.join([n for _, _, n in A[o[1]:o[2]]] + [n for _, _, n in A[q2[1]:q2[2]]]))
            wb = sorted(''.join([n for _, n in B[o[3]:o[4]]] + [n for _, n in B[q2[3]:q2[4]]]))
            if wa == wb:
                moved.update((i, i + 1))
        seg_len = collections.Counter(k for k, _, _ in A)
        order = list(ms)
        first = {}
        for i_, (k, _, _) in enumerate(A):
            first.setdefault(k, i_)
        for i, (op, a1, a2, b1, b2) in enumerate(ops):
            if i in moved:
                continue
            xa, xb = [n for _, _, n in A[a1:a2]], [n for _, n in B[b1:b2]]
            if op in ('delete', 'replace') and len({k for k, _, _ in A[a1:a2]}) == 1 and seg_len[A[a1][0]] == a2 - a1 \
                    and not shown(w for w, _ in B[b1:b2]):
                continue  # the edition has no such line here: a heading or an abbreviation, no reading
            if op == 'insert' and all(len(w) <= 3 and w not in PARTICLES for w in xb):
                continue  # VRI abbreviation marks: ja, jha
            if op == 'delete' and first.get(A[a1][0]) == a1:  # words the alignment left in the segment before
                prev = order[order.index(A[a1][0]) - 1] if order.index(A[a1][0]) else None
                tail = [n for _, n in words(e.get(prev, ''))][-len(xa):] if prev else []
                if tail == xa:
                    continue  # dn34:1.3.0 `Dve dhammā`
            at_end = op == 'insert' and (a1 == len(A) or A[a1][0] != A[a1 - 1][0])
            if at_end and (siglum == 'ms2005' or any(END.search(w) for w in xb)):
                continue  # a heading, an uddāna label, a number at the end of a segment
            if loose(xa) == loose(xb) or PEYYALA & set(xa + xb) or len(xa) > MAX or len(xb) > MAX:
                continue
            if xb and abbreviated(xa, xb):
                continue
            if op in ('insert', 'replace') and xb[-1:] == ['ti'] and loose(xa) == loose(xb[:-1]):
                continue  # a quotation closed with ti (PTS dhp `sāsanan ti`)
            if any(TITLE.search(w) for w in xa + xb):
                continue
            if op == 'insert':  # the edition has more: show it after the word before
                if a1 == 0:
                    continue
                a1, b1 = a1 - 1, b1 - 1
                if A[a1][2] != B[b1][1] or A[a1][2] in PEYYALA or TITLE.search(A[a1][2]):
                    continue
            key = A[a1][0]
            lemma = shown(w for _, w, _ in A[a1:a2])
            reading = shown(w for w, _ in B[b1:b2])
            if not lemma or lemma == reading:
                continue
            had = sc.get(key, '')
            if re.search(re.escape(lemma) + r'\s*→[^|]*' + re.escape(reading) + r'\s*\([^)]*\b' + re.escape(siglum) + r'\b', had):
                continue  # SC gives it already
            new_entries[rel][key][lemma].append((reading, siglum))
    n_files += 1


def entry_text(by_lemma):
    parts = []
    for lemma, rs in by_lemma.items():
        group, shown_as = collections.OrderedDict(), {}
        for reading, siglum in rs:
            k = loose([norm(w) for w in reading.split()])  # idhāvuso, idh āvuso: one reading
            shown_as.setdefault(k, reading)
            group.setdefault(k, [])
            if siglum not in group[k]:
                group[k].append(siglum)
        parts.append(f'{lemma} → ' + '; '.join(f'{shown_as[k]} ({", ".join(s)})' for k, s in group.items()))
    return ' | '.join(parts)


count = collections.Counter()
own_rel = collections.defaultdict(dict)
for p in glob.glob(os.path.join(MS, '**', '*_root-pli-ms.json'), recursive=True):
    for k in json.load(open(p, encoding='utf-8')):
        if k in OWN:
            own_rel[os.path.relpath(p, MS)][k] = OWN[k]
target = os.path.join(DG, 'variant', 'pli', 'ms')
for old in glob.glob(os.path.join(target, '**', '*_variant-pli-ms.json'), recursive=True):
    os.remove(old)  # written anew from variant_own.json and the collation
notes = collections.defaultdict(dict)  # rel -> {key: [entry]}
if NOTES:
    for ed, siglum in NOTE_ED:
        for q in glob.glob(os.path.join(NOTES, ed, '**', f'*_variant-pli-{ed}.json'), recursive=True):
            rel = os.path.relpath(q, os.path.join(NOTES, ed)).replace(f'_variant-pli-{ed}.json', '_root-pli-ms.json')
            for key, text in json.load(open(q, encoding='utf-8')).items():
                for part in text.split(' | '):
                    lemma, _, rest = (x.strip().replace('ṃ', 'ṁ') for x in part.partition('→'))
                    if not _:
                        continue
                    rs = re.findall(r'\s*([^();,][^()]*?)\s*\(([^()]*)\)\s*[;,]?', rest)
                    flat = lambda x: re.sub(r'[\s;,]', '', x)
                    if not rs or flat(''.join(f'{r}({s})' for r, s in rs)) != flat(rest):
                        rs = [(rest, '')]  # else several readings, each with its sources: "a (sī.), b (syā.)"
                    out_ = []
                    for reading, src in rs:
                        t = TH_SRC.match(reading + ' ') if not src else None
                        if t:  # Siam Rath writes the source first: "yu. kāraṃviyaṃ."
                            src, reading = t.group(1).strip(), reading[t.end() - 1:].strip()
                        out_.append(reading.rstrip('.').strip() + f' ({siglum}' + (f': {src.strip()})' if src.strip() else ' note)'))
                    notes[rel].setdefault(key, []).append(f'{lemma} → ' + '; '.join(out_))
for rel in sorted(set(new_entries) | set(own_rel) | set(notes)):
    out = os.path.join(target, rel.replace('_root-pli-ms.json', '_variant-pli-ms.json'))
    merged = dict(own_rel.get(rel, {}))
    for key, by_lemma in new_entries.get(rel, {}).items():
        text = entry_text(by_lemma)
        merged[key] = (merged[key] + ' | ' + text) if key in merged else text
        for rs in by_lemma.values():
            for _, s_ in rs:
                count[s_] += 1
    for key, es in notes.get(rel, {}).items():
        merged[key] = ' | '.join(([merged[key]] if key in merged else []) + es)
        count['notes'] += len(es)
    if not os.path.exists(os.path.join(MS, rel)):
        continue
    ms_keys = list(json.load(open(os.path.join(MS, rel), encoding='utf-8')))
    merged = {k: merged[k] for k in ms_keys if k in merged}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write('\n')
print(n_files, 'ms files,', len(new_entries), 'with variants;', dict(count))

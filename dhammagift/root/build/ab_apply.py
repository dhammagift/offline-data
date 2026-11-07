"""A rule's own changes, from two builds of the editions: A without the rule (or before it), B with it.

The repo's edition files are not always byte for byte what today's builder makes from the same sources (rules added
since a part was last rebuilt), so a rule is not applied by rebuilding: only the segments where B differs from A
are written, and only where the repo still has A's text there. Root and reference files.

usage: ab_apply.py A_OUT B_OUT DHAMMAGIFT_DIR [--apply]
  prints every changed segment (edition, key, A -> B) and the files where the repo differs from A on a changed key
  (those are left alone); --apply writes the changes into DHAMMAGIFT_DIR
"""
import glob, json, os, re, shutil, sys

A_DIR, B_DIR, DG = sys.argv[1:4]
APPLY = '--apply' in sys.argv
n = 0
skipped = []
for b in sorted(glob.glob(os.path.join(B_DIR, 'root', '**', '*.json'), recursive=True)
                + glob.glob(os.path.join(B_DIR, 'reference', '**', '*.json'), recursive=True)):
    rel = os.path.relpath(b, B_DIR)
    a, r = os.path.join(A_DIR, rel), os.path.join(DG, rel)
    if not os.path.exists(a) or open(a, 'rb').read() == open(b, 'rb').read():
        continue
    A, B = json.load(open(a, encoding='utf-8')), json.load(open(b, encoding='utf-8'))
    keys = [k for k in dict.fromkeys(list(A) + list(B)) if A.get(k) != B.get(k)]
    if not keys:
        continue
    ed = rel.split(os.sep)[2]
    for k in keys:
        print(f'{ed}\t{k}\t{A.get(k, "")!r}\t->\t{B.get(k, "")!r}')
    n += len(keys)
    if not os.path.exists(r):
        skipped.append((rel, 'not in repo'))
        continue
    if open(r, 'rb').read() == open(a, 'rb').read():  # the repo file is A: B whole
        if APPLY:
            shutil.copyfile(b, r)
        continue
    R = json.load(open(r, encoding='utf-8'))
    if set(R) != set(A) or any(R.get(k) != A.get(k) for k in keys):
        skipped.append((rel, 'repo differs from A on a changed key'))
        continue
    if APPLY:  # only these keys, the file's own format kept
        raw = open(r, encoding='utf-8').read()
        for k in keys:
            kk = json.dumps(k, ensure_ascii=False)
            o, nn = (json.dumps(x, ensure_ascii=False)[1:-1] for x in (A[k], B[k]))
            rx = re.compile(re.escape(kk) + r'(\s*:\s*")' + re.escape(o) + '"')
            assert len(rx.findall(raw)) == 1, (r, k)
            raw = rx.sub(lambda m: kk + m.group(1) + nn + '"', raw)
        json.loads(raw)
        open(r, 'w', encoding='utf-8').write(raw)
print(f'# {n} segments changed; {"applied" if APPLY else "not applied (--apply)"}; left alone: {skipped}', file=sys.stderr)

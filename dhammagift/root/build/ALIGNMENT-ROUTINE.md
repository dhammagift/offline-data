# Daily alignment work

A scheduled cloud session runs this once a day. It starts in an empty container with this repo checked out. The
aim: every edition's text in the segment of the Mahāsaṅgīti (ms) it belongs to, by rules in `build_editions.py`,
never by editing a segment by hand. Progress and open questions go to `compare/alignment-log.md` (newest on top).

## The rule the data must keep

A word of an edition that is the same word as in ms, at the same place in the sutta, stands in the same segment as
that ms word. `check_segments.py` checks it over all data and lists the breaks (`break`; `repeat` and `peyyala` are
mostly the checker's own uncertainty, a formula repeated or abbreviated). A text the edition prints and ms does not
(the Thai Pātimokkha's own preliminaries) stays whole in one segment (`Stream.body(block=True)`), not cut at stray
shared words.

## Branch

All work goes to the branch `alignment-daily`, never to `main`. The owner reviews it and merges into main what he
accepts. At the start of a run: `git fetch origin main alignment-daily`; check out `alignment-daily` (create it from
`origin/main` if it does not exist yet) and merge `origin/main` into it (a merge commit, no rebase, no force-push),
so each run builds on the last one and on what was merged. Push with `git push -u origin alignment-daily`.

## Each run

1. Sources: `bash dhammagift/root/build/fetch_sources.sh` (into `../src`, about 2 min). Set
   `SRC=$(cd .. && pwd)/src` and a work dir `W` outside the repo.
2. Area of the day: the next one after the last entry of `compare/alignment-log.md`, in this order: dn, mn, sn, an,
   kn, vinaya, abhidhamma, then from the start again.
3. Check: `python3 dhammagift/root/build/check_segments.py $SRC/bilara-data/root/pli/ms dhammagift $W/check.tsv`
   (7 min). Take the `break` rows of the area, worst first, about 100-150 of them.
4. Read them: for each, ms and the editions around it (`root/pli/<ed>/…`, `$SRC/bilara-data/root/pli/ms/…`) and,
   where needed, the edition's source. Sort them into types: what went wrong and why. A checker false alarm is a
   type too (note it; improve `check_segments.py` if it is common).
5. For a type with a clear cause, write a rule in `build_editions.py` (in `place()` or the edition's reader): general,
   with a docstring that names the first case found (as `gap_fragments`, `rule_starts`, `vri_centre_title`).
6. Build without and with the rule, the whole canon, all editions (about 10 min each, run the editions in parallel):
   ```
   ARGS="--bjt $SRC/tipitaka.lk/public/static/text --vri $SRC/tipitaka-xml/romn --ms $SRC/bilara-data/root/pli/ms/sutta
     --thai $SRC/palinew.sqlite --ref $SRC/bilara-data/reference/pli/ms/sutta --mso $SRC/raw/t2500/tipitaka
     --pts $SRC/gretil/x/2_pali/1_tipit --mbu-pm $SRC/raw/mbu-pm --only dn,mn,sn,an,kn,vinaya,abhidhamma"
   # A: the code before the rule (git stash or a copy of build_editions.py); B: with it; --eds one edition per process
   python3 dhammagift/root/build/build_editions.py $ARGS --eds pts --out $W/A --notes $SRC/notes   # A also makes notes
   python3 dhammagift/root/build/ab_apply.py $W/A $W/B dhammagift          # every change the rule makes
   ```
   Read every change against ms. If one is wrong, narrow the rule and build B again; never apply a rule with a
   wrong change in it. Then `ab_apply.py … --apply`.
7. If PTS changed: `pts_notes.py $SRC/gretil/x/2_pali/1_tipit $SRC/bilara-data/root/pli/ms/sutta dhammagift/root/pli/pts $SRC/notes`
   (into an empty notes/pts). Then `collate.py`, `viewer/make_viewer_data.py`, `viewer/find_shifts.py` (commands in
   HANDOFF-4-nikayas.md and README).
8. README: a paragraph on the rule (what, why, the first case, how many places). Commit with the numbers, push to
   `alignment-daily`. Do not commit `$SRC`, `$W` or notes.
9. Log entry in `compare/alignment-log.md`: date, area, breaks before/after in the area, places read, types found,
   rules added (with counts), and what needs the owner (a typo of an edition to report, a case no rule should touch,
   a question). Short, in Russian, as a checklist.

## Limits

- No change to translations, to `variant_own.json`, or to an edition's text itself: an edition's typo is reported
  (compare/bjt-report.md, the tipitaka.lk issue), not fixed.
- No rule that changes a segment it was not meant for: the A/B check is the gate.
- If a run cannot finish (a source unreachable, the build failing), log what happened and stop; do not push half a
  rule.
- One or two rules per run is enough; quality over count.

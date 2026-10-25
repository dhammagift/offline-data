# Pali editions on SuttaCentral ids

Pali root text of other editions, cut into the same segments and keys as SuttaCentral `ms`,
so a reader can switch between editions or show them side by side.

| edition | suffix | source | license |
|---|---|---|---|
| Buddha Jayanti Tipiṭaka (Sri Lanka) | `bjt` | [tipitaka.lk](https://github.com/pathnirvana/tipitaka.lk) `public/static/text/*.json` | CC BY-ND 4.0, attribution tipitaka.lk; text must be kept in sync, errors are reported to them, not fixed here |
| Chaṭṭha Saṅgāyana (Myanmar, VRI CST) | `my` | [VipassanaTech/tipitaka-xml](https://github.com/VipassanaTech/tipitaka-xml) `romn/*.mul.xml` | VRI |
| Syāmaraṭṭha (Siam Rath, Thai) 1927 | `th` | E-Tipitaka [ssutee/e-tipitaka-pc](https://github.com/ssutee/e-tipitaka-pc) `resources/palinew.sqlite` (Git LFS), 45 vols | no data license stated; attribution E-Tipitaka (Sutee Sudprasert), Siam Rath |

`ms` from [bilara-data](https://github.com/suttacentral/bilara-data) `root/pli/ms/sutta` gives only the ids and the segmentation.

## Layout

```
dhammagift/root/pli/<ed>/sutta/sn/sn1/sn1.1_root-pli-<ed>.json        text
dhammagift/variant/pli/<ed>/sutta/sn/sn1/sn1.1_variant-pli-<ed>.json  readings of the edition's footnotes / <note>
dhammagift/reference/pli/<ed>/sutta/sn/sn1/sn1.1_reference-pli-<ed>.json  pages and paragraph numbers
```

One file per `ms` file, same keys in the same order. A key the edition has no text for is `""`.

## Rules

- The edition text is not edited. BJT is transliterated from Sinhala to Roman, `th` from Thai script to Roman
  (`ṃ`, no capitals, as printed; Thai `ฯ` is `.`, a word broken with `-` at a line end is joined),
  `my` is used as VRI gives it. Peyyāla marks are written as in `ms` in all editions: `…pe…`, `…la…`, `…pa…`
  (BJT `-pe-`, Thai `ฯเปฯ`; `...` is `…`). Typos of the source stay (`th` an1.1 `paccassosasa`). Only markup is removed: `**bold**`, footnote marks `{1}`, `<pb/>`, `<note>`, paragraph numbers.
- Every word of the edition goes to exactly one segment; joining the segments gives the whole edition text in its order
  (the build stops if not). Words `ms` does not have go to the neighbour segment, `ms` words the edition does not have
  leave the segment empty (peyyāla expanded on one side, abbreviated on the other).
- Headings and numbers are the edition's own: `0.1` saṃyutta / nipāta and higher titles, `0.2` vagga, `0.3` number and
  sutta title (`1. 7. 1. kalyāṇamittasuttaṃ` in BJT, `10. Nandiyasuttaṃ` in `my`, `paṭhamaṃ oghataraṇasuttaṃ` in `th`;
  Siam Rath numbers vaggas and suttas with ordinal words and prints no sutta titles in SN 45-56, there only its
  paragraph numbers `[355]` in reference/). AN `N.0` gets the edition number.
  A vagga title stands only where the edition prints it, at the first sutta of the vagga.
  Where SC joins several suttas in one file (`sn45.64-68`), the edition's titles of the inner suttas stay inline in the text.
- Variants: `"word → reading (sources)"`, several joined with ` | `, as in SC `variant-pli-ms`.
  Source abbreviations are the edition's: BJT `machasaṃ` (Chaṭṭha Saṅgāyana), `syā` (Thai), `sī.pavi`, `PTS`;
  `my` `sī.` (Sinhala), `syā.` (Thai), `pī.` (PTS), `kaṃ.`, `ka.`; `th` `ma.` (Myanmar), `yu.` (PTS), `sī.` (Sinhala).
- References: BJT `<tipitaka.lk file>.<page>` and `para<n>`; `my` `para<n>` and VRI page marks `M` (Myanmar), `V` (VRI),
  `P` (PTS), `T` (Thai) with volume.page; `th` `sya<volume>.<page>` (the same marks SC reference uses) and `para<n>`.
- Every edition is aligned one volume at a time against all SC books in it: BJT and VRI by the volumes in `VOLUMES`
  (DN and MN in 3, SN by vagga, AN by nipāta), Siam Rath by the volume found from SC `sya` marks (AN 5, 6, 7, 9 have
  none in SC and are set in `SYA_VOLUME`). No text spills from one book into the next; only the books asked for are written.
- At a sutta boundary, edition words ms lacks go with the previous sutta up to the edition's own start of the next one
  (its title or numbered paragraph), the rest with the next sutta: the closing verses (uddāna) of mn9 stay in mn9.
  In the Thai source, centred lines that are no title (verse lines) are text.
- Where a sutta of ms ends with a line the edition lacks (`Paṭhamaṁ.`, a vagga end) and the edition opens the next one
  with words ms lacks (Thai `sāvatthīnidānaṃ.`), the edition's paragraph or heading starts the next sutta.

## Alignment

Words are compared without diacritics and punctuation. Anchors first: words that occur once in both texts and the
sutta titles together with the vagga number (titles repeat across peyyāla vaggas), then the gaps between anchors
(patience diff). `report.tsv`: segments filled and share of edition words matched exactly.

## Run / sync

```
git clone --depth 1 https://github.com/pathnirvana/tipitaka.lk
git clone --depth 1 --filter=blob:none --sparse https://github.com/VipassanaTech/tipitaka-xml && git -C tipitaka-xml sparse-checkout set romn
git clone --depth 1 --filter=blob:none --sparse https://github.com/suttacentral/bilara-data && git -C bilara-data sparse-checkout set root/pli/ms/sutta reference/pli/ms/sutta
curl -LO https://media.githubusercontent.com/media/ssutee/e-tipitaka-pc/master/resources/palinew.sqlite
python3 dhammagift/root/build/build_editions.py \
  --bjt tipitaka.lk/public/static/text --vri tipitaka-xml/romn --ms bilara-data/root/pli/ms/sutta \
  --thai palinew.sqlite --ref bilara-data/reference/pli/ms/sutta \
  --out dhammagift --only dn,mn,sn,an --report dhammagift/root/build/report.tsv
```

Done: DN, MN, SN, AN (about 50 s). Not yet: KN, Vinaya, Abhidhamma. Sources of this build: tipitaka.lk `319c415`, tipitaka-xml `00a2b2b`,
bilara-data `6a395ce`, palinew.sqlite sha256 `62e0b31282b87c2a…`.

Segments with text (whole collections; in brackets the same count for the 4nt `mod` branch columns):

| | BJT | Myanmar | Thai |
|---|---|---|---|
| DN | 98% (94) | 97% (99) | 96% (94) |
| MN | 98% (93) | 99% (96) | 98% (96) |
| SN | 86% (75) | 92% (85) | 84% (71) |
| AN | 89% (81) | 93% (88) | 85% (77) |

Empty segments are mostly where the edition itself has no text there (peyyāla, `Paṭhamaṁ.` lines, SC numbers).
BJT prints in full what ms and VRI abbreviate in DN 3, 5-7, 11-13 (the sīla passages): that text stays in the
neighbouring segments.

## Viewer

A whole book on one page, the four Pali texts side by side, variant readings by majority of BJT / Myanmar / Thai
(ms is checked against them; differing letters in yellow) and problem marks.

- `viewer/index.html` + `viewer/data/` work on any web server as they are: copy the `viewer` folder and open
  `.../viewer/index.html#sn45.1`. (Opened as a file from disk the browser does not let the page read `data/`;
  locally use `python3 -m http.server` in `viewer/`.) Problem marks are kept in that browser;
  "Скопировать список" in the marks panel copies them as `key<TAB>editions<TAB>note` lines.
- `viewer/page.html` is the same page as published on claude.ai, where the marks are shared through the page's database.
- Rebuild after a new run: `python3 viewer/make_viewer_data.py dhammagift bilara-data/root/pli/ms/sutta dhammagift/root/build/viewer`
  for the data, `python3 viewer/make_page.py` for `index.html` from `page.html`.

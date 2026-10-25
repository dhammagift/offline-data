# Pali editions on SuttaCentral ids

Pali root text of other editions, cut into the same segments and keys as SuttaCentral `ms`,
so a reader can switch between editions or show them side by side.

| edition | suffix | source | license |
|---|---|---|---|
| Buddha Jayanti Tipiṭaka (Sri Lanka) | `bjt` | [tipitaka.lk](https://github.com/pathnirvana/tipitaka.lk) `public/static/text/*.json` | CC BY-ND 4.0, attribution tipitaka.lk; text must be kept in sync, errors are reported to them, not fixed here |
| Chaṭṭha Saṅgāyana (Myanmar, VRI CST) | `my` | [VipassanaTech/tipitaka-xml](https://github.com/VipassanaTech/tipitaka-xml) `romn/*.mul.xml` | VRI |

`ms` from [bilara-data](https://github.com/suttacentral/bilara-data) `root/pli/ms/sutta` gives only the ids and the segmentation.

## Layout

```
dhammagift/root/pli/<ed>/sutta/sn/sn1/sn1.1_root-pli-<ed>.json        text
dhammagift/variant/pli/<ed>/sutta/sn/sn1/sn1.1_variant-pli-<ed>.json  readings of the edition's footnotes / <note>
dhammagift/reference/pli/<ed>/sutta/sn/sn1/sn1.1_reference-pli-<ed>.json  pages and paragraph numbers
```

One file per `ms` file, same keys in the same order. A key the edition has no text for is `""`.

## Rules

- The edition text is not edited. BJT is transliterated from Sinhala to Roman (`ṃ`, no capitals, as printed),
  `my` is used as VRI gives it. Only markup is removed: `**bold**`, footnote marks `{1}`, `<pb/>`, `<note>`, paragraph numbers.
- Every word of the edition goes to exactly one segment; joining the segments gives the whole edition text in its order
  (the build stops if not). Words `ms` does not have go to the neighbour segment, `ms` words the edition does not have
  leave the segment empty (peyyāla expanded on one side, abbreviated on the other).
- Headings and numbers are the edition's own: `0.1` saṃyutta / nipāta and higher titles, `0.2` vagga, `0.3` number and
  sutta title (`1. 7. 1. kalyāṇamittasuttaṃ` in BJT, `10. Nandiyasuttaṃ` in `my`). AN `N.0` gets the edition number.
  A vagga title stands only where the edition prints it, at the first sutta of the vagga.
  Where SC joins several suttas in one file (`sn45.64-68`), the edition's titles of the inner suttas stay inline in the text.
- Variants: `"word → reading (sources)"`, several joined with ` | `, as in SC `variant-pli-ms`.
  Source abbreviations are the edition's: BJT `machasaṃ` (Chaṭṭha Saṅgāyana), `syā` (Thai), `sī.pavi`, `PTS`;
  `my` `sī.` (Sinhala), `syā.` (Thai), `pī.` (PTS), `kaṃ.`, `ka.`.
- References: BJT `<tipitaka.lk file>.<page>` and `para<n>`; `my` `para<n>` and VRI page marks `M` (Myanmar), `V` (VRI),
  `P` (PTS), `T` (Thai) with volume.page.

## Alignment

Words are compared without diacritics and punctuation. Anchors first: words that occur once in both texts and the
sutta titles together with the vagga number (titles repeat across peyyāla vaggas), then the gaps between anchors
(patience diff). `report.tsv`: segments filled and share of edition words matched exactly.

## Run / sync

```
git clone --depth 1 https://github.com/pathnirvana/tipitaka.lk
git clone --depth 1 --filter=blob:none --sparse https://github.com/VipassanaTech/tipitaka-xml && git -C tipitaka-xml sparse-checkout set romn
git clone --depth 1 --filter=blob:none --sparse https://github.com/suttacentral/bilara-data && git -C bilara-data sparse-checkout set root/pli/ms/sutta
python3 dhammagift/root/build/build_editions.py \
  --bjt tipitaka.lk/public/static/text --vri tipitaka-xml/romn --ms bilara-data/root/pli/ms/sutta \
  --out dhammagift --only sn1-10,sn45-49,an1-2 --report dhammagift/root/build/report.tsv
```

Done so far: SN 1-10, SN 45-49, AN 1-2. Source commits of this build: tipitaka.lk `319c415`, tipitaka-xml `00a2b2b`,
bilara-data `6a395ce`.

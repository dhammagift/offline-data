# Pali editions on SuttaCentral ids

Pali root text of other editions, cut into the same segments and keys as SuttaCentral `ms`,
so a reader can switch between editions or show them side by side.

| edition | suffix | source | license |
|---|---|---|---|
| Buddha Jayanti Tipiṭaka (Sri Lanka) | `bjt` | [tipitaka.lk](https://github.com/pathnirvana/tipitaka.lk) `public/static/text/*.json` | CC BY-ND 4.0, attribution tipitaka.lk; text must be kept in sync, errors are reported to them, not fixed here |
| Chaṭṭha Saṅgāyana (Myanmar, VRI CST) | `my` | [VipassanaTech/tipitaka-xml](https://github.com/VipassanaTech/tipitaka-xml) `romn/*.mul.xml` | VRI |
| Syāmaraṭṭha (Siam Rath, Thai) 1927 | `th` | E-Tipitaka [ssutee/e-tipitaka-pc](https://github.com/ssutee/e-tipitaka-pc) `resources/palinew.sqlite` (Git LFS), 45 vols | no data license stated; attribution E-Tipitaka (Sutee Sudprasert), Siam Rath |

`ms` from [bilara-data](https://github.com/suttacentral/bilara-data) `root/pli/ms/sutta` and `root/pli/ms/vinaya` gives only
the ids and the segmentation.

## Layout

```
dhammagift/root/pli/<ed>/sutta/sn/sn1/sn1.1_root-pli-<ed>.json        text
dhammagift/variant/pli/ms/sutta/sn/sn1/sn1.1_variant-pli-ms.json       readings of all editions, footnotes included
dhammagift/reference/pli/<ed>/sutta/sn/sn1/sn1.1_reference-pli-<ed>.json  pages and paragraph numbers
dhammagift/root/pli/<ed>/vinaya/pli-tv-bu-vb/pli-tv-bu-vb-pj/pli-tv-bu-vb-pj1_root-pli-<ed>.json  Vinaya, SC folders
dhammagift/root/pli/my/vinaya/pli-tv-bu-pm_root-pli-my.json                                       Pātimokkha
```

One file per `ms` file, same keys in the same order. A key the edition has no text for is `""`.

## Rules

- The edition text is not edited. BJT is transliterated from Sinhala to Roman, `th` from Thai script to Roman
  (`ṃ`, no capitals, as printed; Thai `ฯ` is `.`, a word broken with `-` at a line end is joined),
  `my` is used as VRI gives it. Peyyāla marks are written as in `ms` in all editions: `…pe…`, `…la…`, `…pa…`
  (BJT `-pe-`, Thai `ฯเปฯ`; `...` is `…`). Typos of the source stay (`th` an1.1 `paccassosasa`, a stray `<` or `{`); a vowel sign typed before its consonant
  or with none (BJT `ෙmathi…`, Thai `า`) is read as that vowel, Thai `บ` `ฃ` `ั` `๎` are read, tone marks dropped. Only markup is removed: `**bold**`, footnote marks `{1}`, `<pb/>`, `<note>`, paragraph numbers.
- Every word of the edition goes to exactly one segment; joining the segments gives the whole edition text in its order
  inside every sutta (the build stops if not). A sutta the edition prints elsewhere in the book is the one exception
  to the book order: BJT Jātaka prints Khaṇḍahāla (ms `ja544` Candakumāra) right after Nimi (`ja541`). The edition's
  text is cut at its own sutta titles, each block goes to the ms sutta whose rare words it has (5 times more than
  any other, 200 words at least), and a block whose sutta gets no block in the book order is aligned to it on its own. Words `ms` does not have go to the neighbour segment, `ms` words the edition does not have
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

- Words printed with no space between them count as two (BJT `tīhi:accayaṃ`, `viditavedassa,purindadassa`, `rammā-agamā`,
  `samāno‘na`, `gotamaṃ’jinaṃ`); the text is written back as printed. An elision mark stays inside the word
  (`cattāro’me`, ms `cattārome`).
- An ms subheading inside a sutta at any depth (`dn8:5.0`, `dn16:1.4.0`, `N.0 Tassuddānaṁ`) takes only edition words that match it; edition text
  ms lacks before it (a reading, a vagga end line) closes the previous segment. An edition subheading lands there.
- Section end lines (`paṭhamo paṇṇāsako samatto`, `… niṭṭhitaṃ navamaṃ`, BJT `navapurāṇavaggo pañcadasamo.`,
  `paṭhamo paṇṇāsako.`) are text, not titles of what follows; one printed as a title goes to the empty ms line that
  starts with the same word (`sn35.155:2.9`), not to `Tassuddānaṁ`.
- An edition title line that is word for word one or more whole ms text segments just before the place it fell on
  is text (VRI marks the ja152 verse `subhead`; Thai prints `atha vagguddānaṃ` as a title).
- Where the titles follow their text (BJT Jātaka, Theragāthā, Therīgāthā, Vimānavatthu, Petavatthu: verse, then
  `macchajātakaṃ.`; found per vagga: text before the first title, no text after the last) they are end lines and go
  with their own text, as ms `Macchajātakaṁ pañcamaṁ.`; before, each was the title of the next one.
- Words of an edition end line (`upālipucchākathā niṭṭhitā`) and of an ms subheading or end line (`kd11:1.0.1
  1. Tajjanīyakamma`, `pvr8:11.1 Uposathādipucchāvissajjanā niṭṭhitā`) are no unique anchors: they repeat a title
  printed at the other end of the section, and anchored there a whole section went to its neighbour (kd9, kd11,
  pvr8). They still match in the word by word comparison.
- In a gap too long for difflib, an anchor whose place on the two sides differs by more than a third of the gap is
  dropped: a look-alike line (kd13 `(yathā heṭṭhā tathā vitthāretabbaṁ)`) sent 1200 words astray.
- Compounds spaced differently (`yoniso manasikāro`, ms `yonisomanasikāro`; `tena hāvuso`, ms `tenahāvuso`) are
  matched as one word.
- ms `<b>…</b>` (the lemma in Niddesa, Paṭisambhidāmagga, Nettippakaraṇa) is no part of the words compared.
- An edition title goes to the ms header it names (`sekhiyakaṇḍo` to `0.3 Sekhiyakaṇḍa`, `samaṇasaññā suttaṃ` to
  `Samaṇasaññāsutta`, not `Samaṇasaññāvagga`: the longest common start of the whole titles, leaving no more than an
  ending), else by its class (above, vagga, sutta); in the order printed.
- A 0.x of ms that is a sentence (Vinaya `sk1:0.6` "Ime kho panāyasmanto sekhiyā dhammā uddesaṁ āgacchanti.") is text.
- The sutta title anchors the alignment before the first text segment, after the ms subheadings that open the sutta
  (Vinaya `pc1:1.0.1` Namo, `1.0.2` Ime kho…).
- Edition words that are word for word an ms segment left empty right before or after their segment go there
  (VRI prints "Ime kho panāyasmanto … āgacchanti." after the title, BJT before it).
- A leading `N.0` that ms gives a title takes the edition's first words when they are that title (VRI Pātimokkha
  `Pubbakaraṇaṃ-4`, the number of items glued with `-`).
- Glued in the sources and split: `…pe…` (VRI `nissajjitabbaṃ…pe…`), `,–` (BJT `gotama,–na`), `.‘‘` (VRI
  `jānāhī’’ti.‘‘Suṭṭhu`).
- Thai title lines are recognised by the last word only (`…suttaṃ`, `…vaggo`, `…kathā`); verse lines are text.
- Bare numbers are not used to align (`dn29:8.0` Thai `3`).

## Alignment

Words are compared without diacritics and punctuation. Anchors first: words that occur once in both texts and the
sutta titles together with the vagga number (titles repeat across peyyāla vaggas), then the gaps between anchors
(patience diff). A gap with no such word (SN 34 is one formula repeated) is anchored by 2-, 3-, 5-word runs that
occur once, then by words that occur the same few times on both sides; without that the gap was spread evenly and
Thai SN 34 ran half a segment behind.

`viewer/find_shifts.py` (from the f3 session) lists segments that still carry words of a neighbouring ms segment:
168 before these rules, 51 after; with one-word shifts counted (f3 session) 167, then 57 in the nikāyas; after a
review of those by eye 29 in the nikāyas (100 with KN); after a review of KN 27 + 53 = 80; with Vinaya Vibhaṅga 83, 2 of them Vinaya; with the whole Vinaya 106: the 18 in Khandhaka and Parivāra are all in
place (titles spaced otherwise, `Dvemāsā` / `dve māsā`, or repeating the next line)
(both Thai readings: `np4:1.14` word order, `ss1:3.7.4` printed in full where ms abbreviates). The rest are real readings (`an8.85` nimmalo, `sn48.37` word
order), compounds spaced differently (`yoniso manasikāro`), and BJT elision marks that look like a glued word
(`dn23` ’purato, `mn56` so’dāni). Many of the rest only look like a shift to the check: the same words on both
sides of a boundary (`ps1.1:576.1` samantacakkhūti), an edition title that repeats the first line (`ne23:0.4`),
word order (`thig11.1:7.3` na tvaṃ, all three editions against ms), a sentence the edition has twice (`ps1.7:7.3`).
Run it after every build: `python3 viewer/find_shifts.py viewer/data viewer/data/shifts.json`. `report.tsv`: segments filled and share of edition words matched exactly.

## Run / sync

```
git clone --depth 1 https://github.com/pathnirvana/tipitaka.lk
git clone --depth 1 --filter=blob:none --sparse https://github.com/VipassanaTech/tipitaka-xml && git -C tipitaka-xml sparse-checkout set romn
git clone --depth 1 --filter=blob:none --sparse https://github.com/suttacentral/bilara-data && git -C bilara-data sparse-checkout set root/pli/ms/sutta reference/pli/ms/sutta root/pli/ms/vinaya reference/pli/ms/vinaya
curl -LO https://media.githubusercontent.com/media/ssutee/e-tipitaka-pc/master/resources/palinew.sqlite
python3 dhammagift/root/build/build_editions.py \
  --bjt tipitaka.lk/public/static/text --vri tipitaka-xml/romn --ms bilara-data/root/pli/ms/sutta \
  --thai palinew.sqlite --ref bilara-data/reference/pli/ms/sutta \
  --out dhammagift --notes notes --only dn,mn,sn,an,kn,vinaya --report dhammagift/root/build/report.tsv
```

Done: DN, MN, SN, AN, KN, the whole Vinaya: Vibhaṅga (Bhikkhu, Bhikkhunī), Pātimokkha, Khandhaka (kd1-22),
Parivāra (about 6 min). Not yet: Abhidhamma.
Khandhaka: BJT `vp-mv` + `vp-cv`, VRI `vin02m2` + `vin02m3`, Siam Rath 4-7, aligned as one text; Parivāra: BJT
`vp-pv`, VRI `vin02m4`, Siam Rath 8. Not in the edition (empty there): Siam Rath abbreviates the lineage verses of
`pvr2.1` and kd9 `7.14.17` (pabbājanīya), VRI has no closing verses of `pvr21` (81-87); Siam Rath prints no Pārāyana
verses apart from their Niddesa (`cnd2-4`) and has no `tha-ap553-561`.
Vinaya: BJT `vp-prj` (pj, ss, ay, np) and `vp-pct` (pc, pd, sk, as and the Bhikkhunīvibhaṅga), VRI `vin01m`, `vin02m1`;
Siam Rath volumes 1-3. The Pātimokkha (Dvemātikāpāḷi) is only in VRI (`vin04t.nrf.xml`, read up to the
Kaṅkhāvitaraṇī commentary); tipitaka.lk and Siam Rath have none. In ms the Pātimokkha has SC rule titles
(`Pācittiya 6. Dutiyasahaseyya`) that VRI does not print: most of its empty segments.
palinew.sqlite has no pages 211-220 of volume 1 (end of pj4, from `9.2.2`): those segments are empty in `th`.
Empty Vinaya segments are where an edition abbreviates (`…pe…`, BJT `dutiyampi kho …pe…`) or does not print a line
(Thai `…sikkhāpadaṁ niṭṭhitaṁ.`).
KN: BJT has no Milindapañha; Siam Rath has no Milindapañha, Nettippakaraṇa, Peṭakopadesa (not in its canon).
Apadāna (tha-ap + thi-ap) is one text in all three editions and is aligned as one; Jātaka and Apadāna span two
Siam Rath volumes (27-28, 32-33), read as one text. KN files keep SC's folders (`sutta/kn/iti/vagga1/iti1_…`). Sources of this build: tipitaka.lk `58eed98`, tipitaka-xml `00a2b2b`,
bilara-data `6a395ce`, palinew.sqlite sha256 `62e0b31282b87c2a…`.

Segments with text (whole collections; in brackets the same count for the 4nt `mod` branch columns):

| | BJT | Myanmar | Thai |
|---|---|---|---|
| DN | 98% (94) | 97% (99) | 96% (94) |
| MN | 98% (93) | 99% (96) | 98% (96) |
| SN | 86% (75) | 92% (85) | 84% (71) |
| AN | 89% (81) | 93% (88) | 85% (77) |
| KN | 92% | 95% | 93% |
| Vinaya: Vibhaṅga | 88% | 89% | 87% |
| Vinaya: Pātimokkha | — | 83% | — |
| Vinaya: Khandhaka | 96% | 99% | 94% |
| Vinaya: Parivāra | 96% | 99% | 95% |

Empty segments are mostly where the edition itself has no text there (peyyāla, `Paṭhamaṁ.` lines, SC numbers).
BJT prints in full what ms and VRI abbreviate in DN 3, 5-7, 11-13 (the sīla passages): that text stays in the
neighbouring segments.

## SC ms against the Mahāsaṅgīti as printed

`ms` is the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500 (World Tipiṭaka, Dhamma Society 2005) as SuttaCentral edited it.
For comparison only (not part of the data), the printed text, reconstructed by
[tipitaka2500.github.io](https://github.com/tipitaka2500/tipitaka2500.github.io) (CC0), is built on the same ids:

```
git clone --depth 1 https://github.com/tipitaka2500/tipitaka2500.github.io
python3 dhammagift/root/build/build_editions.py ... --mso tipitaka2500.github.io/tipitaka --eds mso --out compare
python3 dhammagift/root/build/compare/compare_ms.py bilara-data/root/pli/ms compare/root/pli/mso dhammagift/root/build/compare/ms-orig.tsv
```

Of 1 933 660 words of `ms` (DN, MN, SN, AN, KN, Vinaya but the Pātimokkha, which is none of the 40 volumes) all but
a few hundred are the printed words. What SC changed: `ṅ` for the printed `ṃ` before k, g (`saṃgha` → `saṅgha`,
in 8 757 segments); spacing (mostly `ti` after a quotation, SC `bhagavā”ti`, printed `bhagavā ti`, 5 851 places); `ṁ`; punctuation, capitals and its
own headings (the printed headings stand inside its text: `dn34` `dve dhammā`, the Vinaya word glosses). Words that
differ: `dn33:1.11.85, 91` SC `idha bhikkhave`, printed `idhāvuso`; `sn35.19:2.9`, `sn35.20:2.2, 2.8` SC `aparimutto`,
printed `parimutto`; `sn22.7:8.2` word order; `pvr5:122.4` SC `ammukhāvinayena` (a typo), printed `sammukhāvinayena`;
`an1.439-446` printed `ānāmi` for `jānāmi` (a typo of the print or of the reconstruction); `sn48.137-146:1.1`,
`sn48.147-158:1.1`, `sn50.67-76:1.1` SC has the English note `on display title of section only` in the Pali;
`snp5.18:1.1` SC prints `Idamavoca bhagavā magadhesu…` there, the print at the head of the Pārāyana (`snp5.2`).
The list is `compare/ms-orig.tsv` (headings and numbers of the print included).

The text of the print is not in the data; its readings are, with those of the other editions (below).

## PTS

The Pali Text Society editions as input by the Dhammakaya Foundation, from GRETIL `2_pali` (plain text version;
(C) PTS and Dhammakaya 2015, CC BY-SA 4.0), for comparison only: their readings go into the variants (`pts`), the
text is not in the data. The archive is `gretil/2_pali.zip` on the branch `gretil-pali`.

```
git show origin/gretil-pali:gretil/2_pali.zip > 2_pali.zip && unzip -q 2_pali.zip
python3 dhammagift/root/build/build_editions.py ... --pts 2_pali/1_tipit --eds pts --out compare
```

All of DN, MN, SN, AN, the Vinaya but the Pātimokkha, and KN but the Jātaka (printed with its commentary), the
Netti and the Peṭakopadesa (not PTS input in GRETIL); Milinda from `2_parcan`. PTS headings are left out (`SN_1.1,1.1.
Oghaṃ.`, English `CHAPTER I.`): they never fit SC's titles. The PTS apparatus (the annotated version's footnotes) is
not read yet.

## Variant readings

One file per ms file, at SC's place and in SC's form, which the dg.db build mixes with SC's own
`variant-pli-ms`: `dhammagift/variant/pli/ms/sutta/sn/sn35/sn35.19_variant-pli-ms.json`,
`"sn35.19:2.9": "aparimutto → parimutto (bj, cck, sya-all, ms2005, pts)"`. Made by `collate.py` from the editions
on SC ids: `bj` Buddha Jayanti, `cck` Chaṭṭha Saṅgāyana (VRI), `sya-all` Siam Rath, `ms2005` the Mahāsaṅgīti as
printed, `pts` the Pali Text Society editions (below). Each is compared with ms word by word over a whole sutta (a
word the alignment put next door is no reading). Left out: case, punctuation, spacing, spellings that are no
reading (ṁ/ṃ/m and any nasal before a stop, `evam eva`, `yan ti`, a single for a double consonant as PTS `upekhā`,
-nīya/-niya, by/vy, vīriya/viriya), peyyāla, differences of more than 4 words (abbreviation, a passage in full),
abbreviations (PTS `āp`, `a a maggaṃ`), headings, uddāna labels and number words an edition prints in a line, VRI
marks like `jha`, and readings SC already gives for that edition. Readings spelled apart only by spacing are one
(`idhāvuso (cck, ms2005, pts)`). The project's own readings (`variant_own.json`, from the old site) come first.
About 215 000 readings: sya-all 76 800, bj 70 700, pts 65 200, cck 2 700, ms2005 16.

```
python3 dhammagift/root/build/collate.py bilara-data/root/pli/ms bilara-data/variant/pli/ms dhammagift compare/root/pli/mso notes compare/root/pli/pts
```

The editions' own footnotes (`build_editions.py --notes notes`, outside the repo) go into the same file after the
collation, with the edition and the sources the note names: `varaṇajātakaṁ → varuṇajātakaṁ (bj: machasaṁ, syā)`,
`(cck: sī. pī.)`, `(sya-all: yu.)`; a note naming no source is `(bj note)`. About 50 300. Pages and paragraph numbers
are not readings and stay in `reference/pli/<ed>`.

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

# Typos in the Buddha Jayanti text of tipitaka.lk

To: tipitaka.lk (path.nirvana@gmail.com, or an issue at https://github.com/pathnirvana/tipitaka.lk)
Sent: [pathnirvana/tipitaka.lk#154](https://github.com/pathnirvana/tipitaka.lk/issues/154), 2026-10-31.


In four places of `public/static/text` a closing quote `’` stands between two words with no space, where the text
needs a space (and, where a quotation begins, an opening quote `‘`). The same passages elsewhere in your files are
written with the space and `‘`, e.g. Kathāvatthu `න වත්තබ්බං ‘පුග්ගලො …`.

| file | place (0-based) | now | should be | the same place in the Mahāsaṅgīti |
|---|---|---|---|---|
| `dn-2-7.json` | `pages[82].pali.entries[0]` | `අයං භො පුරිසො එවමාහ’පුරතො කන්තාරෙ` | `… එවමාහ: ‘පුරතො කන්තාරෙ` | DN 23 (dn23:23.48-49): `evamāha: “purato kantāre` |
| `kn-thig.json` | `pages[34].pali.entries[12]` | `318. තස්ස බ්රාහ්මණ{1} අරහතො’ධම්මං සුත්වා` | `… අරහතො, ධම්මං සුත්වා` | Thig 13.4 v. 318 (thig13.4:7.1-2): `arahato, / dhammaṁ sutvā` |
| `ap-kvu.json` | `pages[11].pali.entries[9]` | `නො ච වත රෙ වත්තබ්බෙ’පුග්ගලො උපලබ්භති` | `… වත්තබ්බෙ ‘පුග්ගලො උපලබ්භති` | Kv 1.1 (kv1.1:37.2-3): `vattabbe: “puggalo upalabbhati` |
| `kn-petk-6.json` | `pages[11].pali.entries[5]` | `න විචිකිච්ඡති’අරියො අට්ඨඞ්ගිකො මග්ගො` | `න විචිකිච්ඡති, ‘අරියො අට්ඨඞ්ගිකො මග්ගො` | Peṭakopadesa 6 (pe6:51.3-4) |

Not a typo, for reference: `so’dāni` (MN 56) is an elision of `so idāni`.

Found while aligning the Buddha Jayanti text to SuttaCentral's segment ids for dhamma.gift
(https://github.com/dhammagift/offline-data, `dhammagift/root/pli/bjt`). We do not change your text: in our files
these words only go to the segment they belong to, and they will follow your corrections when we rebuild.

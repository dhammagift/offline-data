# Errors in the SuttaCentral Pali text (`root/pli/ms`)

The Pali root text of SuttaCentral (`bilara-data/root/pli/ms`) is the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500
(World Tipiṭaka Edition, Dhamma Society, 2005). We compared it word by word with:

- that printed edition itself, as reconstructed by [tipitaka2500.github.io](https://github.com/tipitaka2500/tipitaka2500.github.io) (`ms2005`);
- Buddha Jayanti Tripiṭaka, tipitaka.lk (`bj`);
- Chaṭṭha Saṅgāyana, VRI tipitaka.org (`cck`);
- Syāmaraṭṭha 1927, E-Tipitaka (`sya-all`);
- Pali Text Society editions, GRETIL / Dhammakaya input (`pts`).

In the places below SC differs from the very edition it was made from, and every other edition agrees with
that edition. These are errors made in SC's text, not variant readings. None of them is recorded in
`variant/pli/ms`.

## 1. Readings that change the meaning

### sn35.19:2.9, sn35.20:2.2, sn35.20:2.8: `aparimutto` for `parimutto`

| | |
|---|---|
| SC | Yo dukkhaṁ nābhinandati, ‘**aparimutto** so dukkhasmā’ti vadāmi. |
| should be | Yo dukkhaṁ nābhinandati, ‘**parimutto** so dukkhasmā’ti vadāmi. |
| witnesses | ms2005, bj, cck, sya-all, pts |

One who does not delight in suffering is *freed* from suffering. The SC text says the same as the first half of
each sutta (`abhinandati … aparimutto`, sn35.19:1.2, 1.6, 1.9; sn35.20:1.2, 1.8), and contradicts sn35.19:2.2 and
2.6, which correctly read `nābhinandati … parimutto`.

- https://suttacentral.net/sn35.19/pli/ms
- https://suttacentral.net/sn35.20/pli/ms

### dn33:1.11.85, dn33:1.11.91: `Idha, bhikkhave` for `Idhāvuso`

| | |
|---|---|
| SC 1.11.85 | **Idha, bhikkhave,** bhikkhu uppannaṁ kāmavitakkaṁ nādhivāseti … |
| SC 1.11.91 | **Idha, bhikkhave,** bhikkhu satisambojjhaṅgaṁ bhāveti … |
| should be | **Idhāvuso,** bhikkhu … |
| witnesses | ms2005, bj, cck, sya-all, pts |

The Saṅgītisutta is spoken by Sāriputta, who addresses the monks as `āvuso` throughout, including the questions
just before these segments (dn33:1.11.84 `Katamañcāvuso, pahānapadhānaṁ?`, 1.11.90 `Katamañcāvuso,
bhāvanāpadhānaṁ?`). `bhikkhave` is the Buddha's address.

- https://suttacentral.net/dn33/pli/ms

### sn22.7:8.2–8.3: the formula out of order

| | |
|---|---|
| SC | 8.2 na attani vā saṅkhāre, na saṅkhāresu vā attānaṁ. 8.3 **na saṅkhāravantaṁ vā attānaṁ;** |
| should be | **na saṅkhāravantaṁ vā attānaṁ;** na attani vā saṅkhāre, na saṅkhāresu vā attānaṁ. |
| witnesses | ms2005, bj, cck, sya-all |

The twenty-fold view of self always runs *khandhavantaṁ vā attānaṁ, attani vā khandhaṁ, khandhasmiṁ vā
attānaṁ*, as SC itself has it for form and feeling in the same passage (sn22.7:6.3, 7.1). Here the first member is moved to the end.

- https://suttacentral.net/sn22.7/pli/ms

### pli-tv-bu-vb-ss13:2.8: `vā` missing

| | |
|---|---|
| SC | … dantakaṭṭhena vā veḷuyā vejjikāya vā jaṅghapesanikena vā. |
| should be | … dantakaṭṭhena vā veḷuyā **vā** vejjikāya vā jaṅghapesanikena vā. |
| witnesses | ms2005, cck, pts (bj, sya-all: `veḷunā vā`) |

Every item of the list is closed by `vā`; without it bamboo and medical treatment run together as one item.

- https://suttacentral.net/pli-tv-bu-vb-ss13/pli/ms

### pli-tv-pvr5:122.4: `ammukhāvinayena` for `sammukhāvinayena`

| | |
|---|---|
| SC | **ammukhāvinayena** ca yebhuyyasikāya ca … |
| should be | **sammukhāvinayena** ca yebhuyyasikāya ca … |
| witnesses | ms2005, bj, cck, sya-all, pts |

A lost first letter in the name of the first of the seven ways of settling disputes.

- https://suttacentral.net/pli-tv-pvr5/pli/ms

## 2. English text inside the Pali

Three Pali segments contain an editorial note instead of text. The printed edition has the section titles there.

| segment | SC | ms2005 |
|---|---|---|
| sn48.137-146:1.1 | On Display: Title of Section Only | Appamādavagga-balakaraṇīyavagga |
| sn48.147-158:1.1 | On Display: Title of Section Only | Esanāvaggā |
| sn50.67-76:1.1 | On Display: Title of Section Only | Appamādavagga-balakaraṇīyavaggā |

## How this was found

The texts of the editions were aligned to SC segment ids by rules, without manual editing, and compared word
by word over whole suttas. Case, punctuation, spacing and spellings that are no reading (ṁ/ṃ, ṅ/ṃ before k, g,
single/double consonants, abbreviations, peyyāla) were not counted. Every place above was then read in all
editions by hand.

Of the 1 930 512 words of `ms` (DN, MN, SN, AN, KN, Vinaya), all but these few are the words of the printed
edition, apart from spacing, punctuation, the ṅ spelling and the words joined with ṅ listed in
[2-other-differences.md](2-other-differences.md). That file also lists the places where the Mahāsaṅgīti itself
stands against all other editions.

Data and code: https://github.com/dhammagift/offline-data/tree/main/dhammagift/root/build

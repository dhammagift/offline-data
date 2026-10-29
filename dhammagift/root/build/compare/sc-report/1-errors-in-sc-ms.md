# Errors in the SuttaCentral Pali text (`root/pli/ms`)

The Pali root text of SuttaCentral (`bilara-data/root/pli/ms`) is the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500
(World Tipiṭaka Edition, Dhamma Society, 2005). We compared it word by word with that printed edition and with
four other editions. In the places below SC differs from the very edition it was made from, and every other
edition agrees with that edition. These are errors in SC's text, not variant readings, and none of them is
recorded in `variant/pli/ms`.

Each place links to the line of the SC file in bilara-data (branch `published`, 59b845a2, 29 October 2026), where the
error is, and lists where to read the place in every other edition. Those editions show the correct reading:

- **Mahāsaṅgīti 2005**, the printed edition SC was made from, as reconstructed by
  [tipitaka2500.github.io](https://github.com/tipitaka2500/tipitaka2500.github.io): a link to the page.
- **Buddha Jayanti** (Sri Lanka), [tipitaka.lk](https://tipitaka.lk): a link that opens the paragraph.
- **Chaṭṭha Saṅgāyana**, VRI, [tipitaka.org](https://www.tipitaka.org/romn/): the file and paragraph number, with the
  page of the Myanmar print (M).
- **Syāmaraṭṭha 1927** (Thai), [84000.org](https://84000.org/tipitaka/pitaka_item/) in Roman script: volume, page and
  item (paragraph) number, a link that opens the item.
- **Pali Text Society**: volume and page of the PTS edition (SC shows these pages itself with *Reference: PTS*),
  and a link to the PTS file in [GRETIL](https://gretil.sub.uni-goettingen.de/) (Dhammakaya input), where `[page 013]`
  marks the page.

Screenshots taken on 29 October 2026: [screens/](https://github.com/dhammagift/offline-data/tree/main/dhammagift/root/build/compare/sc-report/screens) holds `sc-*.png`, each error on suttacentral.net outlined
in red, and `ed-*.png`, the correct reading outlined in green on the linked page of each edition
([screens.js](https://github.com/dhammagift/offline-data/blob/main/dhammagift/root/build/compare/sc-report/screens.js), [check_links.js](https://github.com/dhammagift/offline-data/blob/main/dhammagift/root/build/compare/sc-report/check_links.js) make them again). The 84000.org pages are behind a
Cloudflare check and were not opened by the script.

## 1. Readings that change the meaning

### sn35.19:2.9, sn35.20:2.2, sn35.20:2.8: `aparimutto` for `parimutto`

| | |
|---|---|
| SC | Yo dukkhaṁ nābhinandati, ‘**aparimutto** so dukkhasmā’ti vadāmi. |
| should be | Yo dukkhaṁ nābhinandati, ‘**parimutto** so dukkhasmā’ti vadāmi. |

One who does not delight in suffering is *freed* from suffering. As it stands, SC says the same as the first
half of each sutta (`abhinandati … aparimutto`, sn35.19:1.2, 1.6, 1.9; sn35.20:1.2, 1.8) and contradicts its own
sn35.19:2.2 and 2.6, which correctly read `nābhinandati … parimutto`.

| edition | sn35.19 | sn35.20 |
|---|---|---|
| SuttaCentral | [sn35.19:2.9](https://suttacentral.net/sn35.19/pli/ms), bilara-data [line 22](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn35/sn35.19_root-pli-ms.json#L22) | [sn35.20:2.2, 2.8](https://suttacentral.net/sn35.20/pli/ms), bilara-data [line 14](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn35/sn35.20_root-pli-ms.json#L14), [line 20](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn35/sn35.20_root-pli-ms.json#L20) |
| Mahāsaṅgīti 2005 | [13S4 1.1.2.7](https://tipitaka2500.github.io/tipitaka/13S4/1/1.1/1.1.2/1.1.2.7.html) | [13S4 1.1.2.8](https://tipitaka2500.github.io/tipitaka/13S4/1/1.1/1.1.2/1.1.2.8.html) |
| Buddha Jayanti | [SN IV (BJT) p. 26](https://tipitaka.lk/sn-4-1-1/12-4/pali) | [SN IV (BJT) p. 26](https://tipitaka.lk/sn-4-1-1/12-9/pali) |
| Chaṭṭha Saṅgāyana | [s0304m.mul0.xml](https://www.tipitaka.org/romn/cscd/s0304m.mul0.xml) para 19, M 2.246 | para 20, M 2.246 |
| Syāmaraṭṭha | [vol. 18, p. 16, item 19](https://84000.org/tipitaka/read/roman_item_s.php?book=18&item=19) | [vol. 18, p. 17, item 20](https://84000.org/tipitaka/read/roman_item_s.php?book=18&item=20) |
| PTS | SN IV 13, [samyu4pu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu4pu.htm) | SN IV 14, [samyu4pu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu4pu.htm) |

SuttaCentral today, the error outlined in red:

![SuttaCentral sn35.19:2.9](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn35_19_2_9.png)
![SuttaCentral sn35.20:2.2](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn35_20_2_2.png)
![SuttaCentral sn35.20:2.8](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn35_20_2_8.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io), the correct reading outlined in green:

![Mahāsaṅgīti 2005 sn35.19](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-sn35.19-ms2005.png)
![Mahāsaṅgīti 2005 sn35.20](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-sn35.20-ms2005.png)

### dn33:1.11.85, dn33:1.11.91: `Idha, bhikkhave` for `Idhāvuso`

| | |
|---|---|
| SC 1.11.85 | **Idha, bhikkhave,** bhikkhu uppannaṁ kāmavitakkaṁ nādhivāseti … |
| SC 1.11.91 | **Idha, bhikkhave,** bhikkhu satisambojjhaṅgaṁ bhāveti … |
| should be | **Idhāvuso,** bhikkhu … |

The Saṅgītisutta is spoken by Sāriputta, who addresses the monks as `āvuso` throughout, including the questions
just before these segments (dn33:1.11.84 `Katamañcāvuso, pahānapadhānaṁ?`, 1.11.90 `Katamañcāvuso,
bhāvanāpadhānaṁ?`). `bhikkhave` is the Buddha's address.

| edition | where |
|---|---|
| SuttaCentral | [dn33:1.11.85, 1.11.91](https://suttacentral.net/dn33/pli/ms), bilara-data [line 327](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/dn/dn33_root-pli-ms.json#L327), [line 333](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/dn/dn33_root-pli-ms.json#L333) |
| Mahāsaṅgīti 2005 | [8D 10.4](https://tipitaka2500.github.io/tipitaka/8D/10/10.4.html) |
| Buddha Jayanti | [DN III (BJT) p. 382](https://tipitaka.lk/dn-3-10/15-0/pali), [next paragraph](https://tipitaka.lk/dn-3-10/15-1/pali) |
| Chaṭṭha Saṅgāyana | [s0103m.mul9.xml](https://www.tipitaka.org/romn/cscd/s0103m.mul9.xml) para 310, M 3.189 |
| Syāmaraṭṭha | [vol. 11, p. 238, item 238](https://84000.org/tipitaka/read/roman_item_s.php?book=11&item=238) |
| PTS | DN III 226, [dighn3pu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/1_digh/dighn3pu.htm) |

SuttaCentral today, the error outlined in red:

![SuttaCentral dn33:1.11.85](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-dn33_1_11_85.png)
![SuttaCentral dn33:1.11.91](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-dn33_1_11_91.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io), the correct reading outlined in green:

![Mahāsaṅgīti 2005 dn33](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-dn33-ms2005.png)

### sn22.7:8.2–8.3: two segments in the wrong order

| | |
|---|---|
| SC | 8.1 Na saññaṁ …pe… na saṅkhāre attato samanupassati, 8.2 na attani vā saṅkhāre, na saṅkhāresu vā attānaṁ. 8.3 **na saṅkhāravantaṁ vā attānaṁ;** |
| should be | … na saṅkhāre attato samanupassati, **na saṅkhāravantaṁ vā attānaṁ;** na attani vā saṅkhāre, na saṅkhāresu vā attānaṁ. |

The view of self always runs *khandhavantaṁ vā attānaṁ; attani vā khandhaṁ, khandhasmiṁ vā attānaṁ*, as SC has
it for form and feeling in the same passage (sn22.7:6.3, 7.1). Segment 8.3, ending in a semicolon, belongs
before 8.2, which ends the sentence with a full stop.

| edition | where |
|---|---|
| SuttaCentral | [sn22.7:8.2–8.3](https://suttacentral.net/sn22.7/pli/ms), bilara-data [lines 47–48](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn22/sn22.7_root-pli-ms.json#L47-L48) |
| Mahāsaṅgīti 2005 | [13S3 1.1.1.7](https://tipitaka2500.github.io/tipitaka/13S3/1/1.1/1.1.1/1.1.1.7.html) |
| Buddha Jayanti | [SN III (BJT) p. 30](https://tipitaka.lk/sn-3-1-1-1/14-6/pali) (`na saṅkhāravantaṃ attānaṃ`) |
| Chaṭṭha Saṅgāyana | [s0303m.mul0.xml](https://www.tipitaka.org/romn/cscd/s0303m.mul0.xml) para 7, M 2.16 |
| Syāmaraṭṭha | [vol. 17, p. 23, item 33](https://84000.org/tipitaka/read/roman_item_s.php?book=17&item=33) |
| PTS | SN III 17, [samyu3pu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu3pu.htm) |

SuttaCentral today, the error outlined in red:

![SuttaCentral sn22.7:8.2–8.3](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn22_7_8_2.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io), the correct reading outlined in green:

![Mahāsaṅgīti 2005 sn22.7](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-sn22.7-ms2005.png)

### pli-tv-bu-vb-ss13:2.8: `vā` missing

| | |
|---|---|
| SC | … dantakaṭṭhena vā veḷuyā vejjikāya vā jaṅghapesanikena vā. |
| should be | … dantakaṭṭhena vā veḷuyā **vā** vejjikāya vā jaṅghapesanikena vā. |

Every item of the list is closed by `vā`; without it bamboo and medical treatment run together as one item.
Buddha Jayanti and Syāmaraṭṭha read `veḷunā vā`, also with `vā`.

| edition | where |
|---|---|
| SuttaCentral | [pli-tv-bu-vb-ss13:2.8](https://suttacentral.net/pli-tv-bu-vb-ss13/pli/ms), bilara-data [line 146](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/vinaya/pli-tv-bu-vb/pli-tv-bu-vb-ss/pli-tv-bu-vb-ss13_root-pli-ms.json#L146) |
| Mahāsaṅgīti 2005 | [1V 1.2.13](https://tipitaka2500.github.io/tipitaka/1V/1/1.2/1.2.13.html) |
| Buddha Jayanti | [Pārājikapāḷi (BJT) p. 478](https://tipitaka.lk/vp-prj-3-12/74-3/pali) |
| Chaṭṭha Saṅgāyana | [vin01m.mul2.xml](https://www.tipitaka.org/romn/cscd/vin01m.mul2.xml) para 437, M 281 |
| Syāmaraṭṭha | [vol. 1, p. 426, item 624](https://84000.org/tipitaka/read/roman_item_s.php?book=1&item=624) |
| PTS | Vin III 185, [vin3s1pu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin3s1pu.htm) |

SuttaCentral today, the error outlined in red:

![SuttaCentral pli-tv-bu-vb-ss13:2.8](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-pli-tv-bu-vb-ss13_2_8.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io), the correct reading outlined in green:

![Mahāsaṅgīti 2005 ss13](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-ss13-ms2005.png)

### pli-tv-pvr5:122.4: `ammukhāvinayena` for `sammukhāvinayena`

| | |
|---|---|
| SC | **ammukhāvinayena** ca yebhuyyasikāya ca … |
| should be | **sammukhāvinayena** ca yebhuyyasikāya ca … |

A lost first letter in the name of the first of the seven ways of settling disputes.

| edition | where |
|---|---|
| SuttaCentral | [pli-tv-pvr5:122.4](https://suttacentral.net/pli-tv-pvr5/pli/ms), bilara-data [line 450](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/vinaya/pli-tv-pvr/pli-tv-pvr5_root-pli-ms.json#L450) |
| Mahāsaṅgīti 2005 | [5V 5.13](https://tipitaka2500.github.io/tipitaka/5V/5/5.13.html) |
| Buddha Jayanti | [Parivārapāḷi (BJT) p. 370](https://tipitaka.lk/vp-pv-4-6/91-5/pali) |
| Chaṭṭha Saṅgāyana | [vin02m4.mul2.xml](https://www.tipitaka.org/romn/cscd/vin02m4.mul2.xml) para 308, M 199 |
| Syāmaraṭṭha | [vol. 8, p. 279, item 904](https://84000.org/tipitaka/read/roman_item_s.php?book=8&item=904) |
| PTS | Vin V 109, [vin5papu.htm](https://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin5papu.htm) (abbreviated there: `samm. ca yebh. ca …`) |

SuttaCentral today, the error outlined in red:

![SuttaCentral pli-tv-pvr5:122.4](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-pli-tv-pvr5_122_4.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io), the correct reading outlined in green:

![Mahāsaṅgīti 2005 pvr5](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-pvr5-ms2005.png)

## 2. English text inside the Pali

Three Pali segments contain an editorial note instead of text. The printed edition has the section titles there
(`Appamādavagga-balakaraṇīyavagga…`, `Esanāvaggā`).

| segment | SC |
|---|---|
| [sn48.137-146:1.1](https://suttacentral.net/sn48.137-146/pli/ms), [line 5](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn48/sn48.137-146_root-pli-ms.json#L5) | On Display: Title of Section Only |
| [sn48.147-158:1.1](https://suttacentral.net/sn48.147-158/pli/ms), [line 5](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn48/sn48.147-158_root-pli-ms.json#L5) | On Display: Title of Section Only |
| [sn50.67-76:1.1](https://suttacentral.net/sn50.67-76/pli/ms), [line 5](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/sn/sn50/sn50.67-76_root-pli-ms.json#L5) | On Display: Title of Section Only |

SuttaCentral today, the error outlined in red:

![SuttaCentral sn48.137-146:1.1](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn48_137-146_1_1.png)
![SuttaCentral sn48.147-158:1.1](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn48_147-158_1_1.png)
![SuttaCentral sn50.67-76:1.1](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-sn50_67-76_1_1.png)

## 3. A passage of the source left out: MN 10

Unlike the places above, this is not a copying slip and the other editions are divided; it is listed because here
SC's text is not the edition it names. In the printed Mahāsaṅgīti, as in the Chaṭṭha Saṅgāyana, MN 10 is the
*Mahāsatipaṭṭhānasutta*: after the four truths in brief
([mn10:44.3](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/mn/mn10_root-pli-ms.json#L196)) it has the whole exposition of the truths (`Paṭhamabhāṇavāro niṭṭhito. Dukkhasaccaniddesa:
Katamañca, bhikkhave, dukkhaṃ ariyasaccaṃ? …`, paragraphs 120-136 of the print, as in DN 22), and it ends
`Mahāsatipaṭṭhānasuttaṃ niṭṭhitaṃ dasamaṃ`. SC goes on at once with `Iti ajjhattaṁ vā …`
([mn10:45.1](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/mn/mn10_root-pli-ms.json#L197)) and names the sutta `Satipaṭṭhānasutta` ([mn10:0.2](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/mn/mn10_root-pli-ms.json#L3),
[mn10:47.5](https://github.com/suttacentral/bilara-data/blob/59b845a247cdfe625ce2061ac74b4999e183beb3/root/pli/ms/sutta/mn/mn10_root-pli-ms.json#L230)), as do Buddha Jayanti, Syāmaraṭṭha and PTS. Neither the text nor the title is
noted in SC's variants.

SC once had the long text: in 2015 a reader found DN 22 under MN 10, and Bhikkhu Sujato answered that "this is
unfortunately how the text is presented in the 6th council editions, of which Mahasangiti is one"
([forum, 17 August 2015](https://discourse.suttacentral.net/t/dn-22-instead-of-mn-10/2067)); he holds the passage
to be a late, probably 19th century Burmese, insertion
([forum, 2018](https://discourse.suttacentral.net/t/are-the-satipathana-suttas-not-original-dn22-mn10/10202/8)).
Since then SC's `ms` has the short text. Its English notes say that DN 22 expands the truths
([comment mn10:1.1, 44.3](https://github.com/suttacentral/bilara-data/blob/published/comment/en/sujato/sutta/mn/mn10_comment-en-sujato.json)),
but nothing in the Pali data says that `ms` here leaves its source. We found no notice of the change. If it is
meant, a variant note on `mn10:44.3` and `mn10:0.2` would record what the Mahāsaṅgīti prints.

| edition | MN 10 |
|---|---|
| Mahāsaṅgīti 2005 | with the exposition: [1.10.4.5.1 Dukkhasaccaniddesa](https://tipitaka2500.github.io/tipitaka/9M/1/1.10/1.10.4/1.10.4.5/1.10.4.5.1.html), end title [1.10.4.5.4](https://tipitaka2500.github.io/tipitaka/9M/1/1.10/1.10.4/1.10.4.5/1.10.4.5.4.html) |
| Chaṭṭha Saṅgāyana | with the exposition: [s0201m.mul0.xml](https://www.tipitaka.org/romn/cscd/s0201m.mul0.xml) paras 120-136 |
| Buddha Jayanti, Syāmaraṭṭha, PTS | without it, as SC |

SuttaCentral today, the place outlined in red:

![SuttaCentral mn10:44.3](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/sc-mn10_44_3.png)

The printed Mahāsaṅgīti (tipitaka2500.github.io) and the Chaṭṭha Saṅgāyana (tipitaka.org), outlined in green:

![Mahāsaṅgīti 2005 mn10 Dukkhasaccaniddesa](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-mn10-ms2005.png)
![Mahāsaṅgīti 2005 mn10 end title](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-mn10-ms2005-end.png)
![Chaṭṭha Saṅgāyana mn10 Dukkhasaccaniddeso](https://raw.githubusercontent.com/dhammagift/offline-data/main/dhammagift/root/build/compare/sc-report/screens/ed-mn10-vri.png)

## How this was found

The texts of the editions were aligned to SC segment ids by rules, without manual editing, and compared word by
word over whole suttas. Case, punctuation, spacing and spellings that are no reading (ṁ/ṃ, ṅ/ṃ before k, g,
single/double consonants, abbreviations, peyyāla) were not counted. Every place above was then read in all
editions by hand.

Of the 2 702 748 words of `ms` (DN, MN, SN, AN, KN, Vinaya, Abhidhamma), all but these few are the words of the printed
edition (the Abhidhamma has no difference at all), apart from spacing, punctuation and SC's ṅ for ṃ before k, g. Places where the Mahāsaṅgīti itself
stands against all other editions are listed in [2-other-differences.md](https://github.com/dhammagift/offline-data/blob/main/dhammagift/root/build/compare/sc-report/2-other-differences.md).

Data and code: https://github.com/dhammagift/offline-data/tree/main/dhammagift/root/build

# A typo in the reconstruction, and readings of the Mahāsaṅgīti 2005 to check

To: tipitaka2500.github.io (an issue at https://github.com/tipitaka2500/tipitaka2500.github.io)
Sent: not yet.

Good day

Thank you for the reconstruction of the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500 (World Tipiṭaka, Dhamma Society 2005).
We use it on dhamma.gift as the printed text (`MS05`) next to SuttaCentral's Mahāsaṅgīti, Buddha Jayanti, Chaṭṭha
Saṅgāyana, Siam Rath and PTS, every edition cut into SuttaCentral's segments
(https://github.com/dhammagift/offline-data, `dhammagift/root/pli/mso`). Comparing them word by word we found:

## 1. A typo in the reconstruction

`tipitaka/15A1/18/18.46--53.html` (Aṅguttara, Ekakanipāta, 18.46–53; SuttaCentral `an1.439:1.3`–`an1.446:1.3`), 8 times:

| now | should be |
|---|---|
| `Tāni abhibhuyya— ‘ānāmi passāmī’ti— evaṃsaññī hoti…` | `Tāni abhibhuyya— ‘jānāmi passāmī’ti— evaṃsaññī hoti…` |

The first letter of `jānāmi` is lost in all eight abhibhāyatana lines of the page. SuttaCentral's Mahāsaṅgīti, Buddha
Jayanti, Chaṭṭha Saṅgāyana, Siam Rath and PTS all read `jānāmi passāmi` in these eight lines, as the same formula
reads elsewhere in your files (e.g. `7D/3/3.18.html`, `10M/4/4.5.html`). In our copy it is corrected
(`T2500_FIXES` in `dhammagift/root/build/build_editions.py`); we will drop that once your page is fixed.

## 2. Readings to check against the printed pages

In 278 places (172 different readings) the Mahāsaṅgīti, in your reconstruction and in SuttaCentral's text alike,
reads otherwise than every other edition that has the passage (at least three of Buddha Jayanti, Chaṭṭha
Saṅgāyana, Siam Rath, PTS), all of them in the same way. Some may be choices of the 2005 edition; many look like
misprints or slips of typing. We cannot see the printed volumes: if you can, a look at the most frequent ones
would tell whether the print has them or the digital text does. The most frequent:

| Mahāsaṅgīti | all other editions | where |
|---|---|---|
| `dussilyaṁ` | `dussīlyaṁ` | an10.75, an10.76 (10×) |
| `…anupassanañāṇaṁ` | `…anupassanā ñāṇaṁ` / `…anupassanāñāṇaṁ` | ps1.5 (about 50×) |
| `assasaṁ`, `passasaṁ` | `assāsaṁ`, `passāsaṁ` | ps1.3 (12×) |
| `thinamiddha…` | `thīnamiddha…` | mn10, mn38, mn39, mn43, mn51 (12×) |
| `apurakkharāno` | `apurekkharāno` | mnd9 (5×) |
| `paññapessāmi` | `paññāpessāmi` | Vinaya kd12 (4×) |
| `uttari` | `uttariṁ` | dn21 (4×) |
| `seyyathā` | `seyyathāpi` | mn77 (4×) |
| `abhibhuto` | `abhibhūto` | mn1 (2×) |
| `sivathikāya chaṭṭitaṁ` | `sīvathikāya chaḍḍitaṁ` | an6.29 |
| `tittakālābubījaṁ` | `tittakalābubījaṁ` | an1.314 |
| `nitthiṇṇā` | `nittiṇṇā` | cnd11 |

The whole list, with links: https://github.com/dhammagift/offline-data/blob/main/dhammagift/root/build/compare/sc-report/2-other-differences.md
(segment ids are SuttaCentral's; your volume and paragraph for each are in our `reference/pli/mso`).

SuttaCentral's own departures from the Mahāsaṅgīti, where your reconstruction was the evidence, were reported to
them: https://github.com/dhammagift/dg-node/issues/71 (suttacentral/sc-data#463).

With metta, dhamma.gift

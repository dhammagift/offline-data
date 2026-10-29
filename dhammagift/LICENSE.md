# Licenses

Dhamma.gift is a non-commercial project. The data here comes from several sources, each under its own license;
the files keep the license of the text they hold. Use them free of charge, give the attribution below, and keep each
source's terms. How the Pali files are made: [root/build/README.md](root/build/README.md).

## Pali root texts

| files | text | license, attribution |
|---|---|---|
| SuttaCentral `root/pli/ms` (ids, segments, not copied here) | Mahāsaṅgīti Tipiṭaka Buddhavasse 2500, as edited by [SuttaCentral](https://github.com/suttacentral/bilara-data) | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `root/pli/bjt`, `reference/pli/bjt` | Buddha Jayanti Tipiṭaka (Sri Lanka), from [tipitaka.lk](https://github.com/pathnirvana/tipitaka.lk) | [CC BY-ND 4.0](https://github.com/pathnirvana/tipitaka.lk/blob/master/LICENSE.md), attribution tipitaka.lk. The text is not corrected here: errors are reported to tipitaka.lk, and the files are rebuilt from their repository when it changes. |
| `root/pli/my`, `reference/pli/my` | Chaṭṭha Saṅgāyana Tipiṭaka, from [VipassanaTech/tipitaka-xml](https://github.com/VipassanaTech/tipitaka-xml) | Free for non-commercial use, attribution Vipassana Research Institute (tipitaka.org). Kept in sync with their repository. |
| `root/pli/th`, `reference/pli/th` | Syāmaraṭṭha Tipiṭaka (Siam Rath, 1927), from E-Tipitaka [ssutee/e-tipitaka-pc](https://github.com/ssutee/e-tipitaka-pc) | No data license stated by the source. Attribution E-Tipitaka (Sutee Sudprasert), Siam Rath edition. |
| `root/pli/mso`, `reference/pli/mso` | Mahāsaṅgīti Tipiṭaka Buddhavasse 2500 as printed (World Tipiṭaka Edition, Dhamma Society, 2005), from [tipitaka2500.github.io](https://github.com/tipitaka2500/tipitaka2500.github.io) | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) as published by tipitaka2500.github.io. Attribution: World Tipiṭaka Project, M.L. Maniratana Bunnag Dhamma Society Fund. |
| `root/pli/pts`, `reference/pli/pts` (built for comparison, not in the repository yet) | Pali Text Society editions as input by the Dhammakaya Foundation, from [GRETIL](https://gretil.sub.uni-goettingen.de/) `2_pali` | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), (C) Pali Text Society and Dhammakaya Foundation 2015; attribution PTS, Dhammakaya Foundation, GRETIL. Share-alike: what is made from these files stays CC BY-SA 4.0. |

## Variant readings

`variant/pli/ms` holds the readings of all the editions above on SuttaCentral ids, with the editions' footnotes. Each
reading names its edition (`bj`, `cck`, `sya-all`, `ms2005`, `pts`) and carries that edition's license and
attribution as listed above; the readings marked `pts` are CC BY-SA 4.0. The project's own readings
(`variant_own.json`, from the old site) are Dhamma.gift's, under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Code and comparison

The build scripts in `root/build` and the comparison lists in `root/build/compare` are Dhamma.gift's own work,
under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), like all the project's materials
([Terms](https://github.com/dhammagift/dg-docs/blob/main/docs/user/policies.md#terms)).

Translations (`translation/`, `en`, `ru` and others) are not covered by this file: each keeps the license of its
translator or publisher.

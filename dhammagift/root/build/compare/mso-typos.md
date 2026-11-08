# Опечатки Mahāsaṅgīti 2005 (`mso`): что исправлять у нас

Из `sc-report/2-other-differences.md`: 278 мест (172 чтения), где Mahāsaṅgīti (печать и SC ms) читает иначе, чем все
другие издания (не меньше трёх из BJT, VRI, Сиам Ратх, PTS), и все одинаково. Исправление вносится в `T2500_FIXES`
(`build_editions.py`) и перечисляется здесь. Уже исправлено: `ānāmi` → `jānāmi` (an1.439-446, опечатка реконструкции).

## A. Исправлено (решение владельца, 2026-11-08)

Опечаткой считается выпавшая или искажённая буква, дающая не-слово, в одном месте. Разница долготы гласной
(`dussilyaṁ`, `thinamiddha…`, `abhibhuto`, `dhiro`, `vinitā` …) это возможно норма издания: оставлено. Форма, которую
издание пишет так же в нескольких местах (`bibbohanaṁ` 44 раза, `nitthiṇṇā` 4, `niklesaṭṭho` 2, `kāmakaṇḍako` 2), тоже
оставлена, как и `vuddha-` (v/b) и `dhammā` (слово пали).

| MS 2005 | у нас | где |
|---|---|---|
| `‘ānāmi passāmī’` | `‘jānāmi passāmī’` | an1.439-446 (8), опечатка реконструкции |
| `yoveti` | `yo vedi` | iti99:6.1 |
| `kharapattasannitaṁ` | `kharapattasannibhaṁ` | ja526:41.2 |

Список в коде: `T2500_FIXES` (`build_editions.py`).

### Разобрано, оставлено как есть

| MS 2005 | другие издания | мест | где |
|---|---|---|---|
| `dussilyaṁ` | `dussīlyaṁ` | 10 | an10.75:10.2, an10.75:12.2, an10.75:9.4, an10.76:11.4 … |
| `nitthiṇṇā` | `nittiṇṇā` | 1 | cnd11:66.6 |
| `accantadussilyaṁ` | `accantadussīlyaṁ` | 1 | dhp162:1 |
| `yoveti` | `yo vedi` | 1 | iti99:6.1 |
| `vuddhasāsananti` | `buddhasāsananti` | 1 | ja381:6.6 |
| `kharapattasannitaṁ` | `kharapattasannibhaṁ` | 1 | ja526:41.2 |
| `kuṭakārissa` | `kūṭakārissa` | 1 | ja541:72.1 |
| `dhiro` | `dhīro` | 1 | ja545:89.2 |
| `thinamiddhaṁ` | `thīnamiddhaṁ` | 4 | mn10:36.6, mn38:38.4, mn43:20.3, mn51:19.4 |
| `abhibhuto` | `abhibhūto` | 2 | mn1:14.1, mn1:14.2 |
| `thinamiddhanīvaraṇassa` | `thīnamiddhanīvaraṇassa` | 1 | mn23:4.20 |
| `vigatathinamiddho` | `vigatathīnamiddho` | 4 | mn38:38.4, mn39:13.4, mn51:19.4, mn94:21.4 |
| `thinamiddhā` | `thīnamiddhā` | 4 | mn38:38.4, mn39:13.4, mn51:19.4, mn94:21.4 |
| `thinamiddhapariyuṭṭhānasandosahetu` | `thīnamiddhapariyuṭṭhānasandosahetu` | 1 | mn4:10.2 |
| `vigatathinamiddhohamasmi` | `vigatathīnamiddhohamasmi` | 1 | mn4:10.4 |
| `vigatathinamiddhataṁ` | `vigatathīnamiddhataṁ` | 1 | mn4:10.6 |
| `vigatathinamiddhā` | `vigatathīnamiddhā` | 1 | mn8:12.22 |
| `diṭṭhivisukāyikaṁ` | `diṭṭhivisūkāyikaṁ` | 1 | mnd16:56.3 |
| `bibbohanaṁ` | `bimbohanaṁ` | 1 | pli-tv-bu-vb-ss8:1.4.34 |
| `niklesaṭṭho` | `nikkilesaṭṭho` | 1 | ps1.3:83.5 |
| `dhammā` | `damā` | 1 | sn10.12:10.3 |
| `vinitā` | `vinītā` | 1 | thig16.1:2.2 |
| `kāmakaṇḍako` | `kāmakaṇṭako` | 1 | ud3.3:17.1 |

## B. Написание или другая форма: оставить, если владелец не решит иначе (129 чтений, 212 мест)

Норма написания издания (`bhikkhuni-`, `tūriya`, `-īyamāna`, `-anupassanañāṇaṁ`, `-nāpi`), долгота в стихе, другая
грамматическая форма или другое слово (`seyyathā`/`seyyathāpi`, `uttari`/`uttariṁ`, `sīlaṁ`/`sīlāni`). Это чтения
издания, а не опечатки, либо без печатного тома не решить.

| MS 2005 | другие издания | мест | где |
|---|---|---|---|
| `tittakālābubījaṁ` | `tittakalābubījaṁ` | 1 | an1.314:1.4 |
| `sīlaṁ` | `sīlāni` | 1 | an11.12:5.3 |
| `abyāpajjena` | `avyāpajjhena` | 1 | an3.63:8.5 |
| `sivathikāya chaṭṭitaṁ` | `sīvathikāya chaḍḍitaṁ` | 1 | an6.29:7.1 |
| `chaṭṭitaṁ` | `chaḍḍitaṁ` | 1 | an6.29:8.1 |
| `anūpamo` | `anupamo` | 1 | bv18:15.4 |
| `parāyaṇo` | `parāyano` | 1 | bv1:24.3 |
| `vatenāpi` | `vatenapi` | 1 | cnd11:20.2 |
| `diṭṭhenāpi` | `diṭṭhenapi` | 2 | cnd11:29.1, cnd11:38.1 |
| `vīranti` | `vīrāti` | 1 | cnd15:2.4 |
| `vīramakāmakāmiṁ` | `vīra akāmakāmiṁ` | 1 | cnd15:9.1 |
| `ākiñcaññasambhavaṁ` | `ākiñcaññāsambhavaṁ` | 2 | cnd18:43.3, cnd18:49.1 |
| `nappabhāsati` | `na bhāsati` | 1 | cnd5:4.1 |
| `muni` | `munī` | 3 | cnd8:92.1, cnd8:92.6, cnd8:99.2 |
| `abhijānamāno` | `ājānamāno` | 2 | cnd9:33.4, cnd9:35.3 |
| `saṁyamissanti` | `saññamessanti` | 1 | dhp37:3 |
| `pūjaṁ` | `pūjā` | 1 | dhp73:4 |
| `mārisā` | `mārisa` | 1 | dn14:3.29.15 |
| `pātubhāvāya` | `pātubhāvāyāti` | 1 | dn16:3.20.3 |
| `uttari` | `uttariṁ` | 4 | dn21:2.4.1, dn21:2.5.1, dn21:2.6.1 … |
| `mālakārā` | `mālākārā` | 1 | dn2:14.3 |
| `saṁsaraṁ` | `saṁsāraṁ` | 1 | iti105:3.4 |
| `abyābajjhaṁ` | `abyāpajjhaṁ` | 1 | iti60:4.3 |
| `pamucce` | `pamuñce` | 2 | ja377:4.4, ja377:5.2 |
| `akhīṇampi` | `akhīṇanti` | 1 | ja429:3.3 |
| `raṭṭhe` | `raṭṭhāni` | 1 | ja478:9.1 |
| `anikaṭṭhā` | `anīkaṭṭhā` | 1 | ja520:8.1 |
| `addhayojanaṁ` | `aḍḍhayojanaṁ` | 1 | ja523:12.4 |
| `tadāssu` | `tadassu` | 1 | ja524:10.1 |
| `pāpaparāyaṇo` | `pāpaparāyano` | 1 | ja529:10.4 |
| `yānasmesu` | `yānasmāsu` | 1 | ja534:91.3 |
| `saṅgamesīti` | `saṁgāmesīti` | 1 | ja536:18.3 |
| `nesādā` | `nesāda` | 1 | ja540:64.1 |
| `asaṇṭhitanti` | `saṇṭhitanti` | 1 | mn138:15.2 |
| `vo` | `no` | 1 | mn18:19.5 |
| `seyyathā` | `seyyathāpi` | 4 | mn77:23.15, mn77:23.20, mn77:23.25 … |
| `yasassinaṁ` | `yasassīnaṁ` | 1 | mn77:6.16 |
| `samanuyuñjīyamānā samanuggāhīyamānā samanubhāsīyamānā` | `samanuyuñjiyamānā samanugāhiyamānā samanubhāsiyamānā` | 1 | mn79:19.6 |
| `bhojanasālāyampi` | `bhojanasālāyapi` | 1 | mnd14:186.5 |
| `vokkammāpi` | `vokkammapi` | 1 | mnd14:192.2 |
| `bhesmā` | `bhismā` | 1 | mnd15:11.4 |
| `asesakesu` | `asevitesu` | 1 | mnd15:161.3 |
| `taṁ` | `naṁ` | 1 | mnd15:75.2 |
| `nirupalepasaṅkhātena` | `nirupakkilesasaṅkhātena` | 1 | mnd16:55.11 |
| `bhikkhunigaṇassa` | `bhikkhunīgaṇassa` | 1 | mnd16:71.3 |
| `va` | `ca` | 4 | mnd4:66.1, mnd4:67.3, mnd4:67.5 … |
| `taṁ` | `etaṁ` | 1 | mnd6:33.12 |
| `apurakkharāno` | `apurekkharāno` | 5 | mnd9:69.3, mnd9:71.3, mnd9:85.3 … |
| `bhikkhunupassayaṁ` | `bhikkhunūpassayaṁ` | 1 | pli-tv-bi-vb-pc9:1.2 |
| `bhūmattharaṇaṁ` | `bhumattharaṇaṁ` | 1 | pli-tv-bu-vb-np6:2.15 |
| `bhikkhunisaṅghaṁ` | `bhikkhunīsaṅghaṁ` | 1 | pli-tv-bu-vb-pc21:3.2.2 |
| `kammiyā` | `kammikā` | 1 | pli-tv-bu-vb-pc66:1.10 |
| `yācīyamānā` | `yāciyamānā` | 1 | pli-tv-bu-vb-pc7:2.8 |
| `bhājīyamāne` | `bhājiyamāne` | 1 | pli-tv-bu-vb-pj2:7.12.9 |
| `parivattabbaṁ` | `parivatthabbaṁ` | 1 | pli-tv-bu-vb-ss13:3.2.8 |
| `bhavissati` | `bhavissasi` | 1 | pli-tv-bu-vb-ss3:3.1.21 |
| `bahupāyāsā` | `bahūpāyāsā` | 2 | pli-tv-kd11:32.2.17, pli-tv-kd11:32.2.8 |
| `paññapessāmi` | `paññāpessāmi` | 4 | pli-tv-kd12:4.1.29, pli-tv-kd12:5.1.22, pli-tv-kd12:9.1.23 … |
| `paññapetvā` | `paññāpetvā` | 1 | pli-tv-kd17:4.2.19 |
| `katihākārehi` | `katīhākārehi` | 1 | pli-tv-kd19:5.3.1 |
| `no` | `nu` | 1 | pli-tv-kd1:23.6.4 |
| `pavutto` | `pamutto` | 1 | pli-tv-kd1:78.3.3 |
| `mahāpajāpati` | `mahāpajāpatī` | 2 | pli-tv-kd20:1.4.1, pli-tv-kd20:2.1.2 |
| `bhikkhunisaṅgho` | `bhikkhunīsaṅgho` | 1 | pli-tv-kd20:19.3.2 |
| `bhikkhunisaṅgho` | `bhikkhunī saṅgho` | 1 | pli-tv-kd20:9.4.23 |
| `senesitāni` | `senesikāni` | 1 | pli-tv-kd6:1.5.2 |
| `sandhāgāre` | `santhāgāre` | 1 | pli-tv-kd6:31.1.4 |
| `āpajjanti` | `āpajjati` | 1 | pli-tv-pvr1.10:16.1 |
| `sabbaññutaññāṇaṁ` | `sabbaññutañāṇaṁ` | 1 | ps1.0:72.1 |
| `majjhā` | `majjhimā` | 1 | ps1.1:139.4 |
| `ekarasabhāvanā` | `ekarasā bhāvanā` | 1 | ps1.1:144.1 |
| `indriyaparopariyattañāṇaṁ` | `indriyaparopariyatte ñāṇaṁ` | 1 | ps1.1:576.3 |
| `assasaṁ` | `assāsaṁ` | 6 | ps1.3:142.2, ps1.3:142.5, ps1.3:143.2 … |
| `passasaṁ` | `passāsaṁ` | 6 | ps1.3:142.3, ps1.3:142.6, ps1.3:143.2 … |
| `āpānanti` | `apānanti` | 1 | ps1.3:50.2 |
| `sabbaññutaññāṇassa` | `sabbaññutañāṇassa` | 1 | ps1.3:57.27 |
| `nibbidānupassanañāṇaṁ` | `nibbidānupassanāñāṇaṁ` | 2 | ps1.5:126.10, ps1.5:128.8 |
| `virāgānupassanañāṇaṁ` | `virāgānupassanāñāṇaṁ` | 2 | ps1.5:126.12, ps1.5:128.10 |
| `nirodhānupassanañāṇaṁ` | `nirodhānupassanāñāṇaṁ` | 2 | ps1.5:126.14, ps1.5:128.12 |
| `paṭinissaggānupassanañāṇaṁ` | `paṭinissaggānupassanāñāṇaṁ` | 2 | ps1.5:126.16, ps1.5:128.14 |
| `animittānupassanañāṇaṁ` | `animittānupassanāñāṇaṁ` | 3 | ps1.5:126.18, ps1.5:128.16, ps1.5:129.3 |
| `appaṇihitānupassanañāṇaṁ` | `appaṇihitānupassanāñāṇaṁ` | 4 | ps1.5:126.20, ps1.5:128.18, ps1.5:129.18 … |
| `suññatānupassanañāṇaṁ` | `suññatānupassanāñāṇaṁ` | 9 | ps1.5:126.22, ps1.5:127.12, ps1.5:127.3 … |
| `aniccānupassanañāṇaṁ` | `aniccānupassanāñāṇaṁ` | 8 | ps1.5:126.4, ps1.5:127.1, ps1.5:127.10 … |
| `dukkhānupassanañāṇaṁ` | `dukkhānupassanāñāṇaṁ` | 3 | ps1.5:126.6, ps1.5:128.4, ps1.5:130.4 |
| `anattānupassanañāṇaṁ` | `anattānupassanāñāṇaṁ` | 3 | ps1.5:126.8, ps1.5:128.6, ps1.5:130.6 |
| `paṇidhi` | `paṇidhiyā` | 6 | ps1.5:130.20, ps1.5:130.4, ps1.5:130.6 … |
| `lokiko` | `lokiyo` | 3 | ps1.5:2.13, ps1.5:30.1, ps1.5:30.3 |
| `virāgānupassanañāṇaṁ` | `virāgānupassanā ñāṇaṁ` | 2 | ps1.5:44.10, ps1.5:54.12 |
| `nirodhānupassanañāṇaṁ` | `nirodhānupassanā ñāṇaṁ` | 2 | ps1.5:44.12, ps1.5:54.14 |
| `paṭinissaggānupassanañāṇaṁ` | `paṭinissaggānupassanā ñāṇaṁ` | 2 | ps1.5:44.14, ps1.5:54.16 |
| `animittānupassanañāṇaṁ` | `animittānupassanā ñāṇaṁ` | 3 | ps1.5:44.16, ps1.5:54.18, ps1.5:59.22 |
| `appaṇihitānupassanañāṇaṁ` | `appaṇihitānupassanā ñāṇaṁ` | 2 | ps1.5:44.18, ps1.5:54.20 |
| `suññatānupassanañāṇaṁ` | `suññatānupassanā ñāṇaṁ` | 3 | ps1.5:44.20, ps1.5:46.8, ps1.5:54.22 |
| `anattānupassanañāṇaṁ` | `anattānupassanā ñāṇaṁ` | 2 | ps1.5:44.6, ps1.5:54.8 |
| `nibbidānupassanañāṇaṁ` | `nibbidānupassanā ñāṇaṁ` | 2 | ps1.5:44.8, ps1.5:54.10 |
| `aniccānupassanañāṇaṁ` | `aniccānupassanā ñāṇaṁ` | 2 | ps1.5:45.1, ps1.5:55.1 |
| `dukkhānupassanañāṇaṁ` | `dukkhānupassanā ñāṇaṁ` | 1 | ps1.5:54.6 |
| `anekadhātuṁ nānādhātuṁ lokaṁ` | `anekadhātunānādhātulokaṁ` | 1 | ps2.9:32.2 |
| `puthunānāariyamagge` | `puthunānāariyamaggesu` | 1 | ps3.1:19.25 |
| `gambhīre ariyamagge` | `gambhīresu ariyamaggesu` | 1 | ps3.1:21.25 |
| `tehi` | `yehi` | 1 | sn1.26:1.2 |
| `vipariṇāmi aññathābhāvi` | `vipariṇāmī aññathābhāvī` | 1 | sn25.1:1.6 |
| `taṁva` | `tañca` | 2 | sn3.20:7.2, sn3.4:5.4 |
| `taṁvassa` | `tañcassa` | 1 | sn3.20:7.3 |
| `taṁvassa` | `taṁ cassa` | 1 | sn3.4:5.5 |
| `yaṁ` | `yā` | 3 | sn36.15:1.12, sn36.17:1.12, sn36.23:2.10 |
| `pajjālito` | `pajjalito` | 1 | sn5.7:4.3 |
| `uddharitāni` | `uddhareyya` | 1 | sn56.57:1.1 |
| `kadarīyaṁ` | `kadariyaṁ` | 1 | snp2.13:4.2 |
| `nirākatvā` | `niraṁkatvā` | 1 | snp2.7:33.3 |
| `sayaṁva` | `sayameva` | 1 | snp4.12:16.3 |
| `kuva` | `kuvaṁ` | 1 | snp4.16:16.1 |
| `kālaṅkataṁ` | `kālakataṁ` | 1 | snp4.6:4.4 |
| `samohatesu` | `samūhatesu` | 1 | snp5.7:8.4 |
| `gottena` | `nāmena` | 1 | tha-ap61:8.3 |
| `abyāpajjādhimuttassa` | `abyāpajjhādhimuttassa` | 1 | thag13.1:9.3 |
| `kāḷo` | `kālo` | 1 | thag2.20:3.4 |
| `vātehābādhiko` | `vātehābādhito` | 1 | thag2.33:1.2 |
| `mamaṅge` | `mamaṅke` | 1 | thi-ap25:36.1 |
| `dhāreti` | `dhārehi` | 1 | thig1.7:1.3 |
| `dibbacakkhu` | `dibbacakkhuṁ` | 1 | thig11.1:4.2 |
| `tūriyāriva` | `turiyāriva` | 1 | thig14.1:16.1 |
| `yācatassā` | `yāci tassā` | 1 | thig16.1:68.2 |
| `bhagavatā` | `bhagavato` | 1 | ud5.3:7.1 |
| `upapannāmhi` | `upapannamhi` | 1 | vv24:11.4 |
| `tūriyagaṇā` | `turiyagaṇā` | 1 | vv60:2.3 |
| `tūriyamivappavāditaṁ` | `turiyamivappavāditaṁ` | 1 | vv64:5.4 |
| `upapajjati` | `uppajjati` | 1 | vv9:7.3 |

## C. Слова, которых нет в MS или есть только в MS: вопрос владельцу (20 чтений, 24 мест)

Пропуск в печати (an10.217 `ekacco pāṇātipātaṁ pahāya`) или лишнее слово. Исправить значит вписать или убрать текст.

| MS 2005 | другие издания | мест | где |
|---|---|---|---|
| `ekacco` | `ekacco pāṇātipātaṁ pahāya` | 1 | an10.217:20.2 |
| `bhagavā` | `bhagavā devo` | 1 | cnd19:20.5 |
| `hoti` | `(not there)` | 1 | cnd23:292.2 |
| `dhamme` | `(not there)` | 1 | cnd8:64.14 |
| `etaṁ` | `(not there)` | 1 | dn29:30.4 |
| `hi` | `(not there)` | 1 | dn9:33.26 |
| `āgamayamānā` | `āgamayamānā na` | 1 | mn94:3.6 |
| `kho` | `(not there)` | 2 | mnd15:170.4, sn16.13:2.2 |
| `ca` | `(not there)` | 1 | mnd15:183.4 |
| `vikāle kālasaññitā kāle vikālasaññitā` | `(not there)` | 1 | mnd16:247.1 |
| `vācāya` | `vācāya niviṭṭhā` | 1 | mnd2:49.8 |
| `samuggahītanti` | `(not there)` | 1 | mnd9:11.4 |
| `kacci` | `kacci te` | 1 | pli-tv-bu-vb-pc23:2.10 |
| `sā` | `(not there)` | 1 | pli-tv-bu-vb-ss8:1.8.21 |
| `saddhāya` | `saddhāya sā` | 1 | pli-tv-kd10:1.8.16 |
| `mama` | `(not there)` | 1 | pli-tv-kd19:1.4.8 |
| `ācariyupajjhāye` | `ācariyupajjhāye na` | 2 | pli-tv-kd2:21.1.1, pli-tv-kd2:21.1.3 |
| `vihareyya` | `vihareyya so rūpe` | 1 | sn22.149:1.7 |
| `upasaṅkamitvā` | `(not there)` | 1 | sn5.3:1.3 |
| `saṁvijjante` | `saṁvijjante te` | 3 | sn55.39:3.1, sn55.3:3.1, sn55.3:4.1 |

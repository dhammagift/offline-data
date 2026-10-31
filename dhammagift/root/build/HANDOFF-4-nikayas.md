# 4 никаи (DN, MN, SN, AN): что есть в offline-data и как доработать

Для сессии на сервере (F1 / dg-node). Репо `dhammagift/offline-data`, ветка `main`, всё в `dhammagift/`.
Подробно: `root/build/README.md`. Лицензии: `dhammagift/LICENSE.md`.

## Что уже лежит в данных

| что | где | для чего |
|---|---|---|
| Палийские корни 5 изданий на id сегментов ms | `root/pli/{bjt,my,th,mso,pts}/sutta/{dn,mn,sn,an}/…_root-pli-<ed>.json` | переключение изданий, сравнение |
| Книжная Махасангити 2005 | `root/pli/mso` (+ `reference/pli/mso`, номера параграфов) | печатный текст; в dg.db пока не включён |
| Разночтения всех изданий + сноски | `variant/pli/ms/sutta/{dn,mn,sn,an}/…_variant-pli-ms.json` | показывать под Пали-текстом; первыми идут ошибки SuttaCentral `(SC error: …)` |
| Исправления ошибок SuttaCentral | `root/build/sc-fixes/fixes.json`, `apply.py` | накатываются на чекаут bilara-data после еженедельного обновления |
| Страница сравнения | `root/build/viewer/` (`index.html` + `data/`) | old.dhamma.gift/editions после `git pull` |

Формат всех файлов как у bilara-data: `{ "sn35.19:2.9": "…" }`, ключи и порядок как в `root/pli/ms`.

## Как подключить в dg.db

- Корень по умолчанию остаётся `ms` с наложенными `sc-fixes` (`python3 root/build/sc-fixes/apply.py <bilara-data root/pli/ms>`).
- Дополнительные корни: `root/pli/<ed>` по тем же ключам. Пустая строка `""` значит, что в издании этой строки нет.
- Разночтения: `variant/pli/ms`, одна строка на сегмент, записи через ` | `, вида `слово ms → чтение (издания)`.
  `ms2005` — книжная Махасангити, `pts` — PTS (CC BY-SA 4.0), `(… note)` — сноска издания.
  Длинная запись на `mn10:44.3` (1 300 слов) — блок о четырёх истинах, который SuttaCentral выбросил из MN 10 (в 2017 у них он был).

## Как пересобрать только 4 никаи

Источники вне репо (пути в README, раздел Run / sync): tipitaka.lk, tipitaka-xml, bilara-data, palinew.sqlite,
tipitaka2500.github.io, GRETIL `2_pali` (ветка `gretil-pali`, `gretil/2_pali.zip`).

```
python3 dhammagift/root/build/build_editions.py --bjt tipitaka.lk/public/static/text --vri tipitaka-xml/romn \
  --ms bilara-data/root/pli/ms/sutta --thai palinew.sqlite --ref bilara-data/reference/pli/ms/sutta \
  --out dhammagift --notes notes --only dn,mn,sn,an --report dhammagift/root/build/report.tsv
python3 dhammagift/root/build/build_editions.py ... --eds mso --mso tipitaka2500.github.io/tipitaka --out dhammagift --only dn,mn,sn,an
python3 dhammagift/root/build/build_editions.py ... --eds pts --pts 2_pali/1_tipit --out dhammagift --only dn,mn,sn,an
python3 dhammagift/root/build/pts_notes.py 2_pali/1_tipit bilara-data/root/pli/ms/sutta dhammagift/root/pli/pts notes
python3 dhammagift/root/build/collate.py bilara-data/root/pli/ms bilara-data/variant/pli/ms dhammagift dhammagift/root/pli/mso notes dhammagift/root/pli/pts
python3 dhammagift/root/build/viewer/make_viewer_data.py dhammagift bilara-data/root/pli/ms/sutta dhammagift/root/build/viewer
python3 dhammagift/root/build/viewer/find_shifts.py dhammagift/root/build/viewer/data dhammagift/root/build/viewer/data/shifts.json
```

`collate.py` всегда идёт по всему канону (около 9 минут). Выравнивание делается только правилами в `build_editions.py`,
ручных правок сегментов нет: исправление вносится правилом, потом пересборка.

## Доработки, которые можно сделать (по желанию)

1. **Печатные подзаголовки, которых нет в ms** (15 мест в 4 никаях, список в `root/build/compare/ms-orig.tsv`, op `insert`):
   - sn43.12:2.1–11.1: `Vipassanā`, `Vitakkasamādhi`, `Suññatasamādhi`, `Satipaṭṭhāna`, `Sammappadhāna`, `Iddhipāda`,
     `Indriya`, `Bala`, `Bojjhaṅga`, `Maggaṅga`;
   - dn29:1.3 `Nigaṇṭhanāṭaputtakālaṅkiriyā`, dn33:1.2.1 `Ubbhatakanavasandhāgāra`; an3.20:6.8 `Rathakāravaggo dutiyo`
     (в книге стоит на другом месте).

   Это не ошибки: SuttaCentral их просто не взял. Если нужны в наших данных: показывать как подзаголовок из `root/pli/mso` (они там стоят в начале
   этих сегментов) или собрать в `3-printed-headings.md` для отчёта SuttaCentral.
2. **Страницы PTS.** В GRETIL есть метки `[page 003]`, в reference bilara-data есть ссылки `pts-vp-pli` по абзацам. Чтобы иметь страницы
   с точностью до слова: в `pts_stream` (`build_editions.py`) передавать `[page N]` как маркер `pb` (как у BJT/Thai),
   тогда появится `reference/pli/pts`.
3. **Склейки у BJT** через кавычку на границе сегментов (dn23:23.48, mn56:24.2 и ещё 3) теперь делятся правилом.

## Что сделано недавно (для контекста)

- Граница сегмента, сдвинутая на несколько слов, возвращается правилом (156 сегментов, в основном BJT и Сиам).
- Заголовок ms, повторённый в начале текста (`Eko dhammo` / `Eko, āvuso, dhammo …`), остаётся в тексте издания.
- Ошибки SuttaCentral из `sc-fixes/fixes.json` (все внесены их правками, см. отчёт) стоят первыми в разночтениях; отчёт: `root/build/compare/sc-report/`.

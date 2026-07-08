// Sutta search: maps "mn1", "sn35.5", "an4.1", "dn16", "dhp223", "thag378", "thig45", "ud4.2" etc. to their HTML files
(function() {

  // How many folders deep is the CURRENT page relative to the site root?
  // Read it off this very script's own src attribute rather than assuming
  // a fixed depth. Regular sutta pages load this as
  // <script src="../js/sutta-search.js">  (1 level deep → root prefix "../")
  // while e.g. the ebt-study pages load it as
  // <script src="../../js/sutta-search.js"> (2 levels deep → "../../").
  // This must run synchronously at the top of the IIFE, since
  // document.currentScript is only valid during the script's own initial
  // execution — by the time initSearch()/navigateToSutta() run later
  // (on DOMContentLoaded / a keydown), it would already be null.
  var ROOT_PREFIX = (function() {
    var scriptEl = document.currentScript;
    if (!scriptEl) {
      // Fallback for browsers/contexts where currentScript isn't set:
      // find the <script> tag whose src ends in sutta-search.js.
      var scripts = document.getElementsByTagName('script');
      for (var i = scripts.length - 1; i >= 0; i--) {
        var src = scripts[i].getAttribute('src') || '';
        if (/sutta-search\.js(\?.*)?$/.test(src)) { scriptEl = scripts[i]; break; }
      }
    }
    var src = scriptEl ? (scriptEl.getAttribute('src') || '') : '../js/sutta-search.js';
    var depth = (src.match(/\.\.\//g) || []).length;
    if (depth < 1) depth = 1; // safe fallback: assume at least one level deep
    return new Array(depth + 1).join('../');
  })();

  // Collections whose pages cover a RANGE of numbers rather than one number
  // per file (e.g. Dhammapada is split into chapter files like
  // "dhp221-234.html"). Each range list must be sorted and contiguous,
  // covering every verse number that exists in that collection.
  // Format: [firstVerse, lastVerse, fileBaseName]
  // where fileBaseName omits the folder prefix and .html suffix.
  var RANGE_MAP = {
    dhp: [
      [1, 20], [21, 32], [33, 43], [44, 59], [60, 75], [76, 89], [90, 99],
      [100, 115], [116, 128], [129, 145], [146, 156], [157, 166], [167, 178],
      [179, 196], [197, 208], [209, 220], [221, 234], [235, 255], [256, 272],
      [273, 289], [290, 305], [306, 319], [320, 333], [334, 359], [360, 382],
      [383, 423]
    ],
    // Theragāthā: verse-number → tha/thaNN.html (+ #content anchor)
    // tha0 = intro/table of contents; verse lookup starts from tha1.
    thag: [
      [1,   120,  'tha1'],
      [121, 218,  'tha2'],
      [219, 266,  'tha3'],
      [267, 314,  'tha4'],
      [315, 374,  'tha5'],
      [375, 458,  'tha6'],
      [459, 493,  'tha7'],
      [494, 517,  'tha8'],
      [518, 526,  'tha9'],
      [527, 596,  'tha10'],
      [597, 607,  'tha11'],
      [608, 631,  'tha12'],
      [633, 644,  'tha13'],
      [645, 672,  'tha14'],
      [673, 704,  'tha15'],
      [705, 948,  'tha16'],
      [949, 1053, 'tha17'],
      [1054,1093, 'tha18'],
      [1094,1148, 'tha19'],
      [1149,1217, 'tha20'],
      [1218,1288, 'tha21']
    ],
    // Therīgāthā: verse-number → thi/thiNN.html (+ #content anchor)
    thig: [
      [1,   18,  'thi1'],
      [19,  38,  'thi2'],
      [39,  62,  'thi3'],
      [63,  66,  'thi4'],
      [67,  126, 'thi5'],
      [127, 174, 'thi6'],
      [175, 195, 'thi7'],
      [196, 203, 'thi8'],
      [204, 212, 'thi9'],
      [213, 223, 'thi10'],
      [224, 235, 'thi11'],
      [236, 251, 'thi12'],
      [252, 367, 'thi13'],
      [368, 401, 'thi14'],
      [402, 449, 'thi15'],
      [450, 524, 'thi16']
    ]
  };

  // Sutta Nipata (SNP): maps PTS verse numbers (snp1–snp1149) to their
  // HTML file (e.g. snp5.13.html). Also accepts chapter.sutta notation
  // like snp1.1, snp4.16, etc.
  // Verse ranges sourced from the Modern–PTS concordance table.
  var SNP_VERSE_MAP = [
    // Chapter 1
    { file: 'snp1.1',  lo: 1,    hi: 17   },
    { file: 'snp1.2',  lo: 18,   hi: 34   },
    { file: 'snp1.3',  lo: 35,   hi: 75   },
    { file: 'snp1.4',  lo: 76,   hi: 82   },
    { file: 'snp1.5',  lo: 83,   hi: 90   },
    { file: 'snp1.6',  lo: 91,   hi: 115  },
    { file: 'snp1.7',  lo: 116,  hi: 142  },
    { file: 'snp1.8',  lo: 143,  hi: 152  },
    { file: 'snp1.9',  lo: 153,  hi: 180  },
    { file: 'snp1.10', lo: 181,  hi: 192  },
    { file: 'snp1.11', lo: 193,  hi: 206  },
    { file: 'snp1.12', lo: 207,  hi: 221  },
    // Chapter 2
    { file: 'snp2.1',  lo: 222,  hi: 238  },
    { file: 'snp2.2',  lo: 239,  hi: 252  },
    { file: 'snp2.3',  lo: 253,  hi: 257  },
    { file: 'snp2.4',  lo: 258,  hi: 269  },
    { file: 'snp2.5',  lo: 270,  hi: 273  },
    { file: 'snp2.6',  lo: 274,  hi: 283  },
    { file: 'snp2.7',  lo: 284,  hi: 315  },
    { file: 'snp2.8',  lo: 316,  hi: 323  },
    { file: 'snp2.9',  lo: 324,  hi: 330  },
    { file: 'snp2.10', lo: 331,  hi: 334  },
    { file: 'snp2.11', lo: 335,  hi: 342  },
    { file: 'snp2.12', lo: 343,  hi: 358  },
    { file: 'snp2.13', lo: 359,  hi: 375  },
    { file: 'snp2.14', lo: 376,  hi: 404  },
    // Chapter 3
    { file: 'snp3.1',  lo: 405,  hi: 424  },
    { file: 'snp3.2',  lo: 425,  hi: 449  },
    { file: 'snp3.3',  lo: 450,  hi: 454  },
    { file: 'snp3.4',  lo: 455,  hi: 486  },
    { file: 'snp3.5',  lo: 487,  hi: 509  },
    { file: 'snp3.6',  lo: 510,  hi: 547  },
    { file: 'snp3.7',  lo: 548,  hi: 573  },
    { file: 'snp3.8',  lo: 574,  hi: 593  },
    { file: 'snp3.9',  lo: 594,  hi: 656  },
    { file: 'snp3.10', lo: 657,  hi: 678  },
    { file: 'snp3.11', lo: 679,  hi: 723  },
    { file: 'snp3.12', lo: 724,  hi: 765  },
    // Chapter 4
    { file: 'snp4.1',  lo: 766,  hi: 771  },
    { file: 'snp4.2',  lo: 772,  hi: 779  },
    { file: 'snp4.3',  lo: 780,  hi: 787  },
    { file: 'snp4.4',  lo: 788,  hi: 795  },
    { file: 'snp4.5',  lo: 796,  hi: 803  },
    { file: 'snp4.6',  lo: 804,  hi: 813  },
    { file: 'snp4.7',  lo: 814,  hi: 823  },
    { file: 'snp4.8',  lo: 824,  hi: 834  },
    { file: 'snp4.9',  lo: 835,  hi: 847  },
    { file: 'snp4.10', lo: 848,  hi: 861  },
    { file: 'snp4.11', lo: 862,  hi: 877  },
    { file: 'snp4.12', lo: 878,  hi: 894  },
    { file: 'snp4.13', lo: 895,  hi: 914  },
    { file: 'snp4.14', lo: 915,  hi: 934  },
    { file: 'snp4.15', lo: 935,  hi: 954  },
    { file: 'snp4.16', lo: 955,  hi: 975  },
    // Chapter 5 (Vatthugatha intro + 16 student questions)
    { file: 'snp5.0',  lo: 976,  hi: 1031 },
    { file: 'snp5.1',  lo: 1032, hi: 1039 },
    { file: 'snp5.2',  lo: 1040, hi: 1042 },
    { file: 'snp5.3',  lo: 1043, hi: 1048 },
    { file: 'snp5.4',  lo: 1049, hi: 1060 },
    { file: 'snp5.5',  lo: 1061, hi: 1068 },
    { file: 'snp5.6',  lo: 1069, hi: 1076 },
    { file: 'snp5.7',  lo: 1077, hi: 1083 },
    { file: 'snp5.8',  lo: 1084, hi: 1087 },
    { file: 'snp5.9',  lo: 1088, hi: 1091 },
    { file: 'snp5.10', lo: 1092, hi: 1095 },
    { file: 'snp5.11', lo: 1096, hi: 1100 },
    { file: 'snp5.12', lo: 1101, hi: 1104 },
    { file: 'snp5.13', lo: 1105, hi: 1111 },
    { file: 'snp5.14', lo: 1112, hi: 1115 },
    { file: 'snp5.15', lo: 1116, hi: 1119 },
    { file: 'snp5.16', lo: 1120, hi: 1149 }
  ];

  // Resolve an SNP query string to a file path, or null if unrecognised.
  // Accepts two formats:
  //   - Verse number:  "snp223", "snp1106"  → lookup in SNP_VERSE_MAP
  //   - Chapter.sutta: "snp1.8", "snp5.13"  → direct file name
  function resolveSnp(num) {
    // Chapter.sutta notation: contains a dot (e.g. "1.8", "5.13")
    if (num.indexOf('.') !== -1) {
      // Validate that the chapter.sutta exists in our map
      var target = 'snp' + num;
      for (var i = 0; i < SNP_VERSE_MAP.length; i++) {
        if (SNP_VERSE_MAP[i].file === target) {
          return target + '.html';
        }
      }
      return null; // not a known sutta
    }

    // Plain verse number (e.g. "223", "1106")
    var v = parseInt(num, 10);
    if (isNaN(v)) return null;
    for (var j = 0; j < SNP_VERSE_MAP.length; j++) {
      if (v >= SNP_VERSE_MAP[j].lo && v <= SNP_VERSE_MAP[j].hi) {
        return SNP_VERSE_MAP[j].file + '.html';
      }
    }
    return null; // verse out of range
  }

  // Returns { file, anchor } or null.
  // Ranges with 3 elements use [lo, hi, fileBase]; ranges with 2 elements
  // (dhp legacy) use [lo, hi] and build the filename as
  // nikaya + lo + '-' + hi + '.html'. Either way, the anchor jumps straight
  // to the searched verse's own paragraph (#p<n>) rather than just the
  // top of the file.
  function findRangeFile(nikaya, num) {
    var n = parseInt(num, 10);
    if (isNaN(n)) return null;
    var ranges = RANGE_MAP[nikaya];
    for (var i = 0; i < ranges.length; i++) {
      var r = ranges[i];
      if (n >= r[0] && n <= r[1]) {
        if (r.length === 3) {
          return { file: r[2] + '.html', anchor: '#p' + n };
        } else {
          return { file: nikaya + r[0] + '-' + r[1] + '.html', anchor: '#p' + n };
        }
      }
    }
    return null;
  }

  function navigateToSutta(raw) {
    var q = raw.trim().toLowerCase().replace(/\s+/g, '');
    if (!q) return false;

    // Determine nikaya prefix and number part.
    // NOTE: longer prefixes (snp, thag, thig) must come before any
    // shorter prefix they start with (sn, tha, thi) so the regex
    // alternation picks the right one.
    var m = q.match(/^(mn|dn|snp|sn|an|dhp|thag|thig|ud)(.+)$/);
    if (!m) return false;

    var nikaya = m[1];   // mn, dn, snp, sn, an, dhp, thag, thig, ud
    var num    = m[2];   // e.g. "1", "12.40", "378", "5.13", "4.2"

    var file, anchor;

    if (nikaya === 'snp') {
      file = resolveSnp(num);
      if (!file) return false;
      anchor = '';
    } else if (RANGE_MAP[nikaya]) {
      var result = findRangeFile(nikaya, num);
      if (!result) return false;
      file   = result.file;
      anchor = result.anchor;
      // For thag/thig the folder on disk is tha/thi (without the 'g')
      if (nikaya === 'thag') nikaya = 'tha';
      if (nikaya === 'thig') nikaya = 'thi';
    } else {
      // Simple 1:1 collections (mn, dn, sn, an, ud, etc.)
      // ud4.2 → ud/ud4.2.html#content
      // mn1   → mn/mn1.html  (no anchor)
      file   = nikaya + num + '.html';
      anchor = (nikaya === 'ud') ? '#content' : '';
    }

    // Build the path back to site root dynamically (ROOT_PREFIX), instead
    // of assuming every page is exactly one folder deep — that assumption
    // broke on pages nested deeper, e.g. ebt-study/mncomp/*.html, producing
    // URLs like "ebt-study/mn/mn19.html" instead of "mn/mn19.html".
    var base = ROOT_PREFIX + nikaya + '/' + file + anchor;

    // Navigate
    window.location.href = base;
    return true;
  }

  function initSearch() {
    var input = document.getElementById('sutta-search');
    var err   = document.getElementById('sutta-search-error');
    if (!input) return;

    // Measure width of the three theme pills to size the search bar
    function sizeSearchBar() {
      var btns = document.querySelectorAll('.theme-btn');
      if (btns.length >= 3) {
        var first = btns[0].getBoundingClientRect();
        var last  = btns[2].getBoundingClientRect();
        var w = (last.right - first.left);
        if (w > 20) input.style.width = Math.round(w) + 'px';
      }
    }

    // Size on load and resize
    if (document.readyState === 'complete') {
      sizeSearchBar();
    } else {
      window.addEventListener('load', sizeSearchBar);
    }
    window.addEventListener('resize', sizeSearchBar);

    // Re-measure once custom web fonts finish loading, since a font swap
    // can change the rendered width of the theme buttons after the
    // initial 'load' event has already fired (common on mobile Safari).
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(sizeSearchBar).catch(function() {});
    }
    // Fallback re-measure shortly after paint, in case of any other
    // late layout shift on first load.
    setTimeout(sizeSearchBar, 300);

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        var ok = navigateToSutta(input.value);
        if (!ok && err) {
          err.style.display = 'inline';
          err.textContent = 'Not found: ' + input.value;
          setTimeout(function() { err.style.display = 'none'; }, 2000);
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();

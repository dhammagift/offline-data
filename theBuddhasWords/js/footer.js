/* This file contains everything which needs to happen at the end of
 * loading the main contents
 */

/* Safe localStorage wrapper — file:// pages, private browsing, and some
 * browser storage policies can make real localStorage throw a SecurityError
 * ("opaque origin") the moment it's touched. Since this file has no
 * top-level try/catch, an uncaught throw here kills EVERYTHING after it in
 * this script for the rest of the page load — including the previous/next
 * sutta title-wrap logic much further down. Route all access through this
 * shim (falls back to an in-memory object) so a storage failure only means
 * "preferences don't persist across page loads," not "half the page breaks."
 */
var storage = (function () {
  var mem = {};
  try {
    var testKey = "__bw_storage_test__";
    window.localStorage.setItem(testKey, "1");
    window.localStorage.removeItem(testKey);
    return window.localStorage;
  } catch (e) {
    return {
      getItem: function (k) { return k in mem ? mem[k] : null; },
      setItem: function (k, v) { mem[k] = String(v); },
      removeItem: function (k) { delete mem[k]; },
    };
  }
})();

DEBUGGERIZE = false;

if (DEBUGGERIZE) {
  oldBody = $(document.body).clone();
}

findClass = "search-match";
findTargetSelector = "p:visible";
findResultCurrentClass = "search-current";
sectionDivSelector = "hr, hgroup, h1, h2, h3, h4, h5, h6, div.glob";
sectionDivHiddenSelector = "hr";
paliVisible = storage.getItem("paliVisible") == "true" ? true : false;

/*
$('#pali').removeClass('active')
*/
/* When the english and pali are spliced together, elements are grouped
 * and the groups end on one of the below.
 */
spliceCloses = "p, blockquote, div";
/* A new group should open on these, even if it otherwise wouldn't */
spliceOpens = "hgroup, h1, h2, h3";

/* This function decides whether a paragraph should be lumped anyway
 * It wont be lumped if:
 * The node type is anything other than 'p' (i.e. div or blockquote)
 * If it is at least 200 characters long.
 * If it contains at least 2 sentence-enders.
 * */
function insignificant(e) {
  if (e.nodeName != "P") return false;
  var text = $(e).text();
  if (text.length < 80) return true;
  if (text.length >= 200) return false;
  var m = text.match(/[.!?:]/g),
    periodCount = m ? m.length : 0;

  return periodCount <= 1;
}

var next_sutta = $("#next-sutta").attr("title", "Next Sutta"),
  previous_sutta = $("#previous-sutta").attr("title", "Previous Sutta");

function groupy(collection) {
  var out = [],
    group = [];

  for (var i = 0; i < collection.length; i++) {
    var e = collection[i];
    if ($(e).is(spliceOpens) && $(group).is(spliceCloses)) {
      out.push(group);
      group = [];
    }
    group.push(e);
    if ($(e).is(spliceCloses) && !insignificant(e)) {
      out.push(group);
      group = [];
    }
  }
  if (group.length) {
    out.push(group);
  }
  return out;
}

/* Splits an array on elements for which splitFn returns true
 * these elements are included in the output (at the start of the
 * new group) unless excludeMatching is true.
 */
function arraySplit(array, splitFn, excludeMatching) {
  var current = [],
    out = [current],
    carrying = false;

  for (i = 0; i < array.length; i++) {
    var e = array[i],
      matches = splitFn(e);
    if (matches) {
      if (carrying) {
        current.push(e);
      } else {
        current = [e];
        out.push(current);
        carrying = true;
      }
    } else {
      carrying = false;
      current.push(e);
    }
  }
  return out;
}

function td(lang) {
  return $("<td lang=" + lang + ">");
}

function sum(array) {
  var total = 0;
  return array.reduce(function (a, b) {
    return a + b;
  }, 0);
}

sectionNum = 0;

function extraporlativeSplice(en, pi, table) {
  sectionNum++;

  var tr, entd, pitd;

  function rowReset() {
    tr = $("<tr>");
    entd = td("en").appendTo(tr);
    pitd = td("pi").appendTo(tr);
    table.append(tr);
  }

  if (en.length == 0) {
    rowReset();
    pitd.append(pi);
    return;
  }

  if (pi.length == 0) {
    rowReset();
    entd.append(en);
    return;
  }

  function textLength() {
    var node = $(this).clone();
    node.find(".note").remove();
    if ($(node).is(sectionDivSelector)) {
      return 0.01;
    }
    return node.text().length;
  }

  var enLengths = $(en).map(textLength).toArray(),
    piLengths = $(pi).map(textLength).toArray(),
    enRemains = sum(enLengths),
    piRemains = sum(piLengths),
    overallRatio = 1;
  (enIndex = 0), (piIndex = 0);

  function calculateOverallRatio() {
    return sum(enLengths.slice(enIndex)) / sum(piLengths.slice(piIndex));
  }

  function calculateRatio(ex, px) {
    return (
      sum(
        ex.map(function (i) {
          return enLengths[i];
        })
      ) /
      (sum(
        px.map(function (i) {
          return piLengths[i];
        })
      ) *
        overallRatio)
    );
  }

  function quality(v) {
    if (v > 1) return 1 / v;
    else return v;
  }

  var enStack, piStack;
  function stackReset() {
    enStack = [];
    piStack = [];
  }

  /* This is the meat of the function, it pairs up paragraphs trying
   * to equalize paragraph length. It advances to a new pairing, when it
   * can no longer improve the quality by adding additional paragraphs
   * on either side.
   */
  while (true) {
    var enDone = enIndex >= en.length,
      piDone = piIndex >= pi.length;
    if (enDone || piDone) {
      if (enDone) {
        pitd.append(pi.slice(piIndex));
      } else if (piDone) {
        entd.append(en.slice(enIndex));
      }
      break;
    }

    overallRatio = calculateOverallRatio();
    if (DEBUGGERIZE) {
      console.log("The overall ratio is " + overallRatio);
    }
    stackReset();
    rowReset();
    while ($(enStack[enIndex]).is(sectionDivSelector)) {
      enStack.push(enIndex);
      enIndex++;
    }
    while ($(piStack[piIndex]).is(sectionDivSelector)) {
      piStack.push(piIndex);
      piIndex++;
    }

    enStack.push(enIndex);
    enIndex++;

    piStack.push(piIndex);
    piIndex++;

    var ratio = calculateRatio(enStack, piStack);
    var bestQuality = quality(ratio);

    // While the english paragraph is longer
    while (ratio > 1) {
      var e = pi[piIndex];
      if ($(e).is(sectionDivSelector)) {
        //If we have hit a section divider we can't
        //continue.
        break;
      }

      piStack.push(piIndex);
      piIndex++;
      ratio = calculateRatio(enStack, piStack);
      newQuality = quality(ratio);
      if (newQuality < bestQuality) {
        piStack.pop();
        piIndex--;
        break;
      } else {
        bestQuality = newQuality;
      }
    }

    // While the pali paragraph is longer
    while (ratio < 1) {
      var e = en[enIndex];
      if ($(e).is(sectionDivSelector)) {
        break;
      }
      enStack.push(enIndex);
      enIndex++;
      ratio = calculateRatio(enStack, piStack);
      newQuality = quality(ratio);
      if (newQuality < bestQuality) {
        enStack.pop();
        enIndex--;
        break;
      } else {
        bestQuality = newQuality;
      }
    }

    // The row cannot be improved by adding a paragraph from either side
    entd.append(
      enStack.map(function (i) {
        return en[i];
      })
    );
    pitd.append(
      piStack.map(function (i) {
        return pi[i];
      })
    );
  }

  return;
}

function splice(en, pi, table) {
  if (pi.length == 0 && en.length == 0) {
    return;
  }

  // Group into td's
  var en_tds = groupy(en).map(function (g) {
      return $("<td lang=en>").append(g);
    }),
    pi_tds = groupy(pi).map(function (g) {
      return $("<td lang=pi>").append(g);
    }),
    i = 0;

  while (true) {
    var tr = $("<tr>"),
      en = en_tds.shift(),
      pi = pi_tds.shift();

    if (!en && !pi) {
      break;
    }

    tr.append([en, pi]);
    table.append(tr);
  }
}

function groupAdjacent(elements, wrapper, wrapall) {
  groups = [];
  group = [];
  last = null;
  for (var i = 0; i < elements.length; i++) {
    var e = elements[i];
    if (last != null) {
      if ($(e).prev()[0] == last) {
        group.push(e);
      } else {
        group = [e];
        groups.push(group);
      }
    }
    last = e;
  }
  groups.forEach(function (group) {
    if (!wrapall && group.length <= 1) return;

    var wrap = $(wrapper);
    $(group[0]).replaceWith(wrap);
    wrap.append(group);
  });
}

function alignedSplicer(section, table, selector) {
  if (!selector) selector = "hr";

  // Group section dividers

  groupAdjacent(section.find("div[lang=pi], div[lang=en]").children(sectionDivSelector), "<div class=glob>");

  var pi = section.find("div[lang=pi] > *");
  var en = section.find("div[lang=en] > *");

  en.filter(sectionDivHiddenSelector).show();
  pi.filter(sectionDivHiddenSelector).show();

  var splitFn = function (e) {
    return $(e).is(selector);
  };
  pies = arraySplit(pi, splitFn);
  ensies = arraySplit(en, splitFn);
  var msg =
    "There are " + ensies.length + " divisions of english texts and " + pies.length + " divisions of pali texts.";
  if (DEBUGGERIZE) {
    console.log(msg);
  }
  if (pies.length != ensies.length) {
    /*pies = [pi.toArray()];
 ensies = [en.toArray()];*/
  }
  var end = Math.max(pies.length, ensies.length);
  for (var i = 0; i < end; i++) {
    extraporlativeSplice(ensies[i] || [], pies[i] || [], table);
  }
}

/****** SPLICER ******/
$(document).ready(function () {
  if ($(".raw_sutta").length == 0) {
    // No splice will happen; inject now for non-sutta pages
    injectExternalTranslationLinks();
    injectComparativeStudy();
    return;
  }
  var table = $('<table class="pairs">');
  $(".raw_sutta").each(function () {
    alignedSplicer($(this), table, sectionDivSelector);
  });
  table.find("td[lang=pi]").hide();

  $("#content").append(table);
  /* Set an appropriate caption */
  var h1 = $("h1").first();
  // h1.prepend(previous_sutta);
  // h1.append(next_sutta);
  var caption = $("<caption>").append(h1);
  table.prepend(caption);

  $("tr").each(function () {});

  // On load retrieve the state of pali visibility from localStorage
  // which defaults to null (falsely) if it's never been set.
  setPaliVisibility(paliVisible);

  // Inject after splice has finished reorganising the DOM
  injectExternalTranslationLinks();
    injectComparativeStudy();
});

url_components = /.*\/([\w.]+)\/([\w.-]+)\.html/.exec(location.href);
division = url_components[1];

if ($(".raw_sutta div[lang=pi] > *").length == 0) {
  $("#pali").remove();
}

function loadPaliLookup() {
  if ($(".lookup").length == 0) {
    jQuery.ajax({
      url: "../js/pali-lookup-standalone.js",
      dataType: "script",
      success: function () {
        enablePaliLookup();
      },
      crossDomain: true,
    });
  }
}

function unloadPaliLookup() {
  jQuery.ajax({
    url: "../js/pali-lookup-standalone.js",
    dataType: "script",
    success: function () {
      disablePaliLookup();
    },
    crossDomain: true,
  });
}

// set default state of Pali Lookup to true
if (storage.getItem("paliLookupActive") === null) {
  storage.setItem("paliLookupActive", "true");
}

function setPaliVisibility(state) {
  // This actually both sets the Pali visibility as well as sets the Pali lookup
  if (state) {
    $("td:nth-child(2)").show();
    $("#pali").addClass("active");
    if (storage.getItem("paliLookupActive") === "true") {
      loadPaliLookup();
    } else {
      unloadPaliLookup();
    }
  } else {
    $("td:nth-child(2)").hide();
    $("#pali").removeClass("active");
  }
}

$("#pali").on("click", function () {
  paliVisible = !paliVisible;
  storage.setItem("paliVisible", paliVisible);
  setPaliVisibility(paliVisible);
});

// Move the previous/next sutta links so they flank the sutta title,
// e.g. "< MN4: The Root of All Things >", instead of sitting in the
// corner control panel.
var $suttaTitle = $("#content").children("h1, h2, h3, h4, h5").last();
if ($suttaTitle.length && (previous_sutta.length || next_sutta.length)) {
  previous_sutta.html('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>');
  next_sutta.html('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>');
  var $navContainer = $('<div class="sutta-nav-container"></div>');
  var $titleClone = $suttaTitle.clone();
  $suttaTitle.replaceWith($navContainer);
  $navContainer.append(previous_sutta).append($titleClone).append(next_sutta);
}

// --- Back to Top button (injected once, fixed bottom-right) ---
// Remove any static version baked into the HTML first, then inject a clean one.
(function injectBackToTop() {
  $(".back-to-top-btn, .back-to-top-row").remove();
  var $btn = $(
    '<a class="back-to-top-btn" href="#top" aria-label="Back to top">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
        '<polyline points="18 15 12 9 6 15"></polyline>' +
      '</svg>' +
    '</a>'
  );
  // iOS/Android WebKit keeps :hover active on <a> tags after a tap.
  // Blurring immediately on touchend releases the stuck hover state.
  $btn[0].addEventListener('touchend', function () {
    var el = this;
    setTimeout(function () { el.blur(); }, 0);
  }, { passive: true });
  $("body").append($btn);
})();

// --- Tap-to-open footnotes (.note / .copyrightnote) on touch devices ---
// These popups are shown via CSS :hover, which mobile browsers only fake
// while a finger is held down — that's why they used to need a long-press.
// This adds a real tap-to-toggle by flipping an .is-open class (see
// css.css, which shows .details whenever it has .is-open). Desktop still
// gets the original :hover behaviour, unaffected by this.
(function setupNoteTapToggle() {
  $(document).on("click", function (e) {
    var $target = $(e.target);
    var $note = $target.closest(".note, .copyrightnote");
    var $insideDetails = $target.closest(".details").length > 0;

    if ($note.length) {
      var $details = $note.find(".details");
      var wasOpen = $details.hasClass("is-open");
      $(".details.is-open").removeClass("is-open");
      if (!wasOpen) {
        $details.addClass("is-open");
      }
      e.stopPropagation();
    } else if (!$insideDetails) {
      // Tapped elsewhere on the page — close any open note.
      $(".details.is-open").removeClass("is-open");
    }
  });
})();

Mousetrap.bind("p", function (e) {
  document.getElementById("previous-sutta").click();
});

Mousetrap.bind("n", function (e) {
  document.getElementById("next-sutta").click();
});

Mousetrap.bind("*", function (e) {
  document.getElementById("pali").click();
});

Mousetrap.bind("h", function (e) {
  window.location.href = "../home/index.html";
});

Mousetrap.bind("?", function (e) {
  window.location.href = "../home/help.html";
});

Mousetrap.bind("c", function (e) {
  window.location.href = "../home/contact.html";
});

Mousetrap.bind("d", function (e) {
  var current = storage.getItem("lightMode") || "light";
  var next = current === "light" ? "sepia" : current === "sepia" ? "dark" : "light";
  if (typeof set_theme === "function") { set_theme(next); }
});

Mousetrap.bind("i", function (e) {
  const knBooks = ["kp", "dhp", "ud", "it", "snp", "tha", "thi"];
  const url = location.pathname.replace(/\.html/, "").split(/\//); // splits at  slashes
  const urlLength = url.length;
  const book = url[url.length - 2];
  const secondPart = url[url.length - 1];

  if (book == "home" && secondPart == "index") {
    return;
  } else if (book == "home") {
    window.location.href = "../home/index.html";
  } else if (book == "vi") {
    const vinayaBooks = ["kd", "bu-vb", "bi-vb", "bu-pt", "bi-pt"];
    const bhikkhuRuleTypes = [
      "bu-vb-pj",
      "bu-vb-sn",
      "bu-vb-an",
      "bu-vb-np",
      "bu-vb-pc",
      "bu-vb-pd",
      "bu-vb-sk",
      "bu-vb-as",
    ];
    const bhikkhuniRuleTypes = ["bi-vb-pj", "bi-vb-sn", "bi-vb-np", "bi-vb-pc", "bi-vb-pd", "bi-vb-sk", "bi-vb-as"];

    if (book == secondPart) {
      // move from book home page to site homepage
      window.location.href = "../home/index.html";
    } else if (vinayaBooks.includes(secondPart)) {
      // move from various vinaya books home to vi home
      window.location.href = "../vi/vi.html";
    } else if (bhikkhuRuleTypes.includes(secondPart)) {
      // move from bhikkhu rule-type page to bhikkhu vibhanga home
      window.location.href = "../vi/bu-vb.html";
    } else if (bhikkhuniRuleTypes.includes(secondPart)) {
      // move from bhikkhu rule-type page to bhikkhu vibhanga home
      window.location.href = "../vi/bi-vb.html";
    } else if (/\d/.test(secondPart)) {
      // if there is a number in the second part
      // that means we are on a rule page
      // move up to rule type page
      const ruleType = secondPart.replace(/\d/g, "");
      window.location.href = `../vi/${ruleType}.html`;
    }
  } else if (knBooks.includes(book) && book == secondPart) {
    // this is a top level page for a book in KN
    window.location.href = "../kn/kn.html#content";
  } else if (book == secondPart) {
    // this is a top level page for any nikaya
    window.location.href = "../home/index.html";
  } else if (/\./.test(secondPart)) {
    // This is a sutta page that is within a chapter
    const chapter = secondPart.split(/\./)[0];
    window.location.href = `../${book}/${chapter}.html`;
  } else if (book == "sn" && /sn[1-5]/.test(secondPart)) {
    // This is a samyutta top level page
    const samyutta = parseInt(secondPart.replace("sn", ""));
    if (samyutta >= 1 && samyutta <= 11) {
      window.location.href = `../sn/sn01.html`;
    } else if (samyutta >= 12 && samyutta <= 21) {
      window.location.href = `../sn/sn02.html`;
    } else if (samyutta >= 22 && samyutta <= 34) {
      window.location.href = `../sn/sn03.html`;
    } else if (samyutta >= 35 && samyutta <= 44) {
      window.location.href = `../sn/sn04.html`;
    } else {
      window.location.href = `../sn/sn05.html`;
    }
  } else {
    // This is a sutta not within a chapter
    window.location.href = `../${book}/${book}.html`;
  }
});

// toggle Pali lookup with keyboard command
Mousetrap.bind("mod+alt+l", function (e) {
  changePaliLookupStatus();
});

function changePaliLookupStatus() {
  const paliLookupCheckBox = document.getElementById("paliLookupCheck");

  if (storage.getItem("paliLookupActive") === "true") {
    storage.setItem("paliLookupActive", "false");
    paliLookupCheckBox.checked = false;
    alert("Pali Lookup has been turned off.\n\nPress Control+Alt+l \(Lower case \"L\"\ for \"lookup\") to turn it on.");
  } else {
    storage.setItem("paliLookupActive", "true");
    paliLookupCheckBox.checked = true;
    alert("Pali Lookup has been turned on\n\nPress Control+Alt+l \(Lower case \"L\"\ for \"lookup\") to turn it off.");
  }
  setPaliVisibility(paliVisible);
}

// insert the checkbox for Pali lookup
const footer = document.getElementsByTagName("footer")[0];
const settingsDiv = document.createElement("div");
settingsDiv.innerHTML = `<div class="w3-content w3-padding bwcontainer" style="background-color:#FFF3D6"> 
<label for="paliLookupCheck">Pali Lookup On:</label>
<input type="checkbox" id="paliLookupCheck">
</div>`;
footer.after(settingsDiv);
const paliLookupCheckBox = document.getElementById("paliLookupCheck");

// make the checkbox match the setting stored in local storage
paliLookupCheckBox.checked = JSON.parse(storage.getItem("paliLookupActive"));

paliLookupCheckBox.addEventListener("change", e => {
  changePaliLookupStatus();
});

// --- Random sutta button ---
// Picks a page at random from BW_SUTTA_INDEX (DN, MN, SN, AN + Khuddaka
// Nikaya texts; built from the site's own nikaya index pages, see
// js/sutta-index.js). Vinaya is intentionally excluded.
$("#randomSutta").on("click", function () {
  if (typeof BW_SUTTA_INDEX === "undefined" || !BW_SUTTA_INDEX.length) {
    return;
  }
  var current = location.pathname.split("/").slice(-2).join("/"); // e.g. "mn/mn1.html"
  var pick;
  do {
    pick = BW_SUTTA_INDEX[Math.floor(Math.random() * BW_SUTTA_INDEX.length)];
  } while (pick === current && BW_SUTTA_INDEX.length > 1);
  window.location.href = "../" + pick + "#content";
});

// --- Chinese parallels inline (breadcrumb area) ---
// BW_PARALLELS key = "folder/file.html", value = array of { label, url }.
// Labels are normalised: "SĀ sa213" → "SĀ 213", "EĀ ea11.5" → "EĀ 11.5", etc.
var BW_PARALLELS = window.BW_PARALLELS || {};

function normaliseParallelLabel(label) {
  // Strip the redundant lowercase prefix inside each label:
  // "SĀ sa213"   → "SĀ 213"
  // "SĀ² sa-2.5" → "SĀ² 2.5"
  // "EĀ ea11.5"  → "EĀ 11.5"
  // "EĀ² ea-2.39"→ "EĀ² 2.39"
  // "MĀ ma125"   → "MĀ 125"
  // "DĀ da25"    → "DĀ 25"
  // Handles any uppercase-letter prefix before Ā, optional superscript,
  // then the lowercase abbreviation (sa, ea, ma, da, etc.) followed by digits/dots.
  return label.replace(
    /^([A-Z]Ā[²³⁴⁵]?\s+)[a-z]+-?(\d[\d.]*(\s*\(~\))?)$/,
    "$1$2"
  );
}

(function injectParallelLinks() {
  var current = location.pathname.split("/").slice(-2).join("/");
  var parallels = BW_PARALLELS[current];
  if (!parallels || !parallels.length) return;

  var links = parallels.map(function (p) {
    var cleanLabel = normaliseParallelLabel(p.label);
    return $("<a>")
      .attr("href", p.url)
      .attr("target", "_blank")
      .attr("rel", "noopener")
      .addClass("inline-parallel-link")
      .text(cleanLabel);
  });

  // Build "Parallel to: LinkA / LinkB" span and insert after breadcrumbs
  var $container = $("<div>").addClass("inline-parallels");
  $container.append($("<span>").addClass("inline-parallels-label").text("Parallel to: "));
  links.forEach(function (link, i) {
    if (i > 0) $container.append(document.createTextNode(" / "));
    $container.append(link);
  });

  var $breadcrumbs = $("#breadcrumbs");
  if ($breadcrumbs.length) {
    $breadcrumbs.after($container);
  }
})();

// --- "Parallel to: DĀ 3" on Pali sutta pages ---
// Injects a <p class="parallel-links"> after #metaarea, identical in
// markup and style to what the Āgama parallel pages use.
(function injectParallelToLabel() {
  var current = location.pathname.split("/").slice(-2).join("/");
  var parallels = BW_PARALLELS[current];
  if (!parallels || !parallels.length) return;

  // Skip on the Āgama parallel pages themselves
  if (document.querySelector(".parallel-page")) return;

  var $p = $("<p>").addClass("parallel-links").text("Parallel to: ");

  parallels.forEach(function (p, i) {
    if (i > 0) $p.append(document.createTextNode(" / "));
    var cleanLabel = normaliseParallelLabel(p.label);
    $p.append(
      $("<a>")
        .attr("href", p.url)
        .attr("target", "_blank")
        .attr("rel", "noopener")
        .text(cleanLabel)
    );
  });

  var $metaarea = $("#metaarea");
  if ($metaarea.length) {
    $metaarea.after($p);
  }
})();

// --- External translation links (SuttaCentral and s.4nt.org) ---
// Builds and injects the "Other translations:" paragraph before #nextprev.
// Defined as a named function so it can be called from $(document).ready()
// after alignedSplicer has finished reorganising the DOM.
function injectExternalTranslationLinks() {
  // Only run once
  if ($("#other-translations").length) return;

  // Get current path (e.g., "mn/mn1.html")
  var current = location.pathname.split("/").slice(-2).join("/");

  // Skip Vinaya
  var folder = current.split("/")[0];
  if (folder === "vi") return;

  // Skip Āgama parallel pages
  if (document.querySelector(".parallel-page")) return;

  // Must have #metaarea (i.e. be a sutta page)
  if (!$("#metaarea").length) return;

  // Extract sutta ID from path
  var filename = current.split("/")[1]; // e.g., "mn1.html"
  var suttaId = filename.replace(/\.html$/, ""); // e.g., "mn1"

  // For range files, extract the part before the hyphen (e.g. "an1.1-5" → "an1.1")
  var baseId = suttaId.split("-")[0];

  // Build SuttaCentral URL
  // - Theragatha/Therigatha: files are chapter-level (e.g. tha15.html), so link to
  //   the chapter's first verse using the sutta ID format (e.g. thag15.1, thig15.1)
  // - Itivuttaka: link to the pitaka/collection page
  // - All others: link directly to Sujato's English translation of the sutta
  var scUrl;
  if (folder === "tha") {
    var thagChapterNum = baseId.replace("tha", "");
    scUrl = "https://suttacentral.net/thag" + thagChapterNum + ".1/en/sujato?lang=en&layout=sidebyside&reference=none&notes=asterisk&highlight=false&script=latin";
  } else if (folder === "thi") {
    var thigChapterNum = baseId.replace("thi", "");
    scUrl = "https://suttacentral.net/thig" + thigChapterNum + ".1/en/sujato?lang=en&layout=sidebyside&reference=none&notes=asterisk&highlight=false&script=latin";
  } else if (folder === "it") {
    scUrl = "https://suttacentral.net/pitaka/sutta/minor/kn/iti?lang=en";
  } else {
    scUrl = "https://suttacentral.net/" + suttaId + "/en/sujato?lang=en&layout=sidebyside&reference=none&notes=asterisk&highlight=false&script=latin";
  }

  // Build s.4nt.org URL based on nikāya
  // Note: s.4nt.org uses "thag"/"thig" as subfolder names, not "tha"/"thi"
  var fourAntUrl, groupStr, group;

  if (folder === "dn" || folder === "mn") {
    fourAntUrl = "https://s.4nt.org/" + folder + "/" + suttaId + "/index.html";
  } else if (folder === "sn") {
    groupStr = baseId.split(".")[0].replace("sn", "");
    group = parseInt(groupStr, 10);
    fourAntUrl = "https://s.4nt.org/sn/sn" + group + "/index.html#" + baseId;
  } else if (folder === "an") {
    groupStr = baseId.split(".")[0].replace("an", "");
    group = parseInt(groupStr, 10);
    fourAntUrl = "https://s.4nt.org/an/an" + group + "/index.html#" + baseId;
  } else if (folder === "tha") {
    // Theragāthā: files are chapter-level (e.g. tha15.html), baseId = "tha15"
    // Strip "tha" prefix and append ".1" for the first verse of the chapter
    var thagChapter = baseId.replace("tha", "");
    fourAntUrl = "https://s.4nt.org/kn/thag/index.html#thag" + thagChapter + ".1";
  } else if (folder === "thi") {
    // Therigāthā: files are chapter-level (e.g. thi15.html), baseId = "thi15"
    // Strip "thi" prefix and append ".1" for the first verse of the chapter
    var thigChapter = baseId.replace("thi", "");
    fourAntUrl = "https://s.4nt.org/kn/thig/index.html#thig" + thigChapter + ".1";
  } else if (folder === "ud") {
    // Udāna: link directly to the sutta anchor (e.g. ud2.2 → #ud2.2)
    fourAntUrl = "https://s.4nt.org/kn/ud/index.html#" + baseId;
  } else if (folder === "it") {
    // Itivuttaka: link to main page only
    fourAntUrl = "https://s.4nt.org/kn/iti/index.html";
  } else if (folder === "dhp") {
    // Dhammapada: files are named by verse range (e.g. dhp44-59.html),
    // so baseId is already the first verse of the chapter (e.g. dhp44)
    fourAntUrl = "https://s.4nt.org/kn/dhp/index.html#" + baseId;
  } else if (["snp", "kp"].indexOf(folder) !== -1) {
    fourAntUrl = "https://s.4nt.org/kn/" + folder + "/index.html";
  } else {
    return;
  }

  // Build the paragraph with links
  // Order: B. Sujato / B. Thanissaro (if exists) / s.4nt.org
  var $p = $("<p>").attr("id", "other-translations").addClass("parallel-links").text("Other translations: ");

  $p.append(
    $("<a>")
      .attr("href", scUrl)
      .attr("target", "_blank")
      .attr("rel", "noopener")
      .text("B. Sujato")
  );

  // Add B. Thanissaro link only if Thanissaro translated this sutta
  var BW_DT = window.BW_DHAMMATALKS || {};
  var dtUrl = BW_DT[baseId];
  if (dtUrl) {
    $p.append(document.createTextNode(" / "));
    $p.append(
      $("<a>")
        .attr("href", dtUrl)
        .attr("target", "_blank")
        .attr("rel", "noopener")
        .text("B. Thanissaro")
    );
  }

  $p.append(document.createTextNode(" / "));

  $p.append(
    $("<a>")
      .attr("href", fourAntUrl)
      .attr("target", "_blank")
      .attr("rel", "noopener")
      .text("s.4nt.org")
  );

  // Inject before #nextprev (after sutta content, before prev/next nav)
  var $nextprev = $("#nextprev");
  if ($nextprev.length) {
    $nextprev.before($p);
  } else {
    $("#metaarea").after($p);
  }
}


/****** COMPARATIVE STUDY LINK (Anālayo) ******/
// Adds a "Read: Comparative study" line on MN Pāli sutta pages for which a
// comparative-study file exists in /ebt-study/mncomp/. Extend BW_MNCOMP_AVAILABLE
// as more suttas are built (e.g. ["mn1","mn2",...]).
window.BW_MNCOMP_AVAILABLE = window.BW_MNCOMP_AVAILABLE || ["mn1","mn2","mn3","mn4","mn5","mn6","mn7","mn8","mn9","mn10","mn11","mn12","mn13","mn14","mn15","mn16","mn17","mn18","mn19","mn20","mn21","mn22","mn23","mn24","mn25","mn26","mn27","mn28","mn29","mn30","mn31","mn32","mn33","mn34","mn35","mn36","mn37","mn38","mn39","mn40","mn41","mn42","mn43","mn44","mn45","mn46","mn47","mn48","mn49","mn50","mn51","mn52","mn53","mn54","mn55","mn56","mn57","mn58","mn59","mn60","mn61","mn62","mn63","mn64","mn65","mn66","mn67","mn68","mn69","mn70","mn71","mn72","mn73","mn74","mn75","mn76","mn77","mn78","mn79","mn80","mn81","mn82","mn83","mn84","mn85","mn86","mn87","mn88","mn89","mn90","mn91","mn92","mn93","mn94","mn95","mn96","mn97","mn98","mn99","mn100","mn101","mn102","mn103","mn104","mn105","mn106","mn107","mn108","mn109","mn110","mn111","mn112","mn113","mn114","mn115","mn116","mn117","mn118","mn119","mn120","mn121","mn122","mn123","mn124","mn125","mn126","mn127","mn128","mn129","mn130","mn131","mn132","mn133","mn134","mn135","mn136","mn137","mn138","mn139","mn140","mn141","mn142","mn143","mn144","mn145","mn146","mn147","mn148","mn149","mn150","mn151","mn152"];
function injectComparativeStudy() {
  if ($("#comparative-study").length) return;
  var current = location.pathname.split("/").slice(-2).join("/"); // e.g. "mn/mn1.html"
  var folder = current.split("/")[0];
  if (folder !== "mn") return;                       // MN suttas only
  if (document.querySelector(".parallel-page")) return;
  var suttaId = current.split("/")[1].replace(/\.html$/, ""); // e.g. "mn1"
  if (window.BW_MNCOMP_AVAILABLE.indexOf(suttaId) === -1) return;

  var $p = $("<p>").attr("id", "comparative-study").addClass("parallel-links").text("Read: ");
  $p.append(
    $("<a>").attr("href", "../ebt-study/mncomp/" + suttaId + "comp.html").text("Comparative study")
  );

  var $other = $("#other-translations");
  if ($other.length) {
    $other.after($p);
  } else {
    var $nextprev = $("#nextprev");
    if ($nextprev.length) { $nextprev.before($p); }
    else { $("#metaarea").after($p); }
  }
}

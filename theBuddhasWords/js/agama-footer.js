/* agama-footer.js
 * Runs on Chinese Āgama parallel pages (parallels/).
 * Injects "Other translations: <translators>" after the "Parallel to:" line,
 * reading the ordered list in BW_AGAMA_EN (built from SuttaCentral).
 */
(function injectAgamaTranslationLinks() {
  if (!document.querySelector('.parallel-page')) return;

  var match = location.pathname.match(/\/([^/]+)\.html$/);
  if (!match) return;
  var uid = match[1];

  var BW_AE = window.BW_AGAMA_EN || {};
  var entry = BW_AE[uid];
  if (!entry || !entry.length) return;

  var links = entry.map(function (t) {
    var a = document.createElement('a');
    a.href = t.url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = t.label;
    return a;
  });

  var $p = document.createElement('p');
  $p.className = 'parallel-links';
  $p.id = 'other-translations';
  $p.appendChild(document.createTextNode('Other translations: '));
  links.forEach(function (link, i) {
    if (i > 0) $p.appendChild(document.createTextNode(', '));
    $p.appendChild(link);
  });

  var parallelLinks = document.querySelector('.parallel-page .parallel-links');
  if (parallelLinks && parallelLinks.parentNode) {
    parallelLinks.parentNode.insertBefore($p, parallelLinks.nextSibling);
  } else {
    var content = document.getElementById('content');
    if (content) content.insertBefore($p, content.firstChild);
  }
})();

// --- Repeat "Parallel to:" at the bottom of Āgama pages ---
// Injects a <div class="inline-parallels"> before .bottomlinks inside <footer>,
// identical in markup and style to what footer.js injects after #breadcrumbs
// on Pāli sutta pages.
(function injectBottomParallelLinks() {
  if (!document.querySelector('.parallel-page')) return;

  // Read the links from the static top .parallel-links <p>
  var topLinks = document.querySelector('.parallel-page .parallel-links');
  if (!topLinks) return;
  var anchors = topLinks.querySelectorAll('a');
  if (!anchors.length) return;

  // Build the same inline-parallels div that footer.js builds on Pāli pages
  var container = document.createElement('div');
  container.className = 'inline-parallels';

  var label = document.createElement('span');
  label.className = 'inline-parallels-label';
  label.textContent = 'Parallel to: ';
  container.appendChild(label);

  anchors.forEach(function (a, i) {
    if (i > 0) container.appendChild(document.createTextNode(' / '));
    var link = document.createElement('a');
    link.href = a.href;
    link.className = 'inline-parallel-link';
    link.textContent = a.textContent;
    container.appendChild(link);
  });

  // Insert before .bottomlinks inside <footer> (Āgama pages have no #breadcrumbs)
  var bottomlinks = document.querySelector('footer .bottomlinks');
  if (bottomlinks) {
    bottomlinks.parentNode.insertBefore(container, bottomlinks);
  }
})();

// --- Back to Top button (injected once, fixed bottom-right) ---
// Remove any static version baked into the HTML first, then inject a clean one.
(function injectBackToTop() {
  var existing = document.querySelectorAll('.back-to-top-btn, .back-to-top-row');
  existing.forEach(function (el) { el.parentNode.removeChild(el); });

  var btn = document.createElement('a');
  btn.className = 'back-to-top-btn';
  btn.href = '#top';
  btn.setAttribute('aria-label', 'Back to top');
  btn.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" ' +
      'stroke-linecap="round" stroke-linejoin="round">' +
      '<polyline points="18 15 12 9 6 15"></polyline>' +
    '</svg>';
  // iOS/Android WebKit keeps :hover active on <a> tags after a tap.
  // Blurring immediately on touchend releases the stuck hover state.
  btn.addEventListener('touchend', function () {
    var el = this;
    setTimeout(function () { el.blur(); }, 0);
  }, { passive: true });
  document.body.appendChild(btn);
})();

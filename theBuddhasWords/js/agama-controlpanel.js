/* agama-controlpanel.js
 * Replaces controlpanel.js on Chinese Āgama parallel pages (parallels/).
 * Injects two toggle buttons: English (top) and 中文 (bottom).
 * Both default to visible (active). Clicking hides that column;
 * the remaining column expands to full width automatically.
 */

// Load shared index scripts (same as controlpanel.js)
document.write('<script src="../js/sutta-index.js"><\/script>');
document.write('<script src="../js/parallels-data.js"><\/script>');
document.write('<script src="../js/dhammatalks-index.js"><\/script>');

// Inject control panel with Eng on top, 中文 below
document.write(
  '<div class="controlpanel" id="controlpanel">' +
    '<ul id="cpbuttons">' +
      '<li><button class="cp-btn cp-btn-large" id="english" type="button" title="Show/hide English translation">Eng</button></li>' +
      '<li><button class="cp-btn cp-btn-large" id="chinese" type="button" title="Show/hide Chinese source text">中文</button></li>' +
    '</ul>' +
  '</div>'
);

// Wait for DOM before wiring up toggle logic
document.addEventListener('DOMContentLoaded', function () {

  var engVisible = localStorage.getItem('agamaEngVisible') !== 'false';
  var chiVisible = localStorage.getItem('agamaChiVisible') !== 'false';

  function setEngVisibility(state) {
    var cells = document.querySelectorAll('td.agama-eng');
    cells.forEach(function (td) {
      td.style.display = state ? '' : 'none';
    });
    var btn = document.getElementById('english');
    if (btn) {
      if (state) btn.classList.add('active');
      else btn.classList.remove('active');
    }
  }

  function setChiVisibility(state) {
    var cells = document.querySelectorAll('td.agama-chi');
    cells.forEach(function (td) {
      td.style.display = state ? '' : 'none';
    });
    var btn = document.getElementById('chinese');
    if (btn) {
      if (state) btn.classList.add('active');
      else btn.classList.remove('active');
    }
  }

  // Apply saved state on load
  setEngVisibility(engVisible);
  setChiVisibility(chiVisible);

  var engBtn = document.getElementById('english');
  if (engBtn) {
    engBtn.addEventListener('click', function () {
      engVisible = !engVisible;
      localStorage.setItem('agamaEngVisible', engVisible);
      setEngVisibility(engVisible);
    });
  }

  var chiBtn = document.getElementById('chinese');
  if (chiBtn) {
    chiBtn.addEventListener('click', function () {
      chiVisible = !chiVisible;
      localStorage.setItem('agamaChiVisible', chiVisible);
      setChiVisibility(chiVisible);
    });
  }

  // Keyboard shortcuts mirroring sutta page (e = english, c = chinese)
  if (window.Mousetrap) {
    Mousetrap.bind('e', function () { if (engBtn) engBtn.click(); });
    Mousetrap.bind('c', function () { if (chiBtn) chiBtn.click(); });
  }

});

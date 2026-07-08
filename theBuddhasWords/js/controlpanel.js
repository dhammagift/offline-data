(function () {
	// Locate this script's own directory so the sibling data files below
	// resolve correctly no matter how deeply nested the calling page is
	// (e.g. "../js/controlpanel.js" from mn/mn5.html vs "../../js/controlpanel.js"
	// from ebt-study/mncomp/mn6comp.html both point here). Previously these three
	// paths were hardcoded to "../js/...", which only worked for pages exactly
	// one directory level deep and 404'd for two-level-deep comp pages.
	var thisScript = document.currentScript;
	if (!thisScript) {
		var scripts = document.getElementsByTagName('script');
		thisScript = scripts[scripts.length - 1];
	}
	var jsDir = thisScript.src.replace(/[^\/]*$/, '');

	document.write('<script src="' + jsDir + 'sutta-index.js"></script>');
	document.write('<script src="' + jsDir + 'parallels-data.js"></script>');
	document.write('<script src="' + jsDir + 'dhammatalks-index.js"></script>');
	document.write('<div class="controlpanel" id="controlpanel"><ul id="cpbuttons"><li><button class="cp-btn cp-btn-large" id="randomSutta" type="button" title="Go to a random sutta">Random</button></li><li><button class="cp-btn cp-btn-large palitoggle" id="pali" type="button" title="Display Pali and activate Lookup Dictionary">P\u0101li</button></li></ul></div>');

	// Relocate buttons dynamically on all pages
	$(document).ready(function() {
		var $themeBtns = $('.theme-btns');
		if ($themeBtns.length) {
			// Wrap existing theme buttons in a group (iterate per container for robustness)
			$themeBtns.each(function() {
				$(this).children('button').wrapAll('<div class="theme-switch-group"></div>');
			});

			// Wrap Random and Pali buttons in a control group and append them
			var $random = $('#randomSutta');
			var $pali = $('#pali');
			var $controlGroup = $('<div class="control-group"></div>').append($random).append($pali);
			$themeBtns.append($controlGroup);

			// Add class to main container
			$themeBtns.addClass('theme-btns-relocated');

			// Remove old controlpanel wrapper (hidden by CSS :has() rule during parse)
			$('#controlpanel').remove();
		}
	});
})();

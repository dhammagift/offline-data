import Collapse from 'bootstrap/js/src/collapse';
import { oneEventListener } from './utils.js';

var headers = ["H1","H2","H3","H4","H5","H6"];

function navigateToAccordion() {
    var collapseTargetSel;
    var targetSel = collapseTargetSel = window.location.hash.substr(1);
    if (!targetSel) {
        return;
    }
    targetSel = targetSel.replace("collapse-", "");
    if (targetSel.includes("=")) return;

    if (!collapseTargetSel.includes("collapse-")) {
        collapseTargetSel = "collapse-" + collapseTargetSel;
    }
    var selector = "#" + collapseTargetSel + ".collapse";
    var targetEl;
    var accordionHeader = null;
    var collapseEl = document.querySelector(selector);
    if (collapseEl == null) {
        // Get the closest accordion that contains the target.
        targetEl = document.getElementById(targetSel);
        collapseEl = targetEl?.closest(".collapse");
        if (collapseEl == null)
            return;
    } else {
        accordionHeader = targetEl = collapseEl.previousElementSibling;
    }

    Collapse.getOrCreateInstance(collapseEl, {toggle: false}).show();
    oneEventListener(collapseEl, "shown.bs.collapse", function(event) {
        accordionHeader?.querySelector(".accordion-button")?.focus({preventScroll: true});
        targetEl.scrollIntoView({behavior: "smooth"});
        history.replaceState(null, '', '#' + targetSel);
    })
}

function setupAccordion() {
    document.querySelectorAll(".accordion .collapse").forEach(el => {
        el.addEventListener("show.bs.collapse", function() {
            this.removeAttribute("hidden");

            // Show parents in case they're collapsed (for navigating
            // to nested accordions with URL #hash)
            var parentCollapse = this.parentElement.closest(".collapse");
            if (parentCollapse != null) {
                Collapse.getOrCreateInstance(parentCollapse, {toggle: false}).show();
            }
        });

        el.addEventListener("hidden.bs.collapse", function(event) {
            event.stopPropagation();
            this.setAttribute("hidden", "until-found");
        });

        el.addEventListener("beforematch", function() {
            this.classList.add("no-transition");
            Collapse.getOrCreateInstance(this, {toggle: false}).show();
            oneEventListener(this, "shown.bs.collapse", function () {
                this.classList.remove("no-transition");
            });
        });
    });
    navigateToAccordion();
    window.addEventListener("hashchange", navigateToAccordion);
}

function setupOldAccordion() {
    var accordion = document.querySelector(".accordion-legacy");
    if (accordion == null) {
        return
    }
    accordion.addEventListener("click", function(e) {
        var target = e.target,
            name = target.nodeName.toUpperCase();
        if(headers.indexOf(name) > -1) {
            var subItem = target.nextElementSibling;
            if (subItem.classList.contains("opened")) {
                subItem.classList.remove("opened");
                subItem.classList.add("collapse", "show");
            }
            new Collapse(subItem, {toggle: true});
        }
    });

    accordion.querySelectorAll("a").forEach((el) => {
        el.addEventListener("click", function() {
            href = el.getAttribute('href');
            current = window.location.href.split('#')[0];
            console.log(href);
            history.pushState({needPop: true}, href, current + '#' + href);
        });
    });
}

export { setupAccordion, setupOldAccordion }

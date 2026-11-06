/* EPCSS static site enhancements (informational pages only).
 * No clinical data is read, stored, or transmitted by this script.
 * CSP note: loaded as an external file; no inline scripts anywhere. */
(function () {
    'use strict';

    // Highlight the current page in the nav.
    var here = window.location.pathname.split('/').pop() || 'index.html';
    var links = document.querySelectorAll('.site-nav a');
    Array.prototype.forEach.call(links, function (a) {
        var target = a.getAttribute('href') || '';
        if (target === here || (here === '' && target === 'index.html')) {
            a.classList.add('active');
            a.setAttribute('aria-current', 'page');
        }
    });

    // Mobile nav toggle.
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.site-nav ul');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    // Client-side search across the on-page index of topics (about/privacy/security pages).
    var search = document.getElementById('page-search');
    if (search) {
        var items = document.querySelectorAll('[data-searchable]');
        search.addEventListener('input', function () {
            var q = search.value.trim().toLowerCase();
            Array.prototype.forEach.call(items, function (el) {
                var text = el.textContent.toLowerCase();
                el.classList.toggle('search-hidden', q !== '' && text.indexOf(q) === -1);
            });
            document.querySelectorAll('.measure-group').forEach(function (section) {
                section.hidden = !section.querySelector('[data-searchable]:not(.search-hidden)');
            });
            var empty = document.getElementById('library-empty');
            if (empty) empty.hidden = !!document.querySelector('[data-searchable]:not(.search-hidden)');
        });
    }

    // Footer year.
    var year = document.getElementById('year');
    if (year) { year.textContent = String(new Date().getFullYear()); }
})();

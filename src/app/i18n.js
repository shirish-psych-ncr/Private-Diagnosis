import { renderDomainGrid } from './domain-grid.js';
import { renderResults } from './results-rendering.js';
import { renderScales } from './scale-rendering.js';
import { state, I18N } from './state.js';

/* ------------------------------------------------------------------ *
 * 3. i18n HELPERS
 * ------------------------------------------------------------------ */
function t(key) {
    const dict = I18N[state.lang] || I18N.en || {};
    return dict[key] !== undefined ? dict[key] : (I18N.en && I18N.en[key]) || key;
}

/** Resolve a bilingual {en,hi} object or plain string. */
function L(obj) {
    if (obj == null) return '';
    if (typeof obj === 'string') return obj;
    return obj[state.lang] || obj.en || '';
}

function applyLanguage(lang) {
    state.lang = lang;
    document.documentElement.lang = lang === 'hi' ? 'hi' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });
    // Re-render dynamic content in the new language WITHOUT touching inputs' values.
    renderDomainGrid();
    if (state.stage === 3) renderScales();
    if (state.stage === 4 && state.results) renderResults();
    updateLangButtons();
}

function updateLangButtons() {
    const en = document.getElementById('lang-en');
    const hi = document.getElementById('lang-hi');
    en.classList.toggle('active', state.lang === 'en');
    hi.classList.toggle('active', state.lang === 'hi');
    en.setAttribute('aria-pressed', String(state.lang === 'en'));
    hi.setAttribute('aria-pressed', String(state.lang === 'hi'));
}

export { t, L, applyLanguage, updateLangButtons };

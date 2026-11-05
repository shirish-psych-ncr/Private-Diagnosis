import { loadClinicalData } from './data.js';

import { renderDomainGrid } from './domain-grid.js';
import { bindStaticUI } from './events.js';
import { applyLanguage } from './i18n.js';
import { revealStage } from './navigation.js';
import { state, setClinicalData } from './state.js';

/* ------------------------------------------------------------------ *
 * 2. BOOTSTRAP — load clinical logic JSON, then render.
 * ------------------------------------------------------------------ */
async function boot() {
    try {
        setClinicalData(await loadClinicalData());
    } catch (err) {
        // file:// fallback: some browsers block fetch on local files.
        showError(err);
        return;
    }
    bindStaticUI();
    applyLanguage(state.lang);
    renderDomainGrid();
    // Only the consent stage is revealed on load. Stages 1-4 remain hidden
    // until their Continue controls validate and reveal them in sequence.
    revealStage(0);
}

function showError(err) {
    // DOM-safe insertion (no innerHTML) to honour the strict CSP posture.
    const div = document.createElement('div');
    div.className = 'load-error';
    div.setAttribute('role', 'alert');
    div.textContent = (state.lang === 'hi')
        ? 'डेटा लोड नहीं हो सका। कृपया इस पृष्ठ को HTTP(S) सर्वर (जैसे GitHub Pages) पर चलाएँ।'
        : 'Could not load clinical data (data/). Please serve this page over HTTP(S), e.g. via GitHub Pages.';
    document.getElementById('stage-0').after(div);
    console.error('EPCSS bootstrap failure:', err);
}

export { boot, showError };

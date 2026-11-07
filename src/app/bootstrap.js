import { loadClinicalData } from './data.js';

import { bindStaticUI } from './events.js';
import { applyLanguage } from './i18n.js';
import { revealStage } from './navigation.js';
import { state, setClinicalData } from './state.js';

/* ------------------------------------------------------------------ *
 * 2. BOOTSTRAP — load clinical logic JSON, then render.
 * ------------------------------------------------------------------ */
async function boot() {
    bindConsentUI();
    try {
        setClinicalData(await loadClinicalData());
    } catch (err) {
        // file:// fallback: some browsers block fetch on local files.
        showError(err);
        return;
    }
    bindStaticUI();
    applyLanguage(state.lang);

    // Only the consent stage is revealed on load. Stages 1-4 remain hidden
    // until their Continue controls validate and reveal them in sequence.
    revealStage(0);
}

function bindConsentUI() {
    const consentCheck = document.getElementById('consent-check');
    const consentButton = document.getElementById('consent-btn');
    const consentError = document.getElementById('consent-error');
    consentCheck.addEventListener('change', () => {
        consentButton.disabled = !consentCheck.checked;
        consentError?.classList.add('hidden');
    });
    consentButton.addEventListener('click', () => {
        if (!consentCheck.checked) {
            consentError?.classList.remove('hidden');
            consentError?.focus();
            return;
        }
        state.consent = true;
        revealStage(1);
    });
}

function showError(err) {
    // DOM-safe insertion (no innerHTML) to honour the strict CSP posture.
    const div = document.createElement('div');
    div.className = 'load-error';
    div.setAttribute('role', 'alert');
    const localFile = location.protocol === 'file:';
    div.textContent = localFile
        ? 'Open the hosted screening site to load the questionnaires.'
        : 'The questionnaires could not load. Check your connection and try again.';
    if (!localFile) {
        const retry = document.createElement('button');
        retry.type = 'button';
        retry.className = 'btn-primary';
        retry.textContent = 'Try again';
        retry.addEventListener('click', () => location.reload());
        div.append(document.createElement('br'), retry);
    }
    document.getElementById('stage-0').replaceChildren(div);
    console.error('EPCSS bootstrap failure:', err);
}

export { boot, showError };

import { state, CLINICAL_DATA } from './state.js';

/* ------------------------------------------------------------------ *
 * 7. SAFETY MODAL (non-dismissible except explicit acknowledgement)
 * ------------------------------------------------------------------ */
function openSafetyModal() {
    const modal = document.getElementById('safety-modal');
    const resources = document.getElementById('crisis-resources');
    resources.replaceChildren();
    (CLINICAL_DATA.crisisResources[state.lang] || CLINICAL_DATA.crisisResources.en).forEach(r => {
        const div = document.createElement('div');
        div.className = 'crisis-resource';
        const strong = document.createElement('strong');
        strong.textContent = r.label;
        const val = document.createElement('span');
        val.textContent = r.value;
        div.append(strong, val);
        resources.appendChild(div);
    });
    modal.classList.remove('hidden');
    modal.removeAttribute('aria-hidden');
    document.getElementById('safety-close').focus();
    document.body.style.overflow = 'hidden';
}

function closeSafetyModal() {
    const modal = document.getElementById('safety-modal');
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

export { openSafetyModal, closeSafetyModal };

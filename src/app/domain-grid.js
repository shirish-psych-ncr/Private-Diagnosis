import { L } from './i18n.js';
import { state, CLINICAL_DATA } from './state.js';

/* ------------------------------------------------------------------ *
 * 5. STAGE 2 — SYMPTOM CLUSTERING GRID
 * ------------------------------------------------------------------ */
function renderDomainGrid() {
    const list = document.getElementById('domain-list');
    if (!CLINICAL_DATA) return;
    const frag = document.createDocumentFragment();
    CLINICAL_DATA.domains.forEach(domain => {
        const label = document.createElement('label');
        label.className = 'domain-option' + (state.selectedDomains.has(domain.id) ? ' selected' : '');
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.value = domain.id;
        cb.checked = state.selectedDomains.has(domain.id);
        cb.setAttribute('aria-describedby', 'domains-help');
        cb.addEventListener('change', () => {
            if (cb.checked) state.selectedDomains.add(domain.id);
            else state.selectedDomains.delete(domain.id);
            label.classList.toggle('selected', cb.checked);
            document.getElementById('domains-error').classList.add('hidden');
        });
        const span = document.createElement('span');
        span.className = 'domain-name';
        span.textContent = L(domain.name);
        const desc = document.createElement('span');
        desc.className = 'domain-desc';
        desc.textContent = L(domain.description);
        label.append(cb, span, desc);
        frag.appendChild(label);
    });
    list.replaceChildren(frag);
}

export { renderDomainGrid };

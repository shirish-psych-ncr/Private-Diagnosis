import { L, t } from './i18n.js';
import { state, CLINICAL_DATA, choicesForDomain, defaultChoicesForDomain } from './state.js';

/* ------------------------------------------------------------------ *
 * 5. STAGE 2 — SYMPTOM CLUSTERING GRID
 * ------------------------------------------------------------------ */
function renderDomainGrid() {
    const list = document.getElementById('domain-list');
    if (!CLINICAL_DATA) return;
    const frag = document.createDocumentFragment();
    CLINICAL_DATA.domains.forEach(domain => {
        const topic = t('topic.' + domain.id, L(domain.name));
        const label = document.createElement('label');
        label.className = 'domain-option' + (state.selectedDomains.has(domain.id) ? ' selected' : '');
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.value = domain.id;
        cb.checked = state.selectedDomains.has(domain.id);
        const choices = document.createElement('div');
        const available = choicesForDomain(domain);
        if (domain.defaultForm && !available.length) {
            state.selectedDomains.delete(domain.id);
            state.scaleChoices.delete(domain.id);
            return;
        }
        const hasChoices = available.length > 1;
        if (hasChoices) {
            choices.className = 'scale-choice';
            choices.hidden = !cb.checked;
            const hasSavedChoice = state.scaleChoices.has(domain.id);
            const savedChoice = state.scaleChoices.get(domain.id);
            const selected = new Set(hasSavedChoice
                ? (Array.isArray(savedChoice) ? savedChoice : savedChoice === 'all'
                    ? available : [savedChoice]).filter(id => available.includes(id))
                : defaultChoicesForDomain(domain));
            const choicesLabel = document.createElement('span');
            choicesLabel.textContent = state.lang === 'hi' ? 'प्रश्नावलियाँ चुनें' : 'Choose scales';
            choices.append(choicesLabel);
            available.forEach(id => {
                const scale = id === 'base' ? null : CLINICAL_DATA.scales[id];
                const name = id === 'base' ? (domain.baseInstrument || domain.originalLabel)
                    : L(CLINICAL_DATA.scales[id].name);
                const label = document.createElement('label');
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.value = id;
                input.checked = selected.has(id);
                input.addEventListener('change', () => {
                    if (input.checked) selected.add(id); else selected.delete(id);
                    state.scaleChoices.set(domain.id, [...selected]);
                });
                const count = scale ? scale.parts.flatMap(part => part.questions).length : null;
                label.append(input, document.createTextNode(' ' + name + (count == null ? '' : ' (' + count + (state.lang === 'hi' ? ' प्रश्न' : ' items') + ')')));
                choices.append(label);
            });
        }
        cb.addEventListener('change', () => {
            if (cb.checked) state.selectedDomains.add(domain.id);
            else state.selectedDomains.delete(domain.id);
            choices.hidden = !cb.checked;
            label.classList.toggle('selected', cb.checked);
            document.getElementById('domains-error').classList.add('hidden');
        });
        const span = document.createElement('span');
        span.className = 'domain-name';
        span.textContent = topic;
        label.append(cb, span);
        const group = document.createElement('div');
        group.append(label);
        if (hasChoices) group.append(choices);
        frag.append(group);
    });
    list.replaceChildren(frag);
}

export { renderDomainGrid };

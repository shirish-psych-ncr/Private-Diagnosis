import { L, t } from './i18n.js';
import { state, CLINICAL_DATA } from './state.js';

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
        const ids = [...new Set(domain.questions.map(q => q.scaleId).filter(Boolean))];
        const choices = document.createElement('div');
        const forms = (domain.forms || []).filter(id =>
            CLINICAL_DATA.scales[id].ageGroups.includes(state.context.ageGroup));
        if (domain.defaultForm && !forms.length) {
            state.selectedDomains.delete(domain.id);
            state.scaleChoices.delete(domain.id);
            return;
        }
        if (domain.forms?.includes(state.scaleChoices.get(domain.id)) && !forms.includes(state.scaleChoices.get(domain.id))) {
            state.scaleChoices.delete(domain.id);
        }
        const hasChoices = ids.length + forms.length + Number(Boolean(domain.baseInstrument || domain.originalLabel)) > 1;
        if (hasChoices) {
            choices.className = 'scale-choice';
            choices.hidden = !cb.checked;
            const savedChoice = state.scaleChoices.get(domain.id);
            const defaultIds = forms.length ? [] : [...ids];
            if (domain.baseInstrument || domain.originalLabel) defaultIds.push('base');
            else defaultIds.push(...ids);
            const selected = new Set(Array.isArray(savedChoice)
                ? savedChoice
                : savedChoice === 'all' ? defaultIds
                    : savedChoice ? [savedChoice] : defaultIds);
            const choicesLabel = document.createElement('span');
            choicesLabel.textContent = state.lang === 'hi' ? 'प्रश्नावलियाँ चुनें' : 'Choose scales';
            choices.append(choicesLabel);
            const available = [];
            if (domain.baseInstrument || domain.originalLabel) available.push(['base', domain.baseInstrument || domain.originalLabel, null]);
            if (!domain.baseInstrument && !domain.originalLabel) for (const id of ids)
                available.push([id, t('form.' + id, L(CLINICAL_DATA.scales[id].name)), CLINICAL_DATA.scales[id]]);
            for (const id of forms) available.push([id, L(CLINICAL_DATA.scales[id].name), CLINICAL_DATA.scales[id]]);
            available.forEach(([id, name, scale]) => {
                const label = document.createElement('label');
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.value = id;
                input.checked = selected.has(id);
                input.addEventListener('change', () => {
                    if (input.checked) selected.add(id); else selected.delete(id);
                    if (selected.size) state.scaleChoices.set(domain.id, [...selected]);
                    else state.scaleChoices.delete(domain.id);
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

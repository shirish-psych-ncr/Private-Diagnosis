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
        const choices = document.createElement('label');
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
            choices.append(state.lang === 'hi' ? 'प्रश्नावली' : 'Questionnaire');
            const select = document.createElement('select');
            select.setAttribute('aria-label', topic + (state.lang === 'hi' ? ' — प्रश्नावली' : ' questionnaire'));
            const add = (value, name) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = name;
                select.append(option);
            };
            if (domain.originalLabel) add('original', domain.originalLabel);
            if (domain.baseInstrument) add('base', domain.baseInstrument);
            for (const id of ids) {
                const prefix = domain.baseInstrument ? domain.baseInstrument + ' + ' : '';
                add(id, prefix + t('form.' + id, L(CLINICAL_DATA.scales[id].name)));
            }
            if (ids.length > 1) add('all', state.lang === 'hi' ? 'सभी प्रश्नावलियाँ' : 'All questionnaires');
            for (const id of forms) add(id, L(CLINICAL_DATA.scales[id].name));
            select.value = state.scaleChoices.get(domain.id) || select.options[0].value;
            state.scaleChoices.set(domain.id, select.value);
            select.addEventListener('change', () => state.scaleChoices.set(domain.id, select.value));
            choices.append(select);
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

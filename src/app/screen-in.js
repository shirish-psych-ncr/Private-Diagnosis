import { L } from './i18n.js';
import { onAnswer } from './answers.js';
import { state, CLINICAL_DATA } from './state.js';

function optionsForQuestion(q) {
    if (q.scale) return q.scale;
    // Normalise the shared-scale key so small OCR/typing slips in the data
    // (e.g. "yes_no" vs "yesno") cannot silently drop a question's options.
    const norm = String(q.sharedScale || '').toLowerCase().replace(/[^a-z0-9]/g, '');
    if (norm && CLINICAL_DATA.sharedScales[norm]) return CLINICAL_DATA.sharedScales[norm];
    return [];
}

/** Compact Yes/No screen-in block for domains that always show their tables. */
function renderDomainScreenIns(container, domain) {
    const section = document.createElement('section');
    section.className = 'scale-section domain-screenin';
    const h = document.createElement('h3');
    h.className = 'scale-heading';
    h.textContent = L(domain.name);
    section.appendChild(h);
    if (domain.timeframe) {
        const tf = document.createElement('p');
        tf.className = 'scale-timeframe';
        tf.textContent = L(domain.timeframe);
        section.appendChild(tf);
    }
    if (domain.help) {
        const hp = document.createElement('p');
        hp.className = 'scale-directions';
        hp.textContent = L(domain.help);
        section.appendChild(hp);
    }
    domain.questions.filter(q => q.scaleId).forEach((q, idx) => {
        const fieldset = document.createElement('fieldset');
        fieldset.className = 'question-block' + (q.safety ? ' safety-item' : '');
        const legend = document.createElement('legend');
        legend.textContent = (idx + 1) + '. ' + L(q.text);
        legend.id = 'lbl-' + q.id;
        fieldset.appendChild(legend);
        optionsForQuestion(q).forEach(opt => {
            const key = domain.id + ':' + q.id;
            const input = document.createElement('input');
            input.type = 'radio';
            input.name = key;
            input.value = opt.v;
            input.id = key + '_' + opt.v;
            if (state.responses[key] === opt.v) input.checked = true;
            input.addEventListener('change', () => onAnswer(key, opt.v, q, domain));
            const label = document.createElement('label');
            label.htmlFor = input.id;
            label.textContent = L(opt.label);
            const wrap = document.createElement('div');
            wrap.className = 'radio-row';
            wrap.append(input, label);
            fieldset.appendChild(wrap);
        });
        section.appendChild(fieldset);
    });
    container.appendChild(section);
}

export { optionsForQuestion, renderDomainScreenIns };

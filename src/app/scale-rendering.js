import { L } from './i18n.js';
import { renderMatrix } from './matrix-rendering.js';
import { onAnswer } from './answers.js';
import { routeInstruments } from './routing.js';
import { optionsForQuestion, renderDomainScreenIns } from './screen-in.js';
import { state, CLINICAL_DATA } from './state.js';

function renderScales() {
    const container = document.getElementById('scale-container');
    container.replaceChildren();
    const deployed = routeInstruments();

    // Screen-in questions for the optional rating-table routes are rendered
    // first, as one compact block per domain. Those instruments are always
    // deployed once their domain is selected (gating a table behind its own
    // screen-in item would be circular — both live on the same page), so the
    // Yes/No gate needs its own home above the tables. Endorsing an item tells
    // the clinician which domain narrative to read the table within; it never
    // adds or removes a table.
    const seenScreenIns = new Set();
    deployed.forEach(({ domain, ratingTable }) => {
        if (!ratingTable || !domain.questions.some(q => q.scaleId)) return;
        if (seenScreenIns.has(domain.id)) return;
        seenScreenIns.add(domain.id);
        renderDomainScreenIns(container, domain);
    });

    deployed.forEach(({ domain, scaleId, instrumentLabel, ratingTable }) => {
        const scDef = ratingTable && CLINICAL_DATA.scales[scaleId];
        // The badge describes who completes the form (administeredBy), not
        // which scoring algorithm applies: keyed T/F screens such as FAC22-SR
        // are patient-completed even though they score like the IPDE/PDQ block.
        const isSelfReport = !!(scDef && scDef.administeredBy === 'self-report');
        const isPdScreen = !!(scDef && scDef.keyedScoring);
        const isSummed = !!(scDef && scDef.sumScoring);
        const section = document.createElement('section');
        section.className = 'scale-section' + (ratingTable
            ? (isSelfReport ? ' anger-rating-table' : ' clinician-rating-table')
            : '');
        const secKey = ratingTable ? domain.id + ':' + scaleId : domain.id;
        section.setAttribute('aria-labelledby', 'scale-h-' + secKey);

        const h = document.createElement('h3');
        h.id = 'scale-h-' + secKey;
        h.className = 'scale-heading';
        h.textContent = (scDef ? L(scDef.name) : L(domain.name) + (instrumentLabel ? ' — ' + instrumentLabel : ''));
        if (ratingTable) {
            const badge = document.createElement('span');
            badge.className = 'scale-admin-badge';
            badge.textContent = isPdScreen || isSummed
                ? (state.lang === 'hi' ? 'स्क्रीनिंग केवल — रोग-निर्णायक नहीं' : 'Screening only — not diagnostic')
                : (state.lang === 'hi' ? 'चिकित्सक-रेटित' : 'Clinician-rated');
            h.appendChild(document.createTextNode(' · '), badge);
        }
        section.appendChild(h);

        const help = document.createElement('p');
        help.id = 'domains-help';
        help.className = 'scale-timeframe';
        help.textContent = L(domain.timeframe);
        section.appendChild(help);

        if (scaleId && CLINICAL_DATA.scales[scaleId]) {
            const scale = CLINICAL_DATA.scales[scaleId];
            if (scale.directions) {
                const dir = document.createElement('p');
                dir.className = 'scale-directions';
                dir.textContent = L(scale.directions);
                section.appendChild(dir);
            }
            renderMatrix(section, scale, scaleId);
        } else {
            renderList(section, domain);
        }
        container.appendChild(section);
    });
}

/** Standard vertical radio list (PHQ-9 / GAD-7 / PCL-5 style items). */
function renderList(section, domain) {
    domain.questions.forEach((q, idx) => {
        const fieldset = document.createElement('fieldset');
        fieldset.className = 'question-block' + (q.safety ? ' safety-item' : '');
        const legend = document.createElement('legend');
        legend.textContent = (idx + 1) + '. ' + L(q.text);
        legend.id = 'lbl-' + q.id;
        fieldset.appendChild(legend);
        const opts = optionsForQuestion(q);
        opts.forEach(opt => {
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
}

/** Sticky-column matrix tables mirroring clinical standards (e.g., VADRS). */

export { renderScales, renderList };

import { L, t } from './i18n.js';
import { renderMatrix } from './matrix-rendering.js';
import { onAnswer } from './answers.js';
import { routeInstruments } from './routing.js';
import { optionsForQuestion, renderDomainScreenIns } from './screen-in.js';
import { state, CLINICAL_DATA, questionIsApplicable } from './state.js';

function renderScales() {
    const container = document.getElementById('scale-container');
    container.replaceChildren();
    const deployed = routeInstruments();
    const answered = new Set();
    const total = new Set();
    deployed.forEach(({ domain, scaleId, ratingTable }) => {
        const scale = (ratingTable || domain.directForm) && CLINICAL_DATA.scales[scaleId || domain.id];
        const questions = scale ? scale.parts.flatMap(part => part.questions)
            .filter(question => questionIsApplicable(question, scaleId || domain.id))
            : domain.questions.filter(question => !question.scaleId);
        questions.forEach(question => {
            if (question.nonScored || question.tickBox) return;
            const key = (scale ? (scaleId || domain.id) : domain.id) + ':' + question.id;
            total.add(key);
            if (state.responses[key] !== undefined) answered.add(key);
        });
        if (!ratingTable && !domain.directForm) domain.questions.filter(question => question.scaleId).forEach(question => {
            const key = domain.id + ':' + question.id;
            total.add(key);
            if (state.responses[key] !== undefined) answered.add(key);
        });
    });
    const estimate = document.getElementById('assessment-estimate');
    const progress = document.getElementById('assessment-progress');
    if (estimate) estimate.textContent = t('scales.timeEstimate').replace('{count}', String(total.size));
    if (progress) progress.textContent = t('scales.progress').replace('{answered}', String(answered.size)).replace('{total}', String(total.size));

    // Screen-in questions for explicitly selected rating-table routes are
    // rendered first, as one compact block per domain. The table is chosen by
    // the user; the Yes/No responses provide context and do not change scale
    // selection.
    const seenScreenIns = new Set();
    deployed.forEach(({ domain, ratingTable }) => {
        if (!ratingTable || !domain.questions.some(q => q.scaleId)) return;
        if (seenScreenIns.has(domain.id)) return;
        seenScreenIns.add(domain.id);
        renderDomainScreenIns(container, domain);
    });

    const renderGroups = new Set();
    deployed.forEach(({ domain, scaleId, instrumentLabel, ratingTable }) => {
        const scDef = (ratingTable || domain.directForm) && CLINICAL_DATA.scales[scaleId || domain.id];
        // The badge describes who completes the form (administeredBy), not
        // which scoring algorithm applies: keyed T/F screens such as FAC22-SR
        // are patient-completed even though they score like the IPDE/PDQ block.
        const isSelfReport = !!(scDef && scDef.administeredBy === 'self-report');
        const isClinicianForm = !!(scDef && scDef.administeredBy === 'clinician');
        if (ratingTable && !renderGroups.has(domain.id + ':' + scaleId)) {
            const form = CLINICAL_DATA.scales[scaleId];
            form.parts.forEach(part => {
                const key = JSON.stringify(part.options || form.matrixOptions || CLINICAL_DATA.sharedScales.nrsota);
                const groupKey = domain.id + ':' + key;
                if (renderGroups.has(groupKey)) return;
                const matching = deployed.filter(entry => entry.domain === domain && entry.ratingTable)
                    .flatMap(entry => CLINICAL_DATA.scales[entry.scaleId].parts
                        .filter(p => JSON.stringify(p.options || CLINICAL_DATA.scales[entry.scaleId].matrixOptions || CLINICAL_DATA.sharedScales.nrsota) === key)
                        .map(p => ({ scaleId: entry.scaleId, scale: CLINICAL_DATA.scales[entry.scaleId], part: p })));
                if (matching.length < 2) return;
                matching.forEach(m => renderGroups.add(domain.id + ':' + m.scaleId));
                const grouped = document.createElement('section');
                grouped.className = 'scale-section';
                const title = document.createElement('h3'); title.className = 'scale-heading';
                title.textContent = matching.map(m => L(m.scale.name) + ' (' + m.part.questions.length + ' items)').join(' + ');
                grouped.appendChild(title);
                const synthetic = { ...form, name: { en: title.textContent, hi: title.textContent }, parts: matching.map(m => ({ ...m.part, questions: m.part.questions.map(q => ({ ...q, __scaleId: m.scaleId, __scaleName: m.scale.name })) })) };
                renderMatrix(grouped, synthetic, scaleId);
                container.appendChild(grouped);
            });
            if (renderGroups.has(domain.id + ':' + scaleId)) return;
        }
        const section = document.createElement('section');
        section.className = 'scale-section' + (ratingTable
            ? (isSelfReport ? ' anger-rating-table' : ' clinician-rating-table')
            : (isClinicianForm ? ' clinician-rating-table' : ''));
        const secKey = ratingTable ? domain.id + ':' + scaleId : domain.id;
        section.setAttribute('aria-labelledby', 'scale-h-' + secKey);

        const h = document.createElement('h3');
        h.id = 'scale-h-' + secKey;
        h.className = 'scale-heading';
        const itemCount = scDef ? scDef.parts.flatMap(part => part.questions).length : null;
        h.textContent = (scDef ? L(scDef.name) + ' (' + itemCount + ' items)' : L(domain.name) + (instrumentLabel ? ' - ' + instrumentLabel : ''));
        if (ratingTable || scDef?.administeredBy) {
            const badge = document.createElement('span');
            badge.className = 'scale-admin-badge';
            const roles = {
                'self-report': { en: 'Self-report', hi: 'स्वयं भरें' },
                'self-or-clinician': { en: 'Self or clinician', hi: 'स्वयं या चिकित्सक भरें' },
                clinician: { en: 'Clinician-rated', hi: 'चिकित्सक भरें' },
                informant: { en: 'Observer report', hi: 'पर्यवेक्षक भरें' }
            };
            badge.textContent = L(roles[scDef.administeredBy]);
            h.appendChild(document.createTextNode(' · '), badge);
        }
        section.appendChild(h);

        if (domain.timeframe) {
            const help = document.createElement('p');
            help.className = 'scale-timeframe';
            help.textContent = L(domain.timeframe);
            section.appendChild(help);
        }
        if (domain.help) {
            const help = document.createElement('details');
            help.className = 'assessment-help';
            const summary = document.createElement('summary');
            summary.textContent = t('assessment.about');
            const text = document.createElement('p');
            text.textContent = L(domain.help);
            help.append(summary, text);
            section.appendChild(help);
        }
        for (const field of scDef?.contextFields || domain.contextFields || []) {
            const group = document.createElement('div');
            group.className = 'form-group';
            const label = document.createElement('label');
            const key = (scaleId || domain.id) + ':' + field.id;
            if (field.multiple) {
                const choices = document.createElement('fieldset');
                const legend = document.createElement('legend');
                legend.textContent = field.label;
                choices.append(legend);
                for (const option of field.options) {
                    const row = document.createElement('label');
                    const input = document.createElement('input');
                    input.type = 'checkbox';
                    input.checked = (state.formContext[key] || []).includes(option);
                    input.addEventListener('change', () => {
                        const selected = new Set(state.formContext[key] || []);
                        if (input.checked) selected.add(option);
                        else selected.delete(option);
                        state.formContext[key] = [...selected];
                    });
                    row.append(input, ' ' + option);
                    choices.append(row);
                }
                group.append(choices);
                section.append(group);
                continue;
            }
            label.htmlFor = key;
            label.textContent = L(field.label);
            const control = document.createElement(field.options ? 'select' : 'textarea');
            control.id = key;
            if (field.options) {
                control.add(new Option(t('context.select'), ''));
                for (const option of field.options) {
                    const value = typeof option === 'object' ? option.v : option;
                    const text = typeof option === 'object' ? L(option.label) : option;
                    control.add(new Option(text, value));
                }
            }
            control.value = state.formContext[key] || '';
            control.addEventListener('input', () => { state.formContext[key] = control.value; });
            group.append(label, control);
            section.appendChild(group);
        }

        if ((scaleId || domain.directForm) && CLINICAL_DATA.scales[scaleId || domain.id]) {
            const scale = CLINICAL_DATA.scales[scaleId || domain.id];
            if (scale.directions) {
                const dir = document.createElement('p');
                dir.className = 'scale-directions';
                dir.textContent = L(scale.directions);
                const details = document.createElement('details');
                details.className = 'assessment-directions';
                const summary = document.createElement('summary');
                summary.textContent = t('assessment.instructions');
                details.append(summary, dir);
                section.appendChild(details);
            }
            renderMatrix(section, scale, scaleId || domain.id);
        } else {
            renderList(section, domain);
        }
        container.appendChild(section);
    });
}

/** Standard vertical radio list (PHQ-9 / GAD-7 / PCL-5 style items). */
function renderList(section, domain) {
    domain.questions.filter(q => !q.scaleId).forEach((q, idx) => {
        if (q.section) {
            const heading = document.createElement('h4');
            heading.textContent = L(q.section);
            section.appendChild(heading);
        }
        const fieldset = document.createElement('fieldset');
        fieldset.className = 'question-block' + (q.safety ? ' safety-item' : '');
        const legend = document.createElement('legend');
        legend.textContent = (q.itemNumber ?? idx + 1) + '. ' + L(q.text);
        legend.id = 'lbl-' + q.id;
        fieldset.appendChild(legend);
        if (q.hint) {
            const hint = document.createElement('p');
            hint.textContent = q.hint;
            fieldset.appendChild(hint);
        }
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
        if (domain.durationOptions) {
            const key = domain.id + ':' + q.id;
            const label = document.createElement('label');
            label.textContent = 'How long has this reaction lasted? ';
            const select = document.createElement('select');
            select.add(new Option('Choose duration', ''));
            for (const duration of domain.durationOptions) select.add(new Option(duration, duration));
            select.value = state.formContext[key] || '';
            select.addEventListener('change', () => { state.formContext[key] = select.value; });
            label.append(select);
            const updateDuration = () => {
                label.hidden = !(state.responses[key] > 1);
                if (label.hidden) {
                    select.value = '';
                    delete state.formContext[key];
                }
            };
            fieldset.addEventListener('change', updateDuration);
            updateDuration();
            fieldset.append(label);
        }
        section.appendChild(fieldset);
    });
}

/** Sticky-column matrix tables mirroring clinical standards (e.g., VADRS). */

export { renderScales, renderList };

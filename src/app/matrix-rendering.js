import { L } from './i18n.js';
import { state, CLINICAL_DATA, questionIsApplicable } from './state.js';
import { renderAnchorLegend } from './anchor-legend.js';
import { onAnswer } from './answers.js';

function renderMatrix(section, scale, scaleId) {
    scaleId = scaleId || scale.id;
    const cols = scale.matrixOptions || CLINICAL_DATA.sharedScales.nrsota;
    if (!scale.parts.some(part => part.questions.some(question => question.scale)))
        renderAnchorLegend(section, scale, cols);
    scale.parts.forEach(part => {
        const partTitle = document.createElement('h4');
        partTitle.className = 'matrix-part-title';
        partTitle.textContent = L(part.name);
        section.appendChild(partTitle);

        if (part.clinicianRated) {
            const badge = document.createElement('p');
            badge.className = 'matrix-part-note';
            badge.textContent = state.lang === 'hi'
                ? 'चिकित्सक द्वारा पूर्ण धनात्मक स्क्रीन पश्चात् भरें — रोगी से नहीं पूछें।'
                : 'Completed by the clinician after a positive screen — not shown to the patient as a self-rating.';
            section.appendChild(badge);
        }
        if (part.linkedItem) {
            const link = document.createElement('p');
            link.className = 'matrix-part-note';
            link.textContent = state.lang === 'hi'
                ? 'आइटम ' + part.linkedItem + ' का अनुवर्ती भाग।'
                : 'Follow-up to item ' + part.linkedItem + '.';
            section.appendChild(link);
        }

        const isPerf = !!part.questions[0] && part.questions[0].isPerformance;
        // Per-part option sets: PDQ-4+ Section B checklists and the clinical-
        // significance follow-up are Yes/No, while the 99-item block uses True/False.
        const cols = isPerf ? scale.performanceOptions : (part.options || scale.matrixOptions);

        // Clinician-rated severity tables (e.g. MINI optional assessments A/B)
        // print the numeric score column first, then the verbal anchors, exactly
        // as on the paper form: "Symptom Name | Score 0..10".
        if (scale.ratingScale && !isPerf) {
            const anchorTh = document.createElement('p');
            anchorTh.className = 'scale-rating-anchors';
            anchorTh.textContent = L(scale.ratingScale.note || { en: '', hi: '' });
            section.appendChild(anchorTh);
        }

        const wrap = document.createElement('div');
        wrap.className = 'matrix-scroll';
        const table = document.createElement('table');
        table.className = 'matrix-table';
        table.setAttribute('aria-label', L(scale.name) + ' — ' + L(part.name));

        const thead = document.createElement('tr');
        const thItem = document.createElement('th');
        thItem.scope = 'col';
        thItem.className = 'sticky-col';
        thItem.textContent = state.lang === 'hi' ? 'लक्षण' : 'Item';
        thead.appendChild(thItem);
        const customRows = part.questions.some(q => q.scale);
        const activeQuestions = part.questions.filter(question => questionIsApplicable(question, scaleId));
        const maxColumns = Math.max(cols.length, ...activeQuestions.map(q => q.scale?.length || 0));
        const headerCols = customRows
            ? Array.from({ length: maxColumns }, (_, i) => ({ v: i, label: String(i) }))
            : cols;
        headerCols.forEach(c => {
            const th = document.createElement('th');
            th.scope = 'col';
            th.className = 'matrix-col-header';
            th.textContent = L(c.label);
            thead.appendChild(th);
        });
        table.createTHead().appendChild(thead);
        const body = table.createTBody();

        activeQuestions.forEach((q, idx) => {
            // Non-scored single tick-box note printed on the form (e.g. the GCLS
            // "already had genital surgery" box). Recorded as a clinical note; it
            // contributes to no total, so it is stored as 1/0 rather than a rating.
            if (q.tickBox) {
                const tr = document.createElement('tr');
                tr.className = 'tickbox-row';
                const rowHead = document.createElement('th');
                rowHead.scope = 'row';
                rowHead.className = 'sticky-col row-label';
                rowHead.textContent = (q.itemNumber != null ? q.itemNumber : '') + ' ' + L(q.text);
                rowHead.id = 'mrow-' + q.id;
                tr.appendChild(rowHead);
                const td = document.createElement('td');
                td.colSpan = cols.length;
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.id = 'tick-' + q.id;
                input.checked = state.responses[scaleId + ':' + q.id] === 1;
                input.setAttribute('aria-labelledby', 'mrow-' + q.id);
                input.addEventListener('change', () => onAnswer(scaleId + ':' + q.id,
                    input.checked ? 1 : 0, { id: q.id }, { id: scaleId }));
                const label = document.createElement('label');
                label.htmlFor = input.id;
                label.textContent = state.lang === 'hi' ? 'लागू होता है (अंकित नहीं)' : 'Applies (not scored)';
                td.append(input, label);
                tr.appendChild(td);
                body.appendChild(tr);
                return;
            }
            const tr = document.createElement('tr');
            if (q.safety) tr.className = 'safety-item';
            const rowHead = document.createElement('th');
            rowHead.scope = 'row';
            rowHead.className = 'sticky-col row-label';
            // Printed instrument item numbers (IPDE 1-59 / PDQ-4+ 1-99) take
            // precedence over the sequential index so answers can be transcribed
            // straight onto the paper scoring sheet.
            const shownNumber = q.itemNumber != null ? q.itemNumber : (idx + 1);
                rowHead.textContent = (q.__scaleName ? L(q.__scaleName) + ' · ' : '') + shownNumber + '. ' +
                L(q.itemName || q.text);
            if (q.reverseScored) {
                const rev = document.createElement('span');
                rev.className = 'criterion-note reverse-note';
                rev.textContent = state.lang === 'hi' ? ' (व्युक्रम-अंकित)' : ' (reverse-scored)';
                rowHead.appendChild(rev);
            }
            if (q.criterionNote) {
                const note = document.createElement('span');
                note.className = 'criterion-note';
                note.textContent = ' (' + q.criterionNote + ')';
                rowHead.appendChild(note);
            }
            // Printed instrument definitions (BISS item description) render as a
            // subordinate line so the rating row stays scannable.
            if (q.definition) {
                const dfn = document.createElement('span');
                dfn.className = 'item-definition';
                dfn.textContent = L(q.definition);
                rowHead.appendChild(dfn);
            }
            rowHead.id = 'mrow-' + q.id;
            tr.appendChild(rowHead);
            if (q.inputType === 'number' || q.inputType === 'time' || q.inputType === 'text') {
                const td = document.createElement('td');
                td.colSpan = headerCols.length;
                const input = document.createElement('input');
                input.type = q.inputType;
                if (q.inputType === 'number') {
                    input.min = String(q.min ?? 0);
                    if (q.max != null) input.max = String(q.max);
                    input.step = String(q.step ?? 1);
                    input.inputMode = 'decimal';
                }
                input.id = scaleId + ':' + q.id;
                const stored = state.responses[input.id];
                input.value = q.inputType === 'time' && Number.isFinite(stored)
                    ? String(Math.floor(stored / 60)).padStart(2, '0') + ':' + String(stored % 60).padStart(2, '0')
                    : stored ?? '';
                input.setAttribute('aria-labelledby', 'mrow-' + q.id);
                input.addEventListener('input', () => {
                    if (input.value === '') delete state.responses[input.id];
                    else if (q.inputType === 'text') onAnswer(input.id, input.value, { id: q.id }, { id: scaleId });
                    else {
                        const value = q.inputType === 'time'
                            ? Number(input.value.slice(0, 2)) * 60 + Number(input.value.slice(3, 5))
                            : Number(input.value);
                        onAnswer(input.id, value, { id: q.id }, { id: scaleId });
                    }
                });
                td.appendChild(input);
                tr.appendChild(td);
                body.appendChild(tr);
                return;
            }
            const rowCols = q.scale || cols;
            rowCols.forEach(c => {
                const td = document.createElement('td');
                td.className = 'matrix-cell';
                const responseScaleId = q.__scaleId || scaleId;
                const key = responseScaleId + ':' + q.id;
                const input = document.createElement('input');
                input.type = q.multipleChoice ? 'checkbox' : 'radio';
                input.name = q.multipleChoice ? key + '_' + c.v : key;
                input.value = c.v;
                input.id = key + '_' + c.v;
                const optionLabel = L(c.label) || String(c.v);
                input.setAttribute('aria-label', L(q.itemName || q.text) + ' — ' + optionLabel);
                if (q.multipleChoice) input.checked = (state.responses[key] || []).includes(c.v);
                else if (state.responses[key] === c.v) input.checked = true;
                input.addEventListener('change', () => {
                    if (q.multipleChoice) {
                        const selected = new Set(state.responses[key] || []);
                        if (input.checked) selected.add(c.v); else selected.delete(c.v);
                        if (selected.size) onAnswer(key, [...selected], { id: q.id }, { id: responseScaleId });
                        else {
                            delete state.responses[key];
                            onAnswer(key, [], { id: q.id }, { id: responseScaleId });
                        }
                    } else onAnswer(key, c.v,
                        { id: q.id, safety: !!q.safety, safetyMin: q.safetyMin }, { id: responseScaleId });
                });
                const label = document.createElement('label');
                label.className = 'matrix-answer';
                const caption = document.createElement('span');
                caption.textContent = optionLabel;
                label.append(input, caption);
                td.appendChild(label);
                tr.appendChild(td);
            });
            for (let i = rowCols.length; i < headerCols.length; i++) {
                const spacer = document.createElement('td');
                spacer.className = 'matrix-cell empty-option-cell';
                spacer.setAttribute('aria-hidden', 'true');
                tr.appendChild(spacer);
            }
            if (q.probes && q.probes.length) {
                const td = document.createElement('td');
                td.colSpan = cols.length;
                td.className = 'probe-cell';
                const ul = document.createElement('ul');
                ul.className = 'probe-list';
                q.probes.forEach(p => {
                    const li = document.createElement('li');
                    li.textContent = L(p);
                    ul.appendChild(li);
                });
                const cap = document.createElement('p');
                cap.className = 'probe-caption';
                cap.textContent = state.lang === 'hi'
                    ? 'पूछे जाने वाले प्रश्न:' : 'Ask:';
                td.append(cap, ul);
                tr.appendChild(td);
            }
            body.appendChild(tr);
        });
        wrap.appendChild(table);
        section.appendChild(wrap);
    });
}

export { renderMatrix, renderAnchorLegend, onAnswer };

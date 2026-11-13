import { scoreReading } from './score-reading.js';
import { t, L } from './i18n.js';
import { state } from './state.js';

/* ------------------------------------------------------------------ *
 * 9. RESULTS RENDERING — patient view (labels withheld) + clinician view
 * ------------------------------------------------------------------ */
function renderResults() {
    const r = state.results;
    const pv = document.getElementById('patient-view');
    pv.replaceChildren();

    const concernedAreas = r.instrumentResults
        .filter(x => x.aboveCutoff || /Positive/.test(x.severity))
        .map(x => x.name);
    const para = document.createElement('p');
    para.className = 'patient-summary';
    para.textContent = concernedAreas.length
        ? (state.lang === 'hi'
            ? 'कुछ उत्तरों पर आगे बात करना मददगार हो सकता है। अपनी मुलाकात में इन पर चर्चा करें।'
            : 'Some answers may need follow-up. Discuss them with your clinician.')
        : (state.lang === 'hi'
            ? 'मुलाकात में अपनी चिंताओं पर बात करें, भले ही उनके बारे में यहाँ कोई प्रश्न न पूछा गया हो।'
            : 'Bring up anything that concerns you at your visit, even if it was outside these questions.');
    pv.appendChild(para);

    if (r.safetyTriggered) {
        const alertBox = document.createElement('div');
        alertBox.className = 'patient-safety-note';
        alertBox.textContent = state.lang === 'hi'
            ? 'आपके कुछ उत्तरों ने त्वरित सहायता संसाधनों को दर्शाया है। कृपया आज ही किसी हेल्पलाइन पर संपर्क करें।'
            : 'Some of your responses highlighted immediate support resources. Please consider contacting a helpline today.';
        pv.appendChild(alertBox);
    }

    // Optional ICD-11 boundary references. They are never inferred from
    // questionnaire scores; clinician confirmation is required for selection.
    const codingList = document.getElementById('coding-options');
    if (codingList) {
        codingList.replaceChildren();
        const options = state.icd11BoundaryOptions || [];
        const chooser = document.getElementById('coding-reference');
        if (chooser) chooser.hidden = !options.length;
        options.forEach(option => {
            const li = document.createElement('li');
            const label = document.createElement('label');
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.name = 'icd11-boundary-code';
            input.setAttribute('aria-label', option.code + ' ' + option.label);
            input.value = option.code;
            input.checked = (state.selectedICD11Codes || new Set()).has(option.code);
            const updateSelection = () => {
                state.selectedICD11Codes ||= new Set();
                if (input.checked) state.selectedICD11Codes.add(option.code);
                else state.selectedICD11Codes.delete(option.code);
            };
            input.addEventListener('change', updateSelection);
            const title = document.createElement('span');
            title.className = 'coding-option-title';
            title.textContent = option.code + ' · ' + option.label;
            label.append(input, title);
            const context = document.createElement('p');
            context.className = 'coding-option-context';
            context.textContent = L(option.context) + ' ' + t('coding.related', 'Related references:') + ' ' + option.related.join(', ');
            li.append(label, context);
            codingList.appendChild(li);
        });
    }

    // Clinician detail (on-screen mirror of the PDF)
    const rc = document.getElementById('report-content');
    rc.replaceChildren();
    const tbl = document.createElement('table');
    tbl.className = 'clinician-table';
    const thead = document.createElement('thead');
    const hr = document.createElement('tr');
    [state.lang === 'hi' ? 'उपकरण' : 'Instrument', state.lang === 'hi' ? 'स्कोर' : 'Score', state.lang === 'hi' ? 'स्कोर का अर्थ' : 'How to read this score'].forEach(x => {
        const th = document.createElement('th'); th.textContent = x; hr.appendChild(th);
    });
    thead.appendChild(hr); tbl.appendChild(thead);
    const tbody = document.createElement('tbody');
    r.instrumentResults.forEach(x => {
        const tr = document.createElement('tr');
        [x.name, x.score, scoreReading(x)].forEach(v => {
            const td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    tbl.appendChild(tbody);
    rc.appendChild(tbl);
    r.instrumentResults.filter(x => x.sourceNote).forEach(result => {
        const note = document.createElement('p');
        note.className = 'rating-register-note';
        note.textContent = result.sourceNote;
        rc.appendChild(note);
    });

    // Clinician-rated rating tables (MINI optional assessments A & B)
    r.instrumentResults.filter(x => x.ratingRegister && x.ratingRegister.length).forEach(reg => {
        const h = document.createElement('h4');
        h.textContent = reg.name;
        rc.appendChild(h);
        const t = document.createElement('table');
        t.className = 'clinician-table rating-register';
        const trh = document.createElement('tr');
        [state.lang === 'hi' ? 'नाम' : 'Name', state.lang === 'hi' ? 'स्कोर (0-10)' : 'Score (0-10)'].forEach(x => {
            const th = document.createElement('th'); th.textContent = x; trh.appendChild(th);
        });
        t.appendChild(trh);
        reg.ratingRegister.forEach(row => {
            const tr = document.createElement('tr');
            const td1 = document.createElement('td'); td1.textContent = row.label;
            const td2 = document.createElement('td'); td2.textContent = row.value === undefined ? '—' : String(row.value);
            tr.append(td1, td2);
            t.appendChild(tr);
        });
        rc.appendChild(t);
        const note = document.createElement('p');
        note.className = 'rating-register-note';
        note.textContent = state.lang === 'hi'
            ? 'पैमाना: 0 अनुपस्थित, 1 हल्का, 3 मध्यम, 6 गंभीर, 10 अत्यधिक। प्रत्येक पंक्ति स्वतंत्र रूप से रेट की जाती है; कोई कुल अंक नहीं एवं यह रेटिंग किसी निदान-बक्से को नियंत्रित नहीं करता।'
            : 'Scale: 0 Not present, 1 Mild, 3 Moderate, 6 Severe, 10 Extreme. Each row is rated independently; no composite total is derived and these ratings do not gate any diagnostic box.';
        rc.appendChild(note);
    });

    r.instrumentResults.filter(x => x.eventRegister && x.eventRegister.length).forEach(reg => {
        const h = document.createElement('h4');
        h.textContent = reg.name;
        rc.appendChild(h);
        const t = document.createElement('table');
        t.className = 'clinician-table rating-register';
        const trh = document.createElement('tr');
        ['Event', 'Response recorded'].forEach(label => {
            const th = document.createElement('th'); th.textContent = label; trh.appendChild(th);
        });
        t.appendChild(trh);
        reg.eventRegister.forEach(row => {
            const tr = document.createElement('tr');
            const td1 = document.createElement('td'); td1.textContent = row.label;
            const td2 = document.createElement('td'); td2.textContent = row.value;
            tr.append(td1, td2); t.appendChild(tr);
        });
        rc.appendChild(t);
    });

    // Personality-screen registers (IPDE modules / PDQ-4+ profile)
    r.instrumentResults.filter(x => x.pdRegister && x.pdRegister.rows.length).forEach(reg => {
        const h = document.createElement('h4');
        h.textContent = reg.name + ' — ' + reg.pdRegister.heading;
        rc.appendChild(h);

        if (reg.pdRegister.validity) {
            const v = document.createElement('p');
            v.className = 'pd-validity-note' + (reg.pdRegister.validity.failed ? ' failed' : '');
            v.textContent = reg.pdRegister.validity.message;
            rc.appendChild(v);
        }

        const t = document.createElement('table');
        t.className = 'clinician-table rating-register pd-register';
        const trh = document.createElement('tr');
        [state.lang === 'hi' ? 'मॉड्यूल / पैमाना' : 'Module / scale',
         state.lang === 'hi' ? 'कुंजी-उत्तर' : 'Keyed items',
         state.lang === 'hi' ? 'स्थिति' : 'Status'].forEach(x => {
            const th = document.createElement('th'); th.textContent = x; trh.appendChild(th);
        });
        t.appendChild(trh);
        reg.pdRegister.rows.forEach(row => {
            const tr = document.createElement('tr');
            if (row.flagged) tr.className = 'flagged-row';
            const td1 = document.createElement('td'); td1.textContent = row.label;
            const td2 = document.createElement('td'); td2.textContent = row.value;
            const td3 = document.createElement('td');
            td3.textContent = (row.flagged ? '● ' : '') + (row.detail ||
                (state.lang === 'hi' ? 'चिह्नित नहीं' : 'Not flagged'));
            tr.append(td1, td2, td3);
            t.appendChild(tr);
        });
        rc.appendChild(t);
        const note = document.createElement('p');
        note.className = 'rating-register-note';
        note.textContent = reg.pdRegister.note;
        rc.appendChild(note);
    });

    const diffH = document.createElement('h4');
    diffH.textContent = state.lang === 'hi' ? 'विभेदक विचार (Differential Considerations)' : 'Differential Considerations';
    rc.appendChild(diffH);
    const ul = document.createElement('ul');
    ul.className = 'differential-list';
    if (!r.differentials.length) {
        const li = document.createElement('li');
        li.textContent = state.lang === 'hi' ? 'कोई ध्यान देने योग्य संकेत नहीं।' : 'No significant flags raised.';
        ul.appendChild(li);
    }
    r.differentials.forEach(d => {
        const li = document.createElement('li');
        li.textContent = 'Tier ' + d.tier + ' — ' + L(d.name) + ' (DSM-5-TR: ' + d.dsm5 + ' | ICD-11: ' + d.icd11 + ')';
        ul.appendChild(li);
    });
    rc.appendChild(ul);
}

export { renderResults };

import { L } from './i18n.js';
import { state } from './state.js';

/**
 * Verbal-anchor caption for a matrix table. The printed instruments define
 * each rating by an example of behaviour / proportion of time / severity /
 * functional impairment rather than by a bare number, so the on-screen table
 * has to carry that definition or the rater is left guessing what "3" means.
 * Scales whose options are plain frequency labels (VADRS, ASRS, PHQ-15, ...)
 * have no per-item anchor sets and render nothing here.
 */
function renderAnchorLegend(section, scale, cols) {
    const questions = [];
    (scale.parts || []).forEach(p => (p.questions || []).forEach(q => questions.push(q)));
    const withAnchors = questions.filter(q => q.anchors && q.anchors.length);
    if (!withAnchors.length) return;

    const details = document.createElement('details');
    details.className = 'anchor-legend';
    const sum = document.createElement('summary');
    sum.textContent = state.lang === 'hi'
        ? 'रेटिंग एंकर (प्रत्येक आइटम के लिए छपा अर्थ)'
        : 'Rating anchors (printed meaning for each item)';
    details.appendChild(sum);

    const note = document.createElement('p');
    note.className = 'anchor-legend-note';
    note.textContent = L(((scale.ratingScale || {}).note) || {
        en: 'Anchors are examples of behaviours, proportions of time and functional impairment that qualify for a score; they do not exclude similar experiences. When in doubt between two ratings, assign the higher score.',
        hi: 'एंकर उन व्यवहारों, समय-अनुपात एवं कार्य-क्षति के उदाहरण हैं जो एक अंक हेतु योग्य हैं; समान अनुभवों को नहीं छोड़ा जाता। दो रेटिंगों में संदेह हो तो उच्चतर अंक दें।'
    });
    details.appendChild(note);

    const table = document.createElement('table');
    table.className = 'anchor-table clinician-table';
    const head = document.createElement('tr');
    [state.lang === 'hi' ? 'आइटम' : 'Item'].concat(cols.map(c => L(c.label))).forEach(x => {
        const th = document.createElement('th'); th.textContent = x; head.appendChild(th);
    });
    table.appendChild(head);
    withAnchors.forEach(q => {
        const tr = document.createElement('tr');
        const th = document.createElement('th');
        th.scope = 'row';
        th.className = 'row-label';
        th.textContent = (q.itemNumber != null ? q.itemNumber + '. ' : '') +
            L(q.itemName || q.text);
        tr.appendChild(th);
        cols.forEach((c, i) => {
            const td = document.createElement('td');
            const a = q.anchors[i];
            td.textContent = a ? L(a) : '—';
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    details.appendChild(table);
    section.appendChild(details);
}

export { renderAnchorLegend };

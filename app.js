/* ============================================================================
 * EPCSS — Ephemeral Pre-Consultation Clinical Screening System
 * Zero-backend, zero-persistence client-side engine.
 *
 * Architecture notes (see WHITEPAPER.md):
 *   1. All clinical logic (domains, instruments, disorder tiers, i18n dictionary)
 *      lives in data.json. Clinicians can edit it without touching this code.
 *   2. State is volatile RAM only. localStorage / sessionStorage / cookies are
 *      strictly prohibited for clinical data (Ephemeral State Model).
 *   3. Adaptive two-stage routing: Stage A symptom clustering -> Stage B
 *      instrument deployment (age-aware: VADRS pediatric vs ASRS-v1.1 adult).
 *   4. Safety overrides: items flagged `safety:true` halt the workflow and open
 *      a full-screen crisis-routing modal.
 *   5. Language switching re-renders text nodes only; answers and position are
 *      never disturbed.
 * ==========================================================================*/

(function () {
    'use strict';

    /* ------------------------------------------------------------------ *
     * 1. EPHEMERAL STATE — lives only in volatile memory. Never persisted.
     * ------------------------------------------------------------------ */
    const state = {
        lang: 'en',
        stage: 0,
        consent: false,
        context: { ageGroup: '', reason: '', medications: '', priorDiagnoses: '' },
        selectedDomains: new Set(),
        responses: {},            // key: `${domainId}:${questionId}` or `vadrs:${id}` -> number
        safetyFlags: [],          // [{ questionId, domainId }]
        results: null             // computed at finish
    };

    let CLINICAL_DATA = null;     // populated from data.json
    let I18N = null;              // populated from data.json

    /* ------------------------------------------------------------------ *
     * 2. BOOTSTRAP — load clinical logic JSON, then render.
     * ------------------------------------------------------------------ */
    async function boot() {
        try {
            const res = await fetch('data.json', { cache: 'no-store' });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const payload = await res.json();
            CLINICAL_DATA = payload.clinical || payload;
            I18N = payload.i18n || {};
        } catch (err) {
            // file:// fallback: some browsers block fetch on local files.
            showError(err);
            return;
        }
        bindStaticUI();
        applyLanguage(state.lang);
        renderDomainGrid();
        // Only the consent stage is revealed on load. Stages 1-4 remain hidden
        // until their Continue controls validate and reveal them in sequence.
        revealStage(0);
    }

    function showError(err) {
        // DOM-safe insertion (no innerHTML) to honour the strict CSP posture.
        const div = document.createElement('div');
        div.className = 'load-error';
        div.setAttribute('role', 'alert');
        div.textContent = (state.lang === 'hi')
            ? 'डेटा लोड नहीं हो सका। कृपया इस पृष्ठ को HTTP(S) सर्वर (जैसे GitHub Pages) पर चलाएँ।'
            : 'Could not load clinical data (data.json). Please serve this page over HTTP(S), e.g. via GitHub Pages.';
        document.getElementById('stage-0').after(div);
        console.error('EPCSS bootstrap failure:', err);
    }

    /* ------------------------------------------------------------------ *
     * 3. i18n HELPERS
     * ------------------------------------------------------------------ */
    function t(key) {
        const dict = I18N[state.lang] || I18N.en || {};
        return dict[key] !== undefined ? dict[key] : (I18N.en && I18N.en[key]) || key;
    }

    /** Resolve a bilingual {en,hi} object or plain string. */
    function L(obj) {
        if (obj == null) return '';
        if (typeof obj === 'string') return obj;
        return obj[state.lang] || obj.en || '';
    }

    function applyLanguage(lang) {
        state.lang = lang;
        document.documentElement.lang = lang === 'hi' ? 'hi' : 'en';
        document.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = t(el.getAttribute('data-i18n'));
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
        });
        // Re-render dynamic content in the new language WITHOUT touching inputs' values.
        renderDomainGrid();
        if (state.stage === 3) renderScales();
        if (state.stage === 4 && state.results) renderResults();
        updateLangButtons();
    }

    function updateLangButtons() {
        const en = document.getElementById('lang-en');
        const hi = document.getElementById('lang-hi');
        en.classList.toggle('active', state.lang === 'en');
        hi.classList.toggle('active', state.lang === 'hi');
        en.setAttribute('aria-pressed', String(state.lang === 'en'));
        hi.setAttribute('aria-pressed', String(state.lang === 'hi'));
    }

    /* ------------------------------------------------------------------ *
     * 4. STAGE NAVIGATION
     * ------------------------------------------------------------------ */
    /**
     * Reveal a stage that the user has already legitimately reached. This is
     * the ONLY function allowed to add the `.active` class to a stage section;
     * it is called exclusively from the Continue/Finish handlers (and boot),
     * so later states can never load before their prerequisite is completed.
     */
    function revealStage(n) {
        state.stage = n;
        document.querySelectorAll('.stage').forEach((sec, i) => {
            sec.classList.toggle('active', i === n);
        });
        document.querySelectorAll('.progress-step').forEach((step, i) => {
            step.classList.toggle('completed', i < n);
            step.classList.toggle('active', i === n);
        });
        // Every newly revealed state starts at the top of the page. The next
        // statement runs synchronously while the new stage is still display:none
        // (the stylesheet repaints only after this script yields), so scrollTo
        // cannot be undone by the fadeIn animation's initial translateY(10px).
        window.scrollTo(0, 0);
        const heading = document.querySelector('#stage-' + n + ' h2');
        if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true }); }
    }

    /**
     * Gatekeeper for every "Continue" control. Each stage validates its own
     * required input via `validate()`; on failure an inline alert is shown and
     * focus moves to it — the next state is NOT loaded. On success `onPass`
     * renders the next state's content and reveals it (scrolling to top).
     */
    function continueTo(validate, onPass) {
        if (!validate()) {
            const alertEl = validate.alertEl || null;
            if (alertEl && typeof alertEl.focus === 'function') alertEl.focus();
            return;
        }
        onPass();
    }

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

    /* ------------------------------------------------------------------ *
     * 6. STAGE 3 — ADAPTIVE INSTRUMENT DEPLOYMENT (routing engine)
     * ------------------------------------------------------------------ */

    /**
     * Given the selected domains and the declared age group, decide which
     * instruments to deploy. `auto:adhd` routes VADRS for pediatric/adolescent
     * and ASRS-v1.1 (the domain's own item set) for adults, per the whitepaper.
     */
    /* Routes whose optional instruments are always shown once the domain is picked. */
    const OPTIONAL_TABLE_ROUTES = ['auto:minioptional', 'auto:pdscreen', 'auto:angertable', 'auto:dissociationtable', 'auto:somatoptable', 'auto:genderdistress', 'auto:bipolartable'];

    function routeInstruments() {
        const deployed = [];
        CLINICAL_DATA.domains.forEach(domain => {
            if (!state.selectedDomains.has(domain.id)) return;
            const instName = domain.instrument || null;
            if (instName === 'auto:adhd') {
                const peds = ['pediatric', 'adolescent'].includes(state.context.ageGroup);
                deployed.push({
                    domain,
                    scaleId: peds ? 'vadrs' : null,
                    instrumentLabel: peds ? 'VADRS' : 'ASRS-v1.1'
                });
            } else if (OPTIONAL_TABLE_ROUTES.includes(instName)) {
                if (instName === 'auto:bipolartable' && domain.baseInstrument) {
                    // The mood domain keeps its own PHQ-9 item set as the primary
                    // instrument; the BISS rides along underneath as an optional
                    // clinician-rated table.
                    deployed.push({ domain, scaleId: null, instrumentLabel: domain.baseInstrument });
                }
                // MINI 7.0.2 additional optional interview assessments (pp. 36-37):
                // A - Cross-Cutting Measures (Severity of Symptom) and
                // B - Disability / Functional Impairment. Both are clinician-rated
                // 0-10 tables reached through the domain's own screen-in items.
                //
                // auto:pdscreen is the personality-disorder screening block: endorsing a
                // screen-in item deploys the keyed True/False instrument attached to it
                // (IPDE ICD-10 module screening questionnaire / PDQ-4+). Neither screen
                // is diagnostic — they flag which F60/DSM cluster needs the full interview.
                //
                // auto:angertable deploys the summed anger instruments (STAXI-C/A,
                // Clinical Anger Scale); auto:dissociationtable deploys the dissociative-
                // experience self-report instruments (MID-60 short form, DES-II), each
                // attached to one screen-in item of the `dissociation` domain.
                //
                // auto:genderdistress deploys the Gender Congruence and Life Satisfaction
                // Scale (GCLS) for the `gender` domain - a reverse-keyed, subscale-scored
                // self-report of gender-related distress and life satisfaction.
                //
                // auto:bipolartable deploys the Bipolar Inventory of Signs and Symptoms
                // Scale (BISS, Bowden) on the `mood` domain: 44 clinician-rated items
                // scored 0-4 over the most recent 7 days from self-report plus family
                // and interview observation. The mood domain keeps its own PHQ-9 item
                // scoring, so the BISS rides along as an optional table attached to the
                // domain's two bipolar screen-in items (mood_biss_1/2) rather than
                // replacing the domain instrument.
                // Screen-in questions for these routes are rendered above the
                // instruments they relate to, so they stay answerable (see
                // renderDomainScreenIns).
                domain.questions.forEach(q => {
                    if (!q.scaleId) return;
                    // Optional rating tables (MINI A/B, IPDE, PDQ-4+, anger,
                    // dissociation, somatic instruments) are deployed as soon as their
                    // domain is selected. Gating them behind their own screen-in item
                    // would be a dead end: the screen-in question and the instrument it
                    // unlocks live on the same page, so under an endorse-first rule the
                    // table could never appear and the screen-in could never be endorsed.
                    // The screen-in answers still drive the domain-level flag in
                    // computeResults(); endorsing one records clinical intent and never
                    // adds or removes a table.
                    deployed.push({ domain, scaleId: q.scaleId, instrumentLabel: null, ratingTable: true });
                });
            } else {
                deployed.push({ domain, scaleId: null, instrumentLabel: instName });
            }
        });
        return deployed;
    }

    function optionsForQuestion(q) {
        if (q.scale) return q.scale;
        if (q.sharedScale) return CLINICAL_DATA.sharedScales[q.sharedScale];
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
        const tf = document.createElement('p');
        tf.className = 'scale-timeframe';
        tf.textContent = L(domain.timeframe);
        section.appendChild(tf);
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

    function renderMatrix(section, scale, scaleId) {
        scaleId = scaleId || scale.id;
        const cols = scale.matrixOptions || CLINICAL_DATA.sharedScales.nrsota;
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
            table.setAttribute('role', 'grid');
            table.setAttribute('aria-label', L(scale.name) + ' — ' + L(part.name));

            const thead = document.createElement('tr');
            const thItem = document.createElement('th');
            thItem.scope = 'col';
            thItem.className = 'sticky-col';
            thItem.textContent = state.lang === 'hi' ? 'लक्षण' : 'Item';
            thead.appendChild(thItem);
            cols.forEach(c => {
                const th = document.createElement('th');
                th.scope = 'col';
                th.className = 'matrix-col-header';
                th.textContent = L(c.label);
                thead.appendChild(th);
            });
            table.appendChild(thead);

            part.questions.forEach((q, idx) => {
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
                    table.appendChild(tr);
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
                rowHead.textContent = shownNumber + '. ' +
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
                cols.forEach(c => {
                    const td = document.createElement('td');
                    td.className = 'matrix-cell';
                    const key = scaleId + ':' + q.id;
                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.name = key;
                    input.value = c.v;
                    input.id = key + '_' + c.v;
                    input.setAttribute('aria-labelledby', 'mrow-' + q.id);
                    input.setAttribute('aria-label', L(q.text) + ': ' + L(c.label));
                    if (state.responses[key] === c.v) input.checked = true;
                    input.addEventListener('change', () => onAnswer(key, c.v, { id: q.id, safety: !!q.safety }, { id: scaleId }));
                    td.appendChild(input);
                    tr.appendChild(td);
                });
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
                table.appendChild(tr);
            });
            wrap.appendChild(table);
            section.appendChild(wrap);
        });
    }

    /** Central answer handler with safety override check. */
    function onAnswer(key, value, question, domain) {
        state.responses[key] = value;
        document.getElementById('scales-error').classList.add('hidden');
        // Safety override: high-risk endorsement halts workflow -> crisis modal.
        if (question.safety && Number(value) > 0) {
            state.safetyFlags.push({ key, domainId: domain.id });
            openSafetyModal();
        }
    }

    /* ------------------------------------------------------------------ *
     * 7a. Personality-disorder screens (IPDE / PDQ-4+) — shared helpers   *
     * ------------------------------------------------------------------ */

    /** Screen-in questions whose endorsement deploys a keyed T/F instrument. */
    function deployedPdScreens(domain) {
        return deployedScreenInstruments(domain, s => !!s.keyedScoring);
    }

    /**
     * Generic screen-in deployment: returns the scales attached to a domain's
     * yes/no screen items that the respondent endorsed. `accept` selects which
     * kind of instrument qualifies (keyed personality screens, summed anger
     * instruments, ...).
     */
    function deployedScreenInstruments(domain, accept) {
        const out = [];
        if (!domain || !domain.questions) return out;
        // Tables are shown as soon as the domain is selected (see routeInstruments),
        // so scoring must follow the same rule — otherwise an instrument can be on
        // screen yet silently skipped because its screen-in item was answered "No".
        // Optional rating-table routes therefore score every attached instrument;
        // other routes keep the original endorse-first behaviour.
        const alwaysDeployed = OPTIONAL_TABLE_ROUTES.includes(domain.instrument) &&
            // A hybrid route (mood / auto:bipolartable) still sums its own primary
            // item set, so the usual endorse-first rule keeps applying there.
            !(domain.instrument === 'auto:bipolartable' && domain.baseInstrument);
        domain.questions.forEach(q => {
            if (!q.scaleId) return;
            if (!alwaysDeployed && (state.responses[domain.id + ':' + q.id] || 0) < 1) return;
            const s = CLINICAL_DATA.scales[q.scaleId];
            if (s && accept(s)) out.push({ question: q, scale: s });
        });
        return out;
    }

    /**
     * Keyed-answer count for one IPDE module or PDQ-4+ scale.
     * IPDE items carry `keyedAnswer` ('T' counts when answered True, 'F' when
     * answered False); PDQ-4+ scales list plain item numbers counted when True.
     */
    function keyedCount(scaleId, qids, keyed) {
        let n = 0;
        qids.forEach(id => {
            const v = state.responses[scaleId + ':' + id];
            if (v === undefined) return;
            if (keyed) { if ((keyed[id] === 'T') === (v === 1)) n++; }
            else if (v === 1) n++;
        });
        return n;
    }

    /** Checklists rendered as Yes/No columns inside a PDQ-4+ deployment. */
    function pdqChecklistParts(scale) {
        return (scale.parts || []).filter(p => p.options && !p.clinicianRated);
    }

    /** Number of keyed items endorsed on one IPDE module (part). */
    function ipdeKeyedHits(part, scaleId) {
        const hits = [];
        part.questions.forEach(q => {
            const v = state.responses[scaleId + ':' + q.id];
            if (v === undefined) return;
            if ((q.keyedAnswer === 'T') === (v === 1)) hits.push(q.itemNumber || q.id);
        });
        return hits;
    }

    /**
     * IPDE ICD-10 module screening questionnaire scoring.
     * Official standard: >=3 keyed items per disorder fails the screen. The
     * authors explicitly permit a lower standard, which this app applies
     * (>=1 keyed item) so that no cluster needing the full interview is missed.
     * No dimensional score is produced and nothing here is diagnostic.
     */
    function scoreIpde(scale, addFlag) {
        const sc = scale.scoring || {};
        const official = sc.failThreshold != null ? sc.failThreshold : 3;
        const applied = sc.positiveThreshold != null ? sc.positiveThreshold : 1;
        const modules = [];
        let flaggedTotal = 0, anyKeyed = 0;
        scale.parts.forEach(part => {
            const hits = ipdeKeyedHits(part, scale.id);
            anyKeyed += hits.length;
            const failed = hits.length >= official;
            const flag = hits.length >= applied;
            if (flag) {
                flaggedTotal++;
                (part.disorders || []).forEach(d => addFlag(d, 'IPDE screen'));
            }
            modules.push({
                id: part.id,
                code: part.icd10Module,
                name: L(part.name),
                disorderName: L(part.disorderName),
                keyed: hits.length,
                totalItems: part.questions.length,
                failedOfficial: failed,
                flagged: flag,
                disorders: part.disorders || []
            });
        });
        const hi = state.lang === 'hi';
        return {
            name: L(scale.name),
            score: anyKeyed + ' keyed item(s) · ' + flaggedTotal + '/' + scale.parts.length +
                ' ' + (hi ? 'मॉड्यूल चिह्नित' : 'modules flagged'),
            severity: flaggedTotal
                ? (hi ? 'स्क्रीन असफल — पूर्ण IPDE साक्षात्कार आवश्यक' : 'Screen failed — full IPDE interview indicated')
                : (hi ? 'चिह्नित नहीं' : 'No module flagged'),
            aboveCutoff: flaggedTotal > 0,
            notDiagnostic: true,
            disorders: [],
            pdRegister: {
                kind: 'ipde',
                heading: hi ? 'IPDE स्क्रीनिंग — मॉड्यूल अनुसार कुंजी-उत्तर' : 'IPDE screen — keyed items by ICD-10 module',
                note: L(sc.appStandard || sc.note || { en: '', hi: '' }),
                rows: modules.map(m => ({
                    label: m.name + ' — ' + m.disorderName,
                    value: m.keyed + '/' + m.totalItems,
                    flagged: m.flagged,
                    detail: m.failedOfficial
                        ? (hi ? 'औपचारिक मानदंड (≥3) असफल' : 'Meets official ≥3 fail criterion')
                        : (m.flagged ? (hi ? 'निम्नतर मानदंड से चिह्नित' : 'Flagged under the app\u2019s lower standard') : '')
                }))
            }
        };
    }

    /**
     * PDQ-4+ scoring: validity check first, then True-count per scale against its
     * threshold, Section B gates for Borderline (item 98) and Antisocial (item 99),
     * and finally the mandatory clinical-significance criteria A-E, which must ALL
     * be met before a flagged personality disorder enters the differential list.
     */
    function scorePdq4(scale, addFlag) {
        const sc = scale.scoring || {};
        const hi = state.lang === 'hi';
        const ans = id => state.responses[scale.id + ':' + id];

        // 1. Validity / infrequency items (pathological response = True)
        const validityHits = (scale.validity ? scale.validity.items : [])
            .filter(it => ans(it.id) === 1)
            .map(it => it.id.replace('pdq_', ''));
        const profileInvalid = validityHits.length > 0;

        // 2. Section B checklists
        const sectionB = sc.sectionB || {};
        const gateCount = partId => {
            const part = (scale.parts || []).find(p => p.id === partId);
            if (!part) return 0;
            return part.questions.filter(q => ans(q.id) === 1).length;
        };
        const gatesMet = {};
        Object.keys(sectionB).forEach(partId => {
            const g = sectionB[partId];
            gatesMet[g.gateScale] = gateCount(partId) >= g.minimum;
        });

        // 3. Clinical significance criteria A-E (clinician-rated follow-up)
        const csPart = (scale.parts || []).find(p => p.clinicianRated);
        const csAnswers = csPart ? csPart.questions.map(q => ans(q.id)) : [];
        const csComplete = csAnswers.length > 0 && csAnswers.every(v => v !== undefined);
        const csMet = csComplete && csAnswers.every(v => v === 1);

        // 4. Per-scale True counts vs thresholds
        const rows = [];
        let flagged = 0;
        (scale.scales || []).forEach(s => {
            const n = s.items.filter(num => ans('pdq_' + num) === 1).length;
            const reached = n >= s.threshold;
            const needsB = !!s.requiresSectionB;
            const gateOk = !needsB || gatesMet[s.slug] === true;
            const positive = reached && gateOk && !profileInvalid;
            const significant = positive && csMet;
            if (significant) { flagged++; (s.disorders || []).forEach(d => addFlag(d, 'PDQ-4+')); }
            rows.push({
                label: L(s.name) + ' (' + (s.profileColumn || s.slug) + ')',
                value: n + '/' + s.items.length,
                flagged: positive,
                detail: [
                    reached ? '' : (hi ? 'threshold ' + s.threshold + ' अपूर्ण' : 'below threshold ' + s.threshold),
                    needsB ? (gateOk ? (hi ? 'खंड-B पूर्त' : 'Section B met') : (hi ? 'खंड-B अपूर्ण' : 'Section B not met')) : '',
                    positive && !csMet ? (hi ? 'A-E नैदानिक महत्व अपूर्ण' : 'criteria A–E not all met') : '',
                    significant ? (hi ? 'नैदानिक दृष्ट्या महत्वपूर्ण' : 'clinically significant') : ''
                ].filter(Boolean).join(' · ')
            });
        });

        return {
            name: L(scale.name),
            score: flagged + '/' + rows.length + ' ' + (hi ? 'पैमाने धनात्मक' : 'scales flagged'),
            severity: profileInvalid
                ? (hi ? 'प्रोफ़ाइल अमान्य — सावधानीपूर्वक व्याख्या' : 'Validity flag — interpret with extreme caution')
                : (flagged
                    ? (hi ? 'स्क्रीन धनात्मक — संरचित साक्षात्कार आवश्यक' : 'Positive screen — structured interview indicated')
                    : (hi ? 'कोई पैमाना धनात्मक नहीं' : 'No scale at threshold')),
            aboveCutoff: flagged > 0,
            notDiagnostic: true,
            disorders: [],
            pdRegister: {
                kind: 'pdq4',
                heading: hi ? 'PDQ-4+ प्रोफ़ाइल (12 पैमाने)' : 'PDQ-4+ profile (12 scales)',
                note: L(sc.notDiagnosticNote || { en: '', hi: '' }) + ' ' + L(sc.clinicalSignificance || { en: '', hi: '' }),
                validity: {
                    message: profileInvalid
                        ? (hi ? 'वैधता आइटम ' + validityHits.join(', ') + ' सत्य — प्रोफ़ाइल अमान्य मानें।'
                              : 'Validity item(s) ' + validityHits.join(', ') + ' answered True — consider the profile invalid.')
                        : (hi ? 'वैधता आइटम (64, 76) मिथ्या — प्रतिविमर्श विश्वसनीय।' : 'Validity items (64, 76) False — responding appears valid.'),
                    failed: profileInvalid
                },
                rows: rows
            }
        };
    }

    /**
     * STAXI-CA scoring: raw sums for State Anger (items 1-15), Trait Anger
     * (16-24) and each Part-3 subscale, plus the composite Expression score
     * (Anger-In + Anger-Out + Control-Out reversed). The instrument is purely
     * dimensional - there is no caseness cutoff - so nothing here raises a
     * differential flag; the flagged-disorder list for the anger domain comes
     * from the screen-in items themselves.
     */
    function scoreStaxi(scale) {
        const hi = state.lang === 'hi';
        const ans = id => state.responses[scale.id + ':' + id];
        const slugs = Object.keys(scale.subscales);
        // Item-level totals come from the printed parts, not from the subscale
        // lists: item 25 is scored on Part 3 but belongs to no expression
        // subscale, so counting subscale items would over-report completion.
        const allIds = [];
        (scale.parts || []).forEach(part => part.questions.forEach(q => allIds.push(q.id)));
        const answeredOf = ids => ids.filter(id => ans(id) !== undefined);
        const sumOf = ids => answeredOf(ids).reduce((t, id) => t + Number(ans(id)), 0);
        const rows = [];
        slugs.forEach(slug => {
            const sub = scale.subscales[slug];
            const ids = sub.items.map(n => 'staxi_' + n);
            const got = answeredOf(ids);
            const raw = sumOf(ids);
            const lo = ids.length * (scale.scoring.scaleMin || 1);
            const up = ids.length * (scale.scoring.scaleMax || 4);
            rows.push({
                label: L(sub.name),
                value: got.length === ids.length ? (raw + '/' + up) : (raw + ' (' + got.length + '/' + ids.length + ')'),
                flagged: false,
                detail: (hi ? 'सीमा ' : 'range ') + lo + '-' + up +
                    (slug === 'control' ? (hi ? ' · उच्च = बेहतर नियंत्रण' : ' · higher = better control') : '') +
                    (slug === 'denial' ? (hi ? ' · व्याख्या सावधानी से करें' : ' · interpret with caution') : '')
            });
        });
        // Composite Expression = Anger-In + Anger-Out + reversed Anger Control,
        // where each control item is reversed as (scaleMax + scaleMin - response).
        const mn = scale.scoring.scaleMin || 1, mx = scale.scoring.scaleMax || 4;
        const completePart = slug => scale.subscales[slug].items
            .every(n => ans('staxi_' + n) !== undefined);
        const controlReversed = scale.subscales.control.items
            .map(n => ans('staxi_' + n))
            .filter(v => v !== undefined)
            .reduce((t, v) => t + (mx + mn - Number(v)), 0);
        const exprComplete = ['in', 'out', 'control'].every(completePart);
        const expr = exprComplete
            ? (sumOf(scale.subscales.in.items.map(n => 'staxi_' + n)) +
               sumOf(scale.subscales.out.items.map(n => 'staxi_' + n)) + controlReversed)
            : null;
        const answered = answeredOf(allIds).length;
        const complete = answered === allIds.length;
        if (exprComplete) {
            rows.push({
                label: hi ? 'क्रोध-अभिव्यक्ति संयुक्त स्कोर (AES)' : 'Anger Expression Summary (AES)',
                value: String(expr),
                flagged: false,
                detail: hi
                    ? 'Anger-In + Anger-Out + (5 − प्रत्येक Control आइटम)'
                    : 'Anger-In + Anger-Out + reversed Anger Control (per item: max+min − response)'
            });
        }
        return {
            name: L(scale.name),
            score: answered + '/' + allIds.length + ' ' + (hi ? 'आइटम उत्तरित' : 'items answered'),
            severity: complete
                ? (hi ? 'पूर्ण — आयामगत स्कोर (रोग-निर्णायक नहीं)' : 'Complete — dimensional scores (not diagnostic)')
                : (hi ? 'अपूर्ण' : 'Incomplete'),
            aboveCutoff: false,
            notDiagnostic: true,
            answered, total: allIds.length,
            disorders: [],
            pdRegister: {
                kind: 'staxi',
                heading: hi ? 'STAXi-CA उप-पैमाना प्रोफ़ाइल' : 'STAXI-CA subscale profile',
                note: L((scale.scoring.rule || {}).en ? scale.scoring.rule : { en: '', hi: '' }),
                rows: rows
            }
        };
    }

    /**
     * Clinical Anger Scale scoring: sum of the 21 cluster choices (A=0..D=3,
     * range 0-63) mapped onto the printed interpretive ranges. Severity band
     * only - the CAS is dimensional and does not itself raise a disorder flag.
     */
    function scoreCas(scale) {
        const hi = state.lang === 'hi';
        const ids = [];
        (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
        const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
        const sum = got.reduce((t, id) => t + Number(state.responses[scale.id + ':' + id]), 0);
        const complete = got.length === ids.length;
        // Printed interpretive ranges are inclusive of their lower bound:
        // 0-13 minimal · 14-19 mild · 20-28 moderate · 29-63 severe.
        const bandIdx = (() => {
            const bands = scale.bands || [];
            for (let i = 0; i < bands.length; i++) if (sum <= bands[i].max) return i;
            return bands.length - 1;
        })();
        const maxTotal = ((scale.ratingScale || {}).max || 3) * ids.length;
        return {
            name: L(scale.name),
            score: sum + '/' + maxTotal + ' (' + got.length + '/' + ids.length + ')',
            severity: (bandLabel(sum, scale.bands) || (hi ? 'अपूर्ण' : 'Incomplete')) +
                (hi ? ' · रोग-निर्णायक नहीं' : ' · not diagnostic'),
            aboveCutoff: complete && bandIdx >= 2,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: []
        };
    }

    /* ------------------------------------------------------------------ *
     * 7c. Somatic-symptom instruments (FAC22-SR / PHQ-15)                *
     * ------------------------------------------------------------------ */

    /**
     * Count keyed answers across an instrument's item parts.
     *  - keyed T/F instruments (IPDE, FAC22-SR): each question carries
     *    `keyedAnswer` 'T' (counts when answered True) or 'F' (counts when
     *    answered False);
     *  - plain True-count instruments (PDQ-4+ scales): any answer of 1 counts.
     * `skip` lets a caller exclude follow-up/clinician-rated parts.
     */
    function keyedHitsOfParts(scale, skip) {
        const hits = [];
        // Option value that represents the affirmative answer ("True" / "Yes").
        // PDQ-4+ and IPDE use True=1; FAC22-SR lists Yes first so Yes=1 as well.
        const affirm = (() => {
            const opts = scale.matrixOptions || [];
            const t = opts.find(o => /^(true|yes)$/i.test((o.label || {}).en || ''));
            return t ? t.v : 1;
        })();
        (scale.parts || []).forEach(part => {
            if (skip && skip(part)) return;
            (part.questions || []).forEach(q => {
                const v = state.responses[scale.id + ':' + q.id];
                if (v === undefined) return;
                if (q.keyedAnswer !== undefined) {
                    if ((q.keyedAnswer === 'T') === (v === affirm)) {
                        hits.push(q.itemNumber != null ? q.itemNumber : q.id);
                    }
                } else if (v === affirm) {
                    hits.push(q.itemNumber != null ? q.itemNumber : q.id);
                }
            });
        });
        return hits;
    }

    /**
     * FAC22-SR (Senthil & Prabhakar, 2019) — factitious disorder self-report
     * screen. Keying as printed: Yes to items 5, 8, 10-22 and No to items 1-4,
     * 6, 7, 9, 12, 13. Bands: 9-14 possible factitious disorder, 15+ probable.
     * A screen only — it must never be used to diagnose factitious disorder,
     * which requires excluding deception for external gain and medical
     * malingering, so a positive result flags the category for clinical review.
     */
    function scoreFac22(scale, addFlag) {
        const hi = state.lang === 'hi';
        const ids = [];
        (scale.parts || []).forEach(part => (part.questions || []).forEach(q => ids.push(q.id)));
        const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
        const complete = got.length === ids.length;
        const keyed = keyedHitsOfParts(scale);
        const sc = scale.scoring || {};
        const probableAt = sc.probableThreshold != null ? sc.probableThreshold : 15;
        const possibleAt = sc.possibleThreshold != null ? sc.possibleThreshold : 9;
        const level = keyed.length >= probableAt ? 2 : (keyed.length >= possibleAt ? 1 : 0);
        if (complete && level > 0) {
            (sc.disorders || scale.disorders ||
                ['factitious_disorder', 'somatic_symptom_disorder']).forEach(d => {
                    const key = CLINICAL_DATA.disorders[d] ? d : null;
                    if (key) addFlag(key, 'FAC22-SR');
                });
        }
        return {
            name: L(scale.name),
            score: keyed.length + ' (' + got.length + '/' + ids.length + ')',
            severity: level === 2
                ? (hi ? 'संभावित भत्रुण रोग — पूर्ण मूल्यांकन आवश्यक' : 'Probable factitious disorder — full evaluation indicated')
                : level === 1
                    ? (hi ? 'संभव भत्रुण रोग — पूर्ण मूल्यांकन आवश्यक' : 'Possible factitious disorder — full evaluation indicated')
                    : (hi ? 'स्क्रीन नेगेटिव' : 'Screen negative'),
            aboveCutoff: complete && level > 0,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: [],
            pdRegister: {
                kind: 'fac22',
                heading: hi ? 'FAC22-SR कुंजी-अंक' : 'FAC22-SR keyed score',
                note: L(sc.rule || { en: '', hi: '' }),
                rows: [{
                    label: hi ? 'कुंजीकृत उत्तर (Yes 5,8,10-22 · No 1-4,6,7,9,12,13)' : 'Keyed responses (Yes 5,8,10-22 · No 1-4,6,7,9,12,13)',
                    value: keyed.length + '/22',
                    flagged: level > 0,
                    detail: hi
                        ? possibleAt + '-' + (probableAt - 1) + ' संभव · ' + probableAt + '+ संभावित'
                        : possibleAt + '-' + (probableAt - 1) + ' possible · ' + probableAt + '+ probable'
                }]
            }
        };
    }

    /**
     * PHQ-15 somatic symptom severity index: sum of 15 items scored 0-2 over
     * the past four weeks. Printed cut-points 0-4 no somatisation, 5-9 mild,
     * 10-14 moderate, 15+ severe. Severity measure only — it supplements
     * clinical judgement and does not by itself establish a diagnosis.
     */
    function scorePhq15(scale) {
        const hi = state.lang === 'hi';
        const ids = [];
        (scale.parts || []).forEach(part => (part.questions || []).forEach(q => ids.push(q.id)));
        const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined);
        const complete = got.length === ids.length;
        const sum = got.reduce((t, id) => t + Number(state.responses[scale.id + ':' + id]), 0);
        const maxTotal = ((scale.ratingScale || {}).max || 2) * ids.length;
        // Band list is ordered ascending by `max`; treat "no somatisation" as
        // non-clinical so the differential is only nudged from 5 upwards.
        const bandIdx = (() => {
            const bands = scale.bands || [];
            for (let i = 0; i < bands.length; i++) if (sum <= bands[i].max) return i;
            return bands.length - 1;
        })();
        return {
            name: L(scale.name),
            score: sum + '/' + maxTotal + ' (' + got.length + '/' + ids.length + ')',
            severity: (bandLabel(sum, scale.bands) || (hi ? 'अपूर्ण' : 'Incomplete')) +
                (hi ? ' · रोग-निर्णायक नहीं' : ' · not diagnostic'),
            aboveCutoff: complete && bandIdx >= 1,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: []
        };
    }

    /* ------------------------------------------------------------------ *
     * 7d. Dissociation instruments (MID-60 short form / DES-II)          *
     * ------------------------------------------------------------------ */

    /** Resolve an instrument disorder key, falling back to the legacy
     *  'dissociative' category if a newer key is absent from data.json. */
    function dissDisorder(keys) {
        for (const k of keys) if (CLINICAL_DATA.disorders[k]) return k;
        return CLINICAL_DATA.disorders.dissociative ? 'dissociative' : keys[0];
    }

    /**
     * Transient flag sink used by the standalone scorers (MID-60 / DES-II).
     * `computeResults` installs its own accumulator before deploying any
     * instrument and restores the no-op afterwards, so a scorer can raise a
     * differential-disorder flag without taking the addFlag closure as an
     * argument (keeps the signature aligned with scoreCas / scoreStaxi).
     */
    let addFlagGlobal = () => {};

    /** Resolve the GCLS differential key, falling back gracefully if a newer
     *  data.json does not yet carry it (same pattern as dissDisorder). */
    function genderDisorder(keys) {
        const list = keys || ['gender_incongruence_distress', 'gender_incongruence'];
        for (const k of list) if (CLINICAL_DATA.disorders[k]) return k;
        return null;
    }

    /**
     * MID-60 (Multidimensional Inventory of Dissociation, 60-item short form)
     * scoring: index = mean of all 60 ratings x 10 (0-100), compared against the
     * printed score ranges; each named subscale is scored as its own mean x 10
     * and compared against its published clinical cutoff. Subscales above cutoff
     * flag the dissociative-disorder categories for the structured interview —
     * the inventory itself never makes a diagnosis.
     */
    function scoreMid60(scale) {
        const hi = state.lang === 'hi';
        const ans = id => state.responses[scale.id + ':' + id];
        const ids = [];
        (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
        const got = ids.filter(id => ans(id) !== undefined).map(id => Number(ans(id)));
        const complete = got.length === ids.length;
        const mean = got.length ? got.reduce((a, b) => a + b, 0) / got.length : null;
        const index = mean === null ? null : Math.round(mean * 10 * 10) / 10;   // 0-100, one decimal
        const rangeLabel = r => L(r.label);
        const band = index === null ? null : (scale.scoreRanges || []).find(r => index <= r.max);

        const rows = [];
        const flaggedKeys = [];
        Object.keys(scale.subscales || {}).forEach(slug => {
            const sub = scale.subscales[slug];
            const sids = sub.items.map(n => 'mid_' + n);
            const sgot = sids.filter(id => ans(id) !== undefined).map(id => Number(ans(id)));
            const sMean = sgot.length ? sgot.reduce((a, b) => a + b, 0) / sgot.length : null;
            const sIndex = sMean === null ? null : Math.round(sMean * 10 * 10) / 10;
            const over = sIndex !== null && sgot.length === sids.length && sIndex >= Number(sub.cutoff);
            if (over) flaggedKeys.push(slug);
            rows.push({
                label: L(sub.name),
                value: sIndex === null ? '—' : (sIndex.toFixed(1) + ' / ≥' + sub.cutoff),
                flagged: over,
                detail: sIndex === null
                    ? (hi ? 'अपूर्ण (' + sgot.length + '/' + sids.length + ')' : 'Incomplete (' + sgot.length + '/' + sids.length + ')')
                    : (over
                        ? (hi ? 'कटऑफ से ऊपर — पूर्ण नैदानिक साक्षात्कार आवश्यक' : 'Above clinical cutoff — needs full diagnostic interview')
                        : (hi ? 'कटऑफ से नीचे' : 'Below clinical cutoff'))
            });
        });

        // Persecutory / self-harm intrusions always raise the risk pathway,
        // regardless of the total index.
        const persec = ['did_persecutory_intrusions', 'did_angry_intrusions']
            .filter(slug => flaggedKeys.includes(slug));

        const DISORDERS_BY_SUBSCALE = {
            did_amnesia_recent: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder', 'dissociative_amnesia'],
            did_alt_awareness: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
            did_angry_intrusions: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
            did_persecutory_intrusions: ['dissociative_identity_disorder', 'other_specified_dissociative_disorder'],
            drdepersonalisation: ['depersonalisation_derealisation_disorder'],
            amnesia_memory_distress: ['dissociative_amnesia'],
            amnesia_autobiographical: ['dissociative_amnesia'],
            ptsd_flashbacks: ['ptsd'],
            conversion_body: ['somatic_symptom_disorder'],
            conversion_seizures: ['somatic_symptom_disorder'],
            general_trance: ['other_specified_dissociative_disorder'],
            general_self_confusion: ['other_specified_dissociative_disorder', 'unspecified_dissociative_disorder']
        };
        const disorders = [];
        flaggedKeys.forEach(slug => (DISORDERS_BY_SUBSCALE[slug] || [])
            .forEach(k => { const d = dissDisorder([k]); if (!disorders.includes(d)) disorders.push(d); }));
        // The overall index also gates the differential when it reaches the
        // "may have dissociative disorder" band (>= 21 on the printed ranges).
        if (index !== null && complete && index >= 21) {
            [dissDisorder(['other_specified_dissociative_disorder']),
             dissDisorder(['unspecified_dissociative_disorder'])].forEach(d => {
                if (!disorders.includes(d)) disorders.push(d);
            });
        }
        disorders.forEach(d => addFlagGlobal(d, 'MID-60'));

        return {
            name: L(scale.name),
            score: index === null ? '—'
                : (index.toFixed(1) + '/100 (' + got.length + '/' + ids.length + ')'),
            severity: band ? L(band.label) : (hi ? 'अपूर्ण' : 'Incomplete'),
            aboveCutoff: index !== null && complete && index >= 21,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: disorders,
            pdRegister: {
                kind: 'mid60',
                heading: hi ? 'सूचकांक एवं उप-पैमाना कटऑफ' : 'Index & subscale clinical cutoffs',
                note: (hi
                    ? 'सूचकांक = सभी 60 अनुभव-रेटिंग का माध्य × 10 (0-100)। प्रत्येक उप-पैमाना अपना माध्य × 10 है; '
                    + 'मुद्रित स्कोर-शीट के नैदानिक कटऑफ से तुलना करें। यह स्क्रीनिंग/तीव्रता माप है — रोग-निर्णायक नहीं: '
                    + 'उच्च उप-पैमाना पूर्ण संरचित वियोजीय साक्षात्कार (SCID-5-D / पूर्ण MID) निर्देशित करता है।'
                    : 'Index = mean of all 60 experience ratings x 10 (0-100). Each subscale is its own mean x 10, '
                    + 'compared with the clinical cutoff printed on the score sheet. Screening/severity measure — '
                    + 'not diagnostic: an elevated subscale directs a full structured dissociative interview '
                    + '(SCID-5-D / full MID).') +
                    (persec.length ? (hi
                        ? ' · चिह्नित उत्पीड़नकारी/क्रोधित आंतरिक आवाज़ें — स्व-क्षति/आत्महत्या जोखिम मूल्यांकन अनिवार्य।'
                        : ' · Endorsed persecutory/angry internal voices — a self-harm and suicide-risk assessment is mandatory.')
                        : ''),
                validity: persec.length ? {
                    failed: true,
                    message: hi
                        ? 'उत्पीड़नकारी/क्रोधित आंतरिक आवाज़ों का पैमाना-उपर कटऑफ — तत्काल जोखिम-मूल्यांकन एवं निगरानी आवश्यक।'
                        : 'Persecutory/angry intrusion subscale above cutoff — urgent risk assessment and monitoring required.'
                } : null,
                rows: [{
                    label: hi ? 'कुल सूचकांक (माध्य × 10)' : 'Total index (mean x 10)',
                    value: index === null ? '—' : index.toFixed(1) + '/100',
                    flagged: !!(band && (scale.scoreRanges || []).indexOf(band) >= 3),
                    detail: band ? rangeLabel(band) : (hi ? 'अपूर्ण' : 'Incomplete')
                }].concat(rows)
            }
        };
    }

    /* ------------------------------------------------------------------ *
     * 7f. Gender-related distress (GCLS)                                   *
     * ------------------------------------------------------------------ */

    /**
     * GCLS scoring. Items are rated Never=0 ... Always=4 over the past six
     * months. The positively worded congruence items (16, 20, 22, 25, 30) and
     * the negatively worded satisfaction items (35, 37) are reverse-scored as
     * (scaleMax - response) before summing, exactly as printed in the scale's
     * scoring rule. Three distress subscales (functional impact, body
     * preoccupation, social preoccupation) rise with distress; life
     * satisfaction is reported separately and rises with satisfaction. There
     * are no published cutoffs, so nothing here diagnoses gender incongruence
     * or dysphoria — it describes distress, functioning and satisfaction and
     * supports follow-up measurement. The non-scored surgery tick-box is
     * reported as a clinical note only.
     */
    function scoreGcls(scale) {
        const hi = state.lang === 'hi';
        const maxV = ((scale.ratingScale || {}).max != null ? scale.ratingScale.max : 4);
        const ans = id => state.responses[scale.id + ':' + id];
        const ids = [];
        (scale.parts || []).forEach(part => (part.questions || []).forEach(q => {
            if (!q.nonScored) ids.push({ id: q.id, num: q.itemNumber, rev: !!q.reverseScored });
        }));
        const got = ids.filter(i => ans(i.id) !== undefined);
        const complete = got.length === ids.length;
        const valueOf = i => {
            const v = Number(ans(i.id));
            return i.rev ? maxV - v : v;
        };

        // item number -> scored entry, for subscale lookup
        const byNum = {};
        ids.forEach(i => { byNum[i.num] = i; });

        const rows = [];
        Object.keys(scale.subscales || {}).forEach(slug => {
            const sub = scale.subscales[slug];
            const entries = (sub.items || []).map(n => byNum[n]).filter(Boolean);
            const answered = entries.filter(i => ans(i.id) !== undefined);
            const sum = answered.reduce((t, i) => t + valueOf(i), 0);
            const done = answered.length === entries.length;
            rows.push({
                label: L(sub),
                value: done ? (sum + '/' + (sub.maxTotal != null ? sub.maxTotal : entries.length * maxV))
                            : (hi ? 'अपूर्ण (' + answered.length + '/' + entries.length + ')'
                                  : 'Incomplete (' + answered.length + '/' + entries.length + ')'),
                flagged: false,
                detail: slug === 'life_satisfaction'
                    ? (hi ? 'उच्च = अधिक जीवन-संतुष्टि (पृथक् रिपोर्ट)' : 'Higher = MORE life satisfaction (reported separately)')
                    : (hi ? 'उच्च = अधिक लिंग-संबंधी कष्ट' : 'Higher = more gender-related distress')
            });
        });

        const distressSlugs = ['functional_impact', 'body_preoccupation', 'social_preoccupation'];
        const distressSum = distressSlugs.reduce((t, slug) => {
            const sub = (scale.subscales || {})[slug] || {};
            return t + (sub.items || []).map(n => byNum[n]).filter(Boolean)
                .filter(i => ans(i.id) !== undefined).reduce((a, i) => a + valueOf(i), 0);
        }, 0);
        const satEntry = (scale.subscales.life_satisfaction || {}).items || [];
        const satSum = satEntry.map(n => byNum[n]).filter(Boolean)
            .filter(i => ans(i.id) !== undefined).reduce((a, i) => a + valueOf(i), 0);

        // Safety: items 8 (chest/genital self-harm) and 13 (suicidal thoughts).
        const safetyItems = ids.filter(i => {
            const q = (scale.parts || []).flatMap(pt => pt.questions || [])
                .find(x => x.itemNumber === i.num);
            return q && q.safety;
        });
        const riskEndorsed = safetyItems.filter(i => ans(i.id) !== undefined && Number(ans(i.id)) > 0);

        const disorders = [];
        if (complete && distressSum > 0) {
            const d = genderDisorder();
            if (d) { disorders.push(d); addFlagGlobal(d, 'GCLS'); }
        }

        const tick = (scale.parts || []).flatMap(pt => pt.questions || [])
            .find(q => q.nonScored && q.tickBox);
        const ticked = tick ? !!ans(tick.id) : false;

        return {
            name: L(scale.name),
            score: complete
                ? (hi ? 'कष्ट उप-पैमाने योग ' + distressSum + ' · संतुष्टि ' + satSum
                      : 'Distress subscale sum ' + distressSum + ' · Satisfaction ' + satSum)
                : (got.length + '/' + ids.length + ' ' + (hi ? 'उत्तर' : 'answered')),
            severity: complete
                ? (hi ? 'वर्णनात्मक — रोग-निर्णायक नहीं' : 'Descriptive — not diagnostic')
                : (hi ? 'अपूर्ण' : 'Incomplete'),
            aboveCutoff: false,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: disorders,
            pdRegister: {
                kind: 'gcls',
                heading: hi ? 'उप-पैमाना अंक (व्युक्रम-अंकित)' : 'Subscale scores (reverse-keyed)',
                note: (hi
                    ? 'आइटम 16, 20, 22, 25, 30 (संगति) तथा 35, 37 (नकारात्मक संतुष्टि) को व्युक्रम कर (4 − उत्तर) उप-पैमाना योग निकाले जाते हैं। '
                    + 'कष्ट उप-पैमाने उच्च होने पर अधिक कष्ट; जीवन-संतुष्टि पृथक् रिपोर्ट (उच्च = अधिक संतुष्टि)। '
                    + 'GCLS का कोई नैदानिक कटअफ नहीं — यह कष्ट एवं कार्य-क्षमता वर्णित करता है।'
                    : 'Congruence items 16/20/22/25/30 and negative satisfaction items 35/37 are reverse-scored (4 minus response) before summing. '
                    + 'Higher distress subscales mean more gender-related distress; life satisfaction is reported separately (higher = more satisfied). '
                    + 'The GCLS has no diagnostic cutoffs: it describes distress and functioning and supports outcome monitoring.')
                    + (riskEndorsed.length ? (hi
                        ? ' · आइटम 8/13 पर स्व-क्षति/आत्महत्या विचार — जोखिम-मूल्यांकन अनिवार्य।'
                        : ' · Item 8/13 endorsed chest/genital self-harm or suicidal thoughts — a risk assessment is mandatory.')
                        : '')
                    + (ticked ? (hi ? ' · रोगी ने जननांग-शस्त्रक्रिया पहले होना चिह्नित किया (आइटम 26 सावधानी से व्याख्या करें)।'
                                    : ' · Respondent ticked prior genital surgery — interpret item 26 accordingly.')
                               : ''),
                rows: rows
            }
        };
    }

    /**
     * BISS (Bipolar Inventory of Signs and Symptoms Scale, Bowden v1.5) scoring.
     * 44 clinician-rated items scored 0-4 over the most recent 7 days from
     * self-report plus family and interview observation. Section I Depression is
     * items 1-20 (0-80) and section II Mania is items 21-44 (0-96); an item counts
     * as symptomatic at >= 2 (mild or worse). The printed instrument derives no
     * diagnostic decision rule, so nothing here converts a total into a bipolar
     * diagnosis: the differential categories are flagged only when the domain's
     * own screen-in item is endorsed, exactly as for the other optional tables.
     */
    function scoreBiss(scale, addFlag) {
        const hi = state.lang === 'hi';
        const ans = id => state.responses[scale.id + ':' + id];
        const sections = Object.keys((scale.scoring || {}).sections || {});
        const posV = (scale.scoring || {}).positiveItemValue || 2;
        const rows = [];
        let allAnswered = true;
        sections.forEach(slug => {
            const sec = scale.scoring.sections[slug];
            const values = sec.ids.map(ans);
            const answered = values.filter(v => v !== undefined);
            if (answered.length !== sec.ids.length) allAnswered = false;
            const sum = answered.reduce((t, v) => t + Number(v), 0);
            const done = answered.length === sec.ids.length;
            const bandLabelFor = s => {
                if (s === 0) return hi ? 'अनुपस्थित' : 'Absent';
                if (s <= 10) return hi ? 'हल्का-मंद' : 'Slight-mild';
                if (s <= 25) return hi ? 'मध्यम' : 'Moderate';
                return hi ? 'गंभीर' : 'Severe';
            };
            rows.push({
                label: slug === 'depression'
                    ? (hi ? 'I. अवसाद (आइटम 1-20)' : 'I. Depression (items 1-20)')
                    : (hi ? 'II. उन्माद (आइटम 21-44)' : 'II. Mania (items 21-44)'),
                value: done ? (sum + '/' + sec.maxTotal)
                            : (hi ? 'अपूर्ण (' + answered.length + '/' + sec.count + ')'
                                  : 'Incomplete (' + answered.length + '/' + sec.count + ')'),
                flagged: done && sum > 0,
                detail: done ? (bandLabelFor(sum) + ' · ' +
                    answered.filter(v => Number(v) >= posV).length + ' ≥ mild' +
                    (slug === 'mania' ? '' : ' · ' +
                        answered.filter(v => Number(v) === 1).length + ' slight')) : ''
            });
        });

        // Safety register: suicidality (item 4) at any rating, plus aggression
        // (25), risky behaviour (39) and hallucinations (43) at mild or worse.
        const safetyHits = (scale.safetyItems || []).filter(id => {
            const v = ans(id);
            if (v === undefined) return false;
            return id === 'biss_4' ? Number(v) >= 1 : Number(v) >= posV;
        });
        const itemName = id => {
            const q = (scale.parts || []).flatMap(p => p.questions || [])
                .find(x => x.id === id);
            return q ? L(q.itemName || q.text) : id;
        };

        const depSum = sections.indexOf('depression') >= 0
            ? scale.scoring.sections.depression.ids.map(ans)
                .filter(v => v !== undefined).reduce((t, v) => t + Number(v), 0) : 0;
        const manSum = sections.indexOf('mania') >= 0
            ? scale.scoring.sections.mania.ids.map(ans)
                .filter(v => v !== undefined).reduce((t, v) => t + Number(v), 0) : 0;

        const disorders = [];
        if (allAnswered) {
            // Screen-in endorsement decides which bipolar categories need the
            // structured interview; the BISS itself only grades severity.
            (scale.disorderKeys || []).forEach(k => {
                if (!CLINICAL_DATA.disorders[k]) return;
                const elevated = k === 'bipolar_depressive' ? depSum : manSum;
                if (elevated > 0) disorders.push(k);
            });
            disorders.forEach(d => addFlag(d, 'BISS'));
        }

        return {
            name: L(scale.name),
            score: allAnswered
                ? (hi ? 'अवसाद ' + depSum + '/80 · उन्माद ' + manSum + '/96'
                      : 'Depression ' + depSum + '/80 · Mania ' + manSum + '/96')
                : ((scale.scoring.sections.depression.ids.concat(
                        scale.scoring.sections.mania.ids)
                        .filter(id => ans(id) !== undefined)).length + '/44 ' +
                    (hi ? 'रेटित' : 'rated')),
            severity: allAnswered
                ? (hi ? 'विमात्मक तीव्रता — रोग-निर्णायक नहीं'
                      : 'Dimensional severity — not diagnostic')
                : (hi ? 'अपूर्ण' : 'Incomplete'),
            aboveCutoff: false,
            notDiagnostic: true,
            answered: scale.scoring.sections.depression.ids.concat(
                        scale.scoring.sections.mania.ids).filter(id => ans(id) !== undefined).length,
            total: 44,
            disorders: disorders,
            pdRegister: {
                kind: 'biss',
                heading: hi ? 'विभाग-वार तीव्रता (7 दिन)' : 'Section severity (past 7 days)',
                note: L((scale.scoring || {}).interpretationNote || { en: '', hi: '' }) +
                    (safetyHits.length ? (hi
                        ? ' · सुरक्षा-चिह्न: ' + safetyHits.map(itemName).join(', ') +
                          ' — तत्काल जोखिम-मूल्यांकन आवश्यक।'
                        : ' · Safety flags: ' + safetyHits.map(itemName).join(', ') +
                          ' — an immediate risk assessment is required.')
                        : ''),
                rows: rows
            },
            bissSafety: safetyHits.map(itemName)
        };
    }

    /**
     * DES-II scoring: total = mean of the 28 item percentages (0-100). A mean of
     * 30 or above is the clinical comparison point that warrants a structured
     * dissociative-disorder interview. Dimensional screening only.
     */
    function scoreDesII(scale) {
        const hi = state.lang === 'hi';
        const ids = [];
        (scale.parts || []).forEach(part => part.questions.forEach(q => ids.push(q.id)));
        const got = ids.filter(id => state.responses[scale.id + ':' + id] !== undefined)
            .map(id => Number(state.responses[scale.id + ':' + id]));
        const complete = got.length === ids.length;
        const mean = got.length ? got.reduce((a, b) => a + b, 0) / got.length : null;
        const cutoff = (scale.scoring || {}).cutoff || 30;
        const above = mean !== null && complete && mean >= cutoff;
        const disorders = [];
        if (above) {
            [dissDisorder(['other_specified_dissociative_disorder']),
             dissDisorder(['dissociative_amnesia']),
             dissDisorder(['depersonalisation_derealisation_disorder'])]
                .forEach(k => { if (!disorders.includes(k)) disorders.push(k); });
            disorders.forEach(d => addFlagGlobal(d, 'DES-II'));
        }
        return {
            name: L(scale.name),
            score: mean === null ? '—'
                : (Math.round(mean * 10) / 10 + '% (' + got.length + '/' + ids.length + ')'),
            severity: (mean === null ? (hi ? 'अपूर्ण' : 'Incomplete') : bandLabel(mean, scale.bands)) +
                (above ? (hi ? ' · नैदानिक-तुलना बिंदु ≥' + cutoff + ' पार' : ' · above the ≥' + cutoff + ' clinical comparison point') : ''),
            aboveCutoff: above,
            notDiagnostic: true,
            answered: got.length, total: ids.length,
            disorders: disorders
        };
    }

    /* ------------------------------------------------------------------ *
     * 7. SAFETY MODAL (non-dismissible except explicit acknowledgement)
     * ------------------------------------------------------------------ */
    function openSafetyModal() {
        const modal = document.getElementById('safety-modal');
        const resources = document.getElementById('crisis-resources');
        resources.replaceChildren();
        (CLINICAL_DATA.crisisResources[state.lang] || CLINICAL_DATA.crisisResources.en).forEach(r => {
            const div = document.createElement('div');
            div.className = 'crisis-resource';
            const strong = document.createElement('strong');
            strong.textContent = r.label;
            const val = document.createElement('span');
            val.textContent = r.value;
            div.append(strong, val);
            resources.appendChild(div);
        });
        modal.classList.remove('hidden');
        modal.removeAttribute('aria-hidden');
        document.getElementById('safety-close').focus();
        document.body.style.overflow = 'hidden';
    }

    function closeSafetyModal() {
        const modal = document.getElementById('safety-modal');
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    /* ------------------------------------------------------------------ *
     * 8. SCORING ENGINE — deterministic, rubric-equivalent computation
     * ------------------------------------------------------------------ */
    /**
     * Band lookup that understands both shapes used across the instrument set:
     *  - `{ max, severity: {en, hi} }`   (PHQ-9 / CAS / DES-II style bands)
     *  - `{ max, label:   {en, hi} }`   (MID-60 printed score ranges)
     * Returns a localised string (or null when no bands are configured), so a
     * caller never has to know which shape the scale uses.
     */
    function bandLabel(score, bands) {
        if (!bands || !bands.length) return null;
        let b = bands[bands.length - 1];
        for (const cand of bands) { if (score <= cand.max) { b = cand; break; } }
        const text = b.severity != null ? b.severity : b.label;
        return text == null ? null : L(text);
    }

    function severityBand(score, bands) {
        for (const b of bands) if (score <= b.max) return b.severity;
        return bands[bands.length - 1].severity;
    }

    function computeResults() {
        const instrumentResults = [];
        const flaggedDisorders = new Map(); // disorderKey -> {sources:Set, bestScore}

        const addFlag = (dkey, source) => {
            if (!CLINICAL_DATA.disorders[dkey]) return;
            if (!flaggedDisorders.has(dkey)) flaggedDisorders.set(dkey, { sources: new Set() });
            flaggedDisorders.get(dkey).sources.add(source);
        };
        // Standalone scorers (MID-60 / DES-II) raise flags through this sink.
        addFlagGlobal = addFlag;

        CLINICAL_DATA.domains.forEach(domain => {
            if (!state.selectedDomains.has(domain.id)) return;

            // Deployed VADRS matrix (pediatric ADHD routing)
            if (domain.instrument === 'auto:adhd' && ['pediatric', 'adolescent'].includes(state.context.ageGroup)) {
                const vadrs = CLINICAL_DATA.scales.vadrs;
                const sc = vadrs.scoring;
                const count = (ids, min) => ids.filter(id => (state.responses['vadrs:' + id] || 0) >= min).length;
                const sum = (ids) => ids.reduce((t, id) => t + (state.responses['vadrs:' + id] || 0), 0);
                const inat = count(sc.inattention.ids, sc.inattention.minSymptomValue);
                const hyp = count(sc.hyperactivity.ids, sc.hyperactivity.minSymptomValue);
                const odd = count(sc.oppositionalDefiant.ids, sc.oppositionalDefiant.minSymptomValue);
                const cond = count(sc.conduct.ids, sc.conduct.minSymptomValue);
                const anxdep = count(sc.anxietyDepression.ids, sc.anxietyDepression.minSymptomValue);
                const perfImpaired = count(sc.performance.ids, sc.performance.minImpairedValue);
                const totalSymptomScore = sum(sc.inattention.ids.concat(sc.hyperactivity.ids));
                const perfValues = sc.performance.ids.map(id => state.responses['vadrs:' + id]).filter(v => v !== undefined);
                const avgPerf = perfValues.length ? (perfValues.reduce((a, b) => a + b, 0) / perfValues.length) : null;
                const impairedGate = perfImpaired >= sc.performance.requiresImpairedCount;

                const positive = (inat >= sc.inattention.thresholdCount || hyp >= sc.hyperactivity.thresholdCount) && impairedGate;
                if (positive) sc.disordersOnPositive.forEach(d => addFlag(d, 'VADRS'));
                if (odd >= sc.oppositionalDefiant.thresholdCount && impairedGate)
                    (sc.oppositionalDefiant.disordersOnPositive || []).forEach(d => addFlag(d, 'VADRS'));
                if (cond >= sc.conduct.thresholdCount && impairedGate)
                    (sc.conduct.disordersOnPositive || []).forEach(d => addFlag(d, 'VADRS'));

                instrumentResults.push({
                    name: 'VADRS',
                    score: 'IA ' + inat + '/' + sc.inattention.ids.length +
                           ' · HI ' + hyp + '/' + sc.hyperactivity.ids.length +
                           ' · ODD ' + odd + '/' + sc.oppositionalDefiant.ids.length +
                           ' · CD ' + cond + '/' + sc.conduct.ids.length +
                           ' · Anx/Dep ' + anxdep + '/' + sc.anxietyDepression.ids.length +
                           ' · Perf ' + perfImpaired + '/' + sc.performance.ids.length +
                           ' | Total symptom score 1–18: ' + totalSymptomScore +
                           (avgPerf !== null ? ' | Avg performance: ' + avgPerf.toFixed(2) : ''),
                    severity: positive ? (state.lang === 'hi' ? 'सकारात्मक स्क्रीन' : 'Positive screen') : (state.lang === 'hi' ? 'ऋणात्मक' : 'Negative'),
                    disorders: positive ? sc.disordersOnPositive : []
                });
                return;
            }

            // Clinician-rated severity tables (MINI optional assessments A/B): the
            // printed form records one 0-10 rating per row and derives no total, so
            // these are reported as a rating register rather than a cutoff score.
            if (domain.instrument === 'auto:minioptional') {
                domain.questions.forEach(q => {
                    if (!q.scaleId) return;
                    if ((state.responses[domain.id + ':' + q.id] || 0) < 1) return;
                    const s = CLINICAL_DATA.scales[q.scaleId];
                    if (!s) return;
                    const rows = s.parts[0].questions;
                    const rated = rows.map(r => state.responses[q.scaleId + ':' + r.id])
                        .filter(v => v !== undefined);
                    const anchorName = v => {
                        const anchors = ((s.ratingScale || {}).anchors || []).slice().sort((a, b) => b.v - a.v);
                        const hit = anchors.find(a => v >= a.v);
                        return hit ? L(hit.label) : String(v);
                    };
                    instrumentResults.push({
                        name: L(s.name),
                        score: rated.length + '/' + rows.length + ' rated' +
                            (rated.length ? ' | max ' + Math.max(...rated) + '/10 (' + anchorName(Math.max(...rated)) + ')' : ''),
                        severity: rated.length
                            ? (state.lang === 'hi' ? 'चिकित्सक-रेटित' : 'Clinician-rated')
                            : (state.lang === 'hi' ? 'अपूर्ण' : 'Incomplete'),
                        aboveCutoff: false,
                        answered: rated.length, total: rows.length,
                        disorders: [],
                        ratingRegister: rows.map(r => ({ id: r.id, label: L(r.text), value: state.responses[q.scaleId + ':' + r.id] }))
                    });
                });
                return;
            }

            // Keyed True/False personality screens (IPDE ICD-10 module screen, PDQ-4+).
            // Neither instrument yields a dimensional score: they flag which cluster or
            // DSM personality disorder needs the full structured interview.
            if (domain.instrument === 'auto:pdscreen') {
                domain.questions.forEach(q => {
                    if (!q.scaleId) return;
                    if ((state.responses[domain.id + ':' + q.id] || 0) < 1) return;
                    const s = CLINICAL_DATA.scales[q.scaleId];
                    if (!s || !s.keyedScoring) return;
                    if (s.keying === 'ipde') instrumentResults.push(scoreIpde(s, addFlag));
                    else instrumentResults.push(scorePdq4(s, addFlag));
                });
                return;
            }

            // Summed anger instruments (STAXI-CA / Clinical Anger Scale): deployed
            // through the domain's own screen-in items. Both are dimensional - they
            // report severity, never a diagnosis - but a positive screen-in item
            // still flags the impulse-control categories.
            if (domain.instrument === 'auto:angertable') {
                if ((state.responses[domain.id + ':ang_1'] || 0) >= 1 ||
                    (state.responses[domain.id + ':ang_2'] || 0) >= 1) {
                    (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Anger screen'));
                }
                deployedScreenInstruments(domain, s => !!s.sumScoring).forEach(({ scale }) => {
                    instrumentResults.push(scale.keying === 'staxi' || scale.id === 'staxi_ca'
                        ? scoreStaxi(scale) : scoreCas(scale));
                });
                return;
            }

            // Dissociative-experience inventories (MID-60 short form / DES-II):
            // each is attached to one screen-in item of the `dissociation` domain.
            // Both are dimensional severity measures - they flag the dissociative
            // categories for the structured interview but never diagnose.
            if (domain.instrument === 'auto:dissociationtable') {
                if (domain.questions.some(q => (state.responses[domain.id + ':' + q.id] || 0) >= 1)) {
                    (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Dissociation screen'));
                }
                deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                    instrumentResults.push(scale.id === 'mid60'
                        ? scoreMid60(scale) : scoreDesII(scale));
                });
                return;
            }

            // Somatic-symptom instruments: keyed Yes/No factitious screen (FAC22-SR)
            // plus the summed PHQ-15 somatic severity index. Neither diagnoses; both
            // flag the somatic-symptom / factitious categories for clinical review.
            if (domain.instrument === 'auto:somatoptable') {
                if (domain.questions.some(q => (state.responses[domain.id + ':' + q.id] || 0) >= 1)) {
                    (domain.questions[0].disorders || []).forEach(d => addFlag(d, 'Somatic screen'));
                }
                deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                    if (scale.keyedScoring) instrumentResults.push(scoreFac22(scale, addFlag));
                    else instrumentResults.push(scorePhq15(scale));
                });
                return;
            }

            // Gender-related distress (GCLS): one reverse-keyed, subscale-scored
            // self-report attached to both screen-in items of the `gender` domain.
            // Descriptive only - it never diagnoses gender incongruence/dysphoria,
            // and gender diversity on its own is not a mental disorder.
            if (domain.instrument === 'auto:genderdistress') {
                deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                    instrumentResults.push(scoreGcls(scale));
                });
                return;
            }

            // Bipolar signs & symptoms (BISS) on the mood domain: the nine PHQ-9
            // items keep their usual raw-sum scoring, and every BISS attached to an
            // endorsed screen-in item is scored as a dimensional severity profile.
            if (domain.instrument === 'auto:bipolartable' && domain.baseInstrument) {
                // Same always-deployed rule as the other optional tables: the BISS
                // appears on screen as soon as the mood domain is selected, so it
                // must be scored regardless of how its screen-in items were answered.
                deployedScreenInstruments(domain, () => true).forEach(({ scale }) => {
                    if (scale.id === 'biss') instrumentResults.push(scoreBiss(scale, addFlag));
                });
                // fall through to the generic raw-sum block below for the PHQ-9 items
            }

            // Domain raw-sum scoring against cutoff (PHQ-9/GAD-7/PCL-5/ISI/AUDIT-C/ASRS/CAARS-style)
            let sum = 0, answered = 0;
            domain.questions.forEach(q => {
                if (q.scaleId) return;   // screen-in gates are not scored items
                const v = state.responses[domain.id + ':' + q.id];
                if (v !== undefined) { sum += v; answered++; }
            });
            const maxPossible = domain.questions.filter(q => !q.scaleId).reduce((m, q) =>
                m + Math.max(...optionsForQuestion(q).map(o => o.v)), 0);
            const cutoff = domain.cutoff != null ? domain.cutoff : Math.round(maxPossible * 0.4);
            const bands = domain.bands || [
                { max: Math.floor(cutoff * 0.5), severity: state.lang === 'hi' ? 'हल्का' : 'Mild' },
                { max: Math.floor(cutoff * 0.75), severity: state.lang === 'hi' ? 'मध्यम' : 'Moderate' },
                { max: cutoff, severity: state.lang === 'hi' ? 'गंभीर' : 'Moderately severe' },
                { max: Infinity, severity: state.lang === 'hi' ? 'अत्यंत गंभीर' : 'Severe' }
            ];
            const aboveCutoff = sum >= cutoff;
            const severity = severityBand(sum, bands);
            if (aboveCutoff) {
                domain.questions.forEach(q => {
                    if (q.scaleId) return;   // screen-in gates flag via their own route
                    const v = state.responses[domain.id + ':' + q.id];
                    if ((v || 0) >= 2 && q.disorders) q.disorders.forEach(d => addFlag(d, domain.baseInstrument || domain.instrument || domain.id));
                });
            }
            // Resolve the deployed instrument's canonical name from the library
            // (data.json instruments map), falling back to the domain id.
            let instrumentName = (domain.baseInstrument || domain.instrument || domain.id);
            if (CLINICAL_DATA.instruments) {
                const slug = instrumentName.toLowerCase().replace(/[^a-z0-9]/g, '');
                const matchKey = Object.keys(CLINICAL_DATA.instruments)
                    .find(k => k.toLowerCase().replace(/[^a-z0-9]/g, '') === slug);
                if (matchKey) instrumentName = matchKey;
            }
            instrumentResults.push({
                name: instrumentName,
                score: sum + '/' + maxPossible,
                severity,
                aboveCutoff,
                answered, total: domain.questions.length,
                disorders: aboveCutoff ? collectDomainDisorders(domain) : []
            });
        });

        // Build tiered differential considerations from the harmonized database
        const differentials = [];
        flaggedDisorders.forEach((meta, key) => {
            const d = CLINICAL_DATA.disorders[key];
            differentials.push({ key, ...d, tier: d.tier, sources: [...meta.sources] });
        });
        differentials.sort((a, b) => a.tier - b.tier);

        state.results = { instrumentResults, differentials, safetyTriggered: state.safetyFlags.length > 0 };
        return state.results;
    }

    function collectDomainDisorders(domain) {
        const set = new Set();
        domain.questions.forEach(q => (q.disorders || []).forEach(d => set.add(d)));
        return [...set];
    }

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
                ? 'आपके उत्तरों में चिंता के क्षेत्र परिलक्षित होते हैं। कृपया इन निष्कर्षों को अपने चिकित्सक के साथ चर्चा करें। यह कोई रोग-निर्णय नहीं है।'
                : 'Your responses indicate areas of concern that merit discussion. Please review these findings with your clinician. This screening does not constitute a diagnosis.')
            : (state.lang === 'hi'
                ? 'आपके उत्तर वर्तमान में कोई महत्वपूर्ण चिंता का संकेत नहीं देते हैं। फिर भी अपनी सामान्य देखभाल जारी रखें।'
                : 'Your responses do not currently indicate significant areas of concern. Continue with your routine care.');
        pv.appendChild(para);

        if (r.safetyTriggered) {
            const alertBox = document.createElement('div');
            alertBox.className = 'patient-safety-note';
            alertBox.textContent = state.lang === 'hi'
                ? 'आपके कुछ उत्तरों ने त्वरित सहायता संसाधनों को दर्शाया है। कृपया आज ही किसी हेल्पलाइन पर संपर्क करें।'
                : 'Some of your responses highlighted immediate support resources. Please consider contacting a helpline today.';
            pv.appendChild(alertBox);
        }

        // Clinician detail (on-screen mirror of the PDF)
        const rc = document.getElementById('report-content');
        rc.replaceChildren();
        const tbl = document.createElement('table');
        tbl.className = 'clinician-table';
        const thead = document.createElement('thead');
        const hr = document.createElement('tr');
        [state.lang === 'hi' ? 'उपकरण' : 'Instrument', state.lang === 'hi' ? 'स्कोर' : 'Score', state.lang === 'hi' ? 'तीव्रता' : 'Severity'].forEach(x => {
            const th = document.createElement('th'); th.textContent = x; hr.appendChild(th);
        });
        thead.appendChild(hr); tbl.appendChild(thead);
        const tbody = document.createElement('tbody');
        r.instrumentResults.forEach(x => {
            const tr = document.createElement('tr');
            [x.name, x.score, x.severity].forEach(v => {
                const td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        tbl.appendChild(tbody);
        rc.appendChild(tbl);

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

    /* ------------------------------------------------------------------ *
     * 10. CLIENT-SIDE PDF GENERATION (jsPDF + AutoTable) — no transmission
     * ------------------------------------------------------------------ */
    function generatePDF() {
        if (!window.jspdf || !state.results) return;
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const r = state.results;
        let y = 20;

        doc.setFontSize(16);
        doc.text('Pre-Consultation Clinical Screening Summary', 14, y); y += 8;
        doc.setFontSize(10);
        doc.setTextColor(120);
        doc.text('Generated client-side by EPCSS. No PHI was transmitted or stored.', 14, y); y += 4;
        doc.text('Date: ' + new Date().toISOString().slice(0, 10) +
                 '  |  Schema: ' + (CLINICAL_DATA.meta ? CLINICAL_DATA.meta.schemaVersion : 'n/a'), 14, y); y += 10;

        doc.setTextColor(0);
        doc.setFontSize(12);
        doc.text('Patient Context (de-identified)', 14, y); y += 6;
        doc.setFontSize(10);
        doc.text('Age group: ' + (state.context.ageGroup || '—'), 14, y); y += 5;
        doc.text('Reason for visit: ' + (state.context.reason || '—').substring(0, 180), 14, y); y += 5;
        doc.text('Medications: ' + (state.context.medications || '—').substring(0, 180), 14, y); y += 5;
        doc.text('Prior diagnoses: ' + (state.context.priorDiagnoses || '—').substring(0, 180), 14, y); y += 10;

        doc.autoTable({
            startY: y,
            head: [['Instrument', 'Raw Score', 'Severity']],
            body: r.instrumentResults.map(x => [x.name, x.score, x.severity]),
            theme: 'striped',
            styles: { fontSize: 9 }
        });
        y = doc.lastAutoTable.finalY + 10;

        // Vanderbilt "For Office Use Only" totals (mirrors the NICHQ scoring sheet)
        const vadrsResult = r.instrumentResults.find(x => x.name === 'VADRS');
        if (vadrsResult) {
            const sc = CLINICAL_DATA.scales.vadrs.scoring;
            const cnt = (ids, min) => ids.filter(id => (state.responses['vadrs:' + id] || 0) >= min).length;
            doc.setFontSize(12);
            doc.text('VADRS — For Office Use Only', 14, y); y += 2;
            doc.autoTable({
                startY: y,
                head: [['Scoring Field', 'Value']],
                body: [
                    ['Total scored 2 or 3 in questions 1-9 (inattention)', String(cnt(sc.inattention.ids, sc.inattention.minSymptomValue))],
                    ['Total scored 2 or 3 in questions 10-18 (hyperactivity/impulsivity)', String(cnt(sc.hyperactivity.ids, sc.hyperactivity.minSymptomValue))],
                    ['Total symptom score for questions 1-18', String(sc.inattention.ids.concat(sc.hyperactivity.ids).reduce((t, id) => t + (state.responses['vadrs:' + id] || 0), 0))],
                    ['Total scored 2 or 3 in questions 19-26 (oppositional-defiant)', String(cnt(sc.oppositionalDefiant.ids, sc.oppositionalDefiant.minSymptomValue))],
                    ['Total scored 2 or 3 in questions 27-40 (conduct)', String(cnt(sc.conduct.ids, sc.conduct.minSymptomValue))],
                    ['Total scored 2 or 3 in questions 41-47 (anxiety/depression)', String(cnt(sc.anxietyDepression.ids, sc.anxietyDepression.minSymptomValue))],
                    ['Total scored 4 or 5 in performance questions 48-55', String(cnt(sc.performance.ids, sc.performance.minImpairedValue))],
                    ['Average performance score', (() => {
                        const vals = sc.performance.ids.map(id => state.responses['vadrs:' + id]).filter(v => v !== undefined);
                        return vals.length ? (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2) : '—';
                    })()]
                ],
                theme: 'grid',
                styles: { fontSize: 8 }
            });
            y = doc.lastAutoTable.finalY + 10;
            doc.setFontSize(8);
            doc.setTextColor(120);
            doc.text('Scales should not be used alone to make a diagnosis; DSM criteria require 6+ of 9 core symptoms (parent form items 1-9 or 10-18) plus impairment (score 4 or 5 on any performance item).', 14, y);
            doc.setTextColor(0);
            y += 10;
        }

        // MINI optional assessments A & B: reproduce the printed rating tables
        // ("Symptom Name / Score", "Domain Name / Score") row by row.
        const ratingTables = r.instrumentResults.filter(x => x.ratingRegister && x.ratingRegister.length);
        ratingTables.forEach(tbl => {
            if (y > 230) { doc.addPage(); y = 20; }
            doc.setFontSize(12);
            doc.text(tbl.name + ' — For Office Use Only', 14, y); y += 2;
            doc.autoTable({
                startY: y,
                head: [['Name', 'Score (0-10)']],
                body: tbl.ratingRegister.map(row => [row.label, row.value === undefined ? '—' : String(row.value)]),
                theme: 'grid',
                styles: { fontSize: 8 },
                columnStyles: { 1: { cellWidth: 26 } }
            });
            y = doc.lastAutoTable.finalY + 4;
            doc.setFontSize(8);
            doc.setTextColor(120);
            doc.text('Scale: 0 Not present, 1 Mild, 3 Moderate, 6 Severe, 10 Extreme. Each row is rated independently; no composite total is derived and these ratings do not gate any diagnostic box.', 14, y);
            doc.setTextColor(0);
            y += 10;
        });

        // Personality-disorder screens: reproduce the IPDE scoring summary and the
        // PDQ-4+ profile sheet (scale, keyed count, status) as tables.
        const pdRegisters = r.instrumentResults.filter(x => x.pdRegister && x.pdRegister.rows.length);
        pdRegisters.forEach(reg => {
            if (y > 230) { doc.addPage(); y = 20; }
            doc.setFontSize(12);
            doc.text(reg.name + ' — ' + reg.pdRegister.heading, 14, y); y += 2;
            if (reg.pdRegister.validity) {
                doc.setFontSize(8);
                doc.setTextColor(reg.pdRegister.validity.failed ? 170 : 60, reg.pdRegister.validity.failed ? 40 : 110, reg.pdRegister.validity.failed ? 40 : 60);
                doc.text(reg.pdRegister.validity.message, 14, y); y += 4;
                doc.setTextColor(0);
            }
            doc.autoTable({
                startY: y,
                head: [['Module / scale', 'Keyed items', 'Status']],
                body: reg.pdRegister.rows.map(row => [row.label, row.value, (row.flagged ? '* ' : '') + (row.detail || 'Not flagged')]),
                theme: 'grid',
                styles: { fontSize: 8 },
                columnStyles: { 1: { cellWidth: 24 }, 2: { cellWidth: 60 } }
            });
            y = doc.lastAutoTable.finalY + 4;
            doc.setFontSize(8);
            doc.setTextColor(120);
            doc.text(doc.splitTextToSize('Screening only — not diagnostic and no dimensional score. ' + reg.pdRegister.note, 180), 14, y);
            doc.setTextColor(0);
            y += 12;
        });

        doc.setFontSize(12);
        doc.text('Differential Considerations (hypothesis-generating only)', 14, y); y += 2;
        doc.autoTable({
            startY: y,
            head: [['Tier', 'Condition', 'DSM-5-TR', 'ICD-11', 'Triggering Instruments']],
            body: r.differentials.length
                ? r.differentials.map(d => ['T' + d.tier, d.name.en, d.dsm5, d.icd11, d.sources.join(', ')])
                : [['—', 'No significant flags', '—', '—', '—']],
            theme: 'grid',
            styles: { fontSize: 8 }
        });
        y = doc.lastAutoTable.finalY + 6;

        // Classification governance note (see WHITEPAPER.md Appendix A: Comparative Nosological Index)
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text('Codes are comparative index entries, not a DSM-to-ICD crosswalk. Tier numbers are navigation aids, not prevalence claims.', 14, y); y += 4;
        doc.text('Record the classification system, version and code independently; do not infer a diagnosis from a code label alone.', 14, y); y += 4;
        doc.text('ICD-11 sleep-wake disorders are in Chapter 07 and gender incongruence / sexual dysfunctions in Chapter 17; verify release and local coding rules.', 14, y); y += 4;
        doc.setTextColor(0);
        y += 6;

        if (r.safetyTriggered) {
            doc.setFontSize(11);
            doc.setTextColor(180, 0, 0);
            doc.text('SAFETY FLAG: Patient endorsed one or more crisis items during screening.', 14, y); y += 6;
            doc.setTextColor(0);
        }
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text('This document is a screening aid, not a diagnosis. Clinical judgment is required.', 14, 285);

        doc.save('EPCSS_screening_summary.pdf');
    }

    /* ------------------------------------------------------------------ *
     * 11. EVENT WIRING
     * ------------------------------------------------------------------ */
    function bindStaticUI() {
        document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));
        document.getElementById('lang-hi').addEventListener('click', () => applyLanguage('hi'));

        const contrastBtn = document.getElementById('contrast-toggle');
        contrastBtn.addEventListener('click', () => {
            const on = document.body.classList.toggle('high-contrast');
            contrastBtn.setAttribute('aria-pressed', String(on));
        });

        const consentCheck = document.getElementById('consent-check');
        consentCheck.addEventListener('change', () => {
            document.getElementById('consent-btn').disabled = !consentCheck.checked;
        });

        // Stage 0 -> 1 gate: consent must be actively granted first. The button
        // is normally disabled until the box is checked, but keyboard/AT users
        // (and any future layout where the button stays enabled) get the same
        // standard inline-alert treatment as every other Continue gate.
        const consentError = document.getElementById('consent-error');
        const validateConsent = () => {
            const ok = Boolean(consentCheck.checked);
            if (consentError) consentError.classList.toggle('hidden', ok);
            return ok;
        };
        validateConsent.alertEl = consentError;
        document.getElementById('consent-btn').addEventListener('click', () => {
            continueTo(validateConsent, () => {
                state.consent = true;
                revealStage(1);
            });
        });

        // Stage 1 -> 2 gate: age group is required for adaptive instrument routing.
        const contextAgeError = document.getElementById('context-age-error');
        const validateContext = () => {
            const ok = Boolean(document.getElementById('age-group').value);
            if (contextAgeError) contextAgeError.classList.toggle('hidden', ok);
            return ok;
        };
        validateContext.alertEl = contextAgeError;
        document.getElementById('context-form').addEventListener('submit', e => {
            e.preventDefault();
            continueTo(validateContext, () => {
                state.context.ageGroup = document.getElementById('age-group').value;
                state.context.reason = document.getElementById('visit-reason').value.trim();
                state.context.medications = document.getElementById('medications').value.trim();
                state.context.priorDiagnoses = document.getElementById('prior-diagnoses').value.trim();
                revealStage(2);
            });
        });

        // Stage 2 -> 3 gate: at least one symptom domain must be selected; the
        // scale content is rendered only after the gate passes.
        const domainsError = document.getElementById('domains-error');
        const validateDomains = () => {
            const ok = state.selectedDomains.size > 0;
            domainsError.classList.toggle('hidden', ok);
            return ok;
        };
        validateDomains.alertEl = domainsError;
        document.getElementById('domains-next').addEventListener('click', () => {
            continueTo(validateDomains, () => {
                renderScales();
                revealStage(3);
            });
        });

        // Stage 3 -> 4 gate: every deployed item must be answered before results
        // are computed and revealed.
        const scalesError = document.getElementById('scales-error');
        const validateScales = () => {
            const ok = allAnswered();
            scalesError.classList.toggle('hidden', ok);
            return ok;
        };
        validateScales.alertEl = scalesError;
        document.getElementById('scales-finish').addEventListener('click', () => {
            continueTo(validateScales, () => {
                computeResults();
                renderResults();
                revealStage(4);
            });
        });

        document.getElementById('pdf-btn').addEventListener('click', generatePDF);

        document.getElementById('clear-btn').addEventListener('click', () => {
            // Volatile wipe; tab closure would achieve the same via GC.
            location.reload();
        });

        document.getElementById('safety-close').addEventListener('click', closeSafetyModal);

        // Non-dismissible: ignore backdrop clicks & Escape while open.
        document.getElementById('safety-modal').addEventListener('click', e => {
            if (e.target === e.currentTarget) e.stopPropagation();
        });
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && !document.getElementById('safety-modal').classList.contains('hidden')) {
                e.preventDefault(); // crisis modal cannot be dismissed with Escape
            }
        });
    }

    function allAnswered() {
        for (const domain of CLINICAL_DATA.domains) {
            if (!state.selectedDomains.has(domain.id)) continue;
            if (domain.instrument === 'auto:adhd' && ['pediatric', 'adolescent'].includes(state.context.ageGroup)) {
                const vadrs = CLINICAL_DATA.scales.vadrs;
                for (const part of vadrs.parts)
                    for (const q of part.questions)
                        if (state.responses['vadrs:' + q.id] === undefined) return false;
                continue;
            }
            for (const q of domain.questions)
                if (state.responses[domain.id + ':' + q.id] === undefined) return false;

            // Every optional instrument attached to a screen-in item of this domain
            // must be fully answered before results are shown — scoring a partially
            // completed printed form would misreport its severity bands. Two
            // exceptions: (a) clinician-rated follow-up parts (PDQ-4+ clinical
            // significance, MINI disability register) are completed after the
            // interview, and (b) performance/observer forms keep their own gates.
            if (OPTIONAL_TABLE_ROUTES.includes(domain.instrument)) {
                for (const q of domain.questions) {
                    if (!q.scaleId) continue;
                    const s = CLINICAL_DATA.scales[q.scaleId];
                    if (!s) continue;
                    for (const part of s.parts) {
                        if (part.clinicianRated) continue;
                        for (const item of part.questions) {
                            if (item.nonScored) continue;   // optional clinical tick-box
                            if (state.responses[s.id + ':' + item.id] === undefined) return false;
                        }
                    }
                }
            }
        }
        return true;
    }

    /* ------------------------------------------------------------------ *
     * 12. INIT
     * ------------------------------------------------------------------ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

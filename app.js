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

    function renderScales() {
        const container = document.getElementById('scale-container');
        container.replaceChildren();
        const deployed = routeInstruments();

        deployed.forEach(({ domain, scaleId, instrumentLabel }) => {
            const section = document.createElement('section');
            section.className = 'scale-section';
            section.setAttribute('aria-labelledby', 'scale-h-' + domain.id);

            const h = document.createElement('h3');
            h.id = 'scale-h-' + domain.id;
            h.className = 'scale-heading';
            h.textContent = L(domain.name) + (instrumentLabel ? ' — ' + instrumentLabel : '');
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
    function renderMatrix(section, scale, scaleId) {
        scaleId = scaleId || scale.id;
        scale.parts.forEach(part => {
            const partTitle = document.createElement('h4');
            partTitle.className = 'matrix-part-title';
            partTitle.textContent = L(part.name);
            section.appendChild(partTitle);

            const isPerf = !!part.questions[0] && part.questions[0].isPerformance;
            const cols = isPerf ? scale.performanceOptions : scale.matrixOptions;

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
                const tr = document.createElement('tr');
                if (q.safety) tr.className = 'safety-item';
                const rowHead = document.createElement('th');
                rowHead.scope = 'row';
                rowHead.className = 'sticky-col row-label';
                rowHead.textContent = (idx + 1) + '. ' + L(q.text);
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

            // Domain raw-sum scoring against cutoff (PHQ-9/GAD-7/PCL-5/ISI/AUDIT-C/ASRS/CAARS-style)
            let sum = 0, answered = 0;
            domain.questions.forEach(q => {
                const v = state.responses[domain.id + ':' + q.id];
                if (v !== undefined) { sum += v; answered++; }
            });
            const maxPossible = domain.questions.reduce((m, q) =>
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
                    const v = state.responses[domain.id + ':' + q.id];
                    if ((v || 0) >= 2 && q.disorders) q.disorders.forEach(d => addFlag(d, domain.instrument || domain.id));
                });
            }
            // Resolve the deployed instrument's canonical name from the library
            // (data.json instruments map), falling back to the domain id.
            let instrumentName = (domain.instrument || domain.id);
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

        // Stage 0 -> 1 gate: consent must be actively granted first.
        const validateConsent = () => Boolean(consentCheck.checked);
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

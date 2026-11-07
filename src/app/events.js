import { renderDomainGrid } from './domain-grid.js';
import { firstUnanswered } from './completion.js';
import { applyLanguage } from './i18n.js';
import { revealStage, continueTo } from './navigation.js';
import { generatePDF } from './pdf.js';
import { computeResults } from './results-computation.js';
import { renderResults } from './results-rendering.js';
import { closeSafetyModal } from './safety.js';
import { renderScales } from './scale-rendering.js';
import { state } from './state.js';

/* ------------------------------------------------------------------ *
 * 11. EVENT WIRING
 * ------------------------------------------------------------------ */
function bindStaticUI() {
    document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));
    document.getElementById('lang-hi').addEventListener('click', () => applyLanguage('hi'));

    document.querySelectorAll('[data-back]').forEach(button => {
        button.addEventListener('click', () => revealStage(Number(button.dataset.back)));
    });

    const contrastBtn = document.getElementById('contrast-toggle');
    contrastBtn.addEventListener('click', () => {
        const on = document.body.classList.toggle('high-contrast');
        contrastBtn.setAttribute('aria-pressed', String(on));
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
            renderDomainGrid();
            const contextDetails = document.querySelector('.optional-context');
            if (contextDetails) contextDetails.open = false;
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
    document.getElementById('scales-finish').addEventListener('click', () => {
        const missing = firstUnanswered();
        if (missing) {
            const input = document.getElementsByName(missing)[0];
            scalesError.classList.remove('hidden');
            if (input) {
                const question = input.closest('fieldset, tr');
                question.classList.add('needs-answer');
                input.setAttribute('aria-describedby', scalesError.id);
                input.focus({ preventScroll: true });
                question.scrollIntoView?.({ block: 'center' });
            } else {
                scalesError.focus();
            }
            return;
        }
        scalesError.classList.add('hidden');
        computeResults();
        renderResults();
        revealStage(4);
    });

    document.getElementById('pdf-btn').addEventListener('click', generatePDF);

    document.getElementById('clear-btn').addEventListener('click', () => {
        // Volatile wipe; tab closure would achieve the same via GC.
        location.reload();
    });

    document.getElementById('safety-close').addEventListener('click', closeSafetyModal);

    document.getElementById('safety-modal').addEventListener('keydown', e => {
        if (e.key !== 'Tab') return;
        e.preventDefault();
        document.getElementById('safety-close').focus();
    });

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

export { bindStaticUI };

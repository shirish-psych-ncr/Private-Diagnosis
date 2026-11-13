import { renderScales } from './scale-rendering.js';
import { state, CLINICAL_DATA, questionIsApplicable, requiredQuestionId } from './state.js';
import { syncAssessmentProgress } from './navigation.js';
import { openSafetyModal } from './safety.js';

/** Central answer handler with safety override check. */
function onAnswer(key, value, question, domain) {
    if (Array.isArray(value) && value.length === 0) delete state.responses[key];
    else state.responses[key] = value;
    state.touchedQuestions?.add(key);
    syncAssessmentProgress();
    document.getElementById('scales-error').classList.add('hidden');
    const first = document.getElementsByName(key)[0];
    first?.removeAttribute('aria-describedby');
    first?.closest('fieldset, tr')?.classList.remove('needs-answer');
    const form = CLINICAL_DATA?.scales[domain.id];
    const dependents = form?.parts.flatMap(part => part.questions)
        .filter(item => requiredQuestionId(item, domain.id) === question.id) || [];
    if (dependents.length) {
        for (const item of dependents) {
            if (!questionIsApplicable(item, domain.id)) delete state.responses[domain.id + ':' + item.id];
        }
        renderScales();
        syncAssessmentProgress();
        document.getElementById(key + '_' + value)?.focus({ preventScroll: true });
    }
    if (key === 'cssrs:s2') {
        if (value === 0) {
            for (const id of ['s3', 's4', 's5']) delete state.responses['cssrs:' + id];
        }
        renderScales();
        syncAssessmentProgress();
        document.getElementById(key + '_' + value)?.focus({ preventScroll: true });
    }
    // Safety override: high-risk endorsement halts workflow -> crisis modal.
    const numericAnswer = Number(value);
    const safetyTriggered = question.safety && Number.isFinite(numericAnswer) &&
        (question.safetyMax != null
            ? numericAnswer <= question.safetyMax
            : numericAnswer >= (question.safetyMin ?? 1));
    if (safetyTriggered) {
        if (!state.safetyFlags.some(flag => flag.key === key)) state.safetyFlags.push({ key, domainId: domain.id });
        openSafetyModal();
    }
}

export { onAnswer };

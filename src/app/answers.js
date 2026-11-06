import { renderScales } from './scale-rendering.js';
import { state } from './state.js';
import { openSafetyModal } from './safety.js';

/** Central answer handler with safety override check. */
function onAnswer(key, value, question, domain) {
    state.responses[key] = value;
    document.getElementById('scales-error').classList.add('hidden');
    const first = document.getElementsByName(key)[0];
    first?.removeAttribute('aria-describedby');
    first?.closest('fieldset, tr')?.classList.remove('needs-answer');
    if (key === 'cssrs:s2') {
        if (value === 0) {
            for (const id of ['s3', 's4', 's5']) delete state.responses['cssrs:' + id];
        }
        renderScales();
        document.getElementById(key + '_' + value)?.focus({ preventScroll: true });
    }
    // Safety override: high-risk endorsement halts workflow -> crisis modal.
    if (question.safety && Number(value) >= (question.safetyMin ?? 1)) {
        state.safetyFlags.push({ key, domainId: domain.id });
        openSafetyModal();
    }
}

export { onAnswer };

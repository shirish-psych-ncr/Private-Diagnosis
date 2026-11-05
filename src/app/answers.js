import { state } from './state.js';
import { openSafetyModal } from './safety.js';

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

export { onAnswer };

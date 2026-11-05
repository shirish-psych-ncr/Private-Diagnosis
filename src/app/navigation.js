import { boot } from './bootstrap.js';
import { state } from './state.js';

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

export { revealStage, continueTo };

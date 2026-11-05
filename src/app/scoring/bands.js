import { L } from '../i18n.js';

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

export { bandLabel, severityBand };

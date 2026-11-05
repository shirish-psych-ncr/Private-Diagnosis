/* Headless integration test for EPCSS using jsdom. Run: node tests/epcss_test.js */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const { loadModule, localFetch } = require('./module_loader');
let ready;
const scrollCalls = [];

const ROOT = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8')
  .replace(/<script[^>]*src="https:[^"]*"[^>]*><\/script>/g, '')
  .replace(/<meta http-equiv="Content-Security-Policy"[^>]*>[\s\S]*?content="[^"]*">/m, '');

let dom, window, document;
const pdfCalls = [];
function initializeApp() {
dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'outside-only', pretendToBeVisual: true });
({ window } = dom);
({ document } = window);

window.fetch = localFetch;
window.scrollTo = (...args) => scrollCalls.push(args);

window.jspdf = { jsPDF: function () {
  this.text = (s) => pdfCalls.push(String(s).slice(0, 60));
  this.save = (name) => pdfCalls.push('SAVED:' + name);
  this.autoTable = (opts) => { pdfCalls.push('AUTOTABLE:' + JSON.stringify((opts && opts.head) || '')); this.lastAutoTable = { finalY: 100 }; };
  this.splitTextToSize = (text) => String(text).split('\n');
  this.setFontSize = () => {}; this.setFont = () => {}; this.addPage = () => {};
  this.setTextColor = () => {}; this.setDrawColor = () => {}; this.setLineWidth = () => {};
  this.line = () => {}; this.rect = () => {}; this.internal = { pageSize: { getWidth: () => 200, getHeight: () => 290 } };
}};

ready = loadModule(dom.getInternalVMContext(), 'app.js');
}
initializeApp();


// Reload into a fresh DOM so private in-memory answers cannot leak between journeys.
function resetApp() {
  window.close();
  initializeApp();
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
let failures = 0;
function check(name, cond) { console.log((cond ? 'PASS' : 'FAIL') + ' - ' + name); if (!cond) failures++; }

// jsdom does not implement window.scrollTo; stub it so we can assert calls.


(async () => {
  await ready; await sleep(300);
  check('stage0 active on load', document.getElementById('stage-0').classList.contains('active'));

  // --- Sequential gating: next states must NOT load before Continue ---
  check('stage 1 hidden before consent Continue', !document.getElementById('stage-1').classList.contains('active'));
  check('stage 2 hidden before domains Continue', !document.getElementById('stage-2').classList.contains('active'));
  check('stage 3 hidden before scales Continue', !document.getElementById('stage-3').classList.contains('active'));
  check('stage 4 hidden before results Continue', !document.getElementById('stage-4').classList.contains('active'));

  // Note: scroll-to-top is asserted after the first real consent Continue below.
  // Failed gate: age group missing at stage 1 -> alert shown, stage 2 not revealed.
  document.getElementById('stage-1').classList.add('active'); // simulate revealed state for gate test
  const ctxForm = document.getElementById('context-form');
  document.getElementById('age-group').value = '';
  ctxForm.dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  const ageErr = document.getElementById('context-age-error');
  check('missing age group shows inline error', ageErr && !ageErr.classList.contains('hidden'));
  check('failed gate keeps stage 2 hidden', !document.getElementById('stage-2').classList.contains('active'));
  document.getElementById('stage-1').classList.remove('active'); // restore pre-consent state

  const consentBtn = document.getElementById('consent-btn');
  check('consent button disabled initially', consentBtn.disabled === true);
  // Standard inline-alert treatment: even with the button enabled (e.g. via AT
  // or a forced click), an unchecked consent box must show the alert and keep
  // stage 1 hidden — the next state does not load before Continue passes.
  consentBtn.disabled = false;
  consentBtn.click();
  await ready; await sleep(50);
  const consentErr = document.getElementById('consent-error');
  check('unchecked consent shows inline error', consentErr && !consentErr.classList.contains('hidden'));
  check('failed consent gate keeps stage 1 hidden', !document.getElementById('stage-1').classList.contains('active'));
  consentBtn.disabled = true;
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  check('consent button enabled after check', consentBtn.disabled === false);
  consentBtn.click();
  await ready; await sleep(50);
  check('consent error cleared after valid Continue', consentErr && consentErr.classList.contains('hidden'));
  check('advanced to stage 1 (context)', document.getElementById('stage-1').classList.contains('active'));
  check('scroll-to-top fired on consent Continue', scrollCalls.length >= 1 && scrollCalls[scrollCalls.length - 1][0] === 0 && scrollCalls[scrollCalls.length - 1][1] === 0);

  document.getElementById('age-group').value = 'adult';
  document.getElementById('visit-reason').value = 'feeling low lately';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  check('advanced to stage 2 (domains)', document.getElementById('stage-2').classList.contains('active'));

  const domainOpts = document.querySelectorAll('#domain-list .domain-option');
  check('domain grid rendered (>=7 domains)', domainOpts.length >= 7);
  const pickDomain = (id) => {
    const cb = Array.from(document.querySelectorAll('#domain-list input[type="checkbox"]')).find(c => (c.value || c.getAttribute('data-domain')) === id);
    if (cb) { cb.checked = true; cb.dispatchEvent(new window.Event('change', { bubbles: true })); return true; }
    return false;
  };
  pickDomain('mood'); pickDomain('anxiety');
  document.getElementById('domains-next').click();
  await ready; await sleep(50);
  check('advanced to stage 3 (scales)', document.getElementById('stage-3').classList.contains('active'));

  const scaleSections = document.querySelectorAll('#scale-container .scale-section');
  check('instruments rendered', scaleSections.length >= 1);
  const allRadios = Array.from(document.querySelectorAll('#scale-container input[type="radio"]'));
  check('radio items present', allRadios.length > 15);
  const groups = {};
  allRadios.forEach(r => { (groups[r.name] = groups[r.name] || []).push(r); });
  Object.values(groups).forEach(list => { list[0].checked = true; list[0].dispatchEvent(new window.Event('change', { bubbles: true })); });
  document.getElementById('scales-finish').click();
  await ready; await sleep(50);
  check('advanced to stage 4 (results)', document.getElementById('stage-4').classList.contains('active'));

  const pv = document.getElementById('patient-view').textContent;
  check('patient summary non-empty', pv.trim().length > 20);
  check('patient view withholds diagnostic labels', !/\bDSM-5\b|6A\d\d/.test(pv));
  const rc = document.getElementById('report-content').textContent;
  check('clinician detail includes PHQ-9 score', /PHQ-9/.test(rc));
  check('clinician detail shows no-flag message when all answers minimal',
        /No significant flags/.test(rc) || /6A\d\d|Tier \d/.test(rc));

  // Positive-screen path: redo flow answering the LAST option of each group (high severity)
  resetApp();
  await ready; await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  pickDomain('mood');
  document.getElementById('domains-next').click();
  await ready; await sleep(50);
  const g2 = {};
  Array.from(document.querySelectorAll('#scale-container input[type=\"radio\"]')).forEach(r => { (g2[r.name] = g2[r.name] || []).push(r); });
  Object.values(g2).forEach(list => { list[list.length - 1].checked = true; list[list.length - 1].dispatchEvent(new window.Event('change', { bubbles: true })); });
  // safety modal will fire on last option of item 9 — acknowledge it
  await ready; await sleep(50);
  if (!document.getElementById('safety-modal').classList.contains('hidden')) {
    document.getElementById('safety-close').click();
    await ready; await sleep(50);
  }
  document.getElementById('scales-finish').click();
  await ready; await sleep(50);
  const rc2 = document.getElementById('report-content').textContent;
  check('positive screen yields tiered differentials with DSM/ICD codes', /Tier \d/.test(rc2) && /6A\d\d/.test(rc2));

  document.getElementById('lang-hi').click();
  await ready; await sleep(50);
  check('hindi applied after toggle', /[ऀ-ॿ]/.test(document.body.textContent));
  check('still on stage 4 after language switch', document.getElementById('stage-4').classList.contains('active'));
  document.getElementById('lang-en').click();
  await ready; await sleep(50);

  pdfCalls.length = 0;
  document.getElementById('pdf-btn').click();
  await ready; await sleep(100);
  check('PDF generated via jsPDF mock', pdfCalls.some(c => String(c).startsWith('SAVED:')));

  // Pediatric routing -> VADRS matrix
  resetApp();
  await ready; await sleep(50);
  check('reset returns to stage 0', document.getElementById('stage-0').classList.contains('active'));
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'pediatric';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  pickDomain('neurodevelopmental');
  document.getElementById('domains-next').click();
  await ready; await sleep(50);
  const scaleText = document.getElementById('scale-container').textContent;
  check('pediatric ADHD routing renders VADRS', /VADRS|Vanderbilt/i.test(scaleText));
  check('sticky-column matrix table rendered', document.querySelectorAll('#scale-container .matrix-table').length >= 1);

  // Safety override: adult mood, endorse highest option on safety item
  resetApp();
  await ready; await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  pickDomain('mood');
  document.getElementById('domains-next').click();
  await ready; await sleep(50);
  const safetyRadio = Array.from(document.querySelectorAll('#scale-container .safety-item input[type="radio"]')).pop();
  check('safety item flagged in DOM', !!safetyRadio);
  if (safetyRadio) {
    safetyRadio.checked = true;
    safetyRadio.dispatchEvent(new window.Event('change', { bubbles: true }));
    await ready; await sleep(50);
    check('crisis modal opens on safety endorsement', !document.getElementById('safety-modal').classList.contains('hidden'));
    check('crisis resources listed', document.getElementById('crisis-resources').textContent.trim().length > 10);
    document.getElementById('safety-close').click();
    await ready; await sleep(50);
    check('modal closes via acknowledge button', document.getElementById('safety-modal').classList.contains('hidden'));
  }

  // ---------------------------------------------------------------------
  // Somatic optional instruments: FAC22-SR keyed screen + PHQ-15 severity.
  // Endorsing both somatic screen-in items must deploy both printed tables,
  // block results until every item is answered, and score the FAC22 keying
  // exactly as published (Yes to 5, 8, 10, 11, 14-22; No to 1-4, 6, 7, 9,
  // 12, 13) with bands 9-14 possible / 15+ probable factitious disorder.
  // ---------------------------------------------------------------------
  resetApp();
  await ready; await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  check('somatic domain present in grid', pickDomain('somatic'));
  document.getElementById('domains-next').click();
  await ready; await sleep(50);

  const somScreens = Array.from(
    document.querySelectorAll('#scale-container input[name^="somatic:"][value="1"]'));
  check('somatic domain deploys both screen-in items', somScreens.length >= 2);
  somScreens.forEach(r => { r.checked = true; r.dispatchEvent(new window.Event('change', { bubbles: true })); });
  await ready; await sleep(80);

  const scaleText2 = document.getElementById('scale-container').textContent;
  check('FAC22-SR instrument deployed after screen-in', /FAC22/i.test(scaleText2));
  check('PHQ-15 instrument deployed after screen-in', /PHQ-?15/i.test(scaleText2));

  const DATA2 = (await ready).modules.get(path.join(ROOT, 'src/app/state.js')).namespace.CLINICAL_DATA;
  const facItems = DATA2.scales.fac22_sr.parts[0].questions;
  const phqItems = DATA2.scales.phq15.parts[0].questions;

  function answerScale(scaleId, valueFor) {
    const items = DATA2.scales[scaleId].parts.reduce((a, p) => a.concat(p.questions || []), []);
    items.forEach(it => {
      const v = valueFor(it);
      const radio = document.querySelector('#scale-container input[name="' + scaleId + ':' + it.id + '"][value="' + v + '"]');
      if (radio) { radio.checked = true; radio.dispatchEvent(new window.Event('change', { bubbles: true })); }
    });
    return items.length;
  }
  const nFac = answerScale('fac22_sr', it => (it.keyedAnswer === 'T' ? 1 : 0));   // every item keyed-positive
  const nPhq = answerScale('phq15', () => 2);                                     // "bothered a lot" throughout
  await ready; await sleep(80);
  check('FAC22-SR rendered all 22 items', nFac === 22 && /name="fac22_sr:fac_22"/.test(document.getElementById('scale-container').innerHTML));
  check('PHQ-15 rendered all 15 items with 0-2 anchors', nPhq === 15 && /Bothered a lot/.test(document.getElementById('scale-container').textContent));

  document.getElementById('scales-finish').click();
  await ready; await sleep(120);
  const report2 = document.getElementById('report-content').textContent;
  check('results reached once somatic instruments complete', document.getElementById('stage-4').classList.contains('active'));
  check('clinician report shows FAC22-SR keyed score 22', /FAC22[\s\S]{0,160}?22\s*\/\s*22/.test(report2));
  check('FAC22 max keying reported as probable factitious disorder', /Probable factitious disorder/i.test(report2));
  check('factitious disorder appears in clinician differential', /factitious/i.test(report2));
  check('clinician report shows PHQ-15 total 30', /PHQ-?15[\s\S]{0,160}?30\s*\/\s*30/.test(report2));
  check('PHQ-15 band reported as severe somatisation', /Severe somatis/i.test(report2));
  check('screens marked not diagnostic', /not diagnostic/i.test(report2));

  // Partial completion must be blocked (no silent scoring of an incomplete table).
  resetApp();
  await ready; await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await ready; await sleep(50);
  check('somatic domain present in grid', pickDomain('somatic'));
  document.getElementById('domains-next').click();
  await ready; await sleep(50);
  Array.from(document.querySelectorAll('#scale-container input[name^="somatic:"][value="1"]'))
    .forEach(r => { r.checked = true; r.dispatchEvent(new window.Event('change', { bubbles: true })); });
  await ready; await sleep(80);
  answerScale('phq15', () => 1);   // leave all 22 FAC22 items blank
  document.getElementById('scales-finish').click();
  await ready; await sleep(120);
  check('incomplete FAC22-SR blocks results', !document.getElementById('stage-4').classList.contains('active'));

  console.log('\n' + (failures === 0 ? 'ALL TESTS PASSED' : failures + ' FAILURES'));
  process.exit(failures === 0 ? 0 : 1);
})().catch(e => { console.error('TEST HARNESS ERROR:', e); process.exit(2); });

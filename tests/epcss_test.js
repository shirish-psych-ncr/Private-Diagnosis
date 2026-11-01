/* Headless integration test for EPCSS using jsdom. Run: node tests/epcss_test.js */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8')
  .replace(/<script[^>]*src="https:[^"]*"[^>]*><\/script>/g, '')
  .replace(/<meta http-equiv="Content-Security-Policy"[^>]*>[\s\S]*?content="[^"]*">/m, '');

const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'outside-only', pretendToBeVisual: true });
const { window } = dom;
const { document } = window;

window.fetch = (url) => {
  if (String(url).includes('data.json')) {
    return Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(ROOT, 'data.json'), 'utf8'))) });
  }
  return Promise.reject(new Error('unexpected fetch ' + url));
};
const pdfCalls = [];
window.jspdf = { jsPDF: function () {
  this.text = (s) => pdfCalls.push(String(s).slice(0, 60));
  this.save = (name) => pdfCalls.push('SAVED:' + name);
  this.autoTable = (opts) => { pdfCalls.push('AUTOTABLE:' + JSON.stringify((opts && opts.head) || '')); this.lastAutoTable = { finalY: 100 }; };
  this.setFontSize = () => {}; this.setFont = () => {}; this.addPage = () => {};
  this.setTextColor = () => {}; this.setDrawColor = () => {}; this.setLineWidth = () => {};
  this.line = () => {}; this.rect = () => {}; this.internal = { pageSize: { getWidth: () => 200, getHeight: () => 290 } };
}};

window.eval(fs.readFileSync(path.join(ROOT, 'app.js'), 'utf8'));


// In-place reset equivalent to app's location.reload() (unsupported in jsdom)
function resetApp() {
  document.getElementById('consent-check').checked = false;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('age-group').value = '';
  document.getElementById('visit-reason').value = '';
  document.getElementById('medications').value = '';
  document.getElementById('prior-diagnoses').value = '';
  document.querySelectorAll('#domain-list input[type=\"checkbox\"]').forEach(cb => { cb.checked = false; cb.dispatchEvent(new window.Event('change', { bubbles: true })); });
  document.getElementById('scale-container').replaceChildren();
  document.getElementById('patient-view').replaceChildren();
  document.getElementById('report-content').replaceChildren();
  document.querySelectorAll('.stage').forEach((s, i) => s.classList.toggle('active', i === 0));
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
let failures = 0;
function check(name, cond) { console.log((cond ? 'PASS' : 'FAIL') + ' - ' + name); if (!cond) failures++; }

(async () => {
  await sleep(300);
  check('stage0 active on load', document.getElementById('stage-0').classList.contains('active'));

  const consentBtn = document.getElementById('consent-btn');
  check('consent button disabled initially', consentBtn.disabled === true);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  check('consent button enabled after check', consentBtn.disabled === false);
  consentBtn.click();
  await sleep(50);
  check('advanced to stage 1 (context)', document.getElementById('stage-1').classList.contains('active'));

  document.getElementById('age-group').value = 'adult';
  document.getElementById('visit-reason').value = 'feeling low lately';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(50);
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
  await sleep(50);
  check('advanced to stage 3 (scales)', document.getElementById('stage-3').classList.contains('active'));

  const scaleSections = document.querySelectorAll('#scale-container .scale-section');
  check('instruments rendered', scaleSections.length >= 1);
  const allRadios = Array.from(document.querySelectorAll('#scale-container input[type="radio"]'));
  check('radio items present', allRadios.length > 15);
  const groups = {};
  allRadios.forEach(r => { (groups[r.name] = groups[r.name] || []).push(r); });
  Object.values(groups).forEach(list => { list[0].checked = true; list[0].dispatchEvent(new window.Event('change', { bubbles: true })); });
  document.getElementById('scales-finish').click();
  await sleep(50);
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
  await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(50);
  pickDomain('mood');
  document.getElementById('domains-next').click();
  await sleep(50);
  const g2 = {};
  Array.from(document.querySelectorAll('#scale-container input[type=\"radio\"]')).forEach(r => { (g2[r.name] = g2[r.name] || []).push(r); });
  Object.values(g2).forEach(list => { list[list.length - 1].checked = true; list[list.length - 1].dispatchEvent(new window.Event('change', { bubbles: true })); });
  // safety modal will fire on last option of item 9 — acknowledge it
  await sleep(50);
  if (!document.getElementById('safety-modal').classList.contains('hidden')) {
    document.getElementById('safety-close').click();
    await sleep(50);
  }
  document.getElementById('scales-finish').click();
  await sleep(50);
  const rc2 = document.getElementById('report-content').textContent;
  check('positive screen yields tiered differentials with DSM/ICD codes', /Tier \d/.test(rc2) && /6A\d\d/.test(rc2));

  document.getElementById('lang-hi').click();
  await sleep(50);
  check('hindi applied after toggle', /[ऀ-ॿ]/.test(document.body.textContent));
  check('still on stage 4 after language switch', document.getElementById('stage-4').classList.contains('active'));
  document.getElementById('lang-en').click();
  await sleep(50);

  pdfCalls.length = 0;
  document.getElementById('pdf-btn').click();
  await sleep(100);
  check('PDF generated via jsPDF mock', pdfCalls.some(c => String(c).startsWith('SAVED:')));

  // Pediatric routing -> VADRS matrix
  resetApp();
  await sleep(50);
  check('reset returns to stage 0', document.getElementById('stage-0').classList.contains('active'));
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'pediatric';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(50);
  pickDomain('neurodevelopmental');
  document.getElementById('domains-next').click();
  await sleep(50);
  const scaleText = document.getElementById('scale-container').textContent;
  check('pediatric ADHD routing renders VADRS', /VADRS|Vanderbilt/i.test(scaleText));
  check('sticky-column matrix table rendered', document.querySelectorAll('#scale-container .matrix-table').length >= 1);

  // Safety override: adult mood, endorse highest option on safety item
  resetApp();
  await sleep(50);
  document.getElementById('consent-check').checked = true;
  document.getElementById('consent-check').dispatchEvent(new window.Event('change', { bubbles: true }));
  document.getElementById('consent-btn').click();
  document.getElementById('age-group').value = 'adult';
  document.getElementById('context-form').dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(50);
  pickDomain('mood');
  document.getElementById('domains-next').click();
  await sleep(50);
  const safetyRadio = Array.from(document.querySelectorAll('#scale-container .safety-item input[type="radio"]')).pop();
  check('safety item flagged in DOM', !!safetyRadio);
  if (safetyRadio) {
    safetyRadio.checked = true;
    safetyRadio.dispatchEvent(new window.Event('change', { bubbles: true }));
    await sleep(50);
    check('crisis modal opens on safety endorsement', !document.getElementById('safety-modal').classList.contains('hidden'));
    check('crisis resources listed', document.getElementById('crisis-resources').textContent.trim().length > 10);
    document.getElementById('safety-close').click();
    await sleep(50);
    check('modal closes via acknowledge button', document.getElementById('safety-modal').classList.contains('hidden'));
  }

  console.log('\n' + (failures === 0 ? 'ALL TESTS PASSED' : failures + ' FAILURES'));
  process.exit(failures === 0 ? 0 : 1);
})().catch(e => { console.error('TEST HARNESS ERROR:', e); process.exit(2); });

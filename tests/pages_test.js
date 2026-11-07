const { JSDOM } = require('jsdom');
const fs = require('fs');
const siteJs = fs.readFileSync('site.js', 'utf8');
const pages = ['index.html','library.html','about.html','privacy.html','security.html','contact.html','404.html'];
let fail = 0;

function load(p) {
    const dom = new JSDOM(fs.readFileSync(p, 'utf8'), { url: 'http://localhost:8123/' + p, runScripts: 'outside-only' });
    dom.window.eval(siteJs); // simulate deferred external script execution
    return dom;
}

for (const p of pages) {
    const doc = load(p).window.document;
    const refs = [...doc.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))
        .concat([...doc.querySelectorAll('link[href],script[src]')].map(e => e.getAttribute('href') || e.getAttribute('src')))
        .filter(u => u && u.indexOf('http') !== 0 && u.indexOf('#') !== 0);
    for (const u of refs) {
        if (!fs.existsSync(u)) { console.log('BROKEN REF in', p, '->', u); fail++; }
    }
    if (!doc.querySelector('title')) { console.log('missing title', p); fail++; }
    if (!doc.querySelector('main')) { console.log('missing main', p); fail++; }
    for (const s of doc.querySelectorAll('script')) {
        if (s.textContent.trim().length > 0) { console.log('INLINE SCRIPT in', p); fail++; }
    }
}

for (const [p, expect] of [['about.html','About'], ['privacy.html','Privacy'], ['security.html','Security'], ['contact.html','Contact'], ['index.html', null], ['404.html', null]]) {
    const doc = load(p).window.document;
    const active = doc.querySelector('.site-nav a.active');
    const got = active && active.textContent.trim();
    if (expect === null) {
        if (got) { console.log('unexpected active on', p, got); fail++; }
    } else if (got !== expect) {
        console.log('active nav FAIL on', p, 'expected', expect, 'got', got); fail++;
    }
}

{
    const dom = load('about.html');
    const doc = dom.window.document;
    const search = doc.getElementById('page-search');
    search.value = 'crisis';
    search.dispatchEvent(new dom.window.Event('input'));
    const hidden = doc.querySelectorAll('.topic-list li.search-hidden').length;
    const total = doc.querySelectorAll('.topic-list li').length;
    console.log('search "crisis": hidden', hidden, 'of', total);
    if (hidden >= total || hidden === 0) { console.log('FAIL search filter'); fail++; }
    search.value = '';
    search.dispatchEvent(new dom.window.Event('input'));
    if (doc.querySelectorAll('.topic-list li.search-hidden').length !== 0) { console.log('FAIL search reset'); fail++; }
}

{
    const dom = load('about.html');
    const doc = dom.window.document;
    const toggle = doc.querySelector('.nav-toggle');
    const ul = doc.querySelector('.site-nav ul');
    toggle.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
    if (!ul.classList.contains('open') || toggle.getAttribute('aria-expanded') !== 'true') { console.log('FAIL nav toggle open'); fail++; }
    toggle.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
    if (ul.classList.contains('open') || toggle.getAttribute('aria-expanded') !== 'false') { console.log('FAIL nav toggle close'); fail++; }
}

console.log(fail === 0 ? 'ALL PAGE CHECKS PASSED' : 'PROBLEMS FOUND: ' + fail);
process.exit(fail === 0 ? 0 : 1);

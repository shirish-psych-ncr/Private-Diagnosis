const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const ROOT='/workspace';
const html=fs.readFileSync(path.join(ROOT,'index.html'),'utf8')
 .replace(/<script[^>]*src="https:[^"]*"[^>]*><\/script>/g,'')
 .replace(/<meta http-equiv="Content-Security-Policy"[^>]*>[\s\S]*?content="[^"]*">/m,'');
const dom=new JSDOM(html,{url:'http://localhost/',runScripts:'outside-only',pretendToBeVisual:true});
const {window}=dom,{document}=window;
window.fetch=(u)=>String(u).includes('data.json')?Promise.resolve({ok:true,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(path.join(ROOT,'data.json'),'utf8')))}):Promise.reject(new Error('x'));
window.jspdf={jsPDF:function(){this.text=()=>{};this.save=()=>{};this.autoTable=()=>{};this.setFontSize=()=>{};this.setFont=()=>{};this.addPage=()=>{};this.setTextColor=()=>{};this.setDrawColor=()=>{};this.setLineWidth=()=>{};this.line=()=>{};this.rect=()=>{};this.internal={pageSize:{getWidth:()=>200,getHeight:()=>290}};}};
window.scrollTo=()=>{};
window.eval(fs.readFileSync(path.join(ROOT,'app.js'),'utf8'));
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 await sleep(300);
 document.getElementById('consent-check').checked=true;
 document.getElementById('consent-check').dispatchEvent(new window.Event('change',{bubbles:true}));
 document.getElementById('consent-btn').click();
 document.getElementById('age-group').value='adult';
 document.getElementById('context-form').dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true}));
 await sleep(60);
 const cbs=[...document.querySelectorAll('#domain-list input[type=checkbox]')];
 console.log('domain checkbox values:',cbs.map(c=>c.value));
 const som=cbs.find(c=>c.value==='somatic');
 if(som){som.checked=true;som.dispatchEvent(new window.Event('change',{bubbles:true}));}
 document.getElementById('domains-next').click();
 await sleep(120);
 const cont=document.getElementById('scale-container');
 console.log('--- sections:',[...cont.querySelectorAll('.scale-section h3')].map(h=>h.textContent));
 console.log('--- radio names (first 25):',[...cont.querySelectorAll('input[type=radio]')].slice(0,25).map(i=>i.name+'='+i.value));
 console.log('--- text head:',cont.textContent.slice(0,400).replace(/\s+/g,' '));
 console.log('--- stage2 active?',document.getElementById('stage-2').classList.contains('active'),'stage3?',document.getElementById('stage-3').classList.contains('active'));
 console.log('--- domains-error hidden?',document.getElementById('domains-error').classList.contains('hidden'));
 console.log('--- somatic checked?',som&&som.checked);
 console.log('--- container children:',cont.children.length);
 const somQ=[...document.querySelectorAll('#scale-container input[name^="somatic:"]')];
 console.log('--- somatic radios:',somQ.map(i=>i.name+'='+i.value));
 console.log('--- sections now:',[...cont.querySelectorAll('.scale-section h3')].map(h=>h.textContent));
 console.log('--- stage2?',document.getElementById('stage-2').classList.contains('active'),'stage3?',document.getElementById('stage-3').classList.contains('active'));
})();

let currentLang = 'en';
let currentStage = 0;
let patientData = { age: '', reason: '', domains: [], responses: {} };

function setLanguage(lang) {
    currentLang = lang;
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');
    document.getElementById('lang-hi').classList.toggle('active', lang === 'hi');
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (I18N[lang][key]) el.textContent = I18N[lang][key];
    });
    
    // Re-render dynamic content if on stage 2 or 3
    if (currentStage === 2) renderDomains();
    if (currentStage === 3) renderScales();
    if (currentStage === 4) renderResults();
}

function toggleConsent() {
    document.getElementById('consent-btn').disabled = !document.getElementById('consent-check').checked;
}

function nextStage() {
    document.querySelectorAll('.stage')[currentStage].classList.remove('active');
    document.querySelectorAll('.progress-step')[currentStage].classList.remove('active');
    document.querySelectorAll('.progress-step')[currentStage].classList.add('completed');
    
    currentStage++;
    
    document.querySelectorAll('.stage')[currentStage].classList.add('active');
    document.querySelectorAll('.progress-step')[currentStage].classList.add('active');
    
    if (currentStage === 2) renderDomains();
    if (currentStage === 3) renderScales();
    if (currentStage === 4) renderResults();
}

function saveContext() {
    patientData.age = document.getElementById('age-group').value;
    patientData.reason = document.getElementById('visit-reason').value;
}

function renderDomains() {
    const container = document.getElementById('domain-list');
    container.innerHTML = '';
    
    CLINICAL_DATA.domains.forEach(domain => {
        const div = document.createElement('div');
        div.className = 'domain-card';
        div.innerHTML = `
            <input type="checkbox" id="domain-${domain.id}" value="${domain.id}" onchange="toggleDomain('${domain.id}')">
            <label for="domain-${domain.id}" style="cursor:pointer; flex:1;">
                <strong>${domain.name[currentLang]}</strong>
            </label>
        `;
        container.appendChild(div);
    });
}

function toggleDomain(id) {
    const idx = patientData.domains.indexOf(id);
    if (idx > -1) patientData.domains.splice(idx, 1);
    else patientData.domains.push(id);
}

function generateScaleRecommendations() {
    if (patientData.domains.length === 0) {
        alert(currentLang === 'en' ? 'Please select at least one domain.' : 'कृपया कम से कम एक डोमेन चुनें।');
        return;
    }
    nextStage();
}

function renderScales() {
    const container = document.getElementById('scale-container');
    container.innerHTML = '';
    
    patientData.domains.forEach(domainId => {
        const domain = CLINICAL_DATA.domains.find(d => d.id === domainId);
        domain.scales.forEach(scaleId => {
            const scale = CLINICAL_DATA.scales[scaleId];
            if (!scale.targetAge.includes(patientData.age)) return;
            
            const scaleDiv = document.createElement('div');
            scaleDiv.className = 'scale-wrapper';
            scaleDiv.innerHTML = `
                <div class="scale-header">
                    <h3>${scale.name[currentLang]}</h3>
                    <p>${scale.type === 'matrix' ? (currentLang === 'en' ? 'Rate each behavior and performance area.' : 'प्रत्येक व्यवहार और प्रदर्शन क्षेत्र का मूल्यांकन करें।') : (currentLang === 'en' ? 'Select the option that best describes your experience.' : 'वह विकल्प चुनें जो आपके अनुभव का सबसे अच्छा वर्णन करता है।')}</p>
                </div>
            `;
            
            if (scale.type === 'list') {
                const listDiv = document.createElement('div');
                listDiv.className = 'matrix-container';
                let html = '<table class="matrix-table"><tbody>';
                scale.questions.forEach(q => {
                    html += `<tr><td>${q.text[currentLang]}</td>`;
                    q.options.forEach(opt => {
                        html += `<td><input type="radio" name="${q.id}" value="${opt.v}" onchange="saveResponse('${q.id}', ${opt.v}, ${q.safety || false})"></td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                // Add headers dynamically for list view if needed, or keep simple
                listDiv.innerHTML = html;
                scaleDiv.appendChild(listDiv);
            } else if (scale.type === 'matrix') {
                scale.parts.forEach(part => {
                    const partDiv = document.createElement('div');
                    partDiv.className = 'matrix-container';
                    let html = '<table class="matrix-table"><thead><tr><th></th>';
                    
                    const opts = part.questions[0].isPerformance ? scale.performanceOptions : scale.matrixOptions;
                    opts.forEach(opt => {
                        html += `<th>${opt[currentLang]}</th>`;
                    });
                    html += '</tr></thead><tbody>';
                    
                    part.questions.forEach(q => {
                        html += `<tr><td>${q.text[currentLang]}</td>`;
                        opts.forEach(opt => {
                            html += `<td><input type="radio" name="${q.id}" value="${opt.v}" onchange="saveResponse('${q.id}', ${opt.v}, false)"></td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    partDiv.innerHTML = html;
                    scaleDiv.appendChild(partDiv);
                });
            }
            container.appendChild(scaleDiv);
        });
    });
}

function saveResponse(qId, value, isSafety) {
    patientData.responses[qId] = value;
    if (isSafety && value >= 1) {
        document.getElementById('safety-modal').classList.remove('hidden');
    }
}

function calculateResults() {
    patientData.scores = {};
    patientData.suggestedDisorders = [];
    
    // Simple scoring logic for demonstration
    let phq9Score = 0;
    ['p1', 'p2', 'p9'].forEach(id => { if (patientData.responses[id]) phq9Score += patientData.responses[id]; });
    if (phq9Score >= 10) patientData.suggestedDisorders.push('depression_mdd');
    
    let gad7Score = 0;
    ['g1', 'g2'].forEach(id => { if (patientData.responses[id]) gad7Score += patientData.responses[id]; });
    if (gad7Score >= 6) patientData.suggestedDisorders.push('anxiety_gad');
    
    // VADRS simplified logic: count "Often" (2) or "Very Often" (3) for inattention
    let inattentionCount = 0;
    for (let i = 1; i <= 9; i++) {
        if (patientData.responses[`v${i}`] >= 2) inattentionCount++;
    }
    if (inattentionCount >= 6) patientData.suggestedDisorders.push('neuro_adhd');
}

function renderResults() {
    const container = document.getElementById('report-content');
    let html = `
        <div class="report-section">
            <h3>${currentLang === 'en' ? 'Patient Context' : 'रोगी संदर्भ'}</h3>
            <p><strong>${currentLang === 'en' ? 'Age Group:' : 'आयु वर्ग:'}</strong> ${patientData.age}</p>
            <p><strong>${currentLang === 'en' ? 'Reason for Visit:' : 'आगमन का कारण:'}</strong> ${patientData.reason || (currentLang === 'en' ? 'Not provided' : 'प्रदान नहीं किया गया')}</p>
        </div>
        <div class="report-section">
            <h3>${currentLang === 'en' ? 'Suggested Diagnostic Considerations' : 'सुझाए गए नैदानिक विचार'}</h3>
    `;
    
    if (patientData.suggestedDisorders.length === 0) {
        html += `<p>${currentLang === 'en' ? 'No specific disorder thresholds were met based on screening responses.' : 'स्क्रीनिंग प्रतिक्रियाओं के आधार पर कोई विशिष्ट विकार सीमा पूरी नहीं हुई।'}</p>`;
    } else {
        // Sort by tier
        const disorders = patientData.suggestedDisorders.map(id => CLINICAL_DATA.disorders[id]).sort((a, b) => a.tier - b.tier);
        disorders.forEach(d => {
            html += `
                <div class="report-item">
                    <span class="report-tier">Tier ${d.tier}</span>
                    <strong>${d.name[currentLang]}</strong><br>
                    <small>DSM-5-TR: ${d.dsm5} | ICD-11: ${d.icd11}</small>
                </div>
            `;
        });
    }
    html += `</div>`;
    container.innerHTML = html;
}

function generatePDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.setFontSize(18);
    doc.text("Clinical Pre-Consultation Summary", 14, 20);
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 28);
    doc.text("CONFIDENTIAL: For clinician review only.", 14, 34);
    
    doc.setFontSize(12);
    doc.text("Patient Context", 14, 45);
    doc.setFontSize(10);
    doc.text(`Age Group: ${patientData.age}`, 14, 52);
    doc.text(`Reason: ${patientData.reason || 'N/A'}`, 14, 58);
    
    const tableData = patientData.suggestedDisorders.map(id => {
        const d = CLINICAL_DATA.disorders[id];
        return [`Tier ${d.tier}`, d.name.en, d.dsm5, d.icd11];
    });
    
    if (tableData.length > 0) {
        doc.autoTable({
            startY: 65,
            head: [['Tier', 'Condition', 'DSM-5-TR', 'ICD-11']],
            body: tableData,
            theme: 'grid',
            headStyles: { fillColor: [44, 90, 160] }
        });
    } else {
        doc.text("No specific disorder thresholds met.", 14, 75);
    }
    
    doc.setFontSize(8);
    doc.text("Disclaimer: This is an automated screening summary, not a diagnosis. Clinical correlation required.", 14, doc.internal.pageSize.height - 10);
    
    doc.save("clinical-screening-summary.pdf");
}

// Initialize
setLanguage('en');

/* ═══════════════════════════════════════════════════════════════
   MediReport AI — Frontend Application Logic
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = window.location.port === '3000'
  ? 'http://127.0.0.1:8000'
  : (window.location.origin && window.location.origin.startsWith('http') ? window.location.origin : 'http://127.0.0.1:8000');

/* ── State ── */
let currentJobId   = null;
let selectedFile   = null;
let procStepTimer  = null;

/* ── DOM refs ── */
const uploadZone      = document.getElementById('uploadZone');
const fileInput       = document.getElementById('fileInput');
const fileSelected    = document.getElementById('fileSelected');
const fileNameEl      = document.getElementById('fileName');
const fileSizeEl      = document.getElementById('fileSize');
const removeFileBtn   = document.getElementById('removeFile');
const analyzeBtn      = document.getElementById('analyzeBtn');
const processingOverlay = document.getElementById('processingOverlay');
const procTitle       = document.getElementById('procTitle');
const procSub         = document.getElementById('procSub');
const resultsSection  = document.getElementById('resultsSection');
const riskGrid        = document.getElementById('riskGrid');
const rawTableBody    = document.getElementById('rawTableBody');
const patName         = document.getElementById('patName');
const patAge          = document.getElementById('patAge');
const patGender       = document.getElementById('patGender');
const dlEnBtn         = document.getElementById('dlEnBtn');
const dlHiBtn         = document.getElementById('dlHiBtn');
const newUploadBtn    = document.getElementById('newUploadBtn');
const errorToast      = document.getElementById('errorToast');
const toastMsg        = document.getElementById('toastMsg');
const langEnLabel     = document.getElementById('langEn');
const langHiLabel     = document.getElementById('langHi');
const nav             = document.getElementById('nav');

/* ════════════════════════════════════════════
   PARTICLE CANVAS
   ════════════════════════════════════════════ */
(function initParticles() {
  const canvas = document.getElementById('particleCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const count = 90;
  const particles = Array.from({ length: count }, () => ({
    x:  Math.random() * canvas.width,
    y:  Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.35,
    vy: (Math.random() - 0.5) * 0.35,
    r:  Math.random() * 1.8 + 0.5,
    a:  Math.random() * 0.55 + 0.1,
  }));

  const colors = ['#06b6d4', '#6366f1', '#8b5cf6', '#10b981'];

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // connect nearby
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(99,102,241,${0.12 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.6;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    particles.forEach((p, i) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = colors[i % colors.length].replace(')', `,${p.a})`).replace('rgb', 'rgba').replace('#', '');
      // simple hex → rgba shortcut via CSS
      ctx.fillStyle = colors[i % colors.length];
      ctx.globalAlpha = p.a;
      ctx.fill();
      ctx.globalAlpha = 1;

      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    });

    requestAnimationFrame(draw);
  }
  draw();
})();

/* ════════════════════════════════════════════
   NAV SCROLL
   ════════════════════════════════════════════ */
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
});

/* ════════════════════════════════════════════
   HERO CARD 3-D MOUSE TILT
   ════════════════════════════════════════════ */
(function initCardTilt() {
  const card = document.getElementById('heroCard');
  if (!card) return;
  document.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top  + rect.height / 2;
    const dx = (e.clientX - cx) / window.innerWidth;
    const dy = (e.clientY - cy) / window.innerHeight;
    card.style.transform = `rotateY(${-12 + dx * 12}deg) rotateX(${4 - dy * 8}deg)`;
  });
})();

/* ════════════════════════════════════════════
   LANG TOGGLE
   ════════════════════════════════════════════ */
document.querySelectorAll('input[name="lang"]').forEach(radio => {
  radio.addEventListener('change', () => {
    langEnLabel.classList.toggle('active', radio.value === 'en' && radio.checked);
    langHiLabel.classList.toggle('active', radio.value === 'hi' && radio.checked);
  });
});
langEnLabel.addEventListener('click', () => {
  langEnLabel.classList.add('active');
  langHiLabel.classList.remove('active');
  langEnLabel.querySelector('input').checked = true;
});
langHiLabel.addEventListener('click', () => {
  langHiLabel.classList.add('active');
  langEnLabel.classList.remove('active');
  langHiLabel.querySelector('input').checked = true;
});

/* ════════════════════════════════════════════
   FILE SELECTION
   ════════════════════════════════════════════ */
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function setFile(file) {
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Only PDF files are supported.');
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    showToast('File is too large. Maximum size is 20 MB.');
    return;
  }
  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatBytes(file.size);
  uploadZone.classList.add('hidden');
  fileSelected.classList.remove('hidden');
}

fileInput.addEventListener('change', e => {
  if (e.target.files[0]) setFile(e.target.files[0]);
});

uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') fileInput.click(); });

// Drag & Drop
uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

removeFileBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  fileSelected.classList.add('hidden');
  uploadZone.classList.remove('hidden');
});

/* ════════════════════════════════════════════
   PROCESSING ANIMATION
   ════════════════════════════════════════════ */
const procSteps = [
  { el: document.getElementById('pStep1'), title: 'Reading PDF', sub: 'Reading pages and preparing image renders…' },
  { el: document.getElementById('pStep2'), title: 'Extracting values', sub: 'Running OCR & NLP biomarker extraction…' },
  { el: document.getElementById('pStep3'), title: 'Running AI models', sub: 'Evaluating diagnostic models for Diabetes, Heart & Liver…' },
  { el: document.getElementById('pStep4'), title: 'Building summary', sub: 'Calculating SHAP explainability drivers and finalizing report…' },
];

let procElapsedSec = 0;
let procElapsedTimer = null;

function startProcessingAnim() {
  procElapsedSec = 0;
  clearInterval(procStepTimer);
  clearInterval(procElapsedTimer);

  procSteps.forEach(s => {
    if (s.el) {
      s.el.classList.remove('active', 'done');
      const dot = s.el.querySelector('.proc-dot');
      if (dot) dot.style.animation = '';
    }
  });

  if (procSteps[0].el) procSteps[0].el.classList.add('active');
  procSub.textContent = procSteps[0].sub;

  procElapsedTimer = setInterval(() => {
    procElapsedSec++;
    if (procElapsedSec >= 2 && procElapsedSec < 12) {
      // Step 2: OCR extraction (takes the longest)
      if (procSteps[0].el) { procSteps[0].el.classList.remove('active'); procSteps[0].el.classList.add('done'); }
      if (procSteps[1].el) { procSteps[1].el.classList.add('active'); }
      procSub.textContent = `Running OCR & biomarker extraction (${procElapsedSec}s elapsed — scanning pages)…`;
    } else if (procElapsedSec >= 12 && procElapsedSec < 20) {
      // Step 3: Running AI models
      if (procSteps[1].el) { procSteps[1].el.classList.remove('active'); procSteps[1].el.classList.add('done'); }
      if (procSteps[2].el) { procSteps[2].el.classList.add('active'); }
      procSub.textContent = `Running AI diagnostic models (${procElapsedSec}s elapsed)…`;
    } else if (procElapsedSec >= 20) {
      // Step 4: Finalizing & calculating SHAP
      if (procSteps[2].el) { procSteps[2].el.classList.remove('active'); procSteps[2].el.classList.add('done'); }
      if (procSteps[3].el) { procSteps[3].el.classList.add('active'); }
      procSub.textContent = `Calculating risk factors & finalizing summary (${procElapsedSec}s elapsed)…`;
    }
  }, 1000);
}

function stopProcessingAnim(success = true) {
  clearInterval(procStepTimer);
  clearInterval(procElapsedTimer);
  if (success) {
    procSteps.forEach(s => {
      if (s.el) {
        s.el.classList.remove('active');
        s.el.classList.add('done');
      }
    });
    procSub.textContent = 'Analysis complete! Rendering results…';
  }
}

/* ════════════════════════════════════════════
   ANALYSE
   ════════════════════════════════════════════ */
analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) { showToast('Please select a PDF first.'); return; }

  // Show overlay
  processingOverlay.classList.remove('hidden');
  procTitle.textContent = 'Analyzing Your Report';
  startProcessingAnim();

  // Scroll to top of page so overlay is centered
  window.scrollTo({ top: 0, behavior: 'smooth' });

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const targetUrl = API_BASE ? `${API_BASE}/analyze` : '/analyze';
    console.log('[MediReport] Uploading PDF to:', targetUrl);

    const res = await fetch(targetUrl, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server returned error ${res.status}`);
    }

    const data = await res.json();
    console.log('[MediReport] Analysis response received:', data);

    stopProcessingAnim(true);
    await sleep(400);

    processingOverlay.classList.add('hidden');
    currentJobId = data.job_id;
    renderResults(data);
  } catch (err) {
    console.error('[MediReport] Analysis error:', err);
    stopProcessingAnim(false);
    processingOverlay.classList.add('hidden');
    showToast(err.message || 'Analysis failed. Please verify the server is running.');
  }
});

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ════════════════════════════════════════════
   RENDER RESULTS
   ════════════════════════════════════════════ */
const DISEASE_ICONS = {
  'Diabetes': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 6v4l3 3"/></svg>`,
  'Heart Disease': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>`,
  'Liver Disease': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="12" rx="9" ry="7"/><path d="M3 12c0-2.5 4-5 9-5s9 2.5 9 5"/></svg>`,
  'Heart': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>`,
  'Liver': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="12" rx="9" ry="7"/><path d="M3 12c0-2.5 4-5 9-5s9 2.5 9 5"/></svg>`,
};

const RISK_MAP = {
  GREEN:  { cls: 'risk-green',  label: 'Low Risk',      barColor: '#10b981' },
  YELLOW: { cls: 'risk-yellow', label: 'Moderate Risk', barColor: '#f59e0b' },
  RED:    { cls: 'risk-red',    label: 'High Risk',      barColor: '#ef4444' },
};

function renderResults(data) {
  try {
    // Patient info
    const p = data.patient_info || {};
    patName.innerHTML   = `Patient: <span>${p.Name || 'Not specified'}</span>`;
    patAge.innerHTML    = `Age: <span>${p.Age != null ? p.Age + ' yrs' : 'Not specified'}</span>`;
    const genderLabel   = p.Gender === 1 ? 'Male' : (p.Gender === 0 ? 'Female' : 'Not specified');
    patGender.innerHTML = `Gender: <span>${genderLabel}</span>`;

    // Risk cards
    riskGrid.innerHTML = '';
    const predictions = data.predictions || {};

    for (const [disease, info] of Object.entries(predictions)) {
      const rm       = RISK_MAP[info.risk_color] || { cls: 'risk-green', label: 'Unknown', barColor: '#6366f1' };
      const prob     = ((info.probability || 0) * 100).toFixed(1);
      const status   = info.prediction === 1 ? 'Positive' : 'Negative';
      const icon     = DISEASE_ICONS[disease] || DISEASE_ICONS['Diabetes'];

      const realTags = (info.real_data_features || [])
        .map(f => `<span class="rc-feat-tag real">${f}</span>`).join('');
      const defTags  = (info.default_features || [])
        .map(f => `<span class="rc-feat-tag default">${f}</span>`).join('');

      const shapRows = (info.top_shap_drivers || [])
        .map(([feat, val]) => {
          const numVal = Number(val) || 0;
          return `
          <div class="rc-shap-row">
            <span class="shap-name">${feat}</span>
            <span class="shap-val ${numVal > 0 ? 'shap-up' : 'shap-down'}">${numVal > 0 ? '↑' : '↓'} ${Math.abs(numVal).toFixed(4)}</span>
          </div>`;
        }).join('');

      const warnHtml = info.low_confidence
        ? `<div class="low-conf-warn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>Limited real report data detected — default baseline values were used.</div>`
        : '';

      const card = document.createElement('div');
      card.className = `risk-card ${rm.cls}`;
      card.innerHTML = `
        <div class="rc-top">
          <div class="rc-icon">${icon}</div>
          <div class="rc-name">${disease}<br/><small style="font-weight:500;color:var(--muted);font-size:0.78rem;">${status}</small></div>
          <div class="rc-badge">${rm.label}</div>
        </div>
        <div class="rc-prob-label">
          <span>Risk probability</span><span>${prob}%</span>
        </div>
        <div class="rc-bar-bg">
          <div class="rc-bar-fill" style="width:0%;background:${rm.barColor};" data-width="${prob}%"></div>
        </div>
        <button class="rc-expand-btn" onclick="toggleDetails(this)">
          View details
          <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="rc-details">
          ${warnHtml}
          <div class="rc-detail-section">
            <div class="rc-detail-title">Data from your report</div>
            <div class="rc-feat-tags">${realTags || '<span class="rc-feat-tag">None detected</span>'}</div>
          </div>
          <div class="rc-detail-section">
            <div class="rc-detail-title">Estimated / default baseline values</div>
            <div class="rc-feat-tags">${defTags || '<span class="rc-feat-tag">None</span>'}</div>
          </div>
          <div class="rc-detail-section">
            <div class="rc-detail-title">Top contributing factors (SHAP)</div>
            ${shapRows || '<p style="font-size:0.78rem;color:var(--muted)">No SHAP data</p>'}
          </div>
        </div>
      `;
      riskGrid.appendChild(card);
    }

    // Animate bars after rendering
    requestAnimationFrame(() => {
      document.querySelectorAll('.rc-bar-fill[data-width]').forEach(el => {
        el.style.width = el.dataset.width;
      });
    });

    // Raw tests table
    rawTableBody.innerHTML = '';
    const testsList = Array.isArray(data.extracted_tests)
      ? data.extracted_tests
      : Object.entries(data.extracted_tests || {}).map(([k, v]) => ({ test: k, value: v, unit: '' }));

    if (testsList.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="2" style="text-align:center;color:var(--muted);padding:16px;">No standard blood biomarkers were identified in this document. Baseline estimates were applied.</td>`;
      rawTableBody.appendChild(tr);
    } else {
      for (const item of testsList) {
        const tr = document.createElement('tr');
        const unitHtml = item.unit ? ` <span style="font-size:0.75rem;color:var(--muted);font-weight:normal;">${item.unit}</span>` : '';
        tr.innerHTML = `<td><strong>${item.test || 'Test'}</strong></td><td>${item.value != null ? item.value : '—'}${unitHtml}</td>`;
        rawTableBody.appendChild(tr);
      }
    }

    // Show results section and scroll there
    resultsSection.classList.remove('hidden');
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 150);
  } catch (renderErr) {
    console.error('[MediReport] Error rendering results:', renderErr);
    showToast('Render error: ' + renderErr.message);
  }
}

/* ── Toggle detail panel ── */
window.toggleDetails = function(btn) {
  const details = btn.nextElementSibling;
  const isOpen  = details.classList.toggle('open');
  btn.classList.toggle('open', isOpen);
  btn.childNodes[0].textContent = isOpen ? 'Hide details ' : 'View details ';
};

/* ════════════════════════════════════════════
   DOWNLOAD PDF
   ════════════════════════════════════════════ */
async function downloadPdf(lang) {
  if (!currentJobId) { showToast('No analysis result available. Please analyze a report first.'); return; }
  const btn = lang === 'en' ? dlEnBtn : dlHiBtn;
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation:orbSpin 1s linear infinite"><circle cx="12" cy="12" r="10" stroke-opacity="0.3"/><path d="M12 2a10 10 0 0 1 10 10"/></svg> Generating…`;

  try {
    const res = await fetch(`${API_BASE}/report/${currentJobId}?language=${lang}`);
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const blob  = await res.blob();
    const url   = URL.createObjectURL(blob);
    const a     = document.createElement('a');
    a.href      = url;
    a.download  = lang === 'en' ? 'MediReport_English.pdf' : 'MediReport_Hindi.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    showToast('PDF download failed: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

dlEnBtn.addEventListener('click', () => downloadPdf('en'));
dlHiBtn.addEventListener('click', () => downloadPdf('hi'));

/* ════════════════════════════════════════════
   NEW UPLOAD
   ════════════════════════════════════════════ */
newUploadBtn.addEventListener('click', () => {
  resultsSection.classList.add('hidden');
  riskGrid.innerHTML = '';
  rawTableBody.innerHTML = '';
  currentJobId  = null;
  selectedFile  = null;
  fileInput.value = '';
  fileSelected.classList.add('hidden');
  uploadZone.classList.remove('hidden');
  document.getElementById('upload-section').scrollIntoView({ behavior: 'smooth' });
});

/* ════════════════════════════════════════════
   TOAST
   ════════════════════════════════════════════ */
let toastTimer = null;
function showToast(msg) {
  toastMsg.textContent = msg;
  errorToast.classList.remove('hidden');
  requestAnimationFrame(() => errorToast.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    errorToast.classList.remove('show');
    setTimeout(() => errorToast.classList.add('hidden'), 350);
  }, 4000);
}

/* ════════════════════════════════════════════
   SCROLL-IN ANIMATIONS (IntersectionObserver)
   ════════════════════════════════════════════ */
(function initScrollReveal() {
  const items = document.querySelectorAll('.step-card, .feat-card, .stat-pill');
  items.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  });

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  items.forEach(el => observer.observe(el));
})();

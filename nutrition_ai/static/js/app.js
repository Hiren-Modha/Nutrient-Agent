/**
 * NutriBot — IBM Granite Nutrition AI
 * Frontend Application Logic
 */

'use strict';

// ─── State ────────────────────────────────────────────────────────────────────
let currentStep    = 1;
let selectedGoal   = 'Maintain a healthy lifestyle';
let lastPlanText   = '';
let lastPlanFile   = '';

// ─── Navigation ───────────────────────────────────────────────────────────────
function showSection(name) {
  document.querySelectorAll('.section').forEach(s => {
    s.classList.remove('active');
    s.classList.add('hidden');
  });
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  const sec = document.getElementById('section-' + name);
  if (sec) { sec.classList.remove('hidden'); sec.classList.add('active'); }

  const btn = [...document.querySelectorAll('.nav-btn')]
    .find(b => b.textContent.toLowerCase().includes(name === 'plan' ? 'generate' : name));
  if (btn) btn.classList.add('active');

  if (name === 'history') loadSavedPlans();
}

// ─── Multi-step Form ──────────────────────────────────────────────────────────
function goStep(n) {
  // Validate current step before advancing
  if (n > currentStep) {
    if (!validateStep(currentStep)) return;
  }

  // Hide current, show target
  document.getElementById('form-step-' + currentStep).classList.add('hidden');
  document.getElementById('form-step-' + n).classList.remove('hidden');

  // Update step dots
  for (let i = 1; i <= 4; i++) {
    const dot = document.getElementById('step-dot-' + i);
    dot.classList.remove('active', 'done');
    if (i < n)       dot.classList.add('done');
    else if (i === n) dot.classList.add('active');
  }
  currentStep = n;
}

function validateStep(step) {
  if (step === 1) {
    const name    = val('name');
    const age     = val('age');
    const city    = val('city');
    const country = val('country');
    if (!name || name.length < 2)       { alert('Please enter your name (at least 2 characters).'); return false; }
    if (!age || +age < 2 || +age > 120) { alert('Please enter a valid age (2–120).'); return false; }
    if (!city)                          { alert('Please enter your city.'); return false; }
    if (!country)                       { alert('Please enter your country.'); return false; }
  }
  return true;
}

// ─── Goal Selection ────────────────────────────────────────────────────────────
function selectGoal(btn, goal) {
  document.querySelectorAll('.goal-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  selectedGoal = goal;
}

// ─── Generate Plan ─────────────────────────────────────────────────────────────
async function generatePlan() {
  const diet = document.querySelector('input[name="diet"]:checked')?.value || 'vegetarian';

  const payload = {
    name:             val('name'),
    age:              val('age'),
    weight:           val('weight'),
    height:           val('height'),
    city:             val('city'),
    country:          val('country'),
    diet_preference:  diet,
    medical_history:  val('medical_history'),
    allergies:        val('allergies'),
    goals:            val('custom_goal') || selectedGoal,
  };

  // Show step 4 with loading state
  goStep(4);
  showLoadingState();

  try {
    // Animate loading steps
    await animateLoadingSteps();

    const res  = await fetch('/api/generate-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.success) {
      lastPlanText = data.plan;
      lastPlanFile = data.filepath || '';
      showResultState(data);
    } else {
      showErrorState(data.error || 'An unexpected error occurred.');
    }
  } catch (err) {
    showErrorState('Network error: ' + err.message + '. Please ensure the server is running.');
  }
}

function showLoadingState() {
  document.getElementById('loading-state').classList.remove('hidden');
  document.getElementById('result-state').classList.add('hidden');
  document.getElementById('error-state').classList.add('hidden');
  // Reset steps
  ['ls1','ls2','ls3','ls4'].forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove('active');
    el.textContent = el.textContent.replace('✓ ','').replace('⟳ ','').trim();
    if (id !== 'ls1') el.textContent = '⟳ ' + el.textContent;
    else el.textContent = '⟳ Validating profile';
  });
}

async function animateLoadingSteps() {
  const steps = [
    { id: 'ls1', label: '✓ Validating profile',              delay: 600  },
    { id: 'ls2', label: '✓ Running safety guardrails',       delay: 1200 },
    { id: 'ls3', label: '✓ Generating plan with IBM Granite',delay: 2500 },
    { id: 'ls4', label: '✓ Saving to Markdown file',         delay: 500  },
  ];
  for (const s of steps) {
    await sleep(s.delay);
    const el = document.getElementById(s.id);
    el.classList.add('active');
    el.textContent = s.label;
  }
}

function showResultState(data) {
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('result-state').classList.remove('hidden');
  document.getElementById('error-state').classList.add('hidden');

  if (data.filepath) {
    document.getElementById('filepath-bar').textContent = '💾 Saved: ' + data.filepath;
    document.getElementById('filepath-bar').classList.remove('hidden');
  }

  const out = document.getElementById('plan-output');
  out.innerHTML = markdownToHtml(data.plan);
}

function showErrorState(msg) {
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('result-state').classList.add('hidden');
  document.getElementById('error-state').classList.remove('hidden');
  document.getElementById('error-msg').textContent = msg;
}

// ─── Chat / Q&A ───────────────────────────────────────────────────────────────
async function sendQuery() {
  const input = document.getElementById('chat-input');
  const question = input.value.trim();
  if (!question) return;

  input.value = '';
  document.getElementById('quick-chips').style.display = 'none';

  appendChatMsg('user', question);
  const typingId = appendTyping();

  try {
    const res  = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();

    removeTyping(typingId);

    if (data.success) {
      appendChatMsg('bot', data.answer);
    } else {
      appendChatMsg('bot', '⚠️ ' + (data.error || 'Sorry, I could not answer that question.'));
    }
  } catch (err) {
    removeTyping(typingId);
    appendChatMsg('bot', '⚠️ Connection error. Please check that the server is running.');
  }
}

function askChip(el) {
  document.getElementById('chat-input').value = el.textContent;
  sendQuery();
}

function appendChatMsg(role, text) {
  const msgs    = document.getElementById('chat-messages');
  const div     = document.createElement('div');
  div.className = 'chat-msg ' + role;

  const avatar  = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'bot' ? '🤖' : '👤';

  const bubble  = document.createElement('div');
  bubble.className = 'msg-bubble';

  // Simple formatting: split on newlines
  text.split('\n').filter(l => l.trim()).forEach(line => {
    const p = document.createElement('p');
    p.innerHTML = escapeHtml(line)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
    bubble.appendChild(p);
  });

  div.appendChild(avatar);
  div.appendChild(bubble);
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function appendTyping() {
  const msgs    = document.getElementById('chat-messages');
  const id      = 'typing-' + Date.now();
  const div     = document.createElement('div');
  div.id        = id;
  div.className = 'chat-msg bot msg-typing';
  div.innerHTML = '<div class="msg-avatar">🤖</div><div class="msg-bubble"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>';
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ─── Saved Plans ──────────────────────────────────────────────────────────────
async function loadSavedPlans() {
  const container = document.getElementById('plans-list');
  container.innerHTML = '<p class="loading-text">Loading saved plans…</p>';

  try {
    const res  = await fetch('/api/plans');
    const data = await res.json();

    if (!data.plans || data.plans.length === 0) {
      container.innerHTML = '<p class="loading-text" style="text-align:center;margin-top:40px">No saved plans yet. Generate your first plan! 🥗</p>';
      return;
    }

    container.innerHTML = '';
    data.plans.forEach(name => {
      const parts = name.replace('nutrition_plan_', '').replace('.md', '').split('_');
      const ts    = parts.slice(-2).join('_');
      const uname = parts.slice(0, -2).join(' ');
      const date  = formatTimestamp(ts);

      const item = document.createElement('div');
      item.className = 'plan-item';
      item.innerHTML = `
        <div class="plan-item-info">
          <strong>📄 ${name}</strong>
          <small>👤 ${uname} &nbsp;|&nbsp; 📅 ${date}</small>
        </div>
        <button class="btn-secondary" onclick="viewSavedPlan('${encodeURIComponent(name)}')">View Plan</button>
      `;
      container.appendChild(item);
    });
  } catch {
    container.innerHTML = '<p style="color:red;text-align:center">Error loading plans.</p>';
  }
}

async function viewSavedPlan(encodedName) {
  const name = decodeURIComponent(encodedName);
  const res  = await fetch('/api/plans/' + encodeURIComponent(name));
  const data = await res.json();

  if (data.content) {
    // Switch to plan section and show content
    showSection('plan');
    goStep(4);
    lastPlanText = data.content;
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('result-state').classList.remove('hidden');
    document.getElementById('error-state').classList.add('hidden');
    document.getElementById('filepath-bar').textContent = '📂 Viewing: ' + name;
    document.getElementById('plan-output').innerHTML = markdownToHtml(data.content);
  }
}

// ─── Copy & Download ──────────────────────────────────────────────────────────
function copyPlan() {
  navigator.clipboard.writeText(lastPlanText)
    .then(() => { alert('Plan copied to clipboard!'); })
    .catch(() => { alert('Could not copy. Please select and copy manually.'); });
}

function downloadPlan() {
  const blob = new Blob([lastPlanText], { type: 'text/markdown' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'my_nutrition_plan.md';
  a.click();
  URL.revokeObjectURL(url);
}

function resetForm() {
  ['name','age','weight','height','city','country','medical_history','allergies','custom_goal']
    .forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
  document.querySelector('input[name="diet"][value="vegetarian"]').checked = true;
  document.querySelectorAll('.goal-btn').forEach((b,i) => {
    b.classList.toggle('active', i === 0);
  });
  selectedGoal = 'Maintain a healthy lifestyle';
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function val(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatTimestamp(ts) {
  try {
    const [d, t] = ts.split('_');
    const date = d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6,8);
    const time = t.slice(0,2)+':'+t.slice(2,4)+':'+t.slice(4,6);
    return new Date(date+'T'+time).toLocaleString();
  } catch { return ts; }
}

/**
 * Minimal Markdown → HTML renderer (no external deps)
 */
function markdownToHtml(md) {
  let html = md
    // Code blocks
    .replace(/```[\s\S]*?```/g, m => '<pre><code>' + escapeHtml(m.slice(3,-3).replace(/^\w+\n/,'')) + '</code></pre>')
    // YAML front-matter (strip)
    .replace(/^---[\s\S]*?---\n?/, '')
    // H1-H3
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm,  '<h2>$1</h2>')
    .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
    // Bold/italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g,     '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,         '<em>$1</em>')
    // Tables
    .replace(/\|(.+)\|\n\|[-| :]+\|\n((?:\|.+\|\n?)+)/g, (_, header, rows) => {
      const ths = header.split('|').filter(c => c.trim()).map(c => `<th>${c.trim()}</th>`).join('');
      const trs = rows.trim().split('\n').map(r => {
        const tds = r.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
        return `<tr>${tds}</tr>`;
      }).join('');
      return `<table><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`;
    })
    // Blockquotes
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Unordered lists
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr/>')
    // Line breaks → paragraphs
    .split('\n\n')
    .map(block => {
      block = block.trim();
      if (!block) return '';
      if (/^<(h[1-6]|ul|ol|li|table|pre|blockquote|hr)/.test(block)) return block;
      if (block.includes('<li>')) return `<ul>${block}</ul>`;
      return `<p>${block.replace(/\n/g, '<br/>')}</p>`;
    })
    .join('\n');

  return html;
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Keyboard shortcut: Enter in chat
  const ci = document.getElementById('chat-input');
  if (ci) ci.addEventListener('keydown', e => { if(e.key === 'Enter') sendQuery(); });
});

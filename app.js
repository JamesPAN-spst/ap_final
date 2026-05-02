// ===== AP2 Mock Exam Web App =====
// Charge data/exams.json, affiche un devoir, corrige automatiquement
// les QCM et réponses courtes, et propose auto-évaluation pour les
// questions de code.

const state = {
  data: null,
  currentSet: null,
  answers: {},      // q.id -> {value, selfEval: 'yes'|'no'|null}
  submitted: false,
};

const DATA_VERSION = '2026-05-02-handwritten-v1';

// ----------------- Util -----------------
const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function md(text) {
  if (window.marked) return marked.parse(text);
  return `<pre>${text.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))}</pre>`;
}

// Normalise pour comparaison (réponse courte) : trim, espaces multiples → un seul,
// supprime espaces dans les listes/sets/tuples Python.
function normalize(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*/g, ',')
    .replace(/\s*:\s*/g, ':')
    .replace(/\(\s*/g, '(').replace(/\s*\)/g, ')')
    .replace(/\[\s*/g, '[').replace(/\s*\]/g, ']')
    .replace(/\{\s*/g, '{').replace(/\s*\}/g, '}')
    .toLowerCase();
}

// Pour les sets Python {1,2,3} ↔ {3,2,1}, on essaye aussi un ordre canonique.
function normalizeSet(s) {
  const m = String(s).trim().match(/^\{(.*)\}$/);
  if (!m) return null;
  if (m[1].includes(':')) return null; // c'est un dict
  const parts = m[1].split(',').map(x => x.trim()).filter(x => x.length).sort();
  return '{' + parts.join(',') + '}';
}

function answersEqual(user, expected) {
  if (!user) return false;
  const u = normalize(user), e = normalize(expected);
  if (u === e) return true;
  // Egalité ensembliste pour les sets
  const us = normalizeSet(user), es = normalizeSet(expected);
  if (us && es && us === es) return true;
  // 'true' ⇔ 'vrai', 'false' ⇔ 'faux'
  const map = {
    'vrai': 'true', 'faux': 'false', 'oui': 'true', 'non': 'false',
    '是': 'true', '否': 'false', '对': 'true', '错': 'false',
    '正确': 'true', '错误': 'false', '真': 'true', '假': 'false'
  };
  if ((map[u] || u) === (map[e] || e)) return true;
  return false;
}

// ----------------- Render -----------------
function renderSetPicker() {
  const nav = $('#set-picker');
  nav.innerHTML = '';
  for (let i = 1; i <= state.data.meta.sets_count; i++) {
    const btn = document.createElement('button');
    btn.textContent = `第 ${i} 套`;
    btn.dataset.id = i;
    btn.onclick = () => loadSet(i);
    nav.appendChild(btn);
  }
}

function loadSet(setId) {
  state.currentSet = state.data.sets.find(s => s.id === setId);
  state.answers = {};
  state.submitted = false;
  $$('#set-picker button').forEach(b => b.classList.toggle('active', +b.dataset.id === setId));
  renderExam();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderExam() {
  const main = $('#app');
  const set = state.currentSet;
  main.innerHTML = `
    <div class="exam-header">
      <div class="exam-title">
        <h2>${set.title}</h2>
        ${set.focus ? `<p class="exam-focus">${escapeHtml(set.focus)}</p>` : ''}
      </div>
      <div class="actions">
        <button class="primary" id="btn-submit">提交并批改</button>
        <button class="ghost" id="btn-reset">重新作答</button>
        <button class="ghost" id="btn-print-questions">打印题目</button>
        <button class="ghost" id="btn-print-answers">打印答案</button>
      </div>
    </div>
    <div id="score-zone"></div>
    <div id="questions"></div>
    <div class="exam-header" style="margin-top: 18px;">
      <span style="color:#666">本套试卷结束。</span>
      <div class="actions">
        <button class="primary" id="btn-submit2">提交并批改</button>
        <button class="ghost" id="btn-print-questions2">打印题目</button>
        <button class="ghost" id="btn-print-answers2">打印答案</button>
      </div>
    </div>
  `;
  const qzone = $('#questions');
  set.questions.forEach((q, i) => qzone.appendChild(renderQuestion(q, i + 1)));
  $('#btn-submit').onclick = $('#btn-submit2').onclick = submit;
  $('#btn-reset').onclick = () => loadSet(set.id);
  $('#btn-print-questions').onclick = $('#btn-print-questions2').onclick = () => printExam('questions');
  $('#btn-print-answers').onclick = $('#btn-print-answers2').onclick = () => printExam('answers');
}

function answerDisplay(q) {
  if (q.type === 'mcq') {
    const idx = q.answer.charCodeAt(0) - 65;
    return `<code>${escapeHtml(q.answer)}.</code> ${escapeHtml(q.choices[idx] || '')}`;
  }
  return `<code>${escapeHtml(q.answer || '(voir explication)')}</code>`;
}

function renderQuestion(q, num) {
  const div = document.createElement('div');
  div.className = 'q-card';
  div.id = `q-${q.id}`;
  const chapNames = { 1: 'CH1 类型', 2: 'CH2 函数', 3: 'CH3 抽象类型', 4: 'CH4 类与对象' };

  let inputHTML = '';
  if (q.type === 'mcq') {
    inputHTML = '<ul class="choices">' + q.choices.map((c, i) => {
      const letter = String.fromCharCode(65 + i);
      return `<li><label>
        <input type="radio" name="q-${q.id}" value="${letter}">
        <span><strong>${letter}.</strong> ${escapeHtml(c)}</span>
      </label></li>`;
    }).join('') + '</ul>';
  } else if (q.type === 'short') {
    inputHTML = `<input type="text" class="short-input" name="q-${q.id}" placeholder="输入答案..." autocomplete="off">`;
  } else if (q.type === 'code') {
    inputHTML = `<textarea class="short-input" rows="6" name="q-${q.id}" placeholder="在这里写代码(提交后再手动自评)..."></textarea>`;
  }

  div.innerHTML = `
    <div class="q-head">
      <span><strong>Q${num}.</strong>
        <span class="q-tag ch${q.chapter}">${chapNames[q.chapter]}</span>
        <span class="q-tag">${q.topic}</span>
        <span class="q-tag">难度 ${q.difficulty}</span>
      </span>
      <span style="color:#aaa">id ${q.id}</span>
    </div>
    <div class="q-body">${md(q.statement_md)}</div>
    ${inputHTML}
    <div class="feedback-zone"></div>
    <div class="print-solution">
      <div><strong>参考答案:</strong> ${answerDisplay(q)}</div>
      <div><strong>解析:</strong> ${md(q.explanation_md || '')}</div>
    </div>
  `;

  // Bind input change → state
  div.querySelectorAll('input,textarea').forEach(el => {
    el.addEventListener('input', () => {
      const v = el.type === 'radio'
        ? (div.querySelector('input[type=radio]:checked')?.value || '')
        : el.value;
      state.answers[q.id] = state.answers[q.id] || {};
      state.answers[q.id].value = v;
    });
  });

  return div;
}

function escapeHtml(s) {
  return String(s).replace(/[<>&"']/g, c => ({
    '<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;',"'":'&#39;'
  }[c]));
}

// ----------------- Submit & grading -----------------
function submit() {
  state.submitted = true;
  const set = state.currentSet;
  let auto_correct = 0, auto_total = 0, manual_total = 0;
  const byChapter = {1:[0,0],2:[0,0],3:[0,0],4:[0,0]}; // [correct, total auto]

  set.questions.forEach(q => {
    const card = $(`#q-${q.id}`);
    const fb = card.querySelector('.feedback-zone');
    const userAns = (state.answers[q.id]?.value || '').trim();
    let isCorrect = null;

    if (q.type === 'mcq' || q.type === 'short') {
      auto_total++;
      byChapter[q.chapter][1]++;
      isCorrect = answersEqual(userAns, q.answer);
      if (isCorrect) {
        auto_correct++;
        byChapter[q.chapter][0]++;
      }
    } else {
      manual_total++;
    }

    card.classList.remove('correct', 'incorrect');
    if (isCorrect === true)  card.classList.add('correct');
    if (isCorrect === false) card.classList.add('incorrect');

    let label;
    if (isCorrect === true)  label = '<strong class="label" style="color:#2ec27e">✓ 正确</strong>';
    else if (isCorrect === false) label = '<strong class="label" style="color:#e54848">✗ 错误</strong>';
    else label = '<strong class="label" style="color:#666">📝 需自评</strong>';

    let userDisplay = userAns ? `<code>${escapeHtml(userAns)}</code>` : '<em>(未作答)</em>';
    const expectedHTML = answerDisplay(q);

    fb.innerHTML = `
      <div class="feedback ${isCorrect===true?'correct':isCorrect===false?'incorrect':''}">
        <div>${label} &nbsp; <strong>你的答案:</strong> ${userDisplay}</div>
        <div style="margin-top:4px"><strong>参考答案:</strong> ${expectedHTML}</div>
        <details ${isCorrect===false?'open':''} style="margin-top:6px">
          <summary>解析 / 讲解</summary>
          <div style="margin-top:6px">${md(q.explanation_md || '')}</div>
        </details>
        ${q.type === 'code' ? `
          <div class="self-eval">
            <button class="sel-yes" data-q="${q.id}" data-v="yes">我做对了 ✓</button>
            <button class="sel-no"  data-q="${q.id}" data-v="no">我做错了 ✗</button>
          </div>
        ` : ''}
      </div>
    `;
  });

  // Bind self-eval buttons
  $$('.self-eval button').forEach(btn => {
    btn.onclick = () => {
      const qid = btn.dataset.q, v = btn.dataset.v;
      state.answers[qid] = state.answers[qid] || {};
      state.answers[qid].selfEval = v;
      btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateScore(); // recompute including self-eval
    };
  });

  renderScore(auto_correct, auto_total, manual_total, byChapter);
}

function printExam(mode) {
  document.body.classList.remove('print-questions', 'print-answers');
  document.body.classList.add(mode === 'answers' ? 'print-answers' : 'print-questions');
  window.print();
  setTimeout(() => document.body.classList.remove('print-questions', 'print-answers'), 500);
}

function updateScore() {
  const set = state.currentSet;
  let auto_correct = 0, auto_total = 0, manual_yes = 0, manual_total = 0;
  const byChapter = {1:[0,0],2:[0,0],3:[0,0],4:[0,0]};
  set.questions.forEach(q => {
    const userAns = (state.answers[q.id]?.value || '').trim();
    if (q.type === 'mcq' || q.type === 'short') {
      auto_total++; byChapter[q.chapter][1]++;
      if (answersEqual(userAns, q.answer)) {
        auto_correct++; byChapter[q.chapter][0]++;
      }
    } else {
      manual_total++;
      const ev = state.answers[q.id]?.selfEval;
      if (ev === 'yes') {
        manual_yes++; byChapter[q.chapter][0]++; byChapter[q.chapter][1]++;
      } else if (ev === 'no') {
        byChapter[q.chapter][1]++;
      }
    }
  });
  renderScore(auto_correct + manual_yes, auto_total + manual_total, 0, byChapter);
}

function renderScore(correct, total, manualPending, byChapter) {
  const zone = $('#score-zone');
  const pct = total ? Math.round(100 * correct / total) : 0;
  const chapNames = { 1: 'CH1 类型', 2: 'CH2 函数', 3: 'CH3 抽象类型', 4: 'CH4 类与对象' };
  zone.innerHTML = `
    <div class="score-card">
      <div>得分</div>
      <div class="big">${correct} / ${total} <span style="font-size:24px;opacity:0.8">(${pct}%)</span></div>
      ${manualPending ? `<div style="opacity:0.85">另有 ${manualPending} 道代码题需在下方手动自评</div>` : ''}
      <div class="by-chapter">
        ${[1,2,3,4].map(c => {
          const [cc, tt] = byChapter[c];
          return `<div>${chapNames[c]} : <strong>${cc}/${tt}</strong></div>`;
        }).join('')}
      </div>
    </div>
  `;
}

// ----------------- Boot -----------------
async function boot() {
  try {
    const r = await fetch(`data/exams.json?v=${DATA_VERSION}`, { cache: 'no-store' });
    state.data = await r.json();
    renderSetPicker();
  } catch (e) {
    $('#app').innerHTML = `<div class="exam-header" style="color:#c00">
      ⚠️ 无法加载 <code>data/exams.json</code>。<br>
      如果你是直接用 <code>file://</code> 打开页面,浏览器通常会拦截 <code>fetch</code>。<br>
      请先启动一个本地服务器:<br>
      <pre>cd web; python -m http.server 8000</pre>
      然后打开 <code>http://localhost:8000</code>。<br><br>
      细节: ${e.message}
    </div>`;
  }
}
boot();

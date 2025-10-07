// app/static/app.js
const $  = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const apiBase = window.location.origin;

let token = localStorage.getItem('sap_token') || null;
function authHeader() { return token ? { 'Authorization': 'Bearer ' + token } : {}; }

async function fetchJSON(path, options = {}) {
  const res = await fetch(apiBase + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
      ...(options.headers || {})
    }
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`HTTP ${res.status}: ${t}`);
  }
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

/* ===================== ATHLETES ===================== */
async function loadAthletes() {
  const items = await fetchJSON('/api/v1/athletes');
  const tbody = $('#athletesTable tbody');
  tbody.innerHTML = '';
  const selPlan = $('#planAthlete');
  const selSess = $('#sessAthlete');
  const selSessForm = $('#sessionAthleteSelect');
  if (selPlan) selPlan.innerHTML = '';
  if (selSess) selSess.innerHTML = '';
  if (selSessForm) selSessForm.innerHTML = '';

  items.forEach((a) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${a.id}</td>
      <td>${a.name}</td>
      <td>${a.level || ''}</td>
      <td>${a.weekly_availability}</td>
      <td>${a.goal || ''}</td>
      <td><button class="ghost" data-id="${a.id}">Delete</button></td>`;
    tbody.appendChild(tr);

    const opt = new Option(a.name, a.id);
    if (selPlan) selPlan.add(opt.cloneNode(true));
    if (selSess) selSess.add(opt.cloneNode(true));
    if (selSessForm) selSessForm.add(opt.cloneNode(true));
  });

  tbody.querySelectorAll('button[data-id]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-id');
      if (!confirm('Delete athlete #' + id + '?')) return;
      await fetchJSON('/api/v1/athletes/' + id, { method: 'DELETE' });
      loadAthletes();
    });
  });
}

async function createAthlete(e) {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.weekly_availability = Number(data.weekly_availability || 4);
  await fetchJSON('/api/v1/athletes', { method: 'POST', body: JSON.stringify(data) });
  e.target.reset();
  loadAthletes();
}

/* ===================== PLANS ===================== */
async function generatePlan() {
  const id = $('#planAthlete')?.value;
  const weeks = Number($('#planWeeks')?.value || 6);
  if (!id) return;
  const plan = await fetchJSON(`/api/v1/plans/generate?athlete_id=${id}&weeks=${weeks}`, { method: 'POST' });
  const micro = JSON.parse(plan.microcycles);
  const tb = $('#planTable tbody');
  tb.innerHTML = '';
  micro.forEach((d) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${d.date}</td><td>${d.type}</td><td>${d.rounds}</td><td>${d.minutes}</td><td>${d.rpe}</td>`;
    tb.appendChild(tr);
  });
}

function clearPlan() { const tb = $('#planTable tbody'); if (tb) tb.innerHTML = ''; }

/* ===================== SESSIONS ===================== */
async function loadSessions() {
  const id = $('#sessAthlete')?.value;
  if (!id) return;
  let path = `/api/v1/sessions/athlete/${id}`;
  const from = $('#sessFrom')?.value, to = $('#sessTo')?.value;
  const qs = [];
  if (from) qs.push('from=' + from);
  if (to) qs.push('to=' + to);
  if (qs.length) path += '?' + qs.join('&');

  const rows = await fetchJSON(path);
  const tb = $('#sessionsTable tbody');
  tb.innerHTML = '';
  rows.forEach((s) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.date}</td><td>${s.type}</td><td>${s.rounds}</td><td>${s.minutes}</td><td>${s.rpe ?? ''}</td><td>${s.notes ?? ''}</td>`;
    tb.appendChild(tr);
  });
}

async function createSession(e) {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.athlete_id = Number(data.athlete_id);
  data.rounds = Number(data.rounds || 0);
  data.minutes = Number(data.minutes || 0);
  data.rpe = data.rpe ? Number(data.rpe) : null;
  await fetchJSON('/api/v1/sessions', { method: 'POST', body: JSON.stringify(data) });
  loadSessions();
}

/* ===================== EXERCISES (with fallback badge) ===================== */
async function loadRandomExercise() {
  const m = $('#ex-muscle')?.value;
  const d = $('#ex-difficulty')?.value;
  const qs = [];
  if (m) qs.push('muscle=' + encodeURIComponent(m));
  if (d) qs.push('difficulty=' + encodeURIComponent(d));
  const url = '/api/v1/exercise/random' + (qs.length ? `?${qs.join('&')}` : '');

  try {
    const res = await fetch(apiBase + url, { headers: { 'Content-Type': 'application/json', ...authHeader() }});
    const source = res.headers.get('X-Exercise-Source') || '';
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    const ex = await res.json();
    const badge = source === 'fallback' ? `<span class="badge">offline</span>` :
                  source === 'cache' ? `<span class="badge">cached</span>` : '';
    $('#exResult').innerHTML =
      `<div style="padding:8px 10px">
        <b>${ex.name}</b> ${badge} • ${ex.muscle || ''}/${ex.difficulty || ''}<br>
        <small>${ex.type || ''}</small><br><br>${ex.instructions || ''}
      </div>`;
  } catch (e) {
    $('#exResult').innerHTML = `<div style="color:#b91c1c;font-weight:700">${e.message}</div>`;
  }
}

async function searchExercise() {
  const m = $('#ex-muscle')?.value;
  const d = $('#ex-difficulty')?.value;
  const qs = [];
  if (m) qs.push('muscle=' + encodeURIComponent(m));
  if (d) qs.push('difficulty=' + encodeURIComponent(d));
  const url = '/api/v1/exercise' + (qs.length ? `?${qs.join('&')}` : '');

  try {
    const res = await fetch(apiBase + url, { headers: { 'Content-Type': 'application/json', ...authHeader() }});
    const source = res.headers.get('X-Exercise-Source') || '';
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    const list = await res.json();
    if (!Array.isArray(list) || list.length === 0) { $('#exResult').textContent = 'No results'; return; }
    const badge = source === 'fallback' ? `<span class="badge">offline</span>` :
                  source === 'cache' ? `<span class="badge">cached</span>` : '';
    const html = list.slice(0, 8)
      .map(x => `<tr><td>${x.name}</td><td>${x.muscle || ''}</td><td>${x.difficulty || ''}</td><td>${x.type || ''}</td></tr>`)
      .join('');
    $('#exResult').innerHTML =
      `${badge}
       <table>
         <thead><tr><th>Name</th><th>Muscle</th><th>Difficulty</th><th>Type</th></tr></thead>
         <tbody>${html}</tbody>
       </table>`;
  } catch (e) {
    $('#exResult').innerHTML = `<div style="color:#b91c1c;font-weight:700">${e.message}</div>`;
  }
}

/* ===================== ROUTER: Login-first UX ===================== */
function updateNavVisibility(isLoggedIn) {
  // hide protected links when logged out
  ['#nav-dashboard', '#nav-sessions', '#nav-exercises'].forEach((id) => {
    const el = document.querySelector(id);
    if (el) el.style.display = isLoggedIn ? 'inline-block' : 'none';
  });
  const loginLink = document.querySelector('#nav-login');
  if (loginLink) loginLink.style.display = isLoggedIn ? 'none' : 'inline-block';
}

function showPage(p) {
  const protectedPages = ['dashboard', 'sessions', 'exercises'];
  const isLoggedIn = !!token;

  if (protectedPages.includes(p) && !isLoggedIn) p = 'login';

  $$('.page').forEach((el) => el.classList.remove('active'));
  const target = document.querySelector(`[data-page="${p}"]`);
  if (target) target.classList.add('active');

  $$('.top a').forEach((a) => a.classList.remove('active'));
  const nav = document.getElementById('nav-' + p);
  if (nav) nav.classList.add('active');

  updateNavVisibility(isLoggedIn);

  if (p === 'dashboard' && isLoggedIn) loadAthletes();
  if (p === 'sessions' && isLoggedIn) loadAthletes().then(() => loadSessions());
}

function logout() {
  localStorage.removeItem('sap_token');
  token = null;
  location.hash = '#/login';
  showPage('login');
}

window.addEventListener('hashchange', () => {
  const p = location.hash.replace('#/', '') || 'login';
  showPage(p);
});

document.addEventListener('DOMContentLoaded', () => {
  // do not auto-redirect to dashboard on load; always land on login unless the URL says otherwise
  if (!location.hash) location.hash = '#/login';
  showPage(location.hash.replace('#/', ''));

  // Wire up UI actions
  $('#generatePlan')?.addEventListener('click', generatePlan);
  $('#clearPlan')?.addEventListener('click', clearPlan);
  $('#athleteForm')?.addEventListener('submit', createAthlete);
  $('#refreshSessions')?.addEventListener('click', loadSessions);
  $('#sessionForm')?.addEventListener('submit', createSession);
  $('#btnExRandom')?.addEventListener('click', loadRandomExercise);
  $('#btnExSearch')?.addEventListener('click', searchExercise);
});

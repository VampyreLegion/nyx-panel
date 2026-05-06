'use strict';

const POLL_INTERVAL = 5000;
const LOGS_REFRESH  = 4000;
let lastStatus = {};
let sysinfoCache = {};
let activeModalMachine = null;
let activeTab = 'memory';

// logs state
let logsTimer = null;
let logsContext = null; // {machine, service, type}

// ── HELPERS ──────────────────────────────────────────────────────────────
function stateClass(state) {
  if (state === 'running')  return 'running';
  if (state === 'stopped' || state === 'inactive') return 'stopped';
  if (state === 'error'   || state === 'failed')   return 'error';
  if (state === 'starting' || state === 'activating') return 'starting';
  if (state === 'restarting') return 'starting';
  return 'unknown';
}
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
function slug(s) { return s.replace(/[^a-z0-9]/gi, '-'); }
function getIP(key) {
  return { nyx: '192.168.1.236', astraea: '192.168.1.109', selene: '192.168.1.25' }[key] || '';
}

// ── RENDER CARDS ─────────────────────────────────────────────────────────
function renderServiceCard(machineKey, svc) {
  const cls  = stateClass(svc.state);
  const sl   = slug(svc.name);
  const link = svc.url
    ? `<a class="service-link" href="${svc.url}" target="_blank" rel="noopener" title="${svc.url}">↗</a>`
    : '';
  const startBtn   = `<button class="btn-start"   data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="start"   ${svc.state==='running'  ?'disabled':''}>Start</button>`;
  const stopBtn    = `<button class="btn-stop"    data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="stop"    ${svc.state==='stopped'  ?'disabled':''}>Stop</button>`;
  const restartBtn = `<button class="btn-restart" data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="restart">↺</button>`;
  const logsBtn    = `<button class="btn-logs"    data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}">Logs</button>`;
  const desc = svc.desc ? `<div class="service-desc">${svc.desc}</div>` : '';

  return `
    <div class="service-card" id="card-${machineKey}-${sl}">
      <div class="card-top">
        <div class="status-dot ${cls}"></div>
        <div class="service-info">
          <span class="service-name">${svc.label || svc.name}</span>
          ${desc}
        </div>
        <div class="card-right">
          ${link}
          <div class="service-btns">${logsBtn}${startBtn}${stopBtn}${restartBtn}</div>
        </div>
      </div>
    </div>
    <div class="service-error hidden" id="err-${machineKey}-${sl}"></div>`;
}

function renderMachine(key, data) {
  const uptime = data.uptime ? `<span>${data.uptime}</span>` : '';
  const rebootDis = !data.reachable ? 'disabled' : '';
  const header = `
    <div class="machine-header">
      <div>
        <div class="machine-name">${cap(key)}</div>
        <div class="machine-meta">${getIP(key)} ${uptime}</div>
      </div>
      <div class="machine-actions">
        <button class="btn-sysinfo" data-machine="${key}">Deep Dive</button>
        <button class="btn-reboot"  data-machine="${key}" ${rebootDis}>Reboot</button>
      </div>
    </div>`;
  if (!data.reachable && !(data.services||[]).length)
    return `<div class="machine-col">${header}<div class="unreachable-banner">⚠ Unreachable</div></div>`;
  const cards = (data.services||[]).map(s => renderServiceCard(key, s)).join('');
  return `<div class="machine-col">${header}<div class="services-list">${cards}</div></div>`;
}

function renderAll(status) {
  document.getElementById('machines-grid').innerHTML =
    ['nyx','astraea','selene'].map(k => renderMachine(k, status[k]||{reachable:false,services:[]})).join('');
  attachHandlers();
}

function updateDOM(newStatus) {
  if (JSON.stringify(newStatus) === JSON.stringify(lastStatus)) return;
  lastStatus = newStatus;
  renderAll(newStatus);
}

// ── FETCH STATUS ─────────────────────────────────────────────────────────
async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error(res.status);
    updateDOM(await res.json());
    document.getElementById('last-refresh').textContent = 'Updated ' + new Date().toLocaleTimeString();
  } catch {
    document.getElementById('last-refresh').textContent = '⚠ Fetch failed';
  }
}

// ── ACTIONS ──────────────────────────────────────────────────────────────
async function sendAction(machine, service, type, action) {
  const res = await fetch('/api/action', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({machine, service, type, action}),
  });
  return res.json();
}

async function sendReboot(machine) {
  const res = await fetch('/api/reboot', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({machine}),
  });
  return res.json();
}

function showError(machine, service, msg) {
  const el = document.getElementById(`err-${machine}-${slug(service)}`);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 5000);
}

function attachHandlers() {
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const {machine, service, type, action} = btn.dataset;
      btn.disabled = true;
      try {
        const r = await sendAction(machine, service, type, action);
        if (!r.ok) showError(machine, service, r.error || 'failed');
        else setTimeout(fetchStatus, 800);
      } catch { showError(machine, service, 'network error'); }
      finally  { btn.disabled = false; }
    });
  });

  document.querySelectorAll('.btn-reboot').forEach(btn => {
    btn.addEventListener('click', async () => {
      const machine = btn.dataset.machine;
      if (!confirm(`Reboot ${machine}? This will briefly disconnect services.`)) return;
      btn.disabled = true;
      await sendReboot(machine);
      setTimeout(fetchStatus, 5000);
    });
  });

  document.querySelectorAll('.btn-sysinfo').forEach(btn =>
    btn.addEventListener('click', () => openSysinfo(btn.dataset.machine)));

  document.querySelectorAll('.btn-logs').forEach(btn =>
    btn.addEventListener('click', () => openLogs(btn.dataset.machine, btn.dataset.service, btn.dataset.type)));
}

// ── SYSINFO MODAL ────────────────────────────────────────────────────────
async function openSysinfo(machineKey) {
  closeLogs();
  activeModalMachine = machineKey;
  document.getElementById('modal-title').textContent = cap(machineKey) + ' — System Info';
  document.getElementById('sysinfo-modal').classList.remove('hidden');
  document.getElementById('modal-backdrop').classList.remove('hidden');
  await loadTab(activeTab);
}

function closeSysinfo() {
  document.getElementById('sysinfo-modal').classList.add('hidden');
  document.getElementById('modal-backdrop').classList.add('hidden');
  activeModalMachine = null;
  sysinfoCache = {};
}

async function loadTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  const pre = document.getElementById('modal-pre');
  if (sysinfoCache[activeModalMachine]?.[tab] !== undefined) {
    pre.textContent = sysinfoCache[activeModalMachine][tab] || '(empty)';
    return;
  }
  pre.textContent = 'Loading...';
  try {
    const res  = await fetch(`/api/sysinfo/${activeModalMachine}`);
    const data = await res.json();
    sysinfoCache[activeModalMachine] = data.data || {};
    pre.textContent = sysinfoCache[activeModalMachine][tab] || '(no data)';
  } catch { pre.textContent = 'Failed to fetch.'; }
}

// ── LOGS MODAL ───────────────────────────────────────────────────────────
async function fetchLogs(scrollToBottom = false) {
  if (!logsContext) return;
  const {machine, service, type} = logsContext;
  try {
    const res  = await fetch(`/api/logs/${machine}/${service}?type=${type}&lines=100`);
    const data = await res.json();
    const pre  = document.getElementById('logs-pre');
    const wasAtBottom = pre.parentElement.scrollTop + pre.parentElement.clientHeight >= pre.parentElement.scrollHeight - 20;
    pre.textContent = data.logs || '(no logs)';
    if (scrollToBottom || wasAtBottom) pre.parentElement.scrollTop = pre.parentElement.scrollHeight;
  } catch { document.getElementById('logs-pre').textContent = 'Failed to fetch logs.'; }
}

function startLogsPolling() {
  stopLogsPolling();
  if (document.getElementById('logs-follow').checked)
    logsTimer = setInterval(fetchLogs, LOGS_REFRESH);
}
function stopLogsPolling() {
  if (logsTimer) { clearInterval(logsTimer); logsTimer = null; }
}

function openLogs(machine, service, type) {
  closeSysinfo();
  logsContext = {machine, service, type};
  const label = lastStatus[machine]?.services?.find(s=>s.name===service)?.label || service;
  document.getElementById('logs-modal-title').textContent = `${cap(machine)} — ${label} logs`;
  document.getElementById('logs-modal').classList.remove('hidden');
  document.getElementById('modal-backdrop').classList.remove('hidden');
  document.getElementById('logs-follow').checked = true;
  fetchLogs(true);
  startLogsPolling();
}

function closeLogs() {
  stopLogsPolling();
  logsContext = null;
  document.getElementById('logs-modal').classList.add('hidden');
  document.getElementById('modal-backdrop').classList.add('hidden');
}

// ── INIT ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  fetchStatus();
  setInterval(fetchStatus, POLL_INTERVAL);

  document.getElementById('refresh-btn').addEventListener('click', fetchStatus);

  document.getElementById('modal-close').addEventListener('click', closeSysinfo);
  document.getElementById('logs-close').addEventListener('click', closeLogs);
  document.getElementById('modal-backdrop').addEventListener('click', () => { closeSysinfo(); closeLogs(); });

  document.querySelectorAll('.tab-btn').forEach(btn =>
    btn.addEventListener('click', () => loadTab(btn.dataset.tab)));

  document.getElementById('logs-follow').addEventListener('change', startLogsPolling);
});

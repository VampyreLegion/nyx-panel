'use strict';

const POLL_INTERVAL = 5000;
let lastStatus = {};
let sysinfoCache = {};
let activeModalMachine = null;
let activeTab = 'memory';

// ── RENDER ──────────────────────────────────────────────────────────────
function stateClass(state) {
  if (state === 'running') return 'running';
  if (state === 'stopped' || state === 'inactive') return 'stopped';
  if (state === 'error' || state === 'failed') return 'error';
  if (state === 'starting' || state === 'activating') return 'starting';
  return 'unknown';
}

function renderMachineKey(key) {
  return key.charAt(0).toUpperCase() + key.slice(1);
}

function renderServiceCard(machineKey, svc) {
  const cls = stateClass(svc.state);
  const link = svc.url
    ? `<a class="service-link" href="${svc.url}" target="_blank" rel="noopener">↗</a>`
    : '';
  const canRestart = svc.type === 'docker' || svc.type === 'systemd';
  const startBtn = `<button class="btn-start" data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="start" ${svc.state === 'running' ? 'disabled' : ''}>Start</button>`;
  const stopBtn  = `<button class="btn-stop"  data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="stop"  ${svc.state === 'stopped' ? 'disabled' : ''}>Stop</button>`;
  const restartBtn = canRestart
    ? `<button class="btn-restart" data-machine="${machineKey}" data-service="${svc.name}" data-type="${svc.type}" data-action="restart">↺</button>`
    : '';
  return `
    <div class="service-card" id="card-${machineKey}-${svc.name.replace(/[^a-z0-9]/gi,'-')}">
      <div class="status-dot ${cls}"></div>
      <span class="service-name" title="${svc.name}">${svc.label || svc.name}</span>
      ${link}
      <div class="service-btns">${startBtn}${stopBtn}${restartBtn}</div>
    </div>
    <div class="service-error hidden" id="err-${machineKey}-${svc.name.replace(/[^a-z0-9]/gi,'-')}"></div>`;
}

function renderMachine(key, data) {
  const ip = getIP(key);
  const uptime = data.uptime ? `<span>${data.uptime}</span>` : '';
  const rebootDisabled = !data.reachable ? 'disabled' : '';
  const header = `
    <div class="machine-header">
      <div>
        <div class="machine-name">${renderMachineKey(key)}</div>
        <div class="machine-meta">${ip} ${uptime}</div>
      </div>
      <div class="machine-actions">
        <button class="btn-sysinfo" data-machine="${key}">Deep Dive</button>
        <button class="btn-reboot" data-machine="${key}" ${rebootDisabled}>Reboot</button>
      </div>
    </div>`;
  if (!data.reachable && (!data.services || !data.services.length)) {
    return `<div class="machine-col">${header}<div class="unreachable-banner">⚠ Unreachable</div></div>`;
  }
  const cards = (data.services || []).map(s => renderServiceCard(key, s)).join('');
  return `<div class="machine-col">${header}<div class="services-list">${cards}</div></div>`;
}

function getIP(key) {
  const ips = { nyx: '192.168.1.236', astraea: '192.168.1.109', selene: '192.168.1.25' };
  return ips[key] || '';
}

function renderAll(status) {
  const grid = document.getElementById('machines-grid');
  const order = ['nyx', 'astraea', 'selene'];
  grid.innerHTML = order.map(k => renderMachine(k, status[k] || { reachable: false, services: [] })).join('');
  attachHandlers();
}

// ── DIFF UPDATE (avoid full re-render if unchanged) ──────────────────────
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
    const data = await res.json();
    updateDOM(data);
    document.getElementById('last-refresh').textContent =
      'Updated ' + new Date().toLocaleTimeString();
  } catch (e) {
    document.getElementById('last-refresh').textContent = '⚠ Fetch failed';
  }
}

// ── ACTIONS ──────────────────────────────────────────────────────────────
async function sendAction(machine, service, type, action) {
  const res = await fetch('/api/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ machine, service, type, action }),
  });
  return res.json();
}

async function sendReboot(machine) {
  const res = await fetch('/api/reboot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ machine }),
  });
  return res.json();
}

function showError(machine, service, msg) {
  const id = `err-${machine}-${service.replace(/[^a-z0-9]/gi, '-')}`;
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 5000);
}

function attachHandlers() {
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const { machine, service, type, action } = btn.dataset;
      btn.disabled = true;
      try {
        const r = await sendAction(machine, service, type, action);
        if (!r.ok) showError(machine, service, r.error || 'failed');
        else setTimeout(fetchStatus, 800);
      } catch {
        showError(machine, service, 'network error');
      } finally {
        btn.disabled = false;
      }
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

  document.querySelectorAll('.btn-sysinfo').forEach(btn => {
    btn.addEventListener('click', () => openSysinfo(btn.dataset.machine));
  });
}

// ── DEEP DIVE MODAL ──────────────────────────────────────────────────────
async function openSysinfo(machineKey) {
  activeModalMachine = machineKey;
  document.getElementById('modal-title').textContent =
    renderMachineKey(machineKey) + ' — System Info';
  document.getElementById('sysinfo-modal').classList.remove('hidden');
  document.getElementById('modal-backdrop').classList.remove('hidden');
  await loadTab(activeTab);
}

function closeModal() {
  document.getElementById('sysinfo-modal').classList.add('hidden');
  document.getElementById('modal-backdrop').classList.add('hidden');
  activeModalMachine = null;
  sysinfoCache = {};
}

async function loadTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  const pre = document.getElementById('modal-pre');
  if (sysinfoCache[activeModalMachine]?.[tab] !== undefined) {
    pre.textContent = sysinfoCache[activeModalMachine][tab] || '(empty)';
    return;
  }
  pre.textContent = 'Loading...';
  try {
    const res = await fetch(`/api/sysinfo/${activeModalMachine}`);
    const data = await res.json();
    sysinfoCache[activeModalMachine] = data.data || {};
    pre.textContent = sysinfoCache[activeModalMachine][tab] || '(no data)';
  } catch {
    pre.textContent = 'Failed to fetch system info.';
  }
}

// ── INIT ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  fetchStatus();
  setInterval(fetchStatus, POLL_INTERVAL);

  document.getElementById('refresh-btn').addEventListener('click', fetchStatus);
  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('modal-backdrop').addEventListener('click', closeModal);

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => loadTab(btn.dataset.tab));
  });
});

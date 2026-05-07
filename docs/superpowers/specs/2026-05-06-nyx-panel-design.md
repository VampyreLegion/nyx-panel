# Nyx Control Panel — Design Spec
**Date:** 2026-05-06  
**URL:** services.nyxstudios.net  
**Status:** Approved

---

## Overview

A FastAPI web application providing a unified service control panel for all three Nyx Studios machines (Nyx, Astraea, Selene). Displays real-time service status with auto-refresh, launch links for web-accessible apps, and start/stop/restart/reboot controls.

---

## Architecture

### Deployment

| Stage | Host | Port | Cloudflare route |
|-------|------|------|-----------------|
| Initial | Nyx (192.168.1.236) | 8085 | services.nyxstudios.net → 192.168.1.236:8085 |
| After migration | Astraea (192.168.1.109) | 8085 | services.nyxstudios.net → 192.168.1.109:8085 |

Migration requires: copy app to Astraea, update one tunnel config line, restart cloudflared. No code changes.

### Service layout

```
/home/legion/legionprojects/nyx-panel/
├── nyx_panel.py          # FastAPI app entry point
├── config.py             # Machine definitions, service lists, credentials
├── core/
│   └── executor.py       # SSH (paramiko) + local subprocess abstraction
├── routes/
│   └── panel.py          # /api/status, /api/action, /api/reboot
├── static/
│   ├── style.css
│   └── panel.js          # Auto-polling, action handlers
├── templates/
│   └── index.html        # Single-page shell
├── nyx-panel.service     # systemd unit template
└── requirements.txt
```

### Backend transport

- **Nyx (local):** `subprocess` calling `systemctl` and `docker` directly. `sudo reboot` for reboot.
- **Astraea / Selene (remote):** `paramiko` SSH with password auth (`PubkeyAuthentication=no`). Each API call opens a short-lived SSH connection, runs the command, closes. No persistent tunnel.
- **Credentials:** stored in `config.py` (gitignored fields, or `.env`). Same SSH password for both remote machines (`Zaq12345zaq1`). Sudo password same.

### Auto-refresh

Frontend calls `GET /api/status` every **5 seconds** via `fetch()`. Response is a full JSON snapshot of all machines and services. JS diffs the result against current DOM state and updates only changed cards — no full re-render.

---

## Machine & Service Registry

Defined in `config.py`. Each machine entry has: `host`, `user`, `password`, `sudo_password`, `is_local` (bool), list of services.

### Nyx (local, 192.168.1.236)

| Service | Type | URL | Controllable |
|---------|------|-----|--------------|
| comfyui | systemd | https://ai.nyxstudios.net | start/stop |
| nyx-step | systemd | https://music-ai.nyxstudios.net | start/stop |
| open-webui | systemd | https://nyx.nyxstudios.net | start/stop |
| ollama | systemd | — | start/stop |
| ace-step | systemd | https://ai2.nyxstudios.net | start/stop |
| dgx-dashboard | systemd | https://dgx.nyxstudios.net | start/stop |
| nginx | systemd | — | start/stop |
| smbd | systemd | — | start/stop |
| living-art-web-1 | docker | https://art.nyxstudios.net | start/stop/restart |
| living-art-api-1 | docker | — | start/stop/restart |
| portainer | docker | https://192.168.1.236:9443 (LAN) | start/stop |

### Astraea (remote, 192.168.1.109)

| Service | Type | URL | Controllable |
|---------|------|-----|--------------|
| apache2 | systemd | https://nyxstudios.net | start/stop |
| navidrome | systemd | https://music.nyxstudios.net | start/stop |
| icecast2 | systemd | http://192.168.1.109:8000 (LAN) | start/stop |
| nyx-liquidsoap | systemd | — | start/stop |
| ollama | systemd | — | start/stop |
| hermes | systemd | — | start/stop |
| nyx-bot | systemd | — | start/stop |
| cloudflared | systemd | — | start/stop |

### Selene (remote, 192.168.1.25)

| Service | Type | URL | Controllable |
|---------|------|-----|--------------|
| immich | systemd | https://selene.nyxstudios.net | start/stop |
| postgresql | systemd | — | start/stop |
| redis-server | systemd | — | start/stop |
| nginx | systemd | — | start/stop |

---

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serve index.html |
| GET | `/api/status` | Full status snapshot — all machines, all services |
| POST | `/api/action` | `{machine, service, type, action}` — start/stop/restart |
| POST | `/api/reboot` | `{machine}` — reboot with confirmation token |

### `/api/status` response shape

```json
{
  "nyx":     { "reachable": true,  "services": [{"name": "comfyui", "type": "systemd", "state": "running", "url": "https://ai.nyxstudios.net"}] },
  "astraea": { "reachable": true,  "services": [...] },
  "selene":  { "reachable": false, "services": [] }
}
```

### `/api/action` body

```json
{ "machine": "astraea", "service": "navidrome", "type": "systemd", "action": "stop" }
```

Returns `{"ok": true}` or `{"ok": false, "error": "..."}`.

### `/api/reboot` body

```json
{ "machine": "selene" }
```

Confirmation is handled client-side (JS `confirm()` dialog). Server executes `sudo reboot` (local) or SSH `echo password | sudo -S reboot`.

---

## UI

**Layout:** Three-column card grid (one per machine), Docker section below.

**Service card fields:**
- Status indicator: ● green (running/active), ○ grey (stopped/inactive), ↺ yellow (restarting/error)
- Service name
- Launch link ↗ (only if `url` present)
- Action button: [Start] or [Stop] depending on current state; Docker adds [Restart]

**Machine header:** machine name, IP, uptime (if reachable), [Reboot] button.

**Header bar:** "NYX CONTROL PANEL", last-refreshed timestamp, manual 🔄 button.

**Error states:**
- Machine unreachable → entire column shows "⚠ Unreachable" banner, Reboot button disabled
- Action failed → inline red error text on the card for 5 seconds

**Theme:** Dark, matching nyx-step CSS variables.

---

## Security

- Protected by Cloudflare Access (Google OAuth, `steve.j.petry@gmail.com` only)
- Reboot requires client-side `confirm()` dialog
- No API key or additional auth beyond Cloudflare Access
- Credentials stored in `.env` (gitignored), loaded at startup

---

## Migration to Astraea

1. Copy `/home/legion/legionprojects/nyx-panel/` to Astraea
2. Update `/etc/cloudflared/config.yml` on Astraea: change `services.nyxstudios.net` backend from `192.168.1.236:8085` to `192.168.1.109:8085`
3. In `config.py`: flip `nyx` machine from `is_local=True` to `is_local=False` with SSH details; flip `astraea` to `is_local=True`
4. Install service on Astraea, stop on Nyx
5. Restart cloudflared

---

## Not In Scope

- Logs viewer (could be a future tab)
- Metrics / graphs (DGX dashboard covers GPU)
- User management / multi-user (single-owner setup)
- Mobile layout (desktop browser only)

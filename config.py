from __future__ import annotations
import os

SSH_USER = "legion"
SSH_PASSWORD = os.environ.get("SSH_PASSWORD", "Zaq12345zaq1")
SSH_SUDO_PASSWORD = os.environ.get("SSH_SUDO_PASSWORD", "Zaq12345zaq1")

MACHINES = {
    "nyx": {
        "label": "Nyx",
        "ip": "192.168.1.236",
        "is_local": False,
        "has_gpu": True,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "comfyui",         "type": "systemd", "label": "ComfyUI",        "desc": "AI image & video generation (v0.18.1) — GB10 Blackwell 124 GB unified VRAM",  "url": "https://ai.nyxstudios.net"},
            {"name": "nyx-step",        "type": "systemd", "label": "Nyx-Step",       "desc": "Music AI generation — ACE-Step model, generates & queues tracks for radio",    "url": "https://music-ai.nyxstudios.net"},
            {"name": "open-webui",      "type": "systemd", "label": "Open WebUI",     "desc": "Chat UI fronting Ollama — models: gemma4, mistral, llama3",                    "url": "https://nyx.nyxstudios.net"},
            {"name": "ollama",          "type": "systemd", "label": "Ollama",         "desc": "Local LLM inference server — serves Open WebUI & ACE-Step on :11434",          "url": None},
            {"name": "ace-step",        "type": "systemd", "label": "ACE-Step",       "desc": "ACE-Step standalone Gradio UI — direct model access on :7865",                 "url": "https://ai2.nyxstudios.net"},

            {"name": "smbd",            "type": "systemd", "label": "Samba",          "desc": "File share — smb://192.168.1.236/Nyx_storage → /media/Nyx_storage (1 TB NVMe, open LAN)", "url": None},
            {"name": "portainer",       "type": "docker",  "label": "Portainer",      "desc": "Docker management UI — container logs, exec, volumes on :9443 (LAN only)",     "url": "https://192.168.1.236:9443"},
        ],
    },
    "astraea": {
        "label": "Astraea",
        "ip": "192.168.1.109",
        "is_local": True,
        "has_gpu": False,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "apache2",        "type": "systemd", "label": "Apache2",        "desc": "Main website — https://nyxstudios.net (static HTML, public)",                  "url": "https://nyxstudios.net"},
            {"name": "navidrome",      "type": "systemd", "label": "Navidrome",      "desc": "Music streaming server — serves personal music library on :4533",               "url": "https://music.nyxstudios.net"},
            {"name": "icecast2",       "type": "systemd", "label": "Icecast2",       "desc": "Audio stream server — mount /nyx-radio fed by Liquidsoap on :8000",            "url": "http://192.168.1.109:8000"},
            {"name": "nyx-liquidsoap", "type": "systemd", "label": "Liquidsoap",     "desc": "Radio automation — polls Nyx-Step for next AI track, streams to Icecast",      "url": None},
            {"name": "ollama",         "type": "systemd", "label": "Ollama",         "desc": "Local LLM inference — models: gemma4:e2b, gemma4:e4b — used by Hermes & OpenClaw", "url": None},
            {"name": "openclaw",       "type": "systemd", "label": "OpenClaw",       "desc": "MCP AI gateway — model: ollama/gemma4:e2b, plugins: DuckDuckGo on :18789",     "url": "https://openclaw.nyxstudios.net"},
            {"name": "hermes",         "type": "systemd", "label": "Hermes Agent",   "desc": "Telegram AI agent (v0.8.0) — persona: Nyx Studios security monitor, model: gemma4:e2b", "url": None},
            {"name": "nyx-bot",        "type": "systemd", "label": "Nyx Bot",        "desc": "Telegram command bot — /report /status /help → @Nyx_SecurityBot",              "url": None},
            {"name": "cloudflared",    "type": "systemd", "label": "Cloudflared",    "desc": "Cloudflare Tunnel — routes all *.nyxstudios.net traffic in from the internet", "url": None},
            {"name": "nyx-panel",      "type": "systemd", "label": "Nyx Panel",      "desc": "This control panel — FastAPI on :8085, proxied via Cloudflare Tunnel",         "url": "https://services.nyxstudios.net"},
            {"name": "living-art-web-1","type": "docker",  "label": "Living Art Web", "desc": "Living Art display frontend — generative art on :8090",                       "url": "https://art.nyxstudios.net"},
            {"name": "living-art-api-1","type": "docker",  "label": "Living Art API", "desc": "Living Art backend API — serves art data to the web container",                "url": None},
        ],
    },
    "selene": {
        "label": "Selene",
        "ip": "192.168.1.134",
        "is_local": False,
        "has_gpu": False,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "immich",         "type": "systemd", "label": "Immich",         "desc": "Photo & video library (v2.7.5) — 1.8 TB NVMe, built from source",              "url": "https://selene.nyxstudios.net"},
            {"name": "postgresql",     "type": "systemd", "label": "PostgreSQL",     "desc": "Database for Immich — PostgreSQL 16 on :5432 (localhost only)",                "url": None},
            {"name": "redis-server",   "type": "systemd", "label": "Redis",          "desc": "Cache for Immich — Redis on :6379 (localhost only)",                           "url": None},
            {"name": "nginx",          "type": "systemd", "label": "nginx",          "desc": "HTTPS proxy — :443 → Immich :8080, using Cloudflare Origin Certificate",       "url": None},
            {"name": "ollama",         "type": "systemd", "label": "Ollama",         "desc": "Local LLM inference server — serves Ollama API on :11434",                    "url": None},
        ],
    },
}

TUNNELS = [
    # ── PUBLIC ──────────────────────────────────────────────────────────────────────
    {"host": "nyxstudios.net",         "machine": "astraea",  "backend": "localhost:80",      "service": "Apache static site",          "auth": "Public"},
    {"host": "openclaw.nyxstudios.net","machine": "astraea",  "backend": "localhost:18789",     "service": "OpenClaw MCP gateway",         "auth": "Public"},
    {"host": "art.nyxstudios.net",     "machine": "astraea",  "backend": "localhost:8090",      "service": "Living Art Web",               "auth": "Public"},
    {"host": "artadmin.nyxstudios.net","machine": "astraea",  "backend": "localhost:8090",      "service": "Living Art Admin",             "auth": "Public"},
    {"host": "invaders.nyxstudios.net","machine": "astraea",  "backend": "localhost:80",        "service": "Astraea Apache (invaders)",    "auth": "Public"},
    # ── ACCESS-PROTECTED (Google OAuth / qAuth) ────────────────────────────────────
    {"host": "music.nyxstudios.net",   "machine": "astraea",  "backend": "localhost:4533",      "service": "Navidrome",                    "auth": "Access"},
    {"host": "services.nyxstudios.net","machine": "astraea",  "backend": "localhost:8085",      "service": "Nyx Control Panel",            "auth": "Access"},
    {"host": "autoevents.nyxstudios.net","machine": "astraea","backend": "localhost:8088",      "service": "AutoEvents",                   "auth": "Access"},
    {"host": "autoevents-admin.nyxstudios.net","machine": "astraea","backend": "localhost:8088","service": "AutoEvents Admin",      "auth": "Access"},
    {"host": "app.nyxstudios.net",     "machine": "astraea",  "backend": "localhost:80",        "service": "K8 AI Lab App",                "auth": "Access"},
    {"host": "hello-world.nyxstudios.net","machine": "astraea","backend": "localhost:80",       "service": "Test deploy",                  "auth": "Access"},
    {"host": "hello-nyx.nyxstudios.net","machine": "astraea", "backend": "localhost:80",        "service": "Test deploy",                  "auth": "Access"},
    {"host": "nyx.nyxstudios.net",     "machine": "nyx",      "backend": "192.168.1.236:7000",  "service": "Nyx Odysseus",                 "auth": "Access"},
    {"host": "ai.nyxstudios.net",      "machine": "nyx",      "backend": "192.168.1.236:8188",  "service": "ComfyUI",                      "auth": "Access"},
    {"host": "ai2.nyxstudios.net",     "machine": "nyx",      "backend": "192.168.1.236:7865",  "service": "ACE-Step",                     "auth": "Access"},
    {"host": "music-ai.nyxstudios.net","machine": "nyx",      "backend": "192.168.1.236:8001",  "service": "Nyx-Step / MusicWeb",          "auth": "Access"},
    {"host": "gitlab.nyxstudios.net",  "machine": "nyx",      "backend": "192.168.1.236:8929",  "service": "GitLab CE",                    "auth": "Access"},
    {"host": "portainer.nyxstudios.net","machine": "nyx",     "backend": "192.168.1.236:9443",  "service": "Portainer CE",                 "auth": "Access"},
    {"host": "teamcaster.nyxstudios.net","machine": "nyx",    "backend": "192.168.1.236:8086",  "service": "TeamCaster Studio",            "auth": "Access"},
    {"host": "hermes.nyxstudios.net",  "machine": "nyx",      "backend": "192.168.1.236:6080",  "service": "Hermes Desktop (noVNC)",       "auth": "Access"},
    {"host": "selene.nyxstudios.net",  "machine": "selene",   "backend": "192.168.1.134:8081",  "service": "Selene Open WebUI",            "auth": "Access"},
    {"host": "listen.nyxstudios.net",  "machine": "selene",   "backend": "192.168.1.134:8087",  "service": "TeamCaster Listener",          "auth": "Access"},
    {"host": "teamcaster-selene.nyxstudios.net","machine": "selene","backend": "192.168.1.134:8086","service": "TeamCaster Selene", "auth": "Access"},
    {"host": "chat.nyxstudios.net",    "machine": "nyx",      "backend": "192.168.1.236:8080",  "service": "Nyx Open WebUI",               "auth": "Access"},
    {"host": "nyxnotes.nyxstudios.net","machine": "nyx",      "backend": "192.168.1.236:5055",  "service": "Open Notebook (nyxnotes)",     "auth": "Access"},
    {"host": "notebook.nyxstudios.net","machine": "nyx",      "backend": "192.168.1.236:5055",  "service": "Open Notebook (alias)",        "auth": "Access"},
]

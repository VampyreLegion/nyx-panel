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
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "comfyui",         "type": "systemd", "label": "ComfyUI",        "desc": "AI image & video generation (v0.18.1) — GB10 Blackwell 124 GB VRAM",         "url": "https://ai.nyxstudios.net"},
            {"name": "nyx-step",        "type": "systemd", "label": "Nyx-Step",       "desc": "Music AI generation — ACE-Step model, generates & queues tracks for radio",    "url": "https://music-ai.nyxstudios.net"},
            {"name": "open-webui",      "type": "systemd", "label": "Open WebUI",     "desc": "Chat UI fronting Ollama — models: gemma4, mistral, llama3",                    "url": "https://nyx.nyxstudios.net"},
            {"name": "ollama",          "type": "systemd", "label": "Ollama",         "desc": "Local LLM inference server — serves Open WebUI & ACE-Step on :11434",          "url": None},
            {"name": "ace-step",        "type": "systemd", "label": "ACE-Step",       "desc": "ACE-Step standalone Gradio UI — direct model access on :7865",                 "url": "https://ai2.nyxstudios.net"},
            {"name": "dgx-dashboard",   "type": "systemd", "label": "DGX Dashboard",  "desc": "GPU & system metrics dashboard — proxied via nginx :11001 → :11000",           "url": "https://dgx.nyxstudios.net"},
            {"name": "nginx",           "type": "systemd", "label": "nginx",          "desc": "Reverse proxy — routes :11001 → DGX Dashboard :11000",                        "url": None},
            {"name": "smbd",            "type": "systemd", "label": "Samba",          "desc": "File share — smb://192.168.1.236/Nyx_storage → /media/Nyx_storage (1 TB NVMe, open LAN, no password)", "url": None},
            {"name": "living-art-web-1","type": "docker",  "label": "Living Art Web", "desc": "Living Art display frontend — generative art on :8090",                        "url": "https://art.nyxstudios.net"},
            {"name": "living-art-api-1","type": "docker",  "label": "Living Art API", "desc": "Living Art backend API — serves art data to the web container",                "url": None},
            {"name": "portainer",       "type": "docker",  "label": "Portainer",      "desc": "Docker management UI — container logs, exec, volumes on :9443 (LAN only)",     "url": "https://192.168.1.236:9443"},
        ],
    },
    "astraea": {
        "label": "Astraea",
        "ip": "192.168.1.109",
        "is_local": True,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "apache2",        "type": "systemd", "label": "Apache2",        "desc": "Main website — https://nyxstudios.net (static HTML, public)",                  "url": "https://nyxstudios.net"},
            {"name": "navidrome",      "type": "systemd", "label": "Navidrome",      "desc": "Music streaming server — serves personal music library on :4533",               "url": "https://music.nyxstudios.net"},
            {"name": "icecast2",       "type": "systemd", "label": "Icecast2",       "desc": "Audio stream server — mount /nyx-radio fed by Liquidsoap on :8000",            "url": "http://192.168.1.109:8000"},
            {"name": "nyx-liquidsoap", "type": "systemd", "label": "Liquidsoap",     "desc": "Radio automation — polls Nyx-Step for next AI track, streams to Icecast",      "url": None},
            {"name": "ollama",         "type": "systemd", "label": "Ollama",         "desc": "Local LLM inference — models: gemma4:e2b, gemma4:e4b — used by Hermes & OpenClaw", "url": None},
            {"name": "hermes",         "type": "systemd", "label": "Hermes Agent",   "desc": "Telegram AI agent (v0.8.0) — persona: Nyx Studios security monitor, model: gemma4:e2b", "url": None},
            {"name": "nyx-bot",        "type": "systemd", "label": "Nyx Bot",        "desc": "Telegram command bot — /report /status /help → @Nyx_SecurityBot",              "url": None},
            {"name": "cloudflared",    "type": "systemd", "label": "Cloudflared",    "desc": "Cloudflare Tunnel — routes all *.nyxstudios.net traffic in from the internet", "url": None},
            {"name": "nyx-panel",      "type": "systemd", "label": "Nyx Panel",      "desc": "This control panel — FastAPI on :8085, proxied via Cloudflare Tunnel",         "url": "https://services.nyxstudios.net"},
        ],
    },
    "selene": {
        "label": "Selene",
        "ip": "192.168.1.25",
        "is_local": False,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "immich",         "type": "systemd", "label": "Immich",         "desc": "Photo & video library (v2.7.5) — 1.8 TB NVMe, built from source",              "url": "https://selene.nyxstudios.net"},
            {"name": "postgresql",     "type": "systemd", "label": "PostgreSQL",     "desc": "Database for Immich — PostgreSQL 16 on :5432 (localhost only)",                "url": None},
            {"name": "redis-server",   "type": "systemd", "label": "Redis",          "desc": "Cache for Immich — Redis on :6379 (localhost only)",                           "url": None},
            {"name": "nginx",          "type": "systemd", "label": "nginx",          "desc": "HTTPS proxy — :443 → Immich :8080, using Cloudflare Origin Certificate",       "url": None},
        ],
    },
}

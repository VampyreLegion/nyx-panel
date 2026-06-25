from __future__ import annotations
import os

SSH_USER = "legion"
SSH_PASSWORD=os.getenv("SSH_PASSWORD", "Zaq12345zaq1")
SSH_SUDO_PASSWORD=os.getenv("SSH_SUDO_PASSWORD", "Zaq12345zaq1")

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
            {"name": "comfyui",         "type": "systemd", "label": "ComfyUI",          "desc": "AI image & video generation (v0.18.1) — GB10 Blackwell 124 GB unified VRAM",  "url": "https://ai.nyxstudios.net"},
            {"name": "nyx-step",        "type": "systemd", "label": "Nyx-Step",         "desc": "Music AI generation — ACE-Step model, generates & queues tracks for radio",    "url": "https://music-ai.nyxstudios.net"},
            {"name": "open-webui",      "type": "systemd", "label": "Open WebUI",       "desc": "Chat UI fronting Ollama — models: gemma4, mistral, llama3",                    "url": "https://nyx.nyxstudios.net"},
            {"name": "ollama",          "type": "systemd", "label": "Ollama",           "desc": "Local LLM inference server — serves Open WebUI & ACE-Step on :11434",          "url": None},
            {"name": "ace-step",        "type": "systemd", "label": "ACE-Step",         "desc": "ACE-Step standalone Gradio UI — direct model access on :7865",                 "url": "https://ai2.nyxstudios.net"},
            {"name": "autoevents-vetter","type": "systemd", "label": "AutoEvents Vetter", "desc": "Car event scraper + vetter — Brave Search + Ollama + PDF/image extraction on :8091", "url": "https://autoevents-vetter.nyxstudios.net"},
            {"name": "docker",          "type": "systemd", "label": "Docker",           "desc": "Docker daemon — manages all containers on Nyx",                               "url": None},
            {"name": "gitlab",          "type": "docker",  "label": "GitLab",           "desc": "GitLab CE — self-hosted Git on :8929",                                         "url": "https://gitlab.nyxstudios.net"},
            {"name": "gitlab-runner",   "type": "docker",  "label": "GitLab Runner",    "desc": "GitLab CI runner — executes pipelines for gitlab container",                   "url": None},
            {"name": "portainer",       "type": "docker",  "label": "Portainer",        "desc": "Docker management UI — container logs, exec, volumes on :9443",                "url": "https://portainer.nyxstudios.net"},
            {"name": "teamcaster",      "type": "docker",  "label": "TeamCaster Studio", "desc": "TeamCaster Studio dashboard — podcast production on :8086",                   "url": "https://teamcaster.nyxstudios.net"},
            {"name": "hermes-desktop",  "type": "docker",  "label": "Hermes Desktop",   "desc": "Hermes noVNC web remote desktop — browser-based desktop access on :6080",      "url": "https://hermes.nyxstudios.net"},
            {"name": "kind",            "type": "docker",  "label": "Kind k8s",         "desc": "Local Kubernetes cluster control plane — API on :45305 -> 6443 (local only)",  "url": None},
            {"name": "smbd",            "type": "systemd", "label": "Samba",            "desc": "File share — smb://192.168.1.236/Nyx_storage -> /media/Nyx_storage (1 TB NVMe, open LAN)", "url": None},
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
            {"name": "apache2",         "type": "systemd", "label": "Apache2",          "desc": "Main website — https://nyxstudios.net (static HTML, public)",                  "url": "https://nyxstudios.net"},
            {"name": "navidrome",       "type": "docker",  "label": "Navidrome",        "desc": "Music streaming server — personal library on :4533, Docker",                   "url": "https://music.nyxstudios.net"},
            {"name": "icecast2",        "type": "systemd", "label": "Icecast2",         "desc": "Audio stream server — mount /nyx-radio fed by Liquidsoap on :8000",            "url": "http://192.168.1.109:8000"},
            {"name": "nyx-liquidsoap",  "type": "systemd", "label": "Liquidsoap",       "desc": "Radio automation — polls Nyx-Step for next AI track, streams to Icecast",      "url": None},
            {"name": "ollama",          "type": "systemd", "label": "Ollama",           "desc": "Local LLM inference — models: gemma4:e2b, gemma4:e4b",                         "url": None},
            {"name": "openclaw",        "type": "systemd", "label": "OpenClaw",         "desc": "MCP AI gateway — model: ollama/gemma4:e2b, plugins: DuckDuckGo on :18789",     "url": "https://openclaw.nyxstudios.net"},
            {"name": "hermes",          "type": "systemd", "label": "Hermes Agent",     "desc": "Telegram AI agent (v0.8.0) — security monitor, model: gemma4:e2b",             "url": None},
            {"name": "nyx-bot",         "type": "systemd", "label": "Nyx Bot",          "desc": "Telegram command bot — /report /status /help -> @Nyx_SecurityBot",             "url": None},
            {"name": "cloudflared",     "type": "systemd", "label": "Cloudflared",      "desc": "Cloudflare Tunnel — routes all *.nyxstudios.net traffic in from the internet", "url": None},
            {"name": "nyx-panel",       "type": "systemd", "label": "Nyx Panel",        "desc": "This control panel — FastAPI on :8085, proxied via Cloudflare Tunnel",         "url": "https://services.nyxstudios.net"},
            {"name": "autoevents",      "type": "systemd", "label": "AutoEvents Web",   "desc": "Car events public website — scrape, vet, publish schedule via Ollama",         "url": "https://autoevents.nyxstudios.net"},
            {"name": "autoevents-admin","type": "systemd", "label": "AutoEvents Admin", "desc": "Car events admin panel — manage events, review vetted submissions",             "url": "https://autoevents-admin.nyxstudios.net"},
            {"name": "app",             "type": "docker",  "label": "K8 AI Lab App",    "desc": "K8 AI Lab App — deployed via Kind cluster on Nyx, served via Apache :80",      "url": "https://app.nyxstudios.net"},
            {"name": "invaders",        "type": "docker",  "label": "Invaders",         "desc": "Astro Invaders game — hosted on Apache :80",                                   "url": "https://invaders.nyxstudios.net"},
            {"name": "hello-world",     "type": "docker",  "label": "Hello World",      "desc": "Test deploy — Apache :80, verifies tunnel routing works",                      "url": "https://hello-world.nyxstudios.net"},
            {"name": "hello-nyx",       "type": "docker",  "label": "Hello Nyx",        "desc": "Test deploy — Apache :80, verifies Nyx tunnel routing works",                  "url": "https://hello-nyx.nyxstudios.net"},
            {"name": "living-art-web-1","type": "docker",  "label": "Living Art Web",   "desc": "Living Art display frontend — generative art on :8090",                       "url": "https://art.nyxstudios.net"},
            {"name": "living-art-api-1","type": "docker",  "label": "Living Art API",   "desc": "Living Art backend API — serves art data to the web container",                "url": None},
            {"name": "artadmin",        "type": "systemd", "label": "Living Art Admin",  "desc": "Living Art Admin — management UI via nginx :8090, requires Cloudflare Access", "url": "https://artadmin.nyxstudios.net"},
        ],
    },
    "selene": {
        "label": "Selene",
        "ip": "192.168.1.25",
        "is_local": False,
        "has_gpu": False,
        "ssh_user": SSH_USER,
        "ssh_password": SSH_PASSWORD,
        "sudo_password": SSH_SUDO_PASSWORD,
        "services": [
            {"name": "immich",          "type": "systemd", "label": "Immich",           "desc": "Photo & video library (v2.7.5) — 1.8 TB NVMe, built from source, LAN only",   "url": None},
            {"name": "open-webui",      "type": "systemd", "label": "Open WebUI",       "desc": "Chat UI + Ollama on Selene — models: gemma4:26b, gemma4:latest on :8081",      "url": "https://selene.nyxstudios.net"},
            {"name": "teamcaster-selene","type": "docker", "label": "TeamCaster Selene", "desc": "TeamCaster Studio on Selene — legacy route, unused, on :8086",                "url": "https://teamcaster-selene.nyxstudios.net"},
            {"name": "listen",          "type": "docker",  "label": "TeamCaster Listen", "desc": "TeamCaster Listener — end-user podcast player on :8087",                     "url": "https://listen.nyxstudios.net"},
            {"name": "postgresql",      "type": "systemd", "label": "PostgreSQL",       "desc": "Database for Immich — PostgreSQL 16 on :5432 (localhost only)",                "url": None},
            {"name": "redis-server",    "type": "systemd", "label": "Redis",            "desc": "Cache for Immich — Redis on :6379 (localhost only)",                           "url": None},
            {"name": "nginx",           "type": "systemd", "label": "nginx",            "desc": "HTTPS proxy — :443 -> Immich :8080, using Cloudflare Origin Certificate",      "url": None},
        ],
    },
}

# ── Cloudflare Tunnel routes (tunnel: astraea-new / 6ba0ad1e-7a83-44b0-9361-2af437572b6b) ──
# Source of truth: /etc/cloudflared/config.yml on Astraea + Cloudflare Access apps.
# auth: "Cloudflare Access" = Google OAuth (steve.j.petry@gmail.com only); "Public" = no Access policy.
# Verified live 2026-06-18.
TUNNELS = [
    {"host": "nyxstudios.net",                  "machine": "Astraea", "backend": "localhost:80",       "service": "Apache — main website",            "auth": "Public"},
    {"host": "music.nyxstudios.net",            "machine": "Astraea", "backend": "localhost:4533",     "service": "Navidrome music streaming",        "auth": "Cloudflare Access"},
    {"host": "openclaw.nyxstudios.net",         "machine": "Astraea", "backend": "localhost:18789",    "service": "OpenClaw MCP AI gateway",          "auth": "Public"},
    {"host": "services.nyxstudios.net",         "machine": "Astraea", "backend": "localhost:8085",     "service": "Nyx Control Panel (this app)",     "auth": "Cloudflare Access"},
    {"host": "autoevents.nyxstudios.net",       "machine": "Astraea", "backend": "localhost:8088",     "service": "AutoEvents public website",        "auth": "Public"},
    {"host": "autoevents-admin.nyxstudios.net", "machine": "Astraea", "backend": "localhost:8088",     "service": "AutoEvents admin panel",           "auth": "Cloudflare Access"},
    {"host": "app.nyxstudios.net",              "machine": "Astraea", "backend": "localhost:80",       "service": "K8 AI Lab App (via Apache)",       "auth": "Cloudflare Access"},
    {"host": "invaders.nyxstudios.net",         "machine": "Astraea", "backend": "localhost:80",       "service": "Astro Invaders game (via Apache)", "auth": "Public"},
    {"host": "hello-world.nyxstudios.net",      "machine": "Astraea", "backend": "localhost:80",       "service": "Hello World test deploy",          "auth": "Cloudflare Access"},
    {"host": "hello-nyx.nyxstudios.net",        "machine": "Astraea", "backend": "localhost:80",       "service": "Hello Nyx test deploy",            "auth": "Cloudflare Access"},
    {"host": "ai.nyxstudios.net",               "machine": "Nyx",     "backend": "192.168.1.236:8188", "service": "ComfyUI image/video gen",          "auth": "Cloudflare Access"},
    {"host": "nyx.nyxstudios.net",              "machine": "Nyx",     "backend": "192.168.1.236:7000", "service": "Odysseus AI workspace",            "auth": "Cloudflare Access"},
    {"host": "ai2.nyxstudios.net",              "machine": "Nyx",     "backend": "192.168.1.236:7865", "service": "ACE-Step standalone Gradio UI",    "auth": "Cloudflare Access"},
    {"host": "music-ai.nyxstudios.net",         "machine": "Nyx",     "backend": "192.168.1.236:8001", "service": "MusicWeb / Nyx-Step music gen",    "auth": "Cloudflare Access"},
    {"host": "autoevents-vetter.nyxstudios.net","machine": "Nyx",     "backend": "192.168.1.236:8091", "service": "AutoEvents Vetter API",            "auth": "Public"},
    {"host": "gitlab.nyxstudios.net",           "machine": "Nyx",     "backend": "192.168.1.236:8929", "service": "GitLab CE self-hosted Git",        "auth": "Cloudflare Access"},
    {"host": "portainer.nyxstudios.net",        "machine": "Nyx",     "backend": "192.168.1.236:9443 (https, noTLSVerify)", "service": "Portainer Docker management UI", "auth": "Cloudflare Access"},
    {"host": "teamcaster.nyxstudios.net",       "machine": "Nyx",     "backend": "192.168.1.236:8086", "service": "TeamCaster Studio",                "auth": "Cloudflare Access"},
    {"host": "hermes.nyxstudios.net",           "machine": "Nyx",     "backend": "192.168.1.236:6080", "service": "Hermes noVNC remote desktop",      "auth": "Cloudflare Access"},
    {"host": "art.nyxstudios.net",              "machine": "Astraea",  "backend": "localhost:8090",  "service": "Living Art display frontend",      "auth": "Public"},
    {"host": "artadmin.nyxstudios.net",         "machine": "Astraea",  "backend": "localhost:8090",  "service": "Living Art admin UI",              "auth": "Cloudflare Access"},
    {"host": "selene.nyxstudios.net",           "machine": "Selene",  "backend": "192.168.1.25:8081",  "service": "Open WebUI (chat + Ollama)",       "auth": "Cloudflare Access"},
    {"host": "teamcaster-selene.nyxstudios.net","machine": "Selene",  "backend": "192.168.1.25:8086",  "service": "TeamCaster Studio (legacy)",       "auth": "Cloudflare Access"},
    {"host": "listen.nyxstudios.net",           "machine": "Selene",  "backend": "192.168.1.25:8087",  "service": "TeamCaster Listener player",       "auth": "Cloudflare Access"},
]

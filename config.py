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
            {"name": "comfyui",         "type": "systemd", "label": "ComfyUI",       "url": "https://ai.nyxstudios.net"},
            {"name": "nyx-step",        "type": "systemd", "label": "Nyx-Step",      "url": "https://music-ai.nyxstudios.net"},
            {"name": "open-webui",      "type": "systemd", "label": "Open WebUI",    "url": "https://nyx.nyxstudios.net"},
            {"name": "ollama",          "type": "systemd", "label": "Ollama",        "url": None},
            {"name": "ace-step",        "type": "systemd", "label": "ACE-Step",      "url": "https://ai2.nyxstudios.net"},
            {"name": "dgx-dashboard",   "type": "systemd", "label": "DGX Dashboard", "url": "https://dgx.nyxstudios.net"},
            {"name": "nginx",           "type": "systemd", "label": "nginx",         "url": None},
            {"name": "smbd",            "type": "systemd", "label": "Samba",         "url": None},
            {"name": "living-art-web-1","type": "docker",  "label": "Living Art Web","url": "https://art.nyxstudios.net"},
            {"name": "living-art-api-1","type": "docker",  "label": "Living Art API","url": None},
            {"name": "portainer",       "type": "docker",  "label": "Portainer",     "url": "https://192.168.1.236:9443"},
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
            {"name": "apache2",        "type": "systemd", "label": "Apache2",       "url": "https://nyxstudios.net"},
            {"name": "navidrome",      "type": "systemd", "label": "Navidrome",     "url": "https://music.nyxstudios.net"},
            {"name": "icecast2",       "type": "systemd", "label": "Icecast2",      "url": "http://192.168.1.109:8000"},
            {"name": "nyx-liquidsoap", "type": "systemd", "label": "Liquidsoap",   "url": None},
            {"name": "ollama",         "type": "systemd", "label": "Ollama",        "url": None},
            {"name": "hermes",         "type": "systemd", "label": "Hermes Agent",  "url": None},
            {"name": "nyx-bot",        "type": "systemd", "label": "Nyx Bot",       "url": None},
            {"name": "cloudflared",    "type": "systemd", "label": "Cloudflared",   "url": None},
            {"name": "nyx-panel",      "type": "systemd", "label": "Nyx Panel",     "url": "https://services.nyxstudios.net"},
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
            {"name": "immich",         "type": "systemd", "label": "Immich",        "url": "https://selene.nyxstudios.net"},
            {"name": "postgresql",     "type": "systemd", "label": "PostgreSQL",    "url": None},
            {"name": "redis-server",   "type": "systemd", "label": "Redis",         "url": None},
            {"name": "nginx",          "type": "systemd", "label": "nginx",         "url": None},
        ],
    },
}

"""
Integration tests for API routes — executor calls are mocked so no real
SSH or systemctl is invoked.
"""
from __future__ import annotations
from unittest.mock import patch, AsyncMock
import pytest
import sys
sys.path.insert(0, "/home/legion/nyx-panel")

from fastapi.testclient import TestClient
from nyx_panel import app

client = TestClient(app)

# ── shared mock data ──────────────────────────────────────────────────────────

MOCK_STATUS = {
    "nyx": {
        "reachable": True, "uptime": "up 4 hours", "gpu": None,
        "services": [
            {"name": "comfyui", "label": "ComfyUI", "type": "systemd",
             "state": "running", "url": "https://ai.nyxstudios.net", "desc": "AI gen"},
            {"name": "ace-step", "label": "ACE-Step", "type": "systemd",
             "state": "stopped", "url": None, "desc": None},
        ],
    },
    "astraea": {
        "reachable": True, "uptime": "up 5 hours", "gpu": None,
        "services": [
            {"name": "apache2", "label": "Apache2", "type": "systemd",
             "state": "running", "url": "https://nyxstudios.net", "desc": None},
        ],
    },
    "selene": {"reachable": False, "uptime": None, "gpu": None, "services": []},
}


# ── /api/status ───────────────────────────────────────────────────────────────

class TestStatusEndpoint:
    def test_returns_all_machines(self):
        with patch("routes.panel._get_machine_status", new_callable=AsyncMock,
                   side_effect=lambda k, v: MOCK_STATUS[k]):
            resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"nyx", "astraea", "selene"}

    def test_nyx_reachable_with_services(self):
        with patch("routes.panel._get_machine_status", new_callable=AsyncMock,
                   side_effect=lambda k, v: MOCK_STATUS[k]):
            data = client.get("/api/status").json()
        assert data["nyx"]["reachable"] is True
        assert len(data["nyx"]["services"]) == 2
        assert data["nyx"]["services"][0]["state"] == "running"

    def test_selene_unreachable(self):
        with patch("routes.panel._get_machine_status", new_callable=AsyncMock,
                   side_effect=lambda k, v: MOCK_STATUS[k]):
            data = client.get("/api/status").json()
        assert data["selene"]["reachable"] is False
        assert data["selene"]["services"] == []


# ── /api/action ───────────────────────────────────────────────────────────────

class TestActionEndpoint:
    def test_stop_running_service(self):
        with patch("routes.panel.run_systemd_action", return_value=(True, "")):
            resp = client.post("/api/action", json={
                "machine": "nyx", "service": "comfyui", "type": "systemd", "action": "stop"
            })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_start_stopped_service(self):
        with patch("routes.panel.run_systemd_action", return_value=(True, "")):
            resp = client.post("/api/action", json={
                "machine": "astraea", "service": "hermes", "type": "systemd", "action": "start"
            })
        assert resp.json()["ok"] is True

    def test_docker_restart(self):
        with patch("routes.panel.run_docker_action", return_value=(True, "")):
            resp = client.post("/api/action", json={
                "machine": "nyx", "service": "living-art-web-1", "type": "docker", "action": "restart"
            })
        assert resp.json()["ok"] is True

    def test_action_failure_returns_error(self):
        with patch("routes.panel.run_systemd_action", return_value=(False, "Permission denied")):
            resp = client.post("/api/action", json={
                "machine": "nyx", "service": "comfyui", "type": "systemd", "action": "stop"
            })
        body = resp.json()
        assert body["ok"] is False
        assert "Permission denied" in body["error"]

    def test_unknown_machine(self):
        resp = client.post("/api/action", json={
            "machine": "moon", "service": "whatever", "type": "systemd", "action": "start"
        })
        assert resp.json()["ok"] is False

    def test_invalid_action(self):
        resp = client.post("/api/action", json={
            "machine": "nyx", "service": "comfyui", "type": "systemd", "action": "explode"
        })
        assert resp.json()["ok"] is False

    def test_unknown_service_type(self):
        resp = client.post("/api/action", json={
            "machine": "nyx", "service": "comfyui", "type": "kubernetes", "action": "start"
        })
        assert resp.json()["ok"] is False


# ── /api/reboot ───────────────────────────────────────────────────────────────

class TestRebootEndpoint:
    def test_reboot_known_machine(self):
        with patch("routes.panel.run_reboot", return_value=(True, "reboot command sent")):
            resp = client.post("/api/reboot", json={"machine": "selene"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_reboot_unknown_machine(self):
        resp = client.post("/api/reboot", json={"machine": "pluto"})
        assert resp.json()["ok"] is False


# ── /api/logs ─────────────────────────────────────────────────────────────────

class TestLogsEndpoint:
    def test_returns_log_output(self):
        sample = "May 06 12:00:00 astraea apache2[1]: Started"
        with patch("routes.panel.get_service_logs", return_value=sample):
            resp = client.get("/api/logs/astraea/apache2?type=systemd&lines=10")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert "apache2" in body["logs"]

    def test_docker_logs(self):
        with patch("routes.panel.get_service_logs", return_value="container output"):
            resp = client.get("/api/logs/nyx/living-art-web-1?type=docker")
        assert resp.json()["ok"] is True

    def test_unknown_machine(self):
        resp = client.get("/api/logs/moon/nginx")
        assert resp.json()["ok"] is False


# ── /api/sysinfo ──────────────────────────────────────────────────────────────

class TestSysinfoEndpoint:
    def test_returns_sysinfo_keys(self):
        mock_data = {"memory": "16G total", "cpu": "2%", "disk": "/dev/nvme0n1", 
                     "processes": "ps output", "ports": "ss output",
                     "timers": "timers", "cron": "cron jobs", "uptime": "5h"}
        with patch("routes.sysinfo.get_sysinfo", return_value=mock_data):
            resp = client.get("/api/sysinfo/astraea")
        assert resp.status_code == 200
        assert resp.json()["data"]["memory"] == "16G total"

    def test_unknown_machine(self):
        resp = client.get("/api/sysinfo/mars")
        assert "error" in resp.json()

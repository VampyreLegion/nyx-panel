"""
Tests for core/executor.py — mocks subprocess and paramiko so no
real SSH or systemctl calls are made.
"""
from __future__ import annotations
from unittest.mock import patch, MagicMock, call
import pytest
import sys, os
sys.path.insert(0, "/home/legion/nyx-panel")


# ── _run_local ────────────────────────────────────────────────────────────────

class TestRunLocal:
    def test_basic_command(self):
        from core.executor import _run_local
        mock = MagicMock(returncode=0, stdout="active\n", stderr="")
        with patch("core.executor.subprocess.run", return_value=mock) as sp:
            rc, out, err = _run_local(["systemctl", "is-active", "nginx"])
        sp.assert_called_once()
        assert rc == 0
        assert out == "active\n"

    def test_sudo_pipes_password(self):
        from core.executor import _run_local
        mock = MagicMock(returncode=0, stdout="", stderr="")
        with patch("core.executor.subprocess.run", return_value=mock) as sp:
            _run_local(["sudo", "reboot"], sudo_password="secret")
        kwargs = sp.call_args[1]
        assert kwargs["input"] == "secret\n"


# ── get_systemd_state ─────────────────────────────────────────────────────────

class TestGetSystemdState:
    def _local_mock(self, stdout_val):
        return MagicMock(returncode=0, stdout=stdout_val, stderr="")

    def test_active_returns_running(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "active\n", "")) as m:
            state = get_systemd_state("astraea", "apache2")  # astraea is_local=True
        assert state == "running"

    def test_inactive_returns_stopped(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "inactive\n", "")):
            state = get_systemd_state("astraea", "hermes")
        assert state == "stopped"

    def test_dead_returns_stopped(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "dead\n", "")):
            state = get_systemd_state("astraea", "hermes")
        assert state == "stopped"

    def test_failed_returns_error(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "failed\n", "")):
            state = get_systemd_state("astraea", "broken")
        assert state == "error"

    def test_activating_returns_starting(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "activating\n", "")):
            state = get_systemd_state("astraea", "slow-svc")
        assert state == "starting"

    def test_remote_uses_ssh(self):
        from core.executor import get_systemd_state
        with patch("core.executor._ssh_exec", return_value=(0, "active\n", "")) as ssh:
            state = get_systemd_state("nyx", "comfyui")  # nyx is_local=False
        ssh.assert_called_once()
        assert state == "running"

    def test_remote_inactive(self):
        from core.executor import get_systemd_state
        with patch("core.executor._ssh_exec", return_value=(0, "inactive\n", "")):
            state = get_systemd_state("nyx", "ace-step")
        assert state == "stopped"

    def test_unknown_state(self):
        from core.executor import get_systemd_state
        with patch("core.executor._run_local", return_value=(0, "something-weird\n", "")):
            state = get_systemd_state("astraea", "x")
        assert state == "something-weird"


# ── get_docker_state ──────────────────────────────────────────────────────────

class TestGetDockerState:
    def test_running(self):
        from core.executor import get_docker_state
        with patch("core.executor._ssh_exec", return_value=(0, "running\n", "")):
            state = get_docker_state("nyx", "living-art-web-1")
        assert state == "running"

    def test_exited_returns_stopped(self):
        from core.executor import get_docker_state
        with patch("core.executor._ssh_exec", return_value=(0, "exited\n", "")):
            state = get_docker_state("nyx", "living-art-api-1")
        assert state == "stopped"

    def test_created_returns_stopped(self):
        from core.executor import get_docker_state
        with patch("core.executor._ssh_exec", return_value=(0, "created\n", "")):
            state = get_docker_state("nyx", "portainer")
        assert state == "stopped"

    def test_missing_container(self):
        from core.executor import get_docker_state
        with patch("core.executor._ssh_exec", return_value=(0, "missing\n", "")):
            state = get_docker_state("nyx", "nyx-rancher")
        assert state == "missing"


# ── check_reachable ───────────────────────────────────────────────────────────

class TestCheckReachable:
    def test_local_always_reachable(self):
        from core.executor import check_reachable
        with patch("core.executor._run_local", return_value=(0, "up 2 hours\n", "")):
            reachable, uptime = check_reachable("astraea")
        assert reachable is True
        assert "up 2 hours" in uptime

    def test_remote_reachable(self):
        from core.executor import check_reachable
        with patch("core.executor._run_local", return_value=(0, "", "")):
            with patch("core.executor._ssh_exec", return_value=(0, "up 4 hours, 39 minutes\n", "")):
                reachable, uptime = check_reachable("nyx")
        assert reachable is True
        assert uptime is not None

    def test_remote_reachable_no_ssh(self):
        # Machine responds to ping but SSH is down
        from core.executor import check_reachable
        with patch("core.executor._run_local", return_value=(0, "", "")):
            with patch("core.executor._ssh_exec", side_effect=OSError("Connection refused")):
                reachable, uptime = check_reachable("nyx")
        assert reachable is True
        assert uptime is None

    def test_remote_unreachable_on_exception(self):
        # ping itself fails
        from core.executor import check_reachable
        with patch("core.executor._run_local", side_effect=OSError("Network error")):
            reachable, uptime = check_reachable("selene")
        assert reachable is False
        assert uptime is None

    def test_remote_unreachable_on_timeout(self):
        # ping returns non-zero exit (host down)
        from core.executor import check_reachable
        with patch("core.executor._run_local", return_value=(1, "", "")):
            reachable, uptime = check_reachable("nyx")
        assert reachable is False
        assert uptime is None


# ── run_systemd_action ────────────────────────────────────────────────────────

class TestRunSystemdAction:
    def test_local_start_success(self):
        from core.executor import run_systemd_action
        with patch("core.executor._run_local", return_value=(0, "", "")) as m:
            ok, msg = run_systemd_action("astraea", "navidrome", "start")
        assert ok is True

    def test_local_stop_success(self):
        from core.executor import run_systemd_action
        with patch("core.executor._run_local", return_value=(0, "", "")):
            ok, msg = run_systemd_action("astraea", "navidrome", "stop")
        assert ok is True

    def test_local_invalid_action(self):
        from core.executor import run_systemd_action
        ok, msg = run_systemd_action("astraea", "navidrome", "explode")
        assert ok is False
        assert "invalid" in msg

    def test_local_failure(self):
        from core.executor import run_systemd_action
        with patch("core.executor._run_local", return_value=(1, "", "Permission denied")):
            ok, msg = run_systemd_action("astraea", "navidrome", "start")
        assert ok is False
        assert "Permission denied" in msg

    def test_remote_start(self):
        from core.executor import run_systemd_action
        with patch("core.executor._ssh_exec", return_value=(0, "", "")) as ssh:
            ok, msg = run_systemd_action("nyx", "comfyui", "stop")
        ssh.assert_called_once()
        assert ok is True

    def test_remote_restart(self):
        from core.executor import run_systemd_action
        with patch("core.executor._ssh_exec", return_value=(0, "", "")):
            ok, msg = run_systemd_action("nyx", "open-webui", "restart")
        assert ok is True


# ── run_docker_action ─────────────────────────────────────────────────────────

class TestRunDockerAction:
    def test_remote_stop(self):
        from core.executor import run_docker_action
        with patch("core.executor._ssh_exec", return_value=(0, "", "")):
            ok, msg = run_docker_action("nyx", "living-art-web-1", "stop")
        assert ok is True

    def test_remote_restart(self):
        from core.executor import run_docker_action
        with patch("core.executor._ssh_exec", return_value=(0, "", "")):
            ok, msg = run_docker_action("nyx", "living-art-api-1", "restart")
        assert ok is True

    def test_invalid_action(self):
        from core.executor import run_docker_action
        ok, msg = run_docker_action("nyx", "portainer", "destroy")
        assert ok is False
        assert "invalid" in msg


# ── get_service_logs ──────────────────────────────────────────────────────────

class TestGetServiceLogs:
    def test_local_systemd_logs(self):
        from core.executor import get_service_logs
        sample = "May 06 12:00:00 astraea apache2[123]: Starting...\n"
        with patch("core.executor._run_local", return_value=(0, sample, "")):
            out = get_service_logs("astraea", "apache2", "systemd", lines=10)
        assert "apache2" in out

    def test_remote_docker_logs(self):
        from core.executor import get_service_logs
        sample = "2026-05-06T12:00:00Z INFO Server started\n"
        with patch("core.executor._ssh_exec", return_value=(0, sample, "")):
            out = get_service_logs("nyx", "living-art-web-1", "docker", lines=50)
        assert "Server started" in out

    def test_ssh_error_returns_error_string(self):
        from core.executor import get_service_logs
        with patch("core.executor._ssh_exec", side_effect=Exception("connection refused")):
            out = get_service_logs("nyx", "comfyui", "systemd")
        assert "error" in out.lower()

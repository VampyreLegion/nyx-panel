from __future__ import annotations
import subprocess
import paramiko
from config import MACHINES


def _run_local(cmd: list[str], sudo_password: str | None = None) -> tuple[int, str, str]:
    if sudo_password and cmd[0] == "sudo":
        proc = subprocess.run(
            cmd, input=sudo_password + "\n",
            capture_output=True, text=True, timeout=15
        )
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return proc.returncode, proc.stdout, proc.stderr


def _ssh_exec(host: str, user: str, password: str, command: str, timeout: int = 15) -> tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password,
                   look_for_keys=False, allow_agent=False, timeout=timeout)
    try:
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()
    finally:
        client.close()


def check_reachable(machine_key: str) -> tuple[bool, str | None]:
    """Returns (reachable, uptime_string_or_None). Raises nothing."""
    m = MACHINES[machine_key]
    try:
        if m["is_local"]:
            _, out, _ = _run_local(["uptime", "-p"])
            return True, out.strip() or None
        else:
            _, out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], "uptime -p", timeout=6)
            return True, out.strip() or None
    except Exception:
        return False, None


def get_systemd_state(machine_key: str, service_name: str) -> str:
    m = MACHINES[machine_key]
    if m["is_local"]:
        rc, out, _ = _run_local(["systemctl", "is-active", service_name])
    else:
        rc, out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"],
                               f"systemctl is-active {service_name}")
    state = out.strip()
    if state == "active":
        return "running"
    if state in ("inactive", "dead"):
        return "stopped"
    if state in ("failed", "error"):
        return "error"
    if state == "activating":
        return "starting"
    return state or "unknown"


def get_docker_state(machine_key: str, container_name: str) -> str:
    m = MACHINES[machine_key]
    cmd = f"docker inspect --format={{{{.State.Status}}}} {container_name} 2>/dev/null || echo missing"
    if m["is_local"]:
        rc, out, _ = _run_local(["bash", "-c", cmd])
    else:
        rc, out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd)
    state = out.strip()
    if state == "running":
        return "running"
    if state in ("exited", "created", "dead"):
        return "stopped"
    if state == "missing":
        return "missing"
    return state or "unknown"


def run_systemd_action(machine_key: str, service_name: str, action: str) -> tuple[bool, str]:
    m = MACHINES[machine_key]
    sudo_pw = m["sudo_password"]
    if action not in ("start", "stop", "restart"):
        return False, "invalid action"
    if m["is_local"]:
        cmd = ["sudo", "-S", "systemctl", action, service_name]
        rc, out, err = _run_local(cmd, sudo_password=sudo_pw)
    else:
        cmd = f"echo '{sudo_pw}' | sudo -S systemctl {action} {service_name}"
        rc, out, err = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd)
    ok = rc == 0
    return ok, (err or out).strip()


def run_docker_action(machine_key: str, container_name: str, action: str) -> tuple[bool, str]:
    m = MACHINES[machine_key]
    sudo_pw = m["sudo_password"]
    if action not in ("start", "stop", "restart"):
        return False, "invalid action"
    if m["is_local"]:
        rc, out, err = _run_local(["sudo", "-S", "docker", action, container_name], sudo_password=sudo_pw)
    else:
        cmd = f"echo '{sudo_pw}' | sudo -S docker {action} {container_name}"
        rc, out, err = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd)
    ok = rc == 0
    return ok, (err or out).strip()


def run_reboot(machine_key: str) -> tuple[bool, str]:
    m = MACHINES[machine_key]
    sudo_pw = m["sudo_password"]
    if m["is_local"]:
        _run_local(["sudo", "-S", "reboot"], sudo_password=sudo_pw)
        return True, "rebooting"
    else:
        cmd = f"echo '{sudo_pw}' | sudo -S reboot"
        try:
            _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd, timeout=10)
        except Exception:
            pass
        return True, "reboot command sent"


def get_sysinfo(machine_key: str) -> dict:
    m = MACHINES[machine_key]
    commands = {
        "memory": "free -h",
        "cpu": "top -bn1 | grep '%Cpu' | head -3",
        "disk": "df -h --output=source,size,used,avail,pcent,target -x tmpfs -x devtmpfs | head -20",
        "processes": "ps aux --sort=-%cpu | head -20",
        "ports": "ss -tlnp",
        "timers": "systemctl list-timers --no-pager 2>/dev/null | head -20",
        "cron": "crontab -l 2>/dev/null || echo '(no crontab)'",
        "uptime": "uptime && echo && w",
    }
    results = {}
    for key, cmd in commands.items():
        try:
            if m["is_local"]:
                _, out, _ = _run_local(["bash", "-c", cmd])
            else:
                _, out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd, timeout=10)
            results[key] = out.strip()
        except Exception as e:
            results[key] = f"error: {e}"
    return results


def get_service_logs(machine_key: str, service_name: str, service_type: str, lines: int = 80) -> str:
    m = MACHINES[machine_key]
    if service_type == "docker":
        cmd = f"docker logs --tail {lines} {service_name} 2>&1"
    else:
        cmd = f"journalctl -u {service_name} -n {lines} --no-pager --output=short-iso 2>&1"
    try:
        if m["is_local"]:
            _, out, err = _run_local(["bash", "-c", cmd])
            return out or err or "(no output)"
        else:
            _, out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], cmd, timeout=10)
            return out or "(no output)"
    except Exception as e:
        return f"error: {e}"


def get_gpu_stats(machine_key: str) -> list[dict] | None:
    """Returns list of GPU dicts, or None if nvidia-smi unavailable."""
    m = MACHINES[machine_key]
    smi = "nvidia-smi --query-gpu=index,name,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits 2>/dev/null"
    mem = "free -m | grep Mem"
    try:
        if m["is_local"]:
            _, smi_out, _ = _run_local(["bash", "-c", smi])
            _, mem_out, _ = _run_local(["bash", "-c", mem])
        else:
            _, smi_out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], smi, timeout=6)
            _, mem_out, _ = _ssh_exec(m["ip"], m["ssh_user"], m["ssh_password"], mem, timeout=6)
    except Exception:
        return None

    if not smi_out.strip():
        return None

    gpus = []
    for line in smi_out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 5:
            continue
        idx, name, util, temp, power = parts[0], parts[1], parts[2], parts[3], parts[4]
        gpu = {
            "index": idx,
            "name": name,
            "util_pct": None if util == "[N/A]" else int(float(util)),
            "temp_c": None if temp == "[N/A]" else int(float(temp)),
            "power_w": None if power == "[N/A]" else round(float(power), 1),
        }
        # parse system memory for unified-memory GPUs
        if mem_out.strip():
            parts = mem_out.split()
            try:
                gpu["mem_used_mb"]  = int(parts[2])
                gpu["mem_total_mb"] = int(parts[1])
            except Exception:
                pass
        gpus.append(gpu)
    return gpus or None

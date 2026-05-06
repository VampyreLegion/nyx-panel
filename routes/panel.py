from __future__ import annotations
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from config import MACHINES
from core.executor import (
    check_reachable, get_systemd_state, get_docker_state,
    run_systemd_action, run_docker_action, run_reboot,
    get_gpu_stats, get_service_logs,
)

router = APIRouter()


async def _get_machine_status(machine_key: str, machine: dict) -> dict:
    reachable, uptime = await asyncio.to_thread(check_reachable, machine_key)
    if not reachable:
        return {"reachable": False, "uptime": None, "services": [], "gpu": None}

    async def fetch_service(svc: dict):
        try:
            if svc["type"] == "systemd":
                state = await asyncio.to_thread(get_systemd_state, machine_key, svc["name"])
            elif svc["type"] == "docker":
                state = await asyncio.to_thread(get_docker_state, machine_key, svc["name"])
            else:
                state = "unknown"
        except Exception:
            state = "unknown"
        return {
            "name": svc["name"],
            "label": svc.get("label", svc["name"]),
            "type": svc["type"],
            "state": state,
            "url": svc.get("url"),
            "desc": svc.get("desc"),
        }

    async def fetch_gpu():
        if not machine.get("has_gpu"):
            return None
        try:
            return await asyncio.to_thread(get_gpu_stats, machine_key)
        except Exception:
            return None

    services_results, gpu = await asyncio.gather(
        asyncio.gather(*[fetch_service(s) for s in machine["services"]]),
        fetch_gpu(),
    )
    return {"reachable": True, "uptime": uptime, "services": list(services_results), "gpu": gpu}


@router.get("/api/status")
async def status():
    tasks = {k: _get_machine_status(k, v) for k, v in MACHINES.items()}
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    out = {}
    for key, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            out[key] = {"reachable": False, "uptime": None, "services": [], "gpu": None}
        else:
            out[key] = result
    return out


class ActionRequest(BaseModel):
    machine: str
    service: str
    type: str
    action: str


@router.post("/api/action")
async def action(req: ActionRequest):
    if req.machine not in MACHINES:
        return {"ok": False, "error": "unknown machine"}
    if req.action not in ("start", "stop", "restart"):
        return {"ok": False, "error": "invalid action"}
    if req.type == "systemd":
        ok, msg = await asyncio.to_thread(run_systemd_action, req.machine, req.service, req.action)
    elif req.type == "docker":
        ok, msg = await asyncio.to_thread(run_docker_action, req.machine, req.service, req.action)
    else:
        return {"ok": False, "error": "unknown service type"}
    return {"ok": ok, "error": msg if not ok else None}


class RebootRequest(BaseModel):
    machine: str


@router.post("/api/reboot")
async def reboot(req: RebootRequest):
    if req.machine not in MACHINES:
        return {"ok": False, "error": "unknown machine"}
    ok, msg = await asyncio.to_thread(run_reboot, req.machine)
    return {"ok": ok, "message": msg}


@router.get("/api/logs/{machine_key}/{service_name}")
async def logs(machine_key: str, service_name: str, type: str = "systemd", lines: int = 100):
    if machine_key not in MACHINES:
        return {"ok": False, "error": "unknown machine"}
    output = await asyncio.to_thread(get_service_logs, machine_key, service_name, type, lines)
    return {"ok": True, "machine": machine_key, "service": service_name, "logs": output}

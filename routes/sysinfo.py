from __future__ import annotations
import asyncio
from fastapi import APIRouter
from config import MACHINES
from core.executor import get_sysinfo

router = APIRouter()


@router.get("/api/sysinfo/{machine_key}")
async def sysinfo(machine_key: str):
    if machine_key not in MACHINES:
        return {"error": "unknown machine"}
    try:
        data = await asyncio.to_thread(get_sysinfo, machine_key)
        return {"machine": machine_key, "data": data}
    except Exception as e:
        return {"machine": machine_key, "error": str(e)}

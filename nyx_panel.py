from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from routes.panel import router as panel_router
from routes.sysinfo import router as sysinfo_router

app = FastAPI(title="Nyx Control Panel")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(panel_router)
app.include_router(sysinfo_router)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

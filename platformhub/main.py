"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from platformhub import __version__
from platformhub.database import init_db
from platformhub.routers import admin, auth, catalog, requests

TEMPLATES_DIR = Path(__file__).parent / "templates" / "pages"
STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="PlatformHub",
    description="Developer self-service portal for infrastructure provisioning",
    version=__version__,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(requests.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": __version__}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/catalog", response_class=HTMLResponse)
async def catalog_page(request: Request):
    return templates.TemplateResponse(request, "catalog.html")


@app.get("/new-request/{resource_type}", response_class=HTMLResponse)
async def new_request_page(request: Request, resource_type: str):
    return templates.TemplateResponse(
        request, "new_request.html", {"resource_type": resource_type}
    )


@app.get("/admin/reviews", response_class=HTMLResponse)
async def reviews_page(request: Request):
    return templates.TemplateResponse(request, "reviews.html")

"""MiMo Podcast Production Engine - FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from app.kernel.agent_kernel import AgentKernel
from app.agents import (
    TopicScoutAgent,
    GuestAgent,
    ScriptAgent,
    AudioAgent,
    ClipAgent,
    ShowNoteAgent,
    GrowthAgent,
)
from app.routers.podcast import router as podcast_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

kernel: AgentKernel = None


def create_kernel() -> AgentKernel:
    """Create and configure the agent kernel with all agents."""
    k = AgentKernel()

    k.register_agent("topic_scout", TopicScoutAgent(k))
    k.register_agent("guest_agent", GuestAgent(k))
    k.register_agent("script_agent", ScriptAgent(k))
    k.register_agent("audio_agent", AudioAgent(k))
    k.register_agent("clip_agent", ClipAgent(k))
    k.register_agent("show_note_agent", ShowNoteAgent(k))
    k.register_agent("growth_agent", GrowthAgent(k))

    k.initialize()
    return k


@asynccontextmanager
async def lifespan(app: FastAPI):
    global kernel
    logger.info("Starting MiMo Podcast Production Engine v%s", settings.app_version)
    kernel = create_kernel()
    app.state.kernel = kernel
    logger.info("Kernel ready with %d agents", len(kernel.list_agents()))
    yield
    logger.info("Shutting down MiMo Podcast Production Engine")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered podcast production engine orchestrated by MiMo LLM",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(podcast_router, prefix="/api/v1/podcast", tags=["podcast"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "kernel_initialized": kernel is not None and kernel._initialized,
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = "dashboard/index.html"
    try:
        with open(dashboard_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


def get_kernel() -> AgentKernel:
    return kernel

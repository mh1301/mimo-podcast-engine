"""Podcast API routes."""

import time
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class PipelineRequest(BaseModel):
    episode_id: str
    topic: Optional[str] = None
    niche: Optional[str] = "technology"
    audience: Optional[str] = "general"
    competitors: Optional[list] = []
    audio_file: Optional[str] = None
    platforms: Optional[list] = ["youtube_shorts", "tiktok", "instagram_reels", "twitter"]
    max_clips: Optional[int] = 5
    target_loudness: Optional[float] = -16.0


class AgentRequest(BaseModel):
    task: dict = {}


# Episodes store (in-memory for demo)
episodes = {}


@router.get("/agents")
async def list_agents(request: Request):
    kernel = request.app.state.kernel
    return {"agents": kernel.list_agents()}


@router.get("/status")
async def get_status(request: Request):
    kernel = request.app.state.kernel
    return kernel.get_status()


@router.post("/pipeline")
async def execute_pipeline(req: PipelineRequest, request: Request):
    kernel = request.app.state.kernel
    task = req.model_dump(exclude_none=True)
    task.pop("episode_id")

    result = await kernel.execute_pipeline(req.episode_id, task)

    episodes[req.episode_id] = {
        "episode_id": req.episode_id,
        "status": result.get("status"),
        "run_id": result.get("run_id"),
        "created_at": time.time(),
        "topic": req.topic or task.get("niche", "technology"),
    }

    return result


@router.post("/agent/{name}")
async def execute_agent(name: str, req: AgentRequest, request: Request):
    kernel = request.app.state.kernel
    result = await kernel.execute_agent(name, req.task)
    return result


@router.get("/episodes")
async def list_episodes():
    return {"episodes": list(episodes.values())}


@router.get("/episodes/{episode_id}")
async def get_episode(episode_id: str):
    episode = episodes.get(episode_id)
    if not episode:
        return {"error": "Episode not found"}
    return episode


@router.get("/pipeline/{run_id}")
async def get_pipeline_status(run_id: str, request: Request):
    kernel = request.app.state.kernel
    result = kernel.get_pipeline(run_id)
    if not result:
        return {"error": "Pipeline run not found"}
    return result

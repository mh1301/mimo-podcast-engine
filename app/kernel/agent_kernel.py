"""Agent Kernel - Central orchestration engine for all podcast agents."""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentInfo:
    name: str
    instance: Any
    status: AgentStatus = AgentStatus.IDLE
    last_run: Optional[float] = None
    last_result: Optional[dict] = None
    error: Optional[str] = None
    run_count: int = 0


@dataclass
class PipelineRun:
    run_id: str
    episode_id: str
    agents: List[str]
    status: str = "pending"
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    results: Dict[str, dict] = field(default_factory=dict)
    current_agent: Optional[str] = None


class Event:
    """Simple event for the bus."""

    def __init__(self, event_type: str, source: str, data: dict):
        self.event_type = event_type
        self.source = source
        self.data = data
        self.timestamp = time.time()


class EventBus:
    """Publish-subscribe event bus for agent communication."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    async def publish(self, event: Event):
        subscribers = self._subscribers.get(event.event_type, [])
        tasks = [callback(event) for callback in subscribers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.debug(
            "Event '%s' from '%s' delivered to %d subscribers",
            event.event_type,
            event.source,
            len(tasks),
        )


class AgentKernel:
    """Central kernel that registers agents, manages the event bus,
    and orchestrates pipeline execution."""

    def __init__(self):
        self.event_bus = EventBus()
        self._agents: Dict[str, AgentInfo] = {}
        self._pipelines: Dict[str, PipelineRun] = {}
        self._initialized = False
        logger.info("AgentKernel created")

    def register_agent(self, name: str, agent_instance: Any):
        """Register an agent with the kernel."""
        if name in self._agents:
            logger.warning("Agent '%s' already registered, overwriting", name)
        self._agents[name] = AgentInfo(name=name, instance=agent_instance)
        logger.info("Registered agent: %s", name)

    def get_agent(self, name: str) -> Optional[Any]:
        info = self._agents.get(name)
        return info.instance if info else None

    def list_agents(self) -> List[dict]:
        return [
            {
                "name": info.name,
                "status": info.status.value,
                "run_count": info.run_count,
                "last_run": info.last_run,
                "error": info.error,
            }
            for info in self._agents.values()
        ]

    def get_status(self) -> dict:
        return {
            "initialized": self._initialized,
            "agent_count": len(self._agents),
            "agents": self.list_agents(),
            "pipeline_count": len(self._pipelines),
        }

    async def execute_agent(self, name: str, task: dict) -> dict:
        """Execute a single agent by name."""
        info = self._agents.get(name)
        if not info:
            return {"error": f"Agent '{name}' not found"}

        info.status = AgentStatus.RUNNING
        await self.event_bus.publish(
            Event("agent.started", name, {"task": task})
        )

        try:
            result = await info.instance.execute(task)
            info.status = AgentStatus.COMPLETED
            info.last_result = result
            info.last_run = time.time()
            info.run_count += 1
            info.error = None
            await self.event_bus.publish(
                Event("agent.completed", name, {"result": result})
            )
            return result
        except Exception as exc:
            info.status = AgentStatus.FAILED
            info.error = str(exc)
            logger.exception("Agent '%s' failed", name)
            await self.event_bus.publish(
                Event("agent.failed", name, {"error": str(exc)})
            )
            return {"error": str(exc)}

    async def execute_pipeline(
        self, episode_id: str, task: dict, agent_order: Optional[List[str]] = None
    ) -> dict:
        """Execute agents in sequence, passing accumulated context."""
        run_id = f"run-{episode_id}-{int(time.time())}"

        if agent_order is None:
            agent_order = [
                "topic_scout",
                "guest_agent",
                "script_agent",
                "audio_agent",
                "clip_agent",
                "show_note_agent",
                "growth_agent",
            ]

        run = PipelineRun(
            run_id=run_id,
            episode_id=episode_id,
            agents=agent_order,
        )
        run.status = "running"
        run.started_at = time.time()
        self._pipelines[run_id] = run

        context = {**task, "episode_id": episode_id}
        results = {}

        for agent_name in agent_order:
            run.current_agent = agent_name
            await self.event_bus.publish(
                Event("pipeline.step", "kernel", {"agent": agent_name, "run_id": run_id})
            )

            result = await self.execute_agent(agent_name, context)
            results[agent_name] = result

            if "error" in result and not result.get("warning"):
                run.status = "failed"
                run.completed_at = time.time()
                return {
                    "run_id": run_id,
                    "episode_id": episode_id,
                    "status": "failed",
                    "failed_at": agent_name,
                    "results": results,
                }

            context = {**context, agent_name: result}

        run.status = "completed"
        run.completed_at = time.time()
        run.results = results
        run.current_agent = None

        await self.event_bus.publish(
            Event("pipeline.completed", "kernel", {"run_id": run_id})
        )

        return {
            "run_id": run_id,
            "episode_id": episode_id,
            "status": "completed",
            "duration": run.completed_at - run.started_at,
            "results": results,
        }

    def get_pipeline(self, run_id: str) -> Optional[dict]:
        run = self._pipelines.get(run_id)
        if not run:
            return None
        return {
            "run_id": run.run_id,
            "episode_id": run.episode_id,
            "status": run.status,
            "agents": run.agents,
            "current_agent": run.current_agent,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "results": run.results,
        }

    def initialize(self):
        """Mark kernel as initialized."""
        self._initialized = True
        logger.info("AgentKernel initialized with %d agents", len(self._agents))

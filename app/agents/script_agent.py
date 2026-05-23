"""ScriptAgent - Episode outlining, talking points, and segment transitions."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ScriptAgent:
    """Generates episode outlines, talking points, and natural transitions."""

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.name = "script_agent"
        logger.info("ScriptAgent initialized")

    async def execute(self, task: dict) -> dict:
        logger.info("ScriptAgent executing")
        start = time.time()

        outline = await self._create_outline(task)
        talking_points = await self._generate_talking_points(task, outline)
        transitions = await self._write_transitions(outline)

        return {
            "agent": self.name,
            "outline": outline,
            "talking_points": talking_points,
            "transitions": transitions,
            "estimated_duration": outline.get("total_duration", "45min"),
            "duration": time.time() - start,
        }

    async def _create_outline(self, task: dict) -> dict:
        """Create a structured episode outline."""
        topics = task.get("topic_scout", {}).get("recommended_topics", [])
        topic = topics[0]["topic"] if topics else task.get("topic", "General Discussion")
        logger.info("Creating outline for: %s", topic)

        return {
            "title": f"Episode: {topic}",
            "segments": [
                {"name": "Intro", "duration": "3min", "type": "intro"},
                {"name": "Main Discussion", "duration": "25min", "type": "content"},
                {"name": "Guest Interview", "duration": "15min", "type": "interview"},
                {"name": "Rapid Fire", "duration": "5min", "type": "interactive"},
                {"name": "Outro", "duration": "2min", "type": "outro"},
            ],
            "total_duration": "50min",
        }

    async def _generate_talking_points(self, task: dict, outline: dict) -> list:
        """Generate detailed talking points for each segment."""
        points = []
        for segment in outline.get("segments", []):
            points.append({
                "segment": segment["name"],
                "points": [
                    f"Key point 1 for {segment['name']}",
                    f"Key point 2 for {segment['name']}",
                    f"Supporting example for {segment['name']}",
                ],
                "notes": "Expand with MiMo LLM context",
            })
        return points

    async def _write_transitions(self, outline: dict) -> list:
        """Generate natural transitions between segments."""
        segments = outline.get("segments", [])
        transitions = []
        for i in range(len(segments) - 1):
            transitions.append({
                "from": segments[i]["name"],
                "to": segments[i + 1]["name"],
                "text": f"Moving from {segments[i]['name']} to {segments[i + 1]['name']}...",
                "style": "conversational",
            })
        return transitions

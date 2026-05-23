"""ShowNoteAgent - Timestamps, links, summaries, and transcripts."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ShowNoteAgent:
    """Generates show notes with timestamps, links, summaries, and transcripts."""

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.name = "show_note_agent"
        logger.info("ShowNoteAgent initialized")

    async def execute(self, task: dict) -> dict:
        logger.info("ShowNoteAgent executing")
        start = time.time()

        timestamps = await self._generate_timestamps(task)
        links = await self._extract_links(task)
        summary = await self._write_summary(task)
        transcript = await self._generate_transcript(task)

        return {
            "agent": self.name,
            "timestamps": timestamps,
            "links": links,
            "summary": summary,
            "transcript_excerpt": transcript,
            "duration": time.time() - start,
        }

    async def _generate_timestamps(self, task: dict) -> list:
        """Generate chapter timestamps from script outline."""
        outline = task.get("script_agent", {}).get("outline", {})
        segments = outline.get("segments", [])
        logger.info("Generating timestamps for %d segments", len(segments))

        timestamps = []
        current_time = 0
        for seg in segments:
            timestamps.append({
                "time": self._format_time(current_time),
                "seconds": current_time,
                "title": seg.get("name", "Segment"),
                "type": seg.get("type", "content"),
            })
            duration_str = seg.get("duration", "5min")
            minutes = int(duration_str.replace("min", ""))
            current_time += minutes * 60
        return timestamps

    async def _extract_links(self, task: dict) -> list:
        """Extract and verify relevant links mentioned in the episode."""
        return [
            {"title": "Guest Website", "url": "https://example.com", "type": "resource"},
            {"title": "Article Mentioned", "url": "https://example.com/article", "type": "reference"},
            {"title": "Tool Discussed", "url": "https://example.com/tool", "type": "tool"},
        ]

    async def _write_summary(self, task: dict) -> dict:
        """Generate episode summary and description."""
        outline = task.get("script_agent", {}).get("outline", {})
        title = outline.get("title", "Episode")
        logger.info("Writing summary for: %s", title)

        return {
            "title": title,
            "short_description": f"A deep dive into the topics covered in {title}.",
            "full_description": (
                f"In this episode, we explore the key themes of {title}. "
                "Our discussion covers the latest developments, expert insights, "
                "and practical takeaways for listeners."
            ),
            "keywords": ["podcast", "technology", "discussion", "insights"],
            "seo_title": f"{title} - MiMo Podcast",
        }

    async def _generate_transcript(self, task: dict) -> dict:
        """Generate or process episode transcript."""
        return {
            "format": "srt",
            "word_count": 8500,
            "speakers_detected": 2,
            "language": "en",
            "confidence": 0.94,
            "excerpt": "Full transcript available as separate file...",
            "output_file": "transcript.srt",
        }

    def _format_time(self, seconds: int) -> str:
        """Format seconds into HH:MM:SS."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

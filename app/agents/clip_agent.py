"""ClipAgent - Short-form clip extraction for social media platforms."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ClipAgent:
    """Extracts and formats short-form clips for social media distribution."""

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.name = "clip_agent"
        logger.info("ClipAgent initialized")

    async def execute(self, task: dict) -> dict:
        logger.info("ClipAgent executing")
        start = time.time()

        highlights = task.get("audio_agent", {}).get("highlights", [])
        clips = await self._extract_clips(highlights, task)
        formatted = await self._format_for_platforms(clips, task)

        return {
            "agent": self.name,
            "clips": clips,
            "platform_formats": formatted,
            "total_clips": len(clips),
            "duration": time.time() - start,
        }

    async def _extract_clips(self, highlights: list, task: dict) -> list:
        """Extract clips from audio based on detected highlights."""
        max_clips = task.get("max_clips", 5)
        logger.info("Extracting up to %d clips from %d highlights", max_clips, len(highlights))

        clips = []
        for i, h in enumerate(highlights[:max_clips]):
            clips.append({
                "clip_id": f"clip_{i + 1}",
                "start": h.get("timestamp", 0),
                "end": h.get("end", h.get("timestamp", 0) + 30),
                "duration": h.get("end", 30) - h.get("timestamp", 0),
                "highlight_type": h.get("type", "general"),
                "score": h.get("score", 0.5),
                "transcript": h.get("description", ""),
                "output_file": f"clip_{i + 1}.mp4",
            })
        return clips

    async def _format_for_platforms(self, clips: list, task: dict) -> dict:
        """Generate platform-specific versions of each clip."""
        platforms = task.get("platforms", ["youtube_shorts", "tiktok", "instagram_reels", "twitter"])
        logger.info("Formatting clips for platforms: %s", platforms)

        formatted = {}
        for platform in platforms:
            specs = self._get_platform_specs(platform)
            formatted[platform] = [
                {
                    "clip_id": c["clip_id"],
                    "resolution": specs["resolution"],
                    "aspect_ratio": specs["aspect_ratio"],
                    "max_duration": specs["max_duration"],
                    "captions": True,
                    "output_file": f"{platform}_{c['clip_id']}.mp4",
                }
                for c in clips
            ]
        return formatted

    def _get_platform_specs(self, platform: str) -> dict:
        """Return platform-specific video specifications."""
        specs = {
            "youtube_shorts": {"resolution": "1080x1920", "aspect_ratio": "9:16", "max_duration": 60},
            "tiktok": {"resolution": "1080x1920", "aspect_ratio": "9:16", "max_duration": 180},
            "instagram_reels": {"resolution": "1080x1920", "aspect_ratio": "9:16", "max_duration": 90},
            "twitter": {"resolution": "1280x720", "aspect_ratio": "16:9", "max_duration": 140},
            "linkedin": {"resolution": "1920x1080", "aspect_ratio": "16:9", "max_duration": 600},
        }
        return specs.get(platform, {"resolution": "1080x1920", "aspect_ratio": "9:16", "max_duration": 60})

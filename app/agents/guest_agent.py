"""GuestAgent - Guest discovery, outreach automation, and interview brief generation."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class GuestAgent:
    """Finds suitable guests, automates outreach, and generates interview briefs."""

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.name = "guest_agent"
        logger.info("GuestAgent initialized")

    async def execute(self, task: dict) -> dict:
        logger.info("GuestAgent executing")
        start = time.time()

        candidates = await self._find_guests(task)
        outreach = await self._generate_outreach(candidates, task)
        briefs = await self._create_briefs(candidates, task)

        return {
            "agent": self.name,
            "candidates": candidates,
            "outreach_messages": outreach,
            "interview_briefs": briefs,
            "duration": time.time() - start,
        }

    async def _find_guests(self, task: dict) -> list:
        """Find potential guests based on topic and audience."""
        topics = task.get("topic_scout", {}).get("recommended_topics", [])
        topic_text = topics[0]["topic"] if topics else task.get("topic", "general")
        logger.info("Finding guests for topic: %s", topic_text)

        return [
            {
                "name": f"Expert_{i}",
                "expertise": topic_text,
                "platform": "twitter",
                "followers": 10000 * (3 - i),
                "relevance_score": 95 - i * 5,
            }
            for i in range(3)
        ]

    async def _generate_outreach(self, candidates: list, task: dict) -> list:
        """Generate personalized outreach messages via MiMo LLM."""
        messages = []
        for candidate in candidates:
            messages.append({
                "guest": candidate["name"],
                "subject": f"Podcast Invitation: {candidate['expertise']}",
                "body": f"Hi {candidate['name']}, we'd love to have you on our podcast to discuss {candidate['expertise']}...",
                "channel": "email",
                "status": "draft",
            })
        return messages

    async def _create_briefs(self, candidates: list, task: dict) -> list:
        """Create interview briefs for confirmed guests."""
        return [
            {
                "guest": c["name"],
                "background_summary": f"Expert in {c['expertise']} with {c['followers']} followers",
                "key_questions": [
                    f"What is your approach to {c['expertise']}?",
                    "What trends do you see emerging?",
                    "What advice would you give beginners?",
                ],
                "talking_points": ["career", "current_work", "predictions"],
                "estimated_duration": "45min",
            }
            for c in candidates
        ]

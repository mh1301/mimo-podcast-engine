# MiMo Podcast Production Engine

AI-powered podcast production pipeline orchestrated by the MiMo LLM through an agent kernel architecture.

```
                    ┌─────────────────────────────────────┐
                    │       FastAPI Application            │
                    │   /api/v1/podcast/*                  │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │         Agent Kernel                 │
                    │  ┌─────────────────────────────┐    │
                    │  │  register / execute / status │    │
                    │  │       Event Bus              │    │
                    │  └─────────────────────────────┘    │
                    └──┬───┬───┬───┬───┬───┬───┬─────────┘
                       │   │   │   │   │   │   │
          ┌──────┐ ┌───▼┐ ┌▼──┐┌▼──┐┌▼──┐┌▼──┐┌▼───┐
          │Topic │ │Guest│ │Scr││Aud││Cli││Sho││Grow│
          │Scout │ │Agent│ │ipt││io ││p  ││wN ││th  │
          │      │ │     │ │   ││   ││   ││ote││    │
          └──────┘ └─────┘ └───┘└───┘└───┘└───┘└────┘

   Pipeline: Topic -> Guest -> Script -> Audio -> Clip -> ShowNote -> Growth
```

## File Structure

```
mimo-podcast-engine/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   └── settings.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── kernel/
│   │   ├── __init__.py
│   │   └── agent_kernel.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── topic_scout.py
│   │   ├── guest_agent.py
│   │   ├── script_agent.py
│   │   ├── audio_agent.py
│   │   ├── clip_agent.py
│   │   ├── show_note_agent.py
│   │   └── growth_agent.py
│   └── routers/
│       ├── __init__.py
│       └── podcast.py
└── dashboard/
    └── index.html
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Async API framework
- **MiMo LLM** - Nous Research reasoning model for agent intelligence
- **Docker / Docker Compose** - Containerization
- **Pydantic** - Settings and validation
- **Uvicorn** - ASGI server

## Agents

| Agent | Purpose |
|-------|---------|
| **TopicScout** | Trending topic discovery, audience analysis, competitor monitoring |
| **GuestAgent** | Guest matching, outreach automation, interview brief generation |
| **ScriptAgent** | Episode outlining, talking points, segment transitions |
| **AudioAgent** | Noise reduction, loudness leveling, highlight detection |
| **ClipAgent** | Short-form clip extraction for social platforms |
| **ShowNoteAgent** | Timestamps, link extraction, summaries, transcripts |
| **GrowthAgent** | SEO optimization, platform-specific packaging, cross-promotion |

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/podcast/agents` - List registered agents
- `GET /api/v1/podcast/status` - Kernel and agent status
- `POST /api/v1/podcast/pipeline` - Execute full pipeline
- `POST /api/v1/podcast/agent/{name}` - Execute single agent
- `GET /api/v1/podcast/episodes` - Episode tracker
- `GET /dashboard` - Serve dashboard HTML

## How to Run

```bash
# Local
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Docker
docker-compose up --build

# Dashboard
open http://localhost:8000/dashboard
```

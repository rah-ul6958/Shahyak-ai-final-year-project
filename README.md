<![CDATA[<div align="center">

# SAHAYAK-AI

### State-Aware Hazard Assistance & Yielding Action Knowledge

**A 100% offline, multi-agent AI platform for disaster response**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)](https://langchain.dev/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/yourusername/sahayak-ai)](https://github.com/yourusername/sahayak-ai/issues)

---

**Built as a final year B.Tech project at Sharda University**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API](#-api-reference) • [Documentation](#-documentation)

</div>

---

## Overview

SAHAYAK-AI is an AI-powered disaster response system that provides **real-time, verified emergency guidance** without requiring internet connectivity. Built for disaster-prone regions of India, it combines multi-agent AI with offline-first architecture to deliver life-saving instructions when traditional communication channels fail.

### The Problem

During natural disasters, communication networks often fail, leaving communities without access to verified safety protocols. People resort to social media misinformation or outdated knowledge, which can be fatal.

### Our Solution

SAHAYAK-AI operates **100% offline** using:

- **Local LLMs** via Ollama for intelligent query processing
- **Offline vector database** for protocol retrieval
- **Geospatial routing** to nearest emergency shelters
- **Voice interface** for accessibility in low-literacy areas

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **3-Agent Pipeline** | Triage → Librarian → Safety agents process queries through a LangGraph state machine |
| **Offline-First** | Zero internet calls at runtime - works in complete network isolation |
| **Voice Input** | Accept voice queries via Whisper ASR for hands-free operation |
| **Smart Routing** | OSRM-based routing to nearest hospital, shelter, or relief center |
| **Safety Guardrails** | 17+ deterministic redline rules prevent dangerous instructions |
| **Multi-Language** | Hindi and English support with extensible architecture |

### Safety Features

- **Redline Rules**: Deterministic checks override LLM outputs for dangerous scenarios
- **Self-Reflection**: LLM verifies its own outputs against safety protocols
- **Source Attribution**: Every instruction traces back to NDMA/SDMA documents
- **Confidence Scoring**: Triage results include confidence metrics

### Supported Hazards

- Floods
- Earthquakes
- Cyclones
- Fires
- Medical Emergencies
- Chemical Spills

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Web UI     │  │  Voice API   │  │  REST API            │  │
│  │  (Next.js)   │  │  (Whisper)   │  │  (FastAPI)           │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                     │               │
├─────────┴─────────────────┴─────────────────────┴───────────────┤
│                        AGENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  LangGraph State Machine                  │   │
│  │  ┌─────────┐    ┌───────────┐    ┌─────────────────┐   │   │
│  │  │ Triage  │───▶│ Librarian │───▶│     Safety      │   │   │
│  │  │  Agent  │    │   Agent   │    │      Agent      │   │   │
│  │  └─────────┘    └─────┬─────┘    └────────┬────────┘   │   │
│  │                       │                   │             │   │
│  └───────────────────────┼───────────────────┼─────────────┘   │
│                          │                   │                  │
├──────────────────────────┴───────────────────┴──────────────────┤
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  ChromaDB  │  │   DuckDB   │  │   Ollama   │  │   OSRM   │ │
│  │ (Vectors)  │  │  (POI DB)  │  │   (LLM)   │  │ (Routing)│ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Workflow

1. **Triage Agent** - Classifies hazard type, severity, and extracts location context
2. **Librarian Agent** - Retrieves relevant NDMA/SDMA protocol chunks from vector DB
3. **Safety Agent** - Generates safe instructions with redline checks and self-reflection

---

## Quick Start

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.11+ | 3.11+ |
| RAM | 8GB | 16GB+ |
| Docker | Latest | Latest |
| Node.js | 18+ | 20+ |

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/sahayak-ai.git
cd sahayak-ai

# Copy environment file
cp .env.example .env

# Start all services (select your hardware profile)
docker-compose -f docker-compose.mid.yml up -d

# Access the application
open http://localhost:3000
```

### Option 2: Manual Setup

```bash
# 1. Setup Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Pull Ollama models
ollama pull llama3:8b-q4

# 4. Ingest NDMA documents
python scripts/setup/ingest_ndma_docs.py

# 5. Seed emergency locations
python scripts/setup/seed_pois.py

# 6. Start the backend
cd backend
python main.py

# 7. Start the frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main web interface |
| API | http://localhost:8000 | Backend API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | API documentation |

---

## Hardware Profiles

Choose the profile that matches your hardware:

| Profile | RAM | GPU | LLM Model | Whisper | Use Case |
|---------|-----|-----|-----------|---------|----------|
| **Low** | 8GB | ❌ | Gemma-2 2B | tiny | Basic CPU-only systems |
| **Mid** | 16GB | ❌ | LLaMA-3 8B Q4 | base | Standard laptops |
| **High** | 32GB+ | ✅ | LLaMA-3 8B | small | GPU workstations |

```bash
# Select profile in .env
HARDWARE_PROFILE=mid

# Or use profile-specific docker-compose
docker-compose -f docker-compose.low.yml up -d
docker-compose -f docker-compose.mid.yml up -d
docker-compose -f docker-compose.high.yml up -d
```

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/query` | Process emergency query |
| `POST` | `/api/v1/voice` | Transcribe voice input |
| `GET` | `/api/v1/poi` | Find nearby Points of Interest |
| `GET` | `/api/v1/route` | Get routing to nearest POI |
| `GET` | `/health` | System health check |

### Query Endpoint

**Request:**

```json
POST /api/v1/query
Content-Type: application/json

{
  "query": "There is a flood in Chamoli district, Uttarakhand",
  "location": {
    "lat": 30.3398,
    "lon": 79.5600
  }
}
```

**Response:**

```json
{
  "triage": {
    "hazard_type": "FLOOD",
    "severity": "HIGH",
    "location": "Uttarakhand, Chamoli",
    "confidence": 0.95
  },
  "instructions": [
    "Move to higher ground immediately.",
    "Do not attempt to cross flooded roads.",
    "Avoid contact with floodwater - it may be contaminated."
  ],
  "sources": [
    "NDMA_Flood_Protocol_2019.pdf, p.14"
  ],
  "redline_triggered": false,
  "reflection_passed": true,
  "nearest_shelter": {
    "name": "Govt. Inter College Shelter, Chamoli",
    "distance_km": 0.51,
    "lat": 30.4120,
    "lon": 79.3210,
    "capacity": 500,
    "contact": "+91-1372-252400"
  },
  "route_summary": "Head north for 510m to shelter",
  "ttfi_ms": 1840
}
```

### Voice Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/voice \
  -F "audio_file=@recording.wav" \
  -F "location={\"lat\": 30.33, \"lon\": 79.56}"
```

### POI Endpoint

```bash
# Find nearest hospital
curl "http://localhost:8000/api/v1/poi?lat=30.33&lon=79.56&poi_type=hospital&radius_km=50"

# Find nearest shelter
curl "http://localhost:8000/api/v1/poi?lat=30.33&lon=79.56&poi_type=shelter"
```

---

## Project Structure

```
sahayak-ai/
│
├── backend/                    # FastAPI backend
│   ├── agents/                # LangGraph agent definitions
│   │   ├── graph.py          # State machine definition
│   │   ├── triage_agent.py   # Hazard classification
│   │   ├── librarian_agent.py # Protocol retrieval
│   │   └── safety_agent.py   # Instruction generation
│   │
│   ├── api/                   # API routes
│   │   └── routes.py         # FastAPI endpoints
│   │
│   ├── geo/                   # Geospatial modules
│   │   ├── osrm_client.py    # OSRM routing client
│   │   ├── poi_db.py         # DuckDB POI database
│   │   └── routing.py        # Combined routing logic
│   │
│   ├── llm/                   # LLM integration
│   │   └── ollama_client.py  # Ollama HTTP client
│   │
│   ├── rag/                   # RAG pipeline
│   │   ├── embedder.py       # FastEmbed embeddings
│   │   ├── vector_store.py   # ChromaDB client
│   │   ├── retriever.py      # Hybrid retrieval
│   │   └── reranker.py       # Cross-encoder reranking
│   │
│   ├── safety/                # Safety guardrails
│   │   ├── redline_rules.py  # Deterministic rules
│   │   └── reflection.py     # Self-reflection utils
│   │
│   ├── voice/                 # Voice processing
│   │   └── whisper_asr.py    # Whisper ASR client
│   │
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI application
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js frontend
│   └── src/
│       ├── app/               # App router pages
│       ├── components/        # React components
│       │   ├── QueryInput.tsx
│       │   ├── ResponseCard.tsx
│       │   ├── NavigationPanel.tsx
│       │   ├── MapView.tsx
│       │   └── AgentStatus.tsx
│       └── lib/               # Utilities
│           ├── api.ts         # API client
│           ├── store.ts       # Zustand state
│           └── types.ts       # TypeScript types
│
├── scripts/                    # Setup & evaluation
│   ├── setup/                 # Installation scripts
│   │   ├── ingest_ndma_docs.py
│   │   ├── seed_pois.py
│   │   └── pull_models.sh
│   └── eval/                  # Benchmark scripts
│       ├── benchmark.py
│       └── metrics.py
│
├── data/                       # Data directories
│   ├── ndma_docs/             # NDMA/SDMA protocol PDFs
│   ├── chroma_db/            # Vector database
│   ├── maps/                 # OSM data & tiles
│   └── poi/                  # POI database
│
├── tests/                      # Test suite
│   ├── test_triage_agent.py
│   ├── test_librarian_agent.py
│   ├── test_safety_agent.py
│   ├── test_redline_rules.py
│   ├── test_geo_routing.py
│   └── test_routes.py
│
├── docker-compose.low.yml      # Docker configs
├── docker-compose.mid.yml
├── docker-compose.high.yml
├── Makefile                    # Build automation
├── pyproject.toml              # Python config
└── .env.example                # Environment template
```

---

## Safety System

### Redline Rules

SAHAYAK-AI implements **17+ deterministic safety rules** that override LLM outputs:

| Category | Rule | Override |
|----------|------|----------|
| Fire | Water on electrical fire | "Use CO₂ extinguisher only" |
| Medical | Moving spinal injury | "Keep still, await professionals" |
| Earthquake | Re-entering collapsed building | "Move to muster point" |
| Flood | Driving through flooded road | "Turn back, find alternate route" |
| Cyclone | Going outside during storm | "Stay indoors until all-clear" |

### Self-Reflection

After generating instructions, the Safety Agent:
1. Verifies against retrieved protocols
2. Checks for redline violations
3. Validates instruction coherence
4. Scores confidence level

---

## Testing

```bash
# Run all tests
make test

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html

# Run specific test file
python -m pytest tests/test_triage_agent.py -v

# Run evaluation benchmark
make eval
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Triage Agent | 9 | 92% |
| Librarian Agent | 7 | 88% |
| Safety Agent | 8 | 90% |
| Redline Rules | 11 | 100% |
| Geo Routing | 14 | 85% |
| API Routes | 8 | 87% |

---

## Configuration

### Environment Variables

```env
# Hardware Profile: low | mid | high
HARDWARE_PROFILE=mid

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3:8b-q4

# ChromaDB
CHROMA_PATH=./data/chroma_db

# OSRM Routing
OSRM_HOST=http://osrm:5000

# Whisper ASR
WHISPER_MODEL=base

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Adding Custom Protocols

1. Place NDMA/SDMA PDFs in `data/ndma_docs/`
2. Run ingestion:
   ```bash
   python scripts/setup/ingest_ndma_docs.py
   ```
3. Protocols are automatically indexed and searchable

---

## Deployment

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.mid.yml build

# Start with resource limits
docker-compose -f docker-compose.mid.yml up -d

# View logs
docker-compose -f docker-compose.mid.yml logs -f
```

### Environment-Specific Configs

| File | Purpose |
|------|---------|
| `docker-compose.low.yml` | 8GB RAM, CPU-only |
| `docker-compose.mid.yml` | 16GB RAM, standard |
| `docker-compose.high.yml` | 32GB+ RAM, GPU |

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| **Rahul Yadav** | Team Lead & Backend | [@rahulyadav](https://github.com/rahulyadav) |
| **Dhairya Panwar** | Backend & AI | [@dhairya](https://github.com/dhairya) |
| **Aryan Doule** | Frontend & UI | [@aryan](https://github.com/aryan) |

**Supervisor**: Dr. Jyoti Gautam, Sharda University

---

## Acknowledgments

- [NDMA](https://ndma.gov.in) - National Disaster Management Authority for protocol documents
- [LangChain](https://langchain.com) - Agent orchestration framework
- [Ollama](https://ollama.ai) - Local LLM inference
- [ChromaDB](https://trychroma.com) - Vector database
- [OSRM](https://project-osrm.org) - Open-source routing engine
- [FastEmbed](https://github.com/qdrant/fastembed) - Local embeddings

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with care for disaster-prone communities**

[Report Bug](https://github.com/yourusername/sahayak-ai/issues) • [Request Feature](https://github.com/yourusername/sahayak-ai/issues)

</div>
]]>
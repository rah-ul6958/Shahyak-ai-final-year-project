# SAHAYAK-AI

<div align="center">

### State-Aware Hazard Assistance & Yielding Action Knowledge

**A 100% Offline Multi-Agent AI Platform for Disaster Response**

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black)
![LangGraph](https://img.shields.io/badge/LangGraph-AI-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

---

## Overview

**SAHAYAK-AI** is an offline-first disaster response platform designed to provide reliable emergency guidance even when internet connectivity is unavailable.

The system combines a **LangGraph multi-agent pipeline**, **local Large Language Models**, and **Retrieval-Augmented Generation (RAG)** to retrieve verified NDMA/SDMA disaster protocols and generate safe, context-aware emergency instructions.

It also supports **voice interaction**, **offline routing to nearby shelters**, and deterministic **safety guardrails** to minimize unsafe AI responses.

---

## Key Features

* 100% Offline operation
* Multi-Agent LangGraph workflow
* Retrieval-Augmented Generation (RAG)
* Local LLM inference using Ollama
* Voice input support
* Offline shelter & hospital routing
* NDMA/SDMA protocol retrieval
* Deterministic safety guardrails
* Hindi & English support
* FastAPI REST API
* Modern Next.js frontend

---

## Architecture

```text
                 User
                   │
         ┌──────────────────┐
         │   Next.js UI     │
         └────────┬─────────┘
                  │
             FastAPI Backend
                  │
        LangGraph Agent Pipeline
                  │
    ┌─────────┬──────────┬─────────┐
    │ Triage  │ Librarian│ Safety  │
    └─────────┴──────────┴─────────┘
                  │
       ChromaDB + Ollama + DuckDB
                  │
       Offline Routing (OSRM)
```

---

## Agent Workflow

### Triage Agent

* Identifies disaster type
* Determines severity
* Extracts location
* Calculates confidence score

### Librarian Agent

* Searches local vector database
* Retrieves relevant NDMA/SDMA protocols
* Supplies verified context

### Safety Agent

* Generates final response
* Applies safety guardrails
* Prevents unsafe instructions
* Returns verified emergency guidance

---

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* FastAPI
* LangGraph
* Ollama
* ChromaDB
* DuckDB
* Whisper
* OSRM

### AI & RAG

* Local LLMs
* FastEmbed
* Vector Search
* Retrieval-Augmented Generation

---

## Project Structure

```text
sahayak-ai/

├── backend/
│   ├── agents/
│   ├── api/
│   ├── rag/
│   ├── geo/
│   ├── safety/
│   ├── voice/
│   └── main.py
│
├── frontend/
│   ├── src/
│   └── public/
│
├── data/
│
├── scripts/
│
├── tests/
│
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/sahayak-ai.git

cd sahayak-ai
```

### Create Environment File

```bash
cp .env.example .env
```

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

### Run Backend

```bash
uvicorn main:app --reload
```

---

## Docker

```bash
docker compose up --build
```

---

## API Endpoints

| Method | Endpoint        | Description                 |
| ------ | --------------- | --------------------------- |
| POST   | `/api/v1/query` | Process emergency query     |
| POST   | `/api/v1/voice` | Voice input                 |
| GET    | `/api/v1/poi`   | Nearby hospitals & shelters |
| GET    | `/api/v1/route` | Offline route generation    |
| GET    | `/health`       | Health check                |

---

## Safety Features

SAHAYAK-AI prioritizes safe and reliable responses through multiple layers of protection:

* Deterministic safety rules
* Verified NDMA/SDMA protocol retrieval
* Source attribution
* Agent self-validation
* Confidence scoring
* Hallucination reduction using RAG

---

## Supported Disaster Types

* Flood
* Earthquake
* Cyclone
* Fire
* Medical Emergency
* Chemical Spill

---

## Screenshots

Add screenshots here.

```text
screenshots/
├── home.png
├── query.png
├── map.png
└── response.png
```

---

## Future Improvements

* Additional Indian language support
* Satellite imagery integration
* SMS-based emergency communication
* Offline mobile application
* Real-time disaster alerts
* Multi-modal document retrieval

---

## Team

| Name           | Role                     |
| -------------- | ------------------------ |
| Rahul Yadav    | Team Lead • Backend • AI |
| Dhairya Panwar | AI & Backend             |
| Aryan Doule    | Frontend                 |

**Project Supervisor**

Dr. Jyoti Gautam

Sharda University

---

## License

This project is licensed under the **MIT License**.

---

## Acknowledgements

This project utilizes several open-source technologies, including:

* LangGraph
* FastAPI
* Ollama
* ChromaDB
* Whisper
* DuckDB
* OSRM
* Next.js

---

<div align="center">

### Built to deliver reliable offline AI assistance during disasters.

⭐ If you found this project useful, consider giving it a star.

</div>

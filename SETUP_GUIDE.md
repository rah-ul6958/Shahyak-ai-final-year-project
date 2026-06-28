# SAHAYAK-AI Setup & Run Guide

## ✅ Project Status
All critical errors have been fixed. The project is now ready to run!

## 📋 Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Docker (optional, for containerized setup)
- 8GB+ RAM recommended

## 🚀 Quick Start (Development Mode)

### 1. Backend Setup & Run

```bash
# Navigate to backend
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama (in separate terminal - required for LLM)
ollama serve

# In another terminal, pull the model
ollama pull llama3:8b-q4

# Run the backend
python main.py
# or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Frontend Setup & Run

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Process Emergency Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "There is a flood in Chamoli district, Uttarakhand",
    "location": {"lat": 30.33, "lon": 79.56}
  }'
```

### Find Nearby Shelters
```bash
curl http://localhost:8000/api/v1/poi?lat=30.33&lon=79.56&poi_type=shelter
```

### Get Route to Nearest Shelter
```bash
curl http://localhost:8000/api/v1/route?from_lat=30.33&from_lon=79.56&poi_type=shelter
```

### Process Voice Input
```bash
curl -X POST http://localhost:8000/api/v1/voice \
  -F "audio_file=@voice_input.wav"
```

## 🐳 Docker Setup (Optional)

For containerized deployment:

```bash
# Use the appropriate compose file based on hardware
docker-compose -f docker-compose.mid.yml up -d
```

## 📂 Project Structure

```
sahayak-ai/
├── backend/                    # FastAPI backend (Python)
│   ├── agents/                # LangGraph agents (3-agent pipeline)
│   ├── api/                   # API routes and endpoints
│   ├── geo/                   # Geospatial services (OSRM, POI database)
│   ├── llm/                   # Ollama LLM client
│   ├── rag/                   # RAG pipeline (retrieval, embeddings, reranking)
│   ├── safety/                # Safety guardrails and redline rules
│   ├── voice/                 # Whisper ASR for speech-to-text
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI app entry point
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Next.js frontend
│   └── src/
│       ├── app/               # Page components
│       ├── components/        # React components
│       └── lib/               # Utility functions
│
├── data/                       # Data directories (created on setup)
│   ├── chroma_db/            # ChromaDB vector store
│   ├── poi/                  # POI database
│   ├── models/               # Model caches
│   └── maps/                 # Geospatial data
│
├── scripts/                    # Setup and utility scripts
│   ├── setup/                # Installation scripts
│   └── eval/                 # Evaluation benchmarks
│
├── .env                       # Environment configuration (copy from .env.example)
├── Makefile                   # Build automation
└── README.md                  # Project documentation
```

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# Hardware Profile
HARDWARE_PROFILE=mid  # Options: low, mid, high

# Ollama (LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:8b-q4

# Vector Database
CHROMA_PATH=./data/chroma_db

# OSRM Routing
OSRM_HOST=http://osrm:5000

# Speech Recognition
WHISPER_MODEL=base  # Options: tiny, base, small

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

## 🔄 Typical Workflow

1. **Start Ollama Service**
   ```bash
   ollama serve
   ```

2. **In Another Terminal, Pull Model**
   ```bash
   ollama pull llama3:8b-q4
   ```

3. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```

4. **In Another Terminal, Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 🧪 Testing the Pipeline

Test the 3-agent pipeline with a sample query:

```bash
python -c "
import asyncio
from agents.graph import sahayak_graph

async def test():
    state = {
        'raw_query': 'There is a fire in Mumbai',
        'messages': [],
    }
    result = await sahayak_graph.ainvoke(state)
    print('Triage:', result.get('triage'))
    print('Instructions:', result.get('safety_output').instructions if result.get('safety_output') else None)

asyncio.run(test())
"
```

## 🛠️ Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check Ollama host in `.env`: `OLLAMA_HOST=http://localhost:11434`
- Test connection: `curl http://localhost:11434/api/tags`

### ChromaDB Issues
- Delete and recreate: `rm -rf data/chroma_db`
- ChromaDB will reinitialize on next run

### Missing Models
- Ensure Ollama models are pulled: `ollama list`
- Pull if needed: `ollama pull llama3:8b-q4`

### Frontend Port Already in Use
- Change port in frontend: `npm run dev -- --port 3001`

### Backend Port Already in Use
- Change port in `.env`: `API_PORT=8001`
- Then run: `uvicorn main:app --reload --port 8001`

## 📊 Performance Tips

- **Low-end hardware**: Use `HARDWARE_PROFILE=low` with Gemma 2B model
- **Mid-range**: Use `HARDWARE_PROFILE=mid` with LLaMA 3 8B
- **High-end**: Use `HARDWARE_PROFILE=high` with LLaMA 3 8B full precision

## 📝 Development Commands

```bash
# Run linting
make lint

# Run tests
make test

# Run evaluation benchmark
make eval

# Clean up containers and files
make clean

# Ingest NDMA documents
make ingest
```

## 🤝 Contributing

The project uses:
- **Backend**: Python 3.11+, FastAPI, LangGraph
- **Frontend**: Next.js, React, TypeScript
- **LLM**: Ollama (local, offline)
- **Vector DB**: ChromaDB
- **Geospatial**: OSRM, DuckDB

## 📄 License

MIT License - See LICENSE file for details

## 🎯 Key Features

✅ **100% Offline** - No external API calls at runtime
✅ **3-Agent Pipeline** - Specialized agents for triage, retrieval, safety
✅ **Voice Support** - Speech-to-text transcription
✅ **Geospatial** - Route finding to nearby shelters/hospitals
✅ **Safety Guardrails** - Redline rules + self-reflection checks
✅ **Hardware Flexible** - Configurable for low/mid/high-end systems

---

**Support & Questions**: Check README.md or open an issue on GitHub

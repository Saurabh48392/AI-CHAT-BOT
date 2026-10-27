# Multimodal AI Chatbot

A modular, beginner-friendly **Multimodal AI Chatbot MVP** built with **FastAPI**, **PostgreSQL (+ pgvector)**, and **Streamlit**. 

This chatbot allows users to interact through multiple modalities (text, images, documents, audio), retrieve information from uploaded documents via **Retrieval-Augmented Generation (RAG)**, perform automated **real-time web searches**, create and update study documents with version tracking, and receive compassionate, non-clinical **personal emotional assistance**.

---

## Features

- [x] **Text Chat**: Interactive conversational interface with persistent history and context memory.
- [x] **Image Input**: Multimodal vision analysis supporting JPEG, PNG, and WEBP formats.
- [x] **Document Input**: Ingests PDF, DOCX, TXT, and Markdown files with automatic text extraction.
- [x] **Audio Input**: Ingests audio files (WAV, MP3, M4A) with multimodal playback and processing.
- [x] **RAG (Retrieval-Augmented Generation)**: Chunks, embeds, and indexes document text with vector similarity search.
- [x] **Web Search**: Intelligent intent detection that triggers DuckDuckGo or Tavily searches for current/real-time information.
- [x] **Combined RAG + Web Search**: Synthesizes uploaded document insights with live web search results.
- [x] **Document Creation**: Generates structured notes and study guides with instant multi-format downloads (Markdown, TXT, DOCX, PDF).
- [x] **Document Updating & Versioning**: Modifies existing documents (e.g., rewriting in simpler terms or adding sections) while maintaining version history (`v1` → `v2` → `latest`).
- [x] **Conversation Memory**: Persists messages and conversations in database tables with session switching.
- [x] **Personal Emotional Assistance**: Empathetic, supportive responses with clear non-clinical boundaries and crisis safety resources.

---

## Architecture Overview

```mermaid
graph TD
    subgraph Frontend [Streamlit UI - Port 8501]
        UI_Chat[Chat Interface & History]
        UI_Sidebar[Conversation & Document Manager]
        UI_Media[Media Attachment Drawer: Image/Audio]
        UI_Download[Document Exporter: MD/TXT/DOCX/PDF]
    end

    subgraph Backend [FastAPI Backend - Port 8000]
        API[REST API Endpoints]
        Orchestrator[AI Orchestration Service]

        subgraph CoreServices [Modular Services]
            MultiProc[Multimodal Input Processor]
            RAG[RAG Retrieval & Chunker Engine]
            WebSearch[Web Search Classifier & Engine]
            DocManager[Document Versioning & Generator]
            EmotionalAssist[Emotional Support & Safety Guards]
        end

        subgraph Abstractions [Provider Abstractions]
            LLMProvider[LLM: Gemini / OpenAI / Mock]
            EmbedProvider[Embeddings: Gemini / OpenAI / Simple]
            SearchProvider[Search: DuckDuckGo / Tavily / Mock]
        end
    end

    subgraph DataStore [Data & Storage]
        Postgres[(PostgreSQL + pgvector / SQLite Dev Fallback)]
        UploadsDir[data/uploads/]
        GeneratedDir[data/generated/]
    end

    UI_Chat <-->|HTTP REST| API
    UI_Sidebar <-->|HTTP REST| API
    UI_Media -->|Base64 / Multipart| API
    UI_Download <--|File Download| API

    API --> Orchestrator
    Orchestrator --> MultiProc
    Orchestrator --> RAG
    Orchestrator --> WebSearch
    Orchestrator --> DocManager
    Orchestrator --> EmotionalAssist

    RAG --> EmbedProvider
    RAG --> Postgres
    WebSearch --> SearchProvider
    Orchestrator --> LLMProvider

    DocManager --> UploadsDir
    DocManager --> GeneratedDir
    API --> Postgres
```

---

## Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** | High-performance Python async REST API framework |
| **Data Validation** | **Pydantic v2** | Strong typing, input sanitization, and request/response schemas |
| **Server** | **Uvicorn** | Lightning-fast ASGI web server implementation |
| **Database** | **PostgreSQL + pgvector** | Relational storage for conversations, messages, document metadata, and vector embeddings (with automatic SQLite fallback for local offline testing) |
| **Frontend** | **Streamlit** | Interactive Python web frontend communicating with FastAPI |
| **Document Processing**| **PyMuPDF, python-docx, ReportLab** | Fast parsing for PDFs/DOCX and export generation for Markdown, TXT, DOCX, and PDF |
| **Search Engine** | **DuckDuckGo Search (`ddgs`)** | Zero-API-key live web search with fallback support |
| **AI Providers** | **Google Gemini / OpenAI / Mock** | Swappable provider abstraction layer configured via environment variables |

---

## Project Structure

```text
multimodal-ai-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point, CORS & logging middleware
│   │   │
│   │   ├── api/                        # REST API Route Handlers
│   │   │   ├── health.py               # GET /health
│   │   │   ├── chat.py                 # POST /api/chat
│   │   │   ├── conversations.py        # CRUD /api/conversations
│   │   │   ├── documents.py            # Upload, list, update & download /api/documents
│   │   │   └── search.py               # POST /api/search & POST /api/rag/search
│   │   │
│   │   ├── core/                       # Core configuration and database setup
│   │   │   ├── config.py               # Pydantic Settings (.env loader)
│   │   │   ├── database.py             # Database engine, pgvector support & dev fallback
│   │   │   └── logging.py              # Structured, sanitized logging
│   │   │
│   │   ├── models/                     # SQLAlchemy ORM Models
│   │   │   ├── conversation.py         # Conversation entity
│   │   │   ├── message.py              # Message entity
│   │   │   └── document.py             # Document & DocumentChunk (with Vector embeddings)
│   │   │
│   │   ├── schemas/                    # Pydantic Schemas
│   │   │   ├── chat.py                 # ChatRequest, ChatResponse, Citations
│   │   │   ├── conversation.py         # Conversation and Message schemas
│   │   │   ├── document.py             # Document and DocumentChunk schemas
│   │   │   └── search.py               # Web and RAG search schemas
│   │   │
│   │   └── services/                   # Modular Business Logic Layer
│   │       ├── orchestrator.py         # Central AI workflow orchestrator
│   │       ├── ai/                     # LLM Provider Abstraction (Gemini, OpenAI, Mock)
│   │       ├── rag/                    # Chunker, Embedding Provider & Vector Retriever
│   │       ├── documents/              # File Parsers (PDF/DOCX/TXT) & Generators (MD/PDF)
│   │       ├── web_search/             # Intent Classifier & Search Providers
│   │       ├── multimodal/             # Media Processor (Images, Audio, Docs)
│   │       └── emotional_support/      # Non-clinical emotional support & crisis safety
│   │
│   ├── requirements.txt                # Backend dependencies
│   └── .env.example                    # Template environment variables
│
├── frontend/
│   ├── app.py                          # Streamlit application entry point
│   ├── components/                     # Reusable UI components
│   │   ├── chat_view.py                # Chronological chat history with citation expanders
│   │   ├── sidebar.py                  # Conversations, document library & status
│   │   └── file_preview.py             # Download cards for generated documents
│   └── utils/
│       └── api_client.py               # HTTP client communicating with FastAPI
│
├── data/
│   ├── uploads/                        # Uploaded documents
│   └── generated/                      # Created and updated export artifacts
│
├── tests/                              # Comprehensive Pytest Suite
│   ├── test_health.py                  # Health check & root endpoints
│   ├── test_documents.py               # Parsing, chunking & document export
│   ├── test_rag.py                     # Embeddings & similarity search
│   ├── test_chat.py                    # Chat endpoint, memory & multimodal flow
│   └── test_emotional.py               # Emotional classifier & crisis safety rules
│
├── docker-compose.yml                  # PostgreSQL with pgvector container definition
├── README.md                           # Documentation & user guide
└── .gitignore                          # Git ignore rules
```

---

## Installation & Setup

### 1. Clone Repository & Setup Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd multimodal-ai-chatbot

# Create virtual environment (Python 3.11+)
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

---

## PostgreSQL & pgvector Setup

### Option A: Using Docker Compose (Recommended)

To start PostgreSQL with the `pgvector` extension pre-installed:

```bash
docker compose up -d
```

This launches PostgreSQL on `localhost:5432` with user `postgres` and password `postgres`.

### Option B: Local PostgreSQL Installation

If you already have PostgreSQL installed locally:
1. Open `psql` or pgAdmin:
   ```sql
   CREATE DATABASE multimodal_chatbot;
   \c multimodal_chatbot;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. Update `DATABASE_URL` in `backend/.env`.

> **Note**: If PostgreSQL is not currently running, the application automatically uses an embedded SQLite database (`data/dev_storage.db`) with vector similarity calculation so you can test and explore immediately without database setup.

---

## Environment Variables Configuration

Copy the `.env.example` file to `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your settings:

```env
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
BACKEND_URL=http://localhost:8000

# PostgreSQL + pgvector
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/multimodal_chatbot
ALLOW_SQLITE_FALLBACK=true

# AI Provider: "gemini" | "openai" | "mock"
LLM_PROVIDER=mock
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-1.5-flash

# Embedding Provider: "gemini" | "openai" | "simple"
EMBEDDING_PROVIDER=simple
VECTOR_DIMENSION=768

# Web Search Provider: "duckduckgo" | "tavily" | "mock"
WEB_SEARCH_PROVIDER=duckduckgo
TAVILY_API_KEY=

# Storage settings
UPLOAD_DIR=data/uploads
GENERATED_DIR=data/generated
MAX_UPLOAD_SIZE_MB=25
```

---

## Running the Application

### Step 1: Start the FastAPI Backend

Open a terminal and run:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

The backend starts at `http://localhost:8000`.
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc API Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Status: [http://localhost:8000/health](http://localhost:8000/health)

### Step 2: Start the Streamlit Frontend

Open a second terminal and run:

```bash
streamlit run frontend/app.py
```

The Streamlit UI opens automatically in your browser at `http://localhost:8501`.

---

## How It Works

### 1. Multimodal Chat Pipeline
Users can type text, attach images (for visual analysis), attach audio (for audio processing), and attach documents simultaneously. The input processor normalizes these into a `NormalizedMultimodalInput` passed to the AI layer.

### 2. RAG (Retrieval-Augmented Generation) Pipeline
```text
Upload Document (PDF/DOCX/TXT/MD)
          ↓
Text Extraction (PyMuPDF / python-docx)
          ↓
Chunking (600 chars with 100 char overlap)
          ↓
Vector Embedding Generation (768-dim)
          ↓
Store in PostgreSQL / pgvector
          ↓
User Query → Embed Query → Cosine Similarity Search
          ↓
Top-K Chunks injected into Context Builder
          ↓
Grounded LLM Answer with Source Citations
```

### 3. Web Search Pipeline
When a user asks questions requiring real-time facts (e.g., *"What are the latest developments in AI?"*, *"Current weather in Delhi"*, *"Latest documentation"*), the intent classifier triggers a search via DuckDuckGo. Search results are formatted and cited with clickable links.

### 4. Document Creation & Versioning
- **Creation**: Asking *"Create study notes about DBMS normalization"* generates structured content and produces a downloadable document (Markdown, TXT, DOCX, or PDF).
- **Updating**: Uploading a document and asking *"Rewrite this in simpler language"* creates an updated version (`v1` → `v2`) while preserving the original.

### 5. Emotional Assistance & Safety Guardrails
- **Empathetic Support**: Provides warm, reflective prompts, journaling ideas, and stress-management tips.
- **Safety Boundaries**: Explicitly states it is not a doctor or therapist, never diagnoses mental health conditions, and provides official 24/7 crisis resources (e.g. 988 Lifeline, Tele-MANAS) if self-harm triggers are detected.

---

## Running Automated Tests

Run the full pytest suite with:

```bash
python -m pytest tests/ -v
```

All 14 test cases verify:
- Backend `/health` and root routes
- Document uploading, parsing (PDF/DOCX/TXT), and multi-format exports
- Text chunking and embedding generation
- RAG similarity search and retrieval scoring
- Conversational chat and memory persistence
- Multimodal input handling
- Document generation and versioning
- Emotional support intent classification and crisis safety boundaries

---

## Future Improvements

- User authentication (JWT / OAuth2)
- Multi-user isolation and role-based permissions
- Streaming responses (Server-Sent Events / WebSockets)
- Voice conversation with real-time speech-to-text (STT) and text-to-speech (TTS)
- Agentic tool use (code execution sandbox, calculator)
- Cloud storage integration (AWS S3 / Google Cloud Storage)
- Enterprise observability with OpenTelemetry and Prometheus

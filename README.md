# 🤖 Agentic RAG MCP Agent

An intelligent retrieval-augmented generation (RAG) system powered by **LangChain**, **FastAPI**, and **Model Context Protocol (MCP)**, with multimodal support for text, images, web content, and document processing.

## ✨ Features

- **🔍 Multi-Vector Retrieval**: Semantic search using child documents and parent documents for rich context
- **📸 Multimodal Intelligence**: Vision-based image analysis and summarization
- **🌐 Web Integration**: Real-time web scraping and search capabilities
- **📚 Universal Document Loading**: Support for PDF, DOCX, PPTX, CSV, audio transcription, and more
- **🧠 LLM Orchestration**: OpenRouter integration with configurable LLM models
- **⚡ Streaming API**: Real-time response streaming with Server-Sent Events (SSE)
- **🔌 MCP Tools**: Standardized tools for retrieval, web search, datetime, and calculations
- **💾 Vector Database**: Pinecone integration for scalable embedding storage
- **🎨 Full-Stack**: TypeScript/React frontend with Python FastAPI backend

---

## 🏗️ Architecture

### Backend Stack

- **FastAPI**: High-performance async web framework
- **LangChain**: LLM orchestration and RAG pipeline
- **Pinecone**: Vector database for semantic search
- **Cohere**: Embeddings generation (production)
- **MCP (Model Context Protocol)**: Standardized tool integration
- **DuckDuckGo**: Web search fallback
- **Numexpr**: Safe mathematical expression evaluation

### Frontend Stack

- **React 18**: UI framework
- **TypeScript**: Type-safe development
- **Vite**: Lightning-fast build tool
- **TailwindCSS**: Utility-first styling

---

## 📂 Project Structure

```
Agentic-RAG-MCP-Agent/
├── api/                          # FastAPI backend
│   ├── __init__.py
│   └── agent.py                  # Main API endpoints
├── mcp_server/                   # MCP server & tools
│   ├── mcp_server.py            # FastMCP server
│   ├── mcp_tools.py             # Tool implementations
│   └── mcp_utils.py             # Utility functions
├── embedding_model/              # Embedding pipeline
│   ├── embedding_model.py       # Cohere embeddings config
│   └── multi_vector_embedding.py # Document embedding
├── retrieving_pipeline/          # RAG retrieval logic
│   ├── multi_vector_retrieval.py # Multi-vector search
│   └── retrieving_pipeline.py   # Retrieval orchestration
├── tools/                        # Custom tools
│   ├── img_tool.py              # Vision model integration
│   └── vision_model.py          # Vision model config
├── utils/                        # Utility modules
│   ├── utils.py                 # Common utilities
│   ├── any_doc_loader.py        # Universal document loader
│   └── audio_loader.py          # Audio transcription
├── agentic-rag-frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── types/
│   └── package.json
├── Agent.py                      # LLM configuration (OpenRouter)
├── services.yml                  # Deployment configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+ (for frontend)
- Pinecone API key
- Cohere API key
- OpenAI/OpenRouter API key

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd Agentic-RAG-MCP-Agent
```

#### 2. Setup Backend

Create `.env` file:

```env
# LLM Configuration
OPENAI_API_KEY=your_openrouter_api_key
COHERE_API_KEY=your_cohere_api_key

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name

# MCP Security
MCP_API_KEY=your_secure_mcp_key

# Server Configuration
PORT=8000
```

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Setup Frontend

```bash
cd agentic-rag-frontend
npm install
npm run dev
```

---

## 📖 Usage

### Running the Application

**Terminal 1 - MCP Server** (port 3001):

```bash
python -m mcp_server.mcp_server
```

**Terminal 2 - FastAPI Backend** (port 8000):

```bash
python api/agent.py
```

**Terminal 3 - React Frontend** (port 3000):

```bash
cd agentic-rag-frontend
npm run dev
```

### API Endpoints

#### Chat Streaming

```bash
curl "http://localhost:8000/api/agent/stream?message=What%20is%20RAG?"
```

#### Upload Document

```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/agent/upload
```

#### Embed URL

```bash
curl -X POST -F "url=https://example.com" http://localhost:8000/api/agent/embed-url
```

#### Upload Image

```bash
curl -X POST -F "file=@image.png" http://localhost:8000/api/agent/upload-image
```

#### Get Chat History

```bash
curl http://localhost:8000/api/agent/chat-history
```

#### Clear Chat History

```bash
curl -X DELETE http://localhost:8000/api/agent/chat-history
```

---

## 🔧 MCP Tools

The system provides the following tools via MCP:

| Tool                   | Description                          | Parameters           |
| ---------------------- | ------------------------------------ | -------------------- |
| `retriever`            | Multi-vector semantic search         | `queries: List[str]` |
| `query_transformer`    | Rewrite queries for better retrieval | `query: str`         |
| `web_search`           | DuckDuckGo web search                | `query: str`         |
| `calculate`            | Safe math expression evaluator       | `expression: str`    |
| `get_current_datetime` | Current date/time in timezone        | `timezone: str`      |

---

## 📊 RAG Pipeline

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. Query Transformation             │
│    - Rewrite for better semantics   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Multi-Vector Retrieval           │
│    - Search child documents (k=6)   │
│    - Search image summaries (k=2)   │
│    - Fetch parent documents (k=3)   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Context Enrichment               │
│    - Web search (if needed)         │
│    - Tool execution (math, datetime)│
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. LLM Generation                   │
│    - OpenRouter/OpenAI              │
│    - Streaming response             │
└─────────────────────────────────────┘
    ↓
Response to User
```

---

## 🎯 Key Workflows

### Document Ingestion

1. Upload PDF/DOCX/PPTX/URL
2. Extract text with WebBaseLoader
3. Extract images and generate summaries
4. Split documents into child chunks
5. Generate embeddings with Cohere
6. Store in Pinecone with metadata

### Query Processing

1. Detect query intent (greeting, math, web search needed)
2. Transform query for semantic search
3. Retrieve child docs from vector DB
4. Resolve parent document IDs
5. Fetch full parent documents
6. Combine with web search results
7. Pass context to LLM with chat history
8. Stream response to user

---

## 🔐 Security

- **API Key Validation**: MCP server validates `x-api-key` header
- **CORS Configuration**: Restricted to frontend domains
- **Safe Math Evaluation**: Uses `numexpr` instead of `eval()`
- **Environment Variables**: All secrets in `.env` (never committed)
- **SSE Security**: Streaming responses with proper headers

---

## 📦 Dependencies

### Core

- `langchain>=0.3.0` - LLM orchestration
- `langchain-openai>=0.1.0` - OpenAI/OpenRouter integration
- `langchain-cohere>=0.3.0` - Cohere embeddings
- `langgraph>=0.2.0` - Graph-based agents

### Vector & Search

- `langchain-pinecone>=0.2.0` - Pinecone integration
- `pinecone-client>=4.0.0` - Pinecone API
- `duckduckgo-search` - Web search

### Document Processing

- `pypdf>=4.0.0` - PDF parsing
- `docx2txt>=0.8` - DOCX parsing
- `python-pptx>=0.6.0` - PPTX parsing
- `openai-whisper>=20231117` - Audio transcription
- `unstructured>=0.10.0` - Universal document parsing

### Web & Async

- `fastapi>=0.110.0` - Web framework
- `uvicorn>=0.29.0` - ASGI server
- `httpx>=0.27.0` - Async HTTP client
- `aiohttp>=3.9.0` - Async HTTP

### Utilities

- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment management
- `numexpr>=2.8.0` - Safe math expressions
- `pytz>=2024.1` - Timezone handling

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Submit a pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Troubleshooting

### Issue: "PINECONE_API_KEY not set"

**Solution**: Ensure `.env` file exists with valid Pinecone credentials

### Issue: "MCP connection refused"

**Solution**: Start MCP server first: `python -m mcp_server.mcp_server`

### Issue: "Vision model timeout"

**Solution**: Check internet connection and image URL accessibility

### Issue: "Embedding failed"

**Solution**: Verify Cohere API key and rate limits

---

## 📞 Support

For issues and feature requests, please open a GitHub issue.

---

**Built with ❤️ for intelligent document processing and retrieval**

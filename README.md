# Multi-File Format Embeddings Generator

A FastAPI-based application that processes multiple document formats, generates embeddings using Ollama, stores them in PostgreSQL with pgvector, and provides a chat interface powered by LlamaIndex for querying documents.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Supported File Formats](#supported-file-formats)
- [System Prompts](#system-prompts)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Overview

This project provides a complete RAG (Retrieval-Augmented Generation) system that:
1. Accepts document uploads in 50+ formats
2. Extracts and processes text content
3. Generates embeddings using local Ollama models
4. Stores embeddings in PostgreSQL with pgvector extension
5. Enables semantic search and conversational chat with documents
6. Supports multiple specialized system prompts for different use cases

---

## Features

- **Multi-Format Support**: Process PDF, DOCX, EPUB, Markdown, HTML, and 50+ other formats
- **Local LLM Processing**: Uses Ollama for embeddings and chat (no external API calls)
- **Vector Storage**: PostgreSQL with pgvector for efficient similarity search
- **Intelligent Chunking**: Automatic document splitting with page-aware processing
- **Streaming Chat**: Real-time conversational interface with document context
- **Specialized Prompts**: 10 pre-configured system prompts (technical, legal, medical, tutor, etc.)
- **Source Citations**: Automatic page number references in responses
- **RESTful API**: Easy integration with any client application

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼──────────────────────────────────────┐
│          FastAPI Application                 │
│  ┌────────────────────────────────────────┐ │
│  │      Document Processing Layer         │ │
│  │  • PDF Extractor (PyMuPDF)            │ │
│  │  • Pandoc Extractor (50+ formats)     │ │
│  └─────────────┬──────────────────────────┘ │
│                │                              │
│  ┌─────────────▼──────────────────────────┐ │
│  │       LlamaIndex Integration           │ │
│  │  • Document Chunking                   │ │
│  │  • Embedding Generation                │ │
│  │  • Query Engine                        │ │
│  │  • Chat Engine                         │ │
│  └─────────────┬──────────────────────────┘ │
└────────────────┼────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼─────┐    │    ┌──────▼──────┐
│  Ollama  │    │    │ PostgreSQL  │
│          │    │    │   +pgvector │
│ Embedder │◄───┼───►│             │
│  + LLM   │    │    │ Vector Store│
└──────────┘    │    └─────────────┘
                │
         Persistent Storage
```

---

## Prerequisites

Before starting, ensure you have the following installed:

### 1. **Python 3.9+**
```bash
python --version
```

### 2. **PostgreSQL 15+**
- Download from: https://www.postgresql.org/download/

### 3. **Ollama**
- Download from: https://ollama.com/download
- Required models:
  ```bash
  ollama pull nomic-embed-text
  ollama pull gemma3:1b
  ```

### 4. **Pandoc** (for document conversion)
- Download from: https://pandoc.org/installing.html
- Or via package manager:
  ```bash
  # Windows (using Chocolatey)
  choco install pandoc
  
  # macOS
  brew install pandoc
  
  # Linux
  sudo apt-get install pandoc
  ```

---

## Installation

### Step 1: Clone or Download the Project

```bash
cd c:\Users\erima\Desktop\multi-file-format-embeddings-generator
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- LlamaIndex (document processing and RAG)
- PostgreSQL drivers (asyncpg, psycopg2)
- PyMuPDF (PDF processing)
- Other required libraries

---

## Configuration

### Step 1: Create Environment File

Create a `.env` file in the project root:

```bash
# Copy from template
cp .env.example .env  # or create manually
```

### Step 2: Configure Environment Variables

Edit `.env` with your settings:

```env
# Ollama Configuration
EMBEDDING_MODEL=nomic-embed-text
LLM_URL_EMBEDDING=http://localhost:11434/api/embeddings
LLM_URL=http://localhost:11434
CHAT_MODEL=gemma3:1b

# PostgreSQL Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=embeddings
PGUSER=your_username
PGPASSWORD=your_password
```

**Configuration Details:**

- `EMBEDDING_MODEL`: Ollama model for generating embeddings (nomic-embed-text produces 768-dim vectors)
- `LLM_URL`: Base URL for Ollama API
- `CHAT_MODEL`: Ollama model for chat responses (lightweight models like gemma3:1b recommended)
- `PGDATABASE`: PostgreSQL database name
- `PGUSER`/`PGPASSWORD`: PostgreSQL credentials

---

## Database Setup

### Step 1: Install pgvector Extension

Connect to PostgreSQL:

```bash
# Windows
psql -U postgres

# Or connect to specific database
psql -U your_username -d postgres
```

Create database and enable pgvector:

```sql
-- Create database
CREATE DATABASE embeddings;

-- Connect to the database
\c embeddings

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Verify Database Connection

Test connection from Python:

```bash
python -c "import psycopg2; conn = psycopg2.connect(database='embeddings', user='your_username', password='your_password', host='localhost', port=5432); print('Connected successfully'); conn.close()"
```

### Step 3: Table Creation (Automatic)

The application automatically creates the `llamaindex_embeddings` table on first run with:
- `id`: Primary key
- `text`: Document content
- `metadata`: JSON metadata (filename, page numbers, etc.)
- `embedding`: Vector column (768 dimensions)

---

## Running the Application

### Step 1: Start Ollama Service

Ensure Ollama is running:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

### Step 2: Verify Models are Downloaded

```bash
ollama list
# Should show: nomic-embed-text and gemma3:1b
```

### Step 3: Start FastAPI Server

```bash
# Development mode (with auto-reload)
python app.py

# Or with uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Verify Server is Running

Open browser to: http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "vector_store": "PGVectorStore",
  "embedding_model": "nomic-embed-text"
}
```

### Step 5: Access API Documentation

Interactive API docs: http://localhost:8000/docs

---

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "vector_store": "PGVectorStore",
  "embedding_model": "nomic-embed-text"
}
```

---

### 2. Upload Document

**POST** `/upload`

Upload and process a document for embedding.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@Resume.pdf"
```

**Process Flow:**
1. File saved to `uploads/` directory
2. Content extracted based on file type:
   - PDF → PyMuPDF extractor
   - Other formats → Pandoc extractor
3. Content split into pages (by `\f` or estimated chunks)
4. Each page converted to LlamaIndex Document with metadata
5. Documents embedded and stored in PostgreSQL
6. Metadata includes: filename, page number, content type, file size

**Response:**
```json
{
  "message": "Document embedded successfully",
  "filename": "Resume.pdf",
  "content_length": 15234,
  "embedding_model": "nomic-embed-text",
  "note": "LlamaIndex automatically chunked and embedded the document"
}
```

**Limitations:**
- Max content length: 50,000 characters (prevents Ollama crashes)
- Chunk size: 128 characters with 10 character overlap
- Batch size: 1 (processes one embedding at a time for stability)

---

### 3. Query Documents

**GET** `/query?query=your_question&top_k=5`

Perform semantic search on uploaded documents.

**Request:**
```bash
curl "http://localhost:8000/query?query=What%20are%20the%20key%20skills&top_k=5"
```

**Response:**
```json
{
  "query": "What are the key skills",
  "response": "Based on the documents, the key skills include...",
  "sources": [
    {
      "text": "Skills: Python, JavaScript, Machine Learning...",
      "score": 0.85,
      "filename": "Resume.pdf",
      "page_number": 2,
      "content_type": "application/pdf",
      "metadata": {
        "filename": "Resume.pdf",
        "page_number": 2,
        "total_pages": 5
      }
    }
  ]
}
```

**Parameters:**
- `query` (required): Search query string
- `top_k` (optional, default=5): Number of top results to return

---

### 4. Chat with Documents

**POST** `/chat`

Conversational interface with streaming responses.

**Request Body:**
```json
{
  "message": "What are the main qualifications?",
  "chat_history": [
    {"role": "user", "content": "Tell me about the resume"},
    {"role": "assistant", "content": "This resume shows..."}
  ],
  "system_prompt": "technical"
}
```

**Request Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main qualifications?",
    "system_prompt": "default"
  }'
```

**Response:** Streaming text response with source references

```
The main qualifications include...
- Bachelor's degree in Computer Science
- 5 years of Python development experience
- Machine learning expertise

---
**References:**
- Resume.pdf (Page[1], Page[2])
```

**Parameters:**
- `message` (required): User's question or message
- `chat_history` (optional): Previous conversation context
- `system_prompt` (optional): Prompt type or custom text (see [System Prompts](#system-prompts))

---

### 5. List Available Prompts

**GET** `/prompts`

Get all available system prompt types.

**Response:**
```json
{
  "available_prompts": [
    "default", "technical", "summarizer", "researcher",
    "tutor", "analyst", "legal", "creative", "qa", "medical"
  ],
  "prompts_info": {
    "default": "You are a helpful AI assistant with access to a document knowledge base.",
    "technical": "You are an expert technical assistant analyzing technical documentation.",
    "summarizer": "You are a document summarization assistant."
  },
  "note": "Use these prompt types in the 'system_prompt' field of /chat requests..."
}
```

---

### 6. Get Specific Prompt

**GET** `/prompts/{prompt_type}`

Get the full text of a specific system prompt.

**Request:**
```bash
curl "http://localhost:8000/prompts/technical"
```

**Response:**
```json
{
  "prompt_type": "technical",
  "prompt_text": "You are an expert technical assistant analyzing technical documentation.\n\nGuidelines:\n- Provide detailed technical explanations with precision..."
}
```

---

## Usage Examples

### Example 1: Upload and Query a Resume

```bash
# 1. Upload resume
curl -X POST "http://localhost:8000/upload" \
  -F "file=@Resume.pdf"

# 2. Query for skills
curl "http://localhost:8000/query?query=programming%20skills&top_k=3"

# 3. Chat about experience
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the work experience",
    "system_prompt": "summarizer"
  }'
```

### Example 2: Upload Multiple Documents

```bash
# Upload technical documentation
curl -X POST "http://localhost:8000/upload" -F "file=@API_Documentation.docx"
curl -X POST "http://localhost:8000/upload" -F "file=@User_Guide.epub"
curl -X POST "http://localhost:8000/upload" -F "file=@README.md"

# Query across all documents
curl "http://localhost:8000/query?query=API%20authentication&top_k=10"
```

### Example 3: Technical Document Analysis

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the architecture design",
    "system_prompt": "technical"
  }'
```

### Example 4: Educational Tutoring

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain machine learning concepts from the textbook?",
    "system_prompt": "tutor"
  }'
```

---

## Supported File Formats

### PDF Files
Extracted using PyMuPDF (faster and more accurate for PDFs)
- `.pdf`

### Pandoc-Supported Formats (50+ formats)

**Markdown variants:**
- `.md`, `.markdown`, `.mdown`, `.mkd`, `.mkdn`, `.mdwn`
- `.rmd`, `.commonmark`, `.cm`, `.mmark`, `.mmd`

**Markup languages:**
- `.rst`, `.rest` (reStructuredText)
- `.asciidoc`, `.adoc`, `.asc` (AsciiDoc)
- `.org` (Org-mode)
- `.creole`, `.textile`, `.muse`

**Web formats:**
- `.html`, `.htm`, `.xhtml`
- `.xml`, `.dbk`, `.docbook`
- `.jats`, `.tei`, `.opml`

**Office documents:**
- `.docx` (Microsoft Word)
- `.odt` (OpenDocument Text)
- `.epub` (E-books)
- `.pptx` (PowerPoint)
- `.rtf` (Rich Text Format)

**LaTeX:**
- `.tex`, `.ltx`, `.context`, `.ctx`

**Bibliography:**
- `.bib`, `.bibtex`, `.biblatex`
- `.ris`, `.endnote`, `.enl`
- `.mods`, `.nbib`

**Data:**
- `.csv`, `.txt`

---

## System Prompts

The application includes 10 specialized system prompts for different use cases:

### 1. **default**
General-purpose assistant for document queries
- Balanced tone
- Source citations
- Clear limitations

### 2. **technical**
Expert technical assistant for documentation
- Detailed explanations
- Technical terminology
- Step-by-step breakdowns

### 3. **summarizer**
Focused on creating concise summaries
- Bullet points
- Key highlights
- Objective tone

### 4. **researcher**
Deep research and cross-referencing
- Thorough analysis
- Multiple source synthesis
- Pattern identification

### 5. **tutor**
Educational and explanatory style
- Patient explanations
- Examples and analogies
- Interactive learning

### 6. **analyst**
Critical analysis and evaluation
- Objective assessment
- Pattern recognition
- Balanced perspectives

### 7. **legal**
Legal document information (not advice)
- Precise citations
- Legal terminology
- Disclaimer included

### 8. **creative**
Creative exploration of ideas
- Imaginative connections
- Brainstorming support
- Grounded in sources

### 9. **qa**
Direct question-answering
- Concise responses
- Precise citations
- Minimal elaboration

### 10. **medical**
Medical document information (not advice)
- Medical terminology
- Critical safety awareness
- Healthcare disclaimer

**Usage:**
```json
{
  "message": "Your question",
  "system_prompt": "technical"
}
```

Or provide custom prompt:
```json
{
  "message": "Your question",
  "system_prompt": "You are an expert in environmental science. Focus on sustainability aspects..."
}
```

---

## Troubleshooting

### Issue 1: Ollama Connection Failed

**Error:** `Ollama request failed` or `Connection refused`

**Solution:**
```bash
# 1. Check if Ollama is running
curl http://localhost:11434/api/tags

# 2. Start Ollama if not running
ollama serve

# 3. Verify models are installed
ollama list
ollama pull nomic-embed-text
ollama pull gemma3:1b
```

---

### Issue 2: PostgreSQL Connection Error

**Error:** `could not connect to server` or `authentication failed`

**Solution:**
```bash
# 1. Check PostgreSQL is running
# Windows: Check Services
# Linux: sudo systemctl status postgresql

# 2. Verify credentials in .env file
# 3. Test connection
psql -U your_username -d embeddings -h localhost

# 4. Check pgvector extension
psql -d embeddings -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

---

### Issue 3: Pandoc Not Found

**Error:** `Pandoc is not installed on the server`

**Solution:**
```bash
# Install Pandoc

# Windows (Chocolatey)
choco install pandoc

# Windows (Direct download)
# Visit: https://pandoc.org/installing.html

# Verify installation
pandoc --version
```

---

### Issue 4: Embedding Generation Crashes

**Error:** `Ollama embedding service may have crashed`

**Solution:**
The application is configured with stability measures:
- Batch size: 1 (processes one at a time)
- Chunk size: 128 (small chunks)
- Max content: 50KB (truncates large documents)

If still having issues:
```bash
# 1. Restart Ollama
ollama serve

# 2. Use a smaller embedding model
# Edit .env: EMBEDDING_MODEL=all-minilm

# 3. Reduce chunk size in app.py
# Settings.chunk_size = 64
```

---

### Issue 5: File Upload Fails

**Error:** `Unsupported file type`

**Solution:**
- Verify file extension is in supported formats list
- Check file is not corrupted
- For PDF: Ensure file is readable (not password-protected)
- Check file size (max 50KB content after extraction)

---

### Issue 6: Empty Query Results

**Error:** No results returned from `/query`

**Solution:**
```bash
# 1. Verify documents are uploaded
curl http://localhost:8000/query?query=test&top_k=1

# 2. Check database has embeddings
psql -d embeddings -c "SELECT COUNT(*) FROM llamaindex_embeddings;"

# 3. Try broader queries
# 4. Increase top_k parameter
```

---

## Project Structure

```
multi-file-format-embeddings-generator/
│
├── app.py                      # Main FastAPI application
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── README.md                   # This documentation
│
├── uploads/                    # Uploaded files storage
│   ├── Resume.epub
│   └── Resume.txt
│
├── sample/                     # Sample documents for testing
│   ├── Resume.epub
│   ├── Resume.md
│   └── Resume.txt
│
└── utils/                      # Utility modules
    ├── embed.py                # Embedding generation (legacy)
    ├── pandoc_supported.py     # Supported file formats list
    ├── prompts.py              # System prompts definitions
    │
    └── extractors/             # Document extractors
        ├── pandoc.py           # Pandoc-based extraction
        └── pdf.py              # PDF extraction with PyMuPDF
```

### Key Files Description:

**app.py**
- FastAPI application setup
- LlamaIndex initialization
- API endpoint definitions
- Upload, query, and chat handlers

**utils/embed.py**
- Direct Ollama embedding generation
- Legacy function (LlamaIndex handles embeddings in main app)

**utils/prompts.py**
- 10 pre-configured system prompts
- Prompt management functions

**utils/pandoc_supported.py**
- List of 50+ supported file formats
- Used to route extraction method

**utils/extractors/pandoc.py**
- Converts documents using Pandoc
- Handles markdown, docx, epub, etc.

**utils/extractors/pdf.py**
- Extracts PDF text using PyMuPDF
- Preserves page structure

---

## Advanced Configuration

### Tuning Chunk Size

Edit `app.py` initialization:

```python
Settings.chunk_size = 256  # Default: 128
Settings.chunk_overlap = 20  # Default: 10
```

Larger chunks:
- ✅ Better context preservation
- ❌ Slower embedding generation
- ❌ Higher memory usage

### Changing Embedding Model

Different models offer tradeoffs:

```bash
# High quality, larger (768 dims)
ollama pull nomic-embed-text

# Smaller, faster (384 dims)
ollama pull all-minilm

# Update .env
EMBEDDING_MODEL=all-minilm

# Update embed_dim in app.py
embed_dim=384
```

### Database Performance

For large document collections:

```sql
-- Create index on metadata
CREATE INDEX idx_metadata ON llamaindex_embeddings USING gin(metadata);

-- Create index on embeddings (HNSW for faster search)
CREATE INDEX ON llamaindex_embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## Development Tips

### Testing Locally

```bash
# Run tests with sample documents
python -c "
import requests
response = requests.post(
    'http://localhost:8000/upload',
    files={'file': open('sample/Resume.md', 'rb')}
)
print(response.json())
"
```

### Monitoring Logs

```bash
# Run with verbose logging
uvicorn app:app --log-level debug

# Monitor Ollama logs
ollama logs
```

### Hot Reload Development

```bash
# Auto-reload on code changes
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## Security Considerations

⚠️ **Production Deployment Warnings:**

1. **Authentication**: Add authentication to API endpoints
2. **File Validation**: Implement stricter file type checking
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Database Security**: Use SSL connections for PostgreSQL
5. **Environment Variables**: Never commit `.env` to version control
6. **CORS**: Configure appropriate CORS policies
7. **File Size Limits**: Set maximum upload size limits

---

## Performance Optimization

### For Large Document Collections:

1. **Batch Processing**: Process multiple documents in batches
2. **Async Operations**: Use async/await throughout
3. **Connection Pooling**: Configure PostgreSQL connection pooling
4. **Caching**: Implement query result caching
5. **Index Optimization**: Use appropriate PostgreSQL indexes

### For Faster Responses:

1. **Smaller Models**: Use lightweight chat models (gemma3:1b, phi3)
2. **Reduce top_k**: Lower similarity_top_k in queries
3. **Shorter Chunks**: Use smaller chunk_size
4. **Pre-warm**: Keep Ollama models loaded in memory

---

## Contributing

To extend this project:

1. **Add New Extractors**: Create new extractors in `utils/extractors/`
2. **Custom Prompts**: Add prompts to `utils/prompts.py`
3. **New Endpoints**: Extend `app.py` with additional routes
4. **Model Support**: Add support for different embedding models

---

## License

This project is provided as-is for educational and commercial use.

---

## Support and Resources

- **LlamaIndex Documentation**: https://docs.llamaindex.ai/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Ollama Documentation**: https://github.com/ollama/ollama
- **pgvector Documentation**: https://github.com/pgvector/pgvector
- **Pandoc Documentation**: https://pandoc.org/

---

## Changelog

**v1.0.0** (Current)
- Initial release
- Multi-format document support
- LlamaIndex integration
- Streaming chat interface
- 10 system prompts
- PostgreSQL vector storage

---

**Last Updated**: December 2025

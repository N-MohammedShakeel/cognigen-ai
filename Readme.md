# Cognigen AI Service

Cognigen AI Service is an intelligent AI-powered learning engine designed to generate personalized learning paths, adaptive educational content, curated learning resources, and mini assessments based on a learner’s profile, goals, and experience level.

Built using FastAPI, LangGraph, Ollama, and FAISS, the system dynamically generates structured learning experiences by combining LLM reasoning, vector retrieval, external resource enrichment, and workflow orchestration.

---

## My Contribution (Team Project)

This project was developed as a team project consisting of:

- Profile Management
- Learning Path Module
- Assessment Module
- Interview Module

### My Role

I was responsible for the **Profile Management** and **Learning Path module**, where I designed and implemented:

- Personalized learning path generation
- AI-generated topic content generation
- Profile-aware adaptive learning workflows
- Resource enrichment using vector search + web search + YouTube
- Mini quiz generation for submodules
- LangGraph workflow orchestration
- Production-safe JSON parsing for LLM outputs
- FastAPI AI endpoints for learning workflows

My implementation focused on building an adaptive learning system that generates personalized content based on user profile, goals, experience level, and preferred learning style.

---

## Problem Statement

Traditional online learning systems provide static learning material that does not adapt to a learner’s experience level, learning style, or goals.

Cognigen solves this problem by generating:

- Personalized learning paths
- Adaptive topic sequencing
- Dynamic learning content
- Context-aware educational resources
- AI-generated mini assessments

The system tailors learning experiences based on:

- Experience level
- Learning goals
- Preferred learning style
- Time availability
- Custom topics

---

## Features

### Personalized Learning Path Generation

- Profile-aware learning path creation
- Automatic topic generation
- Support for user-provided custom topics
- Difficulty-based topic prioritization
- Dynamic submodule generation
- Progress tracking support

### AI Content Generation

- Structured markdown content generation
- Profile-aware explanations
- Course-specific content
- Practical examples generation
- Python code examples generation
- Notebook-style content cells

### Multi-Source Resource Enrichment

Learning resources are collected from multiple sources:

- Local vector search (FAISS)
- Web resources using DuckDuckGo
- Educational YouTube videos
- Local curated datasets (`json`, `docx`)

### Mini Quiz Generation

- Automatic assessment generation
- Difficulty-balanced quizzes
- MCQ-based evaluation
- Quality validation for generated questions
- Adaptive assessment pipeline

### AI Workflow Orchestration

- LangGraph-based pipeline execution
- Stateful workflow management
- Multi-step generation flow
- Retry mechanisms for LLM failures
- Production-safe execution paths

### Production Stability Features

- Safe JSON parsing
- LLM output sanitization
- Retry mechanisms
- Failure fallback logic
- Graceful API failure handling
- Logging and monitoring support

---

## Architecture Overview

The system follows an AI orchestration workflow using LangGraph.

```txt
Student Profile
      │
      ▼
Learning Path Generation
      │
      ▼
Topic + Submodule Generation
      │
      ▼
Vector Search (FAISS)
      │
      ├── Local Learning Resources
      ├── DuckDuckGo Search
      └── YouTube Educational Videos
      │
      ▼
Content Generation (LLM)
      │
      ▼
Mini Quiz Generation
      │
      ▼
Personalized Learning Experience
```

---

## Learning Path Workflow (My Contribution)

The learning path system generates a structured roadmap based on:

- Course name
- Experience level
- Goal
- Preferred learning style
- Time availability
- Custom topics

### Workflow

```txt
Input
 → Student Profile Creation
 → Topic Generation
 → Topic Normalization
 → Difficulty Filtering
 → Submodule Generation
 → Learning Path Builder
 → Final Personalized Learning Path
```

### Key Capabilities

#### Profile-Aware Personalization

The system adapts generated topics depending on:

- Beginner
- Intermediate
- Advanced

Difficulty prioritization and estimated learning time are generated automatically.

#### Topic Generation

Supports:

1. Automatic topic generation using LLMs
2. User-defined custom topic learning paths

#### Submodule Generation

Each topic is enriched with:

- Title
- Summary
- Learning sequence order
- Metadata
- Completion tracking

---

## Content Generation Workflow (My Contribution)

The content generation engine creates structured educational material for each submodule.

### Workflow

```txt
Submodule
    │
    ▼
Vector Search
    │
    ├── FAISS
    ├── DuckDuckGo
    └── YouTube
    │
    ▼
LLM Content Generation
    │
    ▼
Markdown + Resources
    │
    ▼
Notebook Style Learning Content
```

### Generated Content Includes

- Markdown explanations
- Learning resources
- Code examples
- Practical explanations
- Resource links
- Structured notebook cells

### Resource Resolution Strategy

Resources are intelligently collected from:

#### Local Vector Database

Curated educational content from FAISS index.

#### DuckDuckGo Search

Searches educational content dynamically.

Examples:

- Tutorials
- Official documentation
- Educational references

#### YouTube Learning Resources

Relevant learning videos are fetched dynamically using the YouTube Data API.

---

## Mini Quiz Generation (My Contribution)

The assessment pipeline automatically generates mini quizzes from learning content.

### Workflow

```txt
Generated Content
      │
      ▼
Text Extraction
      │
      ▼
LLM Quiz Generation
      │
      ▼
Question Quality Validation
      │
      ▼
Final Mini Quiz
```

### Quiz Features

- Exactly 5 questions
- Difficulty balancing
  - 2 Easy
  - 2 Medium
  - 1 Hard
- MCQ format
- Validated answers
- Auto-cleaned formatting

---

## Vector Search & Retrieval

The system uses FAISS for semantic retrieval of curated learning resources.

### Pipeline

```txt
JSON / DOCX Learning Resources
            │
            ▼
Embedding Generation
            │
            ▼
FAISS Index Creation
            │
            ▼
Semantic Similarity Search
            │
            ▼
Relevant Learning Resources
```

Supported data sources:

- JSON
- DOCX
- YouTube metadata
- Educational links

---

## AI Models Used

### Ollama Models

#### qwen2.5:3b

Used for:

- Topic content generation
- Mini quiz generation

#### gemma3:1b

Used for:

- Learning path generation
- Topic creation
- Structured roadmap generation

#### gemma2:2b

Used for:

- Search query planning

---

## Tech Stack

### Backend & AI

- Python
- FastAPI
- LangGraph
- Ollama
- FAISS
- Pydantic

### Data & Processing

- NumPy
- BeautifulSoup
- dotenv
- JSON
- DOCX Parsing

### Integrations

- DuckDuckGo Search
- YouTube Data API

---

## Project Structure

```txt
cognigen-ai-service/
├── main.py
├── schemas.py
├── graphs/
│   ├── learning_path.py
│   ├── content_gen.py
│   └── quiz_gen.py
├── utils/
│   ├── common.py
│   └── text_cleaner.py
├── planners/
│   └── query_planner.py
├── scrapers/
│   └── web_scraper.py
├── vector_stores/
│   ├── faiss_vector.py
│   ├── python.index
│   ├── python_metadata.json
│   └── ingestion/
│       ├── ingest.py
│       ├── youtube_fetcher.py
│       └── docx_parser.py
└── tests/
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Checks service availability.

---

### Generate Learning Path

```http
POST /api/generate-learning-path
```

Generates a personalized learning path using:

- Experience level
- Learning goals
- Learning style
- Time availability
- Custom topics

---

### Generate Topic Content

```http
POST /api/generate-topic-content
```

Generates structured educational content for a topic.

Includes:

- Markdown learning material
- Resource recommendations
- Notebook-style learning cells

---

### Generate Mini Quiz

```http
POST /api/generate-mini-quiz
```

Creates adaptive MCQ quizzes from generated learning content.

---

## Environment Variables

Create a `.env` file:

```env
YOUTUBE_API_KEY=your_api_key
```

---

## Run Locally

### Clone Repository

```bash
git clone <repository-url>
cd cognigen-ai-service
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run FastAPI Server

```bash
uvicorn main:app --reload
```

Server runs on:

```txt
http://localhost:8000
```

---

## Future Improvements

- Real embedding model integration
- Semantic memory for learners
- Personalized adaptive assessments
- Interview preparation generation
- Multi-language content generation
- Better educational ranking models
- Real-time learning analytics

---

## Skills Demonstrated

- AI Workflow Engineering
- LangGraph Orchestration
- FastAPI Development
- LLM Integration
- Retrieval-Augmented Generation (RAG)
- Vector Search (FAISS)
- Personalized Recommendation Systems
- Educational AI Systems
- Prompt Engineering
- Production-safe LLM Parsing
- API Design
- Workflow Automation
- AI Content Generation
- Backend System Design

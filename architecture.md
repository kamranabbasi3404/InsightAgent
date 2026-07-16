# architecture.md — InsightAgent System Architecture

## 1. High-Level Architecture

```
┌─────────────────┐         ┌──────────────────────────┐
│   Next.js UI     │ <-----> │   FastAPI Backend         │
│  (chat + upload) │  REST/  │   (LangGraph Orchestrator)│
└─────────────────┘  SSE     └──────────┬────────────────┘
                                          │
                     ┌────────────────────┼───────────────────────┐
                     │                    │                       │
             ┌───────▼───────┐   ┌────────▼────────┐    ┌────────▼────────┐
             │   ChromaDB     │   │   Groq API       │    │  Tavily Web     │
             │ (local vector  │   │ (LLM: routing,   │    │  Search API     │
             │   store)       │   │  grading, gen)   │    │  (free tier)    │
             └───────┬────────┘   └──────────────────┘    └─────────────────┘
                     │
             ┌───────▼────────┐
             │ sentence-       │
             │ transformers    │
             │ (local embed)   │
             └─────────────────┘
```

## 2. Component Breakdown

### 2.1 Frontend (Next.js)
- **Chat interface**: text input, streaming response display.
- **Upload panel**: drag-drop PDF upload, shows indexed document list.
- **Reasoning trace panel**: collapsible sidebar showing the agent's step-by-step decision trail (route chosen, sub-queries, retries, sources).
- **Citation rendering**: inline citation chips that expand to show source snippet.

### 2.2 Backend (FastAPI)
- `/upload` — accepts PDF, triggers ingestion pipeline.
- `/chat` — accepts user query, streams back agent execution (SSE or chunked response) including intermediate steps + final answer.
- `/documents` — lists currently indexed documents.
- Wraps the LangGraph agent as the core reasoning engine; FastAPI is purely the I/O layer.

### 2.3 Agent Orchestration (LangGraph)
This is the core of the system. Modeled as a directed graph with conditional edges (a state machine), not a linear chain.

**State object** (passed between nodes) contains at minimum:
```python
class AgentState(TypedDict):
    original_query: str
    sub_queries: list[str]
    route: str  # "local_only" | "web_only" | "hybrid" | "no_retrieval"
    local_results: list[dict]
    web_results: list[dict]
    retrieval_grade: str  # "sufficient" | "insufficient"
    retry_count: int
    conflicts: list[dict]
    final_answer: str
    citations: list[dict]
    trace: list[dict]  # human-readable log of every step for the UI
```

**Nodes:**
1. `router_node` — LLM call classifying query → sets `route`.
2. `decompose_node` — if query is compound, splits into `sub_queries`; otherwise `sub_queries = [original_query]`.
3. `local_retrieve_node` — for each sub-query needing local search, queries ChromaDB, returns top-k chunks with metadata (filename, page).
4. `web_retrieve_node` — for each sub-query needing web search, calls Tavily, returns snippets + URLs + dates.
5. `grade_node` — LLM judges whether retrieved content (local and/or web) is sufficient to answer; sets `retrieval_grade`.
6. `rewrite_query_node` — if grade is `insufficient` and `retry_count < MAX_RETRIES`, LLM rewrites the query (broader/narrower/different phrasing), increments `retry_count`, loops back to retrieval.
7. `conflict_check_node` — compares local vs. web findings for factual contradictions; populates `conflicts`.
8. `synthesize_node` — LLM generates final answer, weaving in all sub-query results, citing sources, explicitly noting any conflicts.
9. `format_citations_node` — post-processes the answer to ensure every claim maps to a citation object for the frontend to render.

**Conditional edges:**
- `router_node` → `no_retrieval` route skips straight to a direct-answer generation node (for greetings/meta questions).
- `grade_node` → loops back to `rewrite_query_node` → retrieval, OR proceeds to `conflict_check_node` if sufficient or retries exhausted.

### 2.4 Retrieval Layer

**Local (ChromaDB):**
- Documents chunked via recursive character/token splitter (chunk size ~500–800 tokens, overlap ~100).
- Each chunk embedded via `sentence-transformers` (`BAAI/bge-small-en-v1.5` recommended — good quality/speed tradeoff, fully local, no API cost).
- Metadata stored per chunk: `source_filename`, `page_number`, `chunk_id`.
- Chroma persisted to local disk (`./chroma_db`) so re-indexing isn't required every run.

**Web (Tavily):**
- Tavily is purpose-built for LLM/agentic RAG use cases and has a free tier (1000 searches/month) — this is why it's preferred over raw scraping.
- Each result includes: title, URL, published date (when available), content snippet.
- Snippets are treated as "retrieved chunks" and flow through the same grading/synthesis logic as local chunks — the agent should not treat web and local sources through fundamentally different code paths where avoidable.

### 2.5 LLM Layer (Groq)
- Model: `llama-3.3-70b-versatile` for routing, grading, synthesis (quality-sensitive steps).
- Fallback/cheap model: `llama-3.1-8b-instant` for lightweight steps (e.g., simple query rewriting) if rate limits become an issue.
- All LLM calls should use structured output (JSON mode) for routing/grading decisions to avoid brittle string parsing.

## 3. Data Flow (Single Hybrid Query Example)

1. User asks: "How has Pakistan's IT export growth trended, and what recent policy changes affect it?"
2. `router_node` → classifies as `hybrid` (historical trend = could be in an uploaded report; "recent policy changes" = needs live web).
3. `decompose_node` → splits into: (a) "Pakistan IT export growth trend [from uploaded reports]", (b) "recent Pakistan IT policy changes 2026 [web]".
4. `local_retrieve_node` handles (a) against ChromaDB.
5. `web_retrieve_node` handles (b) against Tavily.
6. `grade_node` checks both result sets. If (a) returns nothing relevant (e.g., no such report uploaded), grade = insufficient for that sub-query.
7. `rewrite_query_node` broadens sub-query (a) and retries local retrieval once. If still nothing, the agent proceeds and will honestly state "no local document covers this" in the final answer instead of fabricating.
8. `conflict_check_node` — e.g., if the uploaded report (2024 data) says one growth figure and a 2026 web article gives a different, updated figure, this is flagged as a conflict (not an error — it's expected and should be surfaced).
9. `synthesize_node` produces a final answer citing both sources and explicitly noting: "Note: the uploaded report (2024) states X; more recent web sources (July 2026) report Y, reflecting updated figures."
10. Frontend renders final answer + citation chips + full reasoning trace.

## 4. File/Folder Structure

```
insightagent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── routers/
│   │   │   ├── chat.py
│   │   │   ├── upload.py
│   │   │   └── documents.py
│   │   ├── agent/
│   │   │   ├── graph.py            # LangGraph definition (nodes + edges)
│   │   │   ├── state.py            # AgentState TypedDict
│   │   │   ├── nodes/
│   │   │   │   ├── router.py
│   │   │   │   ├── decompose.py
│   │   │   │   ├── retrieve_local.py
│   │   │   │   ├── retrieve_web.py
│   │   │   │   ├── grade.py
│   │   │   │   ├── rewrite.py
│   │   │   │   ├── conflict_check.py
│   │   │   │   └── synthesize.py
│   │   │   └── prompts/            # all prompt templates, versioned as .txt or .py
│   │   ├── ingestion/
│   │   │   ├── pdf_parser.py       # PyMuPDF-based extraction
│   │   │   ├── chunker.py
│   │   │   └── embedder.py
│   │   ├── vectorstore/
│   │   │   └── chroma_client.py
│   │   ├── services/
│   │   │   ├── groq_client.py
│   │   │   └── tavily_client.py
│   │   └── config.py               # env vars, model names, constants
│   ├── chroma_db/                  # persisted vector store (gitignored)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                        # Next.js app router
│   │   ├── page.tsx                # main chat UI
│   │   └── components/
│   │       ├── ChatWindow.tsx
│   │       ├── UploadPanel.tsx
│   │       ├── ReasoningTrace.tsx
│   │       └── CitationChip.tsx
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── rules.md
│   ├── phases.md
│   ├── design.md
│   └── memory.md
└── README.md
```

## 5. Key Technical Decisions & Rationale

| Decision | Rationale |
|---|---|
| LangGraph over plain LangChain chains | Need explicit conditional loops (retry) and branching (routing) — a graph/state-machine model fits this naturally; linear chains don't. |
| ChromaDB over Pinecone/Weaviate cloud | Fully local, zero cost, zero account setup — fits the "completely free" constraint. |
| sentence-transformers over OpenAI embeddings | Local inference, no API cost, no rate limits on embedding step. |
| Tavily over raw BeautifulSoup scraping | Purpose-built for agentic RAG, returns clean structured snippets, handles search ranking — scraping raw HTML would add significant unrelated complexity. |
| Groq over local LLM (Ollama) | Groq free tier gives fast, high-quality (70B-class) inference without requiring a powerful local GPU — keeps the project accessible on modest hardware while still free. |
| SSE/streaming for chat endpoint | Reasoning trace + long agent runs (multiple retries) benefit from showing progress rather than a long blank wait. |

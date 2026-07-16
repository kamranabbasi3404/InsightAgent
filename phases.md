# phases.md — Build Roadmap

Each phase must be fully working and testable before moving to the next. Do not start Phase N+1 work while Phase N has open issues, unless explicitly told to parallelize.

## Phase 0 — Project Setup
**Goal:** Skeleton repo that runs, does nothing meaningful yet.

- [ ] Initialize backend (`FastAPI` project, `requirements.txt`, folder structure per `architecture.md`).
- [ ] Initialize frontend (`Next.js` app router project, Tailwind configured).
- [ ] Set up `.env.example` for both backend (`GROQ_API_KEY`, `TAVILY_API_KEY`) and frontend.
- [ ] `/health` endpoint on backend returning 200.
- [ ] Frontend loads a blank chat page and can hit `/health` successfully.
- [ ] Git repo initialized, `.gitignore` in place, initial commit.

**Done when:** `uvicorn` runs backend, `npm run dev` runs frontend, frontend can ping backend health check.

## Phase 1 — Document Ingestion Pipeline
**Goal:** Upload a PDF → it's chunked, embedded, and stored in ChromaDB.

- [ ] `pdf_parser.py`: extract text per page using PyMuPDF.
- [ ] `chunker.py`: recursive chunking with configurable size/overlap, preserving page number metadata.
- [ ] `embedder.py`: load `sentence-transformers` model, embed chunks.
- [ ] `chroma_client.py`: initialize persistent ChromaDB collection, upsert chunks with metadata.
- [ ] `/upload` endpoint: accepts PDF file, runs full pipeline, returns success + chunk count.
- [ ] `/documents` endpoint: lists indexed documents with chunk counts.
- [ ] Frontend `UploadPanel.tsx`: drag-drop or file picker, shows upload progress, lists indexed docs.

**Done when:** Upload 2–3 real PDFs (e.g., a public report), confirm chunks appear in ChromaDB with correct metadata, confirm `/documents` reflects them.

## Phase 2 — Core LangGraph Agent (Local-Only First)
**Goal:** A working agentic loop against local documents only — prove the graph/state-machine pattern before adding web search complexity.

- [ ] Define `AgentState` TypedDict.
- [ ] Build `router_node` (initially can hardcode route to `local_only` for this phase, or implement full classification early — prefer implementing full classification now since it's needed in Phase 3 anyway).
- [ ] Build `local_retrieve_node`.
- [ ] Build `grade_node` (LLM judges relevance of retrieved chunks).
- [ ] Build `rewrite_query_node` + retry loop wiring (max 2 retries).
- [ ] Build `synthesize_node` with citation formatting for local sources.
- [ ] Wire the graph together in `graph.py` with conditional edges.
- [ ] `/chat` endpoint invokes the graph, returns final answer + trace.
- [ ] Basic frontend chat window (no streaming yet — just request/response) showing answer + citations.

**Done when:** Ask a question clearly answerable from an uploaded PDF, get a correctly cited answer. Ask a question NOT covered by any PDF, confirm the agent honestly says so after retries (not hallucinated).

## Phase 3 — Web Search Integration + Full Routing
**Goal:** Add the web search branch and real hybrid routing/decomposition.

- [ ] `tavily_client.py` service wrapper.
- [ ] `web_retrieve_node`.
- [ ] Extend `router_node` to properly classify `local_only` / `web_only` / `hybrid` / `no_retrieval`.
- [ ] Build `decompose_node` for multi-part queries.
- [ ] Extend `grade_node` and `rewrite_query_node` to handle both local and web result sets.
- [ ] Build the hand-crafted 20-question test set (mix of all 4 route types) referenced in `PRD.md` §6 — put it in `backend/tests/test_queries.md` or similar.
- [ ] Run the test set, measure routing accuracy, fix misclassifications by refining the router prompt.

**Done when:** All 4 route types work correctly on the test set with ≥90% routing accuracy (per `PRD.md` success metric).

## Phase 4 — Conflict Detection & Synthesis Quality
**Goal:** Handle the "outdated PDF vs. current web" scenario explicitly — this is the most distinctive/demo-worthy feature.

- [ ] Build `conflict_check_node`: compares local and web findings for factual disagreement (LLM-based comparison, structured output listing conflicts if any).
- [ ] Update `synthesize_node` to explicitly surface conflicts in the final answer rather than silently merging.
- [ ] Craft 2–3 deliberate test cases where an uploaded PDF has intentionally outdated info vs. a live web fact, confirm the conflict is surfaced correctly.

**Done when:** The conflict scenario demos cleanly and reproducibly — this will likely be the centerpiece of any portfolio walkthrough/demo video.

## Phase 5 — Reasoning Trace UI + Streaming
**Goal:** Make the agent's internal process visible — this is what makes "agentic" tangible to a viewer/interviewer, not just an implementation detail.

- [ ] Backend: convert `/chat` to streaming (SSE) emitting trace events as the graph executes, plus a final answer event.
- [ ] Frontend: `ReasoningTrace.tsx` component — collapsible panel showing each step live as it streams (route chosen → sub-queries → retrieval → grading → retry if any → conflict check → final answer).
- [ ] Frontend: `CitationChip.tsx` — inline clickable citations that expand to show the source snippet and origin (PDF page / web URL).
- [ ] Polish `ChatWindow.tsx` UX per `design.md`.

**Done when:** A live demo clearly shows the agent "thinking" step by step, not just a spinner-then-answer.

## Phase 6 — Polish, Docs, Demo Readiness
**Goal:** Portfolio-ready package.

- [ ] Write full `README.md`: problem statement, architecture diagram (can reuse from `architecture.md`), setup instructions, screenshots/GIF, "what makes this agentic" section explaining the retry/routing/conflict-detection explicitly (this is the part interviewers will probe).
- [ ] Record a short demo video/GIF showing: upload → hybrid query → conflict surfaced → cited answer.
- [ ] Clean up dead code, unused imports, stray console.logs/print statements.
- [ ] Final pass on `.env.example` completeness — a stranger should be able to clone and run with only their own free API keys.
- [ ] Optional stretch: deploy to a free-tier host (Render/Railway backend, Vercel frontend) if time allows.

**Done when:** Kamran can hand this repo + README to someone else (or an interviewer) and they can get it running in under 15 minutes.

## Explicit Non-Goals for All Phases
Per `PRD.md` §3 — do not build auth, fine-tuning, non-PDF ingestion, or mobile support unless the phase plan is explicitly revised to include them.

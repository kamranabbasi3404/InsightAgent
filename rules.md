# rules.md — Rules & Constraints for the Coding Agent

These rules are binding. When in doubt, prefer the simpler, more explicit, more free-tier-safe option.

## 1. Cost & API Rules (NON-NEGOTIABLE)

- **Zero paid services.** No credit card required anywhere in the stack.
- Approved external APIs:
  - **Groq API** (LLM inference) — free tier only, no paid rate-limit upgrades.
  - **Tavily API** (web search) — free tier only (1000 searches/month cap). Agent must NOT implement retry logic that could silently burn through this quota (e.g., no infinite retry loops on web search failures).
- Do NOT introduce OpenAI, Anthropic API (outside what's already provided), Pinecone, Weaviate Cloud, or any other paid/paid-by-default service without explicit approval.
- Do NOT add cloud deployment (AWS/GCP/Azure) unless explicitly requested — local-first only.
- If a "free tier" API requires a credit card on file even for free usage, flag it and ask before integrating — do not assume it's acceptable.

## 2. Environment & Secrets

- All API keys go in `.env` files, never hardcoded.
- Every service with a `.env` requirement must have a corresponding `.env.example` with placeholder values and a comment explaining where to get the real key.
- `.env`, `chroma_db/`, `node_modules/`, `__pycache__/`, `.venv/` must all be in `.gitignore`.

## 3. Code Style & Structure

### Python (Backend)
- Python 3.11+.
- Use type hints everywhere (function signatures, TypedDicts for state).
- Follow the folder structure defined in `architecture.md` — do not collapse everything into one giant `main.py`.
- Each LangGraph node lives in its own file under `agent/nodes/`. One responsibility per node.
- Prompts are NOT inline strings scattered in node files — centralize them under `agent/prompts/` so they're easy to iterate on and version.
- Use Pydantic models for all FastAPI request/response schemas.
- All LLM calls that need structured output (routing decision, grading decision) MUST use JSON mode / structured output — never parse free-form text with regex to extract a decision.
- Async/await throughout the FastAPI layer where I/O-bound (LLM calls, web search, DB calls).

### TypeScript/Next.js (Frontend)
- App Router (not Pages Router).
- Functional components only, with hooks.
- Keep API calls in a dedicated `lib/api.ts` — components should not construct fetch calls inline scattered everywhere.
- Use Tailwind for styling (see `design.md` for tokens).
- No `any` types unless truly unavoidable — prefer explicit interfaces for API responses (mirror the backend Pydantic schemas).

## 4. Agentic Behavior Rules (Core Product Correctness)

- **No hallucinated citations.** If a claim cannot be traced to a retrieved chunk or web snippet, it must not appear in the final answer, or must be explicitly flagged as "not found in available sources."
- **Bounded retries.** The self-correction/retry loop (grade → rewrite → retrieve) must have a hard-coded max retry count (default: 2). Never allow an unbounded loop — this is both a cost risk (API calls) and a UX risk (hanging requests).
- **Honesty over completeness.** If, after max retries, retrieval is still insufficient, the agent must say so plainly rather than generating a plausible-sounding but ungrounded answer.
- **Conflicts are surfaced, not resolved silently.** If local and web sources disagree, both must be shown with their sources — the agent should not silently prefer one.
- **Every node in the LangGraph must log a trace entry** (what it did, what it decided, why) into `state["trace"]` so the frontend reasoning panel has real data, not placeholder text.

## 5. Testing & Validation

- Before marking any phase "done," run the hand-crafted test query set (to be built in Phase 3 — see `phases.md`) and confirm routing/grading behaves as expected.
- New nodes added to the LangGraph must be unit-testable in isolation (pass a mock `AgentState` in, assert the output state).
- Do not skip writing the `.env.example` and `README.md` updates when adding a new required environment variable or setup step — undocumented setup steps break the "portfolio demo" goal.

## 6. Scope Discipline

- Do not silently add features beyond what's specified in `PRD.md` / current `phases.md` phase. If a good idea comes up mid-build (e.g., "let's add multi-turn memory"), note it as a stretch goal in `PRD.md` §8 rather than building it immediately — finish the current phase first.
- Do not swap approved tools (e.g., replacing ChromaDB with FAISS, or Tavily with SerpAPI) without flagging the change and the reason — consistency with `architecture.md` matters for a coherent portfolio narrative.

## 7. Communication Style for the Agent's Own Output

- When the agent (Claude Code) reports progress back to Kamran, it should be direct about what was built, what wasn't, and what's broken — no inflated "everything works perfectly" claims without having actually run/tested the relevant piece.
- Flag any deviation from `architecture.md` or `PRD.md` explicitly rather than quietly implementing something different.

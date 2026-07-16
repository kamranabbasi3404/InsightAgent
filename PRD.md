# PRD.md — InsightAgent: Multi-Source Agentic Research Analyst

## 1. Product Overview

**Product Name:** InsightAgent
**One-liner:** An agentic RAG research assistant that intelligently routes user queries across local documents (PDFs) and live web search, self-corrects on weak retrievals, resolves conflicts between stale and current information, and produces cited, synthesized answers.

**Problem Statement:**
Standard RAG systems blindly retrieve from a single static source and answer — they cannot judge whether their own retrieval is good enough, cannot decide between "this needs my uploaded documents" vs "this needs live internet data," and cannot detect when a PDF report is outdated relative to current web information. InsightAgent solves this by giving the LLM agency over the retrieval process itself.

**Target User:** Portfolio/demo project — simulates the persona of a research analyst who needs quick synthesis of both curated documents (reports, papers) and current web information (news, live data) for a given research question.

## 2. Goals

- Demonstrate true **agentic** behavior: routing, self-reflection, retry loops, multi-hop decomposition — not just "retrieve then generate."
- Ground every claim in a cited source (PDF page/section or web URL).
- Detect and explicitly surface conflicts between document-based and web-based information (e.g., outdated report vs. recent news).
- Keep the entire stack free/open-source — zero paid API keys, zero paid infrastructure.
- Ship a working, demoable product (backend + frontend), not just a notebook.

## 3. Non-Goals

- No multi-user authentication/accounts system (single-user local demo is fine; auth can be a stretch goal).
- No fine-tuning of any model.
- No production-scale deployment (Kubernetes, load balancing) — this is a portfolio demo, not a scaled SaaS.
- No support for non-PDF document types in v1 (no .docx, .pptx ingestion in MVP).
- No mobile app.

## 4. Core User Stories

1. **As a user**, I upload one or more PDFs (reports, papers) so the agent has a local knowledge base.
2. **As a user**, I ask a research question in natural language.
3. **As the agent**, I decide whether the question needs local PDF retrieval, live web search, or both.
4. **As the agent**, if my initial retrieval is weak/irrelevant, I reformulate the query and retry (bounded retries).
5. **As the agent**, if a multi-part question is asked, I decompose it into sub-questions, answer each, and synthesize.
6. **As the agent**, if local docs and web results conflict (e.g. different numbers/dates), I flag the conflict explicitly rather than silently picking one.
7. **As a user**, I see the final answer with clearly labeled citations (PDF name + page, or web URL + date).
8. **As a user**, I can see (optionally, via a "reasoning trace" panel) what steps the agent took — which route it chose, what it retrieved, whether it retried.

## 5. Functional Requirements

### 5.1 Document Ingestion
- Upload PDF(s) via frontend.
- Parse, chunk (semantic/recursive chunking), embed, and store in local vector DB.
- Support re-indexing / adding more documents without wiping existing ones.

### 5.2 Query Routing
- LLM-based router classifies each incoming query into: `local_only`, `web_only`, `hybrid`, or `no_retrieval_needed` (for pure conversational queries).

### 5.3 Retrieval
- Local retrieval: top-k semantic search against ChromaDB.
- Web retrieval: live search via free-tier web search API, returning snippets + URLs.

### 5.4 Self-Reflection / Correction Loop
- After retrieval, a grader step judges relevance of retrieved chunks/snippets to the query.
- If insufficient, the query is rewritten (max 2–3 retries) and retrieval repeats.
- If still insufficient after max retries, the agent must say so honestly rather than hallucinate.

### 5.5 Query Decomposition
- For compound/multi-part questions, break into atomic sub-queries, resolve each independently, then synthesize.

### 5.6 Conflict Detection
- When both local and web sources contribute to an answer, compare for factual conflicts (dates, numbers, claims).
- If conflict found, explicitly state both versions and their sources rather than silently merging.

### 5.7 Answer Synthesis & Citation
- Final answer must cite every non-trivial claim: `[Source: filename.pdf, p.4]` or `[Source: example.com, accessed July 2026]`.
- No claim should appear without a traceable source.

### 5.8 Reasoning Trace (Transparency Panel)
- Frontend shows a collapsible panel: route chosen, queries used, sources retrieved, whether a retry occurred, and why.

## 6. Success Metrics (for a portfolio project, these are demo-quality benchmarks, not production KPIs)

- Agent correctly routes at least 90% of a hand-crafted 20-question test set (mix of local-only, web-only, hybrid, conversational).
- Zero un-cited factual claims in final answers across test set.
- Retry loop demonstrably triggers and improves the answer on at least 3 deliberately "hard" test queries.
- End-to-end response time under ~20 seconds for hybrid queries (reasonable for free-tier APIs).

## 7. Constraints

- 100% free tools/APIs only (see rules.md for the enforced allowlist).
- Must run locally on a single developer machine (no cloud infra required for the demo).
- Must be resumable/portfolio-presentable: clean README, clear demo script, screenshots/GIF.

## 8. Out-of-Scope Stretch Goals (only after MVP is fully working)

- Multi-turn conversational memory across sessions.
- Support for additional file types (docx, csv, images with OCR).
- Deployment to a free-tier cloud host (e.g., Render/Railway free tier) for a live demo link.
- Simple auth for a shareable public demo.

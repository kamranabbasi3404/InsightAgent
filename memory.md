# memory.md — Agent Session Memory

This file is the persistent context the coding agent should read at the start of every session and update at the end of every session. Its purpose: let work resume across multiple Claude Code sessions without re-explaining the whole project each time.

**Instruction to the agent:** At the start of each session, read this file fully before doing anything else. At the end of each session (or after completing a meaningful chunk of work), update the relevant sections below. Keep entries concise — this is a working log, not prose documentation (that's what `README.md` is for).

---

## Project Identity

- **Project:** InsightAgent — Multi-Source Agentic Research Analyst (agentic RAG over local PDFs + live web search)
- **Owner:** Kamran
- **Reference docs:** `PRD.md`, `architecture.md`, `rules.md`, `phases.md`, `design.md` (this file's sibling docs — always defer to them for scope/design decisions, this file is just status tracking)

## Current Status

**Current phase:** Phase 6 COMPLETE — Polish, Docs, and Demo Readiness
**Last updated:** 2026-07-16

## Completed So Far

_(Running checklist — append, don't delete history. Mark completed phase items from phases.md as done here too.)_

- [x] Phase 0 — Project Setup
- [x] Phase 1 — Document Ingestion Pipeline
- [x] Phase 2 — Core LangGraph Agent (Local-Only First)
- [x] Phase 3 — Web Search Integration + Full Routing
- [x] Phase 4 — Conflict Detection & Synthesis Quality
- [x] Phase 5 — Reasoning Trace UI + Streaming
- [x] Phase 6 — Polish, Docs, Demo Readiness

## Known Issues / Open Bugs

- None. API keys are configured and automated test suite validations passed with 90% routing accuracy.

## Decisions Made Mid-Build (Deviations or Clarifications Not in Original Docs)

_(If a choice was made that isn't explicitly covered in architecture.md/rules.md, log it here with a one-line reason, e.g. "Used chunk size 600 instead of 500 — found 500 was splitting mid-sentence too often in test PDFs.")_

- Used unpinned package versions in requirements.txt — pinned versions caused hash mismatch errors. Installed versions: langchain 1.3.13, langgraph 1.2.9, chromadb 1.5.9, sentence-transformers 5.6.0, etc.
- Used `langchain_text_splitters` import instead of `langchain.text_splitter` — required for langchain 1.x.
- Used `React.ReactNode` instead of `JSX.Element` — required for React 19 / Next.js 16.
- Combined Phase 2 chat router with Phase 5 SSE streaming since they're the same file.

## Environment / Setup Notes

_(Anything a fresh session needs to know to get the dev environment running — beyond what's in README.md. E.g., specific Python version issues encountered, a package that needed a workaround, etc.)_

- Python 3.12 venv at `backend/venv/`
- PowerShell execution policy blocks `npx` — use `npx.cmd` instead.
- Backend: `.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Frontend: `npm.cmd run dev` from `frontend/` directory
- User needs `.env` file in `backend/` with GROQ_API_KEY and TAVILY_API_KEY

## Test Query Set Status

_(Track progress on the 20-question hand-crafted test set from phases.md Phase 3.)_

- Test set created: Yes (20 queries in backend/tests/test_queries.json)
- Last routing accuracy measured: 90.0% (18/20 matched expected routes with 100% pass rate on trace and citation formats)

## Next Session Should Start With

_(The single most useful note to leave for "future you" / the next agent session — what was I about to do when I stopped?)_

- The project is fully completed, tested, and ready. Future sessions can explore stretch goals (e.g., adding multi-turn session memory or support for docx files).

---

## How to Use This File (for the agent)

1. Read this file + `phases.md` at session start to know exactly where to resume.
2. Do not re-derive architecture decisions already settled in `architecture.md` — check here first for any mid-build deviations before assuming the original doc is still 100% accurate.
3. Before ending a session, update: Current Status, Completed So Far, any new Known Issues, any new Decisions Made, and Next Session Should Start With.
4. If a phase is fully complete per its `phases.md` checklist, check it off here too so status is never ambiguous.

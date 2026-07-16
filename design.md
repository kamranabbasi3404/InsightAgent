# design.md — UI/UX Design Specification

## 1. Design Philosophy

InsightAgent's UI has one job beyond "chat that works": **make the agent's reasoning visible**. The core differentiator of this project (vs. a plain chatbot) is that it routes, retries, and detects conflicts — if the UI hides all of that behind a spinner, the product's main value is invisible. Design should feel like a **research tool / analyst workbench**, not a generic chat bubble app.

## 2. Layout

**Desktop (primary target — this is a demo/portfolio tool, mobile-responsive is nice-to-have, not required for MVP):**

```
┌───────────────────────────────────────────────────────────┐
│  Header: "InsightAgent"  |  [Upload Docs] [Documents: 3]    │
├───────────────────┬───────────────────────────────────────┤
│                   │                                         │
│   Chat Window      │   Reasoning Trace Panel (collapsible)  │
│   (messages,       │   - Route: hybrid                      │
│   citations        │   - Sub-query 1: ...                   │
│   inline)          │   - Local retrieval: 4 chunks found     │
│                   │   - Web retrieval: 3 results found      │
│   [Input box]      │   - Grade: sufficient                   │
│                   │   - Conflicts: 1 found ⚠                │
│                   │                                         │
└───────────────────┴───────────────────────────────────────┘
```

- Left/main column (≈65% width): standard chat interface.
- Right column (≈35% width, collapsible to icon-only on narrow screens): live reasoning trace, updates in real time as the agent works through the graph.
- Header: minimal, product name + upload control + count of indexed documents.

## 3. Visual Design Tokens

Avoid generic "AI chatbot purple gradient" template look — go for a **clean, analytical, slightly technical** aesthetic (think: research/data tool, not consumer chat app).

**Color palette:**
- Background: near-white / very light gray (`#FAFAF9`) for light mode base.
- Primary accent: deep teal/blue (`#0F766E` or similar) — used for active states, sent messages, primary buttons. Avoid default Tailwind `indigo-500`/purple defaults — pick something distinct.
- Secondary accent (for "web source" tags): warm amber (`#B45309`) — for visually distinguishing web-sourced citations from PDF-sourced ones.
- PDF-sourced citation tag color: the primary teal.
- Conflict/warning indicator: red-orange (`#DC2626`) with a ⚠ icon — conflicts should visually stand out, they're a feature, not an error state to hide.
- Text: near-black (`#1C1917`) for primary, muted gray (`#78716C`) for secondary/meta text (timestamps, trace step labels).

**Typography:**
- Sans-serif throughout (e.g., `Inter` or system font stack) for UI chrome and chat text.
- Monospace (e.g., `JetBrains Mono` or `ui-monospace`) for the reasoning trace panel — reinforces the "you're looking at the machinery" feel and makes route/state labels visually distinct from conversational text.

**Spacing/shape:**
- Rounded corners, moderate (6–8px) — not overly soft/bubbly, not sharp/brutalist.
- Generous whitespace in chat; reasoning trace panel can be denser/more compact since it's reference info.

## 4. Key Components

### 4.1 ChatWindow
- User messages: right-aligned, teal background, white text.
- Agent messages: left-aligned, white/light-gray background, dark text.
- Agent messages render inline **CitationChips** wherever a claim is sourced.
- While the agent is working (streaming), show a subtle step indicator inline (e.g., "Routing query...", "Searching documents...", "Checking web...") rather than a generic spinner — this doubles as a lightweight version of the trace panel for users who keep it collapsed.

### 4.2 CitationChip
- Small inline pill/badge immediately after the claim it supports, e.g. `[1]` or a small document/globe icon.
- Color-coded: teal icon = PDF source, amber icon = web source.
- On hover/click: expands a small popover showing — source name, page number or URL, and the exact snippet that supports the claim.

### 4.3 ReasoningTrace Panel
- Vertical timeline/stepper layout, each step is a small card:
  - Icon + label (e.g., 🧭 Router, 🔍 Local Retrieval, 🌐 Web Retrieval, ✅ Grade, 🔁 Retry, ⚠ Conflict Check, ✍ Synthesis).
  - One-line summary per step (e.g., "Found 4 relevant chunks in report.pdf").
  - Retry steps visually nested/indented under the retrieval step they retried, with a distinct "retry" badge — this is the most important visual moment to get right, since it's the clearest proof of "agentic" behavior.
- Conflict entries, if any, get a highlighted (red-orange border) card that's impossible to miss — clicking it scrolls the chat to the relevant part of the answer.
- Collapsible via a toggle in the header, but **defaults to open** on desktop — it's a feature to show off, not clutter to hide.

### 4.4 UploadPanel
- Simple drag-and-drop zone + file picker button.
- Shows upload/processing progress (parsing → chunking → embedding → indexed).
- Below it, a compact list of currently indexed documents with chunk counts — reassures the user their docs are actually in the system.

## 5. Interaction Details

- Streaming text for the final answer (token-by-token or chunk-by-chunk) — feels responsive even though total pipeline latency (routing + retrieval + grading + synthesis) may be 10-20s.
- Reasoning trace steps should appear progressively as they happen (via SSE), not all at once at the end — this is the whole point of building the trace UI.
- Empty states matter: before any documents are uploaded, the chat input area should gently prompt "Upload a document or just ask a question — I can search the web too" rather than being blank.
- Errors (e.g., Tavily quota exceeded, Groq rate limit hit) should surface as a clear, human-readable message in the chat, not a raw stack trace or silent failure.

## 6. Accessibility Basics

- Sufficient color contrast for all text (WCAG AA minimum).
- Citation chips and conflict warnings should not rely on color alone — always paired with an icon and/or text label.
- Keyboard-navigable chat input and upload controls.

## 7. What to Explicitly Avoid

- Generic "ChatGPT clone" look (centered single column, purple gradients, rounded chat bubbles with no distinguishing visual identity).
- Hiding the reasoning trace by default — this undersells the project's core technical achievement.
- Dense walls of unformatted text in the final answer — use short paragraphs, and let citation chips break up claims visually.

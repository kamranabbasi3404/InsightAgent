"""
Conflict Check Node — Detects factual contradictions between local and web sources.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import CONFLICT_CHECK_PROMPT
from app.services.groq_client import get_primary_llm


def _format_source_content(results: list[dict], source_type: str) -> str:
    """Format results for the conflict check prompt."""
    if not results:
        return f"No {source_type} results available."

    parts: list[str] = []
    for i, result in enumerate(results, 1):
        if source_type == "local":
            source = result.get("metadata", {}).get("source_filename", "unknown")
            page = result.get("metadata", {}).get("page_number", "?")
            parts.append(f"[{i}] {source}, page {page}: {result.get('text', '')[:400]}")
        else:
            parts.append(f"[{i}] {result.get('title', 'No title')} ({result.get('url', '')}): {result.get('content', '')[:400]}")

    return "\n".join(parts)


async def conflict_check_node(state: AgentState) -> dict:
    """
    Compare local and web findings for factual contradictions.
    Only runs when both sources have results (hybrid queries).
    """
    local_results = state.get("local_results", [])
    web_results = state.get("web_results", [])

    # If only one source has data, no conflict possible
    if not local_results or not web_results:
        trace_entry = {
            "step": "conflict_check",
            "icon": "✅",
            "label": "Conflict Check",
            "summary": "Skipped — single source only",
            "detail": "Conflict detection only applies when both local and web sources contribute results.",
        }
        return {
            "conflicts": [],
            "trace": state.get("trace", []) + [trace_entry],
        }

    local_content = _format_source_content(local_results, "local")
    web_content = _format_source_content(web_results, "web")

    prompt = CONFLICT_CHECK_PROMPT.format(
        query=state["original_query"],
        local_content=local_content,
        web_content=web_content,
    )

    llm = get_primary_llm(json_mode=True)
    response = await llm.ainvoke(prompt)

    try:
        result = json.loads(response.content)
        has_conflicts = result.get("has_conflicts", False)
        conflicts = result.get("conflicts", [])
        reasoning = result.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        has_conflicts = False
        conflicts = []
        reasoning = "Conflict check JSON parse error — assuming no conflicts."

    if has_conflicts and conflicts:
        trace_entry = {
            "step": "conflict_check",
            "icon": "⚠️",
            "label": "Conflict Detection",
            "summary": f"⚠ {len(conflicts)} conflict(s) found!",
            "detail": reasoning,
            "conflicts": conflicts,
        }
    else:
        trace_entry = {
            "step": "conflict_check",
            "icon": "✅",
            "label": "Conflict Check",
            "summary": "No conflicts detected",
            "detail": reasoning,
        }

    return {
        "conflicts": conflicts,
        "trace": state.get("trace", []) + [trace_entry],
    }

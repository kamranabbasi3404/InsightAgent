"""
Rewrite Node — Rewrites the query to improve retrieval results.
Uses the fallback (8B) model since this is a lightweight task.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import REWRITE_PROMPT
from app.services.groq_client import get_fallback_llm
from app.config import MAX_RETRIES


async def rewrite_query_node(state: AgentState) -> dict:
    """
    Rewrite the query for better retrieval. Increments retry_count.
    """
    retry_count = state.get("retry_count", 0) + 1

    # Summarize what was retrieved (or not) so the rewriter has context
    local_count = len(state.get("local_results", []))
    web_count = len(state.get("web_results", []))
    results_summary = f"Local: {local_count} results, Web: {web_count} results. "
    if local_count == 0 and web_count == 0:
        results_summary += "No relevant content was found at all."
    else:
        results_summary += "Results were graded as insufficient/irrelevant to the query."

    prompt = REWRITE_PROMPT.format(
        original_query=state["original_query"],
        current_query=state.get("current_query", state["original_query"]),
        retry_count=retry_count,
        max_retries=MAX_RETRIES,
        results_summary=results_summary,
    )

    llm = get_fallback_llm(json_mode=True)
    response = await llm.ainvoke(prompt)

    try:
        result = json.loads(response.content)
        rewritten_query = result.get("rewritten_query", state["original_query"])
        strategy = result.get("strategy", "unknown")
    except (json.JSONDecodeError, AttributeError):
        rewritten_query = state["original_query"]
        strategy = "Fallback — using original query."

    trace_entry = {
        "step": "rewrite",
        "icon": "🔁",
        "label": f"Query Rewrite (Retry {retry_count}/{MAX_RETRIES})",
        "summary": f"Rewritten: \"{rewritten_query[:80]}...\"" if len(rewritten_query) > 80 else f"Rewritten: \"{rewritten_query}\"",
        "detail": f"Strategy: {strategy}",
        "is_retry": True,
    }

    return {
        "current_query": rewritten_query,
        "retry_count": retry_count,
        "trace": state.get("trace", []) + [trace_entry],
    }

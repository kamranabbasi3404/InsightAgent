"""
Grade Node — LLM judges whether retrieved content is sufficient to answer the query.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import GRADER_PROMPT
from app.services.groq_client import get_primary_llm


def _format_retrieved_content(state: AgentState) -> str:
    """Format local and web results into a readable string for the grader."""
    parts: list[str] = []

    local_results = state.get("local_results", [])
    if local_results:
        parts.append("=== Local Document Results ===")
        for i, result in enumerate(local_results, 1):
            source = result.get("metadata", {}).get("source_filename", "unknown")
            page = result.get("metadata", {}).get("page_number", "?")
            parts.append(f"[{i}] From {source}, page {page}:")
            parts.append(result.get("text", "")[:500])
            parts.append("")

    web_results = state.get("web_results", [])
    if web_results:
        parts.append("=== Web Search Results ===")
        for i, result in enumerate(web_results, 1):
            parts.append(f"[{i}] {result.get('title', 'No title')} ({result.get('url', 'no URL')}):")
            parts.append(result.get("content", "")[:500])
            parts.append("")

    if not parts:
        return "No results retrieved."

    return "\n".join(parts)


async def grade_node(state: AgentState) -> dict:
    """
    Evaluate whether retrieved content is sufficient to answer the user's query.
    """
    retrieved_content = _format_retrieved_content(state)

    prompt = GRADER_PROMPT.format(
        query=state.get("current_query", state["original_query"]),
        retrieved_content=retrieved_content,
    )

    llm = get_primary_llm(json_mode=True)
    response = await llm.ainvoke(prompt)

    try:
        result = json.loads(response.content)
        grade = result.get("grade", "insufficient")
        reasoning = result.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        # If we have any results at all, consider sufficient to avoid infinite loops
        has_results = bool(state.get("local_results")) or bool(state.get("web_results"))
        grade = "sufficient" if has_results else "insufficient"
        reasoning = "Fallback grading due to JSON parse error."

    # Validate grade
    if grade not in {"sufficient", "insufficient"}:
        grade = "sufficient"
        reasoning += " (corrected to sufficient — invalid grade value)"

    trace_entry = {
        "step": "grade",
        "icon": "✅" if grade == "sufficient" else "⚠️",
        "label": "Relevance Grading",
        "summary": f"Grade: {grade}",
        "detail": reasoning,
    }

    return {
        "retrieval_grade": grade,
        "trace": state.get("trace", []) + [trace_entry],
    }

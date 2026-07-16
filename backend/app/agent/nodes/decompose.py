"""
Decompose Node — Splits compound queries into atomic sub-queries.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import DECOMPOSE_PROMPT
from app.services.groq_client import get_primary_llm


async def decompose_node(state: AgentState) -> dict:
    """
    If the query is compound/multi-part, decompose into sub-queries.
    Otherwise, return [original_query] as the single sub-query.
    """
    prompt = DECOMPOSE_PROMPT.format(
        query=state["original_query"],
        route=state["route"],
    )

    llm = get_primary_llm(json_mode=True)
    response = await llm.ainvoke(prompt)

    try:
        result = json.loads(response.content)
        sub_queries = result.get("sub_queries", [state["original_query"]])
        is_compound = result.get("is_compound", False)
        reasoning = result.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        sub_queries = [state["original_query"]]
        is_compound = False
        reasoning = "Single query (JSON parse fallback)."

    # Ensure we have at least one sub-query
    if not sub_queries:
        sub_queries = [state["original_query"]]

    trace_entry = {
        "step": "decompose",
        "icon": "🔀",
        "label": "Query Decomposition",
        "summary": f"{'Decomposed into ' + str(len(sub_queries)) + ' sub-queries' if is_compound else 'Single query (no decomposition needed)'}",
        "detail": reasoning,
        "sub_queries": sub_queries,
    }

    return {
        "sub_queries": sub_queries,
        "trace": state.get("trace", []) + [trace_entry],
    }

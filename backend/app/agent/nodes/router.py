"""
Router Node — Classifies the user query into a retrieval strategy.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import ROUTER_PROMPT
from app.services.groq_client import get_primary_llm
from app.vectorstore.chroma_client import list_indexed_documents


async def router_node(state: AgentState) -> dict:
    """
    Classify the query into: local_only, web_only, hybrid, or no_retrieval.
    Uses structured JSON output from the LLM.
    """
    # Get list of indexed documents for context
    docs = list_indexed_documents()
    doc_list = ", ".join([d["filename"] for d in docs]) if docs else "No documents indexed."

    prompt = ROUTER_PROMPT.format(
        query=state["original_query"],
        document_list=doc_list,
    )

    llm = get_primary_llm(json_mode=True)
    response = await llm.ainvoke(prompt)

    try:
        result = json.loads(response.content)
        route = result.get("route", "web_only")
        reasoning = result.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        # Fallback: if no documents indexed, default to web_only; otherwise hybrid
        route = "web_only" if not docs else "hybrid"
        reasoning = "Fallback routing due to JSON parse error."

    # Validate route
    valid_routes = {"local_only", "web_only", "hybrid", "no_retrieval"}
    if route not in valid_routes:
        route = "hybrid"
        reasoning += " (corrected to hybrid — invalid route detected)"

    # If no documents are indexed, override local_only to web_only
    if route == "local_only" and not docs:
        route = "web_only"
        reasoning += " (overridden: no documents indexed, switching to web_only)"

    trace_entry = {
        "step": "router",
        "icon": "🧭",
        "label": "Query Router",
        "summary": f"Route: {route}",
        "detail": reasoning,
    }

    return {
        "route": route,
        "current_query": state["original_query"],
        "trace": state.get("trace", []) + [trace_entry],
    }

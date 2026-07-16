"""
Web Retrieve Node — Tavily web search for live information.
"""

from app.agent.state import AgentState
from app.services.tavily_client import search_web


async def retrieve_web_node(state: AgentState) -> dict:
    """
    Search the web via Tavily for each sub-query needing web results.
    """
    all_results: list[dict] = []
    queries_to_search = state.get("sub_queries", [state.get("current_query", state["original_query"])])

    # On retry, use the rewritten query
    if state.get("retry_count", 0) > 0:
        queries_to_search = [state["current_query"]]

    for query in queries_to_search:
        results = search_web(query, max_results=5)
        for result in results:
            # Avoid duplicate URLs across sub-queries
            if not any(r.get("url") == result.get("url") for r in all_results):
                all_results.append(result)

    # Sort by relevance score (higher = more relevant for Tavily)
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Limit total results
    all_results = all_results[:5]

    trace_entry = {
        "step": "retrieve_web",
        "icon": "🌐",
        "label": "Web Search Retrieval",
        "summary": f"Found {len(all_results)} web results",
        "detail": ", ".join(
            r.get("title", r.get("url", "unknown"))[:50] for r in all_results
        ) if all_results else "No web results found.",
        "result_count": len(all_results),
    }

    return {
        "web_results": all_results,
        "trace": state.get("trace", []) + [trace_entry],
    }

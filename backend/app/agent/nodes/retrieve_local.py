"""
Local Retrieve Node — Semantic search against ChromaDB for relevant chunks.
"""

from app.agent.state import AgentState
from app.vectorstore.chroma_client import query_chunks
from app.config import TOP_K


async def retrieve_local_node(state: AgentState) -> dict:
    """
    Query ChromaDB for the most relevant chunks matching the current query/sub-queries.
    """
    all_results: list[dict] = []
    queries_to_search = state.get("sub_queries", [state.get("current_query", state["original_query"])])

    # For local retrieval, use all sub-queries (or the rewritten current_query if retrying)
    if state.get("retry_count", 0) > 0:
        # On retry, use the rewritten query
        queries_to_search = [state["current_query"]]

    for query in queries_to_search:
        results = query_chunks(query, top_k=TOP_K)
        for result in results:
            # Avoid duplicates across sub-queries
            if not any(r["metadata"].get("chunk_id") == result["metadata"].get("chunk_id") for r in all_results):
                all_results.append(result)

    # Sort by relevance score (lower distance = more relevant for cosine)
    all_results.sort(key=lambda x: x.get("score", float("inf")))

    # Limit total results
    all_results = all_results[:TOP_K]

    trace_entry = {
        "step": "retrieve_local",
        "icon": "📄",
        "label": "Local Document Retrieval",
        "summary": f"Found {len(all_results)} relevant chunks from local documents",
        "detail": ", ".join(set(
            r["metadata"].get("source_filename", "unknown") for r in all_results
        )) if all_results else "No relevant chunks found.",
        "result_count": len(all_results),
    }

    return {
        "local_results": all_results,
        "trace": state.get("trace", []) + [trace_entry],
    }

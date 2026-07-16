"""
AgentState — TypedDict defining the state passed between LangGraph nodes.
"""

from typing import TypedDict


class AgentState(TypedDict):
    """
    State object passed between all nodes in the LangGraph agent.

    Fields:
        original_query: The user's original question.
        sub_queries: Decomposed sub-queries (or [original_query] if not compound).
        route: Routing decision — "local_only" | "web_only" | "hybrid" | "no_retrieval".
        local_results: Retrieved chunks from ChromaDB.
        web_results: Retrieved snippets from Tavily.
        retrieval_grade: "sufficient" | "insufficient".
        retry_count: Number of query rewrites performed so far.
        current_query: The current (possibly rewritten) query being used for retrieval.
        conflicts: Detected factual conflicts between local and web sources.
        final_answer: The synthesized final response.
        citations: Structured citation objects for the frontend.
        trace: Human-readable log of every step for the reasoning trace panel.
    """
    original_query: str
    sub_queries: list[str]
    route: str
    local_results: list[dict]
    web_results: list[dict]
    retrieval_grade: str
    retry_count: int
    current_query: str
    conflicts: list[dict]
    final_answer: str
    citations: list[dict]
    trace: list[dict]

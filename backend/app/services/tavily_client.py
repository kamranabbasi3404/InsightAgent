"""
Tavily Client — Web search service wrapper for live web retrieval.
"""

from tavily import TavilyClient
from app.config import TAVILY_API_KEY

# Module-level singleton
_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    """Get or create the Tavily client."""
    global _client
    if _client is None:
        _client = TavilyClient(api_key=TAVILY_API_KEY)
    return _client


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily API.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of result dicts, each containing:
            - title: Result title.
            - url: Source URL.
            - content: Snippet text.
            - score: Relevance score.
    """
    try:
        client = _get_client()
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=False,
        )

        results: list[dict] = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
            })

        return results

    except Exception as e:
        # Return empty results rather than crashing — the agent will handle
        # insufficient results through the grading/retry loop
        print(f"Tavily search error: {e}")
        return []

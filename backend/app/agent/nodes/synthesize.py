"""
Synthesize Node — Generates the final cited answer from retrieved sources.
"""

import json
from app.agent.state import AgentState
from app.agent.prompts.templates import SYNTHESIZE_PROMPT, NO_RETRIEVAL_PROMPT
from app.services.groq_client import get_primary_llm


def _format_local_content(results: list[dict]) -> str:
    """Format local results for the synthesis prompt."""
    if not results:
        return "No local document results available."

    parts: list[str] = []
    for i, result in enumerate(results, 1):
        source = result.get("metadata", {}).get("source_filename", "unknown")
        page = result.get("metadata", {}).get("page_number", "?")
        parts.append(f"[{i}] Source: {source}, Page {page}")
        parts.append(result.get("text", ""))
        parts.append("")

    return "\n".join(parts)


def _format_web_content(results: list[dict]) -> str:
    """Format web results for the synthesis prompt."""
    if not results:
        return "No web search results available."

    parts: list[str] = []
    for i, result in enumerate(results, 1):
        parts.append(f"[{i}] Title: {result.get('title', 'No title')}")
        parts.append(f"    URL: {result.get('url', 'No URL')}")
        parts.append(f"    Content: {result.get('content', '')}")
        parts.append("")

    return "\n".join(parts)


def _format_conflicts(conflicts: list[dict]) -> str:
    """Format conflicts for the synthesis prompt."""
    if not conflicts:
        return "No conflicts detected."

    parts: list[str] = []
    for i, conflict in enumerate(conflicts, 1):
        parts.append(f"Conflict {i}: {conflict.get('topic', 'Unknown topic')}")
        parts.append(f"  Local claim: {conflict.get('local_claim', 'N/A')}")
        parts.append(f"  Web claim: {conflict.get('web_claim', 'N/A')}")
        parts.append(f"  Explanation: {conflict.get('explanation', 'N/A')}")
        parts.append("")

    return "\n".join(parts)


def _extract_citations(state: AgentState) -> list[dict]:
    """Extract structured citation objects from the results for the frontend."""
    citations: list[dict] = []
    citation_id = 1

    for result in state.get("local_results", []):
        metadata = result.get("metadata", {})
        citations.append({
            "id": citation_id,
            "type": "pdf",
            "source": metadata.get("source_filename", "unknown"),
            "page": metadata.get("page_number", None),
            "snippet": result.get("text", "")[:200],
        })
        citation_id += 1

    for result in state.get("web_results", []):
        citations.append({
            "id": citation_id,
            "type": "web",
            "source": result.get("url", ""),
            "title": result.get("title", ""),
            "snippet": result.get("content", "")[:200],
        })
        citation_id += 1

    return citations


async def synthesize_node(state: AgentState) -> dict:
    """
    Generate the final answer with inline citations.
    Handles both retrieval-based and no-retrieval (conversational) queries.
    """
    route = state.get("route", "")

    # No-retrieval route — direct conversational response
    if route == "no_retrieval":
        prompt = NO_RETRIEVAL_PROMPT.format(query=state["original_query"])
        llm = get_primary_llm(temperature=0.7)
        response = await llm.ainvoke(prompt)

        trace_entry = {
            "step": "synthesize",
            "icon": "✍️",
            "label": "Response Generation",
            "summary": "Generated conversational response (no retrieval needed)",
            "detail": "",
        }

        return {
            "final_answer": response.content,
            "citations": [],
            "trace": state.get("trace", []) + [trace_entry],
        }

    # Retrieval-based synthesis
    local_content = _format_local_content(state.get("local_results", []))
    web_content = _format_web_content(state.get("web_results", []))
    conflicts = _format_conflicts(state.get("conflicts", []))

    prompt = SYNTHESIZE_PROMPT.format(
        query=state["original_query"],
        local_content=local_content,
        web_content=web_content,
        conflicts=conflicts,
    )

    llm = get_primary_llm(temperature=0.1)
    response = await llm.ainvoke(prompt)

    citations = _extract_citations(state)

    trace_entry = {
        "step": "synthesize",
        "icon": "✍️",
        "label": "Answer Synthesis",
        "summary": f"Generated cited answer ({len(citations)} sources referenced)",
        "detail": f"Local sources: {len(state.get('local_results', []))}, Web sources: {len(state.get('web_results', []))}, Conflicts: {len(state.get('conflicts', []))}",
    }

    return {
        "final_answer": response.content,
        "citations": citations,
        "trace": state.get("trace", []) + [trace_entry],
    }

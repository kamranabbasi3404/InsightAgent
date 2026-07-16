"""
Chat router — Handles user queries via the LangGraph agent with SSE streaming.
"""

import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.graph import agent_graph
from app.agent.state import AgentState

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str


class ChatResponse(BaseModel):
    """Response model for non-streaming chat endpoint."""
    answer: str
    citations: list[dict]
    trace: list[dict]
    conflicts: list[dict]
    route: str


async def _run_agent(query: str) -> AgentState:
    """
    Run the LangGraph agent with the given query.

    Args:
        query: The user's question.

    Returns:
        Final agent state with answer, citations, trace, etc.
    """
    initial_state: AgentState = {
        "original_query": query,
        "sub_queries": [],
        "route": "",
        "local_results": [],
        "web_results": [],
        "retrieval_grade": "",
        "retry_count": 0,
        "current_query": query,
        "conflicts": [],
        "final_answer": "",
        "citations": [],
        "trace": [],
    }

    # Run the graph
    result = await agent_graph.ainvoke(initial_state)
    return result


async def _stream_agent(query: str):
    """
    Stream agent execution via SSE, emitting trace events as they happen.

    Yields SSE-formatted events:
        - event: trace — each step of the agent's reasoning
        - event: answer — the final synthesized answer
        - event: done — signals completion
    """
    initial_state: AgentState = {
        "original_query": query,
        "sub_queries": [],
        "route": "",
        "local_results": [],
        "web_results": [],
        "retrieval_grade": "",
        "retry_count": 0,
        "current_query": query,
        "conflicts": [],
        "final_answer": "",
        "citations": [],
        "trace": [],
    }

    previous_trace_len = 0

    try:
        # Use astream for step-by-step streaming
        async for step_output in agent_graph.astream(initial_state):
            # Each step_output is a dict keyed by the node name
            for node_name, node_state in step_output.items():
                # Emit new trace entries
                current_trace = node_state.get("trace", [])
                if len(current_trace) > previous_trace_len:
                    for trace_entry in current_trace[previous_trace_len:]:
                        yield f"event: trace\ndata: {json.dumps(trace_entry)}\n\n"
                    previous_trace_len = len(current_trace)

                # If this is the synthesize node, emit the final answer
                if node_name == "synthesize":
                    answer_data = {
                        "answer": node_state.get("final_answer", ""),
                        "citations": node_state.get("citations", []),
                        "conflicts": node_state.get("conflicts", []),
                        "route": node_state.get("route", ""),
                    }
                    yield f"event: answer\ndata: {json.dumps(answer_data)}\n\n"

        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"

    except Exception as e:
        error_data = {"error": str(e), "type": type(e).__name__}
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint. Returns the full response once the agent completes.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        result = await _run_agent(request.query)
        return ChatResponse(
            answer=result.get("final_answer", ""),
            citations=result.get("citations", []),
            trace=result.get("trace", []),
            conflicts=result.get("conflicts", []),
            route=result.get("route", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint via SSE. Emits trace events in real time
    as the agent processes the query, followed by the final answer.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return StreamingResponse(
        _stream_agent(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

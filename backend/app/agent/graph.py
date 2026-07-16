"""
LangGraph Agent Definition — Nodes, edges, and conditional routing.

This is the core orchestration graph implementing the agentic RAG workflow:
    router → decompose → retrieve → grade → [rewrite → retrieve]* → conflict_check → synthesize
"""

from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes.router import router_node
from app.agent.nodes.decompose import decompose_node
from app.agent.nodes.retrieve_local import retrieve_local_node
from app.agent.nodes.retrieve_web import retrieve_web_node
from app.agent.nodes.grade import grade_node
from app.agent.nodes.rewrite import rewrite_query_node
from app.agent.nodes.conflict_check import conflict_check_node
from app.agent.nodes.synthesize import synthesize_node
from app.config import MAX_RETRIES


# --- Conditional Edge Functions ---

def route_after_router(state: AgentState) -> str:
    """After routing, decide which path to take."""
    route = state.get("route", "web_only")
    if route == "no_retrieval":
        return "synthesize"
    return "decompose"


def route_after_decompose(state: AgentState) -> str:
    """After decomposition, decide which retrieval nodes to run."""
    route = state.get("route", "web_only")
    if route == "local_only":
        return "retrieve_local"
    elif route == "web_only":
        return "retrieve_web"
    else:  # hybrid
        return "retrieve_local"  # local first, then web


def route_after_local_retrieve(state: AgentState) -> str:
    """After local retrieval, decide whether to also do web retrieval."""
    route = state.get("route", "")
    if route == "hybrid":
        return "retrieve_web"
    return "grade"


def route_after_grade(state: AgentState) -> str:
    """After grading, decide whether to rewrite or proceed."""
    grade = state.get("retrieval_grade", "sufficient")
    retry_count = state.get("retry_count", 0)

    if grade == "insufficient" and retry_count < MAX_RETRIES:
        return "rewrite"
    return "conflict_check"


def route_after_rewrite(state: AgentState) -> str:
    """After rewriting, go back to retrieval based on the route."""
    route = state.get("route", "web_only")
    if route == "local_only":
        return "retrieve_local"
    elif route == "web_only":
        return "retrieve_web"
    else:  # hybrid — re-run both
        return "retrieve_local"


# --- Build the Graph ---

def build_agent_graph() -> StateGraph:
    """
    Build and compile the LangGraph agent workflow.

    Graph structure:
        START → router → decompose → retrieve_local/retrieve_web → grade
            → (if insufficient & retries left) rewrite → retrieve → grade
            → (if sufficient or retries exhausted) conflict_check → synthesize → END
    """
    workflow = StateGraph(AgentState)

    # --- Add Nodes ---
    workflow.add_node("router", router_node)
    workflow.add_node("decompose", decompose_node)
    workflow.add_node("retrieve_local", retrieve_local_node)
    workflow.add_node("retrieve_web", retrieve_web_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("rewrite", rewrite_query_node)
    workflow.add_node("conflict_check", conflict_check_node)
    workflow.add_node("synthesize", synthesize_node)

    # --- Set Entry Point ---
    workflow.set_entry_point("router")

    # --- Add Conditional Edges ---

    # Router → decompose (or straight to synthesize for no_retrieval)
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "synthesize": "synthesize",
            "decompose": "decompose",
        },
    )

    # Decompose → appropriate retrieval node
    workflow.add_conditional_edges(
        "decompose",
        route_after_decompose,
        {
            "retrieve_local": "retrieve_local",
            "retrieve_web": "retrieve_web",
        },
    )

    # Local retrieve → web retrieve (if hybrid) or grade
    workflow.add_conditional_edges(
        "retrieve_local",
        route_after_local_retrieve,
        {
            "retrieve_web": "retrieve_web",
            "grade": "grade",
        },
    )

    # Web retrieve → always grade
    workflow.add_edge("retrieve_web", "grade")

    # Grade → rewrite (if insufficient) or conflict_check (if sufficient/retries exhausted)
    workflow.add_conditional_edges(
        "grade",
        route_after_grade,
        {
            "rewrite": "rewrite",
            "conflict_check": "conflict_check",
        },
    )

    # Rewrite → back to retrieval
    workflow.add_conditional_edges(
        "rewrite",
        route_after_rewrite,
        {
            "retrieve_local": "retrieve_local",
            "retrieve_web": "retrieve_web",
        },
    )

    # Conflict check → synthesize
    workflow.add_edge("conflict_check", "synthesize")

    # Synthesize → END
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# Pre-compiled graph instance
agent_graph = build_agent_graph()

from functools import lru_cache

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agents.reasoning_agent import reasoning_agent
from app.services.agents.report_agent import report_agent
from app.services.agents.retrieval_agent import retrieval_agent
from app.services.agents.state import AgentState
from app.services.agents.validation_agent import validation_agent


async def run_agent_workflow(request: ChatRequest) -> ChatResponse:
    state: AgentState = {
        "question": request.question,
        "mode": request.mode,
        "sources": [],
        "validation_notes": [],
    }

    state = await _run_langgraph(state)

    return ChatResponse(
        answer=state.get("answer", ""),
        sources=state.get("sources", []),
        validation_status=state.get("validation_status", "not_evaluated"),
        validation_notes=state.get("validation_notes", []),
    )


async def _run_langgraph(state: AgentState) -> AgentState:
    workflow = _get_compiled_workflow()
    if workflow is None:
        return await _run_sequential_fallback(state)

    return await workflow.ainvoke(state)


def warm_agent_workflow() -> None:
    _get_compiled_workflow()


@lru_cache(maxsize=1)
def _get_compiled_workflow():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return None

    graph = StateGraph(AgentState)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("reasoning", reasoning_agent)
    graph.add_node("report", report_agent)
    graph.add_node("validation", validation_agent)

    graph.add_edge(START, "retrieval")
    graph.add_edge("retrieval", "reasoning")
    graph.add_edge("reasoning", "report")
    graph.add_edge("report", "validation")
    graph.add_edge("validation", END)

    return graph.compile()


async def _run_sequential_fallback(state: AgentState) -> AgentState:
    state = retrieval_agent(state)
    state = await reasoning_agent(state)
    state = report_agent(state)
    return validation_agent(state)

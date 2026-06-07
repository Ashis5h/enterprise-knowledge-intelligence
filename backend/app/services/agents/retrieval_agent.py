from app.services.agents.state import AgentState
from app.services.rag.retriever import retrieve_context


def retrieval_agent(state: AgentState) -> AgentState:
    context, sources = retrieve_context(state["question"])
    return {
        **state,
        "context": context,
        "sources": sources,
    }


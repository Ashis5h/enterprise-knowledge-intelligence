from app.services.agents.state import AgentState
from app.services.llm.provider import get_llm_provider


async def reasoning_agent(state: AgentState) -> AgentState:
    if state.get("mode") == "report":
        return {
            **state,
            "answer": "",
        }

    llm = get_llm_provider()
    answer = await llm.generate(prompt=state["question"], context=state.get("context", ""))
    return {
        **state,
        "answer": answer,
    }

from app.services.agents.state import AgentState


def validation_agent(state: AgentState) -> AgentState:
    has_context = bool(state.get("context"))
    has_sources = bool(state.get("sources"))

    if has_context and has_sources:
        return {
            **state,
            "validation_status": "grounded",
            "validation_notes": ["Answer generated with retrieved enterprise context."],
        }

    return {
        **state,
        "validation_status": "needs_review",
        "validation_notes": ["No supporting source context was found."],
    }


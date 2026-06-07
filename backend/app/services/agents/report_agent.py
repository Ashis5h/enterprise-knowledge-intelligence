import re

from app.services.agents.state import AgentState


def report_agent(state: AgentState) -> AgentState:
    answer = state.get("answer", "")
    if state.get("mode") == "report":
        preferred_document = _preferred_document_name(state)
        answer = _build_report(
            question=state.get("question", ""),
            context=_report_context(state, preferred_document),
            preferred_document=preferred_document,
        )
    return {
        **state,
        "answer": answer,
    }


def _build_report(question: str, context: str, preferred_document: str | None = None) -> str:
    sentences = _extract_sentences(context, preferred_document)
    if not sentences:
        return "No report could be generated because no supporting enterprise context was found."

    focus_terms = _focus_terms(question)
    ranked = sorted(
        sentences,
        key=lambda sentence: _sentence_score(sentence, focus_terms),
        reverse=True,
    )
    selected = []
    for sentence in ranked:
        cleaned = _clean_sentence(sentence)
        if cleaned and cleaned not in selected:
            selected.append(cleaned)
        if len(selected) == 5:
            break

    title = _report_title(question)
    bullets = "\n".join(f"- {sentence}" for sentence in selected)
    return f"{title}\n\nKey Insights\n{bullets}\n\nRecommended Follow-Up\n- Review the cited source documents before making operational decisions."


def _extract_sentences(context: str, preferred_document: str | None) -> list[str]:
    compact_context = " ".join(context.split())
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", compact_context)
        if len(sentence.split()) >= 6 and _matches_preferred_document(sentence, preferred_document)
    ]


def _focus_terms(question: str) -> set[str]:
    stop_words = {
        "create",
        "generate",
        "summary",
        "summarize",
        "report",
        "compare",
        "give",
        "about",
        "with",
        "from",
        "the",
        "and",
    }
    return {
        token.rstrip("s")
        for token in re.findall(r"[a-zA-Z0-9]+", question.lower())
        if len(token) > 3 and token not in stop_words
    }


def _sentence_score(sentence: str, focus_terms: set[str]) -> int:
    sentence_terms = {
        token.rstrip("s")
        for token in re.findall(r"[a-zA-Z0-9]+", sentence.lower())
    }
    score = len(sentence_terms.intersection(focus_terms))
    if re.search(r"\b(must|required|should|within|before|approval|restricted)\b", sentence.lower()):
        score += 1
    return score


def _report_title(question: str) -> str:
    if "compare" in question.lower():
        return "Comparative Report"
    if "executive" in question.lower():
        return "Executive Summary"
    return "Enterprise Knowledge Report"


def _clean_sentence(sentence: str) -> str:
    cleaned = " ".join(sentence.strip().split())
    headings = [
        "Enterprise Leave Policy",
        "IT Support SOP",
        "Enterprise Security Guidelines",
        "Employee Handbook",
        "Project Documentation Standard",
    ]
    for heading in headings:
        cleaned = re.sub(rf"^{re.escape(heading)}\s+", "", cleaned)
    return cleaned


def _preferred_document_name(state: AgentState) -> str | None:
    sources = state.get("sources", [])
    if not sources:
        return None

    return sources[0].document_name


def _report_context(state: AgentState, preferred_document: str | None) -> str:
    sources = state.get("sources", [])
    if preferred_document and sources:
        excerpts = [
            source.excerpt
            for source in sources
            if source.document_name == preferred_document and source.excerpt
        ]
        if excerpts:
            return "\n".join(excerpts)

    return state.get("context", "")


def _matches_preferred_document(sentence: str, preferred_document: str | None) -> bool:
    if preferred_document == "security_guidelines.txt":
        return bool(
            re.search(
                r"\b(security|mfa|confidential|phishing|usb|incident|email|vpn|credential)\b",
                sentence.lower(),
            )
        )
    if preferred_document == "it_support_sop.txt":
        return bool(re.search(r"\b(it|support|service desk|incident|ticket|laptop|helpdesk)\b", sentence.lower()))
    if preferred_document == "employee_handbook.txt":
        return bool(re.search(r"\b(employee|working|training|performance|travel|manager)\b", sentence.lower()))
    if preferred_document == "project_documentation.txt":
        return bool(re.search(r"\b(project|documentation|status|technical|change|closure)\b", sentence.lower()))

    return True

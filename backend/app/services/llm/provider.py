import re

import httpx


from app.core.config import settings


NO_CONTEXT_RESPONSE = (
    "I could not find enough trusted enterprise context to answer this yet. "
    "Please upload relevant documents first."
)

_SMALL_TALK_PATTERNS = {
    r"\b(hi|hello|hey|howdy|hiya)\b": "Hello! I'm your Enterprise Knowledge Assistant. Ask me anything about your company documents.",
    r"\b(how are you|how do you do|how's it going)\b": "I'm ready to help! Ask me anything about your enterprise documents.",
    r"\bthank(s| you)\b": "You're welcome! Let me know if you have more questions.",
    r"\b(bye|goodbye|see you|cya|good night|goodnight|good morning|good afternoon|good evening)\b": "Goodbye! Come back anytime you need help with your documents.",
    r"\bwhat (are|r) you\b": "I'm an Enterprise Knowledge Assistant — I help you find answers from your company's uploaded documents.",
    r"\bwho (are|r) you\b": "I'm your Enterprise Knowledge Assistant, built to answer questions from your organization's documents.",
}

_NOT_A_QUESTION_RESPONSE = (
    "I'm your Enterprise Knowledge Assistant. Please ask me a question about your company documents, "
    "policies, or procedures and I'll find the answer for you."
)


def _is_meaningful_question(prompt: str) -> bool:
    """Return False for gibberish, single letters, or very short non-question inputs."""
    text = prompt.strip()
    # Too short to be a real question
    if len(text) < 4:
        return False
    # Only non-alphabetic characters
    if not re.search(r"[a-zA-Z]{2,}", text):
        return False
    # Repeated characters like "kkk", "aaa"
    if re.fullmatch(r"(.)\1+", text.lower()):
        return False
    # Must contain at least one common English vowel pattern or real word structure
    words = re.findall(r"[a-zA-Z]+", text.lower())
    real_words = [w for w in words if re.search(r"[aeiou]", w) or len(w) <= 2]
    if not real_words:
        return False
    # If most words look like gibberish (long consonant clusters), reject
    gibberish_words = [w for w in words if len(w) >= 4 and not re.search(r"[aeiou]", w)]
    if len(gibberish_words) >= len(words):
        return False
    return True

SYSTEM_PROMPT = (
    "You are an enterprise knowledge assistant. Answer only from the "
    "provided enterprise context. If the context is insufficient, say "
    "that the answer is not available in the uploaded documents. "
    "Keep answers concise and factual. Do not invent facts."
)


class LocalLLMProvider:
    async def generate(self, prompt: str, context: str = "") -> str:
        small_talk = _check_small_talk(prompt)
        if small_talk:
            return small_talk
        if not _is_meaningful_question(prompt):
            return _NOT_A_QUESTION_RESPONSE
        if not context:
            return NO_CONTEXT_RESPONSE
        return _extract_grounded_answer(prompt, context)


class OllamaLLMProvider:
    """Calls a local Ollama server (http://localhost:11434 by default)."""

    def __init__(self) -> None:
        self._fallback = LocalLLMProvider()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def generate(self, prompt: str, context: str = "") -> str:
        small_talk = _check_small_talk(prompt)
        if small_talk:
            return small_talk

        if not _is_meaningful_question(prompt):
            return _NOT_A_QUESTION_RESPONSE

        if not context:
            return NO_CONTEXT_RESPONSE

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question:\n{prompt}\n\n"
                    f"Enterprise context:\n{context}\n\n"
                    "Return the final answer only."
                ),
            },
        ]

        try:
            async with httpx.AsyncClient(timeout=settings.openai_timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json={
                        "model": self._model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.1},
                    },
                )
                response.raise_for_status()
                payload = response.json()
                content = payload.get("message", {}).get("content", "").strip()
                return content or await self._fallback.generate(prompt, context)
        except httpx.HTTPError:
            return await self._fallback.generate(prompt, context)


class OpenAICompatibleLLMProvider:
    def __init__(self) -> None:
        self._fallback = LocalLLMProvider()

    async def generate(self, prompt: str, context: str = "") -> str:
        if not context:
            return NO_CONTEXT_RESPONSE

        if not settings.openai_api_key:
            return await self._fallback.generate(prompt, context)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question:\n{prompt}\n\n"
                    f"Enterprise context:\n{context}\n\n"
                    "Return the final answer only."
                ),
            },
        ]

        try:
            async with httpx.AsyncClient(timeout=settings.openai_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.llm_model,
                        "messages": messages,
                        "temperature": 0.1,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                content = payload["choices"][0]["message"]["content"].strip()
                return content or await self._fallback.generate(prompt, context)
        except httpx.HTTPError:
            return await self._fallback.generate(prompt, context)


def get_llm_provider() -> LocalLLMProvider | OllamaLLMProvider | OpenAICompatibleLLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "ollama":
        return OllamaLLMProvider()
    if provider in {"openai", "openai-compatible"}:
        return OpenAICompatibleLLMProvider()
    return LocalLLMProvider()


def _extract_grounded_answer(question: str, context: str) -> str:
    clean_context = _remove_heading_lines(context)
    sentences = re.split(r"(?<=[.!?])\s+", clean_context.strip())
    question_terms = {
        _normalize_term(term)
        for term in re.findall(r"[a-zA-Z0-9]+", question.lower())
        if len(term) > 3 and term not in {"many", "allowed", "what", "when"}
    }

    ranked: list[tuple[int, str]] = []
    for sentence in sentences:
        sentence_terms = {_normalize_term(term) for term in re.findall(r"[a-zA-Z0-9]+", sentence.lower())}
        score = len(question_terms.intersection(sentence_terms))
        if _asks_for_time(question) and re.search(r"\b(within|before|after|days?|minutes?|hours?|friday)\b", sentence.lower()):
            score += 2
        if score:
            ranked.append((score, _clean_sentence(sentence)))

    if ranked:
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked[0][1]

    return _clean_sentence(sentences[0]) if sentences else "No answer could be extracted from the context."


def _remove_heading_lines(context: str) -> str:
    lines = []
    for line in context.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped.split()) <= 5 and not re.search(r"[.!?]$", stripped):
            continue
        lines.append(stripped)
    return " ".join(lines)


def _clean_sentence(sentence: str) -> str:
    cleaned = " ".join(sentence.strip().split())
    return re.sub(r"^Enterprise Leave Policy\s+", "", cleaned)


def _asks_for_time(question: str) -> bool:
    return bool(re.search(r"\b(when|time|due|deadline|acknowledg\w*)\b", question.lower()))


def _check_small_talk(prompt: str) -> str | None:
    text = prompt.strip().lower()
    for pattern, response in _SMALL_TALK_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return response
    return None


def _normalize_term(term: str) -> str:
    if term.startswith("acknowledg"):
        return "acknowledge"
    if term.startswith("submit"):
        return "submit"
    if term.startswith("report"):
        return "report"
    if term.startswith("incident"):
        return "incident"
    return term.rstrip("s")

"""
AI engine integration for RoboUsr.

This module talks to a local llama.cpp server that exposes an
OpenAI-compatible HTTP API (default: http://127.0.0.1:8001/v1).

It supports both OpenAI Python SDK styles:
- v1.x:   from openai import OpenAI; client.chat.completions.create(...)
- legacy: import openai; openai.ChatCompletion.create(...)

Configuration is read from core.config:
- OPENAI_API_BASE: base URL to llama.cpp server (e.g., "http://127.0.0.1:8001/v1")
- OPENAI_API_KEY:  dummy key (required by SDK; not validated by local server)
- LLAMA_MODEL_NAME: model/alias name served by llama.cpp (e.g., "saiga-llama3-8b")

Primary function:
- generate_reply(persona_text, conversation_history, user_message, ...)

The function returns the assistant's reply (str) or None on failure.
"""

from __future__ import annotations

from typing import List, Tuple, Optional, Sequence, Dict, Any
import logging

from core.config import OPENAI_API_BASE, OPENAI_API_KEY, LLAMA_MODEL_NAME

logger = logging.getLogger(__name__)


_USING_OPENAI_V1 = False
_client_v1 = None
_openai_legacy = None

try:
    from openai import OpenAI
    _client_v1 = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
    _USING_OPENAI_V1 = True
    logger.debug("AI engine: using OpenAI v1 client")
except Exception:
    try:
        import openai as _openai_legacy
        _openai_legacy.api_base = OPENAI_API_BASE
        _openai_legacy.api_key = OPENAI_API_KEY
        logger.debug("AI engine: using legacy openai client")
    except Exception as e:
        logger.error("Failed to initialize OpenAI client: %s", e)
        _openai_legacy = None


def build_messages(
    persona_text: Optional[str],
    conversation_history: List[Tuple[str, str]],
    user_message: str,
) -> List[Dict[str, str]]:
    """
    Build OpenAI-style messages array.

    Parameters
    ----------
    persona_text : Optional[str]
        System prompt that describes the persona's style/behavior.
    conversation_history : list[tuple[str, str]]
        Recent messages as (role, content) pairs where role is "user" or "assistant".
    user_message : str
        The latest end-user message that we want to respond to.

    Returns
    -------
    list[dict]
        Messages formatted for the OpenAI Chat Completions API.
    """
    messages: List[Dict[str, str]] = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})

    for role, content in conversation_history or []:
        role_norm = "assistant" if role == "assistant" else "user"
        if content is None:
            continue
        messages.append({"role": role_norm, "content": str(content)})

    messages.append({"role": "user", "content": str(user_message)})
    return messages


def server_ok() -> bool:
    """
    Lightweight health check against the local llama.cpp server.

    Returns
    -------
    bool
        True if the server responds to a basic models list request, False otherwise.
    """
    try:
        if _USING_OPENAI_V1 and _client_v1 is not None:
            _ = _client_v1.models.list()
            return True
        elif _openai_legacy is not None:
            _ = _openai_legacy.Model.list()
            return True
    except Exception as e:
        logger.warning("AI server healthcheck failed: %s", e)
    return False


def generate_reply(
    persona_text: Optional[str],
    conversation_history: List[Tuple[str, str]],
    user_message: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
    stop: Optional[Sequence[str]] = None,
    request_timeout: Optional[float] = None,
) -> Optional[str]:
    """
    Generate a reply using the local Saiga-LLaMA-3 model served by llama.cpp.

    Parameters
    ----------
    persona_text : Optional[str]
        Persona system prompt (in Russian by default).
    conversation_history : list[tuple[str, str]]
        Recent (role, content) messages; role is one of {"user", "assistant"}.
    user_message : str
        Latest user input.
    model : Optional[str]
        Override model/alias name. Defaults to core.config.LLAMA_MODEL_NAME.
    temperature : float
        Sampling temperature (higher = more random).
    top_p : float
        Nucleus sampling (cumulative probability).
    max_tokens : int
        Maximum tokens to generate for the reply.
    stop : Optional[Sequence[str]]
        Optional stop sequences.
    request_timeout : Optional[float]
        Timeout for the API call in seconds.

    Returns
    -------
    Optional[str]
        Assistant reply text, or None if generation failed.
    """
    selected_model = model or LLAMA_MODEL_NAME
    messages = build_messages(persona_text, conversation_history, user_message)

    try:
        if _USING_OPENAI_V1 and _client_v1 is not None:
            resp = _client_v1.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stop=stop,
                timeout=request_timeout,
            )
            if not resp or not getattr(resp, "choices", None):
                return None
            text = getattr(resp.choices[0].message, "content", None)
            return text.strip() if isinstance(text, str) else None

        elif _openai_legacy is not None:
            resp = _openai_legacy.ChatCompletion.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stop=stop,
                request_timeout=request_timeout,
            )
            text = resp.get("choices", [{}])[0].get("message", {}).get("content")
            return text.strip() if isinstance(text, str) else None

        else:
            logger.error("No OpenAI client available; cannot generate reply.")
            return None

    except Exception as e:
        logger.error("AI generation error: %s", e)
        return None

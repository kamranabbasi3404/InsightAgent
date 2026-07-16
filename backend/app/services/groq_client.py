"""
Groq LLM Client — Wrapper for Groq API with primary/fallback model support.
"""

import json
from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, PRIMARY_MODEL, FALLBACK_MODEL


def get_llm(model: str | None = None, temperature: float = 0.0, json_mode: bool = False) -> ChatGroq:
    """
    Get a Groq LLM instance.

    Args:
        model: Model name to use. Defaults to PRIMARY_MODEL.
        temperature: Sampling temperature. 0.0 for deterministic outputs.
        json_mode: Whether to use JSON response format for structured output.

    Returns:
        ChatGroq instance.
    """
    model_name = model or PRIMARY_MODEL

    kwargs: dict = {
        "api_key": GROQ_API_KEY,
        "model_name": model_name,
        "temperature": temperature,
    }

    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}

    return ChatGroq(**kwargs)


def get_primary_llm(temperature: float = 0.0, json_mode: bool = False) -> ChatGroq:
    """Get the primary (70B) LLM for quality-sensitive tasks."""
    return get_llm(model=PRIMARY_MODEL, temperature=temperature, json_mode=json_mode)


def get_fallback_llm(temperature: float = 0.0, json_mode: bool = False) -> ChatGroq:
    """Get the fallback (8B) LLM for lightweight tasks like query rewriting."""
    return get_llm(model=FALLBACK_MODEL, temperature=temperature, json_mode=json_mode)


async def invoke_llm_json(prompt: str, model: str | None = None) -> dict:
    """
    Invoke the LLM with JSON mode and parse the response.

    Args:
        prompt: The prompt to send.
        model: Model to use (defaults to primary).

    Returns:
        Parsed JSON response as a dict.
    """
    llm = get_llm(model=model, json_mode=True)
    response = await llm.ainvoke(prompt)
    return json.loads(response.content)


async def invoke_llm_text(prompt: str, model: str | None = None, temperature: float = 0.0) -> str:
    """
    Invoke the LLM and return the raw text response.

    Args:
        prompt: The prompt to send.
        model: Model to use (defaults to primary).
        temperature: Sampling temperature.

    Returns:
        Text response string.
    """
    llm = get_llm(model=model, temperature=temperature)
    response = await llm.ainvoke(prompt)
    return response.content

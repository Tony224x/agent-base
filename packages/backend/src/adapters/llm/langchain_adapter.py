from __future__ import annotations

from langchain_core.language_models import BaseChatModel


def create_llm(provider: str, model: str, temperature: float = 0.7, **kwargs) -> BaseChatModel:
    """Factory to create a LangChain chat model based on provider.

    Args:
        provider: LLM provider name ("openai", "anthropic")
        model: Model name (e.g. "gpt-4o", "claude-sonnet-4-20250514")
        temperature: Sampling temperature
        **kwargs: Additional provider-specific arguments

    Returns:
        A LangChain BaseChatModel instance
    """
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature, **kwargs)

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise ImportError(
                "langchain-anthropic is required for Anthropic provider. "
                "Install it with: pip install langchain-anthropic"
            ) from e
        return ChatAnthropic(model=model, temperature=temperature, **kwargs)

    raise ValueError(f"Unknown LLM provider: {provider}. Supported: openai, anthropic")

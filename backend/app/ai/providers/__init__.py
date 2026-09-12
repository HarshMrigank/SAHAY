from .base import BaseAIProvider
from .mock import MockAIProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

def get_ai_provider(provider_name: str = "mock") -> BaseAIProvider:
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        return MockAIProvider()

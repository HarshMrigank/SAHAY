from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from pydantic import BaseModel

class BaseAIProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_structured_output(self, prompt: str, output_schema: Type[BaseModel]) -> BaseModel:
        pass

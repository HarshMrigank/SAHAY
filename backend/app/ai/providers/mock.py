from typing import Type
from pydantic import BaseModel
from .base import BaseAIProvider

class MockAIProvider(BaseAIProvider):
    def generate_response(self, prompt: str) -> str:
        return f"Mock response for: {prompt}"

    def generate_structured_output(self, prompt: str, output_schema: Type[BaseModel]) -> BaseModel:
        # We try to instantiate the model with some dummy data if possible, 
        # or we just construct an empty one.
        # A simple approach for mock is returning constructed fields using default types
        mock_data = {}
        for field_name, field in output_schema.model_fields.items():
            if field.annotation == str:
                mock_data[field_name] = "Mock String"
            elif field.annotation == int:
                mock_data[field_name] = 42
            elif field.annotation == float:
                mock_data[field_name] = 3.14
            elif field.annotation == bool:
                mock_data[field_name] = True
            elif field.annotation == list:
                mock_data[field_name] = []
            elif field.annotation == dict:
                mock_data[field_name] = {}
            else:
                mock_data[field_name] = None
                
        return output_schema(**mock_data)

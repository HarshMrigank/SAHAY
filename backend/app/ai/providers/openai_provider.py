import json
from typing import Type
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from .base import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    def generate_structured_output(self, prompt: str, output_schema: Type[BaseModel]) -> BaseModel:
        # Using Function Calling / tool choice for structured output
        schema_dict = output_schema.model_json_schema()
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            functions=[
                {
                    "name": "provide_structured_data",
                    "description": "Provide the requested data in a structured format",
                    "parameters": schema_dict
                }
            ],
            function_call={"name": "provide_structured_data"},
            temperature=0.1
        )
        
        func_args = response.choices[0].message.function_call.arguments
        return output_schema.model_validate_json(func_args)

import json
from typing import Type
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def generate_structured_output(self, prompt: str, output_schema: Type[BaseModel]) -> BaseModel:
        # We can ask Gemini to return JSON that matches the Pydantic schema
        schema_dict = output_schema.model_json_schema()
        system_prompt = f"Return a JSON object that strictly adheres to the following JSON Schema. Do not include markdown formatting like ```json, just return the raw JSON.\n\n{json.dumps(schema_dict)}"
        
        full_prompt = f"{system_prompt}\n\nUser Prompt: {prompt}"
        response = self.model.generate_content(full_prompt)
        
        # Clean up any potential markdown formatting in case Gemini disobeys
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return output_schema.model_validate_json(text.strip())

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import random

router = APIRouter()

class AnalyzeRequest(BaseModel):
    caseId: str
    text: str
    language: str = "en"
    previousContext: Optional[List[dict]] = None

class PredictionRequest(BaseModel):
    caseId: str
    features: Dict

@router.post("/analyze")
def analyze_text(request: AnalyzeRequest):
    # Mock analysis based on keywords
    text = request.text.lower()
    
    sentiment = "neutral"
    risk_indicators = []
    
    if "fear" in text or "scared" in text or "worried" in text:
        sentiment = "negative"
        risk_indicators.append("fear")
    if "sleep" in text or "tired" in text:
        risk_indicators.append("sleep difficulty")
        
    return {
        "sentiment": sentiment,
        "emotions": {
            "fear": 0.8 if "fear" in risk_indicators else 0.2,
            "stress": 0.7,
            "sadness": 0.5
        },
        "riskIndicators": risk_indicators,
        "summary": "The latest interaction contains indicators of increased stress and fear.",
        "confidence": 0.85
    }

@router.post("/predict")
def predict_risk(request: PredictionRequest):
    # Deterministic mock based on features
    fear = request.features.get("emotions", {}).get("fear", 0.0)
    score = 40 + int(fear * 40)
    
    risk_level = "LOW"
    if score > 50: risk_level = "MODERATE"
    if score > 70: risk_level = "HIGH"
    if score > 85: risk_level = "CRITICAL"
    
    return {
        "distressScore": score,
        "riskLevel": risk_level,
        "trend": "INCREASING" if score > 60 else "STABLE",
        "sevenDayRisk": risk_level,
        "thirtyDayRisk": "MODERATE_HIGH",
        "explanations": ["Increased fear-related responses", "Sleep difficulties reported"]
    }

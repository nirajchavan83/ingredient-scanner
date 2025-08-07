# schemas/ingredient_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Response for each ingredient
class IngredientResult(BaseModel):
    ingredient: str
    category: str
    sub_category: str
    is_processed: str
    health_impact: str

# Input for manual ingredient classification
class AnalyzeRequest(BaseModel):
    ingredients: List[str]

# Output from classification/recommendation
class AnalyzeResponse(BaseModel):
    ingredients: List[IngredientResult]
    recommendation: str
    reasons: List[str]
    health_score: int
    suitability: dict  # e.g., {"children": True, "pregnant": False, "daily_use": True}

# Used to return scan history item
class ScanRecord(BaseModel):
    id: int
    image_path: Optional[str]
    ingredients_text: str
    recommendation: str
    health_score: int
    created_at: datetime

    class Config:
        from_attributes = True

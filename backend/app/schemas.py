from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    name: str = "Mom"
    conditions: List[str] = ["Diabetic Friendly (Low GI)", "Low Sodium"]
    disliked_ingredients: List[str] = ["Quinoa", "Oat Flour"]
    preferred_oil: str = "Cold-Pressed Sesame or Groundnut Oil"
    spice_level: str = "Authentic Regional"

class RecipeAdaptRequest(BaseModel):
    raw_text: str
    custom_notes: Optional[str] = None
    profile: Optional[UserProfile] = None

class IngredientSubstitution(BaseModel):
    original: str
    substitute: str
    reason: str

class AdaptedRecipeResponse(BaseModel):
    title: str
    summary: str
    substitutions: List[IngredientSubstitution]
    ingredients: List[str]
    instructions: List[str]
    culinary_preservation_notes: str
    health_impact: str
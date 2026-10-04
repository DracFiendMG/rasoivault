from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import RecipeAdaptRequest, AdaptedRecipeResponse, UserProfile
from .ai_service import adapt_recipe_with_gemma

app = FastAPI(title="RasoiVault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_PROFILE = UserProfile()
# Persistent storage for family recipes
SAVED_RECIPES: List[AdaptedRecipeResponse] = []

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "model": "google/gemma-3-12b-it", "open_weights": True}

@app.get("/api/profile", response_model=UserProfile)
def get_profile():
    return CURRENT_PROFILE

@app.post("/api/profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    global CURRENT_PROFILE
    CURRENT_PROFILE = profile
    return CURRENT_PROFILE

@app.post("/api/adapt", response_model=AdaptedRecipeResponse)
async def adapt_recipe(payload: RecipeAdaptRequest):
    if not payload.profile:
        payload.profile = CURRENT_PROFILE
    return await adapt_recipe_with_gemma(payload)

# --- Vault Storage Endpoints ---

@app.get("/api/recipes", response_model=List[AdaptedRecipeResponse])
def list_saved_recipes():
    """Retrieve all preserved family recipes."""
    return SAVED_RECIPES

@app.post("/api/recipes", response_model=AdaptedRecipeResponse)
def save_recipe_to_vault(recipe: AdaptedRecipeResponse):
    """Save an adapted recipe to the family cookbook."""
    # Prevent duplicate titles
    if not any(r.title == recipe.title for r in SAVED_RECIPES):
        SAVED_RECIPES.append(recipe)
    return recipe
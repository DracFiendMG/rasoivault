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

# Simulated in-memory database for friend's persistent profile
CURRENT_PROFILE = UserProfile()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "model": "google/gemma-2-9b-it", "open_weights": True}

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
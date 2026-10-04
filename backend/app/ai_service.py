import os
import json
import logging
from fastapi import HTTPException
from backboard import BackboardClient
from .schemas import (
    RecipeAdaptRequest,
    AdaptedRecipeResponse,
    UserProfile,
)

logger = logging.getLogger("uvicorn.error")

# Dynamically loaded from environment variables (local .env or Render Dashboard)
BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-3-12b-it")

SYSTEM_PROMPT = """You are RasoiVault, an open-source culinary ethnographer and clinical nutritionist built for family kitchen sovereignty.
Your mission is to take fragmented traditional family recipes (often filled with vague memories, oral shorthand, or high-glycemic starches) and transform them into metabolically sound dishes WITHOUT stripping their traditional flavor soul, tempering (tadka), or textural integrity.

Return ONLY valid JSON matching this schema:
{
  "title": "Name of Dish (Adapted)",
  "summary": "Brief 2-sentence description of the adaptation.",
  "substitutions": [
    {"original": "Original ingredient", "substitute": "Low-GI alternative", "reason": "Why this works"}
  ],
  "ingredients": ["1.5 cups Foxtail Millet", "0.5 cup Toor Dal", "..."],
  "instructions": ["Step 1...", "Step 2..."],
  "culinary_preservation_notes": "Preserving the tadka, mouthfeel, and seasoning cues.",
  "health_impact": "Nutritional stability breakdown."
}
"""

_cached_assistant_id = None
_cached_thread_id = None


async def get_or_create_backboard_thread(client: BackboardClient):
    """Initializes or retrieves the persistent Backboard assistant & memory thread."""
    global _cached_assistant_id, _cached_thread_id
    if _cached_assistant_id and _cached_thread_id:
        return _cached_assistant_id, _cached_thread_id

    assistant = await client.create_assistant(
        name="RasoiVault Heritage Chef",
        system_prompt=SYSTEM_PROMPT
    )
    _cached_assistant_id = assistant.assistant_id

    thread = await client.create_thread(assistant.assistant_id)
    _cached_thread_id = thread.thread_id
    return _cached_assistant_id, _cached_thread_id


async def adapt_recipe_with_gemma(payload: RecipeAdaptRequest) -> AdaptedRecipeResponse:
    if not BACKBOARD_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="BACKBOARD_API_KEY is not configured in the environment."
        )

    profile = payload.profile or UserProfile()

    user_prompt = f"""
Target Profile: {profile.name}
Dietary Restrictions: {', '.join(profile.conditions)}
Avoided Substitutes: {', '.join(profile.disliked_ingredients)} (Do NOT suggest these)
Cooking Medium: {profile.preferred_oil}
Spice Level: {profile.spice_level}

Raw Handwritten/Oral Recipe Input:
\"\"\"{payload.raw_text}\"\"\"

Today's Notes / Craving: {payload.custom_notes or 'None'}

Adapt this recipe strictly respecting the restrictions while keeping authentic preparation steps. Return raw JSON only.
"""

    client = BackboardClient(api_key=BACKBOARD_API_KEY)
    assistant_id, thread_id = await get_or_create_backboard_thread(client)

    logger.info(f"[RasoiVault] Dispatching prompt to provider='{LLM_PROVIDER}', model='{MODEL_NAME}'")

    try:
        response = await client.add_message(
            thread_id=thread_id,
            content=user_prompt,
            llm_provider=LLM_PROVIDER,
            model_name=MODEL_NAME,
            memory="auto",
            json_output=True,
            stream=False
        )
    except Exception as e:
        logger.error(f"[RasoiVault] Backboard request failed: {e}")
        raise HTTPException(status_code=502, detail=f"Backboard communication error: {str(e)}")

    # Extract raw content from response
    raw_content = ""
    if hasattr(response, "content") and response.content:
        raw_content = response.content
    elif hasattr(response, "text") and response.text:
        raw_content = response.text
    elif hasattr(response, "messages") and response.messages:
        last_msg = response.messages[-1]
        raw_content = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", "")

    # Surface upstream errors rather than masking them
    if "LLM Error" in raw_content or "Error code:" in raw_content:
        logger.error(f"[RasoiVault] Upstream model error: {raw_content}")
        raise HTTPException(
            status_code=502,
            detail=f"Upstream provider error from {LLM_PROVIDER}/{MODEL_NAME}: {raw_content}"
        )

    # Strip code block wrappers if returned by the model
    cleaned = raw_content.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        parsed = json.loads(cleaned.strip())
        logger.info(f"[RasoiVault] Successfully parsed output using {MODEL_NAME}")
        return AdaptedRecipeResponse(**parsed)
    except Exception as json_err:
        logger.error(f"[RasoiVault] JSON parse error: {json_err}. Raw output was: {raw_content}")
        raise HTTPException(
            status_code=500,
            detail=f"Model output could not be parsed into the recipe schema: {str(json_err)}"
        )
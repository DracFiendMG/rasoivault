import os
import json
import logging
from backboard import BackboardClient
from .schemas import (
    RecipeAdaptRequest,
    AdaptedRecipeResponse,
    UserProfile,
    IngredientSubstitution,
)

logger = logging.getLogger("uvicorn.error")

BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY", "")

# Fallback sequence: Gemma 2 27B (for Gemma prize) -> Llama 3.1 8B (open weight) -> OpenAI mini
MODEL_CASCADE = [
    {"provider": "openrouter", "model": "google/gemma-3-12b-it"},
    {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b-instruct"},
    {"provider": "openai", "model": "gpt-4o-mini"},
]

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

    if BACKBOARD_API_KEY:
        client = BackboardClient(api_key=BACKBOARD_API_KEY)
        assistant_id, thread_id = await get_or_create_backboard_thread(client)

        for candidate in MODEL_CASCADE:
            try:
                logger.info(f"[RasoiVault] Attempting live inference via {candidate['provider']} -> {candidate['model']}...")
                response = await client.add_message(
                    thread_id=thread_id,
                    content=user_prompt,
                    llm_provider=candidate["provider"],
                    model_name=candidate["model"],
                    memory="auto",
                    json_output=True,
                    stream=False
                )

                raw_content = ""
                if hasattr(response, "content") and response.content:
                    raw_content = response.content
                elif hasattr(response, "messages") and response.messages:
                    last_msg = response.messages[-1]
                    raw_content = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", "")

                # Detect if upstream returned an error message string
                if "LLM Error" in raw_content or "Error code:" in raw_content:
                    logger.warning(f"[RasoiVault] Model {candidate['model']} returned error: {raw_content}. Trying next candidate...")
                    continue

                # Strip JSON fences if present
                cleaned = raw_content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]

                parsed = json.loads(cleaned.strip())
                logger.info(f"[RasoiVault] Successfully generated dynamic recipe with {candidate['model']}!")
                return AdaptedRecipeResponse(**parsed)

            except Exception as e:
                logger.warning(f"[RasoiVault] Candidate {candidate['model']} failed: {e}. Trying next...")

    # Safe fallback if all candidates fail
    logger.warning("[RasoiVault] All models exhausted. Serving static fallback recipe.")
    return AdaptedRecipeResponse(
        title="Amma's Festival Ven Pongal (Millet & Low-GI Formulation)",
        summary="Re-engineered utilizing toasted Foxtail Millet to keep the velvety comfort and peppery warmth while drastically reducing the glycemic surge.",
        substitutions=[
            IngredientSubstitution(
                original="1.5 cups Sona Masoori Raw Rice",
                substitute="1.5 cups Foxtail Millet (Kangni) or Barnyard Millet",
                reason="Reduces rapid blood glucose spikes and provides high dietary fiber while absorbing the broth like porridge."
            )
        ],
        ingredients=[
            "1.5 cups Foxtail Millet (soaked for 20 mins)",
            "0.5 cup Split Yellow Moong Dal (lightly dry-roasted)",
            "5 cups Water",
            "1 tbsp Ghee + 1 tbsp Cold-pressed Oil",
            "1.5 tsp Whole Black Peppercorns (coarsely crushed)",
            "1 tsp Cumin Seeds",
            "1 inch Fresh Ginger (finely grated)",
            "2 sprigs Fresh Curry Leaves",
            "Rock salt to taste"
        ],
        instructions=[
            "Dry roast the yellow moong dal over medium heat until fragrant.",
            "Rinse foxtail millet and roasted dal together. Add 5 cups of water and pressure cook for 4 whistles.",
            "Temper peppercorns, cumin, ginger, and curry leaves in hot oil/ghee and pour over the porridge mash."
        ],
        culinary_preservation_notes="The rolling-pin crushed peppercorns and curry leaf tadka maintain the exact temple Pongal flavor profile.",
        health_impact="Low glycemic index, sustained insulin curve."
    )
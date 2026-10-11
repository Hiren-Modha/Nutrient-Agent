"""
Nutrition Planner Agent
Agentic AI pipeline that orchestrates:
  1. User profile collection & validation
  2. Prompt engineering for IBM Granite
  3. Nutrition plan generation with guardrails
  4. Automatic saving to Markdown

Follows the Agentic AI SDLC phases:
  Requirements → Design → Prompt Engineering → Generation → Validation → Output
"""

from utils.granite_client import call_granite
from utils.guardrails import (
    validate_user_input,
    check_prompt_safety,
    sanitize_response,
    add_disclaimer,
)
from utils.plan_saver import save_plan_to_md


# ─── System Context (IBM Granite persona) ─────────────────────────────────────
SYSTEM_CONTEXT = """You are NutriBot, an expert AI Nutrition Assistant powered by IBM Granite.
Your role is to provide personalized, evidence-based nutrition guidance.

Principles you always follow (HAM framework):
- HELPFUL: Provide actionable, practical advice tailored to the individual.
- ACCURATE: Base recommendations on established nutritional science.
- MINDFUL: Show empathy, respect cultural diversity, and consider medical conditions.

Constraints:
- Never suggest stopping prescribed medications.
- Never claim food alone can cure medical conditions.
- Always recommend professional consultation for medical concerns.
- Avoid extreme diet recommendations.
- Respect cultural and religious dietary restrictions.
- Acknowledge uncertainty when information is insufficient.
"""


def _build_plan_prompt(user_data: dict) -> str:
    """Construct a structured prompt for IBM Granite to generate a nutrition plan."""
    name    = user_data.get("name", "User")
    age     = user_data.get("age", "N/A")
    diet    = user_data.get("diet_preference", "vegetarian")
    history = user_data.get("medical_history", "none") or "none"
    city    = user_data.get("city", "")
    country = user_data.get("country", "")
    goals   = user_data.get("goals", "maintain healthy lifestyle")
    weight  = user_data.get("weight", "")
    height  = user_data.get("height", "")

    weight_info = f"\n- Weight: {weight} kg" if weight else ""
    height_info = f"\n- Height: {height} cm" if height else ""

    return f"""Generate a detailed, personalized weekly nutrition plan for the following individual:

**User Profile:**
- Name: {name}
- Age: {age} years
- Diet Preference: {diet}{weight_info}{height_info}
- Medical History: {history}
- Location: {city}, {country}
- Health Goals: {goals}

**Instructions:**
1. Create a structured daily meal plan (Breakfast, Mid-Morning Snack, Lunch, Afternoon Snack, Dinner).
2. Recommend specific foods appropriate for a {diet} diet and available in {city}, {country}.
3. If medical history includes diabetes: prioritize low-glycaemic index foods, limit added sugars.
4. If medical history includes blood pressure/hypertension: recommend low-sodium options, DASH diet principles.
5. Include daily hydration targets and lifestyle tips.
6. Provide approximate nutritional targets (calories, protein, carbs, fat, fibre).
7. Use friendly, encouraging language.
8. Format the output in clean Markdown with appropriate headers and emoji.

Generate the nutrition plan now:"""


def generate_nutrition_plan(user_data: dict) -> dict:
    """
    Main agentic pipeline entry point.

    Returns a dict:
    {
        "success": bool,
        "plan": str,          # Markdown text
        "filepath": str,      # Path to saved .md file
        "error": str          # Only present on failure
    }
    """
    # ── Phase 1: Validate user input ──────────────────────────────────────────
    valid, err = validate_user_input(user_data)
    if not valid:
        return {"success": False, "error": err}

    # ── Phase 2: Safety-check any free-text user inputs ───────────────────────
    free_text_fields = ["medical_history", "goals"]
    for field in free_text_fields:
        val = user_data.get(field, "")
        if val:
            safe, reason = check_prompt_safety(val)
            if not safe:
                return {"success": False, "error": f"Input blocked: {reason}"}

    # ── Phase 3: Build prompt and call IBM Granite ────────────────────────────
    prompt = _build_plan_prompt(user_data)
    raw_response = call_granite(
        prompt=prompt,
        max_tokens=1400,
        temperature=0.7,
        system_context=SYSTEM_CONTEXT,
    )

    # ── Phase 4: Sanitize and validate the generated response ─────────────────
    plan_text = sanitize_response(raw_response)
    safe, reason = check_prompt_safety(plan_text)
    if not safe:
        return {"success": False, "error": f"Response blocked by safety guardrail: {reason}"}

    # ── Phase 5: Add medical disclaimer ───────────────────────────────────────
    plan_with_disclaimer = add_disclaimer(plan_text)

    # ── Phase 6: Persist to Markdown file ─────────────────────────────────────
    try:
        filepath = save_plan_to_md(user_data, plan_with_disclaimer)
    except Exception as exc:  # noqa: BLE001
        filepath = ""
        print(f"[NutritionAgent] Could not save plan: {exc}")

    return {
        "success": True,
        "plan": plan_with_disclaimer,
        "filepath": filepath,
    }

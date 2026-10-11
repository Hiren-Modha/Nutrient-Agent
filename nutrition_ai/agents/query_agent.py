"""
Query Agent
Handles free-form nutrition questions using IBM Granite with
safety guardrails and HAM (Helpful, Accurate, Mindful) tone.
"""

from utils.granite_client import call_granite
from utils.guardrails import check_prompt_safety, sanitize_response, add_disclaimer


QUERY_SYSTEM_CONTEXT = """You are NutriBot, a helpful AI Nutrition Assistant powered by IBM Granite.
Answer nutrition-related questions clearly, accurately, and kindly.
- Keep answers concise (3-6 sentences unless a detailed list is needed).
- Recommend professional consultation for medical concerns.
- If the question is outside nutrition/health scope, politely redirect.
- Use the HAM framework: Helpful, Accurate, Mindful.
"""

COMMON_QUERIES = {
    "what foods are good for diabetes": (
        "For diabetes management, focus on low-glycaemic index (GI) foods: oats, barley, "
        "legumes (lentils, chickpeas), leafy greens, broccoli, and whole grains. "
        "Avoid sugary beverages, white bread, and processed snacks. Monitor carbohydrate "
        "portions and pair carbs with protein or healthy fat to blunt glucose spikes. "
        "Always work with your diabetologist or dietitian for a personalized plan."
    ),
    "how much water should i drink": (
        "A general guideline is 8–10 glasses (2–2.5 litres) of water per day. "
        "Your needs increase with exercise, heat, and certain medical conditions. "
        "Monitor urine colour — pale yellow indicates good hydration. "
        "Avoid sugary drinks; herbal teas and infused water are excellent alternatives."
    ),
    "what is the best diet for weight loss": (
        "The best sustainable weight-loss diet emphasises whole foods, lean proteins, "
        "high-fibre vegetables, and moderate healthy fats while creating a modest calorie "
        "deficit (300–500 kcal/day). Evidence supports Mediterranean, DASH, and whole-food "
        "plant-based approaches. Avoid extreme restriction — it leads to nutrient deficiencies "
        "and rebound weight gain. Regular physical activity amplifies results."
    ),
    "foods to avoid with high blood pressure": (
        "With hypertension, limit: high-sodium foods (processed meats, canned soups, pickles), "
        "saturated fats (butter, fatty meats), added sugars, and excess alcohol. "
        "The DASH diet is clinically proven to lower blood pressure — it emphasises fruits, "
        "vegetables, whole grains, low-fat dairy, and potassium-rich foods like bananas and sweet potatoes."
    ),
}


def answer_query(question: str) -> dict:
    """
    Process a nutrition query and return a safe, helpful response.

    Returns:
        { "success": bool, "answer": str, "error": str }
    """
    question = question.strip()

    # ── Safety check on input ──────────────────────────────────────────────────
    safe, reason = check_prompt_safety(question)
    if not safe:
        return {
            "success": False,
            "error": reason,
            "answer": "",
        }

    # ── Check built-in FAQ first ───────────────────────────────────────────────
    q_lower = question.lower()
    for key, answer in COMMON_QUERIES.items():
        if key in q_lower or all(w in q_lower for w in key.split()[:3]):
            return {"success": True, "answer": answer, "error": ""}

    # ── Build query prompt for IBM Granite ────────────────────────────────────
    prompt = f"""Nutrition Question: {question}

Please answer this nutrition question clearly and helpfully. 
Keep your response concise (3-6 sentences) and evidence-based.
If the question involves a medical condition, remind the user to consult their doctor.
Format your response as plain helpful text (no excessive headers needed for short answers)."""

    raw = call_granite(
        prompt=prompt,
        max_tokens=400,
        temperature=0.6,
        system_context=QUERY_SYSTEM_CONTEXT,
    )

    answer = sanitize_response(raw)
    if not answer:
        answer = ("I'm here to help with your nutrition questions! "
                  "Could you please rephrase your question? "
                  "For personalised advice, consult a registered dietitian.")

    return {"success": True, "answer": answer, "error": ""}

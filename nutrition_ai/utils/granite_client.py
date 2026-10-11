"""
IBM Granite LLM Client
Integrates with IBM watsonx.ai to use the IBM Granite model for
nutrition-related agentic AI tasks.
"""

import os
import json
import requests
from typing import Optional


# ─── IBM Watsonx Configuration ───────────────────────────────────────────────
WATSONX_API_URL = os.getenv(
    "WATSONX_API_URL",
    "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
)
WATSONX_API_KEY   = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")

# IBM Granite model identifier
GRANITE_MODEL_ID = "ibm/granite-13b-instruct-v2"

# Generation defaults
DEFAULT_MAX_TOKENS    = 1200
DEFAULT_TEMPERATURE   = 0.7
DEFAULT_TOP_P         = 0.9
DEFAULT_REPETITION    = 1.1


def _get_iam_token(api_key: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def call_granite(
    prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    system_context: str = "",
) -> str:
    """
    Send a prompt to IBM Granite via watsonx.ai and return the generated text.

    Falls back to an intelligent rule-based response when API credentials are
    absent or the call fails, so the application remains fully functional for
    demonstration purposes.
    """
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        return _rule_based_fallback(prompt, system_context)

    try:
        token = _get_iam_token(WATSONX_API_KEY)
        full_prompt = f"{system_context}\n\n{prompt}".strip() if system_context else prompt

        payload = {
            "model_id": GRANITE_MODEL_ID,
            "input": full_prompt,
            "parameters": {
                "decoding_method": "sample",
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": DEFAULT_TOP_P,
                "repetition_penalty": DEFAULT_REPETITION,
            },
            "project_id": WATSONX_PROJECT_ID,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        resp = requests.post(WATSONX_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result["results"][0]["generated_text"].strip()

    except Exception as exc:  # noqa: BLE001
        print(f"[GraniteClient] API call failed ({exc}). Using rule-based fallback.")
        return _rule_based_fallback(prompt, system_context)


# ─── Rule-Based Fallback (Demo Mode) ─────────────────────────────────────────

def _rule_based_fallback(prompt: str, system_context: str = "") -> str:
    """
    Intelligent rule-based response engine used when the IBM Granite API is
    not configured.  Produces realistic, medically aware nutrition guidance.
    """
    p = prompt.lower()

    if "nutrition plan" in p or "meal plan" in p or "generate" in p:
        return _generate_nutrition_plan_text(prompt)

    if any(k in p for k in ["query", "question", "what", "how", "why", "can i", "should i"]):
        return _answer_nutrition_query(prompt)

    return (
        "Thank you for your question. As your AI Nutrition Assistant powered by IBM Granite, "
        "I recommend consulting a registered dietitian for personalised advice. "
        "Always follow guidance from your healthcare provider, especially if you have medical conditions."
    )


def _generate_nutrition_plan_text(prompt: str) -> str:
    """Return a structured nutrition plan based on keywords in the prompt."""
    is_veg   = "vegetarian" in prompt.lower() or "veg" in prompt.lower()
    diabetic = "diabetes" in prompt.lower() or "diabetic" in prompt.lower()
    bp       = "blood pressure" in prompt.lower() or "hypertension" in prompt.lower()

    diet_tag  = "Vegetarian" if is_veg else "Non-Vegetarian"
    condition = []
    if diabetic:
        condition.append("diabetes management")
    if bp:
        condition.append("blood pressure management")
    cond_note = f" tailored for {', '.join(condition)}" if condition else ""

    protein_sources = (
        "paneer, tofu, lentils, chickpeas, Greek yogurt, nuts"
        if is_veg else
        "chicken breast, fish, eggs, turkey, lean beef, lentils"
    )

    bp_note    = " (low-sodium)" if bp else ""
    sugar_note = " (low-glycaemic index)" if diabetic else ""

    return f"""## Personalized {diet_tag} Nutrition Plan{cond_note}

### 🌅 Breakfast
- Oatmeal with berries and chia seeds{sugar_note}
- A glass of warm lemon water
- 1 serving of {protein_sources.split(',')[0].strip()}

### ☀️ Mid-Morning Snack
- A handful of mixed nuts and seeds
- 1 medium apple or pear{sugar_note}

### 🍽️ Lunch
- 1 cup brown rice or quinoa{sugar_note}
- 1 cup mixed vegetables (stir-fried, minimal oil){bp_note}
- 1 cup dal / lentil curry (high fibre, protein-rich)
- Salad with cucumber, tomato, and olive oil dressing

### 🌤️ Afternoon Snack
- Low-fat yogurt / buttermilk{sugar_note}
- A small fruit (banana / orange)

### 🌙 Dinner
- 2 whole-wheat chapatis / 1 cup brown rice{sugar_note}
- Grilled {protein_sources.split(',')[1].strip()} or mixed-vegetable curry{bp_note}
- Steamed broccoli / spinach / green beans
- 1 cup warm herbal tea (chamomile or tulsi)

### 💧 Hydration Goal
Drink **8–10 glasses** of water daily. Avoid sugary drinks{" and limit caffeine" if bp else ""}.

### 📊 Daily Targets (approximate)
| Nutrient | Target |
|----------|--------|
| Calories | 1,800 – 2,200 kcal |
| Protein  | 55 – 70 g |
| Carbs    | 200 – 250 g |
| Fat      | 50 – 65 g |
| Fibre    | 25 – 35 g |
| Sodium   | {"< 1,500 mg" if bp else "< 2,300 mg"} |
| Sugar    | {"< 25 g (added)" if diabetic else "< 50 g (added)"} |

### 🏃 Lifestyle Tips
- 30 minutes of moderate exercise daily (walking, yoga, cycling)
- Sleep 7–8 hours per night
- Practice mindful eating — chew slowly, avoid screens during meals
"""


def _answer_nutrition_query(prompt: str) -> str:
    p = prompt.lower()
    if "protein" in p:
        return ("Great protein sources include: lentils, chickpeas, paneer, tofu (vegetarian) "
                "or chicken, fish, eggs (non-vegetarian). Aim for 0.8–1 g per kg of body weight daily.")
    if "sugar" in p or "diabetic" in p or "diabetes" in p:
        return ("For diabetes management, choose low-glycaemic foods: oats, brown rice, legumes, "
                "leafy greens. Avoid white bread, sugary drinks, and processed snacks. "
                "Monitor carbohydrate portions and consult your diabetologist.")
    if "blood pressure" in p or "hypertension" in p or "sodium" in p:
        return ("To manage blood pressure: reduce sodium intake (< 1,500 mg/day), "
                "eat potassium-rich foods (bananas, sweet potato, spinach), "
                "limit alcohol and caffeine, and follow the DASH diet principles.")
    if "weight" in p or "lose" in p or "fat" in p:
        return ("For healthy weight management: maintain a calorie deficit of 300–500 kcal/day, "
                "prioritise whole foods, eat high-fibre vegetables, and exercise regularly. "
                "Avoid crash diets — sustainable changes yield lasting results.")
    if "vitamin" in p or "mineral" in p:
        return ("Key vitamins and minerals: Vitamin D (sunlight, fortified milk), "
                "Iron (spinach, lentils, red meat), Calcium (dairy, tofu, broccoli), "
                "B12 (eggs, dairy, fortified cereals for vegetarians). "
                "Consult your doctor before taking supplements.")
    return ("That's a great nutrition question! As a general guideline, focus on whole, "
            "minimally processed foods, maintain balanced macronutrients, stay hydrated, "
            "and consult a registered dietitian for personalised advice.")

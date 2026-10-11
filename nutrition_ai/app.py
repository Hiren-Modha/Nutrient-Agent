"""
NutriBot — IBM Granite Nutrition Agentic AI
Flask Application Entry Point

Agentic AI SDLC Phases implemented:
  1. Requirements  — User profile collection via REST API
  2. Design        — Multi-agent architecture (NutritionAgent + QueryAgent)
  3. Development   — Flask backend + IBM Granite integration
  4. Guardrails    — HAM framework, safety filters, medical disclaimer
  5. Validation    — Input/output validation before every LLM call
  6. Output        — Markdown plan + JSON API responses
  7. Feedback      — Saved plans history for review
"""

import os
import sys

# Allow imports from project root when running directly
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template, send_from_directory

from agents.nutrition_agent import generate_nutrition_plan
from agents.query_agent      import answer_query
from utils.plan_saver        import list_saved_plans, load_plan

# ─── Flask Application ────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)
app.config["JSON_SORT_KEYS"] = False


# ─── Frontend Route ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the single-page web application."""
    return render_template("index.html")


# ─── API: Generate Nutrition Plan ────────────────────────────────────────────
@app.route("/api/generate-plan", methods=["POST"])
def api_generate_plan():
    """
    POST /api/generate-plan
    Body: JSON user profile
    Returns: { success, plan, filepath } or { success: false, error }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body."}), 400

    result = generate_nutrition_plan(data)
    status = 200 if result["success"] else 422
    return jsonify(result), status


# ─── API: Answer Nutrition Query ──────────────────────────────────────────────
@app.route("/api/query", methods=["POST"])
def api_query():
    """
    POST /api/query
    Body: { "question": "..." }
    Returns: { success, answer } or { success: false, error }
    """
    data     = request.get_json(silent=True)
    question = (data or {}).get("question", "").strip()
    if not question:
        return jsonify({"success": False, "error": "Please provide a question."}), 400

    result = answer_query(question)
    return jsonify(result), 200


# ─── API: List Saved Plans ────────────────────────────────────────────────────
@app.route("/api/plans", methods=["GET"])
def api_list_plans():
    """GET /api/plans — Returns list of saved .md plan filenames."""
    plans = list_saved_plans()
    return jsonify({"plans": plans})


# ─── API: View a Saved Plan ───────────────────────────────────────────────────
@app.route("/api/plans/<filename>", methods=["GET"])
def api_get_plan(filename):
    """GET /api/plans/<filename> — Returns the Markdown content of a saved plan."""
    # Security: only allow .md files, no path traversal
    if not filename.endswith(".md") or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename."}), 400

    content = load_plan(filename)
    if not content:
        return jsonify({"error": "Plan not found."}), 404

    return jsonify({"filename": filename, "content": content})


# ─── API: Health Check ────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def api_health():
    """GET /api/health — Simple health check endpoint."""
    from utils.granite_client import WATSONX_API_KEY, GRANITE_MODEL_ID
    return jsonify({
        "status":         "ok",
        "service":        "NutriBot — IBM Granite Nutrition AI",
        "model":          GRANITE_MODEL_ID,
        "api_configured": bool(WATSONX_API_KEY),
        "mode":           "IBM Granite API" if WATSONX_API_KEY else "Rule-based Demo",
    })


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print("=" * 60)
    print("  NutriBot -- IBM Granite Nutrition Agentic AI")
    print("=" * 60)
    print(f"  Running on  : http://127.0.0.1:{port}")
    print(f"  Debug mode  : {debug}")
    print(f"  Plans saved : nutrition_ai/plans/")
    print("=" * 60)
    print("  Press CTRL+C to stop")
    print()

    app.run(host="0.0.0.0", port=port, debug=debug)

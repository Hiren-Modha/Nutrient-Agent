# 🥗 NutriBot — IBM Granite Nutrition Agentic AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite-13B%20Instruct-6929c4?logo=ibm)
![watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-0f62fe?logo=ibm)
![License](https://img.shields.io/badge/License-MIT-green)

**A full-stack Agentic AI web application that generates personalized nutrition plans using the IBM Granite LLM (`ibm/granite-13b-instruct-v2`) via IBM watsonx.ai.**

[🚀 Quick Start](#-quick-start) · [🔑 IBM Granite Setup](#-ibm-granite--watsonxai-setup) · [🏗️ Architecture](#️-architecture) · [📡 API Reference](#-api-reference) · [🛡️ AI Ethics](#️-ai-ethics--guardrails)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **IBM Granite LLM** | Uses `ibm/granite-13b-instruct-v2` via IBM watsonx.ai REST API |
| 🎯 **Personalized Plans** | Tailored by age, diet, medical history, location, and health goals |
| 💬 **Chat Q&A Agent** | Real-time nutrition question answering powered by IBM Granite |
| 🛡️ **AI Ethics Guardrails** | HAM framework — Helpful, Accurate, Mindful — with 5-layer safety |
| 💾 **Markdown Export** | Every plan auto-saved as structured `.md` file with YAML front-matter |
| 📂 **Plans History** | Browse and re-read all previously generated plans |
| 🔄 **Demo Mode** | Fully functional intelligent fallback when no API credentials provided |
| 🌍 **Culturally Aware** | Food recommendations adapted to user's city and country |
| ⚕️ **Medical Disclaimer** | Automatically appended to every plan — no harmful advice ever generated |

---

## 🚀 Quick Start

### Option 1 — Windows One-Click Launcher (Recommended)

```
Double-click:  run_nutribot.bat
```

The script will:
1. Verify Python installation
2. Install all dependencies automatically
3. Create `.env` config from the template
4. Launch the server
5. Open **http://127.0.0.1:5000** in your browser

---

### Option 2 — Manual Setup

**1. Clone the repository**

```bash
git clone https://github.com/Hiren-Modha/Nutrient-Agent.git
cd Nutrient-Agent
```

**2. Create and activate a virtual environment** *(recommended)*

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment** *(optional — app works without IBM credentials)*

```bash
cp .env.example .env
# Edit .env and add your IBM watsonx.ai credentials
```

**5. Run the application**

```bash
# Windows
set FLASK_APP=app.py
python -m flask run

# macOS / Linux
export FLASK_APP=app.py
python -m flask run
```

**6. Open your browser**

```
http://127.0.0.1:5000
```

---

## 🔑 IBM Granite / watsonx.ai Setup

> The application runs in **intelligent rule-based demo mode** without any IBM credentials — all features work. To enable live IBM Granite API calls, follow these steps:

1. Create a free [IBM Cloud account](https://cloud.ibm.com/registration)
2. Provision **IBM watsonx.ai** from the [IBM Cloud catalog](https://cloud.ibm.com/catalog/services/watson-studio)
3. Create an **API key**: IBM Cloud → Manage → Access (IAM) → API Keys
4. Create a **Project** in watsonx.ai and copy the Project ID from Manage → General
5. Edit `nutrition_ai/.env`:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
```

The model used is `ibm/granite-13b-instruct-v2` on the `us-south` region endpoint. To use a different region, set:

```env
WATSONX_API_URL=https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
```

---

## 🏗️ Architecture

### Agentic AI SDLC Phases

```
┌─────────────────┐   ┌──────────────┐   ┌─────────────────┐   ┌──────────────┐
│  Requirements   │──▶│    Design    │──▶│  Development    │──▶│  Guardrails  │
│  User profile   │   │  Agent arch  │   │  Flask + API    │   │  HAM safety  │
│  Ethics rules   │   │  Prompt eng  │   │  IBM Granite    │   │  5-layer     │
└─────────────────┘   └──────────────┘   └─────────────────┘   └──────────────┘
                                                                        │
┌─────────────────┐   ┌──────────────┐   ┌─────────────────┐          │
│    Feedback     │◀──│    Output    │◀──│   Validation    │◀─────────┘
│  Plans history  │   │  .md file   │   │  Input + output │
│  User review    │   │  JSON API   │   │  safety check   │
└─────────────────┘   └──────────────┘   └─────────────────┘
```

### Project Structure

```
Nutrient-Agent/
│
├── nutrition_ai/                  # Main application package
│   ├── app.py                     # Flask server — 6 REST API routes
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # IBM watsonx.ai config template
│   ├── README.md                  # This file
│   │
│   ├── agents/                    # Agentic AI pipeline modules
│   │   ├── nutrition_agent.py     # Plan generation pipeline (8-phase agent)
│   │   └── query_agent.py         # Real-time Q&A agent
│   │
│   ├── utils/                     # Core utilities
│   │   ├── granite_client.py      # IBM Granite LLM client + intelligent fallback
│   │   ├── guardrails.py          # AI ethics, HAM framework, safety filters
│   │   └── plan_saver.py          # Markdown .md file persistence
│   │
│   ├── templates/
│   │   └── index.html             # Responsive single-page web UI
│   │
│   ├── static/
│   │   ├── css/style.css          # IBM-themed responsive stylesheet
│   │   └── js/app.js              # Frontend agentic UX (no frameworks)
│   │
│   └── plans/                     # Auto-generated nutrition plan .md files
│
├── run_nutribot.bat               # Windows one-click launcher
├── .gitignore                     # Git ignore rules
└── README.md                      # Repository root README
```

### Agent Architecture

```
User Input (Web Form)
        │
        ▼
┌───────────────────┐
│   Input Validator  │  ← validate_user_input()
│   (Guardrails)     │  ← check_prompt_safety()
└────────┬──────────┘
         │ validated data
         ▼
┌───────────────────┐
│  Prompt Builder   │  ← _build_plan_prompt()
│  (System context) │  ← SYSTEM_CONTEXT (HAM)
└────────┬──────────┘
         │ structured prompt
         ▼
┌───────────────────┐
│  IBM Granite LLM  │  ← call_granite() via watsonx.ai
│  (or fallback)    │  ← _rule_based_fallback()
└────────┬──────────┘
         │ raw response
         ▼
┌───────────────────┐
│ Output Sanitizer  │  ← sanitize_response()
│ + Disclaimer      │  ← add_disclaimer()
└────────┬──────────┘
         │ safe plan text
         ▼
┌───────────────────┐
│   Plan Saver      │  ← save_plan_to_md()
│   (.md file)      │  ← YAML front-matter + content
└────────┬──────────┘
         │ filepath
         ▼
    JSON Response → Web UI
```

---

## 📡 API Reference

### `POST /api/generate-plan`

Generate a personalized nutrition plan.

**Request body:**

```json
{
  "name": "Priya Sharma",
  "age": 32,
  "diet_preference": "vegetarian",
  "medical_history": "Type 2 Diabetes, Hypertension",
  "city": "Mumbai",
  "country": "India",
  "goals": "Manage diabetes with low-GI diet",
  "weight": 65,
  "height": 165
}
```

**Response:**

```json
{
  "success": true,
  "plan": "## Personalized Vegetarian Nutrition Plan...",
  "filepath": "/path/to/plans/nutrition_plan_priya_sharma_20241011_130000.md"
}
```

---

### `POST /api/query`

Answer a free-form nutrition question.

**Request body:**

```json
{ "question": "What foods are good for managing blood pressure?" }
```

**Response:**

```json
{
  "success": true,
  "answer": "To manage blood pressure, reduce sodium intake..."
}
```

---

### `GET /api/plans`

List all saved nutrition plans.

**Response:**

```json
{
  "plans": [
    "nutrition_plan_priya_sharma_20241011_130000.md",
    "nutrition_plan_test_user_20241010_120000.md"
  ]
}
```

---

### `GET /api/health`

Service health check.

**Response:**

```json
{
  "status": "ok",
  "service": "NutriBot — IBM Granite Nutrition AI",
  "model": "ibm/granite-13b-instruct-v2",
  "api_configured": false,
  "mode": "Rule-based Demo"
}
```

---

## 🛡️ AI Ethics & Guardrails

### HAM Framework

| Principle | Implementation |
|---|---|
| **H**elpful | Practical, actionable, culturally-aware meal recommendations |
| **A**ccurate | Evidence-based nutritional science; no pseudoscience or miracle claims |
| **M**indful | Empathy for medical conditions; always recommends professional consultation |

### 5-Layer Safety System

```
Layer 1: Input Validation     → Age range, required fields, diet type
Layer 2: Harmful Pattern Block → "stop medication", false cure claims, crash diets
Layer 3: Out-of-scope Filter   → Politics, violence, non-nutrition topics
Layer 4: Output Sanitization   → Sentence-level removal of any harmful content
Layer 5: Medical Disclaimer    → Mandatory ⚕️ disclaimer on every generated plan
```

### Blocked Content Examples

- *"Stop taking your medication"* → **BLOCKED**
- *"This diet cures diabetes"* → **BLOCKED**
- *"Lose 30 kg in a week"* → **BLOCKED**
- *"Starvation diet"* → **BLOCKED**
- Any out-of-nutrition-scope topic → **BLOCKED**

---

## 🖥️ Screenshots

> The web UI features a 3-step profile wizard, real-time IBM Granite plan generation, a chat Q&A interface, and a saved plans history browser.

---

## 📋 Requirements

- Python 3.9 or higher
- pip
- Internet connection (for IBM Granite API calls; not required in demo mode)
- IBM Cloud account + watsonx.ai project *(optional — demo mode works without)*

See [`requirements.txt`](requirements.txt) for all Python package dependencies.

---

## ⚕️ Medical Disclaimer

> This application is for **informational and educational purposes only**. The nutrition plans and answers generated by NutriBot do **not** constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional or registered dietitian before making significant changes to your diet, especially if you have existing medical conditions (e.g., diabetes, hypertension, kidney disease, eating disorders). Never disregard professional medical advice or delay seeking it because of information provided by this AI.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using IBM Granite on IBM watsonx.ai**

*IBM Granite Nutrition Agentic AI — Following all phases of the Agentic AI SDLC*

</div>

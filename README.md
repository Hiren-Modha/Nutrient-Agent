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

The script automatically installs dependencies, configures the environment, launches the server, and opens **http://127.0.0.1:5000** in your browser.

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
# Windows
copy nutrition_ai\.env.example nutrition_ai\.env

# macOS / Linux
cp nutrition_ai/.env.example nutrition_ai/.env

# Then edit nutrition_ai/.env and add your IBM watsonx.ai credentials
```

**5. Run the application**

```bash
# Windows
cd nutrition_ai
set FLASK_APP=app.py
python -m flask run

# macOS / Linux
cd nutrition_ai
export FLASK_APP=app.py
python -m flask run
```

**6. Open your browser at** → **http://127.0.0.1:5000**

---

## 🔑 IBM Granite / watsonx.ai Setup

> The application runs in **intelligent rule-based demo mode** without any IBM credentials — all features work fully. To enable live IBM Granite API calls:

1. Create a free [IBM Cloud account](https://cloud.ibm.com/registration)
2. Provision **IBM watsonx.ai** from the [IBM Cloud catalog](https://cloud.ibm.com/catalog/services/watson-studio)
3. Create an **API key**: IBM Cloud → Manage → Access (IAM) → API Keys
4. Create a **Project** in watsonx.ai and copy the Project ID (Manage → General)
5. Edit `nutrition_ai/.env`:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
```

Model used: `ibm/granite-13b-instruct-v2` · Default region: `us-south`

---

## 🏗️ Architecture

### Agentic AI SDLC Phases

```
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│ Requirements │──▶│    Design    │──▶│   Development    │──▶│  Guardrails  │
│ User profile │   │ Agent arch.  │   │ Flask + Granite  │   │ HAM safety   │
│ Ethics rules │   │ Prompt eng.  │   │ IBM watsonx.ai   │   │ 5 layers     │
└──────────────┘   └──────────────┘   └──────────────────┘   └──────────────┘
                                                                      │
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐          │
│   Feedback   │◀──│    Output    │◀──│   Validation     │◀─────────┘
│ Plans history│   │  .md + JSON  │   │ Input + output   │
└──────────────┘   └──────────────┘   └──────────────────┘
```

### Project Structure

```
Nutrient-Agent/
│
├── nutrition_ai/                  # Main application package
│   ├── app.py                     # Flask server — 6 REST API routes
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # IBM watsonx.ai config template
│   │
│   ├── agents/
│   │   ├── nutrition_agent.py     # Plan generation pipeline (8-phase)
│   │   └── query_agent.py         # Real-time Q&A agent
│   │
│   ├── utils/
│   │   ├── granite_client.py      # IBM Granite LLM client + fallback
│   │   ├── guardrails.py          # AI ethics, HAM framework, safety
│   │   └── plan_saver.py          # Markdown .md file persistence
│   │
│   ├── templates/index.html       # Responsive single-page web UI
│   ├── static/css/style.css       # IBM-themed responsive stylesheet
│   ├── static/js/app.js           # Frontend agentic UX logic
│   └── plans/                     # Auto-saved nutrition .md files
│
├── requirements.txt               # Root-level dependencies (same as above)
├── run_nutribot.bat               # Windows one-click launcher
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web application (UI) |
| `POST` | `/api/generate-plan` | Generate personalized nutrition plan |
| `POST` | `/api/query` | Answer a nutrition question |
| `GET` | `/api/plans` | List all saved plans |
| `GET` | `/api/plans/<filename>` | Read a saved plan |
| `GET` | `/api/health` | Service health check |

### Example: Generate Plan

```bash
curl -X POST http://127.0.0.1:5000/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Sharma",
    "age": 32,
    "diet_preference": "vegetarian",
    "medical_history": "Type 2 Diabetes",
    "city": "Mumbai",
    "country": "India",
    "goals": "Manage diabetes with low-GI diet"
  }'
```

### Example: Ask a Question

```bash
curl -X POST http://127.0.0.1:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What foods help lower blood pressure?"}'
```

---

## 🛡️ AI Ethics & Guardrails

### HAM Framework

| Principle | Implementation |
|---|---|
| **H**elpful | Practical, actionable, culturally-aware meal recommendations |
| **A**ccurate | Evidence-based nutritional science — no pseudoscience |
| **M**indful | Empathy for medical conditions; always recommends professional consultation |

### 5-Layer Safety Pipeline

```
Layer 1: Input Validation      → Age range, required fields, diet preference type
Layer 2: Harmful Pattern Block  → "stop medication", false cure claims, crash diets
Layer 3: Out-of-scope Filter    → Politics, violence, non-nutrition topics blocked
Layer 4: Output Sanitization    → Sentence-level post-generation safety check
Layer 5: Medical Disclaimer     → Mandatory ⚕️ disclaimer on every generated plan
```

---

## 📋 Requirements

- **Python** 3.9 or higher
- **pip** (comes with Python)
- Internet connection *(only for IBM Granite API; not required in demo mode)*

```
flask>=3.0.0
requests>=2.31.0
python-dotenv>=1.0.0
markdown>=3.5.0
```

---

## ⚕️ Medical Disclaimer

> This application is for **informational and educational purposes only**. The nutrition plans and answers generated by NutriBot do **not** constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional or registered dietitian before making significant changes to your diet, especially if you have existing medical conditions (e.g., diabetes, hypertension, kidney disease, eating disorders).

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with IBM Granite on IBM watsonx.ai**

*NutriBot — IBM Granite Nutrition Agentic AI | Following all phases of the Agentic AI SDLC*

</div>

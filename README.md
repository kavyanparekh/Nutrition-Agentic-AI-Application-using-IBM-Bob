# 🥗 NutriAgent AI — Nutrition Agentic AI Application

> **Personalised Nutrition Intelligence powered by IBM Granite LLM & watsonx.ai**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)](https://streamlit.io)
[![IBM Granite](https://img.shields.io/badge/IBM-Granite--13B-0062ff)](https://www.ibm.com/granite)
[![watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-8a3ffc)](https://www.ibm.com/watsonx)

---

## Overview

**NutriAgent AI** is a web-based Agentic AI application that combines a rich user health profile with IBM Granite's enterprise language model to deliver truly personalised nutrition intelligence across **five specialised AI agents**.

---

## Features

| Agent | Description |
|-------|-------------|
| 🗓️ **Nutrition Plan** | Generates 3-day, 7-day, or 14-day personalised meal plans with macros |
| 📊 **Macro Tracker** | Logs daily macros, visualises caloric breakdown via Plotly charts, and gets AI feedback |
| 💬 **Ask NutriAgent** | Multi-turn conversational Q&A on any nutrition topic |
| 🍳 **Recipe Analyser** | Analyses any recipe — calories, macros, health rating, improvement tips |
| 🩺 **Health Insights** | Personalised dietary risks, supplement recommendations, and goal-specific macro targets |

---

## Project Structure

```
.
├── app.py                          # Main Streamlit application (5 AI agents)
├── index.html                      # Static landing/marketing page
├── plan.md                         # Auto-generated nutrition plan output
├── requirements.txt                # Python dependencies
├── run.bat                         # One-click Windows launcher
├── .env.example                    # IBM credentials template
├── README.md                       # This file
└── NutriAgent_AI_Presentation.pptx # 8-slide project presentation
```

---

## Quick Start

### 1. Get IBM watsonx.ai Credentials

1. Log in at [IBM Cloud](https://cloud.ibm.com/)
2. Create an **API key** at IAM → API keys
3. Open [watsonx.ai](https://www.ibm.com/watsonx) and note your **Project ID**

### 2. Configure Credentials

```bash
cp .env.example .env
# Edit .env and fill in your IBM_API_KEY and IBM_PROJECT_ID
```

### 3. Launch (Windows)

```bat
run.bat
```

This script automatically:
- Creates a Python virtual environment
- Installs all dependencies from `requirements.txt`
- Creates a `.env` template if not found
- Launches the Streamlit app at `http://localhost:8501`

### 4. Launch (Mac / Linux)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Architecture

```
Browser / index.html
        ↕
Streamlit Web App (app.py)
        ↕
┌─────────────────────────────────────────────┐
│  User Profile Builder  │  Prompt Constructor │
│  BMI/TDEE Calculator   │  Session State      │
└─────────────────────────────────────────────┘
        ↕
IBM watsonx.ai SDK  →  IBM Granite-13B Instruct
        ↕
┌────────────────────────────────────────────────────────────┐
│ Nutrition Plan │ Macro Tracker │ Q&A │ Recipe │ Insights   │
└────────────────────────────────────────────────────────────┘
        ↕
plan.md output  +  Plotly Charts  +  Chat History
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | IBM Granite-13B Instruct (`ibm/granite-13b-instruct-v2`) |
| AI Platform | IBM watsonx.ai |
| Web Framework | Streamlit 1.35 |
| AI SDK | ibm-watsonx-ai |
| Agent Support | LangChain-IBM |
| Charts | Plotly |
| Data | Pandas |
| Secrets | python-dotenv |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `IBM_API_KEY` | IBM Cloud IAM API key |
| `IBM_PROJECT_ID` | watsonx.ai project ID |
| `IBM_URL` | watsonx.ai endpoint (default: `https://us-south.ml.cloud.ibm.com`) |

---

## Disclaimer

> ⚠️ NutriAgent AI is for informational purposes only and is **not** a substitute for advice from a registered dietitian, nutritionist, or medical professional. Always consult a qualified healthcare provider before making significant dietary changes.

---

*Built with ❤️ using IBM Granite LLM & Streamlit*

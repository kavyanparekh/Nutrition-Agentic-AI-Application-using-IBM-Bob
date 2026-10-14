"""
Nutrition Agentic AI Application
Powered by IBM Granite LLM via IBM watsonx.ai
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ── Environment ──────────────────────────────────────────────────────────────
load_dotenv()

IBM_API_KEY  = os.getenv("IBM_API_KEY", "")
IBM_URL      = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
IBM_PROJECT  = os.getenv("IBM_PROJECT_ID", "")
GRANITE_MODEL = "ibm/granite-13b-instruct-v2"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriAgent AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a6b3a, #2e9e5b);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .card {
        background: #f8fdf9;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .metric-box {
        background: #e8f5e9;
        border-left: 4px solid #2e9e5b;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .stButton > button {
        background-color: #2e9e5b;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }
    .stButton > button:hover { background-color: #1a6b3a; }
    .agent-label {
        font-size: 12px;
        color: #57606a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


# ── IBM Granite LLM Helper ────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_model():
    """Initialise IBM Granite model via watsonx.ai."""
    if not IBM_API_KEY or not IBM_PROJECT:
        return None
    credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
    params = {
        GenParams.MAX_NEW_TOKENS: 1024,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.9,
        GenParams.REPETITION_PENALTY: 1.1,
    }
    model = ModelInference(
        model_id=GRANITE_MODEL,
        credentials=credentials,
        project_id=IBM_PROJECT,
        params=params,
    )
    return model


def call_granite(prompt: str) -> str:
    """Send a prompt to IBM Granite and return the generated text."""
    model = get_model()
    if model is None:
        return (
            "⚠️ **IBM watsonx.ai credentials not configured.**\n\n"
            "Please set `IBM_API_KEY`, `IBM_PROJECT_ID`, and optionally `IBM_URL` "
            "in your `.env` file and restart the app."
        )
    try:
        response = model.generate_text(prompt=prompt)
        return response.strip()
    except Exception as exc:
        return f"❌ Error calling IBM Granite: {exc}"


# ── Agent Prompts ─────────────────────────────────────────────────────────────
SYSTEM_CONTEXT = (
    "You are NutriAgent, an expert AI nutritionist powered by IBM Granite. "
    "You give evidence-based, personalised dietary advice. "
    "Always be concise, actionable, and health-safety conscious."
)

def build_prompt(task: str, user_data: dict | None = None) -> str:
    context = f"{SYSTEM_CONTEXT}\n\n"
    if user_data:
        context += f"User profile: {json.dumps(user_data, indent=2)}\n\n"
    context += f"Task: {task}\n\nResponse:"
    return context


# ── BMI Calculator ────────────────────────────────────────────────────────────
def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str]:
    h = height_cm / 100
    bmi = round(weight_kg / (h ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


def tdee(weight_kg: float, height_cm: float, age: int, sex: str, activity: str) -> int:
    """Harris-Benedict TDEE estimate."""
    if sex == "Male":
        bmr = 88.362 + 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age
    else:
        bmr = 447.593 + 9.247 * weight_kg + 3.098 * height_cm - 4.330 * age
    multipliers = {
        "Sedentary":        1.2,
        "Lightly active":   1.375,
        "Moderately active": 1.55,
        "Very active":      1.725,
        "Extra active":     1.9,
    }
    return int(bmr * multipliers.get(activity, 1.2))


# ── Sidebar – User Profile ────────────────────────────────────────────────────
def sidebar_profile() -> dict:
    st.sidebar.image(
        "https://img.icons8.com/color/96/salad.png",
        width=72,
    )
    st.sidebar.title("👤 Your Profile")

    name   = st.sidebar.text_input("Name", placeholder="e.g. Alex")
    age    = st.sidebar.slider("Age", 10, 90, 30)
    sex    = st.sidebar.selectbox("Biological Sex", ["Male", "Female"])
    weight = st.sidebar.number_input("Weight (kg)", 30.0, 200.0, 70.0, 0.5)
    height = st.sidebar.number_input("Height (cm)", 100.0, 220.0, 170.0, 0.5)
    activity = st.sidebar.selectbox(
        "Activity Level",
        ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"],
    )
    goal = st.sidebar.selectbox(
        "Primary Goal",
        ["Lose weight", "Maintain weight", "Gain muscle", "Improve energy", "Manage condition"],
    )
    conditions = st.sidebar.multiselect(
        "Health Conditions (optional)",
        ["Diabetes", "Hypertension", "High cholesterol", "Celiac disease", "Lactose intolerance",
         "IBS", "Heart disease", "Thyroid disorder", "None"],
        default=["None"],
    )
    diet_pref = st.sidebar.selectbox(
        "Dietary Preference",
        ["Omnivore", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo", "Mediterranean"],
    )

    bmi, bmi_cat = calculate_bmi(weight, height)
    daily_calories = tdee(weight, height, age, sex, activity)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**BMI:** `{bmi}` — *{bmi_cat}*")
    st.sidebar.markdown(f"**Daily Calorie Need:** `{daily_calories} kcal`")

    return {
        "name": name or "User",
        "age": age,
        "sex": sex,
        "weight_kg": weight,
        "height_cm": height,
        "activity": activity,
        "goal": goal,
        "conditions": conditions,
        "diet_preference": diet_pref,
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "daily_calories": daily_calories,
    }


# ── Tab: Nutrition Plan ───────────────────────────────────────────────────────
def tab_nutrition_plan(profile: dict):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗓️ Personalised 7-Day Nutrition Plan")
    duration = st.selectbox("Plan Duration", ["3-day", "7-day", "14-day"], index=1)
    allergies = st.text_input("Food allergies / intolerances (comma-separated)", "")

    if st.button("🤖 Generate Nutrition Plan"):
        with st.spinner("IBM Granite is crafting your nutrition plan…"):
            prompt = build_prompt(
                f"Create a {duration} meal plan for a {profile['age']}-year-old {profile['sex'].lower()} "
                f"weighing {profile['weight_kg']} kg, height {profile['height_cm']} cm, "
                f"BMI {profile['bmi']} ({profile['bmi_category']}), "
                f"daily calorie target {profile['daily_calories']} kcal. "
                f"Goal: {profile['goal']}. "
                f"Diet preference: {profile['diet_preference']}. "
                f"Health conditions: {', '.join(profile['conditions'])}. "
                f"Allergies/intolerances: {allergies if allergies else 'None'}. "
                "Include breakfast, lunch, dinner, and two snacks per day. "
                "Add approximate macros (carbs/protein/fat) for each day. "
                "Format clearly day-by-day.",
                profile,
            )
            result = call_granite(prompt)
        st.markdown(result)

        # Save to plan.md
        with open("plan.md", "w", encoding="utf-8") as f:
            f.write(f"# Nutrition Plan for {profile['name']}\n\n")
            f.write(f"**Generated by NutriAgent AI (IBM Granite)**\n\n")
            f.write(result)
        st.success("✅ Plan saved to `plan.md`")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Tab: Macro Tracker ────────────────────────────────────────────────────────
def tab_macro_tracker(profile: dict):
    st.subheader("📊 Macro & Calorie Tracker")

    col1, col2, col3 = st.columns(3)
    carbs   = col1.number_input("Carbohydrates (g)", 0, 800, 250)
    protein = col2.number_input("Protein (g)", 0, 400, 120)
    fat     = col3.number_input("Fat (g)", 0, 300, 70)

    consumed = carbs * 4 + protein * 4 + fat * 9
    target   = profile["daily_calories"]
    remaining = target - consumed

    fig = go.Figure(go.Pie(
        labels=["Carbs", "Protein", "Fat"],
        values=[carbs * 4, protein * 4, fat * 9],
        hole=0.45,
        marker_colors=["#2e9e5b", "#f4a261", "#e76f51"],
    ))
    fig.update_layout(title="Caloric breakdown", height=320, margin=dict(t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(3)
    cols[0].metric("Consumed (kcal)", consumed)
    cols[1].metric("Target (kcal)", target)
    cols[2].metric("Remaining (kcal)", remaining, delta=remaining)

    if st.button("💡 Get AI Macro Feedback"):
        with st.spinner("Analysing your macros…"):
            prompt = build_prompt(
                f"My today's macros: {carbs}g carbs, {protein}g protein, {fat}g fat "
                f"({consumed} kcal total). My goal is '{profile['goal']}' with a daily target of "
                f"{target} kcal. Evaluate my intake and suggest adjustments.",
                profile,
            )
            st.markdown(call_granite(prompt))


# ── Tab: Food Q&A ─────────────────────────────────────────────────────────────
def tab_food_qa(profile: dict):
    st.subheader("💬 Ask NutriAgent")
    st.caption("Ask anything about nutrition, food, diet, supplements, or health.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your nutrition question…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                prompt = build_prompt(user_input, profile)
                answer = call_granite(prompt)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})


# ── Tab: Recipe Analyser ──────────────────────────────────────────────────────
def tab_recipe_analyser(profile: dict):
    st.subheader("🍳 Recipe Nutrition Analyser")
    recipe = st.text_area(
        "Paste your recipe (ingredients + method)",
        height=200,
        placeholder="e.g. 2 eggs, 1 cup oats, 1 banana, 1 tbsp honey …",
    )
    servings = st.number_input("Number of servings", 1, 20, 2)

    if st.button("🔍 Analyse Recipe"):
        if recipe.strip():
            with st.spinner("Analysing with IBM Granite…"):
                prompt = build_prompt(
                    f"Analyse the following recipe for {servings} servings. "
                    f"Provide: total calories, macros (carbs/protein/fat) per serving, "
                    f"key micronutrients, health rating (1-10), and suggestions to improve nutritional value.\n\n"
                    f"Recipe:\n{recipe}",
                    profile,
                )
                st.markdown(call_granite(prompt))
        else:
            st.warning("Please enter a recipe first.")


# ── Tab: Health Insights ──────────────────────────────────────────────────────
def tab_health_insights(profile: dict):
    st.subheader("🩺 Personalised Health Insights")

    cols = st.columns(4)
    cols[0].metric("BMI", profile["bmi"], profile["bmi_category"])
    cols[1].metric("Daily Calories", f"{profile['daily_calories']} kcal")
    cols[2].metric("Goal", profile["goal"])
    cols[3].metric("Diet", profile["diet_preference"])

    if st.button("🧠 Generate Health Insights"):
        with st.spinner("Generating personalised insights…"):
            prompt = build_prompt(
                "Based on my profile, provide: "
                "1) Key nutritional insights and risks, "
                "2) Three highest-priority dietary changes, "
                "3) Recommended daily supplements (if any), "
                "4) Foods to avoid given my health conditions, "
                "5) One motivational tip tailored to my goal.",
                profile,
            )
            st.markdown(call_granite(prompt))

    st.markdown("---")
    st.subheader("📈 Macronutrient Targets")
    if profile["goal"] == "Lose weight":
        c, p, f = 0.40, 0.30, 0.30
    elif profile["goal"] == "Gain muscle":
        c, p, f = 0.45, 0.35, 0.20
    else:
        c, p, f = 0.50, 0.25, 0.25

    cal = profile["daily_calories"]
    data = pd.DataFrame({
        "Macro":   ["Carbohydrates", "Protein", "Fat"],
        "Calories": [cal * c, cal * p, cal * f],
        "Grams":   [round(cal * c / 4), round(cal * p / 4), round(cal * f / 9)],
    })
    fig = go.Figure(go.Bar(
        x=data["Macro"], y=data["Calories"],
        marker_color=["#2e9e5b", "#f4a261", "#e76f51"],
        text=data["Grams"].astype(str) + "g",
        textposition="outside",
    ))
    fig.update_layout(yaxis_title="Calories", height=320)
    st.plotly_chart(fig, use_container_width=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0">🥗 NutriAgent AI</h1>
        <p style="margin:4px 0 0 0; opacity:0.85">
            Personalised Nutrition Intelligence · Powered by IBM Granite LLM
        </p>
    </div>
    """, unsafe_allow_html=True)

    profile = sidebar_profile()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗓️ Nutrition Plan",
        "📊 Macro Tracker",
        "💬 Ask AI",
        "🍳 Recipe Analyser",
        "🩺 Health Insights",
    ])

    with tab1:
        tab_nutrition_plan(profile)
    with tab2:
        tab_macro_tracker(profile)
    with tab3:
        tab_food_qa(profile)
    with tab4:
        tab_recipe_analyser(profile)
    with tab5:
        tab_health_insights(profile)

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#57606a;font-size:13px'>"
        "NutriAgent AI · Built with IBM Granite & Streamlit · "
        "<em>Not a substitute for professional medical advice.</em></p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

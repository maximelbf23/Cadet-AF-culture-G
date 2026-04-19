#!/usr/bin/env python3
"""
PSY0 Training — Streamlit App V2
Premium design with polished UI, full persistence, and analytics.
"""
import streamlit as st
import json
import os
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "questions.json")
USER_DATA_PATH = os.path.join(BASE_DIR, "data", "user_data.json")
XLSX_PATH = os.path.join(BASE_DIR, "kd-tools-quizlet.xlsx")

st.set_page_config(
    page_title="PSY0 Air France — Entraînement",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM CSS V3 — Ultra polished
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap');

:root {
  --ink-900: #0f1117;
  --ink-800: #1c1f2e;
  --ink-700: #2a2d3e;
  --ink-600: #3d4258;
  --ink-500: #5c6278;
  --ink-400: #8b91a8;
  --ink-300: #b8bccc;
  --ink-200: #e0e2ea;
  --ink-100: #f0f1f5;
  --ink-50:  #f7f8fb;

  --amber:       #c8913a;
  --amber-soft:  #fef6ea;
  --amber-deep:  #9c6e2a;
  --amber-glow:  rgba(200,145,58,0.18);

  --ok:       #1f9e6b;
  --ok-soft:  #edf9f4;
  --err:      #d03a2e;
  --err-soft: #fef1f0;

  --bg:        var(--ink-50);
  --paper:     #ffffff;
  --rule:      var(--ink-200);
  --rule-soft: var(--ink-100);
  --text:      var(--ink-900);
  --text-dim:  var(--ink-500);
  --text-mute: var(--ink-400);

  --serif: "Newsreader", Georgia, serif;
  --sans:  "Geist", -apple-system, sans-serif;
  --mono:  "Geist Mono", monospace;

  --ease: cubic-bezier(0.22, 1, 0.36, 1);

  --shadow-xs: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-sm: 0 2px 12px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.04);
  --shadow-md: 0 12px 32px rgba(0,0,0,0.11), 0 2px 6px rgba(0,0,0,0.04);
  --shadow-focus: 0 0 0 3px var(--amber-glow);
}

/* ── Base ── */
.stApp { font-family: var(--sans); background: var(--bg); color: var(--text); }
.stApp > header { background: transparent !important; }
.block-container { padding-top: 2rem !important; max-width: 920px !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
    background: var(--paper) !important;
    border-right: 1px solid var(--rule) !important;
}
[data-testid="stSidebar"] * { font-family: var(--sans); }
[data-testid="stSidebar"] hr { border-color: var(--rule-soft) !important; }

/* ══════════════════════════════════════════════════════════════
   SIDEBAR NAVIGATION — transform radio → clean pill nav
   ══════════════════════════════════════════════════════════════ */

/* Hide the "nav" widget label */
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    display: none !important;
}

/* Flex column with small gap */
[data-testid="stSidebar"] .stRadio > div > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
}

/* Each nav item label */
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    margin: 0 !important;
    transition: background 0.15s, color 0.15s !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--text-dim) !important;
    width: 100% !important;
    line-height: 1.4 !important;
}

/* ✦ Kill the ugly radio circle in sidebar ONLY ✦ */
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: none !important;
    overflow: hidden !important;
    display: block !important;
}

/* Hover */
[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--ink-100) !important;
    color: var(--text) !important;
}

/* Active / selected page */
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: var(--amber-soft) !important;
    color: var(--amber-deep) !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════════════
   QCM ANSWER CARDS — radio options styled as beautiful cards
   (applies to all radios NOT in sidebar)
   ══════════════════════════════════════════════════════════════ */

/* Card wrapper — the BaseWeb radio component */
[data-baseweb="radio"] {
    background: var(--paper);
    border: 1.5px solid var(--rule);
    border-radius: 12px;
    padding: 14px 18px;
    gap: 14px;
    align-items: center;
    cursor: pointer;
    transition: border-color 0.18s var(--ease), box-shadow 0.18s var(--ease), background 0.18s;
    box-shadow: var(--shadow-xs);
    width: 100%;
}

/* Hover on answer card */
[data-baseweb="radio"]:hover {
    border-color: var(--amber);
    box-shadow: var(--shadow-focus);
    background: var(--amber-soft);
}

/* Selected answer card */
label:has(input:checked) [data-baseweb="radio"] {
    border-color: var(--amber);
    background: var(--amber-soft);
    box-shadow: var(--shadow-focus);
}

/* The circle indicator — style as a clean dot */
[data-baseweb="radio"] > div:first-child {
    width: 18px !important;
    height: 18px !important;
    min-width: 18px !important;
    border-radius: 50% !important;
    border: 2px solid var(--rule) !important;
    background: transparent !important;
    transition: all 0.15s !important;
    flex-shrink: 0 !important;
}

/* Checked indicator dot */
label:has(input:checked) [data-baseweb="radio"] > div:first-child {
    border-color: var(--amber-deep) !important;
    background: var(--amber-deep) !important;
    box-shadow: 0 0 0 3px var(--amber-glow) !important;
}

/* Answer text inside card */
[data-baseweb="radio"] span {
    font-family: var(--sans) !important;
    font-size: 15px !important;
    color: var(--text) !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}

label:has(input:checked) [data-baseweb="radio"] span {
    color: var(--amber-deep) !important;
}

/* Each option label wrapper (spacing) */
.stRadio > div > div > label {
    display: block !important;
    margin: 5px 0 !important;
    padding: 0 !important;
}

/* Override: sidebar circle already killed above, re-override card styles */
[data-testid="stSidebar"] [data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    gap: 0 !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] label:has(input:checked) [data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stRadio > div > div > label {
    margin: 1px 0 !important;
}

/* ── Headings ── */
h1, h2, h3 {
    font-family: var(--serif) !important;
    font-weight: 400 !important;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}
h1 { font-size: clamp(42px, 6vw, 68px) !important; line-height: 0.98 !important; }
h2 { font-size: 32px !important; }
h3 { font-size: 22px !important; font-weight: 500 !important; }
em { font-style: italic; color: var(--amber-deep); }

/* ── Typography utils ── */
.eyebrow {
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-mute);
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}
.eyebrow::before { content: ""; width: 22px; height: 1px; background: var(--text-mute); }

.section-label {
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-mute);
    margin-bottom: 1.2rem;
    margin-top: 0.25rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-label::after { content: ""; flex: 1; height: 1px; background: var(--rule); }

/* ── Hero section ── */
.hero-section {
    display: block;
    margin-bottom: 48px;
    padding-bottom: 36px;
    border-bottom: 1px solid var(--rule);
}
.hero-title {
    font-family: var(--serif);
    font-weight: 400;
    font-size: clamp(38px, 5vw, 56px);
    line-height: 0.98;
    letter-spacing: -0.02em;
    color: var(--text);
    margin-bottom: 16px;
}
.hero-title em { font-style: italic; color: var(--amber-deep); font-weight: 400; }
.hero-subtitle {
    font-family: var(--serif);
    font-size: 18px;
    line-height: 1.55;
    color: var(--text-dim);
    max-width: 54ch;
}
.hero-divider { display: none; }

/* ── Stats strip ── */
.stats-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin-bottom: 48px;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-xs);
}
.stat-cell {
    padding: 22px 24px;
    text-align: center;
    border-right: 1px solid var(--rule);
    background: var(--paper);
}
.stat-cell:last-child { border-right: none; }
.stat-cell .sc-num {
    font-family: var(--serif);
    font-size: 32px;
    line-height: 1;
    color: var(--text);
    margin-bottom: 6px;
    font-variant-numeric: tabular-nums;
}
.stat-cell .sc-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-mute);
}

/* ── Stat grid (flashcards) ── */
.stat-grid {
    display: grid;
    gap: 0;
    margin-bottom: 2rem;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-xs);
}
.stat-card {
    padding: 1.4rem 1.5rem;
    text-align: center;
    border-right: 1px solid var(--rule);
    background: var(--paper);
}
.stat-card:last-child { border-right: none; }
.stat-value {
    font-family: var(--serif);
    font-size: 30px;
    color: var(--text);
    line-height: 1;
    font-variant-numeric: tabular-nums;
    margin-bottom: 6px;
}
.stat-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-mute);
}

/* ── Score display ── */
.score-big {
    font-family: var(--serif);
    font-size: clamp(64px, 12vw, 104px);
    font-weight: 400;
    line-height: 1;
    text-align: center;
    margin: 2rem auto 0.5rem;
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
    display: block;
}
.score-green  { color: var(--ok); }
.score-yellow { color: var(--amber-deep); }
.score-red    { color: var(--err); }
.score-caption {
    text-align: center;
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-mute);
    margin-bottom: 2.5rem;
}

/* ── Glass card (empty state) ── */
.glass-card {
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
}

/* ── Question card ── */
.question-card {
    border-bottom: 1px solid var(--rule);
    padding: 0.75rem 0 2rem;
    margin: 1rem 0 1.8rem;
}
.question-text {
    font-family: var(--serif);
    font-size: 24px;
    font-weight: 500;
    color: var(--text);
    line-height: 1.4;
    letter-spacing: -0.01em;
}
.cat-badge, .category-badge {
    display: inline-block;
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--amber-deep);
    margin-bottom: 14px;
    background: none !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--paper) !important;
    border: 1.5px solid var(--rule) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: var(--sans) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 13px 22px !important;
    transition: all 0.18s var(--ease) !important;
    width: 100%;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button:hover {
    background: var(--ink-100) !important;
    border-color: var(--ink-300) !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:focus-visible {
    outline: none !important;
    box-shadow: var(--shadow-focus) !important;
}
.stButton > button[kind="primary"] {
    background: var(--ink-900) !important;
    color: #fff !important;
    border: none !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-size: 12px !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--ink-700) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ── Answer feedback cards ── */
.correct-answer {
    background: var(--ok-soft);
    border: 1.5px solid var(--ok);
    border-left: 4px solid var(--ok);
    border-radius: 10px;
    padding: 14px 18px;
    color: var(--ok);
    font-weight: 600;
    font-family: var(--sans);
    font-size: 15px;
    margin: 5px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.wrong-answer {
    background: var(--err-soft);
    border: 1.5px solid var(--err);
    border-left: 4px solid var(--err);
    border-radius: 10px;
    padding: 14px 18px;
    color: var(--err);
    font-weight: 600;
    font-family: var(--sans);
    font-size: 15px;
    margin: 5px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.neutral-answer {
    background: var(--paper);
    border: 1.5px solid var(--rule);
    border-radius: 10px;
    padding: 14px 18px;
    color: var(--text-dim);
    font-family: var(--sans);
    font-size: 15px;
    margin: 5px 0;
}

/* ── Flashcard ── */
.flashcard {
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 16px;
    padding: 4rem 3rem;
    text-align: center;
    min-height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    margin: 2rem auto;
    max-width: 600px;
}
.flashcard-front {
    font-family: var(--serif);
    font-size: 28px;
    font-weight: 400;
    color: var(--text);
    line-height: 1.3;
}
.flashcard-back {
    font-family: var(--serif);
    font-size: 24px;
    font-weight: 500;
    color: var(--ok);
    line-height: 1.4;
}

/* ── Progress bar ── */
.stProgress > div > div { background: var(--amber-deep) !important; border-radius: 4px; }
.stProgress > div { background: var(--rule) !important; border-radius: 4px; height: 4px !important; }

/* ── Session history row ── */
.session-row {
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin: 5px 0;
    font-family: var(--sans);
    font-size: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.15s;
}
.session-row:hover { box-shadow: var(--shadow-sm); }
.session-row b { font-family: var(--serif); font-size: 17px; color: var(--text); }

/* ── Form Controls ── */
.stSelectbox > div > div {
    background: var(--paper) !important;
    border-color: var(--rule) !important;
    border-radius: 10px !important;
    font-family: var(--sans) !important;
    font-size: 15px !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-xs) !important;
}
[data-testid="stWidgetLabel"] {
    font-family: var(--mono) !important;
    font-size: 11px !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-mute) !important;
}

/* ── Checkbox ── */
.stCheckbox label {
    font-family: var(--sans) !important;
    font-size: 14px !important;
    cursor: pointer !important;
    color: var(--text-dim) !important;
}
.stCheckbox [data-baseweb="checkbox"] > div:first-child {
    border-radius: 5px !important;
    border-color: var(--rule) !important;
    transition: all 0.15s !important;
}

/* ── Metrics ── */
[data-testid="stMetricValue"] {
    font-family: var(--serif) !important;
    color: var(--text) !important;
    font-weight: 400 !important;
    font-size: 32px !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--mono) !important;
    color: var(--text-mute) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 10px !important;
}

/* ── Alert ── */
.stAlert { border-radius: 10px !important; font-family: var(--sans) !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--rule) !important; border-radius: 10px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--ink-300); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--ink-400); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
# Mapping catégories anglais → français
CAT_MAP = {
    "theory":    "Technique",
    "history":   "Histoire",
    "aircrafts": "Aéronefs",
    "airline":   "Air France & Flotte",
    "airports":  "Aéroports",
    "geography": "Géographie",
    "fleet":     "Air France & Flotte",
    "military":  "Militaire",
    "network":   "Réseau",
}

VALID_CATS = set(CAT_MAP.keys())

@st.cache_data
def load_questions_safe():
    """Charge les QCM depuis le xlsx, les flashcards depuis questions.json."""
    import pandas as pd

    # ── QCM depuis xlsx ──────────────────────────────────────
    df = pd.read_excel(XLSX_PATH)

    # Nettoyer : garder uniquement les lignes dont la catégorie est connue
    df = df[df["category"].isin(VALID_CATS)].copy()

    # Supprimer les lignes sans question ou sans bonne réponse
    df = df.dropna(subset=["question", "correct_answer"])

    # Supprimer les lignes sans au moins 1 distractor
    df = df.dropna(subset=["Answer 1"])

    # Réinitialiser l'index
    df = df.reset_index(drop=True)

    qcm_data = []
    for i, row in df.iterrows():
        # Récupérer les distractors disponibles (peut y avoir des NaN)
        distractors = [
            str(row["Answer 1"]).strip(),
            str(row["Answer 2 "]).strip() if pd.notna(row.get("Answer 2 ")) else None,
            str(row["Answer 3"]).strip() if pd.notna(row.get("Answer 3")) else None,
        ]
        distractors = [d for d in distractors if d and d != "nan"]

        # Construire la liste des 4 options mélangées
        correct_text = str(row["correct_answer"]).strip()
        opts_texts = [correct_text] + distractors[:3]

        # Mélanger les options de façon déterministe pour le cache
        # (on utilise l'index comme seed pour stabilité)
        rng = random.Random(i + 42)
        rng.shuffle(opts_texts)

        letters = ["a", "b", "c", "d"]
        options = [
            {"id": letters[j], "text": txt}
            for j, txt in enumerate(opts_texts[:4])
        ]
        correct_letter = letters[opts_texts.index(correct_text)]

        qcm_data.append({
            "id": int(row["id_display"]) if pd.notna(row.get("id_display")) else i + 10000,
            "question": str(row["question"]).strip(),
            "options": options,
            "answer": correct_letter,
            "explanation": "",
            "category": CAT_MAP.get(str(row["category"]).strip(), str(row["category"]).strip()),
        })

    # ── Flashcards depuis JSON (inchangé) ───────────────────
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    fc_data = data.get("flashcards", [])

    return qcm_data, fc_data

def get_user_data_path(username="Maxime"):
    safe_name = username.lower().replace(" ", "_")
    return os.path.join(BASE_DIR, "data", f"user_data_{safe_name}.json")

def load_user_data():
    username = st.session_state.get("current_profile", "Maxime")
    path = get_user_data_path(username)
    
    old_path = os.path.join(BASE_DIR, "data", "user_data.json")
    if username == "Maxime" and os.path.exists(old_path) and not os.path.exists(path):
        import shutil
        shutil.copy(old_path, path)
        
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"sessions": [], "flashcard_mastery": {}}

def save_user_data(data):
    username = st.session_state.get("current_profile", "Maxime")
    path = get_user_data_path(username)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_profiles():
    data_dir = os.path.join(BASE_DIR, "data")
    profiles = []
    if os.path.exists(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            if fname.startswith("user_data_") and fname.endswith(".json"):
                safe_name = fname[len("user_data_"):-len(".json")]
                display = safe_name.replace("_", " ").title()
                profiles.append(display)
    return profiles if profiles else ["Maxime"]

@st.cache_data
def build_q_map():
    qcm_data, _ = load_questions_safe()
    return {q["id"]: q for q in qcm_data}


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar(qcm_data, fc_data):
    with st.sidebar:
        # Wordmark
        st.markdown(
            '<div style="padding:1.5rem 0.5rem 1rem;">'
            '<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">'
            '<span style="font-size:1.5rem;">✈️</span>'
            '<span style="font-family:\'Newsreader\',Georgia,serif;font-size:1.15rem;'
            'font-style:italic;color:var(--ink-900);letter-spacing:-0.01em;">PSY0 Training</span>'
            '</div>'
            '<span style="font-family:\'Geist Mono\',monospace;font-size:9px;'
            'letter-spacing:0.2em;text-transform:uppercase;color:var(--ink-400);">'
            'AIR FRANCE</span></div>',
            unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "nav", ["🏠 Accueil", "📝 QCM", "🃏 Flashcards", "📊 Analytics", "🌍 Géographie"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        if "current_profile" not in st.session_state:
            st.session_state.current_profile = "Maxime"

        all_profiles = get_all_profiles()
        if st.session_state.current_profile not in all_profiles:
            all_profiles.insert(0, st.session_state.current_profile)

        profil_actuel = st.selectbox(
            "Profil", all_profiles,
            index=all_profiles.index(st.session_state.current_profile),
        )
        if profil_actuel != st.session_state.current_profile:
            st.session_state.current_profile = profil_actuel
            st.rerun()

        new_name = st.text_input(
            "Nouveau profil", placeholder="Prénom...",
            label_visibility="collapsed", key="new_profile_input"
        )
        if st.button("+ Créer profil", use_container_width=True) and new_name.strip():
            name = new_name.strip().title()
            path = get_user_data_path(name)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as _f:
                    json.dump({"sessions": [], "flashcard_mastery": {}}, _f)
            st.session_state.current_profile = name
            st.rerun()

        st.markdown("---")

        # Sidebar stats — visible only if sessions exist
        user_data = load_user_data()
        sessions = user_data.get("sessions", [])
        if sessions:
            total_q = sum(s["total"] for s in sessions)
            avg = sum(s["score"] / s["total"] for s in sessions) / len(sessions) * 100
            avg_color = "var(--ok)" if avg >= 70 else "var(--amber-deep)" if avg >= 50 else "var(--err)"
            st.markdown(
                f'<div style="padding:0.75rem 0.5rem 0.5rem;">'
                f'<div style="font-family:\'Newsreader\',Georgia,serif;'
                f'font-size:2rem;font-weight:400;color:{avg_color};'
                f'line-height:1;font-variant-numeric:tabular-nums;">{avg:.0f}%</div>'
                f'<div style="font-family:\'Geist Mono\',monospace;font-size:9px;'
                f'letter-spacing:0.18em;text-transform:uppercase;'
                f'color:var(--ink-400);margin-top:4px;">'
                f'{len(sessions)} sessions · {total_q} Q</div></div>',
                unsafe_allow_html=True
            )

        # Version footer
        st.markdown(
            f"<div style='margin-top:1rem;font-family:\"Geist Mono\",monospace;"
            f"font-size:9px;letter-spacing:0.12em;color:var(--ink-300);"
            f"text-transform:uppercase;'>"
            f"v4.0 · {len(qcm_data)} QCM · {len(fc_data)} FC</div>",
            unsafe_allow_html=True
        )

    return page


# ============================================================
# PAGE: ACCUEIL
# ============================================================
def page_accueil(qcm_data, fc_data):
    st.markdown(
        '<div class="hero-section">'
        '<div>'
        '<div class="eyebrow">Vol n°01 · Préparation</div>'
        '<h1 class="hero-title">Culture <em>aéronautique</em>.</h1>'
        '<p class="hero-subtitle">Un entraînement aéré, exigeant, pensé pour t\'emmener au niveau du jour J.</p>'
        '</div></div>',
        unsafe_allow_html=True)
    
    user_data = load_user_data()
    sessions = user_data.get("sessions", [])
    total_q = sum(s["total"] for s in sessions) if sessions else 0
    avg = (sum(s["score"]/s["total"] for s in sessions) / len(sessions) * 100) if sessions else 0
    mastery = user_data.get("flashcard_mastery", {})
    known = sum(1 for v in mastery.values() if v.get("status") == "known")
    
    avg_color = '#34d399' if avg >= 70 else '#fbbf24' if avg >= 50 else '#f87171' if sessions else '#a78bfa'
    
    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-cell">
            <div class="sc-num">{len(qcm_data)}</div>
            <div class="sc-label">QCM</div>
        </div>
        <div class="stat-cell">
            <div class="sc-num">{len(fc_data)}</div>
            <div class="sc-label">Flashcards</div>
        </div>
        <div class="stat-cell">
            <div class="sc-num">{total_q}</div>
            <div class="sc-label">Répondues</div>
        </div>
        <div class="stat-cell">
            <div class="sc-num">{avg:.0f}%</div>
            <div class="sc-label">Moyenne</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Categories
    st.markdown('<div class="section-label">Catégories QCM</div>', unsafe_allow_html=True)
    cats = {}
    for q in qcm_data:
        c = q.get("category", "Autre")
        cats[c] = cats.get(c, 0) + 1
    
    cols = st.columns(4)
    for i, (cat, count) in enumerate(sorted(cats.items(), key=lambda x: -x[1])):
        with cols[i % 4]:
            st.metric(cat, f"{count}")
    
    # Recent sessions
    if sessions:
        st.markdown("---")
        st.markdown("### 📋 Dernières sessions")
        for s in sessions[-5:][::-1]:
            pct = s["score"] / s["total"] * 100
            emoji = "🟢" if pct >= 80 else "🟡" if pct >= 60 else "🔴"
            date_str = s.get("date", "")[:16].replace("T", " ")
            cat_label = "Toutes" if s.get("category") == "all" else s.get("category", "?")
            st.markdown(
                f'<div class="session-row">'
                f'<span>{emoji} <b>{pct:.0f}%</b> — {s["score"]}/{s["total"]} · {cat_label}</span>'
                f'<span style="opacity:0.4">{date_str}</span></div>',
                unsafe_allow_html=True
            )


# ============================================================
# PAGE: QCM
# ============================================================
def page_qcm(qcm_data):
    if "qcm_active" not in st.session_state:
        st.session_state.qcm_active = False
    
    if not st.session_state.qcm_active:
        render_qcm_setup(qcm_data)
    elif st.session_state.get("qcm_finished"):
        render_qcm_summary()
    else:
        render_qcm_question()

def render_qcm_setup(qcm_data):
    st.markdown(
        '<div class="hero-section" style="margin-bottom:20px; border-bottom:none;">'
        '<div>'
        '<div class="eyebrow">Corpus principal</div>'
        '<h1 class="hero-title">Mode <em>QCM</em>.</h1>'
        '</div></div>',
        unsafe_allow_html=True)
    st.markdown("")
    
    cats = sorted(set(q.get("category", "Autre") for q in qcm_data))
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("🏷 Catégorie", ["all"] + cats,
                                format_func=lambda x: "Toutes les catégories" if x == "all" else x)
    with col2:
        mode = st.selectbox("🎯 Mode", [
            ("random20", "Série aléatoire — 20 Q"),
            ("random50", "Série aléatoire — 50 Q"),
            ("random100", "Série aléatoire — 100 Q"),
            ("exam", "🔒 Examen réel — 80 Q · 20s"),
            ("all", "Marathon — Toutes"),
        ], format_func=lambda x: x[1])
    
    mode_key = mode[0]
    
    col1, col2 = st.columns(2)
    with col1:
        timer_on = st.checkbox("⏱ Chronomètre", value=mode_key == "exam")
    with col2:
        if timer_on and mode_key != "exam":
            timer_s = st.selectbox("Temps/question", [15, 20, 30], index=1)
        elif mode_key == "exam":
            timer_s = 20
        else:
            timer_s = 0
    
    pool = [q for q in qcm_data if category == "all" or q.get("category") == category]
    st.markdown(f"**{len(pool)}** questions disponibles")
    
    st.markdown("")
    if st.button("🚀 Décoller", type="primary", use_container_width=True):
        random.shuffle(pool)
        limits = {"random20": 20, "random50": 50, "random100": 100, "exam": 80}
        if mode_key in limits:
            pool = pool[:limits[mode_key]]
        
        st.session_state.update({
            "qcm_active": True, "qcm_finished": False,
            "qcm_questions": pool, "qcm_idx": 0, "qcm_score": 0,
            "qcm_answers": [], "qcm_answered": False, "qcm_selected": None,
            "qcm_timer": timer_s, "qcm_mode": mode_key,
            "qcm_category": category, "qcm_q_start": time.time(),
            "qcm_session_start": time.time(),
        })
        st.rerun()

def render_qcm_question():
    questions = st.session_state.qcm_questions
    idx = st.session_state.qcm_idx

    if idx >= len(questions):
        finish_qcm()
        st.rerun()
        return

    q = questions[idx]
    total = len(questions)
    timer_s = st.session_state.get("qcm_timer", 0)
    answered = st.session_state.qcm_answered
    radio_key = f"qcm_radio_{idx}"

    # Timer logic — compute remaining before rendering
    remaining = None
    if timer_s > 0 and not answered:
        elapsed = time.time() - st.session_state.qcm_q_start
        remaining = max(0, timer_s - int(elapsed))
        if remaining == 0:
            # Auto-submit whatever is selected (or None)
            selected_label = st.session_state.get(radio_key)
            if selected_label:
                selected_id = selected_label[0].lower()
                is_correct = selected_id == q["answer"]
                if is_correct:
                    st.session_state.qcm_score += 1
            else:
                selected_id = None
                is_correct = False
            st.session_state.qcm_answers.append({
                "question_id": q["id"], "selected": selected_id,
                "correct": is_correct, "time_ms": int(elapsed * 1000),
            })
            st.session_state.qcm_idx += 1
            st.session_state.qcm_answered = False
            st.session_state.qcm_selected = None
            st.session_state.qcm_q_start = time.time()
            st.rerun()
            return

    progress = idx / total

    # Header
    if timer_s > 0:
        col1, col2, col3 = st.columns([4, 1, 1])
    else:
        col1, col2 = st.columns([3, 1])
        col3 = None

    with col1:
        st.progress(progress, text=f"Question {idx + 1} / {total}")
    with col2:
        st.markdown(
            f"<div style='text-align:right;font-size:1.1rem;font-weight:700;"
            f"color:var(--text);padding-top:0.3rem'>Score : {st.session_state.qcm_score}</div>",
            unsafe_allow_html=True,
        )
    if col3 is not None and remaining is not None:
        with col3:
            color = "var(--err)" if remaining <= 5 else "var(--amber)" if remaining <= 10 else "var(--ok)"
            st.markdown(
                f"<div style='text-align:right;font-size:1.4rem;font-weight:800;"
                f"color:{color};padding-top:0.1rem'>⏱ {remaining}s</div>",
                unsafe_allow_html=True,
            )

    # Category + Question
    cat = q.get("category", "Général")
    st.markdown(f'<span class="cat-badge">{cat}</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="question-card"><div class="question-text">{q["question"]}</div></div>',
        unsafe_allow_html=True,
    )

    selected = st.session_state.qcm_selected
    correct_letter = q["answer"]

    if not answered:
        # Answer options as beautiful radio cards
        option_labels = [f"{opt['id'].upper()} · {opt['text']}" for opt in q["options"]]
        chosen = st.radio(
            "Votre réponse",
            option_labels,
            key=radio_key,
            label_visibility="collapsed",
            index=None,
        )

        st.markdown("")
        if st.button(
            "Valider ma réponse →",
            type="primary",
            use_container_width=True,
            disabled=chosen is None,
        ):
            elapsed = time.time() - st.session_state.qcm_q_start
            selected_id = chosen[0].lower()
            is_correct = selected_id == correct_letter
            if is_correct:
                st.session_state.qcm_score += 1
            st.session_state.qcm_answered = True
            st.session_state.qcm_selected = selected_id
            st.session_state.qcm_answers.append({
                "question_id": q["id"], "selected": selected_id,
                "correct": is_correct, "time_ms": int(elapsed * 1000),
            })
            st.rerun()

        # Tick every second while timer is running
        if timer_s > 0:
            time.sleep(1)
            st.rerun()
    else:
        for opt in q["options"]:
            is_correct_opt = opt["id"] == correct_letter
            is_selected = opt["id"] == selected
            label = f"{opt['id'].upper()} · {opt['text']}"
            if is_correct_opt:
                st.markdown(f'<div class="correct-answer">✅ {label}</div>', unsafe_allow_html=True)
            elif is_selected:
                st.markdown(f'<div class="wrong-answer">❌ {label}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="neutral-answer">{label}</div>', unsafe_allow_html=True)

        if q.get("explanation"):
            st.info(f"💡 {q['explanation']}")

        st.markdown("")
        if st.button("Suivant →", type="primary", use_container_width=True):
            st.session_state.qcm_idx += 1
            st.session_state.qcm_answered = False
            st.session_state.qcm_selected = None
            st.session_state.qcm_q_start = time.time()
            st.rerun()

def finish_qcm():
    questions = st.session_state.qcm_questions
    session = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().isoformat(),
        "mode": st.session_state.qcm_mode,
        "category": st.session_state.qcm_category,
        "score": st.session_state.qcm_score,
        "total": len(questions),
        "duration_seconds": int(time.time() - st.session_state.qcm_session_start),
        "answers": st.session_state.qcm_answers,
    }
    user_data = load_user_data()
    user_data["sessions"].append(session)
    save_user_data(user_data)
    st.session_state.qcm_finished = True
    st.session_state.qcm_session_result = session

def render_qcm_summary():
    s = st.session_state.qcm_session_result
    pct = s["score"] / s["total"] * 100

    color_cls = "score-green" if pct >= 80 else "score-yellow" if pct >= 60 else "score-red"
    dur = s["duration_seconds"]
    st.markdown(
        f'<div class="eyebrow">Bilan du vol</div>'
        f'<div class="score-big {color_cls}">{pct:.0f}%</div>'
        f'<div class="score-caption">{s["score"]} / {s["total"]} bonnes réponses'
        f' &nbsp;·&nbsp; {dur // 60}m{dur % 60}s</div>',
        unsafe_allow_html=True
    )
    
    # Category breakdown
    q_map = build_q_map()
    cat_stats = {}
    for a in s.get("answers", []):
        q = q_map.get(a["question_id"], {})
        cat = q.get("category", "Autre")
        cat_stats.setdefault(cat, {"c": 0, "t": 0})
        cat_stats[cat]["t"] += 1
        if a["correct"]: cat_stats[cat]["c"] += 1
    
    if cat_stats:
        st.markdown("#### Par catégorie")
        for cat, cs in sorted(cat_stats.items()):
            p = cs["c"] / cs["t"] * 100
            st.progress(p / 100, text=f"{cat}: {cs['c']}/{cs['t']} ({p:.0f}%)")
    
    # Wrong answers
    wrong = [a for a in s.get("answers", []) if not a["correct"]]
    if wrong:
        st.markdown("#### ❌ À revoir")
        for a in wrong:
            q = q_map.get(a["question_id"], {})
            correct_text = next((o["text"] for o in q.get("options", []) if o["id"] == q.get("answer")), "?")
            with st.expander(f'{q.get("question", "?")[:80]}'):
                sel_text = next((o["text"] for o in q.get("options", []) if o["id"] == a["selected"]), "?")
                st.markdown(f'<div class="wrong-answer">Ta réponse: {sel_text}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="correct-answer">Bonne réponse: {correct_text}</div>', unsafe_allow_html=True)
    
    st.markdown("")
    if st.button("🔄 Nouveau quiz", type="primary", use_container_width=True):
        st.session_state.qcm_active = False
        st.session_state.qcm_finished = False
        st.rerun()


# ============================================================
# PAGE: FLASHCARDS
# ============================================================
def page_flashcards(fc_data):
    if "fc_active" not in st.session_state:
        st.session_state.fc_active = False
    
    if not st.session_state.fc_active:
        render_fc_setup(fc_data)
    elif st.session_state.get("fc_finished"):
        render_fc_summary()
    else:
        render_fc_card()

def render_fc_setup(fc_data):
    st.markdown(
        '<div class="hero-section">'
        '<div class="hero-title">🃏 Flashcards</div>'
        '<div class="hero-subtitle">Révisez les faits clés par cartes mémo</div>'
        '<div class="hero-divider"></div></div>',
        unsafe_allow_html=True)
    
    user_data = load_user_data()
    mastery = user_data.get("flashcard_mastery", {})
    known = sum(1 for v in mastery.values() if v.get("status") == "known")
    pct_m = known / len(fc_data) * 100 if fc_data else 0
    
    st.markdown(f"""
    <div class="stat-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="stat-card"><div class="stat-value">{len(fc_data)}</div><div class="stat-label">Total</div></div>
        <div class="stat-card"><div class="stat-value" style="-webkit-text-fill-color:var(--ok)">{known}</div><div class="stat-label">Maîtrisées</div></div>
        <div class="stat-card"><div class="stat-value">{pct_m:.0f}%</div><div class="stat-label">Progression</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    cats = sorted(set(f.get("category", "Général") for f in fc_data))
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("🏷 Catégorie", ["all"] + cats,
                                format_func=lambda x: "Toutes" if x == "all" else x, key="fc_cat")
    with col2:
        count = st.selectbox("📊 Nombre", [20, 50, 100, 0],
                             format_func=lambda x: "Toutes" if x == 0 else f"{x} cartes", index=1, key="fc_cnt")
    
    only_unknown = st.checkbox("🔍 Uniquement les cartes non maîtrisées")
    
    pool = [f for f in fc_data if category == "all" or f.get("category") == category]
    if only_unknown:
        pool = [f for f in pool if mastery.get(str(f["id"]), {}).get("status") != "known"]
    
    st.markdown(f"**{len(pool)}** cartes disponibles")
    st.markdown("")
    
    if st.button("🃏 Commencer", type="primary", use_container_width=True):
        random.shuffle(pool)
        if count > 0: pool = pool[:count]
        if not pool:
            st.warning("Aucune carte disponible.")
            return
        st.session_state.update({
            "fc_active": True, "fc_finished": False,
            "fc_cards": pool, "fc_idx": 0, "fc_known": 0, "fc_flipped": False,
        })
        st.rerun()

def render_fc_card():
    cards = st.session_state.fc_cards
    idx = st.session_state.fc_idx
    
    if idx >= len(cards):
        st.session_state.fc_finished = True
        st.rerun()
        return
    
    card = cards[idx]
    total = len(cards)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(idx / total, text=f"Carte {idx + 1} / {total}")
    with col2:
        st.markdown(f"<div style='text-align:right;color:var(--ok);font-weight:700;padding-top:0.3rem'>"
                    f"✅ {st.session_state.fc_known} connues</div>", unsafe_allow_html=True)
    
    cat = card.get("category", "Général")
    st.markdown(f'<span class="cat-badge">{cat}</span>', unsafe_allow_html=True)
    
    flipped = st.session_state.fc_flipped
    
    if not flipped:
        st.markdown(f'<div class="flashcard flashcard-front">{card["front"]}</div>', unsafe_allow_html=True)
        st.markdown("")
        if st.button("🔄 Retourner la carte", use_container_width=True, type="primary"):
            st.session_state.fc_flipped = True
            st.rerun()
    else:
        st.markdown(f'<div class="flashcard flashcard-back">💡 {card["back"]}</div>', unsafe_allow_html=True)
        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ À revoir", use_container_width=True):
                _mark_fc(card, False)
        with col2:
            if st.button("✅ Connue", type="primary", use_container_width=True):
                _mark_fc(card, True)

def _mark_fc(card, known):
    if known: st.session_state.fc_known += 1
    user_data = load_user_data()
    m = user_data.setdefault("flashcard_mastery", {})
    m[str(card["id"])] = {"status": "known" if known else "review", "last_reviewed": datetime.now().isoformat()}
    save_user_data(user_data)
    st.session_state.fc_idx += 1
    st.session_state.fc_flipped = False
    st.rerun()

def render_fc_summary():
    known = st.session_state.fc_known
    total = len(st.session_state.fc_cards)
    pct = known / total * 100 if total else 0

    color_cls = "score-green" if pct >= 80 else "score-yellow" if pct >= 60 else "score-red"
    st.markdown(
        f'<div class="eyebrow">Session terminée</div>'
        f'<div class="score-big {color_cls}">{pct:.0f}%</div>'
        f'<div class="score-caption">{known} / {total} cartes maîtrisées</div>',
        unsafe_allow_html=True
    )

    user_data = load_user_data()
    mastery = user_data.get("flashcard_mastery", {})
    _, fc_data = load_questions_safe()
    total_known = sum(1 for v in mastery.values() if v.get("status") == "known")
    overall = total_known / len(fc_data) * 100 if fc_data else 0
    st.progress(overall / 100, text=f"Maîtrise globale : {total_known}/{len(fc_data)} ({overall:.1f}%)")

    st.markdown("")
    if st.button("🔄 Nouvelle session", type="primary", use_container_width=True):
        st.session_state.fc_active = False
        st.session_state.fc_finished = False
        st.rerun()


# ============================================================
# PAGE: ANALYTICS
# ============================================================
def page_analytics():
    st.markdown(
        '<div class="hero-section">'
        '<div class="eyebrow">Tableau de bord</div>'
        '<div class="hero-title">Analyse <em>des performances</em>.</div>'
        '<p class="hero-subtitle">Identifiez vos points forts et les catégories à renforcer.</p>'
        '</div>',
        unsafe_allow_html=True)

    user_data = load_user_data()
    sessions = user_data.get("sessions", [])

    if not sessions:
        st.markdown(
            '<div class="glass-card" style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">🎯</div>'
            '<div style="font-family:\'Newsreader\',serif;font-size:1.3rem;'
            'color:var(--text-dim);">Complétez au moins un quiz<br>pour voir vos statistiques.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        return

    _, fc_data = load_questions_safe()
    q_map = build_q_map()

    # Plot layout adapté au fond clair
    plot_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='rgba(14,22,40,0.65)', family='Geist, sans-serif'),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    
    # 1. PROGRESSION
    st.markdown('<div class="section-label">Progression</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "Session": i + 1,
        "Score (%)": s["score"] / s["total"] * 100,
        "Date": s.get("date", "")[:10],
    } for i, s in enumerate(sessions)])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Session"], y=df["Score (%)"],
        mode='lines+markers',
        line=dict(color='oklch(58% 0.12 55)', width=2.5),
        marker=dict(size=7, color='oklch(58% 0.12 55)', line=dict(width=2, color='white')),
        fill='tozeroy', fillcolor='rgba(147,97,53,0.08)',
    ))
    fig.add_hline(y=80, line_dash="dot", line_color="rgba(59,161,109,0.5)",
                  annotation_text="Objectif 80%",
                  annotation_font_color="rgba(59,161,109,0.75)",
                  annotation_font_size=11)
    fig.update_layout(
        **plot_layout, height=340, yaxis_range=[0, 105],
        xaxis_title="Session", yaxis_title="Score (%)",
        xaxis=dict(gridcolor='rgba(14,22,40,0.06)', zeroline=False),
        yaxis=dict(gridcolor='rgba(14,22,40,0.06)', zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. RADAR + TIME
    col1, col2 = st.columns(2)
    
    cat_stats = {}
    for s in sessions:
        for a in s.get("answers", []):
            q = q_map.get(a["question_id"], {})
            cat = q.get("category", "Autre")
            cat_stats.setdefault(cat, {"c": 0, "t": 0, "times": []})
            cat_stats[cat]["t"] += 1
            if a["correct"]: cat_stats[cat]["c"] += 1
            cat_stats[cat]["times"].append(a.get("time_ms", 0))
    
    with col1:
        st.markdown('<div class="section-label">Réussite par catégorie</div>', unsafe_allow_html=True)
        if cat_stats:
            cats_r = list(cat_stats.keys())
            vals_r = [cat_stats[c]["c"] / cat_stats[c]["t"] * 100 for c in cats_r]
            fig_r = go.Figure(data=go.Scatterpolar(
                r=vals_r + [vals_r[0]], theta=cats_r + [cats_r[0]],
                fill='toself', fillcolor='rgba(147,97,53,0.10)',
                line=dict(color='oklch(58% 0.12 55)', width=2),
                marker=dict(size=5, color='oklch(58% 0.12 55)'),
            ))
            fig_r.update_layout(
                **plot_layout, height=360,
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 100], ticksuffix="%",
                        gridcolor='rgba(14,22,40,0.08)',
                        color='rgba(14,22,40,0.45)',
                        tickfont=dict(size=9),
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(14,22,40,0.08)',
                        tickfont=dict(size=10),
                    ),
                    bgcolor='rgba(0,0,0,0)',
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)

    with col2:
        st.markdown('<div class="section-label">Temps moyen / catégorie</div>', unsafe_allow_html=True)
        time_data = []
        for cat, cs in cat_stats.items():
            valid = [t for t in cs["times"] if t > 0]
            if valid:
                time_data.append({"Catégorie": cat, "Temps (s)": round(sum(valid) / len(valid) / 1000, 1)})
        if time_data:
            df_t = pd.DataFrame(time_data).sort_values("Temps (s)")
            fig_t = px.bar(
                df_t, x="Temps (s)", y="Catégorie", orientation='h',
                color="Temps (s)",
                color_continuous_scale=["oklch(62% 0.12 160)", "oklch(74% 0.14 72)", "oklch(58% 0.17 25)"]
            )
            fig_t.update_layout(**plot_layout, height=360, showlegend=False, coloraxis_showscale=False,
                                xaxis=dict(gridcolor='rgba(14,22,40,0.06)'),
                                yaxis=dict(gridcolor='rgba(14,22,40,0.06)'))
            st.plotly_chart(fig_t, use_container_width=True)
    
    # 3. TOP FAILED
    st.markdown('<div class="section-label">Top questions les plus ratées</div>', unsafe_allow_html=True)
    q_fails = {}
    for s in sessions:
        for a in s.get("answers", []):
            qid = a["question_id"]
            q_fails.setdefault(qid, {"w": 0, "t": 0})
            q_fails[qid]["t"] += 1
            if not a["correct"]: q_fails[qid]["w"] += 1
    
    ranked = [(qid, st) for qid, st in q_fails.items() if st["t"] >= 2 and st["w"] > 0]
    ranked.sort(key=lambda x: x[1]["w"]/x[1]["t"], reverse=True)
    
    if ranked:
        rows = []
        for qid, st_q in ranked[:20]:
            q = q_map.get(qid, {})
            rows.append({
                "Question": q.get("question", "?")[:70],
                "Catégorie": q.get("category", "?"),
                "Erreurs": f"{st_q['w']}/{st_q['t']}",
                "Taux": f"{st_q['w']/st_q['t']*100:.0f}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Complétez plus de sessions pour voir les statistiques détaillées.")
    
    # 4. FLASHCARD MASTERY
    st.markdown("---")
    st.markdown('<div class="section-label">Maîtrise flashcards</div>', unsafe_allow_html=True)
    mastery = user_data.get("flashcard_mastery", {})
    fc_cats = {}
    for f in fc_data:
        cat = f.get("category", "Général")
        fc_cats.setdefault(cat, {"t": 0, "k": 0})
        fc_cats[cat]["t"] += 1
        if mastery.get(str(f["id"]), {}).get("status") == "known": fc_cats[cat]["k"] += 1
    
    cols = st.columns(min(4, max(1, len(fc_cats))))
    for i, (cat, cs) in enumerate(sorted(fc_cats.items())):
        p = cs["k"] / cs["t"] * 100 if cs["t"] else 0
        with cols[i % len(cols)]:
            st.metric(cat, f"{cs['k']}/{cs['t']}")
            st.progress(p / 100)
    
    # 5. SESSION HISTORY
    st.markdown("---")
    st.markdown('<div class="section-label">Historique des sessions</div>', unsafe_allow_html=True)
    rows = []
    for s in sessions[::-1]:
        p = s["score"] / s["total"] * 100
        d = s.get("duration_seconds", 0)
        ans = s.get("answers", [])
        avg_t = 0
        if ans:
            vt = [a.get("time_ms", 0) for a in ans if a.get("time_ms", 0) > 0]
            avg_t = (sum(vt) / len(vt) / 1000) if vt else 0
        rows.append({
            "Date": s.get("date", "")[:16].replace("T", " "),
            "Mode": s.get("mode", "?"),
            "Catégorie": "Toutes" if s.get("category") == "all" else s.get("category", "?"),
            "Score": f"{s['score']}/{s['total']} ({p:.0f}%)",
            "Durée": f"{d//60}m{d%60}s",
            "Temps/Q": f"{avg_t:.1f}s",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ============================================================
# PAGE: GÉOGRAPHIE (Capitales, Drapeaux, Cartes)
# ============================================================
def page_geographie():
    html_path = Path(BASE_DIR) / "Capitale" / "Drapeau" / "index.html"

    if not html_path.exists():
        st.markdown(
            '<div class="glass-card" style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">⚠️</div>'
            '<div style="font-family:\'Newsreader\',serif;font-size:1.2rem;color:var(--text-dim);">'
            f'Fichier introuvable :<br><code>{html_path}</code></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    html_content = html_path.read_text(encoding="utf-8")
    st.components.v1.html(html_content, height=960, scrolling=True)


# ============================================================
# MAIN
# ============================================================
def main():
    qcm_data, fc_data = load_questions_safe()
    page = render_sidebar(qcm_data, fc_data)
    
    if page == "🏠 Accueil": page_accueil(qcm_data, fc_data)
    elif page == "📝 QCM": page_qcm(qcm_data)
    elif page == "🃏 Flashcards": page_flashcards(fc_data)
    elif page == "📊 Analytics": page_analytics()
    elif page == "🌍 Géographie": page_geographie()

if __name__ == "__main__":
    main()

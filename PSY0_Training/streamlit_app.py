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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "questions.json")
USER_DATA_PATH = os.path.join(BASE_DIR, "data", "user_data.json")

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* === ANIMATED BACKGROUND === */
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px rgba(102,126,234,0.15), 0 8px 32px rgba(0,0,0,0.2); }
    50% { box-shadow: 0 0 25px rgba(102,126,234,0.25), 0 12px 40px rgba(0,0,0,0.3); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #0a0a1a 0%, #0f1528 20%, #141e3c 40%, #0d1a2d 60%, #0a0f1f 80%, #0a0a1a 100%);
    background-size: 400% 400%;
    animation: gradientShift 25s ease infinite;
    color: #e2e8f0;
}
.stApp > header { background: transparent !important; }
.block-container { padding-top: 2.5rem; max-width: 1100px; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080818 0%, #0c0e24 40%, #10123a 100%) !important;
    border-right: 1px solid rgba(102,126,234,0.1);
    box-shadow: 4px 0 30px rgba(0,0,0,0.4);
}
[data-testid="stSidebar"] * { color: #99a8c8 !important; }
[data-testid="stSidebar"] .stRadio label { 
    font-size: 0.95rem !important; font-weight: 500 !important;
    padding: 0.7rem 1rem; border-radius: 12px; transition: all 0.25s ease;
    border: 1px solid transparent; margin: 2px 0;
}
[data-testid="stSidebar"] .stRadio label:hover { 
    background: rgba(102,126,234,0.08);
    border-color: rgba(102,126,234,0.15);
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.04) !important; }

/* === GLASSMORPHISM CARDS === */
.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 2rem;
    margin: 0.8rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
.glass-card:hover { 
    transform: translateY(-3px);
    border-color: rgba(102,126,234,0.15);
    box-shadow: 0 12px 48px rgba(0,0,0,0.4), 0 0 20px rgba(102,126,234,0.05);
}

/* === STAT CARDS === */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; margin: 2rem 0; }
.stat-card {
    background: rgba(255,255,255,0.025);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 1.8rem 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(102,126,234,0.4), transparent);
    opacity: 0; transition: opacity 0.3s;
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(102,126,234,0.2);
    box-shadow: 0 8px 30px rgba(102,126,234,0.08);
}
.stat-card:hover::after { opacity: 1; }
.stat-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
.stat-value {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.stat-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.5rem;
    font-weight: 600;
}

/* === QUESTION CARD === */
.question-card {
    background: linear-gradient(135deg, rgba(102,126,234,0.06) 0%, rgba(167,139,250,0.03) 100%);
    border: 1px solid rgba(102,126,234,0.12);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin: 1.2rem 0 1.8rem;
    position: relative;
    overflow: hidden;
}
.question-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #667eea, #a78bfa, #c084fc, #f093fb);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
.question-card::after {
    content: '';
    position: absolute; top: 0; right: 0; width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(102,126,234,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.question-text {
    font-size: 1.3rem;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1.7;
    letter-spacing: -0.01em;
}

/* === CATEGORY BADGE === */
.cat-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%);
    color: #a5b4fc !important;
    border: 1px solid rgba(102,126,234,0.25);
    padding: 0.4rem 1.3rem;
    border-radius: 25px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* === BUTTONS === */
.stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    color: #c9d1e0 !important;
    font-weight: 500 !important;
    padding: 1rem 1.4rem !important;
    transition: all 0.25s ease !important;
    font-size: 0.93rem !important;
    text-align: left !important;
    line-height: 1.5 !important;
}
.stButton > button:hover {
    background: rgba(102,126,234,0.1) !important;
    border-color: rgba(102,126,234,0.3) !important;
    color: #f1f5f9 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.12) !important;
}
.stButton > button:active { transform: translateY(0); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #7c3aed 50%, #a855f7 100%) !important;
    background-size: 200% 100%;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    box-shadow: 0 4px 25px rgba(102,126,234,0.3), 0 0 60px rgba(102,126,234,0.08) !important;
    transition: all 0.3s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background-position: 100% 0;
    box-shadow: 0 8px 35px rgba(102,126,234,0.45), 0 0 80px rgba(124,58,237,0.12) !important;
    transform: translateY(-3px);
}

/* === CORRECT / WRONG === */
.correct-answer {
    background: linear-gradient(135deg, rgba(72,187,120,0.08), rgba(56,161,105,0.04)) !important;
    border: 1.5px solid rgba(72,187,120,0.3) !important;
    border-radius: 16px; padding: 1.1rem 1.5rem;
    color: #68d391; font-weight: 500; margin: 0.5rem 0;
    box-shadow: 0 0 20px rgba(72,187,120,0.06);
}
.wrong-answer {
    background: linear-gradient(135deg, rgba(252,129,129,0.08), rgba(229,62,62,0.04)) !important;
    border: 1.5px solid rgba(252,129,129,0.3) !important;
    border-radius: 16px; padding: 1.1rem 1.5rem;
    color: #fc8181; font-weight: 500; margin: 0.5rem 0;
    box-shadow: 0 0 20px rgba(252,129,129,0.06);
}
.neutral-answer {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 16px; padding: 1.1rem 1.5rem;
    color: rgba(255,255,255,0.3); margin: 0.5rem 0;
}

/* === FLASHCARD === */
.flashcard {
    background: linear-gradient(135deg, rgba(102,126,234,0.06) 0%, rgba(167,139,250,0.04) 100%);
    border: 1px solid rgba(102,126,234,0.12);
    border-radius: 28px;
    padding: 4rem 3rem;
    text-align: center;
    min-height: 250px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 12px 50px rgba(0,0,0,0.25), 0 0 30px rgba(102,126,234,0.04);
    margin: 2rem auto;
    max-width: 700px;
    position: relative;
    overflow: hidden;
    animation: pulseGlow 4s ease-in-out infinite;
}
.flashcard::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #667eea, #a78bfa, #c084fc, #f093fb);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
.flashcard::after {
    content: '?';
    position: absolute; bottom: -20px; right: 20px;
    font-size: 8rem; font-weight: 900;
    color: rgba(102,126,234,0.04);
    pointer-events: none; line-height: 1;
}
.flashcard-front { font-size: 1.35rem; font-weight: 600; color: #f1f5f9; line-height: 1.6; z-index: 1; }
.flashcard-back {
    font-size: 1.25rem; font-weight: 500; color: #68d391; line-height: 1.6; z-index: 1;
    background: linear-gradient(135deg, rgba(72,187,120,0.06) 0%, rgba(56,161,105,0.03) 100%);
    border-color: rgba(72,187,120,0.15);
}
.flashcard-back::after { content: '💡'; }

/* === SCORE === */
.score-big {
    font-size: 6rem; font-weight: 900;
    text-align: center; line-height: 1;
    letter-spacing: -0.04em;
    filter: drop-shadow(0 4px 20px rgba(0,0,0,0.3));
}
.score-green { background: linear-gradient(135deg, #34d399, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.score-yellow { background: linear-gradient(135deg, #fbbf24, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.score-red { background: linear-gradient(135deg, #f87171, #ef4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.score-purple { background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* === HERO === */
.hero-section { text-align: center; padding: 1rem 0 0.5rem; }
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 30%, #c084fc 60%, #e879f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.4rem;
    filter: drop-shadow(0 2px 10px rgba(102,126,234,0.2));
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.35);
    font-weight: 400;
    letter-spacing: 0.02em;
}
.hero-divider {
    width: 60px; height: 3px; margin: 1.5rem auto;
    background: linear-gradient(90deg, #667eea, #a78bfa);
    border-radius: 2px;
}

/* === SESSION ROW === */
.session-row {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 0.9rem 1.4rem;
    margin: 0.5rem 0;
    display: flex; justify-content: space-between; align-items: center;
    transition: all 0.2s;
}
.session-row:hover {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.08);
    transform: translateX(4px);
}

/* === PROGRESS === */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #818cf8, #a78bfa) !important;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(102,126,234,0.2);
}
.stProgress > div { background: rgba(255,255,255,0.04) !important; border-radius: 10px; }

/* === METRICS === */
[data-testid="stMetricValue"] { 
    color: #a78bfa !important; 
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.4) !important; font-weight: 500 !important; }

/* === HEADINGS === */
h1, h2, h3 { color: #f1f5f9 !important; }
h2 { font-weight: 700 !important; letter-spacing: -0.02em; }
h3 { 
    font-weight: 600 !important; 
    color: rgba(241,245,249,0.9) !important;
    font-size: 1.15rem !important;
}

/* === FORM CONTROLS === */
.stSelectbox > div > div, .stCheckbox, .stRadio { color: #e2e8f0 !important; }
[data-testid="stWidgetLabel"] { color: rgba(255,255,255,0.6) !important; font-weight: 500 !important; }
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}

/* === EXPANDER === */
.streamlit-expanderHeader { 
    background: rgba(255,255,255,0.025) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

/* === DATAFRAME === */
.stDataFrame { border-radius: 16px; overflow: hidden; }

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(102,126,234,0.35); }

/* === DIVIDERS === */
hr { border-color: rgba(255,255,255,0.04) !important; }

/* === ALERTS === */
.stAlert { border-radius: 14px !important; }

/* === TABS (section dividers) === */
.section-label {
    font-size: 0.7rem; font-weight: 700;
    color: rgba(255,255,255,0.25);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 2rem 0 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-title { font-size: 2rem; }
    .question-card { padding: 1.8rem; }
    .flashcard { padding: 2.5rem 1.5rem; min-height: 180px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_questions_safe():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['qcm'], data['flashcards']

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
        st.markdown(
            '<div style="text-align:center;padding:1.5rem 0 0.5rem;">'
            '<div style="width:60px;height:60px;margin:0 auto 0.8rem;'
            'border-radius:16px;background:linear-gradient(135deg,rgba(102,126,234,0.15),rgba(167,139,250,0.1));'
            'border:1px solid rgba(102,126,234,0.2);display:flex;align-items:center;justify-content:center;'
            'box-shadow:0 4px 16px rgba(102,126,234,0.1);">'
            '<span style="font-size:1.8rem;">✈️</span></div>'
            '<span style="font-size:1.15rem;font-weight:800;'
            'background:linear-gradient(135deg,#818cf8,#c084fc);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
            'letter-spacing:-0.02em;">PSY0 Training</span><br>'
            '<span style="font-size:0.7rem;color:rgba(255,255,255,0.2);letter-spacing:0.1em;">'
            'AIR FRANCE</span></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        page = st.radio(
            "nav", ["🏠 Accueil", "📝 QCM", "🃏 Flashcards", "📊 Analytics"],
            label_visibility="collapsed",
        )
        
        st.markdown("---")
        
        if "current_profile" not in st.session_state:
            st.session_state.current_profile = "Maxime"

        all_profiles = get_all_profiles()
        if st.session_state.current_profile not in all_profiles:
            all_profiles.insert(0, st.session_state.current_profile)

        profil_actuel = st.selectbox(
            "👤 Profil", all_profiles,
            index=all_profiles.index(st.session_state.current_profile),
        )
        if profil_actuel != st.session_state.current_profile:
            st.session_state.current_profile = profil_actuel
            st.rerun()

        new_name = st.text_input("✏️ Nouveau profil", placeholder="Prénom...",
                                 label_visibility="collapsed", key="new_profile_input")
        if st.button("+ Créer profil", use_container_width=True) and new_name.strip():
            name = new_name.strip().title()
            path = get_user_data_path(name)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as _f:
                    json.dump({"sessions": [], "flashcard_mastery": {}}, _f)
            st.session_state.current_profile = name
            st.rerun()

        st.markdown("---")
        
        user_data = load_user_data()
        sessions = user_data.get("sessions", [])
        if sessions:
            total_q = sum(s["total"] for s in sessions)
            avg = sum(s["score"]/s["total"] for s in sessions) / len(sessions) * 100
            st.markdown(
                f'<div style="text-align:center;padding:0.5rem 0;">'
                f'<div style="font-size:1.6rem;font-weight:800;color:#a78bfa;">{avg:.0f}%</div>'
                f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.3);margin-top:0.2rem;">'
                f'{len(sessions)} sessions · {total_q} questions</div></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f"<div style='position:fixed;bottom:1rem;left:1rem;opacity:0.2;font-size:0.65rem;letter-spacing:0.05em;'>"
            f"v4.0 · {len(qcm_data)} QCM · {len(fc_data)} FC</div>", unsafe_allow_html=True)
    
    return page


# ============================================================
# PAGE: ACCUEIL
# ============================================================
def page_accueil(qcm_data, fc_data):
    st.markdown(
        '<div class="hero-section">'
        '<div class="hero-title">✈️ PSY0 Air France</div>'
        '<div class="hero-subtitle">Entraînement complet — Culture aéronautique</div>'
        '<div class="hero-divider"></div></div>',
        unsafe_allow_html=True)
    
    user_data = load_user_data()
    sessions = user_data.get("sessions", [])
    total_q = sum(s["total"] for s in sessions) if sessions else 0
    avg = (sum(s["score"]/s["total"] for s in sessions) / len(sessions) * 100) if sessions else 0
    mastery = user_data.get("flashcard_mastery", {})
    known = sum(1 for v in mastery.values() if v.get("status") == "known")
    
    avg_color = '#34d399' if avg >= 70 else '#fbbf24' if avg >= 50 else '#f87171' if sessions else '#a78bfa'
    
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-value">3022</div>
            <div class="stat-label">Questions QCM</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🃏</div>
            <div class="stat-value">2742</div>
            <div class="stat-label">Flashcards</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">{total_q}</div>
            <div class="stat-label">Questions répondues</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value" style="-webkit-text-fill-color:{avg_color}">{avg:.0f}%</div>
            <div class="stat-label">Score moyen</div>
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
        '<div class="hero-section">'
        '<div class="hero-title">📝 Mode QCM</div>'
        '<div class="hero-subtitle">Testez vos connaissances aéronautiques</div>'
        '<div class="hero-divider"></div></div>',
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

    # Timer logic — compute remaining before rendering
    remaining = None
    if timer_s > 0 and not answered:
        elapsed = time.time() - st.session_state.qcm_q_start
        remaining = max(0, timer_s - int(elapsed))
        if remaining == 0:
            st.session_state.qcm_answers.append({
                "question_id": q["id"], "selected": None,
                "correct": False, "time_ms": int(elapsed * 1000),
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
        st.markdown(f"<div style='text-align:right;font-size:1.1rem;font-weight:700;color:#a78bfa;padding-top:0.3rem'>"
                    f"Score: {st.session_state.qcm_score}</div>", unsafe_allow_html=True)
    if col3 is not None and remaining is not None:
        with col3:
            color = "#f87171" if remaining <= 5 else "#fbbf24" if remaining <= 10 else "#48bb78"
            st.markdown(
                f"<div style='text-align:right;font-size:1.4rem;font-weight:800;"
                f"color:{color};padding-top:0.1rem'>⏱ {remaining}s</div>",
                unsafe_allow_html=True,
            )

    # Category + Question
    cat = q.get("category", "Général")
    st.markdown(f'<span class="cat-badge">{cat}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-card"><div class="question-text">{q["question"]}</div></div>',
                unsafe_allow_html=True)

    selected = st.session_state.qcm_selected
    correct_letter = q["answer"]

    if not answered:
        cols = st.columns(2)
        for i, opt in enumerate(q["options"]):
            with cols[i % 2]:
                if st.button(f"**{opt['id'].upper()}** — {opt['text']}", key=f"opt_{idx}_{opt['id']}",
                             use_container_width=True):
                    elapsed = time.time() - st.session_state.qcm_q_start
                    is_correct = opt["id"] == correct_letter
                    if is_correct:
                        st.session_state.qcm_score += 1
                    st.session_state.qcm_answered = True
                    st.session_state.qcm_selected = opt["id"]
                    st.session_state.qcm_answers.append({
                        "question_id": q["id"], "selected": opt["id"],
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
            if is_correct_opt:
                st.markdown(f'<div class="correct-answer">✅ <b>{opt["id"].upper()}</b> — {opt["text"]}</div>',
                            unsafe_allow_html=True)
            elif is_selected:
                st.markdown(f'<div class="wrong-answer">❌ <b>{opt["id"].upper()}</b> — {opt["text"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="neutral-answer"><b>{opt["id"].upper()}</b> — {opt["text"]}</div>',
                            unsafe_allow_html=True)

        if q.get("explanation"):
            st.info(f"💡 {q['explanation']}")

        st.markdown("")
        if st.button("Suivant ➔", type="primary", use_container_width=True):
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
    
    st.markdown("### 🛬 Bilan du vol")
    color_cls = "score-green" if pct >= 80 else "score-yellow" if pct >= 60 else "score-red"
    st.markdown(f'<div class="score-big {color_cls}">{pct:.0f}%</div>'
                f'<p style="text-align:center;color:rgba(255,255,255,0.5);font-size:1.1rem">'
                f'{s["score"]} / {s["total"]} bonnes réponses · {s["duration_seconds"]//60}m{s["duration_seconds"]%60}s</p>',
                unsafe_allow_html=True)
    
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
        <div class="stat-card"><div class="stat-value" style="-webkit-text-fill-color:#48bb78">{known}</div><div class="stat-label">Maîtrisées</div></div>
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
        st.markdown(f"<div style='text-align:right;color:#48bb78;font-weight:700;padding-top:0.3rem'>"
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
    
    st.markdown("### 🃏 Session terminée !")
    color_cls = "score-green" if pct >= 80 else "score-yellow" if pct >= 60 else "score-red"
    st.markdown(f'<div class="score-big {color_cls}">{pct:.0f}%</div>'
                f'<p style="text-align:center;color:rgba(255,255,255,0.5)">'
                f'{known} / {total} cartes maîtrisées</p>', unsafe_allow_html=True)
    
    user_data = load_user_data()
    mastery = user_data.get("flashcard_mastery", {})
    _, fc_data = load_questions_safe()
    total_known = sum(1 for v in mastery.values() if v.get("status") == "known")
    overall = total_known / len(fc_data) * 100 if fc_data else 0
    st.progress(overall / 100, text=f"Maîtrise globale: {total_known}/{len(fc_data)} ({overall:.1f}%)")
    
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
        '<div class="hero-title">📊 Analytics</div>'
        '<div class="hero-subtitle">Analysez vos performances en profondeur</div>'
        '<div class="hero-divider"></div></div>',
        unsafe_allow_html=True)
    
    user_data = load_user_data()
    sessions = user_data.get("sessions", [])
    
    if not sessions:
        st.markdown('<div class="glass-card" style="text-align:center;padding:3rem">'
                    '<span style="font-size:3rem">🎯</span><br><br>'
                    '<span style="font-size:1.1rem;color:rgba(255,255,255,0.5)">'
                    'Complétez au moins un quiz pour voir vos statistiques.</span></div>',
                    unsafe_allow_html=True)
        return
    
    _, fc_data = load_questions_safe()
    q_map = build_q_map()

    plot_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='rgba(255,255,255,0.7)', family='Inter'),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    
    # 1. PROGRESSION
    st.markdown("### 📈 Progression")
    df = pd.DataFrame([{
        "Session": i + 1, "Score (%)": s["score"] / s["total"] * 100,
        "Date": s.get("date", "")[:10],
    } for i, s in enumerate(sessions)])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Session"], y=df["Score (%)"],
        mode='lines+markers',
        line=dict(color='#a78bfa', width=3),
        marker=dict(size=8, color='#667eea', line=dict(width=2, color='#a78bfa')),
        fill='tozeroy', fillcolor='rgba(102,126,234,0.08)',
    ))
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(72,187,120,0.4)",
                  annotation_text="Objectif 80%", annotation_font_color="rgba(72,187,120,0.6)")
    fig.update_layout(**plot_layout, height=350, yaxis_range=[0, 105],
                      xaxis_title="Session #", yaxis_title="Score (%)",
                      xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
                      yaxis=dict(gridcolor='rgba(255,255,255,0.04)'))
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
        st.markdown("### 🎯 Réussite par catégorie")
        if cat_stats:
            cats = list(cat_stats.keys())
            vals = [cat_stats[c]["c"] / cat_stats[c]["t"] * 100 for c in cats]
            fig_r = go.Figure(data=go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', fillcolor='rgba(167,139,250,0.15)',
                line=dict(color='#a78bfa', width=2),
                marker=dict(size=6, color='#667eea'),
            ))
            fig_r.update_layout(**plot_layout, height=380,
                                polar=dict(
                                    radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%",
                                                    gridcolor='rgba(255,255,255,0.06)',
                                                    color='rgba(255,255,255,0.3)'),
                                    angularaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
                                    bgcolor='rgba(0,0,0,0)',
                                ), showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱ Temps moyen / catégorie")
        time_data = []
        for cat, cs in cat_stats.items():
            valid = [t for t in cs["times"] if t > 0]
            if valid: time_data.append({"Catégorie": cat, "Temps (s)": round(sum(valid)/len(valid)/1000, 1)})
        if time_data:
            df_t = pd.DataFrame(time_data).sort_values("Temps (s)")
            fig_t = px.bar(df_t, x="Temps (s)", y="Catégorie", orientation='h',
                           color="Temps (s)", color_continuous_scale=["#48bb78", "#ecc94b", "#fc8181"])
            fig_t.update_layout(**plot_layout, height=380, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_t, use_container_width=True)
    
    # 3. TOP FAILED
    st.markdown("### ❌ Top questions les plus ratées")
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
    st.markdown("### 🃏 Maîtrise flashcards")
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
    st.markdown("### 📋 Historique des sessions")
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
# MAIN
# ============================================================
def main():
    qcm_data, fc_data = load_questions_safe()
    page = render_sidebar(qcm_data, fc_data)
    
    if page == "🏠 Accueil": page_accueil(qcm_data, fc_data)
    elif page == "📝 QCM": page_qcm(qcm_data)
    elif page == "🃏 Flashcards": page_flashcards(fc_data)
    elif page == "📊 Analytics": page_analytics()

if __name__ == "__main__":
    main()

import streamlit as st
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import json
import os
import io
from datetime import datetime

# ── ReportLab imports ────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas as rl_canvas

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ChurnPredict · AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
for k, v in {"logged_in": False, "username": "", "show_signup": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────
# USER STORAGE
# ──────────────────────────────────────────────
USER_FILE = "users.json"
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {"admin": "admin123"}

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f)


# ══════════════════════════════════════════════════════════════════════════════
# AUTH CSS
# ══════════════════════════════════════════════════════════════════════════════
AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif !important;
    margin: 0; padding: 0;
}
html, body { height: 100%; overflow: hidden !important; }

.stApp {
    background: #030b18 !important;
    height: 100vh !important;
    overflow: hidden !important;
}

#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(37,99,235,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37,99,235,0.06) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none; z-index: 0;
}

.stApp::after {
    content: '';
    position: fixed;
    top: -25%; right: -8%;
    width: 50%; height: 65%;
    background: radial-gradient(ellipse, rgba(37,99,235,0.2) 0%, transparent 68%);
    pointer-events: none; z-index: 0;
}

.auth-glow-bl {
    position: fixed;
    bottom: -20%; left: -8%;
    width: 45%; height: 55%;
    background: radial-gradient(ellipse, rgba(14,165,233,0.1) 0%, transparent 65%);
    pointer-events: none; z-index: 0;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    height: 100vh !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stVerticalBlock"] > div { gap: 4px !important; }
div[data-testid="stVerticalBlockSeparator"] { display: none !important; }
.element-container { margin: 0 !important; padding: 0 !important; }

.field-label {
    display: block;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: #4b5563; margin-bottom: 5px; margin-top: 12px;
}
.field-label-first { margin-top: 0 !important; }

div[data-testid="stTextInput"] { margin-bottom: 0 !important; }
div[data-testid="stTextInput"] label { display: none !important; }

div[data-testid="stTextInput"] input {
    background: #0d1f3c !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 11px !important;
    color: #e2e8f0 !important;
    caret-color: #60a5fa !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease;
    width: 100%;
    -webkit-text-fill-color: #e2e8f0 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #4b5563 !important;
    -webkit-text-fill-color: #4b5563 !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] input:focus {
    background: #0d1f3c !important;
    border-color: rgba(59,130,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.2) !important;
    outline: none !important;
    color: #e2e8f0 !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}

div[data-testid="stTextInput"] input:hover {
    background: #0d1f3c !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: #e2e8f0 !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}

div[data-testid="stTextInput"] input:-webkit-autofill,
div[data-testid="stTextInput"] input:-webkit-autofill:hover,
div[data-testid="stTextInput"] input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0px 1000px #0d1f3c inset !important;
    -webkit-text-fill-color: #e2e8f0 !important;
    border-color: rgba(59,130,246,0.5) !important;
    caret-color: #60a5fa !important;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 11px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 11px 0 !important; width: 100% !important;
    cursor: pointer !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.38) !important;
    transition: all 0.2s ease !important;
    margin-top: 2px;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(37,99,235,0.5) !important;
}
div[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

.ghost-btn div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.03) !important;
    color: #475569 !important;
    border: 1.5px solid rgba(255,255,255,0.08) !important;
    box-shadow: none !important;
}
.ghost-btn div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #94a3b8 !important;
    border-color: rgba(255,255,255,0.14) !important;
    transform: none !important; box-shadow: none !important;
}

.auth-divider {
    display: flex; align-items: center; gap: 10px;
    margin: 12px 0;
}
.auth-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.07); }
.auth-divider-text {
    font-size: 10px; color: #334155; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
}

.auth-stats {
    display: flex; margin-top: 16px; padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.auth-stat { flex: 1; text-align: center; }
.auth-stat + .auth-stat { border-left: 1px solid rgba(255,255,255,0.06); }
.auth-stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 18px; font-weight: 700; color: #f1f5f9;
    letter-spacing: -0.02em; line-height: 1.1;
}
.auth-stat-lbl { font-size: 10px; color: #334155; margin-top: 2px; font-weight: 500; }

div[data-testid="stAlert"] {
    border-radius: 9px !important; font-size: 12px !important; margin-top: 4px !important;
}
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD CSS
# ══════════════════════════════════════════════════════════════════════════════
DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif !important;
    color: #e2e8f0 !important;
}

.stApp { background: #030b18 !important; }

.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(37,99,235,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37,99,235,0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none; z-index: 0;
}

.stApp::after {
    content: '';
    position: fixed;
    top: -20%; right: -5%;
    width: 45%; height: 55%;
    background: radial-gradient(ellipse, rgba(37,99,235,0.1) 0%, transparent 68%);
    pointer-events: none; z-index: 0;
}

#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: rgba(8,16,34,0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    width: 288px !important;
    min-width: 288px !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Collapse sidebar"] {
    display: none !important;
    visibility: hidden !important;
}

section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

section[data-testid="stSidebar"] label {
    color: #475569 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: .09em !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #cbd5e1 !important; }

section[data-testid="stSidebar"] input[type="number"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important;
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
}

section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
    background: #3b82f6 !important;
    border-color: #3b82f6 !important;
}

section[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 12px 0 !important;
    width: 100% !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.35) !important;
    -webkit-text-fill-color: #fff !important;
}
section[data-testid="stSidebar"] .stButton:nth-of-type(1) > button:hover {
    box-shadow: 0 6px 24px rgba(37,99,235,0.55) !important;
    transform: translateY(-1px) !important;
}

section[data-testid="stSidebar"] .stButton:nth-of-type(2) > button {
    background: rgba(239,68,68,0.08) !important;
    color: #f87171 !important;
    -webkit-text-fill-color: #f87171 !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 10px 0 !important;
    width: 100% !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton:nth-of-type(2) > button:hover {
    background: rgba(239,68,68,0.14) !important;
    border-color: rgba(239,68,68,0.4) !important;
    transform: none !important;
}

.block-container {
    padding: 0 2rem 3rem !important;
    max-width: 1400px;
}

.cp-card {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
    backdrop-filter: blur(10px);
    transition: border-color 0.25s;
}
.cp-card:hover { border-color: rgba(59,130,246,0.22) !important; }

.cp-metric-label {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .09em;
    color: #334155; margin-bottom: 8px;
}
.cp-metric-value { font-size: 34px; font-weight: 700; line-height: 1; color: #f1f5f9; }
.cp-metric-sub   { font-size: 12px; color: #334155; margin-top: 6px; }

.badge { display: inline-block; font-size: 11px; font-weight: 700; padding: 5px 14px; border-radius: 20px; letter-spacing: .05em; }
.badge-low  { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.badge-med  { background: rgba(234,179,8,0.12);  color: #facc15; border: 1px solid rgba(234,179,8,0.25); }
.badge-high { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }

.cp-page-header {
    background: rgba(8,16,34,0.85);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 16px 2rem;
    margin: 0 -2rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    backdrop-filter: blur(20px);
}
.cp-logo { display: flex; align-items: center; gap: 10px; }
.cp-logo-box {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 800; color: #fff;
    box-shadow: 0 4px 12px rgba(37,99,235,0.4);
}
.cp-logo-text { font-size: 15px; font-weight: 700; color: #f1f5f9; font-family: 'Syne', sans-serif; }
.cp-logo-sub  { font-size: 11px; color: #334155; }

.cp-section {
    font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .1em;
    color: #1e3a5f; margin: 28px 0 14px;
    display: flex; align-items: center; gap: 10px;
}
.cp-section::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.05); }

.insight-chip {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 14px 16px; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.insight-chip:hover { border-color: rgba(59,130,246,0.18); }
.insight-icon {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700; flex-shrink: 0;
}
.insight-warn { background: rgba(234,179,8,0.12);  color: #facc15; }
.insight-ok   { background: rgba(34,197,94,0.12);  color: #4ade80; }
.insight-info { background: rgba(59,130,246,0.12); color: #60a5fa; }
.insight-title { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 3px; }
.insight-desc  { font-size: 12px; color: #475569; line-height: 1.5; }

.action-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.action-chip {
    font-size: 12px; padding: 7px 16px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03); color: #64748b;
}

.sb-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 18px 0 22px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 18px;
}
.sb-brand-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 13px; color: #fff;
    box-shadow: 0 4px 12px rgba(37,99,235,0.4);
}
.sb-section-title {
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #1e3a5f !important;
    font-weight: 600 !important;
    margin: 18px 0 10px !important;
    display: block;
}

.driver-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.driver-name { font-size: 11px; color: #475569; width: 84px; flex-shrink: 0; text-align: right; }
.driver-track { flex: 1; background: rgba(255,255,255,0.05); border-radius: 3px; height: 6px; }
.driver-fill  { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #1d4ed8, #60a5fa); }
.driver-pct   { font-size: 10px; color: #334155; width: 30px; }

.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #64748b !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    padding: 9px 20px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(59,130,246,0.08) !important;
    border-color: rgba(59,130,246,0.25) !important;
    color: #60a5fa !important;
}

div[data-testid="stAlert"] { border-radius: 10px !important; font-size: 13px !important; }

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary { color: #64748b !important; }
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# CARD HTML helper
# ══════════════════════════════════════════════════════════════════════════════
def _card_header(title: str, subtitle: str) -> str:
    return f"""
    <div style="
        background: rgba(10,20,40,0.88);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 28px 30px 20px;
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        box-shadow: 0 0 0 1px rgba(37,99,235,0.13),
                    0 20px 60px rgba(0,0,0,0.65),
                    inset 0 1px 0 rgba(255,255,255,0.05);
        margin-bottom: 0;
    ">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
        <div style="
            width:36px;height:36px;
            background:linear-gradient(135deg,#3b82f6,#1d4ed8);
            border-radius:9px;
            display:flex;align-items:center;justify-content:center;
            font-size:12px;font-weight:800;color:#fff;
            font-family:'Syne',sans-serif;
            box-shadow:0 4px 14px rgba(37,99,235,0.45);
            flex-shrink:0;">CP</div>
        <span style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
                     color:#f1f5f9;letter-spacing:-0.02em;">ChurnPredict</span>
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;
                  color:#f8fafc;letter-spacing:-0.03em;line-height:1.1;margin-bottom:4px;">
        {title}
      </div>
      <div style="font-size:12.5px;color:#475569;font-weight:400;">{subtitle}</div>
    </div>
    """


# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def make_matplotlib_pie(prob_pct, stay_pct):
    """Return a PNG bytes buffer of the pie chart."""
    fig, ax = plt.subplots(figsize=(3.2, 2.6), facecolor="#0a1428")
    ax.set_facecolor("#0a1428")
    wedge_props = dict(width=0.58, edgecolor="#0a1428", linewidth=2)
    ax.pie(
        [prob_pct, stay_pct],
        labels=["Churn", "Stay"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#f87171", "#4ade80"],
        wedgeprops=wedge_props,
        textprops=dict(fontsize=9, color="#94a3b8"),
    )
    ax.set_title("Churn vs Stay", fontsize=10, fontweight="600",
                 color="#e2e8f0", pad=8)
    plt.tight_layout(pad=0.4)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#0a1428")
    plt.close(fig)
    buf.seek(0)
    return buf


def make_matplotlib_bar(prob_pct, stay_pct):
    """Return a PNG bytes buffer of the bar chart."""
    fig, ax = plt.subplots(figsize=(3.2, 2.6), facecolor="#0a1428")
    ax.set_facecolor("#0a1428")
    bars = ax.bar(["Stay", "Churn"], [stay_pct, prob_pct],
                  color=["#4ade80", "#f87171"], width=0.45,
                  edgecolor="none", alpha=0.9)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 1.5,
                f"{h:.1f}%", ha="center", va="bottom",
                fontsize=8, fontweight="600", color="#e2e8f0")
    ax.set_ylim(0, 115)
    ax.set_ylabel("Probability (%)", fontsize=8, color="#64748b")
    ax.tick_params(colors="#64748b", labelsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.yaxis.grid(True, color="#1e3a5f", linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_title("Probability Comparison", fontsize=10,
                 fontweight="600", color="#e2e8f0", pad=8)
    plt.tight_layout(pad=0.4)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#0a1428")
    plt.close(fig)
    buf.seek(0)
    return buf


def make_matplotlib_importance(feature_names, importances):
    """Return a PNG bytes buffer of the horizontal bar importance chart."""
    sorted_feat = sorted(zip(feature_names, importances), key=lambda x: x[1])
    f_names, f_vals = zip(*sorted_feat)
    max_v = max(f_vals)

    fig, ax = plt.subplots(figsize=(5.5, 3.5), facecolor="#0a1428")
    ax.set_facecolor("#0a1428")
    bar_colors = ["#3b82f6" if v == max_v else "#1e3a5f" for v in f_vals]
    bars = ax.barh(f_names, f_vals, color=bar_colors,
                   edgecolor="none", height=0.55)
    for b in bars:
        ax.text(b.get_width() + 0.0008,
                b.get_y() + b.get_height() / 2,
                f"{b.get_width():.3f}",
                va="center", ha="left", fontsize=7.5, color="#64748b")
    ax.set_xlabel("Importance score", fontsize=8, color="#64748b")
    ax.tick_params(colors="#64748b", labelsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.xaxis.grid(True, color="#1e3a5f", linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Feature Importance", fontsize=10,
                 fontweight="600", color="#e2e8f0", pad=8)
    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="#0a1428")
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Colour palette ────────────────────────────────────────────────────────────
PDF_BG          = colors.HexColor("#030b18")
PDF_CARD        = colors.HexColor("#0a1428")
PDF_BORDER      = colors.HexColor("#1e3a5f")
PDF_BLUE        = colors.HexColor("#3b82f6")
PDF_BLUE_DARK   = colors.HexColor("#1d4ed8")
PDF_TEXT        = colors.HexColor("#e2e8f0")
PDF_MUTED       = colors.HexColor("#475569")
PDF_SUBTLE      = colors.HexColor("#334155")
PDF_GREEN       = colors.HexColor("#4ade80")
PDF_RED         = colors.HexColor("#f87171")
PDF_YELLOW      = colors.HexColor("#facc15")
PDF_WHITE       = colors.white


def _hex_risk_color(risk):
    return {
        "LOW":    PDF_GREEN,
        "MEDIUM": PDF_YELLOW,
        "HIGH":   PDF_RED,
    }.get(risk, PDF_TEXT)


class NumberedCanvas(rl_canvas.Canvas):
    """Canvas subclass that draws header & footer on every page."""
    def __init__(self, *args, **kwargs):
        self._username = kwargs.pop("username", "")
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_chrome(num_pages)
            super().showPage()
        super().save()

    def _draw_page_chrome(self, page_count):
        W, H = A4
        # ── Dark header bar ───────────────────────────────────────────
        self.setFillColor(PDF_CARD)
        self.rect(0, H - 28*mm, W, 28*mm, fill=1, stroke=0)

        # Blue accent stripe
        self.setFillColor(PDF_BLUE)
        self.rect(0, H - 29*mm, W, 1*mm, fill=1, stroke=0)

        # Logo box
        self.setFillColor(PDF_BLUE)
        self.roundRect(14*mm, H - 22*mm, 12*mm, 12*mm, 2*mm, fill=1, stroke=0)
        self.setFillColor(PDF_WHITE)
        self.setFont("Helvetica-Bold", 9)
        self.drawCentredString(20*mm, H - 17.5*mm, "CP")

        # Brand name
        self.setFillColor(PDF_TEXT)
        self.setFont("Helvetica-Bold", 13)
        self.drawString(29*mm, H - 16*mm, "ChurnPredict")
        self.setFillColor(PDF_MUTED)
        self.setFont("Helvetica", 8)
        self.drawString(29*mm, H - 20.5*mm, "AI Customer Analytics · Confidential Report")

        # Generated date (right side)
        self.setFillColor(PDF_SUBTLE)
        self.setFont("Helvetica", 8)
        dt = datetime.now().strftime("%d %b %Y, %H:%M")
        self.drawRightString(W - 14*mm, H - 15*mm, f"Generated: {dt}")
        if self._username:
            self.drawRightString(W - 14*mm, H - 20*mm, f"User: {self._username}")

        # ── Footer ────────────────────────────────────────────────────
        self.setFillColor(PDF_CARD)
        self.rect(0, 0, W, 14*mm, fill=1, stroke=0)
        self.setFillColor(PDF_BORDER)
        self.rect(0, 14*mm, W, 0.3*mm, fill=1, stroke=0)

        self.setFillColor(PDF_SUBTLE)
        self.setFont("Helvetica", 7.5)
        self.drawString(14*mm, 5*mm, "ChurnPredict v2.0  ·  Built by Tharun  ·  AI Portfolio")
        self.drawRightString(W - 14*mm, 5*mm,
                             f"Page {self._pageNumber} of {page_count}")


def generate_pdf_report(
    prob_pct, stay_pct, risk,
    credit_score, country, gender, age, tenure,
    balance, products_number, credit_card,
    active_member, estimated_salary,
    feature_names, importances,
    msg, sub, username,
):
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=14*mm,
        rightMargin=14*mm,
        topMargin=34*mm,
        bottomMargin=20*mm,
        title="ChurnPredict Report",
        author="ChurnPredict AI",
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ─────────────────────────────────────────────────────
    S = {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold",
                             fontSize=20, textColor=PDF_TEXT,
                             spaceAfter=4, leading=24),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold",
                             fontSize=13, textColor=PDF_TEXT,
                             spaceAfter=4, spaceBefore=10, leading=18),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold",
                                  fontSize=8, textColor=PDF_BLUE,
                                  spaceAfter=4, spaceBefore=14,
                                  leading=10, letterSpacing=1.5),
        "body": ParagraphStyle("body", fontName="Helvetica",
                               fontSize=9, textColor=PDF_MUTED,
                               leading=14, spaceAfter=3),
        "label": ParagraphStyle("label", fontName="Helvetica-Bold",
                                fontSize=7.5, textColor=PDF_SUBTLE,
                                leading=10),
        "big_num": ParagraphStyle("big_num", fontName="Helvetica-Bold",
                                  fontSize=28, textColor=PDF_TEXT,
                                  leading=32),
        "badge": ParagraphStyle("badge", fontName="Helvetica-Bold",
                                fontSize=11, alignment=TA_CENTER,
                                leading=16),
        "decision_title": ParagraphStyle("decision_title",
                                         fontName="Helvetica-Bold",
                                         fontSize=13, textColor=PDF_TEXT,
                                         leading=18, spaceAfter=4),
        "decision_body": ParagraphStyle("decision_body",
                                        fontName="Helvetica",
                                        fontSize=9.5, textColor=PDF_MUTED,
                                        leading=15),
        "insight_title": ParagraphStyle("insight_title",
                                        fontName="Helvetica-Bold",
                                        fontSize=9.5, textColor=PDF_TEXT,
                                        leading=13, spaceAfter=2),
        "insight_body": ParagraphStyle("insight_body",
                                       fontName="Helvetica",
                                       fontSize=8.5, textColor=PDF_MUTED,
                                       leading=13),
        "center": ParagraphStyle("center", fontName="Helvetica",
                                 fontSize=9, textColor=PDF_MUTED,
                                 alignment=TA_CENTER, leading=13),
        "table_hdr": ParagraphStyle("table_hdr", fontName="Helvetica-Bold",
                                    fontSize=8, textColor=PDF_BLUE,
                                    leading=11),
        "table_val": ParagraphStyle("table_val", fontName="Helvetica",
                                    fontSize=9, textColor=PDF_TEXT,
                                    leading=13),
    }

    prob_color  = PDF_RED  if prob_pct >= 50 else PDF_GREEN
    risk_color  = _hex_risk_color(risk)
    story       = []

    # ══════════════════════════════════════════════
    # PAGE 1 — Hero + Customer Profile
    # ══════════════════════════════════════════════

    # Title block
    story.append(Paragraph("Customer Churn Analysis", S["h1"]))
    story.append(Paragraph(
        f"Prediction report for {username}  ·  {datetime.now().strftime('%d %B %Y')}",
        S["body"],
    ))
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=PDF_BORDER, spaceAfter=14))

    # ── KPI cards row ──────────────────────────────
    story.append(Paragraph("PREDICTION OVERVIEW", S["section"]))

    def kpi_cell(label, value, sub_text, val_color=PDF_TEXT):
        return [
            Paragraph(label.upper(), S["label"]),
            Paragraph(f'<font color="#{val_color.hexval()[2:] if hasattr(val_color,"hexval") else "f1f5f9"}">{value}</font>',
                      ParagraphStyle("kv", fontName="Helvetica-Bold",
                                     fontSize=26, textColor=val_color, leading=30)),
            Paragraph(sub_text, S["body"]),
        ]

    # Helper: render colour without .hexval
    def hex_str(c):
        return c.hexval()[1:] if hasattr(c, "hexval") else "f1f5f9"

    kpi_data = [
        [
            [Paragraph("CHURN PROBABILITY", S["label"]),
             Paragraph(f"{prob_pct}%",
                       ParagraphStyle("kv", fontName="Helvetica-Bold",
                                      fontSize=26, textColor=prob_color, leading=30)),
             Paragraph("Above 50% threshold" if prob_pct >= 50 else "Below 50% threshold", S["body"])],

            [Paragraph("RETENTION SCORE", S["label"]),
             Paragraph(f"{stay_pct}%",
                       ParagraphStyle("kv", fontName="Helvetica-Bold",
                                      fontSize=26, textColor=PDF_GREEN, leading=30)),
             Paragraph("Likelihood to stay", S["body"])],

            [Paragraph("RISK LEVEL", S["label"]),
             Paragraph(risk,
                       ParagraphStyle("kv", fontName="Helvetica-Bold",
                                      fontSize=26, textColor=risk_color, leading=30)),
             Paragraph("Overall risk assessment", S["body"])],

            [Paragraph("CUSTOMER TENURE", S["label"]),
             Paragraph(f"{tenure} yrs",
                       ParagraphStyle("kv", fontName="Helvetica-Bold",
                                      fontSize=26, textColor=PDF_BLUE, leading=30)),
             Paragraph("Years with the bank", S["body"])],
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=["25%", "25%", "25%", "25%"])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PDF_CARD),
        ("BOX",           (0, 0), (-1, -1), 0.5, PDF_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, PDF_BORDER),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [PDF_CARD]),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), [4, 4, 4, 4]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # ── Customer profile table ─────────────────────
    story.append(Paragraph("CUSTOMER PROFILE", S["section"]))

    profile_rows = [
        [Paragraph("Field", S["table_hdr"]),
         Paragraph("Value", S["table_hdr"]),
         Paragraph("Field", S["table_hdr"]),
         Paragraph("Value", S["table_hdr"])],
        [Paragraph("Country",        S["body"]), Paragraph(country,                        S["table_val"]),
         Paragraph("Gender",         S["body"]), Paragraph(gender,                         S["table_val"])],
        [Paragraph("Age",            S["body"]), Paragraph(str(age),                       S["table_val"]),
         Paragraph("Tenure",         S["body"]), Paragraph(f"{tenure} years",              S["table_val"])],
        [Paragraph("Credit Score",   S["body"]), Paragraph(str(credit_score),              S["table_val"]),
         Paragraph("# Products",     S["body"]), Paragraph(str(products_number),           S["table_val"])],
        [Paragraph("Balance (EUR)",  S["body"]), Paragraph(f"{balance:,.0f}",              S["table_val"]),
         Paragraph("Est. Salary",    S["body"]), Paragraph(f"EUR {estimated_salary:,.0f}", S["table_val"])],
        [Paragraph("Credit Card",    S["body"]), Paragraph(credit_card,                    S["table_val"]),
         Paragraph("Active Member",  S["body"]), Paragraph(active_member,                  S["table_val"])],
    ]

    col_w = [35*mm, 45*mm, 35*mm, 45*mm]
    prof_table = Table(profile_rows, colWidths=col_w)
    prof_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), PDF_BLUE_DARK),
        ("BACKGROUND",    (0, 1), (-1, -1), PDF_CARD),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [PDF_CARD, colors.HexColor("#0d1f3c")]),
        ("BOX",           (0, 0), (-1, -1), 0.5, PDF_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, PDF_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(prof_table)

    # ══════════════════════════════════════════════
    # PAGE 2 — Charts
    # ══════════════════════════════════════════════
    story.append(Spacer(1, 14))
    story.append(Paragraph("VISUAL ANALYSIS", S["section"]))

    # Generate matplotlib PNGs
    pie_buf  = make_matplotlib_pie(prob_pct, stay_pct)
    bar_buf  = make_matplotlib_bar(prob_pct, stay_pct)
    imp_buf  = make_matplotlib_importance(feature_names, importances)

    pie_img = RLImage(pie_buf,  width=74*mm, height=60*mm)
    bar_img = RLImage(bar_buf,  width=74*mm, height=60*mm)
    imp_img = RLImage(imp_buf,  width=130*mm, height=68*mm)

    chart_row = Table(
        [[pie_img, bar_img]],
        colWidths=[90*mm, 90*mm],
    )
    chart_row.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), PDF_CARD),
        ("BOX",          (0, 0), (-1, -1), 0.5, PDF_BORDER),
        ("INNERGRID",    (0, 0), (-1, -1), 0.4, PDF_BORDER),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    story.append(chart_row)
    story.append(Spacer(1, 10))

    imp_table = Table([[imp_img]], colWidths=[182*mm])
    imp_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), PDF_CARD),
        ("BOX",          (0, 0), (-1, -1), 0.5, PDF_BORDER),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    story.append(imp_table)

    # ══════════════════════════════════════════════
    # PAGE 3 — Insights + Business Decision
    # ══════════════════════════════════════════════
    story.append(Spacer(1, 14))
    story.append(Paragraph("INSIGHTS", S["section"]))

    def insight_row(icon_char, icon_color, title, desc):
        icon_cell = Paragraph(
            f'<font color="#{icon_color[1:]}" size="14"><b>{icon_char}</b></font>',
            ParagraphStyle("ic", fontName="Helvetica-Bold",
                           fontSize=14, textColor=colors.HexColor(icon_color),
                           alignment=TA_CENTER, leading=18),
        )
        text_cell = [
            Paragraph(title, S["insight_title"]),
            Paragraph(desc,  S["insight_body"]),
        ]
        return [icon_cell, text_cell]

    insight_data = []
    if age > 50:
        insight_data.append(insight_row("!", "#facc15", "Older customer – higher risk",
            "Customers over 50 churn at nearly 2x the base rate. Consider proactive outreach."))
    else:
        insight_data.append(insight_row("OK", "#4ade80", "Age factor stable",
            "Customer age is within the lower-risk cohort average."))

    if active_member == "No":
        insight_data.append(insight_row("!", "#facc15", "Inactive member – churn risk",
            "Inactive customers churn 2x more. Consider a personalised re-engagement offer."))
    else:
        insight_data.append(insight_row("OK", "#4ade80", "Active member – good signal",
            "Active membership is a strong predictor of customer retention."))

    if balance > 100_000:
        insight_data.append(insight_row("!", "#facc15", "High balance – monitor closely",
            "High-balance churners represent significant revenue risk for the bank."))
    else:
        insight_data.append(insight_row("i", "#60a5fa", "Balance within normal range",
            "Account balance is at an expected level for this customer profile."))

    if tenure < 4:
        insight_data.append(insight_row("!", "#facc15", "Short tenure – higher churn risk",
            "Fewer than 4 years tenure carries a statistically higher probability of churn."))
    else:
        insight_data.append(insight_row("OK", "#4ade80", "Established customer",
            "Long tenure is one of the strongest signals of customer loyalty and retention."))

    ins_table = Table(insight_data, colWidths=[16*mm, 166*mm])
    ins_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), PDF_CARD),
        ("BOX",          (0, 0), (-1, -1), 0.4, PDF_BORDER),
        ("LINEBELOW",    (0, 0), (-1, -2), 0.3, PDF_BORDER),
        ("ALIGN",        (0, 0), (0,  -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(ins_table)
    story.append(Spacer(1, 14))

    # ── Business Decision ──────────────────────────
    story.append(Paragraph("BUSINESS DECISION", S["section"]))

    prob_val = prob_pct / 100
    if prob_val > 0.7:
        dec_icon = "🚨"
        dec_bg   = colors.HexColor("#1a0808")
        dec_brd  = PDF_RED
        dec_col  = PDF_RED
    elif prob_val > 0.3:
        dec_icon = "⚠"
        dec_bg   = colors.HexColor("#1a1500")
        dec_brd  = PDF_YELLOW
        dec_col  = PDF_YELLOW
    else:
        dec_icon = "✓"
        dec_bg   = colors.HexColor("#081a10")
        dec_brd  = PDF_GREEN
        dec_col  = PDF_GREEN

    dec_data = [[
        Paragraph(f'<font size="20">{dec_icon}</font>',
                  ParagraphStyle("di", fontName="Helvetica-Bold",
                                 fontSize=20, textColor=dec_col,
                                 alignment=TA_CENTER, leading=24)),
        [
            Paragraph(msg, ParagraphStyle("dt", fontName="Helvetica-Bold",
                                          fontSize=12, textColor=dec_col,
                                          leading=16, spaceAfter=4)),
            Paragraph(sub, S["decision_body"]),
        ],
    ]]
    dec_table = Table(dec_data, colWidths=[18*mm, 164*mm])
    dec_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), dec_bg),
        ("BOX",          (0, 0), (-1, -1), 1.2, dec_brd),
        ("ALIGN",        (0, 0), (0,  -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 10))

    # ── Recommended actions ────────────────────────
    story.append(Paragraph("RECOMMENDED ACTIONS", S["section"]))
    actions = ["📧  Send personalised retention offer",
               "🚩  Flag customer for retention team review",
               "👁  Add to 30-day monitoring watchlist"]
    action_rows = [[Paragraph(a, S["body"])] for a in actions]
    act_table = Table(action_rows, colWidths=[182*mm])
    act_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PDF_CARD),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [PDF_CARD, colors.HexColor("#0d1f3c")]),
        ("BOX",           (0, 0), (-1, -1), 0.4, PDF_BORDER),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.3, PDF_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(act_table)

    # ── Disclaimer ────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", thickness=0.4, color=PDF_BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This report is generated by ChurnPredict AI and is intended for internal business use only. "
        "Predictions are based on a trained machine-learning model and should be reviewed by a "
        "qualified analyst before acting on the recommendations.",
        ParagraphStyle("disc", fontName="Helvetica-Oblique",
                       fontSize=7.5, textColor=PDF_SUBTLE,
                       leading=11, alignment=TA_CENTER),
    ))

    # ── Build with custom canvas ───────────────────
    doc.build(
        story,
        canvasmaker=lambda *a, **kw: NumberedCanvas(*a, username=username, **kw),
    )
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_login():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-glow-bl"></div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([1.3, 1, 1.3])

    with mid:
        st.markdown(_card_header("Welcome back", "Sign in to your AI dashboard"),
                    unsafe_allow_html=True)

        # st.form lets Enter key submit the form
        with st.form(key="login_form", border=False):
            st.markdown('<span class="field-label field-label-first" style="margin-top:14px;">Username</span>',
                        unsafe_allow_html=True)
            username = st.text_input("u", placeholder="Enter your username",
                                     label_visibility="collapsed", key="li_user")

            st.markdown('<span class="field-label">Password</span>', unsafe_allow_html=True)
            password = st.text_input("p", type="password", placeholder="••••••••",
                                     label_visibility="collapsed", key="li_pass")

            st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Sign in →", use_container_width=True)

        if submitted:
            if username in users and users[username] == password:
                st.session_state.logged_in   = True
                st.session_state.username    = username
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error("Incorrect username or password.")

        st.markdown("""
        <div class="auth-divider">
          <div class="auth-divider-line"></div>
          <span class="auth-divider-text">or</span>
          <div class="auth-divider-line"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Create new account", key="goto_signup", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="auth-stats">
          <div class="auth-stat">
            <div class="auth-stat-val">94%</div>
            <div class="auth-stat-lbl">Accuracy</div>
          </div>
          <div class="auth-stat">
            <div class="auth-stat-val">2.3×</div>
            <div class="auth-stat-lbl">Retention lift</div>
          </div>
          <div class="auth-stat">
            <div class="auth-stat-val">10k+</div>
            <div class="auth-stat-lbl">Customers</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function applyCenter() {
        var doc = window.parent.document;
        var bc = doc.querySelector('.block-container');
        if (bc) bc.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;height:100vh !important;padding:0 !important;max-width:100% !important;overflow:hidden !important;';
        var colRow = doc.querySelector('[data-testid="stHorizontalBlock"]');
        if (colRow) colRow.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;width:100% !important;height:100vh !important;';
    })();
    setTimeout(function() {
        var doc = window.parent.document;
        var bc = doc.querySelector('.block-container');
        if (bc) bc.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;height:100vh !important;padding:0 !important;';
    }, 300);
    </script>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIGNUP PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_signup():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-glow-bl"></div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([1.3, 1, 1.3])

    with mid:
        st.markdown(_card_header("Create account", "Get access to the AI dashboard"),
                    unsafe_allow_html=True)

        with st.form(key="signup_form", border=False):
            st.markdown('<span class="field-label" style="margin-top:14px;">Username</span>',
                        unsafe_allow_html=True)
            new_user = st.text_input("nu", placeholder="Choose a username",
                                     label_visibility="collapsed", key="su_user")

            st.markdown('<span class="field-label">Password</span>', unsafe_allow_html=True)
            new_pass = st.text_input("np", type="password", placeholder="Choose a password",
                                     label_visibility="collapsed", key="su_pass")

            st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

            submitted_signup = st.form_submit_button("Create account →", use_container_width=True)

        if submitted_signup:
            if len(new_user) < 3:
                st.warning("Username must be at least 3 characters.")
            elif len(new_pass) < 4:
                st.warning("Password must be at least 4 characters.")
            elif new_user in users:
                st.warning("Username already taken.")
            else:
                users[new_user] = new_pass
                save_users()
                st.success("Account created! Sign in now.")
                st.session_state.show_signup = False
                st.rerun()

        st.markdown("""
        <div class="auth-divider">
          <div class="auth-divider-line"></div>
          <span class="auth-divider-text">or</span>
          <div class="auth-divider-line"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Back to sign in", key="back_btn", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function applyCenter() {
        var doc = window.parent.document;
        var bc = doc.querySelector('.block-container');
        if (bc) bc.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;height:100vh !important;padding:0 !important;';
        var colRow = doc.querySelector('[data-testid="stHorizontalBlock"]');
        if (colRow) colRow.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;width:100% !important;height:100vh !important;';
    })();
    setTimeout(function() {
        var doc = window.parent.document;
        var bc = doc.querySelector('.block-container');
        if (bc) bc.style.cssText += 'display:flex !important;align-items:center !important;justify-content:center !important;height:100vh !important;padding:0 !important;';
    }, 300);
    </script>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# AUTH GUARD
# ──────────────────────────────────────────────
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        render_signup()
    else:
        render_login()
    st.stop()

# ──────────────────────────────────────────────
# SIDEBAR FIX
# ──────────────────────────────────────────────
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    width: auto !important;
    min-width: 244px !important;
    pointer-events: auto !important;
}
[data-testid="collapsedControl"] { display: flex !important; }
</style>
<script>
(function forceSidebar() {
    function show() {
        var doc = window.parent ? window.parent.document : document;
        var sb = doc.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            sb.style.cssText = sb.style.cssText
                .replace(/display\s*:\s*none\s*!important/gi, 'display: flex !important')
                .replace(/visibility\s*:\s*hidden/gi, 'visibility: visible');
            sb.style.setProperty('display', 'flex', 'important');
            sb.style.setProperty('visibility', 'visible', 'important');
            sb.style.setProperty('opacity', '1', 'important');
            sb.style.setProperty('transform', 'none', 'important');
        }
    }
    show();
    setTimeout(show, 50);
    setTimeout(show, 200);
    setTimeout(show, 500);
})();
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    mdl = pickle.load(open("model.pkl", "rb"))
    scl = pickle.load(open("scaler.pkl", "rb"))
    return mdl, scl

model, scaler = load_model()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
      <div class="sb-brand-icon">CP</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:#f1f5f9;
                    font-family:'Syne',sans-serif;letter-spacing:-0.01em;">ChurnPredict</div>
        <div style="font-size:11px;color:#334155;">AI Dashboard</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-section-title">Customer Profile</span>', unsafe_allow_html=True)

    credit_score     = st.slider("Credit Score", 300, 900, 600)
    country          = st.selectbox("Country", ["France", "Spain", "Germany"])
    gender           = st.selectbox("Gender", ["Female", "Male"])
    age              = st.slider("Age", 18, 90, 30)
    tenure           = st.slider("Tenure (years)", 0, 10, 3)
    balance          = st.number_input("Balance (EUR)", 0.0, 300000.0, 50000.0, step=1000.0)
    products_number  = st.slider("Number of Products", 1, 4, 1)
    credit_card      = st.selectbox("Has Credit Card", ["No", "Yes"])
    active_member    = st.selectbox("Active Member", ["No", "Yes"])
    estimated_salary = st.number_input("Est. Salary (EUR)", 0.0, 200000.0, 50000.0, step=1000.0)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    predict_clicked = st.button("🔍  Run Prediction", use_container_width=True)

    st.markdown(f"""
    <div style="margin-top:18px;padding:12px 14px;
                background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;">
      <div style="font-size:9px;color:#1e3a5f;text-transform:uppercase;
                  letter-spacing:.09em;font-weight:600;margin-bottom:5px;">Signed in as</div>
      <div style="font-size:13px;color:#60a5fa;font-weight:600;">
        👤 {st.session_state.username}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("⎋  Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.rerun()


# ── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cp-page-header">
  <div class="cp-logo">
    <div class="cp-logo-box">CP</div>
    <div>
      <div class="cp-logo-text">ChurnPredict</div>
      <div class="cp-logo-sub">AI Customer Analytics</div>
    </div>
  </div>
  <div style="font-size:12px;color:#334155;">
    Welcome back,&nbsp;<span style="color:#60a5fa;font-weight:600;">{st.session_state.username}</span>
  </div>
</div>
""", unsafe_allow_html=True)

country_map = {"France": 0, "Spain": 1, "Germany": 2}
gender_map  = {"Female": 0, "Male": 1}
binary_map  = {"No": 0, "Yes": 1}


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
if predict_clicked:
    input_data = np.array([[
        credit_score, country_map[country], gender_map[gender],
        age, tenure, balance, products_number,
        binary_map[credit_card], binary_map[active_member], estimated_salary
    ]])

    with st.spinner("Analysing customer data..."):
        input_scaled = scaler.transform(input_data)
        prob = float(model.predict_proba(input_scaled)[0][1])

    prob_pct = round(prob * 100, 1)
    stay_pct = round(100 - prob_pct, 1)

    if prob < 0.3:   risk, risk_class = "LOW",    "badge-low"
    elif prob < 0.7: risk, risk_class = "MEDIUM", "badge-med"
    else:            risk, risk_class = "HIGH",   "badge-high"

    # ── KPI Row ──
    st.markdown('<div class="cp-section">Overview</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    prob_color = "#f87171" if prob > 0.5 else "#4ade80"
    with k1:
        st.markdown(f"""<div class="cp-card">
          <div class="cp-metric-label">Churn Probability</div>
          <div class="cp-metric-value" style="color:{prob_color};">{prob_pct}%</div>
          <div class="cp-metric-sub">{'⚠ Above' if prob>0.5 else '✓ Below'} 50% threshold</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="cp-card">
          <div class="cp-metric-label">Retention Score</div>
          <div class="cp-metric-value" style="color:#4ade80;">{stay_pct}%</div>
          <div class="cp-metric-sub">Likelihood to stay</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="cp-card">
          <div class="cp-metric-label">Risk Level</div>
          <div style="margin-top:10px;">
            <span class="badge {risk_class}" style="font-size:14px;padding:6px 18px;">{risk}</span>
          </div>
          <div class="cp-metric-sub" style="margin-top:12px;">Overall assessment</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="cp-card">
          <div class="cp-metric-label">Customer Tenure</div>
          <div class="cp-metric-value" style="color:#60a5fa;">{tenure} yrs</div>
          <div class="cp-metric-sub">Years with bank</div>
        </div>""", unsafe_allow_html=True)

    # ── Charts Row ──
    st.markdown('<div class="cp-section">Distribution & Comparison</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns(3)

    PLOT_BG = "#060f20"

    with ch1:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(4, 3.2))
        fig1.patch.set_facecolor(PLOT_BG)
        ax1.set_facecolor(PLOT_BG)
        ax1.pie([prob_pct, stay_pct],
                labels=["Churn", "Stay"],
                autopct="%1.1f%%",
                startangle=90,
                colors=["#f87171", "#4ade80"],
                wedgeprops=dict(width=0.62, edgecolor=PLOT_BG, linewidth=2),
                textprops=dict(fontsize=11, color='#64748b'))
        ax1.set_title("Churn vs Stay", fontsize=12, fontweight='600',
                      pad=12, color='#e2e8f0')
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)
        plt.close(fig1)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(4, 3.2))
        fig2.patch.set_facecolor(PLOT_BG)
        ax2.set_facecolor(PLOT_BG)
        bars = ax2.bar(["Stay", "Churn"], [stay_pct, prob_pct],
                       color=["#4ade80", "#f87171"],
                       width=0.48, edgecolor='none', alpha=0.9)
        for b in bars:
            h = b.get_height()
            ax2.text(b.get_x()+b.get_width()/2, h+1.5,
                     f"{h:.1f}%", ha='center', va='bottom',
                     fontsize=10, fontweight='600', color='#e2e8f0')
        ax2.set_ylim(0, 115)
        ax2.set_ylabel("Probability (%)", fontsize=10, color='#334155')
        ax2.tick_params(colors='#334155', labelsize=10)
        for sp in ax2.spines.values(): sp.set_visible(False)
        ax2.yaxis.grid(True, color='#0d1f3c', linestyle='--', linewidth=0.8)
        ax2.set_axisbelow(True)
        ax2.set_title("Probability Comparison", fontsize=12,
                      fontweight='600', pad=12, color='#e2e8f0')
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch3:
        feature_names = ["CreditScore","Country","Gender","Age","Tenure",
                         "Balance","Products","CreditCard","ActiveMember","Salary"]
        importances   = model.feature_importances_
        sorted_idx    = np.argsort(importances)[::-1]
        sorted_names  = [feature_names[i] for i in sorted_idx]
        sorted_vals   = importances[sorted_idx]
        max_val       = sorted_vals[0]

        html = '<div class="cp-card"><div style="font-size:13px;font-weight:600;color:#f1f5f9;margin-bottom:16px;">Key Drivers</div>'
        for name, val in zip(sorted_names, sorted_vals):
            pct = round((val / max_val) * 100)
            html += f"""<div class="driver-row">
              <div class="driver-name">{name}</div>
              <div class="driver-track"><div class="driver-fill" style="width:{pct}%"></div></div>
              <div class="driver-pct">{pct}%</div>
            </div>"""
        st.markdown(html + '</div>', unsafe_allow_html=True)

    # ── Feature importance expander ──
    st.markdown('<div class="cp-section">Feature Importance</div>', unsafe_allow_html=True)
    with st.expander("Expand full chart", expanded=False):
        fig3, ax3 = plt.subplots(figsize=(9, 4))
        fig3.patch.set_facecolor(PLOT_BG)
        ax3.set_facecolor(PLOT_BG)
        sorted_feat = sorted(zip(feature_names, importances), key=lambda x: x[1])
        f_names, f_vals = zip(*sorted_feat)
        max_v = max(f_vals)
        colors3 = ['#3b82f6' if v == max_v else '#1e3a5f' for v in f_vals]
        bars3 = ax3.barh(f_names, f_vals, color=colors3, edgecolor='none', height=0.55)
        for b in bars3:
            ax3.text(b.get_width()+0.001, b.get_y()+b.get_height()/2,
                     f"{b.get_width():.3f}", va='center', ha='left',
                     fontsize=9, color='#475569')
        ax3.set_xlabel("Importance score", fontsize=10, color='#334155')
        ax3.tick_params(colors='#334155', labelsize=10)
        for sp in ax3.spines.values(): sp.set_visible(False)
        ax3.xaxis.grid(True, color='#0d1f3c', linestyle='--', linewidth=0.8)
        ax3.set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close(fig3)

    # ── Insights ──
    st.markdown('<div class="cp-section">Insights</div>', unsafe_allow_html=True)

    def insight(kind, title, desc):
        icons = {
            "warn": ("⚠", "insight-warn"),
            "ok":   ("✓", "insight-ok"),
            "info": ("i", "insight-info")
        }
        sym, cls = icons[kind]
        return f"""<div class="insight-chip">
          <div class="insight-icon {cls}">{sym}</div>
          <div>
            <div class="insight-title">{title}</div>
            <div class="insight-desc">{desc}</div>
          </div>
        </div>"""

    age_ins     = insight("warn","Older customer – higher risk",
                          "Customers over 50 churn at nearly 2× the base rate.") \
                  if age > 50 else \
                  insight("ok","Age factor stable",
                          "Customer age is within the lower-risk cohort average.")
    active_ins  = insight("warn","Inactive member – churn risk",
                          "Inactive customers churn 2× more. Consider a re-engagement offer.") \
                  if active_member == "No" else \
                  insight("ok","Active member – good signal",
                          "Active membership strongly predicts retention.")
    balance_ins = insight("warn","High balance – monitor",
                          "High-balance churners represent significant revenue loss.") \
                  if balance > 100000 else \
                  insight("info","Balance is normal",
                          "Account balance within expected range.")
    tenure_ins  = insight("warn","Short tenure",
                          "Fewer than 4 years tenure carries a statistically higher churn risk.") \
                  if tenure < 4 else \
                  insight("ok","Established customer",
                          "Long tenure is a strong retention signal.")

    ins1, ins2 = st.columns(2)
    with ins1: st.markdown(age_ins + balance_ins, unsafe_allow_html=True)
    with ins2: st.markdown(active_ins + tenure_ins, unsafe_allow_html=True)

    # ── Business decision ──
    st.markdown('<div class="cp-section">Business Decision</div>', unsafe_allow_html=True)

    if prob > 0.7:
        bg, border, txt = "rgba(239,68,68,0.08)", "rgba(239,68,68,0.25)", "#f87171"
        icon, msg = "🚨", "Immediate retention action required"
        sub = "High churn probability. Escalate to the retention team and issue a personalised offer immediately."
    elif prob > 0.3:
        bg, border, txt = "rgba(234,179,8,0.08)", "rgba(234,179,8,0.25)", "#facc15"
        icon, msg = "⚠️", "Monitor engagement closely"
        sub = "Churn risk is elevated. Schedule a check-in and consider a loyalty incentive over the next 30 days."
    else:
        bg, border, txt = "rgba(34,197,94,0.08)", "rgba(34,197,94,0.25)", "#4ade80"
        icon, msg = "✅", "Customer appears stable"
        sub = "Low churn risk. Maintain regular engagement and review at the next cycle."

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:14px;
                padding:22px 26px;display:flex;align-items:flex-start;gap:16px;">
      <div style="font-size:24px;line-height:1;flex-shrink:0;">{icon}</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:{txt};margin-bottom:6px;">{msg}</div>
        <div style="font-size:13px;color:#475569;line-height:1.65;">{sub}</div>
      </div>
    </div>
    <div class="action-row">
      <div class="action-chip">📧 Send retention offer</div>
      <div class="action-chip">🚩 Flag for review</div>
      <div class="action-chip">👁 Add to watchlist</div>
    </div>
    <div style='height:20px'></div>
    """, unsafe_allow_html=True)

    # ── PDF Report download ───────────────────────────────────────────────────
    st.markdown('<div class="cp-section">Export Report</div>', unsafe_allow_html=True)

    with st.spinner("Generating PDF report..."):
        pdf_bytes = generate_pdf_report(
            prob_pct=prob_pct,
            stay_pct=stay_pct,
            risk=risk,
            credit_score=credit_score,
            country=country,
            gender=gender,
            age=age,
            tenure=tenure,
            balance=balance,
            products_number=products_number,
            credit_card=credit_card,
            active_member=active_member,
            estimated_salary=estimated_salary,
            feature_names=feature_names,
            importances=importances,
            msg=msg,
            sub=sub,
            username=st.session_state.username,
        )

    fname = f"ChurnPredict_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    st.download_button(
        label="📄  Download PDF Report",
        data=pdf_bytes,
        file_name=fname,
        mime="application/pdf",
        use_container_width=True,
    )


# ── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid rgba(255,255,255,0.05);margin-top:48px;padding-top:18px;
            display:flex;align-items:center;justify-content:space-between;">
  <div style="font-size:12px;color:#1e3a5f;">
    Built by <strong style="color:#334155;">Tharun</strong> · AI Portfolio
  </div>
  <div style="font-size:12px;color:#0d1f3c;">ChurnPredict v2.0</div>
</div>
""", unsafe_allow_html=True)
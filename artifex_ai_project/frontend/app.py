"""
ArtifexAI Enhanced Frontend — POLISHED SINGLE FILE
- Clear, modern UI/UX with glassmorphism + subtle gradients
- Robust session-state (no weird reruns, no duplicate button clashes)
- Reliable image-feature auto-fill flow
- Safer API calls (timeouts, messages)
- Beautiful Results + export (PDF or text)
"""

import os
import io
import time
import json
import base64
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Optional

import requests
import streamlit as st
from PIL import Image

# ────────────────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ArtifexAI — Art Auction Price Predictor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

@dataclass
class FrontendConfig:
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: tuple[str, ...] = ("image/jpeg", "image/png", "image/jpg")
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 2
    HERO_IMAGE: str = "url('img/123.jpg')"  # you can swap to a local asset

config = FrontendConfig()

API = {
    "health": f"{config.API_BASE_URL}/health",
    "predict": f"{config.API_BASE_URL}/predict",
    "analyze_image": f"{config.API_BASE_URL}/analyze-image",
    "model_info": f"{config.API_BASE_URL}/model/info",
}

def get_starry_night_base64():
    """Convert The Starry Night image to base64 for embedding"""
    try:
        image_path = "img/night.jpg"
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            # Fallback: return empty string if image not found
            return ""
    except Exception:
        return ""

# Optional PDF export - ReportLab is installed and working
REPORTLAB = True
A4 = canvas = cm = ImageReader = HexColor = getSampleStyleSheet = ParagraphStyle = SimpleDocTemplate = Paragraph = Spacer = Table = TableStyle = colors = None

# Import ReportLab modules
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
print("ReportLab successfully imported for PDF generation")


# ────────────────────────────────────────────────────────────────────────────────
# GLOBAL STATE (safe defaults)
# ────────────────────────────────────────────────────────────────────────────────

def _init_state():
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("image_features", {})
    st.session_state.setdefault("prediction", {})
    st.session_state.setdefault("inputs", {})
    st.session_state.setdefault("uploaded_image", None)          # PIL image
    st.session_state.setdefault("uploaded_file_raw", None)       # original uploader object
    st.session_state.setdefault("colorfulness_score", 0.0)
    st.session_state.setdefault("svd_entropy", 0.0)

def clear_image_state():
    """Clear all image-related state consistently"""
    st.session_state.uploaded_image = None
    st.session_state.uploaded_file_raw = None
    st.session_state.image_features = {}
    st.session_state.colorfulness_score = 0.0
    st.session_state.svd_entropy = 0.0

_init_state()


# ────────────────────────────────────────────────────────────────────────────────
# THEME & CSS
# ────────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
:root{
  --bg-1:#0b1220; --bg-2:#0e1626; --card:#0f172a; --muted:#9fb0c7; --text:#e5e7eb;
  --accent:#60a5fa; --accent2:#22d3ee; --accent3:#10b981; --warn:#f59e0b; --pink:#a23b72;
  --shadow:0 20px 60px rgba(0,0,0,.35); --radius:18px;
}
html, body { background: linear-gradient(180deg,var(--bg-1),var(--bg-2)); }
.block-container { padding-top: 1.3rem; }
.glass {
  background: linear-gradient(180deg, rgba(17,24,39,.75), rgba(15,23,42,.6));
  border: 1px solid rgba(255,255,255,.08); border-radius: var(--radius); box-shadow: var(--shadow);
}
.hero {
  height: 72vh; display:flex; align-items:center; justify-content:center;
  border-radius: var(--radius); position: relative; overflow: hidden;
  background:
    radial-gradient(60rem 60rem at -10% -10%, rgba(96,165,250,.18) 0%, transparent 40%),
    radial-gradient(60rem 60rem at 110% 110%, rgba(34,211,238,.18) 0%, transparent 40%),
    linear-gradient(135deg, rgba(59,130,246,.25), rgba(162,59,114,.35)),
    url('img/night.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: var(--shadow);
}
.hero h1 { color: var(--text); font-weight: 800; font-size: 3.5rem; margin: .2rem 0 .6rem }
.hero p  { color: var(--muted); font-size: 1.15rem; max-width: 720px; margin: 0 auto }
.pill { display:inline-flex; gap:.5rem; align-items:center; padding:.5rem .9rem; border-radius:999px;
  border:1px solid rgba(255,255,255,.15); color:#dbeafe; background:rgba(59,130,246,.18) }
.kv { background: rgba(17,24,39,.65); border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:12px }
.kv .k { color: var(--muted); font-size: .75rem; text-transform: uppercase; letter-spacing: .4px; margin-bottom:6px}
.kv .v { color: var(--text) }
.metric-card, .prediction-card {
  background: linear-gradient(180deg, rgba(17,24,39,.85), rgba(15,23,42,.7));
  border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 20px; box-shadow: var(--shadow);
}
.big-number { font-weight: 800; font-size: 2.3rem; letter-spacing: .4px; color: var(--text); }
.badge { display:inline-block; padding:.4rem .7rem; border-radius:999px; border:1px solid #164e3d;
  background:#0b1f17; color:#9ef6d6; font-weight:600; font-size:2rem; letter-spacing:.3px }
.navbar { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 1rem }
.navbar .brand { font-weight:800; font-size:2.5rem !important; color:#cfe2ff; letter-spacing:.3px }
.btn {
  display:inline-flex; align-items:center; justify-content:center; gap:.5rem; cursor:pointer;
  padding:.7rem 1.1rem; border-radius:12px; border:1px solid rgba(255,255,255,.12);
  background: linear-gradient(180deg, rgba(46,134,171,.35), rgba(162,59,114,.35));
  color: white; text-decoration:none; transition: .18s ease;
}
.btn:hover{ transform: translateY(-1px); box-shadow: 0 10px 30px rgba(46,134,171,.25) }
.section-title { color: var(--text); font-weight: 700; font-size: 1.25rem; margin: .3rem 0 .8rem }
.hr { height:1px; background:linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent); margin: .7rem 0 1rem }
.footer { color: var(--muted); font-size: .85rem; text-align:center; margin-top: 1.2rem }

/* --- Team cards: center image perfectly --- */
.team-card{
  display:flex; flex-direction:column; align-items:center; gap:10px;
  padding:15px; background:rgba(17,24,39,.65);
  border:1px solid rgba(255,255,255,.08); border-radius:12px; margin:10px 0;
}
.team-photo-wrap{
  width:160px; height:200px; border-radius:12px; overflow:hidden;
  display:flex; align-items:center; justify-content:center;
  background:rgba(2,6,23,.35);
}
.team-photo-wrap img{
  max-width:100%; max-height:100%; object-fit:cover; display:block;
}
.team-name{ font-weight:700; color:#e5e7eb; }
.team-id{ font-style:italic; color:#9fb0c7; }

/* --- Prediction box styling --- */
.pred-box{
  padding:20px 24px;border-radius:16px;
  background:linear-gradient(180deg, rgba(17,24,39,.85), rgba(15,23,42,.72));
  border:2px solid rgba(255,255,255,.15); box-shadow:var(--shadow);
  margin:20px 0;
}
.pred-amount{font-weight:900;font-size:2rem;letter-spacing:.3px;color:var(--text);margin:0}
.pred-sub{display:flex;gap:10px;align-items:center;margin-top:6px;flex-wrap:wrap}
.pred-badge{display:inline-block;padding:.35rem .65rem;border-radius:999px;border:1px solid #164e3d;background:#0b1f17;color:#9ef6d6;font-weight:700;font-size:2rem}
.pred-meta{color:var(--muted);font-size:2rem}

.range-wrap{margin:14px 0 6px}
.range-scale{display:flex;justify-content:space-between;color:var(--muted);font-size:1.2rem;font-weight:600;margin-bottom:6px}
.range-bar{
  position:relative;height:12px;border-radius:999px;
  background:linear-gradient(90deg,#314255 0%, #4b6b8e 40%, #5f87b0 60%, #7cb6ff 100%);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);
}
.range-star{
  position:absolute;top:50%;
  transform:translate(-50%,-60%);
  font-size:28px;line-height:1;
  color:#d4af37;
  filter:drop-shadow(0 3px 8px rgba(0,0,0,.55));
}
.center-img{display:flex;justify-content:center;margin:24px 0}

/* Center wrapper below the hero card */
.hero-cta{
  width:100%;
  display:flex;
  justify-content:center;
  align-items:center;
  margin: 28px 0 10px;
}

/* Big light blue CTA — same size as the H1 (3.5rem), centered */
.hero-cta-btn{
  display:block;
  width:min(640px, 90%);
  height:86px;
  line-height:86px;          /* vertical centering of the text */
  text-align:center;
  text-decoration:none;
  font-size:2.5rem;          /* matches .hero h1 size */
  font-weight:800;
  border-radius:20px;
  border:2px solid rgba(255,255,255,.2);
  color:#fff;
  background:#322540;        /* darker purple */
  box-shadow:0 22px 60px rgba(76,29,149,.38);
}

.hero-cta-btn:hover{
  transform:translateY(-2px);
  background:#1f2e52;        /* even darker purple on hover */
  box-shadow:0 26px 70px rgba(76,29,149,.48);
}

.hero-cta-btn,
.hero-cta-btn:hover,
.hero-cta-btn:focus,
.hero-cta-btn:active {
  text-decoration: none !important;
  outline: none;                   /* optional: hides focus ring */
  text-underline-offset: 0 !important;
  text-decoration-thickness: 0 !important;
}

/* Range scale text & star bigger */
.range-scale{
  display:flex;justify-content:space-between;
  color:var(--text);font-weight:800;font-size:2rem;margin-bottom:6px
}
.range-star{ font-size:64px; }

/* Center the "📸 Image Upload & Analysis" block heading */
.center-title{ text-align:center; }

/* --- Prediction box styling --- */
.pred-box{
  padding:20px 24px;border-radius:16px;
  background:linear-gradient(180deg, rgba(17,24,39,.85), rgba(15,23,42,.72));
  border:2px solid rgba(255,255,255,.15); box-shadow:var(--shadow);
  margin:20px 0;
}
.pred-amount{font-weight:900;font-size:2rem;letter-spacing:.3px;color:var(--text);margin:0}
.pred-sub{display:flex;gap:10px;align-items:center;margin-top:6px;flex-wrap:wrap}
.pred-badge{display:inline-block;padding:.25rem .45rem;border-radius:999px;border:1px solid #164e3d;background:#0b1f17;color:#9ef6d6;font-weight:700;font-size:2rem}
.pred-meta{color:var(--muted);font-size:2rem}

.range-wrap{margin:14px 0 6px}

@media (max-width: 900px){ .hero{height:auto; padding: 60px 18px} .hero h1{font-size: 2.4rem} }

/* Navbar brand styling with ID selector (high specificity) */
#artifex-brand {
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: #cfe2ff;
  letter-spacing: .3px;
}

/* Progress indicator styling */
.progress-step{
  text-align: center;
  padding: 8px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.progress-step.active{
  background: rgba(96,165,250,.2);
  color: #60a5fa;
}
.progress-step.inactive{
  background: rgba(255,255,255,.05);
  color: #9fb0c7;
}

/* Form validation styling */
.stAlert{
  border-radius: 8px;
  border: 1px solid;
}
.stAlert[data-testid="alert"]{
  border-radius: 8px;
}

/* Button improvements */
.stButton > button {
  border-radius: 8px;
  transition: all 0.2s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Input field improvements */
.stNumberInput > div > div > input {
  border-radius: 8px;
}
.stSelectbox > div > div > div {
  border-radius: 8px;
}
.stTextInput > div > div > input {
  border-radius: 8px;
}

/* Placeholder styling */
.stTextInput > div > div > input::placeholder {
  color: #9fb0c7 !important;
  opacity: 0.8;
  font-style: italic;
}

.stNumberInput > div > div > input::placeholder {
  color: #9fb0c7 !important;
  opacity: 0.8;
  font-style: italic;
}

/* Selectbox placeholder styling */
.stSelectbox > div > div > div[data-baseweb="select"] > div {
  color: #9fb0c7;
}

/* Make empty selectbox options look like placeholders */
.stSelectbox > div > div > div[data-baseweb="select"] > div:first-child {
  color: #9fb0c7;
  font-style: italic;
}

/* CM-perfect hero (scoped) */
.hero-cm {
  width: 20cm;                /* gradient box width  */
  height: 10cm;               /* gradient box height */
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.10);
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
  /* 3) Gradient background (bottom layer) */
  background:
    radial-gradient(60rem 60rem at -10% -10%, rgba(96,165,250,.18) 0%, transparent 40%),
    radial-gradient(60rem 60rem at 110% 110%, rgba(34,211,238,.18) 0%, transparent 40%),
    linear-gradient(135deg, rgba(59,130,246,.25), rgba(162,59,114,.35));
}

/* New centered container with 8cm width and 18cm height */
.hero-new {
  width: 8cm;                 /* 8cm width */
  height: 18cm;               /* 18cm height */
  margin: 0 auto;             /* center align */
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.10);
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
  z-index: 2;                 /* appear above other elements */
  /* Night image background with blue-purple gradient overlay */
  background:
    radial-gradient(60rem 60rem at -10% -10%, rgba(96,165,250,.18) 0%, transparent 40%),
    radial-gradient(60rem 60rem at 110% 110%, rgba(34,211,238,.18) 0%, transparent 40%),
    linear-gradient(135deg, rgba(59,130,246,.25), rgba(162,59,114,.35)),
    url('img/night.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Outer container that wraps the hero section - larger than the image */
.outer-hero-wrapper {
  padding: 40px;              /* Large padding around the hero */
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(55, 48, 163, 0.8), rgba(79, 70, 229, 0.7));  /* Dark blue-purple gradient */
  border-radius: 24px;        /* Larger border radius */
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 15px 50px rgba(0,0,0,.4);
  margin: 30px auto;          /* Center and add vertical margin */
  max-width: 1400px;          /* Larger max width */
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-cm .hero-pic {
  /* 2) Picture layer — 19×9 cm, centered */
  position: absolute;
  top: 0.5cm;                 /* gap from the top */
  left: 50%;
  transform: translateX(-50%);
  width: 19cm;
  height: 9cm;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,.35);
  z-index: 2;
}

.hero-cm .hero-info {
  /* 1) Information box — sits above picture */
  position: relative;
  z-index: 3;
  text-align: center;
  color: #eaeaea;
  /* push content below the image footprint (0.5cm + 9cm + 0.2cm) */
  padding-top: calc(0.5cm + 9cm + 0.2cm);
  padding-left: 0.6cm;
  padding-right: 0.6cm;
}

.hero-cm .pill {
  display:inline-flex; gap:.5rem; align-items:center;
  padding:.5rem .9rem; border-radius:999px;
  border:1px solid rgba(255,255,255,.15);
  color:#dbeafe; background:rgba(59,130,246,.18);
}
.hero-cm h1 { margin: 8px 0 10px; font-size: clamp(22px, 3.2vw, 34px); line-height: 1.15; color:#fff; }
.hero-cm p  { margin: 0 auto; max-width: 18cm; font-size: 15px; opacity:.95; }

/* Gentle responsive scale for narrow viewports so cm layout doesn't overflow */
@media (max-width: 1200px){
  .hero-cm { transform: scale(.85); transform-origin: top center; }
}
@media (max-width: 900px){
  .hero-cm { transform: scale(.72); }
}
</style>
""",
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────────────────────

def go(page: str):
    st.session_state.page = page
    st.rerun()

def validate_image_file(uploaded_file) -> Tuple[bool, str]:
    if uploaded_file is None:
        return False, "No file uploaded."
    if uploaded_file.size > config.MAX_FILE_SIZE:
        return False, f"File too large. Max size: {config.MAX_FILE_SIZE//(1024*1024)}MB"
    if uploaded_file.type not in config.ALLOWED_IMAGE_TYPES:
        return False, f"Invalid file type. Allowed: {', '.join(config.ALLOWED_IMAGE_TYPES)}"
    return True, "OK"

def validate_form_inputs(artist: str, year: int, width: float, height: float, 
                        colorfulness_score: float, svd_entropy: float) -> Tuple[bool, list]:
    """Validate form inputs with comprehensive checks"""
    errors = []
    
    # Artist validation
    if not artist or not artist.strip():
        errors.append("Artist name is required")
    elif len(artist.strip()) < 2:
        errors.append("Artist name must be at least 2 characters")
    elif len(artist.strip()) > 100:
        errors.append("Artist name must be less than 100 characters")
    
    # Year validation
    if year is None:
        errors.append("Year is required")
    elif year < 1200 or year > 2024:
        errors.append("Year must be between 1200 and 2024")
    
    # Dimension validation
    if width is None or width <= 0:
        errors.append("Width is required and must be greater than 0")
    elif width > 500:
        errors.append("Width must be between 0.1 and 500 cm")
    
    if height is None or height <= 0:
        errors.append("Height is required and must be greater than 0")
    elif height > 500:
        errors.append("Height must be between 0.1 and 500 cm")
    
    if width and height and (width / height > 10 or height / width > 10):
        errors.append("Aspect ratio seems unrealistic (max 10:1)")
    
    # Image features validation
    if colorfulness_score < 0 or colorfulness_score > 1000:
        errors.append("Colorfulness score must be between 0 and 1000")
    if svd_entropy < 0 or svd_entropy > 1000:
        errors.append("SVD entropy must be between 0 and 1000")
    
    return len(errors) == 0, errors

def analyze_image(uploaded_file) -> Dict[str, Any]:
    """Analyze image with retry mechanism and better user feedback"""
    for attempt in range(config.RETRY_ATTEMPTS):
        try:
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            
            # Show retry attempt info
            if attempt > 0:
                st.info(f"🔄 Retry attempt {attempt + 1}/{config.RETRY_ATTEMPTS}...")
            
            r = requests.post(API["analyze_image"], files=files, timeout=config.REQUEST_TIMEOUT)

            if r.status_code == 200:
                data = r.json()
                # Validate response data
                if not isinstance(data, dict) or 'colorfulness_score' not in data or 'svd_entropy' not in data:
                    return {"success": False, "error": "Invalid response from image analysis service"}
                return {"success": True, "data": data}
            elif r.status_code == 503:
                return {"success": False, "error": "Image processing not available. Please try again later."}
            elif r.status_code == 422:
                return {"success": False, "error": f"Invalid image format: {r.text}"}
            else:
                return {"success": False, "error": f"Server Error {r.status_code}: {r.text}"}

        except requests.exceptions.Timeout:
            if attempt == config.RETRY_ATTEMPTS - 1:
                return {"success": False, "error": "Image analysis timed out after multiple attempts."}
            time.sleep(1)  # wait before retry

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend. Please check if the API is running."}

        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    return {"success": False, "error": "Failed after multiple attempts."}

def predict_price(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Predict price with retry mechanism and better user feedback"""
    for attempt in range(config.RETRY_ATTEMPTS):
        try:
            # Show retry attempt info
            if attempt > 0:
                st.info(f"🔄 Retry attempt {attempt + 1}/{config.RETRY_ATTEMPTS}...")
            
            r = requests.post(API["predict"], json=payload, timeout=config.REQUEST_TIMEOUT)

            if r.status_code == 200:
                data = r.json()
                if not isinstance(data, dict) or 'predicted_price' not in data:
                    return {"success": False, "error": "Invalid response from prediction service"}
                return {"success": True, "data": data}
            elif r.status_code == 422:
                return {"success": False, "error": f"Validation Error: {r.text}"}
            elif r.status_code == 503:
                return {"success": False, "error": "Model not loaded. Please try again later."}
            else:
                return {"success": False, "error": f"Server Error {r.status_code}: {r.text}"}
        except requests.exceptions.Timeout:
            if attempt == config.RETRY_ATTEMPTS - 1:
                return {"success": False, "error": "Prediction timed out after multiple attempts."}
            time.sleep(1)

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to backend. Please check if the API is running."}

        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    return {"success": False, "error": "Failed after multiple attempts."}

def calculate_title_word_count(title: str) -> int:
    if not title or title.strip().lower() == "untitled":
        return 3
    return len(title.strip().split())

def price_range_text(p: Optional[float]) -> Tuple[float, float, str]:
    if not p or p <= 0:
        return 0.0, 0.0, "N/A"
    lo, hi = p * 0.8, p * 1.2
    return lo, hi, f"${lo:,.0f} – ${hi:,.0f}"

def fmt_money(v: Optional[float]) -> str:
    try:
        return "${:,.0f}".format(float(v))
    except Exception:
        return "–"

def build_pdf(inputs: Dict[str, Any], result: Dict[str, Any], image: Optional[Image.Image]) -> bytes:
    """Build a modern, one-page PDF report (ReportLab). Falls back to text if ReportLab unavailable."""
    if not REPORTLAB:
        # Fallback: simple text report
        lines = [
            "="*60, "ARTIFEXAI - PREDICTION REPORT", "="*60, "",
            "ARTWORK DETAILS:", "-"*30
        ]
        for k in ["artist","title","object_type","technique","signature","condition",
                  "edition_type","year","width","height","has_edition","has_certificate",
                  "has_frame","has_damage","colorfulness_score","svd_entropy","expert"]:
            if k in inputs:
                lines.append(f"{k.replace('_',' ').title()}: {inputs[k]}")
        lines += ["", "PREDICTION RESULTS:", "-"*30]
        pred = result.get("predicted_price")
        lo, hi, rng = price_range_text(pred)
        lines.append(f"Predicted Price: {fmt_money(pred)}")
        lines.append(f"Estimated Range: {rng}")
        if "log_price" in result:
            lines.append(f"Log-space: {result['log_price']:.3f}")
        lines.append(f"Confidence: {result.get('confidence','–')}")
        lines.append(f"Model: {result.get('model_type','CatBoost')}")
        lines += ["", "="*60, "Generated by ArtifexAI", "="*60]
        return "\n".join(lines).encode("utf-8")

    # ===== ReportLab version =====
    try:
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepInFrame
        )
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io
        from datetime import datetime

        # ---- Colors / theme
        brand = HexColor("#1e40af")   # Indigo-900
        brand_light = HexColor("#3b82f6")  # Blue-500 for accents
        text_muted = HexColor("#475569")   # Slate-600
        bg_card = HexColor("#f8fafc")      # Slate-50
        line = HexColor("#e2e8f0")         # Slate-200
        success = HexColor("#059669")      # Emerald-600
        warn = HexColor("#ca8a04")         # Amber-600

        # ---- Try to use Inter or Poppins if present (optional). Falls back silently.
        try:
            pdfmetrics.registerFont(TTFont("Inter", "Inter-Regular.ttf"))
            pdfmetrics.registerFont(TTFont("Inter-Bold", "Inter-Bold.ttf"))
            base_font = "Inter"
            bold_font = "Inter-Bold"
        except Exception:
            base_font = "Helvetica"
            bold_font = "Helvetica-Bold"

        # ---- Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="TitleBrand",
            parent=styles["Heading1"],
            fontName=bold_font,
            fontSize=20,
            leading=24,
            textColor=white,
            alignment=0
        ))
        styles.add(ParagraphStyle(
            name="SubBrand",
            parent=styles["Heading3"],
            fontName=base_font,
            fontSize=10.5,
            leading=14,
            textColor=white,
        ))
        styles.add(ParagraphStyle(
            name="HSection",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=12.5,
            leading=16,
            textColor=brand
        ))
        styles.add(ParagraphStyle(
            name="NormalMuted",
            parent=styles["Normal"],
            fontName=base_font,
            fontSize=9.8,
            leading=13,
            textColor=text_muted
        ))
        styles.add(ParagraphStyle(
            name="Hero",
            parent=styles["Normal"],
            fontName=bold_font,
            fontSize=22,
            leading=26,
            textColor=brand
        ))
        styles.add(ParagraphStyle(
            name="Badge",
            parent=styles["Normal"],
            fontName=bold_font,
            fontSize=8.8,
            textColor=white
        ))

        # ---- Header / Footer painter
        def paint_header_footer(canv, doc_):
            w, h = A4
            # Header bar
            canv.saveState()
            canv.setFillColor(brand)
            canv.rect(0, h-60, w, 60, stroke=0, fill=1)
            # Brand title
            canv.setFillColor(white)
            canv.setFont(bold_font, 15)
            canv.drawString(72, h-38, "ArtifexAI")
            canv.setFont(base_font, 9)
            canv.drawString(72, h-52, "AI-Powered Art Valuation Report")
            # Footer
            canv.setFillColor(HexColor("#0f172a"))  # Slate-900 at low alpha via text
            canv.setFont(base_font, 8)
            footer = f"Generated on {datetime.now().strftime('%b %d, %Y %I:%M %p')}  |  © 2025 ArtifexAI"
            canv.drawRightString(w-72, 32, footer)
            # Top subtle separator for body
            canv.setFillColor(line)
            canv.rect(72, h-60-1, w-144, 1, stroke=0, fill=1)
            canv.restoreState()

        # ---- Document
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=1.2*cm, rightMargin=1.2*cm,
            topMargin=2.8*cm, bottomMargin=1.4*cm
        )

        story = []

        # ===== HERO PREDICTION CARD =====
        pred = result.get("predicted_price", 0) or 0
        lo, hi, rng_text = price_range_text(pred)
        confidence = result.get("confidence", "Unknown")
        model_type = result.get("model_type", "CatBoost")
        features_used = str(result.get("features_used", "57"))
        r2_disp = result.get("r2_display", "84.49%")  # keep existing display but let API override via r2_display

        hero_rows = [
            [
                Paragraph("Predicted Price", styles["NormalMuted"]),
                Paragraph(fmt_money(pred), styles["Hero"])
            ],
            [
                Paragraph("Estimated Range", styles["NormalMuted"]),
                Paragraph(rng_text, styles["Normal"])
            ],
            [
                Paragraph("Confidence", styles["NormalMuted"]),
                Paragraph(f"{confidence}", styles["Normal"])
            ],
        ]
        hero_tbl = Table(
            hero_rows,
            colWidths=[4.1*cm, None],
            hAlign="LEFT"
        )
        hero_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("BACKGROUND", (0, 0), (-1, -1), bg_card),
            ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        # Badges row (model / features / R²)
        badge_style = styles["Badge"]
        badge_model = Table([[Paragraph(f"Model: {model_type}", badge_style)]])
        badge_feats = Table([[Paragraph(f"{features_used} features", badge_style)]])
        badge_r2 = Table([[Paragraph(f"R² {r2_disp}", badge_style)]])
        for t, c in [(badge_model, brand), (badge_feats, brand_light), (badge_r2, success)]:
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), c),
                ("TEXTCOLOR", (0, 0), (-1, -1), white),
                ("BOX", (0, 0), (-1, -1), 0, c),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
        badges = Table([[badge_model, badge_feats, badge_r2]], colWidths=[None, None, None], hAlign="LEFT", spaceBefore=2)
        badges.setStyle(TableStyle([("RIGHTPADDING", (0, 0), (-1, -1), 4)]))

        # Group hero card + badges
        hero_block = [Paragraph("Prediction", styles["HSection"]), hero_tbl, Spacer(1, 4), badges]

        # ===== LEFT COLUMN: DETAILS & ATTRIBUTES =====
        dims = f"{float(inputs.get('width', 0) or 0):.1f} × {float(inputs.get('height', 0) or 0):.1f} cm"
        details_data = [
            ["Artist", inputs.get("artist", "Unknown") or "Unknown"],
            ["Title", inputs.get("title", "Untitled") or "Untitled"],
            ["Object Type", inputs.get("object_type", "Unknown") or "Unknown"],
            ["Technique", inputs.get("technique", "Unknown") or "Unknown"],
            ["Year", str(inputs.get("year", "Unknown") or "Unknown")],
            ["Dimensions", dims],
            ["Signature", inputs.get("signature", "Unknown") or "Unknown"],
            ["Condition", inputs.get("condition", "Unknown") or "Unknown"],
            ["Edition Type", inputs.get("edition_type", "Unknown") or "Unknown"],
        ]
        details_tbl = Table(details_data, colWidths=[3.2*cm, None])
        details_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("BACKGROUND", (0, 0), (-1, -1), white),
            ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        physical_data = [
            ["Has Edition Info", "Yes" if inputs.get("has_edition") else "No"],
            ["Certificate of Authenticity", "Yes" if inputs.get("has_certificate") else "No"],
            ["Has Frame", "Yes" if inputs.get("has_frame") else "No"],
            ["Has Damage", "Yes" if inputs.get("has_damage") else "No"],
        ]
        physical_tbl = Table(physical_data, colWidths=[5.0*cm, None])
        physical_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("BACKGROUND", (0, 0), (-1, -1), bg_card),
            ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        image_feats = [
            ["Colorfulness", f"{float(inputs.get('colorfulness_score', 0) or 0):.2f}"],
            ["SVD Entropy", f"{float(inputs.get('svd_entropy', 0) or 0):.2f}"],
        ]
        image_feat_tbl = Table(image_feats, colWidths=[3.2*cm, None])
        image_feat_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("BACKGROUND", (0, 0), (-1, -1), white),
            ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        left_col = [
            Paragraph("Artwork Details", styles["HSection"]),
            details_tbl,
            Spacer(1, 6),
            Paragraph("Physical Attributes", styles["HSection"]),
            physical_tbl,
            Spacer(1, 6),
            Paragraph("Image Features", styles["HSection"]),
            image_feat_tbl,
        ]

        # ===== RIGHT COLUMN: IMAGE (if provided) + TECHNICAL =====
        right_col = []
        if image is not None:
            # Convert PIL -> ReportLab Image
            img_io = io.BytesIO()
            # Use JPEG to keep PDF small
            image.convert("RGB").save(img_io, format="JPEG", quality=85)
            img_io.seek(0)
            rl_img = RLImage(img_io, width=8.0*cm, height=8.0*cm, kind='proportional')
            img_card = Table([[rl_img]], colWidths=[8.0*cm])
            img_card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), white),
                ("BOX", (0, 0), (-1, -1), 0.6, line),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            right_col += [Paragraph("Artwork Image", styles["HSection"]), img_card, Spacer(1, 8)]

        tech_rows = [
            ["Model Type", model_type],
            ["Features Used", features_used],
            ["R² (display)", r2_disp],
            ["Artist Popularity", str(result.get("artist_popularity", "Unknown"))],
        ]
        if "log_price" in result:
            try:
                tech_rows.append(["Log-space Price", f"{float(result['log_price']):.3f}"])
            except Exception:
                tech_rows.append(["Log-space Price", str(result['log_price'])])

        tech_tbl = Table(tech_rows, colWidths=[4.0*cm, None])
        tech_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("BACKGROUND", (0, 0), (-1, -1), bg_card),
            ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        right_col += [Paragraph("Technical Analysis", styles["HSection"]), tech_tbl]

        # ===== Assemble two-column grid =====
        # Top section: hero block spanning both columns
        top_block = Table([[KeepInFrame(0, 0, hero_block, mode="shrink")]],
                          colWidths=[None])
        top_block.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), white),
            ("BOX", (0, 0), (-1, -1), 0.8, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        # Two columns under hero
        two_col = Table(
            [
                [
                    KeepInFrame(0, 0, left_col, mode="shrink"),
                    KeepInFrame(0, 0, right_col, mode="shrink"),
                ]
            ],
            colWidths=[(doc.width*0.56), (doc.width*0.44)],
            hAlign="LEFT",
            spaceBefore=8
        )
        two_col.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Add final assembled blocks, all kept to one page via KeepInFrame
        story.append(KeepInFrame(doc.width, doc.height, [top_block], mode="shrink"))
        story.append(Spacer(1, 6))
        story.append(KeepInFrame(doc.width, doc.height, [two_col], mode="shrink"))

        # Build
        doc.build(story, onFirstPage=paint_header_footer, onLaterPages=paint_header_footer)
        buf.seek(0)
        return buf.read()

    except Exception as e:
        # Fallback: simple text report on error
        print(f"Error building PDF: {e}")
        lines = [
            "="*60, "ARTIFEXAI - PREDICTION REPORT", "="*60, "",
            "ARTWORK DETAILS:", "-"*30
        ]
        for k in ["artist","title","object_type","technique","signature","condition",
                  "edition_type","year","width","height","has_edition","has_certificate",
                  "has_frame","has_damage","colorfulness_score","svd_entropy","expert"]:
            if k in inputs:
                lines.append(f"{k.replace('_',' ').title()}: {inputs[k]}")
        lines += ["", "PREDICTION RESULTS:", "-"*30]
        pred = result.get("predicted_price")
        lo, hi, rng = price_range_text(pred)
        lines.append(f"Predicted Price: {fmt_money(pred)}")
        lines.append(f"Estimated Range: {rng}")
        if "log_price" in result:
            try:
                lines.append(f"Log-space: {float(result['log_price']):.3f}")
            except Exception:
                lines.append(f"Log-space: {result['log_price']}")
        lines.append(f"Confidence: {result.get('confidence','–')}")
        lines.append(f"Model: {result.get('model_type','CatBoost')}")
        lines += ["", "="*60, "Generated by ArtifexAI", "="*60]
        return "\n".join(lines).encode("utf-8")


# ────────────────────────────────────────────────────────────────────────────────
# UI SECTIONS
# ────────────────────────────────────────────────────────────────────────────────

def navbar():
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🏠 Home", use_container_width=True, key="nav_home"):
            go("home")
    with col2:
        st.markdown('<div id="artifex-brand" class="brand" style="text-align:center;">ArtifexAI</div>', unsafe_allow_html=True)
    with col3:
        if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
            go("about")
    st.markdown('</div>', unsafe_allow_html=True)

def hero():
    # Get the night image as base64 for embedding
    night_b64 = get_starry_night_base64() or ""
    
    # Create the HTML content
    hero_html = f"""
    <div class="hero" style="position: relative; min-height: 70vh; display: flex; align-items: center; justify-content: center; background-image: radial-gradient(60rem 60rem at -10% -10%, rgba(96,165,250,.18) 0%, transparent 40%), radial-gradient(60rem 60rem at 110% 110%, rgba(34,211,238,.18) 0%, transparent 40%), linear-gradient(135deg, rgba(59,130,246,.25), rgba(162,59,114,.35)), {'url(data:image/jpeg;base64,' + night_b64 + ')' if night_b64 else 'url(img/night.jpg)'}; background-size: cover; background-position: center; background-repeat: no-repeat; border-radius: 18px; border: 1px solid rgba(255,255,255,.08); box-shadow: 0 20px 60px rgba(0,0,0,.35); width: calc(100% + 4cm);">
        <div style="max-width: 1100px; width: 100%; padding: 24px;">
            <div class="glass" style="padding: 28px; border-radius: 20px; border: 1px solid rgba(255,255,255,.12); box-shadow: 0 18px 60px rgba(0,0,0,.35); backdrop-filter: blur(10px); background: linear-gradient(180deg, rgba(17,24,39,.85), rgba(15,23,42,.75));">
                <div style="text-align: center; max-width: 900px; margin: 0 auto;">
                    <span class="pill">🧠 AI-Powered • 🎨 Art Valuation • 📈 Evidence-based</span>
                    <h1 style="margin: .5rem 0 .25rem; font-weight: 800; color: white; font-size: 3.5rem;">Accurate, Explainable Art Price Predictions</h1>
                    <p style="color: #cbd5e1; margin-bottom: 20px; font-size: 1.15rem; max-width: 720px; margin-left: auto; margin-right: auto;">
                        Upload an image, enter key details, and receive a fair-value estimate with a confidence range.
                        Built with image features (Colorfulness, SVD Entropy), rich metadata, and robust statistical priors.
                    </p>
                    <div style="margin-top: 20px;">
                        <a href="?goto=predict" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3); transition: all 0.3s ease;">🚀 Start Prediction</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Wrap the hero content in the outer container
    wrapped_hero_html = f"""
    <div class="outer-hero-wrapper">
        {hero_html}
    </div>
    """
    
    st.markdown(wrapped_hero_html, unsafe_allow_html=True)



# Removed complex JavaScript navigation - using simple Streamlit buttons instead

def section_title(txt: str):
    st.markdown(f'<div class="section-title">{txt}</div>', unsafe_allow_html=True)

def home_page():
    hero()
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

def about_page():
    st.markdown(
        """
        <div class="glass" style="padding:26px;">
          <h2 style="margin:0 0 10px 0">✨ ArtifexAI</h2>
          <p style="color:#c6d2e3">Price Intelligence for Art Markets</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Project Summary
    st.markdown(
        """
        <div class="glass" style="padding:22px;">
          <h3 style="margin-top:0">📋 Project Summary</h3>
          <p style="color:#c6d2e3; line-height:1.6;">
            This project develops a comprehensive Art Auction Price Prediction System using advanced machine learning 
            techniques on a dataset of 60,000+ print auction records from 2024. We implemented a multi-layered approach 
            combining traditional auction features (artist, technique, signature, condition, dimensions) with advanced 
            image-derived metrics (colorfulness score and SVD entropy) extracted using computer vision techniques.
          </p>
          <p style="color:#c6d2e3; line-height:1.6;">
            Our feature engineering pipeline created over 50 derived features including artist popularity scores, 
            temporal features, dimension ratios, and interaction terms. The best performing model (CatBoost) achieved 
            an R² score of 84.49%, RMSE of 0.33 in log-space, and predicted 65.2% of artworks within ±20% of actual prices.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Model Performance Metrics
    g1, g2, g3, g4 = st.columns(4)
    for (c, title, sub) in [
        (g1, "CatBoost", "Model"),
        (g2, "57", "Features"),
        (g3, "84.49%", "R² Score"),
        (g4, "~25%", "MAPE"),
    ]:
        with c:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div style="font-size:1.8rem;font-weight:800;color:#60A5FA">{title}</div>
                    <div style="color:#94A3B8">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # How It Works
    st.markdown(
        """
        <div class="glass" style="padding:22px;">
          <h3 style="margin-top:0">🏗️ How It Works</h3>
          <div style="display:grid; gap:14px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));">
            <div class="kv"><div class="k">Image Features</div><div class="v">Colorfulness, SVD Entropy, Aspect Ratio</div></div>
            <div class="kv"><div class="k">Metadata</div><div class="v">Artist, Technique, Year, Dimensions</div></div>
            <div class="kv"><div class="k">Priors</div><div class="v">Artist/Technique medians, Price buckets</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Team Information with Images
    st.markdown("### 👥 Our Team")
    
    # Team Members with Images (centered) - Cached for performance
    col1, col2, col3, col4 = st.columns(4)
    team_members = [
        ("a.jpeg", "Fernando W A A T", "IT23144408"),
        ("o.jpeg", "Liyanage M L V O", "IT23173040"),
        ("s.jpeg", "Fernando R S R", "IT23449282"),
        ("t.jpeg", "Fernando H T D", "IT23177864"),
    ]
    
    # Cache team images in session state for performance
    if "team_images_cache" not in st.session_state:
        st.session_state.team_images_cache = {}
    
    for i, (img_file, name, sid) in enumerate(team_members):
        with [col1, col2, col3, col4][i]:
            # Check cache first
            if img_file in st.session_state.team_images_cache:
                img_tag = st.session_state.team_images_cache[img_file]
            else:
                # Load image and convert to base64 for embedding in HTML
                try:
                    image_path = f"img/{img_file}"
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        # Resize image to fit the card
                        image.thumbnail((160, 200), Image.Resampling.LANCZOS)
                        # Convert to base64 for embedding
                        import io
                        import base64
                        buffer = io.BytesIO()
                        image.save(buffer, format='JPEG')
                        img_str = base64.b64encode(buffer.getvalue()).decode()
                        img_tag = f'<img src="data:image/jpeg;base64,{img_str}" alt="{name}" style="width:160px;height:200px;object-fit:cover;border-radius:12px;">'
                        # Cache the result
                        st.session_state.team_images_cache[img_file] = img_tag
                    else:
                        img_tag = '<div style="width:160px;height:200px;background:rgba(2,6,23,.35);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#9fb0c7;">Image not found</div>'
                        st.session_state.team_images_cache[img_file] = img_tag
                except Exception as e:
                    img_tag = '<div style="width:160px;height:200px;background:rgba(2,6,23,.35);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#9fb0c7;">Error loading image</div>'
                    st.session_state.team_images_cache[img_file] = img_tag
            
            st.markdown(
                f"""
                <div class="team-card" style="padding:15px; background:rgba(17,24,39,.65); border:1px solid rgba(255,255,255,.08); border-radius:12px; margin:10px 0; display:flex; flex-direction:column; align-items:center; gap:10px;">
                  <div class="team-photo-wrap" style="width:160px; height:200px; border-radius:12px; overflow:hidden; display:flex; align-items:center; justify-content:center; background:rgba(2,6,23,.35);">
                    {img_tag}
                  </div>
                  <div class="team-name" style="font-weight:700; color:#e5e7eb;">{name}</div>
                  <div class="team-id" style="font-style:italic; color:#9fb0c7;">{sid}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Supervisor section removed as requested

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Key Features
    st.markdown(
        """
        <div class="glass" style="padding:22px;">
          <h3 style="margin-top:0">🎯 Key Features</h3>
          <div style="display:grid; gap:14px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));">
            <div class="kv">
              <div class="k">🎨 Image Analysis</div>
              <div class="v">Automatic colorfulness and SVD entropy calculation</div>
            </div>
            <div class="kv">
              <div class="k">📊 57+ Features</div>
              <div class="v">Comprehensive feature engineering for optimal accuracy</div>
            </div>
            <div class="kv">
              <div class="k">🤖 AI-Powered</div>
              <div class="v">CatBoost model with 84.5% R² score</div>
            </div>
            <div class="kv">
              <div class="k">📈 Evidence-based</div>
              <div class="v">Transparent predictions with confidence ranges</div>
            </div>
            <div class="kv">
              <div class="k">💾 Database Integration</div>
              <div class="v">SQLite for artist data management</div>
            </div>
            <div class="kv">
              <div class="k">🚀 Production Ready</div>
              <div class="v">Docker support and comprehensive error handling</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Project Information
    st.markdown(
        """
        <div class="glass" style="padding:22px;">
          <h3 style="margin-top:0">📚 Project Information</h3>
          <div style="display:grid; gap:14px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));">
            <div class="kv">
              <div class="k">Course</div>
              <div class="v">Fundamentals of Data Mining (IT3051)</div>
            </div>
            <div class="kv">
              <div class="k">Institution</div>
              <div class="v">Sri Lanka Institute of Information Technology</div>
            </div>
            <div class="kv">
              <div class="k">Dataset</div>
              <div class="v">60,000+ print auction records (2024)</div>
            </div>
            <div class="kv">
              <div class="k">Technology</div>
              <div class="v">Python, FastAPI, Streamlit, CatBoost</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    if st.button("🔙 Back to Home", use_container_width=True, key="about_back"):
        go("home")

def unit_dimensions():
    section_title("📏 Physical Dimensions")
    year = st.number_input(
        "Year Created*", 
        min_value=1200, 
        max_value=2024, 
        value=None, 
        step=1,
        help="Year the artwork was created (1200-2024)",
        placeholder="e.g., 1950",
        key="year"
    )
    col_u, col_w, col_h = st.columns(3)
    with col_u:
        unit = st.selectbox("Unit", ["cm", "inches"], help="Measurement unit for dimensions", key="unit")
    with col_w:
        if unit == "cm":
            width = st.number_input(
                "Width (cm)*", 
                min_value=0.1, 
                max_value=500.0, 
                value=None, 
                step=0.1, 
                help="Width in centimeters (0.1-500 cm)",
                placeholder="e.g., 50.0",
                key="width_cm"
            )
        else:
            width_in = st.number_input(
                "Width (inches)*", 
                min_value=0.1, 
                max_value=200.0, 
                value=None, 
                step=0.1, 
                help="Width in inches (0.1-200 inches)",
                placeholder="e.g., 19.7",
                key="width_in"
            )
            width = width_in * 2.54 if width_in else 0
    with col_h:
        if unit == "cm":
            height = st.number_input(
                "Height (cm)*", 
                min_value=0.1, 
                max_value=500.0, 
                value=None, 
                step=0.1, 
                help="Height in centimeters (0.1-500 cm)",
                placeholder="e.g., 60.0",
                key="height_cm"
            )
        else:
            height_in = st.number_input(
                "Height (inches)*", 
                min_value=0.1, 
                max_value=200.0, 
                value=None, 
                step=0.1, 
                help="Height in inches (0.1-200 inches)",
                placeholder="e.g., 23.6",
                key="height_in"
            )
            height = height_in * 2.54 if height_in else 0
    return year, width, height

def predict_page():
    st.markdown('<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("### 🎨 Artwork Price Prediction")
    st.caption("Upload an image, analyze features, fill details, then predict.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Progress indicator
    progress_steps = ["📸 Upload Image", "🔍 Analyze Features", "📝 Fill Details", "🔮 Predict Price"]
    current_step = 0
    if st.session_state.uploaded_image is not None:
        current_step = 1
    if st.session_state.colorfulness_score > 0 or st.session_state.svd_entropy > 0:
        current_step = 2
    
    # Progress bar
    progress_cols = st.columns(4)
    for i, step in enumerate(progress_steps):
        with progress_cols[i]:
            if i <= current_step:
                st.markdown(f'<div style="text-align: center; padding: 8px; background: rgba(96,165,250,.2); border-radius: 8px; color: #60a5fa; font-weight: 600;">{step}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align: center; padding: 8px; background: rgba(255,255,255,.05); border-radius: 8px; color: #9fb0c7;">{step}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # IMAGE AREA - VERTICAL LAYOUT
    with st.container():
        # Image Upload Section
        st.markdown("### <div class='center-title'>📸 Image Upload & Analysis</div>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_image is None:
            up = st.file_uploader(
                "Upload artwork image", 
                type=["png", "jpg", "jpeg"], 
                help="Upload a clear image of your artwork (PNG, JPG, JPEG up to 10MB)",
                key="uploader"
            )
            if up:
                ok, msg = validate_image_file(up)
                if not ok:
                    st.error(f"❌ {msg}")
                else:
                    # Store both the raw file and processed image
                    st.session_state.uploaded_file_raw = up
                    st.session_state.uploaded_image = Image.open(up).convert("RGB")
                    # Centered preview when a file was just uploaded
                    centerL, centerC, centerR = st.columns([1, 2, 1])
                    with centerC:
                        st.image(st.session_state.uploaded_image, caption="Your Artwork", use_container_width=True)
                    st.success("✅ Image uploaded successfully! Click 'Analyze Image' to compute features.")
                    st.rerun()
            else:
                st.info("👆 Please upload an image to get started")
        else:
            # Centered preview + centered stacked buttons when image already exists
            imgL, imgC, imgR = st.columns([1, 2, 1])
            with imgC:
                st.image(st.session_state.uploaded_image, caption="Your Artwork", use_container_width=True)

            # Improved button layout - horizontal with better spacing
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
            
            with btn_col1:
                # Analyze Image Button
                if st.button("🔍 Analyze Image", use_container_width=True, key="analyze_now"):
                    if st.session_state.uploaded_file_raw is None:
                        st.warning("Please re-upload the image to analyze.")
                    else:
                        with st.spinner("🔄 Analyzing image features..."):
                            res = analyze_image(st.session_state.uploaded_file_raw)
                        if res.get("success"):
                            data = res["data"] or {}
                            st.session_state.image_features = data
                            st.session_state.colorfulness_score = float(data.get("colorfulness_score", 0.0))
                            st.session_state.svd_entropy = float(data.get("svd_entropy", 0.0))
                            st.success(
                                f"✅ Analysis Complete!  🎨 Colorfulness: {st.session_state.colorfulness_score:.2f}  "
                                f"🔢 SVD Entropy: {st.session_state.svd_entropy:.2f}"
                            )
                            st.rerun()  # ← forces the number inputs to refresh with new values
                        else:
                            st.error(f"❌ Analysis failed: {res.get('error')}")
            
            with btn_col2:
                # Clear Image Button
                if st.button("🗑️ Clear Image", use_container_width=True, key="clear_img"):
                    clear_image_state()
                    st.success("✅ Image cleared successfully!")
                    st.rerun()
            
            with btn_col3:
                # Change Image Button
                if st.button("🔄 Change Image", use_container_width=True, key="change_img"):
                    clear_image_state()
                    st.rerun()
            
            with btn_col4:
                # Skip Analysis Button
                if st.button("⏭️ Skip Analysis", use_container_width=True, key="skip_analysis"):
                    st.info("ℹ️ You can manually enter image features below or leave them as 0.")
                    st.rerun()

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # IMAGE FEATURES (always visible; auto-filled if analyzed)
    section_title("🖼️ Image Features")
    
    # Show analysis status
    if st.session_state.colorfulness_score > 0 or st.session_state.svd_entropy > 0:
        st.success(f"✅ Image features analyzed: Colorfulness={st.session_state.colorfulness_score:.2f}, SVD Entropy={st.session_state.svd_entropy:.2f}")
    else:
        st.info("ℹ️ Image features will be auto-calculated when you analyze an image, or you can enter them manually.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Use session state key directly to ensure proper synchronization
        colorfulness_score = st.number_input(
            "Colorfulness Score*", 
            min_value=0.0, max_value=1000.0,
            step=0.01, 
            help="Auto-calculated from uploaded image - Click to clear and enter manually (0-1000). Measures color intensity and vibrancy.",
            key="colorfulness_score"  # Use same key as session state
        )
    with col_b:
        # Use session state key directly to ensure proper synchronization
        svd_entropy = st.number_input(
            "SVD Entropy*", 
            min_value=0.0, max_value=1000.0,
            step=0.01, 
            help="Auto-calculated from uploaded image - Click to clear and enter manually (0-1000). Measures image complexity and detail.",
            key="svd_entropy"  # Use same key as session state
        )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # FORM
    with st.form("artwork_form"):
        section_title("🎛️ Details")
        colL, colR = st.columns(2)
        with colL:
            artist = st.text_input("Artist Name*", placeholder="e.g., Pablo Picasso", max_chars=100, help="Name of the artist who created the artwork", key="artist")
            object_type = st.selectbox("Object Type*", ["other","painting","drawing","print","sculpture","photograph"], index=0, help="Type of artwork (painting, drawing, print, etc.)", key="object_type")
            technique = st.selectbox("Technique*", ["other","oil on canvas","watercolor","etching","lithograph","woodcut","screenprint","painting"], index=0, help="Artistic technique or medium used", key="technique")
        with colR:
            signature = st.selectbox("Signature*", ["unknown","hand signed","plate signed","unsigned"], index=0, help="Whether the artwork is signed by the artist", key="signature")
            condition = st.selectbox("Condition*", ["unknown","excellent","very good","good","fair","poor"], index=0, help="Physical condition of the artwork", key="condition")
            edition_type = st.selectbox("Edition Type*", ["unknown","unique","numbered","limited","open"], index=0, help="Type of edition (unique piece, numbered print, etc.)", key="edition_type")

        year, width, height = unit_dimensions()

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        section_title("🔍 Physical Attributes")
        cpa1, cpa2 = st.columns(2)
        with cpa1:
            has_edition = st.checkbox("Has Edition Information", help="Whether the artwork has edition information (numbered, limited, etc.)", key="has_edition")
            has_certificate = st.checkbox("Has Certificate of Authenticity", help="Whether the artwork comes with a certificate of authenticity", key="has_certificate")
        with cpa2:
            has_frame = st.checkbox("Has Frame", help="Whether the artwork is framed", key="has_frame")
            has_damage = st.checkbox("Has Damage", help="Whether the artwork has any visible damage", key="has_damage")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        section_title("📝 Extra")
        cel1, cel2 = st.columns(2)
        with cel1:
            title = st.text_input("Title (optional)", placeholder="e.g., Untitled", max_chars=200, help="Title of the artwork (leave empty if untitled)", key="title_text")
        with cel2:
            expert = st.text_input("Expert/Appraiser", placeholder="e.g., Unknown", max_chars=100, help="Name of the expert or appraiser who evaluated the artwork", key="expert")

        cc1, cc2 = st.columns([1, 2])
        with cc1:
            clear = st.form_submit_button("🗑️ Clear All", use_container_width=True)
        with cc2:
            submitted = st.form_submit_button("🔮 Predict Price", use_container_width=True, type="primary")

        if clear:
            # Clear all state except page
            for key in list(st.session_state.keys()):
                if key != "page":
                    del st.session_state[key]
            _init_state()
            clear_image_state()
            st.success("✅ All data cleared! You can start a new prediction.")
            st.rerun()
            
        if submitted:
            # Comprehensive form validation
            is_valid, errors = validate_form_inputs(
                artist, year, width, height, 
                st.session_state.colorfulness_score, 
                st.session_state.svd_entropy
            )
            
            if not is_valid:
                for error in errors:
                    st.error(f"❌ {error}")
                return  # Prevent submission if there are errors

            title_wc = calculate_title_word_count(title or "Untitled")
            payload = {
                "artist": artist.strip() if artist else "",
                "object_type": object_type,
                "technique": technique,
                "signature": signature,
                "condition": condition,
                "edition_type": edition_type,
                "year": int(year) if year else 1950,
                "width": float(width) if width else 50.0,
                "height": float(height) if height else 60.0,
                "has_edition": bool(has_edition),
                "has_certificate": bool(has_certificate),
                "has_frame": bool(has_frame),
                "has_damage": bool(has_damage),
                "expert": expert.strip() if expert else "Unknown",
                "title": title.strip() if title else "Untitled",
                "title_word_count": title_wc,
            }
            # Always include image features (even if 0)
            payload["colorfulness_score"] = float(st.session_state.colorfulness_score or 0.0)
            payload["svd_entropy"] = float(st.session_state.svd_entropy or 0.0)

            with st.spinner("Predicting..."):
                res = predict_price(payload)

            if res.get("success"):
                st.session_state.prediction = res["data"]
                st.session_state.inputs = payload
                st.success("Prediction complete.")
                go("results")
            else:
                st.error(f"Prediction failed: {res.get('error')}")

def results_page():
    data = st.session_state.get("prediction") or {}
    inputs = st.session_state.get("inputs") or {}

    if not data:
        st.info("No prediction available yet.")
        if st.button("Start a Prediction", use_container_width=True):
            go("predict")
        return

    # ---------- helpers ----------
    def clamp(x, lo_, hi_): 
        return max(lo_, min(hi_, x))

    pred = data.get("predicted_price", 0)
    lo, hi, rng_text = price_range_text(pred)
    confidence = data.get('confidence', 'Unknown')
    model_type = data.get('model_type', 'CatBoost')
    features_used = data.get('features_used', '57')

    try:
        pos_pct = 50.0
        if isinstance(pred, (int, float)) and isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and hi > lo:
            pos_pct = clamp((pred - lo) * 100.0 / (hi - lo), 0, 100)
    except Exception:
        pos_pct = 50.0

    # ---------- CSS (center everything, remove box, 2× star, big fonts) ----------
    st.markdown("""
    <style>
    .pred-block{
      max-width: 980px;
      margin: 8px auto 18px;   /* Center the whole section */
      text-align: center;      /* Center all text inside */
    }

    /* Headings */
    .pred-block .title{
      font-weight: 800;
      letter-spacing:.02em;
      margin-bottom: 6px;
      font-size: clamp(1.25rem, 2.2vw, 1.75rem);
    }
    .pred-block .amount{
      font-weight: 900;
      line-height: 1;
      margin: 2px 0 20px 0;
      font-size: clamp(3rem, 6vw, 5rem);  /* BIG and centered */
    }

    /* Meta badges now below amount and centered */
    .pred-block .meta{
      display:flex; gap:10px; flex-wrap:wrap; justify-content:center;
      margin: 2px 0 20px 0;
    }
    .pred-block .badge{
      font-weight: 700; font-size: 0.95rem; 
      padding: 6px 10px; border-radius: 9999px; display:inline-block;
    }
    .pred-block .badge.conf { background:#065f46; color:#fff; }
    .pred-block .badge.model { background:#0f172a; color:#e5e7eb; }
    .pred-block .badge.feats { background:#1e293b; color:#e5e7eb; }

    /* Range bar */
    .pred-block .range{
      position: relative; height: 10px; border-radius: 8px;
      background: linear-gradient(90deg, #93c5fd, #64748b);
      margin: 12px auto 20 auto;           /* center the bar */
    }
    .pred-block .range .min,
    .pred-block .range .max{
      position:absolute; top:-36px;
      font-size: clamp(1.2rem, 2.2vw, 2rem); /* ~4× bigger */
      font-weight: 700;
    }
    .pred-block .range .min{ left:0; }
    .pred-block .range .max{ right:0; }

    /* Star 2× */
    .pred-block .range .star{
      position:absolute; top:-16px; transform: translateX(-50%) scale(2);
      font-size: 1.2rem; color:#fbbf24; text-shadow:0 0 6px rgba(251,191,36,.55);
    }

    /* Range label (below bar) */
    .pred-block .range-label{
      margin-top: 16px; 
      font-size: clamp(1.2rem, 2.2vw, 2rem); /* 4× */
    }

    /* Center the preview image nicely */
    .center-img{
      max-width: 980px; margin: 4px auto 0 auto; 
      display:flex; flex-direction:column; align-items:center;
    }
    .center-img img{
      width: 100%; max-width: 480px; height:auto;
      border-radius: 10px;
    }
    .center-img .cap{ margin-top:6px; opacity:.75; font-size:.95rem; }
    </style>
    """, unsafe_allow_html=True)

    # ---------- HTML for centered prediction ----------
    st.markdown(f"""
    <div class="pred-block">
      <div class="title">Prediction</div>
      <div class="amount">{fmt_money(pred)}</div>

      <div class="meta">
        <span class="badge conf">CONFIDENCE: {str(confidence).upper()}</span>
        <span class="badge model">Model: {model_type}</span>
        <span class="badge feats">Features used: {features_used}</span>
          </div>

      <div class="range">
        <span class="min">{fmt_money(lo)}</span>
        <span class="max">{fmt_money(hi)}</span>
        <div class="star" style="left:{pos_pct}%;">★</div>
          </div>

      <div class="range-label">Range: {fmt_money(lo)} – {fmt_money(hi)}</div>
        </div>
    """, unsafe_allow_html=True)

    # ---------- centered artwork image ----------
    img = st.session_state.get("uploaded_image")
    if img is not None:
        import base64, io
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(f"""
        <div class="center-img">
          <img src="data:image/jpeg;base64,{b64}" alt="Your Artwork"/>
          <div class="cap">Your Artwork</div>
        </div>
        """, unsafe_allow_html=True)

    # ===== COMPREHENSIVE DATA ANALYSIS SECTION =====
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 Detailed Analysis & Database Insights")
    
    # Create columns for different data categories
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:1.2rem;font-weight:700;color:#60A5FA;margin-bottom:8px;">Confidence Level</div>
                <div style="font-size:2rem;font-weight:800;color:#e5e7eb;">{data.get('confidence', 'UNKNOWN').upper()}</div>
                <div style="font-size:0.9rem;color:#9fb0c7;margin-top:4px;">Prediction Reliability</div>
      </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:1.2rem;font-weight:700;color:#60A5FA;margin-bottom:8px;">Artist Popularity</div>
                <div style="font-size:2rem;font-weight:800;color:#e5e7eb;">{data.get('artist_popularity', 'UNKNOWN').upper()}</div>
                <div style="font-size:0.9rem;color:#9fb0c7;margin-top:4px;">Market Recognition</div>
    </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:1.2rem;font-weight:700;color:#60A5FA;margin-bottom:8px;">Features Used</div>
                <div style="font-size:2rem;font-weight:800;color:#e5e7eb;">{data.get('features_used', '57')}</div>
                <div style="font-size:0.9rem;color:#9fb0c7;margin-top:4px;">Data Points Analyzed</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-size:1.2rem;font-weight:700;color:#60A5FA;margin-bottom:8px;">Model R²</div>
                <div style="font-size:2rem;font-weight:800;color:#e5e7eb;">{data.get('r2_display', '84.49%')}</div>
                <div style="font-size:0.9rem;color:#9fb0c7;margin-top:4px;">Accuracy Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    
    # Detailed breakdown section
    st.markdown("### 🔍 Detailed Breakdown")
    
    # Create two columns for detailed information
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown(
            """
            <div class="glass" style="padding:20px;">
                <h4 style="margin-top:0;color:#60A5FA;">🎨 Artwork Analysis</h4>
                <div style="display:grid;gap:12px;">
                    <div class="kv">
                        <div class="k">Artist</div>
                        <div class="v">{artist_name}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Technique</div>
                        <div class="v">{technique}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Year Created</div>
                        <div class="v">{year}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Dimensions</div>
                        <div class="v">{width} × {height} cm</div>
                    </div>
                    <div class="kv">
                        <div class="k">Condition</div>
                        <div class="v">{condition}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Signature</div>
                        <div class="v">{signature}</div>
                    </div>
                </div>
            </div>
            """.format(
                artist_name=inputs.get('artist', 'Unknown'),
                technique=inputs.get('technique', 'Unknown'),
                year=inputs.get('year', 'Unknown'),
                width=inputs.get('width', '0'),
                height=inputs.get('height', '0'),
                condition=inputs.get('condition', 'Unknown'),
                signature=inputs.get('signature', 'Unknown')
            ),
            unsafe_allow_html=True
        )
    
    with detail_col2:
        st.markdown(
            """
            <div class="glass" style="padding:20px;">
                <h4 style="margin-top:0;color:#60A5FA;">📈 Technical Analysis</h4>
                <div style="display:grid;gap:12px;">
                    <div class="kv">
                        <div class="k">Model Type</div>
                        <div class="v">{model_type}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Colorfulness Score</div>
                        <div class="v">{colorfulness:.2f}</div>
                    </div>
                    <div class="kv">
                        <div class="k">SVD Entropy</div>
                        <div class="v">{svd_entropy:.2f}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Log-space Price</div>
                        <div class="v">{log_price:.3f}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Price Range</div>
                        <div class="v">{price_range}</div>
                    </div>
                    <div class="kv">
                        <div class="k">Analysis Date</div>
                        <div class="v">{analysis_date}</div>
                    </div>
                </div>
            </div>
            """.format(
                model_type=data.get('model_type', 'CatBoost'),
                colorfulness=float(inputs.get('colorfulness_score', 0)),
                svd_entropy=float(inputs.get('svd_entropy', 0)),
                log_price=float(data.get('log_price', 0)),
                price_range=rng_text,
                analysis_date=data.get('analysis_date', 'Today')
            ),
            unsafe_allow_html=True
        )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Market insights section
    st.markdown("### 💡 Market Insights & Recommendations")
    
    # Generate insights based on the data
    insights = []
    
    # Confidence-based insights
    confidence = data.get('confidence', 'UNKNOWN').upper()
    if confidence == 'HIGH':
        insights.append("✅ High confidence prediction - reliable for valuation purposes")
    elif confidence == 'MEDIUM':
        insights.append("⚠️ Medium confidence - consider additional market research")
    else:
        insights.append("❓ Low confidence - prediction may vary significantly")
    
    # Artist popularity insights
    artist_pop = data.get('artist_popularity', 'UNKNOWN').upper()
    if artist_pop in ['HIGH', 'VERY HIGH']:
        insights.append("🌟 Artist has strong market recognition - premium pricing expected")
    elif artist_pop == 'MEDIUM':
        insights.append("📊 Moderate artist recognition - standard market pricing")
    else:
        insights.append("🔍 Limited artist data - pricing based on technique and condition")
    
    # Technique insights
    technique = inputs.get('technique', '').lower()
    if 'oil' in technique:
        insights.append("🎨 Oil paintings typically command higher prices in auctions")
    elif 'watercolor' in technique:
        insights.append("💧 Watercolors may have different market dynamics")
    elif 'print' in technique or 'lithograph' in technique:
        insights.append("🖨️ Prints and lithographs follow different pricing patterns")
    
    # Condition insights
    condition = inputs.get('condition', '').lower()
    if condition in ['excellent', 'very good']:
        insights.append("✨ Excellent condition enhances market value significantly")
    elif condition in ['good', 'fair']:
        insights.append("📝 Good condition - minor restoration may increase value")
    else:
        insights.append("🔧 Consider professional restoration to maximize value")
    
    # Display insights
    for insight in insights:
        st.info(insight)
    
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Export
    st.subheader("📄 Export")

    
    cL, cR = st.columns([2, 1])

    with cL:
        # Text fallback always available
        txt_lines = [
        f"Artist: {inputs.get('artist','')}",
        f"Title: {inputs.get('title','')}",
        f"Year: {inputs.get('year','')}",
        f"Technique: {inputs.get('technique','')}",
        f"Signature: {inputs.get('signature','')}",
        f"Predicted Price: {fmt_money(pred)}",
        f"Estimated Range: {rng_text}",
        f"Confidence: {data.get('confidence','—')}",
        f"Model: {data.get('model_type','CatBoost')}",
    ]
        st.download_button(
            "📥 Download Text Report",
            data="\n".join(txt_lines).encode("utf-8"),
            file_name=f"artifexai_prediction_{inputs.get('artist','unknown').replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with cR:
        if REPORTLAB:
            try:
                with st.spinner("🔄 Generating PDF..."):
                    pdf_bytes = build_pdf(inputs, data, st.session_state.get("uploaded_image"))

                if pdf_bytes and len(pdf_bytes) > 0:
                    st.download_button(
                    "📄 Download PDF",
                    data=pdf_bytes,
                        file_name=f"artifexai_prediction_{inputs.get('artist','unknown').replace(' ','_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                        use_container_width=True,
                        help="Download a professional PDF report with all prediction details"
                    )
                else:
                    st.error("❌ Failed to generate PDF - empty content")
                    st.info("📄 Please try again or contact support if the issue persists.")
            except Exception as e:
                st.error(f"❌ PDF generation failed: {str(e)}")
                st.info("📄 Please try again or contact support if the issue persists.")
        else:
            st.info("📄 PDF export is disabled. Install **reportlab**: `pip install reportlab`")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("🔙 Home", use_container_width=True):
            go("home")
    with b2:
        if st.button("🔄 New Prediction", use_container_width=True, type="primary"):
            go("predict")
    with b3:
        if st.button("ℹ️ About", use_container_width=True):
            go("about")

    st.markdown('<div class="footer">© 2025 ArtifexAI — Fair-value insights for art markets</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────────
# ROUTER
# ────────────────────────────────────────────────────────────────────────────────

def main():
    # Sidebar: API config
    with st.sidebar:
        st.header("Settings")
        api_url = st.text_input(
            "Backend API Base URL", 
            value=config.API_BASE_URL,
            help="Enter the base URL for the backend API (e.g., http://localhost:8000)"
        )
        
        # Validate URL format
        if api_url.strip() and api_url.strip() != config.API_BASE_URL:
            if not api_url.strip().startswith(("http://", "https://")):
                st.error("❌ URL must start with http:// or https://")
            else:
                config.API_BASE_URL = api_url.strip()
                API["health"] = f"{config.API_BASE_URL}/health"
                API["predict"] = f"{config.API_BASE_URL}/predict"
                API["analyze_image"] = f"{config.API_BASE_URL}/analyze-image"
                API["model_info"] = f"{config.API_BASE_URL}/model/info"
                st.success("✅ API URL updated!")
        
        st.caption("Leave empty to keep the default. The app will still render without a backend.")

        st.markdown("---")
        st.caption("Tip: Analyze image to auto-fill image features (Colorfulness, SVD Entropy).")
        
        # Show current API status
        st.markdown("---")
        st.subheader("API Status")
        try:
            import requests
            response = requests.get(API["health"], timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend connected")
            else:
                st.warning("⚠️ Backend responding with errors")
        except Exception as e:
            st.error(f"❌ Backend not available: {str(e)[:50]}...")
        
        # Show current configuration
        st.markdown("---")
        st.subheader("Current Config")
        st.text(f"API Base: {config.API_BASE_URL}")
        st.text(f"Max File Size: {config.MAX_FILE_SIZE//(1024*1024)}MB")
        st.text(f"Retry Attempts: {config.RETRY_ATTEMPTS}")
        st.text(f"ReportLab Available: {REPORTLAB}")
        
        # PDF Status
        st.markdown("---")
        st.subheader("PDF Export Status")
        if REPORTLAB:
            st.success("✅ PDF export is ready!")
            st.caption("You can download professional PDF reports")
        else:
            st.warning("⚠️ PDF export not available")
            st.caption("Install reportlab: pip install reportlab>=4.0.0")

    # --- Query param navigation for the big hero CTA ---
    qp = st.query_params
    if qp.get("goto") == "predict":
        st.session_state.page = "predict"
        # optional: clear the param so refreshes don't bounce you back
        try:
            del st.query_params["goto"]
        except Exception:
            pass

    navbar()

    page = st.session_state.page
    if page == "home":
        home_page()
    elif page == "about":
        about_page()
    elif page == "predict":
        predict_page()
    elif page == "results":
        results_page()
    else:
        st.session_state.page = "home"
        home_page()

if __name__ == "__main__":
    main()
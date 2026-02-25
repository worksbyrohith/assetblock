"""
client.py — AssetBlock Client Interface
Premium dark UI for end users to manage their digital assets.
Run: streamlit run src/client/client.py
"""

import streamlit as st
import requests
import pyrebase
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Resolve .env from project root
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

# ── Config: Streamlit secrets (cloud) or env vars (local) ────────────────────
def _secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets if available, else env vars."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

API = _secret("API_BASE_URL", "http://localhost:8000")

# ── Firebase Config ───────────────────────────────────────────────────────────
firebase_config = {
    "apiKey": _secret("FIREBASE_WEB_API_KEY"),
    "authDomain": _secret("FIREBASE_AUTH_DOMAIN", "assetblock-3df65.firebaseapp.com"),
    "projectId": _secret("FIREBASE_PROJECT_ID", "assetblock-3df65"),
    "storageBucket": _secret("FIREBASE_STORAGE_BUCKET", "assetblock-3df65.appspot.com"),
    "messagingSenderId": _secret("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": _secret("FIREBASE_APP_ID", ""),
    "databaseURL": "",
}

firebase = pyrebase.initialize_app(firebase_config)
auth_client = firebase.auth()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AssetBlock | Client",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

/* ─── RESET & BASE ─── */
* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050A14 !important;
    color: #C8D6E5 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070D1A 0%, #0A1020 100%) !important;
    border-right: 1px solid rgba(0, 212, 255, 0.12) !important;
}

/* ─── HIDE DEFAULT ELEMENTS ─── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050A14; }
::-webkit-scrollbar-thumb { background: #00D4FF44; border-radius: 4px; }

/* ─── BUTTONS ─── */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF22, #0066FF22) !important;
    border: 1px solid #00D4FF55 !important;
    color: #00D4FF !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00D4FF44, #0066FF44) !important;
    border-color: #00D4FF !important;
    box-shadow: 0 0 20px #00D4FF33 !important;
    transform: translateY(-1px) !important;
}

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0A1020 !important;
    border: 1px solid #00D4FF33 !important;
    border-radius: 2px !important;
    color: #C8D6E5 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 15px #00D4FF22 !important;
}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] {
    background: #0A1020 !important;
    border: 1px dashed #00D4FF44 !important;
    border-radius: 4px !important;
}

/* ─── METRIC CARDS ─── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0A1525, #0D1A2E) !important;
    border: 1px solid #00D4FF22 !important;
    border-radius: 4px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] {
    color: #00D4FF !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 28px !important;
}
[data-testid="stMetricLabel"] {
    color: #5A7A9A !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {
    border: 1px solid #00D4FF22 !important;
    border-radius: 4px !important;
}

/* ─── SUCCESS / ERROR / WARNING ─── */
.stSuccess, [data-testid="stAlert"][data-baseweb="notification"] {
    background: #001A1A !important;
    border-left: 3px solid #00FF88 !important;
    border-radius: 2px !important;
    color: #00FF88 !important;
}
.stError {
    background: #1A0008 !important;
    border-left: 3px solid #FF2D6B !important;
    border-radius: 2px !important;
}
.stWarning {
    background: #1A1000 !important;
    border-left: 3px solid #FFB800 !important;
    border-radius: 2px !important;
}
.stInfo {
    background: #001A2A !important;
    border-left: 3px solid #00D4FF !important;
    border-radius: 2px !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid #00D4FF22 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5A7A9A !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #00D4FF !important;
    border-bottom-color: #00D4FF !important;
    background: transparent !important;
}

/* ─── SIDEBAR NAV ─── */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    margin: 4px 0;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #5A7A9A;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: rgba(0, 212, 255, 0.08);
    border-color: rgba(0, 212, 255, 0.2);
    color: #00D4FF;
}

/* ─── CUSTOM CARDS ─── */
.asset-card {
    background: linear-gradient(135deg, #0A1525 0%, #0D1A2E 100%);
    border: 1px solid #00D4FF22;
    border-radius: 4px;
    padding: 20px;
    margin: 8px 0;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}
.asset-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #00D4FF, #0066FF);
}
.asset-card:hover {
    border-color: #00D4FF44;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
    transform: translateX(2px);
}
.asset-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 16px;
    color: #E2E8F0;
    margin-bottom: 6px;
}
.asset-hash {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #00D4FF88;
    letter-spacing: 1px;
    margin-bottom: 10px;
    word-break: break-all;
}
.asset-meta {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}
.asset-badge {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 2px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.badge-active { background: #00FF8822; color: #00FF88; border: 1px solid #00FF8833; }
.badge-pending { background: #FFB80022; color: #FFB800; border: 1px solid #FFB80033; }
.badge-suspended { background: #FF2D6B22; color: #FF2D6B; border: 1px solid #FF2D6B33; }

/* ─── PAGE HEADER ─── */
.page-header {
    padding: 24px 0 32px;
    border-bottom: 1px solid #00D4FF15;
    margin-bottom: 32px;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 32px;
    color: #E2E8F0;
    letter-spacing: -0.5px;
    margin: 0;
}
.page-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #00D4FF;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ─── GLOW DIVIDER ─── */
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00D4FF44, transparent);
    margin: 24px 0;
}

/* ─── HASH DISPLAY ─── */
.hash-display {
    background: #020810;
    border: 1px solid #00D4FF33;
    border-radius: 2px;
    padding: 12px 16px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #00D4FF;
    letter-spacing: 1px;
    word-break: break-all;
    margin: 12px 0;
}

/* ─── LOGO ─── */
.brand-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 22px;
    background: linear-gradient(135deg, #00D4FF, #0066FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-tag {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #00D4FF55;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ─── SPINNER ─── */
.stSpinner > div {
    border-color: #00D4FF !important;
}

/* ─── PROGRESS BAR ─── */
.stProgress > div > div {
    background: linear-gradient(90deg, #00D4FF, #0066FF) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "uid": None,
        "email": None,
        "page": "dashboard",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── API Helpers ────────────────────────────────────────────────────────────────
def api_get(endpoint: str):
    try:
        r = requests.get(f"{API}{endpoint}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def api_post(endpoint: str, json=None, data=None, files=None):
    try:
        r = requests.post(f"{API}{endpoint}", json=json, data=data, files=files, timeout=15)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


# ── Auth Page ─────────────────────────────────────────────────────────────────
def show_auth_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Logo
        st.markdown("""
        <div style="text-align:center; margin-bottom:40px;">
            <div class="brand-logo" style="font-size:36px;">AssetBlock</div>
            <div class="brand-tag">Secure Asset Management System</div>
            <div style="margin-top:20px; font-family:'Space Mono',monospace; font-size:10px; 
                        color:#5A7A9A; letter-spacing:2px;">
                SHA-256 VERIFIED · BLOCKCHAIN SECURED · TAMPER PROOF
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["SIGN IN", "SIGN UP"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ACCESS SYSTEM", key="login_btn"):
                if email and password:
                    with st.spinner("Authenticating..."):
                        try:
                            user = auth_client.sign_in_with_email_and_password(email, password)
                            uid = user["localId"]
                            # Auto-register in DB if needed
                            api_post("/users/register", json={"uid": uid, "email": email, "role": "client"})
                            st.session_state.logged_in = True
                            st.session_state.uid = uid
                            st.session_state.email = email
                            st.session_state.user = user
                            st.success("Access granted.")
                            st.rerun()
                        except Exception as e:
                            st.error("Authentication failed. Check your credentials.")
                else:
                    st.warning("Please fill in all fields.")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="reg_username", placeholder="your_handle")
            email_r = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
            pass_r = st.text_input("Password", type="password", key="reg_pass", placeholder="min. 8 characters")
            pass_r2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("CREATE ACCOUNT", key="reg_btn"):
                if not all([username, email_r, pass_r, pass_r2]):
                    st.warning("Please fill in all fields.")
                elif pass_r != pass_r2:
                    st.error("Passwords do not match.")
                elif len(pass_r) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            user = auth_client.create_user_with_email_and_password(email_r, pass_r)
                            uid = user["localId"]
                            api_post("/users/register", json={
                                "uid": uid, "email": email_r,
                                "username": username, "role": "client"
                            })
                            st.session_state.logged_in = True
                            st.session_state.uid = uid
                            st.session_state.email = email_r
                            st.session_state.user = user
                            st.success("Account created successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Registration failed: {str(e)}")

        st.markdown("""
        <div class="glow-divider"></div>
        <div style="text-align:center; font-family:'Space Mono',monospace; font-size:9px; 
                    color:#2A3A4A; letter-spacing:2px;">
            ASSETBLOCK v2.0 · ENCRYPTED · SECURE
        </div>
        """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 8px 28px;">
            <div class="brand-logo">AssetBlock</div>
            <div class="brand-tag">Client Portal</div>
        </div>
        """, unsafe_allow_html=True)

        email_display = st.session_state.email or ""
        st.markdown(f"""
        <div style="background:#0A1525; border:1px solid #00D4FF22; border-radius:4px; 
                    padding:14px 16px; margin-bottom:24px;">
            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A7A9A; 
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">LOGGED IN AS</div>
            <div style="font-family:'Syne',sans-serif; font-size:14px; color:#E2E8F0; 
                        word-break:break-all;">{email_display}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("dashboard", "◈", "Dashboard"),
            ("upload", "⊕", "Upload Asset"),
            ("my_assets", "◱", "My Assets"),
            ("transfer", "⇄", "Transfer"),
            ("activity", "◎", "Activity Log"),
        ]

        for page_id, icon, label in nav_items:
            is_active = st.session_state.page == page_id
            if st.button(f"{icon}  {label}", key=f"nav_{page_id}",
                         help=label, use_container_width=True):
                st.session_state.page = page_id
                st.rerun()

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        if st.button("⊗  SIGN OUT", key="signout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ── Dashboard Page ─────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Dashboard</div>
        <div class="page-subtitle">Asset Overview</div>
    </div>
    """, unsafe_allow_html=True)

    uid = st.session_state.uid
    data = api_get(f"/assets/my/{uid}")
    assets = data.get("assets", []) if data else []

    total = len(assets)
    active = sum(1 for a in assets if a.get("status") == "Active")
    pending = sum(1 for a in assets if a.get("status") == "Pending")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Assets", total)
    with c2:
        st.metric("Active", active)
    with c3:
        st.metric("Pending", pending)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    if assets:
        st.markdown("""
        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A; 
                    letter-spacing:2px; text-transform:uppercase; margin-bottom:16px;">
            RECENT ASSETS
        </div>
        """, unsafe_allow_html=True)

        for asset in assets[:5]:
            status = asset.get("status", "Active")
            badge_class = f"badge-{status.lower()}"
            size_kb = round(asset.get("file_size", 0) / 1024, 1)
            created = str(asset.get("created_at", ""))[:10]

            st.markdown(f"""
            <div class="asset-card">
                <div class="asset-name">{asset.get('asset_name', 'Unknown')}</div>
                <div class="asset-hash">SHA-256: {asset.get('hash', '')}</div>
                <div class="asset-meta">
                    <span class="asset-badge {badge_class}">{status}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A;">
                        {asset.get('file_type','?')}
                    </span>
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A;">
                        {size_kb} KB
                    </span>
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A;">
                        {created}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.3;">◱</div>
            <div style="font-family:'Space Mono',monospace; font-size:12px; color:#2A3A4A; 
                        letter-spacing:2px;">NO ASSETS REGISTERED</div>
            <div style="font-family:'Syne',sans-serif; font-size:14px; color:#3A5A6A; margin-top:8px;">
                Upload your first asset to get started
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Upload Page ────────────────────────────────────────────────────────────────
def page_upload():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Upload Asset</div>
        <div class="page-subtitle">Register New Digital Asset</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#020810; border:1px solid #00D4FF22; border-radius:4px; 
                padding:16px 20px; margin-bottom:28px;">
        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#00D4FF; 
                    letter-spacing:2px; margin-bottom:8px;">HOW IT WORKS</div>
        <div style="font-family:'Syne',sans-serif; font-size:14px; color:#5A7A9A; line-height:1.7;">
            Your file is hashed using SHA-256 to generate a unique 64-character fingerprint. 
            No two files can share the same hash — duplicates are rejected system-wide.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Drop your file here",
            help="Any file type accepted. Max size: 200MB",
            label_visibility="visible"
        )
        description = st.text_area(
            "Asset Description",
            placeholder="Describe this asset...",
            height=100
        )

        if st.button("⊕  REGISTER ASSET", key="upload_btn"):
            if not uploaded_file:
                st.warning("Please select a file to upload.")
            else:
                with st.spinner("Generating SHA-256 hash and registering asset..."):
                    try:
                        file_bytes = uploaded_file.read()
                        files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                        data = {
                            "owner_uid": st.session_state.uid,
                            "owner_email": st.session_state.email,
                            "description": description,
                        }
                        status, resp = api_post("/assets/upload", data=data, files=files)
                        if status == 200:
                            st.success("✓ Asset registered successfully!")
                            asset = resp.get("asset", {})
                            st.markdown(f"""
                            <div style="margin-top:16px;">
                                <div style="font-family:'Space Mono',monospace; font-size:10px; 
                                            color:#5A7A9A; letter-spacing:2px; margin-bottom:8px;">
                                    SHA-256 FINGERPRINT
                                </div>
                                <div class="hash-display">{resp.get('hash','')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style="background:#001A0A; border:1px solid #00FF8833; border-radius:4px;
                                        padding:16px 20px; margin-top:12px;">
                                <div style="display:flex; gap:24px;">
                                    <div>
                                        <div style="font-family:'Space Mono',monospace; font-size:9px; 
                                                    color:#5A7A9A;">ASSET ID</div>
                                        <div style="font-family:'Space Mono',monospace; font-size:18px; 
                                                    color:#00FF88;">#{asset.get('id','?')}</div>
                                    </div>
                                    <div>
                                        <div style="font-family:'Space Mono',monospace; font-size:9px; 
                                                    color:#5A7A9A;">FILE NAME</div>
                                        <div style="font-family:'Syne',sans-serif; font-size:15px; 
                                                    color:#E2E8F0;">{asset.get('asset_name','')}</div>
                                    </div>
                                    <div>
                                        <div style="font-family:'Space Mono',monospace; font-size:9px; 
                                                    color:#5A7A9A;">STATUS</div>
                                        <span class="asset-badge badge-active">ACTIVE</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif status == 409:
                            st.error(f"⚠ Duplicate detected: {resp.get('detail', 'Asset already exists.')}")
                        else:
                            st.error(f"Upload failed: {resp.get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with col2:
        st.markdown("""
        <div style="background:#0A1525; border:1px solid #00D4FF22; border-radius:4px; padding:20px;">
            <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A; 
                        letter-spacing:2px; margin-bottom:16px;">SUPPORTED FORMATS</div>
        """, unsafe_allow_html=True)
        formats = [
            ("📄", "Documents", "PDF, DOCX, TXT"),
            ("🖼", "Images", "PNG, JPG, SVG"),
            ("🎵", "Audio", "MP3, WAV, FLAC"),
            ("🎬", "Video", "MP4, MOV, AVI"),
            ("📦", "Archives", "ZIP, RAR, TAR"),
            ("💻", "Code", "PY, JS, JSON"),
        ]
        for icon, cat, fmts in formats:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:8px 0; 
                        border-bottom:1px solid #0A1525;">
                <span style="font-size:16px;">{icon}</span>
                <div>
                    <div style="font-family:'Syne',sans-serif; font-size:13px; color:#C8D6E5;">{cat}</div>
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A;">{fmts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── My Assets Page ─────────────────────────────────────────────────────────────
def page_my_assets():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">My Assets</div>
        <div class="page-subtitle">Registered Asset Portfolio</div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("Search assets", placeholder="Search by name, hash...", label_visibility="collapsed")
    
    uid = st.session_state.uid
    if search:
        data = api_get(f"/assets/search/{search}")
    else:
        data = api_get(f"/assets/my/{uid}")
    
    assets = data.get("assets", []) if data else []
    # Filter to only user's assets when searching
    if search:
        assets = [a for a in assets if a.get("owner_uid") == uid]

    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A; 
                letter-spacing:2px; margin-bottom:20px;">
        {len(assets)} ASSETS FOUND
    </div>
    """, unsafe_allow_html=True)

    if assets:
        for asset in assets:
            status = asset.get("status", "Active")
            badge_class = f"badge-{status.lower()}"
            size_kb = round(asset.get("file_size", 0) / 1024, 2)

            with st.expander(f"  {asset.get('asset_name', 'Unknown')}  ·  #{asset.get('id')}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"""
                    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A; margin-bottom:4px;">SHA-256 HASH</div>
                    <div class="hash-display">{asset.get('hash', '')}</div>
                    """, unsafe_allow_html=True)
                    if asset.get("description"):
                        st.markdown(f"""
                        <div style="font-family:'Syne',sans-serif; font-size:13px; color:#5A7A9A; margin-top:8px;">
                            {asset.get('description','')}
                        </div>
                        """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style="display:grid; gap:12px;">
                        <div>
                            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A; letter-spacing:2px;">STATUS</div>
                            <span class="asset-badge {badge_class}">{status}</span>
                        </div>
                        <div>
                            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A; letter-spacing:2px;">TYPE</div>
                            <div style="font-family:'Space Mono',monospace; font-size:12px; color:#C8D6E5;">{asset.get('file_type','unknown')}</div>
                        </div>
                        <div>
                            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A; letter-spacing:2px;">SIZE</div>
                            <div style="font-family:'Space Mono',monospace; font-size:12px; color:#C8D6E5;">{size_kb} KB</div>
                        </div>
                        <div>
                            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A; letter-spacing:2px;">REGISTERED</div>
                            <div style="font-family:'Space Mono',monospace; font-size:11px; color:#C8D6E5;">{str(asset.get('created_at',''))[:10]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Transfer history
                hist = api_get(f"/transfer/history/{asset['id']}")
                transfers = hist.get("history", []) if hist else []
                if transfers:
                    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A7A9A; letter-spacing:2px; margin-bottom:8px;">TRANSFER HISTORY</div>
                    """, unsafe_allow_html=True)
                    for t in transfers:
                        st.markdown(f"""
                        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#3A5A6A; padding:4px 0; border-bottom:1px solid #0A1525;">
                            {str(t.get('transferred_at',''))[:16]} · {t.get('from_email','')} → {t.get('to_email','')}
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.3;">◱</div>
            <div style="font-family:'Space Mono',monospace; font-size:12px; color:#2A3A4A; letter-spacing:2px;">
                NO ASSETS FOUND
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Transfer Page ─────────────────────────────────────────────────────────────
def page_transfer():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Transfer Asset</div>
        <div class="page-subtitle">Transfer Ownership to Another User</div>
    </div>
    """, unsafe_allow_html=True)

    uid = st.session_state.uid
    data = api_get(f"/assets/my/{uid}")
    assets = data.get("assets", []) if data else []
    active_assets = [a for a in assets if a.get("status") != "Suspended"]

    if not active_assets:
        st.info("You have no assets available for transfer.")
        return

    col1, col2 = st.columns([1.2, 1])
    with col1:
        asset_options = {f"#{a['id']} — {a['asset_name']}": a["id"] for a in active_assets}
        selected_label = st.selectbox("Select Asset to Transfer", list(asset_options.keys()))
        selected_id = asset_options[selected_label]

        selected_asset = next((a for a in active_assets if a["id"] == selected_id), None)
        if selected_asset:
            st.markdown(f"""
            <div style="background:#0A1525; border:1px solid #00D4FF22; border-radius:4px; 
                        padding:14px 16px; margin:12px 0;">
                <div class="asset-hash">SHA-256: {selected_asset.get('hash','')}</div>
                <div style="display:flex; gap:16px;">
                    <span class="asset-badge badge-{selected_asset.get('status','active').lower()}">
                        {selected_asset.get('status','Active')}
                    </span>
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:#5A7A9A;">
                        {selected_asset.get('file_type','?')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        recipient_email = st.text_input("Recipient Email", placeholder="recipient@example.com")
        note = st.text_input("Transfer Note (optional)", placeholder="e.g. Project handover")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⇄  INITIATE TRANSFER", key="transfer_btn"):
            if not recipient_email:
                st.warning("Please enter the recipient's email.")
            else:
                with st.spinner("Processing transfer..."):
                    status, resp = api_post("/assets/transfer", json={
                        "asset_id": selected_id,
                        "from_uid": uid,
                        "to_email": recipient_email,
                        "note": note,
                    })
                    if status == 200:
                        st.success(f"✓ Asset transferred to {recipient_email}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Transfer failed."))

    with col2:
        st.markdown("""
        <div style="background:#0A1525; border:1px solid #00D4FF22; border-radius:4px; padding:20px;">
            <div style="font-family:'Space Mono',monospace; font-size:10px; color:#00D4FF; 
                        letter-spacing:2px; margin-bottom:16px;">TRANSFER RULES</div>
        """, unsafe_allow_html=True)

        rules = [
            ("◈", "Recipient must be a registered AssetBlock user"),
            ("◈", "You can only transfer assets you own"),
            ("◈", "Transfer is permanent and logged on-chain"),
            ("◈", "Suspended assets cannot be transferred"),
            ("◈", "You cannot transfer an asset to yourself"),
        ]
        for icon, rule in rules:
            st.markdown(f"""
            <div style="display:flex; gap:10px; padding:8px 0; border-bottom:1px solid #0A1020;">
                <span style="color:#00D4FF; font-size:10px; margin-top:2px;">{icon}</span>
                <span style="font-family:'Syne',sans-serif; font-size:13px; color:#5A7A9A;">{rule}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Activity Page ──────────────────────────────────────────────────────────────
def page_activity():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Activity Log</div>
        <div class="page-subtitle">Your Recent Actions</div>
    </div>
    """, unsafe_allow_html=True)

    uid = st.session_state.uid
    data = api_get(f"/activity/{uid}")
    logs = data.get("logs", []) if data else []

    if logs:
        for log in logs:
            action = log.get("action", "")
            colors = {"UPLOAD": "#00D4FF", "TRANSFER": "#FFB800", "REGISTER": "#00FF88"}
            color = colors.get(action, "#5A7A9A")
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; gap:16px; padding:14px 0; 
                        border-bottom:1px solid #0A1525;">
                <div style="min-width:80px;">
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:{color}; 
                                 background:{color}22; border:1px solid {color}33; 
                                 padding:3px 8px; border-radius:2px;">{action}</span>
                </div>
                <div style="flex:1;">
                    <div style="font-family:'Syne',sans-serif; font-size:13px; color:#C8D6E5;">
                        {log.get('details', '')}
                    </div>
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A5A6A; margin-top:4px;">
                        {str(log.get('created_at',''))[:19]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity recorded yet.")


# ── Main App ───────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_auth_page()
        return

    show_sidebar()

    page = st.session_state.page
    if page == "dashboard":
        page_dashboard()
    elif page == "upload":
        page_upload()
    elif page == "my_assets":
        page_my_assets()
    elif page == "transfer":
        page_transfer()
    elif page == "activity":
        page_activity()


if __name__ == "__main__":
    main()

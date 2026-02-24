"""
server.py — AssetBlock Admin / Server Interface
Premium admin panel for system administrators.
Run: streamlit run src/server/server.py
"""

import streamlit as st
import requests
import pyrebase
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Resolve .env from project root (3 levels above src/server/server.py)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

API = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── Firebase Config ───────────────────────────────────────────────────────────
firebase_config = {
    "apiKey": os.getenv("FIREBASE_WEB_API_KEY", ""),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "assetblock-3df65.firebaseapp.com"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "assetblock-3df65"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "assetblock-3df65.appspot.com"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": os.getenv("FIREBASE_APP_ID", ""),
    "databaseURL": "",
}
firebase = pyrebase.initialize_app(firebase_config)
auth_client = firebase.auth()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AssetBlock | Admin",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #07030F !important;
    color: #D0C4E0 !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0515 0%, #0F0820 100%) !important;
    border-right: 1px solid rgba(180, 100, 255, 0.15) !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #07030F; }
::-webkit-scrollbar-thumb { background: #B464FF44; border-radius: 4px; }

.stButton > button {
    background: linear-gradient(135deg, #B464FF22, #7B2FFF22) !important;
    border: 1px solid #B464FF55 !important;
    color: #B464FF !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.3s !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #B464FF44, #7B2FFF44) !important;
    border-color: #B464FF !important;
    box-shadow: 0 0 20px #B464FF33 !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #0F0820 !important;
    border: 1px solid #B464FF33 !important;
    border-radius: 2px !important;
    color: #D0C4E0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #B464FF !important;
    box-shadow: 0 0 15px #B464FF22 !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0F0820, #160D28) !important;
    border: 1px solid #B464FF22 !important;
    border-radius: 4px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] {
    color: #B464FF !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 28px !important;
}
[data-testid="stMetricLabel"] {
    color: #5A4A7A !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #B464FF22 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5A4A7A !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #B464FF !important;
    border-bottom-color: #B464FF !important;
    background: transparent !important;
}

.stSuccess { background: #0A0F05 !important; border-left: 3px solid #00FF88 !important; }
.stError   { background: #0F0508 !important; border-left: 3px solid #FF2D6B !important; }
.stWarning { background: #0F0A00 !important; border-left: 3px solid #FFB800 !important; }
.stInfo    { background: #050A18 !important; border-left: 3px solid #B464FF !important; }

/* Admin-specific */
.admin-card {
    background: linear-gradient(135deg, #0F0820, #160D28);
    border: 1px solid #B464FF22;
    border-radius: 4px;
    padding: 20px;
    margin: 8px 0;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}
.admin-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #B464FF, #7B2FFF);
}
.admin-card:hover {
    border-color: #B464FF44;
    box-shadow: 0 4px 20px rgba(180, 100, 255, 0.1);
}

.brand-logo-admin {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 22px;
    background: linear-gradient(135deg, #B464FF, #7B2FFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.page-header {
    padding: 24px 0 32px;
    border-bottom: 1px solid #B464FF15;
    margin-bottom: 32px;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 32px;
    color: #E2D8F0;
    letter-spacing: -0.5px;
}
.page-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #B464FF;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #B464FF44, transparent);
    margin: 24px 0;
}
.stat-row {
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 6px;
}
.tag {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    padding: 3px 10px;
    border-radius: 2px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.tag-active    { background: #00FF8822; color: #00FF88; border: 1px solid #00FF8833; }
.tag-pending   { background: #FFB80022; color: #FFB800; border: 1px solid #FFB80033; }
.tag-suspended { background: #FF2D6B22; color: #FF2D6B; border: 1px solid #FF2D6B33; }
.tag-client    { background: #00D4FF22; color: #00D4FF; border: 1px solid #00D4FF33; }
.tag-admin     { background: #B464FF22; color: #B464FF; border: 1px solid #B464FF33; }
.hash-display {
    background: #020208;
    border: 1px solid #B464FF33;
    border-radius: 2px;
    padding: 10px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #B464FF;
    word-break: break-all;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False, "uid": None,
        "email": None, "page": "overview",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── API Helpers ────────────────────────────────────────────────────────────────
def api_get(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def api_post(endpoint, json=None):
    try:
        r = requests.post(f"{API}{endpoint}", json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


def api_put(endpoint, json=None):
    try:
        r = requests.put(f"{API}{endpoint}", json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


def api_delete(endpoint, params=None):
    try:
        r = requests.delete(f"{API}{endpoint}", params=params, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}


# ── Auth Page ──────────────────────────────────────────────────────────────────
def show_auth_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:40px;">
            <div class="brand-logo-admin" style="font-size:36px;">AssetBlock</div>
            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#B464FF55; 
                        letter-spacing:3px; text-transform:uppercase; margin-top:4px;">
                Admin Control Panel
            </div>
            <div style="margin-top:20px; font-family:'Space Mono',monospace; font-size:10px; 
                        color:#3A2A5A; letter-spacing:2px;">
                RESTRICTED ACCESS · AUTHORIZED PERSONNEL ONLY
            </div>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Admin Email", placeholder="admin@assetblock.io", key="a_email")
        password = st.text_input("Password", type="password", placeholder="••••••••••", key="a_pass")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⬡  ACCESS ADMIN PANEL", key="admin_login"):
            if email and password:
                with st.spinner("Verifying credentials..."):
                    try:
                        user = auth_client.sign_in_with_email_and_password(email, password)
                        uid = user["localId"]
                        # Check if admin role
                        user_data = api_get(f"/users/{uid}")
                        if not user_data:
                            # Register automatically for now
                            api_post("/users/register", json={"uid": uid, "email": email, "role": "admin"})
                            user_data = {"role": "admin"}
                        st.session_state.logged_in = True
                        st.session_state.uid = uid
                        st.session_state.email = email
                        st.rerun()
                    except Exception:
                        st.error("Authentication failed.")
            else:
                st.warning("Enter credentials.")


# ── Sidebar ────────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 8px 28px;">
            <div class="brand-logo-admin">AssetBlock</div>
            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#B464FF55; 
                        letter-spacing:3px; text-transform:uppercase; margin-top:4px;">
                Admin Panel
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#0F0820; border:1px solid #B464FF22; border-radius:4px; 
                    padding:12px 16px; margin-bottom:24px;">
            <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A; 
                        letter-spacing:2px;">ADMIN SESSION</div>
            <div style="font-family:'Syne',sans-serif; font-size:13px; color:#D0C4E0; 
                        margin-top:4px; word-break:break-all;">{st.session_state.email}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("overview", "⬡", "Overview"),
            ("all_assets", "◰", "All Assets"),
            ("all_users", "◎", "All Users"),
            ("transfers", "⇄", "Transfers"),
            ("activity", "◈", "Activity Log"),
        ]
        for page_id, icon, label in nav_items:
            if st.button(f"{icon}  {label}", key=f"anav_{page_id}", use_container_width=True):
                st.session_state.page = page_id
                st.rerun()

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        if st.button("⊗  SIGN OUT", key="admin_out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ── Overview Page ──────────────────────────────────────────────────────────────
def page_overview():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">System Overview</div>
        <div class="page-subtitle">Platform Statistics</div>
    </div>
    """, unsafe_allow_html=True)

    stats = api_get("/stats")
    if stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("Total Users", stats.get("total_users", 0))
        with c2: st.metric("Total Assets", stats.get("total_assets", 0))
        with c3: st.metric("Transfers", stats.get("total_transfers", 0))
        with c4: st.metric("Active", stats.get("active_assets", 0))
        with c5: st.metric("Pending", stats.get("pending_assets", 0))
    else:
        st.warning("Could not connect to API. Make sure the FastAPI server is running.")
        return

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#B464FF; 
                    letter-spacing:2px; margin-bottom:16px;">RECENT ASSETS</div>
        """, unsafe_allow_html=True)
        data = api_get("/assets/read")
        assets = data.get("assets", [])[:5] if data else []
        for asset in assets:
            status = asset.get("status", "Active")
            st.markdown(f"""
            <div class="admin-card">
                <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:14px; 
                            color:#E2D8F0;">{asset.get('asset_name', '')}</div>
                <div class="hash-display" style="margin:6px 0;">{asset.get('hash','')[:32]}...</div>
                <div class="stat-row">
                    <span class="tag tag-{status.lower()}">{status}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A;">
                        {asset.get('owner_email','unknown')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="font-family:'Space Mono',monospace; font-size:10px; color:#B464FF; 
                    letter-spacing:2px; margin-bottom:16px;">RECENT ACTIVITY</div>
        """, unsafe_allow_html=True)
        logs = api_get("/activity/admin/all")
        log_list = logs.get("logs", [])[:8] if logs else []
        action_colors = {"UPLOAD": "#00D4FF", "TRANSFER": "#FFB800", "REGISTER": "#00FF88"}
        for log in log_list:
            action = log.get("action", "")
            color = action_colors.get(action, "#B464FF")
            st.markdown(f"""
            <div style="display:flex; gap:12px; padding:10px 0; 
                        border-bottom:1px solid #0F0820;">
                <span style="font-family:'Space Mono',monospace; font-size:9px; min-width:72px;
                             color:{color}; background:{color}22; border:1px solid {color}33;
                             padding:2px 8px; border-radius:2px; height:fit-content;">{action}</span>
                <div>
                    <div style="font-family:'Syne',sans-serif; font-size:12px; color:#C0B4D0;">
                        {log.get('details','')}
                    </div>
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A;">
                        {log.get('email','')} · {str(log.get('created_at',''))[:16]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── All Assets Page ────────────────────────────────────────────────────────────
def page_all_assets():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">All Assets</div>
        <div class="page-subtitle">Platform-Wide Asset Registry</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search assets", placeholder="Name, hash, description...", label_visibility="collapsed")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Active", "Pending", "Suspended"], label_visibility="collapsed")

    if search:
        data = api_get(f"/assets/search/{search}")
    else:
        data = api_get("/assets/read")

    assets = data.get("assets", []) if data else []

    if status_filter != "All":
        assets = [a for a in assets if a.get("status") == status_filter]

    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A4A7A; 
                letter-spacing:2px; margin-bottom:16px;">{len(assets)} ASSETS</div>
    """, unsafe_allow_html=True)

    for asset in assets:
        status = asset.get("status", "Active")
        size_kb = round(asset.get("file_size", 0) / 1024, 2)
        with st.expander(f"#{asset['id']}  {asset.get('asset_name', '')}  ·  {asset.get('owner_email', '')}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A; margin-bottom:4px;">SHA-256</div>
                <div class="hash-display">{asset.get('hash','')}</div>
                <div style="font-family:'Syne',sans-serif; font-size:13px; color:#5A4A7A; margin-top:8px;">
                    {asset.get('description') or 'No description'}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="display:grid; gap:10px;">
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; letter-spacing:2px;">STATUS</div>
                        <span class="tag tag-{status.lower()}">{status}</span>
                    </div>
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; letter-spacing:2px;">TYPE</div>
                        <div style="font-family:'Space Mono',monospace; font-size:11px; color:#C0B4D0;">{asset.get('file_type','?')}</div>
                    </div>
                    <div>
                        <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; letter-spacing:2px;">SIZE</div>
                        <div style="font-family:'Space Mono',monospace; font-size:11px; color:#C0B4D0;">{size_kb} KB</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A; letter-spacing:2px; margin-bottom:8px;">
                    UPDATE STATUS
                </div>
                """, unsafe_allow_html=True)
                new_status = st.selectbox(
                    "Status", ["Active", "Pending", "Suspended"],
                    index=["Active","Pending","Suspended"].index(status),
                    key=f"status_{asset['id']}", label_visibility="collapsed"
                )
                if st.button("UPDATE", key=f"upd_{asset['id']}"):
                    r = requests.put(f"{API}/assets/status",
                                     json={"asset_id": asset["id"], "status": new_status}, timeout=10)
                    if r.status_code == 200:
                        st.success("Status updated.")
                        st.rerun()
                    else:
                        st.error("Update failed.")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("⊗ DELETE", key=f"del_{asset['id']}"):
                    r = requests.delete(f"{API}/assets/{asset['id']}",
                                        params={"admin_uid": st.session_state.uid}, timeout=10)
                    if r.status_code == 200:
                        st.success("Asset deleted.")
                        st.rerun()
                    else:
                        st.error("Delete failed.")


# ── All Users Page ─────────────────────────────────────────────────────────────
def page_all_users():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">All Users</div>
        <div class="page-subtitle">Registered User Accounts</div>
    </div>
    """, unsafe_allow_html=True)

    data = api_get("/users")
    users = data.get("users", []) if data else []

    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A4A7A; 
                letter-spacing:2px; margin-bottom:16px;">{len(users)} USERS REGISTERED</div>
    """, unsafe_allow_html=True)

    for user in users:
        role = user.get("role", "client")
        st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; align-items:flex-start; justify-content:space-between;">
                <div>
                    <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:15px; 
                                color:#E2D8F0;">{user.get('username') or user.get('email','').split('@')[0]}</div>
                    <div style="font-family:'Space Mono',monospace; font-size:11px; color:#5A4A7A; margin-top:3px;">
                        {user.get('email','')}
                    </div>
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; margin-top:4px;">
                        UID: {user.get('uid','')[:24]}...
                    </div>
                </div>
                <div style="text-align:right;">
                    <span class="tag tag-{role}">{role.upper()}</span>
                    <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; margin-top:8px;">
                        {str(user.get('created_at',''))[:10]}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Transfers Page ─────────────────────────────────────────────────────────────
def page_transfers():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Transfer Log</div>
        <div class="page-subtitle">All Asset Transfers</div>
    </div>
    """, unsafe_allow_html=True)

    asset_id = st.text_input("Enter Asset ID to view transfer history", placeholder="e.g. 1")
    if asset_id:
        try:
            data = api_get(f"/transfer/history/{int(asset_id)}")
            transfers = data.get("history", []) if data else []
            if transfers:
                st.markdown(f"""
                <div style="font-family:'Space Mono',monospace; font-size:10px; color:#5A4A7A; 
                            letter-spacing:2px; margin-bottom:16px;">
                    {len(transfers)} TRANSFER(S) FOR ASSET #{asset_id}
                </div>
                """, unsafe_allow_html=True)
                for t in transfers:
                    st.markdown(f"""
                    <div class="admin-card">
                        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
                            <div>
                                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A;">FROM</div>
                                <div style="font-family:'Syne',sans-serif; font-size:14px; color:#E2D8F0;">{t.get('from_email','')}</div>
                            </div>
                            <div style="font-size:20px; color:#B464FF;">→</div>
                            <div>
                                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#5A4A7A;">TO</div>
                                <div style="font-family:'Syne',sans-serif; font-size:14px; color:#E2D8F0;">{t.get('to_email','')}</div>
                            </div>
                            <div style="margin-left:auto; text-align:right;">
                                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A;">DATE</div>
                                <div style="font-family:'Space Mono',monospace; font-size:11px; color:#C0B4D0;">{str(t.get('transferred_at',''))[:19]}</div>
                            </div>
                        </div>
                        {f'<div style="font-family:Space Mono,monospace; font-size:10px; color:#5A4A7A; margin-top:8px;">Note: {t.get("note","")}</div>' if t.get("note") else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transfers found for this asset.")
        except ValueError:
            st.error("Please enter a valid numeric Asset ID.")


# ── Activity Page ──────────────────────────────────────────────────────────────
def page_activity():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Activity Log</div>
        <div class="page-subtitle">System-Wide Event Log</div>
    </div>
    """, unsafe_allow_html=True)

    data = api_get("/activity/admin/all")
    logs = data.get("logs", []) if data else []

    action_colors = {"UPLOAD": "#00D4FF", "TRANSFER": "#FFB800", "REGISTER": "#00FF88", "DELETE": "#FF2D6B"}

    for log in logs:
        action = log.get("action", "")
        color = action_colors.get(action, "#B464FF")
        st.markdown(f"""
        <div style="display:flex; gap:16px; padding:12px 0; border-bottom:1px solid #0F0820; align-items:flex-start;">
            <div style="min-width:85px;">
                <span style="font-family:'Space Mono',monospace; font-size:9px; color:{color};
                             background:{color}22; border:1px solid {color}33;
                             padding:3px 8px; border-radius:2px;">{action}</span>
            </div>
            <div style="flex:1;">
                <div style="font-family:'Syne',sans-serif; font-size:13px; color:#C0B4D0;">
                    {log.get('details','')}
                </div>
                <div style="font-family:'Space Mono',monospace; font-size:9px; color:#3A2A5A; margin-top:3px;">
                    {log.get('email','')} · {str(log.get('created_at',''))[:19]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_auth_page()
        return

    show_sidebar()

    page = st.session_state.page
    if page == "overview":
        page_overview()
    elif page == "all_assets":
        page_all_assets()
    elif page == "all_users":
        page_all_users()
    elif page == "transfers":
        page_transfers()
    elif page == "activity":
        page_activity()


if __name__ == "__main__":
    main()

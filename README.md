# ◈ AssetBlock v2.0
### Secure Digital Asset Management System using SHA-256

A blockchain-inspired asset management platform with a premium dark UI, built with Python, FastAPI, Streamlit, PostgreSQL, and Firebase.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Client UI | Streamlit (dark cyberpunk theme) |
| Admin UI | Streamlit (dark purple theme) |
| Database | PostgreSQL |
| Authentication | Firebase Auth |
| Hashing | SHA-256 (Python hashlib) |

---

## Setup Guide

### Step 1 — Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2 — Configure Firebase
1. Create a project at https://console.firebase.google.com
2. Enable **Email/Password** authentication
3. Go to **Project Settings → Service Accounts → Generate new private key**
4. Rename downloaded JSON to `firebase.json` and place it in the `src/` folder
5. Copy the **Web API Key** from Project Settings → General

### Step 3 — Configure `.env`
Open the `.env` file and fill in:
```env
FIREBASE_WEB_API_KEY=your_web_api_key_here
POSTGRE_USER=postgres
POSTGRE_PASSWORD=your_postgres_password
```

### Step 4 — Install & Configure PostgreSQL
1. Download from https://www.postgresql.org/download/
2. Install with default settings, remember your password
3. Run the database setup:
```bash
python src/process.py
```

### Step 5 — Run the Application

**Option A: Double-click `START.bat`** (Windows, recommended)

**Option B: Manual (3 terminals)**

Terminal 1 — API:
```bash
cd src
uvicorn api:app --reload
```

Terminal 2 — Client:
```bash
streamlit run src/client/client.py
```

Terminal 3 — Admin:
```bash
streamlit run src/server/server.py --server.port 8502
```

---

## Access URLs

| Service | URL |
|---------|-----|
| Client Portal | http://localhost:8501 |
| Admin Panel | http://localhost:8502 |
| API Docs | http://localhost:8000/docs |

---

## Features

- **SHA-256 Asset Fingerprinting** — every uploaded file gets a unique 64-char hash
- **Duplicate Detection** — same file cannot be uploaded twice, system-wide
- **Ownership Transfer** — seamlessly transfer assets between registered users
- **Full Transfer History** — complete audit trail for every asset
- **Activity Logging** — all user actions recorded
- **Admin Dashboard** — full platform visibility and control
- **Firebase Authentication** — secure email/password login
- **Premium Dark UI** — cyberpunk-inspired design

---

## Project Structure

```
AssetBlock/
├── src/
│   ├── client/
│   │   └── client.py       ← User dashboard (port 8501)
│   ├── server/
│   │   └── server.py       ← Admin panel (port 8502)
│   ├── api.py              ← FastAPI backend (port 8000)
│   ├── database.py         ← PostgreSQL helpers
│   ├── sha256_hash.py      ← Hashing utility
│   ├── process.py          ← DB initialization script
│   └── firebase.json       ← Firebase credentials (you add this)
├── .streamlit/
│   └── config.toml         ← Streamlit dark theme
├── .env                    ← Secret configuration
├── requirements.txt
├── START.bat               ← One-click Windows startup
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/register` | Register user after Firebase auth |
| GET | `/users/{uid}` | Get user profile |
| POST | `/assets/upload` | Upload & hash an asset |
| GET | `/assets/my/{uid}` | Get user's assets |
| GET | `/assets/read` | Admin: all assets |
| POST | `/assets/transfer` | Transfer asset ownership |
| GET | `/transfer/history/{id}` | Asset transfer history |
| GET | `/stats` | Platform statistics |
| PUT | `/assets/status` | Admin: update asset status |
| DELETE | `/assets/{id}` | Admin: delete asset |

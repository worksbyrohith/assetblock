"""
api.py — AssetBlock FastAPI Backend
Handles all asset operations, user management, and transfer logic.
Run: uvicorn api:app --reload  (from inside /src folder)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
from pathlib import Path
import os
import json

from database import execute_query, execute_one
from sha256_hash import generate_hash

# Resolve .env from project root (one level above src/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── Firebase Admin Init ──────────────────────────────────────────────────────
if not firebase_admin._apps:
    # On cloud (Render): load from FIREBASE_CREDENTIALS_JSON env var
    firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Local dev: load from firebase.json file
        firebase_json_path = os.path.join(os.path.dirname(__file__), "firebase.json")
        cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred)

# ── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AssetBlock API",
    description="🔒 Blockchain-inspired Asset Management System using SHA-256",
    version="2.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    uid: str
    email: str
    username: Optional[str] = ""
    role: Optional[str] = "client"


class TransferRequest(BaseModel):
    asset_id: int
    from_uid: str
    to_email: str
    note: Optional[str] = ""


class AssetStatusUpdate(BaseModel):
    asset_id: int
    status: str


class ActivityLog(BaseModel):
    uid: str
    email: str
    action: str
    details: Optional[str] = ""


# ── Helper: Verify Firebase Token ────────────────────────────────────────────
def verify_token(token: str) -> dict:
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── ROOT ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "app": "AssetBlock",
        "version": "2.0.0",
        "status": "running",
        "message": "🔒 Secure Asset Management System",
    }


# ── USERS ─────────────────────────────────────────────────────────────────────
@app.post("/users/register", tags=["Users"])
def register_user(user: UserCreate):
    """Register a new user after Firebase authentication."""
    existing = execute_one("SELECT * FROM users WHERE uid = %s", (user.uid,))
    if existing:
        return {"message": "User already registered", "user": existing}

    execute_query(
        "INSERT INTO users (uid, email, username, role) VALUES (%s, %s, %s, %s)",
        (user.uid, user.email, user.username or user.email.split("@")[0], user.role),
    )
    log_activity(user.uid, user.email, "REGISTER", "New user registered")
    return {"message": "User registered successfully"}


@app.get("/users/{uid}", tags=["Users"])
def get_user(uid: str):
    """Get user profile by Firebase UID."""
    user = execute_one("SELECT * FROM users WHERE uid = %s", (uid,))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/email/{email}", tags=["Users"])
def get_user_by_email(email: str):
    """Get user by email (used for transfers)."""
    user = execute_one("SELECT * FROM users WHERE email = %s", (email,))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", tags=["Users"])
def get_all_users():
    """Admin: Get all registered users."""
    users = execute_query(
        "SELECT id, uid, email, username, role, created_at FROM users ORDER BY created_at DESC",
        fetch=True,
    )
    return {"users": users, "total": len(users)}


# ── ASSETS ────────────────────────────────────────────────────────────────────
@app.post("/assets/upload", tags=["Assets"])
async def upload_asset(
    file: UploadFile = File(...),
    owner_uid: str = Form(...),
    owner_email: str = Form(...),
    description: str = Form(""),
):
    """Upload a file asset. Generates SHA-256 hash and rejects duplicates."""
    content = await file.read()
    file_hash = generate_hash(content)
    file_size = len(content)
    file_type = file.content_type or "unknown"
    asset_name = file.filename

    # Check for duplicate hash
    existing = execute_one("SELECT * FROM assets WHERE hash = %s", (file_hash,))
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Asset already exists. Registered to asset ID #{existing['id']} — '{existing['asset_name']}'",
        )

    # Insert asset
    result = execute_one(
        """
        INSERT INTO assets (asset_name, hash, file_type, file_size, description, owner_uid)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, asset_name, hash, file_type, file_size, description, status, created_at
        """,
        (asset_name, file_hash, file_type, file_size, description, owner_uid),
    )

    log_activity(owner_uid, owner_email, "UPLOAD", f"Uploaded '{asset_name}' [hash: {file_hash[:16]}...]")
    return {
        "message": "Asset uploaded successfully",
        "asset": result,
        "hash": file_hash,
    }


@app.get("/assets/my/{uid}", tags=["Assets"])
def get_my_assets(uid: str):
    """Get all assets owned by a user."""
    assets = execute_query(
        """
        SELECT a.*, u.email as owner_email, u.username as owner_name
        FROM assets a
        LEFT JOIN users u ON a.owner_uid = u.uid
        WHERE a.owner_uid = %s
        ORDER BY a.created_at DESC
        """,
        (uid,),
        fetch=True,
    )
    return {"assets": assets, "total": len(assets)}


@app.get("/assets/read", tags=["Assets"])
def get_all_assets():
    """Admin: Get all assets across all users."""
    assets = execute_query(
        """
        SELECT a.*, u.email as owner_email, u.username as owner_name
        FROM assets a
        LEFT JOIN users u ON a.owner_uid = u.uid
        ORDER BY a.created_at DESC
        """,
        fetch=True,
    )
    return {"assets": assets, "total": len(assets)}


@app.get("/assets/search/{query}", tags=["Assets"])
def search_assets(query: str):
    """Search assets by name, hash, or description."""
    assets = execute_query(
        """
        SELECT a.*, u.email as owner_email, u.username as owner_name
        FROM assets a
        LEFT JOIN users u ON a.owner_uid = u.uid
        WHERE a.asset_name ILIKE %s OR a.hash ILIKE %s OR a.description ILIKE %s
        ORDER BY a.created_at DESC
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%"),
        fetch=True,
    )
    return {"assets": assets, "total": len(assets)}


@app.get("/assets/{asset_id}", tags=["Assets"])
def get_asset(asset_id: int):
    """Get a single asset by ID."""
    asset = execute_one(
        """
        SELECT a.*, u.email as owner_email, u.username as owner_name
        FROM assets a
        LEFT JOIN users u ON a.owner_uid = u.uid
        WHERE a.id = %s
        """,
        (asset_id,),
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@app.put("/assets/status", tags=["Assets"])
def update_asset_status(payload: AssetStatusUpdate):
    """Admin: Update asset status (Active/Pending/Suspended)."""
    valid_statuses = ["Active", "Pending", "Suspended"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
    execute_query(
        "UPDATE assets SET status = %s, updated_at = %s WHERE id = %s",
        (payload.status, datetime.now(), payload.asset_id),
    )
    return {"message": f"Asset status updated to '{payload.status}'"}


@app.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(asset_id: int, admin_uid: str):
    """Admin: Delete an asset."""
    asset = execute_one("SELECT * FROM assets WHERE id = %s", (asset_id,))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    execute_query("DELETE FROM assets WHERE id = %s", (asset_id,))
    return {"message": "Asset deleted successfully"}


# ── TRANSFER ──────────────────────────────────────────────────────────────────
@app.post("/assets/transfer", tags=["Transfer"])
def transfer_asset(payload: TransferRequest):
    """Transfer asset ownership to another user by email."""
    # Check asset exists and belongs to sender
    asset = execute_one("SELECT * FROM assets WHERE id = %s", (payload.asset_id,))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset["owner_uid"] != payload.from_uid:
        raise HTTPException(status_code=403, detail="You don't own this asset")

    # Find recipient
    recipient = execute_one("SELECT * FROM users WHERE email = %s", (payload.to_email,))
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found. They must be registered on AssetBlock.")

    if recipient["uid"] == payload.from_uid:
        raise HTTPException(status_code=400, detail="Cannot transfer asset to yourself")

    # Get sender info
    sender = execute_one("SELECT * FROM users WHERE uid = %s", (payload.from_uid,))

    # Update asset owner
    execute_query(
        "UPDATE assets SET owner_uid = %s, updated_at = %s WHERE id = %s",
        (recipient["uid"], datetime.now(), payload.asset_id),
    )

    # Log transfer history
    execute_query(
        """
        INSERT INTO transfer_history (asset_id, from_uid, to_uid, from_email, to_email, note)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            payload.asset_id,
            payload.from_uid,
            recipient["uid"],
            sender["email"] if sender else "",
            payload.to_email,
            payload.note,
        ),
    )

    log_activity(
        payload.from_uid,
        sender["email"] if sender else "",
        "TRANSFER",
        f"Transferred asset #{payload.asset_id} to {payload.to_email}",
    )
    return {
        "message": f"Asset successfully transferred to {payload.to_email}",
        "asset_id": payload.asset_id,
        "new_owner": payload.to_email,
    }


@app.get("/transfer/history/{asset_id}", tags=["Transfer"])
def get_transfer_history(asset_id: int):
    """Get complete transfer history for an asset."""
    history = execute_query(
        "SELECT * FROM transfer_history WHERE asset_id = %s ORDER BY transferred_at DESC",
        (asset_id,),
        fetch=True,
    )
    return {"history": history, "total": len(history)}


# ── ACTIVITY LOG ──────────────────────────────────────────────────────────────
def log_activity(uid: str, email: str, action: str, details: str = ""):
    try:
        execute_query(
            "INSERT INTO activity_log (uid, email, action, details) VALUES (%s, %s, %s, %s)",
            (uid, email, action, details),
        )
    except Exception:
        pass  # Don't break main flow if logging fails


@app.get("/activity/{uid}", tags=["Activity"])
def get_user_activity(uid: str, limit: int = 20):
    """Get recent activity log for a user."""
    logs = execute_query(
        "SELECT * FROM activity_log WHERE uid = %s ORDER BY created_at DESC LIMIT %s",
        (uid, limit),
        fetch=True,
    )
    return {"logs": logs}


@app.get("/activity/admin/all", tags=["Activity"])
def get_all_activity(limit: int = 50):
    """Admin: Get all recent activity."""
    logs = execute_query(
        "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT %s",
        (limit,),
        fetch=True,
    )
    return {"logs": logs}


# ── STATS ─────────────────────────────────────────────────────────────────────
@app.get("/stats", tags=["Stats"])
def get_stats():
    """Admin: Get platform statistics."""
    total_users = execute_one("SELECT COUNT(*) as count FROM users")
    total_assets = execute_one("SELECT COUNT(*) as count FROM assets")
    total_transfers = execute_one("SELECT COUNT(*) as count FROM transfer_history")
    active_assets = execute_one("SELECT COUNT(*) as count FROM assets WHERE status = 'Active'")
    pending_assets = execute_one("SELECT COUNT(*) as count FROM assets WHERE status = 'Pending'")

    return {
        "total_users": total_users["count"] if total_users else 0,
        "total_assets": total_assets["count"] if total_assets else 0,
        "total_transfers": total_transfers["count"] if total_transfers else 0,
        "active_assets": active_assets["count"] if active_assets else 0,
        "pending_assets": pending_assets["count"] if pending_assets else 0,
    }

# backend.py
"""
FastAPI SaaS scaffold for real-time resonance API with subscription + API-keys.
Dependencies:
  pip install fastapi uvicorn sqlalchemy pydantic python-jose[cryptography] passlib[bcrypt] stripe
Run:
  uvicorn backend:app --reload --port 8000
Notes:
  - Replace SECRET_KEY and STRIPE_WEBHOOK_SECRET before production.
  - This is a scaffold. Harden, add rate-limits, logging, proper error handling and deployment configs.
"""
import os
import secrets
import time
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import (create_engine, Table, Column, Integer, String, Boolean, Text, MetaData, select, ForeignKey)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
import stripe

# --- CONFIG (change for production) ---
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key_for_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24  # 24h
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test_placeholder")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resonance.db")
# ----------------------------------------

# Stripe init (stub)
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_placeholder")

# DB Setup (SQLAlchemy Core for compactness)
engine: Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_subscribed", Boolean, default=False),  # simple subscription flag
)

api_keys = Table(
    "api_keys", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("key", String, unique=True, nullable=False),
    Column("label", String, nullable=True),
    Column("active", Boolean, default=True),
)

resonance_events = Table(
    "resonance_events", metadata,
    Column("id", Integer, primary_key=True),
    Column("api_key_id", Integer, ForeignKey("api_keys.id")),
    Column("payload", Text),
    Column("ts", Integer),
)

metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Memnora Resonance Matrix API")

# ----------------- Utilities -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    expire = int(time.time()) + (expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------- Pydantic models -----------------
class UserCreate(BaseModel):
    username: str
    password: str

class ApiKeyCreate(BaseModel):
    label: Optional[str] = None

class ResonancePayload(BaseModel):
    spectrum: Dict[str, float]  # example: { "440Hz": 0.8, ... }
    emotion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ----------------- Auth endpoints -----------------
@app.post("/register")
def register(user: UserCreate, db=Depends(get_db)):
    conn = db.connection()
    stmt = select(users).where(users.c.username == user.username)
    res = conn.execute(stmt).first()
    if res:
        raise HTTPException(status_code=400, detail="username exists")
    ins = users.insert().values(username=user.username, hashed_password=hash_password(user.password))
    conn.execute(ins)
    db.commit()
    return {"ok": True, "username": user.username}

@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    conn = db.connection()
    stmt = select(users).where(users.c.username == form_data.username)
    row = conn.execute(stmt).first()
    if not row or not verify_password(form_data.password, row.hashed_password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    access_token = create_access_token({"sub": row.username, "user_id": row.id})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(request: Request, db=Depends(get_db)):
    auth: str = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="invalid token")
    conn = db.connection()
    stmt = select(users).where(users.c.username == username)
    row = conn.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=401, detail="user not found")
    return row

# ----------------- API Key management -----------------
@app.post("/apikeys/create")
def create_api_key(body: ApiKeyCreate, user=Depends(get_current_user), db=Depends(get_db)):
    conn = db.connection()
    raw = secrets.token_urlsafe(32)
    ins = api_keys.insert().values(user_id=user.id, key=raw, label=body.label, active=True)
    conn.execute(ins)
    db.commit()
    # return full key once. Store only server side.
    return {"api_key": raw, "label": body.label}

def validate_api_key(key: str, db) -> Optional[Dict]:
    conn = db.connection()
    stmt = select(api_keys).where(api_keys.c.key == key, api_keys.c.active == True)
    row = conn.execute(stmt).first()
    return dict(row) if row else None

# ----------------- Simple WebSocket manager -----------------
class ConnectionManager:
    def __init__(self):
        # map api_key_id -> list[WebSocket]
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, api_key_id: int):
        await ws.accept()
        self.active.setdefault(api_key_id, []).append(ws)

    def disconnect(self, ws: WebSocket, api_key_id: int):
        conns = self.active.get(api_key_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self.active.pop(api_key_id, None)

    async def broadcast(self, api_key_id: int, message: Dict):
        for ws in list(self.active.get(api_key_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                # stale connection
                try:
                    await ws.close()
                except Exception:
                    pass
                self.disconnect(ws, api_key_id)

manager = ConnectionManager()

# WebSocket endpoint for realtime resonance updates.
# Clients connect with ?api_key=<key>
@app.websocket("/ws/resonance")
async def ws_resonance(websocket: WebSocket, api_key: str = ""):
    if not api_key:
        await websocket.close(code=1008)
        return
    db = SessionLocal()
    try:
        key_row = validate_api_key(api_key, db)
        if not key_row:
            await websocket.close(code=1008)
            return
        api_key_id = key_row["id"]
        await manager.connect(websocket, api_key_id)
        try:
            while True:
                # keep connection alive, optionally receive control messages
                data = await websocket.receive_text()
                # echo control or ignore
                await websocket.send_text("ack")
        except WebSocketDisconnect:
            manager.disconnect(websocket, api_key_id)
    finally:
        db.close()

# ----------------- Resonance input endpoint (server receives updates) -----------------
@app.post("/resonance")
def post_resonance(payload: ResonancePayload, x_api_key: str = Header(None), db=Depends(get_db)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-Api-Key header")
    key_row = validate_api_key(x_api_key, db)
    if not key_row:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    # enforce subscription check on owner
    conn = db.connection()
    stmt_user = select(users).where(users.c.id == key_row["user_id"])
    user_row = conn.execute(stmt_user).first()
    if not user_row or not user_row.is_subscribed:
        raise HTTPException(status_code=402, detail="Subscription required")
    # record event
    ins = resonance_events.insert().values(api_key_id=key_row["id"], payload=str(payload.dict()), ts=int(time.time()))
    conn.execute(ins)
    db.commit()
    # broadcast to websocket clients that subscribed with same api_key
    import asyncio
    asyncio.create_task(manager.broadcast(key_row["id"], {"type": "resonance", "data": payload.dict(), "ts": int(time.time())}))
    return {"ok": True, "received": True}

# ----------------- Stripe webhook (subscription status updates) -----------------
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, db=Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    # verify signature (optional here), in production use stripe.Webhook.construct_event
    try:
        event = stripe.Event.construct_from(stripe.util.json.loads(payload), stripe.api_key)
    except Exception:
        # Fallback: attempt to parse JSON even if signature not validated
        try:
            event = stripe.util.json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid stripe payload")
    # handle relevant webhook types
    ev_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    conn = db.connection()
    if ev_type == "invoice.payment_succeeded":
        # map to user via metadata or customer email - placeholder
        # Example: event['data']['object']['customer'] -> lookup and set users.is_subscribed True
        pass
    elif ev_type in ("customer.subscription.deleted", "invoice.payment_failed"):
        pass
    # For this scaffold we return 200.
    return {"received": True}

# ----------------- Admin helper endpoints (quick checks) -----------------
@app.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "is_subscribed": bool(user.is_subscribed)}

@app.get("/apikeys/list")
def list_apikeys(user=Depends(get_current_user), db=Depends(get_db)):
    conn = db.connection()
    stmt = select(api_keys).where(api_keys.c.user_id == user.id)
    rows = conn.execute(stmt).fetchall()
    return [{"id": r.id, "label": r.label, "active": r.active} for r in rows]

# ----------------- Minimal health check -----------------
@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1"}

# ----------------- Run if executed directly -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
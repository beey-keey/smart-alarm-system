import psycopg
import requests

import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# === CONFIG ===

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = os.getenv("API_KEY")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

SERVER_IP = os.getenv("SERVER_IP")
PORT = os.getenv("PORT")

DATABASE_URL = os.getenv("DATABASE_URL")

alarm_state = "ON"

# === TELEGRAM ===

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }

    requests.post(url, data=data)


def send_alarm_notification():
    message = (
        "🚨 Алармата се задейства!\n\n"
        "👉 Искаш ли да я изключиш?\n"
        f"http://{SERVER_IP}:{PORT}/control"
    )

    send_telegram_message(message)


# === AUTHENTICATION ===

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


# === DATABASE ===

def save_alarm_to_db(alarm_type: str):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO alarm_events (type) VALUES (%s)",
                (alarm_type,),
            )


def get_alarms_from_db():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, type, created_at
                FROM alarm_events
                ORDER BY created_at DESC
                """
            )

            alarms = cur.fetchall()

    return alarms


# === ALARM FROM RASPBERRY PI ===

@app.post("/alarm")
async def receive_alarm(
    request: Request,
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    global alarm_state
    alarm_state = "ON"

    print("🚨 Alarm triggered!")

    save_alarm_to_db("MOTION")

    send_alarm_notification()

    return JSONResponse(
        content={
            "message": "Alarm received and notification sent"
        }
    )


# === LOGIN ===

@app.post("/login")
async def login(request: Request):
    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    if username != USERNAME or password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {
        "access_token": token
    }


# === ACTIVATE ALARM ===

@app.post("/activate")
def activate_alarm():
    global alarm_state

    alarm_state = "ON"

    print("✅ Alarm activated by user")

    return JSONResponse(
        content={
            "status": alarm_state
        }
    )


# === ALARM STATUS ===

@app.get("/status")
def get_alarm_status():
    return JSONResponse(
        content={
            "status": alarm_state
        }
    )


# === ALARM HISTORY ===

@app.get("/alarms")
def get_alarms(user=Depends(verify_token)):
    alarms = get_alarms_from_db()

    return [
        {
            "id": alarm[0],
            "type": alarm[1],
            "created_at": alarm[2],
        }
        for alarm in alarms
    ]


# === TELEGRAM CONTROL PAGE ===

@app.get("/control", response_class=HTMLResponse)
def control_page():
    html = """
    <html>
        <body style="font-family:sans-serif;text-align:center;margin-top:40px;">
            <h2>Искаш ли да изключиш алармата?</h2>

            <form action="/deactivate" method="post">
                <button
                    type="submit"
                    style="padding: 10px 20px; font-size: 16px;"
                >
                    Изключи алармата
                </button>
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=html)


# === DEACTIVATE ALARM ===

@app.post("/deactivate")
def deactivate_alarm():
    global alarm_state

    alarm_state = "OFF"

    print("✅ Alarm turned off by user")

    send_telegram_message(
        "✅ Алармата беше изключена."
    )

    return HTMLResponse(
        content="<h2>Алармата е изключена успешно.</h2>"
    )
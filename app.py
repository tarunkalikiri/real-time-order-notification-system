import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

clients = set()


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/client.html", "r", encoding="utf-8") as f:
        return f.read()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print("Client connected")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")


async def broadcast(message):
    disconnected_clients = []

    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected_clients.append(client)

    for client in disconnected_clients:
        clients.remove(client)


def notification_handler(connection, pid, channel, payload):
    print("Received from DB:", payload)
    asyncio.create_task(broadcast(payload))


async def listen_db():
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.add_listener(
        "orders_channel",
        notification_handler
    )

    print("Listening for database changes...")

    while True:
        await asyncio.sleep(3600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_db())
import asyncio
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

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
        except:
            disconnected_clients.append(client)

    for client in disconnected_clients:
        clients.remove(client)


def notification_handler(connection, pid, channel, payload):
    print("Received from DB:", payload)
    asyncio.create_task(broadcast(payload))


async def listen_db():
    conn = await asyncpg.connect(
        "postgresql://neondb_owner:npg_rZ6XfUpcK2xW@ep-shiny-leaf-aq8v0a7z-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    await conn.add_listener("orders_channel", notification_handler)

    print("Listening for database changes...")

    while True:
        await asyncio.sleep(3600)
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_db())
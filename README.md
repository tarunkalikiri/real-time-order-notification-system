# Real-Time Order Notification System

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- WebSockets

## Architecture

PostgreSQL Trigger
        ↓
LISTEN / NOTIFY
        ↓
FastAPI Backend
        ↓
WebSocket
        ↓
Client

## Features
- Real-time updates
- No polling
- Supports INSERT, UPDATE and DELETE events

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

http://127.0.0.1:8000

## Database

Execute schema.sql to create:

- orders table
- trigger function
- trigger

## Note

Cloud PostgreSQL providers using pooled connections may require direct connections for LISTEN/NOTIFY support.
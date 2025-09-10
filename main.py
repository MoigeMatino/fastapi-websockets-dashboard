import asyncio
import logging
import json
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db import get_db, get_async_db, engine, Base, ASYNC_DATABASE_URL
from models import Inventory, InventoryCreate, InventoryUpdate, InventoryResponse
from notify import PostgresNotifier


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.remove(connection)

manager = ConnectionManager()
notifier = None


async def handle_postgres_notification(data: dict):
    """Handle PostgreSQL notifications and broadcast to WebSocket clients"""
    await manager.broadcast(data)
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    global notifier

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Start PostgreSQL listener
    notifier = PostgresNotifier(ASYNC_DATABASE_URL.replace("+asyncpg", ""))
    notifier.add_listener(handle_postgres_notification)

    # create background task for the listener to eavesdrop on all database interactions
    task = asyncio.create_task(start_postgres_listener())

    yield

    # Shutdown
    task.cancel()
    if notifier:
        await notifier.disconnect()
        

async def start_postgres_listener():
    """Start the PostgreSQL listener"""
    try:
        await notifier.listen_to_channel('inventory_channel')
        await notifier.start_listening()
    except Exception as e:
        logger.error(f"Error in PostgreSQL listener: {e}")

app = FastAPI(title="Real-Time Inventory Tracker", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

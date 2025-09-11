import asyncio
import json
import logging
from typing import Callable

import asyncpg


logger = logging.getLogger(__name__)


class PostgresNotifier:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.listeners = []
        self._stop_event = asyncio.Event()

    async def connect(self):
        """Connect to PostgreSQL"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            logger.info("Connected to PostgreSQL for notifications")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from PostgreSQL")
            
    
    def add_listener(self, callback: Callable):
        """Add a callback function to handle notifications"""
        self.listeners.append(callback)

    
    async def listen_to_channel(self, channel: str):
        """Listen to a specific PostgreSQL channel"""
        if not self.connection: # ensure active connection exists
            await self.connect()
        # set up asyncpg listening on a channe
        await self.connection.add_listener(channel, self._handle_notification)
        logger.info(f"Listening to channel: {channel}")
        
    
    async def _handle_notification_async(self, connection, pid, channel, payload):
        """Actual async logic"""
        try:
            data = json.loads(payload)
            logger.info(f"Received notification: {data}")
            for listener in self.listeners:
                await listener(data)
        except Exception as e:
            logger.error(f"Error handling notification: {e}")

    
    def _handle_notification(self, connection, pid, channel, payload):
        """Sync wrapper for asyncpg"""
        asyncio.create_task(
            self._handle_notification_async(connection, pid, channel, payload)
        )

    async def start_listening(self):
        """Start the listening loop"""
        if not self.connection:
            await self.connect()

        try:
            # keep connection alive without hogging CPU
            await self._stop_event.wait()  
        except asyncio.CancelledError:
            logger.info("Listening cancelled")
        except Exception as e:
            logger.error(f"Error in listening loop: {e}")
        finally:
            await self.disconnect()



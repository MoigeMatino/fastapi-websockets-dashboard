# FastAPI + Postgres + WebSockets Demo

This repository demonstrates real-time communication between a **Postgres database**, a **FastAPI backend**, and a **WebSocket-enabled frontend**.  
It is based on the tutorial from [TestDriven.io](https://testdriven.io/blog/fastapi-postgres-websockets/).

---

## 📖 Overview

The project showcases how to use Postgres's `LISTEN/NOTIFY` feature to push database changes to a FastAPI backend, which then broadcasts updates to connected frontend clients via WebSockets.

**Flow of information:**

1. **Database Event**
   - The application logic fires a trigger in Postgres signalling a data change, which executes a `NOTIFY` command on a specific channel.
   - Example: `NOTIFY channel, 'payload'`.

2. **Backend Listener**
   - FastAPI uses an async connection to Postgres (`asyncpg` or `psycopg`) to `LISTEN` on the same channel.
   - When Postgres sends a notification, the backend receives the payload immediately without polling.

3. **WebSocket Broadcast**
   - The FastAPI backend forwards the payload to all connected WebSocket clients.
   - Clients subscribed to the WebSocket endpoint receive the update in real time.

4. **Frontend Update**
   - The frontend (e.g., a simple HTML/JS app) maintains a WebSocket connection to the backend.
   - Incoming messages are rendered dynamically, ensuring the UI reflects the latest database changes.

---

## 🛠️ Tech Stack

- **Backend**
  - [FastAPI](https://fastapi.tiangolo.com/) for API and WebSocket handling
  - [asyncpg](https://github.com/MagicStack/asyncpg) for Postgres communication
- **Database**
  - PostgreSQL with `LISTEN/NOTIFY`
- **Frontend**
  - Vanilla JavaScript WebSocket client (or any framework of choice)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fastapi-postgres-websockets.git
cd fastapi-postgres-websockets
```

### 2. Set up Postgres
```sql
CREATE DATABASE realtime_demo;
CREATE USER demo_user WITH PASSWORD 'demo_pass';
GRANT ALL PRIVILEGES ON DATABASE realtime_demo TO demo_user;
```

### 3. Run migrations / create tables
Apply schema as needed (see `schema.sql`).

### 4. Start the backend
```bash
uvicorn app.main:app --reload
```

## Data Flow in Detail
| Step | Component                 | Action                                                                                   |
|------|---------------------------|------------------------------------------------------------------------------------------|
| 1    | Postgres                  | A trigger or app logic executes NOTIFY channel, 'payload'.                               |
| 2    | FastAPI Backend           | Maintains a persistent connection and LISTENs on the channel.                            |
| 3    | Backend WebSocket Manager | On receiving a notification, broadcasts the payload to all active WebSocket connections. |
| 4    | Frontend Client           | Receives the message via WebSocket and updates the UI in real time.                      |

## Example
1. Insert a row into the database:
  ```sql
  INSERT INTO inventory (apples) VALUES (10);
  ```

2. Postgres trigger executes:
```sql
   NOTIFY messages_channel, '{"name":apples,"quantity":10}';
  ```

3. FastAPI backend receives the notification and broadcasts it:
  ```sql
  {"name":apples,"quantity":10}
  ```

4. Frontend WebSocket client displays the new message instantly.






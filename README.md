# Django Realtime Chat Backend (API + WebSocket)

Backend-only **chat system** built with:

-   **Django** (REST + ORM)
-   **Django REST Framework** for APIs
-   **Django Channels + Redis** for realtime messaging
-   **JWT** auth for REST API

Supports:

-   🔹 One-to-one (private) chats\
-   🔹 Group chats\
-   🔹 Realtime sending/receiving of messages via WebSocket\
-   🔹 REST APIs for chat + message history

(No frontend---your frontend developer can integrate the API.)

------------------------------------------------------------------------

## 🚀 Tech Stack

-   Python 3.10+
-   Django 4.x
-   Django REST Framework
-   Django Channels
-   Redis
-   JWT (SimpleJWT)

------------------------------------------------------------------------

## 📁 Project Structure

    chat-backend/
    ├─ manage.py
    ├─ requirements.txt
    ├─ core/
    │  ├─ asgi.py
    │  ├─ settings.py
    │  ├─ urls.py
    └─ chat/
       ├─ admin.py
       ├─ models.py
       ├─ serializers.py
       ├─ views.py
       ├─ permissions.py
       ├─ consumers.py
       ├─ routing.py
       └─ migrations/

------------------------------------------------------------------------

## 🔧 Setup Instructions

### 1. Install dependencies

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

requirements.txt:

    Django>=4.2
    djangorestframework>=3.15
    djangorestframework-simplejwt>=5.3
    channels>=4.0
    channels-redis>=4.1

------------------------------------------------------------------------

### 2. Start Redis

    redis-server

Or via Docker:

    docker run --name chat-redis -p 6379:6379 -d redis

------------------------------------------------------------------------

### 3. Apply migrations

    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser

------------------------------------------------------------------------

### 4. Run server

    daphne -b 0.0.0.0 -p 8000 core.asgi:application

------------------------------------------------------------------------

## 🔐 Authentication (JWT)

### Get tokens

`POST /api/token/`

**Body:**

``` json
{
  "username": "your_username",
  "password": "your_password"
}
```

### Refresh token

`POST /api/token/refresh/`

------------------------------------------------------------------------

## 📡 API Endpoints

Base path: `/api/`

------------------------------------------------------------------------

### **1. List user chats**

GET `/api/chats/`

------------------------------------------------------------------------

### **2. Chat detail**

GET `/api/chats/{chat_id}/`

------------------------------------------------------------------------

### **3. Create/fetch private chat**

POST `/api/chats/private/`

``` json
{
  "other_user_id": 2
}
```

------------------------------------------------------------------------

### **4. Create group chat**

POST `/api/chats/group/`

``` json
{
  "name": "Team Chat",
  "member_ids": [2,3]
}
```

------------------------------------------------------------------------

### **5. Add group member**

POST `/api/chats/{chat_id}/add-member/`

------------------------------------------------------------------------

### **6. Remove member**

POST `/api/chats/{chat_id}/remove-member/`

------------------------------------------------------------------------

### **7. List messages**

GET `/api/chats/{chat_id}/messages/`

------------------------------------------------------------------------

### **8. Send message**

POST `/api/chats/{chat_id}/messages/`

``` json
{
  "content": "Hello world!"
}
```

------------------------------------------------------------------------

## 🔥 WebSocket Realtime Messaging

### URL:

    ws://<host>/ws/chat/{chat_id}/

### Client → Server:

``` json
{
  "message": "Hello"
}
```

### Server Broadcast:

``` json
{
  "type": "chat_message",
  "id": "msg-uuid",
  "message": "Hello",
  "sender_id": 1,
  "chat_id": "chat-id",
  "created_at": "2025-01-01T12:00:00Z"
}
```

------------------------------------------------------------------------

## 🧱 Data Models

### Chat

-   id (UUID)
-   is_group (bool)
-   name
-   created_at

### ChatMembership

-   chat FK
-   user FK
-   joined_at

### Message

-   id (UUID)
-   chat FK
-   sender FK
-   content
-   created_at

------------------------------------------------------------------------

## 📌 Frontend Integration Overview

1.  Authenticate → store JWT\
2.  List chats → `/api/chats/`\
3.  Load chat messages → `/api/chats/{chat_id}/messages/`\
4.  Open WebSocket `/ws/chat/{chat_id}/`\
5.  Send message via WS or HTTP\
6.  Listen for incoming broadcast events

------------------------------------------------------------------------

## 📘 License

Free for personal & commercial use.

# WorldWide Chat App

A simple real-time chat application where people from anywhere in the world can connect in one shared room.

## Features
- Real-time messaging using WebSockets
- Join with a display name
- System join/leave events
- UTC timestamps (rendered in each user's local timezone)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then open: `http://localhost:8000`

## Deploy idea
Deploy on any cloud VM/container platform and expose port 8000 with HTTPS for secure WebSockets (`wss://`).

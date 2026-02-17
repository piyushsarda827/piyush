# AI App

A simple AI chat web app using only Python standard library.

## Features

- Chat UI with user/assistant message history
- `/api/chat` endpoint for responses
- Uses OpenAI Chat Completions when `OPENAI_API_KEY` is present
- Falls back to a local helper response when no API key is configured

## Run locally

```bash
python3 app.py
```

Open: <http://localhost:8000>

## Environment variables

- `OPENAI_API_KEY` (optional)
- `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`)
- `PORT` (optional, defaults to `8000`)

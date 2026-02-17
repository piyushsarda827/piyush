import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

SYSTEM_PROMPT = (
    "You are a helpful AI assistant for a demo web app. "
    "Be concise, practical, and friendly."
)


def build_fallback_reply(user_message: str) -> str:
    cleaned = user_message.strip()
    if not cleaned:
        return "Tell me what you're working on, and I'll help you break it down."

    tips = [
        f"You asked: \"{cleaned}\".",
        "Try this quick plan:",
        "1) Define the expected outcome in one sentence.",
        "2) Split the work into small tasks you can finish in under 30 minutes each.",
        "3) Do the first task now and iterate.",
    ]
    return "\n".join(tips)


def call_openai(messages):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return build_fallback_reply(messages[-1]["content"] if messages else "")

    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ],
        "temperature": 0.7,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
    except Exception:
        return build_fallback_reply(messages[-1]["content"] if messages else "")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, content, content_type="text/plain; charset=utf-8"):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
            return self._send(200, html, "text/html; charset=utf-8")

        if self.path == "/static/style.css":
            css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
            return self._send(200, css, "text/css; charset=utf-8")

        return self._send(404, "Not found")

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, "Not found")

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return self._send(400, json.dumps({"error": "Invalid JSON"}), "application/json")

        messages = data.get("messages", [])
        sanitized = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
            if isinstance(m, dict)
        ]

        reply = call_openai(sanitized)
        return self._send(200, json.dumps({"reply": reply}), "application/json")


def run():
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

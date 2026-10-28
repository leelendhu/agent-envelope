"""Check that the Mistral and Gemini API keys in .env both return a reply.

Usage: uv run python scripts/smoke_test.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROMPT = "Reply with exactly: pong"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def post(url: str, headers: dict[str, str], body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def mistral(key: str) -> str:
    model = os.environ.get("MISTRAL_MODEL") or "mistral-small-latest"
    data = post(
        "https://api.mistral.ai/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {"model": model, "messages": [{"role": "user", "content": PROMPT}]},
    )
    return f"{model}: {data['choices'][0]['message']['content'].strip()}"


def gemini(key: str) -> str:
    model = os.environ.get("GEMINI_MODEL") or "gemini-flash-lite-latest"
    data = post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"x-goog-api-key": key},
        {"contents": [{"parts": [{"text": PROMPT}]}]},
    )
    return f"{model}: {data['candidates'][0]['content']['parts'][0]['text'].strip()}"


def main() -> int:
    load_env(Path(__file__).resolve().parent.parent / ".env")
    failed = False
    for name, env_var, call in [
        ("Mistral", "MISTRAL_API_KEY", mistral),
        ("Gemini", "GEMINI_API_KEY", gemini),
    ]:
        key = os.environ.get(env_var, "")
        if not key:
            print(f"[FAIL] {name}: {env_var} is empty in .env")
            failed = True
            continue
        try:
            print(f"[ OK ] {name}: {call(key)}")
        except urllib.error.HTTPError as e:
            print(f"[FAIL] {name}: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
            failed = True
        except Exception as e:
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

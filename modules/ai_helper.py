"""
AI Error Helper module.

Sends an error message / stack trace to the Anthropic Claude API and
returns a plain-language explanation plus suggested fixes.

IMPORTANT: the API key is read from config.json at runtime and is never
hard-coded in source. If no key is configured, the module returns a clear
instructional message instead of failing silently.
"""

import json
import os

import requests

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

SYSTEM_PROMPT = (
    "You are an on-device Android/Python debugging assistant embedded inside "
    "the SalmTool Ultimate app. Given an error message or stack trace, explain "
    "briefly what went wrong in plain language, then list concrete, numbered "
    "steps to fix it. Keep the whole answer under 200 words."
)


def _load_ai_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("ai_helper", {})
    except Exception:
        return {}


def explain_error(error_text, timeout=20):
    """Returns {'ok': bool, 'text': str}. Never raises to the caller —
    network or config problems are surfaced as a readable message."""
    ai_cfg = _load_ai_config()
    api_key = ai_cfg.get("api_key", "")
    model = ai_cfg.get("model", "claude-sonnet-4-6")

    if not api_key:
        return {
            "ok": False,
            "text": (
                "AI Helper is not configured yet. Add your Anthropic API key "
                "to the 'ai_helper.api_key' field in config.json to enable "
                "this feature."
            ),
        }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 500,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": error_text}],
    }

    try:
        resp = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        parts = [block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"]
        return {"ok": True, "text": "\n".join(parts).strip() or "(empty response)"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "text": f"AI request failed: {e}"}
    except Exception as e:
        return {"ok": False, "text": f"Unexpected error: {e}"}

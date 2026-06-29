from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl"

HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json",
}


def scrape(url: str, output_format: str = "markdown") -> dict[str, Any]:
    if not url:
        raise ValueError("Debes indicar una URL")

    fmt = (output_format or "markdown").strip().lower()
    if fmt == "json":
        payload = {
            "url": url,
            "renderHtml": False,
            "elementWait": 5000,
            "returnContentAsJson": True,
        }
    elif fmt == "html":
        payload = {
            "url": url,
            "renderHtml": True,
            "elementWait": 5000,
            "returnMarkdown": False,
            "returnHtml": True,
        }
    else:
        fmt = "markdown"
        payload = {
            "url": url,
            "renderHtml": True,
            "elementWait": 5000,
            "returnMarkdown": True,
        }

    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=300)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Fallo la peticion HTTP: {exc}"}

    if response.status_code != 200:
        text = response.text or ""
        try:
            detail = response.json()
        except ValueError:
            detail = text
        return {
            "success": False,
            "error": f"Cloudflare respondio {response.status_code}",
            "detail": detail,
        }

    try:
        data = response.json()
    except ValueError as exc:
        return {"success": False, "error": f"Respuesta no es JSON valido: {exc}"}

    if data.get("success") is False:
        return {
            "success": False,
            "error": data.get("errors") or data.get("error") or "Cloudflare devolvio error",
        }

    result = data.get("result") or {}

    if fmt == "json":
        content = result.get("data")
    elif fmt == "html":
        content = result.get("html") or result.get("content") or ""
    else:
        content = result.get("content") or result.get("markdown") or ""

    return {"success": True, "format": fmt, "content": content}

"""
PB-QKD client helpers — patent-aligned endpoints (/api/qkd/v1/).

Uses only stdlib urllib so there are no extra dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict

DEFAULT_API_BASE = os.getenv("QBITSHIELD_API_BASE", "http://127.0.0.1:8000")


def _request(
    path: str,
    *,
    method: str,
    api_key: str,
    payload: Dict[str, Any] | None = None,
    api_base: str | None = None,
) -> Dict[str, Any]:
    base = (api_base or DEFAULT_API_BASE).rstrip("/")
    url = base + path
    data = None
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    if payload is not None and method != "GET":
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def generate_key(
    payload: Dict[str, Any],
    *,
    api_key: str,
    api_base: str | None = None,
) -> Dict[str, Any]:
    """POST /api/qkd/v1/generate — generate a PB-QKD key.

    Minimal payload example::

        {
            "primes": [2, 3, 5],
            "times":  [0.1, 0.2, 0.3],
            "bases":  ["Z", "X", "Z"]
        }
    """
    return _request(
        "/api/qkd/v1/generate",
        method="POST",
        api_key=api_key,
        payload=payload,
        api_base=api_base,
    )


def verify_key(
    params: Dict[str, str],
    *,
    api_key: str,
    api_base: str | None = None,
) -> Dict[str, Any]:
    """GET /api/qkd/v1/verify — verify a PB-QKD key.

    Required params: ``final_key``, ``key_material``, ``entropy_digest``.
    """
    base = (api_base or DEFAULT_API_BASE).rstrip("/")
    query = urllib.parse.urlencode(params)
    url = f"{base}/api/qkd/v1/verify?{query}"
    headers = {"X-API-Key": api_key}
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def report_usage(
    payload: Dict[str, Any],
    *,
    api_key: str,
    api_base: str | None = None,
) -> Dict[str, Any]:
    """POST /api/qkd/v1/usage/report — submit a usage report."""
    return _request(
        "/api/qkd/v1/usage/report",
        method="POST",
        api_key=api_key,
        payload=payload,
        api_base=api_base,
    )


# ── Terminal output helpers ───────────────────────────────────────────────

_WIDTH = 64
_BORDER = "║"
_TOP    = "╔" + "═" * (_WIDTH - 2) + "╗"
_MID    = "╠" + "═" * (_WIDTH - 2) + "╣"
_BOT    = "╚" + "═" * (_WIDTH - 2) + "╝"


def _row(label: str, value: str, indent: int = 2) -> str:
    pad = " " * indent
    content = f"{pad}{label:<14}{value}"
    # Truncate long values with ellipsis
    max_val = _WIDTH - 4 - indent - 14
    if len(value) > max_val:
        content = f"{pad}{label:<14}{value[:max_val - 3]}..."
    inner = content.ljust(_WIDTH - 2)
    return f"{_BORDER}{inner}{_BORDER}"


def _blank() -> str:
    return f"{_BORDER}{' ' * (_WIDTH - 2)}{_BORDER}"


def print_result(result: Dict[str, Any]) -> None:
    """Pretty-print a PB-QKD key generation result to stdout.

    Example output::

        ╔══════════════════════════════════════════════════════════════╗
        ║           QbitShield  ·  PB-QKD Key Generation              ║
        ╠══════════════════════════════════════════════════════════════╣
        ║  Session      7b31afe9b26e437e85179...                       ║
        ║  Final Key    54de1c58f816d113a3b7c...                       ║
        ║  Digest       18e57070cf191aac...                            ║
        ║  Primes       [2, 3, 5, 7, 11]                               ║
        ║  Patent       NPA-N417-2025                                  ║
        ║  Runtime      SYMBOLIC                                       ║
        ╠══════════════════════════════════════════════════════════════╣
        ║  Status   ✓  KEY GENERATED                                   ║
        ╚══════════════════════════════════════════════════════════════╝
    """
    title = "QbitShield  ·  PB-QKD Key Generation"
    title_padded = title.center(_WIDTH - 2)
    header = f"{_BORDER}{title_padded}{_BORDER}"

    meta = result.get("metadata", {}) or {}
    primes = result.get("prime_signature", meta.get("primes", []))
    patent = meta.get("patent_ref", "NPA-N417-2025")
    runtime = meta.get("runtime_mode", "SYMBOLIC")

    lines = [
        _TOP,
        header,
        _MID,
        _row("Session", result.get("session_id", "")),
        _row("Final Key", result.get("final_key", "")),
        _row("Digest", result.get("entropy_digest", "")),
        _row("Primes", str(primes)),
        _row("Patent", patent),
        _row("Runtime", runtime),
        _MID,
        _row("Status", "\u2713  KEY GENERATED", indent=3),
        _BOT,
    ]
    print("\n" + "\n".join(lines) + "\n")


def print_verify_result(result: Dict[str, Any]) -> None:
    """Pretty-print a PB-QKD key verification result."""
    valid = result.get("valid", False)
    status_icon = "\u2713" if valid else "\u2717"
    status_text = "VALID" if valid else "INVALID"

    title = "QbitShield  ·  PB-QKD Key Verification"
    title_padded = title.center(_WIDTH - 2)
    header = f"{_BORDER}{title_padded}{_BORDER}"

    lines = [
        _TOP,
        header,
        _MID,
        _row("Expected Key", result.get("expected_final_key", "")),
        _row("Entropy", result.get("entropy_digest", "")),
        _MID,
        _row("Status", f"{status_icon}  {status_text}", indent=3),
        _BOT,
    ]
    print("\n" + "\n".join(lines) + "\n")

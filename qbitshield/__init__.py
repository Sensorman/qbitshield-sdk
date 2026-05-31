"""QbitShield Python SDK — quantum-safe key generation via Prime Harmonic Modulation."""

import os
import sys

__version__ = "2.3.0"

# Banner only shows in interactive TTY terminals, never in production pipelines.
_SHOW_BANNER = (
    os.getenv("QBITSHIELD_BANNER", "auto") != "0"
    and os.getenv("_QBITSHIELD_BANNER_SHOWN") is None
    and hasattr(sys.stderr, "isatty")
    and sys.stderr.isatty()
)

if _SHOW_BANNER:
    _BANNER = (
        "\n"
        " ██████╗ ██████╗ ██╗████████╗███████╗██╗  ██╗██╗███████╗██╗     ██████╗ \n"
        "██╔═══██╗██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗\n"
        "██║   ██║██████╔╝██║   ██║   ███████╗███████║██║█████╗  ██║     ██║  ██║\n"
        "██║▄▄ ██║██╔══██╗██║   ██║   ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║\n"
        "╚██████╔╝██████╔╝██║   ██║   ███████║██║  ██║██║███████╗███████╗██████╔╝\n"
        " ╚══▀▀═╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝\n"
        "\n"
        f"                          Python SDK v{__version__}\n"
        "                          https://qbitshield.com\n"
    )
    try:
        print(_BANNER, file=sys.stderr, flush=True)
        os.environ["_QBITSHIELD_BANNER_SHOWN"] = "1"
    except Exception:
        pass

from .client import QbitShieldClient, KeyResult, PBQKDResult, MetricsResult
from .pb_qkd import generate_key, verify_key, report_usage, print_result, print_verify_result

__all__ = [
    "__version__",
    "QbitShieldClient",
    "KeyResult",
    "PBQKDResult",
    "MetricsResult",
    "generate_key",
    "verify_key",
    "report_usage",
    "print_result",
    "print_verify_result",
]

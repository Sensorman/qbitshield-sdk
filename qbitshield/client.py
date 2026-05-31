"""QbitShield SDK — main client."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from hashlib import sha256, sha512
from typing import Any, Dict, List, Optional, Sequence

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DEFAULT_BASE_URL = os.getenv(
    "QBITSHIELD_API_BASE",
    "https://api.qbitshield.com",
)

# Status codes that are transient and safe to retry
_RETRYABLE = {429, 502, 503, 504}
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds

SUPPORTED_STRENGTHS: Sequence[int] = (128, 192, 256)


# ── Low-level HTTP (stdlib only, no requests dependency) ──────────────────

def _http(
    url: str,
    *,
    method: str,
    api_key: str,
    payload: Dict[str, Any] | None = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    data = None
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "User-Agent": "qbitshield-python/2.3.0",
    }
    if payload is not None and method != "GET":
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in _RETRYABLE and attempt < _MAX_RETRIES - 1:
                delay = int(exc.headers.get("Retry-After", _RETRY_BASE_DELAY * (2 ** attempt)))
                time.sleep(min(delay, 30))
                last_err = exc
                continue
            raise
        except urllib.error.URLError as exc:
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BASE_DELAY * (2 ** attempt))
                last_err = exc
                continue
            raise
    raise last_err  # type: ignore[misc]


# ── Response dataclasses ──────────────────────────────────────────────────

@dataclass
class KeyResult:
    """Result of a /api/v2/generate call.

    When IBM Quantum Runtime is active in the backend, `quantum_hardware` is
    True and `entropy_job_id` contains the IBM Quantum job ID — independently
    verifiable at https://quantum.ibm.com/jobs/{entropy_job_id}.

    NIST SP 800-22 per-key validation results are in `nist_score` and
    `nist_grade`. Source-level 15/15 evidence: IACR ePrint 2026/109748.
    """
    key_id: str
    key: str
    security_level: int
    latency_ms: float
    timestamp: str
    source: str = "unknown"
    quantum_hardware: bool = False
    entropy_job_id: Optional[str] = None
    nist_score: Optional[float] = None
    nist_grade: Optional[str] = None
    entropy_bits: Optional[float] = None
    qasm_circuit: str = ""
    hash_proof: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_quantum(self) -> bool:
        """True when key entropy came from real IBM quantum hardware."""
        return self.quantum_hardware

    @property
    def verification_url(self) -> Optional[str]:
        """IBM Quantum job verification URL, or None if simulator was used."""
        if self.entropy_job_id:
            return f"https://quantum.ibm.com/jobs/{self.entropy_job_id}"
        return None


@dataclass
class PBQKDResult:
    """Result of a /api/qkd/v1/generate call."""
    session_id: str
    final_key: str
    entropy_digest: str
    prime_signature: List[int]
    metadata: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsResult:
    total_keys: int
    average_latency_ms: float
    uptime_percentage: float
    nist_pass_rate: float
    raw: Dict[str, Any] = field(default_factory=dict)


# ── QKD namespace (/api/v2/) ──────────────────────────────────────────────

class _QKDNamespace:
    """client.qkd — classic Prime Harmonics v2 key generation."""

    def __init__(self, client: "QbitShieldClient") -> None:
        self._c = client

    def generate_key(
        self,
        security_level: int = 256,
        *,
        enable_nist_validation: bool = True,
        metadata: Dict[str, Any] | None = None,
    ) -> KeyResult:
        """POST /api/v2/generate — generate a quantum-safe key."""
        payload: Dict[str, Any] = {
            "security_level": security_level,
            "enable_nist_validation": enable_nist_validation,
        }
        if metadata:
            payload["metadata"] = metadata
        data = self._c._post("/api/v2/generate", payload)
        return KeyResult(
            key_id=data.get("key_id", ""),
            key=data.get("key", ""),
            security_level=data.get("security_level", security_level),
            latency_ms=data.get("latency_ms", 0.0),
            timestamp=data.get("timestamp", ""),
            source=data.get("source", "unknown"),
            quantum_hardware=data.get("quantum_hardware", False),
            entropy_job_id=data.get("entropy_job_id"),
            nist_score=data.get("nist_score"),
            nist_grade=data.get("nist_grade"),
            entropy_bits=data.get("entropy_bits"),
            qasm_circuit=data.get("qasm_circuit", ""),
            hash_proof=data.get("hash_proof", ""),
            raw=data,
        )

    async def generate_key_async(
        self,
        security_level: int = 256,
        *,
        enable_nist_validation: bool = True,
        metadata: Dict[str, Any] | None = None,
    ) -> KeyResult:
        """Async version of generate_key."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate_key(
                security_level,
                enable_nist_validation=enable_nist_validation,
                metadata=metadata,
            ),
        )

    def validate_key(
        self,
        *,
        key: str,
        qasm: str,
        hash_proof: str,
    ) -> Dict[str, Any]:
        """Validate a previously generated key against its QASM circuit and proof."""
        return self._c._post(
            "/api/v2/validate",
            {"key": key, "qasm": qasm, "hash_proof": hash_proof},
        )

    def get_metrics(self, hours: int = 24) -> MetricsResult:
        """GET /api/v2/metrics — performance and usage metrics."""
        data = self._c._get(f"/api/v2/metrics?hours={hours}")
        perf = data.get("metrics", {}).get("performance", {})
        return MetricsResult(
            total_keys=perf.get("total_keys_generated", 0),
            average_latency_ms=perf.get("average_latency_ms", 0.0),
            uptime_percentage=perf.get("uptime_percentage", 0.0),
            nist_pass_rate=perf.get("nist_compliance_rate", 0.0),
            raw=data,
        )

    async def get_metrics_async(self, hours: int = 24) -> MetricsResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.get_metrics(hours))


# ── PB-QKD namespace (/api/qkd/v1/) ──────────────────────────────────────

class _PBQKDNamespace:
    """client.pbqkd — patent-aligned PB-QKD (NPA-N417).

    Uses prime-indexed phase rotations: |ψ_p⟩ = (1/√2)(|0⟩ + exp(iπ/p)|1⟩)
    """

    def __init__(self, client: "QbitShieldClient") -> None:
        self._c = client

    def generate_key(
        self,
        primes: List[int],
        times: List[float],
        bases: List[str],
        *,
        base_phase_strategy: str = "linear",
        strategy_params: Dict[str, float] | None = None,
        derive_prime_key: bool = False,
        runtime_mode: str = "SYMBOLIC",
        metadata: Dict[str, Any] | None = None,
    ) -> PBQKDResult:
        """POST /api/qkd/v1/generate — patent-aligned prime-basis QKD.

        Args:
            primes: List of prime indices (e.g. [2, 3, 5, 7])
            times:  Time parameters, same length as primes
            bases:  Measurement bases — "Z" or "X"
            base_phase_strategy: "linear" (default) or "fixed"
            strategy_params:  e.g. {"start": 0.05, "increment": 0.01}
            derive_prime_key: Include prime-derived component in key material
            runtime_mode:     "SYMBOLIC" (default), "SIMULATION", "HARDWARE"
            metadata:         Arbitrary metadata attached to the session

        Returns:
            PBQKDResult with session_id, final_key (SHA3-256), prime_signature
        """
        payload: Dict[str, Any] = {
            "primes": primes,
            "times": times,
            "bases": [b.upper() for b in bases],
            "base_phase_strategy": base_phase_strategy,
            "derive_prime_key": derive_prime_key,
            "runtime_mode": runtime_mode,
        }
        if strategy_params:
            payload["strategy_params"] = strategy_params
        if metadata:
            payload["metadata"] = metadata
        data = self._c._post("/api/qkd/v1/generate", payload)
        return PBQKDResult(
            session_id=data.get("session_id", ""),
            final_key=data.get("final_key", ""),
            entropy_digest=data.get("entropy_digest", ""),
            prime_signature=data.get("prime_signature", primes),
            metadata=data.get("metadata") or {},
            raw=data,
        )

    async def generate_key_async(
        self,
        primes: List[int],
        times: List[float],
        bases: List[str],
        **kwargs: Any,
    ) -> PBQKDResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.generate_key(primes, times, bases, **kwargs)
        )

    def verify_key(
        self,
        *,
        final_key: str,
        key_material: str,
        entropy_digest: str,
    ) -> Dict[str, Any]:
        """GET /api/qkd/v1/verify — verify key material produces the expected final key."""
        params = urllib.parse.urlencode(
            {"final_key": final_key, "key_material": key_material, "entropy_digest": entropy_digest}
        )
        return self._c._get(f"/api/qkd/v1/verify?{params}")

    def report_usage(
        self,
        *,
        client_id: str,
        session_id: str,
        status: str = "success",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """POST /api/qkd/v1/usage/report — record a PB-QKD usage event."""
        return self._c._post(
            "/api/qkd/v1/usage/report",
            {"client_id": client_id, "session_id": session_id,
             "status": status, "metadata": metadata or {}},
        )


# ── Main client ───────────────────────────────────────────────────────────

class QbitShieldClient:
    """QbitShield Python SDK client.

    Usage::

        from qbitshield import QbitShieldClient

        client = QbitShieldClient(api_key="qs_your_api_key")

        # Classic Prime Harmonics v2
        res = client.qkd.generate_key(security_level=256)
        print(res.key_id, res.key[:16] + "...")

        # Patent-aligned PB-QKD (NPA-N417)
        pb = client.pbqkd.generate_key(
            primes=[2, 3, 5, 7],
            times=[0.1, 0.2, 0.3, 0.4],
            bases=["Z", "X", "Z", "X"],
        )
        print(pb.final_key)

        # AES-GCM encryption with quantum key material
        cipher = client.encrypt_message("secret", res.key, strength=256)
        plain  = client.decrypt_message(cipher, res.key, strength=256)
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or ""
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.latency_log: List[Dict[str, Any]] = []

        self.qkd = _QKDNamespace(self)
        self.pbqkd = _PBQKDNamespace(self)

    # -- Internal HTTP helpers --

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("API key is required")
        return _http(
            self.base_url + path,
            method="POST",
            api_key=self.api_key,
            payload=payload,
            timeout=self.timeout,
        )

    def _get(self, path: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("API key is required")
        return _http(
            self.base_url + path,
            method="GET",
            api_key=self.api_key,
            timeout=self.timeout,
        )

    # -- AES-GCM crypto helpers --

    def _derive_aes_key(self, key_material: str, strength: int) -> bytes:
        if strength not in SUPPORTED_STRENGTHS:
            raise ValueError(f"Unsupported strength {strength}; choose from {SUPPORTED_STRENGTHS}")
        cleaned = key_material.strip().lower().replace("0x", "")
        raw = bytes.fromhex(cleaned)
        if not raw:
            raise ValueError("Key material is empty or invalid hex")
        digest = sha256(raw).digest() if strength <= 256 else sha512(raw).digest()
        return digest[: {128: 16, 192: 24, 256: 32}[strength]]

    def encrypt_message(self, message: str, key: str, strength: int = 256) -> str:
        """Encrypt a UTF-8 string with AES-GCM using quantum key material."""
        if not message:
            raise ValueError("Message must not be empty")
        aes_key = self._derive_aes_key(key, strength)
        iv = os.urandom(12)
        t0 = time.perf_counter()
        ct = AESGCM(aes_key).encrypt(iv, message.encode(), None)
        self.latency_log.append({"op": "encrypt", "latency_ms": (time.perf_counter() - t0) * 1000})
        return base64.b64encode(iv + ct).decode()

    def decrypt_message(self, ciphertext_b64: str, key: str, strength: int = 256) -> str:
        """Decrypt an AES-GCM ciphertext produced by encrypt_message."""
        if not ciphertext_b64:
            raise ValueError("Ciphertext must not be empty")
        raw = base64.b64decode(ciphertext_b64)
        if len(raw) <= 12:
            raise ValueError("Ciphertext too short")
        iv, ct = raw[:12], raw[12:]
        aes_key = self._derive_aes_key(key, strength)
        t0 = time.perf_counter()
        try:
            plaintext = AESGCM(aes_key).decrypt(iv, ct, None)
        except InvalidTag as exc:
            raise InvalidTag("Authentication failed — wrong key or corrupted data") from exc
        self.latency_log.append({"op": "decrypt", "latency_ms": (time.perf_counter() - t0) * 1000})
        return plaintext.decode()

    def encrypt_payload(self, payload: Any, key: str, strength: int = 256) -> str:
        """Serialize payload to JSON and encrypt with AES-GCM."""
        return self.encrypt_message(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False), key, strength
        )

    def decrypt_payload(self, ciphertext_b64: str, key: str, strength: int = 256) -> Any:
        """Decrypt and deserialize a JSON payload encrypted with encrypt_payload."""
        return json.loads(self.decrypt_message(ciphertext_b64, key, strength))

    # Backwards-compat alias
    def get_latest_key(
        self,
        token: str = "",
        *,
        security_level: int = 256,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Legacy method — prefer client.qkd.generate_key()."""
        res = self.qkd.generate_key(security_level=security_level, metadata=metadata)
        return {
            "key": res.key,
            "timestamp": res.timestamp,
            "source": res.source,
            "metadata": res.raw.get("metadata"),
        }

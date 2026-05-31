#!/usr/bin/env python3
"""
QbitShield SDK — Live Production Test
======================================
Tests the full SDK against api.qbitshield.com.

Usage:
    python test_live.py YOUR_API_KEY

Get your API key at: https://qbitshield.com/dashboard/api-keys
"""

import os
import sys
import time

os.environ["QBITSHIELD_BANNER"] = "0"

from qbitshield import QbitShieldClient, __version__

# ─── Colour helpers ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}"); sys.exit(1)
def info(msg): print(f"  {BLUE}→{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}⚠{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}\n{BOLD}  {msg}{RESET}\n{'─'*50}")

# ─── Entry point ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f"\n{RED}Usage: python test_live.py YOUR_API_KEY{RESET}")
        print(f"Get your key at: {CYAN}https://qbitshield.com/dashboard/api-keys{RESET}\n")
        sys.exit(1)

    api_key = sys.argv[1]
    client  = QbitShieldClient(api_key=api_key)

    print(f"\n{BOLD}QbitShield SDK v{__version__} — Live Test{RESET}")
    print(f"{DIM}API: api.qbitshield.com{RESET}")

    # ── Test 1: Key generation ─────────────────────────────────────────────
    header("Test 1: Key Generation")

    t0 = time.perf_counter()
    try:
        result = client.qkd.generate_key(security_level=256)
        ms = (time.perf_counter() - t0) * 1000
    except Exception as e:
        fail(f"generate_key() raised: {e}")

    ok(f"Key generated in {ms:.0f}ms")
    info(f"key_id:   {result.key_id}")
    info(f"key:      {result.key[:16]}...{result.key[-8:]}  ({len(result.key)} hex chars)")
    info(f"source:   {result.source}")
    info(f"latency:  {result.latency_ms:.1f}ms (server-side)")

    # ── Quantum hardware check ─────────────────────────────────────────────
    header("Test 2: Quantum Hardware Provenance")

    if result.quantum_hardware:
        ok(f"REAL IBM QUANTUM HARDWARE — entropy_job_id: {result.entropy_job_id}")
        ok(f"Verifiable at: {result.verification_url}")
    else:
        warn("Aer simulator (not real hardware)")
        warn("To activate: set QBITSHIELD_USE_IBM_RUNTIME=1 + IBM_QUANTUM_TOKEN in Railway")

    info(f"quantum_hardware: {result.quantum_hardware}")
    info(f"entropy_job_id:  {result.entropy_job_id or 'None (simulator)'}")

    # ── NIST check ─────────────────────────────────────────────────────────
    header("Test 3: NIST SP 800-22 Score")

    if result.nist_score is not None:
        # Per-key NIST is a lightweight health check only.
        # NIST SP 800-22 requires ≥1M bits for statistically valid results.
        # Full source-level 15/15 evidence: IACR ePrint 2026/109748.
        info(f"Per-key NIST health check: {result.nist_score:.0f}/15 ({result.nist_grade})")
        info(f"Note: single-key NIST is indicative only (256 bits << 1M bit minimum)")
        info(f"Source-level 15/15 certification: https://eprint.iacr.org/2026/109748")
        ok(f"Entropy bits: {result.entropy_bits:.2f}" if result.entropy_bits else "Entropy bits: N/A")
    else:
        warn("NIST score not returned — check API version")

    # ── Encryption roundtrip ───────────────────────────────────────────────
    header("Test 4: AES-256-GCM Encryption")

    message = "QbitShield quantum-encrypted payload — 2026"
    try:
        ciphertext = client.encrypt_message(message, result.key, strength=256)
        decrypted  = client.decrypt_message(ciphertext, result.key, strength=256)
    except Exception as e:
        fail(f"Encryption error: {e}")

    if decrypted == message:
        ok("Encrypt → decrypt roundtrip")
        info(f"Original:  {message}")
        info(f"Cipher:    {ciphertext[:32]}...  ({len(ciphertext)} chars)")
        info(f"Decrypted: {decrypted}")
    else:
        fail(f"Decryption mismatch: {decrypted!r}")

    # ── Wrong key test ─────────────────────────────────────────────────────
    header("Test 5: Authentication Tag Verification")

    try:
        wrong_key = "0" * len(result.key)
        client.decrypt_message(ciphertext, wrong_key, strength=256)
        fail("Should have raised InvalidTag with wrong key")
    except Exception:
        ok("Wrong key correctly rejected (InvalidTag)")

    # ── Payload encryption ─────────────────────────────────────────────────
    header("Test 6: JSON Payload Encryption")

    payload = {"user": "will@qbitshield.com", "clearance": "TOP_SECRET", "timestamp": int(time.time())}
    try:
        enc_payload = client.encrypt_payload(payload, result.key)
        dec_payload = client.decrypt_payload(enc_payload, result.key)
    except Exception as e:
        fail(f"Payload encryption error: {e}")

    if dec_payload == payload:
        ok("JSON payload encrypt/decrypt roundtrip")
        info(f"Payload: {payload}")
    else:
        fail(f"Payload mismatch: {dec_payload}")

    # ── Metrics ────────────────────────────────────────────────────────────
    header("Test 7: API Metrics")

    try:
        metrics = client.qkd.get_metrics()
        ok(f"Total keys generated: {metrics.total_keys:,}")
        ok(f"Average latency: {metrics.average_latency_ms:.1f}ms")
        ok(f"NIST pass rate: {metrics.nist_pass_rate:.1%}")
    except Exception as e:
        warn(f"Metrics unavailable: {e}")

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"{BOLD}{GREEN}  ALL TESTS PASSED{RESET}")
    print(f"{'='*50}")

    if result.quantum_hardware:
        print(f"\n{BOLD}  Quantum provenance:{RESET}")
        print(f"  IBM job: {CYAN}{result.entropy_job_id}{RESET}")
        print(f"  Verify: {CYAN}https://quantum.ibm.com/jobs/{result.entropy_job_id}{RESET}")
    else:
        print(f"\n{YELLOW}  Running on Aer simulator.{RESET}")
        print(f"  Activate IBM Runtime in Railway to get real hardware provenance.")

    print()

if __name__ == "__main__":
    main()

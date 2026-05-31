"""
QbitShield Python SDK — Unit Tests
===================================
Tests run without hitting the live API (responses are mocked).
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

# Suppress banner during tests
os.environ["QBITSHIELD_BANNER"] = "0"

from qbitshield import QbitShieldClient, KeyResult, __version__


# ─── Mock response builders ────────────────────────────────────────────────

def _mock_key_response(
    *,
    quantum_hardware: bool = False,
    entropy_job_id: str | None = None,
    nist_score: float | None = 14.0,
    nist_grade: str | None = "A",
    entropy_bits: float | None = 255.9,
    source: str = "aer_simulator",
) -> dict:
    return {
        "success": True,
        "key_id": "qbit_test_001",
        "key": "a1b2c3d4e5f6" * 8,
        "security_level": 256,
        "latency_ms": 42.5,
        "timestamp": "2026-05-31T18:00:00Z",
        "source": source,
        "quantum_hardware": quantum_hardware,
        "entropy_job_id": entropy_job_id,
        "nist_score": nist_score,
        "nist_grade": nist_grade,
        "entropy_bits": entropy_bits,
        "qasm_circuit": "OPENQASM 2.0;",
        "hash_proof": "qbit_proof_1234",
    }


# ─── Version ──────────────────────────────────────────────────────────────

class TestVersion(unittest.TestCase):
    def test_version_format(self):
        parts = __version__.split(".")
        self.assertEqual(len(parts), 3)
        for p in parts:
            self.assertTrue(p.isdigit(), f"Non-numeric version part: {p}")

    def test_version_is_current(self):
        major, minor, patch_ = [int(x) for x in __version__.split(".")]
        self.assertGreaterEqual(major * 100 + minor * 10 + patch_, 230,
                                "Version must be >= 2.3.0")


# ─── KeyResult dataclass ─────────────────────────────────────────────────

class TestKeyResult(unittest.TestCase):
    def _make(self, **kwargs) -> KeyResult:
        data = _mock_key_response(**kwargs)
        return KeyResult(
            key_id=data["key_id"],
            key=data["key"],
            security_level=data["security_level"],
            latency_ms=data["latency_ms"],
            timestamp=data["timestamp"],
            source=data["source"],
            quantum_hardware=data["quantum_hardware"],
            entropy_job_id=data["entropy_job_id"],
            nist_score=data["nist_score"],
            nist_grade=data["nist_grade"],
            entropy_bits=data["entropy_bits"],
            qasm_circuit=data["qasm_circuit"],
            hash_proof=data["hash_proof"],
            raw=data,
        )

    def test_simulator_result(self):
        r = self._make(quantum_hardware=False, entropy_job_id=None)
        self.assertFalse(r.quantum_hardware)
        self.assertFalse(r.is_quantum)
        self.assertIsNone(r.entropy_job_id)
        self.assertIsNone(r.verification_url)

    def test_hardware_result(self):
        jid = "d8e3v607jphs739k6kig"
        r = self._make(quantum_hardware=True, entropy_job_id=jid,
                       source="ibm_quantum_runtime")
        self.assertTrue(r.quantum_hardware)
        self.assertTrue(r.is_quantum)
        self.assertEqual(r.entropy_job_id, jid)
        self.assertEqual(r.verification_url,
                         f"https://quantum.ibm.com/jobs/{jid}")

    def test_nist_fields(self):
        r = self._make(nist_score=15.0, nist_grade="A+", entropy_bits=255.99)
        self.assertEqual(r.nist_score, 15.0)
        self.assertEqual(r.nist_grade, "A+")
        self.assertAlmostEqual(r.entropy_bits, 255.99)

    def test_raw_contains_full_response(self):
        r = self._make()
        self.assertIn("success", r.raw)
        self.assertTrue(r.raw["success"])


# ─── QbitShieldClient ─────────────────────────────────────────────────────

class TestQbitShieldClient(unittest.TestCase):
    def setUp(self):
        self.client = QbitShieldClient(api_key="qs_test_key_abc123")

    def test_client_initializes(self):
        self.assertEqual(self.client.api_key, "qs_test_key_abc123")
        self.assertEqual(self.client.base_url, "https://api.qbitshield.com")
        self.assertIsNotNone(self.client.qkd)
        self.assertIsNotNone(self.client.pbqkd)

    def test_custom_base_url(self):
        c = QbitShieldClient(api_key="k", base_url="https://staging.qbitshield.com/")
        self.assertEqual(c.base_url, "https://staging.qbitshield.com")  # trailing slash stripped

    def test_no_api_key_raises(self):
        c = QbitShieldClient()
        with self.assertRaises(ValueError):
            c.qkd.generate_key()

    @patch("qbitshield.client._http")
    def test_generate_key_aer(self, mock_http):
        mock_http.return_value = _mock_key_response()
        result = self.client.qkd.generate_key(security_level=256)
        self.assertIsInstance(result, KeyResult)
        self.assertEqual(result.key_id, "qbit_test_001")
        self.assertFalse(result.quantum_hardware)
        self.assertIsNone(result.entropy_job_id)
        self.assertEqual(result.nist_score, 14.0)

    @patch("qbitshield.client._http")
    def test_generate_key_ibm_hardware(self, mock_http):
        jid = "d8e3v607jphs739k6kig"
        mock_http.return_value = _mock_key_response(
            quantum_hardware=True,
            entropy_job_id=jid,
            source="ibm_quantum_runtime",
            nist_score=15.0,
            nist_grade="A+",
        )
        result = self.client.qkd.generate_key()
        self.assertTrue(result.quantum_hardware)
        self.assertTrue(result.is_quantum)
        self.assertEqual(result.entropy_job_id, jid)
        self.assertEqual(result.verification_url,
                         f"https://quantum.ibm.com/jobs/{jid}")
        self.assertEqual(result.nist_grade, "A+")

    @patch("qbitshield.client._http")
    def test_generate_key_passes_security_level(self, mock_http):
        mock_http.return_value = _mock_key_response()
        self.client.qkd.generate_key(security_level=128)
        call_args = mock_http.call_args
        payload = call_args.kwargs.get("payload") or call_args[1].get("payload")
        self.assertEqual(payload["security_level"], 128)

    @patch("qbitshield.client._http")
    def test_raw_field_preserved(self, mock_http):
        resp = _mock_key_response()
        mock_http.return_value = resp
        result = self.client.qkd.generate_key()
        self.assertEqual(result.raw["success"], True)
        self.assertIn("entropy_job_id", result.raw)


# ─── AES-GCM encryption ───────────────────────────────────────────────────

class TestEncryption(unittest.TestCase):
    def setUp(self):
        self.client = QbitShieldClient(api_key="qs_test")
        self.key = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"

    def test_encrypt_decrypt_roundtrip(self):
        message = "Hello, quantum world!"
        ct = self.client.encrypt_message(message, self.key, strength=256)
        pt = self.client.decrypt_message(ct, self.key, strength=256)
        self.assertEqual(pt, message)

    def test_encrypt_produces_different_ciphertext_each_time(self):
        ct1 = self.client.encrypt_message("same", self.key)
        ct2 = self.client.encrypt_message("same", self.key)
        self.assertNotEqual(ct1, ct2)  # different IVs

    def test_encrypt_payload_roundtrip(self):
        payload = {"key": "value", "number": 42}
        ct = self.client.encrypt_payload(payload, self.key)
        result = self.client.decrypt_payload(ct, self.key)
        self.assertEqual(result, payload)

    def test_wrong_key_raises(self):
        from cryptography.exceptions import InvalidTag
        ct = self.client.encrypt_message("secret", self.key)
        wrong_key = "0" * 64
        with self.assertRaises(InvalidTag):
            self.client.decrypt_message(ct, wrong_key)

    def test_unsupported_strength_raises(self):
        with self.assertRaises(ValueError):
            self.client.encrypt_message("test", self.key, strength=512)

    def test_latency_log_populated(self):
        self.client.encrypt_message("test", self.key)
        self.assertTrue(len(self.client.latency_log) > 0)
        self.assertIn("op", self.client.latency_log[-1])


# ─── HTTP retry logic ─────────────────────────────────────────────────────

class TestRetryLogic(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_retries_on_429(self, mock_open):
        import urllib.error
        http_err = urllib.error.HTTPError(
            url="", code=429, msg="Too Many Requests",
            hdrs=MagicMock(get=lambda k, d=None: d), fp=None
        )
        mock_open.side_effect = [http_err, http_err, http_err]
        from qbitshield.client import _http
        with self.assertRaises(urllib.error.HTTPError):
            _http("http://test", method="GET", api_key="k")
        self.assertEqual(mock_open.call_count, 3)

    @patch("urllib.request.urlopen")
    def test_succeeds_after_retry(self, mock_open):
        import urllib.error
        http_err = urllib.error.HTTPError(
            url="", code=503, msg="Service Unavailable",
            hdrs=MagicMock(get=lambda k, d=None: d), fp=None
        )
        success_resp = MagicMock()
        success_resp.__enter__ = lambda s: s
        success_resp.__exit__ = MagicMock(return_value=False)
        success_resp.read.return_value = json.dumps({"ok": True}).encode()
        mock_open.side_effect = [http_err, success_resp]
        from qbitshield.client import _http
        result = _http("http://test", method="GET", api_key="k")
        self.assertEqual(result["ok"], True)
        self.assertEqual(mock_open.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

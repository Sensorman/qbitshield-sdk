# QbitShield SDK

Official Python SDK for generating quantum-safe keys using the [QbitShield](https://qbitshield.com) API, powered by Prime Harmonic Modulation.

---

## 🔧 Installation

```bash
pip install git+https://github.com/Sensorman/qbitshield-sdk.git


from qbitshield import client


## Usage

api_key = "your-api-key"
key = client.generate_key(api_key, return_full=True)

print("✅ Hashed Key:", key["hashed_key"])
print("🧬 Measured Bits:", key["measured_bits"])
print("📄 QASM:", key["qasm"][:100] + "...")

---

## 🔐 Endpoint

- **URL:** `https://qbitshield-api-258062438248.us-central1.run.app/qkd/generate`
- **Method:** `GET`
- **Headers:**
  - `api-key`: Your QbitShield API key
- **Returns:**
  - `hashed_key` (SHA-256 string)
  - `measured_bits` (qubit collapse result)
  - `qasm` (full circuit structure in OpenQASM 3.0)
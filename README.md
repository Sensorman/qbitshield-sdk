
# 🔐 QbitShield SDK

**Quantum-Safe Key Infrastructure Powered by Prime Harmonic Modulation**

QbitShield is a deterministic entropy SDK that generates quantum-safe encryption keys using our patented Prime Harmonic Modulation (PHM) and Prime-Based Quantum Key Distribution (PB-QKD). Designed for developers building post-quantum resilient systems.

---

## 📦 Installation

### PyPI (coming soon)

```bash

pip install qbitshield
```

### GitHub (latest version)

```bash

pip install git+https://github.com/qbitshield/qbitshield-sdk.git
```

---

## 🚀 Quick Start

```python
from qbitshield import QbitShieldClient

client = QbitShieldClient(api_key="your_api_key_here")
result = client.generate_key()

print("Key:", result['key'])
print("Bits:", result['bits'])
print("QASM:", result['qasm'])
```

---

## 🧪 Features

- 🧠 Deterministic entropy using prime harmonics
- 🔐 SHA-256 compatible secure key output
- 🧬 QASM stream support for quantum simulation
- ☁️ API-ready and developer-friendly
- ⚡ Modular and lightweight

---

## 📁 File Structure

```
qbitshield-sdk/
├── qbitshield/           # SDK logic
│   ├── __init__.py
│   └── client.py
├── tests/                # Unit tests
│   └── test_client.py
├── examples/             # Jupyter notebooks
│   └── demo_notebook.ipynb
├── setup.py              # Package config
├── pyproject.toml        # Modern build config
├── README.md             # This file
```

---

## 🧪 Testing

```bash

pytest tests/
```

---

## 📘 Notebook Demo

Explore the [`examples/demo_notebook.ipynb`](examples/demo_notebook.ipynb) for a step-by-step walkthrough using the SDK.

---

## 🌐 API Endpoint

All requests are routed through:

```
https://theqbitshield-api-258062438248.us-central1.run.app/qkd/generate
```

You must include your API key in the headers:
```python
headers = {
  "Authorization": "Bearer YOUR_API_KEY"
}
```

---

## 🧠 About QbitShield

QbitShield is building the future of post-quantum encryption by introducing deterministic entropy generation through Prime Harmonic Modulation. We eliminate reliance on vulnerable randomness, enabling truly secure key infrastructures for finance, Web3, and defense.

- Website: [qbitshield.com](https://qbitshield.com)
- Email: will@qbitshield.com

> “Random is broken. Deterministic is the future.”

---

## 📄 License

MIT License — use, fork, and build freely.

## 📄 License & IP Notice

This SDK is released under the [MIT License](LICENSE), allowing free use, modification, and distribution of the code.

However, QbitShield’s core technologies — including **Prime Harmonic Modulation (PHM)** and **Prime-Based Quantum Key Distribution (PB-QKD)** — are **patent-pending** under U.S. and WIPO filings. Commercial use of QbitShield’s deterministic entropy framework beyond this SDK requires a licensing agreement.

By using this SDK, you agree not to reverse engineer, extract, or commercialize the protected cryptographic methods outside the scope of its intended use.

For licensing inquiries, contact:  
📧 **will@qbitshield.com**
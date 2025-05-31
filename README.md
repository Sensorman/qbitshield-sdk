# QbitShield SDK

[![PyPI version](https://badge.fury.io/py/qbitshield.svg)](https://badge.fury.io/py/qbitshield)

QbitShield is a quantum-safe key generation SDK leveraging Prime Harmonic Modulation to produce deterministic entropy-rich keys suitable for post-quantum cryptography and secure communications.

## 🚀 Installation

```bash
pip install qbitshield
```

## 🔐 Usage

```python
from qbitshield import QbitShieldClient

client = QbitShieldClient(api_key="QSDemo")
result = client.generate_key()

print("Key:", result["key"])
print("QASM:", result["qasm"])
```

## 📦 Features

- Deterministic, entropy-rich quantum keys
- Prime Harmonic Modulation engine
- QASM circuit output for validation
- Developer-friendly SDK interface

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

## 🌐 Learn More

Visit [qbitshield.com](https://qbitshield.com) for full documentation and roadmap.

## 🛠 Maintainer

**Will Daoud**  
[will@qbitshield.com](mailto:will@qbitshield.com)

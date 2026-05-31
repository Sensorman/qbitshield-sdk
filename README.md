# QbitShield SDK  v2.1.0

Python client for QbitShield's quantum-safe key distribution API — Prime Harmonic Modulation, patent NPA-N417.

## Installation

```bash
pip install qbitshield
```

## Quick Start — QbitShieldClient

```python
from qbitshield import QbitShieldClient

client = QbitShieldClient(api_key="YOUR_API_KEY")

# Classic Prime Harmonics v2
res = client.qkd.generate_key(security_level=256)
print(res.key_id, res.key[:16] + "...")

# Patent-aligned PB-QKD (NPA-N417)
pb = client.pbqkd.generate_key(
    primes=[2, 3, 5, 7, 11],
    times=[0.1, 0.2, 0.3, 0.4, 0.5],
    bases=["Z", "X", "Z", "X", "Z"],
)
print(pb.final_key)

# AES-GCM encryption with quantum key material
cipher = client.encrypt_message("top secret", res.key, strength=256)
plain  = client.decrypt_message(cipher, res.key, strength=256)
```

## Quick Start — Functional API (PB-QKD)

```python
from qbitshield import generate_key, verify_key, report_usage
from qbitshield.pb_qkd import print_result

result = generate_key(
    {
        "primes": [2, 3, 5, 7, 11],
        "times":  [0.1, 0.2, 0.3, 0.4, 0.5],
        "bases":  ["Z", "X", "Z", "X", "Z"],
    },
    api_key="YOUR_API_KEY",
    api_base="https://qbitshield-api.railway.app",
)

print_result(result)
```

Terminal output of `print_result()`:

```
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
```

## Key Verification

```python
from qbitshield import verify_key

check = verify_key(
    {
        "final_key":      result["final_key"],
        "key_material":   "...",
        "entropy_digest": result["entropy_digest"],
    },
    api_key="YOUR_API_KEY",
)
print("Valid:", check["valid"])
```

## API Base URL

| Environment | URL |
|-------------|-----|
| Production  | `https://qbitshield-api.railway.app` |
| Local       | `http://localhost:8000` |

Override the default with the `QBITSHIELD_API_BASE` environment variable.

## Resources

- [User Guide](USER_GUIDE.md) — full reference including error handling, retries, best practices
- [API Reference](https://qbitshield-api.railway.app/docs)
- [Enterprise Portal](https://qbitshield-enterprise.vercel.app)

## License

MIT License. See `LICENSE` for details.

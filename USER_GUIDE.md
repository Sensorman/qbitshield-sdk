# QbitShield SDK User Guide

Complete guide to using the QbitShield Python SDK for quantum-safe key distribution and encryption.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication & API Keys](#authentication--api-keys)
4. [SDK Core Concepts](#sdk-core-concepts)
5. [Key Generation](#key-generation)
6. [Encryption & Decryption](#encryption--decryption)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Common Use Cases](#common-use-cases)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Examples & Code Samples](#examples--code-samples)

---

## Introduction

### What is QbitShield?

QbitShield is the world's first NIST SP 800-22 certified quantum-safe key infrastructure platform. It provides enterprise-grade quantum key generation using **Prime Harmonic Modulation**, delivering cryptographic keys that are resistant to both classical and quantum computing threats.

### Why Quantum-Safe Keys Matter

Traditional cryptographic systems rely on mathematical problems that quantum computers can solve efficiently. As quantum computing advances, these systems become vulnerable. QbitShield generates keys using quantum simulation techniques that remain secure even against quantum attacks, providing **post-quantum cryptography** protection.

### SDK Capabilities

The QbitShield Python SDK provides:

- **Quantum Key Generation**: Request NIST-certified quantum keys via REST API
- **Local Encryption**: Encrypt and decrypt data using AES-GCM with quantum-derived keys
- **Key Derivation**: Automatically derive encryption keys from quantum key material
- **Performance Monitoring**: Built-in latency logging for benchmarking
- **Error Handling**: Comprehensive exception handling and retry logic
- **Type Safety**: Full type hints for better developer experience

### NIST SP 800-22 Certification

QbitShield is the first open-source framework to achieve **perfect NIST SP 800-22 certification** (15/15 tests passing). This certification validates that the generated keys have:

- True randomness properties
- Statistical independence
- Uniform distribution
- No predictable patterns

All keys generated through the SDK are backed by this certification, ensuring cryptographic security suitable for enterprise and government applications.

---

## Getting Started

### Installation

Install the QbitShield SDK using pip:

```bash
pip install qbitshield-sdk
```

When you install the package, you'll see a welcome banner displaying the QbitShield branding and version information.

### Quick Start Example

Here's a minimal example to get you started:

```python
from qbitshield.client import QbitShieldClient

# Initialize the client
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-api-key-here"
)

# Generate a quantum key
key_data = client.get_latest_key(
    token="your-auth0-token",  # Optional for some endpoints
    security_level=256
)

# Encrypt a message
message = "Sensitive data to protect"
ciphertext = client.encrypt_message(message, key_data["key"], strength=256)

# Decrypt the message
plaintext = client.decrypt_message(ciphertext, key_data["key"], strength=256)

print(f"Original: {message}")
print(f"Decrypted: {plaintext}")
```

### Basic Setup

#### 1. Import the Client

```python
from qbitshield.client import QbitShieldClient
```

#### 2. Configure the Base URL

The SDK needs to know where your QbitShield API is hosted:

```python
# Production API
client = QbitShieldClient("https://qbitshield-api.railway.app/api")

# Local development
client = QbitShieldClient("http://localhost:8000/api")

# Custom deployment
client = QbitShieldClient("https://your-custom-domain.com/api")
```

#### 3. Set Your API Key

API keys are required for all key generation requests:

```python
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="sk_live_your_api_key_here"
)
```

#### 4. Optional: Configure Session

The SDK uses a `requests.Session` for connection pooling. You can customize it:

```python
import requests

session = requests.Session()
session.headers.update({"User-Agent": "MyApp/1.0"})

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-api-key",
    session=session
)
```

---

## Authentication & API Keys

### Obtaining API Keys

API keys are obtained through the QbitShield enterprise portal:

1. Sign up at [qbitshield-enterprise.vercel.app](https://qbitshield-enterprise.vercel.app)
2. Navigate to your dashboard
3. Go to API Keys section
4. Generate a new API key
5. Copy and securely store the key

**Important**: API keys are secret credentials. Never commit them to version control or expose them in client-side code.

### API Key Format

API keys follow this format:
- **Test keys**: `sk_test_...`
- **Live keys**: `sk_live_...`
- **Demo keys**: `QSDemo` (for testing only)

### Setting Up Authentication

#### Using API Keys Only

For basic key generation, you only need an API key:

```python
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="sk_live_your_key"
)

# Generate key without Auth0 token
key_data = client.get_latest_key(token="", security_level=256)
```

#### Using Auth0 Tokens (Enterprise)

For enterprise features and organization-scoped access, you'll need an Auth0 ID token:

```python
# Get Auth0 token from your authentication flow
auth0_token = get_auth0_id_token()  # Your implementation

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="sk_live_your_key"
)

# Generate key with Auth0 token
key_data = client.get_latest_key(
    token=auth0_token,
    security_level=256
)
```

The SDK automatically includes both the API key (in `X-API-Key` header) and the Auth0 token (in `Authorization: Bearer` header) when making requests.

### API Key Management

#### Environment Variables

Store API keys securely using environment variables:

```python
import os
from qbitshield.client import QbitShieldClient

api_key = os.getenv("QBITSHIELD_API_KEY")
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key=api_key
)
```

#### Key Rotation

Regularly rotate your API keys:

1. Generate a new key in the dashboard
2. Update your application configuration
3. Test with the new key
4. Revoke the old key

### Security Best Practices

1. **Never commit keys**: Use environment variables or secret management systems
2. **Use different keys**: Separate keys for development, staging, and production
3. **Rotate regularly**: Change keys every 90 days or after security incidents
4. **Monitor usage**: Check your dashboard for unusual activity
5. **Restrict permissions**: Use the minimum required API key permissions

### Rate Limiting and Quotas

API keys are subject to rate limits based on your subscription tier:

| Tier | Rate Limit | Monthly Quota |
|------|------------|---------------|
| Research | 10 req/min | 1,000 keys |
| Professional | 60 req/min | 100,000 keys |
| Enterprise | 200 req/min | 1,000,000 keys |
| Strategic | Custom | Unlimited |

When rate limits are exceeded, the API returns `429 Too Many Requests`. The SDK will raise a `requests.HTTPError` that you can handle:

```python
import requests
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

try:
    key_data = client.get_latest_key(token="", security_level=256)
except requests.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded. Please wait before retrying.")
        # Implement exponential backoff
    else:
        raise
```

---

## SDK Core Concepts

### QbitShieldClient Class

The `QbitShieldClient` is the main interface to the QbitShield API. It's a dataclass that manages:

- **Base URL**: The API endpoint
- **Session**: HTTP session for connection pooling
- **API Key**: Authentication credential
- **Latency Log**: Performance metrics

```python
@dataclass
class QbitShieldClient:
    base_url: str
    session: requests.Session
    latency_log: List[Dict[str, Any]]
    api_key: Optional[str]
```

### Base URL Configuration

The base URL should point to your QbitShield API instance:

```python
# Standard format
base_url = "https://qbitshield-api.railway.app/api"

# The SDK appends endpoint paths
# Final URL: https://qbitshield-api.railway.app/api/qkd/generate
```

**Important**: Don't include a trailing slash. The SDK handles path joining automatically.

### Session Management

The SDK uses `requests.Session` for efficient HTTP connections:

- **Connection pooling**: Reuses TCP connections
- **Cookie persistence**: Maintains session state
- **Header management**: Centralized header configuration

You can customize the session:

```python
import requests
from qbitshield.client import QbitShieldClient

# Create custom session
session = requests.Session()
session.timeout = 60  # 60 second timeout
session.headers.update({
    "User-Agent": "MyApp/1.0",
    "X-Custom-Header": "value"
})

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key",
    session=session
)
```

### Error Handling Patterns

The SDK raises standard Python exceptions:

#### Network Errors

```python
import requests
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

try:
    key_data = client.get_latest_key(token="", security_level=256)
except requests.exceptions.ConnectionError:
    print("Failed to connect to API. Check your network.")
except requests.exceptions.Timeout:
    print("Request timed out. The API may be slow.")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

#### API Errors

```python
try:
    key_data = client.get_latest_key(token="", security_level=256)
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 403:
        print("API key lacks required permissions")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    elif e.response.status_code >= 500:
        print("Server error. Try again later.")
    else:
        raise
```

#### SDK Errors

```python
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api"
    # Missing api_key
)

try:
    key_data = client.get_latest_key(token="", security_level=256)
except ValueError as e:
    print(f"Configuration error: {e}")
    # Output: "API key is required – supply api_key when constructing QbitShieldClient"
```

#### Encryption Errors

```python
from cryptography.exceptions import InvalidTag
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

key_data = client.get_latest_key(token="", security_level=256)
ciphertext = client.encrypt_message("secret", key_data["key"], strength=256)

# Try to decrypt with wrong key
try:
    wrong_key = "0" * 64  # Wrong key
    client.decrypt_message(ciphertext, wrong_key, strength=256)
except InvalidTag:
    print("Decryption failed: wrong key or corrupted data")
```

---

## Key Generation

### Understanding Quantum Key Generation

QbitShield generates cryptographic keys using **Prime Harmonic Modulation**, a quantum simulation technique that produces truly random key material. The process:

1. **Quantum Simulation**: Uses quantum circuit simulation to generate entropy
2. **Prime Modulation**: Applies prime number harmonics for enhanced randomness
3. **NIST Validation**: Runs 15 statistical tests to certify randomness
4. **Key Material**: Outputs cryptographically secure key bytes

### Using `get_latest_key()`

The `get_latest_key()` method requests a new quantum key from the API:

```python
key_data = client.get_latest_key(
    token="auth0-token-or-empty-string",
    security_level=256,
    metadata={"application": "my-app", "user_id": "123"}
)
```

#### Parameters

- **`token`** (str): Auth0 ID token (optional, can be empty string)
- **`security_level`** (int): Key security level (128, 192, 256, or 384)
- **`metadata`** (dict, optional): Custom metadata to attach to the key

#### Return Value

Returns a dictionary with:

```python
{
    "key": "694887d326681a6d1ba2d5b21e575787b8bea356065e0695c77641efba6b6341",
    "entropy": 99.9,
    "timestamp": "2025-01-18T20:37:33.254699+00:00",
    "nist": {
        "certification_status": "PASS",
        "tests_passed": 15,
        "total_tests": 15,
        "compliance_level": "CERTIFICATION_READY"
    },
    "metadata": {"application": "my-app", "user_id": "123"}
}
```

### Security Levels

Choose the security level based on your use case:

| Level | Use Case | NIST Compliance |
|-------|----------|-----------------|
| **128-bit** | Research, development, testing | Basic |
| **192-bit** | Professional applications | Recommended |
| **256-bit** | Enterprise, government (default) | Full |
| **384-bit** | Strategic, military, high-security | Full |

```python
# Research/development
research_key = client.get_latest_key(token="", security_level=128)

# Enterprise (recommended)
enterprise_key = client.get_latest_key(token="", security_level=256)

# High-security applications
strategic_key = client.get_latest_key(token="", security_level=384)
```

### Response Structure

#### Key Field

The `key` field contains the raw quantum key material as a hexadecimal string:

```python
key_hex = key_data["key"]
# Example: "694887d326681a6d1ba2d5b21e575787b8bea356065e0695c77641efba6b6341"

# Convert to bytes if needed
import binascii
key_bytes = binascii.unhexlify(key_hex)
```

#### Entropy Field

The `entropy` field indicates the quality of randomness (0-100):

```python
entropy = key_data["entropy"]
# Example: 99.9

if entropy < 95.0:
    print("Warning: Lower entropy detected")
```

#### Timestamp Field

The `timestamp` field is an ISO 8601 formatted UTC timestamp:

```python
from datetime import datetime

timestamp_str = key_data["timestamp"]
timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
print(f"Key generated at: {timestamp}")
```

#### NIST Validation Field

The `nist` field contains NIST SP 800-22 test results:

```python
nist = key_data["nist"]

print(f"Status: {nist['certification_status']}")  # "PASS"
print(f"Tests: {nist['tests_passed']}/{nist['total_tests']}")  # "15/15"
print(f"Compliance: {nist['compliance_level']}")  # "CERTIFICATION_READY"
```

### Metadata and Customization

Attach custom metadata to keys for tracking and organization:

```python
key_data = client.get_latest_key(
    token="",
    security_level=256,
    metadata={
        "application": "secure-messaging",
        "user_id": "user_12345",
        "session_id": "sess_abc",
        "environment": "production"
    }
)

# Metadata is returned in the response
print(key_data["metadata"])
# Output: {"application": "secure-messaging", "user_id": "user_12345", ...}
```

---

## Encryption & Decryption

### Key Derivation Process

The SDK automatically derives encryption keys from quantum key material using cryptographic hash functions:

```python
def _derive_key(self, key_material: str, strength: int) -> bytes:
    # Clean and parse hex string
    cleaned = key_material.strip().lower().replace("0x", "")
    raw = bytes.fromhex(cleaned)
    
    # Hash based on strength
    if strength <= 256:
        digest = sha256(raw).digest()  # 32 bytes
    else:
        digest = sha512(raw).digest()  # 64 bytes
    
    # Extract required bytes
    target_bytes = {128: 16, 192: 24, 256: 32}[strength]
    return digest[:target_bytes]
```

**Process**:
1. Parse hexadecimal key material
2. Hash with SHA-256 (for ≤256-bit) or SHA-512 (for >256-bit)
3. Extract required bytes for AES key size

### Message Encryption

Encrypt plaintext strings using `encrypt_message()`:

```python
key_data = client.get_latest_key(token="", security_level=256)
ciphertext = client.encrypt_message(
    message="Sensitive data to protect",
    key=key_data["key"],
    strength=256
)

# Ciphertext is base64-encoded
print(ciphertext)
# Output: "dGVzdGl2YW5kY2lwaGVydGV4dA=="
```

#### Parameters

- **`message`** (str): Plaintext to encrypt (UTF-8)
- **`key`** (str): Quantum key material (hex string)
- **`strength`** (int): AES key strength (128, 192, or 256)

#### Return Value

Returns a base64-encoded string containing:
- **12-byte IV** (Initialization Vector)
- **Ciphertext** (AES-GCM encrypted data)
- **16-byte authentication tag** (included in ciphertext)

### Message Decryption

Decrypt ciphertext using `decrypt_message()`:

```python
plaintext = client.decrypt_message(
    ciphertext_b64=ciphertext,
    key=key_data["key"],
    strength=256
)

print(plaintext)
# Output: "Sensitive data to protect"
```

#### Parameters

- **`ciphertext_b64`** (str): Base64-encoded ciphertext
- **`key`** (str): Same quantum key material used for encryption
- **`strength`** (int): Same strength used for encryption

#### Return Value

Returns the decrypted plaintext as a UTF-8 string.

**Important**: The key and strength must match those used for encryption.

### Payload Encryption

Encrypt JSON-compatible Python objects using `encrypt_payload()`:

```python
payload = {
    "user_id": "12345",
    "message": "Hello, world!",
    "timestamp": "2025-01-18T12:00:00Z",
    "metadata": {"source": "mobile-app"}
}

ciphertext = client.encrypt_payload(
    payload=payload,
    key=key_data["key"],
    strength=256
)
```

The method automatically:
1. Serializes the payload to JSON
2. Encrypts the JSON string
3. Returns base64-encoded ciphertext

### Payload Decryption

Decrypt and deserialize payloads using `decrypt_payload()`:

```python
decrypted_payload = client.decrypt_payload(
    ciphertext_b64=ciphertext,
    key=key_data["key"],
    strength=256
)

print(decrypted_payload["user_id"])  # "12345"
print(decrypted_payload["message"])  # "Hello, world!"
```

The method automatically:
1. Decrypts the ciphertext
2. Parses the JSON string
3. Returns the Python object

### AES-GCM Encryption Details

The SDK uses **AES-GCM** (Galois/Counter Mode) encryption:

- **Algorithm**: AES (Advanced Encryption Standard)
- **Mode**: GCM (authenticated encryption)
- **IV Size**: 12 bytes (96 bits)
- **Tag Size**: 16 bytes (128 bits)
- **Key Sizes**: 128, 192, or 256 bits

**Why AES-GCM?**
- **Authenticated**: Detects tampering automatically
- **Fast**: Hardware-accelerated on modern CPUs
- **Secure**: NIST-approved for sensitive data
- **Efficient**: Single pass encryption and authentication

### Supported Strength Levels

| Strength | Key Size | Use Case |
|----------|----------|----------|
| 128-bit | 16 bytes | Fast encryption, lower security |
| 192-bit | 24 bytes | Balanced performance and security |
| 256-bit | 32 bytes | Maximum security (recommended) |

```python
# Fast encryption (128-bit)
ciphertext_128 = client.encrypt_message("data", key_data["key"], strength=128)

# Maximum security (256-bit)
ciphertext_256 = client.encrypt_message("data", key_data["key"], strength=256)
```

**Note**: Strength must be one of `(128, 192, 256)`. Other values raise `ValueError`.

---

## API Endpoints Reference

### REST API Architecture

The QbitShield API is a RESTful service built on FastAPI:

```
https://qbitshield-api.railway.app/api
├── /qkd/generate          # Key generation (POST)
├── /health                # Health check (GET)
├── /api/v2/generate       # Alternative endpoint (POST)
└── /docs                  # Interactive API documentation (GET)
```

### `/qkd/generate` Endpoint

The primary endpoint for quantum key generation.

#### Request

```http
POST /api/qkd/generate
Content-Type: application/json
X-API-Key: sk_live_your_api_key
Authorization: Bearer your_auth0_token

{
  "security_level": 256,
  "metadata": {
    "application": "my-app"
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "key": "694887d326681a6d1ba2d5b21e575787b8bea356065e0695c77641efba6b6341",
    "entropy": 99.9,
    "timestamp": "2025-01-18T20:37:33.254699+00:00",
    "nist_validation": {
      "certification_status": "PASS",
      "tests_passed": 15,
      "total_tests": 15,
      "compliance_level": "CERTIFICATION_READY"
    },
    "metadata": {
      "application": "my-app"
    }
  }
}
```

#### Using curl

```bash
curl -X POST "https://qbitshield-api.railway.app/api/qkd/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_your_api_key" \
  -H "Authorization: Bearer your_auth0_token" \
  -d '{
    "security_level": 256,
    "metadata": {"application": "my-app"}
  }'
```

### Request/Response Formats

#### Request Body Schema

```typescript
{
  security_level: 128 | 192 | 256 | 384,  // Required
  metadata?: {                              // Optional
    [key: string]: any
  }
}
```

#### Response Schema

```typescript
{
  success: boolean,
  data?: {
    key: string,              // Hex-encoded key material
    entropy: number,          // 0-100
    timestamp: string,         // ISO 8601
    nist_validation: {
      certification_status: "PASS" | "FAIL",
      tests_passed: number,
      total_tests: number,
      compliance_level: string
    },
    metadata?: object
  },
  error?: string,
  details?: string
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "success": false,
  "error": "Invalid security level",
  "details": "Security level must be 128, 192, 256, or 384"
}
```

#### 401 Unauthorized

```json
{
  "success": false,
  "error": "Invalid API key"
}
```

#### 429 Too Many Requests

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "details": "60 requests per minute limit reached"
}
```

#### 500 Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error",
  "details": "Key generation failed"
}
```

### Rate Limiting Information

Rate limits are enforced per API key:

- **Window**: 1 minute rolling window
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Response**: `429 Too Many Requests` when exceeded

```python
import requests
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

try:
    key_data = client.get_latest_key(token="", security_level=256)
    # Check rate limit headers
    response = client.session.post(...)  # Access last response
    print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
except requests.HTTPError as e:
    if e.response.status_code == 429:
        reset_time = e.response.headers.get('X-RateLimit-Reset')
        print(f"Rate limit resets at: {reset_time}")
```

### Health Check Endpoints

#### `/health`

Simple health check:

```bash
curl https://qbitshield-api.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T20:37:33.254699+00:00"
}
```

#### SDK vs Direct API Usage

**When to use the SDK:**
- You want encryption/decryption helpers
- You prefer Python objects over JSON
- You want automatic error handling
- You need latency logging

**When to use direct API calls:**
- You're not using Python
- You need fine-grained control
- You're building a custom client
- You want to avoid SDK dependencies

---

## Common Use Cases

### Secure Messaging Application

Encrypt messages between users:

```python
from qbitshield.client import QbitShieldClient

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

def send_secure_message(recipient_id: str, message: str):
    # Generate a new key for this message
    key_data = client.get_latest_key(
        token="",
        security_level=256,
        metadata={"recipient": recipient_id}
    )
    
    # Encrypt the message
    ciphertext = client.encrypt_message(message, key_data["key"], strength=256)
    
    # Store ciphertext and key_id (not the key itself!)
    store_message(recipient_id, ciphertext, key_data["key_id"])
    
    return ciphertext

def read_secure_message(key_id: str, ciphertext: str):
    # Retrieve the key (from secure storage)
    key = retrieve_key(key_id)
    
    # Decrypt the message
    plaintext = client.decrypt_message(ciphertext, key, strength=256)
    
    return plaintext
```

### Data Encryption for Storage

Encrypt sensitive data before storing in databases:

```python
def encrypt_user_data(user_data: dict):
    # Generate key
    key_data = client.get_latest_key(
        token="",
        security_level=256,
        metadata={"user_id": user_data["id"]}
    )
    
    # Encrypt sensitive fields
    encrypted_data = {
        "id": user_data["id"],
        "email_encrypted": client.encrypt_message(
            user_data["email"],
            key_data["key"],
            strength=256
        ),
        "ssn_encrypted": client.encrypt_message(
            user_data["ssn"],
            key_data["key"],
            strength=256
        ),
        "key_id": key_data["key_id"]  # Store for decryption
    }
    
    return encrypted_data
```

### API Payload Protection

Encrypt API request/response payloads:

```python
def secure_api_call(endpoint: str, payload: dict):
    # Generate session key
    key_data = client.get_latest_key(
        token="",
        security_level=256,
        metadata={"endpoint": endpoint}
    )
    
    # Encrypt payload
    encrypted_payload = client.encrypt_payload(payload, key_data["key"], strength=256)
    
    # Send to API
    response = requests.post(
        endpoint,
        json={
            "encrypted_payload": encrypted_payload,
            "key_id": key_data["key_id"]
        }
    )
    
    return response
```

### Session Key Management

Generate and rotate session keys:

```python
class SessionManager:
    def __init__(self):
        self.client = QbitShieldClient(
            base_url="https://qbitshield-api.railway.app/api",
            api_key="your-key"
        )
        self.session_keys = {}
    
    def create_session(self, session_id: str):
        key_data = self.client.get_latest_key(
            token="",
            security_level=256,
            metadata={"session_id": session_id}
        )
        self.session_keys[session_id] = key_data["key"]
        return key_data["key"]
    
    def encrypt_session_data(self, session_id: str, data: dict):
        key = self.session_keys.get(session_id)
        if not key:
            key = self.create_session(session_id)
        return self.client.encrypt_payload(data, key, strength=256)
    
    def decrypt_session_data(self, session_id: str, ciphertext: str):
        key = self.session_keys.get(session_id)
        if not key:
            raise ValueError("Session not found")
        return self.client.decrypt_payload(ciphertext, key, strength=256)
```

### Batch Encryption Operations

Encrypt multiple items efficiently:

```python
def encrypt_batch(items: list, key_data: dict):
    encrypted_items = []
    for item in items:
        encrypted = client.encrypt_payload(item, key_data["key"], strength=256)
        encrypted_items.append(encrypted)
    return encrypted_items

# Generate one key for the batch
key_data = client.get_latest_key(
    token="",
    security_level=256,
    metadata={"batch_id": "batch_123"}
)

# Encrypt all items with the same key
items = [{"id": i, "data": f"item_{i}"} for i in range(100)]
encrypted_batch = encrypt_batch(items, key_data)
```

### Integration with Existing Systems

Integrate with web frameworks:

#### Flask Example

```python
from flask import Flask, request, jsonify
from qbitshield.client import QbitShieldClient

app = Flask(__name__)
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key=os.getenv("QBITSHIELD_API_KEY")
)

@app.route("/encrypt", methods=["POST"])
def encrypt_endpoint():
    data = request.json
    key_data = client.get_latest_key(token="", security_level=256)
    ciphertext = client.encrypt_payload(data, key_data["key"], strength=256)
    return jsonify({"ciphertext": ciphertext})

@app.route("/decrypt", methods=["POST"])
def decrypt_endpoint():
    data = request.json
    key = data["key"]  # Retrieve from secure storage
    plaintext = client.decrypt_payload(data["ciphertext"], key, strength=256)
    return jsonify({"plaintext": plaintext})
```

#### Django Example

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from qbitshield.client import QbitShieldClient
import os

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key=os.getenv("QBITSHIELD_API_KEY")
)

@require_http_methods(["POST"])
def encrypt_view(request):
    data = request.POST
    key_data = client.get_latest_key(token="", security_level=256)
    ciphertext = client.encrypt_payload(dict(data), key_data["key"], strength=256)
    return JsonResponse({"ciphertext": ciphertext})
```

---

## Advanced Features

### Latency Logging and Performance Monitoring

The SDK automatically logs encryption/decryption latency:

```python
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

# Perform operations
key_data = client.get_latest_key(token="", security_level=256)
client.encrypt_message("test", key_data["key"], strength=256)
client.decrypt_message(ciphertext, key_data["key"], strength=256)

# Access latency log
for entry in client.latency_log:
    print(f"{entry['operation']}: {entry['latency_ms']:.2f}ms")

# Calculate statistics
import statistics
latencies = [e["latency_ms"] for e in client.latency_log]
print(f"Mean: {statistics.mean(latencies):.2f}ms")
print(f"Median: {statistics.median(latencies):.2f}ms")
print(f"Max: {max(latencies):.2f}ms")
```

### Custom Metadata Handling

Attach and retrieve custom metadata:

```python
# Attach metadata during key generation
key_data = client.get_latest_key(
    token="",
    security_level=256,
    metadata={
        "user_id": "12345",
        "operation": "data_encryption",
        "environment": "production",
        "custom_field": "custom_value"
    }
)

# Metadata is returned in response
print(key_data["metadata"])
# Output: {"user_id": "12345", "operation": "data_encryption", ...}
```

### Error Handling Strategies

#### Retry Logic

Implement exponential backoff for transient errors:

```python
import time
import requests
from qbitshield.client import QbitShieldClient

def get_key_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.get_latest_key(token="", security_level=256)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
            time.sleep(wait_time)
```

#### Circuit Breaker Pattern

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

# Usage
breaker = CircuitBreaker()
key_data = breaker.call(client.get_latest_key, token="", security_level=256)
```

### Connection Pooling

The SDK uses connection pooling automatically via `requests.Session`:

```python
# Single client instance reuses connections
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key"
)

# All requests reuse the same TCP connection
for i in range(100):
    key_data = client.get_latest_key(token="", security_level=256)
    # Efficient connection reuse
```

---

## Best Practices

### Key Management Recommendations

1. **Never store keys in code**: Use environment variables or secret management
2. **Rotate keys regularly**: Generate new keys periodically
3. **Use different keys per environment**: Separate dev/staging/prod keys
4. **Limit key scope**: Use keys only for their intended purpose
5. **Monitor key usage**: Track key generation and usage patterns

```python
# Good: Environment variables
api_key = os.getenv("QBITSHIELD_API_KEY")

# Bad: Hardcoded keys
api_key = "sk_live_abc123"  # Never do this!
```

### Security Considerations

1. **HTTPS only**: Always use HTTPS for API calls
2. **Validate keys**: Check key format before use
3. **Secure storage**: Store keys in encrypted storage
4. **Access control**: Limit who can access API keys
5. **Audit logging**: Log all key generation and usage

```python
# Validate API key format
def validate_api_key(key: str) -> bool:
    return key.startswith(("sk_test_", "sk_live_")) and len(key) > 20

# Secure key storage
import keyring
keyring.set_password("qbitshield", "api_key", api_key)
stored_key = keyring.get_password("qbitshield", "api_key")
```

### Performance Optimization

1. **Reuse client instances**: Don't create new clients for each request
2. **Batch operations**: Generate one key for multiple encryptions
3. **Connection pooling**: Let the SDK handle connection reuse
4. **Async operations**: Use async/await for concurrent requests (if supported)

```python
# Good: Reuse client
client = QbitShieldClient(...)
for item in items:
    key_data = client.get_latest_key(...)  # Reuses connection

# Bad: New client each time
for item in items:
    client = QbitShieldClient(...)  # New connection each time
    key_data = client.get_latest_key(...)
```

### Testing Strategies

1. **Use test keys**: Use `sk_test_` keys for development
2. **Mock API calls**: Mock the SDK in unit tests
3. **Test error handling**: Test all error paths
4. **Integration tests**: Test against staging environment

```python
# Mock for unit tests
from unittest.mock import Mock, patch

@patch('qbitshield.client.QbitShieldClient.get_latest_key')
def test_encryption(mock_get_key):
    mock_get_key.return_value = {"key": "0" * 64}
    client = QbitShieldClient(...)
    # Test encryption logic
```

### Production Deployment Tips

1. **Environment configuration**: Use environment-specific configs
2. **Monitoring**: Set up alerts for API errors
3. **Logging**: Log all cryptographic operations
4. **Backup keys**: Store keys in multiple secure locations
5. **Documentation**: Document key management procedures

```python
# Production configuration
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = QbitShieldClient(
    base_url=os.getenv("QBITSHIELD_API_URL", "https://qbitshield-api.railway.app/api"),
    api_key=os.getenv("QBITSHIELD_API_KEY")
)

try:
    key_data = client.get_latest_key(token="", security_level=256)
    logger.info(f"Key generated: {key_data['key'][:16]}...")
except Exception as e:
    logger.error(f"Key generation failed: {e}")
    raise
```

---

## Troubleshooting

### Common Errors and Solutions

#### "API key is required"

**Error**: `ValueError: API key is required – supply api_key when constructing QbitShieldClient`

**Solution**: Provide an API key when creating the client:

```python
client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-api-key"  # Required!
)
```

#### "Invalid API key"

**Error**: `401 Unauthorized` or `403 Forbidden`

**Solution**: 
- Check that your API key is correct
- Verify the key hasn't been revoked
- Ensure you're using the right key type (test vs live)

```python
# Verify key format
api_key = os.getenv("QBITSHIELD_API_KEY")
if not api_key or not api_key.startswith(("sk_test_", "sk_live_")):
    raise ValueError("Invalid API key format")
```

#### "Rate limit exceeded"

**Error**: `429 Too Many Requests`

**Solution**: 
- Implement exponential backoff
- Reduce request frequency
- Upgrade your subscription tier

```python
import time

def get_key_with_backoff(client, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.get_latest_key(token="", security_level=256)
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

#### "Failed to authenticate ciphertext"

**Error**: `InvalidTag: Failed to authenticate ciphertext – wrong key or corrupted data`

**Solution**: 
- Ensure you're using the same key for encryption and decryption
- Verify the key hasn't been corrupted
- Check that the ciphertext hasn't been modified

```python
# Store key securely
key_id = store_key_securely(key_data["key"])

# Retrieve same key for decryption
key = retrieve_key_securely(key_id)
plaintext = client.decrypt_message(ciphertext, key, strength=256)
```

### API Connection Issues

#### Connection Timeout

**Symptom**: `requests.exceptions.Timeout`

**Solution**: Increase timeout or check network:

```python
import requests

session = requests.Session()
session.timeout = 60  # 60 seconds

client = QbitShieldClient(
    base_url="https://qbitshield-api.railway.app/api",
    api_key="your-key",
    session=session
)
```

#### DNS Resolution Failure

**Symptom**: `requests.exceptions.ConnectionError`

**Solution**: 
- Check internet connection
- Verify API URL is correct
- Check DNS settings

```python
# Test connectivity
import requests
try:
    response = requests.get("https://qbitshield-api.railway.app/health", timeout=5)
    print("API is reachable")
except requests.exceptions.ConnectionError:
    print("Cannot reach API. Check network connection.")
```

### Authentication Problems

#### Invalid Auth0 Token

**Symptom**: `401 Unauthorized` even with valid API key

**Solution**: 
- Verify Auth0 token is valid and not expired
- Check token format (should be JWT)
- Ensure token is for the correct audience

```python
# Validate token format (basic check)
def is_valid_jwt(token: str) -> bool:
    parts = token.split('.')
    return len(parts) == 3  # JWT has 3 parts

if not is_valid_jwt(auth0_token):
    raise ValueError("Invalid Auth0 token format")
```

### Performance Issues

#### Slow Key Generation

**Symptom**: Key generation takes >1 second

**Solution**: 
- Check network latency
- Verify API is not under heavy load
- Consider caching keys for short periods

```python
# Cache keys for 5 minutes
from functools import lru_cache
from time import time

_key_cache = {}
_cache_ttl = 300  # 5 minutes

def get_cached_key(client, security_level=256):
    cache_key = f"key_{security_level}"
    if cache_key in _key_cache:
        key_data, timestamp = _key_cache[cache_key]
        if time() - timestamp < _cache_ttl:
            return key_data
    
    key_data = client.get_latest_key(token="", security_level=security_level)
    _key_cache[cache_key] = (key_data, time())
    return key_data
```

### Debugging Tips

#### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('requests.packages.urllib3')
logger.setLevel(logging.DEBUG)
```

#### Inspect Requests/Responses

```python
# Enable request/response logging
import http.client
http.client.HTTPConnection.debuglevel = 1

# Or use requests logging
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

#### Test API Connectivity

```python
def test_api_connection(base_url: str, api_key: str):
    client = QbitShieldClient(base_url=base_url, api_key=api_key)
    try:
        # Test health endpoint
        response = client.session.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        
        # Test key generation
        key_data = client.get_latest_key(token="", security_level=256)
        print(f"Key generation: SUCCESS")
        print(f"Key: {key_data['key'][:16]}...")
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
```

---

## Examples & Code Samples

### Complete Working Example

```python
#!/usr/bin/env python3
"""
Complete QbitShield SDK example demonstrating key generation and encryption.
"""

import os
from qbitshield.client import QbitShieldClient

def main():
    # Initialize client
    client = QbitShieldClient(
        base_url=os.getenv("QBITSHIELD_API_URL", "https://qbitshield-api.railway.app/api"),
        api_key=os.getenv("QBITSHIELD_API_KEY", "QSDemo")  # Use demo key for testing
    )
    
    print("🔐 QbitShield SDK Example")
    print("=" * 50)
    
    # Generate quantum key
    print("\n1. Generating quantum key...")
    try:
        key_data = client.get_latest_key(
            token="",  # Empty for demo
            security_level=256,
            metadata={"example": "complete_working_example"}
        )
        print(f"✅ Key generated: {key_data['key'][:32]}...")
        print(f"   Entropy: {key_data['entropy']}")
        print(f"   NIST Status: {key_data['nist']['certification_status']}")
        print(f"   Tests Passed: {key_data['nist']['tests_passed']}/{key_data['nist']['total_tests']}")
    except Exception as e:
        print(f"❌ Key generation failed: {e}")
        return
    
    # Encrypt a message
    print("\n2. Encrypting message...")
    message = "This is a secret message that needs protection!"
    try:
        ciphertext = client.encrypt_message(message, key_data["key"], strength=256)
        print(f"✅ Message encrypted")
        print(f"   Original length: {len(message)} bytes")
        print(f"   Ciphertext length: {len(ciphertext)} bytes (base64)")
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return
    
    # Decrypt the message
    print("\n3. Decrypting message...")
    try:
        plaintext = client.decrypt_message(ciphertext, key_data["key"], strength=256)
        print(f"✅ Message decrypted")
        print(f"   Decrypted: {plaintext}")
        assert plaintext == message, "Decrypted message doesn't match original!"
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return
    
    # Encrypt a payload
    print("\n4. Encrypting JSON payload...")
    payload = {
        "user_id": "12345",
        "email": "user@example.com",
        "data": {"sensitive": "information"}
    }
    try:
        payload_cipher = client.encrypt_payload(payload, key_data["key"], strength=256)
        print(f"✅ Payload encrypted")
        
        # Decrypt payload
        payload_plain = client.decrypt_payload(payload_cipher, key_data["key"], strength=256)
        print(f"✅ Payload decrypted")
        print(f"   User ID: {payload_plain['user_id']}")
        assert payload_plain == payload, "Decrypted payload doesn't match original!"
    except Exception as e:
        print(f"❌ Payload encryption/decryption failed: {e}")
        return
    
    # Show latency statistics
    print("\n5. Performance Statistics...")
    if client.latency_log:
        latencies = [e["latency_ms"] for e in client.latency_log]
        print(f"   Operations logged: {len(client.latency_log)}")
        print(f"   Average latency: {sum(latencies) / len(latencies):.2f}ms")
        print(f"   Max latency: {max(latencies):.2f}ms")
        print(f"   Min latency: {min(latencies):.2f}ms")
    
    print("\n" + "=" * 50)
    print("✅ All operations completed successfully!")

if __name__ == "__main__":
    main()
```

### Integration Patterns

#### Flask Web Application

```python
from flask import Flask, request, jsonify
from qbitshield.client import QbitShieldClient
import os

app = Flask(__name__)
client = QbitShieldClient(
    base_url=os.getenv("QBITSHIELD_API_URL", "https://qbitshield-api.railway.app/api"),
    api_key=os.getenv("QBITSHIELD_API_KEY")
)

@app.route("/api/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    message = data.get("message")
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    try:
        key_data = client.get_latest_key(token="", security_level=256)
        ciphertext = client.encrypt_message(message, key_data["key"], strength=256)
        return jsonify({
            "ciphertext": ciphertext,
            "key_id": key_data.get("key_id")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/decrypt", methods=["POST"])
def decrypt():
    data = request.json
    ciphertext = data.get("ciphertext")
    key = data.get("key")  # In production, retrieve from secure storage
    
    if not ciphertext or not key:
        return jsonify({"error": "ciphertext and key required"}), 400
    
    try:
        plaintext = client.decrypt_message(ciphertext, key, strength=256)
        return jsonify({"plaintext": plaintext})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
```

#### Batch Processing

```python
def process_batch(items: list):
    """Process a batch of items with a single key."""
    # Generate one key for the entire batch
    key_data = client.get_latest_key(
        token="",
        security_level=256,
        metadata={"batch_size": len(items), "operation": "batch_encryption"}
    )
    
    encrypted_items = []
    for item in items:
        encrypted = client.encrypt_payload(item, key_data["key"], strength=256)
        encrypted_items.append({
            "id": item["id"],
            "encrypted_data": encrypted
        })
    
    return {
        "key_id": key_data.get("key_id"),
        "encrypted_items": encrypted_items
    }
```

### Testing Examples

```python
import pytest
from unittest.mock import Mock, patch
from qbitshield.client import QbitShieldClient
from cryptography.exceptions import InvalidTag

def test_key_generation():
    """Test key generation."""
    client = QbitShieldClient("https://api.example.com", api_key="test-key")
    
    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "key": "a1" * 32,
                "entropy": 99.9,
                "timestamp": "2025-01-18T12:00:00Z",
                "nist_validation": {
                    "certification_status": "PASS",
                    "tests_passed": 15,
                    "total_tests": 15
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        key_data = client.get_latest_key(token="", security_level=256)
        
        assert key_data["key"] == "a1" * 32
        assert key_data["entropy"] == 99.9

def test_encrypt_decrypt_roundtrip():
    """Test encryption/decryption roundtrip."""
    client = QbitShieldClient("https://api.example.com", api_key="test-key")
    key_hex = "a1" * 32
    plaintext = "test message"
    
    ciphertext = client.encrypt_message(plaintext, key_hex, strength=256)
    assert ciphertext != plaintext
    
    decrypted = client.decrypt_message(ciphertext, key_hex, strength=256)
    assert decrypted == plaintext

def test_wrong_key_fails():
    """Test that wrong key fails decryption."""
    client = QbitShieldClient("https://api.example.com", api_key="test-key")
    key_hex = "a1" * 32
    plaintext = "test message"
    
    ciphertext = client.encrypt_message(plaintext, key_hex, strength=256)
    
    wrong_key = "ff" * 32
    with pytest.raises(InvalidTag):
        client.decrypt_message(ciphertext, wrong_key, strength=256)
```

---

## Additional Resources

- **API Documentation**: [https://qbitshield-api.railway.app/docs](https://qbitshield-api.railway.app/docs)
- **Enterprise Portal**: [https://qbitshield-enterprise.vercel.app](https://qbitshield-enterprise.vercel.app)
- **GitHub Repository**: [https://github.com/Sensorman/qbitshield-v2](https://github.com/Sensorman/qbitshield-v2)
- **Support**: support@qbitshield.com

---

**Last Updated**: January 2025  
**SDK Version**: 0.1.1  
**API Version**: 2.0.0

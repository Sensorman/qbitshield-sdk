import requests

API_URL = "https://qbitshield-api-258062438248.us-central1.run.app/qkd/generate"

def generate_key(api_key: str, return_full: bool = False) -> dict:
    """Generate a quantum-safe hashed key from QbitShield."""
    headers = {"api-key": api_key}
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if return_full:
            return data  # includes qasm + measured_bits
        return {"hashed_key": data.get("hashed_key")}

    except requests.RequestException as e:
        return {"error": str(e)}
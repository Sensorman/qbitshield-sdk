import requests


class QbitShieldClient:
    def __init__(self, api_key, base_url="https://theqbitshield-api-258062438248.us-central1.run.app"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_key(self):
        url = f"{self.base_url}/qkd/generate"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            print(f"[QbitShield SDK] POST to: {url}")
            print(f"[QbitShield SDK] Headers: {headers}")

            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"[QbitShield SDK] HTTP error: {http_err}")
            return {"error": str(http_err)}

        except requests.exceptions.RequestException as req_err:
            print(f"[QbitShield SDK] Request error: {req_err}")
            return {"error": str(req_err)}
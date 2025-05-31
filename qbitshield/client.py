import requests

class QbitShieldClient:
    def __init__(self, api_key, base_url="https://theqbitshield-api-258062438248.us-central1.run.app"):
        self.api_key = api_key
        self.base_url = base_url

    def generate_key(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(f"{self.base_url}/qkd/generate", headers=headers)
        response.raise_for_status()
        return response.json()

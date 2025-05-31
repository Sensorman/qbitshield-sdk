from qbitshield.client import QbitShieldClient

def test_generate_key():
    client = QbitShieldClient(api_key="demo_or_test_key")
    result = client.generate_key()
    assert "key" in result

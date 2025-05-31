from qbitshield import QbitShieldClient


def test_generate_key():
    client = QbitShieldClient(api_key="QSDemo")
    result = client.generate_key()

    print("Key:", result["key"])
    print("QASM:", result["qasm"])

    assert "key" in result
    assert "qasm" in result
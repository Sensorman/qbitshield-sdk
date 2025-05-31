from qbitshield import QbitShieldClient

client = QbitShieldClient(api_key="QSDemo")
result = client.generate_key()

print(result["key"])
print(result["qasm"])
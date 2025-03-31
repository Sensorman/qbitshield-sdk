from qbitshield import client

key_data = client.generate_key(api_key="a`R$qE;nHM><:/tpGyFDL%^,kjxs*4_", return_full=True)

print("✅ Hashed Key:", key_data.get("hashed_key"))
print("🧬 Bits:", key_data.get("measured_bits"))
print("📄 QASM:", key_data.get("qasm")[:100] + "...")
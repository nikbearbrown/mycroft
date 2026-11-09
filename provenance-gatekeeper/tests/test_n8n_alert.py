import requests

API_URL = "http://localhost:8000/verify"
TOKEN_URL = "http://localhost:8000/token"

print("1. Authenticating as Admin...")
auth_response = requests.post(TOKEN_URL, data={"username": "admin", "password": "secret_password"})
token = auth_response.json().get("access_token")

if not token:
    print("Authentication failed. Is the Docker container running?")
    exit()

print(f"Token retrieved. Proceeding to trigger n8n alert webhook...")

# Intentionally trigger a Magnitude Error (4.5M vs truth of 5.0M)
bad_payload = {
    "claim_id": "ALERT-TEST-01",
    "generated_claim": "$4,500,000.00"
}

headers = {"Authorization": f"Bearer {token}"}

response = requests.post(API_URL, json=bad_payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print("\n--- GATEKEEPER RESPONSE ---")
    print(f"Verdict: {result['verdict']}")
    print(f"Variance Type: {result['variance_type']}")
    print(f"Explanation: {result['explanation']}")
    print("\n✅ Webhook triggered! Check your n8n dashboard at http://localhost:5678")
else:
    print(f"Error: {response.status_code} - {response.text}")
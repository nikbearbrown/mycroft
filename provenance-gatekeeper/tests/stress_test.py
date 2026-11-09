import requests

API_URL = "http://localhost:8000/verify"
TOKEN_URL = "http://localhost:8000/token"

# Assuming the seeded ChromaDB ground truth is still:
# "The company revenue grew to exactly 5000000 this quarter."
adversarial_payloads = [
    # These should now PASS (Valid variants of 5,000,000)
    {"claim_id": "NORM-01", "generated_claim": "$5,000,000.00"},       
    {"claim_id": "NORM-02", "generated_claim": "5.0M"},                
    {"claim_id": "NORM-03", "generated_claim": "exactly 5 million"}, 
    {"claim_id": "NORM-04", "generated_claim": "5000000"}, 
    
    # These should FAIL (Magnitude errors)
    {"claim_id": "STRESS-01", "generated_claim": "$4,500,000.00"},       
    {"claim_id": "STRESS-02", "generated_claim": "4.5M"}, 
    
    # These should FAIL (Data type errors / SQL Injection)
    {"claim_id": "STRESS-03", "generated_claim": "N/A"},                    
    {"claim_id": "STRESS-04", "generated_claim": "null"},                     
    {"claim_id": "STRESS-05", "generated_claim": "DROP TABLE logs;"}        
]

print("COMMENCING JWT AUTH & ADVERSARIAL STRESS TEST...\n")

# 1. Attempt unauthorized access (Should fail)
print("1. Testing Unauthorized Access (Expect 401)...")
response = requests.post(API_URL, json=adversarial_payloads[0])
print(f"Status: {response.status_code} | Response: {response.json()}\n")

# 2. Authenticate and get JWT Token
print("2. Authenticating as Admin...")
auth_response = requests.post(TOKEN_URL, data={"username": "admin", "password": "secret_password"})
if auth_response.status_code == 200:
    token = auth_response.json()["access_token"]
    print(f"Success! Retrieved JWT Token: {token[:20]}...\n")
else:
    print(f"Authentication failed! Status: {auth_response.status_code}")
    exit()

# 3. Use Token for Authorized Request
print("3. Testing Authorized Access with Mixed Payloads...")
headers = {"Authorization": f"Bearer {token}"}

for i, payload in enumerate(adversarial_payloads):
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        status = response.status_code
        
        if status == 200:
            result = response.json().get("verdict", "UNKNOWN")
            variance = response.json().get("variance_type", "")
            print(f"Test {i+1:<2} | Claim: {payload['generated_claim']:<20} | Verdict: {result} | Type: {variance}")
        else:
            result = response.json().get("detail", "HTTP ERROR")
            print(f"Test {i+1:<2} | Claim: {payload['generated_claim']:<20} | Status: {status} | Error: {result}")
            
    except Exception as e:
        print(f"Test {i+1:<2} | Claim: {payload['generated_claim']:<20} | FATAL CRASH: {e}")
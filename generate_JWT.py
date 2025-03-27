import jwt
import base64
import sys

if len(sys.argv) != 2:
    print("Usage: generate_JWT.py <base64-encoded-secret-key>")
    sys.exit(1)

secret_base64 = sys.argv[1]
secret = base64.b64decode(secret_base64)
payload = {"role": "event_logger"}
token = jwt.encode(payload, secret, algorithm="HS256")

# echo JWT
print(token)

